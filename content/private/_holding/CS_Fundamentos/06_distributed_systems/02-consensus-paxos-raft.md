# 02 — Consensus: Paxos y Raft

> **Doc 2 del cluster Distributed Systems**. Cómo varios nodos se ponen de acuerdo en algo cuando la red es no fiable. El problema más fundamental de sistemas distribuidos.
> **Frecuencia interview**: aparece en system design senior. Saber qué es Raft y por qué existe te diferencia.
> **Tiempo de lectura estimado**: 40-55 min.

---

## 1. Por qué consensus es el problema duro

Imagina 3 servidores que necesitan estar de acuerdo en quién es el "líder" para procesar writes. Suena trivial: "votad". Pero en un sistema distribuido real:

- Mensajes pueden **perderse** en la red.
- Mensajes pueden **llegar duplicados**.
- Mensajes pueden **llegar en distinto orden** a distintos nodos.
- Nodos pueden **caerse** y reaparecer más tarde.
- Un nodo puede **estar lento** indistinguible de "caído".
- La **red puede partirse** en grupos que no se ven.

El problema es: **¿cómo garantizar que todos los nodos vivos lleguen a la misma decisión, sin importar qué falle?**

Esto es **consensus**. Y es **demostrablemente difícil**: el teorema FLP (Fischer-Lynch-Paterson, 1985) prueba que **es imposible garantizar consensus en un sistema asíncrono con un solo fallo**, en tiempo finito.

Los algoritmos prácticos (Paxos, Raft) **rodean** este resultado asumiendo timeouts y mayorías, sacrificando teoría por practicidad. Funcionan en la práctica aunque teóricamente puedan no terminar (en escenarios adversariales muy específicos).

---

## 2. Para qué se usa consensus en sistemas reales

Consensus no es un fin en sí mismo. Es la **primitiva fundamental** sobre la que se construyen muchas cosas:

- **Leader election**: elegir qué nodo coordina (writes a la BD, scheduler de tareas).
- **Replicated state machines**: garantizar que N réplicas aplican la misma secuencia de operaciones (base de cualquier BD distribuida consistente).
- **Distributed locks**: ¿quién tiene el lock? Consensus.
- **Configuration management**: cambios en config consistentes a todos los nodos.
- **Membership**: qué nodos forman parte del cluster ahora.

Sistemas que **internamente usan Raft o Paxos**: Etcd, Zookeeper, Consul, CockroachDB, TiDB, Spanner, Kafka (KRaft mode), MongoDB (modo replica set).

---

## 3. Paxos — el original (Leslie Lamport, 1989)

Paxos es el algoritmo clásico de consensus. **Probablemente correcto** y **demostradamente difícil de entender**. Lamport mismo bromeó publicando el paper como "The Part-Time Parliament" usando metáfora de un parlamento ficticio en una isla griega — y nadie lo entendió. Tuvo que reescribirlo en "Paxos Made Simple" años después.

### Idea básica

Tres roles: **proposers** (quieren proponer un valor), **acceptors** (votan), **learners** (descubren la decisión). Un nodo puede tener varios roles.

El algoritmo trabaja en **2 fases**:

**Fase 1 — Prepare/Promise**: el proposer manda un número de propuesta `n` a una **mayoría** de acceptors. Cada acceptor responde "promise: no aceptaré propuestas con número < n". Si alguno ya aceptó algo previamente, devuelve ese valor.

**Fase 2 — Accept/Accepted**: el proposer manda "accept(n, valor)". Acceptors aceptan si no han prometido a alguien con número mayor. Si una mayoría acepta, el valor está **decidido**.

### Por qué funciona (intuición)

La clave es la **mayoría**. Cualquier dos mayorías de un set se superponen en al menos un nodo. Ese nodo "recuerda" lo que prometió y bloquea decisiones contradictorias. Garantiza que **una vez decidido un valor, todas las propuestas futuras vean ese valor**.

### Por qué es complejo

- Los papers asumen "asíncrono pero con timeouts vagos".
- Maneja casos edge (proposers compitiendo, mensajes retrasados) de forma sutil.
- Para usar Paxos en producción real, necesitas **Multi-Paxos** (decidir secuencias de valores), **Cheap Paxos**, **Fast Paxos**, **Generalized Paxos**... cada variante con sus particularidades.

