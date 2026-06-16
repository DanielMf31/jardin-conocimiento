# 02 — ACID y transactions

> 📚 **Doc 2 del cluster Database Internals**. La razón por la que confías en tu DB con datos críticos. Las garantías que distinguen una DB seria de un archivo glorificado.
> 🔥 **Frecuencia interview**: aparece en backend interviews siempre. "Explica ACID", "qué es una transacción", "cómo garantiza consistencia tu DB".
> ⏱️ **Tiempo de lectura estimado**: 35-50 min.

---

## 1. Qué es una transacción

Una **transacción** es un grupo de operaciones que la DB ejecuta como **una unidad atómica**: o se completan TODAS o no se aplica NINGUNA. Si algo falla a medias, la DB revierte todo al estado anterior (rollback).

El ejemplo clásico es la **transferencia bancaria**:

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

Si entre los dos UPDATEs cae el server, sin transacciones: la cuenta 1 perdió 100€ y la 2 no recibió nada. **100€ desaparecieron**. Con transacciones: ambos updates están en una transacción, si algo falla → rollback → los 100€ siguen en la cuenta 1.

Las transacciones son **el contrato fundamental** entre tu app y la DB. Sin ellas, programar lógica financiera o cualquier dato crítico sería imposible.

---

## 2. ACID — las 4 garantías

ACID es el acrónimo de las 4 propiedades que define una transacción "seria". Acuñado por Härder y Reuter en 1983.

### Atomicity

**Todo o nada**. Si una transacción tiene N operaciones, o se completan las N o se completa 0. Nunca un estado intermedio.

Esto se implementa típicamente con un **write-ahead log (WAL)**: antes de modificar las tablas reales, la DB escribe en el log "voy a hacer X". Si crashea a medias, al reiniciar lee el log y o **redo** (re-aplicar lo que faltaba) o **undo** (revertir lo aplicado).

### Consistency

La transacción **deja la DB en un estado válido** según las reglas definidas (constraints, foreign keys, triggers, invariantes de la app). Si la transacción violaría una regla, se aborta.

**OJO con la confusión**: la C de ACID **no es** la C de CAP. Aquí "consistency" se refiere a **invariantes definidas por ti** (constraints, etc.), no a "todas las réplicas ven el mismo valor".

Esta C es en realidad responsabilidad parcial de la app: la DB enforce constraints (NOT NULL, FK, CHECK) pero las invariantes de negocio las defines tú.

### Isolation

**Transacciones concurrentes no interfieren entre sí**. El resultado debería ser como si se ejecutaran una detrás de otra (serial), aunque en realidad la DB las solapa para mejorar throughput.

Esta es la propiedad MÁS compleja. Tiene **niveles** (Read Uncommitted, Read Committed, Repeatable Read, Serializable) con trade-offs entre consistencia y performance. Tan importante que tiene un doc dedicado: ver [[03-isolation-levels]].

### Durability

Una vez **committed**, los cambios sobreviven aunque caiga la luz al instante después. Garantizado típicamente con **fsync()** (forzar el write a disco físico) antes de confirmar el commit al cliente.

Es por esto que `fsync()` es caro pero crítico — sin él la D de ACID se rompe.

---

## 3. WAL — el corazón de A y D

El **Write-Ahead Log** (WAL) es la técnica fundamental que garantiza atomicity y durability:

- **Antes** de modificar las páginas de datos, escribir el cambio al log.
- El log es **append-only** (escrituras secuenciales = rapidísimas en disco).
- Cuando se hace COMMIT, **fsync()** del log → garantizado en disco.
- Después se aplican los cambios a las páginas de datos en background.
- Si crashea: al reiniciar, lee el log desde el último checkpoint y replay.

**Por qué funciona**:
- Si crashea ANTES del COMMIT: los cambios están en log pero marcados como pending → undo.
- Si crashea DESPUÉS del COMMIT: los cambios están en log committed → redo cuando la DB vuelva.

**Beneficios secundarios**:
- Replication: enviar el WAL a réplicas → reproducen el mismo estado.
- Point-in-time recovery: replay del WAL hasta cierto timestamp.

Postgres lo llama WAL. MySQL InnoDB lo llama redo log + undo log. SQLite tiene modo WAL. Casi toda DB seria usa esta técnica.

---

## 4. Cómo se implementa rollback

Si una transacción aborta (por error o por `ROLLBACK` explícito), la DB tiene que **revertir** todos los cambios hechos. Hay dos enfoques:

### Undo log

Antes de modificar un valor, guardar el viejo en un undo log. Si rollback: leer el undo log y restaurar.

MySQL InnoDB usa undo logs (en tablespace separado, llamado "rollback segments").

### Multi-version (MVCC)

