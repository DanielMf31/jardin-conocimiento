---
title: CI/CD Avanzado en GitLab
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/cicd, programacion/automatizacion]
type: nota
status: en-progreso
source: claude-code
aliases: [cicd avanzado, gitlab cd, gitlab pipelines avanzado]
---

# CI/CD Avanzado en GitLab

## Por qué existe esto (el problema que resuelve)

El documento [[05-gitlab-cicd-fundamentos]] cubre el bucle básico: **commit → test → build → notificación**. Eso es CI (Integración Continua). Pero CI sin CD es como un taller que inspecciona las piezas pero nunca monta el producto.

CD — Continuous Delivery o Continuous Deployment — cierra el ciclo:

- **Continuous Delivery**: el pipeline lleva el artefacto hasta un punto donde *podría* desplegarse con un clic humano.
- **Continuous Deployment**: el pipeline despliega automáticamente en producción si todos los gates pasan.

Los temas de este documento son las piezas que hacen ese salto posible y fiable:

| Concepto | Para qué sirve |
|---|---|
| Environments | Modelar staging/prod dentro de GitLab |
| Review Apps | Entorno efímero por cada MR |
| `needs` / DAG | Pipelines no lineales, más rápidos |
| `include` + templates | Reutilizar YAML entre proyectos |
| Child/multi-project pipelines | Coordinar repositorios independientes |
| `when: manual` | Gates humanos en el flujo |
| Pipeline schedules | Cron dentro de GitLab |
| Auto DevOps | Convención sobre configuración |

---

## Environments y Deployments

### El concepto

Un **environment** (entorno) en GitLab es un nombre simbólico que representa *dónde* corre tu aplicación: `staging`, `production`, `review/MR-42`, etc. GitLab lo usa para:

- Mostrar un historial de despliegues por entorno (quién desplegó, cuándo, qué commit).
- Activar protecciones (solo ciertos usuarios pueden desplegar a `production`).
- Generar URLs de acceso directo desde la UI.

### Cómo declararlo

```yaml
deploy-staging:
  stage: deploy
  script:
    - ./deploy.sh $STAGING_HOST
  environment:
    name: staging
    url: https://staging.miapp.com   # aparece como botón en la UI
```

```yaml
deploy-prod:
  stage: deploy
  script:
    - ./deploy.sh $PROD_HOST
  environment:
    name: production
    url: https://miapp.com
  # Solo se puede ejecutar si el entorno está protegido y el usuario tiene permiso
```

### Entornos protegidos

En **Settings → CI/CD → Protected environments** puedes exigir que solo roles específicos (Maintainer, Owner) puedan aprobar despliegues a `production`. Esto es el equivalente a una llave de seguridad física: el pipeline puede llegar hasta ahí, pero alguien con autoridad debe aprobar.

---

## Review Apps (entornos efímeros por MR)

### El problema que resuelven

Con CI básico, el revisor de un MR ve código y resultados de tests. Para verificar que la *interfaz* o el *comportamiento* funcionan, tiene que hacer checkout en local. Las Review Apps automatizan esto: **cada MR levanta su propio entorno temporal**, accesible por URL, que se destruye al mergear o cerrar el MR.

### Flujo típico

```
push a rama feature → pipeline se activa →
  job "deploy-review" despliega en subdominio review/MR-55.miapp.com →
  MR muestra botón "View App" →
revisor hace clic, ve la app funcionando →
MR mergeado → job "stop-review" borra el entorno
```

### YAML con ciclo de vida completo

```yaml
deploy-review:
  stage: deploy
  script:
    - kubectl apply -f k8s/review/  # o docker run, heroku deploy, etc.
    - echo "APP_URL=https://review-${CI_MERGE_REQUEST_IID}.miapp.com" >> deploy.env
  environment:
    name: review/$CI_COMMIT_REF_SLUG   # nombre único por rama
    url: https://review-${CI_MERGE_REQUEST_IID}.miapp.com
    on_stop: stop-review               # qué job limpia el entorno
  artifacts:
    reports:
      dotenv: deploy.env               # expone APP_URL a jobs posteriores
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

stop-review:
  stage: deploy
  script:
    - kubectl delete namespace review-${CI_MERGE_REQUEST_IID}
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    action: stop                       # marca este job como el destructor
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: manual                     # o cuando: on_stop se activa automáticamente
```

**Variables CI útiles aquí:**
- `CI_MERGE_REQUEST_IID`: número del MR (único por proyecto).
- `CI_COMMIT_REF_SLUG`: nombre de rama sanitizado (sin slashes, sin espacios).

