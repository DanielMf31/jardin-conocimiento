---
title: Contenedores y Serverless en GCP
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/contenedores, programacion/serverless, programacion/kubernetes, programacion/docker]
type: nota
status: en-progreso
source: claude-code
aliases: [Cloud Run, GKE, contenedores GCP]
---

# 📦 Contenedores y Serverless en GCP

## ¿Por qué esto importa?

El modelo clásico es: **tú gestionas servidores** → instalas dependencias → despliegas código → vigilas que no se caiga. Eso escala mal y consume tiempo de ingeniería.

Los contenedores y serverless invierten la ecuación: **empaquetas tu app con todo lo que necesita** (imagen Docker) y le dices a GCP "ejecútala". GCP decide dónde, cuándo y cuántas instancias. Tú pagas solo lo que usas.

Esto tiene dos sabores en GCP:

| Modelo | Tu responsabilidad | Cuándo escala |
|---|---|---|
| **Serverless** (Cloud Run, Functions) | Solo el código/contenedor | Automático, incluido a cero |
| **Contenedores orquestados** (GKE) | El clúster Kubernetes completo | Automático, pero tú configuras el autoscaler |

> Analogía hardware: Cloud Run es como un PLC que ejecuta tu programa cuando llega una señal — no gestionas el hardware subyacente. GKE es como tener un rack propio donde tú decides la distribución de carga.

---

## 🗂️ Artifact Registry — El almacén de imágenes

### Qué problema resuelve

Antes de desplegar un contenedor, la imagen tiene que vivir en algún sitio. Artifact Registry (AR) es el registro privado de GCP para imágenes Docker (y también paquetes Maven, npm, PyPI).

Es el sucesor de **Container Registry** (`gcr.io`). Si ves `gcr.io` en documentación antigua, AR es el equivalente moderno.

### Estructura conceptual

```
Artifact Registry
└── Repositorio  (zona + nombre, ej: europe-west1/mi-repo)
    └── Imagen   (ej: mi-api)
        └── Tags (ej: latest, v1.2, sha256:abc...)
```

Un **repositorio** es como un namespace con región y formato definidos. Puedes tener uno por proyecto o uno por equipo.

### Comandos esenciales

```bash
# Crear repositorio Docker en Europa
gcloud artifacts repositories create mi-repo \
  --repository-format=docker \
  --location=europe-west1 \
  --description="Imágenes de producción"

# Autenticar Docker con AR (una sola vez por máquina)
gcloud auth configure-docker europe-west1-docker.pkg.dev

# Etiquetar y subir imagen
docker tag mi-api:latest europe-west1-docker.pkg.dev/PROJECT_ID/mi-repo/mi-api:v1

docker push europe-west1-docker.pkg.dev/PROJECT_ID/mi-repo/mi-api:v1

# Listar imágenes
gcloud artifacts docker images list europe-west1-docker.pkg.dev/PROJECT_ID/mi-repo
```

### Buenas prácticas

- Activa **Vulnerability Scanning** automático (gratis para las primeras exploraciones, luego por imagen).
- Usa tags semánticos (`v1.2.3`) además de `latest` para poder hacer rollback.
- Configura **políticas de limpieza** para borrar imágenes antiguas y no pagar almacenamiento innecesario.

---

## 🚀 Cloud Run — Serverless para contenedores

### Qué es y por qué es especial

Cloud Run ejecuta **cualquier contenedor HTTP** sin que gestiones servidores, VMs ni Kubernetes. La característica más importante: **escala a cero**. Si no hay peticiones, no hay instancias, no hay coste.

Internamente usa **Knative** (estándar open-source sobre Kubernetes), pero tú no ves nada de eso.

> Equivalente AWS: AWS Fargate / App Runner. Diferencia: Cloud Run escala a cero por defecto sin configuración extra.

### Cuándo usar Cloud Run

