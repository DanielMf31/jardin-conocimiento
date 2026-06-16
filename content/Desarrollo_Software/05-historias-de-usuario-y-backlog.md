---
title: Historias de usuario y backlog
date: 2026-06-13
tags: [programacion/agile, programacion/scrum, programacion/gestion-producto, programacion/estimacion]
type: nota
status: en-progreso
source: claude-code
aliases: [user stories, product backlog, historias usuario]
---

# 📋 Historias de usuario y backlog

## Por qué existe esto — el problema que resuelve

En proyectos de hardware/técnico tienes un plano: el cliente ve el dibujo técnico y sabe exactamente qué se va a fabricar. En software, el "plano" es ambiguo por naturaleza — el producto cambia mientras se construye y los requisitos se descubren iterando.

La solución clásica era escribir un documento de requisitos exhaustivo antes de tocar código (modelo Waterfall, ver [[01-sdlc-e-historia]]). El problema: cuando terminas de documentar todo, ya cambiaron la mitad de los requisitos.

Las **historias de usuario** son la respuesta ágil: unidades mínimas de valor entregable, escritas en lenguaje de negocio (no técnico), que guían la conversación entre quien construye y quien necesita el producto. El **backlog** es la lista viva y priorizada de esas historias.

> Analogía técnico: si el plano CAD es el "qué hay que fabricar", la historia de usuario es la ficha de un cliente que dice "necesito que esto levante 50 kg a 2 m/s". El cómo lo decides tú como ingeniero.

---

## 🧱 Estructura de una historia de usuario

### El formato canónico

```
Como <rol/persona>
quiero <objetivo/funcionalidad>
para <beneficio/valor de negocio>
```

**Ejemplo malo** (sin las tres partes):
> "El sistema debe mostrar un dashboard del producto."

**Ejemplo bien formado**:
> Como **usuario registrado**
> quiero **ver un resumen diario de mis macronutrientes**
> para **saber si estoy cumpliendo mis objetivos calóricos sin tener que sumar manualmente**.

El "para" es la parte más importante y la más omitida. Sin él, el equipo no sabe cuándo la funcionalidad es "suficientemente buena" — y tiende a sobre-construir.

### El rol importa

El rol no es siempre "el usuario". Puede ser:
- `Como administrador del sistema` — funcionalidades de gestión
- `Como sistema externo (webhook de Stripe)` — integraciones
- `Como usuario no autenticado` — casos de acceso anónimo

En proyectos con varios tipos de usuario, definir **personas** (perfiles ficticios con nombre, contexto y frustraciones) ayuda a escribir mejores historias.

---

## ✅ Criterios INVEST — cómo saber si tu historia es buena

INVEST es un acrónimo que funciona como checklist de calidad para cada historia:

| Letra | Criterio | Qué significa en la práctica |
|-------|----------|-------------------------------|
| **I** | Independent (independiente) | Se puede desarrollar y entregar sin depender de otra historia. Si no puedes ordenarlas libremente, hay acoplamiento. |
| **N** | Negotiable (negociable) | No es un contrato fijo. Los detalles se negocian entre el equipo y el Product Owner hasta el momento de desarrollarla. |
| **V** | Valuable (valiosa) | Entrega valor al usuario o al negocio por sí sola. Evitar historias puramente técnicas ("crear la tabla en BD") — eso va como tarea interna. |
| **E** | Estimable (estimable) | El equipo puede dar una estimación de esfuerzo. Si no puede, la historia es demasiado vaga o demasiado grande. |
| **S** | Small (pequeña) | Cabe en un sprint (1-2 semanas). Si no cabe, hay que dividirla. |
| **T** | Testable (testeable) | Existe una forma concreta de verificar que está hecha. Si no puedes definir "done", no puedes desarrollarla. |

**Error frecuente**: escribir historias que violan "Independent" porque el equipo piensa en capas técnicas (primero backend, luego frontend). Cada historia debería ser una rebanada vertical — atravesar todas las capas para entregar algo que el usuario puede usar.

---

## 🔬 Criterios de aceptación — Given / When / Then

Los criterios de aceptación son las condiciones concretas que deben cumplirse para dar la historia por terminada. Sin ellos, "listo" es subjetivo.

El formato **Given / When / Then** (también llamado Gherkin, el lenguaje de la herramienta Cucumber) estructura cada criterio como un escenario:

```gherkin
Given <contexto inicial / estado del sistema>
When  <acción que realiza el usuario o el sistema>
Then  <resultado esperado observable>
```

**Ejemplo** para la historia del dashboard del producto:

```gherkin
Escenario 1: Usuario con registros del día
Given que el usuario ha registrado al menos una comida hoy
When accede a la sección "Hoy"
Then ve el total de calorías, proteínas, carbohidratos y grasas consumidas
  And los valores se muestran como barra de progreso respecto a su objetivo

Escenario 2: Usuario sin registros
Given que el usuario no ha registrado ninguna comida hoy
When accede a la sección "Hoy"
Then ve un estado vacío con el mensaje "Aún no has registrado comidas hoy"
  And ve un botón "Añadir comida"

Escenario 3: Datos del día anterior (edge case)
Given que son las 00:05 del día siguiente
When el usuario abre la app
Then el dashboard muestra 0 registros para el nuevo día
  And los registros del día anterior siguen accesibles en el historial
```

