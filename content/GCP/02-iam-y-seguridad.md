---
title: IAM y seguridad en GCP
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/seguridad, ciberseguridad/iam, ciberseguridad/secretos]
type: nota
status: en-progreso
source: claude-code
aliases: [IAM GCP, Cloud IAM, seguridad GCP]
---

# 🔐 IAM y seguridad en GCP

## ¿Por qué existe IAM?

En hardware, controlas el acceso físicamente: quién tiene la llave del rack, quién puede tocar el PLC. En cloud, cualquiera con credenciales puede borrar tu base de datos desde el otro lado del mundo. IAM (Identity and Access Management) es el mecanismo que responde a la pregunta:

> **"¿Quién puede hacer qué sobre qué recurso?"**

Es la primera línea de defensa en GCP y uno de los temas de mayor peso en las certificaciones (Associate Cloud Engineer, Professional Cloud Architect). Si aspiras a Google, IAM no es opcional — es infraestructura mental.

---

## 🗺️ El modelo central: Principal → Rol → Recurso

Antes de cualquier detalle, el esquema que unifica todo:

```
PRINCIPAL (quién)  +  ROL (qué permisos)  →  RECURSO (sobre qué)
```

Cada **binding** (enlace) en una **política IAM** une estos tres elementos. GCP evalúa: "¿Tiene este principal un rol que incluya el permiso requerido sobre este recurso?"

La política IAM se puede poner en cualquier nivel de la jerarquía: Organización > Carpeta > Proyecto > Recurso específico. Los permisos se **heredan hacia abajo** pero **nunca hacia arriba**.

---

## 👤 Identidades (Principals)

Un *principal* es cualquier entidad que puede recibir permisos. No confundir con "usuario" — hay varios tipos:

| Tipo | Descripción | Ejemplo |
|---|---|---|
| **Google Account** | Cuenta personal de Google | `user:daniel@gmail.com` |
| **Google Group** | Colección de cuentas/SAs con un email de grupo | `group:devs@empresa.com` |
| **Google Workspace / Cloud Identity Domain** | Todos los usuarios de un dominio corporativo | `domain:empresa.com` |
| **Service Account** | Identidad para apps/máquinas (ver sección propia) | `serviceAccount:bot@proyecto.iam.gserviceaccount.com` |
| **`allAuthenticatedUsers`** | Cualquier cuenta Google autenticada (¡peligroso!) | — |
| **`allUsers`** | Literalmente todo el mundo, anónimos incluidos | — |

> **Regla práctica**: nunca uses `allUsers` ni `allAuthenticatedUsers` en recursos con datos sensibles. Es equivalente a dejar la puerta abierta en internet.

Los **Google Groups** son el patrón recomendado para gestionar equipos: asignas el rol al grupo, añades/quitas personas del grupo, y no tocas las políticas IAM cada vez que alguien entra o sale.

---

## 🎭 Roles: tipos y jerarquía

Un *rol* es una colección de *permisos*. Los permisos individuales tienen la forma `servicio.recurso.verbo` (ej: `storage.objects.get`). Nunca se asignan permisos sueltos — siempre a través de roles.

### 1. Roles primitivos (básicos) — Evítalos en producción

Existían antes de IAM moderno. Son muy amplios:

| Rol | Lo que hace |
|---|---|
| `roles/owner` | Control total: IAM incluido. Puede borrar el proyecto. |
| `roles/editor` | Crear/modificar recursos, pero no cambiar IAM |
| `roles/viewer` | Solo lectura |

**Problema**: son "blast radius" enorme. Si una cuenta con `owner` se compromete, el atacante tiene las llaves del reino.

### 2. Roles predefinidos — El estándar

Google crea y mantiene roles específicos por servicio. Son granulares y auditados:

```
roles/storage.objectViewer       → leer objetos en GCS
roles/storage.objectAdmin        → leer/escribir/borrar objetos
roles/cloudsql.client            → conectarse a Cloud SQL (no administrar)
roles/container.developer        → desplegar en GKE
roles/logging.viewer             → leer logs
```

Regla: busca siempre el rol predefinido más restrictivo que cubra tu caso.

