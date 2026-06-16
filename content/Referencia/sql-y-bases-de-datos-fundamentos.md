---
title: SQL y bases de datos — fundamentos para proyectos backend (con ejemplos de Booking)
date: 2026-05-13
tags: [programacion/referencia, programacion/databases, programacion/sql, programacion/postgres]
type: nota
status: permanente
source: claude-code
aliases: [sql-fundamentos, bases-datos-fundamentos, postgres-basics, orm-vs-sql]
---

# SQL y bases de datos — fundamentos para backend (con ejemplos de Booking)

> Doc transversal de [[Referencia/00_README|Referencia]]. Cubre la teoría de relational databases + SQL que necesitas dominar AUNQUE estés usando un ORM (SQLAlchemy). Calibrado con ejemplos del proyecto Booking v0.1, pero aplica a cualquier proyecto backend con DB relacional.

## Por qué importa (aunque uses ORM)

El ORM **genera SQL automáticamente** — pero cuando algo va mal, lo que lees en logs es SQL. Sin entender SQL:

- No puedes leer EXPLAIN ANALYZE → no diagnosticas queries lentas
- No detectas N+1 queries (el ORM las oculta)
- No diseñas índices apropiados
- No entiendes deadlocks ni race conditions
- Caes en anti-patterns que el ORM te deja hacer (lazy loading async, join cartesiano)
- En interview de senior te preguntan SQL puro — y NO sabes responder

**Senior backend = ORM fluent + SQL fluent**. Ambos. El ORM es ergonomía, NO substituto del entendimiento.

## SCHEMA: el modelo relacional en 30 segundos

```
TABLA = colección de FILAS con MISMA estructura (mismas columnas)

   id  │ name        │ city     │ owner_id  ←── columnas (atributos)
   ────┼─────────────┼──────────┼─────────
    1  │ Hotel Sol   │ Madrid   │ 5         ←── fila (registro)
    2  │ Hotel Luna  │ Barcelona│ 5         ←── fila
    3  │ Hotel Mar   │ Valencia │ 7         ←── fila

   ↑                                ↑
PRIMARY KEY                     FOREIGN KEY → users.id
(identifica fila única)         (referencia otra tabla)
```

3 conceptos fundamentales:
1. **Tabla** = entidad (Hotel, User, Room)
2. **Relación** = link entre tablas vía FK (Hotel.owner_id → User.id)
3. **Constraint** = regla que la DB impone (UNIQUE, NOT NULL, FK CASCADE)

Tu Booking v0.1:
- 3 tablas: `users`, `hotels`, `rooms`
- 2 FKs: `hotels.owner_id → users.id`, `rooms.hotel_id → hotels.id`
- Cardinalidad: User 1—N Hotel 1—N Room

## PATTERNS — los 4 grupos de SQL operations

### 1. CRUD operations (el 80% de lo que harás)

```sql
-- CREATE
INSERT INTO hotels (name, city, owner_id)
VALUES ('Hotel Sol', 'Madrid', 5);

-- READ
SELECT id, name, city FROM hotels WHERE city = 'Madrid';

-- UPDATE
UPDATE hotels SET city = 'Sevilla' WHERE id = 42;

-- DELETE
DELETE FROM hotels WHERE id = 42;
```

**Equivalencias SQLAlchemy** (lo que tu ORM genera):

| SQL | SQLAlchemy ORM |
|---|---|
| `INSERT INTO ...` | `db.add(obj); await db.commit()` |
| `SELECT ... WHERE ...` | `select(Model).where(...)` + `db.execute()` |
| `UPDATE ... SET ...` | `obj.field = value; await db.commit()` |
| `DELETE FROM ...` | `await db.delete(obj); await db.commit()` |

### 2. Filtering — WHERE clauses

```sql
SELECT * FROM hotels
WHERE city = 'Madrid'                  -- igualdad
  AND price >= 50                       -- comparación
  AND name LIKE '%Sol%'                 -- pattern matching (case-sensitive)
  AND name ILIKE '%sol%'                -- case-insensitive (Postgres)
  AND country IN ('ES', 'PT', 'FR')     -- in list
  AND created_at > '2026-01-01'         -- date comparison
  AND description IS NOT NULL;          -- null check (NUNCA usar = NULL)
```

