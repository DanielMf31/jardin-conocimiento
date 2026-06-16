# 04 — Replication y sharding

> 📚 **Doc 4 del cluster Database Internals**. Cómo escalas tu DB cuando un solo nodo no aguanta. Replication para disponibilidad/lecturas, sharding para escribir más.
> 🔥 **Frecuencia interview**: aparece en system design siempre. "Cómo escalas tu DB a 100K req/s", "qué pasa si tu DB principal cae".
> ⏱️ **Tiempo de lectura estimado**: 40-55 min.

---

## 1. Los dos problemas distintos: lecturas vs escrituras

Cuando tu DB se queda corta, primero hay que entender QUÉ se está quedando corto:

- **Lecturas**: si tu app hace 90% reads y solo 10% writes, lo que satura es el read throughput. Solución: **replication** — copias de los datos en N nodos, distribuyes lecturas.

- **Escrituras**: si tu app es write-heavy o el dataset no cabe en un solo nodo, replication no ayuda (todos los nodos siguen recibiendo todos los writes). Solución: **sharding** — dividir los datos en N partes, cada nodo lleva una parte.

- **Disponibilidad**: aunque tu DB no esté saturada, quieres que sobreviva caídas. Solución: **replication** (failover a réplica).

Replication y sharding son **ortogonales**: puedes tener uno, el otro, o ambos. Producción típica de sistemas grandes: ambos.

---

## 2. Replication — los modelos

### Single-leader (master-replica)

Un nodo es el **leader** (también llamado primary, master). Los demás son **followers** (replicas, slaves). Solo el leader acepta writes. Los followers reciben writes via **replication log** y los aplican.

Lecturas pueden ir a cualquier nodo. Escrituras solo al leader.

**Pros**:
- Simple. Sin conflictos de write (un solo escritor).
- Lecturas escalables horizontalmente.

**Contras**:
- Leader es SPOF para writes. Si cae, hay que promover follower (failover).
- Replication lag: followers van detrás (ms a segundos).
- Read-your-writes complicado (lees del follower antes de que replique).

**Ejemplos**: MySQL, Postgres, MongoDB (modo replica set), Redis.

### Multi-leader (multi-master)

Múltiples nodos aceptan writes. Cada uno propaga a los demás.

**Pros**:
- Alta disponibilidad para writes (cualquier nodo cae, otros siguen).
- Multi-region: escritor local en cada región (latencia baja).

**Contras**:
- **Conflictos**: dos writes simultáneos al mismo dato en distintos leaders. Requiere resolución (LWW, CRDT, custom).
- Más complejo de razonar.

**Ejemplos**: Cassandra (todos los nodos son leaders), CouchDB, MySQL multi-source replication, DynamoDB multi-region active-active.

### Leaderless (Dynamo-style)

No hay leader. Cualquier nodo acepta writes. El cliente escribe a N nodos y lee de N nodos. Quorum (R + W > N) garantiza consistencia eventual fuerte.

**Pros**: máxima disponibilidad, sin failover (no hay leader que falle).
**Contras**: misma resolución de conflictos. Lecturas pueden devolver versiones distintas.

**Ejemplos**: Cassandra, DynamoDB, Riak.

---

## 3. Cómo se replica realmente — los métodos

### Statement-based replication

El leader envía las queries SQL a los followers, que las re-ejecutan.

**Pros**: simple, log compacto.
**Contras**: NO determinista para queries con `NOW()`, `RAND()`, autoincrement. Tiende a romper sutilmente.

MySQL lo soportó históricamente. Hoy se usa poco.

### Write-ahead log (WAL) shipping

El WAL (que la DB ya escribe para durability) se envía a los followers. Reproducen los cambios físicos exactos.

**Pros**: determinista, eficiente.
**Contras**: acoplado al storage engine. Versiones distintas de la DB pueden no entender el WAL del otro.

Postgres usa esto (streaming replication).

### Logical (row-based) replication

En vez del WAL físico, se envían los cambios en formato lógico (tabla, fila, valores). Independiente del formato físico interno.

**Pros**: permite versiones distintas. Permite replicar subset de tablas.
**Contras**: ligeramente más overhead que WAL shipping.

Postgres logical replication (desde v10), MySQL row-based replication.

### Trigger-based

Triggers en la DB capturan cambios y los exportan. Lento y complejo. Usado por herramientas como Debezium para capturar CDC (Change Data Capture).

---

## 4. Sync vs async replication

### Sync replication

El leader **espera** a que los followers (todos o quórum) confirmen antes de hacer commit al cliente.

**Pros**: garantía de durabilidad cross-replica. Si el leader cae, los followers tienen TODO.
**Contras**: latencia alta (espera red + fsync de followers). Si un follower cae o va lento, el leader bloquea.

### Async replication

El leader hace commit y responde al cliente. **Después** propaga al follower en background.

**Pros**: latencia baja para writes. Followers caídos no bloquean.
**Contras**: si el leader cae con writes no replicados, **se pierden**. Replication lag visible.

### Semi-sync (compromise)

El leader espera a **al menos UN** follower antes de commit. Si el leader cae, ese follower tiene los datos. Pero no espera a todos.