### 3. Roles personalizados (Custom Roles) — Para casos específicos

Cuando ningún rol predefinido se ajusta exactamente, puedes crear uno con los permisos exactos que necesitas. Solo disponibles a nivel de organización o proyecto.

```bash
# Crear un rol custom en un proyecto
gcloud iam roles create mi_rol_lectura_sql \
  --project=mi-proyecto \
  --title="Solo lectura Cloud SQL" \
  --description="Permite conectar y leer, nada más" \
  --permissions="cloudsql.instances.connect,cloudsql.instances.get" \
  --stage=GA
```

**Riesgo**: los custom roles los mantienes tú. Si Google añade un nuevo permiso peligroso a un servicio, no se añade automáticamente a tu rol (en predefinidos sí). Hay que auditarlos periódicamente.

---

## 🤖 Service Accounts (SAs) — Identidades para máquinas

Un Service Account es como un "usuario robot". No tiene contraseña humana — las apps lo usan para autenticarse en GCP sin necesitar credenciales de persona.

**Cuándo usarlo**: cualquier app, script, VM, contenedor o función que necesite llamar a APIs de GCP.

### Tipos de SA

| Tipo | Gestionado por | Uso |
|---|---|---|
| **User-managed SA** | Tú | Tus apps. Tú creates, rotas claves, asignas roles |
| **Default SA** | GCP (auto) | Se crea al activar ciertos servicios. Frecuentemente sobre-permisado. |
| **Google-managed SA** | Google | Servicios internos de GCP. No las tocas. |

### Cómo funciona una SA

```bash
# Crear una SA
gcloud iam service-accounts create mi-app-sa \
  --display-name="SA para mi aplicación" \
  --project=mi-proyecto

# Asignarle un rol sobre un recurso específico (bucket GCS)
gcloud storage buckets add-iam-policy-binding gs://mi-bucket \
  --member="serviceAccount:mi-app-sa@mi-proyecto.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

### Clave JSON vs Workload Identity — El dilema de las claves

Una SA puede autenticarse de dos formas:

| Método | Cómo funciona | Riesgo |
|---|---|---|
| **Clave JSON** | Descargas un archivo `.json` con credenciales privadas | Si se filtra (en git, logs, etc.) → compromiso total |
| **Workload Identity / ADC** | La app toma credenciales del entorno de forma automática | Sin claves que rotar ni filtrar. **Preferido siempre** |

**Application Default Credentials (ADC)**: cuando corres código en GCP (VM, Cloud Run, GKE), las librerías cliente buscan credenciales automáticamente en el entorno. No hace falta clave JSON.

```bash
# En local, para desarrollo, autenticarte como tú mismo
gcloud auth application-default login

# Nunca hagas esto en producción:
# export GOOGLE_APPLICATION_CREDENTIALS=/path/to/clave.json  ← peligro
```

> **Nota de seguridad crítica**: las claves JSON de SA son el vector de ataque más frecuente en GCP. Si no puedes evitar usarlas, rótalas cada 90 días y almacénalas en Secret Manager (ver abajo).

### SA como recurso vs SA como identidad

Una SA tiene doble naturaleza:
- **Como identidad**: a quién le asignas roles para que pueda hacer cosas
- **Como recurso**: quién puede *usar* esa SA (impersonar)

El permiso `iam.serviceAccounts.actAs` permite que un principal use una SA. Es muy potente — limítalo.

---

## 🛡️ Principio de mínimo privilegio

La regla más importante en IAM. Solo dar el permiso mínimo necesario para que algo funcione.

**En la práctica**:

1. Empieza sin permisos. Añade solo lo que falle.
2. Usa roles predefinidos, no primitivos.
3. Asigna roles al nivel de recurso más específico posible (ej: a un bucket concreto, no a todo el proyecto).
4. Usa grupos, no individuos, para simplificar la gestión.
5. Audita regularmente con IAM Recommender.

```bash
# Ver recomendaciones de IAM Recommender (puede sugerir quitar permisos no usados)
gcloud recommender recommendations list \
  --recommender=google.iam.policy.Recommender \
  --project=mi-proyecto \
  --location=global
