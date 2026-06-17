# 01 — B-trees e indexing

> **Doc 1 del cluster Database Internals**. Por qué tu DB es rápida buscando entre millones de filas. La estructura de datos que sostiene todo SQL del mundo.
> **Frecuencia interview**: aparece SIEMPRE en backend interviews. "¿Qué es un índice?", "¿Cuándo añadir un índice?", "¿Por qué B-tree y no hash?".
> **Tiempo de lectura estimado**: 40-55 min.

---

## 1. El problema sin índices

Sin índices, una query como `SELECT * FROM users WHERE email = 'x@y.com'` tiene que **leer la tabla entera** y comparar cada fila. Esto se llama **table scan** o **sequential scan**.

Para 1.000 filas: trivial, milisegundos.
Para 1 millón de filas: 1-2 segundos.
Para 100 millones: imposible. Tu app se rompe.

**Un índice es una estructura auxiliar que la DB mantiene para encontrar filas sin escanear toda la tabla**. Es esencialmente lo mismo que un índice de un libro: en vez de leer página por página buscando "B-tree", vas al índice del final, encuentras "B-tree → página 47" y vas directo.

El coste: el índice ocupa espacio extra y hay que actualizarlo en cada INSERT/UPDATE/DELETE. La ganancia: lookups en milisegundos en lugar de segundos.

---

## 2. Por qué B-trees y no otras estructuras

Hay varias estructuras de datos que permiten lookup rápido. ¿Por qué casi todas las DBs usan B-trees (concretamente B+trees)?

### Hash table

Lookup O(1) promedio. Buenísimo para `WHERE email = 'X'` (igualdad exacta).

**Pero**: no soporta **range queries** (`WHERE age > 30`). El hash es desordenado por construcción. Tampoco soporta **prefix matches** (`WHERE name LIKE 'Juan%'`). Tampoco ordering eficiente (`ORDER BY age`).

DBs que usan hash indexing solo para algunos casos: Postgres (HASH index, raro), Memcached (es key-value puro, no DB).

### Binary search tree balanceado (AVL, Red-Black)

Lookup O(log n), soporta ranges, ordering. Perfecto en RAM.

**Pero**: cada nodo tiene 2 hijos. Para 1B filas, el árbol tiene depth log₂(1B) ≈ 30. Cada nivel = una cache miss en CPU si está en RAM, o una **lectura de disco** si no cabe en RAM. **30 lecturas de disco por query → inviable**.

### B-tree (la solución)

Igual que un BST balanceado pero **cada nodo tiene MUCHOS hijos** (típicamente 100-500). Para 1B filas con 100 hijos por nodo: depth = log₁₀₀(1B) ≈ 5 niveles. **5 lecturas de disco vs 30 del BST**.

La forma del B-tree está **diseñada para ajustarse al tamaño de página del disco** (típicamente 4-16 KB). Cada nodo del B-tree es una página de disco. Una sola lectura trae cientos de keys de golpe. **Aprovecha la localidad del disco al máximo**.

### LSM-tree — la alternativa moderna

**Log-Structured Merge-tree**. En vez de actualizar in-place, escribes secuencialmente a archivos inmutables que se compactan periódicamente. Mucho mejor para **writes** (escrituras secuenciales son rapidísimas), peor para **reads** puntuales (puede tocar varios archivos).

DBs que usan LSM: Cassandra, RocksDB, LevelDB, BigTable, HBase, ScyllaDB, parte de InfluxDB.

DBs que usan B-tree: Postgres, MySQL InnoDB, SQLite, Oracle, SQL Server, MongoDB (WiredTiger).

**Trade-off general**: B-tree mejor para read-heavy + workloads mixtos. LSM-tree mejor para write-heavy.

---

## 3. B+ tree — la variante que realmente se usa

Las DBs no usan **B-tree** original sino **B+ tree** (la variante "plus"). Diferencia clave:

- En **B-tree**: las claves y los datos pueden estar en cualquier nodo (interno o hoja).
- En **B+ tree**: solo las hojas tienen los datos. Los nodos internos solo tienen claves para guiar la búsqueda. Las hojas están **enlazadas** entre sí en orden secuencial.

**Por qué es mejor para DBs**:

1. **Range queries súper eficientes**: una vez encuentras la primera hoja del rango, recorres las hojas enlazadas secuencialmente. `WHERE age BETWEEN 20 AND 30` es trivialmente rápido.
2. **Nodos internos más densos**: como solo guardan claves (no datos), caben muchas más por página → árbol más bajo → menos lecturas.
3. **Iteración ordenada gratis**: `ORDER BY` sobre la columna indexada usa las hojas en orden directamente, sin sort.

