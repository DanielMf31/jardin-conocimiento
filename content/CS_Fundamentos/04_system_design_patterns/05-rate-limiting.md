# 05 — Rate limiting

> 📚 **Doc 5 (último) del cluster System Design Patterns**. Cómo proteger tu sistema de abuso, picos y errores en cascada.
> 🔥 **Frecuencia interview**: aparece SIEMPRE en system design. "Cómo proteges tu API de DDoS / scrapers / bug en cliente que hace 1000 req/s".
> ⏱️ **Tiempo de lectura estimado**: 30-45 min.

---

## 1. Por qué rate limiting

Sin rate limiting, **cualquier cliente puede hacer infinitas requests**. Los problemas que esto crea son múltiples y todos serios:

- **Coste descontrolado**: tu API hace queries DB, llama a otros servicios, paga por egress. Un cliente con bug puede dispararte la factura cloud.
- **Saturación del backend**: si 1 cliente envía 10K req/s, satura tu DB y los demás clientes sufren latency.
- **Abuso intencional**: scrapers que descargan tu catálogo entero, ataques DDoS, intentos de brute-force a passwords.
- **Cascading failures**: un cliente saturado satura tu servicio → otros servicios que dependen de ti también caen.

**Rate limiting** = **limitar cuántas requests puede hacer cada cliente en una ventana de tiempo**. Es la primera línea de defensa de toda API pública.

---

## 2. Anatomía de un rate limit

Toda regla de rate limiting tiene tres dimensiones:

1. **Cuánto** — el límite. Ej: "100 requests".
2. **En qué tiempo** — la ventana. Ej: "por minuto".
3. **Por quién** — la clave de identidad. Ej: "por API key", "por IP", "por user_id".

**Ejemplo típico**: "100 requests por minuto por API key".

Cuando un cliente excede, el server responde con **HTTP 429 Too Many Requests** y típicamente headers indicando cuándo puede volver a intentar:

- `X-RateLimit-Limit: 100` — el límite total.
- `X-RateLimit-Remaining: 0` — cuántas le quedan.
- `X-RateLimit-Reset: 1715353200` — Unix timestamp cuando se resetea.
- `Retry-After: 30` — segundos a esperar antes de retry.

---

## 3. Los algoritmos clásicos

Hay 5 algoritmos clásicos. Cada uno tiene un trade-off entre simplicidad, precisión y consumo de memoria.

### Fixed Window

El más simple. Divide el tiempo en ventanas fijas (cada minuto, cada hora). Cuenta requests dentro de la ventana actual. Cuando se llena, rechaza hasta la siguiente.

**Ejemplo**: límite de 100 req/min. Ventana de las 12:00:00 a 12:00:59. Si en esa ventana hay 100 requests, las siguientes 100 a 12:00:30 son rechazadas. A las 12:01:00 empieza ventana nueva con contador a 0.

**Implementación trivial en Redis**:
```python
key = f"rate:{user_id}:{int(time.time() // 60)}"
count = redis.incr(key)
if count == 1:
    redis.expire(key, 60)
if count > 100:
    return 429
```

**Problema clásico**: el "burst de límite". Si el cliente hace 100 requests al final de una ventana y otras 100 al inicio de la siguiente, son 200 requests en 2 segundos, "respetando" el límite técnicamente. Esto puede saturar tu backend.

**Cuándo usarlo**: prototipos, casos donde el burst no importa, o cuando la implementación trivial vale más que la precisión.

### Sliding Window Log

Guarda el **timestamp de cada request**. Para chequear, cuenta cuántos timestamps están dentro de los últimos 60 segundos.

**Ventaja**: precisión total. No hay efecto burst de borde.

**Desventaja**: memoria proporcional al volumen de requests. Si tu API tiene 1M req/min, guardas 1M timestamps. Inviable a gran escala.

**Cuándo usarlo**: APIs con bajo volumen donde la precisión importa (e.g. límites estrictos en login attempts).

### Sliding Window Counter

Aproximación inteligente del Sliding Window Log. Guarda el contador de la ventana ACTUAL y la ANTERIOR. Cuando chequea, calcula un "contador efectivo" interpolando.

**Fórmula**: `count_efectivo = count_actual + count_anterior * (1 - posición_dentro_de_ventana)`.

**Ejemplo**: estás a 30 segundos de una ventana de 60s. Tienes 50 requests en la actual y 80 en la anterior. Count efectivo: 50 + 80 × 0.5 = 90.

**Ventaja**: precisión decente con O(1) memoria por usuario. Es el algoritmo que usan **Cloudflare y muchas APIs grandes** por defecto.

