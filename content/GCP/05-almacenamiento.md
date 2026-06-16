---
title: Almacenamiento en GCP
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/storage, programacion/infraestructura]
type: nota
status: en-progreso
source: claude-code
aliases: [GCP Storage, Cloud Storage GCP, almacenamiento google cloud]
---

# 💾 Almacenamiento en GCP

## ¿Por qué importa la capa de almacenamiento?

En cualquier sistema cloud, el almacenamiento es la capa que **persiste datos más allá de la vida de una instancia de cómputo**. Si el servidor muere, los datos sobreviven (o no, si no elegiste bien). GCP ofrece tres familias con propósitos radicalmente distintos:

| Familia | Analogía hardware | Caso de uso raíz |
|---|---|---|
| **Cloud Storage** (objetos) | Disco duro externo en la nube, acceso por URL | Archivos sueltos, backups, datos para ML, activos web |
| **Persistent Disk** (bloques) | SSD/HDD montado en una VM | Sistema de archivos adjunto a una VM, base de datos |
| **Filestore** (archivos) | NAS compartido en red (NFS) | Varias VMs o pods que necesitan el mismo árbol de directorios |

Elegir mal entre estos tres es uno de los errores de coste más comunes en cloud.

---

## 🪣 Cloud Storage

### ¿Qué es?

**Object storage**: los datos se guardan como objetos (blob + metadatos + URL global única). No hay sistema de archivos real — no puedes hacer `cd` ni `ls` como en un disco. El "árbol de carpetas" que ves en la consola es solo una convención de nombres con `/`.

**Conceptos clave:**
- **Bucket**: contenedor raíz. Nombre globalmente único en todo GCP. Asociado a una región o multi-región.
- **Objeto**: cualquier fichero (hasta 5 TB). Se identifica por `gs://nombre-bucket/ruta/archivo.ext`.
- **Namespace plano**: internamente no hay carpetas; `fotos/2026/imagen.jpg` es un string completo como nombre del objeto.

### Clases de almacenamiento (Storage Classes)

La clase determina el **precio de almacenamiento vs. precio de acceso**. Se fija por objeto (o bucket como default), y puede cambiar mediante lifecycle rules.

| Clase | Mínimo almacenamiento | Coste almacenamiento | Coste recuperación | Caso de uso típico |
|---|---|---|---|---|
| **Standard** | Sin mínimo | ~$0.020/GB/mes | Sin cargo extra | Datos activos, web, ML pipelines |
| **Nearline** | 30 días | ~$0.010/GB/mes | ~$0.01/GB leído | Backups mensuales, logs recientes |
| **Coldline** | 90 días | ~$0.004/GB/mes | ~$0.02/GB leído | Disaster recovery, datos accedidos <1x/año |
| **Archive** | 365 días | ~$0.0012/GB/mes | ~$0.05/GB leído | Archivos legales, cumplimiento normativo |

> **Regla mental**: cuanto menos accedes, más barato guardar pero más caro recuperar. Si recuperas datos Archive de forma inesperada frecuente, pagas más que con Standard.

> **Free tier**: 5 GB en Standard (región US), 1 GB de egress a Internet por mes, 5000 operaciones Class A y 50000 Class B al mes.

### Versionado de objetos

Cuando activas **Object Versioning** en un bucket, al sobreescribir o borrar un objeto GCP lo convierte en una **versión no-current** (conservada). Útil para:
- Protección contra borrado accidental.
- Auditoría de cambios en ficheros de configuración.

```bash
# Activar versionado en un bucket
gcloud storage buckets update gs://mi-bucket --versioning

# Listar todas las versiones de un objeto
gcloud storage ls -a gs://mi-bucket/config.json

# Restaurar versión anterior (copiar versión específica sobre la actual)
gcloud storage cp \
  "gs://mi-bucket/config.json#1718300000000000" \
  gs://mi-bucket/config.json
```

> El número tras `#` es el **generation** (timestamp en microsegundos). Sin versionado, cada objeto tiene solo un generation.

### Lifecycle Rules

Reglas automáticas que cambian la clase o borran objetos según condiciones. Se definen en JSON y se aplican al bucket.

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
        "condition": {"age": 90}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365, "isLive": false}
      }
    ]
  }
}
```

```bash
# Aplicar lifecycle desde archivo JSON
gcloud storage buckets update gs://mi-bucket \
  --lifecycle-file=lifecycle.json

# Ver lifecycle actual
gcloud storage buckets describe gs://mi-bucket \
  --format="json(lifecycle)"
```

### Signed URLs

Una **Signed URL** es una URL temporal que da acceso a un objeto privado sin requerir autenticación de GCP. La firma incluye: quién la emite, para qué objeto, con qué método HTTP, y hasta cuándo expira.

```bash
# Generar signed URL válida por 1 hora (requiere clave de SA o credenciales de usuario)
gcloud storage sign-url gs://mi-bucket/informe.pdf \
  --duration=1h \
  --private-key-file=mi-service-account-key.json

