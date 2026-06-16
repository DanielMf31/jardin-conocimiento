---
title: Fundamentos de cloud y GCP
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/infraestructura, programacion/devops]
type: nota
status: en-progreso
source: claude-code
aliases: [fundamentos gcp, intro cloud, cloud basics]
---

# ☁️ Fundamentos de cloud y GCP

## Por qué existe la nube (el problema que resuelve)

Antes de la nube, montar una app en producción implicaba comprar servidores físicos, instalarlos en un datacenter, pagar por la capacidad máxima posible (aunque el 80% del tiempo la usaras al 10%), y gestionar el hardware tú. Esto tiene tres problemas graves:

- **CAPEX elevado**: pagas el servidor aunque no lo uses.
- **Escalado lento**: si tienes pico de tráfico, no puedes añadir capacidad en minutos.
- **Operación especializada**: necesitas equipo de sistemas para mantener el hardware.

La nube resuelve esto convirtiendo infraestructura en **servicio por uso** (pay-as-you-go). Alquilas capacidad de cómputo, almacenamiento y red de los datacenters de Google/AWS/Azure, y pagas solo lo que consumes.

---

## 🏗️ IaaS / PaaS / SaaS — los tres niveles del servicio

Piénsalo como cuánto control tienes sobre la "pila" vs. cuánto gestiona el proveedor.

| Capa | Quien gestiona qué | Ejemplo en GCP | Ejemplo fuera de GCP |
|---|---|---|---|
| **IaaS** (Infrastructure as a Service) | Tú: SO, runtime, apps. Proveedor: hardware, red física | Compute Engine (VMs) | AWS EC2 |
| **PaaS** (Platform as a Service) | Tú: solo tu código/datos. Proveedor: SO, runtime, escalado | App Engine, Cloud Run | Heroku, AWS Elastic Beanstalk |
| **SaaS** (Software as a Service) | Tú: solo configurar y usar. Proveedor: todo | Gmail, Google Workspace | Salesforce, Slack |

**Regla de oro**: más arriba en la pila = menos control pero menos trabajo operacional. Para una startup o un proyecto personal, PaaS/SaaS te libera tiempo; para control fino (configuración de kernel, GPUs específicas), necesitas IaaS.

---

## 🔐 Modelo de responsabilidad compartida

Este concepto es crítico para seguridad y aparece en cualquier certificación.

La idea es simple: **hay cosas que Google garantiza y cosas que tú debes garantizar**. El límite depende del modelo de servicio.

```
RESPONSABILIDAD DEL CLIENTE ↑
┌─────────────────────────────────────────────┐
│  Datos del cliente                          │ ← SIEMPRE tuya
│  Control de acceso (IAM, permisos)          │ ← SIEMPRE tuya
├────────────────────┬────────────┬───────────┤
│  Configuración SO  │    Tuya    │  Google   │ IaaS vs PaaS
│  Runtime/librerías │    Tuya    │  Google   │
├────────────────────┴────────────┴───────────┤
│  Red física, hardware, datacenters          │ ← SIEMPRE Google
│  Seguridad física de los edificios          │ ← SIEMPRE Google
└─────────────────────────────────────────────┘
RESPONSABILIDAD DE GOOGLE ↓
```

**Error común**: creer que "está en la nube = está seguro automáticamente". Si configuras mal los permisos de un bucket de Cloud Storage (lo pones público), Google no lo impide. La seguridad de configuración es siempre tu responsabilidad.

---

## 🌍 Regiones y zonas

Google opera su infraestructura en ubicaciones físicas distribuidas por el mundo.

- **Región**: área geográfica que agrupa varios datacenters. Ej: `europe-west1` (Bélgica), `us-central1` (Iowa). Hoy hay más de 40 regiones.
- **Zona**: datacenter específico dentro de una región. Ej: `europe-west1-b`, `europe-west1-c`, `europe-west1-d`. Una región suele tener 3+ zonas.

**Por qué importa:**

| Concepto | Zona única | Multi-zona | Multi-región |
|---|---|---|---|
| Tolerancia a fallos | Baja (si cae la zona, cae todo) | Alta (si cae una zona, las otras siguen) | Muy alta (sobrevive corte regional) |
| Latencia para el usuario | Depende de ubicación | Igual | Puede reducirse acercando al usuario |
| Coste | Base | Ligeramente mayor (replicación) | Mayor (tráfico entre regiones se paga) |

