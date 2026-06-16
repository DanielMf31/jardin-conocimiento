---
title: Qué es GitLab y sus ediciones
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/git, programacion/cicd]
type: nota
status: en-progreso
source: claude-code
aliases: [gitlab-intro, que-es-gitlab]
---

# 🏗️ Qué es GitLab y sus ediciones

## El problema que resuelve

En cualquier proyecto de software coexisten varias herramientas distintas: un repositorio Git, un sistema de tickets/issues, una pipeline de integración continua, un registro de contenedores Docker, una herramienta de revisión de código... En la práctica, los equipos combinan GitHub + Jenkins + Jira + Docker Hub + Confluence, y pasan tiempo considerable manteniendo las integraciones entre ellas y sincronizando contexto.

**GitLab apuesta por una sola aplicación** que cubra todo ese ciclo sin integraciones externas. La idea es que el código, los tests, los despliegues, la planificación y la seguridad compartan el mismo modelo de datos, la misma interfaz y las mismas credenciales.

> "Single application for the whole DevOps lifecycle" — lema oficial de GitLab.

El resultado práctico: abres una tarea en Issues, creas una rama desde ahí, haces tu Merge Request, la pipeline se lanza automáticamente, y el deploy queda trazado en el mismo hilo. Sin cambiar de pestaña ni de herramienta.

---

## 🗺️ Panorama del ciclo DevOps que cubre GitLab

GitLab divide su funcionalidad en etapas del ciclo DevOps. Esto no es marketing: cada etapa corresponde a una sección real de la interfaz y a una categoría de features:

| Etapa | Qué hace GitLab aquí | Equivalente externo típico |
|---|---|---|
| **Plan** | Issues, tableros Kanban, milestones, roadmaps | Jira, Linear, Trello |
| **Create** | Repositorios Git, revisión de código (Merge Requests) | GitHub, Bitbucket |
| **Verify** | CI/CD pipelines (`.gitlab-ci.yml`), test reports | Jenkins, CircleCI, GitHub Actions |
| **Package** | Container Registry, Package Registry (npm, PyPI…) | Docker Hub, Artifactory |
| **Release** | Deploy, feature flags, release notes | Spinnaker, LaunchDarkly |
| **Configure** | Kubernetes integration, Helm charts | ArgoCD, Helm |
| **Monitor** | Métricas de aplicación, alertas, trazas | Grafana, Datadog |
| **Secure** | SAST, DAST, dependency scanning, secrets detection | Snyk, SonarQube |

No tienes que usar todas las etapas; puedes adoptarlas incrementalmente. Muchos equipos empiezan solo con repositorios + CI y añaden el resto cuando escalan.

---

## 🌐 GitLab.com (SaaS) vs Self-Managed (Autoalojado)

Esta es la diferencia más importante entre GitLab y GitHub para el mercado profesional: **GitLab puedes instalarlo tú mismo en tus servidores**, y eso es algo que muchas empresas exigen por razones regulatorias o de seguridad.

### Conceptos clave
- **SaaS** (Software as a Service): GitLab gestiona la infraestructura. Tú solo creas cuenta y usas.
- **Self-managed** (autoalojado): instalas GitLab en tu propia máquina, VM o clúster. Tú gestionas actualizaciones, backups, escalado.

| Dimensión | GitLab.com (SaaS) | Self-Managed |
|---|---|---|
| **Instalación** | Ninguna — cuenta gratuita | Requiere servidor + instalación |
| **Actualizaciones** | Automáticas, gestionadas por GitLab | Manuales, responsabilidad tuya |
| **Control de datos** | Los datos están en servidores de GitLab (EE.UU.) | Los datos están en tu infraestructura |
| **Cumplimiento normativo** | Depende de los acuerdos de GitLab | Control total (GDPR, ISO 27001, etc.) |
| **Escalado** | Automático | Debes dimensionar y mantener |
| **Precio base** | Free tier generoso; pago por usuario/mes | Requiere infraestructura propia (coste hardware/cloud) |
| **Runners CI/CD** | Runners compartidos incluidos (minutos limitados en Free) | Tú configuras tus propios Runners |
| **Ideal para** | Proyectos personales, startups, equipos pequeños | Empresas con datos sensibles, regulación estricta, o escala grande |

> **Analogía de hardware**: SaaS es como comprar una PCB ya montada; self-managed es fabricar la placa tú mismo. Tienes más control pero más responsabilidad.

### Cuándo elegir cada uno

**GitLab.com si:**
- Empiezas a aprender o prototipas.
- Tu equipo es pequeño y no tienes DevOps dedicado.
- No hay restricciones regulatorias sobre dónde residen los datos.

**Self-managed si:**
- Trabajas con datos confidenciales (salud, finanzas, defensa).
- La empresa requiere auditoría completa de la cadena de herramientas.
- Tienes infraestructura propia y quieres integrar GitLab en ella.
- Necesitas customizar la instancia (LDAP propio, autenticación SSO corporativo, etc.).

---

## 📦 Ediciones: CE vs EE

GitLab tiene un modelo open-core: el núcleo es software libre, y las features avanzadas son de pago.

