---
title: Bases de datos en GCP
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/bases-de-datos, programacion/sql, programacion/nosql]
type: nota
status: en-progreso
source: claude-code
aliases: [GCP databases, bases de datos GCP, gcp-bd]
---

# 🗄️ Bases de datos en GCP

## ¿Por qué importa elegir bien la base de datos?

La base de datos es el componente con mayor "lock-in" de un sistema: cambiarla en producción es caro y lento. GCP ofrece un abanico muy amplio —desde MySQL gestionado hasta una base relacional que corre en múltiples continentes sin conflictos— y la elección correcta depende de **tres ejes**:

1. **Modelo de datos**: ¿relacional (filas y columnas) o no-relacional (documentos, clave-valor, wide-column)?
2. **Escala y latencia**: ¿cuántos QPS? ¿latencia de milisegundos o microsegundos?
3. **Consistencia**: ¿necesitas ACID fuerte o puedes tolerar eventual consistency a cambio de escala masiva?

> **Jerga rápida**
> - **ACID**: Atomicity, Consistency, Isolation, Durability — garantías de una transacción relacional clásica.
> - **QPS**: Queries per second, medida de carga.
> - **Sharding**: partir una tabla en fragmentos distribuidos entre servidores para escalar horizontalmente.
> - **Wide-column**: estructura donde cada fila puede tener columnas distintas; óptima para datos dispersos y series temporales.

---

## 🗺️ Panorama de servicios

```
┌─────────────────────────────────────────────────────────────┐
│                  GCP Database Portfolio                     │
│                                                             │
│  RELACIONAL                      NO-RELACIONAL              │
│  ┌──────────────┐                ┌──────────────┐           │
│  │  Cloud SQL   │  ← familiar    │  Firestore   │  docs     │
│  │  (MySQL/PG)  │                │  (NoSQL)     │           │
│  ├──────────────┤                ├──────────────┤           │
│  │   AlloyDB    │  ← PG turbo    │  Bigtable    │  cols     │
│  ├──────────────┤                ├──────────────┤           │
│  │   Spanner    │  ← global ACID │  Memorystore │  cache    │
│  └──────────────┘                └──────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🐘 Cloud SQL — El punto de entrada relacional

### ¿Qué problema resuelve?

Tener MySQL o PostgreSQL sin gestionar el servidor: GCP se ocupa de parches, backups, réplicas y failover. Equivale a **Amazon RDS** en AWS.

### Cuándo usarlo

- Aplicación web/backend clásica (CRUD, Django, FastAPI, Rails…)
- Migración lift-and-shift de una BD on-premise
- Equipo que ya conoce SQL y no necesita escala masiva (< ~10 000 QPS)

### Características clave

| Característica | Detalle |
|---|---|
| Motores | MySQL 5.7/8.0, PostgreSQL 13-16, SQL Server |
| Alta disponibilidad | Instancia standby en otra zona; failover ~30 s |
| Réplicas de lectura | Hasta 10 réplicas; pueden estar en otras regiones |
| Almacenamiento | SSD autoescalable, hasta 64 TB |
| Backups | Automáticos diarios + point-in-time recovery (PITR) |
| Conexión segura | Cloud SQL Auth Proxy (no exponer puerto 5432/3306 al exterior) |

### Cloud SQL Auth Proxy — Patrón correcto de conexión

```bash
# Descargar el proxy
curl -o cloud-sql-proxy \
  https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.11.4/cloud-sql-proxy.linux.amd64
chmod +x cloud-sql-proxy

# Iniciar túnel local (el proxy autentica con Application Default Credentials)
./cloud-sql-proxy "mi-proyecto:us-central1:mi-instancia-sql" --port 5432

# Ahora conéctate como si fuera localhost
psql "host=127.0.0.1 port=5432 dbname=mi_bd user=mi_usuario"
```

> No abras el puerto 5432 en el firewall. Usa siempre el proxy o Private IP.

### Comandos gcloud básicos

```bash
# Crear instancia PostgreSQL
gcloud sql instances create mi-bd \
  --database-version=POSTGRES_15 \
  --tier=db-g1-small \
  --region=europe-west1 \
  --storage-auto-increase