**Gotcha clave**: `NULL` NO es igualable con `=`. SIEMPRE `IS NULL` o `IS NOT NULL`. Razón: NULL representa "desconocido" y comparar desconocido con cualquier cosa es indefinido.

```sql
SELECT * FROM hotels WHERE description = NULL;  -- ❌ NO devuelve nada (siempre falso)
SELECT * FROM hotels WHERE description IS NULL; -- ✅ correcto
```

### 3. Sorting + Pagination

```sql
SELECT * FROM hotels
ORDER BY price ASC, id ASC      -- 2 columnas: price asc, id como tiebreaker
LIMIT 20 OFFSET 40;             -- skip 40, return 20 (página 3 con tamaño 20)
```

**Por qué OFFSET muere a escala** (preview de tu doc 09 cursor pagination):
- DB tiene que leer y descartar 40 filas antes de devolverte las buenas
- Para `OFFSET 1000000` → lee y descarta 1M filas → segundos de latencia
- Solución producción = cursor: `WHERE id > 1042 LIMIT 20` (O(log N) constante)

### 4. Aggregations — GROUP BY

```sql
-- Contar hoteles por ciudad
SELECT city, COUNT(*) AS hotel_count
FROM hotels
GROUP BY city
ORDER BY hotel_count DESC;

-- Precio medio por país
SELECT country, AVG(price_cents) / 100.0 AS avg_price_eur
FROM rooms
GROUP BY country
HAVING COUNT(*) > 10;            -- HAVING = WHERE pero post-aggregation
```

Funciones agregadas: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. Aplican a grupos definidos por GROUP BY.

**Regla**: en la SELECT solo puedes incluir columnas del GROUP BY o agregaciones. NO mezclar columnas no-agrupadas (error en Postgres, comportamiento raro en MySQL).

## JOINs — los 4 + cuándo cada uno

JOINs combinan filas de 2+ tablas. La diferencia clave es **qué filas se preservan cuando NO hay match**.

### Setup mental con tu Booking

```
hotels                 rooms
┌─────┬────────┐      ┌─────┬──────────┬───────┐
│ id  │ name   │      │ id  │ hotel_id │ price │
├─────┼────────┤      ├─────┼──────────┼───────┤
│  1  │ Sol    │      │ 100 │    1     │  80   │
│  2  │ Luna   │      │ 101 │    1     │  120  │
│  3  │ Mar    │      │ 102 │    2     │  90   │
└─────┴────────┘      └─────┴──────────┴───────┘
                       (Hotel "Mar" id=3 NO tiene rooms)
```

### INNER JOIN — solo matches

```sql
SELECT h.name, r.price
FROM hotels h
INNER JOIN rooms r ON r.hotel_id = h.id;
```
Resultado:
```
Sol  | 80
Sol  | 120
Luna | 90
```
Hotel "Mar" desaparece porque no tiene rooms. INNER = intersección.

### LEFT JOIN — todas las filas de la izquierda + matches de la derecha

```sql
SELECT h.name, r.price
FROM hotels h
LEFT JOIN rooms r ON r.hotel_id = h.id;
```
Resultado:
```
Sol  | 80
Sol  | 120
Luna | 90
Mar  | NULL    ← Mar aparece, pero r.price es NULL porque no hay match
```

**Cuándo LEFT JOIN**: queremos contar/listar TODOS los hoteles (incluso sin rooms). Típico para "hoteles con/sin X".

### RIGHT JOIN — espejo del LEFT (poco usado, prefiero LEFT con tablas swap)

### FULL OUTER JOIN — todas las filas de ambos lados

```sql
SELECT h.name, r.price
FROM hotels h
FULL OUTER JOIN rooms r ON r.hotel_id = h.id;
```
Devuelve hoteles sin rooms + rooms huérfanas (no debería pasar con FK CASCADE pero útil para detectar inconsistencias).

### Equivalencia SQLAlchemy

```python
# INNER JOIN explícito
stmt = select(Hotel.name, Room.price).join(Hotel.rooms)

# LEFT JOIN
stmt = select(Hotel.name, Room.price).outerjoin(Hotel.rooms)

# Carga eager (NO es JOIN literal pero evita N+1)
stmt = select(Hotel).options(selectinload(Hotel.rooms))
```

