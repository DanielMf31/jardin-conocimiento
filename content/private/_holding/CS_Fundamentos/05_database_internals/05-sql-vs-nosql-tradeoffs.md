# 05 — SQL vs NoSQL — tradeoffs

> **Doc 5 (último) del cluster Database Internals**. La decisión que marca arquitectura: relacional o no, y dentro de no-relacional, qué tipo. Sin religión, con criterios.
> **Frecuencia interview**: aparece en system design siempre. "Qué BD usas y por qué" es respuesta crítica.
> **Tiempo de lectura estimado**: 35-50 min.

---

## 1. Por qué la dicotomía es falsa (parcialmente)

"SQL vs NoSQL" se popularizó hace 15 años cuando los unicornios necesitaban escalar más allá de lo que las DBs relacionales clásicas permitían. La narrativa: "SQL = viejo y no escala, NoSQL = nuevo y escala".

Hoy esa narrativa está **muy obsoleta**:

- **PostgreSQL moderno** escala a millones de queries/s con tuning.
- **MySQL Vitess** (YouTube) es sharded a escala absurda.
- **DynamoDB y MongoDB** ahora tienen transacciones ACID.
- **CockroachDB / Spanner** son SQL distribuido con strong consistency.

La dicotomía real moderna no es "SQL vs NoSQL". Es:

- **Modelo de datos**: relacional vs documento vs key-value vs columnar vs grafo.
- **Garantías de consistencia**: ACID strict vs eventual configurable.
- **Modelo de query**: SQL vs API custom vs MapReduce.
- **Escalado**: vertical (1 nodo grande) vs horizontal (N nodos).

Cada decisión es ortogonal a las otras. Una BD moderna puede ser "relacional + ACID + SQL + escalado horizontal" (CockroachDB) o "documento + eventual + API custom + escalado horizontal" (DynamoDB).

---

## 2. Los 5 modelos de datos principales

### Relacional (SQL)

Datos en **tablas** con filas y columnas. Schema fijo. Relaciones via foreign keys. Queries con SQL.

**Cuándo encaja**:
- Datos con relaciones complejas (joins frecuentes).
- Necesidad de garantías ACID.
- Schema bien definido y estable.
- Reportes y analytics ad-hoc (SQL es rey aquí).

**Ejemplos**: PostgreSQL, MySQL, SQL Server, Oracle, SQLite, CockroachDB, Spanner.

### Documento

Datos como **documentos JSON/BSON** anidados. Schema flexible (cada doc puede ser distinto). Sin joins (típicamente).

**Cuándo encaja**:
- Datos con estructura jerárquica natural (productos con variantes, perfiles con preferencias).
- Schema cambia frecuentemente (early stage startups).
- Lecturas dominantes de "objetos completos" (no joins).

**Ejemplos**: MongoDB, CouchDB, Amazon DocumentDB, Firestore.

### Key-Value

El más simple. **Solo lookup por key → value**. Value puede ser bytes opacos o estructura simple.

**Cuándo encaja**:
- Caches.
- Sessions.
- Counters / contadores.
- Datos donde solo lookup por ID importa.

**Ejemplos**: Redis (key-value con tipos ricos), DynamoDB (modo key-value), Memcached, etcd.

### Columnar (wide-column)

Datos organizados por columnas en vez de filas. **Muy bueno para queries analíticos** que escanean millones de filas pero pocas columnas.

**Cuándo encaja**:
- Data warehousing.
- Time-series.
- Analytics OLAP.

**Ejemplos**: Cassandra, HBase, Bigtable, ScyllaDB, ClickHouse, BigQuery, Redshift.

### Grafo

Datos como **nodos y aristas**. Optimizado para queries de relaciones (amigos de amigos, shortest path).

**Cuándo encaja**:
- Redes sociales.
- Recomendaciones basadas en grafos.
- Detección de fraude (patrones).
- Knowledge graphs.

**Ejemplos**: Neo4j, Amazon Neptune, ArangoDB, JanusGraph.

---

## 3. SQL vs NoSQL — los trade-offs reales

### Schema flexible vs strict

**SQL**: schema fijo. Cambios requieren migrations (ALTER TABLE). Postgres añadió `JSONB` que permite columnas flexibles dentro de schema fijo (lo mejor de ambos mundos en muchos casos).

**NoSQL documento**: schema-less. Cada doc puede ser distinto. Cambios sin migration.

