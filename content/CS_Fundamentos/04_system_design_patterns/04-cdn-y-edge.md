# 04 — CDN y edge computing

> 📚 **Doc 4 del cluster System Design Patterns**. Cómo servir contenido en milisegundos a usuarios en cualquier punto del planeta.
> 🔥 **Frecuencia interview**: aparece en system design global (YouTube, Netflix, Twitter, e-commerce internacional).
> ⏱️ **Tiempo de lectura estimado**: 30-45 min.

---

## 1. El problema y la solución

**Problema**: tu server está en `us-east-1` (Virginia). Un usuario en Tokio carga tu web.

- Latencia round-trip Tokio↔Virginia: ~150-200ms.
- Cada asset (imagen, JS, CSS) → ~150ms.
- Página con 50 assets → 7.5s solo en latencia.

**Solución — CDN**: distribuir copias de tu contenido en POPs (Points of Presence) cerca del usuario. Usuario en Tokio → cache en Tokio → ~10ms.

**Efectos**:
- **Latencia**: orden de magnitud menor.
- **Coste**: menos egress de tu origin (el CDN cobra menos por byte).
- **Resiliencia**: si tu origin cae, el CDN sigue sirviendo cache.
- **DDoS protection**: el CDN absorbe ataques antes de llegar a ti.

---

## 2. Arquitectura típica de CDN

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  USUARIOS GLOBALES                                   │
│                                                      │
└─────┬──────────────┬─────────────┬───────────┬───────┘
      ↓              ↓             ↓           ↓
   ┌─────┐        ┌─────┐       ┌─────┐    ┌─────┐
   │ POP │        │ POP │       │ POP │    │ POP │
   │ NYC │        │ FRA │       │ TYO │    │ SAO │
   └──┬──┘        └──┬──┘       └──┬──┘    └──┬──┘
      └──────────────┴─────────────┴───────────┘
                          ↓
                  ┌──────────────┐
                  │   ORIGIN     │
                  │ (tu server)  │
                  └──────────────┘
```

**POP (Point of Presence)**:
- Servers en data centers regionales.
- Cachean contenido del origin.
- 200+ POPs en CDNs grandes (Cloudflare, Akamai).

**Origin**:
- Tu server real. Donde vive el contenido original.
- Los POPs van al origin solo cuando no tienen el contenido cacheado.

---

## 3. Cómo funciona — flujo de un request

Un usuario en Tokio pide `GET https://miapp.com/img/foto.jpg`:

1. **DNS resuelve `miapp.com`**: Geo-DNS responde con la IP del POP de Tokio (no del origin).
2. **Cliente conecta al POP de Tokio (10ms)**: el POP busca `foto.jpg` en su cache.
3a. **Cache hit**: el POP devuelve la imagen directamente. FIN. ~10ms total.
3b. **Cache miss**: el POP pide al origin (`GET miapp.com/img/foto.jpg`). El origin responde con la imagen + headers de cache (`Cache-Control`, etc.). El POP guarda en cache + devuelve al usuario. El próximo usuario en Tokio: cache hit.

**Optimización**: múltiples niveles de cache (edge → regional → origin shield). Si el edge no tiene → pregunta a regional. Si regional no → origin. Reduce origin requests aún más.

---

## 4. Qué cachear (y qué no)

**Cacheable típico**:
- Imágenes, vídeos, PDFs (binarios estáticos).
- JS, CSS, fonts (assets web).
- HTML estático (landing pages, blog posts).
- API responses con datos públicos (precios, availability).
- Respuestas con auth pero share-able (con segmentación).

**No cacheable típico**:
- Páginas personalizadas (dashboard de usuario).
- Datos sensibles (transactions, profile).
- Resultados de búsqueda muy variados.
- POST/PUT/DELETE responses (mutaciones).

**Regla de oro**: cachea lo que es **igual** para muchos usuarios. No cachees lo que es **personal**.

---

## 5. Cache control — cómo le dices al CDN qué hacer

Headers HTTP que controlan el caching:

| Header | Efecto |
|---|---|
| `Cache-Control: max-age=3600, public` | Cachea 1 hora, accesible a CDN intermediarios |
| `Cache-Control: max-age=0, no-cache` | Revalida con origin antes de servir cache |
| `Cache-Control: no-store` | NO cachees nunca |
| `Cache-Control: private, max-age=600` | Solo browser puede cachear, no CDN intermediarios |
| `Cache-Control: s-maxage=3600` | CDN cachea 1h (browser puede usar otro tiempo) |
| `ETag: "abc123"` | Identificador de versión. Cliente envía `If-None-Match`. Si match → 304 Not Modified, no body. Ahorra bandwidth |
| `Vary: Accept-Encoding` | Cachear copias separadas por header Vary (gzip vs brotli) |
| `Vary: Cookie` | ⚠️ Casi inutiliza el cache (cada cookie distinta = entrada distinta) |