**Desventaja**: aproximación, no exacto. Asume distribución uniforme dentro de cada ventana.

### Token Bucket

Modelo más flexible y popular. Imagina un cubo que se rellena a ritmo constante (R tokens/segundo) hasta una capacidad máxima (B tokens). Cada request consume 1 token. Si no hay tokens, se rechaza.

**Por qué es popular**: permite **bursts controlados**. Si un cliente está callado 5 minutos, su cubo se llena al máximo. Después puede hacer un burst hasta el tamaño del cubo, y luego sigue al ritmo de refill.

**Parámetros**:
- **Capacity (B)**: tamaño del cubo. Define el burst máximo.
- **Refill rate (R)**: tokens añadidos por segundo. Define el throughput sostenido.

**Ejemplo**: B=100, R=10/s. El cliente puede hacer 100 req instantáneas (consume todos los tokens) y después solo 10/s sostenidas hasta que el cubo se rellene.

**Implementación Redis** con Lua script para atomicidad:
```lua
-- Pseudocódigo
local now = tonumber(ARGV[1])
local capacity, refill_rate = 100, 10
local last_refill = redis.call('HGET', key, 'last_refill') or now
local tokens = redis.call('HGET', key, 'tokens') or capacity
local elapsed = now - last_refill
tokens = math.min(capacity, tokens + elapsed * refill_rate)
if tokens >= 1 then
    tokens = tokens - 1
    redis.call('HSET', key, 'tokens', tokens, 'last_refill', now)
    return 1  -- allowed
else
    return 0  -- rejected
end
```

**Cuándo usarlo**: la opción default moderna. Stripe, AWS, GCP, casi todas las APIs serias usan token bucket o variante.

### Leaky Bucket

Modelo dual al token bucket. Las requests **entran** a un cubo que tiene capacidad limitada. El cubo **gotea** (procesa) a ritmo constante. Si llega una request cuando el cubo está lleno, se rechaza.

**Diferencia clave con token bucket**: el leaky bucket **suaviza el output** (envía requests al backend a ritmo constante), mientras que el token bucket **suaviza el input** (limita lo que entra).

**Ejemplo**: cubo de 100 requests, leak rate 10/s. Si llegan 200 requests instantáneas, las primeras 100 se encolan, las otras 100 se rechazan. El backend recibe a ritmo de 10/s constantes, sin importar bursts.

**Cuándo usarlo**: cuando quieres proteger un backend frágil que se rompe con bursts. Útil en colas de procesamiento batch.

---

## 4. Comparativa rápida

| Algoritmo | Memoria | Precisión | Permite burst | Complejidad |
|---|---|---|---|---|
| Fixed Window | O(1) | Baja (efecto borde) | No (instantáneo) | Trivial |
| Sliding Window Log | O(N) | Total | No | Media |
| Sliding Window Counter | O(1) | Alta (aprox) | No | Media |
| Token Bucket | O(1) | Alta | Sí (controlado) | Media |
| Leaky Bucket | O(N) | Total | Suaviza output | Media |

**Recomendación práctica**: empezar con **Sliding Window Counter** (Cloudflare-style) o **Token Bucket** según necesites o no permitir bursts.

---

## 5. Por dónde identificar al cliente

Decidir **por quién** rate-limitas es tan importante como el algoritmo. Las opciones típicas, de menos a más fina:

- **Por IP**: simple pero falla con NAT (todos detrás del mismo router parecen 1 cliente) y con clientes legítimos compartiendo IP (oficinas, universidades). También fácil de evadir con VPN/proxy.
- **Por API key**: identifica al cliente real registrado. La opción para APIs B2B.
- **Por user_id (autenticado)**: para apps con login. Más fino que API key cuando un user puede tener múltiples sesiones.
- **Por endpoint + identidad**: límites distintos por endpoint. `/login` con límite estricto (5/min para anti-brute-force), `/api/products` con límite generoso.
- **Por tier de usuario**: free tier 100 req/h, pro 10K req/h, enterprise 1M req/h. Lo que hace Stripe, GitHub, OpenAI.

**Patrón típico moderno**: combinar varios. "Por IP para no autenticados (anti-abuse) + por user_id para autenticados (anti-bug)".

---

## 6. Rate limiting distribuido — el problema duro

Si tu API tiene **N servers** detrás de un load balancer, cada uno tiene su propio contador. Un cliente puede hacer 100 req a cada server (total 100×N). El límite "100 req/min" se viola fácilmente.

**Soluciones**:

### Centralizar en Redis

