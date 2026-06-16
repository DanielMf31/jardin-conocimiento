# 03 — Isolation levels

> 📚 **Doc 3 del cluster Database Internals**. La I de ACID en profundidad. Probablemente el tema más mal entendido en bases de datos. Si lo dominas, ya estás por encima del 80% de developers.
> 🔥 **Frecuencia interview**: aparece en backend interviews senior. "Diferencia READ COMMITTED vs REPEATABLE READ", "qué es phantom read".
> ⏱️ **Tiempo de lectura estimado**: 45-60 min.

---

## 1. Por qué isolation es complicado

Si una sola transacción ejecuta a la vez (serial), no hay problema: cada una ve el resultado de la anterior. Pero **eso no escala**: tu DB procesaría 1 tx a la vez. Para throughput real, las DBs ejecutan **transacciones concurrentes**.

El problema: cuando varias transacciones tocan los mismos datos a la vez, pueden **ver estados raros** o **interferir entre sí**. Hay 4 anomalías clásicas que pueden ocurrir, y los **isolation levels** son las distintas garantías que la DB te da contra esas anomalías — con trade-off entre garantías y performance.

---

## 2. Las 4 anomalías clásicas

### Dirty read

Lees datos que **otra transacción modificó pero todavía no ha hecho commit**. Si esa otra transacción luego hace rollback, leíste datos que "nunca existieron".

**Ejemplo**:
- TX A: `UPDATE accounts SET balance = 50 WHERE id = 1` (no commit todavía).
- TX B: `SELECT balance FROM accounts WHERE id = 1` → ve 50.
- TX A: ROLLBACK.
- TX B actuó basándose en un valor falso.

### Non-repeatable read

Lees el mismo registro **dos veces** dentro de tu TX, y obtienes valores **distintos** porque otra TX modificó entre medio.

**Ejemplo**:
- TX A: `SELECT balance FROM accounts WHERE id = 1` → 100.
- TX B: `UPDATE balance = 200 WHERE id = 1; COMMIT`.
- TX A: `SELECT balance FROM accounts WHERE id = 1` → 200. **Distinto**.

Tu lógica puede romperse si asumió que el valor no cambia.

### Phantom read

Ejecutas la misma **query con condición** dos veces, y obtienes **distinto número de filas** porque otra TX insertó/borró entre medio.

**Ejemplo**:
- TX A: `SELECT count(*) FROM users WHERE active=true` → 50.
- TX B: `INSERT INTO users (...) VALUES (active=true); COMMIT`.
- TX A: `SELECT count(*) FROM users WHERE active=true` → 51.

Las filas anteriores siguen igual (no es non-repeatable read). Pero hay **filas nuevas**.

### Serialization anomaly (write skew)

Caso sutil: dos transacciones leen el mismo dato, basan decisión en él, escriben distintas cosas. Cada una vio el otro NO había escrito todavía.

**Ejemplo médico** (clásico):
- Regla: "siempre debe haber al menos 1 doctor de guardia".
- Doctores Alice y Bob ambos de guardia.
- TX A (Alice): `SELECT count(*) FROM doctors WHERE on_call=true` → 2. `UPDATE doctors SET on_call=false WHERE name='Alice'`. COMMIT.
- TX B (Bob, simultánea): mismo SELECT → 2. UPDATE Bob → COMMIT.
- Resultado: 0 doctores de guardia. Regla rota.

Las dos vieron 2 doctores. Cada una pensó "puedo irme, queda otro". Ninguna anomalía dirty/non-repeatable/phantom ocurrió. Es **write skew**.

---

## 3. Los 4 isolation levels (estándar SQL)

El standard SQL define 4 niveles, ordenados de menos a más estricto. Cada nivel previene un subset de anomalías:

| Nivel | Dirty read | Non-repeatable read | Phantom read | Write skew |
|---|---|---|---|---|
| **READ UNCOMMITTED** | ❌ posible | ❌ posible | ❌ posible | ❌ posible |
| **READ COMMITTED** | ✅ previene | ❌ posible | ❌ posible | ❌ posible |
| **REPEATABLE READ** | ✅ previene | ✅ previene | ❌ posible (en SQL standard) | ❌ posible |
| **SERIALIZABLE** | ✅ previene | ✅ previene | ✅ previene | ✅ previene |

### READ UNCOMMITTED — casi nadie lo usa

