---
title: Issues, tableros y gestión ágil en GitLab
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/agile, programacion/kanban, programacion/scrum]
type: nota
status: en-progreso
source: claude-code
aliases: [GitLab Issues, GitLab Kanban, GitLab Agile]
---

# Issues, tableros y gestión ágil en GitLab

## ¿Por qué existe esto aquí?

El trabajo de software tiene dos mitades: **el código** y **la conversación sobre el código** (qué construir, quién lo hace, cuándo, con qué prioridad). GitLab unifica ambas dentro del mismo sistema: el issue vive junto al commit que lo resuelve, el merge request que lo cierra y el pipeline que lo despliega.

Esto no es cosmético. Cuando un issue cierra automáticamente un MR y ese MR dispara un pipeline, tienes **trazabilidad completa** sin saltar entre Jira, GitHub, Jenkins y Slack. Esa integración es la propuesta de valor central de GitLab frente a herramientas aisladas.

> **Posición en el mapa**: este documento cubre la capa de *gestión de trabajo* de GitLab. Para la capa de ejecución (CI/CD, pipelines, runners) ver [[05-gitlab-cicd-fundamentos]] y [[06-runners]].

---

## Issues — la unidad básica de trabajo

### ¿Qué es un issue?

Un **issue** es cualquier unidad de trabajo que necesita rastrearse: una feature, un bug, una tarea técnica, una pregunta, una deuda técnica. Es intencionalmente genérico para que el equipo decida qué pone ahí.

Campos principales de un issue:

| Campo | Para qué sirve |
|---|---|
| **Title** | Descripción corta, accionable. Ej: "Añadir endpoint `/api/nutrition/daily`" |
| **Description** | Contexto, criterios de aceptación, mockups. Soporta Markdown completo |
| **Assignees** | Quién lo trabaja. Puede haber varios (diferente a GitHub clásico) |
| **Labels** | Clasificación libre: tipo, prioridad, área, estado... (ver sección Labels) |
| **Milestone** | Agrupa issues bajo un objetivo con fecha límite |
| **Due date** | Fecha de vencimiento individual del issue |
| **Weight** | Número arbitrario de esfuerzo (como story points en Scrum) |
| **Confidential** | Solo visible para miembros del proyecto con rol >= Reporter |
| **Epic** | (Ultimate) Agrupa issues de múltiples proyectos bajo un objetivo mayor |

### Buenas prácticas al escribir issues

- **Título = acción**: "Implementar X" o "Corregir Y", no "Problema con Z".
- **Description = criterios de aceptación**: ¿Cómo sé que este issue está terminado? Usa una checklist `- [ ]`.
- **Un issue = un ámbito de trabajo**: si el issue necesita >3 días de trabajo continuo de una persona, probablemente deba dividirse.

```markdown
<!-- Plantilla típica de description -->
## Contexto
¿Por qué necesitamos esto?

## Criterios de aceptación
- [ ] El endpoint responde 200 con payload correcto
- [ ] Tests de integración pasan
- [ ] Documentación de API actualizada

## Notas técnicas
...
```

---

## Labels — el sistema de clasificación

### Por qué importan

Las labels son la forma de **filtrar, priorizar y visualizar** el trabajo en GitLab. Sin labels, el tablero es un montón de issues sin estructura. Con labels bien diseñadas, puedes responder en segundos: "¿qué bugs críticos no tienen asignado?".

### Tipos de labels

**Labels de grupo** (heredadas por todos los proyectos del grupo) vs **labels de proyecto** (solo aplican a ese proyecto). Usa labels de grupo para vocabulario compartido del equipo.

Patrones comunes (elige los que encajen, no los copies todos):

| Prefijo | Ejemplos | Para qué |
|---|---|---|
| `type::` | `type::bug`, `type::feature`, `type::debt` | Qué tipo de trabajo es |
| `priority::` | `priority::critical`, `priority::low` | Urgencia |
| `status::` | `status::doing`, `status::blocked`, `status::review` | Flujo del tablero |
| `area::` | `area::backend`, `area::frontend`, `area::infra` | Qué parte del sistema |
| `size::` | `size::S`, `size::M`, `size::XL` | Estimación rápida |

> **Regla de oro**: los prefijos con `::` activan el comportamiento de **label "scoped"** en GitLab. Si pones `priority::high` y luego `priority::low` al mismo issue, GitLab automáticamente elimina la anterior. Evita tener dos labels del mismo scope en un issue — GitLab lo gestiona solo.

