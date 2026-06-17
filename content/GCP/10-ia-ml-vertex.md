---
title: IA y ML en GCP (Vertex AI)
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/ia-ml, ciencia-datos/ml, programacion/llm]
type: nota
status: en-progreso
source: claude-code
aliases: [Vertex AI, GCP ML, IA en GCP]
---

# IA y ML en GCP (Vertex AI)

## ¿Por qué existe este stack y qué problema resuelve?

Antes de Vertex AI (antes de 2021), Google Cloud tenía los servicios de ML dispersos: AI Platform para entrenar, Cloud ML Engine para desplegar, AutoML Tables en otro sitio... Era un mosaico. **Vertex AI unifica todo eso bajo una sola API y consola.**

El problema que resuelve: llevar un modelo de "notebook de Jupyter en tu ordenador" a "endpoint en producción que escala y no te cuesta dinero cuando no se usa" es sorprendentemente difícil. Vertex AI es la respuesta de Google a ese pipeline completo.

**Posición en GCP:** Vertex AI vive sobre [[08-contenedores-y-serverless]] (Cloud Run, GKE) y [[07-datos-y-analitica]] (BigQuery, Dataflow). Es el consumidor natural de datos procesados y el productor de predicciones que alimentan aplicaciones.

---

## Mapa del territorio: tres capas de abstracción

```
┌────────────────────────────────────────────────────────────┐
│  CAPA 3: Modelos preentrenados y APIs                      │
│  (cero ML propio) → Vision API, Speech, Translation...     │
├────────────────────────────────────────────────────────────┤
│  CAPA 2: Gemini API + Model Garden                         │
│  (prompting / fine-tuning sobre modelos de Google)         │
├────────────────────────────────────────────────────────────┤
│  CAPA 1: Vertex AI completo                                │
│  (tus datos, tus modelos, AutoML, training jobs, pipelines)│
└────────────────────────────────────────────────────────────┘
```

Cuanto más abajo vas, más control tienes y más responsabilidad asumes. La elección correcta depende de tu caso de uso.

---

## Vertex AI — la plataforma completa

### Conceptos clave

| Término Vertex AI | Qué es en lenguaje llano |
|---|---|
| **Dataset** | Datos etiquetados registrados en Vertex (no los almacena, apunta a GCS/BigQuery) |
| **Training Job** | Proceso que ejecuta tu código de entrenamiento en VMs gestionadas |
| **Model** | Artefacto resultante del training, registrado en **Model Registry** |
| **Endpoint** | Servidor HTTP que expone un modelo para predicción online |
| **Model Registry** | Control de versiones de modelos (equivale a MLflow Model Registry) |
| **Experiment** | Tracking de hiperparámetros y métricas (equivale a MLflow Experiments) |
| **Pipeline** | DAG de pasos ML orquestado (equivale a Airflow pero para ML) |

### Entrenar un modelo personalizado

Vertex AI ejecuta tu código como un **Custom Training Job**. Tu código va en un contenedor Docker (o usas containers prediseñados de Google con TF/PyTorch/scikit-learn).

```bash
# Enviar un training job con contenedor prebuilt de sklearn
gcloud ai custom-jobs create \
  --region=europe-west1 \
  --display-name="mi-modelo-clasificacion" \
  --worker-pool-spec=machine-type=n1-standard-4,replica-count=1,container-image-uri=europe-docker.pkg.dev/vertex-ai/training/sklearn-cpu.1-0:latest \
  --args="--epochs=50,--learning-rate=0.01"
```

El output del entrenamiento (el modelo serializado) se guarda en **Cloud Storage** (GCS). Luego se registra:

```bash
# Registrar el modelo en Model Registry
gcloud ai models upload \
  --region=europe-west1 \
  --display-name="clasificador-v1" \
  --artifact-uri="gs://mi-bucket/modelos/clasificador/" \
  --container-image-uri="europe-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest"
```

### Desplegar un endpoint

Un **endpoint** en Vertex AI es un balanceador de carga gestionado que enruta tráfico a una o varias versiones del modelo. Soporta **traffic splitting** (p.ej. 90% modelo v1, 10% modelo v2 para A/B testing).

```bash
# Crear endpoint
gcloud ai endpoints create \
  --region=europe-west1 \
  --display-name="endpoint-clasificador"

# Desplegar modelo en el endpoint (obtén ENDPOINT_ID del paso anterior)
gcloud ai endpoints deploy-model ENDPOINT_ID \
  --region=europe-west1 \
  --model=MODEL_ID \
  --display-name="clasificador-v1-deploy" \
  --machine-type=n1-standard-2 \
  --min-replica-count=1 \
  --max-replica-count=3 \
  --traffic-split=0=100
```