Permite todo. Lecturas pueden ver dirty data. **Casi ninguna app real lo usa**. Algunas DBs ni lo implementan (Postgres lo trata como READ COMMITTED).

### READ COMMITTED — el default de muchas DBs

Solo lees datos COMMITTED por otras transacciones. Pero entre dos lecturas tuyas, los datos pueden cambiar (non-repeatable read).

**Postgres default**. Oracle default. SQL Server default (configurable).

**Para qué sirve**: la mayoría de apps. Si tu lógica no asume que los datos no cambian dentro de una TX, READ COMMITTED es suficiente.

### REPEATABLE READ

Garantiza que dentro de UNA transacción, las **mismas queries devuelven los mismos resultados**. Snapshot del momento en que empezó la TX.

**MySQL InnoDB default**. Postgres lo soporta (no es el default).

**Caveat importante en SQL standard**: REPEATABLE READ **no previene phantom reads**. Si haces `SELECT count(*)` dos veces y otra TX inserta filas que matchean, ves números distintos.

**Pero hay diferencias entre DBs**:
- **Postgres REPEATABLE READ**: en realidad es **Snapshot Isolation**. Previene phantoms también (porque snapshot del inicio).
- **MySQL InnoDB REPEATABLE READ**: previene phantoms para SELECT normal pero NO para `SELECT FOR UPDATE`.

**Esta inconsistencia entre DBs es famosa fuente de bugs**.

### SERIALIZABLE — el más estricto

Garantiza que el resultado es **como si las transacciones se hubieran ejecutado serialmente** (una detrás de otra, en algún orden). Previene TODAS las anomalías incluyendo write skew.

**Implementación**:
- **2-Phase Locking (2PL)**: locks pesimistas. Cualquier read bloquea writes y viceversa. Lento bajo carga.
- **Serializable Snapshot Isolation (SSI)**: aproximación optimista. Detecta conflictos al commit y aborta. Es lo que usa Postgres SERIALIZABLE.
- **Actual serial execution**: literalmente ejecutar 1 TX a la vez. Solo viable si las TX son ultra-rápidas (Redis con scripts Lua hace esto).

**Coste**: SERIALIZABLE puede ser 2-10x más lento que READ COMMITTED bajo contención. Pero es la única garantía contra TODAS las anomalías sin pensar en cada caso.

---

## 4. Snapshot Isolation — la variante moderna

Casi todas las DBs modernas implementan **Snapshot Isolation (SI)** además (o en lugar) del REPEATABLE READ clásico:

Cada transacción ve un **snapshot consistente** de la DB del momento en que empezó (o cuando hace su primera lectura). Lecturas no bloquean nada. Writes pueden conflictuar y se resuelven al commit.

**Implementación**: MVCC (Multi-Version Concurrency Control). Cada UPDATE crea una nueva versión, las viejas siguen ahí. Cada TX lee la versión correcta para su snapshot.

**Lo que SI previene**: dirty reads, non-repeatable reads, phantom reads.

**Lo que SI NO previene**: write skew (sección 2). Esto es la diferencia con SERIALIZABLE.

**DBs que usan SI** como modo principal:
- Postgres: REPEATABLE READ es realmente SI.
- Oracle: SERIALIZABLE de Oracle es realmente SI.
- SQL Server: tiene SNAPSHOT ISOLATION explícito.
- MongoDB: snapshot consistency en transactions.
- CockroachDB, Spanner: SI con extensiones.

---

## 5. SSI — Serializable Snapshot Isolation

**SSI** (Postgres lo llama así) extiende Snapshot Isolation para prevenir también write skew, manteniendo el approach optimista (sin locks pesimistas).

**Idea**: durante la TX, la DB **trackea** qué reads y writes hace cada TX. Al commit, detecta si hubo un patrón de "rw-conflict" entre TXs concurrentes que podría causar anomalía. Si lo detecta → aborta una de las TXs.

**Pros**: throughput cercano a snapshot isolation, sin locks pesimistas.
**Contras**: más overhead de tracking, abort rate puede ser alto bajo contención.

Postgres SERIALIZABLE es SSI. Es **la forma más práctica de tener serializability moderna**.

---

## 6. Cómo elegir isolation level

**Default razonable**: READ COMMITTED (Postgres default) o REPEATABLE READ (MySQL default). **El 90% de apps no necesitan más**.

