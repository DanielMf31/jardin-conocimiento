# 03 — Eventual consistency

> 📚 **Doc 3 del cluster Distributed Systems**. La alternativa pragmática a strong consistency. Lo que usan Twitter, Facebook, DynamoDB, Cassandra y la mayoría de sistemas a escala web.
> 🔥 **Frecuencia interview**: aparece cada vez que se discute escalar a millones de usuarios. Saber explicar bien los trade-offs es marca de seniority.
> ⏱️ **Tiempo de lectura estimado**: 35-50 min.

---

## 1. Qué es eventual consistency (la definición precisa)

**Eventual consistency** = si dejas de escribir, eventualmente todas las réplicas convergerán al mismo valor.

Lo importante son las palabras precisas:

- **"Si dejas de escribir"**: no se garantiza nada DURANTE writes activos. Lecturas pueden ver valores viejos, distintos según réplica.
- **"Eventualmente"**: no se especifica cuándo. Puede ser milisegundos o minutos según el sistema.
- **"Convergerán"**: todas las réplicas llegarán al mismo estado. No se especifica qué estado (puede ser uno u otro de los conflictivos).

Comparado con **strong consistency** (linealizable), eventual:
- ✅ Mucho más rápida (lecturas y escrituras locales).
- ✅ Más disponible (no necesita coordinar entre réplicas).
- ✅ Tolera particiones (réplicas siguen sirviendo aunque no se vean).
- ❌ Lecturas pueden ser stale.
- ❌ Read-your-writes no garantizado por defecto.
- ❌ Conflicting writes requieren resolución.

---

## 2. El espectro de consistencias

Eventual no es la única alternativa a strong. Hay un **espectro** entre las dos:

**Strong consistency (linealizable)** — todas las lecturas ven el último write. Costoso pero simple de razonar.

**Sequential consistency** — todas las operaciones aparecen en algún orden global, pero ese orden no necesariamente refleja tiempo real.

**Causal consistency** — si una operación causó otra (envié un mensaje, alguien respondió), todos los nodos verán la causa antes que el efecto. Operaciones independientes pueden verse en cualquier orden.

**Read-your-writes consistency** — tras un write tuyo, tus lecturas lo verán (otros usuarios pueden no). Crítico para UX (acabas de actualizar tu perfil, recargas y debe aparecer).

**Monotonic reads** — nunca leerás algo más viejo que algo que ya leíste. Previene "viajar al pasado" en sucesivas lecturas.

**Bounded staleness** — eventual con SLA: "lecturas son a lo más N segundos viejas".

**Eventual consistency** — convergencia eventual. Sin garantías intermedias.

**Para apps reales**, casi nadie necesita strong. Pero casi todos necesitan más que eventual puro. **Read-your-writes + monotonic reads suelen ser el mínimo aceptable** para UX humana.

---

## 3. Implementación: cómo se replica con eventual consistency

Hay tres modelos comunes:

### Replicación leader-follower asíncrona

Un nodo es el leader que recibe writes. Los followers reciben writes en background. **Si el leader cae, puedes promover un follower** pero podrías perder writes que no replicó.

**Ejemplo**: MySQL/Postgres con `async replication`. Default en muchas configuraciones.

**Trade-off**: writes rápidos (no esperan a réplicas), pero hay riesgo de pérdida.

### Replicación multi-master (multi-leader)

Múltiples nodos aceptan writes. Cada uno propaga a los demás. **Conflictos posibles** cuando dos nodos modifican el mismo dato simultáneamente.

**Ejemplos**: Cassandra, DynamoDB en modo multi-region active-active, CouchDB.

**Resolución de conflictos** es la parte difícil — ver sección 5.

### Replicación leaderless (Dynamo-style)

Cualquier nodo acepta writes. El cliente envía a N réplicas, espera respuesta de W (escritura) o R (lectura). Cuando `R + W > N`, garantiza algo cercano a strong consistency aunque cada nodo individualmente sea eventual.

**Ejemplos**: DynamoDB, Cassandra, Riak.

**Tunable consistency**: el cliente elige R y W por query. R=1, W=1 es máxima velocidad/disponibilidad. R=N, W=N es máxima consistencia.

---

## 4. Replication lag — el síntoma que verás

**Replication lag** es la diferencia de tiempo entre que el leader aplica un write y los followers lo replican. En sistemas saludables: pocos milisegundos. Bajo carga o problemas de red: segundos o minutos.

**Síntomas en producción**:
- Usuario actualiza perfil. Recarga (otra réplica). Ve viejo.
- Pago procesado. Cliente consulta historial. No aparece todavía.
- Métricas dashboard atrasadas vs realidad.

**Soluciones a problemas concretos**:

**Read-your-writes**: forzar lecturas tras write a leader (no follower) durante una ventana de tiempo. O usar tokens (cliente envía "leído hasta versión N", server espera).

**Monotonic reads**: hacer que un usuario use SIEMPRE la misma réplica (sticky sessions). O servidor central que indica versión mínima que la siguiente lectura debe ver.

