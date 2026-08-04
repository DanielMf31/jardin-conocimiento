---
title: Herramientas y Certificaciones Agile
date: 2026-06-13
tags: [programacion/agile, programacion/herramientas, programacion/gestion-proyectos]
type: nota
status: en-progreso
source: claude-code
aliases: [herramientas agile, certificaciones scrum, jira trello linear]
---

# Herramientas y Certificaciones Agile

## ¿Por qué importa esto?

Conocer Scrum o Kanban en teoría no es suficiente: en la práctica real, los equipos usan **tableros digitales** para hacer visible el trabajo, y algunos profesionales buscan **certificaciones** para validar ese conocimiento ante empleadores o clientes.

Este documento responde dos preguntas prácticas:
1. ¿Qué herramienta uso para gestionar mi proyecto?
2. ¿Vale la pena certificarme, y en qué?

Ambas son ortogonales: puedes usar Jira sin certificarte, y puedes tener PSM I sin haber tocado Jira en tu vida.

---

## Herramientas de gestión de proyectos

### El problema que resuelven

Sin herramienta, el backlog vive en un Excel, los sprints se acuerdan de palabra, y el "tablero Kanban" es post-its que alguien tiró. Las herramientas digitales centralizan:
- **Ítems de trabajo** (issues, tickets, tareas)
- **Flujos** (columnas Kanban o sprints Scrum)
- **Trazabilidad** (quién hizo qué, cuándo, por qué)
- **Métricas** automáticas (burndown, cycle time, throughput)

### Las cinco herramientas principales

| Herramienta | Empresa | Modelo | Para qué brilla | Para qué no es ideal |
|---|---|---|---|---|
| **Jira** | Atlassian | Freemium / SaaS | Equipos de software medianos-grandes, flujos complejos, integración CI/CD, métricas avanzadas | Proyectos personales o equipos <5 (demasiado overhead) |
| **Trello** | Atlassian | Freemium / SaaS | Tableros Kanban visuales simples, proyectos no técnicos, usuarios no técnicos | Scrum real (sprints, velocity, backlog refinado): no tiene soporte nativo |
| **Linear** | Linear Inc. | Freemium / SaaS | Equipos de ingeniería modernos, velocidad de UI, ciclos (≈sprints) + proyectos | Organizaciones enterprise con flujos muy customizados |
| **GitHub Projects** | GitHub | Gratuito (incluido en GitHub) | Equipos que ya usan GitHub: issues y PRs como ítems de trabajo sin cambiar de plataforma | Sin funciones avanzadas de Scrum; métricas limitadas |
| **Azure DevOps (Boards)** | Microsoft | Freemium / Enterprise | Entornos Microsoft/.NET, empresas que ya pagan Azure, integración pipelines CI/CD propios | Overhead enorme para proyectos pequeños o equipos sin stack Microsoft |

### Cuándo usar cuál

```
¿Proyecto personal o side project?
  → GitHub Projects (ya tienes el repo) o Trello (si no es software puro)

¿Startup / equipo pequeño de ingeniería (<20 personas)?
  → Linear (rápido, moderno, barato) o Jira Cloud free

¿Empresa mediana/grande con procesos Scrum formales?
  → Jira (el estándar de facto en la industria)

¿Stack Microsoft / Azure?
  → Azure DevOps Boards (todo integrado)

¿Necesitas explicarlo a stakeholders no técnicos?
  → Trello o GitHub Projects (bajo ruido visual)
```

### Jira en detalle (es el que más verás en ofertas de trabajo)

**Conceptos clave** (jerga que aparecerá en entrevistas y onboarding):

- **Project**: agrupación de ítems. Puede tener board Scrum o Kanban.
- **Issue**: unidad de trabajo. Tipos: Epic > Story > Task > Subtask / Bug.
- **Epic**: contenedor grande (ej. "Módulo de autenticación"). Suele abarcar varios sprints.
- **Sprint**: bloque de tiempo fijo (1-4 semanas) con un subconjunto del backlog comprometido.
- **Board**: vista visual del sprint activo en columnas (To Do / In Progress / Done).
- **Backlog view**: lista ordenada de todo lo pendiente, fuera del sprint.
- **JQL** (Jira Query Language): lenguaje de filtros tipo SQL para buscar issues. Ej: `project = "APP" AND sprint in openSprints() AND assignee = currentUser()`.

> Nota para contexto hardware: piensa en un "issue" como una tarea en un Gantt de PLC, pero viva y trazable en vez de estática.

---

## Certificaciones Agile

