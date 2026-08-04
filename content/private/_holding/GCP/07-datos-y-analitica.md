---
title: Datos y Analítica en GCP
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/datos, ciencia-datos/ingenieria-datos, ciencia-datos/analitica]
type: nota
status: en-progreso
source: claude-code
aliases: [GCP datos, BigQuery GCP, data engineering GCP]
---

# Datos y Analítica en GCP

## ¿Por qué existe este stack?

En cualquier empresa real los datos no nacen limpios ni en el sitio correcto. El problema que resuelve GCP aquí es el **pipeline de datos**: cómo llevar información desde sus fuentes (sensores, apps, logs, APIs) hasta un lugar donde puedas hacerle preguntas de negocio con SQL o modelos ML.

GCP domina este espacio. BigQuery es consistentemente uno de los data warehouses más valorados del mercado, y el stack completo (Pub/Sub + Dataflow + BigQuery + Looker) cubre el ciclo completo sin que tú gestiones servidores.

```
[FUENTES]       [INGESTA]      [PROCESAMIENTO]   [ALMACEN]      [ANÁLISIS]
App / IoT  -->  Pub/Sub    --> Dataflow        --> BigQuery  --> Looker
Archivos   -->  Cloud Storage  Dataproc           BigQuery       SQL / ML
APIs       -->  Datastream --> (batch ETL)        Bigtable       Vertex AI
```

---

## El pipeline típico (panorama primero)

Antes de entrar en cada servicio, entiende los cuatro roles funcionales:

| Rol | Pregunta que responde | Servicio GCP principal |
|---|---|---|
| **Ingesta** | ¿Cómo llegan los datos? | Pub/Sub, Storage Transfer, Datastream |
| **Procesamiento** | ¿Cómo los limpio/transformo? | Dataflow, Dataproc |
| **Almacén analítico** | ¿Dónde los guardo para consultar? | BigQuery |
| **Visualización/BI** | ¿Cómo los exploro y presento? | Looker, Looker Studio |

El matiz clave: **Storage (GCS) no es un almacén analítico**. Es un lago de objetos (data lake). BigQuery es el warehouse donde los datos ya están estructurados para consulta rápida con SQL.

---

## BigQuery — Data Warehouse Serverless

### Por qué es distinto

Un data warehouse clásico (como Redshift de AWS) es un clúster de nodos que tú aprovisionas. BigQuery es serverless: no hay clúster, pagas por lo que consultas (o por capacidad reservada), y escala a petabytes automáticamente.

**Separación compute/storage**: BigQuery guarda los datos en Colossus (el sistema de archivos de Google) y ejecuta las consultas en Dremel (motor de análisis columnar distribuido). Esto significa que el coste de guardar y el coste de consultar son independientes.

### Modelo de coste

| Modalidad | Qué pagas | Cuándo usarla |
|---|---|---|
| **On-demand** (default) | $6.25/TB de datos escaneados | Exploración, consultas esporádicas |
| **Capacity (slots)** | Slots de cómputo reservados/autoscaled | Cargas predecibles y altas |
| **BigQuery Sandbox** | Gratis (1 TB/mes consultas, 10 GB storage) | Aprendizaje |

> **Trampa de costes frecuente**: `SELECT *` en una tabla de 500 GB te cuesta aunque solo necesitaras 3 columnas. BigQuery lee columnas, no filas. Selecciona siempre las columnas que necesitas.

### Estructura: Dataset > Tabla > Partición/Cluster

```
Proyecto
└── Dataset (como un "schema" en SQL clásico)
    └── Tabla
        ├── Partición (divide físicamente por fecha o rango entero)
        └── Clustering (ordena dentro de la partición por columnas)
```

**Particionado** — divide la tabla en segmentos físicos. Cuando filtras por la columna de partición, BigQuery solo lee los segmentos relevantes:

```sql
-- Crear tabla particionada por fecha de ingesta
CREATE TABLE proyecto.dataset.eventos (
  id STRING,
  tipo STRING,
  ts TIMESTAMP
)
PARTITION BY DATE(ts);

-- Esta consulta solo escaneará las particiones de esa semana
SELECT tipo, COUNT(*) as total
FROM `proyecto.dataset.eventos`
WHERE DATE(ts) BETWEEN '2026-06-01' AND '2026-06-07'
GROUP BY tipo;
```

