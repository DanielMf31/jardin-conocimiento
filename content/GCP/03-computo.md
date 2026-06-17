---
title: Cómputo en GCP
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/kubernetes, programacion/serverless, programacion/devops]
type: nota
status: en-progreso
source: claude-code
aliases: [GCP Computo, Compute GCP, VMs GCP]
---

# Cómputo en GCP

## ¿Por qué existe este espectro?

El cómputo en la nube no es un monolito — es un menú con distintos niveles de **control vs. responsabilidad**. Cuanto más control tienes (VMs desnudas), más tienes que gestionar tú (OS, parches, escalado). Cuanto más gestionado (Cloud Functions), GCP se encarga de casi todo pero pierdes flexibilidad.

**Analogía hardware**: es como elegir entre montar un PC desde cero (Compute Engine), comprar un mini-PC preconstruido (GKE), un portátil (App Engine) o directamente usar una calculadora científica para lo que necesitas (Cloud Functions).

Este espectro importa porque el error más común es usar VMs para todo cuando Cloud Run o Functions resolvería lo mismo con 1/10 de la operación.

---

## El espectro: de más a menos gestionado

```
Tú gestionas más ←————————————————————————→ GCP gestiona más

Compute Engine → GKE → App Engine → Cloud Run → Cloud Functions
(IaaS)          (CaaS)   (PaaS)      (Serverless) (FaaS)
```

| Dimensión | Compute Engine | GKE | App Engine | Cloud Run | Cloud Functions |
|---|---|---|---|---|---|
| Unidad de despliegue | VM / imagen de disco | Contenedor (pod) | Código fuente / contenedor | Contenedor | Función (handler) |
| OS | Tú lo eliges y parcheas | Nodo gestionado por GKE | N/A | N/A | N/A |
| Escala mínima en idle | 1 VM (pagas) | 1 nodo mínimo | 0 (Flex=1) | 0 instancias | 0 instancias |
| Arranque en frío | Segundos-minutos | Segundos | Segundos | ~1s | <1s |
| Estado (stateful) | Sí, disco persistente | Sí, con PersistentVolume | No | No (por defecto) | No |
| Precio base | Por hora de VM | Por hora de nodo | Por hora de instancia | Por solicitud + CPU·s | Por invocación + CPU·s |
| Nivel gratuito | No | Cluster Autopilot gratis (1 nodo) | Sí (F1 Standard) | Sí (2M req/mes) | Sí (2M invocaciones/mes) |

---

## 1. Compute Engine — IaaS, VMs puras

### Qué es y cuándo usarlo

Compute Engine (CE) son **máquinas virtuales** corriendo sobre la infraestructura de Google. El equivalente en AWS es EC2.

Úsalo cuando:
- Necesitas control total del OS (ej: instalar drivers específicos, kernel custom).
- Tienes una app legada que no está en contenedores y no vale la pena migrar ahora.
- Necesitas GPU para ML de baja latencia o rendering.
- Levantas tu propio Kubernetes "a mano" (en lugar de GKE).

### Tipos de máquina

La nomenclatura sigue el patrón `FAMILIA-VERCPU-NUMERO`:

| Familia | Para qué | Ejemplo |
|---|---|---|
| `e2` | Propósito general, precio-eficiencia | `e2-medium` (1 vCPU compartida, 4 GB) |
| `n2` / `n2d` | Propósito general, rendimiento | `n2-standard-4` (4 vCPU, 16 GB) |
| `c2` / `c3` | Computación intensiva (CPU-bound) | `c2-standard-8` |
| `m1` / `m2` / `m3` | Memoria intensiva (SAP HANA, DBs grandes) | `m1-megamem-96` |
| `a2` / `g2` | GPU (NVIDIA A100 / L4) | `a2-highgpu-1g` |
| `t2a` | ARM (Ampere Altra), barato | `t2a-standard-1` |

**Tip**: para aprender y experimentar, `e2-micro` está en el free tier (1 VM por región us-*).

### Discos (almacenamiento de VM)

