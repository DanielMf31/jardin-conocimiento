---
title: Producto y Priorización
date: 2026-06-13
tags: [programacion/agile, programacion/product-management, programacion/priorizacion]
type: nota
status: en-progreso
source: claude-code
aliases: [Product Management, Priorización de Backlog, MVP]
---

# 🎯 Producto y Priorización

## ¿Por qué existe el product management?

Construir software es caro. La historia del sector está llena de proyectos que **terminaron a tiempo, dentro de presupuesto y que nadie usó**. El product management nace para responder una pregunta antes de escribir código: *¿esto resuelve un problema real para alguien dispuesto a pagarlo (con dinero, tiempo o atención)?*

En hardware/técnico tienes una disciplina análoga: la ingeniería de requisitos y el análisis de valor (FMEA, QFD). El product management es eso aplicado a software, pero iterando mucho más rápido y con más contacto continuo con el usuario.

---

## 🗺️ Panorama: dónde encaja esto

```
ESTRATEGIA DE NEGOCIO
       ↓
  VISIÓN DE PRODUCTO  ←── Product Manager / Product Owner
       ↓
  ROADMAP (qué, cuándo, por qué)
       ↓
  BACKLOG PRIORIZADO (cómo, detalle)
       ↓
  SPRINTS / ENTREGAS  ←── Equipo de desarrollo
```

El product management vive entre el negocio (o el usuario) y el equipo técnico. Sin este puente, el equipo técnico construye lo que le parece interesante; con el puente, construye lo que genera valor.

---

## 🧪 MVP — Producto Mínimo Viable

### El problema que resuelve

La trampa clásica: pasar 6 meses construyendo el producto "completo" y descubrir que la hipótesis de partida era errónea. Un **MVP** (Minimum Viable Product) es la versión más pequeña del producto que permite aprender si la hipótesis central es válida.

> "Viable" no significa "funcional al 50%". Significa "suficiente para validar el aprendizaje más importante".

### Qué es y qué no es

| Es un MVP | No es un MVP |
|---|---|
| La funcionalidad mínima para probar la hipótesis principal | Un prototipo a medias que no resuelve nada real |
| Una versión que usuarios reales pueden usar | Una demo bonita solo para inversores |
| Algo que entrega valor aunque sea pequeño | Recortes aleatorios para "salir rápido" |

### La curva de aprendizaje

```
Tiempo/Dinero invertido
        │
        │          ██ Producto completo (aprendizaje tardío)
        │       ███
        │    ███
        │ ███
        │██  ← MVP: aprendo aquí con mínimo gasto
        └──────────────────────────────→ Aprendizaje acumulado
```

El objetivo es mover el punto de aprendizaje lo más a la izquierda posible.

---

## 🔍 Discovery vs Delivery

Dos modos de trabajo radicalmente distintos que deben coexistir:

| | Discovery | Delivery |
|---|---|---|
| **Pregunta central** | ¿Qué debemos construir? | ¿Cómo construimos esto bien? |
| **Herramientas** | Entrevistas, prototipos, A/B tests, análisis | Sprints, código, tests, CI/CD |
| **Output** | Decisiones validadas, hipótesis descartadas | Features funcionando en producción |
| **Quién lidera** | Product Manager + UX | Equipo de ingeniería |
| **Frecuencia** | Continuo (paralelo a delivery) | Por sprint/ciclo |

**Error común**: hacer solo delivery (construir sin validar) o solo discovery (hablar con usuarios sin nunca entregar). El equilibrio sano es discovery continuo *mientras* el equipo entrega el sprint actual.

En proyectos personales/pequeños, tú haces ambos roles: dedica tiempo explícito a cada modo.

---

## ⚖️ Técnicas de Priorización

El backlog siempre tiene más ítems de los que puedes construir. Priorizar es decidir explícitamente qué *no* harás ahora. Aquí las técnicas más usadas:

### 1. MoSCoW

Clasifica cada ítem del backlog en cuatro cubos:

| Cubo | Significado | Criterio práctico |
|---|---|---|
| **M**ust have | Sin esto el producto no funciona / no se puede lanzar | Si falta, es un bloqueante real |
| **S**hould have | Importante, pero hay workaround temporal | Alta prioridad para la siguiente iteración |
| **C**ould have | Deseable, enriquece la experiencia | Solo si sobra capacidad |
| **W**on't have (this time) | Descartado para este ciclo | Puede revisarse en el futuro |

