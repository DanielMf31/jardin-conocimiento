# 04 — JWT y session management

> 📚 **Doc 4 (último) del cluster Security**. Cómo gestionas usuarios autenticados sin pisarte. JWT vs sessions tradicionales, refresh tokens, revocation, los trade-offs que casi todo developer mete mal.
> 🔥 **Frecuencia interview**: aparece siempre en backend interviews. "Diferencia JWT vs session", "cómo invalidas un JWT".
> ⏱️ **Tiempo de lectura estimado**: 35-50 min.

---

## 1. El problema fundamental

Tras un login exitoso, ¿cómo recuerda el server que TÚ eres TÚ en requests posteriores? **HTTP es stateless** — cada request llega "nueva", sin memoria. Necesitas algún mecanismo para mantener sesión.

Hay dos enfoques principales:

1. **Sessions tradicionales (server-side)**: server guarda estado, cliente solo lleva un identificador.
2. **Tokens (client-side, típicamente JWT)**: cliente lleva el estado completo (firmado por server).

Cada uno con trade-offs específicos. La elección **depende del caso de uso** — no hay "mejor" universal.

---

## 2. Sessions tradicionales — el approach clásico

### Cómo funcionan

1. Usuario hace login. Server valida.
2. Server genera **session_id** aleatorio (e.g. 32 bytes hex).
3. Server guarda en su DB/cache: `session_id → {user_id, created_at, ...}`.
4. Server envía cookie: `Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Strict`.
5. Cada request del browser incluye automático: `Cookie: session_id=abc123`.
6. Server lee cookie, busca session_id en DB, identifica al usuario.
7. Logout: server borra session de DB. Cookie en browser queda inútil.

### Storage típico

- **Redis**: la opción más común. Sessions en memoria con TTL automático.
- **DB (Postgres tabla `sessions`)**: más simple pero más lento.
- **In-memory por server**: solo si tienes 1 server (no escala).
- **Memcached**: histórico, similar a Redis.

### Pros

- **Revocation trivial**: borras de DB, sesión muerta inmediato.
- **Datos no expuestos al cliente**: session_id es opaco. Toda info en server.
- **Cambios de permisos inmediatos**: si actualizas el rol del usuario, próxima request lo usa.
- **Session size**: cliente lleva solo 32 bytes (el ID). Server puede tener mucha info asociada.

### Contras

- **Stateful**: server necesita storage compartido entre instancias (Redis cluster, etc.).
- **Lookup en cada request**: 1 round trip a Redis añade latencia (~1ms).
- **Single point of failure**: si Redis cae, nadie puede autenticarse.
- **Replication lag**: en Redis cluster, posible inconsistencia momentánea.

---

## 3. JWT — el approach moderno (con caveats)

### Qué es un JWT