**Clustering** — dentro de cada partición, ordena por columnas que usas en WHERE o JOIN. Reduce el escaneo adicional:

```sql
CREATE TABLE proyecto.dataset.eventos (
  id STRING,
  tipo STRING,
  ts TIMESTAMP
)
PARTITION BY DATE(ts)
CLUSTER BY tipo;
-- Ahora filtrar por tipo también es barato
```

### Comandos gcloud útiles

```bash
# Cargar CSV desde GCS a BigQuery
bq load \
  --source_format=CSV \
  --autodetect \
  mi_proyecto:mi_dataset.mi_tabla \
  gs://mi-bucket/datos.csv

# Ejecutar una consulta y guardar resultado
bq query \
  --use_legacy_sql=false \
  --destination_table mi_proyecto:mi_dataset.resultado \
  'SELECT * FROM `mi_proyecto.mi_dataset.origen` LIMIT 1000'

# Ver esquema de una tabla
bq show --schema mi_proyecto:mi_dataset.mi_tabla

# Listar datasets del proyecto actual
bq ls
```

### BigQuery ML

Puedes entrenar modelos directamente con SQL sin exportar datos:

```sql
CREATE OR REPLACE MODEL `mi_dataset.modelo_regresion`
OPTIONS(model_type='linear_reg', input_label_cols=['precio'])
AS SELECT caracteristica1, caracteristica2, precio
   FROM `mi_dataset.entreno`;
```

Esto conecta directamente con [[10-ia-ml-vertex]] — Vertex AI puede consumir modelos entrenados en BQML.

---

## Pub/Sub — Mensajería Asíncrona y Streaming

### El problema que resuelve

Imagina que tienes 200 sensores IoT enviando datos a tu backend. Si el backend cae 5 minutos, pierdes datos. Pub/Sub actúa como **buffer desacoplado**: los productores publican mensajes y los consumidores los leen cuando pueden, con garantía de entrega.

Es el equivalente de GCP a **Kafka** (AWS Kinesis en AWS). Arquitectura publicador/suscriptor:

```
[Sensor A]  \
[Sensor B]  --> [TOPIC: lecturas-sensores] --> [Suscripción A: Dataflow]
[App web]   /                               --> [Suscripción B: Cloud Function]
```

### Conceptos clave (jerga)

| Término | Significado |
|---|---|
| **Topic** | Canal lógico al que se publican mensajes |
| **Subscription** | "Cola" de un consumidor; cada suscripción recibe todos los mensajes del topic |
| **Push vs Pull** | Push: Pub/Sub llama a tu endpoint HTTP. Pull: tu app pide mensajes activamente |
| **ACK (acknowledge)** | Confirmas que procesaste el mensaje; si no, Pub/Sub lo reenvía |
| **Retention** | Cuánto tiempo guarda mensajes no consumidos (hasta 7 días) |

### Comandos gcloud

```bash
# Crear topic y suscripción
gcloud pubsub topics create lecturas-sensores
gcloud pubsub subscriptions create sub-dataflow \
  --topic=lecturas-sensores \
  --ack-deadline=60

# Publicar mensaje de prueba
gcloud pubsub topics publish lecturas-sensores \
  --message='{"sensor":"S01","temp":23.5,"ts":"2026-06-14T10:00:00Z"}'

# Leer mensajes (pull manual, útil para debug)
gcloud pubsub subscriptions pull sub-dataflow \
  --max-messages=5 \
  --auto-ack
```

### Free tier

- 10 GB de mensajes/mes gratuitos.
- Después: ~$0.04/GB.

---

## Dataflow — Procesamiento Batch y Stream (Apache Beam)

### Qué es y por qué importa

Dataflow es el **servicio gestionado de GCP para ejecutar pipelines Apache Beam**. Beam es el SDK (disponible en Python, Java, Go) que describe la lógica de transformación de datos de forma agnóstica al motor de ejecución.

La gran ventaja de Beam/Dataflow: **el mismo código sirve para batch (archivo completo) y streaming (datos en tiempo real)**. Cambias el runner, no la lógica.

```
[Código Beam] --runner=DataflowRunner--> [Dataflow en GCP]   (producción)
[Código Beam] --runner=DirectRunner  --> [Tu máquina local]  (desarrollo)
```

