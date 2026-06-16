# 01 — CAP y PACELC

> 📚 **Doc 1 del cluster Distributed Systems**. El teorema más famoso de sistemas distribuidos. Marca los límites fundamentales de cualquier sistema con datos replicados.
> 🔥 **Frecuencia interview**: aparece en TODA system design seria. Si te preguntan "qué BD usas y por qué", CAP/PACELC es la justificación.
> ⏱️ **Tiempo de lectura estimado**: 35-50 min.

---

## 1. Qué es el teorema CAP

Eric Brewer formuló el **teorema CAP** en 2000 (formalizado por Gilbert & Lynch en 2002). Dice que un sistema distribuido **no puede garantizar las 3 propiedades simultáneamente** cuando hay particiones de red:

- **Consistency (C)**: todas las lecturas ven el último write más reciente.
- **Availability (A)**: cada request recibe una respuesta no-error (puede ser lectura stale).
- **Partition tolerance (P)**: el sistema sigue funcionando aunque la red se parta.

La trampa común es decir "elige 2 de las 3". La realidad es más sutil: **las particiones de red ocurren en cualquier sistema distribuido real**, así que la P es **inevitable**. Lo que realmente eliges es **CP o AP** durante una partición.

### Las particiones SON inevitables

Si tienes 2 nodos comunicándose por red, en algún momento la red fallará: cable cortado, switch caído, congestión, latencia infinita. Cuando eso pasa, los nodos no pueden coordinarse y debes elegir:

- **CP**: sacrifico disponibilidad. El nodo que no puede coordinarse rechaza requests para garantizar consistencia.
- **AP**: sacrifico consistencia. Cada nodo sigue respondiendo con sus datos locales, aunque sean viejos.

---

## 2. Qué significa cada propiedad concretamente

### Consistency (linealizabilidad)

La C de CAP es **strong consistency** (linealizabilidad). Significa que tras un write exitoso, **toda lectura subsiguiente** ve ese valor o uno más reciente. El sistema se comporta como si hubiera **una sola copia** lógica de los datos.

**Ejemplo**: actualizo `user.email = "x@y.com"` en el nodo A. Una lectura inmediata desde el nodo B debe ver "x@y.com" o un valor más nuevo. Nunca el viejo.

Importante: esto **no es lo mismo** que la C de ACID (transactional consistency, que se refiere a invariantes de la BD). Mismo nombre, distinta cosa.

### Availability

Cada request a un nodo no caído devuelve una respuesta válida (no error, no timeout indefinido). Importante: la respuesta puede ser **stale** (datos viejos). Solo se exige que NO sea error.

### Partition tolerance

El sistema funciona aunque mensajes entre nodos se pierdan o lleguen con delay arbitrario. Es la asunción de que la red es **no fiable**.

---

## 3. Sistemas CP — sacrifican availability

Si la red se parte, el nodo en minoría rechaza requests para no servir datos potencialmente stale. **Prioriza no devolver datos incorrectos sobre estar disponible**.

**Ejemplos**:
- **HBase**: CP estricto sobre HDFS.
- **MongoDB con majority writes**: rechaza writes si la mayoría de réplicas no responde.
- **Etcd, Zookeeper, Consul**: usan Raft/Paxos, eligen CP. Son sistemas de coordinación donde la consistencia es no-negociable.
- **Postgres con sync replication**: si la réplica sync no responde, el primario bloquea writes.

**Cuándo elegir CP**: bancos, inventario crítico, sistemas de coordinación, donde devolver "saldo incorrecto" es peor que devolver "no disponible temporalmente".

---

## 4. Sistemas AP — sacrifican consistency

Cada nodo sigue respondiendo con sus datos locales aunque no pueda hablar con los demás. Acepta que diferentes lectores puedan ver distintos valores temporalmente. **Eventualmente** los nodos convergen (eventual consistency — ver doc 03).

**Ejemplos**:
- **DynamoDB (modo eventual consistency)**: cada réplica responde local.
- **Cassandra**: AP por diseño (configurable a nivel de query).
- **CouchDB**: replicación multi-master con resolución eventual.
- **Redis cluster con replicación async**: AP en modo default.

**Cuándo elegir AP**: feeds sociales, métricas, productos en e-commerce (mejor mostrar datos un poco viejos que "no disponible"), cualquier sistema donde "siempre arriba" importa más que "siempre exacto".