Cuando alguien dice "B-tree" en contexto de bases de datos, casi siempre se refiere a **B+ tree**.

### Estructura visual

```
                    [50 | 100]                  ← nodo interno (raíz)
                  /     |      \
        [10|30]    [60|80|95]    [120|150|180]  ← nodos internos
        /  |  \    /  |  |  \     /   |   |   \
     hojas con datos enlazadas    →   →   →     ← hojas (datos reales)
     (cada hoja apunta a la siguiente)
```

Una búsqueda de "key=85" hace 3 lecturas: raíz (50/100 → ir derecha medio), nodo interno (60/80/95 → ir entre 80 y 95), hoja final donde está el dato.

---

## 4. Tipos de índices

### Primary index (clustered index)

El **orden físico** de las filas en disco coincide con el orden del índice. Solo puede haber UNO por tabla (los datos solo pueden estar ordenados de una forma).

**MySQL InnoDB**: la clave primaria ES el clustered index. Las filas se almacenan físicamente ordenadas por PK.

**Postgres**: NO tiene clustered indexes nativos (las filas están en orden de inserción, en heap files). El comando `CLUSTER` reordena pero no se mantiene automático.

**Implicación**: en MySQL, lookup por PK es súper rápido (1 acceso). En Postgres, todos los índices son secundarios.

### Secondary index

Estructura B+tree separada que mapea valores → puntero a la fila real. Puedes tener N secundarios por tabla.

**Coste**: cada secondary index requiere update en cada INSERT/UPDATE/DELETE. Más índices = writes más lentos. Trade-off real.

### Composite index (multi-column)

Índice sobre **varias columnas** en orden específico: `INDEX (lastname, firstname)`.

**Importante**: el orden de columnas importa. Este índice sirve para:
- `WHERE lastname = 'Smith' AND firstname = 'John'`
- `WHERE lastname = 'Smith'` (usa solo prefix)
- `WHERE firstname = 'John'` (NO sirve, lastname no especificado)

Regla mnemotécnica: **leftmost prefix rule**. El índice se usa solo si tu WHERE usa un prefijo de las columnas.

### Covering index

Un índice que **contiene todas las columnas** que tu query necesita. La DB no tiene que ir a la tabla principal a buscar datos extra.

Ejemplo: query `SELECT firstname FROM users WHERE lastname = 'Smith'`. Si tienes `INDEX (lastname, firstname)`, ya tienes ambas en el índice → no hay que ir a la fila.

**Postgres**: `CREATE INDEX ON users (lastname) INCLUDE (firstname)`. Las columnas en INCLUDE están en las hojas pero no son parte del orden.

**MySQL**: simplemente añade columnas al índice composite.

Las covering indexes son **una de las optimizaciones más potentes**. Pueden hacer queries 10-100x más rápidas.

### Partial index

Índice solo sobre **un subset de filas** que cumple condición. Útil cuando la mayoría de queries filtran por algún flag.

```sql
CREATE INDEX active_users_email ON users (email) WHERE active = true;
```

Si el 90% de tus queries son sobre usuarios activos, este índice es 10x más pequeño y rápido que uno sobre toda la tabla.

### Unique index

Implementa la constraint UNIQUE. Internamente es un B+tree normal pero la DB rechaza inserts que violen unicidad.

---

## 5. EXPLAIN — la herramienta para entender qué hace tu DB

Cualquier DB seria tiene `EXPLAIN` (o `EXPLAIN ANALYZE` en Postgres) que muestra el **plan de ejecución** de tu query. Te dice:

- ¿Está usando un índice o haciendo seq scan?
- ¿Cuántas filas estima leer?
- ¿Qué tipo de join (nested loop, hash join, merge join)?
- Tiempo estimado vs real.

