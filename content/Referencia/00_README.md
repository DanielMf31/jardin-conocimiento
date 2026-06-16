# Referencia — docs generales transversales de programación

> 📚 **Catálogos y referencias de patrones, archetypes y conceptos** que NO pertenecen a un proyecto específico sino que aplican transversalmente a cualquier proyecto backend/sistemas que construyas.

## Propósito

Esta carpeta es el **lookup** de conceptos y patrones que reconoces en TODOS los proyectos. Reduce la duplicación: en lugar de explicar "qué es un handler" en cada proyecto, lo explicas UNA vez aquí y los proyectos linkean a esta referencia.

Pensada para crecer con el tiempo según vayas reconociendo más patrones automáticamente (transición Dreyfus Competent → Proficient — ver).

## Convención

- **Filename**: kebab-case descriptivo
- **Frontmatter**: `type: nota`, `status: permanente`, tags `programacion/referencia/*`
- **Estructura interna**: schema → patterns → ejemplos concretos de tus proyectos

## Contenido actual

| Archivo | Tema | Para qué |
|---|---|---|
| [[archetipos-funciones-backend]] | Catálogo de ~20 archetypes de funciones (handler, validator, getter, transformer, etc.) con cómo identificarlos en código | Reconocer chunks de capa 1 al leer cualquier codebase |
| [[sql-y-bases-de-datos-fundamentos]] | Teoría SQL + DB relacional necesaria para proyectos backend (con ejemplos de Booking) — JOINs, constraints, indexes, normalization, transactions+ACID, ORM↔SQL, EXPLAIN | Entender qué hace tu ORM por debajo + diagnosticar queries lentas + diseñar schemas correctos |
| [[debugging-python-fastapi-sqlalchemy]] | Workflow profesional debugging — ruff, mypy, pyright, Pylance, smoke test, pdb, common error decoder, Docker logs efectivos, psql shortcuts, anti-patterns | Reemplazar ciclo doloroso edit→restart→logs por workflow rápido con feedback inmediato. Atrapar 50% bugs ANTES de levantar Docker |
| [[glosario-programacion]] | Glosario propio en 3 partes: P1 Booking alfabético (97 + 21 sub-variantes), P2 CS Fundamentos por área (10 áreas), P3 Telemetría por subsistema (91). Definición corta + **relaciones tipadas** + enlace al doc que lo explica a fondo, no duplica | Poder **definir y relacionar** conceptos que sabes usar pero no articular (API, BD, async, JWT, Kafka…) |

## Posibles futuros docs (a crear cuando los necesites)

- `naming-conventions.md` — patrones de nombrado (snake_case en Python, getXxx vs xxx, is/has/can prefix, etc.)
- `error-handling-patterns.md` — try/except patterns, error types, when to wrap
- `api-design-checklist.md` — REST vs RPC, idempotency, versioning, pagination
- `database-anti-patterns.md` — N+1, table scans, missing indexes, premature denormalization
- `concurrency-patterns.md` — async vs threads vs procesos, locks, channels, queues
- `observability-checklist.md` — RED metrics, structured logs, tracing, health endpoints

## Cómo usar

1. Cuando estés leyendo código de cualquier proyecto y veas algo que reconoces como pattern conocido → consulta esta carpeta
2. Cuando aprendas un pattern nuevo en un proyecto que se va a repetir en otros → considera promoverlo aquí
3. Linkea desde docs específicos de proyectos: `Ver [[archetipos-funciones-backend]] para clasificación`

## Conexiones

- [[MOC_Programacion]] — área padre
- — la metodología de chunking que justifica esta carpeta