### Cuándo usar Dataflow vs alternativas

| Situación | Herramienta |
|---|---|
| ETL complejo con lógica Python/Java, batch o stream | **Dataflow** |
| Clúster Spark/Hadoop ya existente, migración desde on-prem | **Dataproc** |
| Transformaciones SQL simples entre GCS y BigQuery | **BigQuery scheduled queries** o **dbt** |
| Trigger por evento pequeño (un mensaje = una acción) | **Cloud Functions** |

### Ejemplo mínimo en Python (Beam)

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

opciones = PipelineOptions([
    '--runner=DataflowRunner',
    '--project=mi-proyecto',
    '--region=us-central1',
    '--temp_location=gs://mi-bucket/temp'])

with beam.Pipeline(options=opciones) as p:
    (
        p
        | 'Leer de Pub/Sub' >> beam.io.ReadFromPubSub(
            topic='projects/mi-proyecto/topics/lecturas-sensores')
        | 'Parsear JSON'    >> beam.Map(lambda msg: json.loads(msg))
        | 'Filtrar temp>25' >> beam.Filter(lambda r: r['temp'] > 25)
        | 'Escribir a BQ'   >> beam.io.WriteToBigQuery(
            'mi-proyecto:mi_dataset.alertas_temp',
            schema='sensor:STRING,temp:FLOAT,ts:STRING')
    )
```

### Modelo de coste

Pagas por los workers (vCPU + RAM + disco) mientras el job está corriendo. Dataflow hace autoscaling — añade o quita workers según la carga. Ojo: jobs streaming nunca terminan solos, así que tienen coste continuo.

---

## Dataproc — Spark y Hadoop Gestionado

### Cuándo lo necesitas

Si ya tienes código Spark o Hadoop (o el equipo lo conoce), Dataproc te evita instalar y gestionar el clúster. Puedes levantar un clúster en ~90 segundos, ejecutar el job, y eliminarlo.

**Diferencia clave con Dataflow**: Dataproc es un clúster Spark/Hadoop que tú controlas (versión, configuración, plugins). Dataflow es un servicio totalmente gestionado donde solo defines la lógica Beam. Dataproc da más flexibilidad; Dataflow da menos overhead operativo.

| | Dataflow | Dataproc |
|---|---|---|
| Paradigma | Beam (Python/Java/Go) | Spark, Hadoop, Hive, Flink |
| Gestión de clúster | Ninguna (serverless) | Tú controlas workers, versión |
| Autoscaling | Automático | Configurable |
| Migración desde on-prem | Reescritura en Beam | Lift-and-shift de Spark jobs |
| Coste jobs cortos | Pago por uso | Clúster levantado = coste corriendo |

### Comandos gcloud

```bash
# Crear clúster Dataproc
gcloud dataproc clusters create mi-cluster \
  --region=us-central1 \
  --num-workers=2 \
  --worker-machine-type=n1-standard-4 \
  --image-version=2.1-debian11

# Enviar job PySpark
gcloud dataproc jobs submit pyspark gs://mi-bucket/mi_job.py \
  --cluster=mi-cluster \
  --region=us-central1

# Eliminar clúster cuando termines (evita costes)
gcloud dataproc clusters delete mi-cluster --region=us-central1
```

> **Patrón recomendado (eficiencia de coste)**: clústeres efímeros. Crea el clúster, ejecuta el job, elimínalo. No dejes clústeres corriendo sin trabajo.

---

## Looker — Business Intelligence y Exploración

### Qué es Looker (y qué no es)

Looker es la plataforma de BI de Google (adquirida en 2019). Hay dos productos que se confunden:

| Producto | Para quién | Qué hace |
|---|---|---|
| **Looker Studio** (antes Data Studio) | Cualquier usuario, gratuito | Dashboards rápidos, conecta a BQ/Sheets/etc. |
| **Looker** (Enterprise) | Empresas, de pago | BI completo con LookML (lenguaje semántico), gobernanza de datos, embedido en apps |

**LookML** es el diferenciador de Looker: defines métricas y dimensiones de negocio en un lenguaje declarativo, y los usuarios finales pueden explorar sin escribir SQL. Esto evita el problema clásico de "cada equipo calcula el revenue diferente".

Para empezar: Looker Studio es gratuito y suficiente para exploración y portfolios. Conecta directo a BigQuery.

### Looker Studio — conexión rápida a BigQuery

1. Ve a `lookerstudio.google.com`
2. Crear informe > Añadir datos > BigQuery
3. Selecciona proyecto/dataset/tabla
4. Arrastra dimensiones y métricas

No requiere CLI.

---

## Pipeline Completo — Ejemplo Integrado

Caso: app de fitness que registra entrenamientos en tiempo real y genera métricas semanales.

```
[App móvil]
    |
    v
