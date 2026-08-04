---
title: Scrum
date: 2026-06-13
tags: [programacion/agile, programacion/scrum, programacion/gestion-proyectos]
type: nota
status: en-progreso
source: claude-code
aliases: [Scrum Framework, Scrum Guide]
---

# Scrum

## Por qué existe Scrum

El desarrollo de software tiene un problema estructural: **los requisitos cambian, el conocimiento se acumula durante el trabajo, y los entregables son intangibles**. Los enfoques tipo "diseña todo primero, construye después" (waterfall) asumen que puedes saber al principio lo que necesitas al final — algo que rara vez ocurre en software.

Scrum es la respuesta práctica: en lugar de planificar con precisión un proyecto largo e impredecible, divides el trabajo en ciclos cortos, inspeccionas lo construido, y ajustas. Es empírico por diseño.

> **Framework vs metodología**: Scrum es un *framework* (marco de trabajo), no una metodología. Una metodología te dice exactamente qué hacer paso a paso. Un framework te da la estructura mínima (roles, eventos, artefactos) y deja que el equipo decida cómo llenarlo. Esta distinción importa: si alguien en tu equipo dice "Scrum dice que hay que hacer X de forma Y", probablemente está confundiendo Scrum con una herramienta concreta.

La fuente canónica es la **Scrum Guide** (scrumguides.org), mantenida por Ken Schwaber y Jeff Sutherland, los creadores originales. Todo lo que contradiga la Guía oficial es una adaptación o malentendido.

---

## Los 3 Pilares empíricos

Scrum está construido sobre **empirismo**: el conocimiento viene de la experiencia, las decisiones se toman sobre lo observado. Hay tres pilares que lo sostienen:

| Pilar | Qué significa en la práctica |
|---|---|
| **Transparencia** | Quien hace el trabajo y quien evalúa los resultados deben ver la misma realidad. Sin información oculta, sin métricas de vanidad. |
| **Inspección** | Los artefactos y el progreso se revisan frecuentemente para detectar desviaciones. |
| **Adaptación** | Si algo se desvía, se ajusta cuanto antes. Un proceso que no cambia ante la evidencia no es ágil. |

Sin transparencia, la inspección es ciega. Sin inspección, la adaptación es aleatoria. Los tres pilares son interdependientes.

### Los 5 Valores de Scrum

Los pilares describen el *qué*; los valores describen el *cómo se comporta el equipo* para que los pilares funcionen:

- **Compromiso** — con los objetivos del equipo y del Sprint, no solo "lo intento"
- **Foco** — priorizar el trabajo del Sprint, reducir multitasking
- **Apertura** — ser honesto sobre obstáculos, progreso real, deuda técnica
- **Respeto** — confiar en que tus compañeros son capaces; no microgestionar
- **Coraje** — decir "no cabe en el Sprint", señalar problemas, cuestionar decisiones malas

---

## Los 3 Roles (Scrum Team)

El equipo Scrum es pequeño (típicamente ≤10 personas) y **autoorganizado**: decide internamente cómo hacer el trabajo, sin que un jefe externo asigne tareas. Tiene tres roles distintos.

### 1. Product Owner (PO)

**Problema que resuelve**: alguien tiene que decidir *qué* construir y en qué orden. Sin este rol, el equipo construye según criterio técnico o lo que llegó último, no lo que da más valor.

**Responsabilidades clave:**
- Es el único responsable del **Product Backlog** (la lista priorizada de todo lo que podría construirse)
- Representa los intereses del negocio/usuario — puede ser el cliente directamente o un representante designado
- Prioriza basándose en valor, riesgo, dependencias
- Acepta o rechaza el incremento al final del Sprint
- Define el **Product Goal** (ver Artefactos)

El PO es **una persona**, no un comité. Puede escuchar a muchos stakeholders (partes interesadas), pero las decisiones las toma él/ella.

### 2. Scrum Master (SM)

**Problema que resuelve**: Scrum no se implementa solo. Alguien tiene que asegurarse de que el equipo entiende el framework, eliminar impedimentos, y proteger al equipo de interferencias externas.

**Responsabilidades clave:**
- Servant-leader (líder al servicio del equipo, no jefe)
- Facilita los eventos de Scrum (no participa como desarrollador, facilita)
- Elimina impedimentos que el equipo no puede resolver solo
- Educa a la organización sobre Scrum
- Protege al equipo de cambios de scope durante el Sprint