## Constraints — las 5 reglas que la DB impone

Constraints **garantizan integridad** antes de escribir. Si rompes una → INSERT/UPDATE falla con error.

| Constraint | Qué impone | Ejemplo Booking |
|---|---|---|
| **PRIMARY KEY** | Identifica fila única, NOT NULL implícito, indexed automático | `id INTEGER PRIMARY KEY` |
| **FOREIGN KEY** | Referencia a otra tabla, opcional CASCADE/SET NULL on delete | `owner_id REFERENCES users(id) ON DELETE CASCADE` |
| **UNIQUE** | Valor único en la tabla (puede ser compuesto) | `email VARCHAR UNIQUE` |
| **NOT NULL** | Columna no puede ser NULL | `name VARCHAR NOT NULL` |
| **CHECK** | Expresión booleana custom | `CHECK (price_cents > 0)` |

### CASCADE — cómo se propagan los DELETEs

Tu Booking usa CASCADE explícitamente:

```python
# models/hotel.py
owner_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    index=True,
)

rooms: Mapped[list["Room"]] = relationship(
    back_populates="hotel",
    cascade="all, delete-orphan",
)
```

**Significa**:
- Borrar User 5 → DB automáticamente borra TODOS los hoteles con `owner_id=5`
- Borrar Hotel 1 → DB borra TODAS las rooms con `hotel_id=1`

**Alternativas a CASCADE**:
- `RESTRICT` (default): no permite borrar User si tiene Hotels (raise FK violation)
- `SET NULL`: setea owner_id=NULL en sus Hotels (huérfanos)
- `NO ACTION`: similar a RESTRICT pero deferrable

**Cuándo CASCADE**: cuando la entidad hija NO tiene sentido sin la padre (Room sin Hotel = absurdo).
**Cuándo RESTRICT**: cuando quieres prevenir borrados accidentales (User con Hotels = "ojo, tiene cosas").

### IntegrityError = constraint violado

Cuando ves esto en Python:
```python
sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint "users_email_key"
```

= la DB rechazó tu INSERT porque violaba un constraint UNIQUE. Patrón canónico:

```python
try:
    db.add(new_user)
    await db.commit()
except IntegrityError:
    await db.rollback()
    raise HTTPException(409, "Email already exists")
```

## Indexes — el corazón de la performance

Sin índice apropiado, queries que parecen rápidas en dev (10 hoteles) **mueren en producción** (1M hoteles). Es el bug más común de junior.

### Modelo mental: índice = libro con índice analítico vs sin él

Sin índice (Sequential Scan):
```
SELECT * FROM hotels WHERE city = 'Madrid';
→ DB lee TODAS las filas, descarta las que no son Madrid
→ O(N) con N filas
```

Con índice en `city`:
```
SELECT * FROM hotels WHERE city = 'Madrid';
→ DB salta directo en B-tree a "Madrid" → lee solo las matches
→ O(log N) — milisegundos en cualquier escala
```

### Tipos de índice (Postgres)

| Tipo | Cuándo | Ejemplo en Booking |
|---|---|---|
| **B-tree** (default) | Equality + range queries (`=`, `>`, `<`, `BETWEEN`, `ORDER BY`) | `CREATE INDEX ON hotels(city)` |
| **GIN** | Full-text search, JSONB, array containment | v0.2: `CREATE INDEX ON hotels USING GIN (search_vector)` |
| **GIST** | Geographical (PostGIS), range types | si añades coordinates |
| **Hash** | Solo equality (poco usado, B-tree es más versátil) | raro |
| **BRIN** | Tablas enormes con datos correlados (timestamps en orden) | logs, time-series |

### Composite indexes (multi-column)

```sql
CREATE INDEX idx_hotels_city_price ON hotels(city, price_cents);
```

**Regla leftmost prefix**: este índice es útil para queries que filtran por `city` o `(city, price)` — pero **NO** por `price` solo.

| Query | Usa el índice? |
|---|---|
| `WHERE city = 'Madrid'` | ✅ |
| `WHERE city = 'Madrid' AND price_cents = 8000` | ✅ |
| `WHERE price_cents = 8000` | ❌ (no city → no usa) |

