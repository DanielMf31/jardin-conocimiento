---
title: Costes y buenas prácticas en GCP
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/finops, programacion/arquitectura]
type: nota
status: en-progreso
source: claude-code
aliases: [GCP costes, FinOps GCP, GCP billing]
---

# 💸 Costes y buenas prácticas en GCP

## ¿Por qué este documento?

En cloud, **no pagar de más es una habilidad de ingeniería**, no solo de gestión. A diferencia de un servidor físico (coste fijo), GCP factura por lo que consumes — y si no entiendes el modelo, una carga de trabajo mal configurada puede generar una factura de cientos de euros en horas.

Este documento cubre el modelo mental de pricing, las herramientas que GCP da para controlarlo, las trampas habituales, y el marco de buenas prácticas que Google usa para evaluar arquitecturas (el Architecture Framework).

---

## 1. 🧱 Modelo de pricing: pago por uso

GCP factura en varias dimensiones según el producto. Es clave entender **qué contador se activa** en cada servicio.

| Dimensión de coste | Ejemplo | Analogía hardware |
|----|----|----|
| **Tiempo de cómputo** | VM encendida por hora | CPU encendida |
| **Almacenamiento por GB/mes** | Disco persistente, GCS | Disco montado |
| **Operaciones / peticiones** | Cloud Functions invocaciones | Interrupciones de CPU |
| **Tráfico de red (egress)** | Datos saliendo de GCP | Ancho de banda consumido |
| **Datos procesados** | BigQuery por TB escaneado | — |
| **Instancias activas** | Cloud SQL por hora | Base de datos encendida |

### Descuentos automáticos (sin hacer nada)

- **Sustained Use Discounts (SUD)**: si una VM Compute Engine corre >25% del mes, GCP aplica descuento automático escalonado — hasta ~30% si corre todo el mes. Solo aplica a N1/N2/N2D.
- **Committed Use Discounts (CUD)**: si te comprometes 1 o 3 años, obtienes hasta 57% de descuento (vCPU/RAM). Equivalente a Reserved Instances en AWS. Útil cuando la carga es predecible.
- **Preemptible VMs / Spot VMs**: VMs que GCP puede interrumpir con 30s de aviso. Hasta 91% más baratas. Ideales para batch, entrenamiento ML, renderizado.

```bash
# Ver descuentos CUD disponibles
gcloud compute commitments list --project=MI_PROYECTO

# Crear un CUD de 1 año para 4 vCPU + 16 GB RAM en us-central1
gcloud compute commitments create mi-commitment \
  --plan=12-month \
  --region=us-central1 \
  --resources=vcpu=4,memory=16GB
```

---

## 2. 🆓 Free Tier: lo que siempre es gratis

GCP tiene dos capas de gratuidad:

### 2a. Free Trial (crédito inicial)
- **$300 USD en 90 días** para cuentas nuevas.
- Puedes usar cualquier producto, incluidos los de pago.
- Cuidado: si activas facturación real, el crédito sigue activo pero ya puedes ser cobrado si se agota.

### 2b. Always Free (permanente, sin fecha de caducidad)

| Producto | Límite gratuito mensual | Notas |
|----|----|----|
| **Compute Engine** | 1 VM e2-micro (us-central1/us-east1/us-west1) | Solo esa región y tipo |
| **Cloud Storage** | 5 GB en Standard | Solo en regiones US |
| **BigQuery** | 1 TB de queries / mes + 10 GB almacenamiento | El más valioso para DS |
| **Cloud Run** | 2M peticiones / mes | Muy útil para APIs pequeñas |
| **Cloud Functions** | 2M invocaciones / mes | Gen1 |
| **Pub/Sub** | 10 GB / mes | — |
| **Firestore** | 1 GB almacenamiento + 50K lecturas/día | — |
| **Artifact Registry** | 0.5 GB almacenamiento | — |
| **Secret Manager** | 6 versiones activas + 10K accesos | — |

