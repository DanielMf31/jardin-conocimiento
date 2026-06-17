---
title: Kanban y Lean
date: 2026-06-13
tags: [programacion/agile, programacion/kanban, programacion/lean, programacion/flujo]
type: nota
status: en-progreso
source: claude-code
aliases: [kanban, lean-software, scrumban]
---

# Kanban y Lean

## Por qué existe esto (el problema que resuelven)

En los años 50, Toyota tenía un problema de producción: los equipos fabricaban piezas en grandes lotes aunque el siguiente paso de la cadena aún no las necesitara. El resultado: montones de inventario acumulado, defectos ocultos durante semanas, y sistemas que colapsaban bajo su propio peso.

Su solución fue el **Sistema de Producción Toyota (TPS)**, la raíz de todo lo que veremos aquí.

En software, el problema análogo es el **trabajo en curso desbordado** (*Work In Progress* o WIP): tareas empezadas pero no terminadas, que acumulan dependencias, contexto mental y riesgo. Cuantas más cosas simultáneas tiene un equipo "en progreso", más tarda cada una en salir y más errores se introducen.

Kanban y Lean atacan exactamente ese problema: **hacer fluir el trabajo en lugar de acumularlo.**

---

## Kanban — el tablero como sistema de señales

### Origen

**Kanban** (看板) significa literalmente "señal visual" en japonés. En Toyota era una tarjeta física que autorizaba producir o mover una pieza. Taiichi Ohno lo diseñó para que la producción fuera *pull* (tirada por la demanda) en lugar de *push* (empujada desde el inicio de la cadena).

David J. Anderson adaptó el concepto a desarrollo de software a mediados de los 2000.

### Anatomía de un tablero Kanban

```
┌───────────────┬───────────────┬───────────────┬───────────────┐
│   BACKLOG     │  EN PROGRESO  │   REVISIÓN    │    LISTO      │
│               │   (WIP ≤ 3)   │   (WIP ≤ 2)   │               │
├───────────────┼───────────────┼───────────────┼───────────────┤
│ [ Tarea A ]   │ [ Tarea C ]   │ [ Tarea E ]   │ [ Tarea F ]   │
│ [ Tarea B ]   │ [ Tarea D ]   │               │ [ Tarea G ]   │
│ [ Tarea H ]   │ [ Tarea I ]   │               │               │
└───────────────┴───────────────┴───────────────┴───────────────┘
```

| Elemento | Qué es | Para qué sirve |
|---|---|---|
| **Columna** | Etapa del flujo de trabajo | Mapear el proceso real, no el ideal |
| **Tarjeta** | Una unidad de trabajo | Visualizar qué existe y dónde está |
| **Límite WIP** | Máximo de tarjetas simultáneas en una columna | Forzar que se termine antes de empezar |
| **Política de columna** | Criterios de entrada/salida de cada columna | Hacer explícitas las reglas tácitas |

### Las columnas son las que TÚ definas

No existe una lista canónica. Un tablero mínimo puede ser `Pendiente → Haciendo → Hecho`. Un tablero maduro puede tener `Análisis → Desarrollo → Code Review → QA → Deploy → Producción`. La regla es: **cada columna debe representar un estado real en tu proceso**.

### El corazón del sistema: límites WIP

El **límite WIP** (*Work In Progress limit*) es el número máximo de tarjetas que pueden estar simultáneamente en una columna (o en todo el tablero).

Por qué funciona:

- Cuando una columna está llena, el desarrollador **no puede empezar algo nuevo**: debe primero ayudar a desbloquear lo que ya está en progreso.
- Esto crea presión natural para terminar, colaborar y detectar cuellos de botella.
- La Ley de Little (teoría de colas) lo formaliza: `Tiempo de ciclo = WIP / Rendimiento`. Menos WIP → menos tiempo de ciclo.

> **Error común:** poner límites WIP demasiado altos al principio "para no incomodar al equipo". Un límite de 10 en un equipo de 3 personas es básicamente no tener límite. Empieza conservador (número de personas ± 1) y ajusta.

### Flujo continuo

A diferencia de Scrum, Kanban **no tiene iteraciones fijas** (sprints). El trabajo entra al tablero cuando hay capacidad y sale cuando está listo. Esto lo hace ideal para flujos de trabajo continuos: soporte, mantenimiento, operaciones, pipelines de datos.

---

## Métricas de flujo

Kanban tiene sus propias métricas, distintas a las de Scrum (que mide velocidad en puntos).

