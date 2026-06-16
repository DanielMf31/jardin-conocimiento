# 02 — HTTP y su evolución (1.0 → 3.0)

> 📚 **Doc 2 del cluster Networking**. Lee primero [[01-tcp-ip-osi]] (TCP es el transporte sobre el que corre HTTP).
> 🔥 **Frecuencia interview**: aparece en TODA system design web. Conocer las diferencias entre 1.1, 2 y 3 te diferencia de candidatos superficiales.
> ⏱️ **Tiempo de lectura estimado**: 45-75 min.

---

## 1. Qué es HTTP

**HTTP (HyperText Transfer Protocol)** es el protocolo de aplicación que mueve la web. Cliente envía **request**, servidor envía **response**. **Stateless** por diseño (cada request es independiente, sin memoria del anterior).

**Propiedades clave**:
- Texto plano (en HTTP/1.x; binario en 2 y 3).
- Stateless (el server no recuerda requests previas — cookies/sesiones lo emulan).
- Request-response (cliente inicia siempre — pull, no push).
- Sobre TCP (excepto HTTP/3 que usa QUIC sobre UDP).
- Default port 80 (HTTP) / 443 (HTTPS).

**Por qué stateless es bueno**: cualquier server del cluster puede atender cualquier request (no hay "sticky session" forzada). Esto es lo que permite **escalado horizontal trivial** de la web.

**Por qué stateless es problemático**: tu app necesita estado (login, carrito). Solución: **cookies + session IDs** o **JWT**. El server NO mantiene estado, pero el cliente lo "carga" en cada request.

---

## 2. Anatomía de un HTTP request

```
GET /users/42?include=posts HTTP/1.1
Host: api.example.com
User-Agent: curl/8.0
Accept: application/json
Authorization: Bearer eyJhbGc...
Cookie: session_id=abc123
Content-Length: 0

(body vacío en GET; en POST/PUT habría body aquí)
```

**Las partes**:

- **Línea 1 (Request line)**: el método (`GET`), el path (`/users/42`), la query string (`?include=posts`), la versión (`HTTP/1.1`).
- **Líneas 2-N (Headers)**: pares `Key: Value` separados por `\r\n`. Algunos importantes son `Host` (servidor objetivo, obligatorio en HTTP/1.1+), `User-Agent` (quién hace el request), `Accept` (qué formato de respuesta acepta), `Authorization` (credenciales), `Cookie` (cookies guardadas).
- **Línea en blanco**: separa headers del body.
- **Body**: datos opcionales (solo POST/PUT/PATCH típicamente).

---

## 3. Anatomía de un HTTP response

```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 87
Cache-Control: max-age=3600
Set-Cookie: session_id=abc123; HttpOnly; Secure

{"id":42,"name":"Alice","email":"alice@example.com","created_at":"2026-05-10"}
```

**Las partes**:

- **Línea 1 (Status line)**: la versión (`HTTP/1.1`), el código de estado (`200`), la descripción legible (`OK`).
- **Headers**: `Content-Type` (qué hay en el body), `Content-Length` (bytes del body), `Cache-Control` (cómo cachear), `Set-Cookie` (cookies a guardar).
- **Body**: el contenido (HTML, JSON, imagen, lo que sea).

---

## 4. Métodos HTTP — los verbos REST

Los 5 métodos que usas el 99% del tiempo:

| Método | Propósito | Body | Idempotente |
|---|---|---|---|
| `GET` | Leer recurso | NO | Sí (cacheable) |
| `POST` | Crear recurso | SÍ | NO |
| `PUT` | Reemplazar recurso entero | SÍ | Sí |
| `PATCH` | Modificación parcial | SÍ | Sí (en teoría) |
| `DELETE` | Borrar | NO típicamente | Sí |

Otros menos usados: `HEAD` (como GET pero solo headers), `OPTIONS` (preflight CORS), `CONNECT` (tunneling proxies HTTPS), `TRACE` (debug, casi nunca).

### Idempotencia — concepto clave

**Idempotente** = mismo resultado si lo llamas 1 vez o N veces.

- `POST /contacts` (con mismo body) → **NO idempotente**: 1 call → 1 contacto creado, 3 calls → 3 contactos creados (con ids 1, 2, 3).
- `PUT /contacts/42` (con mismo body) → **idempotente**: 1 call → contacto 42 con datos X, 3 calls → contacto 42 con datos X (mismo resultado).
- `DELETE /contacts/42` → **idempotente**: 1 call → borrado, 3 calls → ya no existe (404 en repeticiones, pero estado final = mismo).

