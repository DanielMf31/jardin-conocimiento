---
title: Container Registry, Package Registry y GitLab Pages
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/docker, programacion/ci-cd, programacion/packaging]
type: nota
status: en-progreso
source: claude-code
aliases: [gitlab-registry, gitlab-pages, container-registry]
---

# 📦 Container Registry, Package Registry y GitLab Pages

## ¿Por qué existen? El problema que resuelven

En un flujo DevOps moderno tienes tres necesidades de distribución que van más allá del código fuente:

1. **Imágenes Docker** — necesitas construirlas en CI y que tus servidores/K8s las descarguen de un lugar estable, sin depender de Docker Hub público.
2. **Librerías y dependencias internas** — si tu equipo produce paquetes npm, pip o Maven que otros proyectos consumen, necesitas un repositorio privado (como PyPI o npm registry, pero tuyo).
3. **Documentación o sitios estáticos** — quieres publicar la docs de tu API, un storybook de componentes o una web sencilla sin montar un servidor.

GitLab resuelve los tres desde el mismo lugar donde vive tu código. Esto no es solo comodidad: elimina el problema de autenticación cruzada entre servicios externos, y todos los artefactos quedan vinculados al proyecto que los genera.

---

## 🐳 Container Registry — Registro Docker propio

### Qué es y dónde encaja

El **Container Registry** de GitLab es un registro OCI (Open Container Initiative) por proyecto. Funciona exactamente como Docker Hub, pero privado y ligado a tu proyecto. Cada proyecto tiene su propia URL de registro con la forma:

```
registry.gitlab.com/<namespace>/<proyecto>
# Ejemplo:
registry.gitlab.com/mi-empresa/app-backend
```

Si usas GitLab autoalojado (ver [[10-autoalojamiento]]), la URL base cambia a tu dominio, pero el concepto es idéntico.

### Por qué no usar Docker Hub directamente

| Criterio | Docker Hub (gratis) | GitLab Container Registry |
|---|---|---|
| Privacidad | Solo 1 repo privado gratis | Ilimitado, privado por defecto |
| Autenticación en CI | Credencial externa adicional | Usa `$CI_REGISTRY_*` automáticamente |
| Rate limiting | Sí (100 pulls/6h sin login) | No (en tu instancia) |
| Versionado ligado a commit | Manual | Automático con variables CI |
| Escaneo de vulnerabilidades | Pago | Incluido en GitLab Ultimate / parcial en Free |

### Variables CI predefinidas que debes conocer

GitLab inyecta estas variables en cada pipeline sin configuración adicional:

| Variable | Valor |
|---|---|
| `CI_REGISTRY` | `registry.gitlab.com` (o tu dominio) |
| `CI_REGISTRY_IMAGE` | URL completa del registro de este proyecto |
| `CI_REGISTRY_USER` | Usuario para autenticar (`gitlab-ci-token`) |
| `CI_REGISTRY_PASSWORD` | Token efímero de la pipeline actual |

### Build y push desde `.gitlab-ci.yml`

```yaml
# .gitlab-ci.yml — ejemplo completo de build y push de imagen Docker

stages:
  - build
  - deploy

variables:
  # Tag de imagen: usa el SHA del commit para trazabilidad exacta
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  # Tag "latest" apuntando siempre a la rama principal
  IMAGE_LATEST: $CI_REGISTRY_IMAGE:latest

build-image:
  stage: build
  image: docker:24          # Imagen base que tiene el cliente Docker
  services:
    - docker:24-dind         # "Docker in Docker" — el daemon que ejecuta los builds
  before_script:
    # Login al registro usando las variables automáticas de GitLab
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
  script:
    # Construye la imagen usando el Dockerfile del repo
    - docker build -t "$IMAGE_TAG" -t "$IMAGE_LATEST" .
    # Sube ambos tags al registro
    - docker push "$IMAGE_TAG"
    - docker push "$IMAGE_LATEST"
  rules:
    # Solo hace push en la rama main; en ramas de feature solo construye (sin push)
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

> **Nota sobre Docker-in-Docker (dind):** requiere que el runner tenga el executor `docker` y, en algunos entornos, privilegios elevados. En runners compartidos de GitLab.com funciona out-of-the-box. Ver [[06-runners]] para configuración de runners.

### Estrategia de tags recomendada

```yaml
variables:
  # Para producción: tag inmutable basado en el tag git (v1.2.3)
  IMAGE_RELEASE: $CI_REGISTRY_IMAGE:$CI_COMMIT_TAG

  # Para staging: basado en nombre de rama (feature-login)
  IMAGE_BRANCH: $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG

  # Para desarrollo: SHA corto
  IMAGE_SHA: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