### Reglas operativas

1. **Indexa columnas de WHERE frecuentes**
2. **Indexa FKs** (Postgres NO lo hace automático, MySQL sí)
3. **Indexa columnas de ORDER BY** (sino DB hace sort en memoria)
4. **NO indexes**: booleans (cardinalidad 2 → no ayuda), columnas con función aplicada (`WHERE LOWER(name) = ...` rompe el índice — usa expression index)
5. **Trade-off**: cada índice **acelera reads pero ralentiza writes** (cada INSERT/UPDATE actualiza todos los índices). Regla: pocos índices bien elegidos > muchos índices mediocres.

### Cómo verificar que tu índice se usa

```sql
EXPLAIN ANALYZE SELECT * FROM hotels WHERE city = 'Madrid';
```

Output bueno (con índice):
```
Index Scan using idx_hotels_city on hotels  (cost=0.28..8.30 rows=1 ...)
```

Output malo (sin índice o no usado):
```
Seq Scan on hotels  (cost=0.00..1234.00 rows=10000 ...)
```

`Seq Scan` en tabla grande = bandera roja. Investiga.

## Normalization — 1NF / 2NF / 3NF brief

Normalización = organizar tablas para evitar redundancia y anomalías de update.

### 1NF (First Normal Form)

Cada celda contiene **un solo valor atómico** — no listas, no estructuras anidadas.

```
❌ amenities: "wifi,pool,gym"           ← string con valores múltiples
✅ tabla amenity_hotel separada con 1 amenity por fila
```

(Postgres permite arrays nativos, técnicamente "rompe" 1NF pero práctico para casos simples).

### 2NF — depender de la PK completa

Aplicable solo si tu PK es composite. Tu Booking usa PKs simples (id integer) → automáticamente cumple.

### 3NF — atributos dependen SOLO de la PK, no de otros atributos

```
❌ rooms(id, hotel_id, hotel_city)  ← hotel_city depende de hotel_id, no de rooms.id (anomalía)
✅ rooms(id, hotel_id) + JOIN con hotels para obtener city  ← city solo en hotels
```

**Regla práctica**: si actualizas un dato y tienes que actualizarlo en 2+ lugares → no estás en 3NF.

### Denormalization deliberada (rompiendo reglas con propósito)

A veces denormalizas para **performance** (evitar JOINs caros):

```python
# rooms tiene precio_cents
# Pero si listas 10k hoteles con su precio MÍNIMO, JOIN+MIN es caro
# Solución: cachear "cheapest_price" en hotels (denormalizar)
hotels.cheapest_room_price_cents  ← actualizado vía trigger o app-level
```

Trade-off: SELECT más rápido, UPDATE complica (mantener consistencia). v0.6 (Caching) cubrirá esto.

## Transactions + ACID + isolation levels

### Transaction = unidad atómica

```sql
BEGIN;                                    -- abre transacción
INSERT INTO reservations (...) VALUES (...);
UPDATE rooms SET booked = true WHERE id = 42;
COMMIT;                                   -- todo OK, persiste
-- o:
ROLLBACK;                                 -- algo falló, descarta TODO
```

Si crashea entre INSERT y UPDATE: NADA se persiste. Atomicidad.

En SQLAlchemy:
```python
async with db.begin():     # implicit BEGIN
    db.add(reservation)
    room.booked = True
    # implicit COMMIT al salir del bloque sin excepción
    # implicit ROLLBACK si excepción
```

### ACID

| Letra | Significa | Garantiza |
|---|---|---|
| **A**tomicity | Todo-o-nada | Crash mid-transaction → rollback completo |
| **C**onsistency | Constraints siempre respetados | No puedes commit un estado que viola FK/UNIQUE |
| **I**solation | Transactions concurrentes no se ven entre sí (parcialmente) | Depende de isolation level |
| **D**urability | Una vez commit, sobrevive crashes | Postgres usa WAL (write-ahead log) |

### Isolation levels (los 4)

Concurrencia es donde las cosas se complican. 2 transactions paralelas pueden leer/escribir mismas filas.