**Por qué importa**: si tu cliente reintenta un request por timeout, los métodos idempotentes son seguros de reintentar. Los no idempotentes (POST) pueden duplicar datos. Por eso muchos APIs modernos exigen "idempotency key" en POST (un UUID que el server usa para detectar duplicados).

---

## 5. Status codes — los 5 grupos

**1xx — INFORMATIONAL** (raros): `100 Continue` (server dice "sigue mandando"), `101 Switching Protocols` (upgrade a WebSocket).

**2xx — SUCCESS**:
- `200 OK` — éxito genérico (GET, PUT, DELETE).
- `201 Created` — POST exitoso (recurso creado).
- `204 No Content` — éxito sin body (DELETE típico).
- `206 Partial Content` — range requests (descargas parciales).

**3xx — REDIRECTION**:
- `301 Moved Permanently` — recurso cambió de URL para siempre.
- `302 Found` — redirect temporal.
- `304 Not Modified` — cache válida, no descargues de nuevo.

**4xx — CLIENT ERROR**:
- `400 Bad Request` — request malformado.
- `401 Unauthorized` — falta autenticación.
- `403 Forbidden` — autenticado pero sin permiso.
- `404 Not Found` — recurso no existe.
- `405 Method Not Allowed` — método incorrecto para esa URL.
- `409 Conflict` — conflicto (e.g. email duplicado al crear).
- `422 Unprocessable` — validación falló (FastAPI default Pydantic).
- `429 Too Many Requests` — rate limit superado.

**5xx — SERVER ERROR**:
- `500 Internal Server Error` — algo se rompió en server.
- `502 Bad Gateway` — proxy/gateway recibió respuesta inválida.
- `503 Service Unavailable` — server caído / sobrecargado.
- `504 Gateway Timeout` — proxy no recibió respuesta a tiempo.

**Trampa típica**: NO devolver 200 con `{"error": "not found"}`. Devolver 404 explícito. Es la diferencia entre **API REST de juguete** y **API REST seria**.

---

## 6. Headers importantes que debes conocer

### Headers de request

- **`Host: api.example.com`** — obligatorio HTTP/1.1+. Permite virtual hosting (1 IP, varios dominios).
- **`User-Agent`** — identifica el cliente. Algunos servers responden distinto según UA.
- **`Accept`** — qué formato de respuesta prefiero. Server puede ignorarlo.
- **`Accept-Encoding`** — qué compresiones acepto (gzip, br). Server elige una.
- **`Authorization`** — credenciales. `Bearer <jwt>` o `Basic base64(user:pass)`.
- **`Cookie`** — cookies guardadas para ESTE dominio.
- **`Content-Type`** — si mando body, qué formato es.
- **`Content-Length`** — tamaño del body en bytes.
- **`If-None-Match: "abc123"`** — Etag, "solo me lo mandes si cambió desde abc123".
- **`If-Modified-Since: <date>`** — lo mismo pero por fecha.

### Headers de response

- **`Content-Type, Content-Length, Content-Encoding`** — equivalentes al request.
- **`Cache-Control`** — cómo y cuánto cachear. Ver doc 02 de System Design Patterns.
- **`ETag: "abc123"`** — identificador de versión. El cliente lo manda en `If-None-Match`.
- **`Set-Cookie`** — cookie a guardar. Atributos importantes:
  - `HttpOnly` — JavaScript NO puede leerla (anti-XSS).
  - `Secure` — solo se manda por HTTPS.
  - `SameSite=Strict` — no se manda en requests cross-site (anti-CSRF).
- **`Location: /contacts/42`** — en 201 Created: dónde está el recurso nuevo. En 3xx redirect: a dónde redirigir.
- **`Access-Control-Allow-Origin: https://app.example.com`** — CORS, qué orígenes pueden hacer requests cross-origin.
- **`X-RateLimit-Remaining: 47`** — no estándar pero común. Cuántos requests te quedan.

---

## 7. HTTP/1.0 — el origen (1996)

**Características**:
- 1 conexión TCP = 1 request + 1 response, después se cierra.
- SIN Host header → 1 IP servía 1 dominio. Limitación grave.
- SIN persistent connections.

**Problema**: cada imagen, CSS, JS de una página HTML requiere una conexión TCP nueva. Con 50 recursos en una página, son 50 handshakes TCP. Lentísimo.