- **Boot disk**: donde va el OS. Por defecto SSD persistente (`pd-balanced`).
- **Persistent Disk (PD)**: bloque de red desacoplable. Puede ser `pd-standard` (HDD, barato), `pd-ssd`, `pd-balanced` o `pd-extreme` (IOPS garantizados).
- **Local SSD**: NVMe directamente en el host, efímero (se pierde al parar la VM), ultrarápido. Útil para cachés o scratch.
- **Hiperdisk**: siguiente generación de PD, con IOPS y throughput configurables independientemente del tamaño.

> Diferencia clave: PD persiste aunque pares/muevas la VM. Local SSD no.

### Preemptible vs Spot

| | Preemptible (legacy) | Spot (actual) |
|---|---|---|
| Descuento | Hasta 91% vs precio on-demand | Similar |
| GCP puede terminarla | Sí, en ≤24h siempre | Sí, cuando necesita capacidad |
| Aviso antes de terminar | 30 segundos | 30 segundos |
| Cuándo usar | Batch jobs, renderizado, ML training tolerante a fallos | Lo mismo; Spot es el recomendado hoy |

**Regla**: si tu carga de trabajo puede reiniciarse sin problema (checkpoints), usa Spot y ahorra mucho.

### Comandos gcloud esenciales

```bash
# Listar imágenes de OS disponibles (ej: Debian)
gcloud compute images list --filter="family:debian-12" --no-standard-images

# Crear una VM mínima (free tier: e2-micro en us-*)
gcloud compute instances create mi-vm \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=10GB

# SSH directo sin configurar claves manualmente
gcloud compute ssh mi-vm --zone=us-central1-a

# Listar VMs corriendo
gcloud compute instances list

# Parar / arrancar / borrar
gcloud compute instances stop mi-vm --zone=us-central1-a
gcloud compute instances start mi-vm --zone=us-central1-a
gcloud compute instances delete mi-vm --zone=us-central1-a

# Crear VM Spot
gcloud compute instances create mi-vm-spot \
  --zone=us-central1-a \
  --machine-type=n2-standard-2 \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --image-family=debian-12 \
  --image-project=debian-cloud
```

### Errores y costes comunes

- **Dejar VMs encendidas de noche/finde**: pagas por hora aunque no las uses. Usa **scheduled instances** o para manualmente.
- **Boot disk demasiado grande**: el disco persistente se cobra aunque la VM esté parada. 10-20 GB suele sobrar para desarrollo.
- **No usar Spot para batch**: coste innecesario de 5-10x.
- **Olvidar asignar Service Account**: sin ella, la VM no puede acceder a otros servicios GCP con permisos adecuados.

---

## 2. GKE — Kubernetes gestionado

### Qué es y cuándo usarlo

**GKE (Google Kubernetes Engine)** es Kubernetes como servicio. GCP gestiona el _control plane_ (el cerebro de K8s) y tú gestionas los _workloads_ (pods, deployments, services).

> Kubernetes (K8s) es un orquestador de contenedores: describe el estado deseado ("quiero 3 réplicas de este contenedor") y K8s lo mantiene. GKE elimina el trabajo de instalar y mantener K8s tú mismo.

Úsalo cuando:
- Ya tienes workloads en contenedores con lógica compleja de despliegue (múltiples servicios, dependencias entre pods).
- Necesitas control fino de red, scheduling, recursos por pod.
- Migras una arquitectura de microservicios existente en K8s on-prem.
- Necesitas stateful workloads con K8s (bases de datos en K8s, aunque generalmente mejor usar servicios gestionados).

**No lo uses** si tu caso es "quiero desplegar un contenedor sin pensar en K8s" — ahí está Cloud Run.

### Modos de GKE

| Modo | Quién gestiona los nodos | Control | Coste mínimo |
|---|---|---|---|
| **Standard** | Tú (eliges tipo de VM, configuras node pools) | Total | Pagas los nodos siempre |
| **Autopilot** | GCP (gestiona nodos automáticamente) | Solo pods | Pagas por pod activo; 1 cluster gratis |