---

## 5. PACELC — la extensión necesaria

CAP solo habla del comportamiento durante particiones. Pero **las particiones son raras**. La pregunta interesante es: **qué pasa cuando NO hay partición**.

Daniel Abadi propuso **PACELC** en 2010 para cubrir ambos casos:

- **Si hay Partition**: eliges entre **A**vailability y **C**onsistency.
- **Else (no partición)**: eliges entre **L**atency y **C**onsistency.

La parte ELC es la novedad: incluso cuando todo va bien, hay un trade-off. Para garantizar consistencia fuerte, debes coordinar entre nodos antes de responder, lo que añade latencia. Si quieres latencia mínima, debes responder localmente sin coordinar, sacrificando consistencia.

### Clasificación PACELC de sistemas reales

| Sistema | PACELC | Significado |
|---|---|---|
| Postgres (síncrono) | PC/EC | Consistencia siempre, latencia más alta |
| MongoDB (majority) | PC/EC | Consistencia siempre |
| MySQL (default async) | PA/EC | AP en partición, consistencia con baja latencia normal |
| DynamoDB (default) | PA/EL | Eventual siempre, latencia mínima |
| Cassandra | PA/EL | Lo mismo, configurable por query |
| Spanner (Google) | PC/EC | Consistencia global con TrueTime, latencia mayor |

**Lo que dice PACELC sobre tu stack**: incluso en condiciones normales, tu BD ya está eligiendo. Postgres síncrono es lento porque garantiza consistencia. DynamoDB es rapidísimo porque renuncia a ella. **No hay almuerzo gratis**.

---

## 6. Los matices que casi nadie cuenta

CAP es famoso pero está **simplificado en exceso**. Los matices reales:

### "C" tiene niveles, no es binario

Hay un espectro de consistencias, no solo "fuerte" vs "eventual":

- **Strong (linealizable)**: toda lectura ve el último write. Lo más caro.
- **Sequential**: ordenar globalmente todas las operaciones.
- **Causal**: si A causó B, todos ven A antes que B (pero ops independientes pueden verse en cualquier orden).
- **Read-your-writes**: tras tu write, tus lecturas lo ven (otros usuarios pueden no).
- **Monotonic reads**: nunca lees algo más viejo que algo que ya leíste.
- **Eventual**: con suficiente tiempo sin writes, todas las réplicas convergen.

**La mayoría de apps no necesitan strong consistency**. Read-your-writes + monotonic reads suelen ser suficientes y mucho más baratas.

### Las particiones tienen niveles

No es solo "todo o nada". Pueden ser parciales (solo algunos nodos no se ven), asimétricas (A ve B pero B no ve A), de alta latencia (no caída pero sí degradada). Cada caso requiere manejo distinto.

### Las decisiones se toman por OPERACIÓN, no por sistema

Cassandra te deja elegir el nivel de consistencia POR QUERY. Puedes hacer una lectura "ONE" (rápida, eventual) o "QUORUM" (consistencia fuerte, lenta) en la misma BD. La elección es por caso de uso, no por sistema entero.

### CAP no aplica a sistemas no distribuidos

Si tu BD es un solo nodo (Postgres single-instance), CAP no aplica. Tienes consistencia trivialmente. Pierdes disponibilidad si ese nodo cae, pero eso no es CAP, es SPOF.

---

## 7. CAP en arquitecturas reales

La mayoría de sistemas reales NO son puro CP o puro AP. Son **híbridos por capa**:

- **Edge / cache**: AP (mostrar contenido cacheado mejor que error).
- **API layer**: AP (degradación graceful).
- **Database principal**: CP para datos críticos (pagos, inventario).
- **Data warehouse / analytics**: AP (datos viejos OK).
- **Coordinación (locks, leader election)**: CP estricto (Zookeeper, Etcd).

**Diseño realista**: clasifica cada dato según su importancia y aplica el modelo apropiado. Mismo sistema, distintas decisiones por componente.

---

## 8. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Hoy es single-node JSON. CAP no aplica. Cuando migres a Postgres con réplicas (proyecto futuro), tendrás que decidir:

- Replicación síncrona → CP → bloqueas writes si réplica cae.
- Replicación async → AP → puedes perder writes si primario cae sin replicar.

Para una agenda de contactos, AP es razonable (perder un contacto raramente es catastrófico).