**Por eso casi nadie usa Paxos directamente** en código nuevo. Se usa Raft.

---

## 4. Raft — el moderno y entendible (Ongaro & Ousterhout, 2014)

Raft fue diseñado **explícitamente para ser entendible**. Mismo poder que Multi-Paxos, mucho más fácil de implementar correctamente. Hoy es **el estándar de facto** para nuevos sistemas que necesitan consensus.

### Roles

En Raft, en cada momento cada nodo está en uno de 3 estados:

- **Leader**: el único que acepta writes de clientes y los replica.
- **Follower**: réplica pasiva. Recibe writes del leader.
- **Candidate**: estado transitorio durante elección de leader.

**En cualquier momento solo hay UN leader** (en cada term). Esta simplificación es la clave de la entendibilidad.

### Las dos sub-problemas que Raft separa

Raft es entendible porque divide el problema en dos cosas independientes:

1. **Leader election**: elegir UN líder.
2. **Log replication**: el líder replica una secuencia ordenada de operaciones a los followers.

### Leader election

Cada nodo tiene un **timeout aleatorio** (150-300ms típicamente). Si un follower no oye al leader en ese timeout, se convierte en **candidate** y pide votos.

Si recibe votos de la **mayoría**, se convierte en **leader** y empieza a enviar **heartbeats** para mantener su autoridad.

**El timeout aleatorio** es la magia anti-split-vote: si dos nodos arrancan a la vez, sus timeouts diferentes hacen que uno gane antes que otro empiece. La aleatoriedad rompe simetrías.

### Log replication

El leader recibe writes de clientes y los añade a su **log**. Después manda `AppendEntries` RPCs a los followers replicando la entrada. Cuando una **mayoría** de followers ha replicado, la entrada se considera **committed** y se aplica al state machine.

Si un follower va atrasado, el leader le manda las entradas que le faltan. Si hay inconsistencias (follower tiene entries del log de un leader anterior), el leader **fuerza al follower a copiar el suyo**.

### Term — el mecanismo de versionado

Cada elección crea un nuevo **term** (número monotónico). Solo el leader del term actual tiene autoridad. Si un nodo recibe un mensaje con term mayor, sabe que hay un nuevo leader y pasa a follower.

Términos resuelven el problema de "leader viejo despierta y cree que sigue siendo leader" — su term es viejo, sus mensajes se rechazan.

### Garantías de Raft

- **Election Safety**: a lo más un leader por term.
- **Leader Append-Only**: el leader nunca borra ni reescribe entries.
- **Log Matching**: si dos logs tienen una entry con mismo index y term, son idénticos hasta ese punto.
- **Leader Completeness**: una entry committed en un term aparecerá en logs de todos los leaders futuros.
- **State Machine Safety**: si un nodo aplicó entry en un index, ningún otro aplicará algo distinto en ese index.

Estas 5 propiedades juntas implican **linearizabilidad** del sistema replicado.

---

## 5. Quorum — el concepto crítico

Tanto Paxos como Raft requieren **mayoría** (más de la mitad) de nodos activos para progresar. Esto es **quorum**.

Para N nodos, el quorum es `floor(N/2) + 1`:
- N=3 → quorum=2 (tolera 1 fallo).
- N=5 → quorum=3 (tolera 2 fallos).
- N=7 → quorum=4 (tolera 3 fallos).

**Por qué impar**: N=4 → quorum=3, tolera 1 fallo (igual que N=3). N=6 → quorum=4, tolera 2 (igual que N=5). **Pares no añaden tolerancia**, solo coste. Por eso clusters de Etcd/Zookeeper/Consul son siempre 3, 5 o 7 nodos.

### Por qué quorum garantiza consistencia

Cualquier dos quorums se intersectan en al menos un nodo. Ese nodo "sabe" lo último decidido y bloquea decisiones contradictorias.

### Trade-off

- **Cluster pequeño (3 nodos)**: rápido, barato, tolera 1 fallo.
- **Cluster grande (7-9 nodos)**: tolera más fallos, pero CADA write necesita confirmación de la mayoría → latencia mayor.

