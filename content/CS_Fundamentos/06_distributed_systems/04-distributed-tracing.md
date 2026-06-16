# 04 — Distributed tracing

> 📚 **Doc 4 (último) del cluster Distributed Systems**. Cómo entender qué pasa en un sistema con N microservicios cuando algo va lento o falla. La herramienta de observabilidad más importante en arquitecturas distribuidas modernas.
> 🔥 **Frecuencia interview**: aparece en preguntas de "cómo debugeas X falla" en sistemas distribuidos. Conocer OpenTelemetry te diferencia.
> ⏱️ **Tiempo de lectura estimado**: 30-45 min.

---

## 1. El problema que resuelve

En un monolito, debugar es relativamente simple: stack trace + logs + metrics y tienes la película. En microservicios moderno, una sola request del usuario puede tocar 20+ servicios:

```
Usuario → API Gateway → Auth → User service → Recommendations →
  → ML model serving → Cache → DB → Analytics → Notifier → Email service
```

Si la respuesta tarda 3 segundos cuando debería tardar 200ms, **¿quién es el culpable?** ¿El ML serving? ¿La DB? ¿La red entre dos nodos? ¿La cola que está saturada?

Con **logs por servicio individual no puedes saberlo**: cada servicio tiene su propio log, sin saber a qué request del usuario corresponde cada línea.

**Distributed tracing** resuelve esto: capturar **el camino completo de cada request** a través de todos los servicios, con timing detallado de cada salto.

---

## 2. Vocabulario fundamental

### Trace

Una **trace** representa el viaje completo de UNA request del usuario a través del sistema. Tiene un identificador único (`trace_id`) que la sigue por TODOS los servicios.

### Span

Un **span** es una operación individual dentro de una trace. Cada servicio crea uno o más spans para representar su trabajo. Un span tiene:

- **Operation name**: qué representa ("HTTP GET /users", "DB query SELECT", "ML inference").
- **start_time + end_time**: cuándo empezó y terminó.
- **trace_id**: a qué trace pertenece.
- **span_id**: identificador único del span.
- **parent_span_id**: quién lo invocó (para construir el árbol).
- **attributes / tags**: metadata (HTTP status, user_id, query, etc.).
- **events / logs**: eventos discretos durante el span.
- **status**: OK, error, etc.

### Árbol de spans

Los spans de una trace forman un **árbol** según las relaciones padre-hijo:

```
trace abc123:
  span: API Gateway (1500ms)
    span: Auth service (50ms)
    span: User service (1300ms)
      span: DB query (200ms)
      span: External API call (1000ms) ← AQUÍ está el cuello
      span: Cache get (50ms)
    span: Notifier (100ms)
```

A simple vista ves que el "External API call" tarda 1000ms y es el cuello.

---

## 3. Cómo se propaga el contexto

El truco fundamental de distributed tracing: **cada servicio debe saber qué trace_id le toca y propagarlo a los servicios que llama**.

Cuando el servicio A llama al servicio B (HTTP, gRPC, cola), debe pasar el contexto:

- `trace_id`: identificador de la trace.
- `span_id` del span que está creando (será el `parent_span_id` del span de B).
- Flags (sampled, etc.).

Esto se hace típicamente en **HTTP headers**:
- `traceparent: 00-trace_id-span_id-flags` (W3C standard).
- O propiedad de Jaeger: `uber-trace-id`.
- O Zipkin: `X-B3-TraceId`, `X-B3-SpanId`, etc.

**Sin propagación correcta**, las traces se rompen. Es el bug clásico — un microservicio no propaga headers y queda como "isla", sin conectar con la trace global.

---

## 4. Sampling — no puedes guardarlo todo

Capturar TODA la trace de TODA request en producción es carísimo:
- Storage: TBs por día en sistemas grandes.
- Network overhead: cada span es un evento que se manda al backend de tracing.
- CPU overhead: serializar y enviar todo es trabajo no despreciable.

**Sampling**: solo capturar una **muestra** de las traces. Estrategias:

### Head sampling (decisión al inicio)