# Crear base de datos dentro de la instancia
gcloud sql databases create app_db --instance=mi-bd

# Crear usuario
gcloud sql users create app_user \
  --instance=mi-bd \
  --password=CAMBIAR_ESTO

# Ver instancias
gcloud sql instances list
```

### Free tier / coste

- No tiene free tier permanente. La instancia más pequeña (`db-f1-micro`, solo dev/test) cuesta ~7 USD/mes.
- **Error frecuente**: dejar réplicas de lectura encendidas en un entorno de desarrollo — cada réplica cobra igual que la primaria.

---

## ⚡ AlloyDB — PostgreSQL con superpoderes

### ¿Qué lo diferencia de Cloud SQL?

AlloyDB es la respuesta de GCP al **Aurora de AWS**: PostgreSQL 100 % compatible pero con una arquitectura de almacenamiento distribuido propia que separa compute de storage.

| Métrica | Cloud SQL PG | AlloyDB |
|---|---|---|
| Velocidad OLTP | Baseline | ~2× más rápido |
| Velocidad analítica (OLAP) | Baseline | ~100× más rápido (columnar cache) |
| Disponibilidad SLA | 99,95 % | 99,99 % |
| Cache inteligente | No | Sí (ML-driven buffer pool) |
| Precio | Menor | Mayor (~2-3× Cloud SQL) |

### Cuándo usarlo

- Workloads PostgreSQL exigentes: e-commerce, SaaS con muchos usuarios concurrentes.
- Quieres análisis sobre datos operacionales sin replicar a BigQuery (AlloyDB AI columnar).
- Necesitas SLA de cuatro nueves.

```bash
# Crear cluster AlloyDB
gcloud alloydb clusters create mi-cluster \
  --region=us-central1 \
  --password=CAMBIAR_ESTO

# Crear instancia primaria
gcloud alloydb instances create mi-instancia \
  --instance-type=PRIMARY \
  --cpu-count=2 \
  --cluster=mi-cluster \
  --region=us-central1
```

---

## 🌐 Cloud Spanner — Relacional distribuido a escala global

### El problema que resuelve

Los sistemas relacionales clásicos escalan *verticalmente* (más RAM/CPU) hasta un límite. Para escala horizontal real con ACID fuerte, la industria históricamente elegía NoSQL y sacrificaba consistencia. **Spanner elimina ese trade-off**: es relacional, ACID, y escala horizontalmente de forma global.

> Analogía hardware: es como tener múltiples microcontroladores sincronizados con un reloj de alta precisión (TrueTime) en lugar de un único procesador más potente.

### Casos de uso

- Fintech, gaming, reservas en tiempo real: necesitan transacciones fuertes a millones de QPS.
- Aplicación que sirve usuarios en múltiples continentes con latencia baja en todos.
- Cuando Bigtable/Firestore no son suficientes por necesitar JOINs y transacciones.

### Conceptos clave

| Concepto | Qué es |
|---|---|
| **TrueTime** | Reloj atómico + GPS interno de Google para ordenar transacciones globalmente |
| **Interleaving** | Colocar filas de tabla hija físicamente junto a la fila padre (optimiza JOINs de padre-hijo) |
| **Splits** | Fragmentos automáticos de datos; Spanner los gestiona sin intervención manual |
| **Nodes** | Unidad de compute; 1 node ≈ 2000 QPS lectura, 1800 QPS escritura |

```bash
# Crear instancia Spanner (regional, más barata)
gcloud spanner instances create mi-spanner \
  --config=regional-us-central1 \
  --processing-units=100 \
  --description="Dev instance"

# Crear base de datos con DDL
gcloud spanner databases create mi-db \
  --instance=mi-spanner \
  --ddl="CREATE TABLE Usuarios (
    UserId STRING(36) NOT NULL,
    Email STRING(255),
    CreadoEn TIMESTAMP
  ) PRIMARY KEY (UserId)"