> Referencia oficial actualizada: https://cloud.google.com/free/docs/free-cloud-features

---

## 3. 🔔 Presupuestos y alertas de gasto

Sin alertas, puedes descubrir el problema en la factura de fin de mes. GCP permite definir **budgets** con notificaciones automáticas.

### Cómo crear una alerta (consola)
1. Billing → Budgets & Alerts → Create budget
2. Define el ámbito: toda la cuenta, un proyecto, o un conjunto de servicios/labels.
3. Define el importe objetivo (p.ej. 50 USD/mes).
4. Configura umbrales: GCP notifica al 50%, 90%, 100% del presupuesto (o del gasto real proyectado).

### Con gcloud / Terraform (preferible en proyectos serios)

```bash
# No hay gcloud directo para budgets; se usa la Billing API o Terraform

# Con Terraform (google_billing_budget)
resource "google_billing_budget" "alerta_proyecto" {
  billing_account = "XXXXXX-YYYYYY-ZZZZZZ"
  display_name    = "Alerta 50 USD"

  budget_filter {
    projects = ["projects/123456789"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = "50"
    }
  }

  threshold_rules {
    threshold_percent = 0.5
  }
  threshold_rules {
    threshold_percent = 0.9
  }
  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "FORECASTED_SPEND"
  }
}
```

> Las alertas **no detienen** el gasto por defecto. Para cortar automáticamente, conecta un Pub/Sub topic a una Cloud Function que deshabilite la facturación del proyecto. Documentado en: https://cloud.google.com/billing/docs/how-to/notify

---

## 4. 🏷️ Labels: imputar costes a contexto

Un **label** es un par clave-valor que puedes añadir a casi cualquier recurso GCP. Son la base del **FinOps** (gestión financiera de cloud): sin labels, no sabes qué proyecto/equipo/entorno genera el gasto.

### Estrategia de labels mínima

```
env        = prod | staging | dev
team       = backend | data | infra
project    = producto-app | embebido | personal
cost-center = ingenieria | investigacion
```

```bash
# Añadir labels a una VM
gcloud compute instances add-labels mi-vm \
  --labels=env=dev,team=backend,project=producto-app \
  --zone=us-central1-a

# Añadir labels a un bucket de GCS
gcloud storage buckets update gs://mi-bucket \
  --update-labels=env=dev,project=producto-app
```

Los labels aparecen en **Cloud Billing export to BigQuery** — la forma más potente de analizar costes con SQL. Actívalo en Billing → Billing export → BigQuery export.

```sql
-- ¿Cuánto gasta cada proyecto la última semana?
SELECT
  labels.value AS proyecto,
  SUM(cost) AS coste_usd
FROM `mi_dataset.gcp_billing_export_v1_*`,
  UNNEST(labels) AS labels
WHERE labels.key = 'project'
  AND DATE(_PARTITIONTIME) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY proyecto
ORDER BY coste_usd DESC
```

---

## 5. ⚠️ Trampas de coste típicas

Estas son las sorpresas más frecuentes para equipos que vienen de on-premise o AWS.

### 5a. Egress (tráfico de red saliente)

El **tráfico entrante a GCP es gratis**. El saliente, no:

| Destino del tráfico | Coste aproximado |
|----|----|
| Dentro de la misma zona | Gratis |
| Entre zonas (misma región) | ~$0.01/GB |
| Entre regiones GCP | ~$0.02–0.08/GB según regiones |
| Hacia internet (egress) | ~$0.08–0.12/GB (primeros 1 TB/mes) |
| Hacia otras clouds (AWS, Azure) | ~$0.08/GB |

**Trampa clásica**: poner un cliente en AWS y el backend en GCP. Cada llamada API paga egress doble.

**Solución**: colocar los servicios que se hablan mucho en la misma zona. Usar Cloud CDN para servir assets estáticos (el egress desde CDN es más barato).

