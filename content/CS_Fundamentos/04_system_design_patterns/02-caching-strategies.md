# 02 — Caching strategies

> 📚 **Doc 2 del cluster System Design Patterns**. Cómo guardar datos cerca para ir más rápido. Patrón ubicuo: del CPU L1 cache al CDN global.
> 🔥 **Frecuencia interview**: aparece SIEMPRE en system design. "Cómo aceleras X" → respuesta incluye cache.
> ⏱️ **Tiempo de lectura estimado**: 40-55 min.

---

## 1. Por qué caching

**Problema**: recuperar datos de la fuente original es **caro**:

- DB query: 1-50ms.
- HTTP request a otro servicio: 10-200ms.
- Disco lento: 1-10ms.
- Cómputo complejo: variable.

Si tienes 10K usuarios pidiendo lo mismo, repites el mismo trabajo 10K veces por segundo.

**Solución — cache**: guarda copia del resultado en lugar más rápido. La próxima request lee del cache (μs en RAM, ms en cache distribuido) en vez de regenerar.

**Efectos positivos**:
- Latencia mucho menor para hits.
- Carga reducida en backend / DB.
- Coste menor (menos compute, menos I/O).

**Coste**:
- Complejidad: invalidación, consistencia eventual.
- Memoria adicional (RAM no es gratis).
- *"There are only two hard things in CS: cache invalidation and naming things."* — Phil Karlton.

---

## 2. Niveles de caching (de más cerca a más lejos)

Jerarquía típica con latencias representativas:

| Nivel | Latencia |
|---|---|
| 1. CPU cache (L1/L2/L3) | ~1-10 ns |
| 2. RAM | ~100 ns |
| 3. App-level cache (in-process) | ~1 μs |
| 4. Distributed cache (Redis local) | ~1 ms |
| 5. Distributed cache (Redis remoto) | ~5-10 ms |
| 6. CDN edge | ~10-50 ms (geo) |
| 7. DB / origin | ~10-200 ms |

**Regla**: cachea lo más cerca posible donde tenga sentido. Múltiples niveles combinados (browser → CDN → app cache → Redis → DB).

---

## 3. Patrones de cache (los 4 fundamentales)

### Cache-Aside (lazy loading) — el más común

**Lectura**:
1. App pide dato a cache.
2. Cache hit → devuelve. FIN.
3. Cache miss → app va a DB.
4. App escribe el dato en cache.
5. App devuelve al cliente.

**Escritura**:
1. App escribe en DB.
2. App invalida (o actualiza) la entrada en cache.

**Pseudocódigo**:

```python
def get_user(id):
    user = cache.get(f"user:{id}")
    if user is None:
        user = db.query(f"SELECT * FROM users WHERE id={id}")
        cache.set(f"user:{id}", user, ttl=300)
    return user

def update_user(id, data):
    db.update(...)
    cache.delete(f"user:{id}")  # o cache.set(f"user:{id}", new_value)
```

**Ventajas**:
- Solo cachea lo que se pide (no llena cache con basura).
- Fácil de implementar.
- Si cache cae, app sigue funcionando (más lento).

**Desventajas**:
- Primer request de cada dato es lento (cache miss).
- Race conditions posibles entre miss + escritura cache.

**Uso**: el default. 80% de los caches en producción son cache-aside.

### Read-Through

Similar a cache-aside pero el cache library/lib gestiona el "miss". La app SOLO habla con el cache. El cache va a DB si no tiene.

**Pseudocódigo** (la app no sabe de DB):

```python
user = cache.get(f"user:{id}", loader=lambda: db.query(...))
```

**Ventajas**:
- Lógica centralizada en el cache.
- App más limpia.

**Desventajas**: necesita cache library que soporte loader (no todos).

**Uso**: caches con bibliotecas avanzadas (Caffeine en Java, etc.).

### Write-Through

La app escribe en cache primero. El cache propaga la escritura a DB sincronamente.

**Pseudocódigo**:

```python
cache.set(f"user:{id}", new_data)   # cache también escribe DB
```

**Ventajas**: cache siempre sincronizado con DB (consistencia fuerte).

**Desventajas**:
- Cada write tiene latencia de DB.
- Cachea cosas que quizás nadie lee.

**Uso**: sistemas que requieren consistencia sólida cache↔DB.

### Write-Behind (Write-Back) — más rápido pero peligroso