Al inicio de la trace, se decide si capturarla o no. Si no, **todos** los spans descendientes se descartan también. Decisión local en el primer servicio.

**Pros**: simple, eficiente (no se serializa lo que se descarta).
**Contras**: si una request resulta interesante (e.g. error) pero no fue sampled, la perdiste.

**Estrategias**:
- **Probabilistic**: cada trace tiene probabilidad N% de ser capturada. E.g. 1%.
- **Rate limiting**: capturar máximo N traces/segundo.
- **Per-endpoint**: muestrear endpoints críticos al 10%, otros al 1%.

### Tail sampling (decisión al final)

Capturar TODOS los spans, decidir al final si guardar la trace completa o descartar.

**Pros**: puedes basar la decisión en el resultado (errores, latencia alta → siempre guardar). No pierdes información valiosa.
**Contras**: requiere infraestructura más compleja (capturar todo, decidir, descartar).

**Strategies modernas** combinan: head sampling para volumen normal + force-keep para errores y traces lentas.

### Adaptive sampling

Sistemas que ajustan el rate de sampling según condiciones (más sampling en momentos críticos, menos cuando todo va bien).

---

## 5. OpenTelemetry — el estándar moderno

**OpenTelemetry (OTel)** es la fusión de OpenTracing y OpenCensus. Es ahora **el estándar CNCF** para observabilidad. Define:

- **API**: cómo crear spans en tu código (lenguaje-agnóstico).
- **SDK**: implementaciones en cada lenguaje (Python, Java, Go, JS, etc.).
- **Protocol** (OTLP): formato wire para enviar spans al backend.
- **Collectors**: agentes que reciben de SDKs, procesan, envían a backends.

### Por qué importa el estándar

Antes de OTel, cada vendor tenía su propia API (Jaeger, Zipkin, Datadog, NewRelic). Si cambiabas de vendor, reescribías toda la instrumentación.

Con OTel: **instrumentas tu código una vez** con la API estándar. Después configuras el SDK para enviar a Jaeger, Datadog, NewRelic, lo que sea. **Vendor lock-in eliminado**.

### Auto-instrumentation vs manual

**Auto-instrumentation**: librerías que instrumentan automáticamente frameworks comunes (FastAPI, Flask, Express, Django, gRPC, requests, SQLAlchemy, redis-py, etc.). Se cargan al arrancar el proceso y crean spans sin que toques tu código.

**Manual instrumentation**: añadir spans específicos a tu lógica de negocio:

```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@app.post("/process_order")
def process_order(order: Order):
    with tracer.start_as_current_span("validate_order") as span:
        span.set_attribute("order.id", order.id)
        span.set_attribute("order.amount", order.amount)
        validate(order)

    with tracer.start_as_current_span("charge_payment"):
        charge(order)

    with tracer.start_as_current_span("send_confirmation"):
        notify(order.user_id)
```

**Combinación típica**: auto-instrumentation para HTTP/DB/cache (gratis) + manual para lógica de negocio crítica.

---

## 6. Backends populares

Los SDKs OTel envían a un **backend de tracing** que almacena, indexa y permite consultar.

**Open source**:
- **Jaeger** (Uber): el más popular. Web UI decente, escalable.
- **Tempo** (Grafana): integrado con stack Grafana/Prometheus/Loki.
- **Zipkin** (Twitter): el original, todavía usado en algunos lados.
- **SigNoz**: alternativa open-source más moderna, integra metrics + logs + traces.

**Comerciales**:
- **Datadog APM**: el más usado en empresas. Caro pero muy completo.
- **New Relic**: similar.
- **Honeycomb**: pioneros en observability moderna, slicing/dicing de datos avanzado.
- **Lightstep**: ahora ServiceNow. Muy bueno para sistemas grandes.
- **AWS X-Ray, GCP Cloud Trace**: managed por cloud providers.

**Stack típico moderno**:
```
Tu código (con OTel SDK)
  → OTel Collector (agente local)
    → Backend (Jaeger / Datadog / Tempo / etc.)
      → Web UI para consultar
```

---

## 7. Qué puedes hacer con tracing — casos de uso