---

## 6. Invalidación en CDN

**Desafío**: subes versión nueva del JS. ¿Cómo evitar que el CDN sirva el viejo durante `max-age`?

**Estrategias**:

**A) URL versioning (la más usada)**: `/js/app.v1.js` → `/js/app.v2.js`. Nueva URL = no hay cache previo. Cache HIT solo cuando todos vean v2. Build tools (Webpack, Vite) generan hashes en filenames automáticamente.

**B) Purge explícito**: API del CDN para invalidar URLs. `POST /purge?url=https://miapp.com/img/foto.jpg`. Tarda segundos a minutos en propagar globalmente.

**C) Short TTL + ETag**: `max-age=60` + ETag. Cada minuto el cliente revalida con `If-None-Match`. Si no cambió → 304 (rápido). Si cambió → nueva versión.

**D) Cache-Control: no-cache para HTML**: el HTML siempre revalida (es chico). El HTML referencia `/js/app.HASH.js`. Los assets con URL hash se cachean para siempre.

---

## 7. Geo-routing y anycast

**Geo-DNS**: el DNS responde con IP distinta según la ubicación del cliente.
- Cliente en EU → IP del POP europeo.
- Cliente en US → IP del POP americano.
- **Implementación**: Cloudflare DNS, Route53 latency-based routing, Google Cloud DNS.

**Anycast**: la **misma** IP anunciada desde múltiples POPs vía BGP. Internet enruta al "más cercano" topológicamente.

- **Pros**: failover automático (si un POP cae, BGP reenruta). Sin cambio de IP en el cliente.
- **Contras**: requiere ASN propio (no aplicable al common dev).
- **Uso**: Cloudflare 1.1.1.1, Google DNS 8.8.8.8, todos los CDNs grandes.

---

## 8. Edge computing — más allá del cache

**CDN tradicional**: cachea contenido estático.

**Edge computing**: ejecuta **código** en los POPs cercanos al usuario. No solo sirve cache — **transforma, genera, decide**.

**Ejemplos de productos**:
- **Cloudflare Workers**: código JS/Rust ejecutado en 200+ POPs. Latencia ~10ms al cliente más cercano.
- **AWS Lambda@Edge / CloudFront Functions**: funciones Lambda corriendo en edge CloudFront.
- **Vercel Edge Functions**: para Next.js apps.
- **Fastly Compute@Edge**: WASM en edge.

**Casos de uso en edge**:
- Auth/JWT validation antes del hit a backend.
- A/B testing (decide variante en edge).
- Personalización ligera (geo, language detection).
- Rate limiting per-user.
- Image transformation on-the-fly.
- Bot detection.

**Limitaciones**:
- CPU/memoria limitados (no para cómputo pesado).
- Sin acceso a tu DB típicamente (latency).
- Cold starts en algunos providers.
- Modelo de programación distinto (no Node tradicional).

---

## 9. CDN providers — comparativa rápida

| Provider | Características |
|---|---|
| **Cloudflare** | 300+ POPs, anycast. Tier gratuito muy generoso. Workers (edge compute). DDoS protection incluida. Default para muchos sites pequeños y medianos |
| **Akamai** | El CDN más viejo (1998), enterprise heavy. Caro pero feature-rich. Big media customers (Netflix histórico) |
| **AWS CloudFront** | Integración perfecta con AWS (S3, EC2, Lambda). 400+ edges. Más caro que Cloudflare pero pago por uso |
| **Fastly** | Real-time purge (~150ms global). Compute@Edge con WASM. Customers: GitHub, Reddit, Stripe |
| **Google Cloud CDN** | Integración con GCP. Compute@Edge limitado |
| **Bunny.net** | Barato, simple, popular en startups. Sin enterprise tier |

---

## 10. Origin shield — capa intermedia

**Problema**: cache miss en muchos POPs simultáneos → todos van al origin. El origin se satura.

**Solución — origin shield**: un POP "supervisor" entre los edge POPs y el origin. Los edge POPs van al shield. Solo el shield va al origin. Reduce origin requests dramáticamente.

**Números**:
- Sin shield: 100 POPs × cache miss = 100 origin requests.
- Con shield: 100 POPs → shield (cache hit) → 0 origin requests. Solo cuando el shield miss → 1 origin request.

**Uso**: sites con tráfico global y origin con throughput limitado.

---

## 11. CDN para video — caso especial

**HLS (HTTP Live Streaming) / DASH**: el video se trocea en chunks de 2-10 segundos (`.ts` files). Un manifest (`.m3u8`) lista los chunks. El cliente descarga chunks según necesite.

**Por qué encaja en CDN**: los chunks son archivos estáticos → cacheables fácilmente. El CDN sirve chunks desde el POP cercano. Resultado: streaming global con baja latencia.

