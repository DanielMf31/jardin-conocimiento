# 03 — Message queues

> **Doc 3 del cluster System Design Patterns**. Cómo desacoplas servicios y absorbes picos de carga sin que nada explote. Patrón omnipresente en arquitecturas distribuidas.
> **Frecuencia interview**: aparece en cualquier system design "asíncrono" o "evento-driven". Diferenciar Kafka vs RabbitMQ es clásico.
> **Tiempo de lectura estimado**: 40-55 min.

---

## 1. Por qué message queues

**Problema sin MQ**: el servicio A llama directamente a B (HTTP síncrono).

- Si B está caído → A falla.
- Si B es lento → A espera.
- Burst de tráfico → B se satura → A se satura → cascade failure.
- A debe conocer la dirección y API de B (acoplamiento fuerte).

**Solución — message queue**: A escribe el mensaje en una cola. B (uno o varios consumers) lo lee cuando puede.

```
┌─────┐    ┌───────┐    ┌─────┐
│  A  │ ──→│ Queue │←── │  B  │
└─────┘    └───────┘    └─────┘
```

**Efectos**:
- Desacoplamiento (A no conoce a B).
- Buffering (la cola absorbe bursts).
- Resilience (B puede caerse temporalmente, los mensajes esperan).
- Async (A no bloquea esperando a B).
- Múltiples consumers para paralelizar.

---

## 2. Modelos: queue vs pub/sub

### Queue (point-to-point)

1 mensaje → 1 consumer (de los disponibles). Cuando uno lo procesa, los demás NO lo ven.

**Uso**: trabajos a procesar (envío de emails, generación de PDFs). Distribución de carga entre N workers.

**Implementaciones**: RabbitMQ (queue mode), AWS SQS, Celery con Redis.

### Pub/Sub (publish-subscribe)

1 mensaje → TODOS los suscriptores activos lo reciben.

**Uso**: eventos broadcasted (user created → email + analytics + audit). Notificaciones a múltiples sistemas.

**Implementaciones**: Redis Pub/Sub, AWS SNS, RabbitMQ (fanout exchange).

### Híbrido — log-based (Kafka, Pulsar)

Mensaje persistente en LOG ordenado. Cada consumer mantiene su PROPIO offset (puntero a "dónde está"). Múltiples consumers pueden leer el mismo log a distinto ritmo. Los mensajes NO se borran al consumirse (retention por tiempo o tamaño).

**Uso**: event sourcing, stream processing, analytics, replay.

**Ventajas**:
- Replay: vuelves a procesar mensajes viejos.
- Múltiples sistemas leen el mismo evento.
- Throughput enorme (millones msg/s).

**Desventajas**:
- Más complejo de operar que queue tradicional.
- Requiere conocer offsets, partitions, consumer groups.

---

## 3. Garantías de entrega

Las 3 garantías posibles:

| Garantía | Comportamiento | Uso típico | Implementación |
|---|---|---|---|
| **At-most-once** | 0 o 1 vez. Puede perderse, NUNCA se duplica | Métricas, telemetry (perder algunas es OK, dup las distorsiona) | Fire-and-forget. UDP. Sin ACK |
| **At-least-once** | 1 o más veces. NUNCA se pierde, puede duplicarse | El más común. Aceptable si tu consumer es idempotente | ACK del consumer. Si no llega ACK → reenvía |
| **Exactly-once** | Exactamente 1 vez. Ideal pero MUY difícil ("santo grial") | Cuando duplicar tiene coste real (pagos) | Requiere coordinación (idempotency keys, transactional outbox). Kafka y Pulsar lo soportan en algunos modos |

**Regla operativa**: "Diseña tus consumers como idempotentes y usa at-least-once". Más robusto que perseguir exactly-once teórico.

### Idempotencia — qué es y por qué

**Idempotente** = ejecutar 1 vez o N veces produce el MISMO resultado final.