### Colores

Usa colores con semántica consistente: rojo = urgente/bloqueado, amarillo = en revisión, verde = listo, gris = deuda/técnico. El equipo lo aprende en una semana y lee tableros visualmente.

---

## Milestones — sprints e hitos

Un **milestone** (hito) es un contenedor temporal: tiene nombre, descripción, fecha de inicio y fecha de fin, y agrupa issues y merge requests.

**Usos comunes:**

- **Sprint de Scrum**: un milestone por sprint (ej. "Sprint 2026-06-16 / 06-30"). Ver [[03-scrum]].
- **Release**: milestone = versión del producto ("v1.2.0").
- **Fase de proyecto**: milestone = entregable ("Fase 1 — MVP").

Lo que el milestone te da en la UI:
- Barra de progreso (issues cerrados / total).
- Lista de todos los issues y MRs agrupados.
- Fecha límite visible en todas partes.

```
Grupo > Proyecto > Issues > Milestones > New milestone
- Title: Sprint 12
- Start date: 2026-06-16
- Due date: 2026-06-30
```

> **Cuando NO usar milestones**: si tu equipo trabaja en flujo continuo (Kanban puro sin sprints), los milestones añaden overhead innecesario. En ese caso, las labels de `status::` y el tablero hacen el trabajo. Ver [[04-kanban-y-lean]].

---

## Issue Boards — Kanban en GitLab

### El problema que resuelven

Una lista de 80 issues es inmanejable. Un tablero convierte esa lista en columnas visuales que muestran **el estado del flujo** de trabajo de un vistazo.

### Cómo funciona

Un **Issue Board** es una vista Kanban de los issues de un proyecto o grupo. Cada columna del tablero corresponde a **una label** (o a los estados especiales "Open" y "Closed").

Cuando mueves un issue de columna, GitLab añade/quita la label correspondiente automáticamente. El issue no cambia de sitio en la base de datos — solo cambia su label. Esto es importante: el tablero es una **vista**, no una estructura separada.

```
Columnas típicas de un tablero:
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│  Backlog │  To Do   │  Doing   │  Review  │   Done   │
│ (Open)   │status::todo│status::doing│status::review│(Closed)│
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

### Tableros múltiples

Un proyecto puede tener varios tableros. Casos de uso:

| Tablero | Configuración | Audiencia |
|---|---|---|
| "Sprint actual" | Filtrado por milestone activo | Equipo de desarrollo |
| "Por área" | Columnas = area::backend, area::frontend | Tech leads |
| "Bugs críticos" | Filtrado por type::bug + priority::critical | QA / producto |
| "Vista global" | Sin filtros, todas las labels de status | Manager |

### Configurar un tablero

```
Proyecto > Plan > Boards > New board
  - Nombre: "Sprint 12"
  - Scope: filtrar por milestone "Sprint 12" (opcional)
  - Columnas: + Add list > selecciona label
```

Cada lista/columna puede tener un **WIP limit** (Work In Progress limit) — máximo de issues simultáneos. Si superas el límite, la columna se colorea en rojo. Mecanismo fundamental del Kanban real. Ver [[04-kanban-y-lean]].

### Tableros de grupo

Si tienes múltiples proyectos bajo un grupo (ej. `backend`, `frontend`, `infra`), el **Group Board** muestra issues de todos ellos en un tablero unificado. Requiere que las labels sean de grupo (no de proyecto).

---

## Time Tracking — registro de tiempo

GitLab incluye time tracking básico sin plugins externos.

```bash
# En un comentario de issue o MR:
/estimate 3h       # Estimación del issue
/spend 1h 30m      # Tiempo real invertido hoy
/spend -30m        # Restar tiempo (corrección)
/remove_time_estimate  # Borrar estimación
```

El issue muestra:
- **Time estimate**: lo que se estimó
- **Time spent**: suma acumulada de todos los `/spend`

> Útil para proyectos con clientes que piden reportes de horas, o equipos que quieren calibrar sus estimaciones. No es un sustituto de herramientas de time tracking dedicadas, pero evita salir de GitLab para lo básico.

---

## Quick Actions — comandos de texto

Los **quick actions** son comandos que escribes en un comentario (o en la description al crear/editar). GitLab los ejecuta y los borra del texto visible. No son slash commands de chat — son acciones reales sobre el issue.

### Referencia de quick actions más usados

```bash
# Asignación
/assign @usuario          # Asignar a alguien
/assign me                # Asignarte a ti mismo
/unassign @usuario        # Quitar asignación

