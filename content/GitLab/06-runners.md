---
title: GitLab Runners
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/cicd, programacion/docker]
type: nota
status: en-progreso
source: claude-code
aliases: [runners, gitlab-runner, agente CI]
---

# 🏃 GitLab Runners

## Por qué existen los runners

Cuando defines un pipeline en `.gitlab-ci.yml`, le dices a GitLab *qué* ejecutar. Pero alguien tiene que *ejecutarlo físicamente*: descargar el código, correr los comandos, devolver los logs y el resultado.

Ese "alguien" es el **runner**: un proceso demonio (`gitlab-runner`) instalado en alguna máquina (tuya, de la nube, o de GitLab) que escucha trabajos de la cola del servidor y los ejecuta.

Sin runners, el pipeline existe en papel pero nunca corre. Es el puente entre la definición YAML y la ejecución real.

Analogía de hardware: si el servidor GitLab es el controlador (PLC/MCU), el runner es el actuador — recibe la orden y hace el trabajo físico.

---

## 🗺️ Panorama: tipos de runner por alcance

| Tipo | Alcance | Quién lo administra | Cuándo usarlo |
|---|---|---|---|
| **Shared runner** | Toda la instancia GitLab | Administrador de GitLab | GitLab.com SaaS; proyectos pequeños sin infra propia |
| **Group runner** | Un grupo y todos sus subproyectos | Owner del grupo | Organización/empresa con varios repos; mismo entorno para todos |
| **Project runner** | Un solo proyecto | Maintainer del proyecto | Proyecto con requisitos únicos (GPU, secretos especiales, hardware físico) |

Los runners **se heredan hacia abajo**: un group runner está disponible para todos los proyectos del grupo. Los shared runners están disponibles para todos (salvo que se desactiven explícitamente).

---

## ⚙️ Executors: el motor del runner

El **executor** define *cómo* el runner ejecuta el job: en qué entorno, con qué aislamiento. Es la decisión de diseño más importante al registrar un runner.

### Tabla comparativa de executors principales

| Executor | Aislamiento | Requiere | Ideal para |
|---|---|---|---|
| **Docker** | Alto (contenedor por job) | Docker instalado | La mayoría de proyectos; imagen limpia por job |
| **Shell** | Ninguno (corre directo en el host) | Solo el runner instalado | Pruebas rápidas, hardware físico, cuando no puedes Docker |
| **Kubernetes** | Alto (pod por job) | Cluster K8s | Escala horizontal; entornos cloud-native |
| **Docker Machine** | Alto (VM efímera por job) | Docker Machine (deprecated) | Legado; mejor usar K8s en su lugar |
| **VirtualBox / Parallels** | Muy alto (VM completa) | Hypervisor | Pruebas de SO completas; raro en CI moderno |

### Docker executor (el principal)

Cada job arranca un contenedor **desde cero** usando la imagen que especifiques en el YAML (`image: node:20`, `image: python:3.12`, etc.). Cuando el job termina, el contenedor desaparece. Ventajas:

- **Reproducibilidad**: dos ejecuciones del mismo job son idénticas.
- **Aislamiento**: un job no contamina el siguiente.
- **Flexibilidad**: cambias la imagen en el YAML sin tocar el runner.

Desventaja: el runner necesita Docker instalado y permisos para manejarlo.

### Shell executor

El job corre directamente en la shell del host donde está instalado el runner (como si lo ejecutaras tú en terminal). Sin contenedores, sin aislamiento.

**Cuándo tiene sentido:**
- Acceder a hardware físico (puerto serie, GPIO, microcontroladores — muy relevante para proyectos PlatformIO).
- Máquinas donde Docker no está disponible o tiene coste prohibitivo.
- Scripts de despliegue que necesitan identidad del sistema real.

**Cuándo NO usarlo:**
- Si los jobs instalan dependencias globales que podrían chocar entre sí.
- Entornos multi-proyecto donde el aislamiento importa.

---

## 📋 Registrar un runner

Registrar = conectar el proceso `gitlab-runner` instalado en tu máquina con tu instancia GitLab. Se hace una sola vez (o cuando cambias de servidor).

