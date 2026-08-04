---
title: GitLab CI/CD — Fundamentos
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/cicd, programacion/yaml, programacion/docker]
type: nota
status: en-progreso
source: claude-code
aliases: [gitlab-cicd, ci-cd-gitlab, pipeline-gitlab]
---

# GitLab CI/CD — Fundamentos

## ¿Por qué existe CI/CD?

Sin automatización, el ciclo de vida del código es manual y frágil:

1. Desarrollador escribe código
2. Lo sube al repo
3. **Alguien** (¿quién?) ejecuta tests
4. **Alguien** empaqueta el binario/imagen
5. **Alguien** lo despliega al servidor

Este "alguien" es error-prone, lento y no repetible. Si el equipo crece, el caos escala.

**CI (Continuous Integration)** resuelve el paso 2-3: cada `git push` ejecuta tests automáticamente — todos saben en minutos si el código está roto.

**CD (Continuous Delivery/Deployment)** resuelve el paso 4-5: el pipeline empaqueta y despliega sin intervención manual (o con un click de aprobación).

GitLab CI/CD integra todo esto **dentro del mismo repositorio**, sin herramientas externas como Jenkins. La lógica del pipeline vive junto al código que automatiza.

---

## Panorama: dónde encaja en GitLab

```
git push
    │
    ▼
GitLab detecta .gitlab-ci.yml
    │
    ▼
Pipeline creado  ──► Runner lo ejecuta
    │
    ├── Stage: build   → Job: compile, Job: docker-build
    ├── Stage: test    → Job: unit-tests, Job: lint
    └── Stage: deploy  → Job: deploy-staging
```

El Runner es el proceso que **ejecuta el trabajo real** (ver [[06-runners]]). El archivo `.gitlab-ci.yml` es la **declaración** de qué hacer y cuándo.

---

## El archivo `.gitlab-ci.yml`

### Por qué en la raíz del repo

El pipeline es **código** — vive en el repo junto al proyecto, se versiona con Git, se revisa en Merge Requests, y cada rama puede tener su propia variante. No hay configuración escondida en un panel de administración.

### Estructura mínima

```yaml
# .gitlab-ci.yml en la raíz del repositorio

stages:          # Orden de ejecución de etapas
  - build
  - test
  - deploy

mi-primer-job:   # Nombre del job (arbitrario, debe ser único)
  stage: build   # A qué etapa pertenece
  script:        # Comandos a ejecutar (lista de strings)
    - echo "Hola pipeline"
    - echo "Rama: $CI_COMMIT_BRANCH"
```

---

## Conceptos clave: PIPELINE, STAGES, JOBS

### Pipeline

Una **ejecución completa** del archivo `.gitlab-ci.yml`, disparada por un evento (push, MR, schedule, etc.). Tiene un ID único (`#123`) y un estado global (passed / failed / canceled).

### Stages (etapas)

Grupos ordenados de jobs. Todos los jobs de un stage corren **en paralelo** (si hay runners disponibles). El siguiente stage solo empieza cuando **todos** los jobs del anterior han pasado.

```
Stage build  ──[parallel]──►  job A  +  job B
                                         │
                                         ▼ (si ambos pasan)
Stage test   ──[parallel]──►  job C  +  job D
```

### Jobs

La unidad mínima de trabajo. Cada job:
- Tiene un `stage` asignado
- Ejecuta uno o más `script` commands
- Corre en un entorno limpio (contenedor Docker o VM)
- Tiene su propio estado: passed / failed / skipped / canceled

> **Analogia hardware**: si el pipeline es un proceso de fabricación (línea de montaje), los stages son las estaciones y los jobs son las operaciones dentro de cada estación.

---

## La clave `script`

El corazón de cada job. Lista de comandos shell ejecutados en orden. Si **cualquier comando devuelve código distinto de 0**, el job falla y el pipeline se detiene (por defecto).

```yaml
test-unitarios:
  stage: test
  script:
    - pip install -r requirements.txt   # Paso 1
    - pytest tests/ -v                  # Paso 2 — si falla aquí, para
    - echo "Tests completados"          # Paso 3 — solo si paso 2 pasó
```

Variantes útiles:

```yaml
  script:
    - comando-que-puede-fallar || true   # Ignorar fallo de este comando
    - |                                  # Bloque multilínea (pipe)
        if [ "$CI_COMMIT_BRANCH" = "main" ]; then
          echo "En rama principal"
        fi
```

---

## Imagen Docker por job (`image:`)

Cada job corre en un contenedor Docker. Puedes definir la imagen **globalmente** o **por job**. Esto es poder real: cada job tiene exactamente las herramientas que necesita, sin conflictos.