# Ejecutar consulta SQL
gcloud spanner databases execute-sql mi-db \
  --instance=mi-spanner \
  --sql="SELECT * FROM Usuarios LIMIT 10"
```

### Coste — el más caro de GCP databases

- Mínimo ~65 USD/mes (100 processing units). **No tiene free tier real.**
- Alternativa económica para dev/test: **Spanner Emulator** (corre local en Docker).

```bash
# Emulador local para desarrollo
docker pull gcr.io/cloud-spanner-emulator/emulator
docker run -p 9010:9010 -p 9020:9020 gcr.io/cloud-spanner-emulator/emulator
```

---

## 📄 Firestore — Documentos para apps web/mobile

### ¿Qué es?

Base de datos NoSQL de **documentos** (como MongoDB) gestionada, serverless y con sincronización en tiempo real. Ideal para apps donde los datos se leen desde el cliente directamente.

> **Documento** = objeto JSON con campos anidados. Se agrupa en **colecciones**. No hay schema fijo.

### Dos modos (elige al crear, no se puede cambiar)

| Modo | Cuándo |
|---|---|
| **Native** | Apps móviles/web con SDK cliente, tiempo real, offline sync |
| **Datastore** | Apps server-side puras, migración desde Cloud Datastore legacy |

### Características

- **Serverless**: escala a cero, pagas por operaciones (lecturas/escrituras/borrados), no por instancia.
- **Consultas**: índices automáticos; consultas compuestas requieren índice compuesto manual.
- **Transacciones**: ACID dentro de un documento o entre documentos (limitado).
- **Tiempo real**: listeners que actualizan la UI del cliente al cambiar el dato.

```python
# Python — SDK server-side
from google.cloud import firestore

db = firestore.Client()

# Escribir documento
db.collection("usuarios").document("user-001").set({
    "nombre": "Daniel",
    "email": "usuario@ejemplo.com",
    "activo": True
})

# Leer documento
doc = db.collection("usuarios").document("user-001").get()
print(doc.to_dict())

# Consulta
usuarios_activos = db.collection("usuarios").where("activo", "==", True).stream()
for u in usuarios_activos:
    print(u.to_dict())
```

### Limitaciones importantes

- **No JOINs**: si necesitas cruzar colecciones, lo haces en el cliente o con varias queries.
- **1 escritura/segundo por documento**: evitar documentos contadores muy frecuentes (usar sharded counter).
- **Consultas limitadas**: no puedes hacer `OR` entre campos distintos sin índice compuesto; no hay `!=` eficiente.

### Free tier (generoso)

- 1 GB almacenamiento
- 50 000 lecturas/día, 20 000 escrituras/día, 20 000 borrados/día

---

## 🔢 Bigtable — Wide-column para escala masiva

### ¿Qué problema resuelve?

Series temporales, IoT, logs, datos de sensores, analítica operacional a **miles de millones de filas**. Es la base de datos interna que Google usó para Gmail, Google Search, y Maps.

> Equivalente AWS: **DynamoDB** (aunque el modelo interno es diferente); el open-source equivalente es **Apache HBase** y **Apache Cassandra**.

### Modelo de datos

```
Table: sensores_temperatura
│
├── Row Key: "sensor-001#2026-06-14T10:00:00"
│   └── Column Family: "datos"
│       ├── temperatura: 23.5
│       └── humedad: 67.2
│
└── Row Key: "sensor-001#2026-06-14T10:00:01"
    └── Column Family: "datos"
        └── temperatura: 23.6
```

- **Row Key**: el único índice nativo. Su diseño es crítico para el rendimiento.
- **Column Family**: agrupación lógica de columnas; se define al crear la tabla.
- **No hay SQL**: se accede con la API de Bigtable o librerías HBase.

### Cuándo usarlo (y cuándo no)

| Usar Bigtable | No usar Bigtable |
|---|---|
| > 1 TB de datos estructurados | < 1 TB (usa Firestore o Cloud SQL) |
| Alta velocidad de escritura (> 1 000 QPS) | Necesitas SQL/JOINs |
| Series temporales, IoT, logs | Necesitas transacciones ACID multi-fila |
| Workload predecible de acceso por row key | Datos relacionales normalizados |

```bash
# Crear instancia Bigtable
gcloud bigtable instances create mi-bigtable \
  --display-name="Mi Bigtable" \
  --cluster-config=id=mi-cluster,zone=us-central1-a,nodes=1