- APIs REST o GraphQL
- Webhooks, procesadores de eventos
- Apps web completas (incluso con SSR)
- Jobs batch de corta duración (Cloud Run Jobs)
- Prototipado rápido con tiempo hasta producción real

### Modelo de ejecución

```
Petición HTTP entrante
       ↓
  Cloud Run (si no hay instancias → cold start ~1-2s)
       ↓
  Tu contenedor (puerto 8080 por defecto)
       ↓
  Respuesta → instancia se mantiene "caliente" N minutos
       ↓
  Sin peticiones → instancia se destruye (escala a cero)
```

**Cold start**: el tiempo que tarda en arrancar una instancia nueva. Para Python/Node suele ser 1-3s. Para JVM puede ser 5-10s. Minimizan con `--min-instances=1` (sacrifica escala-a-cero).

### Paso a paso: desplegar en Cloud Run

**Paso 1 — Construir la imagen**

```bash
# Desde la carpeta de tu proyecto
docker build -t mi-api:v1 .

# O dejar que Cloud Build la construya directamente (sin Docker local)
gcloud builds submit --tag europe-west1-docker.pkg.dev/PROJECT_ID/mi-repo/mi-api:v1
```

**Paso 2 — Subir a Artifact Registry**

```bash
docker push europe-west1-docker.pkg.dev/PROJECT_ID/mi-repo/mi-api:v1
```

**Paso 3 — Desplegar en Cloud Run**

```bash
gcloud run deploy mi-api \
  --image=europe-west1-docker.pkg.dev/PROJECT_ID/mi-repo/mi-api:v1 \
  --region=europe-west1 \
  --platform=managed \
  --allow-unauthenticated \         # Para APIs públicas; quitar para internas
  --port=8080 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \               # Escala a cero
  --max-instances=10 \
  --concurrency=80                  # Peticiones simultáneas por instancia
```

**Paso 4 — Verificar**

```bash
# Ver URL del servicio
gcloud run services describe mi-api --region=europe-west1 --format='value(status.url)'

# Ver logs en tiempo real
gcloud run services logs tail mi-api --region=europe-west1
```

### Variables de entorno y secretos

```bash
# Variables planas (para config no sensible)
gcloud run deploy mi-api \
  --set-env-vars="ENV=production,API_VERSION=v1"

# Secretos (con Secret Manager — lo correcto para passwords/API keys)
gcloud run deploy mi-api \
  --set-secrets="DB_PASSWORD=mi-secreto:latest"
```

### Revisiones y tráfico

Cloud Run usa el concepto de **revisiones** (cada deploy crea una nueva). Puedes hacer splits de tráfico para canary releases:

```bash
# 90% a la revisión estable, 10% a la nueva
gcloud run services update-traffic mi-api \
  --to-revisions=mi-api-v1=90,mi-api-v2=10 \
  --region=europe-west1
```

### Precios Cloud Run (orientativo 2026)

- **CPU**: facturada solo mientras procesa peticiones (cuando `--cpu-boost` no está activado)
- **Free tier**: 2 millones de peticiones/mes, 360.000 GB-s de CPU/mes, 180.000 GB-s de RAM/mes
- Para una API de baja carga: **efectivamente gratis**

---

## ☸️ GKE — Google Kubernetes Engine

### Qué es y cuándo lo necesitas

GKE es Kubernetes gestionado. Google mantiene el **control plane** (el cerebro del clúster) y tú gestionas los **nodos** (las VMs donde corren tus pods).

Kubernetes (K8s) es el estándar de facto para orquestar contenedores a escala: define cómo se despliegan, se comunican, se escalan y se recuperan de fallos.

> Analogía: si Cloud Run es un servicio de mensajería (entregas sin pensar en la logística), GKE es tener tu propia flota de camiones donde tú decides rutas, capacidad y mantenimiento — más control, más responsabilidad.

### Cuándo GKE sobre Cloud Run