```

---

## 🏢 Org Policies — Guardrails a nivel organización

Mientras IAM controla "quién puede hacer qué", las **Org Policies** controlan "qué está permitido hacer en absoluto", independientemente de los permisos IAM.

Son restricciones que el administrador de la organización impone y que no pueden saltarse con IAM. Ejemplos reales:

| Constraint | Efecto |
|---|---|
| `constraints/iam.disableServiceAccountKeyCreation` | Nadie puede crear claves JSON de SA |
| `constraints/compute.restrictCloudSQLInstances` | Limita qué regiones pueden tener Cloud SQL |
| `constraints/iam.allowedPolicyMemberDomains` | Solo se pueden añadir miembros de dominios aprobados |
| `constraints/gcp.resourceLocations` | Fuerza que recursos se creen solo en ciertas regiones |

```bash
# Ver políticas de org activas
gcloud org-policies list --organization=ORGANIZATION_ID

# Aplicar una política (requiere rol orgpolicy.policyAdmin)
gcloud org-policies set-policy policy.yaml --organization=ORGANIZATION_ID
```

Las Org Policies son el mecanismo de compliance corporativo: cumplimiento de GDPR (datos solo en EU), SOC2, restricciones de red, etc.

---

## 🔑 Secret Manager — Gestión de secretos

**El problema**: credenciales de BD, API keys, tokens OAuth. No pueden ir en variables de entorno en el código ni en repositorios git (ver [[MOC_Ciberseguridad]]).

**Secret Manager** es el almacén centralizado y auditado de secretos de GCP. Equivale a HashiCorp Vault o AWS Secrets Manager.

### Conceptos clave

- **Secret**: el objeto con nombre (`mi-db-password`). Tiene metadatos y una política de acceso IAM propia.
- **Secret version**: el valor real del secreto. Pueden coexistir versiones múltiples (útil para rotación).
- **Acceso**: siempre con `roles/secretmanager.secretAccessor` sobre el secret específico.

```bash
# Crear un secreto
echo -n "mi_password_seguro" | gcloud secrets create mi-db-password \
  --data-file=- \
  --replication-policy=automatic

# Dar acceso a una SA
gcloud secrets add-iam-policy-binding mi-db-password \
  --member="serviceAccount:mi-app-sa@mi-proyecto.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Leer el secreto (en código o CLI)
gcloud secrets versions access latest --secret=mi-db-password

# Rotar: añadir nueva versión y deshabilitar la anterior
echo -n "nuevo_password" | gcloud secrets versions add mi-db-password --data-file=-
gcloud secrets versions disable 1 --secret=mi-db-password
```

### Acceso desde código (Python)

```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
name = "projects/mi-proyecto/secrets/mi-db-password/versions/latest"
response = client.access_secret_version(request={"name": name})
secret_value = response.payload.data.decode("UTF-8")
```

La app necesita `roles/secretmanager.secretAccessor` en su SA. Sin clave JSON en el código.

---

## 🔒 Cloud KMS — Gestión de claves criptográficas

**El problema que resuelve**: Secret Manager guarda secretos como texto. ¿Y si necesitas cifrar tus propios datos, o controlar quién tiene la clave de cifrado de un bucket/disco/BD?

**Cloud KMS** (Key Management Service) gestiona claves criptográficas de forma centralizada. No puedes exportar la clave raw — solo usarla a través de la API.

### Conceptos

```
Key Ring → Key → Key Version
```

- **Key Ring**: contenedor de claves, ligado a una región.
- **Key**: una clave nombrada, con propósito definido (ENCRYPT_DECRYPT, ASYMMETRIC_SIGN, etc.).
- **Key Version**: el material criptográfico real. Puede rotarse.

### Casos de uso principales

| Caso | Qué hace KMS |
|---|---|
| **CMEK** (Customer-Managed Encryption Keys) | Tú controlas la clave que GCP usa para cifrar tus datos en GCS/BigQuery/etc. |
| **Cifrado en aplicación** | Tu app cifra/descifra datos usando la API de KMS |
| **Firma digital** | Claves asimétricas para firmar tokens, artefactos, etc. |

```bash
# Crear un key ring y una clave de cifrado simétrica
gcloud kms keyrings create mi-keyring --location=europe-west1
gcloud kms keys create mi-clave-datos \
  --keyring=mi-keyring \
  --location=europe-west1 \
  --purpose=encryption