Además, slow-start de TCP nunca aprovecha la conexión. Cada nueva conexión empieza con throughput bajo.

---

## 8. HTTP/1.1 — el estándar durante 20 años (1997)

**Mejoras clave**:

1. **Persistent connections (keep-alive)**: 1 conexión TCP soporta MÚLTIPLES requests/responses secuenciales. Default ON.
2. **Pipelining (poco usado en práctica)**: cliente puede enviar request 2 sin esperar response 1. Pero responses TIENEN que ir en orden (HOL blocking). En la práctica, browsers no lo usan.
3. **Host header obligatorio**: permite virtual hosting (varias webs en 1 IP).
4. **Chunked transfer encoding**: server puede enviar response sin saber su tamaño total a priori.
5. **Cache headers sofisticados**: ETag, Cache-Control, Vary.

**Limitaciones que quedaron**:

- **Head-of-line blocking**: en una conexión, las responses van en orden de request. Si el request 1 tarda mucho, los siguientes esperan. Browsers compensan abriendo 6 conexiones TCP paralelas por dominio.
- **Headers repetidos**: cada request lleva headers similares (cookies, user-agent). Sin compresión, son cientos de bytes redundantes por request.
- **No push del server**: server no puede enviar nada que el cliente no pidió primero.

---

## 9. HTTP/2 — el cambio mayor (2015)

Basado en SPDY de Google. Cambio fundamental: **binario en lugar de texto**, **multiplexing**.

**Mejoras clave**:

1. **Binary framing**: en lugar de texto plano, frames binarios. Más eficiente parseo, menos errores.

2. **Multiplexing (la gran mejora)**: 1 conexión TCP soporta MÚLTIPLES streams CONCURRENTES. Request 1, 2, 3, 4 en paralelo en LA MISMA conexión. Adiós head-of-line blocking de aplicación.

   ```
   ┌─────────── conexión TCP única ───────────┐
   │ stream 1: req → ... → resp                │
   │ stream 2: req → resp                      │
   │ stream 3: req → ......... → resp          │
   │ stream 4: req → resp                      │
   └───────────────────────────────────────────┘
   ```
   Antes (HTTP/1.1) necesitabas 4 conexiones.

3. **Header compression (HPACK)**: headers se comprimen y los repetidos se omiten. Ahorra 80%+ del tamaño de headers en práctica.

4. **Server push (poco adoptado, deprecated en 2020)**: server podía enviar recursos sin pedirlos primero. En la práctica casi no se usó. Chrome lo deshabilitó.

5. **Stream prioritization**: cliente puede decir "este stream es más importante".

**Limitación que queda**: **head-of-line blocking a nivel TCP**. HTTP/2 multiplexa a nivel HTTP, pero TCP sigue siendo UN solo stream de bytes. Si se pierde 1 paquete TCP, TODOS los streams HTTP/2 esperan (porque TCP retiene los siguientes hasta retransmitir).

---

## 10. HTTP/3 — el cambio radical (2022)

Basado en QUIC de Google. Cambio: **abandona TCP**, usa **UDP**.

**Por qué abandonar TCP**: HTTP/2 resolvió HOL a nivel HTTP, pero TCP sigue siendo el cuello. Cambiar TCP es imposible (legacy enorme, kernel level). Solución: nuevo protocolo en USERSPACE sobre UDP.

**QUIC en vez de TCP**:
- Sobre UDP (rápido, sin handshake "pesado").
- Streams independientes a nivel transporte (no solo HTTP).
- Si se pierde paquete de stream A, stream B no espera.
- **Connection migration**: tu IP cambia (cambias de WiFi a 4G) y la conexión sobrevive (identificada por connection ID, no IP+puerto).
- **Encryption built-in** (TLS 1.3 integrado, no añadido encima).

**Ventajas**:
- 0-RTT handshake (en reconexiones — primera conexión es 1 RTT).
- Sin HOL blocking de TCP.
- Mejor rendimiento en redes con loss (móviles).

**Adopción**: YouTube, Google, Cloudflare, Facebook ya lo usan. Browsers modernos soportan (Chrome, Firefox, Safari). Server-side: Cloudflare, nginx (con módulo), Caddy (built-in).

---

## 11. Comparativa rápida HTTP/1.1 vs 2 vs 3

| | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| **Año** | 1997 | 2015 | 2022 |
| **Formato** | Texto | Binario | Binario |
| **Transporte** | TCP | TCP | QUIC sobre UDP |
| **Multiplexing** | No (necesita N conexiones) | Sí (1 conexión) | Sí (1 conexión) |
| **Header compression** | No | HPACK | QPACK |
| **HOL blocking app** | Sí | No | No |
| **HOL blocking TCP** | Sí | Sí (limita) | No (UDP no tiene) |
| **TLS** | Opcional (HTTPS) | Casi obligatorio | Built-in |
| **Server push** | No | Sí (deprecated) | No (parecido con prioridad) |
| **Connection migration** | No | No | Sí |

---

## 12. Cookies y sesiones

Una **cookie** es un pequeño dato (max 4KB) que el server pide al browser guardar. El browser lo manda automáticamente en cada request a ese dominio.

**Flow típico**:

1. Cliente hace `POST /login` con credentials.
2. Server valida, crea session_id en su DB.
3. Server responde con: `Set-Cookie: session_id=abc123; HttpOnly`.
4. Browser guarda la cookie.
5. En cada request futuro al mismo dominio: `Cookie: session_id=abc123`.
6. Server lee cookie, busca session en DB, identifica usuario.

**Atributos de cookie importantes**:
- `HttpOnly` — JavaScript NO puede leerla (anti-XSS).
- `Secure` — solo se manda por HTTPS.
- `SameSite` — controla cuándo se manda en cross-site:
  - `Strict`: nunca cross-site (más seguro, rompe algunos flows).
  - `Lax`: solo en navegación top-level (default moderno).
  - `None`: siempre (requiere `Secure`).
- `Domain` — para qué dominio aplica.
- `Path` — para qué path aplica.
- `Max-Age / Expires` — cuánto vive.

**Alternativa moderna: JWT (JSON Web Tokens)**. En vez de session_id apuntando a row en DB, el token contiene la info del usuario, firmada por el server. Server NO necesita guardar nada (stateless de verdad). Ver [[../08_security/04-jwt-y-session-management]].

---

## 13. CORS — el dolor de cabeza típico

**CORS = Cross-Origin Resource Sharing**.

**El problema**: browser bloquea por defecto requests JavaScript a dominios distintos del que sirvió la página (Same-Origin Policy). Esto es POR SEGURIDAD: evita que script malicioso de evil.com haga requests autenticados a tu banco.

**La solución**: el SERVER del recurso al que quieres acceder pone headers diciendo "permito requests desde estos orígenes".

**Ejemplo**: tu frontend en `https://app.example.com` hace fetch a `https://api.example.com`. Browser bloquea por defecto. Para permitirlo, `api.example.com` debe responder con:

```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Headers: Content-Type, Authorization
```

**Preflight request**: para métodos no-simples (PUT, DELETE) o headers custom, browser envía un OPTIONS request ANTES del real para preguntar "¿permites esto?". Si server responde OK, browser hace el request real.