**Para apps user-facing**: tipicamente lecturas críticas van al leader, lecturas no críticas a followers. Sacrifica throughput de leader pero mejora UX.

---

## 5. Resolución de conflictos — el problema del multi-master

Cuando dos nodos aceptan writes simultáneos al mismo dato, ¿qué valor gana cuando se sincronizan?

### Last Write Wins (LWW)

El write más reciente (por timestamp) sobrescribe al anterior. **Simple pero peligroso**: pierdes datos. Si dos usuarios modificaron el mismo registro casi a la vez, uno desaparece silenciosamente.

**Cuándo es aceptable**: contadores donde la diferencia no importa, datos donde la atomicidad cross-réplica no es crítica.

**Problema con timestamps**: relojes de distintos servers pueden estar desincronizados. NTP ayuda pero no garantiza orden estricto.

### Application-level merge

La app define cómo combinar valores conflictivos. Por ejemplo: lista de items en carrito → unión de ambas listas. Saldo de cuenta → suma de cambios desde último estado común.

**Más correcto** que LWW pero más complejo. Cada tipo de dato necesita lógica de merge específica.

### CRDTs (Conflict-free Replicated Data Types)

Estructuras de datos diseñadas matemáticamente para que **cualquier orden de aplicación produzca el mismo resultado final**. La convergencia es automática, sin lógica de merge en la app.

Ejemplos: G-Counter (contador que solo crece), OR-Set (set con add/remove resolviendo correctamente concurrencia), LWW-Register, sequences (Yjs, Automerge).

**Usado por**: Riak, Redis (CRDT-types in Active-Active), Figma collab, Notion realtime, Yjs/Automerge para apps colaborativas.

**Trade-off**: complejidad matemática pero correctness garantizada. Para apps colaborativas es el estado del arte.

### Vector clocks

En vez de timestamps físicos, mantener un "reloj lógico" por nodo. Cada write incrementa el reloj del nodo y registra el reloj completo. Permite distinguir:
- Si A causó B (A's clock < B's clock).
- Si A y B son concurrentes (clocks no comparables).

Cuando hay concurrencia → resolver con app o presentar ambos al usuario ("conflict — choose one").

**Usado por**: DynamoDB internamente, Riak, sistemas con multi-master.

---

## 6. BASE — el contramodelo a ACID

ACID describe transacciones (Atomicity, Consistency, Isolation, Durability) para sistemas relacionales fuertes. **BASE** es el modelo opuesto, popularizado para sistemas distribuidos eventuales:

- **Basically Available** — el sistema responde, aunque sea con datos parciales.
- **Soft state** — el estado puede cambiar sin input (sincronizándose en background).
- **Eventual consistency** — convergerá eventualmente.

BASE no es "anti-ACID" sino una **filosofía distinta** apropiada para distintos casos:
- ACID para sistemas transaccionales (bancos, inventario).
- BASE para sistemas a escala web (feeds, social, analytics).

Sistemas reales mezclan: la cuenta bancaria es ACID (Postgres), las métricas de uso de esa cuenta son BASE (Cassandra).

---

## 7. Casos de uso reales

### Twitter timeline

Cuando publicas un tweet, llegará a millones de followers. **Strong consistency es imposible** (latencia inaceptable). Eventual está bien — si tu tweet aparece en el feed de un follower 200ms más tarde que de otro, no importa.

**Implementación**: fanout-on-write a feeds individuales (cassandra-like). Acepta inconsistencia temporal.

### Carrito de compra Amazon (multi-region)

Carrito necesita estar disponible globalmente. Si comprador en US East añade item y se cae esa región, no debe perder el carrito.

**Implementación**: replicación multi-region asíncrona. Conflictos (mismo item añadido en dos regiones) → unión de items (CRDT-style). Trade-off aceptable: a veces ves un item duplicado, mejor que perder el carrito.

### DNS

Cambias un registro DNS. Tarda hasta 24-48h en propagar globalmente. Es el ejemplo clásico de eventual consistency aceptada por todos.

### Cache distribuida

Tu Redis cluster con replication async. Reads pueden ir a réplicas locales (eventual). Writes al primario. Si el primario cae, eliges nuevo primario aceptando posible pérdida de últimos writes.

### Métricas / analytics

Eventual consistency es aceptable y eficiente. Datos que se procesan en batches o streaming, donde "estar al día con 5 minutos de lag" no afecta valor.

---

## 8. Cuándo NO usar eventual consistency

Eventual no encaja para:

- **Saldos bancarios**: una transferencia que aparece y desaparece destruye confianza.
- **Inventario crítico**: vender 1 unidad cuando no queda stock por replicación lag → cliente cabreado.
- **Distributed locks**: si dos nodos creen tener el lock, race conditions.
- **Coordinación de scheduler**: dos nodos ejecutan el mismo job → trabajo duplicado o conflictivo.
- **Configuración de feature flags**: media flota usando v1 y otra media v2 puede romper invariantes cross-service.

Para estos: **strong consistency con consensus** (Etcd, Postgres sync replication, etc.) es el camino.