**Recomendación para empezar**: Autopilot. Menos superficie de gestión, precio más predecible.

### Comandos gcloud / kubectl esenciales

```bash
# Crear cluster Autopilot (gratis el cluster, pagas pods)
gcloud container clusters create-auto mi-cluster \
  --region=us-central1

# Obtener credenciales para kubectl
gcloud container clusters get-credentials mi-cluster \
  --region=us-central1

# Ver nodos (Autopilot los crea on-demand)
kubectl get nodes

# Desplegar una imagen de contenedor
kubectl create deployment mi-app \
  --image=gcr.io/google-samples/hello-app:1.0 \
  --replicas=3

# Exponer con LoadBalancer (crea una IP pública)
kubectl expose deployment mi-app \
  --type=LoadBalancer \
  --port=80 \
  --target-port=8080

# Ver pods y servicios
kubectl get pods
kubectl get services

# Escalar
kubectl scale deployment mi-app --replicas=5

# Ver logs de un pod
kubectl logs -l app=mi-app --tail=50
```

---

## 3. App Engine — PaaS clásico

### Qué es y cuándo usarlo

**App Engine** es la opción más antigua de GCP (2008). Subes código, GCP lo empaqueta y ejecuta. No ves servidores ni contenedores directamente.

Dos entornos:
- **Standard**: sandboxed, arranque instantáneo, escala a 0, lenguajes específicos (Python, Java, Go, Node, PHP, Ruby). Muy barato / gratuito para tráfico bajo.
- **Flexible**: corre en contenedores Docker, cualquier lenguaje, más lento en arranque, no escala a 0 (mínimo 1 instancia).

Úsalo cuando:
- Tienes una app web sencilla y quieres el mínimo de ops posible.
- El free tier de Standard es suficiente para tu caso (aplicaciones internas, demos).
- Tu stack es Python/Node/Go y no quieres configurar Cloud Run.

**Limitación importante**: una sola app Engine por proyecto. Si necesitas múltiples servicios independientes, mejor Cloud Run.

```bash
# Desplegar (desde directorio con app.yaml)
gcloud app deploy

# Ver logs en tiempo real
gcloud app logs tail -s default

# Ver URL de la app
gcloud app browse

# Listar versiones desplegadas
gcloud app versions list
```

**app.yaml mínimo (Python Standard)**:
```yaml
runtime: python311
entrypoint: gunicorn -b :$PORT main:app
```

---

## 4. Cloud Run — Contenedores serverless

### Qué es y cuándo usarlo

**Cloud Run** ejecuta contenedores Docker de forma serverless: escala de 0 a N instancias automáticamente según tráfico, y pagas solo mientras procesa solicitudes (CPU + memoria × segundos activos).

Es el punto dulce para la mayoría de workloads modernos: tienes la flexibilidad de contenedores (cualquier lenguaje, cualquier dependencia) sin gestionar infraestructura.

Úsalo cuando:
- Tienes una API REST, un webhook, un microservicio web.
- El tráfico es variable o irregular (escala a 0 en idle = coste cero).
- Quieres desplegar rápido desde CI/CD sin pensar en K8s.
- Tu app tiene arranque rápido (<10s) — si tarda más, el cold start duele.

**Equivalente AWS**: AWS Fargate + API Gateway, o AWS Lambda Container Images.

### Conceptos clave

- **Servicio**: la unidad principal. Un contenedor expuesto en HTTPS con URL automática (`*.run.app`).
- **Revisión**: cada despliegue crea una revisión inmutable. Puedes hacer traffic splitting entre revisiones (ej: canary 10% → nueva versión).
- **Concurrencia**: cuántas solicitudes simultáneas maneja una instancia (default 80). Clave para el coste.
- **Min instances**: si pones `--min-instances=1`, evitas cold starts pero pagas esa instancia en idle.
- **Cloud Run Jobs**: para tareas batch (no HTTP), ejecuta el contenedor hasta que termina.

### Comandos gcloud