**JWT (JSON Web Token)** es un token con 3 partes separadas por puntos:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NSIsImV4cCI6MTczNTAwMDAwMH0.signature_aqui
└──────── header ────────┘ └──────── payload ────────┘ └─── signature ───┘
```

- **Header**: `{"alg": "HS256", "typ": "JWT"}` — qué algoritmo de firma se usa.
- **Payload**: `{"sub": "user_id", "exp": 1735000000, "iat": 1734996400, "role": "admin"}` — claims sobre el usuario.
- **Signature**: HMAC del header+payload con una key secret del server.

Las primeras dos partes son **base64url**, no cifradas. **Cualquiera puede leer** el payload de un JWT. Lo que las hace seguras es la signature: si modificas el payload, la signature ya no matcha y el server lo rechaza.

### Algoritmos de firma

- **HS256**: HMAC con SHA-256. Symmetric — server usa la misma key para firmar y verificar.
- **RS256**: RSA con SHA-256. Asymmetric — server firma con privkey, cualquiera puede verificar con pubkey.
- **ES256**: ECDSA con SHA-256. Asymmetric, más eficiente que RSA.

**Cuándo cada uno**:
- HS256: 1 server o sistema cerrado donde todos comparten la key.
- RS256/ES256: microservices donde el server-A firma y server-B verifica (server-B solo necesita la pubkey, no puede firmar tokens fake).

### Cómo se usa

1. Login. Server valida.
2. Server crea JWT con `{user_id, exp: now+15min, ...}` y lo firma.
3. Server envía: `{"access_token": "eyJ..."}` en response body.
4. Cliente almacena (localStorage, secure cookie, memoria).
5. Cliente envía en cada request: `Authorization: Bearer eyJ...`.
6. Server **verifica firma** y lee payload. Si OK → usuario identificado.
7. Server **NO consulta ninguna DB** para auth. Todo está en el token.

---

## 4. JWT vs sessions — los trade-offs reales

### Stateless vs stateful

JWT es **stateless en el server**: no necesitas DB para validar (solo verificar firma). Sessions necesitan DB lookup en cada request.

**Pros JWT**: escalable horizontalmente, no hay bottleneck en Redis, microservices independientes.
**Pros sessions**: control total en server.

### Revocation — el gran problema con JWT

**Sessions**: borras de DB, sesión muerta inmediato.

**JWT**: una vez emitido, válido hasta su `exp`. NO puedes "borrarlo" del cliente. **Revocar un JWT antes de su expiry requiere mantener una blacklist server-side**, lo cual rompe la propiedad stateless que era el atractivo principal.

**Soluciones imperfectas**:
1. **Tokens cortos** (15 min) + refresh tokens. Si quiero revocar, espero hasta expiry.
2. **Token blacklist en Redis**: TTL = remaining lifetime del token. Funciona pero re-introduce stateful lookup.
3. **Token version en DB**: cada user tiene `token_version`. JWT incluye su version. Cuando quiero revocar todos los tokens del user, incremento version. Cualquier token con version vieja → reject.

Cada solución tiene trade-offs. **No hay buena solución universal a revocation con JWT**.

### Datos visibles al cliente

JWT payload es **legible** (solo base64). Cliente puede leer claims. Esto puede ser feature (cliente sabe expiry, role) o bug (no metas datos sensibles en JWT).

Sessions: identifier opaco. Server puede tener metadata sensible internamente sin exponerla.

### Cambios de permisos

JWT: si cambias el rol del user, los JWT activos siguen con el rol viejo hasta expirar. Para forzar update, espera al refresh.

Sessions: cambias en DB, próxima request lo usa.

### Tamaño

JWT: payload + headers + signature. Típicamente 200-500 bytes. Se envía en CADA request.

Sessions: cookie con ID (32 bytes). Mucho menor.

Para apps con muchos requests pequeños, JWT añade overhead notable.

---

## 5. Cuándo usar cada uno

### Usa sessions cuando

- **App web tradicional** con frontend en mismo dominio.
- **Necesitas revocation immediate** (logout, ban user).
- **Usuarios críticos** (admin) donde control fino importa.
- **Datos sensibles** que no quieres en cliente.
- **Lecturas dominantes** (no muchos requests por session).

### Usa JWT cuando

- **APIs públicas** o microservices.
- **Mobile/SPA** donde cookies son problemáticas.
- **Cross-domain** auth (varias apps comparten auth).
- **Stateless requirement** (escalado masivo, edge functions).
- **Federated identity** (OAuth, OpenID Connect).

### Híbrido moderno (lo mejor de ambos)

**Backend-for-Frontend (BFF) pattern**: tu SPA habla con un BFF via session cookies (HttpOnly). El BFF habla con tus APIs internas via JWT. Cliente nunca ve JWT, server tiene revocation control.

Es lo que hace muchas apps modernas (Auth0 + BFF, Cloudflare Access).

---

## 6. Refresh tokens — el patrón estándar

JWT corto (15-60 min) tiene problema: usuario tiene que re-login frecuente.

**Solución**: pareja de tokens.

- **Access token**: JWT corto (15-60 min). Se envía en cada request a APIs.
- **Refresh token**: token largo (7-30 días) opaco/random. Solo se usa para obtener nuevo access token.

### Flow

1. Login → server emite access + refresh.
2. Cliente usa access en requests normales.
3. Access expira (15 min después). Cliente recibe 401.
4. Cliente envía refresh a `/auth/refresh`. Server valida + emite nuevo access (y opcionalmente nuevo refresh).
5. Refresh almacenado server-side (DB) con info del user. Permite revocation.
6. Logout: borra refresh de DB. Próximo intento de refresh → falla.

### Refresh token rotation

Mejora moderna: **cada uso del refresh emite un refresh NUEVO** (rotation). El viejo se invalida.

**Por qué**: si alguien roba un refresh token y lo usa, el legítimo usuario notará (el suyo ya no funciona). Detección de breach.

Esto es lo que recomienda OAuth 2.1 spec.

---

## 7. Almacenamiento del token en cliente — el debate

Para apps web, dónde guarda el cliente el JWT importa MUCHO:

### localStorage / sessionStorage

Acceso desde JavaScript. Se envía manualmente en headers.

**Pros**: simple, funciona cross-domain.
**Contras**: **vulnerable a XSS**. Si atacante inyecta script en tu página, lee localStorage entero.

### Cookies HttpOnly + Secure + SameSite

El browser las maneja. JavaScript NO puede leerlas.

**Pros**: inmune a XSS reading. Auto-incluidas en requests al mismo dominio.
**Contras**: vulnerable a CSRF (si no usas SameSite=Strict). No funciona cross-domain trivial.

### Memoria (variables JS)

Solo durante sesión del browser. Se pierde al refresh.

**Pros**: no persiste después de cerrar tab. Inmune a XSS storage.
**Contras**: se pierde en refresh. Mala UX para usuarios.

### El consenso moderno

**Para mayor seguridad**: HttpOnly cookies + CSRF tokens (o SameSite=Strict). Browsers manejan todo, JavaScript no toca tokens.

**Para SPAs cross-domain**: refresh token en cookie HttpOnly + access token en memoria JS. Refresh recupera access cuando hace falta.

**Anti-pattern**: poner JWT con datos sensibles en localStorage. Vulnerable a cualquier XSS.

---

## 8. JWT — claims comunes y su significado

El payload puede tener cualquier claim, pero hay convenciones:

### Registered claims (estándar)

- **`iss`** (issuer): quién emitió el token.
- **`sub`** (subject): a quién identifica (user_id típicamente).
- **`aud`** (audience): para qué API/servicio es válido.
- **`exp`** (expiration time): Unix timestamp cuando expira.
- **`nbf`** (not before): no válido antes de este time.
- **`iat`** (issued at): cuándo se emitió.
- **`jti`** (JWT ID): identificador único (para blacklist).

### Custom claims

Cualquier dato que quieras meter: `role`, `permissions`, `email`, etc.

**Ojo con tamaño**: JWT se envía en cada request. Custom claims grandes hinchan cada request.

**Ojo con sensibilidad**: payload es base64 (legible). NO metas passwords, tokens internos, info que no quieres exponer.

---

## 9. OAuth 2.0 y OpenID Connect — el ecosistema más amplio

JWT no es lo mismo que OAuth, pero suelen ir juntos.

**OAuth 2.0**: framework de autorización. Permite que App A acceda a recursos de App B en nombre del usuario, sin que A tenga la password de B. "Login with Google" usa OAuth.

**OpenID Connect (OIDC)**: capa de autenticación encima de OAuth 2.0. Define cómo obtener info del usuario (email, nombre, etc.).

**Tokens de OAuth/OIDC**:
- **Access token**: típicamente JWT (en OIDC) o opaco (en OAuth puro).
- **ID token**: JWT con info del user (en OIDC).
- **Refresh token**: opaco, para obtener nuevos access tokens.

**Providers comunes**: Google, GitHub, Microsoft, Auth0, Okta, Clerk, Supabase Auth, Firebase Auth.

Para apps modernas: usar provider gestionado (Auth0, Clerk, Supabase) en vez de implementar auth desde cero. Auth es difícil de hacer bien.

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

T1.2 build: cuando añadas auth, decisión:

**Opción A — JWT con FastAPI**:
```python
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# emitir
token = jwt.encode({"sub": user.id, "exp": now + timedelta(minutes=15)}, SECRET_KEY)