**MySQL semi-sync** y **Postgres `synchronous_commit = remote_write`** son variantes de esto.

**Producción típica**: 2-3 réplicas en sync para garantía + N replicas async para escalado de reads.

---

## 5. Failover — cuando el leader cae

Si el leader cae, hay que **promover un follower** a leader. El proceso (failover) es delicado:

1. **Detectar fallo**: timeouts, health checks. Falsos positivos (network blip vs caída real) son problema.
2. **Elegir nuevo leader**: típicamente el follower más al día (menos lag).
3. **Promover**: el follower se convierte en leader, acepta writes.
4. **Reconfigurar clientes**: apuntar al nuevo leader.
5. **Reincorporar el viejo leader** cuando vuelva (como follower).

**Problemas comunes**:
- **Split-brain**: el viejo leader vuelve y cree que sigue siéndolo. Two leaders → conflictos. Solución: STONITH (Shoot The Other Node In The Head), fencing tokens.
- **Pérdida de datos**: si replication era async, writes no replicados se pierden.
- **Downtime**: failover típicamente 10-60 segundos en sistemas reales.

**Tooling**: Patroni (Postgres), Orchestrator (MySQL), MongoDB built-in.

---

## 6. Read replicas — escalando lecturas

Una vez tienes replication async, los followers pueden servir lecturas. Throughput de read se multiplica por N.

**Caveats**:

- **Replication lag**: lo que escribiste hace 50ms puede no estar en el follower todavía. Si tu app necesita "leer lo que acabas de escribir" (read-your-writes), problema.

  Soluciones: leer del leader para esos casos, sticky sessions a leader durante una ventana, monotonic reads via tokens.

- **Lag bajo carga**: si el leader recibe muchos writes, los followers pueden ir minutos detrás. Monitorear lag es crítico.

- **No todas las queries van a réplicas**: queries que requieren absoluta freshness (e.g. en checkout) deben ir al leader.

---

## 7. Sharding — cuando un nodo no basta

Sharding (también llamado **horizontal partitioning**) divide los datos en N partes que viven en nodos distintos. Cada **shard** es una DB independiente con un subset de los datos.

Lecturas y escrituras se enrutan al shard correcto según una **shard key** (típicamente PK o hash).

### Estrategias de sharding

**Range-based sharding**: cada shard cubre un rango de keys. Ej: shard 1 = users con id 0-1M, shard 2 = 1M-2M, etc.

**Pros**: range queries eficientes.
**Contras**: hot shards (newest IDs reciben todo el tráfico).

**Hash-based sharding**: shard = hash(key) mod N. Distribución uniforme.

**Pros**: balanceo automático.
**Contras**: range queries ineficientes (datos repartidos).

**Consistent hashing**: hash a un círculo. Cuando añades/quitas shards, solo 1/N de las keys se mueven (no todas).

**Pros**: rebalancing barato.
**Contras**: implementación más compleja.

**Geographic / by-tenant**: shard por región o por tenant (multi-tenant SaaS). Datos próximos van juntos.

### Choosing the shard key

Quizás la decisión más importante en sharding. Mala shard key = problemas para siempre.

**Buena shard key**:
- Alta cardinalidad (no booleana).
- Distribución uniforme.
- Aparece en la mayoría de queries (para evitar scatter-gather).
- Inmutable (cambiar shard key requiere mover datos entre shards).

**Ejemplos típicos**:
- `user_id`: queries por usuario van a 1 shard. Bueno para apps user-centric.
- `tenant_id`: SaaS multi-tenant.
- `hash(date)`: workloads de logs/eventos.

### Problemas con sharding

- **Cross-shard queries**: si necesitas datos de varios shards, cada query es scatter-gather (consultar todos, agregar). Lento.
- **Cross-shard transactions**: muy difícil. 2PC clásico bloqueante. Saga / outbox / aceptar inconsistencia.
- **Joins**: cross-shard joins son anti-pattern. Solución: denormalizar o repetir datos.
- **Resharding**: cambiar de N shards a M es operación compleja y arriesgada.

---

## 8. Replication + sharding — el patrón típico

Sistemas grandes combinan ambos:

```
Cluster con K shards × R réplicas = K × R nodos totales.

Ejemplo: 10 shards × 3 réplicas = 30 nodos.
  Cada shard tiene 1 leader + 2 followers.
  Datos divididos en 10 partes.
  Cada parte replicada 3 veces para HA + read scaling.
```

Sistemas que usan esto:
- **MongoDB**: sharded cluster + replica sets dentro de cada shard.
- **Cassandra**: replication factor + tokens (consistent hashing).
- **Vitess**: MySQL sharded usado por YouTube, Slack, GitHub.
- **CockroachDB**: ranges (shards lógicos) + Raft consensus (replication).
- **Spanner**: paxos groups (replication) + tablets (sharding).

---

## 9. CAP / PACELC en contexto

Cuando hay particiones de red (lado del leader cortado del lado de réplicas):

- **CP**: el lado sin quorum rechaza requests. Consistencia, no disponibilidad parcial.
- **AP**: ambos lados siguen aceptando. Disponibilidad, posibles conflictos.