### El ecosistema de certificaciones (panorama)

Hay cuatro organismos principales que emiten certificaciones Agile/Scrum. No son equivalentes — apuntan a perfiles y objetivos distintos:

| Organismo | Filosofía | Tipo de examen |
|---|---|---|
| **Scrum.org** | Rigor técnico, sin membresía obligatoria, libre | Online, sin supervisión presencial |
| **Scrum Alliance** | Comunidad + formación obligatoria (curso antes de certificar) | Online supervisado |
| **SAFe (Scaled Agile)** | Agile a escala empresarial (SAFe framework) | Online supervisado, requiere formación |
| **PMI** | Project Management estándar + Agile | Online supervisado, requiere experiencia acreditada |

---

### Scrum.org — PSM I / PSM II / PSPO

**PSM I** (Professional Scrum Master I) es la certificación con mejor ratio coste/valor para empezar.

| Dato | Detalle |
|---|---|
| Coste | ~150 USD (precio oficial 2025) |
| Requisito previo | Ninguno — solo pagar y hacer el examen |
| Formato | 80 preguntas, 60 minutos, multiple-choice |
| Nota mínima | 85% para aprobar |
| Caducidad | No caduca (diferencia clave vs Scrum Alliance) |
| Material oficial | Scrum Guide (gratuito en scrumguides.org) + Open Assessments en scrum.org |

**Cómo preparar PSM I** (ruta probada):
1. Lee el **Scrum Guide 2020** completo (20 páginas). Léelo 2-3 veces, no una.
2. Haz el **Scrum Open** (assessment gratuito en scrum.org) hasta sacar >95% de forma consistente.
3. Haz el **Product Owner Open** y el **Developer Open** (también gratis) — salen preguntas de esos roles.
4. Practica con simuladores de pago opcionales: Mikhail Lapshin, ExamTopics, MLapshin.com.
5. Cuando superes 90% estable en varios simulacros → presenta el examen real.

**PSM II** — nivel avanzado. Preguntas abiertas (ensayo). Útil solo si vas a ser Scrum Master profesional o coach. ~250 USD.

**PSPO I/II** — equivalente pero centrado en el rol de **Product Owner** (el que gestiona el backlog y prioriza). Misma estructura que PSM I.

---

### Scrum Alliance — CSM (Certified Scrum Master)

| Dato | Detalle |
|---|---|
| Coste | ~400-1000 USD (incluye curso obligatorio de 2 días con trainer certificado) |
| Requisito previo | Curso presencial/virtual de 16 h con Certified Scrum Trainer (CST) |
| Formato | 50 preguntas, online, sin tiempo límite estricto |
| Nota mínima | 74% |
| Caducidad | **Caduca a los 2 años** — requiere renovación con SEUs (créditos de educación) |

**¿Vale la pena vs PSM I?** Para la mayoría: no, a no ser que el empleador lo exija específicamente. El PSM I tiene mayor rigor técnico y no caduca. El CSM tiene más reconocimiento en sectores no-tech (banca, consultoría clásica).

---

### SAFe — SA / SSM

**SAFe** (Scaled Agile Framework) es un framework para aplicar Agile en organizaciones grandes (>50 personas en múltiples equipos). Tiene su propio vocabulario: ARTs (Agile Release Trains), PI Planning, etc.

| Certificación | Para quién |
|---|---|
| **SA** (SAFe Agilist) | Líderes y managers que quieren entender SAFe |
| **SSM** (SAFe Scrum Master) | Scrum Masters que operan dentro de un ART |

| Dato | Detalle |
|---|---|
| Coste | ~995 USD (incluye curso de 2 días) |
| Caducidad | Caduca al año — renovación de pago |
| Relevancia | Alta en grandes corporaciones (Telefónica, BBVA, empresas Fortune 500) |

> Para proyectos personales o startups: SAFe es excesivo. Solo lo necesitas si trabajas en una empresa que ya lo usa o apunta a ese mercado.

---

### PMI — PMI-ACP y PMP

**PMI-ACP** (Agile Certified Practitioner): híbrido entre gestión de proyectos clásica y Agile. Exige experiencia acreditada (2.000 h en proyectos Agile) y educación formal (21 h de formación Agile).

**PMP** (Project Management Professional): la certificación de gestión de proyectos más reconocida globalmente. Desde 2021 incluye ~50% de contenido Agile. Exige 36 meses de experiencia liderando proyectos + 35 h de formación.