# verificar
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
user_id = payload["sub"]
```

**Opción B — sessions con Redis**:
```python
session_id = secrets.token_urlsafe(32)
redis.setex(f"session:{session_id}", 3600, json.dumps({"user_id": user.id}))
# enviar cookie
```

Para tu proyecto: cualquiera vale. JWT es más "moderno" y aprende patrones útiles.

### En entrevistas tecnicas

**Pregunta clásica**: "Diferencia JWT vs session".

JWT stateless (server no necesita storage), revocation difícil, payload visible. Session stateful (server tiene DB), revocation trivial, opaco al cliente.

**Pregunta avanzada**: "Cómo invalidas un JWT".

Mal pregunta — JWT mal entendido como "stateless mágico". Soluciones: tokens cortos + refresh, blacklist en Redis (re-introduce state), token versioning per user.

**Pregunta sobre seguridad**: "Dónde guardas el JWT en el cliente".

HttpOnly cookies preferido (inmune XSS). Si necesitas localStorage: assume XSS robe el token, asegúrate que daño sea limitado (token corto, scope limitado).

**Pregunta de diseño**: "Diseña sistema de auth para SPA + API".

OAuth 2.0 con refresh token rotation. Access token en memoria JS, refresh en cookie HttpOnly. Refresh corto (días), access muy corto (minutos). Logout invalida refresh server-side.

---

## 11. Trampas típicas

**"JWT son seguros porque son firmados"**: firma garantiza integridad, NO confidencialidad. Payload es legible. NO metas secretos.

**"JWT no necesita server-side state"**: parcialmente cierto. Pero revocation requiere state. Refresh tokens requieren state. En la práctica casi siempre hay algo de state.

**"Tokens largos son más cómodos"**: y MÁS PELIGROSOS. Un token robado dura más. 15-60 min para access, 7-30 días refresh es estándar.

**"localStorage es seguro porque solo mi domain accede"**: vulnerable a XSS. Cualquier inject de script roba todo.

**"Refresh token en localStorage también"**: peor. Si robas refresh, tienes acceso indefinido. Refresh debe estar en cookie HttpOnly.

**"Implemento auth desde cero"**: en producción, casi nunca buena idea. Use Auth0, Clerk, Supabase, etc. Auth tiene mil edge cases.

**"HS256 con key compartida entre microservices"**: anti-pattern. Cualquier service puede emitir tokens fake. Usa RS256 con privkey en auth service y pubkey en consumers.

**"JWT exp resuelve revocation"**: no si necesitas revocar BEFORE expiry (logout, ban, password reset).

---

## 12. Preguntas típicas de interview

**JWT vs session**: stateless vs stateful trade-off. Revocation vs scaling.

**Estructura JWT**: header.payload.signature. Header dice algoritmo. Payload tiene claims. Signature garantiza integridad.

**HS256 vs RS256**: symmetric vs asymmetric. RS256 cuando varios services verifican.

**Cómo invalidar JWT**: blacklist Redis, token versioning, refresh tokens.

**Refresh tokens — cómo funcionan**: corto access + largo refresh. Refresh server-side para revocation. Rotation moderna.

**Donde guardar tokens en cliente**: HttpOnly cookies preferido. Refresh en cookie + access en memoria es patrón moderno.

**OAuth vs OIDC**: OAuth = autorización. OIDC = autenticación encima de OAuth. JWT suele ser el formato.

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Diferencia JWT vs sessions con trade-offs.
- Estructura JWT (header.payload.signature).
- HS256 vs RS256 (symmetric vs asymmetric).
- Por qué JWT revocation es problema y soluciones imperfectas.
- Refresh tokens y rotation.
- Trade-offs storage cliente (localStorage vs HttpOnly cookies).
- Cuándo sessions vs JWT.
- BFF pattern como híbrido.

Si no puedes → relee.

---

## ¡Cluster Security completado! 🎉

4 docs:
- `01-tls-handshake-detallado` — TLS 1.3 paso a paso.
- `02-hashing-vs-cifrado` — primitivas crypto y password hashing.
- `03-owasp-top-10` — las 10 vulnerabilidades más comunes.
- `04-jwt-y-session-management` — auth modernos.

**Próximo (último)**: cluster 09 (Compilers — 2 docs, Tier 3 opcional).

---

## Conexiones

- [[01-tls-handshake-detallado]] — token transport seguro
- [[02-hashing-vs-cifrado]] — base de tokens y passwords
- [[03-owasp-top-10]] — A07 auth failures
- [[../04_system_design_patterns/05-rate-limiting]] — anti-brute-force
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **JWT.io** — debugger de JWTs y referencia de algoritmos.
- **OAuth 2.0 Simplified** (Aaron Parecki, gratis online) — claro y completo.
- **OWASP JWT Cheatsheet** — práctico.
- **The Copenhagen Book** — moderno guide de auth (`thecopenhagenbook.com`).
- **Auth0, Clerk, Supabase Auth** — providers a considerar para no implementar desde cero.
- **`python-jose`** (Python), **`jsonwebtoken`** (Node) — librerías JWT.