| Necesitas GKE si... | Cloud Run es suficiente si... |
|---|---|
| Workloads con estado (stateful sets, bases de datos) | App sin estado (APIs, web) |
| Protocolos distintos a HTTP/gRPC (TCP, UDP crudo) | Solo HTTP/HTTPS |
| Control fino de networking (CNI, Network Policies) | El networking automático es suficiente |
| Migrando un clúster K8s existente | Empezando desde cero |
| Necesitas DaemonSets, Jobs complejos, CronJobs | Jobs simples (Cloud Run Jobs) |
| Equipo con expertise Kubernetes ya existente | Equipo pequeño sin K8s experience |

### Modos de GKE

| Modo | Qué gestionas | Para quién |
|---|---|---|
| **Autopilot** | Solo los pods (GKE gestiona nodos) | La mayoría de casos; recomendado por Google |
| **Standard** | Nodos + pods | Necesitas control de nodos (GPU, spot VMs, configuración OS) |

**Autopilot es el default recomendado** desde 2021. Pagas por pod, no por nodo reservado.

### Comandos básicos GKE

```bash
# Crear clúster Autopilot
gcloud container clusters create-auto mi-cluster \
  --region=europe-west1

# Obtener credenciales para kubectl
gcloud container clusters get-credentials mi-cluster \
  --region=europe-west1

# Desplegar una app (igual que K8s estándar)
kubectl apply -f deployment.yaml

# Ver pods corriendo
kubectl get pods -n default

# Escalar manualmente
kubectl scale deployment mi-api --replicas=5
```

### Estructura mínima de un Deployment en GKE

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mi-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mi-api
  template:
    metadata:
      labels:
        app: mi-api
    spec:
      containers:
      - name: mi-api
        image: europe-west1-docker.pkg.dev/PROJECT_ID/mi-repo/mi-api:v1
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: mi-api-svc
spec:
  selector:
    app: mi-api
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer  # Expone con IP pública
```

---

## ⚡ Cloud Functions — Serverless para fragmentos de código

Cloud Functions ejecuta **una función** en respuesta a un evento, sin contenedor que gestionar. La unidad mínima de despliegue.

- **Gen 1**: entorno fijo, lenguajes específicos.
- **Gen 2**: basada en Cloud Run internamente; más potente, soporta mayor tiempo de ejecución (hasta 60 min).

```bash
# Desplegar una función Python (Gen 2)
gcloud functions deploy mi-funcion \
  --gen2 \
  --runtime=python312 \
  --region=europe-west1 \
  --source=. \
  --entry-point=handler \
  --trigger-http \
  --allow-unauthenticated
```

---

## 📊 Comparativa: Cloud Run vs GKE vs Cloud Functions

| Criterio | Cloud Functions | Cloud Run | GKE (Autopilot) |
|---|---|---|---|
| **Unidad de despliegue** | Función | Contenedor | Pod (contenedor + metadatos K8s) |
| **Escala a cero** | Sí | Sí | No (mínimo 1 pod en Autopilot) |
| **Cold start** | Bajo (runtime prefabricado) | Bajo-medio (imagen personalizada) | Sin cold start relevante |
| **Latencia máxima por invocación** | 60 min (Gen 2) | 60 min | Ilimitada |
| **Protocolos** | HTTP, eventos GCP | HTTP, gRPC | Cualquiera (TCP, UDP) |
| **Estado** | Sin estado | Sin estado | Con o sin estado |
| **Complejidad operacional** | Muy baja | Baja | Media-alta |
| **Control** | Mínimo | Medio | Máximo |
| **Coste base (sin tráfico)** | Cero | Cero | ~$70-150/mes (nodos mínimos) |
| **Mejor para** | Webhooks, glue code | APIs, web apps | Microservicios complejos |

### Árbol de decisión rápido

```
¿Necesitas K8s o workloads con estado?
├── Sí → GKE
└── No → ¿Es una función simple (<15 min, 1 propósito)?
    ├── Sí → Cloud Functions (Gen 2)
    └── No → Cloud Run