| Nivel | Permite ver... | Anomalías que NO previene |
|---|---|---|
| **READ UNCOMMITTED** | Cambios sin commit de otras tx | dirty read, non-repeatable read, phantom |
| **READ COMMITTED** (Postgres default) | Solo cambios committed | non-repeatable read, phantom read |
| **REPEATABLE READ** | Snapshot consistente toda la tx | phantom read (Postgres lo previene aquí también) |
| **SERIALIZABLE** | Como si fueran secuenciales | ninguna |

**Para Booking v0.1**: READ COMMITTED default es OK porque solo haces CRUDs simples sin race conditions críticas.

**Para Booking v0.3 (Reservations)**: necesitarás SERIALIZABLE o explicit locking — ahí es donde 2 usuarios intentan reservar la misma room simultáneamente y SOLO 1 debe ganar.

### Race condition clásica que verás en v0.3

```
T1: SELECT availability FROM rooms WHERE id = 1;  → "available"
T2: SELECT availability FROM rooms WHERE id = 1;  → "available"
T1: UPDATE rooms SET availability = 'booked' WHERE id = 1;
T2: UPDATE rooms SET availability = 'booked' WHERE id = 1;  ← OVERBOOK!
```

Soluciones:
1. **Optimistic locking** (version column): `UPDATE ... WHERE id = 1 AND version = 5`. Si otro UPDATE pasó primero, version cambió, tu UPDATE matchea 0 filas → retry o conflict.
2. **Pessimistic locking** (SELECT FOR UPDATE): `SELECT ... FROM rooms WHERE id = 1 FOR UPDATE` → bloquea esa fila hasta tu COMMIT. Otras tx esperan.
3. **Serializable isolation**: la DB detecta conflictos automáticamente y aborta una tx.

Cubrirás esto en profundidad en v0.3 docs.

## Postgres-specific things que aparecen en Booking

### Tipos de datos que usarás

| Tipo SQL | SQLAlchemy | Cuándo |
|---|---|---|
| `INTEGER` / `BIGINT` | `Integer`, `BigInteger` | counters, IDs |
| `VARCHAR(N)` | `String(N)` | strings con límite |
| `TEXT` | `Text` | strings largos sin límite |
| `BOOLEAN` | `Boolean` | flags |
| `TIMESTAMP WITH TIME ZONE` | `DateTime(timezone=True)` | fechas (SIEMPRE timezone-aware) |
| `DATE` | `Date` | solo fecha sin hora |
| `NUMERIC(N,M)` | `Numeric(N, M)` | precisión exacta (precios → o INTEGER cents para evitar floats) |
| `JSONB` | `JSON` (Postgres backend) | datos semi-estructurados, indexable |
| `UUID` | `UUID(as_uuid=True)` | IDs distribuidos |
| `tsvector` | tipo custom | full-text search (v0.2) |

### server_default vs default

```python
# default (Python-side) — calculado al crear el objeto en Python
created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# server_default (SQL-side) — calculado por Postgres al INSERT
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
)
```

**Preferir `server_default`** para timestamps de auditoría: garantiza correctness aunque INSERT venga de psql directo o de otra app, no solo de tu código Python.

### Generated columns (v0.2)

```sql
-- Columna calculada automáticamente por Postgres
ALTER TABLE hotels ADD COLUMN search_vector tsvector
GENERATED ALWAYS AS (to_tsvector('english', name || ' ' || description)) STORED;
```

Postgres mantiene `search_vector` actualizado automáticamente cada vez que `name` o `description` cambian. Sin trigger manual. **Usado en tu v0.2 para FTS**.

## ORM ↔ SQL — qué SQL genera SQLAlchemy

Activar logging para VER el SQL real:

```python
engine = create_async_engine(DATABASE_URL, echo=True)
```

Lo que verás (output ejemplo de `db.execute(select(Hotel))`):
```
SELECT hotels.id, hotels.name, hotels.city, hotels.country,
       hotels.address, hotels.owner_id, hotels.created_at
FROM hotels
```

Lo que verás (output de `await db.get(Hotel, 42)`):
```
SELECT hotels.id, hotels.name, ...
FROM hotels
WHERE hotels.id = $1
```
($1 es bind parameter — Postgres reemplaza por 42, NO concatenación de string → previene SQL injection).

### El N+1 problem visualizado en SQL