**ABR (Adaptive Bitrate)**: el manifest lista el MISMO video en múltiples calidades. El cliente cambia calidad según ancho de banda. 4K si tienes fibra. 480p si móvil 3G.

**Casos reales**:
- **Netflix Open Connect**: CDN propio en ISPs.
- **YouTube**: CDN propio de Google + ISP peering.
- **Twitch**: AWS + propia.

---

## 12. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

- No necesitas CDN para una API privada.
- Si el frontend es público (HTML/JS/CSS), CDN para assets estáticos (Cloudflare Free tier sobra).

### En entrevistas tecnicas

**Pregunta**: "Diseña YouTube".
→ CDN para video chunks (Open Connect / Akamai equivalent). Origin storage en GCS/S3. Encoding pipeline (job queue) para múltiples bitrates. Manifest server (rápido, pequeño JSON). Recommendations service.

**Pregunta**: "Cómo aceleras tu app para usuarios globales".
→ CDN para assets estáticos (Cloudflare/CloudFront). Edge functions para auth/personalization. Multi-region origin con geo-DNS. Database read replicas regionales.

**Pregunta**: "Cuándo usarías edge compute vs serverless central".
→ Edge: latency-sensitive (auth, A/B, personalization light, rate limit). Central: cómputo pesado, acceso DB, lógica core. Híbrido: edge filtra/transforma, central computa.

**Pregunta**: "Cómo invalidas cache CDN cuando cambias contenido".
→ URL versioning (preferido) o purge API. URL versioning es más robusto (no hay race conditions con propagación).

**Pregunta**: "Por qué los CDNs usan anycast".
→ Misma IP anunciada desde múltiples ubicaciones via BGP. El cliente conecta al más cercano topológicamente. Failover automático (si un POP cae, BGP reenruta).

---

## 13. Trampas típicas

**Trampa 1 — "CDN cachea todo automáticamente"**: solo cachea según headers (`Cache-Control`). Por defecto, muchos CDNs no cachean dynamic responses.

**Trampa 2 — "Purge es instantáneo"**: tarda segundos a minutos en propagar a todos los POPs.

**Trampa 3 — "`Vary: Cookie` sirve"**: casi inutiliza el cache (cada cookie = entrada distinta). Mejor: separar URLs por contenido público vs privado.

**Trampa 4 — "CDN solo es para sites grandes"**: el Cloudflare free tier es excelente incluso para proyectos pequeños. Mejora seguridad (DDoS) y performance gratis.

**Trampa 5 — "Edge compute reemplaza tu backend"**: para lógica simple sí. Para acceso DB, ML, cómputo pesado, no. Es complemento, no sustituto.

**Trampa 6 — "Geo-DNS es perfecto"**: el "más cercano" geográficamente puede no ser el más rápido. El routing de internet no siempre sigue geografía. Latency-based routing es más fiable.

---

## 14. Preguntas típicas de interview

**Pregunta 1 — "Qué es un CDN y por qué"**: cache distribuido geográficamente. Reduce latency, costo, mejora resilience.

**Pregunta 2 — "Cómo invalidas cache"**: URL versioning (preferido), purge API, short TTL + ETag.

**Pregunta 3 — "Diferencia entre CDN cache y edge compute"**: CDN: cache de contenido estático. Edge compute: ejecutar código en POPs (Workers, Lambda@Edge).

**Pregunta 4 — "Por qué un CDN es seguro"**: filtra ataques (DDoS), rate limiting, WAF, esconde IP del origin.

**Pregunta 5 — "Diseña Netflix streaming"**: Open Connect (CDN propio en ISPs), encoding pipeline, ABR streaming, recommendations centrales.

**Pregunta 6 — "Cuándo NO usar CDN"**: apps internas privadas, contenido completamente personalizado, latency-critical RPC entre microservices internos (usa service mesh).

---

## 15. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué CDN (latency, coste, resilience, DDoS).
- Flujo cache miss vs cache hit.
- Qué se cachea y qué no.
- Cache-Control headers principales.
- Estrategias de invalidación (URL versioning vs purge).
- Geo-DNS y anycast.
- Edge compute: qué resuelve, casos de uso, limitaciones.
- CDN providers principales (Cloudflare, CloudFront, Akamai, Fastly).

Si no puedes → relee.

---

## Conexiones

- [[01-load-balancing]] — CDN es LB geográfico
- [[02-caching-strategies]] — CDN es nivel de cache más externo
- [[../01_networking/03-dns-resolucion-nombres]] — geo-DNS base de CDN
- [[../01_networking/05-tls-https]] — CDN suele hacer TLS termination
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Cloudflare Learning Center** (cloudflare.com/learning/cdn/) — gratis, excelente.
- **High Performance Browser Networking** capítulo CDN (hpbn.co).
- **Netflix Tech Blog — Open Connect** — case study real.
- **AWS CloudFront docs**.
- **Fastly blog** — moderno y técnico.