En vez de modificar in-place, escribir una **nueva versión** del registro. La vieja sigue ahí. Las transacciones que estaban activas antes ven la versión vieja, las nuevas ven la nueva. Rollback = simplemente marcar la nueva como inválida.

Postgres usa MVCC. CockroachDB también. La mayoría de DBs modernas tienden a MVCC.

**Ventajas de MVCC**:
- Lecturas no bloquean escrituras y viceversa.
- Snapshots consistentes muy baratos.
- Mejor concurrency.

**Desventajas**:
- Necesita VACUUM/garbage collection para limpiar versiones viejas.
- Storage overhead.

---

## 5. Savepoints — transacciones anidadas

A veces dentro de una transacción quieres poder revertir solo una parte:

```sql
BEGIN;
INSERT INTO orders (...) VALUES (...);
SAVEPOINT sp1;
INSERT INTO order_items (...) VALUES (...);
-- si falla:
ROLLBACK TO sp1;
-- el INSERT de orders sigue. Solo se revierte order_items.
COMMIT;
```

Útil para lógica compleja con sub-pasos opcionales. Disponible en Postgres, MySQL, Oracle.

---

## 6. ACID vs BASE — el debate

A finales de 2000s, con la explosión de NoSQL, surgió **BASE** como filosofía opuesta a ACID:

- **B**asically Available
- **S**oft state
- **E**ventual consistency

BASE prioriza **disponibilidad y escalabilidad** sobre consistencia estricta. Cassandra, DynamoDB, Riak históricamente eran BASE.

**El debate**: ACID es más caro (sync, fsyncs, locks). BASE escala mejor pero la app debe lidiar con inconsistencias.

**Realidad moderna**: la dicotomía se ha disuelto. DBs "NoSQL" modernas ofrecen transacciones ACID (DynamoDB añadió transactions en 2018, MongoDB en 4.0, FoundationDB siempre lo tuvo). DBs "SQL" pueden configurarse en modos relajados.

**No es ACID o BASE absoluto**. Es: qué nivel de garantía necesita CADA operación.

---

## 7. Two-phase commit (2PC) — transacciones distribuidas

Cuando una transacción afecta a **múltiples DBs**, el problema se complica. Si uno hace commit y el otro falla, inconsistencia.

**2PC** es el algoritmo clásico:

**Fase 1 — Prepare**: el coordinator pregunta a cada participant "¿puedes commitear?". Cada uno responde "yes" (y promete poder commitear si se le pide después) o "no".

**Fase 2 — Commit/Abort**: si TODOS dijeron yes → coordinator manda "commit" a todos. Si alguno dijo no → "abort" a todos.

**Problemas de 2PC**:
- **Bloqueante**: si el coordinator cae después de fase 1, los participants se quedan esperando con sus locks.
- **Lento**: doble round-trip + necesita disponibilidad de todos.
- **No tolerante a particiones**: cualquier nodo caído bloquea.

**Por qué casi nadie lo usa hoy**: prefieren **patrones alternativos**:
- **Saga**: dividir en sub-transacciones con compensaciones (ver [[../04_system_design_patterns/03-message-queues]]).
- **Outbox pattern**: escribir DB y mensaje en misma TX, worker async publica.
- **Eventual consistency**: aceptar inconsistencia temporal.

2PC es más teoría histórica que herramienta común hoy.

---

## 8. Idempotencia — el patrón cliente

Independiente de ACID server-side, los **clientes** deben diseñarse pensando en retries. Si un request se cae sin saber si la TX se aplicó, el cliente puede reintentar y duplicar.

**Solución**: idempotency keys. El cliente genera un UUID por request. La DB rechaza requests con UUID ya procesado.

Stripe API es el ejemplo canonical:

```python
import requests
requests.post(
    "https://api.stripe.com/v1/charges",
    headers={"Idempotency-Key": "uuid-del-cliente"},
    data={"amount": 1000, "currency": "usd"}
)
```

Si Stripe procesó el cargo pero la respuesta se perdió, retry con mismo UUID devuelve el resultado anterior. **Cero double-charges**.

---

## 9. ACID en sistemas distribuidos modernos

Históricamente "ACID = no escala, BASE = escala". Esa creencia ya no es del todo cierta:

- **Spanner (Google)**: ACID con strong consistency a escala global. TrueTime API hace consensus eficiente.
- **CockroachDB**: ACID distribuido inspirado en Spanner.
- **TiDB**: similar.
- **FoundationDB (Apple)**: ACID puro distribuido. Multi-key transactions.
- **PlanetScale**: MySQL escalado horizontalmente con ACID.

El secreto suele ser: **Raft/Paxos** para coordinación + **timestamp-based ordering** + **MVCC**. ACID a escala es posible, solo es más caro.

Pero para muchos casos NO necesitas ACID full distribuido. Eventual o ACID single-region suelen bastar.

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Hoy: JSON sin transacciones. Si tu app crashea entre `load + modify + save`, puedes tener archivo corrupto.

