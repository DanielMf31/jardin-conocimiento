---
title: MOC GCP (Google Cloud)
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, moc]
type: moc
status: en-progreso
source: claude-code
aliases: [MOC GCP, GCP MOC, MOC Google Cloud]
---

# MOC GCP (Google Cloud)

> Mapa de **Google Cloud**: fundamentos, IAM, cómputo, redes, almacenamiento, BBDD, datos
> (BigQuery), contenedores/serverless, DevOps/IaC, IA (Vertex), costes y certificaciones.
> Clúster en `50_Areas/Ingenieria/Programacion/GCP/`.
>
> Área padre: [[MOC_Programacion]] · doble interés.

## Índice y registros vivos
- [[GCP/00_README|README del clúster]] — qué es y cómo recorrerlo
- [[GCP/00_Dudas_y_Preguntas|Dudas y Preguntas]]

## Documentación por tema
| # | Tema | Doc |
|---|---|---|
| 01 | Fundamentos cloud + GCP (jerarquía, gcloud, Cloud Shell) | [[01-fundamentos-cloud-y-gcp]] |
| 02 | IAM y seguridad (roles, service accounts, mínimo privilegio) | [[02-iam-y-seguridad]] |
| 03 | Cómputo (Compute Engine, **Cloud Run**, GKE, Functions) | [[03-computo]] |
| 04 | Redes (VPC, firewall, Load Balancing, DNS/CDN) | [[04-redes]] |
| 05 | Almacenamiento (Cloud Storage + clases, discos) | [[05-almacenamiento]] |
| 06 | Bases de datos (Cloud SQL, Firestore, Bigtable, Spanner) | [[06-bases-de-datos]] |
| 07 | **Datos y analítica** (BigQuery, Pub/Sub, Dataflow) | [[07-datos-y-analitica]] |
| 08 | Contenedores y serverless (Cloud Run, GKE, Artifact Registry) | [[08-contenedores-y-serverless]] |
| 09 | DevOps, IaC y observabilidad (Cloud Build, Terraform, Logging) | [[09-devops-iac-observabilidad]] |
| 10 | IA/ML (Vertex AI, Gemini API) | [[10-ia-ml-vertex]] |
| 11 | Costes y buenas prácticas (free tier, presupuestos, well-architected) | [[11-costes-y-buenas-practicas]] |
| 12 | Certificaciones y aprendizaje (ACE, Skills Boost) | [[12-certificaciones-y-aprendizaje]] |

## Roadmap de aprendizaje
1. **Base**: [[01-fundamentos-cloud-y-gcp]] → [[02-iam-y-seguridad]] → [[03-computo]] → [[04-redes]]/[[05-almacenamiento]].
2. **Practica gratis**: free tier + **Google Cloud Skills Boost** (labs guiados); despliega un en **Cloud Run** ([[08-contenedores-y-serverless]]).
3. **Especializa**: datos ([[07-datos-y-analitica]]), app/infra ([[03-computo]], [[09-devops-iac-observabilidad]]) o IA ([[10-ia-ml-vertex]]).
4. **Cert** (opcional): [[12-certificaciones-y-aprendizaje]] — la **Associate Cloud Engineer** es la de mejor relación esfuerzo/valor.
5. **No te asustes con la factura**: [[11-costes-y-buenas-practicas]] desde el día 1.

## Conexiones
- [[MOC_Programacion]] — área raíz
- [[MOC_GitLab]] · [[MOC_Desarrollo_Software]] — CI/CD que despliega a GCP
- [[MOC_Ciberseguridad]] — IAM y seguridad en la nube