**Sube a SERIALIZABLE cuando**:
- Tu lógica tiene invariantes cross-row (saldos, inventario, no-overbooking).
- No quieres pensar en anomalías caso por caso.
- Tu workload no es ultra-write-heavy donde aborts SSI dolerían.

**Considera bajar a READ UNCOMMITTED**: nunca. Salvo casos muy específicos donde la performance es crítica y aceptas datos corruptos (no se me ocurre uno bueno).

**Patrón pragmático**: usar READ COMMITTED por defecto + `SELECT FOR UPDATE` para casos donde necesites lock explícito en filas críticas.

---

## 7. SELECT FOR UPDATE — locks explícitos

Cuando lees datos que vas a modificar, puedes pedir un lock explícito:

```sql
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- otras TXs que intenten leer FOR UPDATE o modificar esta fila se bloquean
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
```

**Lock pesimista**: bloquea otras TXs hasta tu commit. Garantiza que entre tu read y tu write, nadie cambia el dato.

**Variantes**:
- `FOR UPDATE`: lock exclusivo (otros bloqueados).
- `FOR SHARE`: lock compartido (otros pueden leer FOR SHARE pero no FOR UPDATE).
- `FOR UPDATE NOWAIT`: si no puede adquirir → error inmediato (no espera).
- `FOR UPDATE SKIP LOCKED`: si no puede adquirir → salta esa fila. Útil para colas de tareas.

---

## 8. Optimistic vs Pessimistic concurrency

Dos filosofías de manejar concurrencia:

### Pesimista (locks)

"Asumo que va a haber conflicto, así que bloqueo de antemano". `SELECT FOR UPDATE`, 2PL, etc.

**Pros**: simple de razonar. Si tienes el lock, nadie te puede pisar.
**Contras**: locks pueden bloquear. Deadlocks. Throughput limitado.

### Optimista (versioning)

"Asumo que no va a haber conflicto. Si lo hay, detecto y reintento". MVCC, SSI, version numbers en app.

**Implementación típica en app**:

```sql
-- Read: incluye version number
SELECT id, balance, version FROM accounts WHERE id = 1;
-- supongamos version=5

-- Update: solo si version no cambió
UPDATE accounts SET balance = 50, version = 6
WHERE id = 1 AND version = 5;

-- Si rows_affected = 0 → otra TX cambió → retry o error
```

**Pros**: sin locks. Mucho mejor throughput cuando conflictos son raros.
**Contras**: tienes que reintentar bajo conflicto. App lógica más compleja.

**Cuándo cada uno**:
- Optimista: contención baja, lecturas dominantes.
- Pesimista: contención alta, escrituras críticas que no toleran retry.

---

## 9. Locks bajo el capó

Las DBs usan **muchos tipos de locks** internamente:

- **Row locks**: lock por fila individual.
- **Page locks**: lock por página de disco (varias filas).
- **Table locks**: lock toda la tabla. Pesado.
- **Predicate locks**: lock todas las filas que cumplan condición. Para prevenir phantoms.
- **Index locks / gap locks**: lock en huecos del índice (MySQL InnoDB) para prevenir inserts en rangos.
- **Schema locks**: lock para DDL (ALTER TABLE).

**Lock escalation**: si una TX adquiere demasiados row locks, la DB puede "escalar" a page o table lock para reducir overhead. Útil pero puede causar contención.

Saber esto en detalle es útil para debugging de deadlocks y queries lentas. Para uso normal, no necesitas pensar en ello.

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

JSON sin transacciones. Cuando migres a Postgres: default READ COMMITTED basta. Para operaciones tipo "transferir contacto entre listas", considerar wrap en TX explícita.

Si añades concurrencia (varios workers Uvicorn), cuidado con race conditions tipo "dos workers leen contactos.json, modifican y guardan" → último gana. Solución: mover a Postgres con TX o usar file lock.

### En entrevistas tecnicas

**Pregunta clásica**: "Diferencia entre READ COMMITTED y REPEATABLE READ".

Tu respuesta: READ COMMITTED solo previene dirty reads. REPEATABLE READ además previene non-repeatable reads (mismas queries dentro de TX devuelven mismos resultados). REPEATABLE READ típicamente NO previene phantoms en SQL standard pero Postgres+otras lo hacen vía Snapshot Isolation.

**Pregunta sobre anomalías**: "Qué es phantom read y cómo prevenirlo".