```

Regla general: **nunca uses `latest` como único tag en producción**. `latest` muta; si algo falla, no sabes qué imagen tenías desplegada. Usa SHA o tag semántico como tag primario.

### Pull desde otro proyecto o servidor externo

Para descargar la imagen desde un servidor de producción o desde otra pipeline necesitas un **Deploy Token** o un **Project Access Token** con scope `read_registry`:

```bash
docker login registry.gitlab.com -u <deploy-token-username> -p <deploy-token>
docker pull registry.gitlab.com/mi-empresa/app-backend:v1.2.3
```

En Kubernetes, esto se convierte en un `imagePullSecret`. GitLab tiene documentación específica para integración con K8s.

### Errores comunes

- **`denied: access forbidden`** en CI: faltó el paso `docker login` en `before_script`, o la variable `$CI_REGISTRY_PASSWORD` no tiene permiso (raro en GitLab.com, más frecuente en autoalojado mal configurado).
- **Imagen no encontrada desde producción**: el servidor intenta hacer pull antes de que la pipeline haya hecho push; revisa el orden de los stages.
- **Registry lleno**: en instancias propias hay límite de espacio. Configura **Cleanup Policies** (Settings → Packages & Registries → Clean up image tags) para borrar tags antiguos automáticamente.

---

## 📚 Package Registry — Librerías internas

### Qué problema resuelve

Cuando escribes una librería interna (por ejemplo, un SDK para tu API, o una librería de componentes UI), necesitas distribuirla a otros proyectos sin copiar archivos manualmente. El **Package Registry** de GitLab actúa como tu propio PyPI, npm registry o Maven Central, pero privado.

### Formatos soportados

| Formato | Para qué | Comando de consumo |
|---|---|---|
| npm | JavaScript / Node.js | `npm install @scope/paquete` |
| PyPI | Python | `pip install mi-libreria` |
| Maven / Gradle | Java / Kotlin | `<dependency>` en pom.xml |
| NuGet | .NET / C# | `dotnet add package ...` |
| Helm | Charts de Kubernetes | `helm install` |
| Generic | Binarios arbitrarios (firmware, zips) | Descarga por URL |

### Publicar un paquete Python desde CI

```yaml
publish-python-package:
  stage: deploy
  image: python:3.11
  script:
    # Construye la distribución (wheel + sdist)
    - pip install build twine
    - python -m build
    # Sube al Package Registry usando autenticación CI
    # TWINE_* son variables de entorno que entiende twine
    - TWINE_PASSWORD=$CI_JOB_TOKEN
      TWINE_USERNAME=gitlab-ci-token
      python -m twine upload
        --repository-url $CI_API_V4_URL/projects/$CI_PROJECT_ID/packages/pypi
        dist/*
  rules:
    - if: $CI_COMMIT_TAG   # Solo publica cuando hay un tag de versión
```

### Consumir el paquete en otro proyecto

```toml
# pip.conf o en pyproject.toml
[global]
index-url = https://gitlab.com/api/v4/projects/<PROJECT_ID>/packages/pypi/simple
extra-index-url = https://pypi.org/simple/  # fallback a PyPI público
```

Para autenticación, usa un **Deploy Token** con scope `read_package_registry` y pásalo como `--extra-index-url https://deploy-token-name:TOKEN@gitlab.com/...`.

### Dependency Proxy — caché de imágenes públicas

El **Dependency Proxy** (disponible en GitLab Free a nivel de grupo) actúa como proxy y caché para Docker Hub. En vez de que cada pipeline descargue `python:3.11` directamente de Docker Hub (con rate limiting), lo descarga de GitLab que lo tiene en caché:

```yaml
# En lugar de:
image: python:3.11

# Usa el proxy de tu grupo:
image: ${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}/python:3.11
```

La variable `CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX` la inyecta GitLab automáticamente. Solo necesitas activar el Dependency Proxy en Settings del grupo.

**Beneficio real**: si tus runners hacen 50 pipelines al día, evitas 50 pulls a Docker Hub y eliminas el rate limiting. En grupos grandes el ahorro de tiempo es notable.

---

## 🌐 GitLab Pages — Hosting de sitios estáticos

### Qué es y cuándo usarlo

**GitLab Pages** publica cualquier carpeta de archivos estáticos (HTML, CSS, JS) generada durante la pipeline en una URL pública (o privada). No hay servidor que mantener; GitLab sirve los archivos.

**Casos de uso típicos:**
- Documentación de una librería (Sphinx, MkDocs, Docusaurus)
- Storybook de componentes UI
- Reportes de cobertura de tests
- Portfolio o landing page sencilla

**Cuándo NO es adecuado:**
- Si necesitas backend dinámico (usa un servidor real o serverless)
- Si el sitio tiene millones de visitas (Pages no es un CDN de producción)
- Si quieres control total sobre cabeceras HTTP, redirects complejos, etc.

### Estructura del job en `.gitlab-ci.yml`

La única regla que impone GitLab Pages es que el job se llame exactamente `pages` y que el contenido final esté en una carpeta llamada `public/`.

```yaml
# .gitlab-ci.yml — publicar docs MkDocs en GitLab Pages

stages:
  - build
  - pages

build-docs:
  stage: build
  image: python:3.11
  script:
    - pip install mkdocs mkdocs-material
    # MkDocs genera el sitio en la carpeta 'site/' por defecto
    - mkdocs build --site-dir public
  artifacts:
    paths:
      - public/         # GitLab Pages buscará exactamente esta carpeta

# El job DEBE llamarse 'pages' — este es el nombre mágico que activa Pages
pages:
  stage: pages
  script:
    - echo "Publicando Pages..."  # El trabajo real ya está en los artifacts
  artifacts:
    paths:
      - public/
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH  # Solo desde main
```

Versión más compacta cuando no necesitas separar stages:

```yaml
pages:
  image: python:3.11
  script:
    - pip install mkdocs-material
    - mkdocs build --site-dir public
  artifacts:
    paths:
      - public/
  only:
    - main
```

### URL resultante

En GitLab.com:
```
https://<namespace>.gitlab.io/<proyecto>/
```

En GitLab autoalojado, depende de la configuración del administrador (ver [[10-autoalojamiento]] y [[11-administracion-backups-upgrades]]).

### Dominio personalizado

Puedes apuntar tu dominio propio (ej: `docs.mi-empresa.com`) desde Settings → Pages → New Domain. GitLab gestiona el certificado TLS automáticamente vía Let's Encrypt.

### Control de acceso a Pages

Por defecto, Pages es público. Puedes hacerlo privado (acceso solo a miembros del proyecto) desde Settings → General → Visibility → Pages Access Control → "Only project members".

---

## 🔗 Cómo encajan los tres en una pipeline real

```yaml
# Pipeline completa: test → build imagen → publicar docs → publicar paquete

stages:
  - test
  - build
  - publish
  - pages

run-tests:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements-dev.txt
    - pytest --cov=src --cov-report=html:public/coverage
  artifacts:
    paths:
      - public/coverage/   # El reporte de cobertura irá a Pages

build-docker:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
  script:
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"

publish-package:
  stage: publish
  image: python:3.11
  script:
    - pip install build twine
    - python -m build
    - TWINE_PASSWORD=$CI_JOB_TOKEN TWINE_USERNAME=gitlab-ci-token
      python -m twine upload
        --repository-url $CI_API_V4_URL/projects/$CI_PROJECT_ID/packages/pypi
        dist/*
  rules:
    - if: $CI_COMMIT_TAG

pages:
  stage: pages
  script:
    - echo "Publicando cobertura en Pages"
  artifacts:
    paths:
      - public/
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

---

## 🛠 Aplícalo a tus proyectos

**app web (FastAPI + React):**
- Container Registry: construye y pushea la imagen del backend FastAPI en cada merge a main. Tu `docker-compose.yml` en producción la consume con `image: registry.gitlab.com/...` en vez de hacer build local.
- Pages: publica la cobertura de tests del backend (`pytest-cov --cov-report html`) como sitio estático. Útil para seguimiento sin tener que correr tests localmente.

**proyecto embebido (PlatformIO/C++):**
- Package Registry (Generic): sube el firmware compilado (`.bin`, `.elf`) como artefacto versionado. Así mantienes un historial de firmwares flasheados ligado al tag de git.
- Pages: publica la documentación Doxygen generada automáticamente en cada release.

**Librería interna compartida:**
- Si algún día extraes lógica común (por ejemplo, parsers de datos de sensores), publícala en Package Registry (PyPI o npm) y consúmela desde múltiples proyectos sin copiar código.

---

## ⚠️ Errores comunes y sus causas

| Error | Causa más probable | Solución |
|---|---|---|
| `denied: access forbidden` al pushear imagen | Falta `docker login` o runner sin permisos | Añadir `before_script` con login |
| Pages no actualiza tras pipeline exitosa | Job no se llama exactamente `pages` | Renombrar el job |
| `404` al instalar paquete pip interno | URL del índice incorrecta o token sin scope | Verificar PROJECT_ID y scope del token |
| Imagen Docker Hub bloqueada por rate limit | Pulls directos sin Dependency Proxy | Activar Dependency Proxy en el grupo |
| Carpeta `public/` vacía en Pages | Artifact path mal configurado o build falla silenciosamente | Revisar artifacts y log del build |

---

## Conexiones

- [[MOC_GitLab]]
- [[01-que-es-gitlab]]
- [[05-gitlab-cicd-fundamentos]]
- [[06-runners]]
- [[07-cicd-avanzado]]
- [[10-autoalojamiento]]
- [[11-administracion-backups-upgrades]]
- [[MOC_Desarrollo_Software]]
