---
title: "GitLab vs alternativas: qué aprender"
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/github, programacion/herramientas]
type: nota
status: en-progreso
source: claude-code
aliases: [gitlab-vs-github, comparativa-git-platforms, alternativas-gitlab]
---

# 🔀 GitLab vs alternativas: qué aprender

## Por qué importa esta pregunta

Cuando empiezas con DevOps/CI/CD, la primera trampa es aprender **la herramienta** en lugar de aprender **el concepto**. GitLab, GitHub, Bitbucket y Gitea/Forgejo resuelven el mismo problema central: alojar repositorios Git y automatizar el ciclo de vida del software. Pero tienen filosofías, pesos y nichos de mercado muy distintos.

Saber cuándo usar cada uno — y qué vale la pena aprender en profundidad — es una habilidad de ingeniería transferible, no solo una preferencia personal.

---

## 🗺️ El panorama: qué plataforma hace qué

Todas comparten el núcleo: repositorios Git + pull/merge requests + sistema de CI/CD. Las diferencias están en el **alcance** (¿solo repositorios o plataforma DevOps completa?), el **modelo de despliegue** (SaaS / auto-alojado / ambos) y el **coste de operación**.

---

## 📊 Tabla comparativa

| Criterio | **GitLab** | **GitHub** | **Gitea / Forgejo** | **Bitbucket** |
|---|---|---|---|---|
| **Modelo** | SaaS + autoalojado | SaaS + autoalojado | Solo autoalojado | SaaS + autoalojado (Atlassian) |
| **Peso en servidor** | Muy pesado (4–8 GB RAM mínimo real) | N/A en SaaS; pesado en self-hosted | Muy ligero (~200–500 MB RAM) | Medio (Cloud gestionado por Atlassian) |
| **Alcance** | Plataforma DevOps completa (issues, CI, registry, security, pages, packages…) | Repositorios + Actions + Marketplace muy rico | Repositorios Git básico + CI limitado (Forgejo tiene más) | Repositorios + Pipelines + integración Jira/Confluence |
| **CI/CD nativo** | GitLab CI/CD (`.gitlab-ci.yml`) — muy potente y maduro | GitHub Actions (`.github/workflows/*.yml`) — ecosistema de actions enorme | Forgejo Actions (compatible con GitHub Actions) / Gitea CI rudimentario | Bitbucket Pipelines (YAML, menos potente) |
| **Mantenimiento si autoalojas** | Alto: actualizaciones frecuentes, migración DB, mucha RAM | Medio (GitHub Enterprise es costoso) | Muy bajo: binario único, actualizar = reemplazar binario | N/A en Cloud; alto en Data Center |
| **Mercado laboral** | ★★★★☆ (muy demandado en empresas medianas/corporativo europeo) | ★★★★★ (dominante en OSS, startups, EE.UU.) | ★★☆☆☆ (homelab, comunidades pequeñas) | ★★★☆☆ (entornos Atlassian, legacy) |
| **Gratis en SaaS** | Sí, tier Free con CI (400 min/mes) | Sí, muy generoso (Actions gratis en repos públicos) | N/A (autoalojado) | Sí (límite de usuarios y minutos) |
| **Community/OSS** | GitLab CE es open-source (core) | Cerrado (solo GitHub Enterprise es propietario) | Forgejo es fork comunitario de Gitea, 100% FOSS | Cerrado (Atlassian) |

---

## 🎯 Cuándo usar cada uno

### GitLab
**Úsalo cuando:**
- La empresa ya lo usa (muy común en Europa, corporativo, defensa, industria).
- Necesitas una plataforma DevOps integrada sin montar herramientas externas: CI + registry + gestión de seguridad (SAST, dependency scanning) + GitOps todo en un sitio.
- El equipo necesita autoalojar por cumplimiento normativo (datos sensibles, regulación).

**No lo uses cuando:**
- Eres una persona sola en homelab con una Raspberry Pi o VPS de 2 GB: GitLab lo aplastará.
- Solo necesitas un repositorio simple con un CI básico.

### GitHub
**Úsalo cuando:**
- Proyecto open-source o colaboración pública: es donde está la comunidad.
- Startup o proyecto personal: el tier gratuito es muy generoso y Actions tiene un ecosistema de integraciones enorme.
- Quieres aprender CI/CD con menos fricción: SaaS, sin administrar nada, feedback inmediato.

**No lo uses cuando:**
- Necesitas control total sobre los datos o el servidor (algunos entornos regulados exigen esto).