```

---

## 🛠️ Ejemplo completo: FastAPI en Cloud Run

Supón que tienes la app web (FastAPI + Python) y quieres desplegarla sin gestionar infraestructura.

### Estructura del proyecto

```
mi-api/
├── app/
│   └── main.py
├── requirements.txt
└── Dockerfile
```

### Dockerfile mínimo para FastAPI

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Cloud Run espera el puerto 8080 por defecto
ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### requirements.txt

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
```

### Script de despliegue completo

```bash
#!/bin/bash
PROJECT_ID="mi-proyecto-gcp"
REGION="europe-west1"
SERVICE="producto-api"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/mi-repo/$SERVICE"

# 1. Construir y subir (Cloud Build — no necesita Docker local)
gcloud builds submit \
  --tag "$IMAGE:$(git rev-parse --short HEAD)" \
  --project "$PROJECT_ID"

# 2. Desplegar en Cloud Run
gcloud run deploy "$SERVICE" \
  --image "$IMAGE:$(git rev-parse --short HEAD)" \
  --region "$REGION" \
  --platform managed \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --set-env-vars "ENV=production" \
  --no-allow-unauthenticated \  # Solo acceso autenticado
  --project "$PROJECT_ID"

echo "Desplegado: $(gcloud run services describe $SERVICE --region $REGION --format='value(status.url)')"
```

### Verificar el despliegue

```bash
# Llamar al endpoint con autenticación IAM
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://producto-api-XXXX-ew.a.run.app/health
```

---

## 🔗 CI/CD con Cloud Run

El flujo típico en un equipo:

```
Push a main en GitLab/GitHub
    ↓
Cloud Build (o GitLab CI) ejecuta pipeline
    ↓
docker build + push a Artifact Registry
    ↓
gcloud run deploy (nueva revisión)
    ↓
Split de tráfico canary (opcional)
    ↓
100% tráfico a nueva revisión si métricas OK
```

Ver [[09-devops-iac-observabilidad]] para el pipeline completo.

---

## ⚠️ Errores y costes comunes

| Error | Causa | Solución |
|---|---|---|
| `Container failed to start` | App no escucha en el puerto correcto | Cloud Run espera el puerto de `--port` (default 8080) |
| Cold start alto | Imagen grande o runtime pesado (JVM) | Imagen slim, `--min-instances=1` para servicios críticos |
| `Memory limit exceeded` | Pico de RAM no previsto | Aumentar `--memory`, revisar leaks |
| Coste inesperado en GKE | Nodos siempre corriendo aunque sin carga | Usar Autopilot o configurar node pool scale-to-zero |
| Imagen no encontrada | AR en región diferente o permisos IAM | Service Account del Cloud Run necesita rol `Artifact Registry Reader` |

---

## 🏋️ Aplícalo / Practica

1. **Nivel 0 (15 min)**: Despliega la imagen `gcr.io/google-samples/hello-app:1.0` en Cloud Run con `gcloud run deploy`. Prueba la URL.

2. **Nivel 1 (1h)**: Toma la API de producto (FastAPI), escribe el Dockerfile, publícala en AR y despliégala en Cloud Run con variables de entorno desde Secret Manager.

3. **Nivel 2 (2-3h)**: Crea un clúster GKE Autopilot, escribe el `deployment.yaml` y el `service.yaml`, y despliega la misma imagen. Compara la experiencia operacional con Cloud Run.

4. **Nivel 3 (diseño)**: Diseña la arquitectura de microservicios de la app web: ¿qué servicios irían a Cloud Run, cuáles a GKE, y qué eventos dispararían Cloud Functions?

---

## Conexiones

- [[MOC_GCP]]
- [[01-fundamentos-cloud-y-gcp]]
- [[02-iam-y-seguridad]]
- [[03-computo]]
- [[04-redes]]
- [[05-almacenamiento]]
- [[09-devops-iac-observabilidad]]
- [[11-costes-y-buenas-practicas]]
- [[MOC_Desarrollo_Software]]