# Labels
/label ~"type::bug" ~"priority::high"   # Añadir labels
/unlabel ~"status::doing"               # Quitar label
/relabel ~"status::review"              # Reemplazar todas las labels

# Milestone y due date
/milestone %"Sprint 12"   # Asignar milestone
/due 2026-06-30           # Fecha de vencimiento
/remove_due_date

# Estado
/close                    # Cerrar issue
/reopen                   # Reabrir
/confidential             # Marcar como confidencial

# Peso y tiempo
/weight 5                 # Story points
/estimate 4h
/spend 2h

# Relacionar con otros issues
/relate #123              # Marcar como relacionado
/blocks #456              # Este issue bloquea al 456
/blocked_by #789          # Este issue está bloqueado por el 789
/duplicate of #234        # Marcar como duplicado y cerrar

# Crear MR desde el issue
/create_merge_request     # Crea MR con rama vinculada automáticamente
```

> **Truco**: puedes poner varios quick actions en el mismo comentario, uno por línea. Se ejecutan todos al guardar el comentario.

---

## Epics y Roadmaps (GitLab Ultimate)

> Esta sección aplica a GitLab.com plan Ultimate o instancias self-hosted con licencia Ultimate. En Free/Premium, los epics no existen.

### Epics — issues de issues

Un **epic** es un contenedor de nivel superior que agrupa issues (y otros epics anidados) que pertenecen a un objetivo de negocio grande. Vive a nivel de **grupo**, no de proyecto, lo que permite agrupar trabajo distribuido en múltiples repos.

```
Grupo
└── Epic: "Sistema de producto — MVP"
    ├── Issue (proyecto backend): Endpoint /api/daily
    ├── Issue (proyecto frontend): Pantalla de registro diario
    ├── Epic anidado: "Módulo de reportes"
    │   ├── Issue: Generador PDF
    │   └── Issue: Gráficas de evolución
    └── ...
```

Los epics tienen:
- Fecha de inicio y fin.
- Barra de progreso (% de issues cerrados).
- Jerarquía anidada (epics dentro de epics).
- Relaciones: "este epic bloquea a X".

### Roadmap

El **Roadmap** es la visualización Gantt/timeline de los epics de un grupo. Muestra en el tiempo qué epics están activos, cuándo empiezan, cuándo terminan, y cómo se solapan.

```
Grupo > Plan > Roadmap
  - Filtrar por label, autor, milestone
  - Vista: trimestral / mensual / semanal
  - Zoom in/out
```

Útil para comunicar a stakeholders "qué se está construyendo y cuándo" sin entrar en la granularidad de issues individuales.

---

## GitLab como herramienta ágil completa

### ¿Cómo encajan las piezas?

```
Gestión estratégica:   Epics + Roadmap (Ultimate)
        ↓
Gestión táctica:       Milestones (= sprints o releases)
        ↓
Unidad de trabajo:     Issues (con labels, assignees, weight)
        ↓
Ejecución:             Merge Requests (vinculados a issues)
        ↓
Automatización:        Pipelines CI/CD (disparados por MRs)
        ↓
Entrega:               Deploys, Registry, Pages
```

### GitLab + Scrum

| Elemento Scrum | Equivalente GitLab |
|---|---|
| Product Backlog | Lista de issues del proyecto, ordenados |
| Sprint | Milestone con fecha de inicio y fin |
| Sprint Backlog | Tablero filtrado por milestone activo |
| Story Points | Weight del issue |
| Definition of Done | Criterios de aceptación en la description |
| Sprint Review | Milestone cerrado, issues cerrados |
| Retrospectiva | Issue específico o wiki del proyecto |

Ver [[03-scrum]] para el modelo completo.

### GitLab + Kanban

| Elemento Kanban | Equivalente GitLab |
|---|---|
| Columnas del tablero | Labels de status:: en un Issue Board |
| WIP limits | WIP limit por columna en el tablero |
| Flujo continuo | Sin milestones, issues entran al tablero cuando están listos |
| Lead time / Cycle time | Time tracking (aproximado) |

Ver [[04-kanban-y-lean]] para el modelo completo.

### ¿Cuándo GitLab es suficiente y cuándo no?

| Necesidad | GitLab | Alternativa |
|---|---|---|
| Gestión básica de tareas con CI/CD | Muy bueno | — |
| Sprints simples de equipo pequeño | Bien | — |
| Roadmaps multiproyecto | Solo Ultimate | Jira, Linear |
| Reportes de burndown/velocity | Básico (Ultimate) | Jira, Shortcut |
| Time tracking detallado | Básico | Toggl, Harvest |
| Gestión de OKRs | Limitado | Notion, Lattice |
| Equipo >50 personas con procesos complejos | Puede tensionarse | Jira + GitLab vía integración |

---

## Vincular issues a código

### Cierre automático desde commits y MRs

Cuando un commit o MR menciona un issue con ciertas palabras clave, GitLab lo cierra automáticamente al mergear:

```bash
# En el mensaje de commit o en la description del MR:
Closes #42
Fixes #42
Resolves #42

