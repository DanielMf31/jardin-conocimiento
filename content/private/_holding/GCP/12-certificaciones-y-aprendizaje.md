---
title: Certificaciones y aprendizaje de GCP
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/certificaciones, programacion/carrera]
type: nota
status: en-progreso
source: claude-code
aliases: [GCP certs, certificaciones Google Cloud, aprendizaje GCP]
---

# Certificaciones y aprendizaje de GCP

## ¿Por qué importa certificarse en GCP?

Las certificaciones de Google Cloud no son solo papel: son el único proxy externo de que sabes qué estás haciendo en una plataforma que no se puede "instalar en local". Resuelven tres problemas distintos:

1. **Orientan el estudio**: el temario de cada cert obliga a cubrir servicios que de otro modo evitarías.
2. **Señalizan competencia** en entrevistas y proyectos, especialmente en empresas que usan GCP (y en Google mismo).
3. **Dan acceso a labs reales**: prepararse con Skills Boost significa haber tocado la consola, no solo leído docs.

Para alguien que aspira a trabajar en Google, la lógica es directa: Google recomienda internamente que sus propios ingenieros tengan al menos el Associate Cloud Engineer. Una cert Professional Cloud Architect en el CV de un candidato externo es una señal fuerte.

---

## El ecosistema de certificaciones: panorama

Google organiza sus certificaciones en tres niveles:

```
Foundational  →  Associate  →  Professional (varias especialidades)
```

| Cert | Nivel | Duración examen | Precio | Mejor para |
|---|---|---|---|---|
| Cloud Digital Leader | Foundational | 90 min | $99 | No-técnicos, managers |
| Associate Cloud Engineer (ACE) | Associate | 120 min | $200 | Ingenieros generalistas |
| Professional Cloud Architect (PCA) | Professional | 120 min | $200 | Diseño de sistemas cloud |
| Professional Data Engineer (PDE) | Professional | 120 min | $200 | Pipelines, BigQuery, ML |
| Professional Cloud Security Engineer | Professional | 120 min | $200 | IAM, VPC, cumplimiento |
| Professional ML Engineer | Professional | 120 min | $200 | Vertex AI, MLOps |
| Professional Cloud DevOps Engineer | Professional | 120 min | $200 | CI/CD, observabilidad |
| Professional Cloud Network Engineer | Professional | 120 min | $200 | VPC avanzada, Interconnect |

> **Renovación**: todas las Professional caducan a los 2 años. ACE a los 3. Se renuevan con un examen de recertificación (mismo precio, igual de difícil).

---

## Cloud Digital Leader — ¿cuándo tiene sentido?

**Qué cubre**: visión de negocio de GCP, conceptos de transformación digital, panorama de productos sin profundidad técnica.

**Para quién**: gerentes, PMs, comerciales, o cualquiera que quiera entender el lenguaje cloud sin tocar una terminal.

**Para un ingeniero**: tiene poco valor a nivel técnico. Si vienes de técnico y ya estás estudiando los docs técnicos de GCP, **sáltala y ve directamente al ACE**. La única excepción es si tu empresa la paga y sirve para justificar horas de estudio.

---

## Associate Cloud Engineer — la de mejor relación esfuerzo/valor

### Qué evalúa

El ACE mide que puedes **operar** GCP: desplegar VMs, configurar redes básicas, gestionar IAM, usar GKE, monitorizar con Cloud Monitoring. No pide que diseñes arquitecturas complejas, sino que te muevas con soltura.

### Temario clave (pesos aproximados)

| Dominio | Peso |
|---|---|
| Configurar el entorno cloud (proyectos, facturación, APIs) | ~17% |
| Planificar y configurar soluciones cloud (cómputo, storage, BD) | ~17% |
| Desplegar e implementar soluciones cloud | ~25% |
| Garantizar operaciones exitosas | ~20% |
| Configurar acceso y seguridad (IAM, service accounts) | ~20% |

### Por qué es la mejor primera cert técnica