**Trade-off real**:
- Schema strict = bugs de tipo se atrapan en write time. Datos siempre consistentes.
- Schema flexible = bugs llegan a producción silenciosos. Pero iteración rápida en early stage.

**Patrón moderno**: SQL con JSONB para campos cambiantes. Lo mejor de ambos.

### Joins vs denormalization

**SQL**: joins son nativos y eficientes. Normalizas datos sin penalización.

**NoSQL documento**: joins pobres o inexistentes. Tienes que denormalizar (duplicar datos) o hacer múltiples queries y juntar en app.

**Trade-off**:
- Normalización: menos espacio, sin duplicación. Joins en cada query.
- Denormalización: más espacio, datos duplicados. Lecturas más rápidas.

Para apps **read-heavy** con queries predecibles, denormalizar puede ser ganancia. Para apps **write-heavy** con relaciones complejas, normalización es mejor.

### ACID vs eventual

**SQL clásico**: ACID estricto. Single-node típicamente.

**NoSQL clásico (2010s)**: eventual consistency, BASE. Para escalar.

**Realidad moderna**: muchas NoSQL ahora soportan transacciones ACID (DynamoDB, MongoDB, FoundationDB). Y muchos SQL distribuidos mantienen ACID a escala (CockroachDB, Spanner).

La elección hoy es **por dato/operación**, no por "SQL o NoSQL".

### Escalado vertical vs horizontal

**SQL clásico**: vertical (servidor más grande). Tope ~1 TB RAM, costoso.

**NoSQL**: horizontal (N nodos). Escala "infinitamente".

**Hoy**: SQL también escala horizontal con sharding (Vitess, Citus, CockroachDB). La diferencia se diluye.

### SQL como lenguaje

**SQL**: declarativo, expresivo, maduro (50 años). Universal — todo developer SQL puede usar tu DB. Reportes ad-hoc trivial.

**NoSQL**: APIs específicas por DB. Más rígidas. Reportes ad-hoc pobre.

**Punto a favor de SQL**: el lenguaje es activo enorme. Aprenderlo paga durante toda tu carrera. Cada NoSQL nueva tiene su API que olvidarás en 5 años cuando pase de moda.

---

## 4. Cuándo elegir cada uno

### Elige SQL (Postgres por defecto) cuando

- **No estás seguro qué DB necesitas**. Postgres es la elección por defecto razonable hoy.
- **Tienes relaciones complejas** entre entidades.
- **Necesitas ACID estricto**.
- **Quieres reports ad-hoc** y flexibilidad de queries.
- **Tu equipo conoce SQL** (la mayoría lo conoce).
- **Tu volumen es razonable** (millones a decenas de millones de filas, no necesitas escalar a TBs).

### Elige documento (MongoDB) cuando

- Datos con **estructura jerárquica natural**.
- Schema **cambia frecuentemente** (MVP, early stage).
- Queries son típicamente "dame el objeto completo" sin joins.
- Tu equipo no quiere lidiar con migrations.

### Elige key-value (Redis) cuando

