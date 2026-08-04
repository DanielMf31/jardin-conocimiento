---
title: Equipo, Retros y Anti-patrones
date: 2026-06-13
tags: [programacion/agile, programacion/scrum, programacion/equipos, programacion/proceso]
type: nota
status: en-progreso
source: claude-code
aliases: [retrospectivas, antipatrones agile, dark scrum]
---

# Equipo, Retros y Anti-patrones

## ¿Por qué existe esto?

El código no falla en el vacío: falla en un contexto de equipo, proceso y comunicación. Agile promete mejorar eso, pero sin cuidado se convierte en el problema mismo.

Este documento cubre dos caras de la misma moneda:

- **La retrospectiva** — el mecanismo principal para que un equipo se auto-mejore.
- **Los anti-patrones** — señales de que el proceso está sirviendo al proceso, no al equipo ni al producto.

Si ya tienes claro qué es Scrum y los marcos ágiles, este doc es el "¿y cómo funciona esto en la realidad imperfecta?". Complementa directamente a [[03-scrum]], [[04-kanban-y-lean]] y [[06-otros-marcos]].

---

## Panorama: el bucle de mejora continua

Todos los marcos ágiles comparten una idea central: **inspeccioná → adaptá**. La retrospectiva es el evento donde eso ocurre a nivel de equipo (no de producto).

```
Sprint/Iteración → Revisión (qué construimos) → Retrospectiva (cómo lo construimos) → siguiente Sprint
```

Sin retro, el equipo repite los mismos errores indefinidamente. Con retro mal facilitada, el equipo repite los mismos errores y además pierde 1 hora por sprint.

---

## La Retrospectiva

### Qué es y qué NO es

| Es | No es |
|---|---|
| Espacio seguro para hablar de proceso y dinámica de equipo | Sesión de quejas sin cierre |
| Genera 1-3 acciones concretas y asignadas | Genera una lista de deseos que nadie ejecuta |
| Facilitada (con estructura) | Una reunión más sin agenda |
| Foco en el equipo, no en la tecnología | Revisión técnica del código |

**Regla de oro**: si al final de la retro no hay *al menos una acción asignada a alguien con fecha*, fue una charla, no una retro.

---

### Formatos de retrospectiva

Cada formato sirve para un momento diferente del equipo. No hay uno "correcto".

#### 1. Start / Stop / Continue
El más simple. Bueno para equipos nuevos o cuando hay poco tiempo.

| Columna | Pregunta |
|---|---|
| **Start** | ¿Qué deberíamos empezar a hacer? |
| **Stop** | ¿Qué deberíamos dejar de hacer? |
| **Continue** | ¿Qué está funcionando y queremos mantener? |

**Cuándo usarlo**: sprint 1-3 de un equipo nuevo, o cuando el equipo está bloqueado y necesita claridad rápida.

#### 2. Mad / Sad / Glad
Apunta a las emociones, no solo a los procesos. Útil cuando hay tensión no expresada.

| Columna | Qué captura |
|---|---|
| **Mad** (enojado) | Qué frustró al equipo |
| **Sad** (triste) | Qué salió mal o se perdió |
| **Glad** (contento) | Qué salió bien o celebrar |

**Cuándo usarlo**: después de un sprint difícil, un lanzamiento fallido, o cuando notas que la gente está quemada.
**Riesgo**: se queda en catarsis si el facilitador no cierra con acciones.

#### 3. 4Ls (Liked / Learned / Lacked / Longed For)
Más estructurado cognitivamente. Bueno para equipos maduros que quieren profundidad.

| L | Pregunta |
|---|---|
| **Liked** | ¿Qué disfrutamos? |
| **Learned** | ¿Qué aprendimos? |
| **Lacked** | ¿Qué nos faltó? |
| **Longed For** | ¿Qué desearíamos haber tenido? |

**Cuándo usarlo**: retros de fin de proyecto, equipos con 3+ meses juntos, cuando quieres capturar aprendizajes transferibles.

#### 4. Sailboat (Barco de Vela)
Formato visual/metafórico. El equipo es un barco navegando hacia un objetivo (isla = meta del sprint o release).