```bash
# Desplegar directamente desde código fuente (buildpacks, sin Dockerfile)
gcloud run deploy mi-api \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated

# Desplegar desde imagen en Artifact Registry
gcloud run deploy mi-api \
  --image=us-central1-docker.pkg.dev/MI_PROYECTO/mi-repo/mi-app:latest \
  --region=us-central1 \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=80 \
  --max-instances=10 \
  --allow-unauthenticated

# Ver servicios desplegados
gcloud run services list --region=us-central1

# Ver detalles y URL
gcloud run services describe mi-api --region=us-central1

# Actualizar variable de entorno sin redesplegar imagen
gcloud run services update mi-api \
  --region=us-central1 \
  --set-env-vars="DB_HOST=mi-host,DEBUG=false"

# Traffic splitting: 10% a revisión nueva, 90% a la anterior
gcloud run services update-traffic mi-api \
  --region=us-central1 \
  --to-revisions=mi-api-00002-abc=10,LATEST=90

# Cloud Run Job (batch)
gcloud run jobs create mi-job \
  --image=us-central1-docker.pkg.dev/MI_PROYECTO/mi-repo/mi-job:latest \
  --region=us-central1 \
  --tasks=10 \
  --max-retries=3

gcloud run jobs execute mi-job --region=us-central1
```

### Errores y costes comunes

- **Cold start inesperado**: si `--min-instances=0` y el servicio lleva tiempo sin tráfico, la primera solicitud puede tardar 2-5s. Para APIs de usuario final, pon `--min-instances=1`.
- **Timeout demasiado corto**: default 300s. Para jobs largos, sube hasta 3600s con `--timeout`.
- **Imagen demasiado grande**: imágenes de >1 GB ralentizan el pull. Usa imágenes base alpine/distroless.
- **No configurar límites de instancias**: sin `--max-instances`, en un spike puede crear 1000 instancias y generar costes inesperados.

---

## 5. Cloud Functions — FaaS, funciones individuales

### Qué es y cuándo usarlo

**Cloud Functions** ejecuta una función individual (un handler) en respuesta a un evento. No gestionas contenedor ni servidor. GCP se encarga de todo el runtime.

Dos generaciones:
- **1ª gen**: por función, límite 9 min, concurrencia = 1 por instancia.
- **2ª gen**: basada en Cloud Run internamente, límite 60 min, concurrencia configurable, más potente. **Usa siempre 2ª gen** para proyectos nuevos.

Úsalo cuando:
- Tienes un trigger de evento puntual: un mensaje en Pub/Sub, un fichero subido a Cloud Storage, una llamada HTTP simple.
- La lógica es pequeña y autocontenida (no toda una API REST).
- Quieres el mínimo de código de infraestructura posible.

**Cuándo preferir Cloud Run sobre Functions**: si la función tiene muchas dependencias, arranque lento, o formas parte de una API con múltiples endpoints — agrúpalos en un contenedor Cloud Run.

### Triggers disponibles

| Trigger | Descripción |
|---|---|
| HTTP | Llamada directa vía HTTPS |
| Pub/Sub | Mensaje en un topic |
| Cloud Storage | Objeto creado / eliminado / modificado |
| Firestore | Documento creado / modificado |
| Firebase Auth | Usuario creado / eliminado |
| Eventarc (gen 2) | Cualquier evento de GCP vía Cloud Audit Logs |

### Ejemplo y comandos

```python
# main.py — función HTTP mínima (Python)
import functions_framework

@functions_framework.http
def hola_mundo(request):
    nombre = request.args.get("nombre", "mundo")
    return f"Hola, {nombre}!", 200
```