El endpoint escala automáticamente entre min y max réplicas. Si `min-replica-count=0`, escala a cero cuando no hay tráfico (pero tiene cold start de ~30-60 s).

### Predicción online vs. batch

| | Online Prediction | Batch Prediction |
|---|---|---|
| **Cuándo** | Respuesta en tiempo real (<1 s) | Millones de filas de una vez |
| **Input** | JSON por petición HTTP | Archivo en GCS o tabla BigQuery |
| **Output** | JSON inmediato | Archivo en GCS |
| **Coste** | Por hora de endpoint activo | Por nodo-hora de batch job |
| **Ejemplo** | App que clasifica imagen del usuario | Inferir sobre todo el catálogo cada noche |

```bash
# Predicción online con curl
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://europe-west1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/europe-west1/endpoints/ENDPOINT_ID:predict" \
  -d '{"instances": [{"feature1": 1.2, "feature2": 3.4}]}'
```

### Vertex AI Pipelines

Un **pipeline** es un grafo dirigido acíclico (DAG) de pasos ML: preprocesar → entrenar → evaluar → si métrica OK → desplegar. Se define con **Kubeflow Pipelines SDK (KFP)** o **TFX**.

```python
# Fragmento de pipeline con KFP
from kfp.v2 import dsl
from kfp.v2.dsl import component

@component(base_image="python:3.10")
def train_component(data_path: str, model_output: dsl.Output[dsl.Model]):
    # tu código de entrenamiento aquí
    pass

@dsl.pipeline(name="mi-pipeline-ml")
def mi_pipeline(data_gcs_path: str):
    train_task = train_component(data_path=data_gcs_path)

# Compilar y enviar
from google.cloud import aiplatform
aiplatform.init(project="mi-proyecto", location="europe-west1")
job = aiplatform.PipelineJob(
    display_name="pipeline-clasificacion",
    template_path="pipeline.json",
    pipeline_root="gs://mi-bucket/pipeline-root/"
)
job.run()
```

Los pipelines se pueden programar (equivale a un cron que lanza reentrenamiento automático).

### AutoML

**AutoML** entrena modelos sin escribir código de ML. Le das datos etiquetados y Google busca la mejor arquitectura y hiperparámetros. Disponible para:

- **Tabular** (clasificación, regresión, forecasting)
- **Imagen** (clasificación, detección de objetos, segmentación)
- **Texto** (clasificación, extracción de entidades, análisis de sentimiento)
- **Vídeo** (clasificación, seguimiento de objetos)

```bash
# Crear dataset tabular desde BigQuery para AutoML
gcloud ai datasets create \
  --region=europe-west1 \
  --display-name="dataset-ventas" \
  --metadata-schema-uri="gs://google-cloud-aiplatform/schema/dataset/metadata/tabular_1.0.0.yaml" \
  --metadata='{"inputConfig": {"bigquerySource": {"uri": "bq://proyecto.dataset.tabla"}}}'
```

AutoML **no te da acceso al modelo subyacente** (es una caja negra de Google). Si necesitas portabilidad o interpretabilidad profunda, mejor Custom Training.

### Model Garden

**Model Garden** es el catálogo de modelos en Vertex AI: modelos de Google (Gemini, PaLM, Imagen) y modelos open-source (Llama, Mistral, Stable Diffusion). Permite:

- Desplegar un modelo open-source con un clic en un endpoint de Vertex
- Fine-tune algunos modelos directamente desde la consola
- Comparar modelos en el playground antes de comprometerte

---

## Gemini API y modelos generativos

### La jerarquía de modelos Gemini en GCP

```
Gemini Ultra / Pro / Flash / Nano
      │
      ▼
Vertex AI (acceso enterprise, tu VPC, logs, fine-tuning)
Google AI Studio (acceso rápido, dev, free tier generoso)
```

Desde GCP, Gemini se accede a través de **Vertex AI Generative AI** o directamente por la **Gemini API** con una API key (Google AI Studio).

```python
# Con Vertex AI SDK (enterprise, dentro de tu proyecto GCP)
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="mi-proyecto", location="us-central1")
model = GenerativeModel("gemini-1.5-pro")
response = model.generate_content("Explica qué es un transformador en una frase")
print(response.text)
```

```python
# Con google-generativeai SDK (más simple, usa API key)
import google.generativeai as genai
genai.configure(api_key="TU_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Explica qué es un transformador en una frase")
print(response.text)
```