### Gitea / Forgejo
**Úsalo cuando:**
- Homelab, servidor personal, NAS, VPS pequeño.
- Quieres un espejo privado de tus repos con cero dependencia de terceros.
- Forgejo Actions (si usas Forgejo ≥1.21) te da CI compatible con GitHub Actions sin el peso de GitLab.

**No lo uses cuando:**
- El equipo espera las funcionalidades completas de GitLab/GitHub (security dashboards, registry maduro, pages…).

**Diferencia Gitea vs Forgejo:** Forgejo es el fork comunitario surgido en 2022 cuando la gobernanza de Gitea se centralizó en una empresa. Forgejo tiene desarrollo más abierto y es la recomendación actual para homelab.

### Bitbucket
**Úsalo cuando:**
- Ya usas Jira y Confluence: la integración nativa es genuinamente buena.
- El equipo ya tiene licencia Atlassian.

**No lo uses cuando:**
- Empiezas desde cero: tiene menos comunidad, menos recursos de aprendizaje, y el ecosistema de integraciones no compite con GitHub Actions ni con GitLab CI.

---

## 🏠 Qué autoalojar: la decisión correcta

La regla práctica:

```
¿Necesitas plataforma DevOps completa (CI robusto, registry, security, gestión de proyectos)?
  → GitLab self-hosted (pero necesitas ≥8 GB RAM reales y tiempo de admin)

¿Necesitas solo repositorios privados + CI ligero + homelab?
  → Forgejo (binario único, ~300 MB RAM, actualización trivial)

¿No quieres administrar nada?
  → GitHub SaaS o GitLab SaaS (tier free)
```

**Escenario típico para un ingeniero individual aprendiendo DevOps:**

1. Aprende CI/CD en **GitHub Actions o GitLab SaaS** — sin pagar ni administrar servidores, feedback inmediato.
2. Pon un **Forgejo** en tu homelab/VPS como espejo privado y para experimentar con runners propios.
3. Cuando trabajes en empresa, adaptarás los conceptos a lo que usen ellos (probablemente GitLab o GitHub Enterprise).

---

## 💼 Qué tiene valor de mercado aprender

Esta es la pregunta más importante y la que menos se responde directamente.

### Los conceptos transfieren, la sintaxis no

Los conceptos de CI/CD son universales:

| Concepto | GitLab CI | GitHub Actions | Bitbucket Pipelines |
|---|---|---|---|
| Pipeline como código | `.gitlab-ci.yml` | `.github/workflows/*.yml` | `bitbucket-pipelines.yml` |
| Etapa (stage) | `stages: [build, test, deploy]` | `jobs:` con `needs:` | `step:` con pipelines |
| Runner / agente | GitLab Runner | GitHub-hosted runner / self-hosted | Atlassian runner |
| Artefacto | `artifacts: paths:` | `actions/upload-artifact` | `artifacts:` |
| Variable de entorno / secreto | CI/CD Variables (Settings > CI) | Secrets (Settings > Secrets) | Repository variables |
| Cache de dependencias | `cache: key:` | `actions/cache` | `caches:` |
| Entorno (staging/prod) | Environments + deployment | `environment:` en job | `deployment:` |
| Trigger de rama/tag | `only/except` o `rules:` | `on: push: branches:` | `branches:` |

Si entiendes **por qué** existe cada uno de estos conceptos, aprender la sintaxis de otra plataforma te lleva horas, no semanas.

### Los dos grandes del mercado: GitLab CI y GitHub Actions

```
GitHub Actions  →  open source, startups, EE.UU., frontend/backend web
GitLab CI/CD    →  corporativo, Europa, industria, DevSecOps, Kubernetes
```

**Recomendación concreta:** aprende uno en profundidad y conoce el otro superficialmente. Para autoaprendizaje, empieza por **GitHub Actions** (más recursos, más ejemplos, más proyectos OSS donde ver pipelines reales). Luego estudia **GitLab CI** porque es donde vas a encontrar más trabajo en entornos industriales/empresariales europeos.

### Qué profundizar (por orden de retorno en el mercado)