**Regla práctica**: pon siempre tus recursos en al menos 2 zonas de la misma región para alta disponibilidad sin coste de tráfico inter-regional. Multi-región solo para datos críticos o usuarios en continentes distintos.

---

## 🏢 Jerarquía de recursos GCP

Este es el concepto más importante del capítulo. GCP organiza todo en una jerarquía de 4 niveles:

```
Organización  (ej: empresa.com)
│
├── Carpeta  (ej: "Producción", "Desarrollo")
│   │
│   └── Carpeta  (anidables)
│       │
│       └── Proyecto  ← UNIDAD CLAVE
│           │
│           ├── Compute Engine VM
│           ├── Cloud Storage Bucket
│           ├── Cloud SQL Database
│           └── ... (todos los recursos GCP)
│
└── Proyecto  (también puede colgar directo de la Org)
```

### Por qué el PROYECTO es la unidad clave

Cada recurso GCP existe dentro de exactamente un proyecto. El proyecto es la frontera de:

- **Facturación**: cada proyecto se vincula a una cuenta de facturación. Sabes exactamente cuánto cuesta cada proyecto.
- **IAM y permisos**: los permisos se gestionan por proyecto (aunque también se heredan de arriba).
- **APIs habilitadas**: en un proyecto nuevo, casi ninguna API está activa. Debes habilitar las que necesitas (`Cloud Run API`, `BigQuery API`, etc.).
- **Cuotas**: los límites de uso son por proyecto.
- **Identificadores únicos**: cada proyecto tiene un `Project ID` (string único global, inmutable) y un `Project Number` (numérico). El Project ID es lo que usarás en comandos.

```bash
# Ver el proyecto activo actual
gcloud config get-value project

# Listar todos tus proyectos
gcloud projects list

# Cambiar de proyecto activo
gcloud config set project MI_PROJECT_ID
```

### Organización y Carpetas (nivel empresa)

- **Organización**: se crea automáticamente si tienes un dominio de Google Workspace o Cloud Identity. Es el nodo raíz; los administradores de la org pueden ver/controlar todo.
- **Carpetas**: agrupación lógica de proyectos. Útil para separar entornos (`prod/`, `dev/`, `staging/`) o equipos. Las políticas IAM aplicadas a una carpeta se heredan en cascada.

**Sin cuenta de empresa**: si usas GCP con una cuenta personal de Gmail, no tienes Organización — tus proyectos viven "sueltos" bajo tu cuenta. Funciona bien para proyectos personales/aprendizaje.

---

## 💳 Facturación

- **Cuenta de facturación**: entidad separada del proyecto. Un proyecto debe estar vinculado a una cuenta de facturación para usar recursos de pago. Una cuenta de facturación puede pagar N proyectos.
- **Free Tier**: GCP tiene un nivel gratuito **permanente** (no expira) para ciertos servicios:
  - 1 VM `e2-micro` al mes (us-east1, us-west1, us-central1)
  - 5 GB en Cloud Storage
  - 10 GB en BigQuery al mes
  - Cloud Functions: 2M invocaciones/mes
- **$300 de crédito inicial**: cuenta nueva recibe $300 para usar en 90 días (oferta varía, verificar).
- **Presupuestos y alertas**: configura siempre un budget alert en Billing → Budgets. Sin esto, un recurso mal configurado puede generar costes inesperados.

```bash
# Vincular proyecto a cuenta de facturación (requiere permisos de billing)
gcloud billing projects link MI_PROJECT_ID \
  --billing-account=XXXXXX-XXXXXX-XXXXXX
```

---

## 🖥️ Formas de interactuar con GCP

### 1. Cloud Console (web)

`console.cloud.google.com` — interfaz gráfica. Útil para explorar, ver dashboards, hacer cosas puntuales. No es reproducible ni automatizable, así que no es suficiente para trabajo serio.

### 2. gcloud CLI

La herramienta de línea de comandos principal. Instalable localmente. Agrupa comandos por servicio:

```bash
# Autenticación inicial
gcloud auth login
gcloud auth application-default login  # para SDKs y librerías

# Estructura general de un comando gcloud
gcloud <grupo> <subcomando> <recurso> [flags]
# Ej:
gcloud compute instances list
gcloud storage buckets create gs://mi-bucket --location=europe-west1
gcloud run deploy mi-servicio --image=gcr.io/mi-project/mi-imagen

# Ver configuración activa (proyecto, región, zona por defecto)
gcloud config list
```

