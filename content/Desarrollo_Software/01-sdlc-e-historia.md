---
title: Ciclo de vida del software e historia
date: 2026-06-13
tags: [programacion/agile, programacion/sdlc, programacion/historia, programacion/metodologias]
type: nota
status: en-progreso
source: claude-code
aliases: [SDLC, ciclo de vida software, historia agile]
---

# 🏗️ Ciclo de vida del software e historia

## ¿Por qué existe esto?

En hardware/técnico tienes procesos bien definidos: especificación → diseño → prototipo → validación → producción. El software también necesita estructura, pero durante décadas no hubo acuerdo sobre cuál. El resultado fue la **crisis del software** (años 60-80): proyectos que se entregaban tarde, con coste desorbitado o directamente fallaban. El SDLC es el intento de respuesta sistemática a ese caos.

---

## 📐 ¿Qué es el SDLC?

**SDLC** (*Software Development Life Cycle*, ciclo de vida del desarrollo de software) es el marco conceptual que describe las **fases por las que pasa un producto software**, desde la idea hasta su retirada.

No es un proceso concreto — es la abstracción. Los modelos concretos (Waterfall, Scrum, Kanban…) son instancias del SDLC con distintas respuestas a la pregunta: *¿en qué orden hacemos estas fases y cuántas veces?*

### Fases canónicas del SDLC

| # | Fase | Qué ocurre |
|---|------|-----------|
| 1 | **Planificación** | Alcance, viabilidad, recursos, calendario |
| 2 | **Análisis de requisitos** | Qué debe hacer el sistema (no cómo) |
| 3 | **Diseño** | Arquitectura, BD, interfaces, tecnología |
| 4 | **Implementación** | Escritura de código |
| 5 | **Pruebas / Verificación** | Detección de defectos, validación contra requisitos |
| 6 | **Despliegue** | Puesta en producción |
| 7 | **Mantenimiento** | Correcciones, mejoras, operación continuada |

Los distintos modelos difieren en: ¿se hacen en secuencia única, en bucles, en paralelo?

---

## 🌊 Modelos clásicos

### Waterfall (Cascada) — 1970

El más antiguo y el más conocido. Las fases se ejecutan **en secuencia estricta, una sola vez**, como el agua que cae: no se sube.

```
Planificación → Requisitos → Diseño → Implementación → Pruebas → Despliegue
```

**Origen**: Winston Royce, 1970 — con la ironía de que su paper original ya advertía que el modelo puro era *arriesgado* y proponía iteración. La industria adoptó el diagrama y olvidó la advertencia.

**Supuesto implícito**: los requisitos se conocen completos y estables desde el inicio. En la práctica, raramente es verdad en software.

---

### Modelo en V — 1980s

Refinamiento del cascada que explicita el **vínculo entre cada fase de desarrollo y su fase de prueba correspondiente**.

```
Requisitos ←————————————→ Pruebas de aceptación
  Diseño sistema ←——————→ Pruebas de integración
    Diseño detalle ←————→ Pruebas unitarias
             [Implementación]
```

La forma de V refleja que la verificación se planifica *al mismo tiempo* que el desarrollo, no después. Muy usado en sistemas embebidos, automoción (ASPICE) y dispositivos médicos — ámbitos donde la trazabilidad requisito↔test es regulatoria. **Si vienes de hardware, este modelo te sonará familiar.**

**Ventaja sobre cascada puro**: los defectos se detectan antes porque los planes de prueba se diseñan en paralelo a los requisitos.

---

### Iterativo e Incremental — 1980s-1990s

En lugar de un único ciclo largo, el desarrollo se divide en **iteraciones** (ciclos cortos): en cada una se produce un **incremento** funcional del sistema.

- **Iterativo**: se repite el ciclo de fases; cada vuelta refina y corrige.
- **Incremental**: cada vuelta añade funcionalidad nueva sobre lo anterior.
- En la práctica se combinan: cada iteración es incremental *y* refina lo previo.

**Ejemplos históricos**: Proceso Unificado de Rational (RUP), espiral de Boehm.

La idea central: *entregar algo funcional pronto y corregir el rumbo con feedback real*, en lugar de descubrir al final que los requisitos eran erróneos.

---

## 💥 La crisis del software

Entre los años 60 y 90, la industria acumuló evidencia de fracasos masivos:

- El informe **CHAOS Report** (Standish Group, 1994) documentó que solo el 16% de los proyectos software se entregaban a tiempo y dentro del presupuesto.
- El 31% se cancelaban antes de completarse.
- Proyectos gubernamentales y militares (el sistema de reservas de vuelos SABRE, el software del transbordador espacial) mostraban la escala del problema.

### Causas identificadas del fracaso en cascada

1. **Requisitos que cambian** — el cliente no sabe qué quiere hasta que lo ve; el mercado cambia en 18 meses de desarrollo.
2. **Feedback tardío** — los errores de análisis se descubren en la fase de pruebas, cuando cambiarlos es 10-100x más caro que al inicio.
3. **Integración "big bang"** — todo se junta al final; los problemas de integración aparecen tarde y son devastadores.
4. **Planificación ilusoria** — los calendarios se fijan con incertidumbre altísima y se cumplen mal.
5. **Documentación como fin en sí misma** — se producen cientos de páginas de especificación que nadie lee y que quedan obsoletas.