- Cubre **todo el stack** de GCP a nivel funcional — te fuerza a no ignorar los servicios que te parecen aburridos.
- La profundidad es la justa: no pide diseñar un sistema multi-región con 99.999% SLA, pero sí que sepas cuándo usar Cloud SQL vs Spanner.
- Al acabarla tienes una base sólida para cualquiera de las Professional.
- Para alguien con perfil hardware/sistemas: los conceptos de redes (subnets, firewall rules, VPN) y de cómputo (VMs, preemptibles, GPUs) te resultarán más naturales que a alguien de negocio.

### Comandos típicos que salen en el examen

```bash
# Crear una VM con gcloud
gcloud compute instances create mi-vm \
  --zone=europe-west1-b \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud

# Ver logs de una instancia
gcloud compute ssh mi-vm --zone=europe-west1-b -- "sudo journalctl -xe"

# Crear un cluster GKE
gcloud container clusters create mi-cluster \
  --num-nodes=3 \
  --zone=europe-west1-b

# Dar un rol IAM a un service account
gcloud projects add-iam-policy-binding mi-proyecto \
  --member="serviceAccount:sa@mi-proyecto.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

---

## Professional Cloud Architect — el salto de operador a diseñador

### Qué evalúa

No te pregunta cómo ejecutar comandos, sino **por qué elegir una arquitectura sobre otra**. Los casos de estudio son el elemento diferenciador: te dan una empresa ficticia con requisitos de negocio (disponibilidad, coste, cumplimiento) y tienes que razonar el diseño.

### Lo que te exige que sepas de verdad

- Trade-offs entre servicios (Cloud SQL vs AlloyDB vs Spanner, por ejemplo).
- Patrones de alta disponibilidad: multi-region, health checks, load balancers.
- Diseño de IAM a nivel de organización (Organization → Folder → Project).
- Migración de on-premise a cloud (lift-and-shift vs re-architect).
- Costes y optimización: committed use, autoscaling, preemptibles.

### Cuándo hacerla

Después del ACE, con al menos 6 meses de práctica real o intensiva en labs. Sin base previa, los casos de estudio son incomprensibles porque no tienes intuición sobre qué duele en producción.

---

## Professional Data Engineer — para el perfil DS/ML

### Qué cubre

BigQuery (modelado, optimización de queries, particionado), Dataflow (Apache Beam), Pub/Sub, Dataproc (Hadoop/Spark managed), pipelines de ML con Vertex AI, y gobernanza de datos.

### Relevancia si quieres trabajar en ML/datos en Google

Alta. Google usa BigQuery internamente a escala masiva y Vertex AI es el core de sus productos ML. Entender cómo funcionan desde dentro (no solo desde la API) te da ventaja real.

### Lo más difícil del examen

Optimizar queries de BigQuery (particionado por fecha vs columna, clustering, slots de BigQuery Reservations) y diseñar pipelines Dataflow que no revienten en costes.

---

## Professional Cloud Security Engineer

### Qué cubre

IAM avanzado, VPC Service Controls (perímetros de seguridad alrededor de APIs), Binary Authorization (solo imágenes firmadas en GKE), Cloud Armor (WAF), gestión de secretos con Secret Manager, cumplimiento (GDPR, PCI-DSS, HIPAA en GCP).

### Cuándo tiene sentido

Si tu rol implica auditorías, seguridad de infraestructura, o trabajas en sectores regulados (banca, salud). Para un perfil de software generalista, el ACE + PCA ya cubren lo necesario de seguridad.

---

## Professional ML Engineer

### Qué cubre

Vertex AI (entrenamiento, despliegue, Feature Store, Pipelines), MLOps en producción, monitorización de modelos (data drift, model drift), optimización de hiperparámetros con Vertex AI Vizier, TFX.

### Para quién

Alguien que ya sabe ML (modelos, evaluación, feature engineering) y quiere aprender a llevar eso a producción en GCP. No enseña ML desde cero — asume que ya sabes.

---

## Plataformas de práctica

### Google Cloud Skills Boost (antes Qwiklabs)

URL: [https://www.cloudskillsboost.google](https://www.cloudskillsboost.google)

Es la plataforma oficial de Google. La mecánica:

- **Labs**: te dan un proyecto GCP real (con credenciales temporales), una tarea guiada, y ~30-90 min para completarla. Al acabar, el proyecto se destruye.
- **Quests**: colecciones temáticas de labs (ej. "Kubernetes in Google Cloud").
- **Skill badges**: completas una quest y obtienes un badge digital verificable en LinkedIn.
- **Learning paths**: rutas oficiales para cada certificación.

**Precios**: labs individuales cuestan "créditos" (~$1-5 cada uno). La suscripción mensual (~$29/mes) da acceso a todo. Para preparar el ACE, con 1-2 meses de suscripción es suficiente si eres constante.

**Tip de eficiencia**: cuando hagas un lab, no lo sigas ciegamente paso a paso. Entiende qué hace cada comando antes de ejecutarlo. El lab guiado es el andamiaje; el aprendizaje es tuyo.

### Coursera — Google Cloud Professional Certificates

Google tiene cursos oficiales en Coursera. El más relevante es la especialización **"Preparing for Google Cloud Certification: Cloud Engineer"** (5 cursos). Incluye labs de Skills Boost. Con la suscripción de Coursera (~$49/mes) o con audit gratuito (sin certificado).

**AWS equivalente para contexto**: si vienes de AWS, Cloud Practitioner ≈ Cloud Digital Leader, Solutions Architect Associate ≈ ACE+PCA.

### ExamTopics y dumps — úsalos bien

Existen bancos de preguntas de exámenes anteriores (ExamTopics, Whizlabs). Son útiles para **calibrar el formato** de las preguntas, no para memorizar respuestas. Las preguntas del examen real cambian frecuentemente y el valor real es entender el razonamiento detrás, no la respuesta.

---

## Free Tier para proyectos reales

GCP tiene dos capas de gratuidad que conviene distinguir:

| Tipo | Qué es | Cuánto dura |
|---|---|---|
| Free Trial | $300 de crédito | 90 días desde que activas la cuenta |
| Always Free | Ciertos recursos sin límite de tiempo | Mientras exista tu cuenta |

### Always Free más útiles para aprender

```
Compute Engine:    1x e2-micro VM, 30 GB HDD, en us-* regions
Cloud Storage:     5 GB en US multi-region
BigQuery:          10 GB storage + 1 TB queries/mes
Cloud Run:         2 millones de requests/mes, 360K GB-segundos
Cloud Functions:   2 millones de invocaciones/mes
Pub/Sub:           10 GB mensajes/mes
Firestore:         1 GB storage, 50K lecturas/día
Secret Manager:    6 versiones activas, 10K operaciones/mes
```

### Estrategia para usar el free tier sin sustos de factura

```bash
# 1. Pon siempre una alerta de presupuesto antes de tocar nada
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="alerta-aprendizaje" \
  --budget-amount=10EUR \
  --threshold-rule=percent=0.5 \
  --threshold-rule=percent=0.9