```bash
# Desplegar función HTTP (2ª gen)
gcloud functions deploy hola-mundo \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=hola_mundo \
  --trigger-http \
  --allow-unauthenticated \
  --memory=256Mi \
  --timeout=60s

# Desplegar función Pub/Sub (2ª gen)
gcloud functions deploy procesar-evento \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=procesar_evento \
  --trigger-topic=mi-topic \
  --memory=512Mi

# Ver funciones
gcloud functions list --region=us-central1

# Invocar manualmente (HTTP)
gcloud functions call hola-mundo \
  --region=us-central1 \
  --gen2 \
  --data='{"nombre": "Daniel"}'

# Ver logs
gcloud functions logs read hola-mundo \
  --region=us-central1 \
  --gen2 \
  --limit=50
```

---

## Tabla: ¿Cuándo usar qué?

| Escenario | Servicio recomendado | Por qué |
|---|---|---|
| App legada sin contenedores, necesito levantar y que funcione | **Compute Engine** | Control total, puedo instalar lo que sea |
| ML training con GPU, workload largo | **Compute Engine** (Spot) | GPU disponible, ahorro con Spot |
| Arquitectura de microservicios ya en K8s | **GKE** | Portabilidad, ecosistema K8s |
| Escalar a 100+ pods con lógica de red compleja | **GKE** | Control de red, scheduling avanzado |
| API REST moderna, tráfico variable | **Cloud Run** | Serverless, paga por uso, fácil CI/CD |
| App web sencilla, Python/Node, free tier | **App Engine Standard** | Más simple aún que Cloud Run, gratis |
| Procesar fichero al subirse a Cloud Storage | **Cloud Functions** | Trigger de evento puntual |
| Webhook de tercero (GitHub, Stripe) | **Cloud Functions** o **Cloud Run** | HTTP simple; Functions si es un handler, Run si es una API mayor |
| Job batch nocturno en contenedor | **Cloud Run Jobs** | Serverless batch, no necesita estar up 24h |
| Pipeline de datos complejo en batch | **Cloud Dataflow** o **Batch** | Herramientas específicas de datos (ver [[07-datos-y-analitica]]) |

---

## Free Tier resumido

| Servicio | Qué incluye gratis (por mes) |
|---|---|
| Compute Engine | 1 e2-micro en us-* (30 GB HDD, 1 GB egress a NA) |
| GKE Autopilot | 1 cluster Autopilot gratis (pagas pods) |
| App Engine Standard | 28 h de instancia F1/día, 5 GB Cloud Storage |
| Cloud Run | 2 M solicitudes, 360.000 GB-s CPU, 180.000 GB-s memoria |
| Cloud Functions | 2 M invocaciones, 400.000 GB-s, 200.000 GHz-s |

---

## Aplícalo / Practica

1. **VM básica**: crea una `e2-micro` en `us-central1-a`, conéctate por SSH, instala nginx, y accede desde el navegador. Borra la VM al terminar.
2. **Cloud Run desde cero**: crea una API FastAPI mínima, escribe un `Dockerfile`, súbela a Artifact Registry y despliégala en Cloud Run. Verifica que escala a 0.
3. **Cloud Function event-driven**: crea un bucket en Cloud Storage y una Cloud Function (gen 2) que imprima en logs el nombre de cada fichero que subas.
4. **Comparativa de coste**: calcula con la [calculadora de GCP](https://cloud.google.com/products/calculator) el coste mensual de: (a) una VM `e2-standard-2` 24/7 vs (b) Cloud Run con 1M solicitudes/mes de 200ms a 1 vCPU.
5. **GKE Autopilot**: despliega el `hello-app` de Google en un cluster Autopilot, exponlo con LoadBalancer, escala a 5 réplicas, y observa cómo Autopilot aprovisiona nodos automáticamente.

---

## Conexiones

- [[MOC_GCP]]
- [[01-fundamentos-cloud-y-gcp]]
- [[02-iam-y-seguridad]]
- [[04-redes]]
- [[05-almacenamiento]]
- [[06-bases-de-datos]]
- [[07-datos-y-analitica]]
- [[08-contenedores-y-serverless]]
- [[09-devops-iac-observabilidad]]
- [[10-ia-ml-vertex]]
- [[11-costes-y-buenas-practicas]]
- [[12-certificaciones-y-aprendizaje]]
- [[MOC_Desarrollo_Software]]