| Dato | PMI-ACP | PMP |
|---|---|---|
| Coste (PMI member) | ~435 USD | ~405 USD |
| Coste (no-member) | ~495 USD | ~555 USD |
| Experiencia requerida | 2.000 h en Agile | 36 meses liderando proyectos |
| Caducidad | 3 años (PDUs para renovar) | 3 años (PDUs para renovar) |
| Perfil objetivo | Practicantes Agile con experiencia | Project Managers en general |

> Para alguien saliendo de técnico al software: el PMP es overkill al inicio. Empieza con PSM I; considera PMP si en 3-5 años quieres gestionar proyectos de forma formal.

---

### Tabla comparativa global de certificaciones

| Certificación | Dificultad | Coste aprox. | Caduca | Mejor para |
|---|---|---|---|---|
| PSM I (Scrum.org) | Media | ~150 USD | No | Ingenieros que quieren base Scrum sólida, máximo ROI |
| PSPO I (Scrum.org) | Media | ~200 USD | No | Quienes apuntan a rol de Product Owner |
| CSM (Scrum Alliance) | Baja-Media | ~400-1000 USD | 2 años | Roles no-tech, empresas que la exigen |
| PSM II (Scrum.org) | Alta | ~250 USD | No | Scrum Masters / coaches profesionales |
| SAFe SA/SSM | Media | ~995 USD | 1 año | Grandes corporaciones con SAFe implantado |
| PMI-ACP | Alta | ~495 USD | 3 años | PMs con experiencia Agile real acreditada |
| PMP | Muy alta | ~555 USD | 3 años | Project Managers senior con amplia experiencia |

---

## Errores comunes

- **Estudiar solo el Scrum Guide para el PSM I sin hacer simulacros**: el examen tiene preguntas de aplicación en contexto, no solo definiciones. Los Open Assessments de scrum.org son los más parecidos al examen real.
- **Elegir CSM por ser "más fácil"**: es más cara, caduca, y en entornos técnicos tiene menos peso que PSM I.
- **Certificarse en SAFe sin entender Scrum base**: SAFe asume que ya sabes Scrum; sin esa base, te pierdes en el vocabulario.
- **Confundir herramienta con proceso**: usar Jira no te hace Agile. Jira mal configurado puede replicar todos los vicios del waterfall (tickets infinitos sin prioridad, sprints que nunca se cierran, etc.).
- **No renovar certificaciones caducas**: CSM, SAFe y PMI requieren PDUs/SEUs. Si no los acumulas, la certificación expira y tienes que repetirla o pagar la renovación.

---

## Aplícalo a tus proyectos

### app web (React + FastAPI + Docker)

- **Herramienta recomendada**: **GitHub Projects** — ya tienes el repo, puedes convertir issues en ítems del tablero sin coste adicional.
- Crea un tablero Kanban simple: `Backlog | In Progress | In Review | Done`.
- Agrupa issues por épica (ej. "Módulo de autenticación", "Tracking Na/K", "Dashboard").
- Si quieres practicar Scrum de verdad: define sprints de 1 semana en GitHub Projects y mide tu velocity (issues completados por sprint).

### proyecto embebido (PlatformIO / Hardware)

- Los proyectos hardware tienen ciclos más largos y menos paralelismo que software puro → **Trello o GitHub Projects en modo Kanban** encaja mejor que Scrum.
- Columnas útiles: `Ideas | Diseño | Prototipo | Test | Integrado`.

### Certificación recomendada para tu perfil actual

Dado tu perfil (técnico → Software, aprendiendo proceso Agile):

1. **Empieza con PSM I**: inversión mínima (~150 USD), preparación autodidacta con recursos gratuitos (Scrum Guide + Open Assessments), no caduca.
2. Si en el futuro gestionas equipos o apuntas a Product Manager → **PSPO I**.
3. Si acabas en una empresa grande con SAFe → haz el SAFe cuando sea relevante, no antes.

**Plan de estudio PSM I** (4-6 semanas a 30 min/día):
- Semanas 1-2: leer Scrum Guide (3 veces), tomar notas en esta bóveda.
- Semanas 3-4: Scrum Open diario hasta >95% estable.
- Semana 5: Product Owner Open + Developer Open.
- Semana 6: simulador de pago opcional → presentar examen.

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[01-sdlc-e-historia]]
- [[02-manifiesto-agil]]
- [[03-scrum]]
- [[04-kanban-y-lean]]
- [[05-historias-de-usuario-y-backlog]]
- [[08-devops-y-cicd]]
- [[09-metricas-y-seguimiento]]
- [[11-equipo-retros-y-antipatrones]]
