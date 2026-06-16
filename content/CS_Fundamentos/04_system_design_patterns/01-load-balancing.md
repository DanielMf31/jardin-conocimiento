# 01 — Load balancing

> 📚 **Doc 1 del cluster System Design Patterns**. El patrón #1 que aparece en TODA system design entrevistas tecnicas. Sin load balancer no hay sistema escalable.
> 🔥 **Frecuencia interview**: aparece SIEMPRE. Si te preguntan "diseña Twitter" o "diseña X", el LB es de las primeras decisiones.
> ⏱️ **Tiempo de lectura estimado**: 40-55 min.

---

## 1. Qué es y qué problema resuelve

**Problema sin load balancer**: 1 servidor recibe TODAS las peticiones.

- Si cae → todo el sistema cae (single point of failure).
- Si sube el tráfico → se satura, la latencia se dispara.
- No puedes escalar añadiendo más servers (¿a cuál van las requests?).

**Solución: load balancer (LB)**. Componente que distribuye las requests entrantes entre N servidores. El cliente solo conoce al LB; el LB decide qué backend atiende.

**Efectos**:

- ✅ **Escalado horizontal**: añade más backends y el LB los usa.
- ✅ **Alta disponibilidad**: si 1 backend cae, el LB enruta a otros.
- ✅ **Mantenimiento sin downtime**: drenas un backend para actualizarlo.
- ✅ **Distribución geográfica** (en LBs avanzados).

---

## 2. Anatomía del flujo

**Antes (sin LB)**:

```
Cliente1 ──┐
Cliente2 ──┼──→ Server único (192.168.1.10:8000)
Cliente3 ──┘
```

**Con LB**:

```
                   ┌──→ Backend1 (192.168.1.10:8000)
Cliente1 ──┐       │
Cliente2 ──┼──→ LB ┼──→ Backend2 (192.168.1.11:8000)
Cliente3 ──┘       │
                   └──→ Backend3 (192.168.1.12:8000)
```

El cliente solo conoce al LB. El LB decide cuál backend recibe cada request.

---

## 3. Layer 4 vs Layer 7 — la distinción crítica

Los LBs operan en distintas capas del modelo OSI/TCP-IP. Cada capa permite/limita decisiones distintas.

### Layer 4 (Transport — TCP/UDP)

**El LB solo ve**: IP origen, IP destino, puertos, protocolo (TCP/UDP). **No ve** el contenido HTTP (no hace TLS termination).

**Decisión**: basada en cabeceras TCP/IP. Round robin, hash de IP, etc.

**Pros**:

- Súper rápido (poco que parsear).
- No necesita conocer el protocolo de aplicación.
- Funciona con cualquier protocolo (TCP, UDP, custom).

**Contras**:

- No puede tomar decisiones basadas en URL, headers o cookies.
- La conexión TCP del cliente termina en el backend (passthrough).

**Ejemplos**: AWS NLB (Network Load Balancer), HAProxy en modo TCP, IPVS (Linux kernel), Nginx stream module.

### Layer 7 (Application — HTTP)

**El LB entiende HTTP**: URL path (`/api/users` vs `/static/css`), headers (Authorization, User-Agent, Cookie), método (GET, POST), hostname (Host header).

**Decisión**: basada en contenido HTTP. Routing inteligente.

**Pros**:

- Routing por path: `/api` → backend A, `/images` → backend B (CDN).
- Sticky sessions por cookie.
- Compresión, caching, TLS termination.
- Rate limiting por user/IP.
- WAF (Web Application Firewall).

**Contras**:

- Más lento (parsea HTTP).
- Solo HTTP/HTTPS.
- Termina la conexión TCP del cliente y abre una nueva al backend.

**Ejemplos**: AWS ALB (Application Load Balancer), Nginx, Caddy, Traefik (modo HTTP), HAProxy en modo HTTP, Envoy, Cloudflare.

