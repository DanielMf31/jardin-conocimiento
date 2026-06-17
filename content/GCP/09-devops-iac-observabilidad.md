---
title: DevOps, IaC y observabilidad en GCP
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/devops, programacion/iac, programacion/observabilidad, programacion/ci-cd]
type: nota
status: en-progreso
source: claude-code
aliases: [GCP DevOps, IaC GCP, Cloud Build, Cloud Monitoring]
---

# DevOps, IaC y observabilidad en GCP

## ¿Por qué importa este clúster?

En GCP puedes desplegar manualmente desde la consola... durante cinco minutos, hasta que necesitas reproducir el entorno en otro proyecto, auditar quién cambió qué, o detectar que un servicio lleva 20 minutos con latencia alta. Ahí entran tres disciplinas que se solapan:

| Disciplina | Pregunta que responde | Herramienta principal |
|---|---|---|
| **CI/CD** | ¿Cómo llega mi código a producción de forma fiable y repetible? | Cloud Build → Cloud Deploy |
| **IaC** | ¿Cómo defino mi infraestructura como código versionable? | Terraform / Config Connector |
| **Observabilidad** | ¿Qué está pasando ahora mismo en mi sistema? | Cloud Operations Suite |

Estas tres piezas forman el **loop de confianza DevOps**: el código entra limpio, la infraestructura es predecible, y el sistema avisa cuando algo falla antes de que lo note el usuario.

---

## CI/CD en GCP

### El problema que resuelve

Construir un binario o imagen Docker a mano en tu portátil introduce variables: versión de Python, variables de entorno locales, permisos. CI/CD mueve esa construcción a un entorno controlado y reproducible.

### Cloud Build — el motor de CI

**Cloud Build** ejecuta pasos (steps) definidos en un fichero YAML (`cloudbuild.yaml`). Cada step es un contenedor Docker que corre un comando. No hay servidor que mantener: es serverless y factura por minuto de CPU.

```yaml
# cloudbuild.yaml — ejemplo real
steps:
  - name: 'python:3.12-slim'
    entrypoint: pip
    args: ['install', '-r', 'requirements.txt', '-t', '.packages']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/mi-repo/mi-app:$COMMIT_SHA', '.']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/mi-repo/mi-app:$COMMIT_SHA']

substitutions:
  _REGION: us-central1

options:
  logging: CLOUD_LOGGING_ONLY
```

**Triggers**: Cloud Build puede arrancarse automáticamente con un push a GitHub, GitLab (via mirroring o webhook), o Pub/Sub. El trigger lee el `cloudbuild.yaml` del repo.

```bash
# Crear un trigger manual desde CLI
gcloud builds triggers create github \
  --repo-name=mi-repo \
  --repo-owner=mi-org \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --name=build-on-main
```

**Free tier**: 120 minutos de build al día en la máquina más pequeña (n1-standard-1). Para proyectos personales cubre bastante.

### Artifact Registry — dónde viven los artefactos

**Artifact Registry** (AR) es el sucesor de Container Registry. Guarda no solo imágenes Docker sino también paquetes Maven, npm, Python (PyPI), Helm charts, etc. Es el "almacén central de lo que se despliega".

```bash
# Crear repositorio Docker en AR
gcloud artifacts repositories create mi-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Imágenes de producción"

# Autenticar Docker contra AR
gcloud auth configure-docker us-central1-docker.pkg.dev

# Listar imágenes
gcloud artifacts docker images list us-central1-docker.pkg.dev/$PROJECT_ID/mi-repo
```

> Analogía AWS: AR equivale a **ECR** (Elastic Container Registry) pero con soporte multi-formato.

### Cloud Deploy — el motor de CD

**Cloud Deploy** gestiona la progresión de un artefacto (imagen, chart Helm) a través de un conjunto de **targets** (entornos: dev → staging → prod). Define un pipeline declarativo; tú promueves manualmente o apruebas despliegues.

```yaml
# clouddeploy.yaml
apiVersion: deploy.cloud.google.com/v1
kind: DeliveryPipeline
metadata:
  name: mi-pipeline
description: Pipeline app web
serialPipeline:
  stages:
  - targetId: dev
  - targetId: staging
    strategy:
      canary:
        runtimeConfig:
          cloudRun:
            automaticTrafficControl: true
        canaryDeployment:
          percentages: [25, 50, 75]
  - targetId: prod
    deployParameters:
    - values:
        replicas: "3"
```