### Prerequisitos

```bash
# Instalar gitlab-runner (Ubuntu/Debian)
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
sudo apt install gitlab-runner

# Verificar que el servicio corre
sudo gitlab-runner status
```

### Obtener el registration token

- **Shared runner**: Admin Area → CI/CD → Runners → Registration token
- **Group runner**: Grupo → Settings → CI/CD → Runners → Registration token
- **Project runner**: Proyecto → Settings → CI/CD → Runners → Registration token

> Nota: GitLab ≥15.6 reemplaza los registration tokens por **runner authentication tokens** (flujo nuevo con `gitlab-runner create` en la UI primero). La lógica es la misma; solo cambia dónde copias el token.

### Comando de registro (interactivo)

```bash
sudo gitlab-runner register
```

Te pedirá:
1. URL de tu instancia (`https://gitlab.com` o la tuya propia)
2. Registration token
3. Descripción del runner (nombre libre)
4. Tags (importante — ver sección siguiente)
5. Executor (`docker`, `shell`, etc.)
6. Imagen Docker por defecto (si elegiste Docker)

### Registro no interactivo (para scripts/automatización)

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.com" \
  --registration-token "TU_TOKEN_AQUI" \
  --description "runner-docker-local" \
  --executor "docker" \
  --docker-image "alpine:latest" \
  --tag-list "docker,linux,mi-proyecto" \
  --run-untagged="false"   # solo acepta jobs con tags coincidentes
```

La configuración se guarda en `/etc/gitlab-runner/config.toml`.

---

## 🏷️ Tags de runner: enrutamiento de jobs

Los **tags** son etiquetas que funcionan como un sistema de enrutamiento: conectan jobs específicos del YAML con runners específicos.

### Cómo funciona el matching

```yaml
# .gitlab-ci.yml
build-firmware:
  stage: build
  tags:
    - embedded        # este job solo lo acepta un runner con tag "embedded"
    - stm32
  script:
    - make all

run-tests:
  stage: test
  tags:
    - docker          # runner con Docker executor
  image: python:3.12
  script:
    - pytest
```

Si ningún runner disponible tiene los tags requeridos, el job queda en cola indefinidamente (`pending`). Esto es el error más común al configurar runners propios.

### Runners sin tags (untagged)

Un runner configurado con `run-untagged = true` acepta jobs que no tienen `tags:` en el YAML. Útil como runner genérico para trabajos simples.

### Estrategia recomendada de tags

| Tag | Significado | Runner asignado |
|---|---|---|
| `docker` | Necesita Docker executor | Runner Docker en servidor |
| `shell` | Necesita acceso directo al host | Runner shell en máquina específica |
| `embedded` | Necesita toolchain de firmware | Runner en tu máquina de desarrollo |
| `gpu` | Necesita GPU (ML/rendering) | Servidor con GPU |
| `deploy-prod` | Solo runners de producción | Runner dedicado, red segura |

---

## 🆚 Runners autoalojados vs minutos SaaS

Esta es la decisión económica y operacional clave.

| Aspecto | GitLab.com SaaS (shared) | Runner autoalojado |
|---|---|---|
| **Coste** | Minutos incluidos (400/mes free; 10.000 en paid) | Hardware propio + electricidad; software gratis |
| **Límite de tiempo** | Sí: se agotan los minutos | No: ilimitado |
| **Mantenimiento** | Ninguno | Tú instalas, actualizas, monitorizas |
| **Aislamiento de red** | Internet público | Acceso a tu red local (ideal para deploys internos) |
| **Hardware especial** | No (CPU estándar) | El que pongas (GPU, puertos serie, etc.) |
| **Arranque** | Inmediato | Depende de carga del servidor |
| **Privacidad de secretos** | El código corre en infra de GitLab | El código nunca sale de tu máquina |

**Cuándo autoalojar:**
- Proyectos con builds largos (firmware, ML) que agotarían minutos.
- Necesitas acceso a hardware físico o red local.
- Datos sensibles que no deben salir de tu infraestructura.
- Organización con muchos repos: un runner propio para todos sale más barato.

**Cuándo usar shared (SaaS):**
- Proyectos pequeños o abiertos.
- No quieres gestionar infraestructura.
- Builds cortos que caben en la cuota gratuita.

---

## 🐳 Montar tu propio runner con executor Docker

Guía paso a paso para un servidor Linux (Ubuntu 22.04 / Debian 12).

### 1. Instalar Docker

```bash
# Si no tienes Docker instalado
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker gitlab-runner   # dar permisos al usuario del runner
```

### 2. Instalar gitlab-runner

```bash
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
sudo apt install gitlab-runner -y
sudo gitlab-runner status   # debe mostrar "running"
```

### 3. Registrar el runner

```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.com" \
  --registration-token "PEGA_TU_TOKEN" \
  --description "mi-runner-docker" \
  --executor "docker" \
  --docker-image "alpine:latest" \
  --docker-volumes "/cache" \
  --tag-list "docker,linux" \
  --run-untagged="true"
