---
title: "Conceptos: grupos, proyectos y permisos"
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/gestion-equipos]
type: nota
status: en-progreso
source: claude-code
aliases: [gitlab-jerarquia, gitlab-grupos, gitlab-permisos]
---

# 🏗️ Conceptos: grupos, proyectos y permisos

## ¿Por qué importa entender esto primero?

Antes de tocar un pipeline o una merge request, necesitas entender cómo GitLab **organiza el trabajo**. Si llegas directamente a "crear un proyecto", te vas a perder la estructura que hace que GitLab escale de 1 persona a 500: la jerarquía de grupos.

El problema que resuelve: en un proyecto real, tienes múltiples repositorios (backend, frontend, infra, libs), múltiples equipos con distintos niveles de acceso, y necesitas que las reglas de CI/CD, los secretos y los permisos no tengan que configurarse repo por repo. La jerarquía de GitLab permite **heredar configuración hacia abajo** y **aislar acceso hacia arriba**.

---

## 🗺️ La jerarquía de GitLab

```
Instancia de GitLab (gitlab.com o tu servidor)
│
├── Grupo A                    ← namespace raíz
│   ├── Subgrupo A1
│   │   ├── Proyecto A1a      ← donde vive el código
│   │   └── Proyecto A1b
│   └── Subgrupo A2
│       └── Proyecto A2a
│
├── Grupo B
│   └── Proyecto B1
│
└── Usuario personal
    └── Proyecto personal     ← namespace personal (username)
```

### Los tres niveles que debes dominar

| Nivel | Qué es | Analogía |
|---|---|---|
| **Instancia** | El servidor GitLab completo. gitlab.com o tu GitLab autohospedado | El edificio entero |
| **Grupo / Subgrupo** | Contenedor de proyectos. Puede anidarse hasta 20 niveles | La empresa / el departamento |
| **Proyecto** | Un repositorio Git + su CI/CD + issues + registry | El producto concreto |

### ¿Qué es un namespace?

Un **namespace** es el "apellido" de una URL. Determina dónde vive algo:

```
gitlab.com/mi-empresa/backend-api
           ──────────  ───────────
           namespace   proyecto
           (grupo)

gitlab.com/danmf31/experimento-personal
           ───────  ────────────────────
           namespace   proyecto
           (usuario)
```

El namespace evita colisiones de nombres: dos empresas distintas pueden tener un repo llamado `api` sin conflicto.

---

## 👥 Grupos y subgrupos — cuándo y cómo usarlos

Un **grupo** es más que una carpeta. Cuando creas un grupo puedes:

- Definir **variables CI/CD** que todos sus proyectos heredan automáticamente (secretos, tokens de despliegue).
- Asignar **miembros** con su rol, y ese rol se propaga a todos los proyectos del grupo.
- Configurar **runners** compartidos para todos los proyectos.
- Aplicar reglas de **aprobación de MR** a nivel de grupo.

Los **subgrupos** añaden un nivel de separación lógica sin perder la herencia. Ejemplo real:

```
empresa/
├── plataforma/          ← subgrupo: equipo de plataforma
│   ├── infra-k8s
│   └── observabilidad
├── producto/            ← subgrupo: equipo de producto
│   ├── app-backend
│   ├── app-frontend
│   └── app-mobile
└── libs/                ← subgrupo: librerías compartidas
    ├── design-system
    └── shared-utils
```

Con esto, un secreto `DB_PASSWORD` definido en el grupo `empresa` llega a todos los proyectos de todos los subgrupos. Un secreto definido en `empresa/producto` solo llega a los tres proyectos de producto.

### Cuándo usar grupo vs. subgrupo vs. proyecto separado

| Situación | Decisión |
|---|---|
| Equipo independiente con acceso propio | Subgrupo nuevo |
| Mismo equipo, mismo acceso, distinto repo | Otro proyecto dentro del subgrupo actual |
| Empresa diferente / cliente diferente | Grupo raíz separado |
| Experimento personal tuyo | Namespace personal, sin grupo |

---

## 🔐 Los 5 roles de GitLab

GitLab usa **RBAC** (Role-Based Access Control — control de acceso basado en roles). Hay 5 roles en orden creciente de privilegio:

### Tabla de capacidades por rol

| Acción | Guest | Reporter | Developer | Maintainer | Owner |
|---|:---:|:---:|:---:|:---:|:---:|
| Ver código e issues | ✓ | ✓ | ✓ | ✓ | ✓ |
| Clonar repositorio | — | ✓ | ✓ | ✓ | ✓ |
| Crear issues / comentar | ✓ | ✓ | ✓ | ✓ | ✓ |
| Crear branches | — | — | ✓ | ✓ | ✓ |
| Crear merge requests | — | — | ✓ | ✓ | ✓ |
| Hacer push a branches protegidos | — | — | — | ✓ | ✓ |
| Mergear MRs | — | — | — | ✓ | ✓ |
| Editar settings del proyecto | — | — | — | ✓ | ✓ |
| Gestionar miembros del grupo | — | — | — | — | ✓ |
| Borrar el proyecto/grupo | — | — | — | — | ✓ |
| Gestionar runners, tokens de deploy | — | — | — | ✓ | ✓ |