```yaml
# Imagen global por defecto
default:
  image: ubuntu:22.04

build-python:
  stage: build
  image: python:3.11-slim     # Sobreescribe la global para este job
  script:
    - pip install -r requirements.txt
    - python -m build

build-node:
  stage: build
  image: node:20-alpine        # Otro job, otra imagen, mismo stage
  script:
    - npm ci
    - npm run build

test-rust:
  stage: test
  image: rust:1.78             # Sin conflicto con Python o Node
  script:
    - cargo test
```

> **Por qué es importante**: en un entorno sin Docker (como un runner shell), tendrías que instalar Python, Node y Rust en la misma máquina y gestionar versiones. Con Docker, cada job trae su propio entorno.

---

## Variables

### Variables predefinidas de GitLab

GitLab inyecta automáticamente decenas de variables en cada job. Las más útiles:

| Variable | Qué contiene |
|---|---|
| `$CI_COMMIT_BRANCH` | Nombre de la rama actual (`main`, `feature/x`) |
| `$CI_COMMIT_SHA` | Hash completo del commit (40 chars) |
| `$CI_COMMIT_SHORT_SHA` | Hash corto (8 chars) — útil para tags de imagen |
| `$CI_PROJECT_NAME` | Nombre del proyecto |
| `$CI_PROJECT_URL` | URL completa del proyecto |
| `$CI_PIPELINE_ID` | ID numérico del pipeline |
| `$CI_JOB_NAME` | Nombre del job actual |
| `$CI_ENVIRONMENT_NAME` | Nombre del environment (si se define) |
| `$CI_REGISTRY` | URL del Container Registry de GitLab |
| `$CI_REGISTRY_USER` | Usuario para autenticarse en el registry |
| `$CI_REGISTRY_PASSWORD` | Token de acceso al registry |
| `$CI_DEFAULT_BRANCH` | Rama por defecto del proyecto (`main`) |

```yaml
build-imagen:
  stage: build
  script:
    # Etiqueta la imagen con el hash corto del commit — trazabilidad perfecta
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA .
```

### Variables propias (definidas en el `.gitlab-ci.yml`)

```yaml
variables:                          # Nivel global — disponibles en todos los jobs
  APP_PORT: "8080"
  DOCKER_DRIVER: overlay2
  PYTHON_VERSION: "3.11"

test-unitarios:
  stage: test
  variables:                        # Nivel job — solo para este job
    LOG_LEVEL: debug
  script:
    - echo "Puerto: $APP_PORT"
    - echo "Log level: $LOG_LEVEL"
```

### Variables CI/CD (secretas) — Settings → CI/CD → Variables

Para credenciales, tokens, claves de API. **No se escriben en el `.gitlab-ci.yml`** — se configuran en la UI de GitLab y GitLab las inyecta en el entorno del job.

| Propiedad | Qué hace |
|---|---|
| **Masked** | El valor no aparece en los logs del pipeline (lo sustituye por `[MASKED]`) |
| **Protected** | Solo disponible en ramas/tags protegidos (no en feature branches) |
| **Expandable** | Permite referencias a otras variables dentro del valor |

```yaml
# En el job, las usas igual que cualquier variable
deploy-produccion:
  stage: deploy
  script:
    # DEPLOY_TOKEN viene de CI/CD Variables, no del .gitlab-ci.yml
    - curl -H "Authorization: Bearer $DEPLOY_TOKEN" https://api.ejemplo.com/deploy
```

> **Regla de oro**: si el valor es secreto, va en CI/CD Variables con Masked=true. Nunca hardcodes una contraseña en el `.gitlab-ci.yml` — ese archivo es público (o al menos versionado y visible a todos los que tienen acceso al repo).

---

## Artifacts vs Cache

Esta distinción confunde a todo el mundo al principio.

### Diferencia conceptual

| | Artifacts | Cache |
|---|---|---|
| **Propósito** | Pasar archivos **entre stages** / descargar resultados | Acelerar el pipeline reutilizando dependencias |
| **Quién lo usa** | Jobs downstream del pipeline actual + usuario final | El mismo job en ejecuciones **futuras** |
| **Garantía** | Siempre disponible para jobs dependientes | Best-effort (puede no existir) |
| **Ejemplo típico** | Binario compilado, informe de tests, imagen | `node_modules/`, `.venv/`, caché de pip/cargo |
| **Cuándo expira** | Configurable (días), default 30 días | Configurable, se invalida por `key` |

### Artifacts — pasar archivos entre stages

```yaml
compile:
  stage: build
  script:
    - cargo build --release
    - cp target/release/mi-app ./mi-app-binario   # Copia al workspace
  artifacts:
    paths:
      - mi-app-binario      # Este archivo se sube a GitLab
    expire_in: 1 week       # Se borra después de 7 días

test-integracion:
  stage: test
  # GitLab descarga los artifacts de 'compile' automáticamente
  script:
    - ./mi-app-binario --test    # El binario ya está aquí
```