# Con gsutil (forma clásica, equivalente)
gsutil signurl -d 1h mi-service-account-key.json \
  gs://mi-bucket/informe.pdf
```

> Caso típico: backend genera una signed URL, la devuelve al frontend, y el usuario descarga directamente desde GCS sin pasar el archivo por tu servidor. Reduce latencia y coste de egress.

### Comandos gsutil / gcloud storage esenciales

`gcloud storage` es la CLI moderna (reemplaza a `gsutil` gradualmente, aunque `gsutil` sigue funcionando).

```bash
# Crear bucket en región específica
gcloud storage buckets create gs://mi-bucket \
  --location=europe-west1 \
  --default-storage-class=STANDARD

# Subir archivo
gcloud storage cp archivo.csv gs://mi-bucket/datos/

# Subir directorio completo (recursivo)
gcloud storage cp -r ./carpeta/ gs://mi-bucket/destino/

# Listar objetos
gcloud storage ls gs://mi-bucket/

# Descargar objeto
gcloud storage cp gs://mi-bucket/datos/archivo.csv ./local/

# Borrar objeto
gcloud storage rm gs://mi-bucket/datos/viejo.csv

# Sincronizar directorio local -> bucket (como rsync)
gcloud storage rsync ./local/ gs://mi-bucket/sync/ --delete-unmatched-destination-objects

# Ver tamaño de bucket
gcloud storage du gs://mi-bucket/ --summarize

# Cambiar clase de un objeto existente
gcloud storage objects update gs://mi-bucket/archivo.csv \
  --storage-class=NEARLINE
```

---

## 💿 Persistent Disk (PD)

### ¿Qué es?

Almacenamiento de **bloques** (block storage) que se monta en una VM como si fuera un disco físico. El SO ve un dispositivo de bloques (`/dev/sdb`) sobre el que puedes crear particiones, formatear con ext4/xfs, y montar.

**Diferencia clave con Cloud Storage**: los datos residen en un sistema de archivos real. Puedes usarlo como volumen para PostgreSQL, archivos de trabajo de un proceso, etc.

### Tipos de Persistent Disk

| Tipo | Latencia | IOPS max | Precio relativo | Cuándo usarlo |
|---|---|---|---|---|
| **Standard (pd-standard)** | Alta (~ms) | ~7500 | Bajo | Datos fríos, backups de VM, dev/test |
| **Balanced (pd-balanced)** | Media | ~80000 | Medio | Carga de trabajo general, default recomendado |
| **SSD (pd-ssd)** | Baja (<1ms) | ~100000 | Alto | Bases de datos OLTP, alta concurrencia |
| **Extreme (pd-extreme)** | Muy baja | Configurable (hasta 120000) | Muy alto | Cargas críticas de BD, SAP HANA |

```bash
# Crear disco SSD de 100 GB en la misma zona que la VM
gcloud compute disks create mi-disco-ssd \
  --size=100GB \
  --type=pd-ssd \
  --zone=europe-west1-b

# Adjuntar a una VM existente
gcloud compute instances attach-disk mi-vm \
  --disk=mi-disco-ssd \
  --zone=europe-west1-b

# Dentro de la VM: formatear y montar (solo la primera vez)
# sudo mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/sdb
# sudo mount -o discard,defaults /dev/sdb /mnt/datos
```

**Notas importantes:**
- El **boot disk** (disco del SO) es siempre un PD.
- Un PD puede adjuntarse a **múltiples VMs en modo lectura**, pero solo a una en modo escritura.
- Las snapshots de PD van a Cloud Storage (son incrementales, puedes programarlas).

```bash
# Crear snapshot de un disco
gcloud compute snapshots create snap-$(date +%Y%m%d) \
  --source-disk=mi-disco-ssd \
  --source-disk-zone=europe-west1-b

# Programar snapshots automáticas
gcloud compute resource-policies create snapshot-schedule mi-politica \
  --region=europe-west1 \
  --daily-schedule \
  --start-time=03:00 \
  --max-retention-days=7