Cada server consulta/incrementa contadores en un Redis compartido. Es la solución estándar.

**Pros**: precisión global. Implementación conocida.

**Contras**: latencia extra por cada request (~1ms). Redis se convierte en SPOF — necesita HA. Si Redis cae, ¿permites o rechazas todo? (fail-open vs fail-closed).

**Optimización con Lua**: script atómico en Redis evita race conditions y requiere solo 1 round-trip por request.

### Sticky sessions

Si el load balancer envía siempre al mismo cliente al mismo server (via cookie o IP hash), cada server lleva contador local sin Redis. Más simple pero perdemos las ventajas de stateless backends.

### Sharding del rate limiter

Distribuir las claves entre N nodos (consistent hashing). Cada nodo lleva una porción de los contadores.

**Pros**: escala horizontalmente. Sin SPOF.

**Contras**: complejidad. Si un nodo cae, su porción de límites se pierde temporalmente.

### Approximation (counters locales + sync periódico)

Cada server cuenta local. Periódicamente (cada 100ms) sincroniza con un servicio central que tiene la suma. Aproximación rápida, no exacta.

**Pros**: latencia mínima (no sync por request).

**Contras**: aproximación. Cliente puede exceder ligeramente entre sincronizaciones. Aceptable si el coste de exactitud es alto.

---

## 7. Backoff y retry — del lado del cliente

Cuando un cliente recibe **429**, debe esperar antes de reintentar. La estrategia importa enormemente:

- **Linear backoff**: espera N segundos entre retries. Simple pero peligroso bajo carga (todos los clientes retrian al mismo tiempo → thundering herd).
- **Exponential backoff**: 1s, 2s, 4s, 8s, 16s... Mejor que lineal. Pero si todos los clientes empiezan al mismo tiempo, retrian al mismo tiempo.
- **Exponential backoff + jitter**: añadir aleatoriedad a cada retry. Es **el estándar moderno**. Evita el thundering herd.

**Implementación recomendada** (AWS/Stripe-style):
```python
import random, time

for attempt in range(max_retries):
    try:
        response = make_request()
        if response.status == 429:
            base_delay = min(2 ** attempt, 60)  # exponencial capped a 60s
            jitter = random.uniform(0, base_delay)
            time.sleep(jitter)
            continue
        return response
    except Exception:
        ...
```

**Honra el header `Retry-After`** si el server lo manda — es más inteligente que tu backoff a ciegas.

---

## 8. Diferencia con load balancing y throttling

Estos conceptos suelen confundirse:

- **Load balancing**: distribuye carga entre N backends. No limita.
- **Rate limiting**: limita peticiones por cliente identificado. Defensa.
- **Throttling**: ralentiza requests (no las rechaza). Devuelve 200 pero más lento.
- **Circuit breaker**: detecta backend caído y deja de mandarle tráfico. Resilience.
- **Bulkhead**: aísla recursos para que un fallo no propague. Resilience.

Todos son patrones de protección complementarios. Un sistema serio usa varios a la vez.

---

## 9. Rate limiting en distintos lugares

Un sistema con rate limiting maduro tiene capas:

1. **CDN / edge** (Cloudflare, AWS WAF): primera línea contra DDoS volumétricos. Bloquea IPs malicias antes de llegar a ti.
2. **Load balancer / API Gateway** (Nginx, Kong, Envoy): rate limits gruesos por IP/API key.
3. **Application middleware** (FastAPI middleware, Express middleware): rate limits finos por endpoint y user.
4. **Service-level** entre microservicios: para evitar que un servicio rompa otro.

Cada capa filtra distinto. **Las primeras protegen contra ataques masivos; las últimas contra abuso fino**.

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Hoy no necesitas rate limiting (API local sin exposición). Cuando despliegues a cloud y sea pública, sí. Implementación rápida con `slowapi` (basado en `flask-limiter` portado a FastAPI):

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/contacts")
@limiter.limit("10/minute")
def create_contact(...):
    ...