Los criterios de aceptación los escribe el **Product Owner** con input del equipo, y se acuerdan antes de empezar el desarrollo — no al final.

---

## 🗂️ Jerarquía: temas, épicas e historias

Las historias individuales se agrupan en estructuras más grandes para mantener visión de conjunto:

```
Tema
└── Épica
    └── Historia de usuario
        └── Tarea técnica (solo visible para el equipo)
```

| Nivel | Definición | Horizonte temporal | Ejemplo (app web) |
|-------|------------|--------------------|-------------------------|
| **Tema** | Gran área estratégica del producto | Meses / roadmap | "Seguimiento del producto" |
| **Épica** | Funcionalidad grande que requiere varios sprints | 2-6 semanas | "Registro de alimentos" |
| **Historia** | Unidad entregable en un sprint | 1-5 días | "Como usuario, quiero buscar alimentos por nombre para añadirlos rápido" |
| **Tarea** | Trabajo técnico interno (no visible al usuario) | Horas | "Crear endpoint GET /foods/search con paginación" |

Las **épicas** no se desarrollan directamente — se descomponen en historias cuando se acercan al tope del backlog. Mantenerlas como épicas mientras están lejos evita invertir tiempo en detalles que van a cambiar.

---

## 📦 El Product Backlog

El **Product Backlog** (backlog de producto) es la lista ordenada y priorizada de todo lo que podría hacerse en el producto. Es la única fuente de verdad sobre el trabajo pendiente.

Propiedades clave:
- **Vivo**: se actualiza continuamente, nunca está "completo"
- **Priorizado**: el ítem más valioso/urgente siempre está arriba
- **Estimado (aproximadamente)**: los ítems de arriba tienen más detalle y estimación precisa; los de abajo son burdos
- **Propiedad del Product Owner**: él decide el orden; el equipo decide cómo hacerlo

### Anatomía del backlog por zonas

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ARRIBA  │ Historias listas para el sprint
  (Ready) │ Detalladas, estimadas, pequeñas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MEDIO   │ Épicas en proceso de descomposición
          │ Estimación aproximada
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ABAJO   │ Ideas, épicas futuras, "algún día"
  (Ice Box)│ Sin estimar, pueden desaparecer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Refinamiento del backlog (Backlog Grooming)

El **refinamiento** (antes llamado "grooming") es la ceremonia periódica donde el equipo trabaja el backlog para mantenerlo saludable. No es una reunión puntual — es un proceso continuo, aunque suele tener sesiones formales de 1-2h por semana.

Qué se hace en una sesión de refinamiento:
1. Añadir nuevas historias que surgieron
2. Descomponer épicas que se acercan al sprint
3. Estimar historias que aún no tienen estimación
4. Añadir/refinar criterios de aceptación
5. Eliminar o archivar ítems obsoletos
6. Re-priorizar según cambios de negocio

**Definición de "Ready"** (DoR — Definition of Ready): conjunto de condiciones mínimas para que una historia pueda entrar a un sprint. Ejemplo:
- Tiene criterios de aceptación definidos
- Está estimada
- No tiene dependencias bloqueantes
- El diseño de UX está disponible (si aplica)

---

## 🃏 Estimación — por qué no en horas

### El problema de estimar en horas

Estimar en horas parece natural (como en un presupuesto de ingeniería), pero falla sistemáticamente en software:

1. **La hora no es la unidad correcta**: la misma tarea la hace un senior en 2h y un junior en 8h. La estimación se vuelve personal, no del equipo.
2. **Los humanos son malos estimando en absoluto**: somos mucho mejores comparando (¿esto es más grande o más pequeño que aquello?).
3. **Genera compromisos falsos**: decir "lo termino el martes a las 3pm" crea expectativas que el software invariablemente rompe, generando desconfianza.
4. **Ignora la incertidumbre**: en semanas 1-2 de un sprint no sabes lo que no sabes.

### Story Points — estimación relativa

Los **story points** son una unidad de medida relativa que captura **esfuerzo + complejidad + incertidumbre** de forma combinada. No se traducen directamente a horas.

El proceso:
1. El equipo elige una historia de referencia ("esta es un 3 — la conocemos bien, es mediana")
2. Todas las demás se estiman relativas a esa: "esto es el doble de complejo → 5 o 8 puntos"
3. Los números suelen seguir la secuencia de Fibonacci: **1, 2, 3, 5, 8, 13, 21** (la brecha crece con la incertidumbre)

> Si algo es un 21, es señal de que la historia es demasiado grande o demasiado incierta — hay que descomponerla o investigar más antes de estimarla.

### Planning Poker

Técnica de estimación grupal para evitar el sesgo de anclaje (que la primera persona en hablar influya a todos):