**Para tu Phone Book**: si despliegas FastAPI detrás de un proxy, casi siempre será L7 (Caddy/Nginx). Si necesitaras balancear gRPC nativo (no vía HTTP/2 wrapping) o protocolos custom, L4.

---

## 4. Algoritmos de balanceo

### Round Robin (RR)

Asigna requests **en orden**: backend 1, 2, 3, 1, 2, 3, ...

- **Ventaja**: simple, fair en condiciones uniformes.
- **Desventaja**: no considera la carga real de cada backend. Si el backend 2 está ocupado, sigue recibiendo.
- **Uso**: cuando todos los backends son idénticos y las requests son homogéneas.

### Weighted Round Robin

Round robin con pesos. `Backend1 weight=3`, `Backend2 weight=1`: 3 requests al primero por cada 1 al segundo.

- **Uso**: cuando los backends tienen distinta capacidad (CPU, RAM). Migración gradual: nuevo deployment con weight bajo, sube progresivamente.

### Least Connections

El LB envía la request al backend con **menos conexiones activas** en este momento.

- **Ventaja**: se adapta a la carga real. Backends con requests largos no se saturan más.
- **Desventaja**: requiere LB stateful (cuenta conexiones). Más overhead que round robin.
- **Uso**: cuando las requests tienen duraciones muy variables. Ej: API que mezcla queries rápidas con jobs largos.

### Least Response Time

Combina menos conexiones + tiempo de respuesta promedio. Envía al backend más "rápido" actualmente.

- **Ventaja**: optimiza la latencia percibida por el cliente.
- **Desventaja**: mide latencia (overhead). Puede oscilar.
- **Uso**: APIs latency-sensitive.

### IP Hash / Consistent Hashing

`Hash(IP cliente) → backend`. El mismo cliente siempre va al mismo backend (sticky por IP).

- **Ventaja**: cache locality, sticky sessions sin cookies.
- **Desventaja**: si el backend cae, todos sus clientes pierden caché. Distribución desigual si hay pocos clientes con mucho tráfico.

**Consistent hashing**: variante avanzada. Si añades/quitas backends, solo `1/N` de las claves se redistribuyen (no todas). Esencial para sistemas distribuidos (Cassandra, Memcached). Ver doc 04 (CDN) para más detalle.

- **Uso**: cache layers, stateful services con afinidad.

### Random

Aleatorio simple. Sorprendentemente, tan bueno como round robin para muchos casos, sin necesidad de mantener estado.

- **Uso**: backends idénticos, simplicidad máxima.

### Power of Two Choices (P2C)

Elige 2 backends al azar y manda al que tenga **menos conexiones**.

Contraintuitivo pero brillante: casi tan bueno como Least Connections puro, mucho más eficiente (no escanea todos los backends), probabilísticamente excelente.

- **Uso**: sistemas modernos a gran escala (Netflix, Twitter).

---

## 5. Health checks — vital para evitar enviar tráfico a backends muertos

El LB chequea periódicamente si cada backend está vivo. Si un backend falla N checks consecutivos → "unhealthy" y se quita del pool. Si vuelve a responder → "healthy" y se reincorpora.

**Tipos de health check**:

- **Active (proactive)**: el LB hace requests periódicas, ej: `GET /health` cada 5s. Si responde 200 → healthy. Si timeout o 5xx → unhealthy.
- **Passive (reactive)**: el LB observa requests reales. Si N consecutivas fallan → unhealthy. No genera tráfico extra pero detecta más lento.

**Endpoints de health**:

- `/health`: básico, "estoy vivo".
- `/ready`: "puedo aceptar tráfico" (deps OK, warmup hecho).
- `/startup`: "todavía arrancando, no me peguen".

Kubernetes usa los 3 distintos (liveness, readiness, startup probes).

**Parámetros típicos**:

| Parámetro | Descripción | Default típico |
|---|---|---|
| Interval | Cada cuántos segundos chequear | 5-30s |
| Timeout | Cuánto esperar respuesta | 2-5s |
| Healthy threshold | N éxitos para marcar healthy | 2 |
| Unhealthy threshold | N fallos para marcar unhealthy | 3 |

**Tradeoff**: detectar fallos más rápido = más tráfico de health check.

---

## 6. Sticky sessions — cuando el cliente debe ir al mismo backend

**Problema**: cliente hace login → sesión guardada en RAM del backend1. Próxima request → el LB la envía a backend2 → "no estás logueado".

**Soluciones**:

**A) Stateless backends (la mejor)**: la sesión se guarda en un lugar compartido (Redis, DB, JWT en cookie). Cualquier backend puede atender. No hace falta sticky. Patrón "Twelve-Factor App".

**B) Sticky sessions (cuando A no es viable)**: el LB usa cookie o IP hash para enviar al mismo backend siempre.

- **Cookie-based**: el LB inyecta una cookie, ej: `AWSALB=backend2-id`. En la próxima request, el LB lee la cookie y envía a backend2.
- **IP hash**: `Hash(client_ip) → backend` determinista.

**Desventajas de sticky**:

- Si el backend cae, sus sesiones se pierden.
- Carga desigual (algunos clientes generan más tráfico).
- Migración rolling más compleja.

**Regla de oro moderna**: diseña stateless desde el principio. Sticky solo como último recurso.

---

## 7. SSL/TLS termination

**TLS termination en el LB**:

- Cliente ↔ LB: HTTPS (cifrado).
- LB ↔ Backend: HTTP plano (red privada interna).

El LB descifra y envía al backend en claro.

**Ventajas**:

- Los backends no necesitan cert ni hacer cripto (más rápidos).
- Renovación de certs centralizada (1 sitio, no N).
- Cache HTTP simple (no hay que descifrar para cachear).

**Desventaja**:

- Tráfico LB↔backend va en claro. Si tu network no es trusted, expone datos. Solución: TLS re-encryption (LB descifra, vuelve a cifrar para backend).

**Patrón moderno**: TLS termination en el edge (LB/CDN público); mTLS interno entre microservicios (zero-trust).

---

## 8. DNS load balancing — el LB "barato"

En vez de un LB dedicado, usar DNS:

- `api.example.com` → A records: `10.0.0.1`, `10.0.0.2`, `10.0.0.3`.
- El cliente recibe los 3 y prueba el primero.
- Diferentes resolvers reciben distinto orden → balanceo.

**Ventajas**:

- Cero infraestructura.
- Funciona globalmente con geo-DNS (Cloudflare, Route53).

**Desventajas**:

- El TTL DNS controla la "rapidez de failover".
- Algunos resolvers no respetan el TTL.
- El cliente cachea — si el backend cae, sigue intentando.
- Sin health checks reales (DNS no sabe si el backend vive).

**Uso**:

- Geo-routing (US clients → US POP, EU → EU POP).
- Failover entre datacenters (si A cae, DNS apunta a B).
- **No** para load balancing fino (usa LB real).

---

## 9. Topologías comunes

### LB único (simple)

```
Internet → LB → [Backends]
```

- **Problema**: el LB es SPOF (single point of failure).
- **Solución**: HA pair de LBs (active-passive con keepalived/VRRP).

### Múltiples LBs con DNS

```
Internet → DNS → [LB1, LB2] → [Backends comunes]
```

DNS reparte entre los LBs. Si uno cae, DNS quita su IP.

### Multi-tier

```
Internet → CDN (edge LB) → Regional LB → Internal LB → Backends
```

Cada capa optimiza algo distinto:

- **CDN**: caché estática + DDoS.
- **Regional**: por país/zona.
- **Internal**: routing por servicio.
- **Backend**: la app real.

Patrón típico de grandes tecnologicas.

### Service Mesh (Kubernetes)