> **Analogía hardware**: imagina diseñar un PCB sin prototipo, mandar a fabricar 10.000 unidades, y descubrir el error de diseño cuando ya están en el almacén. El cascada en software tenía ese problema de forma sistemática.

---

## 🚀 Por qué nació Agile (2001)

A finales de los 90, varios practicantes con metodologías alternativas (XP, Scrum, DSDM, Crystal…) convergieron en la misma intuición: el problema no era la falta de disciplina, sino la **ilusión de que el software es predecible como la manufactura**.

En **febrero de 2001**, 17 personas se reunieron en Snowbird, Utah. El resultado: el **Manifiesto Ágil** — cuatro valores y doce principios que priorizaban:

- **Individuos e interacciones** sobre procesos y herramientas
- **Software funcionando** sobre documentación exhaustiva
- **Colaboración con el cliente** sobre negociación de contratos
- **Respuesta al cambio** sobre seguir un plan

No era anti-proceso ni anti-documentación; era una reordenación de prioridades. El manifiesto reconoce explícitamente el valor de la columna derecha — solo dice que la izquierda vale *más*.

El detonante conceptual: el software opera en un dominio **complejo** (en el sentido del marco Cynefin — donde causa y efecto solo son visibles en retrospectiva), no en un dominio *complicado* (donde expertos pueden predecir). Los métodos predictivos funcionan en lo complicado; en lo complejo, necesitas empirismo e inspección continua.

---

## ⚖️ Cascada vs. Iterativo — comparativa directa

| Dimensión | Cascada | Iterativo/Ágil |
|-----------|---------|---------------|
| **Planificación** | Completa al inicio | Progresiva; detalle emerge |
| **Requisitos** | Fijos, documentados exhaustivamente | Evolucionan con feedback |
| **Entrega de valor** | Al final del proyecto | Cada iteración (semanas) |
| **Coste del cambio** | Muy alto (tardío = caro) | Bajo (se asume y se gestiona) |
| **Feedback del cliente** | En la entrega final | Continuo, cada sprint |
| **Riesgo** | Concentrado al final | Distribuido y mitigado pronto |
| **Documentación** | Exhaustiva y previa | Suficiente y justo-a-tiempo |
| **Estructura del equipo** | Roles separados por fase | Equipos cross-funcionales |
| **Apropiado cuando…** | Requisitos estables, regulación alta | Requisitos inciertos, innovación |

---

## ✅ Cuándo el cascada sigue teniendo sentido

No todo es ágil. El cascada (o el modelo en V) es la elección correcta cuando:

1. **Los requisitos son completos, estables y verificables** — proyectos de defensa, aeroespacial, dispositivos médicos (FDA, IEC 62304).
2. **La regulación exige trazabilidad exhaustiva** — la documentación pesada es un requisito legal, no burocracia opcional.
3. **El coste de iteración es prohibitivo** — firmware de hardware ya fabricado, sistemas de control en producción.
4. **El equipo está distribuido o subcontratado** — contratos de precio fijo con terceros necesitan especificación cerrada.
5. **El problema es bien conocido y repetible** — una versión mayor de un sistema con 20 años de historia y requisitos estabilizados.

> Si vienes de diseñar PCBs para series de producción: la lógica es la misma. El cascada es razonable cuando cambiar en producción es carísimo. En software de producto o startup, el coste de cambio es bajo — entonces el iterativo gana.

### Errores comunes al elegir modelo

- **Usar cascada "porque el cliente lo pide"** — a menudo el cliente pide un plan fijo por miedo a la incertidumbre; la respuesta ágil es gestionar esa incertidumbre explícitamente, no ignorarla.
- **Usar ágil en proyectos regulados sin adaptación** — Scrum puro no satisface IEC 62304. Existen marcos híbridos (SAFe, DAD) para ese caso.
- **Confundir "ágil" con "sin plan"** — Agile tiene planificación continua y rigurosa; simplemente es adaptativa, no predictiva.

---

## 🔧 Aplícalo a tus proyectos

**app web (React + FastAPI + MongoDB)**
Este proyecto tiene requisitos que evolucionan (no sabes exactamente qué pantallas necesitarás hasta probarlas). El cascada sería un error: trabaja iterativo. Define un MVP funcional (ej: registro de comida + cálculo de Na/K), despliégalo, úsalo tú mismo, luego itera. Cada semana debería haber algo funcionando.

**proyecto embebido (PlatformIO / embebido)**
El firmware de hardware ya fabricado está más cerca del dominio del modelo en V: los requisitos de interfaz hardware son fijos (pines, protocolos). Aplica V para la parte de firmware crítica; puedes ser más iterativo en la capa de aplicación/comunicaciones si el hardware lo permite.

**Bóveda Obsidian**
La propia bóveda es un proyecto iterativo de PKM: no diseñas la estructura completa al inicio, la dejas emerger. El CLAUDE.md es tu "backlog de arquitectura" — una lista viva, no un spec congelado.

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[02-manifiesto-agil]]
- [[03-scrum]]
- [[04-kanban-y-lean]]
- [[07-practicas-de-ingenieria]]
- [[08-devops-y-cicd]]
- [[09-metricas-y-seguimiento]]