1. El Product Owner lee la historia y responde preguntas de clarificación
2. Cada miembro del equipo elige su carta en secreto (baraja con valores Fibonacci)
3. Se revelan todas a la vez
4. Si hay divergencias grandes (ej: alguien pone 3, otro pone 13), los extremos explican su razonamiento
5. Se debate y se vota de nuevo hasta converger

El valor es la **conversación que surge de las discrepancias** — revelan supuestos distintos sobre el trabajo.

### T-Shirt Sizing — para estimación rápida de épicas

Cuando el backlog está lleno de épicas que aún no se han descompuesto, el planning poker es excesivo. El **T-Shirt Sizing** (tallas de camiseta) da una estimación rápida de orden de magnitud:

| Talla | Equivalencia aproximada | Uso |
|-------|------------------------|-----|
| XS | Horas (< 1 día) | Tareas muy pequeñas |
| S | 1-2 días | Historias simples |
| M | 3-5 días | Historias medianas |
| L | 1-2 semanas | Épicas pequeñas |
| XL | Más de un sprint | Épica — descomponer |

No se usa para compromiso de entrega, solo para priorización y planificación de roadmap.

---

## 📈 Velocity — la consecuencia, no la meta

La **velocity** (velocidad del equipo) es la suma de story points completados en un sprint. No se fija de antemano — emerge de los sprints reales.

Ejemplo: si en los últimos 3 sprints el equipo completó 24, 20 y 22 puntos → velocity media ≈ 22 puntos/sprint.

Usos legítimos de la velocity:
- **Predecir entregas**: si quedan 110 puntos en backlog y la velocity es 22 → ~5 sprints (~10 semanas)
- **Detectar problemas**: velocity cayendo sostenidamente indica deuda técnica, interrupciones o scope creep
- **Planificar sprints**: no coger más de lo que la velocity histórica indica

Usos incorrectos (antipatrones comunes):
- Comparar velocities entre equipos (los puntos no son comparables entre equipos)
- Presionar al equipo para "subir la velocity" (inflan estimaciones o bajan calidad)
- Usarla como KPI de productividad para management

> La velocity es una brújula interna del equipo, no un indicador de rendimiento externo.

---

## ⚠️ Errores comunes

| Error | Por qué pasa | Cómo evitarlo |
|-------|-------------|---------------|
| Historias técnicas ("Refactorizar el módulo de auth") | El equipo piensa en implementación, no en valor | Reformular: "Como usuario quiero que el login sea más rápido para no esperar"; si es deuda técnica pura, ponla como tarea interna o spike |
| Sin criterios de aceptación | Parecen obvios durante la escritura | Hacerlos obligatorios para pasar a "Ready" |
| Épicas que entran al sprint | El PO no tuvo tiempo de descomponer | La DoR actúa de filtro; si no está descompuesta, no entra |
| Estimación en horas presionada por management | Necesitan fechas de entrega | Usar velocity + story points para dar rangos de fecha, no compromisos puntuales |
| Backlog infinito y nunca priorizado | Se añade todo "por si acaso" | Limitar el backlog a lo que es realista hacer en 3-6 meses; el resto va al "ice box" o se descarta |
| Velocity como objetivo | Manager dice "necesito que suban la velocity" | Explicar que medir la regla no cambia lo que mides; el objetivo es entregar valor, la velocity es una lectura |

---

## 🛠️ Aplícalo a tus proyectos

### app web (React + FastAPI + MongoDB)

Tienes una app en curso. Puedes arrancar un backlog mínimo ahora mismo:

**Épica actual (inferida)**: "Seguimiento de ingesta diaria"

Historias candidatas:
```
Como usuario registrado
quiero buscar alimentos por nombre
para añadirlos a mi registro del día sin escribir los valores manualmente

Criterios de aceptación:
  Given que escribo "pollo" en el buscador
  When presiono buscar
  Then veo una lista de ≤10 resultados con nombre, calorías y macros por 100g
  And puedo seleccionar uno y especificar la cantidad en gramos
```

Para estimar sin equipo: usa una escala personal de 1-5 (1 = trivial, 5 = requiere investigación + implementación compleja). Úsala consistentemente y tu "velocity personal" emergerá en 2-3 semanas.

### proyecto embebido (PlatformIO / hardware)

Los proyectos embebidos también tienen backlog. Las historias pueden tener rol de "operador" o "sistema":

```
Como operador del invernadero
quiero recibir una alerta si la temperatura supera 30°C
para actuar antes de que las plantas sufran daño
```

El formato funciona igual — te fuerza a pensar en el valor antes que en el sensor y el threshold.

### Gestión personal de proyectos

Si usas Obsidian para gestionar tus proyectos, el backlog puede vivir como lista en `40_Proyectos/<proyecto>/backlog.md` con etiquetas de prioridad (`#p1`, `#p2`) y estado (`#listo`, `#en-progreso`, `#hecho`). Dataview puede renderizarlo como tabla dinámica.

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[02-manifiesto-agil]]
- [[03-scrum]]
- [[04-kanban-y-lean]]
- [[06-otros-marcos]]
- [[09-metricas-y-seguimiento]]
- [[10-producto-y-priorizacion]]
- [[11-equipo-retros-y-antipatrones]]