> **Nota**: en GitLab.com, **Owner** solo existe a nivel de grupo, no de proyecto individual. En proyectos el máximo es Maintainer (salvo el creador del proyecto personal).

### Cuándo asignar cada rol — regla práctica

- **Guest**: clientes, stakeholders que necesitan ver el tablero de issues sin tocar código.
- **Reporter**: QA que reporta bugs, PM que monitorea avance, integraciones de lectura (Jira, bots).
- **Developer**: el rol por defecto para cualquier ingeniero activo del equipo.
- **Maintainer**: tech leads, responsables de releases, quien aprueba merges a `main`.
- **Owner**: administrador del grupo. Mínimo 1, máximo los necesarios (nunca todo el equipo).

### Herencia y override de roles

Los roles se heredan hacia abajo en la jerarquía:

```
Grupo: Juan = Developer
  └── Proyecto A: Juan hereda Developer
  └── Proyecto B: Juan tiene rol explícito Maintainer  ← override; gana el mayor
```

Un rol en un proyecto puede ser **mayor** que el heredado del grupo (se usa el mayor), pero **nunca menor** — no puedes rebajar a alguien en un proyecto si tiene rol superior en el grupo.

---

## 👁️ Niveles de visibilidad

Tanto grupos como proyectos tienen tres niveles de visibilidad independientes:

| Nivel | Quién puede ver | Cuándo usarlo |
|---|---|---|
| **Private** | Solo miembros invitados explícitamente | Código propietario, proyectos cliente, datos sensibles |
| **Internal** | Cualquier usuario autenticado en la instancia | Proyectos internos de empresa en GitLab autohospedado |
| **Public** | Todo el mundo, sin login | Open source, portfolios, documentación pública |

> **Internal** no existe en gitlab.com para proyectos nuevos desde 2022 (se deprecó para evitar filtrados). En instancias autohospedadas sigue siendo útil.

### Regla de herencia de visibilidad

Un proyecto **no puede ser más público que su grupo padre**. Si el grupo es Private, el proyecto solo puede ser Private. Esto evita fugas accidentales.

```
Grupo: Private
  ├── Proyecto: Private   ✓
  ├── Proyecto: Internal  ✗ (GitLab lo bloquea)
  └── Proyecto: Public    ✗ (GitLab lo bloquea)
```

---

## 🗂️ Cómo organizar tu trabajo: patrones recomendados

### Patrón 1 — Proyecto personal / hobby
```
tu-usuario/
├── proyecto embebido       ← directo en namespace personal
├── experimento-ml
└── scripts-personales
```
Sin grupos. Simple, rápido de crear.

### Patrón 2 — Proyecto propio con varios repos
```
grupo-mi-app/              ← grupo tuyo
├── backend
├── frontend
├── infra
└── docs
```
Las variables CI y los runners se configuran una vez en el grupo.

### Patrón 3 — Empresa / equipo profesional
```
empresa/
├── producto/
│   ├── api
│   ├── webapp
│   └── mobile
├── data/
│   ├── etl-pipeline
│   └── ml-models
└── infra/
    ├── terraform
    └── helm-charts
```
Cada subgrupo tiene su propio Maintainer. Los secretos de producción viven en el grupo raíz, los de staging en los subgrupos.

---

## ⚠️ Errores comunes

| Error | Por qué ocurre | Solución |
|---|---|---|
| "No tengo acceso al repo" | El usuario está en el grupo pero no en el proyecto con visibilidad private | Verificar membresía a nivel de proyecto o bajar la visibilidad |
| "No puedo hacer push a main" | `main` está protegido y el usuario es Developer | Pedir a Maintainer que haga el merge, o subir rol si corresponde |
| "Las variables de CI no llegan" | Las variables se definieron en el proyecto equivocado o en subgrupo incorrecto | Mover la variable al nivel correcto de la jerarquía |
| Fork sin actualizar la visibilidad | El fork hereda visibilidad pública del original aunque no quieras | Cambiar visibilidad del fork a Private manualmente |
| Demasiados Owners | "por si acaso" | Mínimo necesario; Owner puede borrar todo sin confirmación adicional |

---

## 🛠️ Aplícalo a tus proyectos

**Para proyecto embebido (PlatformIO / embebido):**
Si tienes o planeas tener más repos relacionados (firmware, scripts de análisis, documentación técnica), crea un grupo `embebido/` y mete ahí los proyectos. Así puedes compartir variables CI (tokens, URLs de servidor) en un solo lugar.

**Para app web (FastAPI + React):**
Ya tienes estructura `backend/`, `frontend/`, `infra/`. Si lo subes a GitLab, un grupo `app-producto/` con tres proyectos separados es más limpio que un monorepo y te permite tener pipelines independientes con variables heredadas.

**Regla de oro para proyectos personales:** empieza con namespace personal. Migra a grupo cuando tengas 2+ repos relacionados o necesites compartir secretos de CI.

---

## Conexiones

- [[MOC_GitLab]]
- [[01-que-es-gitlab]]
- [[03-repos-y-flujo-git]]
- [[04-merge-requests-y-code-review]]
- [[05-gitlab-cicd-fundamentos]]
- [[10-autoalojamiento]]
- [[11-administracion-backups-upgrades]]
- [[MOC_Desarrollo_Software]]