# Crear tabla y column family (con cbt CLI)
cbt -project mi-proyecto -instance mi-bigtable createtable sensores
cbt -project mi-proyecto -instance mi-bigtable createfamily sensores datos

# Escribir/leer (cbt es para pruebas; en producción usa SDK)
cbt -project mi-proyecto -instance mi-bigtable set sensores \
  "sensor-001#2026-06-14" datos:temperatura=23.5

cbt -project mi-proyecto -instance mi-bigtable read sensores
```

### Coste

- Mínimo 1 nodo SSD: ~65 USD/mes + almacenamiento.
- **Sin free tier permanente**. Usa el emulador para desarrollo:

```bash
gcloud beta emulators bigtable start
```

---

## 🚀 Memorystore — Redis/Valkey gestionado (caché)

### ¿Qué es?

Redis (ahora también Valkey, el fork open-source) gestionado por GCP. Equivale a **ElastiCache** en AWS. Sirve como:

- **Caché**: evitar queries repetidas a Cloud SQL/Spanner.
- **Session store**: sesiones de usuario en apps web.
- **Pub/Sub simple**: mensajes entre microservicios de baja latencia.
- **Rate limiting**: contadores atómicos.

### Características

| Característica | Detalle |
|---|---|
| Latencia | Sub-milisegundo (datos en RAM) |
| Versiones | Redis 6/7, Valkey 7/8 |
| Modos | Standalone (hasta 300 GB) o Cluster (hasta 3 TB) |
| Persistencia | RDB snapshots opcionales; no es una BD primaria |
| Réplicas | Hasta 5 réplicas de lectura en Cluster mode |
| VPC | Siempre dentro de una VPC; no tiene IP pública |

```bash
# Crear instancia Redis
gcloud redis instances create mi-cache \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0 \
  --tier=basic

# Ver detalles (IP interna para conectar)
gcloud redis instances describe mi-cache --region=us-central1

# Conectar desde una VM en la misma VPC
redis-cli -h <IP_INTERNA> -p 6379
```

```python
# Python — uso típico como caché
import redis
import json

r = redis.Redis(host="10.0.0.3", port=6379)

# Cache-aside pattern
def get_usuario(user_id: str):
    cache_key = f"usuario:{user_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # Si no está en caché, consultar DB
    usuario = db.query(f"SELECT * FROM usuarios WHERE id = '{user_id}'")
    r.setex(cache_key, 3600, json.dumps(usuario))  # TTL 1 hora
    return usuario
```

### Coste

- ~0.049 USD/GB/hora para Basic tier (1 GB ≈ 35 USD/mes).
- **Sin free tier**.

---

## 📊 Tabla comparativa — ¿Qué servicio elegir?

| Servicio | Modelo | Escala | Consistencia | Latencia | Precio relativo | Caso típico |
|---|---|---|---|---|---|---|
| **Cloud SQL** | Relacional | Media (TB) | ACID fuerte | ms | $ | Web/backend clásico, migraciones |
| **AlloyDB** | Relacional PG | Alta (TB) | ACID fuerte | ms | $$$ | SaaS exigente, OLTP+OLAP mixto |
| **Spanner** | Relacional dist. | Muy alta (PB) | ACID global | ms (multi-región) | $$$$ | Fintech, gaming global |
| **Firestore** | Documentos | Alta | Eventual / fuerte doc | ms | $ (serverless) | Apps móvil/web, datos jerárquicos |
| **Bigtable** | Wide-column | Masiva (PB) | Fuerte por fila | ms | $$$ | IoT, series temporales, logs |
| **Memorystore** | Clave-valor RAM | Media | No persistente | µs-ms | $$ | Caché, sesiones, rate limiting |

### Árbol de decisión rápido

```
¿Necesitas SQL y JOINs?
├── Sí → ¿Escala global o >10 000 QPS escritura?
│         ├── Sí → Spanner
│         ├── No + rendimiento PG máximo → AlloyDB
│         └── No → Cloud SQL
└── No → ¿Qué acceso predomina?
          ├── Por clave + series temporales/IoT masivo → Bigtable
          ├── Documentos jerarquizados / app móvil → Firestore
          └── Caché / sesiones → Memorystore