### Community Edition (CE)
- Licencia: **MIT** — puedes usar, modificar y redistribuir libremente.
- Incluye: repositorios Git, Merge Requests, Issues básicos, CI/CD completo, Container Registry, Pages.
- **Es muy capaz**. Para la mayoría de proyectos personales y muchas empresas medianas, CE es suficiente.
- Código fuente en [gitlab.com/gitlab-org/gitlab-foss](https://gitlab.com/gitlab-org/gitlab-foss).

### Enterprise Edition (EE)
- Licencia propietaria, con tiers **Premium** y **Ultimate**.
- Incluye todo lo de CE más features avanzadas según tier.
- El código también es público (puedes leerlo), pero no puedes redistribuirlo sin licencia.

| Feature | CE (Free) | EE Premium | EE Ultimate |
|---|---|---|---|
| Repositorios Git ilimitados | ✅ | ✅ | ✅ |
| CI/CD pipelines | ✅ | ✅ | ✅ |
| Container Registry | ✅ | ✅ | ✅ |
| GitLab Pages | ✅ | ✅ | ✅ |
| Issues y tableros básicos | ✅ | ✅ | ✅ |
| Merge Requests con aprobaciones | Básico | **Avanzado** (reglas por rama) | ✅ |
| Protected branches por rol | Básico | **Por grupo** | ✅ |
| Subgrupos anidados | 1 nivel | Ilimitados | ✅ |
| Auditoría de eventos | Limitada | Completa | ✅ |
| Epics y roadmaps (planificación) | ❌ | ✅ | ✅ |
| SAST / Dependency Scanning | Básico | ✅ | ✅ |
| DAST, Fuzzing | ❌ | Limitado | ✅ |
| Compliance management | ❌ | ❌ | ✅ |
| Value stream analytics | ❌ | ✅ | ✅ |

> Los precios (2024 aprox.) son ~$29/usuario/mes para Premium y ~$99/usuario/mes para Ultimate en SaaS. Self-managed tiene precios similares por usuario.

### La trampa del "free tier en GitLab.com"
GitLab.com Free usa la EE (código Enterprise) pero con la mayoría de features avanzadas desactivadas por licencia. No es lo mismo que instalar CE self-managed. En la práctica, GitLab.com Free es funcional para proyectos personales y académicos, pero en equipos comerciales pronto chocas con los límites de aprobaciones o de seguridad.

---

## 🔍 GitLab vs GitHub: diferencias estratégicas

| Dimensión | GitLab | GitHub |
|---|---|---|
| **Self-hosting** | Primera clase, muy completo | GitHub Enterprise (caro, complejo) |
| **CI/CD nativo** | `.gitlab-ci.yml` integrado desde 2012 | GitHub Actions (llegó en 2018) |
| **Open source del núcleo** | CE bajo MIT | No (propietario de Microsoft) |
| **Modelo de negocio** | Open-core + SaaS | SaaS + Enterprise (Microsoft) |
| **Ecosistema** | Más fuerte en DevOps enterprise | Mayor comunidad OSS |
| **Interfaz de planificación** | Más completa (epics, roadmaps) | Básica en Free |

No hay un ganador universal. GitHub domina en open source y comunidad; GitLab domina en entornos enterprise con self-hosting y DevOps integrado.

---

## ⚠️ Errores comunes al empezar

- **Confundir GitLab.com con "GitLab"**: GitLab es el software, GitLab.com es una instancia SaaS. Cuando una empresa dice "tenemos GitLab", suele referirse a una instancia self-managed propia.
- **Pensar que CE es una versión recortada inutilizable**: CE tiene CI/CD completo, Runners, Registry, etc. Solo faltan features enterprise de aprobaciones complejas, seguridad avanzada y planificación estratégica.
- **Instalar EE pensando que es gratis**: EE instalado sin licencia funciona como CE; no activa features de pago automáticamente.
- **Mezclar conceptos SaaS/self-managed**: los minutos de CI, los Runners compartidos y los límites de almacenamiento son cosas de GitLab.com; en self-managed tú pones los Runners y el almacenamiento.

---

## 🛠️ Aplícalo a tus proyectos

**app web** (FastAPI + React + Docker):
- Puedes usar GitLab.com Free y ya tienes CI/CD real: linting, tests, build de imágenes Docker, todo en `.gitlab-ci.yml`.
- Si en el futuro la app maneja datos de salud de usuarios reales, self-managed en un VPS propio daría control total sobre dónde residen los datos — relevante dado tu contexto EDS/POTS y privacidad médica.

**proyecto embebido** (PlatformIO / firmware):
- GitLab CI puede correr builds de firmware (PlatformIO CLI en Docker) y archivar los `.bin` como artefactos descargables — sin Jenkins ni nada externo.

**Bóveda Obsidian**:
- Un repositorio GitLab con CI puede hacer lint de Markdown, verificar links rotos, o publicar un subset como GitLab Pages si algún día quieres una versión web de tus notas.

---

## Conexiones

- [[MOC_GitLab]]
- [[02-conceptos-grupos-proyectos-permisos]]
- [[03-repos-y-flujo-git]]
- [[05-gitlab-cicd-fundamentos]]
- [[06-runners]]
- [[10-autoalojamiento]]
- [[12-gitlab-vs-alternativas]]
- [[MOC_Desarrollo_Software]]