La app escribe en cache. El cache responde OK inmediatamente. El cache flushea a DB de forma **asíncrona** (cola).

**Ventajas**:
- Writes muy rápidos (no espera DB).
- Bursts de writes se absorben.

**Desventajas**:
- Si el cache cae antes de flush → **datos perdidos**.
- Consistencia eventual (DB está atrasada).
- Implementación compleja.

**Uso**: métricas, contadores, logs (donde perder algo es aceptable). **NO** para datos críticos (pagos, inventario).

---

## 4. Invalidación — el problema duro

> *"There are only two hard things in CS: cache invalidation and naming things."*

**El problema**: el dato cambia en DB. ¿Cómo se entera el cache?

**Estrategias**:

1. **TTL (Time To Live)**: cada entrada expira tras N segundos. Tras expirar, próximo request va a DB.
   - **Pros**: simple, garantiza consistencia eventual.
   - **Contras**: sirve datos viejos durante el TTL. Tráfico burst tras expiración (thundering herd).
   - **Uso típico**: 90% de caches simples.

2. **Explicit invalidation**: cuando escribes en DB, también invalidas/actualizas cache.
   - **Pros**: datos siempre frescos.
   - **Contras**: requiere disciplina (siempre invalidar). Si tu app olvida → dato stale forever. Race conditions: write A → cache invalidate, write B sees stale, etc.

3. **Write-through** (ya visto): cache se actualiza cada write. Sin invalidación explícita.

4. **Event-driven invalidation**: la DB publica evento (cambio en row X). Workers consumen y invalidan caches.
   - **Uso**: sistemas grandes con CDC (Change Data Capture, Debezium).

5. **Version-based**: cada entrada tiene versión. La read incluye versión esperada. Si no coincide → reintenta.

**Estrategia mixta típica**: TTL corto (60s) + invalidation explícita en writes críticos. Lo mejor de ambos: garantía de eventual consistency + frescura en writes importantes.

---

## 5. Eviction policies — qué tirar cuando el cache está lleno

El cache tiene tamaño limitado. Cuando se llena, hay que sacar algo. ¿Qué?

| Política | Criterio | Notas |
|---|---|---|
| **LRU** (Least Recently Used) | Tira lo menos recientemente accedido | Asume "lo que se usó hace poco se usará pronto". Default en Redis (allkeys-lru), Memcached |
| **LFU** (Least Frequently Used) | Tira lo menos veces accedido en total | Mejor para distribuciones power-law |
| **FIFO** | Tira lo más viejo (insertado primero) | Simple pero no considera uso |
| **Random** | Tira algo aleatorio | Sorprendentemente bueno en algunos benchmarks (Redis allkeys-random) |
| **TTL-only (volatile)** | Solo tira lo que ha expirado por TTL | — |
| **ARC** (Adaptive Replacement Cache) | Combina recency + frequency | Más sofisticado, usado en filesystems (ZFS) |

**Políticas de Redis**:
- `noeviction`: rechaza writes nuevos cuando full.
- `allkeys-lru`: LRU sobre todas las keys.
- `volatile-lru`: LRU sobre keys con TTL.
- `allkeys-lfu`, `volatile-lfu`: similar con LFU.
- `allkeys-random`, `volatile-random`: aleatorio.
- `volatile-ttl`: tira keys con TTL más cercano a expirar.

---

## 6. Tipos de cache por ubicación

### Browser cache (HTTP)

Los HTTP headers controlan el caching:

- `Cache-Control: max-age=3600` → cachea 1h.
- `Cache-Control: no-store` → no cachees.
- `Cache-Control: private` → solo browser, no shared caches.
- `ETag: "abc123"` → versión del recurso.

El cliente envía `If-None-Match: "abc123"`. El server responde `304 Not Modified` si no cambió → no body.

**Uso**: assets estáticos, API responses cacheables.

### CDN (edge cache)

Cache geográficamente distribuida. Cloudflare, Akamai, AWS CloudFront, Fastly.

**Uso**: contenido estático (imágenes, JS, CSS, video), API responses globales. Ver doc 04 para detalle.

### Reverse proxy cache

Nginx, Varnish cachean responses HTTP del backend. Sirven directamente sin pegar al backend.

**Config Nginx típica**:

```nginx
proxy_cache_path /var/cache/nginx ...;
location /api/ {
    proxy_pass http://backend;
    proxy_cache cache_zone;
    proxy_cache_valid 200 5m;
}
```

### App-level cache (in-memory, in-process)

Cache dentro del proceso de la app:
- `functools.lru_cache` (Python).
- Caffeine, Guava (Java).
- node-cache (Node).

**Pros**: súper rápido (RAM local).
**Contras**: no compartido entre instancias. Se pierde al reiniciar.

**Uso**: cosas inmutables (config), o caches per-user de corta duración.

### Distributed cache (Redis, Memcached)

Cache compartida entre todos los servers:
- **Redis**: muy popular, soporta estructuras complejas (lists, sets, sorted sets).
- **Memcached**: más simple, solo key-value.

**Pros**: shared state. Sobrevive al restart de la app.
**Contras**: hop de red (~ms). Hay que manejar conexión/pool.

**Uso**: el cache "principal" de la mayoría de apps modernas.

### Database query cache

La DB cachea internamente:
- **Postgres**: `shared_buffers` (páginas en RAM).
- **MySQL**: query cache (deprecated en 8+, era buggy).

**Uso**: implícito, transparente. Tu app no sabe.

---

## 7. Problemas comunes

### Cache stampede (thundering herd)

**Escenario**: una key popular expira. 10K requests concurrent llegan, todas cache miss. Las 10K van a DB simultáneamente. La DB se satura.

**Soluciones**:

**A) Probabilistic early expiration**: un pequeño % de requests refresca antes del TTL real. Reparte el load.

**B) Lock on miss**: solo el primer request en miss va a DB. Otros esperan o devuelven valor stale.

```python
def get(key):
    value = cache.get(key)
    if value is None:
        if cache.set_lock(f"lock:{key}", timeout=10):
            try:
                value = db.query(...)
                cache.set(key, value, ttl=300)
            finally:
                cache.unlock(f"lock:{key}")
        else:
            # Otro está fetcheando, espera o retorna stale
            value = wait_or_stale(key)
    return value
```

**C) Stale-while-revalidate**: sirve valor stale + dispara refresh async. El cliente nunca espera DB.

### Hot key

Una key recibe muchísimo tráfico (ej: post viral, perfil de famoso). Concentra carga en un solo nodo del cache distribuido.

**Soluciones**:
- Replicar key en N nodos.
- Cache local en cada app server (L1 + L2 layered cache).
- Sharding por subkey (`post:123:part1`, `part2`, `part3`).

### Cache poisoning

Un atacante consigue meter datos malos en cache. Próximos usuarios reciben datos contaminados.

**Prevención**:
- Validar input antes de cachear.
- No cachear responses de errores.
- TLS entre app y cache (Redis con AUTH y TLS).

### Cache penetration

Requests para keys que NO existen inundan la DB. Ej: scraper pidiendo IDs que no existen → siempre cache miss → siempre DB.

**Soluciones**:
- Cachear el "no existe" (con TTL corto).
- Bloom filter: chequea si la key PUEDE existir antes de ir a DB.
- Rate limiting por user/IP.

---

## 8. Cache key design

**Buenas prácticas**:
- **Namespacing**: `user:123`, `post:456`, no solo `"123"`.
- **Versionar**: `user:v2:123`. Permite migración sin invalidar todo.
- **Hash de queries complejas**: `query:abc123def...`.
- **No incluir datos sensibles** (los logs revelan keys).

**Estructura típica**:

```
<env>:<service>:<entity>:<id>
prod:userservice:user:123
```

Permite multi-tenant en el mismo Redis cluster.

---

## 9. Métricas críticas

- **Hit ratio**: `cache_hits / (cache_hits + cache_misses)`. Target típico: 80%+ para cache útil. <50% es señal de mal diseño.
- **Latency**: P50, P95, P99 de get/set. Si P99 dispara, problema (network, GC pauses).
- **Eviction rate**: cuántas keys se evictan/segundo. Si alto: cache demasiado pequeño.
- **Memory usage**: RSS del Redis. Si llega al `maxmemory`: la eviction comienza.

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

- T1.3 build cache con Redis: cache-aside es el patrón natural.
- TTL de 60s para listings, invalidación explícita en POST/PUT/DELETE.
- En tu MOC_Build_Things ya está documentado.

### En entrevistas tecnicas