Puedes descargar los artifacts desde la UI de GitLab (pestaña pipeline → job → Download artifacts).

### Cache — acelerar dependencias

```yaml
test-python:
  stage: test
  image: python:3.11-slim
  cache:
    key: "$CI_COMMIT_BRANCH-pip"   # Clave única por rama
    paths:
      - .venv/                      # Cachea el entorno virtual
  script:
    - python -m venv .venv
    - source .venv/bin/activate
    - pip install -r requirements.txt   # Rápido si cache hit
    - pytest
```

> **Cuándo NO usar cache**: cuando el output tiene que ser determinista y reproducible (como en builds de producción). El cache puede enmascarar problemas de dependencias.

---

## Reglas de ejecución — `rules` y `only/except`

Por defecto, todos los jobs corren en cada pipeline. Las reglas permiten ejecutar jobs **condicionalmente**.

### `only/except` — sintaxis antigua (aún funcional, pero deprecada)

```yaml
deploy-prod:
  stage: deploy
  script: ./deploy.sh
  only:
    - main          # Solo corre en la rama 'main'
  except:
    - schedules     # Nunca en pipelines programados
```

### `rules` — sintaxis moderna y flexible (preferida)

`rules` evalúa condiciones en orden. La primera que coincide gana.

```yaml
deploy-staging:
  stage: deploy
  script: ./deploy-staging.sh
  rules:
    - if: '$CI_COMMIT_BRANCH == "develop"'    # Si es la rama develop
      when: on_success                          # Ejecutar si stage anterior pasó
    - if: '$CI_PIPELINE_SOURCE == "schedule"'  # Si es pipeline programado
      when: never                               # Nunca ejecutar
    - when: manual                             # En cualquier otro caso, manual

test-mr:
  stage: test
  script: pytest
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'  # Solo en MRs
```

### Valores de `when`

| Valor | Cuándo ejecuta |
|---|---|
| `on_success` | Si todos los jobs anteriores pasaron (default) |
| `on_failure` | Si algún job anterior falló (útil para notificaciones de error) |
| `always` | Siempre, sin importar el estado anterior |
| `manual` | Solo si alguien hace click en "Play" en la UI |
| `never` | Nunca (equivale a no definir el job en ese contexto) |
| `delayed` | Con un retraso configurable (`start_in: 30 minutes`) |

---

## Ejemplo completo comentado

Un pipeline real para una aplicación Python con Docker:

```yaml
# .gitlab-ci.yml — Pipeline completo: build → test → deploy

# ─── Variables globales ─────────────────────────────────────────────────────
variables:
  # Imagen Docker que construiremos; usa el registro de GitLab del proyecto
  IMAGE_NAME: $CI_REGISTRY_IMAGE
  # Tag único por commit — garantiza trazabilidad
  IMAGE_TAG: $CI_COMMIT_SHORT_SHA

# ─── Imagen por defecto ─────────────────────────────────────────────────────
default:
  image: docker:24.0               # Docker-in-Docker para builds de imagen
  services:
    - docker:24.0-dind             # Daemon Docker dentro del runner

# ─── Orden de stages ────────────────────────────────────────────────────────
stages:
  - build
  - test
  - deploy

# ═══════════════════════════════════════════════════════════════════════════
# STAGE: BUILD
# ═══════════════════════════════════════════════════════════════════════════

build-imagen:
  stage: build
  script:
    # Autenticarse en el Container Registry de GitLab
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    # Construir la imagen
    - docker build -t $IMAGE_NAME:$IMAGE_TAG .
    # También taggear como 'latest' si es la rama principal
    - |
      if [ "$CI_COMMIT_BRANCH" = "$CI_DEFAULT_BRANCH" ]; then
        docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest
        docker push $IMAGE_NAME:latest
      fi
    # Subir la imagen al registry
    - docker push $IMAGE_NAME:$IMAGE_TAG
  rules:
    # Solo construir en ramas (no en pipelines de tags, por ejemplo)
    - if: '$CI_COMMIT_BRANCH'

# ═══════════════════════════════════════════════════════════════════════════
# STAGE: TEST (corre en paralelo si hay runners disponibles)
# ═══════════════════════════════════════════════════════════════════════════

unit-tests:
  stage: test
  image: python:3.11-slim          # Imagen específica para este job
  cache:
    key: "$CI_COMMIT_BRANCH-pip"
    paths:
      - .venv/                     # Cachear dependencias Python
  script:
    - python -m venv .venv
    - source .venv/bin/activate
    - pip install -r requirements.txt
    - pytest tests/unit/ -v --junitxml=report.xml
  artifacts:
    when: always                   # Subir el reporte aunque los tests fallen
    reports:
      junit: report.xml            # GitLab parsea esto y muestra resultados en la UI
    expire_in: 1 week

lint:
  stage: test
  image: python:3.11-slim
  cache:
    key: "$CI_COMMIT_BRANCH-pip"
    paths:
      - .venv/
  script:
    - source .venv/bin/activate || python -m venv .venv && source .venv/bin/activate
    - pip install flake8 black
    - flake8 src/                  # Linter
    - black --check src/           # Verificar formato

# ═══════════════════════════════════════════════════════════════════════════
# STAGE: DEPLOY
# ═══════════════════════════════════════════════════════════════════════════

deploy-staging:
  stage: deploy
  image: alpine:3.18
  before_script:
    # Instalar herramientas necesarias para el despliegue
    - apk add --no-cache curl
  script:
    # Ejemplo: notificar a un servidor de staging via webhook
    # $STAGING_WEBHOOK viene de CI/CD Variables (masked)
    - |
      curl -X POST "$STAGING_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"image\": \"$IMAGE_NAME:$IMAGE_TAG\"}"
    - echo "Desplegado $IMAGE_TAG a staging"
  environment:
    name: staging                  # Crea un 'Environment' rastreable en GitLab
    url: https://staging.ejemplo.com
  rules:
    # Solo en develop, automáticamente
    - if: '$CI_COMMIT_BRANCH == "develop"'
      when: on_success

deploy-produccion:
  stage: deploy
  image: alpine:3.18
  script:
    - echo "Desplegando $IMAGE_TAG a producción..."
    - curl -X POST "$PROD_WEBHOOK" -d "{\"image\": \"$IMAGE_NAME:$IMAGE_TAG\"}"
  environment:
    name: production
    url: https://app.ejemplo.com
  rules:
    # Solo en main, con aprobación manual (no automático)
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: manual
      allow_failure: false          # El pipeline no pasa hasta que alguien aprueba
```