### En entrevistas tecnicas

**Pregunta clásica**: "Por qué eliges X BD para tu sistema".

Tu respuesta debe incluir:
1. ¿Qué consistencia necesita el dato? (strong vs eventual).
2. ¿Qué latencia es aceptable?
3. ¿Qué disponibilidad necesitas? (SLA real, no aspiracional).
4. PACELC del sistema candidato → encaja con tus requirements.

**Pregunta avanzada**: "Diseña sistema de banking transactions".
- Coordinación: Etcd (CP estricto).
- Cuentas con saldos: Postgres con sync replication (CP).
- Logs de auditoría: Cassandra (AP, append-only, eventual está bien).
- Notificaciones a usuarios: Kafka (AP para events).

Cada componente con el modelo apropiado, no un único sistema "que lo hace todo".

---

## 9. Trampas típicas

**"CAP me obliga a elegir 2 de 3"**: incorrecto. Las particiones son inevitables, así que P es siempre. Eliges entre C y A en presencia de P.

**"Voy a hacer un sistema CA"**: imposible en distribuido. Solo single-node. Si pierdes ese nodo, pierdes A.

**"NoSQL = AP, SQL = CP"**: simplificación falsa. Postgres puede ser AP (async replication). MongoDB puede ser CP (majority writes). Depende de la configuración.

**"Eventual consistency = mal"**: no, es trade-off válido para muchísimos casos. Twitter, Facebook feeds funcionan con eventual y la gente no se da cuenta.

**"Strong consistency es siempre mejor si te lo puedes permitir"**: tampoco. Strong consistency tiene latencia mayor SIEMPRE (PACELC ELC). Para datos donde 100ms de delay es OK, eventual es mejor por la latencia.

**"CAP aplica al sistema entero"**: aplica a cada operación/dato. Diseña por capas con el modelo apropiado en cada una.

---

## 10. Preguntas típicas de interview

**Explica CAP**: 3 propiedades, eliges 2 cuando hay partición (en realidad eliges entre A y C porque P es inevitable).

**Diferencia CAP y PACELC**: PACELC añade el caso "no partición" donde eliges entre Latency y Consistency.

**Sistemas CP vs AP — ejemplos y cuándo**: cubierto secciones 3-4.

**¿Por qué Spanner consigue PC/EC?**: TrueTime API (relojes atómicos en datacenters) permite consistency global con coordinación más eficiente. Trade-off es la latencia añadida y la infraestructura cara.

**Diseña sistema con consistency tiers**: clasificar datos por criticidad y aplicar BD distinta a cada uno (Etcd para coordinación, Postgres para transactional, Cassandra para analytics).

**¿Eventual consistency cuándo es problema?**: cuando read-your-writes falla (usuario actualiza perfil y al recargar ve el viejo), o cuando hay invariantes cross-objeto (saldo total). Solución: leer del primario para casos críticos, o usar BD con consistencia fuerte para esas tablas.

---

## 11. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Las 3 propiedades CAP y por qué P es inevitable en distribuido.
- Diferencia CP vs AP con ejemplos reales.
- Por qué CAP es insuficiente y PACELC lo extiende.
- Las 6 categorías de consistencia (strong → eventual).
- Sistemas reales y su clasificación PACELC.
- Por qué arquitecturas reales mezclan CP y AP por capa.
- Trampa "CAP obliga a 2 de 3".

Si no puedes → relee.

---

## Conexiones

- [[02-consensus-paxos-raft]] — cómo conseguir CP en práctica
- [[03-eventual-consistency]] — qué es realmente AP
- [[04-distributed-tracing]] — debugging cuando CAP te muerde
- [[../05_database_internals/02-acid-transactions]] — la C de ACID NO es la C de CAP
- [[../05_database_internals/04-replication-y-sharding]] — implementación de replicación
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Designing Data-Intensive Applications** (Kleppmann) capítulos 5 y 9 — la mejor explicación moderna.
- **Brewer's CAP Conjecture** — paper original (2000).
- **Gilbert & Lynch CAP proof** (2002) — formalización.
- **Daniel Abadi PACELC** (2010) — paper original.
- **Aphyr's Jepsen analyses** (jepsen.io) — tests reales de claims de consistencia. Brutalmente honesto.
- **Spanner paper** (Google) — TrueTime y consistencia global.