# 2. Borra recursos cuando acabes el lab
gcloud compute instances delete mi-vm --zone=europe-west1-b

# 3. Revisa qué está corriendo
gcloud compute instances list
gcloud container clusters list
gcloud run services list
```

**Error común**: olvidar un cluster GKE corriendo. 3 nodos e2-medium = ~$150/mes. Crea un proyecto separado para labs y bórralo entero cuando acabes.

```bash
# Borrar un proyecto entero (borra todos sus recursos)
gcloud projects delete mi-proyecto-labs
```

---

## Ruta recomendada de autoaprendizaje

La ruta asume que ya tienes base de programación y sistemas (lo cual cumples) pero poca exposición a cloud.

### Fase 0 — Fundamentos (2-4 semanas)

Leer el doc [[01-fundamentos-cloud-y-gcp]] de esta bóveda. Entender qué es un proyecto GCP, cómo funciona la jerarquía de organización, y activar una cuenta free trial.

Instalar y configurar `gcloud`:
```bash
# Instalar Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
gcloud auth application-default login
```

### Fase 1 — Breadth first (6-8 semanas)

Leer los docs de esta bóveda en orden: 02 (IAM), 03 (Cómputo), 04 (Redes), 05 (Storage), 06 (Bases de datos), 08 (Contenedores/serverless). Para cada uno, hacer al menos 1 lab en Skills Boost.

Objetivo: haber desplegado una VM, un Cloud Run service, un bucket, y una Cloud SQL instance.

### Fase 2 — Preparar ACE (4-6 semanas)

- Hacer el learning path oficial de ACE en Skills Boost.
- Hacer los quests de GKE, IAM, y Networking.
- Practicar con ExamTopics para calibrar el formato.
- Mock exam oficial de Google (disponible en Skills Boost).

**Señal de que estás listo**: puedes responder en <30 segundos "cuándo usar Cloud Run vs GKE vs Compute Engine" y justificarlo.

### Fase 3 — Proyecto real (paralelo o posterior)

La cert te da credencial, pero un proyecto real en tu CV te da diferenciación. Ideas con el free tier:

- Desplegar la app web en Cloud Run + Cloud SQL + Secret Manager (ya tienes el código).
- Pipeline de datos: ingesta con Pub/Sub, proceso con Cloud Functions, salida a BigQuery.
- Bot o API serverless con Cloud Functions + Firestore.

### Fase 4 — Professional (opcional, +3-6 meses)

Elegir especialidad según tu trayectoria: PCA si vas a arquitectura, PDE si vas a datos, ML Engineer si vas a Vertex AI. No hace falta hacerlas todas — mejor una bien hecha.

---

## Relevancia para una carrera en Google

Google es usuario de GCP (usa su propia nube internamente, aunque algunos sistemas son anteriores a GCP y más propietarios). Algunas realidades:

**Qué pesa en un proceso de selección**:
- El examen técnico (coding + system design) pesa más que cualquier certificación.
- Pero una Professional Cloud Architect o ACE en el CV filtra positivo en el screening inicial, especialmente para roles SRE, Cloud CE, o Data Engineer.
- Los Googlers que entrevistan conocen bien el temario de las certs y pueden hacer preguntas que se solapan.

**Roles donde las certs GCP tienen más peso**:
- Customer Engineer (CE) / Solutions Engineer: requieren demostrar conocimiento técnico de GCP a clientes.
- Site Reliability Engineer (SRE): GCP + sistemas distribuidos.
- Data/ML Engineer: BigQuery, Vertex AI.

**Lo que Google valora por encima de las certs**:
- Proyectos reales desplegados (con arquitectura justificada).
- Contribuciones open source relacionadas.
- Capacidad de razonar trade-offs en voz alta (exactamente lo que entrena el PCA).

> Nota: Google tiene también el programa **Google Cloud Partner Advantage** y el **Google Developer Expert (GDE)** program — ambos van más allá de las certs y son reconocimientos de comunidad, no exámenes.

---

## Aplícalo / practica

1. **Crea tu cuenta GCP** (si no la tienes) y activa el free trial. Pon una alerta de presupuesto de $10 inmediatamente.
2. **Instala gcloud CLI** y completa `gcloud init`. Verifica con `gcloud projects list`.
3. **Haz un lab gratuito en Skills Boost**: busca "Google Cloud Essentials" — es gratuito y da un skill badge. Hazlo en <2 horas.
4. **Define tu objetivo de cert**: ¿ACE en 3 meses? ¿PDE en 6? Ponlo en con fecha.
5. **Despliega la app web en Cloud Run** usando el free tier como proyecto de práctica real. Cada servicio que configures (Cloud SQL, Secret Manager, Artifact Registry) es un ítem de temario ACE que puedes marcar.

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
- [[11-costes-y-buenas-practicas]]
- [[MOC_Desarrollo_Software]]