El SM **no es un Project Manager** (no gestiona personas), **no es el jefe técnico** (no asigna tareas), y **no es el secretario** (no toma minutas de reuniones para que nadie las lea).

### 3. Developers

**Quiénes son**: todos los que hacen el trabajo de crear el incremento — programadores, testers, diseñadores UX, analistas de datos. El término "Developers" es más amplio que "programadores".

**Responsabilidades clave:**
- Crean el Sprint Backlog
- Estiman el trabajo durante el Sprint Planning
- Aseguran la calidad cumpliendo la Definition of Done
- Se autoorganizan para completar los ítems del Sprint

No hay jerarquía dentro de los Developers. No hay "tech lead" en Scrum (aunque el equipo puede tener especialistas de facto).

---

## Los 5 Eventos

Los eventos son contenedores de tiempo fijos (*timeboxed*) — tienen una duración máxima y no se alargan. Esto crea cadencia y obliga a tomar decisiones dentro del tiempo disponible.

### Sprint

**El contenedor de todo lo demás.** Un Sprint es un ciclo de trabajo de duración fija (1 a 4 semanas, habitualmente 2 semanas). Dentro de cada Sprint suceden los otros 4 eventos.

- Duración consistente: si decides hacer Sprints de 2 semanas, todos son de 2 semanas
- No se cancela salvo que el Product Goal quede obsoleto (muy raro)
- No se añaden ítems nuevos una vez comenzado (salvo que el PO y los Developers lleguen a un acuerdo, reduciendo otro ítem)
- Termina en una fecha fija, haya o no todo el trabajo acabado

### Sprint Planning

**Qué problema resuelve**: sin planificación, el equipo empieza a hacer cosas aleatorias. El Sprint Planning alinea al equipo sobre qué construir y cómo.

**Duración máxima**: 8 horas para un Sprint de 4 semanas (proporcional para Sprints más cortos).

**Tres preguntas que responde:**

| Pregunta | Quién lidera | Output |
|---|---|---|
| ¿Por qué es valioso este Sprint? | Product Owner | Sprint Goal |
| ¿Qué se puede hacer en este Sprint? | PO + Developers | Ítems seleccionados del Product Backlog |
| ¿Cómo se hará el trabajo? | Developers | Plan inicial en el Sprint Backlog |

El **Sprint Goal** (objetivo del Sprint) es la razón de ser del Sprint. No es "completa estos 7 tickets"; es algo como "el usuario puede registrarse y recuperar su contraseña". Si el equipo acaba antes, puede añadir más trabajo; si surgen problemas, puede renegociar el scope sin perder el objetivo.

### Daily Scrum

**Qué problema resuelve**: sin sincronización diaria, los problemas se detectan al final, cuando ya es tarde para reencauzar el Sprint.

**Formato**: 15 minutos máximo, mismo lugar y hora, solo Developers. El Scrum Master puede asistir pero no facilita activamente; el PO puede asistir si ayuda.

**No es una reunión de estado para el jefe.** Es para que los Developers sincronicen su trabajo y detecten impedimentos. Las tres preguntas clásicas ("¿qué hice ayer?", "¿qué haré hoy?", "¿hay impedimentos?") son una sugerencia de la Guía antigua, no obligatorias en la versión actual. Lo que importa: el equipo sale con un plan para las próximas 24 horas.

Si algo necesita más discusión, se hace después de la Daily con las personas implicadas, no con todo el equipo.

### Sprint Review

**Qué problema resuelve**: si nunca enseñas lo construido a los stakeholders, no recibes feedback real. La revisión cierra el loop entre equipo y negocio.

**Duración máxima**: 4 horas para Sprint de 4 semanas.

**Quién participa**: todo el Scrum Team + stakeholders invitados por el PO.

**Qué sucede:**
- Los Developers presentan el incremento (idealmente una demo funcional, no slides)
- El PO revisa el Product Backlog a la luz del feedback
- Se discute qué hacer a continuación (input para el próximo Sprint Planning)

La Sprint Review **no es una reunión de aceptación de tickets**. No es para que el PO diga "apruebo este ticket, rechazo aquel". Es una conversación sobre el producto y su futuro.

### Sprint Retrospective