Código aparentemente inocente:
```python
hotels = (await db.execute(select(Hotel))).scalars().all()
for h in hotels:
    rooms = (await db.execute(
        select(Room).where(Room.hotel_id == h.id)
    )).scalars().all()
    print(f"{h.name}: {len(rooms)} rooms")
```

SQL real generado:
```sql
SELECT * FROM hotels;                            -- 1 query
SELECT * FROM rooms WHERE hotel_id = 1;          -- N queries
SELECT * FROM rooms WHERE hotel_id = 2;
SELECT * FROM rooms WHERE hotel_id = 3;
... (N veces)
```

Con 10k hoteles → **10001 queries** → catástrofe.

Solución (SQLAlchemy `selectinload`):
```python
stmt = select(Hotel).options(selectinload(Hotel.rooms))
hotels = (await db.execute(stmt)).scalars().all()
```

SQL real generado:
```sql
SELECT * FROM hotels;                                          -- 1 query
SELECT * FROM rooms WHERE hotel_id IN (1, 2, 3, ..., 10000);   -- 1 query
```

**Total: 2 queries**, no 10001. Esto es el challenge #3 de v0.1.

## Common pitfalls que vas a cometer (todos los hacemos)

| Pitfall | Síntoma | Fix |
|---|---|---|
| Olvidar `await` en sql operation async | "coroutine was never awaited" o no se persiste | Añadir `await` |
| Comparar con `= NULL` | WHERE devuelve siempre vacío | Usar `IS NULL` / `IS NOT NULL` |
| N+1 queries | Endpoint lento, logs llenos de queries | `selectinload` o `joinedload` |
| Sin índice en FK | JOINs lentos en producción | Añadir `index=True` en mapped_column de FK |
| Devolver ORM en response | Leak de campos privados (password_hash) | Usar Pydantic schema con response_model |
| `expire_on_commit=True` default | DetachedInstanceError post-commit | `expire_on_commit=False` en sessionmaker |
| String concatenation en query | SQL injection | SIEMPRE bind parameters via ORM o `text("... :param")` |
| Float para precios | Errores de redondeo | INTEGER cents (`price_cents`) o `Numeric(10,2)` |
| Naive datetime (sin tz) | Bugs cuando deployes a otra timezone | SIEMPRE `datetime.now(timezone.utc)` + `DateTime(timezone=True)` |
| Migrations no aplicadas en startup | "table doesn't exist" en producción | `alembic upgrade head` en entrypoint.sh |
| Connection pool agotado | Hangs aleatorios bajo load | Configurar `pool_size`, `max_overflow`, no leak de sessions |

## EXPLAIN básico — cómo leer el plan de ejecución

```sql
EXPLAIN SELECT * FROM hotels WHERE city = 'Madrid';
```

Output:
```
Seq Scan on hotels  (cost=0.00..1234.00 rows=120 width=80)
  Filter: (city = 'Madrid'::text)
```

Lectura:
- `Seq Scan` = sequential scan (lee toda la tabla) ← MAL si tabla grande
- `cost=0.00..1234.00` = estimated startup cost..total cost (unidad arbitraria, sirve para comparar)
- `rows=120` = filas estimadas que devolverá
- `width=80` = bytes promedio por fila
- `Filter: ...` = filtro aplicado post-scan

`EXPLAIN ANALYZE` añade tiempos REALES de ejecución (más útil pero EJECUTA la query — cuidado con DELETEs en EXPLAIN ANALYZE!):

```sql
EXPLAIN ANALYZE SELECT * FROM hotels WHERE city = 'Madrid';
```

Output:
```
Seq Scan on hotels  (cost=0.00..1234.00 rows=120 width=80)
                    (actual time=0.123..15.456 rows=118 loops=1)
```

Comparas `rows=120` (estimado) con `rows=118` (real). Si difieren mucho → estadísticas desactualizadas (`ANALYZE hotels;` para refrescar).

Buscar en el plan:
- `Index Scan` ✅ (usa índice)
- `Bitmap Index Scan` + `Bitmap Heap Scan` ✅ (índice multi-resultado)
- `Seq Scan` en tabla grande ❌ (falta índice)
- `Sort` con muchos rows ❌ (debería usar índice ordenado)
- `Nested Loop` con muchos rows ❌ (preferir Hash Join o Merge Join para grandes datasets)