Producción típica: **5 nodos** es el sweet spot para sistemas críticos. **3 nodos** para casos menos críticos o donde la latencia importa.

---

## 6. Multi-region consensus — el caso difícil

Si tus 5 nodos están en el mismo datacenter, latencia inter-nodo es <1ms. Quorum confirma writes en ~5ms.

Si pones nodos en regiones distintas (US East, US West, EU), latencia inter-nodo es 50-200ms. Quorum confirma en ~150ms. **Cada write tarda 150ms**. Inviable para apps user-facing.

**Soluciones**:
- **Quorum por región**: lecturas locales (eventual), writes globales con consensus (lentos).
- **Sharding por región**: cada shard tiene su quorum local. Writes locales rápidos, cross-region lentos.
- **Spanner-style con TrueTime**: relojes atómicos sincronizados permiten consenso geográfico con latencia más baja (pero infraestructura cara).

Esta es una de las razones por las que **bases de datos multi-region son difíciles** y caras.

---

## 7. Failures y recuperación

Raft maneja varios escenarios de fallo:

**Leader cae**: followers no reciben heartbeat → timeout → election. Nuevo leader en ~150-300ms (depende del timeout configurado).

**Follower cae**: leader sigue funcionando si todavía hay quorum. Follower al volver pide al leader las entries que perdió.

**Partición de red**: el lado con quorum sigue funcionando. El lado sin quorum se queda bloqueado (no acepta writes). Cuando se reúne, los del lado minoritario sincronizan.

**Split-brain prevention**: si un leader queda aislado en partición sin quorum, NO puede committear (no tiene mayoría). El otro lado elige nuevo leader. Cuando se reúnen, el viejo leader ve term mayor y abandona.

Esta robustez ante particiones es por qué Raft es **CP** en el espectro CAP — sacrifica disponibilidad del lado minoritario para garantizar consistencia.

---

## 8. ¿Cuándo NO usar consensus?

Consensus es **caro**. Cada operación requiere round-trips entre nodos para alcanzar quorum. Para muchos casos, **eventual consistency es suficiente y mucho más rápida**.

**Usa consensus cuando**:
- Los datos son críticos y debes garantizar consistencia (saldos, inventario, locks).
- El volumen de writes no es masivo (consensus tiene throughput limitado).
- La latencia mayor es aceptable.

**Evita consensus cuando**:
- Eventual consistency es aceptable (feeds, analytics, métricas).
- Necesitas throughput muy alto (consensus serializa, eventual paraleliza).
- Tu workload es read-heavy con writes raros (read replicas eventual son más simples).

---

## 9. Implementaciones populares

**Etcd (CoreOS, ahora Kubernetes)**: Raft en Go. Usado por Kubernetes para almacenar todo el cluster state. Es probablemente el sistema Raft más usado del mundo.

**Zookeeper (Apache)**: usa Zab (similar a Paxos). Veterano. Usado por Hadoop, Kafka (hasta v3), HBase.

**Consul (HashiCorp)**: Raft en Go. Service discovery + KV store.

**CockroachDB**: Raft por shard. Cada partición de datos tiene su grupo Raft. Permite escalar consensus horizontalmente.

**TiDB / TiKV**: Raft, similar a CockroachDB.

**MongoDB Replica Set**: protocolo propio inspirado en Raft.

**Kafka KRaft mode**: desde v3, Kafka migró de Zookeeper a su propio Raft interno.

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

No necesitas consensus. Single-instance Postgres o JSON sirven. Cuando arquitectes algo distribuido (cluster Kubernetes para embebido, por ejemplo), tendrás Raft funcionando "debajo" en Etcd sin que lo veas.

### En entrevistas tecnicas

**Pregunta clásica**: "Cómo eliges el leader en un sistema distribuido". Respuesta: leader election via Raft, con timeouts aleatorios para evitar split-vote.

**Pregunta avanzada**: "Diseña un sistema de distributed locks".
1. Cluster Etcd (3-5 nodos) con Raft.
2. Lock = clave en Etcd con TTL.
3. Cliente intenta crear con `if not exists`.
4. Si tiene éxito, refresca TTL periódicamente (lease).
5. Si crashea, TTL expira y lock se libera.

