---
title: Otros marcos ágiles
date: 2026-06-13
tags: [programacion/agile, programacion/xp, programacion/escalado, programacion/lean]
type: nota
status: en-progreso
source: claude-code
aliases: [XP, marcos de escalado, Shape Up]
---

# 🗺️ Otros marcos ágiles

Scrum y Kanban son los más populares, pero el ecosistema ágil es más amplio. Este documento cubre tres territorios distintos:

1. **XP** — un marco centrado en prácticas de ingeniería concretas (el "cómo construir bien")
2. **Marcos de escalado** — qué hacer cuando Scrum/Kanban no alcanzan para múltiples equipos
3. **Shape Up y Lean Startup** — enfoques alternativos al ciclo estándar de sprints

La pregunta de fondo que responden todos: *¿cómo mantenemos velocidad y calidad cuando el producto, el equipo o la incertidumbre crecen?*

---

## 1. XP — Extreme Programming

### ¿Por qué existe?

A finales de los 90, Kent Beck trabajaba en un proyecto C3 en Chrysler con un equipo pequeño bajo presión. Observó que algunas prácticas de ingeniería — cuando se llevaban al extremo — reducían bugs y aceleraban el desarrollo. Las formalizó en un conjunto coherente: XP.

XP no es un proceso de gestión (no te dice cómo planificar sprints); es un conjunto de **prácticas técnicas** que se refuerzan mutuamente. Se puede combinar con Scrum (de hecho, muchos equipos Scrum adoptan prácticas XP sin saberlo).

### Las prácticas clave

#### 🤝 Pair Programming (programación en pareja)
Dos personas, un teclado. Una conduce (*driver*), la otra revisa en tiempo real (*navigator*). Se rotan.

- **Qué ganas**: menos bugs, transferencia de conocimiento instantánea, menos silos.
- **Qué pierdes**: velocidad individual a corto plazo, puede cansar si se abusa.
- **Cuándo usarlo**: código crítico, onboarding de alguien nuevo, lógica compleja que un solo par de ojos no ve.
- **Cuándo NO**: tareas mecánicas, exploración rápida de un spike (*spike* = investigación acotada sin presión de calidad).

#### 🔴🟢🔵 TDD — Test-Driven Development
El ciclo es: **Rojo → Verde → Refactor**.

1. Escribe un test que falla (rojo) — defines el comportamiento esperado antes de implementar.
2. Escribe el código mínimo para pasarlo (verde).
3. Limpia sin romper tests (refactor).

Para alguien de hardware: es como escribir primero el pliego de especificaciones del módulo y después el circuito. El test es la especificación ejecutable.

Lo que TDD realmente aporta no es la cobertura de tests — es que **fuerza a pensar en la interfaz antes que en la implementación**, lo que produce APIs más limpias.

#### 🔁 Integración Continua (CI)
Todos los desarrolladores integran su código al repositorio compartido **varias veces al día**. Cada integración lanza una batería de tests automáticamente.

El problema que resuelve: el "infierno de la integración" — cuando cada equipo trabaja en su rama durante semanas y al mergear todo explota. CI lo convierte en micro-explosiones manejables.

> No confundir CI con el pipeline de CD/despliegue — eso se expande en [[08-devops-y-cicd]].

#### ♻️ Refactoring continuo
Mejorar la estructura interna del código sin cambiar su comportamiento externo, de forma continua — no como una tarea puntual cada 6 meses.

La metáfora clásica: la **deuda técnica** (*technical debt*). Código rápido-pero-sucio es como pedir un crédito: funciona ahora, pero pagas intereses (tiempo extra) cada vez que tocas esa parte. Refactorizar es amortizar la deuda.

La regla **Boy Scout**: *deja el código más limpio de como lo encontraste*. Pequeñas mejoras constantes evitan la entropía.

#### 🧑‍🤝‍🧑 Propiedad colectiva del código (*Collective Code Ownership*)
Cualquier miembro del equipo puede modificar cualquier parte del código en cualquier momento. No hay "dueños" de módulos.

Combinado con pair programming y TDD, esto elimina los cuellos de botella por conocimiento silado. El riesgo — que alguien rompa algo que no entiende — lo mitiga la batería de tests.

### XP en una frase
> XP es el conjunto de prácticas técnicas que hace sostenible el ritmo ágil a largo plazo.