Lecturas con condiciones devuelven distinto número de filas porque otra TX insertó. Prevenido por SERIALIZABLE o por Snapshot Isolation (en Postgres REPEATABLE READ).

**Pregunta avanzada**: "Cómo implementarías inventario sin overselling".

Opciones:
1. SERIALIZABLE isolation (más simple, menos throughput).
2. SELECT FOR UPDATE en la fila del producto + UPDATE atómico.
3. UPDATE con condición en el WHERE: `UPDATE stock SET qty = qty - 1 WHERE id = X AND qty > 0` y check rows_affected.
4. Cola: solo 1 worker procesa orders de cada producto (sin contención).

**Pregunta sobre trade-offs**: "Por qué no usar SERIALIZABLE siempre".

Performance: 2-10x más lento bajo contención. Aborts SSI requieren retry logic. Sobrekill para muchas operaciones.

---

## 11. Trampas típicas

**"REPEATABLE READ es igual en todas las DBs"**: NO. Postgres = Snapshot Isolation (previene phantoms). MySQL InnoDB = standard (no previene phantoms en algunos casos).

**"SERIALIZABLE es siempre seguro"**: garantiza correctness, pero abort rate puede ser alto bajo contención. Necesitas retry logic.

**"Locks son caros, evítalos"**: depende. Para casos críticos con baja contención, FOR UPDATE es la solución más simple.

**"Snapshot isolation = serializable"**: NO. SI no previene write skew. SSI sí.

**"NoSQL no tiene isolation"**: las modernas sí. MongoDB, DynamoDB, FoundationDB tienen niveles configurables.

**"Mi app no necesita transactions"**: si tu app modifica más de 1 row en operaciones lógicas, sí las necesita aunque no lo notes.

**"Long-running transactions están bien"**: NO. Mantienen locks/snapshots → contención + bloat (Postgres MVCC necesita versiones viejas mientras alguna TX las pueda ver). Mantén las TX cortas.

---

## 12. Preguntas típicas de interview

**Las 4 anomalías**: dirty read, non-repeatable read, phantom read, write skew. Saber dar ejemplos.

**Los 4 isolation levels**: read uncommitted, read committed, repeatable read, serializable. Qué previene cada uno.

**Snapshot Isolation**: qué es, qué previene (dirty/non-repeatable/phantom) y qué NO (write skew).

**Optimistic vs pessimistic**: filosofías. Cuándo cada una.

**SELECT FOR UPDATE**: cuándo usarlo. Variantes (NOWAIT, SKIP LOCKED).

**Cómo implementar contador atómico bajo concurrencia**: opciones múltiples — SERIALIZABLE, FOR UPDATE, UPDATE con WHERE condition + retry, atomic ops específicas (INCR en Redis).

**Por qué long-running transactions son malas**: locks/snapshots prolongados, contención, bloat MVCC.

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Las 4 anomalías clásicas con ejemplos.
- Los 4 isolation levels y qué anomalías previene cada uno.
- Diferencia REPEATABLE READ entre Postgres (SI, previene phantoms) y MySQL standard.
- Snapshot Isolation vs Serializable Snapshot Isolation.
- Optimistic (versioning) vs Pessimistic (locks).
- SELECT FOR UPDATE y variantes.
- Patrón de retry con optimistic concurrency.
- Cuándo subir a SERIALIZABLE.

Si no puedes → relee.

---

## Conexiones

- [[01-b-trees-y-indexing]] — locks operan sobre índices
- [[02-acid-transactions]] — la I de ACID
- [[04-replication-y-sharding]] — isolation se complica en distribuido
- [[../06_distributed_systems/01-cap-pacelc]] — la C de CAP no es esto
- [[../03_concurrency/02-locks-y-mutex]] — locks a nivel app
- [[../03_concurrency/01-race-conditions]] — anomalías son tipos de race
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Designing Data-Intensive Applications** capítulo 7 (Transactions) — la mejor explicación.
- **A Critique of ANSI SQL Isolation Levels** (Berenson et al., 1995) — paper clásico que muestra los problemas con la spec original.
- **Postgres docs: Concurrency Control** (postgresql.org/docs/current/mvcc.html).
- **MySQL InnoDB locks reference**.
- **Aphyr Jepsen analyses** — lo que claiman vs lo que realmente garantizan.
