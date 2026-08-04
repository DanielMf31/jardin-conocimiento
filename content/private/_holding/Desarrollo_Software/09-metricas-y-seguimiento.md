---
title: Métricas y seguimiento
date: 2026-06-13
tags: [programacion/agile, programacion/devops, programacion/gestion, programacion/metricas]
type: nota
status: en-progreso
source: claude-code
aliases: [metricas agile, DORA, velocity]
---

# Métricas y seguimiento

## ¿Por qué existen las métricas en software?

En ingeniería mecánica tienes tolerancias, curvas de fatiga, coeficientes de seguridad: números que te dicen si el sistema está dentro de spec. En software el equivalente tardó décadas en madurar porque el "producto" es invisible. Las métricas modernas de desarrollo no miden el esfuerzo (líneas de código, horas trabajadas) sino los **resultados y el flujo**: ¿qué entrega el equipo?, ¿qué tan rápido llega al usuario?, ¿cuándo se rompe y cuánto tarda en recuperarse?

Sin métricas terminas en uno de dos extremos: piloto automático (nadie sabe si mejora) o microgestión (jefes mirando horas). Con métricas bien elegidas el equipo tiene un tablero de instrumentos, no un vigilante.

---

## 1. Velocity y Capacity

### Capacity (capacidad)

**Qué es**: la cantidad de trabajo que el equipo *podría* hacer en un sprint, expresada en horas disponibles reales.

```
Capacity = suma de horas disponibles de cada miembro × factor de enfoque
Factor de enfoque típico: 0.6–0.7  (reuniones, interrupciones, slack)
```

Ejemplo: 4 devs × 40 h × 0.65 = **104 h efectivas** por sprint de 2 semanas.

La capacity se usa para **planificación**: no metas más trabajo del que el equipo puede absorber físicamente.

### Velocity (velocidad)

**Qué es**: puntos de historia (story points) completados por sprint, promediado sobre los últimos 3–5 sprints.

- Los **story points** son unidades relativas de esfuerzo/complejidad, no horas. Una historia de 3 puntos no vale 3 horas; vale "lo que sea que el equipo llama 3 puntos".
- La velocity emerge del equipo: no se impone desde arriba.
- Sirve para **pronosticar** cuántos sprints quedan para terminar un backlog.

```
Sprints restantes ≈ puntos pendientes en backlog / velocity media
```

| Concepto | Mide | Para qué sirve |
|---|---|---|
| Capacity | Horas disponibles | Planificar cuánto cabe en el sprint |
| Velocity | Puntos entregados | Pronosticar fecha de entrega |

> **Trampa frecuente**: inflación de puntos. Si el equipo siente presión por velocity alta, empieza a estimar alto sin que el trabajo aumente. La velocity pierde valor predictivo.

---

## 2. Gráficos Burndown y Burnup

Estos gráficos son herramientas de **transparencia**: muestran el estado de un sprint o release de un vistazo.

### Burndown (quema hacia abajo)

Eje Y: trabajo restante (puntos o tareas). Eje X: días del sprint.

- La línea ideal desciende linealmente de "trabajo total" a cero.
- La línea real rara vez es lineal: revela problemas (bloqueos, scope añadido).

```
Trabajo restante
│\
│ \  ← ideal
│  \____  ← real (se estancó 3 días)
│       \_
└──────────── días
```

**Cuándo usarlo**: seguimiento diario dentro de un sprint. Si la línea real está por encima de la ideal a mitad de sprint, hay que actuar.

**Limitación**: no muestra si se añadió trabajo durante el sprint (scope creep — añadir tareas no planeadas). Todo se ve como "trabajo restante que no baja".

### Burnup (quema hacia arriba)

Eje Y: trabajo completado + línea de scope total. Eje X: tiempo.

- Dos líneas: trabajo hecho (sube) y scope total (puede cambiar).
- Cuando las dos líneas se tocan: sprint/release completado.

**Ventaja sobre burndown**: hace visible el scope creep (la línea de scope sube y la brecha no se cierra aunque el equipo trabaje bien).

| Gráfico | Ve scope creep | Mejor para |
|---|---|---|
| Burndown | No (oculto) | Seguimiento diario de sprint |
| Burnup | Sí (explícito) | Tracking de release multi-sprint |

---

## 3. Métricas de flujo