---

## 2. 📈 Marcos de escalado

### ¿Por qué hacen falta?

Scrum funciona bien para **un solo equipo de 5-9 personas**. Cuando el producto crece y necesitas 5, 10 o 50 equipos trabajando sobre el mismo sistema, aparecen problemas nuevos:

- ¿Quién prioriza qué cuando dos equipos quieren el mismo componente?
- ¿Cómo se sincroniza la entrega si los sprints no están alineados?
- ¿Quién decide la arquitectura compartida?

Los marcos de escalado intentan responder esto. Ninguno es perfecto — todos añaden overhead (*overhead* = trabajo de coordinación que no produce código).

### SAFe — Scaled Agile Framework

El más extendido en grandes corporaciones. Organiza los equipos en capas:

```
Portfolio (estrategia, OKRs)
    └── Value Stream (flujo de valor de extremo a extremo)
            └── ART — Agile Release Train (8-12 equipos sincronizados)
                    └── Equipos Scrum individuales
```

El **ART** (*Agile Release Train* — tren de liberación ágil) es la unidad central: un conjunto de equipos que planifican juntos cada 8-12 semanas (PI Planning, *Program Increment*) y entregan de forma coordinada.

**Cuándo usar SAFe**: organizaciones grandes (>100 devs), con múltiples líneas de producto, que ya tienen procesos establecidos y necesitan un marco que "hable el idioma corporativo" (ROI, portfolio, compliance).

**Crítica habitual**: SAFe añade mucha ceremonia y roles, y puede recrear burocracia waterfall con etiquetas ágiles. Requiere transformación cultural real para funcionar.

### LeSS — Large-Scale Scrum

Filosofía opuesta a SAFe: **menos proceso, más Scrum**. En lugar de añadir capas, elimina roles y escala Scrum directamente.

- Un solo **Product Backlog** compartido para todos los equipos.
- Un solo **Product Owner** (o muy pocos).
- Múltiples equipos Feature — cada uno hace un Scrum completo.
- **Sprint Review** y **Retrospectiva** conjuntas.

Existe en dos versiones:
- **LeSS** básico: hasta 8 equipos.
- **LeSS Huge**: más de 8 equipos, introduce "Area Product Owners".

**Cuándo usar LeSS**: organizaciones dispuestas a una transformación real (eliminar roles intermedios, reorganizar equipos). Más difícil de vender en empresas tradicionales, pero más coherente con los principios ágiles.

### Nexus

Creado por Scrum.org (los mismos que definen Scrum). Es la opción más conservadora: añade una única capa sobre Scrum estándar, el **Nexus Integration Team** — un equipo responsable de integrar el trabajo de 3-9 equipos Scrum.

**Cuándo usar Nexus**: escala moderada (30-70 devs), equipos que ya saben Scrum bien, quieres el mínimo overhead añadido.

### Modelo Spotify 🎵

No es un framework formal — es una descripción de cómo Spotify organizó sus equipos alrededor de 2012. Se popularizó tanto que se trata como modelo.

La terminología clave:

| Término | Qué es | Analogía |
|---|---|---|
| **Squad** (escuadrón) | Equipo autónomo de ~8 personas, dueño de un área de producto | Un Scrum Team |
| **Tribe** (tribu) | Conjunto de Squads con misión relacionada (~100 personas) | Una división de producto |
| **Chapter** (capítulo) | Personas del mismo rol técnico en distintos Squads (ej: todos los QAs de una Tribe) | Comunidad de práctica vertical |
| **Guild** (gremía) | Comunidad de interés transversal a toda la empresa | Club voluntario |

**Lo que realmente aportó**: la idea de que los equipos deben ser *autónomos y alienados* (*loosely coupled, tightly aligned*) — libres de decidir cómo construyen, pero alineados en qué construyen.

**Advertencia crítica**: el propio Spotify ha dicho que ellos no siguen "el modelo Spotify" — evolucionaron más allá. Muchas empresas copian la estructura sin la cultura que la sustenta, con resultados pobres.

### ¿Cuándo escalar?

| Señal | Qué considera |
|---|---|
| Varios equipos pisándose constantemente | Empieza por Nexus o LeSS básico |
| Gran empresa, necesitas "vender" el cambio al management | SAFe (pese a sus críticas) |
| Quieres autonomía real de equipos + cultura fuerte | Modelo Spotify como inspiración, no como receta |
| Tienes un solo equipo de <9 personas | **No escales. Scrum o Kanban directo.** |