```bash
# Crear release y desplegar en dev
gcloud deploy releases create release-$(date +%Y%m%d-%H%M) \
  --delivery-pipeline=mi-pipeline \
  --region=us-central1 \
  --images=mi-app=us-central1-docker.pkg.dev/$PROJECT_ID/mi-repo/mi-app:$TAG

# Promover de dev a staging
gcloud deploy releases promote \
  --release=RELEASE_NAME \
  --delivery-pipeline=mi-pipeline \
  --region=us-central1 \
  --to-target=staging
```

**Estrategias de despliegue** que soporta: recreate (baja todo, sube todo), canary (porcentaje progresivo), blue/green. Esto es crítico para producción sin downtime.

### Pipeline completo (diagrama conceptual)

```
GitHub/GitLab push
        │
        ▼
  Cloud Build Trigger
        │  (cloudbuild.yaml)
        ├─ lint / tests
        ├─ docker build
        └─ push → Artifact Registry
                      │
                      ▼
               Cloud Deploy
               dev → staging → prod
               (aprobación manual en prod)
```

---

## Infraestructura como Código (IaC)

### El problema que resuelve

Si creas recursos desde la consola, el siguiente que quiera replicar el entorno (tú mismo en 6 meses, un compañero, el CI de otro proyecto) no sabe exactamente qué creaste. IaC convierte la infraestructura en código versionable, revisable en PR y reproducible.

### Terraform en GCP

**Terraform** es la herramienta más usada para IaC multi-cloud. En GCP usa el **provider `google`** (y `google-beta` para features en preview).

```hcl
# main.tf — ejemplo mínimo
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "mi-proyecto-tfstate"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloud_run_v2_service" "api" {
  name     = "producto-api"
  location = var.region

  template {
    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/mi-repo/mi-app:latest"
      resources {
        limits = { memory = "512Mi", cpu = "1" }
      }
    }
  }
}

# Permitir acceso público al Cloud Run
resource "google_cloud_run_service_iam_member" "public" {
  service  = google_cloud_run_v2_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
```

```bash
# Flujo de trabajo estándar
terraform init          # descarga provider, inicializa backend
terraform plan          # muestra qué cambiará (DRY RUN)
terraform apply         # aplica los cambios
terraform destroy       # destruye todos los recursos (cuidado en prod)

# Ver estado actual
terraform state list
terraform state show google_cloud_run_v2_service.api
```

**Backend en GCS**: el estado de Terraform (`.tfstate`) debe vivir en un bucket GCS, no en local ni en el repo. Así varios desarrolladores comparten estado y hay bloqueo de concurrencia.

```bash
# Crear bucket para tfstate (una sola vez)
gsutil mb -l us-central1 gs://mi-proyecto-tfstate
gsutil versioning set on gs://mi-proyecto-tfstate
```

**Organización recomendada para un proyecto real**:

```
infra/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       └── terraform.tfvars
└── modules/
    ├── cloud-run/
    └── networking/
```

### Config Connector — IaC nativo de Kubernetes

**Config Connector** es un addon de GKE que permite gestionar recursos GCP como Custom Resources de Kubernetes (CRDs). Si ya usas GKE y kubectl, puedes crear un bucket GCS o una Cloud SQL con manifiestos YAML en lugar de Terraform.

```yaml
# Ejemplo: crear un bucket GCS con Config Connector
apiVersion: storage.cnrm.cloud.google.com/v1beta1
kind: StorageBucket
metadata:
  name: mi-bucket-config-connector
  namespace: default
spec:
  location: us-central1
  uniformBucketLevelAccess: true
```

**Cuándo usar Terraform vs Config Connector**:

| Criterio | Terraform | Config Connector |
|---|---|---|
| Ecosistema | Multi-cloud, cualquier stack | Solo si ya usas GKE |
| Curva de aprendizaje | Media (HCL) | Baja si conoces k8s |
| Estado | Fichero tfstate explícito | Gestionado por el operador k8s |
| Madurez / comunidad | Muy alta | Media |
| Caso de uso ideal | Proyecto nuevo, cualquier equipo | Equipo GKE-first |

Para la mayoría de proyectos: **Terraform**. Config Connector tiene su nicho en plataformas GKE con GitOps estricto.

---

## Observabilidad en GCP (Cloud Operations Suite)

### El modelo de los tres pilares

La observabilidad moderna se basa en tres señales complementarias:

| Pilar | Pregunta | Herramienta GCP |
|---|---|---|
| **Logs** | ¿Qué ocurrió exactamente? | Cloud Logging |
| **Métricas** | ¿Cuánto/cuándo? (números a lo largo del tiempo) | Cloud Monitoring |
| **Trazas** | ¿Por qué tardó tanto? (flujo entre servicios) | Cloud Trace |