**Ejemplos**:
- [OK] "set user.email = X" → repetible sin daño.
- [NO] "increment counter" → no idempotente.
- [OK] "increment counter IF version=N" → idempotente con version check.

**Cómo hacer idempotente**:
- Idempotency key (UUID) por mensaje. El consumer guarda processed IDs.
- Operaciones inherentemente idempotentes (set, no increment).
- Conditional updates (compare-and-swap).

**Ejemplo Stripe**: cada API request acepta el header `Idempotency-Key: uuid`. Stripe guarda el resultado. Si llega un segundo request con el mismo key, devuelve el resultado cacheado. El cliente puede reintentar sin doble cobro.

---

## 4. Backpressure — cuando los consumers van más lento que producers

**Problema**: los producers escriben más rápido de lo que los consumers procesan. La cola crece sin límite → consume RAM/disco → eventualmente colapso.

**Soluciones**:

1. **Throttling del producer**: el producer ralentiza si la cola está llena. Reactive Streams, `asyncio.Queue` con `maxsize`.

2. **Auto-scaling de consumers**: si la cola crece → arrancar más instancias de consumer. Kubernetes HPA basado en queue depth.

3. **Dropping (último recurso)**: si la cola se llena, descartar mensajes nuevos (o viejos). Solo aceptable para datos no-críticos.

4. **Spill to disk**: la cola guarda en disco cuando la RAM se llena. Lento pero no se pierde.

5. **Dead letter queue (DLQ)**: mensajes que fallan repetidamente → DLQ. Inspección manual o reprocessing offline.

---

## 5. Comparativa de las herramientas más usadas

### Kafka

Log-based, alto throughput.

**Modelo**: topics divididos en PARTITIONS. Cada partition es un log ordenado e inmutable. Los producers escriben al final, los consumers leen desde su offset.

**Escalado**: particionado horizontal (más partitions = más paralelismo). Replicación de partitions entre brokers (HA).

**Uso**: event sourcing, stream processing, log aggregation, real-time analytics. LinkedIn, Netflix, Uber, prácticamente todos los unicornios.

**Pros**:
- Throughput brutal (millones msg/s).
- Retention configurable (días, semanas).
- Replay desde cualquier offset.
- Ecosistema enorme (Kafka Streams, Connect, Schema Registry).

**Contras**:
- Complejo de operar (Zookeeper hasta v3, KRaft moderno).
- Latencia mayor que queues simples (ms vs μs).
- Curva de aprendizaje.

**Alternativas modernas compatibles**:
- **Redpanda** — Kafka API, sin Zookeeper, escrita en C++. Más simple.
- **WarpStream** — Kafka API, almacenamiento en S3.

### RabbitMQ

Tradicional message broker (AMQP).

**Modelo**: Exchanges → Bindings → Queues → Consumers. Routing flexible: direct, topic, fanout, headers.

**Uso**: task queues, RPC patterns, comunicación entre microservices. Cuando necesitas routing flexible más que throughput extremo.

**Pros**:
- Maduro (2007), estable.
- Routing patterns ricos.
- Management UI excelente.
- Plugin system.

**Contras**:
- Throughput menor que Kafka (decenas de miles msg/s vs millones).
- Menos preparado para event sourcing.

**Uso típico**: Celery con RabbitMQ es estándar Python.

### Redis Pub/Sub + Streams

**Redis Pub/Sub**: fire-and-forget. Si no hay subscriber, el mensaje SE PIERDE. Súper rápido pero sin persistencia ni replay. Uso: notificaciones realtime no críticas.

**Redis Streams (Redis 5+)**: log persistente similar a Kafka pero más simple. Consumer groups, ACKs, DLQ. Uso: queues de tareas medianas, eventos con persistencia.

**Pros**: ya tienes Redis, no añades dependencia.
**Contras**: throughput menor que Kafka, no escala a TB.

### AWS SQS / SNS / EventBridge

- **SQS**: queue managed (FIFO o standard).
- **SNS**: pub/sub managed.
- **EventBridge**: bus de eventos con routing rules.