---

## Errores comunes

| Error | Causa habitual | Solución |
|---|---|---|
| `No stages defined` | El archivo `.gitlab-ci.yml` tiene errores de sintaxis o está vacío | Usar el CI Lint integrado en GitLab (CI/CD → Editor → Validate) |
| Job falla con `command not found` | La imagen Docker no tiene el comando instalado | Cambiar la imagen o añadir instalación en `before_script` |
| Cache no funciona | El runner no tiene caché configurado o la `key` cambió | Verificar la configuración del runner y la key del cache |
| Artifact no encontrado en job downstream | El job que genera el artifact falló | Revisar si el job upstream pasó; considerar `dependencies: []` |
| Variable masked aparece en logs | Se usa en un contexto donde GitLab no puede mascarar (ej: dentro de un archivo) | Aceptarlo o restructurar para que no se imprima |
| `docker: command not found` | El runner no tiene Docker o falta `services: docker:dind` | Añadir la imagen `docker:XX` y el service `docker:dind` |
| Pipeline no se dispara en MR | Las `rules` no incluyen `merge_request_event` | Añadir `if: '$CI_PIPELINE_SOURCE == "merge_request_event"'` |

---

## `before_script` y `after_script`

Comandos que corren antes o después del `script` principal de cada job.

```yaml
default:
  before_script:
    - echo "Inicio de job: $CI_JOB_NAME"   # Ejecuta en TODOS los jobs

build:
  stage: build
  before_script:
    - apt-get update -qq               # Sobreescribe el before_script global
    - apt-get install -y build-tools
  script:
    - make build
  after_script:
    - echo "Job terminado con estado: $CI_JOB_STATUS"  # Siempre corre, incluso si falla
```

---

## Aplícalo a tus proyectos

### app web (FastAPI + React + Docker)

```yaml
stages: [build, test, deploy]

build-backend:
  stage: build
  image: docker:24.0
  services: [docker:dind]
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHORT_SHA ./backend
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHORT_SHA

test-backend:
  stage: test
  image: python:3.11-slim
  script:
    - pip install -r backend/requirements.txt
    - pytest backend/tests/ -v
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
```

### proyecto embebido (PlatformIO / C++)

```yaml
build-firmware:
  stage: build
  image: python:3.11
  before_script:
    - pip install platformio
  script:
    - pio run -e esp32dev        # Compilar para el target definido
  artifacts:
    paths:
      - .pio/build/esp32dev/firmware.bin   # Guardar el binario
    expire_in: 30 days
```

---

## Conexiones

- [[MOC_GitLab]]
- [[01-que-es-gitlab]]
- [[03-repos-y-flujo-git]]
- [[04-merge-requests-y-code-review]]
- [[06-runners]]
- [[07-cicd-avanzado]]
- [[08-registry-paquetes-y-pages]]
- [[MOC_Desarrollo_Software]]