**Postgres ejemplo**:

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'a@b.com';
```

Output relevante:
- `Seq Scan on users` → rojo, está leyendo toda la tabla. Falta índice.
- `Index Scan using users_email_idx` → verde, usa el índice.
- `Bitmap Index Scan` → híbrido, usa el índice para localizar páginas y luego las lee.

Saber leer EXPLAIN es **literalmente la habilidad #1 para optimizar queries**. Más útil que cualquier "trick".

---

## 6. Cuándo añadir un índice

No siempre conviene. Cada índice tiene **coste**:

- **Espacio**: típicamente 5-20% del tamaño de la tabla por índice.
- **Writes más lentos**: cada INSERT/UPDATE/DELETE actualiza todos los índices afectados.
- **Optimizer más lento**: el planner de queries tarda más decidiendo entre índices.

**Cuándo SÍ añadir índice**:
1. Columnas usadas frecuentemente en `WHERE`, `JOIN`, `ORDER BY`, `GROUP BY`.
2. Columnas con alta **cardinalidad** (muchos valores distintos). Indexar `boolean` o `gender` casi nunca ayuda.
3. Tablas grandes (>10K filas típicamente).
4. Cuando EXPLAIN muestra Seq Scan en queries que se ejecutan mucho.

**Cuándo NO añadir índice**:
1. Tablas pequeñas (<1K filas) — seq scan es igual de rápido.
2. Columnas con baja cardinalidad (booleans, status enum de 3 valores).
3. Tablas muy write-heavy donde el coste de mantener índices supera la ganancia de reads.
4. Si el optimizer ya está usando otro índice efectivamente.

**Métrica útil en producción**: en Postgres, `pg_stat_user_indexes` muestra cuántas veces se ha usado cada índice. Índices con `idx_scan = 0` son candidatos a borrar.

---

## 7. Selectividad — el concepto clave

**Selectividad** = porcentaje de filas que devuelve un filtro. Determina si el índice ayuda.

- `WHERE email = 'X'` → típicamente 1 fila → selectividad 0.0001%. Índice **muy útil**.
- `WHERE country = 'US'` → 50% de filas. Índice **inútil**: leer el índice + saltar a las filas es más caro que un seq scan.
- `WHERE age > 30` → 60% filas. Índice **probablemente inútil**.

**Regla heurística**: si tu filtro selecciona **más del 5-10% de las filas**, el índice probablemente no ayuda. La DB hace seq scan igualmente.

Por eso la **cardinalidad alta** importa para índices: muchos valores distintos = filtros más selectivos posibles.

---

## 8. Index-only scan — la optimización máxima

Cuando un índice **incluye todas las columnas** que necesita la query, la DB **no toca la tabla**. Solo lee el índice. Esto es **index-only scan** y es lo más rápido posible.

Si tu query es `SELECT email FROM users WHERE active = true` y tienes `INDEX (active, email)`, todo el dato está en el índice. La DB recorre las hojas relevantes y ya está. Sin saltos a la tabla.

Esta es la justificación principal de **covering indexes** y de Postgres `INCLUDE`.

---

## 9. Cuándo el índice se pone en el medio

A veces el optimizer **decide no usar tu índice** aunque exista. Razones comunes:

1. **Función sobre la columna**: `WHERE LOWER(email) = 'x@y.com'` no usa el índice sobre `email`. Solución: índice funcional `CREATE INDEX ON users (LOWER(email))`.
2. **Tipo casting**: comparar `int_column = '5'` (string vs int) puede impedir uso del índice.
3. **OR rompiendo el patrón**: `WHERE a = 1 OR b = 2` puede no usar índices individuales si están en columnas distintas.
4. **Estadísticas obsoletas**: el optimizer decide basado en estadísticas. Si están viejas (mucho insert sin VACUUM ANALYZE en Postgres), elige mal.
5. **Query devuelve muchas filas**: si el WHERE es poco selectivo, seq scan es más rápido (sección 7).

EXPLAIN te dice qué decisión tomó. Si no usa tu índice, EXPLAIN te dice cuántas filas estima — frecuentemente la causa.

---

## 10. Fragmentación y mantenimiento

Los índices se **fragmentan** con uso intensivo. Inserts/updates dejan páginas medio vacías, splits de nodos crean ineficiencias. Después de mucha actividad:

**Postgres**: `REINDEX` reconstruye el índice desde cero. `VACUUM` recupera espacio sin reconstruir. `pg_repack` permite reindex sin lock.

**MySQL**: `OPTIMIZE TABLE` reconstruye índices.

Esto es trabajo periódico de DBA. Para apps modernas pequeñas-medianas, los autovacuum y autoreindex bastan.

---

## 11. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Hoy: JSON en disco, sin índices reales. Cada query es seq scan implícito (Python recorre la lista entera).

Cuando migres a Postgres (proyecto futuro):
- PK sobre `id` (clustered en MySQL, secundario en Postgres).
- Índice sobre `email` (probablemente UNIQUE).
- Índice sobre `phone` para búsqueda por fragmento — caveat: `LIKE '%600%'` (con % al inicio) NO usa B-tree índice. Necesitas trigram index (`pg_trgm` extension en Postgres).
- Para sort by name: índice sobre `name`.

### En entrevistas tecnicas

**Pregunta clásica**: "¿Qué es un índice y cómo funciona?".

Tu respuesta: estructura B+tree (en la mayoría de DBs) que mapea valores ordenados → puntero a fila. Permite lookup O(log n) en lugar de O(n) seq scan. Coste en espacio + writes más lentos.

**Pregunta típica**: "Cuándo NO añadir un índice".

Tablas pequeñas, columnas con baja cardinalidad, columnas raramente filtradas, tablas write-heavy donde el coste supera la ganancia.

**Pregunta sobre EXPLAIN**: "Cómo investigarías una query lenta".

EXPLAIN ANALYZE → identificar Seq Scan vs Index Scan → ver estimación vs real → si discrepancia, ANALYZE para actualizar stats → considerar índice composite, covering, o reescribir query.

**Pregunta avanzada**: "Diferencia B-tree vs LSM-tree y cuándo cada uno".

B-tree: read-optimized, in-place updates, mejor para workloads mixtos. LSM-tree: write-optimized (escrituras secuenciales), compactación periódica, mejor para write-heavy. Postgres/MySQL usan B-tree. Cassandra/RocksDB usan LSM.

---

## 12. Trampas típicas

**"Más índices = más rápido"**: NO. Cada índice ralentiza writes y ocupa espacio. Hay que medir.

**"Índice en cada WHERE"**: tampoco. Si la columna tiene baja cardinalidad o el WHERE es poco selectivo, no ayuda.

**"Índice en booleanos"**: casi nunca útil. 2 valores distintos → cada uno cubre 50% de filas → no selectivo.

**"`LIKE '%X%'` usa índice"**: NO. Solo `LIKE 'X%'` (prefix) usa B-tree. Para substring necesitas trigram (Postgres) o full-text search.

**"El composite index sirve para todas las combinaciones"**: NO. Solo prefijos del índice. `INDEX (a, b, c)` sirve para `WHERE a` o `WHERE a AND b` o `WHERE a AND b AND c`. NO para `WHERE b` solo.

**"Índices se actualizan automáticamente sin coste"**: tienen coste. Cada write actualiza N índices. En tablas write-heavy es notable.

**"DROP INDEX si no estoy seguro de si se usa"**: peligroso en producción sin medir. Mira `pg_stat_user_indexes` primero. Si idx_scan = 0 durante semanas, candidato real.

---

## 13. Preguntas típicas de interview

**¿Qué es un B-tree y por qué se usa en DBs?**: árbol balanceado con muchos hijos por nodo, optimizado para minimizar lecturas de disco. log base alto → árbol bajo → pocas lecturas.

**B-tree vs B+ tree**: B+ tiene los datos solo en hojas, hojas enlazadas → range queries súper eficientes. Casi todas las DBs usan B+.

**Clustered vs secondary index**: clustered = orden físico de filas coincide con índice (1 por tabla). Secondary = estructura separada apuntando a filas (N por tabla).

**Covering index**: contiene todas las columnas que la query necesita → la DB no toca la tabla, solo el índice.

**Cuándo usar índice composite**: cuando frecuentemente filtras por múltiples columnas juntas. Ojo con leftmost prefix rule.

**B-tree vs LSM-tree**: B-tree para read-heavy y mixed. LSM para write-heavy. Postgres usa B-tree, Cassandra LSM.

---

## 14. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué existen los índices (evitar seq scan).
- Por qué B+tree y no BST (depth bajo aprovechando page size).
- Diferencia B+ vs B normal (datos solo en hojas, hojas enlazadas).
- Clustered vs secondary index.
- Composite index y leftmost prefix rule.
- Covering index e index-only scan.
- Selectividad y cuándo el índice no ayuda.
- EXPLAIN como herramienta principal de optimización.
- B-tree vs LSM-tree y cuándo cada uno.

Si no puedes → relee.

---

## Conexiones

- [[02-acid-transactions]] — los índices participan en transacciones
- [[03-isolation-levels]] — locks sobre índices
- [[04-replication-y-sharding]] — índices se replican también
- [[05-sql-vs-nosql-tradeoffs]] — modelos de datos distintos
- [[../02_operating_systems/05-filesystems]] — page cache afecta lecturas de índice
- [[../02_operating_systems/02-memoria-virtual-paging]] — paginación de disco
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Designing Data-Intensive Applications** capítulo 3 (Storage and Retrieval) — la mejor explicación moderna.
- **Use The Index, Luke!** (use-the-index-luke.com) — gratis online, exhaustivo sobre indexing en SQL real.
- **Postgres docs: Indexes** (postgresql.org/docs/current/indexes.html) — excelente.
- **High Performance MySQL** (Schwartz et al.) — clásico, denso.
- **`EXPLAIN ANALYZE` Postgres**, `EXPLAIN FORMAT=JSON` MySQL — empieza a usarlos hoy.