Cada pod tiene un sidecar proxy (Envoy, Istio, Linkerd). La comunicación pod ↔ pod va vía sidecars. Los sidecars hacen LB, health checks, mTLS y observability.

Cada microservicio se descubre vía DNS interno (`service.namespace.svc.cluster.local`).

---

## 10. Failover y high availability

- **Active-passive**: LB1 activo, LB2 standby. Si LB1 cae, LB2 toma su IP virtual (VIP) vía VRRP/keepalived. Tiempo de failover: ~1-5 segundos.
- **Active-active**: ambos LBs activos. DNS reparte entre ellos. Si uno cae, DNS quita su IP (con failover health check). Mejor utilización de recursos.
- **Anycast (avanzado)**: la misma IP se anuncia desde múltiples ubicaciones globales (BGP). Internet enruta al "más cercano" topológicamente. Usado por Cloudflare, Google DNS (8.8.8.8), CDNs grandes.

---

## 11. Implementaciones populares

**Software LBs (open source)**:

| LB | Capa | Notas |
|---|---|---|
| Nginx | L7 HTTP | Muy popular, simple |
| HAProxy | L4/L7 | Alto throughput, configurable |
| Caddy | L7 | HTTPS automático, simple |
| Traefik | L7 | Dynamic config (Docker, K8s native) |
| Envoy | L7 moderno | Base de service meshes |
| IPVS | L4 | Kernel Linux, muy rápido |

**Hardware LBs (legacy)**: F5 BIG-IP, Citrix ADC, Cisco. Caros, on-premise enterprise.

**Cloud managed**:

- **AWS ELB**: ALB (L7) para HTTP/HTTPS; NLB (L4) para TCP/UDP/TLS passthrough; GLB (Global) para multi-region.
- **GCP**: Cloud Load Balancing — global o regional. Anycast IPs.
- **Azure**: Load Balancer + Application Gateway.
- **Cloudflare**: edge LB con CDN integrado.

---

## 12. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

- Hoy: 1 container Docker en tu localhost. Sin LB.
- Si lo despliegas con Caddy delante (T1.4): Caddy actúa como L7 LB (incluso con 1 backend, hace TLS termination + routing).
- Si añades `--workers 4` a Uvicorn: hay 4 procesos compartiendo el puerto vía `SO_REUSEPORT` — el kernel hace LB básico entre ellos.

### En entrevistas tecnicas

- **Pregunta**: "Diseña Twitter timeline. Cómo escalas a 100K req/s" → múltiples capas:
  1. Cloudflare edge (DDoS, geo-routing, caché estática).
  2. Regional ALB (HTTPS termination, health checks).
  3. Servicio API stateless con N pods.
  4. Service mesh interno para inter-service.
  5. Cache layer (Redis cluster) con consistent hashing.
- **Pregunta**: "Layer 4 vs Layer 7 LB" → L4: ve TCP, decide por IP/puerto. Rápido, protocolo-agnóstico. L7: ve HTTP, decide por URL/header/cookie. Más features, más coste.
- **Pregunta**: "Algoritmos de balanceo y cuándo usar cada uno":
  - RR: backends idénticos, requests uniformes.
  - Least connections: requests de duración variable.
  - IP hash / consistent hashing: cache locality, sticky.
  - Power of two choices: escalable y eficiente.
- **Pregunta**: "Cómo hacer failover sin downtime" → active-passive con VRRP, o active-active con anycast. Health checks rápidos (1-5s). Stateless backends (sesión en Redis/DB).
- **Pregunta**: "Por qué evitar sticky sessions" → los backends stateless escalan mejor. Sticky pierde sesiones si el backend cae. Migración rolling más compleja. Solo usar si no hay alternativa.

---

## 13. Trampas típicas