Además: **Error Reporting** agrega automáticamente excepciones similares para que no ahogues en ruido.

### Cloud Logging

Recibe logs de todos los servicios GCP automáticamente (Cloud Run, GKE, Compute Engine, funciones...) y también acepta logs de aplicaciones vía **Cloud Logging API** o agente.

```bash
# Leer logs de Cloud Run en tiempo real (como tail -f)
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=producto-api" \
  --format="value(textPayload)"

# Buscar errores de las últimas 2 horas
gcloud logging read \
  'resource.type="cloud_run_revision" AND severity>=ERROR' \
  --limit=50 \
  --freshness=2h \
  --format=json
```

**Desde código (Python)**:

```python
import google.cloud.logging

client = google.cloud.logging.Client()
client.setup_logging()  # integra con logging estándar de Python

import logging
logging.warning("Este mensaje aparece en Cloud Logging")
```

**Log sinks**: puedes exportar logs a BigQuery (análisis histórico), GCS (archivo barato) o Pub/Sub (procesamiento en tiempo real). Fundamental para auditoría y cumplimiento.

**Retención**: por defecto 30 días para logs de usuario, 400 días para logs de auditoría de administrador.

### Cloud Monitoring

Recolecta **métricas** (series temporales de números): CPU, memoria, latencia, peticiones por segundo, errores por minuto... GCP emite métricas de sus servicios automáticamente; tus aplicaciones pueden emitir métricas custom.

**Conceptos clave**:
- **Workspace de Monitoring**: agrupa proyectos para ver métricas de varios proyectos en un panel.
- **Dashboards**: paneles con gráficas configurables.
- **Alerting policies**: define una condición (p.ej. "error rate > 5% durante 5 min") y una acción (email, PagerDuty, Pub/Sub).
- **Uptime checks**: pings periódicos a URLs para detectar downtime.

```bash
# Crear un uptime check básico
gcloud monitoring uptime create \
  --display-name="Check API de ejemplo" \
  --resource-type=uptime-url \
  --hostname=mi-api.run.app \
  --path=/health \
  --period=1m
```

**Métricas custom desde Python**:

```python
from google.cloud import monitoring_v3
import time

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{PROJECT_ID}"

series = monitoring_v3.TimeSeries()
series.metric.type = "custom.googleapis.com/mi_app/peticiones_procesadas"
series.resource.type = "global"

point = monitoring_v3.Point()
point.value.int64_value = 42
now = time.time()
point.interval.end_time.seconds = int(now)
series.points = [point]

client.create_time_series(name=project_name, time_series=[series])
```

### Cloud Trace

Implementa **distributed tracing**: cuando una petición pasa por varios microservicios, Trace construye el árbol de spans que muestra cuánto tardó cada pieza. Indispensable para diagnosticar latencia en arquitecturas con múltiples servicios.

GCP integra Trace automáticamente con Cloud Run y GKE si usas la librería OpenTelemetry (estándar abierto, recomendado) o la librería propia.

```python
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configuración
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(CloudTraceSpanExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

def procesar_alimento(nombre: str):
    with tracer.start_as_current_span("procesar_alimento") as span:
        span.set_attribute("alimento.nombre", nombre)
        # ... lógica de negocio
        return resultado
```

> **OpenTelemetry** es el estándar CNCF para instrumentación. Si lo usas desde el inicio, puedes cambiar el backend (Trace, Jaeger, Grafana Tempo) sin tocar el código de la app.

### Error Reporting

Agrega automáticamente excepciones similares y las agrupa como "errores únicos" con:
- Stack trace completo
- Frecuencia (cuántas veces ocurrió)
- Primer y último visto
- Enlace directo a los logs

Se activa sin configuración para Cloud Run, App Engine y GKE si los logs contienen stack traces. Para apps custom, puedes usar la librería:

```python
from google.cloud import error_reporting

client = error_reporting.Client()

try:
    operacion_riesgosa()
except Exception:
    client.report_exception()  # captura automáticamente el stack trace actual
```

---

## Integrar GitLab con GCP CI/CD

Si usas GitLab como repositorio (ver [[MOC_GitLab]]), tienes dos opciones para conectarlo con Cloud Build:

### Opción A: Cloud Build + GitLab mirror
1. En GitLab, configura un **mirror push** a un repo de GitHub o Cloud Source Repositories.
2. Cloud Build escucha ese repo y dispara el trigger.
3. Más simple pero con latencia adicional del mirror.