### Cuándo usar Vertex AI Gemini vs. Google AI Studio

| | Vertex AI (Gemini vía Vertex) | Google AI Studio / API key |
|---|---|---|
| **Contexto** | Producción, enterprise | Prototipado, personal |
| **Facturación** | Factura GCP del proyecto | API key, factura aparte |
| **VPC / privacidad** | Puede quedar dentro de tu red | Tráfico sale a internet de Google |
| **Fine-tuning** | Sí, con tus datos | No |
| **Logs y auditoría** | Cloud Logging integrado | Limitado |
| **Free tier** | 60 req/min con Gemini Flash (jun 2026) | Más generoso en AI Studio |

### Fine-tuning de Gemini

Vertex AI permite hacer **Supervised Fine-Tuning (SFT)** de Gemini con tus propios pares (prompt, respuesta). Útil cuando el modelo base no sigue tu estilo/dominio y el prompting no es suficiente.

```bash
# Lanzar un tuning job (requiere dataset en JSONL en GCS)
# Formato: {"input_text": "...", "output_text": "..."}
gcloud ai tuning-jobs create \
  --region=us-central1 \
  --base-model=gemini-1.0-pro-002 \
  --training-dataset-uri="gs://mi-bucket/datos/fine-tune.jsonl" \
  --tuned-model-display-name="gemini-producto-v1"
```

---

## APIs de IA preentrenadas (Cloud AI APIs)

Son REST APIs que consumes sin saber nada de ML. Google ya entrenó el modelo, tú mandas datos y recibes predicciones.

### Catálogo principal

| API | Qué hace | Caso de uso típico |
|---|---|---|
| **Vision API** | Detectar objetos, texto (OCR), caras, etiquetas, logos, Safe Search | Moderar imágenes de usuarios, extraer texto de facturas |
| **Document AI** | OCR avanzado + extracción estructurada de documentos | Parsear facturas, contratos, formularios |
| **Speech-to-Text** | Transcripción de audio (>125 idiomas, tiempo real o batch) | Transcribir llamadas, subtitular vídeos |
| **Text-to-Speech** | Síntesis de voz natural (voces WaveNet/Studio) | Asistentes de voz, accesibilidad |
| **Natural Language API** | Análisis de sentimiento, entidades, sintaxis, clasificación de contenido | Analizar reseñas, clasificar tickets de soporte |
| **Translation API** | Traducción automática (>100 idiomas) | Internacionalización de apps |
| **Video Intelligence API** | Detectar escenas, objetos, texto en vídeo | Catalogar vídeos, búsqueda en video |

```bash
# Ejemplo: Vision API — detectar etiquetas en una imagen
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://vision.googleapis.com/v1/images:annotate" \
  -d '{
    "requests": [{
      "image": {"source": {"imageUri": "gs://mi-bucket/foto.jpg"}},
      "features": [{"type": "LABEL_DETECTION", "maxResults": 10}]
    }]
  }'
```

```python
# Natural Language API — análisis de sentimiento
from google.cloud import language_v1

client = language_v1.LanguageServiceClient()
document = language_v1.Document(
    content="El producto llegó roto y el servicio al cliente fue terrible.",
    type_=language_v1.Document.Type.PLAIN_TEXT,
    language="es"
)
sentiment = client.analyze_sentiment(request={"document": document}).document_sentiment
print(f"Score: {sentiment.score:.2f}, Magnitude: {sentiment.magnitude:.2f}")
# Score: -0.8 (negativo), Magnitude: alta
```

---

## ¿Cuándo usar qué? (árbol de decisión)

```
¿Tienes datos propios y necesitas un modelo a medida?
    │
    ├─ SÍ ──► ¿Cuánto control / portabilidad necesitas?
    │             │
    │             ├─ Mucho (quieres el artefacto, explainability, etc.)
    │             │      → Custom Training en Vertex AI
    │             │
    │             └─ Poco (solo quiero que funcione, no me importa la caja negra)
    │                    → AutoML en Vertex AI
    │
    └─ NO ──► ¿Es una tarea generativa (texto, código, imágenes)?
                  │
                  ├─ SÍ ──► ¿Suficiente con prompting?
                  │             ├─ SÍ → Gemini API (AI Studio o Vertex)
                  │             └─ NO → Fine-tuning Gemini en Vertex AI
                  │
                  └─ NO ──► ¿Es visión / voz / texto / traducción estándar?
                                └─ SÍ → Cloud AI API preentrenada (Vision, Speech, NL...)
```

### Tabla comparativa de coste/complejidad