Las métricas de flujo vienen del mundo **Lean/Kanban** (ver [[04-kanban-y-lean]]). Tratan el trabajo como partículas que fluyen por un sistema, igual que analizar un proceso de fabricación.

### Lead Time (tiempo de entrega)

**Desde que el cliente/usuario pide algo hasta que lo recibe.**

Incluye tiempo de espera en backlog, tiempo de desarrollo, revisión, QA, despliegue. Es la métrica que más le importa al usuario final.

```
Lead Time = tiempo desde "tarea creada" hasta "en producción"
```

### Cycle Time (tiempo de ciclo)

**Desde que el equipo *empieza* a trabajar en algo hasta que está en producción.**

```
Cycle Time = tiempo desde "en progreso" hasta "hecho"
Lead Time = tiempo de espera + Cycle Time
```

Si el cycle time es bajo pero el lead time es alto, el cuello de botella está en la cola (backlog, priorización), no en el desarrollo.

### Throughput (rendimiento)

**Número de ítems completados por unidad de tiempo** (por semana, por sprint).

No confundir con velocity (que usa puntos). Throughput cuenta *ítems*, independientemente de su tamaño. Más útil cuando las historias están bien desglosadas y son de tamaño similar.

### Diagrama de Flujo Acumulado (CFD — Cumulative Flow Diagram)

Muestra cuántos ítems hay en cada columna del tablero (Backlog → En progreso → En revisión → Hecho) a lo largo del tiempo. Cada banda es una columna.

```
Ítems
│         Hecho ████████████
│      Revisión ████
│  En progreso  ████
│      Backlog  ████████████████
└────────────────────── tiempo
```

Lo que buscas:
- Bandas delgadas y estables → flujo sano.
- Banda que engrosa rápido → cuello de botella en esa columna.
- "Revisión" que crece sin parar → los devs producen más de lo que QA puede revisar.

---

## 4. Las 4 métricas DORA

DORA (DevOps Research and Assessment) es un programa de investigación de Google que estudió miles de equipos de software durante años. Encontró que **4 métricas predicen el rendimiento organizacional** (velocidad + estabilidad). No son opiniones, son resultado empírico.

| Métrica | Pregunta que responde | Unidad típica |
|---|---|---|
| **Deployment Frequency** | ¿Con qué frecuencia desplegamos a producción? | Veces/día, semana, mes |
| **Lead Time for Changes** | ¿Cuánto tarda un commit en llegar a producción? | Horas, días |
| **MTTR** (Mean Time to Restore) | ¿Cuánto tardamos en recuperarnos de un fallo? | Minutos, horas |
| **Change Failure Rate** | ¿Qué % de despliegues causan incidentes? | % |

### Niveles de rendimiento DORA (referencia 2023)

| Nivel | Deploy Freq | Lead Time | MTTR | Failure Rate |
|---|---|---|---|---|
| Elite | Múltiples/día | < 1 hora | < 1 hora | < 5% |
| High | 1/día – 1/semana | 1 día – 1 semana | < 1 día | 5–10% |
| Medium | 1/semana – 1/mes | 1 semana – 1 mes | 1 día – 1 semana | 10–15% |
| Low | < 1/mes | > 1 mes | > 1 semana | > 15% |

**Por qué importan las 4 juntas**: un equipo puede desplegar mucho (frecuencia alta) pero romperse todo el tiempo (failure rate alto). O puede tener failure rate bajo porque casi nunca despliega (baja frecuencia). Las 4 en conjunto distinguen velocidad real de velocidad aparente.

> DORA refuta el mito de que velocidad y estabilidad son opuestas: los equipos elite tienen ambas altas simultáneamente. La clave está en [[08-devops-y-cicd]] (CI/CD, testing automatizado, trunk-based development).

---

## 5. OKRs vs KPIs

Dos sistemas para definir y medir éxito. Se confunden mucho; sirven para cosas distintas.

### KPIs (Key Performance Indicators)

Indicadores clave de rendimiento. Miden si el negocio/sistema *funciona con normalidad*. Son **métricas de salud continua**, no de ambición.

Ejemplos: uptime del servicio, tiempo de respuesta de API, NPS (Net Promoter Score — índice de satisfacción de clientes), coste por transacción.

- No cambian mucho trimestre a trimestre.
- Una caída en un KPI es una alarma, no un objetivo.

### OKRs (Objectives and Key Results)