| Métrica | Definición | Para qué sirve |
|---|---|---|
| **Tiempo de ciclo** (*Cycle Time*) | Tiempo desde que una tarjeta empieza hasta que se entrega | Predecir cuándo terminará algo nuevo |
| **Tiempo de entrega** (*Lead Time*) | Tiempo desde que se solicita algo hasta que se entrega | Lo que percibe el cliente |
| **Rendimiento** (*Throughput*) | Tarjetas completadas por unidad de tiempo | Medir capacidad real del equipo |
| **Diagrama de flujo acumulado** (CFD) | Líneas apiladas de tarjetas por columna a lo largo del tiempo | Detectar cuellos de botella visualmente |

> **Nota:** el Lead Time siempre es ≥ Cycle Time. La diferencia es el tiempo que la tarjeta estuvo esperando en el backlog antes de empezarse.

---

## Principios Lean aplicados a software

Lean es la filosofía subyacente a Kanban. Mary y Tom Poppendieck la formalizaron para software en 2003.

### Los 7 desperdicios (Muda) en software

"Desperdicio" (*muda* en japonés) es todo lo que consume recursos sin aportar valor al cliente:

| Desperdicio en manufactura | Equivalente en software |
|---|---|
| Inventario | Trabajo en curso sin terminar, features a medias |
| Sobreproducción | Código que nadie usa, documentación nadie lee |
| Transporte | Handoffs innecesarios entre equipos o personas |
| Esperas | Pull requests esperando revisión, deployments manuales |
| Movimiento | Reuniones innecesarias, buscar información dispersa |
| Sobreprocesado | Burocracia, aprobaciones excesivas |
| Defectos | Bugs, retrabajo, deuda técnica que se acumula |

### Los principios Lean centrales

1. **Eliminar desperdicio** — si una actividad no aporta valor directo al cliente, cuestiona su existencia.
2. **Amplificar el aprendizaje** — ciclos de feedback cortos; errores descubiertos pronto son baratos.
3. **Decidir lo más tarde posible** — no tomes decisiones irreversibles antes de tener información suficiente.
4. **Entregar lo más rápido posible** — velocidad de entrega = frecuencia de aprendizaje.
5. **Empoderar al equipo** — quien hace el trabajo conoce mejor el problema; evita microgestión.
6. **Construir con integridad** — calidad incorporada desde el inicio, no inspeccionada al final.
7. **Ver el sistema completo** — optimizar una parte puede empeorar el todo (cuello de botella aguas abajo).

### Flujo Pull vs. Push

- **Push:** alguien asigna trabajo al equipo según un plan. El equipo recibe independientemente de su capacidad.
- **Pull:** el equipo *tira* del siguiente ítem del backlog cuando tiene capacidad libre. El sistema no produce más de lo que puede procesar.

Kanban implementa pull mediante los límites WIP: si una columna está llena, no se puede "empujar" más trabajo desde la izquierda.

### Kaizen — mejora continua

**Kaizen** (改善) significa "cambio para bien". En práctica: retrospectivas frecuentes donde el equipo identifica un desperdicio específico, propone un experimento concreto, lo mide y ajusta. No transformaciones grandes — mejoras pequeñas y constantes.

---

## Scrumban — el híbrido

Scrumban (acuñado por Corey Ladas, 2008) combina estructura de Scrum con el flujo de Kanban. Es útil como **estado de transición** (equipos que vienen de Scrum y quieren más fluidez) o para equipos con mezcla de trabajo planificado y emergente.

| Elemento | Scrum puro | Scrumban típico | Kanban puro |
|---|---|---|---|
| Iteraciones | Sprints fijos | Opcionales / flexibles | No |
| Backlog priorizado | Sí | Sí | Sí (pero más fluido) |
| Planning periódico | Sí, cada sprint | "Cuando el backlog baje de N ítems" | Continuo o por demanda |
| Límites WIP | No | Sí | Sí (central) |
| Roles definidos | PO, SM, Dev | Flexibles | Ninguno obligatorio |
| Retrospectivas | Cada sprint | Periódicas | Al detectar problemas |

---

## Scrum vs. Kanban — cuándo usar cada uno

| Criterio | Scrum | Kanban |
|---|---|---|
| Tipo de trabajo | Desarrollo de features nuevas, proyectos definidos | Soporte, mantenimiento, operaciones, flujo continuo |
| Predictibilidad del alcance | Alta (puedes planificar sprints) | Baja o cambia frecuentemente |
| Tamaño del equipo | 3-9 personas dedicadas | Flexible; incluso equipos de 1 |
| Necesitas cadencia | Sí, ayuda a un equipo nuevo a organizarse | No es necesaria |
| Cultura del equipo | Necesita compromiso con los rituales | Más autónomo, menos ceremonial |
| Métricas principales | Velocidad (puntos/sprint), burndown | Cycle time, throughput, CFD |