# También:
Closes grupo/proyecto#42   # Issue de otro proyecto
Closes https://gitlab.com/grupo/proyecto/-/issues/42
```

Esto crea la trazabilidad completa: el issue queda vinculado al MR, y el MR al commit.

### Menciones sin cerrar

```bash
# Referencia cruzada (sin cerrar):
Related to #15
See also grupo/otro-proyecto#7
```

---

## Errores comunes

1. **Labels sin sistema**: crear labels ad hoc sin prefijos ni convención. El tablero se vuelve ilegible en semanas. Diseña el vocabulario antes de usarlo.

2. **Un issue = una tarea enorme**: issues que duran 3 semanas son señal de que deberían dividirse. Los issues grandes son difíciles de rastrear, difíciles de estimar y difíciles de revisar en MR.

3. **Milestones sin issues cerrados**: si al final del sprint el 70% está abierto, el problema no es GitLab — es el proceso de estimación o el alcance del sprint. GitLab muestra el síntoma, no lo crea.

4. **Tablero sin WIP limits**: sin límites, el tablero se convierte en otra lista. El WIP limit es lo que hace que el Kanban funcione como sistema de flujo.

5. **Cerrar issues manualmente en lugar de via MR**: pierde trazabilidad. Siempre que puedas, ciérralos desde el MR con `Closes #N`.

6. **No usar quick actions**: editar campos uno a uno desde la UI es lento. Un comentario con 5 quick actions actualiza todo en un segundo.

---

## Aplícalo a tus proyectos

### app web (backend FastAPI + frontend React)

```
Estructura sugerida:

Grupo: app web
├── Proyecto: backend
├── Proyecto: frontend
└── Proyecto: infra (docker-compose, scripts)

Labels de grupo (compartidas):
  type::feature, type::bug, type::debt, type::docs
  priority::critical, priority::high, priority::low
  status::todo, status::doing, status::review, status::blocked
  area::backend, area::frontend, area::infra, area::ci

Milestone actual: "MVP — Registro diario"
  Due date: [tu fecha objetivo]
  Issues incluidos:
    - [ ] Modelo de datos nutrientes (#1)
    - [ ] Endpoint POST /api/nutrition/daily (#2)
    - [ ] Pantalla de registro diario (#3)
    - [ ] Autenticación básica (#4)

Tablero "Desarrollo activo":
  Columnas: Backlog | To Do | Doing | Review | Done
  Scope: milestone activo
```

### proyecto embebido (PlatformIO / firmware)

En proyectos de hardware/firmware la gestión de issues es igual de útil:

```
Labels sugeridas para firmware:
  type::feature, type::bug, type::test, type::hw-dependency
  status::todo, status::doing, status::blocked-hw, status::validated
  area::sensores, area::comunicacion, area::control, area::config

Un issue típico:
  Title: "Implementar lectura sensor humedad SHT31 via I2C"
  Labels: type::feature, area::sensores
  Checklist:
    - [ ] Driver I2C inicializado
    - [ ] Lectura temperatura OK
    - [ ] Lectura humedad OK
    - [ ] Test en hardware real
    - [ ] Documentar calibración
```

---

## Conexiones

- [[MOC_GitLab]]
- [[MOC_Desarrollo_Software]]
- [[01-que-es-gitlab]]
- [[02-conceptos-grupos-proyectos-permisos]]
- [[04-merge-requests-y-code-review]]
- [[05-gitlab-cicd-fundamentos]]
- [[10-autoalojamiento]]
- [[03-scrum]]
- [[04-kanban-y-lean]]