| Elemento | Representa |
|---|---|
| **Viento** | Lo que nos empuja / acelera |
| **Ancla** | Lo que nos frena o bloquea |
| **Rocas** | Riesgos futuros que vemos |
| **Isla** | El objetivo que queremos alcanzar |

**Cuándo usarlo**: cuando el equipo está desconectado del "para qué", o cuando necesitas una conversación más estratégica. Funciona muy bien con equipos que vienen de hardware/ingeniería porque es visual y concreto.

---

### Cómo facilitar una retro que funcione

**Estructura de 5 fases** (de Esther Derby y Diana Larsen, libro clásico del tema):

1. **Set the stage** (5 min): rompe el hielo, recuerda las reglas (lo que se dice aquí queda aquí). La "primera voz" — que cada persona diga algo al inicio — activa la participación.
2. **Gather data** (10-15 min): todos escriben post-its / tarjetas con sus observaciones. En silencio primero, luego se comparten.
3. **Generate insights** (10-15 min): agrupar ítems similares, identificar patrones, preguntar "¿por qué aparece esto?".
4. **Decide what to do** (10 min): priorizar 1-3 acciones. Cada acción = qué, quién, cuándo.
5. **Close the retrospective** (5 min): una palabra o frase de cada persona sobre cómo se van.

**Regla de la retro anterior**: siempre empezar revisando qué pasó con las acciones del sprint pasado. Si nadie las ejecutó, ese es el problema a resolver hoy.

---

## Seguridad Psicológica

*Seguridad psicológica* (término de Amy Edmondson, investigadora de Harvard): la creencia de que puedes hablar, preguntar, cometer errores o disentir sin ser castigado social o profesionalmente.

Es el **predictor más fuerte** de si una retro funciona. Sin ella, la gente dice lo que es seguro decir, no lo que es verdad.

### Señales de que hay seguridad psicológica
- La gente señala sus propios errores sin que se lo pidan.
- Alguien junior contradice a alguien senior y no pasa nada.
- Los "no sé" y "me equivoqué" son frecuentes.
- Las retros tienen ítems reales, no solo elogios mutuos.

### Señales de que NO la hay
- Las retros siempre son positivas (todo está bien, siempre).
- Nadie critica decisiones del management.
- La gente habla en privado lo que no dice en la retro.
- Un mismo problema aparece sprint tras sprint sin que nadie lo nombre directo.

### Cómo construirla (y qué destruye)

| Construye | Destruye |
|---|---|
| Líder modela vulnerabilidad ("me equivoqué en esto") | Culpar a personas en público |
| Curiosidad genuina sobre errores ("¿qué pasó?") | Respuestas defensivas ante críticas |
| Separar persona de comportamiento | Jerarquía que no se puede cuestionar |
| Retro con facilitador neutro | Jefe que facilita su propia retro |
| Acuerdos de confidencialidad del equipo | Que lo dicho en retro llegue a RRHH |

---

## Anti-patrones famosos

Un *anti-patrón* es una "solución" reconocible que parece resolver un problema pero en realidad lo empeora o crea nuevos. En software, el término viene de la programación (análogo inverso a los patrones de diseño), pero aplica igual a procesos.

### 1. Dark Scrum

Acuñado por Ron Jeffries (uno de los firmantes del Manifiesto Ágil). Scrum aplicado de forma que **perjudica a los developers** en lugar de empoderarlos.

**Síntomas:**
- El Product Owner dicta estimaciones en lugar de aceptar las del equipo.
- Velocity (velocidad — número de puntos completados por sprint) se convierte en KPI de rendimiento individual.
- El Sprint Backlog cambia durante el sprint sin negociación.
- "¿Por qué no terminaste los puntos?" se vuelve la pregunta habitual del Daily.

**Por qué ocurre**: Scrum da poder al equipo *en teoría*, pero si la cultura organizacional es jerárquica, ese poder no existe. El framework se usa para dar apariencia ágil sin cambiar nada.

**Cómo detectarlo**: preguntá a los developers si se sienten dueños de su proceso. Si la respuesta es "en teoría sí, en práctica no", es Dark Scrum.

---

### 2. Cargo-Cult Agile