---

## `needs` y DAG (pipelines no secuenciales)

### El problema

El modelo por defecto de GitLab CI es de **stages secuenciales**: todos los jobs del stage `test` terminan antes de que empiece cualquier job del stage `deploy`. Esto es simple pero desperdicia tiempo: si `build-backend` termina en 2 min y `build-frontend` tarda 8 min, el deploy del backend espera 6 minutos innecesarios.

### DAG: Directed Acyclic Graph

Con `needs`, le dices a un job exactamente de qué otros jobs depende, ignorando los stages. GitLab construye un grafo de dependencias (DAG) y ejecuta cada job tan pronto como sus dependencias directas terminan.

```yaml
stages:
  - build
  - test
  - deploy

build-backend:
  stage: build
  script: make build-backend

build-frontend:
  stage: build
  script: make build-frontend

test-backend:
  stage: test
  needs: [build-backend]   # no espera a build-frontend
  script: pytest

test-frontend:
  stage: test
  needs: [build-frontend]  # no espera a build-backend
  script: npm test

deploy-backend:
  stage: deploy
  needs: [test-backend]    # parte en cuanto test-backend pasa
  script: ./deploy-backend.sh

deploy-frontend:
  stage: deploy
  needs: [test-frontend]
  script: ./deploy-frontend.sh
```

**Resultado**: backend y frontend corren en paralelo completo, cada uno con su propio tren de test→deploy. El pipeline total puede pasar de 20 min a 10 min.

### Necesitar artefactos de otro job

```yaml
deploy-backend:
  stage: deploy
  needs:
    - job: build-backend
      artifacts: true      # descarga los artefactos de build-backend automáticamente
  script: ./deploy.sh dist/backend.tar.gz
```

### Cuándo NO usar `needs`

- Pipelines pequeños (< 5 jobs): la complejidad no compensa.
- Cuando el orden de stages es exactamente el correcto ya: no rompas lo que funciona.
- Si un job necesita que *todos* los de un stage anterior pasen: usa stages normales.

---

## `include` y Templates (reutilizar configuración)

### El problema

Con un solo proyecto está bien tener todo en `.gitlab-ci.yml`. Con 10 proyectos, cada uno tiene su propio YAML con jobs de lint, security scan, y docker build casi idénticos. Un cambio en la política de seguridad implica editar 10 archivos.

### `include`: tipos disponibles

```yaml
include:
  # 1. Fichero local del mismo repo
  - local: '.gitlab/ci/test-jobs.yml'

  # 2. Fichero en otro proyecto GitLab (plantilla compartida del equipo)
  - project: 'mi-organizacion/ci-templates'
    ref: main
    file: '/templates/docker-build.yml'

  # 3. URL pública (útil para plantillas de terceros)
  - remote: 'https://example.com/ci-template.yml'

  # 4. Plantillas oficiales de GitLab
  - template: 'Security/SAST.gitlab-ci.yml'
```

### Plantilla compartida real

Archivo en `mi-organizacion/ci-templates:/templates/docker-build.yml`:

```yaml
# Plantilla: construye y empuja imagen Docker al registry del proyecto
.docker-build:        # el punto inicial hace que sea un "job oculto" (no se ejecuta solo)
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_DRIVER: overlay2
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:latest
```

Uso en el proyecto que consume la plantilla:

```yaml
include:
  - project: 'mi-organizacion/ci-templates'
    ref: main
    file: '/templates/docker-build.yml'

build-image:
  extends: .docker-build    # hereda todo, puedes sobreescribir lo que necesites
  variables:
    DOCKER_BUILDKIT: "1"    # añades tu variable, el resto viene de la plantilla
```

### `extends` vs `!reference` vs anchors YAML

| Mecanismo | Qué hace | Cuándo usarlo |
|---|---|---|
| `extends` | Herencia de jobs completos con merge profundo | Reutilizar jobs entre proyectos (con `include`) |
| `!reference` | Referencia a una clave específica de otro job | Compartir `script` o `before_script` sin heredar todo |
| Anchors YAML (`&`, `*`) | Alias dentro del mismo fichero | Reutilización local simple sin `include` |

```yaml
# !reference ejemplo: tomar solo el script de otro job
.login-script:
  script:
    - docker login ...

build:
  script:
    - !reference [.login-script, script]   # inserta el script de .login-script
    - docker build .
```

---

## Child Pipelines y Multi-Project Pipelines

### Child Pipelines (mismo repo, YAML separado)

Útil cuando tienes un monorepo con varios componentes independientes. El pipeline padre detecta qué cambió y dispara solo el child pipeline relevante.