PACELC añade: incluso sin partición, replicación tiene trade-off:
- **EC** (else consistency): sync replication, latencia mayor.
- **EL** (else latency): async, eventual consistency.

Ver [[../06_distributed_systems/01-cap-pacelc]] para detalle.

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Hoy single instance JSON. Sin replication ni sharding.

Cuando crezca:
1. **Primero**: migrar a Postgres single-instance.
2. **Después**: añadir read replicas (Postgres streaming replication).
3. **Mucho después**: si crece a millones de contactos, sharding por user_id.

Realísticamente para un proyecto personal, single Postgres con backups regulares cubre años.

### En entrevistas tecnicas

**Pregunta clásica**: "Cómo escalas tu DB cuando se queda corta".

Tu respuesta:
1. Identificar bottleneck: reads o writes.
2. Si reads: read replicas async.
3. Si writes: sharding por shard key apropiada.
4. Si ambos: replication + sharding (cada shard con réplicas).

**Pregunta sobre failover**: "Qué pasa si tu DB principal cae".

Failover automático con tooling (Patroni). Promover follower al día. Reconfigurar clientes (DNS o config dinámica). Aceptar pérdida de writes no replicados (si async). Downtime típico 10-60s.

**Pregunta sobre sharding**: "Cómo eliges la shard key".

Alta cardinalidad, distribución uniforme, aparece en la mayoría de queries para evitar scatter-gather, inmutable. Para apps user-centric: user_id. Para multi-tenant: tenant_id.

**Pregunta avanzada**: "Diseña sistema multi-region con baja latencia".

Multi-leader replication por región. Cada región tiene leader local (writes locales rápidos). Replicación async cross-region. Resolución de conflictos via LWW o CRDT. Sharding por región para datos region-scoped (no todos).

---

## 11. Trampas típicas

**"Más réplicas = más rápido"**: solo para reads. Writes no escalan con replication. Para writes necesitas sharding.

**"Sharding desde día 1"**: anti-pattern. Premature optimization. Single instance + read replicas cubre la mayoría de casos durante años.

**"Failover es instantáneo"**: 10-60s típico. Para apps que requieren 99.99% uptime, hay que diseñar para eso (retry logic, queueing).

**"Multi-leader resuelve todo"**: introduce conflictos. Si tu app tiene invariantes cross-row (saldos), multi-leader puede corromper datos.

**"Cross-shard joins son posibles"**: técnicamente sí (scatter-gather), pero lentísimo. Anti-pattern. Denormalizar.

**"Resharding es trivial"**: NO. Es operación arriesgada que requiere planning meticuloso. Algunos sistemas (CockroachDB) lo hacen automático con menos dolor.

**"Sync replication = sin pérdida de datos"**: sin pérdida si TODOS los nodos sync no caen simultáneamente. Si caen → pérdida. Soluciones: 3+ réplicas en zonas distintas.

---

## 12. Preguntas típicas de interview

**Single-leader vs multi-leader vs leaderless**: ya cubierto sección 2.

**Sync vs async replication**: cubierto sección 4. Trade-off latency vs durabilidad.

**Cómo escalas reads vs writes**: reads → replication. Writes → sharding.

**Cómo eliges shard key**: criterios sección 7.

**Problemas con sharding**: cross-shard queries, transactions, joins, resharding.

**Replication lag — qué problemas causa**: read-your-writes rota. Soluciones: leer del leader para casos críticos, sticky sessions, version tokens.

**Failover — proceso y problemas**: detect → promote → reconfigure → reincorporate. Split-brain, pérdida de datos async, downtime.

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Diferencia entre escalar reads (replication) y writes (sharding).
- Single-leader vs multi-leader vs leaderless.
- Sync vs async replication, trade-offs.
- WAL shipping vs logical replication.
- Failover process y problemas (split-brain).
- Estrategias de sharding (range, hash, consistent hashing, geographic).
- Cómo elegir shard key.
- Problemas con sharding (cross-shard queries, joins, transactions).
- Patrón típico replication + sharding combinados.

Si no puedes → relee.

---

## Conexiones

- [[01-b-trees-y-indexing]] — índices se replican también
- [[02-acid-transactions]] — transactions cross-shard son problema
- [[03-isolation-levels]] — isolation se complica en distribuido
- [[05-sql-vs-nosql-tradeoffs]] — modelos distintos
- [[../06_distributed_systems/01-cap-pacelc]] — los trade-offs fundamentales
- [[../06_distributed_systems/02-consensus-paxos-raft]] — base de replication CP moderna
- [[../06_distributed_systems/03-eventual-consistency]] — el modelo de muchas DBs distribuidas
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Designing Data-Intensive Applications** capítulos 5 (Replication) y 6 (Partitioning) — el referente.
- **MongoDB sharded cluster docs** — ejemplo bien documentado.
- **Vitess docs** — sharding sobre MySQL real-world.
- **CockroachDB docs** — modern approach automático.
- **Postgres streaming replication** docs.
- **Patroni** (github.com/zalando/patroni) — failover automation Postgres.