### Opción B: GitLab CI/CD con runners en GCP (recomendado)
Corres **GitLab Runners** en GKE o Compute Engine. El `.gitlab-ci.yml` controla el pipeline completo y usa `gcloud` / `terraform` directamente.

```yaml
# .gitlab-ci.yml — fragmento
stages:
  - build
  - deploy

variables:
  IMAGE: us-central1-docker.pkg.dev/$GCP_PROJECT/mi-repo/mi-app:$CI_COMMIT_SHA

build:
  stage: build
  image: google/cloud-sdk:slim
  script:
    - echo $GCP_SA_KEY | gcloud auth activate-service-account --key-file=-
    - gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
    - docker build -t $IMAGE .
    - docker push $IMAGE

deploy-dev:
  stage: deploy
  image: google/cloud-sdk:slim
  script:
    - gcloud run deploy producto-api --image=$IMAGE --region=us-central1
  environment:
    name: dev
  only:
    - main
```

**Autenticación segura**: usa **Workload Identity Federation** en lugar de exportar claves de Service Account. Permite que GitLab CI se autentique en GCP sin secretos de larga duración.

```bash
# Configurar Workload Identity para GitLab
gcloud iam workload-identity-pools create gitlab-pool \
  --location=global \
  --display-name="GitLab CI Pool"

gcloud iam workload-identity-pools providers create-oidc gitlab-provider \
  --location=global \
  --workload-identity-pool=gitlab-pool \
  --display-name="GitLab OIDC" \
  --attribute-mapping="google.subject=assertion.sub,attribute.project_path=assertion.project_path" \
  --issuer-uri="https://gitlab.com"
```

---

## Errores y costes comunes

| Error / trampa | Cómo evitarlo |
|---|---|
| Estado Terraform en local o en el repo | Siempre usar backend GCS con versionado |
| Service Account key exportada en el CI | Usar Workload Identity Federation |
| Logs sin estructura (texto plano) | Emitir JSON estructurado; Cloud Logging parsea los campos automáticamente |
| Alertas que nunca notifican | Crear un canal de notificación (email/Slack) ANTES del incidente y probarlo |
| Cloud Build sin caché de capas Docker | Usar `--cache-from` o el buildkit cache de AR para no rebajar capas en cada build |
| Drift de infraestructura (cambios manuales en consola) | `terraform plan` periódico en CI para detectar drift; nunca tocar consola en prod |
| Cloud Trace sin sampling configurado | Samplear al 100% en dev, reducir en prod (p.ej. 10%) para no disparar costes |

**Costes a vigilar**:
- Cloud Build: gratuito 120 min/día; las máquinas más grandes (n1-highcpu-32) son caras.
- Cloud Logging: primeros 50 GiB/mes gratis; después ~$0.50/GiB. Excluye logs de alta frecuencia que no aportan valor.
- Cloud Trace: primeros 2.5M spans/mes gratis.

---

## Aplícalo / practica

1. **Pipeline mínimo**: crea un `cloudbuild.yaml` que haga `docker build` y `docker push` a AR. Conecta un trigger a tu rama `main`.
2. **IaC desde cero**: escribe un `main.tf` que despliegue un Cloud Run service. Ejecuta `terraform plan` y verifica que el plan es coherente con lo que tienes en consola.
3. **Log query**: busca todos los errores 5xx de tu Cloud Run de las últimas 24h con `gcloud logging read`.
4. **Alerta de latencia**: crea una alerting policy en Cloud Monitoring que te avise si el p95 de latencia de tu Cloud Run supera 2 segundos.
5. **Tracing end-to-end**: instrumenta una función Python con OpenTelemetry y verifica que aparece en Cloud Trace.
6. **Workload Identity**: sustituye la SA key de tu GitLab CI por Workload Identity Federation.

---

## Conexiones

- [[MOC_GCP]]
- [[01-fundamentos-cloud-y-gcp]]
- [[02-iam-y-seguridad]]
- [[03-computo]]
- [[04-redes]]
- [[05-almacenamiento]]
- [[06-bases-de-datos]]
- [[07-datos-y-analitica]]
- [[08-contenedores-y-serverless]]
- [[10-ia-ml-vertex]]
- [[11-costes-y-buenas-practicas]]
- [[12-certificaciones-y-aprendizaje]]
- [[MOC_GitLab]]
- [[MOC_Desarrollo_Software]]