## Cómo aplicar TODO esto a tu Booking — checklist mental

Cuando trabajes en v0.1 y siguientes, hazte estas preguntas en cada cambio:

| Pregunta | Cuándo |
|---|---|
| ¿Esta query usa índice? | Cualquier WHERE/JOIN/ORDER BY nuevo |
| ¿Hay riesgo de N+1 aquí? | Cualquier loop sobre relaciones ORM |
| ¿Esta operación necesita transaction explícita? | Múltiples writes que deben ser atómicos |
| ¿Estoy expuesto a race condition? | Updates concurrentes posibles → v0.3 |
| ¿Mi schema response leak campos privados? | Cualquier `response_model` nuevo |
| ¿Tipo de datos correcto? | Precios = INTEGER cents NO Float; fechas = timezone aware |
| ¿FK con CASCADE apropiado? | Cualquier FK nueva |
| ¿Migration backwards-compatible? | Cualquier migration que toque tabla con datos |
| ¿Constraint UNIQUE protege contra dupes? | Cualquier campo "único lógicamente" |
| ¿Tengo índice en esta FK? | Cualquier FK nueva (Postgres NO autoindexa FKs) |

## Conexiones

- [[Referencia/00_README]] — área padre
- [[archetipos-funciones-backend]] — función + DB combinadas
- (Booking v0.1) — el ORM específico
- (Booking v0.1) — schema versioning
- (Booking v0.2 spec) — EXPLAIN profundo
- (Booking v0.2 spec) — paginación a escala

## Recursos canónicos para profundizar

**Esenciales** (cuando necesites más profundidad):

1. **"Designing Data-Intensive Applications"** (Martin Kleppmann) — el libro definitivo de DBs distribuidas. Lectura obligada para senior.
2. **PostgreSQL official docs** — sí, son bookworm pero la única fuente fiable de comportamiento exacto de Postgres
3. **"SQL Performance Explained"** (Markus Winand) — cómo escribir queries que escalen. Solo 200 páginas, gold standard.
4. **use-the-index-luke.com** (Markus Winand) — versión web del libro anterior, gratuita

**Para ORM específicamente**:

5. **SQLAlchemy 2.0 docs — Async I/O** — para entender lo async correctamente
6. **"Architecture Patterns with Python"** (Percival & Gregory) — repository pattern + DDD aplicado a Python con SQLAlchemy

**Cuándo leer cada uno**: 4 (use-the-index-luke) ahora si quieres deep dive en performance. 1 (Kleppmann) cuando llegues a v0.3-v0.4 (concurrency + payments). 5 (SQLAlchemy docs) on-demand cuando una API te confunda.

## Resumen mental

> "ORM es ergonomía, NO substituto del entendimiento SQL. Senior backend = ORM fluent + SQL fluent. 5 grupos: CRUD (INSERT/SELECT/UPDATE/DELETE), JOINs (INNER vs LEFT vs FULL — diferencia es qué filas se preservan sin match), constraints (PK/FK/UNIQUE/NOT NULL/CHECK con CASCADE para propagación), índices (B-tree para equality+range, GIN para FTS, leftmost prefix en composites, trade-off reads vs writes), normalization (1NF/2NF/3NF — denormaliza con propósito para performance). Transactions ACID con isolation levels (READ COMMITTED Postgres default OK para v0.1, SERIALIZABLE o explicit locking para v0.3 reservations). Postgres specifics: server_default vs Python default, generated columns para v0.2 FTS, JSONB para semi-estructurado, INTEGER cents para precios (NO float). ORM↔SQL: activa echo=True para ver SQL real, N+1 problem con selectinload/joinedload, gotchas comunes (await, IS NULL no =, response_model para evitar leak). EXPLAIN/EXPLAIN ANALYZE: Seq Scan en tabla grande = bandera roja, Index Scan = bueno. Para Booking aplicar checklist mental en cada cambio: índices, N+1, transactions, race conditions, response leaks, tipos correctos. Recursos canónicos: Kleppmann (DDIA), Winand (SQL Performance Explained + use-the-index-luke gratuito), SQLAlchemy 2.0 async docs."