**Cuándo usarlo**: kick-off de proyecto, cuando el equipo debate qué entra en un release, o cuando el cliente pide "todo para mañana".

**Cuándo NO**: cuando ya tienes muchos ítems en Must y necesitas diferenciar entre ellos (MoSCoW no distingue dentro del cubo M).

---

### 2. RICE

Puntuación cuantitativa para comparar ítems entre sí:

```
RICE = (Reach × Impact × Confidence) / Effort
```

| Factor | Qué mide | Escala típica |
|---|---|---|
| **Reach** | ¿A cuántos usuarios impacta en un período? | Número absoluto (usuarios/mes) |
| **Impact** | ¿Cuánto mejora la experiencia? | 0.25 / 0.5 / 1 / 2 / 3 |
| **Confidence** | ¿Qué tan seguros estamos de R e I? | 20% / 50% / 80% / 100% |
| **Effort** | ¿Cuánto trabajo requiere? | Persona-meses |

El ítem con mayor RICE va primero. Útil porque **fuerza a hacer explícitas las suposiciones** (especialmente Confidence).

**Cuándo usarlo**: equipos medianos con varios PMs compitiendo por el mismo equipo de desarrollo.

**Cuándo NO**: proyectos personales o equipos pequeños donde el overhead de calcular no compensa.

---

### 3. Matriz Valor / Esfuerzo

La más rápida de aplicar. Dibuja un cuadrante 2×2:

```
Valor
  ▲
  │  Quick Wins ★  │  Proyectos grandes
  │  (hacer ya)    │  (planificar)
  ├────────────────┼────────────────────
  │  Fill-ins      │  Tareas ingrato
  │  (si sobra)    │  (evitar/delegar)
  └────────────────────────────────────→ Esfuerzo
```

| Cuadrante | Estrategia |
|---|---|
| Alto valor, bajo esfuerzo | Hacer primero (Quick Wins) |
| Alto valor, alto esfuerzo | Planificar con cuidado (Proyectos grandes) |
| Bajo valor, bajo esfuerzo | Solo si no hay nada más (Fill-ins) |
| Bajo valor, alto esfuerzo | Evitar o cancelar |

**Cuándo usarlo**: sesiones de refinamiento, retros de planning, proyectos personales donde quieres decidir en minutos.

---

### 4. Modelo Kano

Categoriza features según cómo afectan la **satisfacción del usuario** en función de si están presentes o ausentes:

| Categoría | Ausente | Presente | Ejemplo |
|---|---|---|---|
| **Must-be** (básico) | Muy insatisfecho | Neutral (se da por sentado) | Que la app no crashee |
| **Performance** (lineal) | Insatisfecho | Más satisfecho en proporción | Velocidad de carga |
| **Attractive** (delighter) | Neutral | Muy satisfecho (sorpresa positiva) | Modo oscuro, easter eggs |
| **Indifferent** | Neutral | Neutral | Features que nadie usa |
| **Reverse** | Más satisfecho | Insatisfecho | Demasiadas notificaciones |

**Por qué importa**: los Must-be no generan satisfacción extra si los implementas bien (son el piso), pero destruyen la experiencia si fallan. Los Attractive son los que generan boca a boca. **Primero piso sólido, luego delighters.**

**Cuándo usarlo**: cuando diseñas el set de features de un producto nuevo o cuando quieres priorizar qué invertir para mejorar NPS.

---

## 🗓️ Roadmaps de Producto

Un roadmap es la **comunicación visual de la estrategia de producto en el tiempo**. No es un Gantt de tareas técnicas — es una narrativa de por qué se construye qué y cuándo.

### Tipos comunes

| Tipo | Horizonte | Uso |
|---|---|---|
| Now / Next / Later | Sin fechas exactas | Equipos ágiles; comunica prioridad sin comprometerse |
| Por trimestres | 6-12 meses | Empresas con planning trimestral (OKRs) |
| Por temas (themes) | Estratégico | Agrupa features bajo objetivos de negocio |
| Gantt de producto | Fijo | Contratos/proyectos con fechas comprometidas |

### Errores comunes en roadmaps

- **Comprometer fechas exactas para features específicas**: garantiza frustración. Usa rangos o quarters.
- **No comunicar el "por qué"**: el equipo optimiza para entregar lo pedido, no para resolver el problema.
- **Roadmap como contrato**: el roadmap debe cambiar cuando el aprendizaje lo justifica. Si no cambia nunca, no estás aprendiendo.

---

## 👤 El Rol del Product Owner