---

## 9. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Single-instance. No tiene réplicas. Consistencia trivial (no hay nada que reconciliar). Cuando escales a múltiples instancias compartiendo Postgres, el modelo será "una BD compartida" — strong consistency dentro de la BD, eventual en caches Redis si los pones.

### En entrevistas tecnicas

**Pregunta clásica**: "Diseña Twitter feed".

Tu respuesta debe incluir:
1. Eventual consistency aceptable (200ms lag entre followers no importa).
2. Fanout-on-write a feeds individuales en Cassandra (escala writes).
3. CDN para contenido estático (más eventual aún).
4. Strong consistency solo para cosas críticas (auth, payments si aplica).

**Pregunta sobre trade-offs**: "Por qué eventual no siempre es mejor aunque sea más rápida".

Casos donde rompe UX (read-your-writes), casos donde rompe correctness (saldo, inventario). Eventual exige disciplina de diseño y testing exhaustivo de edge cases.

**Pregunta avanzada**: "Cómo implementarías collaborative editing como Google Docs".

CRDTs (Yjs/Automerge). Cada cliente local-first. Operaciones se sincronizan en background. Convergencia matemáticamente garantizada sin servidor central de resolución de conflictos.

---

## 10. Trampas típicas

**"Eventual = inconsistente y mal"**: NO. Es trade-off correcto para 80% de sistemas web modernos. Twitter, Facebook funcionan así y los usuarios no lo notan.

**"Eventual = lento de razonar"**: SÍ, eso sí es cierto. Edge cases multiplicados. Hay que diseñar y testear conscientemente. Por eso strong consistency es tentadora aunque sea más cara.

**"LWW resuelve todos los conflictos"**: NO. Pierde datos silenciosamente. Solo apropiado para casos muy específicos (overwrite OK).

**"Replication lag es bug"**: es feature. La elección de async replica es consciente. Si necesitas no-lag, sync replication (más lento, menos disponible).

**"Eventual no necesita testing de concurrencia"**: AL CONTRARIO. Necesita más, porque hay más estados posibles. Property-based testing y herramientas como Jepsen son útiles.

**"CRDTs resuelven todo"**: solo para tipos de datos específicos. No funcionan para invariantes cross-objeto (ej: "saldo nunca negativo" requiere coordinación, no es CRDT-friendly).

**"Read-your-writes lo resuelve sticky sessions"**: parcialmente. Si el usuario cambia de dispositivo o IP, sticky se pierde. Implementaciones serias usan tokens de versión.

---

## 11. Preguntas típicas de interview

**Define eventual consistency**: si dejas de escribir, todas las réplicas convergerán al mismo valor. Sin garantías durante writes activos.

**Espectro de consistencias**: strong → sequential → causal → read-your-writes → monotonic reads → bounded staleness → eventual. Cada nivel es trade-off entre coste y garantías.

**LWW vs CRDT**: LWW simple, pierde datos. CRDT matemáticamente correcto, complejo, requiere tipos de datos específicos.

**Replication lag — cómo manejarlo**: read from leader para read-your-writes, sticky sessions para monotonic, tokens de versión, async replication con monitoring de lag.

**Cuándo eventual NO sirve**: saldos, inventario, locks, coordinación. Donde la inconsistencia visible rompe correctness o UX.

**BASE vs ACID**: filosofías distintas. ACID para transactional. BASE para distribuido a escala. Sistemas reales mezclan ambos por componente.

---

## 12. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Definición precisa de eventual consistency (las palabras importan).
- El espectro de consistencias (no es binario strong vs eventual).
- Tres modelos de replicación (leader-follower async, multi-master, leaderless).
- Replication lag y soluciones (read from leader, sticky, tokens).
- Resolución de conflictos: LWW (peligroso), app merge, CRDTs, vector clocks.
- BASE como filosofía dual de ACID.
- Cuándo eventual sirve (feeds, métricas) y cuándo no (saldos, locks).

Si no puedes → relee.

---

## Conexiones

- [[01-cap-pacelc]] — eventual consistency es la A de AP
- [[02-consensus-paxos-raft]] — la alternativa cuando necesitas strong
- [[04-distributed-tracing]] — debugging de eventual es más complejo
- [[../05_database_internals/02-acid-transactions]] — la C de ACID es distinta
- [[../05_database_internals/04-replication-y-sharding]] — modelos de replicación
- [[../04_system_design_patterns/02-caching-strategies]] — caches son eventual por naturaleza
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Designing Data-Intensive Applications** capítulo 5 (Replication) — referencia principal.
- **Dynamo paper (Amazon, 2007)** — origen del modelo Dynamo-style. Lectura clásica.
- **CRDT papers** (inria.fr/Papers — Shapiro et al.) — fundamentos matemáticos.
- **Jepsen analyses** (jepsen.io) — tests reales de claims de consistencia.
- **Yjs** (yjs.dev) — CRDT práctico para apps colaborativas.
- **AWS DynamoDB docs** — ejemplo industry-grade de eventual configurable.