**Qué problema resuelve**: sin reflexión sistemática, los equipos repiten los mismos errores Sprint tras Sprint. La Retro es el mecanismo de mejora continua del proceso.

**Duración máxima**: 3 horas para Sprint de 4 semanas.

**Solo Scrum Team** (sin stakeholders externos). El SM facilita.

**Qué se inspecciona:**
- Personas e interacciones
- Herramientas y prácticas
- Definition of Done

**Output esperado**: al menos un ítem de mejora concreto y accionable para el próximo Sprint. No una lista de 20 problemas sin dueño.

### Orden de los eventos en el Sprint

```
Sprint inicia
  └── Sprint Planning (día 1)
        Días 2-N:
          └── Daily Scrum (cada día)
  └── Sprint Review (último día o penúltimo)
  └── Sprint Retrospective (después de la Review, antes del cierre)
Sprint termina → siguiente Sprint inicia inmediatamente
```

---

## Los 3 Artefactos y sus Compromisos

Un artefacto en Scrum es información que hace el trabajo transparente. Cada artefacto tiene un **compromiso** asociado — la promesa que maximiza su valor y mantiene el empirismo.

### Product Backlog → compromiso: Product Goal

**Qué es**: lista ordenada y dinámica de todo lo que podría necesitar el producto. Es la única fuente de trabajo para el equipo Scrum.

- El PO es responsable de su contenido, disponibilidad y orden
- Los ítems más arriba (más prioritarios) son más detallados; los de abajo son vagos y grandes
- Se **refina** continuamente (*refinement* o *grooming*): desglosar ítems grandes, clarificar criterios de aceptación, re-estimar. No es un evento oficial de Scrum, pero es una actividad necesaria (≈10% del tiempo del equipo)

**Product Goal**: el objetivo a largo plazo del producto. Es el "hacia dónde vamos". Cada Sprint debe acercarnos a él. Solo puede haber un Product Goal a la vez; cuando se alcanza o abandona, se define el siguiente.

### Sprint Backlog → compromiso: Sprint Goal

**Qué es**: plan para el Sprint actual. Tiene tres partes:
1. El Sprint Goal (el por qué)
2. Los ítems del Product Backlog seleccionados (el qué)
3. El plan de acción para entregar el incremento (el cómo)

Pertenece a los Developers. Solo ellos lo modifican durante el Sprint. Se actualiza cada día basándose en el progreso real.

**Sprint Goal**: el objetivo concreto del Sprint. Da coherencia a los ítems seleccionados. Si el equipo tiene problemas con un ítem específico, puede renegociar el alcance con el PO manteniendo el Sprint Goal intacto.

### Increment → compromiso: Definition of Done (DoD)

**Qué es**: la suma de todos los ítems del Product Backlog completados durante el Sprint (más todos los incrementos anteriores). Debe ser *usable* — no "casi listo" ni "falta el deploy".

**Definition of Done**: descripción formal de lo que significa que un ítem está "hecho". Ejemplos típicos:
- Código revisado por al menos un compañero
- Tests unitarios escritos y pasando
- Documentación actualizada
- Desplegado en staging

Si un ítem no cumple la DoD, no forma parte del incremento. No se "acepta con deuda". La DoD crea el estándar de calidad mínimo del equipo y puede endurecerse con el tiempo (nunca relajarse).

---

## Flujo completo de un Sprint (2 semanas)

```
SEMANA 1
  Lunes AM   → Sprint Planning (2-4h)
               - PO presenta Sprint Goal candidato
               - Team selecciona ítems del Product Backlog
               - Developers planifican el trabajo
               → Output: Sprint Goal + Sprint Backlog

  Lunes-Viernes → Daily Scrum (15 min cada día)
               → Trabajo de desarrollo continuo

  Durante la semana → Refinement del Product Backlog
               (no es evento oficial, se acuerda cuándo hacerlo)

SEMANA 2
  Lunes-Jueves → Daily Scrum + desarrollo

  Jueves PM  → Sprint Review (1-2h)
               - Demo del incremento a stakeholders
               - Feedback → ajuste del Product Backlog

  Viernes AM  → Sprint Retrospective (1-1.5h)
               - Qué fue bien, qué mejorar
               - Al menos 1 acción concreta para el próximo Sprint

  Viernes    → Sprint termina. Lunes siguiente: nuevo Sprint Planning
```

---