```yaml
# .gitlab-ci.yml (pipeline padre)
trigger-backend:
  trigger:
    include: backend/.gitlab-ci.yml   # fichero YAML del componente
    strategy: depend                  # el padre espera al child para marcar estado
  rules:
    - changes:
        - backend/**/*

trigger-frontend:
  trigger:
    include: frontend/.gitlab-ci.yml
    strategy: depend
  rules:
    - changes:
        - frontend/**/*
```

`strategy: depend` hace que el pipeline padre falle si el child falla. Sin él, el trigger es "fire and forget".

### Multi-Project Pipelines (repos distintos)

Cuando el despliegue de un servicio debe disparar el pipeline de otro repositorio (por ejemplo, el repo de infraestructura):

```yaml
deploy-infra:
  trigger:
    project: mi-org/infra-repo        # repo distinto
    branch: main
    strategy: depend
  variables:
    UPSTREAM_VERSION: $CI_COMMIT_SHA  # pasa información al pipeline disparado
```

**Caso de uso real**: tienes `api-repo` y `deploy-repo`. Cuando `api-repo` publica una nueva imagen Docker, dispara el pipeline de `deploy-repo` que aplica los manifiestos de Kubernetes.

---

## Jobs Manuales como Gates (`when: manual`)

### El concepto

Un gate es un punto de pausa deliberada en el pipeline. El pipeline llega hasta ese job y se detiene, esperando que un humano (con permisos) pulse "Ejecutar". Es la diferencia entre Continuous Delivery y Continuous Deployment:

- Con gate manual en producción → **Continuous Delivery** (entrega lista, humano decide cuándo).
- Sin gate → **Continuous Deployment** (automatización total).

```yaml
stages:
  - test
  - staging
  - production

deploy-staging:
  stage: staging
  script: ./deploy.sh staging
  environment:
    name: staging

deploy-production:
  stage: production
  script: ./deploy.sh production
  environment:
    name: production
  when: manual             # gate: el pipeline no avanza hasta que alguien pulse
  allow_failure: false     # si se omite, el pipeline queda en "bloqueado", no fallido
```

### Combinaciones útiles

```yaml
# Gate que solo aparece en rama main
deploy-production:
  when: manual
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

# Gate con protección adicional de entorno (doble llave)
# El job es manual Y el entorno production requiere aprobación de Maintainer
deploy-production:
  when: manual
  environment:
    name: production
```

### Cuándo usar gates manuales

- Despliegues a producción en equipos que aún no tienen confianza total en el pipeline.
- Pasos destructivos (migraciones de base de datos, cambios de esquema).
- Rollback: un job manual `rollback-production` siempre disponible.
- Auditoría: queda registro de quién ejecutó el gate y cuándo.

---

## Pipeline Schedules (Cron en GitLab)

### Qué son

GitLab puede disparar un pipeline completo según un horario cron, independientemente de commits. Útil para:

- Tests de regresión nocturnos (más lentos y exhaustivos que los de PR).
- Generación periódica de reportes.
- Limpieza de recursos (borrar imágenes viejas del registry).
- Auditorías de seguridad programadas.

### Configuración

En la UI: **CI/CD → Schedules → New schedule**. Defines:
- Expresión cron: `0 2 * * *` (cada noche a las 02:00 UTC).
- Rama objetivo.
- Variables extra (opcionales).

### Hacer que ciertos jobs solo corran en schedules

```yaml
heavy-regression-tests:
  script: pytest tests/regression/ -v
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"   # solo cuando lo dispara el cron
      when: always
    - when: never                             # nunca en pipelines normales

security-audit:
  script: trivy image $CI_REGISTRY_IMAGE:latest
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule" && $AUDIT_TYPE == "security"
```

La variable `AUDIT_TYPE` se puede pasar desde la configuración del schedule en la UI, permitiendo tener varios schedules distintos que disparan comportamientos diferentes.

---

## Auto DevOps

### Qué es

Auto DevOps es la apuesta de GitLab por **convención sobre configuración**: si no tienes `.gitlab-ci.yml`, GitLab activa automáticamente un pipeline predefinido que detecta el lenguaje del proyecto e intenta hacer build, test, security scan, y deploy sin que escribas nada.

### Qué hace por defecto