**En FastAPI**:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["https://app.example.com"])
```

CORS es lo que MÁS lía a developers nuevos en frontend+backend separados. Ahora ya sabes por qué.

---

## 14. Aplicación al perfil del usuario

### En el Phone Book FastAPI

Cuando tu `cli.py` hace `requests.post(...)`, está usando HTTP/1.1 (default de `requests` library). Si quisieras HTTP/2, necesitarías `httpx` con configuración explícita.

Tu FastAPI sirve HTTP/1.1 por defecto vía Uvicorn. Para HTTP/2 necesitarías un reverse proxy delante (nginx, Caddy, Traefik) que haga la traducción.

Cookies y sesiones: tu Phone Book no los necesita (sin auth), pero cuando hagas T1.2 (Auth con JWT) verás todo esto en práctica.

### En entrevistas tecnicas

La pregunta clásica *"¿qué pasa cuando escribes google.com en el navegador?"* requiere mencionar HTTP en algún punto. Saber distinguir 1.1 vs 2 vs 3 te diferencia.

Pregunta típica: *"¿por qué HTTP/2 es más rápido que HTTP/1.1?"* → multiplexing + header compression + binary framing. Sección 9 te lo da.

Pregunta avanzada: *"¿por qué HTTP/3 abandona TCP?"* → HOL blocking de TCP que HTTP/2 no podía resolver. Sección 10.

---

## 15. Trampas típicas

**"GET no puede tener body"**: técnicamente PUEDE (la spec no lo prohíbe), pero la mayoría de proxies/CDNs lo descartan. Convención: GET sin body.

**"DELETE sí o no body"**: igual que GET — puede pero NO se debe. Pasa parámetros por path/query.

**"200 con error message en body"**: ANTI-PATTERN. Status code = 200 significa SUCCESS. Si hubo error, devuelve 4xx o 5xx con detalle en body. Por desgracia muchos APIs hacen esto mal y luego es lío.

**"Cookies funcionan cross-domain por defecto"**: NO. Cookies son por DOMINIO. tu_app.com NO ve cookies de otro_dominio.com. CORS añade headers, pero las cookies necesitan también `Access-Control-Allow-Credentials: true` + `credentials: 'include'` en fetch.

**"HTTPS y HTTP son protocolos distintos"**: HTTPS = HTTP sobre TLS. Es el MISMO HTTP encapsulado en TLS. Por eso 99% de lo que sabes de HTTP aplica a HTTPS también.

**"Status code 500 significa que mi código tiene un bug"**: casi siempre sí. 500 = "el server falló inesperadamente". Pero también puede ser DB caída, OOM, disk full, etc. Por eso es importante tener logging estructurado para distinguir.

**"CORS lo arreglas en el frontend"**: NO. CORS lo decide el SERVER del recurso (los headers). Si tu API no tiene los headers, no hay nada que tu frontend pueda hacer. Tienes que arreglarlo en backend.

---

## 16. Cosas típicas que preguntan en interview

**"Diferencia entre PUT y PATCH"**: PUT reemplaza el recurso ENTERO. Si omites un campo, se pierde. PATCH modifica SOLO los campos que mandas.

**"Diferencia entre POST y PUT"**: POST crea (no idempotente). PUT actualiza (idempotente). Aunque algunos APIs usan PUT también para crear con id conocido.

**"¿Qué es REST y por qué tu API no es realmente REST?"**: REST tiene 6 constraints (Roy Fielding 2000): client-server, stateless, cacheable, uniform interface (HATEOAS específicamente), layered system, code on demand (opcional). El 99% de "REST APIs" no implementa HATEOAS. Realmente son "HTTP APIs JSON". Más honesto.

**"¿Cuándo usarías HTTP/2 vs HTTP/3?"**: HTTP/2: cualquier server moderno, soporte universal. HTTP/3: si tienes muchos clientes móviles (mejor en redes con loss), si te importa connection migration, si tu CDN lo soporta.

**"Diferencia entre 401 y 403"**: 401 = no estás autenticado (no me has dicho quién eres). 403 = estás autenticado pero no tienes permiso para esto.

**"¿Cómo manejas idempotencia en POST?"**: idempotency key. Cliente genera UUID, lo manda en header. Server lo guarda con el resultado. Si llega segundo request con mismo UUID → devuelve resultado guardado, no procesa de nuevo. Stripe lo hace así, es estándar moderno.

---

## 17. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Anatomía request/response (request line + headers + body).
- Los 5 métodos REST y diferencias (GET/POST/PUT/PATCH/DELETE).
- Idempotencia: qué es y qué métodos son idempotentes.
- Los 5 grupos de status codes y 1-2 ejemplos típicos de cada uno.
- Diferencia entre 401 y 403, entre 502 y 504.
- Cookies vs JWT (stateful vs stateless).
- CORS: por qué existe y cómo se resuelve.
- HTTP/1.1 vs 2 vs 3: 2-3 diferencias clave.
- Por qué HTTP/2 multiplexa y por qué HTTP/3 abandona TCP.

Si no puedes → relee la sección correspondiente.

---

## Conexiones

- [[01-tcp-ip-osi]] — el transporte sobre el que corre HTTP
- [[03-dns-resolucion-nombres]] — cómo se resuelve el dominio antes de HTTP
- [[04-sockets-y-puertos]] — qué pasa por debajo de HTTP en código
- [[05-tls-https]] — HTTPS = HTTP + TLS
- [[../00_README]] — cluster CS Fundamentos
- — HTTP aplicado en FastAPI
- — HTTP aplicado en `requests` cliente
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **MDN HTTP docs** (developer.mozilla.org/HTTP) — referencia exhaustiva, accesible.
- **High Performance Browser Networking** (hpbn.co — gratis online) — Ilya Grigorik, capítulos HTTP excelentes.
- **HTTP/3 explained** (http3-explained.haxx.se) — gratis, denso pero completo.
- **REST in Practice** (Webber et al.) — si quieres profundizar en REST de verdad.
- **jwt.io** — para ver cómo se forman JWTs.
- **httpie / curl / wireshark** — herramientas para inspeccionar tráfico HTTP real.