## Errores comunes (y cómo evitarlos)

| Error | Por qué ocurre | Corrección |
|---|---|---|
| **Scrum de boquilla** | Adoptan los nombres pero no el espíritu. Hay "Sprints" pero el scope cambia cada día. | Revisar si realmente se respetan los pilares: transparencia, inspección, adaptación. |
| **SM como secretario/gestor** | Organizaciones que no entienden el rol lo tratan como coordinador administrativo. | El SM es un agente de cambio y coach, no un secretario. |
| **Daily como reunión de estado para el jefe** | El PO o manager asiste y el equipo le reporta a él, no entre ellos. | La Daily es del equipo. Si el manager quiere info, se la da el PO o se la busca en el tablero. |
| **Sprint Review como demo interna** | Solo asiste el equipo, sin stakeholders reales. | Invitar activamente a usuarios reales, clientes, o representantes de negocio. |
| **Retro sin acción concreta** | Se habla de problemas pero no se asigna a nadie ni tiene fecha. | Cada retro termina con ≥1 ítem en el Sprint Backlog del siguiente Sprint. |
| **DoD vacía o ignorada** | El equipo acepta ítems "casi listos". La deuda técnica se acumula. | La DoD es el contrato de calidad. Si no se cumple, el ítem no va al incremento. |
| **Product Backlog enorme e inamovible** | Se creó al inicio y nunca se revisó. Los ítems de abajo llevan meses sin tocarse. | Refinar regularmente. Los ítems que llevan >3 sprints sin subir se borran o archivan. |
| **Sprints de duración variable** | Alargan el Sprint porque "casi estamos". | La duración es fija. Lo que no se termina vuelve al Product Backlog. |
| **Multitasking durante el Sprint** | Developers trabajando en 3-4 cosas a la vez. | WIP limit implícito: termina antes de empezar. El tablero Kanban dentro del Sprint ayuda. |

---

## Cuándo usar Scrum / cuándo NO

**Scrum funciona bien cuando:**
- El trabajo es complejo y los requisitos van a evolucionar
- Necesitas feedback frecuente de usuarios o clientes
- El equipo puede estar co-ubicado o comunicarse fluidamente
- El producto tiene un ciclo de vida largo y evolución continua

**Scrum NO es la mejor opción cuando:**
- El trabajo es predecible y bien definido (instalación de infraestructura estándar, mantenimiento repetitivo)
- El equipo es una sola persona con flujo de trabajo continuo → Kanban es más simple
- El "producto" es un proyecto con entregable único bien definido y sin iteración → gestión de proyectos clásica puede ser suficiente
- La organización no tiene capacidad o voluntad de dar feedback entre Sprints → sin inspección, Scrum pierde su razón de ser

---

## Aplícalo a tus proyectos

**app web (React + FastAPI + MongoDB):**
- El Product Backlog ya existe implícitamente como lista de features. Formalizarlo con criterios de aceptación por ítem.
- Define un Sprint Goal por iteración que sea funcionalidad de usuario ("el usuario puede registrar una comida y ver sus macros del día"), no lista de tickets técnicos.
- La Definition of Done mínima: endpoint testeado, frontend conectado, funcionando en Docker local.
- Daily Scrum informal: aunque trabajes solo, una revisión de 5 minutos cada mañana ("¿qué hice ayer? ¿qué hago hoy? ¿hay algo bloqueante?") mantiene el foco.
- Sprint Review contigo mismo + alguien externo que use la app (un familiar, amigo) cada 2 semanas.

**proyecto embebido (PlatformIO/embedded):**
- El firmware embebido tiene ciclos de feedback más lentos (hardware en mano), pero los Sprints siguen teniendo sentido: un Sprint = una funcionalidad del sensor funcionando end-to-end.
- La DoD en embedded debe incluir: prueba en hardware real, no solo en simulador.

**Proyectos de aprendizaje (Ciencia de Datos, etc.):**
- Scrum es probablemente excesivo para estudio individual. Considera Kanban para flujo continuo de temas, o simplemente un Product Backlog de "cosas a aprender" priorizado.

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[01-sdlc-e-historia]]
- [[02-manifiesto-agil]]
- [[04-kanban-y-lean]]
- [[05-historias-de-usuario-y-backlog]]
- [[09-metricas-y-seguimiento]]
- [[11-equipo-retros-y-antipatrones]]