| Fase | Qué hace |
|---|---|
| Auto Build | Detecta lenguaje (Dockerfile o Heroku buildpacks) y construye imagen |
| Auto Test | Ejecuta tests detectados (pytest, jest, etc.) |
| Auto Code Quality | Análisis estático de calidad |
| Auto SAST | Escaneo de vulnerabilidades en código fuente |
| Auto Dependency Scanning | Vulnerabilidades en dependencias |
| Auto Container Scanning | CVEs en la imagen Docker |
| Auto Deploy | Despliega en Kubernetes (requiere cluster configurado) |
| Auto Review Apps | Activa review apps automáticamente en MRs |

### Cuándo tiene sentido

**SI** tienes un proyecto estándar (web app sin quirks), quieres empezar rápido, y trabajas con Kubernetes en GitLab.

**NO** si tu proyecto tiene un build personalizado, múltiples servicios, o ya tienes `.gitlab-ci.yml` propio — en ese caso Auto DevOps se desactiva automáticamente.

Se puede activar/desactivar por proyecto: **Settings → CI/CD → Auto DevOps**.

---

## Cómo pasar de CI a CD: la ruta práctica

El salto de CI (solo integración) a CD (despliegue real) es incremental. Esta es la secuencia recomendada:

```
Etapa 1 — CI sólido
   Tests pasan en pipeline
   Build de artefacto automatizado
   Artefacto guardado (registry, S3, etc.)

Etapa 2 — CD a staging automático
   Deploy a staging en cada merge a main
   Environment "staging" declarado en GitLab
   Smoke tests post-deploy (¿la app levanta?)

Etapa 3 — Review Apps
   Entorno efímero por MR
   Job stop-review configurado

Etapa 4 — CD a producción con gate manual
   Job deploy-production con when: manual
   Environment "production" protegido
   Historial de deployments visible en GitLab

Etapa 5 — CD a producción automático (Continuous Deployment)
   Confianza total en test suite y smoke tests
   Rollback automático configurado
   Métricas de producción monitorizadas
   Eliminar when: manual
```

**El gate manual es el seguro de aprendizaje**: empieza con él, retíralo cuando el equipo confíe en el pipeline.

### Checklist mínimo antes de eliminar el gate de producción

- [ ] Cobertura de tests > 80% en paths críticos
- [ ] Smoke tests post-deploy que verifican endpoints reales
- [ ] Estrategia de rollback (blue-green, canary, o `helm rollback`)
- [ ] Alertas de monitorización activas (si el deploy rompe algo, te enteras en < 5 min)
- [ ] Pipeline completo < 15 min (si tarda más, nadie confía en él)

---

## Errores comunes

| Error | Causa | Solución |
|---|---|---|
| `needs` rompe el pipeline | Job en `needs` no existe o está en stage posterior | Verifica nombres y stages |
| `include` no encuentra el fichero | Ruta incorrecta o permisos de acceso al repo | Usa ruta absoluta desde raíz del repo (`/templates/...`) |
| Review App no se borra | Falta `on_stop` o el job `stop` no tiene `action: stop` | Añade ambas claves |
| Child pipeline no falla el padre | `strategy: depend` ausente | Añade `strategy: depend` al trigger |
| Schedule no se ejecuta | Rama no existe o pipeline desactivado | Verifica rama y estado del schedule en la UI |
| Environment bloqueado | Solo Maintainer puede desplegar | Revisa Protected Environments o pide permiso |

---

## Aplícalo a tus proyectos

**app web (React + FastAPI + Docker):**
- Añade `needs` para que `test-backend` y `test-frontend` corran en paralelo sin esperar el uno al otro.
- Declara environments `staging` y `production` desde el primer día aunque el deploy sea manual — el historial de deployments es valioso.
- Review Apps con Docker Compose en una VPS de staging: cada MR levanta un stack en un puerto distinto (usa `$CI_MERGE_REQUEST_IID` como offset de puerto).
- Gate manual `deploy-production` mientras el proyecto es personal; retíralo si algún día hay equipo con CI maduro.

**proyecto embebido (PlatformIO / embebido):**
- Pipeline schedule nocturno para compilar todas las variantes de board y detectar regresiones de compilación.
- Jobs manuales para flashear firmware en hardware real (requiere runner con acceso a USB — ver [[06-runners]]).
- Multi-project pipeline si separas el firmware del dashboard de datos: el repo del firmware dispara el pipeline del repo de dashboard cuando hay nueva versión.

---

## Conexiones

- [[MOC_GitLab]]
- [[05-gitlab-cicd-fundamentos]]
- [[06-runners]]
- [[04-merge-requests-y-code-review]]
- [[08-registry-paquetes-y-pages]]
- [[03-repos-y-flujo-git]]
- [[MOC_Desarrollo_Software]]