**Pros**: zero ops, integración total AWS, cobro por uso.
**Contras**: vendor lock-in, latencia mayor que self-hosted.

### NATS / NATS JetStream

Lightweight messaging. Muy rápido. JetStream añade persistencia (similar a Kafka pero más simple). Usado por Synadia, CNCF graduated.

### Celery (Python específico)

Task queue Python sobre broker (Redis o RabbitMQ). Defines tasks, las llamadas son async, los workers procesan.

```python
@celery.task
def send_email(to, body):
    ...

send_email.delay("user@x.com", "hi")  # async, ejecuta en worker
```

**Uso estándar** para background jobs en Python.

---

## 6. Patterns típicos

### Work queue (task distribution)

N workers consumen de UNA queue. Cada mensaje a 1 worker. Distribuye carga.

**Uso**: envío de emails, procesamiento de imágenes, jobs ML batch.

### Pub/Sub fanout

1 evento → varios consumers independientes. Cada uno hace su procesamiento (analytics, notifications, audit).

### Request-Reply (RPC sobre MQ)

El producer envía mensaje + reply queue. El worker procesa, responde a la reply queue. El producer espera respuesta. Como HTTP RPC pero asíncrono.

### Event sourcing

TODO cambio de estado se escribe como EVENTO en log inmutable. Estado actual = replay de eventos. Permite auditoría total, time-travel, derived views.

**Ejemplo**:
- Account events: Created, Deposited 100, Withdrew 30.
- Balance actual = sum(events) = 70.
- Si cambias lógica → re-replay para nuevo estado.

**Uso**: sistemas financieros, audit-heavy, CQRS.

### Saga pattern (transacciones distribuidas)

Una "transacción" cross-service se modela como secuencia de pasos. Cada paso emite evento. Si falla → compensating action.

**Ejemplo order**:
- Step 1: `reserve_inventory` → ok.
- Step 2: `charge_payment` → failed.
- Compensate: `release_inventory`.

**Alternativa** al 2-phase commit (que escala mal).

### Outbox pattern

**Problema**: quieres "guardar en DB" + "enviar mensaje" atomic. Si la DB OK pero el envío falla → estado inconsistente.

**Solución**: en la misma TX de DB, guardas el mensaje en una tabla `outbox`. Un worker async lee la outbox y publica en la cola → marca como enviado.

Garantiza at-least-once + atomicidad con DB.

---

## 7. Ordering guarantees

| Tipo | Comportamiento | Coste / nota |
|---|---|---|
| **Total order** | Todos los mensajes se procesan en orden absoluto | Costoso. Limita paralelismo (1 consumer por queue) |
| **Partition order** (Kafka) | Orden garantizado dentro de cada partition. Múltiples partitions paralelas | Choose key con cuidado: same key → same partition → ordered. Ej: `order_id` como key → todos eventos de un order van en orden |
| **No order** (most queues default) | Mensajes se procesan en paralelo en N workers | Si necesitas orden, debes implementarlo |

---

## 8. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

- Hoy: no necesitas message queue (síncrono está bien).
- Cuando hagas T1.5 (Celery), implementarás esto:
  - Producer: tu API genera tarea (envío email, generar PDF).
  - Broker: Redis o RabbitMQ.
  - Worker: proceso separado consume y procesa.

### En entrevistas tecnicas

**Pregunta**: "Diferencia entre Kafka y RabbitMQ".
→ Kafka: log-based, alto throughput, replay, retention. RabbitMQ: queue tradicional, routing flexible, less throughput. Kafka para event streaming, RabbitMQ para task distribution.

**Pregunta**: "Cómo garantizas exactly-once delivery".
→ Strictly: muy difícil. En la práctica: at-least-once + consumer idempotente. Idempotency key (UUID) por mensaje.

**Pregunta**: "Diseña sistema de notificaciones para Twitter".
→ Producer (tweet creado) → Kafka topic. Consumers: push notif service, email service, in-app feed updater. Cada uno suscribe al mismo topic, procesa independiente.