```

---

## 🔗 Integración con otros servicios GCP

- **Cloud SQL → Cloud Run**: conéctate con el socket Unix del proxy (sin abrir puertos).
- **Firestore → Cloud Functions**: triggers nativos cuando un documento cambia.
- **Bigtable → Dataflow**: pipeline de procesamiento de streams; también exporta a BigQuery.
- **Spanner → BigQuery**: federación; puedes hacer queries en BigQuery sobre datos en Spanner sin mover datos.
- **Memorystore → GKE**: acceso por IP privada desde pods en la misma VPC.

```bash
# Conectar Cloud Run a Cloud SQL con socket Unix
gcloud run services update mi-servicio \
  --add-cloudsql-instances mi-proyecto:us-central1:mi-bd \
  --set-env-vars DB_HOST=/cloudsql/mi-proyecto:us-central1:mi-bd
```

---

## ⚠️ Errores y costes comunes

| Error | Consecuencia | Prevención |
|---|---|---|
| Dejar réplicas Cloud SQL en dev | Costo doble o triple | Destruir réplicas fuera de horario de trabajo |
| Row key en Bigtable con timestamp como prefijo | Hotspot: todo el tráfico va al mismo nodo | Invertir el timestamp o usar hash como prefijo |
| No poner TTL en Memorystore | Memoria llena, evictions inesperadas | `SETEX` o política `allkeys-lru` |
| Índices compuestos ausentes en Firestore | Queries fallan en producción aunque pasen en dev | Probar con datos reales; revisar los logs de Firestore |
| Spanner con un solo nodo para producción | Sin alta disponibilidad real | Mínimo 3 nodos para producción |
| Cloud SQL sin PITR activado | Pérdida de datos ante error humano | Activar backups automáticos + PITR desde el inicio |

---

## 🛠️ Aplícalo / practica

### Ejercicio 1 — Cloud SQL con proxy (30 min)
1. Crea una instancia Cloud SQL PostgreSQL en `us-central1` con `db-f1-micro`.
2. Crea una base de datos y un usuario.
3. Conecta con el Auth Proxy desde tu máquina.
4. Crea una tabla `productos` con al menos 3 columnas y ejecuta queries SQL básicas.

### Ejercicio 2 — Firestore serverless (20 min)
1. Activa Firestore en modo Native.
2. Usa el SDK de Python para escribir 5 documentos en una colección `inventario`.
3. Haz una consulta filtrada por un campo.
4. Observa el consumo de cuota en la consola (debe ser cero o mínimo con el free tier).

### Ejercicio 3 — Memorystore cache-aside (45 min)
1. Crea una instancia Memorystore Basic (1 GB).
2. Despliega un script Python en una VM que implemente el patrón cache-aside sobre Cloud SQL.
3. Mide la latencia de la primera query (sin caché) vs. la segunda (con caché) con `time`.

### Ejercicio 4 — Bigtable diseño de row key (conceptual, 20 min)
Dado el dataset: `sensor_id`, `timestamp`, `valor`. Diseña un row key que:
- Evite hotspots de escritura.
- Permita leer todos los valores de un sensor en un rango de tiempo eficientemente.
Pista: considera `sensor_id#timestamp_invertido`.

---

## Conexiones

- [[MOC_GCP]]
- [[01-fundamentos-cloud-y-gcp]]
- [[02-iam-y-seguridad]]
- [[03-computo]]
- [[04-redes]]
- [[05-almacenamiento]]
- [[07-datos-y-analitica]]
- [[08-contenedores-y-serverless]]
- [[09-devops-iac-observabilidad]]
- [[11-costes-y-buenas-practicas]]
- [[MOC_Desarrollo_Software]]