- **Cache** (use case #1).
- **Sessions** efímeras.
- **Counters atómicos** y operaciones simples.
- Necesitas **latencia sub-ms**.

### Elige wide-column (Cassandra) cuando

- **Time-series** (logs, métricas, events).
- **Write-heavy** masivo.
- Queries predecibles (no ad-hoc).
- Multi-region active-active.

### Elige grafo (Neo4j) cuando

- Queries son **traversals** de relaciones (friends of friends).
- Algoritmos de grafos son core (recomendaciones, fraude).

### Elige analytics OLAP (BigQuery, Snowflake, ClickHouse) cuando

- Data warehouse / data lake.
- Queries analíticos sobre TBs de datos históricos.
- No transactional workload.

---

## 5. Postgres como elección por defecto moderna

Si tuviera que recomendar una sola BD para 80% de proyectos nuevos en 2026: **Postgres**.

Razones:

- Madura (1996), estable, sin bugs raros.
- Escala vertical hasta donde la mayoría necesita.
- ACID estricto.
- SQL completo + extensiones (PostGIS para geo, pgvector para embeddings, TimescaleDB para time-series, Citus para sharding).
- JSONB para flexibilidad documento-style cuando hace falta.
- Full-text search built-in.
- Open source, sin vendor lock-in.
- Comunidad enorme.

**Cuándo NO Postgres**:
- Necesitas escalado horizontal extremo desde día 1 (raro).
- Workload write-heavy especializada (time-series → TimescaleDB o ClickHouse).
- Latencia sub-ms required (Redis).

Postgres + Redis cubre el 90% de stacks modernas razonables.

---

## 6. Polyglot persistence — usar varias

Las apps reales suelen usar **varias DBs según necesidad**. Ejemplo típico:

- **Postgres**: datos transaccionales (usuarios, órdenes, productos).
- **Redis**: cache + sessions + counters + colas simples.
- **Elasticsearch / Meilisearch**: full-text search complejo.
- **S3**: blobs grandes (imágenes, vídeos, PDFs).
- **ClickHouse / BigQuery**: analytics y data warehouse.
- **DynamoDB / Cassandra**: si necesitas escalado horizontal específico.

Cada herramienta para lo que es buena. **Anti-pattern**: usar una sola DB para todo y forzarla a casos para los que no es buena.

**Caveat**: cada DB extra es complejidad operativa. Empieza con menos, añade cuando duela.

---

## 7. NewSQL — la fusión moderna

**NewSQL** = bases que combinan SQL + escalado horizontal + ACID distribuido. Lo mejor de ambos mundos.

Ejemplos:
- **Spanner** (Google): el original, requiere infraestructura propietaria (TrueTime).
- **CockroachDB**: open source, inspirado en Spanner. Postgres-compatible.
- **TiDB**: MySQL-compatible. Usado en China masivamente.
- **YugabyteDB**: Postgres-compatible.
- **PlanetScale**: MySQL serverless basado en Vitess.

**Por qué importa**: para sistemas que necesitan SQL + escalar a millones de transactions, antes solo había workarounds. Ahora hay opciones reales.

**Caveat**: no es magia. Tienen latencias mayores que Postgres single-node (consensus por write). Útiles cuando realmente necesitas su escala.

---

## 8. Cuándo NO migrar a NoSQL

Casos típicos donde la gente migra a NoSQL pensando que va a "escalar" y termina arrepentida:

1. **Tu DB SQL es lenta y crees que NoSQL la salvará**. Probablemente no falta tunear queries / añadir índices / leer EXPLAIN. Migrar a NoSQL no arregla queries mal escritas.

2. **Tu schema cambia frecuentemente y crees que NoSQL es la solución**. Postgres con JSONB cubre eso casi siempre. Mejor que abandonar todas las garantías ACID.

3. **Necesitas escalar reads y crees que necesitas Cassandra**. Read replicas Postgres es más simple y suele bastar.

4. **Te dijeron en una conferencia que MongoDB es web-scale**. MongoDB es buena BD para casos específicos. No reemplaza Postgres genérico.

**Migración SQL → NoSQL** es decisión grande. Si no tienes razón muy concreta y medida, no migrar.

---

## 9. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Hoy: JSON. Mañana: Postgres. Razones:
- Datos relacionales (contactos pueden tener tags, historial de cambios).
- ACID útil para no perder datos.
- SQL te permite reportes ad-hoc.
- Postgres sobrevivirá tu carrera.

NoSQL aquí sería overkill y peor experiencia.

### En entrevistas tecnicas

**Pregunta clásica**: "Qué BD elegirías para X y por qué".

Tu respuesta debe articular:
1. Modelo de datos (relacional, documento, KV, columnar, graph).
2. Garantías necesarias (ACID, eventual).
3. Patrones de query (point lookup, range, full-text, analytics).
4. Volumen y escala esperados.
5. Operación (managed vs self-hosted, equipo).

**Pregunta sobre polyglot**: "Diseña stack de DBs para Twitter".

- Postgres: usuarios, settings, datos transaccionales.
- Cassandra: tweets (write-heavy, time-series).
- Redis: timelines en memoria, counters.
- Elasticsearch: search.
- S3: media.
- BigQuery / Snowflake: analytics.

**Pregunta sobre cuándo NoSQL**: "Caso de uso para MongoDB sobre Postgres".

Schema realmente flexible que cambia cada semana en early MVP, datos jerárquicos profundos sin necesidad de joins, equipo más cómodo con JSON que SQL. Pero para producción seria, Postgres+JSONB suele ser mejor.

---

## 10. Trampas típicas

**"NoSQL escala mejor que SQL"**: simplificación. SQL distribuido moderno (CockroachDB, Spanner) escala. Y NoSQL tiene sus propios problemas a escala.

**"MongoDB es como Postgres pero flexible"**: no, son modelos distintos. MongoDB sin joins, sin ACID en operaciones cross-doc por defecto (hasta 4.0).

**"Redis es una DB"**: es key-value en RAM. Sirve para cache, queues, sessions. NO para "almacenar datos críticos" sin replicación + persistencia bien configurada.

**"Cassandra para todo write-heavy"**: solo si tus queries son simples (point lookup por partition key). Range queries cross-partition son anti-pattern.

**"NewSQL es estrictamente mejor"**: tiene latencia mayor que Postgres single-node por consensus. Solo gana cuando realmente necesitas su escala.

**"Polyglot persistence siempre"**: cada BD extra es complejidad operativa. Empieza con una. Añade cuando hay caso real.

**"NoSQL = sin schema"**: tu app tiene schema implícito en el código. Sin schema explícito en DB, los bugs de tipo te muerden en producción.

---

## 11. Preguntas típicas de interview

**Diferencia SQL vs NoSQL**: cubierto en sección 1 (la dicotomía es falsa moderna). Mejor: distinguir por modelo de datos, garantías, query language.

**Cuándo Postgres vs MongoDB**: relacional + ACID + reports → Postgres. Schema cambiante + jerárquico + read-by-id → Mongo.

**Por qué Cassandra es para write-heavy**: arquitectura LSM-tree (writes secuenciales rápidos), partitioning automático, sin coordinación cross-partition.

**Polyglot persistence — tradeoffs**: cada DB para lo que es buena, pero complejidad operativa multiplicada. Empezar simple.

**NewSQL — qué es**: SQL + ACID + escalado horizontal. CockroachDB, Spanner. Mayor latencia por consensus.

**Cuándo NO migrar SQL → NoSQL**: si la causa es queries lentas (tunea), schema cambiante (JSONB), o "escala" sin medir.

---

## 12. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué "SQL vs NoSQL" es dicotomía falsa moderna.
- Los 5 modelos de datos (relacional, documento, KV, columnar, grafo) y casos de uso.
- Postgres como default razonable para 80% de casos.
- Polyglot persistence: cuándo conviene, cuándo es overkill.
- NewSQL (CockroachDB, Spanner): qué resuelve.
- Cuándo NO migrar a NoSQL ("tu SQL es lenta" no es razón).
- Schema flexible vs strict — JSONB es el patrón híbrido moderno.
- Joins vs denormalización — read-heavy puede beneficiar denorm.

Si no puedes → relee.

---

## ¡Cluster Database Internals completado!

Has completado el quinto Tier 1 (último de los críticos). Resumen:

- `01-b-trees-y-indexing` — B+trees, índices, EXPLAIN, optimización.
- `02-acid-transactions` — las 4 garantías, WAL, MVCC.
- `03-isolation-levels` — anomalías, levels, snapshot isolation.
- `04-replication-y-sharding` — escalar reads y writes.
- `05-sql-vs-nosql-tradeoffs` — modelos de datos, cuándo cada uno.

**Tier 1 ENTERO completo**: Networking + OS + Concurrency + System Design + Database Internals = 24 docs.

**Próximo**: cluster 07 (Computer Architecture), 08 (Security), 09 (Compilers).

---

## Conexiones

- [[01-b-trees-y-indexing]] — base de cualquier DB
- [[02-acid-transactions]] — garantías
- [[03-isolation-levels]] — concurrencia en DB
- [[04-replication-y-sharding]] — escalar
- [[../06_distributed_systems/01-cap-pacelc]] — los trade-offs fundamentales
- [[../06_distributed_systems/03-eventual-consistency]] — modelo de muchas NoSQL
- [[../04_system_design_patterns/02-caching-strategies]] — Redis
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Designing Data-Intensive Applications** capítulos 2 (Data Models) y 3 (Storage) — referente moderno.
- **Postgres docs** — el manual más completo de cualquier DB.
- **MongoDB docs**.
- **DynamoDB Single-Table Design** (Alex DeBrie blog) — masterclass de modelado NoSQL.
- **Use The Index, Luke!** (use-the-index-luke.com) — SQL real-world.
- **DB-Engines ranking** (db-engines.com) — popularity y trends.