### 5b. BigQuery: pago por datos escaneados

BigQuery cobra ~$5 por TB escaneado en el modo on-demand. Una query mal escrita sobre una tabla grande puede costar decenas de dólares.

```sql
-- MAL: escanea toda la tabla (si tiene 10 TB → $50)
SELECT * FROM `proyecto.dataset.tabla_enorme`

-- BIEN: filtra la partición primero
SELECT campo1, campo2
FROM `proyecto.dataset.tabla_enorme`
WHERE DATE(timestamp_col) = '2026-06-14'  -- usa partición
  AND pais = 'ES'
LIMIT 1000
```

**Buenas prácticas BQ**:
- Usa el **estimador de bytes** antes de ejecutar (esquina inferior derecha en consola).
- Activa **particionado** en tablas grandes (por fecha casi siempre).
- Usa **clustering** en columnas de filtro frecuentes.
- Considera el modo **BigQuery Editions** (Reservations) si el equipo hace muchas queries: precio fijo por slots.

### 5c. Recursos olvidados encendidos

| Recurso | Coste típico abandonado |
|----|----|
| VM e2-standard-4 corriendo 24/7 | ~$100/mes |
| Cloud SQL db-n1-standard-2 | ~$130/mes |
| NAT Gateway sin tráfico | ~$30/mes base |
| Load Balancer sin backends | ~$18/mes (regla de reenvío) |
| IP estática no asignada | ~$7/mes |

```bash
# Listar VMs encendidas en todos los proyectos
gcloud compute instances list --filter="status=RUNNING" --format="table(name,zone,status,machineType)"

# Listar IPs estáticas no usadas (no asignadas)
gcloud compute addresses list --filter="status=RESERVED" --format="table(name,region,address,status)"

# Listar Cloud SQL instances
gcloud sql instances list --format="table(name,state,databaseVersion,settings.tier)"
```

**Automatización**: usa **Resource Manager** o scripts en Cloud Scheduler que apaguen recursos de dev fuera de horario laboral.

### 5d. Cloud Storage: clases y operaciones

GCP cobra por clase de almacenamiento Y por operaciones (lecturas/escrituras):

| Clase | Precio/GB/mes | Mínimo retención | Uso |
|----|----|----|----|
| Standard | $0.020 | Ninguno | Datos activos |
| Nearline | $0.010 | 30 días | Acceso <1/mes |
| Coldline | $0.004 | 90 días | Backups |
| Archive | $0.0012 | 365 días | Archivos legales |

**Trampa**: guardar logs de acceso frecuente en Coldline — las operaciones de lectura cuestan más, y pagas penalización si borras antes del mínimo.

**Solución**: usa **Object Lifecycle Management** para mover automáticamente objetos entre clases según edad.

```bash
# Aplicar política de ciclo de vida (archivo JSON)
gcloud storage buckets update gs://mi-bucket \
  --lifecycle-file=lifecycle.json
```

```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30, "matchesStorageClass": ["STANDARD"]}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90, "matchesStorageClass": ["NEARLINE"]}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365, "matchesStorageClass": ["COLDLINE"]}
      }
    ]
  }
}
```

---

## 6. 🏛️ Google Cloud Architecture Framework

El Architecture Framework de Google es el equivalente al AWS Well-Architected Framework. Define **6 pilares** para evaluar si una arquitectura está bien diseñada:

| Pilar | Pregunta clave | Herramienta GCP |
|----|----|----|
| **Excelencia operativa** | ¿Puedes desplegar, operar y evolucionar sin fricción? | Cloud Operations, CI/CD |
| **Seguridad** | ¿Están los datos y accesos protegidos? | IAM, VPC SC, Secret Manager |
| **Fiabilidad** | ¿Funciona bajo carga y se recupera de fallos? | Load Balancing, Cloud Spanner |
| **Optimización de costes** | ¿Pagas solo lo que necesitas? | Budgets, CUD, autoscaling |
| **Rendimiento** | ¿La latencia y throughput cumplen los SLOs? | Cloud CDN, regiones, Memorystore |
| **Sostenibilidad** | ¿Minimizas el impacto ambiental? | Regiones limpias, eficiencia |