**Pregunta sobre trade-offs**: "Por qué no usar consensus para todo".
Latencia (cada op necesita quorum), throughput limitado (serialización), coste (más nodos), complejidad operativa. Para datos no críticos, eventual consistency es mejor.

---

## 11. Trampas típicas

**"Raft es para lecturas y escrituras rápidas"**: NO. Raft prioriza correctness sobre throughput. Es 10-100x más lento que un sistema eventual.

**"Más nodos = más rápido"**: al revés. Más nodos = quorum más grande = más latencia por escritura.

**"4 nodos = mejor que 3"**: NO. Mismo nivel de tolerancia (1 fallo) con coste mayor. Siempre número impar.

**"Si tengo Raft, no necesito locks"**: Raft te da consensus sobre operaciones, no sobre acceso. Sigues necesitando locks/transactions para coordinar accesos.

**"Si la red se parte, ambos lados siguen"**: solo el lado con quorum sigue. El otro queda bloqueado para writes. Esa es la garantía CP.

**"Consensus = consistencia perfecta"**: garantiza linealizabilidad. No protege contra bugs en tu app, race conditions en cliente, errores humanos.

**"Voy a implementar Raft yo mismo"**: NO. Usa una librería (etcd/raft, hashicorp/raft, MIT 6.824 implementación de referencia). Implementar correctly es trabajo de meses-años. Casos edge te van a pillar.

---

## 12. Preguntas típicas de interview

**¿Qué es consensus y por qué es difícil?**: ponerse de acuerdo entre N nodos cuando la red es no fiable. FLP demuestra imposibilidad teórica con asincronía + 1 fallo. Algoritmos prácticos rodean con timeouts.

**Diferencia Paxos vs Raft**: ambos resuelven consensus. Paxos es original, complejo, varias variantes. Raft es moderno, separa leader election y log replication, mucho más entendible.

**Explica leader election en Raft**: timeout aleatorio → candidate → pide votos → si mayoría → leader. Aleatoriedad rompe simetrías.

**Por qué número impar de nodos**: par no añade tolerancia, solo coste. 3, 5, 7 son típicos.

**Multi-region consensus problemas**: latencia inter-región (50-200ms) hace cada write lento. Soluciones: sharding por región, Spanner-style.

**Cuándo NO usar consensus**: datos no críticos donde eventual consistency basta. Es 10-100x más lento.

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Qué es consensus y por qué es el problema fundamental.
- Por qué FLP dice "imposible teóricamente" pero los algoritmos funcionan.
- Diferencia Paxos vs Raft (Paxos primero pero complejo, Raft moderno y entendible).
- Roles en Raft: leader, follower, candidate.
- Cómo funciona leader election (timeout aleatorio + votos).
- Quorum: por qué mayoría, por qué impar.
- Trade-off de Raft: CP, latencia mayor, throughput menor.
- Sistemas que usan Raft (Etcd, Consul, CockroachDB, KRaft).

Si no puedes → relee.

---

## Conexiones

- [[01-cap-pacelc]] — Raft es CP en CAP
- [[03-eventual-consistency]] — la alternativa cuando consensus es overkill
- [[04-distributed-tracing]] — debugging de sistemas con consensus
- [[../05_database_internals/04-replication-y-sharding]] — replication usa consensus
- [[../03_concurrency/02-locks-y-mutex]] — distributed locks usan consensus
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Raft paper original** (raft.github.io) — In Search of an Understandable Consensus Algorithm. Lectura obligatoria.
- **The Raft visualization** (raft.github.io) — visualización interactiva. Buenísima.
- **MIT 6.824 Distributed Systems** — curso completo gratis en YouTube, implementas Raft.
- **Designing Data-Intensive Applications** capítulo 9 (Consistency and Consensus).
- **Paxos Made Simple** (Lamport) — el rewrite intentando ser claro. Aún denso.
- **Etcd source code** (github.com/etcd-io/etcd) — Raft implementado en Go, referencia.
- **Aphyr's Jepsen** — tests reales que rompen sistemas que claiman ser correctos.