```

### 4. Verificar la configuración generada

```toml
# /etc/gitlab-runner/config.toml  (fragmento relevante)
[[runners]]
  name = "mi-runner-docker"
  url = "https://gitlab.com"
  executor = "docker"
  [runners.docker]
    tls_verify = false
    image = "alpine:latest"
    privileged = false          # true solo si necesitas Docker-in-Docker
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache"]
    shm_size = 0
```

### 5. Comprobar que GitLab lo ve

En GitLab: Proyecto/Grupo → Settings → CI/CD → Runners. Aparecerá con un punto verde cuando esté online.

### 6. Job de prueba

```yaml
# .gitlab-ci.yml
smoke-test:
  stage: test
  tags:
    - docker
  image: alpine:latest
  script:
    - echo "Runner funcionando en $(hostname)"
    - uname -a
```

### Optimización: caché de imágenes Docker

Por defecto, el runner descarga la imagen Docker en cada job. Para proyectos con builds frecuentes, configura un volumen de caché o un registry mirror local para acelerar.

```toml
# En config.toml, dentro de [runners.docker]
pull_policy = ["if-not-present"]   # usa imagen local si ya existe; no descarga siempre
```

---

## ⚠️ Errores comunes

| Error | Causa probable | Solución |
|---|---|---|
| Job en `pending` indefinido | Ningún runner con los tags requeridos | Revisar tags del runner vs tags del job |
| `Cannot connect to Docker daemon` | `gitlab-runner` no tiene permisos Docker | `sudo usermod -aG docker gitlab-runner` + reiniciar servicio |
| Job falla con `image not found` | Imagen Docker del job no existe o mal escrita | Verificar el nombre/tag de la imagen en el YAML |
| Runner aparece offline en GitLab | Servicio parado o token inválido | `sudo gitlab-runner restart`; re-registrar si persiste |
| `privileged` requerido para Docker-in-Docker | El job lanza Docker dentro de Docker | Activar `privileged = true` en config.toml (con precaución de seguridad) |
| Minutos SaaS agotados | Cuota del plan alcanzada | Registrar runner propio o subir de plan |

---

## 🔧 Aplícalo a tus proyectos

**app web (Docker Compose, FastAPI + React):**
- Runner con executor Docker + tags `docker,linux`.
- En el pipeline: imagen `python:3.12` para tests de backend, `node:20` para build de frontend.
- Runner autoalojado para deploy en tu servidor local: el job puede hacer SSH o llamar a `docker compose up` directamente.

**proyecto embebido (PlatformIO / embedded):**
- Runner con executor **shell** en tu máquina de desarrollo donde está el toolchain de PlatformIO.
- Tags: `embedded,platformio`.
- Job de build: `pio run -e <environment>`; job de test: `pio test`.
- Ventaja: el runner tiene acceso al puerto USB/serie si necesitas flash automático.

---

## Conexiones

- [[MOC_GitLab]]
- [[05-gitlab-cicd-fundamentos]]
- [[07-cicd-avanzado]]
- [[03-repos-y-flujo-git]]
- [[MOC_Desarrollo_Software]]