**Configuración por defecto** — evita repetir flags en cada comando:

```bash
gcloud config set compute/region europe-west1
gcloud config set compute/zone europe-west1-b
```

### 3. Cloud Shell

Terminal en el navegador (accesible desde el icono `>_` en la Console). Viene con `gcloud`, `kubectl`, `terraform`, `git`, Python, Go, Node preinstalados. Tiene 5 GB de disco persistente en `$HOME`. Ideal para no instalar nada localmente, aunque se desconecta si llevas >20 min inactivo.

```bash
# Dentro de Cloud Shell, ya estás autenticado automáticamente
gcloud projects list  # funciona sin login
```

### 4. APIs REST y SDKs

Cada servicio de GCP expone una API REST. Los SDKs oficiales (Python, Go, Java, Node...) son wrappers sobre esa API. Útil para integrar GCP en tu código.

```python
# Ejemplo: listar buckets con el SDK de Python
from google.cloud import storage

client = storage.Client()
for bucket in client.list_buckets():
    print(bucket.name)
```

Las credenciales las gestiona `application-default login` (para desarrollo local) o el Service Account vinculado al recurso (para producción en GCP).

### Comparativa: cuándo usar cada uno

| Herramienta | Cuándo usarla |
|---|---|
| Console web | Exploración, aprendizaje, dashboards, cosas puntuales |
| gcloud CLI | Trabajo diario, scripts, CI/CD |
| Cloud Shell | Acceso rápido sin instalar nada, demostraciones |
| SDK / API | Integración en código de aplicación |
| Terraform / IaC | Infraestructura reproducible a escala (ver [[09-devops-iac-observabilidad]]) |

---

## 🚀 Primer contacto práctico

Secuencia mínima para tener GCP operativo:

```bash
# 1. Instalar gcloud SDK localmente (si no usas Cloud Shell)
# https://cloud.google.com/sdk/docs/install

# 2. Autenticarte
gcloud auth login
gcloud auth application-default login

# 3. Crear un proyecto nuevo
gcloud projects create mi-primer-proyecto-gcp --name="Mi Primer Proyecto GCP"

# 4. Establecerlo como activo
gcloud config set project mi-primer-proyecto-gcp

# 5. Ver qué APIs hay activas (pocas, por defecto)
gcloud services list --enabled

# 6. Habilitar una API (ej: Cloud Storage)
gcloud services enable storage.googleapis.com

# 7. Crear un bucket de prueba
gcloud storage buckets create gs://mi-bucket-prueba-gcp \
  --location=europe-west1

# 8. Subir un fichero de prueba
echo "hola GCP" > test.txt
gcloud storage cp test.txt gs://mi-bucket-prueba-gcp/

# 9. Listar el contenido
gcloud storage ls gs://mi-bucket-prueba-gcp/

# 10. Limpiar (evitar costes)
gcloud storage rm -r gs://mi-bucket-prueba-gcp
```

**Punto de control**: si llegaste hasta el paso 9 y viste tu fichero listado, tienes el ciclo completo funcionando: autenticación → proyecto → API → recurso → operación.

---

## ⚠️ Errores y costes comunes

| Error | Consecuencia | Cómo evitarlo |
|---|---|---|
| No poner presupuesto/alerta de billing | Sorpresa en la factura | Billing → Budgets & Alerts → crear alerta al 50/90/100% |
| Dejar VMs encendidas sin usar | Coste continuo aunque no haya tráfico | Apagar o usar Cloud Run (paga solo por petición) |
| Bucket público accidentalmente | Exposición de datos y posible tráfico de egreso | Revisar IAM del bucket; usar `Uniform bucket-level access` |
| Project ID ≠ Project Name | Confusión en scripts | El ID es inmutable y globalmente único; el Name es solo etiqueta |
| No habilitar la API antes de usar el servicio | Error 403 o "API not enabled" | `gcloud services enable X.googleapis.com` |

---

## Conexiones

- [[MOC_GCP]]
- [[02-iam-y-seguridad]]
- [[03-computo]]
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
- [[MOC_Ciberseguridad]]