**Pregunta**: "Cómo optimizas tu API que hace muchas queries lentas".
→ Cache-aside con Redis. Identificar queries hot. TTL ajustado al churn de datos. Invalidation en writes.

**Pregunta**: "¿Cuál es la diferencia entre write-through y write-behind?"
→ WT: escribe en cache + DB sync. Consistencia, latencia alta. WB: escribe solo cache, async a DB. Rápido, riesgo de pérdida.

**Pregunta**: "Cómo manejas cache stampede".
→ Probabilistic early expiration, lock on miss, o stale-while-revalidate.

**Pregunta**: "Diferencia entre LRU y LFU".
→ LRU: least recently used. LFU: least frequently used (cuenta accesos totales). LFU mejor para distribuciones long-tail estables.

**Pregunta**: "Por qué Redis en vez de DB cache".
→ Redis es in-memory (RAM), DB cache lee de disk (incluso buffer). Latencia ~1ms vs ~10ms. Soporta estructuras (lists, sets, sorted sets).

---

## 11. Trampas típicas

**Trampa 1 — "Cache always improves performance"**: si hit ratio < 50%, añade overhead sin beneficio. Si keys muy variadas (long tail extrema), cache no ayuda. Mide antes y después.

**Trampa 2 — "TTL infinito está bien"**: datos viejos contaminan respuestas. Siempre poner TTL razonable.

**Trampa 3 — "Invalidation está resuelta con DEL key"**: race conditions: write A → DEL cache → read mete dato viejo en cache. Patrón: write + DEL + delay + DEL otra vez ("double delete").

**Trampa 4 — "Cachear responses con cookies/auth"**: diferentes usuarios ven cosas distintas. No cachear personalizado o usar key incluyendo `user_id`.

**Trampa 5 — "Redis tiene tamaño infinito"**: la RAM cuesta dinero. `maxmemory` + eviction policy son obligatorios en producción.

**Trampa 6 — "Mismo TTL para todo"**: datos distintos cambian a ritmos distintos. TTL ajustado por tipo.

**Trampa 7 — "Cache cae = catástrofe"**: si tu app no funciona sin cache, hay que rediseñar. El cache debe ser optimización, no dependencia crítica.

---

## 12. Preguntas típicas de interview

**Pregunta 1 — "Patrones de cache"**: cache-aside (lazy), read-through, write-through, write-behind. Tradeoffs.

**Pregunta 2 — "Eviction policies"**: LRU, LFU, FIFO, random, TTL. Cuándo cada una.

**Pregunta 3 — "Cache invalidation strategies"**: TTL, explicit, write-through, event-driven, version-based.

**Pregunta 4 — "Cache stampede y soluciones"**: múltiples requests miss → DB saturada. Lock on miss, probabilistic early expiration, stale-while-revalidate.

**Pregunta 5 — "Diseña cache de Twitter timeline"**: multi-layer: CDN para static, Redis para timelines (sorted set por user), fanout-on-write o fanout-on-read según usuario.

**Pregunta 6 — "Cómo medir si tu cache es útil"**: hit ratio target 80%+. Latency P99. Eviction rate. Memory usage. Si quitas el cache, ¿cómo cambia P95 latency?

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué cachear (latencia, carga DB, coste).
- Niveles: L1/L2/L3 CPU → Redis → CDN.
- Cache-aside: el patrón default y por qué.
- Diferencia write-through vs write-behind.
- Eviction: LRU vs LFU vs FIFO vs random.
- TTL como invalidación implícita.
- Cache stampede: 3 soluciones.
- Cache penetration con bloom filter.
- Cuándo cachear y cuándo NO.

Si no puedes → relee.

---

## Conexiones

- [[01-load-balancing]] — caches detrás del LB
- [[03-message-queues]] — alternative a cache para algunos casos
- [[04-cdn-y-edge]] — cache geográfico
- [[05-rate-limiting]] — Redis útil para ambos
- [[../05_database_internals/01-b-trees-y-indexing]] — cache de DB internamente
- [[../02_operating_systems/02-memoria-virtual-paging]] — page cache del SO
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Redis docs** (redis.io/docs) — referencia.
- **Designing Data-Intensive Applications** capítulos 1, 5 — caches y replicación.
- **AWS Caching Best Practices** — guía práctica.
- **Caching at Netflix** (techblog.netflix.com) — case study real.
- **Cache replacement policies** (Wikipedia) — comparativa académica.