1. **Conceptos universales** (runners, stages, artefactos, secrets, cachés, environments): aprende esto una vez, vale para todo.
2. **GitLab CI/CD** (`.gitlab-ci.yml`, runners, variables, protected branches, environments): alta demanda en empresas medianas y grandes.
3. **GitHub Actions** (workflows, marketplace, self-hosted runners, reusable workflows): esencial para OSS y startups.
4. **Docker + registry**: presente en ambas plataformas. Saber construir y publicar imágenes es más valioso que saber la sintaxis exacta del YAML de cada plataforma.
5. **Kubernetes/GitOps** (ArgoCD, Flux): nivel avanzado, pero GitLab tiene integración nativa que se usa mucho en entornos cloud.

Lo que **no** vale la pena profundizar para el mercado: Bitbucket Pipelines (nicho Atlassian), Gitea CI (casi no existe en empresas), Forgejo Actions (solo homelab por ahora).

---

## 🧪 Bloques de código: sintaxis equivalente

### Pipeline mínimo: build + test

**GitLab CI (`.gitlab-ci.yml`)**
```yaml
# Etapas del pipeline (orden de ejecución)
stages:
  - build
  - test

# Job de build
build-app:
  stage: build
  image: python:3.12-slim          # imagen Docker donde corre el job
  script:
    - pip install -r requirements.txt
  artifacts:
    paths:
      - dist/                      # guarda el artefacto para el siguiente stage

# Job de test (solo en ramas que no sean main)
run-tests:
  stage: test
  image: python:3.12-slim
  script:
    - pytest tests/
  rules:
    - if: '$CI_COMMIT_BRANCH != "main"'   # condicional GitLab
```

**GitHub Actions (`.github/workflows/ci.yml`)**
```yaml
name: CI

on:
  push:
    branches-ignore:
      - main                        # equivalente al rules: de arriba

jobs:
  build:
    runs-on: ubuntu-latest          # runner gestionado por GitHub
    steps:
      - uses: actions/checkout@v4   # action del marketplace: clona el repo
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt

  test:
    needs: build                    # equivalente a stages: en GitLab
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pytest tests/
```

Los dos pipelines hacen lo mismo. La diferencia clave: en GitLab los stages son secuenciales por defecto; en GitHub Actions declaras dependencias con `needs:`.

---

## ⚠️ Errores comunes al elegir plataforma

| Error | Por qué es un error | Alternativa |
|---|---|---|
| Autoalojar GitLab en un VPS de 2 GB "para aprender" | GitLab consume 4–8 GB reales; el servidor irá lento o crasheará | Usa GitLab SaaS gratis o Forgejo |
| Aprender solo GitHub Actions y asumir que GitLab es igual | La sintaxis difiere bastante; el modelo mental también | Aprende los conceptos, luego adapta la sintaxis |
| Ignorar Forgejo porque "no es del mercado" | Para homelab y privacidad es perfecto; te enseña a gestionar runners propios sin el peso de GitLab | Forgejo para práctica de autoalojamiento |
| Usar Bitbucket sin ya estar en el ecosistema Atlassian | Curva de aprendizaje, menos recursos, menos comunidad | GitHub o GitLab son mejor inversión de tiempo |
| Pensar que la plataforma es lo más importante | Lo importante es el concepto de CI/CD; la plataforma es el vehículo | Aprende conceptos primero |

---

## 🔧 Aplícalo a tus proyectos

**Para app web (FastAPI + React + Docker):**
- Ya tienes Docker Compose: el siguiente paso natural es un pipeline CI que construya y testee la imagen en cada push.
- En GitHub Actions: `.github/workflows/ci.yml` con `docker build` + `pytest` dentro del contenedor.
- En GitLab SaaS: `.gitlab-ci.yml` con `image: docker:latest` y `services: [docker:dind]`.
- El concepto (construir imagen, correr tests, publicar al registry) es el mismo en ambas plataformas.

**Para proyecto embebido (PlatformIO/embebido):**
- GitHub Actions tiene runners con `platformio` disponibles; puedes compilar firmware en CI para verificar que el código compila sin hardware físico.
- GitLab CI también puede hacerlo con una imagen Docker que tenga PlatformIO instalado.

**Para la bóveda y homelab:**
- Forgejo en un VPS pequeño o Raspberry Pi: privacidad, espejo de repos, y si usas Forgejo ≥1.21, puedes montar runners compatibles con GitHub Actions para experimentar.

---

## Conexiones

- [[MOC_GitLab]]
- [[MOC_Desarrollo_Software]]
- [[01-que-es-gitlab]]
- [[05-gitlab-cicd-fundamentos]]
- [[06-runners]]
- [[07-cicd-avanzado]]
- [[10-autoalojamiento]]
- [[11-administracion-backups-upgrades]]