| Opción | Complejidad técnica | Coste (aproximado) | Control |
|---|---|---|---|
| Cloud AI API | Baja (REST call) | Por petición (~0,001–0,01 $/req) | Ninguno |
| Gemini API (prompting) | Baja | Por tokens (~0,07 $/M tokens Flash) | Prompting |
| AutoML | Media (preparar datos) | Training + predicción (~3–20 $/hora GPU) | Bajo |
| Fine-tuning Gemini | Media-alta | Training job + endpoint | Medio |
| Custom Training + Vertex | Alta (código ML completo) | GPU/TPU on-demand | Total |

---

## Intersección con tu área de Ciencia de Datos

Si estudias DS/ML en paralelo, Vertex AI es el lugar donde ese conocimiento aterriza en producción:

- **Scikit-learn / XGBoost** → Custom Training Job con container `sklearn-cpu` o `xgboost-cpu`
- **TensorFlow / PyTorch** → Custom Training con containers `tf-cpu/gpu` o `pytorch-gpu`
- **Experimentos y tracking** → Vertex AI Experiments (alternativa cloud a MLflow)
- **Feature engineering repetible** → Vertex AI Feature Store (almacén de features compartido entre modelos)
- **Datos en BigQuery** → Vertex AI puede entrenar directamente sobre tablas BQ sin exportar (BigQuery ML o AutoML Tabular)

```python
# Ejemplo: crear experiment y loggear métricas (alternativa a MLflow)
from google.cloud import aiplatform
aiplatform.init(project="mi-proyecto", location="europe-west1", experiment="clasificacion-v2")

with aiplatform.start_run("run-lr-0.01"):
    aiplatform.log_params({"learning_rate": 0.01, "epochs": 50})
    aiplatform.log_metrics({"accuracy": 0.92, "f1": 0.89})
```

---

## Free tier y costes comunes (jun 2026)

**Free tier relevante:**
- Gemini 1.5 Flash: 60 RPM gratis en AI Studio (limitado en Vertex)
- Vision API: 1.000 unidades/mes gratis
- Natural Language API: 5.000 unidades/mes gratis
- Speech-to-Text: 60 min/mes gratis
- Translation API: 500.000 caracteres/mes gratis

**Errores de coste comunes:**
- Dejar un **endpoint online con réplicas activas** cuando no hay tráfico: puede costar 100–500 $/mes fácilmente. Usa `min-replica-count=0` en dev/test.
- **Training jobs en GPU A100** sin acotar tiempo: pon `--max-running-time` siempre.
- AutoML tabular: el "budget" se define en horas de nodo; 1 hora mínima, que puede ser cara.
- Gemini en Vertex cobra por **token de entrada Y salida**: un contexto largo en un loop puede dispararse.

```bash
# Ver coste estimado de un training job antes de lanzar
gcloud ai custom-jobs describe JOB_ID --region=europe-west1 --format="yaml(encryptionSpec,jobSpec.workerPoolSpecs)"

# Poner límite de tiempo en un training job
gcloud ai custom-jobs create ... \
  --max-running-time=7200s  # 2 horas máximo
```

---

## Aplícalo / practica

1. **Nivel 0 (15 min):** Activa la Vision API en un proyecto GCP, sube una foto a GCS y analízala con `curl`. Lee las etiquetas que devuelve.

2. **Nivel 1 (1 h):** Usa la Natural Language API para analizar el sentimiento de 20 reseñas de un producto (puedes inventarlas). Muestra los resultados en un DataFrame de pandas.

3. **Nivel 2 (3–4 h):** Entrena un modelo de clasificación tabular con AutoML en Vertex AI (puedes usar el dataset Titanic o cualquier CSV que tengas). Despliega el endpoint y haz predicciones online.

4. **Nivel 3 (medio día):** Convierte un script de entrenamiento de scikit-learn que ya tengas en un Custom Training Job de Vertex AI. Regístralo en Model Registry y despliégalo como endpoint con `min-replica-count=0`.

5. **Nivel 4 (avanzado):** Escribe un pipeline KFP con al menos 3 pasos (preprocesar → entrenar → evaluar). Si accuracy > umbral, despliega automáticamente; si no, escribe un log de fallo.

---

## Conexiones

- [[MOC_GCP]]
- [[01-fundamentos-cloud-y-gcp]]
- [[02-iam-y-seguridad]]
- [[07-datos-y-analitica]]
- [[08-contenedores-y-serverless]]
- [[09-devops-iac-observabilidad]]
- [[11-costes-y-buenas-practicas]]
- [[MOC_Desarrollo_Software]]