### Latency analysis

La pregunta más típica: "el endpoint X tarda 2 segundos, ¿por qué?"

Abres una trace de ese endpoint y ves dónde se va el tiempo. **Visualmente obvio** qué span domina. Mucho más rápido que mirar logs de N servicios.

### Error correlation

Una request falla. ¿Quién falló primero, y por qué los demás siguieron procesando?

Con tracing, ves la propagación del error: qué span fue el primer "error", qué hicieron los demás (retried? siguieron? cayeron?). Resuelve mucho debugging de "X falló y arrastró Y".

### Service dependency mapping

Después de capturar miles de traces, los backends generan mapas automáticos: "el servicio A llama a B, C y D. C llama a E. ...". Te da imagen del sistema real, no la documentación desactualizada.

### Performance regressions

Comparas las latencias por percentil entre semanas. "El servicio X tenía P99 = 200ms hace una semana, ahora es 800ms. ¿Qué cambió?". Tracing te lleva al span responsable.

### Capacity planning

Vías la distribución de carga real. "El 80% de tiempo se va en queries DB. Si dobluo carga, ¿escalo DB o app?".

---

## 8. Logs vs metrics vs traces — los 3 pilares

La observabilidad moderna se construye con tres tipos de telemetría:

### Logs

**Eventos discretos** con texto. "Usuario X login fallido". "Error en función Y".

- **Pros**: ricos en información, contexto del momento exacto.
- **Contras**: caros (storage), buscar en TBs es lento, no agregables fácilmente.
- **Cuándo**: debugging post-mortem de cosas específicas.

### Metrics

**Números agregados** con dimensiones. "Latency P99 del endpoint /users en últimos 5 min, por región".

- **Pros**: súper baratos (números pre-agregados), rápidos de consultar, ideales para dashboards y alertas.
- **Contras**: pierden detalle (no sabes QUÉ request específica, solo el agregado).
- **Cuándo**: dashboards, alertas, monitoring continuo.

### Traces

**El camino de UNA request específica** con timing por span.

- **Pros**: muestran flujo entre servicios, explican LATENCY, encuentran bottlenecks específicos.
- **Contras**: caros si capturas todo (sampling necesario), no buenos para alertas (son por-request).
- **Cuándo**: debugging de latency, errores entre servicios, análisis de flujos.

**Los 3 son complementarios, no alternativos**. Sistemas serios tienen los 3.

---

## 9. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Single service, no hay nada que tracear entre servicios. Cuando hagas T1.6 (observabilidad) podrías añadir OTel local + Jaeger en docker-compose para practicar:

```python
# Auto-instrumentation FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
FastAPIInstrumentor.instrument_app(app)
```

Y verás traces en Jaeger UI. Útil para entender el concepto antes de necesitarlo en producción.

### En entrevistas tecnicas

**Pregunta clásica**: "Tu microservicio en producción tiene latencia espontánea esporádica, cómo lo debugeas".

Tu respuesta:
1. Mirar metrics (latency P50/P95/P99 por endpoint, por región, por hora).
2. Identificar patrón temporal o por endpoint.
3. Buscar traces lentas en ese tiempo/endpoint.
4. Analizar spans para ver dónde se va el tiempo.
5. Si es DB → query slow log. Si es servicio externo → su SLA. Si es interno → profundizar en sus traces.

**Pregunta sobre observability strategy**: "Diseña observability para sistema microservicios".

- Logs: estructurados, agregados (Loki/ELK).
- Metrics: Prometheus + Grafana, RED method (Rate, Errors, Duration) por servicio.
- Traces: OTel SDK + Jaeger/Tempo. Sampling head 1%, force-keep en errores.
- Alertas: en metrics (latency P99 > X, error rate > Y).
- Debugging: trazas para casos específicos.

**Pregunta avanzada**: "Cómo diferenciarías el problema entre 'red lenta' y 'servicio lento'".

Las traces te dan el timing de la network call vs el timing del servicio receptor (si ambos están instrumentados). Si la diferencia es grande → red lenta. Si el receptor reporta que tardó casi todo → servicio lento.