```

### En entrevistas tecnicas

**Pregunta clásica**: "Diseña rate limiting para una API global con 1B req/día".

Tu respuesta debería tocar:
1. Algoritmo: token bucket por defecto (permite bursts controlados).
2. Identificación: combinar IP (anti-DDoS) + API key (anti-bug).
3. Distribución: Redis cluster centralizado con Lua scripts atómicos.
4. Múltiples capas: CDN/WAF + LB + app middleware.
5. Tiers: free/pro/enterprise con límites distintos.
6. Headers de respuesta: 429 + Retry-After + X-RateLimit-*.
7. Cliente: documentar exponential backoff + jitter.

**Pregunta avanzada**: "Cómo prevenir DDoS de un atacante con 1M IPs distintas".

Aquí no basta con rate limiting clásico. Necesitas:
- WAF en edge con detección de patrones anómalos.
- Captcha tras N intentos.
- Behavioral analysis (ML).
- IP reputation databases.
- Rate limit por sesión TLS (más caro de evadir que IP).

---

## 11. Trampas típicas

- **Rate limit demasiado estricto**: rompe casos legítimos (clientes con burst legítimo, retrials por errores temporales). Empezar generoso, ajustar.
- **No comunicar el límite**: si el cliente no sabe cuánto puede pedir, su único feedback es el 429. Headers `X-RateLimit-*` son obligatorios en APIs serias.
- **Solo rate limit por IP**: NAT/VPN rompe esto. Combinar con autenticación.
- **Olvidar fail-open vs fail-closed**: si Redis cae, ¿permites todo (fail-open, riesgo de abuso pero servicio sigue) o rechazas todo (fail-closed, seguro pero servicio caído)? Decisión consciente.
- **No rate limit en login**: cualquier endpoint de auth necesita rate limit AGRESIVO (5/min por IP típicamente) contra brute-force.
- **Bursts ilimitados con token bucket**: si capacity = 10000 y refill = 10/s, un cliente puede hacer 10000 req instantáneas. Calibrar capacity en función de lo que tu backend tolere.
- **Rate limiting en el lado equivocado**: si pones rate limit solo en application server pero no en CDN, el ataque DDoS te tira el server antes.

---

## 12. Preguntas típicas de interview

**¿Por qué rate limiting?** Proteger backend de abuso, controlar coste, prevenir cascading failures, fairness entre clientes.

**Algoritmos y cuándo usar cada uno**: ya cubierto en sección 3. Mencionar token bucket como default + sliding window counter para Cloudflare-style.

**¿Cómo lo implementarías distribuido?** Redis centralizado con Lua scripts (atomic). Considerar fail-open vs fail-closed cuando Redis cae.

**Token bucket vs leaky bucket**: token suaviza input (permite bursts). Leaky suaviza output (ritmo constante al backend).

**¿Qué headers HTTP usarías?** 429 status, X-RateLimit-Limit/Remaining/Reset, Retry-After.

**¿Cómo manejas DDoS de millones de IPs?** WAF en edge con behavioral detection, captcha, IP reputation, rate limit por sesión TLS.

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué existe rate limiting (4-5 razones).
- Anatomía: cuánto, en qué tiempo, por quién.
- Los 5 algoritmos clásicos y trade-offs principales.
- Token bucket (capacity + refill rate) como default.
- Sliding window counter como aproximación O(1) precisa.
- 429 + headers X-RateLimit-* + Retry-After.
- Distribuido: Redis centralizado con Lua atomic.
- Exponential backoff + jitter en cliente.
- Capas: CDN/WAF → LB → app middleware → service-level.

Si no puedes → relee.

---

## ¡Cluster System Design Patterns completado! 🎉

Has completado el cuarto Tier 1. Resumen de lo dominado:

- `01-load-balancing` — distribuir carga (L4/L7, algoritmos, health checks).
- `02-caching-strategies` — cache patterns, eviction, invalidation, stampede.
- `03-message-queues` — queue/pubsub/log, garantías de entrega, Kafka vs RabbitMQ.
- `04-cdn-y-edge` — distribución geográfica, edge compute.
- `05-rate-limiting` — protección, algoritmos, distribución, backoff.

**Próximo**: cluster 06 (Distributed Systems), siguiendo tu pedido de hacerlo antes que el 05.

---

## Conexiones

- [[01-load-balancing]] — rate limit suele integrarse con LB
- [[02-caching-strategies]] — Redis sirve para ambos
- [[03-message-queues]] — backpressure tiene relación
- [[04-cdn-y-edge]] — primera línea de defensa contra DDoS
- [[../01_networking/02-http-y-evolucion]] — HTTP 429 + headers
- [[../03_concurrency/02-locks-y-mutex]] — atomic ops para counters
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **System Design Interview** (Alex Xu) capítulo Rate Limiter — referencia clásica.
- **Cloudflare blog: How we built rate limiting** — case study real.
- **Stripe API docs: rate limits** — ejemplo práctico bien documentado.
- **AWS: Exponential backoff and jitter** — paper clásico (aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/).
- **slowapi** (Python), **express-rate-limit** (Node), **bucket4j** (Java) — librerías populares.