**Pregunta**: "Cómo manejas backpressure".
→ Bounded queues, throttling de producers, auto-scaling consumers, DLQ para fallos persistentes.

**Pregunta**: "Por qué async > sync entre microservicios".
→ Decoupling, resilience (B caído no tira a A), absorbe picos de carga, permite scaling independiente.

**Pregunta**: "Qué es outbox pattern".
→ Atomic write a DB + message en misma TX. Worker publica desde tabla outbox. Garantiza at-least-once + consistencia DB-message.

---

## 9. Trampas típicas

**Trampa 1 — "Exactly-once es trivial"**: no lo es. Requiere idempotency + transacciones cuidadosas. La industria moderna usa "effectively once" = at-least-once + idempotent.

**Trampa 2 — "Más colas siempre mejor"**: cada cola añade ops complexity. Empieza simple, evoluciona.

**Trampa 3 — "Kafka para todo"**: si solo tienes 100 msg/s y necesitas routing simple, RabbitMQ o Redis Streams son más simples y suficientes.

**Trampa 4 — "Olvidar el DLQ"**: sin dead letter queue, los mensajes problemáticos bloquean el sistema o se pierden. Siempre configura DLQ.

**Trampa 5 — "Pensar que async = más rápido"**: async desacopla. Latency end-to-end puede ser igual o peor. Lo que cambia: resilience, scalability, throughput agregado.

**Trampa 6 — "Mensaje de 10 MB"**: casi todos los brokers tienen límites (RabbitMQ 128 MB default, Kafka similar). Mejor: pasa referencia (S3 URL), no payload grande.

**Trampa 7 — "Order es siempre necesario"**: casi nunca. Diseña para no depender de orden global → escala mejor.

---

## 10. Preguntas típicas de interview

**Pregunta 1 — "Por qué usar message queues"**: decoupling, resilience, buffering, async, paralelización.

**Pregunta 2 — "Queue vs pub/sub vs log"**: queue: 1-to-1 (1 worker procesa). Pub/sub: 1-to-many (todos suscriptores reciben). Log: persistent ordered, múltiples consumer groups con offsets.

**Pregunta 3 — "Garantías de entrega"**: at-most-once, at-least-once, exactly-once. En la práctica: at-least-once + idempotent.

**Pregunta 4 — "Diferencia Kafka vs RabbitMQ"**: ya cubierto.

**Pregunta 5 — "Cómo manejarías una cola que crece sin parar"**: backpressure: throttle producers, auto-scale consumers, DLQ para errores, alertar para investigar root cause.

**Pregunta 6 — "Outbox pattern"**: garantizar atomicidad entre DB write y message send.

---

## 11. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué MQ (decoupling, resilience, async).
- Queue vs pub/sub vs log (Kafka).
- 3 garantías de entrega + idempotencia como solución práctica.
- Backpressure: 4 estrategias.
- Kafka vs RabbitMQ vs Redis Streams (cuándo cada uno).
- DLQ y por qué es obligatorio.
- Outbox pattern para atomicidad DB+MQ.
- Saga pattern para transacciones distribuidas.

Si no puedes → relee.

---

## Conexiones

- [[01-load-balancing]] — distribuir tráfico vs distribuir tareas
- [[02-caching-strategies]] — Redis sirve ambos roles
- [[../06_distributed_systems/01-cap-pacelc]] — tradeoffs distribución
- [[../06_distributed_systems/03-eventual-consistency]] — async = eventual
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]
- [[../../Build_Things/00_README]] — T1.5 Celery, T2.3 Kafka

## Recursos externos

- **Designing Data-Intensive Applications** capítulo 11 (Stream Processing) — el referente.
- **Kafka: The Definitive Guide** (Narkhede et al.) — biblia Kafka.
- **RabbitMQ in Action** (Videla & Williams) — buen intro.
- **Confluent blog** — case studies Kafka enterprise.
- **AWS messaging docs** — SQS/SNS/EventBridge comparison.