El término *cargo cult* viene de fenómenos antropológicos post-WWII: isleños del Pacífico construían pistas de aterrizaje falsas esperando que los aviones (con carga) volvieran, porque habían visto que eso precedía a los aviones reales.

Aplicado a Agile: **copiar las ceremonias y artefactos sin entender por qué existen**.

**Síntomas:**
- "Hacemos Daily standups de 45 minutos" (el standup existe para ser corto y de sincronización, no una reunión de status).
- "Usamos story points porque Scrum lo dice" (sin entender que son estimación relativa, no horas).
- Burndown charts que nadie mira.
- Retrospectivas que generan el mismo plan de acción sprint tras sprint.
- "Somos ágiles" en el onboarding, pero hay un proceso de aprobación de 3 semanas para deployar.

**Raíz del problema**: se certificó a personas en Scrum pero no se cambió la cultura ni la estructura de poder.

---

### 3. Water-Scrum-Fall

El anti-patrón más común en organizaciones grandes. La apariencia es ágil, la realidad es cascada (*waterfall* = desarrollo secuencial por fases: análisis → diseño → desarrollo → testing → deploy).

```
[Planificación anual en cascada]
        ↓
[Sprints Scrum en el medio]
        ↓
[Deploy y aprobaciones en cascada]
```

**Síntomas:**
- El roadmap anual está fijo y los sprints solo ejecutan lo que ya se decidió arriba.
- Los developers hacen sprints, pero QA y deploy tardan meses.
- "Somos ágiles en dev, pero ops tiene su propio proceso".

**Por qué importa**: el valor de Agile está en el bucle de feedback corto. Si el feedback tarda meses (porque el deploy tarda meses), los sprints son solo microgestión de tareas, no iteración real.

**Relación con DevOps**: Water-Scrum-Fall es exactamente el problema que [[08-devops-y-cicd]] intenta resolver.

---

### 4. Zombie Scrum

Término de Christiaan Verwijs y Johannes Schartau. El equipo hace *todas* las ceremonias de Scrum pero **sin energía, sin propósito, sin mejora**.

**Síntomas:**
- Las retros son siempre iguales: 3 cosas buenas, 1 mala, la misma acción de siempre.
- El equipo no sabe para quién construye ni si lo que hizo fue útil.
- No hay contacto real con usuarios o stakeholders.
- El Increment (lo que se terminó en el sprint) nunca se revisa con nadie de negocio.
- "Cumplimos el proceso" es el objetivo implícito.

**Diferencia con Dark Scrum**: en Dark Scrum hay presión externa que aplasta al equipo. En Zombie Scrum, el equipo está desconectado y apático, a veces por elección o por hábito.

**Remedio**: reconectar al equipo con el impacto real. ¿Quién usa esto? ¿Qué cambió en su vida? Traer usuarios a la Sprint Review.

---

### 5. Scrum Master que es Jefe Disfrazado

El Scrum Master *no es* un jefe de proyecto (*project manager*) ni un manager de personas. Es un **facilitador y coach de proceso**. Cuando alguien en ese rol tiene autoridad jerárquica real (o actúa como si la tuviera), el equipo pierde autonomía.

**Síntomas:**
- El Scrum Master asigna tareas del sprint a personas específicas.
- Participa en evaluaciones de desempeño del equipo.
- Toma decisiones técnicas.
- Los developers le consultan antes de hacer cosas porque "necesitan aprobación".
- El Daily standup se reporta *a* él, no *entre* el equipo.

**Distinción clave**:

| Scrum Master real | Scrum Master-jefe |
|---|---|
| Pregunta "¿qué os bloquea?" | Pregunta "¿por qué no avanzaste?" |
| Elimina impedimentos externos | Controla el trabajo interno |
| Protege al equipo de interrupciones | Es la fuente de interrupciones |
| Empuja hacia auto-organización | Centraliza decisiones |

---

## Críticas honestas a Agile/Scrum

Agile no es una religión. Hay críticas legítimas que vale la pena conocer para no ser fundamentalista.

### "Agile se convirtió en burocracia"