En Scrum (ver [[03-scrum]]), el **Product Owner (PO)** es la persona responsable de maximizar el valor del producto. Sus responsabilidades concretas:

1. **Gestionar el Product Backlog**: crear, refinar y ordenar los ítems.
2. **Definir el criterio de aceptación** de cada historia de usuario.
3. **Ser el punto de contacto** entre stakeholders y el equipo.
4. **Tomar decisiones de priorización** (no puede delegarlas al equipo ni al Scrum Master).
5. **Aceptar o rechazar** el trabajo al final de cada Sprint.

> En proyectos personales o startups pequeñas, tú eres el PO. Asume el rol conscientemente: bloquea tiempo para hablar con usuarios (aunque seas tú mismo el usuario).

**Product Owner ≠ Project Manager**: el PO decide *qué* construir y *por qué*. El PM (Project Manager) gestiona *cómo* se entrega (tiempos, recursos, riesgos). En muchos equipos modernos, el PO absorbe parte del trabajo del PM.

---

## 📊 OKRs de Producto

**OKR** = Objectives and Key Results. Marco para definir metas ambiciosas y medir su consecución.

### Estructura

```yaml
Objective: "Hacer que los usuarios recurrentes confíen en la app para su dieta diaria"
  Key Result 1: "DAU/MAU ratio pasa de 0.15 a 0.35 en Q3"
  Key Result 2: "Retención a 30 días supera el 40%"
  Key Result 3: "NPS pasa de 22 a 45"
```

| Elemento | Descripción | Característica |
|---|---|---|
| **Objective** | Qué queremos lograr | Cualitativo, inspiracional, sin ambigüedad sobre dirección |
| **Key Result** | Cómo medimos el éxito | Cuantitativo, verificable, no una tarea sino un resultado |

### OKRs vs KPIs

- **KPI** (Key Performance Indicator): métrica de salud continua que monitoreas (ej: uptime, tiempo de carga). No tiene fecha de expiración.
- **OKR**: objetivo con horizonte temporal (trimestre/año) que guía dónde enfocar el esfuerzo. Los Key Results *pueden* ser KPIs, pero con un target específico para un período.

**Error clásico**: poner tareas como Key Results. "Lanzar feature X" es una tarea. "Reducir churn un 10%" es un Key Result.

---

## 🚀 Aplícalo a tus proyectos

### app web (`app web`)

**Discovery inmediato**:
- ¿Para quién es primero: para ti (usuario con EDS/POTS) o para cualquier usuario? Definir esto cambia todo el backlog.
- La hipótesis de MVP: *"Un usuario puede registrar su ingesta de Na/K y ver si está en rango."* ¿Está validada? ¿Lo usarías hoy si existiera?

**Priorización con Matriz Valor/Esfuerzo**:

| Feature | Valor | Esfuerzo | Acción |
|---|---|---|---|
| Registro manual de ingesta | Alto | Bajo | Quick Win — ya |
| Dashboard Na/K diario | Alto | Medio | Planificar |
| Base de datos de alimentos (scraping/API) | Alto | Alto | Proyecto grande |
| Modo oscuro | Bajo | Bajo | Fill-in |
| Integración con wearable | Bajo (ahora) | Alto | Evitar por ahora |

**MoSCoW para el primer release**:
- Must: autenticación, registro de comida, visualización de Na/K del día
- Should: historial de 7 días, targets configurables
- Could: sugerencias de alimentos, exportar CSV
- Won't (ahora): integración wearable, modo multiusuario

**OKR de producto (Q3 2026 hipotético)**:
```
Objective: "Convertir la app en mi herramienta real de tracking diario"
  KR1: Uso durante 30 días consecutivos sin fricción
  KR2: Tiempo de registro de una comida < 60 segundos
  KR3: Identificar al menos 2 patrones entre Na/K y síntomas POTS
```

### Proyectos personales en general

Antes de arrancar cualquier proyecto nuevo, hazte estas preguntas (tu propio mini-discovery):
1. ¿Qué problema resuelve y para quién?
2. ¿Cuál es la hipótesis central que quiero validar?
3. ¿Cuál es el MVP que valida esa hipótesis con el mínimo esfuerzo?
4. ¿Cómo sabré que funciona? (métrica o criterio concreto)

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[01-sdlc-e-historia]]
- [[02-manifiesto-agil]]
- [[03-scrum]]
- [[05-historias-de-usuario-y-backlog]]
- [[09-metricas-y-seguimiento]]
- [[11-equipo-retros-y-antipatrones]]