**Usa Scrum cuando** el equipo es nuevo en metodologías ágiles, el trabajo es desarrollo de producto con features grandes, o necesitas cadencia para coordinar con stakeholders.

**Usa Kanban cuando** el trabajo es heterogéneo (bugs + soporte + mejoras pequeñas), los ítems tienen tamaños muy distintos, o la demanda es impredecible.

**No uses Kanban como excusa** para no planificar ni tener ningún proceso. Sin límites WIP explícitos, un tablero Kanban es solo decoración.

---

## Cómo montar un Kanban básico desde cero

### Paso 1 — Mapea tu proceso real (no el ideal)

Pregunta: ¿qué pasos sigue UNA tarea desde que existe hasta que está en producción? Escríbelos. Ese es tu conjunto inicial de columnas.

Ejemplo para un proyecto personal con CI/CD:
`Backlog → En desarrollo → En revisión → En QA → Desplegado`

### Paso 2 — Define los límites WIP

Empieza con: `número de personas que trabajan en esa etapa + 1`. Si eres solo, "En desarrollo" con WIP = 2 es razonable.

### Paso 3 — Define las políticas de cada columna

Para cada columna responde:
- ¿Qué tiene que ser verdad para que una tarjeta entre aquí?
- ¿Qué tiene que ser verdad para que salga?

Escríbelo en el tablero (literalmente, una nota pegada arriba de la columna). Esto elimina debates tácitos.

### Paso 4 — Operación diaria

- Mira el tablero antes de empezar.
- Si hay algo bloqueado, primero desbloquea. Luego tira nueva tarjeta.
- Si una columna está en el límite, no abras nueva tarjeta: pregunta dónde puedes ayudar.

### Paso 5 — Mide y ajusta (Kaizen)

Cada 2 semanas (o cuando el sistema se sienta incómodo): revisa el CFD o simplemente el promedio de cycle time. ¿Dónde se acumula el trabajo? ¿Qué causa bloqueos frecuentes? Cambia una cosa, observa el resultado.

### Herramientas

| Herramienta | Cuándo usarla |
|---|---|
| Tablero físico (post-its) | Equipo en misma oficina; bajo coste de arranque |
| Trello | Proyecto personal o equipo pequeño; simple |
| GitHub Projects | Si tu código ya está en GitHub; integración nativa |
| Linear | Equipos de producto/desarrollo; métricas avanzadas |
| Jira (modo Kanban) | Organizaciones grandes; configuración compleja |

---

## Aplícalo a tus proyectos

### app web (FastAPI + React + MongoDB)

Tu tablero actual podría tener:

```
Backlog → En desarrollo → Code Review (PR abierto) → QA local → Merged/Deploy
WIP:        ∞              2                            1            ∞
```

- Cuando tengas un PR abierto, resiste la tentación de abrir otro feature hasta que ese PR esté mergeado (límite WIP = 1 en Code Review).
- Métrica útil: cycle time desde "rama creada" hasta "mergeado". Si sube, investiga por qué.

### proyecto embebido (PlatformIO)

Para firmware embebido el flujo tiene etapas físicas:

```
Backlog → Diseño/HW → Implementación → Test unitario → Test integración → Validado
```

El desperdicio más común en proyectos de HW: features de firmware esperando que el PCB llegue. Identifícalo explícitamente en el tablero (columna "Bloqueado/HW") para que sea visible, no invisible.

### Proyectos personales de aprendizaje (DS, Go, etc.)

Para proyectos de aprendizaje: límite WIP = 1 en "En estudio activo". Termina un módulo antes de abrir otro. Es exactamente el mismo principio.

---

## Errores comunes

- **Tablero decorativo:** tarjetas que no se mueven, políticas que nadie respeta. Si el tablero no refleja la realidad, deja de tener valor.
- **Sin límites WIP:** un tablero sin límites es solo una lista de tareas con más pasos. El límite es el mecanismo central.
- **Columnas demasiado gruesas:** "En progreso" que engloba análisis + desarrollo + revisión oculta dónde se acumula el trabajo.
- **Ignorar bloqueos:** una tarjeta bloqueada debería tener un indicador visual (color, etiqueta). Si no es visible, se olvida.
- **Mezclar tipos de trabajo sin diferenciarlo:** bugs urgentes y features grandes en el mismo carril distorsionan las métricas. Usa "swimlanes" (filas) para separarlos.

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[01-sdlc-e-historia]]
- [[02-manifiesto-agil]]
- [[03-scrum]]
- [[05-historias-de-usuario-y-backlog]]
- [[09-metricas-y-seguimiento]]
- [[11-equipo-retros-y-antipatrones]]