---

## 10. Trampas típicas

**"Instrumentar todo manualmente"**: usa auto-instrumentation. Solo añade manual para lógica de negocio importante.

**"Capturar 100% de traces en producción"**: vas a quemar dinero y storage. Sampling es obligatorio. 1% probabilistic + force-keep errores es buen default.

**"Confiar en que la propagación funciona"**: un servicio que olvida propagar headers rompe traces. Test it.

**"Tracing reemplaza logs y metrics"**: NO. Son complementarios. Tracing es caro y puntual. Logs son detallados pero no agregables. Metrics son agregables y baratas pero pierden detalle.

**"Logging dentro de spans con todos los detalles"**: si pones todo el body de cada request como span attribute, vas a explotar storage. Atributos selectivos.

**"OpenTelemetry es solo para tracing"**: NO. Cubre los 3 pilares (traces, metrics, logs) bajo un solo standard. La estrategia moderna es ir all-in con OTel.

**"Tracing arregla problemas"**: tracing te muestra dónde está el problema. Arreglarlo es otra historia (fix del código, escalar, refactorizar).

---

## 11. Preguntas típicas de interview

**Diferencia trace vs span**: trace = viaje completo de una request. Span = operación individual dentro.

**Cómo se propaga el contexto entre servicios**: HTTP headers (`traceparent` W3C, `X-B3-*` B3, etc.) que cada servicio debe pasar al siguiente.

**Sampling — por qué y estrategias**: capturar todo es caro. Probabilistic, rate limiting, force-keep errores, tail sampling.

**OpenTelemetry vs Jaeger/Datadog**: OTel es el standard (API + SDK + protocol). Jaeger/Datadog son backends donde envías la telemetría. OTel evita vendor lock-in.

**Logs vs metrics vs traces — cuándo cada uno**: logs detallados puntuales. Metrics agregadas baratas. Traces para flujo entre servicios y latency analysis.

**Cómo debugarías microservicio lento**: metrics → identificar pattern → traces de ese caso → analizar spans para encontrar bottleneck.

---

## 12. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué tracing es necesario en microservicios (logs por servicio no bastan).
- Trace vs span. Árbol de spans con padre-hijo.
- Cómo se propaga el contexto (HTTP headers).
- Sampling: por qué (coste), estrategias (head, tail, adaptive).
- OpenTelemetry: standard, evita vendor lock-in.
- Auto-instrumentation vs manual.
- Logs vs metrics vs traces (3 pilares complementarios).
- Backends populares (Jaeger, Tempo, Datadog).

Si no puedes → relee.

---

## ¡Cluster Distributed Systems completado! 🎉

Has completado el sexto Tier 2 (segundo de los avanzados). Resumen:

- `01-cap-pacelc` — los límites fundamentales y cómo razonar trade-offs.
- `02-consensus-paxos-raft` — cómo conseguir strong consistency con N nodos.
- `03-eventual-consistency` — la alternativa pragmática para escalar.
- `04-distributed-tracing` — cómo entender qué pasa cuando algo va mal.

**Próximo (según tu pedido)**: cluster 05 (Database Internals — 5 docs).

---

## Conexiones

- [[01-cap-pacelc]] — el modelo teórico
- [[02-consensus-paxos-raft]] — cómo conseguir strong cuando hace falta
- [[03-eventual-consistency]] — la alternativa pragmática
- [[../05_database_internals/04-replication-y-sharding]] — replication usa estos conceptos
- [[../04_system_design_patterns/03-message-queues]] — colas necesitan tracing también
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **OpenTelemetry docs** (opentelemetry.io) — referencia oficial.
- **Distributed Systems Observability** (Cindy Sridharan, gratis O'Reilly) — el ebook clásico.
- **Observability Engineering** (Charity Majors et al., 2022) — estado del arte.
- **Honeycomb blog** — escriben muy bien sobre observability moderna.
- **Google Dapper paper (2010)** — el padre del distributed tracing moderno.
- **Jaeger docs** (jaegertracing.io) — para empezar a practicar.