# Cifrar un archivo
gcloud kms encrypt \
  --key=mi-clave-datos \
  --keyring=mi-keyring \
  --location=europe-west1 \
  --plaintext-file=datos.txt \
  --ciphertext-file=datos.enc

# Descifrar
gcloud kms decrypt \
  --key=mi-clave-datos \
  --keyring=mi-keyring \
  --location=europe-west1 \
  --ciphertext-file=datos.enc \
  --plaintext-file=datos_recuperados.txt
```

**CMEK vs CSEK vs Google-managed keys**:

| Tipo | Quien gestiona | Control | Overhead |
|---|---|---|---|
| Google-managed | Google | Ninguno tuyo | Cero |
| CMEK (Cloud KMS) | Tú (via KMS) | Puedes revocar/rotar | Medio |
| CSEK (Customer-supplied) | Tú (clave externa) | Total | Alto — tienes que guardarla tú |

Para la mayoría de casos: CMEK es el equilibrio correcto si necesitas control, sin la complejidad de gestionar claves externas.

---

## ⚠️ Errores y costes comunes

| Error | Consecuencia | Prevención |
|---|---|---|
| SA con `roles/editor` a nivel proyecto | Si la SA se compromete, atacante controla todo el proyecto | Mínimo privilegio, roles específicos |
| Clave JSON de SA en repositorio git | Filtración de credenciales (frecuente, crítico) | Usar ADC, o Secret Manager si necesitas la clave |
| `allUsers` en bucket GCS | Datos públicos accidentales — puede costar miles en egress | Org Policy + auditorías de Cloud Asset Inventory |
| Olvidar deshabilitar SAs inactivas | Superficie de ataque innecesaria | Auditoría mensual de SAs no usadas |
| Custom roles sin revisar | Permisos obsoletos acumulados | Revisión trimestral con IAM Recommender |

Secret Manager tiene un **free tier** de 6 versiones de secretos activas y 10.000 operaciones de acceso al mes. KMS cobra por operaciones de criptografía (~$0.03/10.000 ops) y por versiones de clave activas ($0.06/versión/mes).

---

## 🛠️ Aplícalo / Práctica

1. **Mínimo privilegio desde cero**: crea un proyecto de prueba, una SA, y dale solo `roles/storage.objectViewer` sobre un bucket concreto. Verifica que no puede listar buckets del proyecto (`gcloud storage ls`) pero sí leer objetos del bucket específico.

2. **Secret Manager flow completo**: guarda una cadena ficticia como secreto, lee desde CLI, añade segunda versión, deshabilita la primera. Simula acceso desde una SA con `secretAccessor`.

3. **Auditoría IAM**: sobre cualquier proyecto tuyo, corre:
   ```bash
   gcloud projects get-iam-policy mi-proyecto --format=json | \
     python3 -c "import json,sys; p=json.load(sys.stdin); [print(b) for b in p['bindings']]"
   ```
   Identifica cualquier binding con roles primitivos o `allUsers`.

4. **IAM Recommender**: activa la API y lista recomendaciones. Observa qué permisos recomienda eliminar por no haberse usado en 90 días.

5. **Org Policy local (si tienes acceso a org)**: aplica `constraints/iam.disableServiceAccountKeyCreation` en un proyecto de sandbox y comprueba que ya no puedes crear claves JSON.

---

## Conexiones

- [[MOC_GCP]]
- [[01-fundamentos-cloud-y-gcp]]
- [[03-computo]]
- [[04-redes]]
- [[08-contenedores-y-serverless]]
- [[09-devops-iac-observabilidad]]
- [[11-costes-y-buenas-practicas]]
- [[12-certificaciones-y-aprendizaje]]
- [[MOC_Ciberseguridad]]
- [[MOC_Desarrollo_Software]]