**Objetivo**: dirección cualitativa ambiciosa. ¿A dónde queremos ir?
**Key Results**: métricas cuantificables que prueban que llegamos.

```
Objetivo: Hacer que nuestros usuarios confíen en la plataforma de producto.
  KR1: Reducir el tiempo de carga de la pantalla principal de 3 s a < 1 s.
  KR2: Aumentar el porcentaje de usuarios que completan su perfil de 40% a 70%.
  KR3: Alcanzar NPS > 50.
```

- Los OKRs son **temporales** (trimestrales o anuales).
- Diseñados para ser ambiciosos: 70% de cumplimiento se considera éxito. Si siempre llegas al 100%, no eran suficientemente ambiciosos.
- Alinean equipo con estrategia: cada KR conecta trabajo diario con el objetivo.

| Dimensión | KPI | OKR |
|---|---|---|
| Horizonte | Continuo | Trimestral / anual |
| Propósito | Salud operativa | Dirección estratégica |
| Reacción a fallo | Alarma / acción correctiva | Revisión de prioridades |
| Ambición | Mantener nivel | Crecer / cambiar |
| Ejemplo | Uptime > 99.9% | Doblar retención de usuarios en Q3 |

> Los mejores equipos usan ambos: KPIs para no romperse, OKRs para saber a dónde ir.

---

## Anti-patrones clásicos

### Comparar velocity entre equipos

La velocity es **interna y relativa**. Dos equipos que usan la misma escala de puntos pueden calibrar "3 puntos" de forma completamente distinta. Comparar velocity entre equipos es como comparar precios en monedas distintas sin tipo de cambio. Solo conduce a inflación de estimaciones para quedar bien.

**Regla**: la velocity de un equipo solo se compara consigo misma en el tiempo.

### Usar métricas como látigo (metrics as a whip)

Cuando los managers usan la velocity, el cycle time o las DORA para presionar o evaluar el desempeño individual, los equipos aprenden a optimizar la métrica, no el resultado.

- Velocity alta → historias infladas o "done" sin criterios de aceptación reales.
- Deployment frequency alta → deploys vacíos o de features flags.
- MTTR bajo → incidentes declarados resueltos antes de estar realmente arreglados.

**Principio de Goodhart**: *cuando una medida se convierte en objetivo, deja de ser una buena medida.*

Las métricas son diagnóstico, no juicio. Sirven para que el equipo tome mejores decisiones, no para que el jefe reparta culpas.

---

## Cuándo usar cada métrica

| Situación | Métrica útil |
|---|---|
| Planificar sprint | Capacity + Velocity |
| Pronosticar fecha de entrega | Velocity + Burnup |
| Detectar bloqueos en el día a día | Burndown + CFD |
| Identificar cuello de botella en el proceso | Cycle Time + CFD |
| Medir madurez de DevOps | DORA |
| Alinear equipo con estrategia | OKRs |
| Monitorizar salud del producto | KPIs |

---

## Aplícalo a tus proyectos

**app web (FastAPI + React + Docker)**:
- Empieza por las **métricas DORA** más simples: mide cuánto tarda un commit tuyo en llegar a Docker Hub / servidor desplegado (Lead Time for Changes). Con un pipeline de CI/CD básico en [[08-devops-y-cicd]] puedes tenerlo medido desde el día 1.
- Define 1–2 **KPIs de producto**: tiempo de respuesta de `/api/meals` (p95), % de usuarios que completan el onboarding de perfil del producto.
- Si usas GitHub Projects o un tablero Kanban, activa el registro de fechas de inicio/fin para calcular **Cycle Time** por historia aunque sea manualmente al principio.
- Para el backlog del proyecto, un **Burnup** te da más información que un Burndown porque a medida que defines nuevas historias el scope sube; el Burnup lo hace visible.

**Proyectos hardware/técnico con firmware**:
- Las métricas DORA aplican igual: ¿con qué frecuencia flasheas firmware al prototipo?, ¿cuánto tarda un fix de bug en llegar al dispositivo?
- Change Failure Rate es especialmente útil: ¿qué % de tus flashes rompen algo en el banco de pruebas?

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[03-scrum]]
- [[04-kanban-y-lean]]
- [[05-historias-de-usuario-y-backlog]]
- [[08-devops-y-cicd]]
- [[10-producto-y-priorizacion]]
- [[11-equipo-retros-y-antipatrones]]