---

## 3. 🍃 Shape Up (Basecamp)

### ¿Por qué existe?

Ryan Singer y Jason Fried (Basecamp) diseñaron Shape Up después de sentir que los sprints de 2 semanas creaban demasiado overhead de planificación y no dejaban tiempo para trabajo ambicioso. Lo publicaron como libro gratuito en 2019.

Shape Up no es ágil en el sentido clásico — es una alternativa para equipos de producto pequeños que quieren ciclos más largos y menos reuniones.

### Los conceptos clave

#### Appetite (apetito)
En Scrum estimas cuánto tarda una tarea. En Shape Up te preguntas: **¿cuánto tiempo estamos dispuestos a invertir en este problema?**

Esto invierte la ecuación: el tiempo es fijo, el alcance es variable. Si no terminas en el tiempo asignado, no alargas — reduces alcance o descartas.

Existen dos apetitos estándar:
- **Small batch**: 2 semanas
- **Big batch**: 6 semanas

#### Shaping (moldeado)
Antes de apostar por un trabajo, alguien (generalmente un senior técnico o de producto) lo "moldea" — define el problema, los límites de la solución y los riesgos, sin especificar exactamente cómo implementarlo.

El resultado es un **pitch** (*propuesta estructurada*): problema + apetito + solución en boceto + rabbit holes (*trampas conocidas a evitar*).

#### Betting (apuesta)
Cada ciclo, un grupo pequeño de decision-makers elige qué pitches se ejecutan. No hay backlog interminable — si algo no se apuesta, simplemente no entra en este ciclo. Puede volver a proponerse después.

Esto elimina la "cola de prioridades" que en Scrum puede tener items olvidados durante meses.

#### Cycles (ciclos)
- **6 semanas de trabajo** en equipos pequeños (1-2 devs + 1 diseñador) con total autonomía sobre cómo construir.
- **2 semanas de cooldown** (*enfriamiento*): sin sprints, sin deadlines. Tiempo para arreglar bugs, explorar ideas, hacer refactor, descansar.

| Shape Up | Scrum |
|---|---|
| Ciclos de 6 semanas | Sprints de 1-4 semanas |
| Alcance flexible, tiempo fijo | Alcance fijo por sprint (ideal) |
| No hay backlog formal | Backlog central priorizado |
| Equipos con autonomía total | PO define qué, equipo define cómo |
| Orientado a producto pequeño/mediano | Escalable |

**Cuándo usar Shape Up**: equipo pequeño (<20 personas), producto maduro donde los cambios son mejoras ambiciosas más que MVPs, cultura de autonomía alta.

**Cuándo NO**: equipos grandes que necesitan coordinación, cuando los stakeholders exigen visibilidad sprint a sprint, proyectos con muchas dependencias externas.

---

## 4. 🚀 Lean Startup

### ¿Por qué existe?

Eric Ries adaptó los principios de manufactura Lean (Toyota) al contexto de startups. El problema que resuelve: **la mayoría de startups fracasan no por no poder construir, sino por construir algo que nadie quiere.**

Lean Startup no es un marco de gestión de equipo — es una metodología para validar hipótesis de negocio bajo incertidumbre extrema.

### Build-Measure-Learn

El ciclo central:

```
Idea
  ↓
BUILD → Producto (MVP mínimo viable)
  ↓
MEASURE → Métricas accionables
  ↓
LEARN → ¿Validamos o invalidamos la hipótesis?
  ↓
¿Perseverar o Pivotar?
```

**MVP** (*Minimum Viable Product — Producto Mínimo Viable*): la versión más simple que permite aprender si la hipótesis es válida. No es un producto malo — es un experimento.

**Métricas accionables vs. métricas vanidosas**:
- Vanidosa: "tenemos 10.000 usuarios registrados" — no dice si el producto funciona.
- Accionable: "el 40% de los usuarios que completan el onboarding vuelven en 7 días".

### Pivot

Un *pivot* es un **cambio estructurado de dirección** manteniendo lo aprendido. No es abandonar — es redirigir. Tipos comunes:

- **Zoom-in**: lo que era una feature se convierte en el producto entero.
- **Zoom-out**: el producto entero pasa a ser una feature de algo mayor.
- **Segmento de cliente**: mismo producto, distinto mercado objetivo.
- **Plataforma**: de app a plataforma que otros usan.

**Cuándo usar Lean Startup**: fase inicial de producto (no sabes si hay mercado), validación de nuevas líneas dentro de un producto existente, proyectos de I+D con alta incertidumbre.

**Cuándo NO**: desarrollo de un producto ya validado donde el problema conocido es velocidad de ejecución, no descubrimiento.

---

## 📊 Tabla resumen

| Marco | Nivel | Para qué | Overhead | Cuándo NO |
|---|---|---|---|---|
| **XP** | Equipo | Prácticas técnicas de calidad | Bajo-medio | Si el equipo no tiene cultura de tests |
| **SAFe** | Enterprise | Coordinar >8 equipos en corp. grande | Alto | Equipos pequeños, startups |
| **LeSS** | Multi-equipo | Escalar Scrum con menos proceso | Medio | Sin voluntad de transformación real |
| **Nexus** | Multi-equipo | Integrar 3-9 equipos Scrum | Bajo | Más de 9 equipos |
| **Modelo Spotify** | Multi-equipo | Inspiración de autonomía por squads | Variable | Como receta rígida |
| **Shape Up** | Equipo/producto | Ciclos largos, producto maduro | Bajo | Coordinación multi-equipo compleja |
| **Lean Startup** | Producto/negocio | Validar hipótesis bajo incertidumbre | Bajo | Producto ya validado, ejecución pura |

---

## Errores comunes

- **Adoptar SAFe sin transformación cultural**: el resultado es Waterfall con post-its.
- **Copiar el modelo Spotify como org chart**: la estructura sin la cultura es decorativa.
- **Confundir MVP con prototipo malo**: un MVP es un experimento válido, no "la versión chapuza".
- **Usar Shape Up con muchos stakeholders externos**: funciona con autonomía interna; si hay dependencias externas fijas, los ciclos de 6 semanas se rompen.
- **Adoptar TDD al 100% desde el día 1**: la curva de aprendizaje es real. Empieza con las partes más críticas del código.
- **Pivotar demasiado pronto o demasiado tarde**: pivotar antes de tener datos es pánico; no pivotar ante datos claros es ego.

---

## 🛠️ Aplícalo a tus proyectos

### app web (React + FastAPI + MongoDB)

- **TDD**: empieza por los endpoints críticos (registro de alimentos, cálculo de macros). Escribe el test de la ruta antes de implementarla con pytest.
- **Integración Continua**: ya tienes Docker Compose — añade un workflow de GitHub Actions que corra los tests en cada push. Ver [[08-devops-y-cicd]].
- **Refactor continuo**: cuando añadas la capa de servicios, aplica la regla Boy Scout: si tocas un módulo, mejora una cosa pequeña.
- **Lean Startup**: antes de implementar features complejas (ej: recomendaciones de dieta con IA), define la hipótesis y el MVP mínimo para validarla contigo mismo como usuario.

### proyecto embebido (PlatformIO / embedded)

- **Propiedad colectiva**: si eventualmente colaboras, documenta las interfaces de módulos (sensores, actuadores) para que cualquiera pueda tocar sin miedo.
- **Pair Programming**: si trabajas con alguien, úsalo en la lógica de control/FSM donde los bugs son caros de depurar en hardware.
- **Shape Up por inspiración**: para features nuevas de embebido, define el apetito ("no más de 2 semanas para el módulo de riego automático") antes de empezar, y ajusta el alcance si no acabas.

### Proyectos personales pequeños (scripts, herramientas)

- No sobreapliques — Shape Up o Lean Startup son excesivos para un script de backup. Kanban personal es suficiente. Ver [[04-kanban-y-lean]].

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[01-sdlc-e-historia]]
- [[02-manifiesto-agil]]
- [[03-scrum]]
- [[04-kanban-y-lean]]
- [[05-historias-de-usuario-y-backlog]]
- [[07-practicas-de-ingenieria]]
- [[08-devops-y-cicd]]
- [[09-metricas-y-seguimiento]]
- [[10-producto-y-priorizacion]]
- [[11-equipo-retros-y-antipatrones]]