```

---

## 📁 Filestore

### ¿Qué es?

**File storage gestionado**: un servidor NFS (Network File System) completamente manejado por GCP. Varios clientes (VMs, pods de GKE) pueden montar el mismo sistema de archivos simultáneamente con acceso de lectura/escritura.

**¿Por qué NFS y no Cloud Storage?** Porque algunas aplicaciones legacy, frameworks de ML o pipelines necesitan un sistema de archivos POSIX real con semántica de directorios, permisos, locks de archivo, etc. Cloud Storage no lo ofrece.

### Tiers de Filestore

| Tier | Capacidad mínima | Rendimiento | Precio | Cuándo |
|---|---|---|---|---|
| **Basic HDD** | 1 TB | ~180 MB/s | Bajo | Dev, pruebas, workloads ligeros |
| **Basic SSD** | 2.5 TB | ~1.2 GB/s | Medio | Producción general |
| **Zonal** | 1 TB | Hasta 1 GB/s | Medio | Alta disponibilidad zonal |
| **Enterprise** | 1 TB | Hasta 2.5 GB/s | Alto | Producción crítica, multi-zona |

```bash
# Crear instancia de Filestore (Basic SSD, 2.5 TB)
gcloud filestore instances create mi-nfs \
  --tier=BASIC_SSD \
  --file-share=name=datos,capacity=2560GB \
  --network=name=default \
  --zone=europe-west1-b

# Ver la IP del servidor NFS
gcloud filestore instances describe mi-nfs \
  --zone=europe-west1-b \
  --format="json(networks)"

# Montar desde una VM (dentro de la VM)
# sudo mount -t nfs 10.X.X.X:/datos /mnt/compartido
```

---

## 🗺️ ¿Cuándo usar cada uno? — Tabla de decisión

| Necesito... | Usa |
|---|---|
| Guardar archivos estáticos para web (imágenes, JS, CSS) | Cloud Storage Standard |
| Backups diarios que rara vez accedo | Cloud Storage Nearline / Coldline |
| Archivos de cumplimiento legal por años | Cloud Storage Archive |
| Disco del SO de una VM | Persistent Disk (Balanced o SSD) |
| Base de datos PostgreSQL/MySQL en una VM | Persistent Disk SSD o Extreme |
| Dataset de ML compartido entre múltiples workers | Cloud Storage (gs://) |
| App legacy que necesita `mount` NFS real | Filestore |
| Varios pods de GKE leen/escriben el mismo directorio | Filestore |
| Compartir disco entre VMs con concurrencia | Filestore (o PD en modo read-only multi) |

---

## ⚠️ Errores y costes comunes

1. **Usar Standard para datos fríos**: si tienes 10 TB de logs que no lees, pagas ~$200/mes vs $12/mes en Archive. El cambio de clase es un comando.

2. **Egress inesperado**: mover datos de GCS a Internet (fuera de GCP) o a otra región tiene coste. Los datos dentro de la misma región son gratuitos. Usa `gcloud storage du` para auditar.

3. **Versioning sin lifecycle de borrado**: activas versioning y en 6 meses tienes el doble de datos porque las versiones antiguas nunca se purgan. Siempre añade una regla `Delete` para versiones `isLive: false`.

4. **PD oversized por defecto**: la gente redondea a 500 GB porque "está bien". Los PD se pueden **ampliar** pero no reducir; empieza con lo justo.

5. **Filestore mínimo 1 TB**: aunque uses 10 GB, pagas 1 TB. Para cantidades pequeñas, Cloud Storage es más económico (si no necesitas semántica POSIX).

6. **Signed URLs con claves de SA en el cliente**: la clave privada nunca debe llegar al frontend. Genera la URL en el backend y devuélvela; la URL ya no requiere la clave para usarse.

---

## 🛠️ Aplícalo / Practica

1. **Lab básico Cloud Storage**:
   - Crea un bucket en `europe-west1`.
   - Sube 3 archivos de distintos tipos.
   - Activa versionado, sobreescribe un archivo, lista las versiones.
   - Aplica una lifecycle rule que mueva objetos a Nearline tras 30 días.
   - Genera una signed URL válida 10 minutos y ábrela en el navegador.

2. **Lab Persistent Disk**:
   - Crea una VM `e2-micro` con disco boot `pd-balanced` de 20 GB.
   - Añade un segundo disco `pd-standard` de 50 GB.
   - Dentro de la VM: formatea, monta en `/mnt/datos`, crea un archivo de prueba.
   - Toma un snapshot manual y verifica que aparece en la consola.

3. **Lab Filestore** (opcional, tiene coste):
   - Crea una instancia Filestore Basic HDD de 1 TB.
   - Monta en dos VMs distintas a la vez.
   - Crea un archivo desde VM-1 y verifica que VM-2 lo ve.

4. **Optimización de costes**:
   - Usa `gcloud storage ls -l gs://tu-bucket/ | awk '{sum += $1} END {print sum/1024/1024/1024 " GB"}'` para auditar tamaño.
   - Identifica objetos Standard con más de 90 días y calcula el ahorro de moverlos a Coldline.

---

## Conexiones

- [[MOC_GCP]]
- [[01-fundamentos-cloud-y-gcp]]
- [[02-iam-y-seguridad]]
- [[03-computo]]
- [[04-redes]]
- [[06-bases-de-datos]]
- [[07-datos-y-analitica]]
- [[08-contenedores-y-serverless]]
- [[09-devops-iac-observabilidad]]
- [[MOC_Desarrollo_Software]]