[Pub/Sub: topic "entrenos-raw"]          <- Ingesta en tiempo real
    |
    v
[Dataflow: pipeline streaming]           <- Enriquece, valida, normaliza
    |
    v
[BigQuery: tabla "entrenos" particionada por fecha]  <- Almacén analítico
    |
    +---> [BigQuery ML: modelo de anomalías]          <- ML directo en BQ
    |
    v
[Looker Studio: dashboard semanal]       <- Visualización
```

Para datos históricos (batch) el flujo es:
```
[GCS: archivos CSV históricos]
    |
[Dataproc/Dataflow: job ETL]
    |
[BigQuery]
```

---

## Equivalencias AWS (referencia cruzada)

| GCP | AWS equivalente | Diferencia notable |
|---|---|---|
| BigQuery | Redshift | BQ es más serverless; Redshift requiere gestionar clústeres (Serverless existe pero menos maduro) |
| Pub/Sub | Kinesis / SNS+SQS | Pub/Sub más simple; Kinesis da más control de shards |
| Dataflow | Kinesis Data Analytics / Glue Streaming | Beam es portable; Glue usa Spark gestionado |
| Dataproc | EMR | Muy similares; ambos Spark/Hadoop gestionado |
| Looker Studio | QuickSight | Looker Studio gratuito; QuickSight tiene free tier limitado |

---

## Errores y Costes Comunes

1. **`SELECT *` en BigQuery**: escanea todas las columnas aunque no las uses. Siempre especifica columnas.
2. **Tablas sin particionar**: en tablas grandes, cualquier consulta escanea todo. Añade partición por fecha desde el inicio.
3. **Jobs streaming Dataflow olvidados**: un job streaming es continuo. Si lo pruebas y no lo cancelas, sigue gastando.
4. **Clústeres Dataproc idle**: crear el clúster y olvidarse. Usa clústeres efímeros o configura tiempo de inactividad máximo (`--max-idle`).
5. **No usar `bq --dry_run`**: antes de ejecutar una consulta cara, estima el coste:
   ```bash
   bq query --use_legacy_sql=false --dry_run \
     'SELECT * FROM `mi-proyecto.dataset.tabla_grande`'
   # Output: Query will process X bytes
   ```

---

## Aplícalo / Práctica

**Nivel 0 — Free tier, sin coste:**
- Crea un dataset en BigQuery Sandbox.
- Consulta los datasets públicos de GCP: `bigquery-public-data.chicago_taxi_trips.taxi_trips` (miles de millones de filas, ideal para practicar particiones).
- Conecta ese dataset a Looker Studio y haz un dashboard básico.

**Nivel 1 — Pipeline mínimo:**
- Crea un topic Pub/Sub y publica 10 mensajes con `gcloud pubsub topics publish`.
- Lee los mensajes con una Cloud Function o con pull manual.

**Nivel 2 — Pipeline completo (requiere billing activo):**
- Beam en DirectRunner local (sin coste):
  ```bash
  pip install apache-beam
  python mi_pipeline.py --runner=DirectRunner
  ```
- Cuando funcione local, cambia `--runner=DataflowRunner` con tu proyecto.

**Nivel 3 — Integración con tu proyecto:**
- La app web genera datos de ingesta calórica. Podrías enviarlos a Pub/Sub > Dataflow > BigQuery y analizar patrones con SQL.

---

## Conexiones

- [[MOC_GCP]]
- [[01-fundamentos-cloud-y-gcp]]
- [[02-iam-y-seguridad]]
- [[05-almacenamiento]]
- [[06-bases-de-datos]]
- [[08-contenedores-y-serverless]]
- [[09-devops-iac-observabilidad]]
- [[10-ia-ml-vertex]]
- [[11-costes-y-buenas-practicas]]
- [[MOC_Desarrollo_Software]]