### Principios clave de optimización de costes (pilar 4)

1. **Rightsize antes de comprometer**: usa recomendaciones del Recommender para ajustar tamaño de VMs.
2. **Autoscaling por defecto**: Compute Engine Managed Instance Groups, Cloud Run, GKE Autopilot escalan a cero o ajustan capacity.
3. **Spot/Preemptible para cargas tolerantes**: ML training, procesamiento batch.
4. **Eliminar lo inactivo**: el Recommender de GCP identifica VMs infrautilizadas, snapshots huérfanos, IPs sin usar.
5. **Preferir servicios gestionados a VMs**: una VM corriendo PostgreSQL cuesta más en operación humana que Cloud SQL.

```bash
# Ver recomendaciones de rightsizing automáticas de GCP
gcloud recommender recommendations list \
  --project=MI_PROYECTO \
  --location=us-central1 \
  --recommender=google.compute.instance.MachineTypeRecommender \
  --format="table(name,description,primaryImpact.costProjection.cost)"
```

### Principios de fiabilidad

- **Define SLOs** (Service Level Objectives) antes de elegir infraestructura. No necesitas multi-region si tu SLO es 99%.
- **Chaos engineering lite**: usa el pilar de fiabilidad para identificar single points of failure.
- **Cloud Spanner** si necesitas SQL global con 99.999% SLA. Alternativa: Cloud SQL con réplicas de lectura.

---

## 7. 🛠️ Herramientas de visibilidad de costes

| Herramienta | Para qué sirve |
|----|----|
| **Cloud Billing Console** | Vista general de facturas y tendencias |
| **Cost Table / Cost Breakdown** | Desglose por servicio/SKU |
| **BigQuery Billing Export** | Análisis SQL avanzado de costes (labels, tiempo) |
| **Recommender** | Sugerencias automáticas de ahorro |
| **Active Assist** | Suite de recomendaciones (incluye seguridad y rendimiento) |
| **Pricing Calculator** | Estimar coste antes de desplegar |

```bash
# Ver costes del proyecto actual con el SDK (limitado, mejor BigQuery export)
gcloud billing accounts list

# Vincular proyecto a cuenta de facturación
gcloud billing projects link MI_PROYECTO \
  --billing-account=XXXXXX-YYYYYY-ZZZZZZ
```

---

## 8. 🎯 Aplícalo / práctica

Ejercicios concretos para interiorizar este documento:

1. **Activa BigQuery Billing Export**: ve a Billing → Billing export y apúntalo a un dataset en BigQuery. Espera 24h y ejecuta la query de labels del apartado 4.
2. **Crea un budget de $10**: para tu proyecto personal/de pruebas. Configura alerta al 80% y al 100%.
3. **Audita IPs estáticas y VMs olvidadas**: ejecuta los comandos del apartado 5c en tu proyecto.
4. **Estima el coste de tu app web**: usa la Pricing Calculator con los recursos de [[08-contenedores-y-serverless]] y [[06-bases-de-datos]]. ¿Cuánto costaría en prod con 1000 usuarios activos?
5. **Lifecycle en GCS**: crea un bucket de logs con política que mueva a Nearline a los 30 días y borre a los 180.
6. **Lee un pilar del Architecture Framework**: https://cloud.google.com/architecture/framework — elige Reliability y aplícalo a tu arquitectura actual.

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
- [[09-devops-iac-observabilidad]]
- [[10-ia-ml-vertex]]
- [[12-certificaciones-y-aprendizaje]]
- [[MOC_Desarrollo_Software]]