Cuando migres a Postgres, transacciones automáticas para lecturas. Para escrituras múltiples (ej: mover contacto entre grupos), envolver en `BEGIN/COMMIT`.

SQLAlchemy maneja esto: cada session es una transacción implícita, `session.commit()` cierra.

### En entrevistas tecnicas

**Pregunta clásica**: "Explica ACID".

Tu respuesta: 4 propiedades de transacciones. A=todo o nada. C=mantiene invariantes. I=concurrentes no interfieren. D=committed sobrevive crash.

**Pregunta sobre implementación**: "Cómo garantiza tu DB durability".

WAL + fsync(). Antes de confirmar commit, escribir log a disco con fsync. Si crashea después, al reiniciar replay del log.

**Pregunta sobre trade-offs**: "Por qué fsync es lento".

Operación de disco real (no cache). 1-10ms en SSD, decenas en HDD. Limita throughput de transacciones. Soluciones: group commit (batch múltiples commits en un fsync).

**Pregunta avanzada**: "Cómo harías transacciones distribuidas".

2PC clásico (bloqueante, lento). Mejor: Saga pattern, outbox, eventual consistency. Para ACID distribuido real: Spanner-style con TrueTime o Raft + timestamps.

**Pregunta sobre idempotencia**: "Cómo evitas double-charges en API de pagos".

Idempotency keys (UUID por request). Server guarda mapping UUID → resultado. Reintento con mismo UUID devuelve resultado anterior, no procesa de nuevo.

---

## 11. Trampas típicas

**"ACID significa que los datos están perfectos siempre"**: NO. ACID es contrato dentro de transacciones. Bugs en tu app pueden meter datos malos válidos.

**"ACID consistency = CAP consistency"**: NO. La C de ACID es invariantes de negocio. La C de CAP es replicación.

**"Las transacciones son gratis"**: tienen coste. Locks, writes al WAL, fsyncs. En workloads con TX largas y muchas concurrentes, contention puede degradar mucho.

**"NoSQL no tiene transacciones"**: anticuado. La mayoría de NoSQL modernas las tienen ahora.

**"2PC resuelve transacciones distribuidas"**: técnicamente sí, pero es bloqueante y lento. La industria moderna prefiere alternativas.

**"COMMIT siempre triunfa"**: puede fallar (constraint violation, deadlock victim, network error). Tu código debe manejar el error.

**"Locks de DB son pequeños y rápidos"**: pueden escalar mal. Long-running TX manteniendo locks bloquean a otras. Mantén las TX cortas.

---

## 12. Preguntas típicas de interview

**Define ACID**: las 4 propiedades. Atomicity, Consistency, Isolation, Durability.

**WAL — qué es y por qué**: log secuencial de cambios pendientes antes de aplicarlos. Garantiza atomicity (rollback) y durability (recovery tras crash).

**Diferencia ACID vs BASE**: ACID prioriza consistency, BASE prioriza availability/scalability. Históricamente "SQL=ACID, NoSQL=BASE", hoy más mezclado.

**MVCC vs locking**: MVCC = nuevas versiones, lecturas no bloquean. Locking = locks pesimistas, contención bajo carga.

**2PC y problemas**: distributed commit en 2 fases. Bloqueante si coordinator cae. Reemplazado por Saga, outbox, etc.

**Cómo garantizas exactly-once en pagos**: idempotency keys. Cliente UUID por request, server detecta duplicados.

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Definición de transacción (todo o nada).
- Las 4 propiedades ACID y qué garantiza cada una.
- Diferencia C de ACID vs C de CAP.
- WAL como mecanismo de A y D.
- MVCC vs undo log para implementar rollback.
- Por qué fsync es caro y necesario.
- Saga / outbox como alternativas modernas a 2PC.
- Idempotency keys para retries seguros.

Si no puedes → relee.

---

## Conexiones

- [[01-b-trees-y-indexing]] — índices participan en transacciones
- [[03-isolation-levels]] — la I de ACID en profundidad
- [[04-replication-y-sharding]] — replicación con transactions
- [[../06_distributed_systems/01-cap-pacelc]] — la C de ACID NO es la C de CAP
- [[../06_distributed_systems/02-consensus-paxos-raft]] — base de DBs ACID distribuidas
- [[../04_system_design_patterns/03-message-queues]] — Saga + outbox
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Designing Data-Intensive Applications** capítulo 7 (Transactions) — la mejor explicación moderna.
- **Postgres docs: WAL** (postgresql.org/docs/current/wal.html).
- **MySQL InnoDB redo/undo logs** docs.
- **Spanner paper** (Google, 2012) — ACID a escala global.
- **Stripe API docs: Idempotency** — patrón industry-standard.
- **Aphyr Jepsen** — tests de claims de transactionality. Brutal.