- **Trampa 1 — "Round robin garantiza balanceo perfecto"**: solo si las requests son uniformes en duración. Si algunas tardan 10s y otras 10ms, RR puede saturar backends.
- **Trampa 2 — "Sticky sessions son seguras"**: si un backend cae, sus usuarios pierden la sesión. Mejor stateless desde el diseño.
- **Trampa 3 — "El LB nunca cae"**: es un componente más, también puede caer. Necesita HA propio (active-passive, anycast).
- **Trampa 4 — "Health check `/health` basta"**: `/health` puede responder 200 mientras la DB está caída → enrutas tráfico a backend roto. Diferenciar `/health` (vivo) vs `/ready` (DB OK + warmup).
- **Trampa 5 — "L7 siempre mejor que L4"**: L4 tiene menor latencia y mayor throughput. Si solo necesitas pass-through TCP, L4 gana.
- **Trampa 6 — "TLS termination en LB es siempre seguro"**: tráfico LB↔backend en claro. Si la network no es trusted, usa re-encryption o mTLS interno.
- **Trampa 7 — "DNS LB es suficiente"**: no tiene health checks reales en cliente, el TTL controla un failover lento. OK para geo-routing, no para LB fino.

---

## 14. Preguntas típicas de interview

- **Pregunta 1 — "Qué hace un load balancer"**: distribuye requests entre N backends. Permite escalado horizontal, alta disponibilidad y mantenimiento sin downtime.
- **Pregunta 2 — "L4 vs L7"**: L4 ve TCP, decide por IP/puerto. L7 ve HTTP, decide por URL/header.
- **Pregunta 3 — "Algoritmos de balanceo"**: RR, weighted RR, least connections, IP hash, consistent hashing, P2C. Cada uno tiene sus tradeoffs.
- **Pregunta 4 — "Health checks"**: active (proactive `GET /health`) vs passive (observa requests reales). `/health` vs `/ready` (sutilmente distintos).
- **Pregunta 5 — "Sticky sessions: cuándo y cómo evitar"**: cuando hay estado en el backend (RAM). Mejor stateless vía Redis/DB/JWT. Si es necesario: cookie-based o IP hash.
- **Pregunta 6 — "Cómo escalar tu API a 1M req/s"**: multi-tier — CDN + LB regional + servicio stateless + cache distribuido. Auto-scaling basado en métricas (CPU, latencia, queue depth). Health checks rigurosos. Failover automático.

---

## 15. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué un load balancer (escalado, HA, mantenimiento).
- Diferencia L4 vs L7 con cuándo usar cada uno.
- Al menos 4 algoritmos de balanceo y sus tradeoffs.
- Health checks: active vs passive, `/health` vs `/ready`.
- Por qué los stateless backends son preferidos a sticky sessions.
- TLS termination: dónde y por qué.
- HA del propio LB (active-passive, anycast).
- Por qué el DNS LB es limitado vs un LB real.
- Diferencia entre Nginx, HAProxy, Caddy y Envoy.

Si no puedes → relee.

---

## Conexiones

- [[02-caching-strategies]] — caches detrás del LB
- [[03-message-queues]] — alternative async sin LB clásico
- [[04-cdn-y-edge]] — LB geográfico distribuido
- [[05-rate-limiting]] — LB con rate limiting integrado
- [[../01_networking/01-tcp-ip-osi]] — base TCP/IP del LB
- [[../01_networking/02-http-y-evolucion]] — base HTTP de L7 LB
- [[../06_distributed_systems/01-cap-pacelc]] — tradeoffs de distribución
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Designing Data-Intensive Applications** (Kleppmann) capítulo 8 (Trouble with Distributed Systems).
- **System Design Interview** (Alex Xu) volumen 1, capítulo "Load Balancers".
- **NGINX docs** (nginx.org/en/docs/) — referencia práctica.
- **HAProxy docs** (haproxy.org/#docs) — más profundo.
- **Envoy proxy** (envoyproxy.io/docs) — moderno, base de Istio/service mesh.
- **AWS ELB / ALB / NLB docs** — cuando uses cloud.
- **High Scalability blog** — case studies reales con LB.