El Manifiesto Ágil (2001) tenía 12 principios y 4 valores. La industria de certificaciones creció alrededor de él y produjo frameworks de cientos de páginas (SAFe tiene más de 120 páginas de documentación). Irónicamente, esto contradice el valor original de "software funcionando sobre documentación exhaustiva".

**Síntoma concreto**: equipos que pasan más tiempo en ceremonias y actualizando Jira que construyendo.

### "Micromanagement con post-its"

Un Daily Scrum mal facilitado es una reunión de status diaria donde cada persona reporta su progreso. Eso es micromanagement, independientemente del color de los post-its.

La diferencia entre un standup ágil y micromanagement:
- **Ágil**: el equipo se sincroniza *entre sí* para coordinarse.
- **Micromanagement**: el equipo reporta *al manager* para que tenga visibilidad.

Si en tu standup hay alguien que no produce código pero sí hace preguntas de "¿cuándo estará listo X?", ese es el síntoma.

### "No escala bien"

Scrum fue diseñado para equipos de 3-9 personas. Frameworks de escalado (SAFe, LeSS, Nexus) existen precisamente porque escalar Scrum es difícil. Muchas organizaciones adoptan un framework de escalado cuando el problema real es otro (silos, falta de APIs internas, deuda técnica).

### "Agile favorece velocidad sobre calidad"

Cuando velocity (puntos por sprint) se convierte en métrica de éxito, el incentivo es cerrar tickets rápido. Eso puede degradar calidad, documentación, y pruebas. El valor original del Manifiesto dice "excelencia técnica y buen diseño" como principio. Muchas implementaciones lo ignoran.

**Contrapunto**: esto no es un defecto de Agile, es un defecto de cómo se mide. [[09-metricas-y-seguimiento]] cubre métricas más sanas.

### ¿Cuándo Scrum no es la respuesta?

| Situación | Por qué Scrum puede no servir |
|---|---|
| Trabajo de mantenimiento/soporte puro | Kanban es más adecuado (flujo continuo, no sprints) |
| Investigación o exploración sin deliverable claro | El Sprint Goal presiona a entregar algo que quizás no existe aún |
| Equipo de 1-2 personas | La ceremonia tiene overhead mayor que el beneficio |
| Proyecto con requerimientos completamente fijos (legales, normativos) | El cambio ágil no aplica si nada puede cambiar |
| Hardware/firmware con ciclos largos de validación | Los sprints de 2 semanas no casan con ciclos de test de meses |

---

## Aplícalo a tus proyectos

### app web (React + FastAPI + Docker)

- **Retro personal**: al final de cada "sprint" informal (aunque trabajes solo), dedicá 15 minutos a un Start/Stop/Continue. Las decisiones de arquitectura que tomaste ¿las repetirías? ¿Qué te bloqueó más?
- **Anti-patrón a vigilar**: en proyectos personales el riesgo es *Zombie Scrum* — seguir el proceso sin propósito. Si no tenés usuario real todavía, definí un hipotético y preguntate si lo que construiste le serviría.
- **Seguridad psicológica contigo mismo**: si cometés un error de arquitectura, documentalo en la bóveda en lugar de ignorarlo. Eso es la versión personal de "líder que modela vulnerabilidad".

### proyecto embebido (PlatformIO / Embedded)

- Hardware tiene ciclos de validación largos. El anti-patrón Water-Scrum-Fall aplica si hacés sprints de firmware pero el ciclo de test de hardware tarda semanas. Considerá Kanban en lugar de sprints para el firmware, o sprints más largos (3-4 semanas) alineados con los ciclos de PCB/validación.
- Las retros de proyectos de hardware pueden incluir una pregunta extra: "¿qué aprendimos del hardware que cambia nuestras suposiciones de software?".

### Bóveda y PKM

- La revisión semanal ya es estructuralmente una retro: Stop (qué descartar), Continue (qué mantener), Start (qué incorporar). Si la enlazás conscientemente con este framework, le sacás más valor.

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[02-manifiesto-agil]]
- [[03-scrum]]
- [[04-kanban-y-lean]]
- [[06-otros-marcos]]
- [[08-devops-y-cicd]]
- [[09-metricas-y-seguimiento]]
- [[10-producto-y-priorizacion]]
