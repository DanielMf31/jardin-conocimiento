# 03 — OWASP Top 10

> **Doc 3 del cluster Security**. Las 10 vulnerabilidades más comunes en aplicaciones web. Saberlas todas + cómo prevenirlas es el mínimo profesional para cualquier backend developer.
> **Frecuencia interview**: aparece en preguntas de seguridad básica. Conocerlas TODAS te diferencia del que solo sabe SQL injection y XSS.
> **Tiempo de lectura estimado**: 40-55 min.

---

## 1. Qué es OWASP Top 10

**OWASP** (Open Worldwide Application Security Project) es una fundación que publica, cada 3-4 años, **una lista de las 10 vulnerabilidades más críticas en apps web**. Es el documento de referencia de la industria para seguridad web.

La lista cambia con el tiempo según evoluciona el panorama de amenazas. La versión actual es **OWASP Top 10 2021** (la siguiente esperada para 2025-2026).

Saber el Top 10 es **el mínimo profesional**. Si no conoces estas, tu app casi seguramente tiene varias.

---

## 2. La lista 2021 (versión vigente)

1. **A01: Broken Access Control**
2. **A02: Cryptographic Failures**
3. **A03: Injection**
4. **A04: Insecure Design**
5. **A05: Security Misconfiguration**
6. **A06: Vulnerable and Outdated Components**
7. **A07: Identification and Authentication Failures**
8. **A08: Software and Data Integrity Failures**
9. **A09: Security Logging and Monitoring Failures**
10. **A10: Server-Side Request Forgery (SSRF)**

Vamos una a una con qué es, ejemplo y cómo prevenir.

---

## 3. A01 — Broken Access Control

**Qué es**: la app no enforce correctamente quién puede hacer qué. Usuarios acceden a recursos que no deberían.

### Ejemplos típicos

**IDOR (Insecure Direct Object Reference)**: la URL `/api/orders/123` permite ver la orden 123. Pero si cambio a `/api/orders/124` veo la orden de OTRO usuario. La app no verificó que la orden 124 me pertenece.

**Vertical privilege escalation**: usuario normal accede a endpoints de admin (`/admin/users`) porque el endpoint no verifica el rol.

**Force browsing**: rutas no listadas pero accesibles directamente (`/internal/debug`, `/api/v0/old-endpoint`).

**Mass assignment**: PUT request con campo `role: admin` se aplica porque el server hace `user.update(request.json)` sin filtrar campos.

### Prevención

- **Deny by default**: cada endpoint requiere check explícito de permisos.
- **Verificar ownership en cada query**: `WHERE id = ? AND user_id = ?` (no solo by id).
- **Roles enforced en backend**, no confiar en UI (cliente puede saltarse).
- **Whitelist de campos editables** en updates (`UserUpdate` Pydantic con campos específicos, no `**request.json`).
- **Rate limit + audit logs** para detectar enumeration attacks.

OWASP 2021 dijo que **A01 es la #1** porque es ubicua y fácil de cometer.

---

## 4. A02 — Cryptographic Failures

**Qué es**: datos sensibles expuestos por mal uso de criptografía (o falta de ella). Antes se llamaba "Sensitive Data Exposure".

### Ejemplos típicos

- Passwords almacenados en plaintext o con MD5/SHA-1.
- HTTP en lugar de HTTPS para datos sensibles.
- Datos sensibles (números de tarjeta, SSN) almacenados sin cifrar.
- Cifrado con algoritmos deprecated (DES, RC4).
- Keys hardcoded en el código fuente.
- TLS mal configurado (cipher suites débiles, certs vencidos, sin HSTS).

### Prevención

- **HTTPS everywhere**, redirect HTTP → HTTPS, HSTS header.
- **Cifrado at-rest** para datos sensibles (AES-GCM con keys del KMS).
- **bcrypt/Argon2** para passwords (ver doc 02).
- **Keys en env vars o KMS**, nunca en código.
- **TLS 1.3** como mínimo, deshabilitar 1.0/1.1.
- **Don't store what you don't need**: el dato más seguro es el que no tienes.

---

## 5. A03 — Injection

**Qué es**: input no sanitizado se interpreta como código/comandos por algún sistema downstream.

### Tipos

**SQL injection**: el clásico. `SELECT * FROM users WHERE name = '" + user_input + "'"`. Si user_input = `' OR '1'='1`, la query selecciona todo.

**NoSQL injection**: `db.users.find({name: req.body.name})`. Si `req.body.name = {$gt: ""}`, devuelve todos.

**Command injection**: `os.system(f"ping {user_input}")` con `user_input = "google.com; rm -rf /"`.

**LDAP injection**, **XML injection**, **Header injection**, etc.

**XSS (Cross-Site Scripting)** es injection de JavaScript en el browser de otros usuarios. Categorizada por OWASP como tipo de injection.

### Prevención

- **Parameterized queries / prepared statements** (SQL): la DB sabe qué es código y qué es data. NUNCA concatenar input en SQL.

```python
# MAL
db.execute(f"SELECT * FROM users WHERE name = '{name}'")

# BIEN
db.execute("SELECT * FROM users WHERE name = ?", (name,))
```

- **ORMs bien usados** (SQLAlchemy, Django ORM) hacen esto automáticamente. Pero ojo con `text()` o queries raw.
- **Escape output** según contexto (HTML, JS, URL, SQL).
- **Validation de input** (whitelist > blacklist).
- **Para shell commands**: usa `subprocess` con lista de args, NUNCA shell=True con f-strings.
- **CSP headers** para mitigar XSS.

---

## 6. A04 — Insecure Design

**Qué es**: nuevo en 2021. Categoría amplia para **decisiones de arquitectura/diseño** que crean vulnerabilidades, antes de cualquier bug de implementación.

### Ejemplos

- Sistema de password reset que envía la nueva password por email (en plain text, recoverable).
- Workflow de pago que confía en datos del cliente (precios, descuentos en el JSON del request).
- Threat model que NO considera abuso por usuarios legítimos.
- Falta de rate limiting en operaciones costosas.
- API que expone IDs secuenciales (facilita enumeration).

### Prevención

- **Threat modeling** durante diseño (¿qué puede salir mal?).
- **Secure-by-default**: las decisiones por defecto deben ser seguras.
- **Defense in depth**: múltiples capas, no confiar en una sola.
- **Principio de menor privilegio**: cada componente con permisos mínimos.
- **Failure modes analysis**: ¿qué pasa si X componente cae?
- **Limits everywhere**: rate limits, file size limits, timeouts.

Esto es **arquitectura**, no implementación. Más difícil de arreglar después.

---

## 7. A05 — Security Misconfiguration

**Qué es**: la app o infrastructure está mal configurada. Defaults inseguros, debug en producción, headers faltantes.

### Ejemplos

- Stack traces visibles en producción (leak de info interna).
- Cuentas default no cambiadas (admin/admin).
- Directories listings habilitados (`/uploads/` muestra todos los archivos).
- CORS demasiado permisivo (`Access-Control-Allow-Origin: *`).
- Headers de seguridad faltantes (HSTS, CSP, X-Frame-Options).
- Servicios cloud configurados como public (S3 buckets, BD ports).
- Software actualizado al mínimo (último parche).
- Endpoints de debug/admin expuestos (`/actuator`, `/debug`).

### Prevención

- **Hardening guides** del SO/framework usado.
- **Security headers** automáticos (helmet.js, secure-cookie, FastAPI middleware).
- **Errores genéricos** en producción, sin stack traces visibles.
- **Defaults seguros** en código (deny by default).
- **Infrastructure as code** + scanners (Checkov, tfsec, kube-bench).
- **Minimal attack surface**: deshabilitar features no usadas.
- **Auditoria de config** periódica.

---

## 8. A06 — Vulnerable and Outdated Components

**Qué es**: tu app usa dependencias con vulnerabilidades conocidas. Probablemente la categoría más común.

### Ejemplo histórico — Equifax 2017

Equifax sufrió breach masivo (147 millones de usuarios) por usar Apache Struts con vuln conocida desde meses antes. Habían existido patches. No los aplicaron. Pérdidas: $1.4B.

### Prevención

- **Dependency scanning automático**: Dependabot (GitHub), Snyk, Renovate.
- **Vulnerability databases**: CVE, GitHub Advisory, OSV, npm audit.
- **Security updates en CI**: actualizar deps regularmente, tests automáticos detectan regresiones.
- **SCA (Software Composition Analysis) tools**: BlackDuck, Sonatype, FOSSA.
- **SBOM (Software Bill of Materials)**: lista de tus deps + sus vulns.
- **Política**: actualizar críticos en <X días, mediums en <Y semanas.

Para tu Python: `pip-audit`, `safety check`. Para JavaScript: `npm audit`. Para imágenes Docker: Trivy, Grype.

---

## 9. A07 — Identification and Authentication Failures

**Qué es**: bugs en cómo identificas/autenticas usuarios. Antes "Broken Authentication".

### Ejemplos

- Brute-force sin rate limiting.
- Passwords débiles permitidos.
- Session IDs predecibles o expuestos en URL.
- Multi-factor authentication ausente.
- Recovery flows débiles (security questions adivinables).
- Sessions que nunca expiran.
- Logout que no invalida la session realmente.

### Prevención

- **Rate limiting** agresivo en endpoints de auth (5 intentos/min por IP).
- **Strong password policy** (longitud mínima, no compromised passwords — check contra haveibeenpwned).
- **MFA** (TOTP, WebAuthn).
- **Session IDs**: random suficiente (>=128 bits), HttpOnly + Secure cookies.
- **Session expiry** + sliding expiry.
- **Logout invalida**: borrar de DB session store.
- **CAPTCHA** después de N intentos.
- **Account lockout** temporal (con reactivación segura).

Ver [[04-jwt-y-session-management]] para detalle de auth modernos.

---

## 10. A08 — Software and Data Integrity Failures

**Qué es**: nuevo en 2021. Confianza en código/data sin verificar integridad. Ejemplo masivo: SolarWinds attack.

### Ejemplos

- Auto-update de software desde fuentes no firmadas.
- CI/CD pipeline que ejecuta código de PR sin sandbox.
- Deserialization de objetos no confiables (Java/Python pickle desde input externo).
- Plugins/dependencies cargadas dinámicamente sin verificación.
- Webhooks sin verificación de signature.

### Prevención

- **Verificar signatures** en updates (apt, npm, container images).
- **Subresource Integrity (SRI)** para JS/CSS de CDNs externos: `<script integrity="sha384-...">`.
- **Supply chain security**: pinear versiones exactas, lockfiles.
- **Sandboxes** para CI ejecutando PRs externos.
- **NUNCA deserializar pickle/yaml.load sin trust** del input.
- **Webhook signatures** (HMAC).

---

## 11. A09 — Security Logging and Monitoring Failures

**Qué es**: no detectas ataques porque no logueas suficiente, o no monitoreas los logs.

### Ejemplos

- Login failures no logueadas → brute-force pasa desapercibido.
- API errors no monitoreados → ataques en curso pasan días sin detectar.
- Logs en local sin agregación → si server cae, logs se pierden.
- No alerts → equipo se entera por incidente público.

### Prevención

- **Loguear eventos de seguridad**: logins (éxito y fallo), cambios de privilegios, acciones admin, transacciones financieras.
- **Centralizar logs**: ELK, Loki, Datadog, Splunk.
- **No loguear secretos** (passwords, tokens, PII innecesaria).
- **Alertas en patrones sospechosos**: spike de errores, IPs atacando, geolocations inusuales.
- **Retention adecuada**: logs disponibles meses, no horas.
- **Tabletop exercises**: simular incidente, ¿el equipo lo detectaría?

---

## 12. A10 — Server-Side Request Forgery (SSRF)

**Qué es**: la app hace requests a URLs controladas por el atacante. El atacante usa tu server para acceder a recursos internos.

### Ejemplo

App permite "fetch URL para preview" → atacante envía `http://169.254.169.254/latest/meta-data/iam/security-credentials/` (metadata endpoint AWS) → server fetcha y devuelve credentials de AWS al atacante.

Otro: `http://internal-admin.company.com/dangerous-action` → server (que está en VPN interna) puede acceder, atacante (externo) no podía directamente.

### Prevención

- **Allowlist de URLs/dominios** permitidos. NO blacklist.
- **Bloquear IPs internas** (169.254.x.x, 10.x.x.x, 192.168.x.x, localhost) en cualquier fetch desde server.
- **DNS resolution antes**: bloquear si resuelve a IP privada.
- **Disable HTTP redirects** automáticos (atacante puede redirigir a IP interna).
- **Network segmentation**: el server no debería poder acceder a metadata APIs (firewall).
- **Use libraries seguras**: validar URLs antes de fetch.

---

## 13. Vulnerabilidades fuera del Top 10 que también importan

El Top 10 es el inicio. Hay otros vectores comunes:

- **CSRF (Cross-Site Request Forgery)**: atacante hace que tu browser autenticado envíe requests a otro site. Mitigación: SameSite cookies, CSRF tokens.
- **CORS misconfiguration**: ya en A05 pero merece énfasis.
- **Open redirect**: `?redirect_url=https://evil.com` se usa para phishing.
- **Race conditions en lógica de negocio** (ej: TOCTOU en cobros).
- **Information disclosure** via mensajes de error, headers, metadata.
- **DOS / DDoS**: rate limiting + WAF + CDN.

---

## 14. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Hoy:
- A03 Injection: usar SQLAlchemy ORM (parameterized queries automáticas), NO concatenar SQL.
- A05 Misconfiguration: stack traces NO en producción (FastAPI tiene flag).
- A07 Auth: cuando añadas auth (T1.2), bcrypt + rate limit + session expiry.

### En entrevistas tecnicas

**Pregunta clásica**: "Cómo previenes SQL injection".

Parameterized queries / prepared statements. ORMs lo hacen automático. NUNCA concatenar input en SQL. Validar input adicional (whitelist).

**Pregunta sobre access control**: "Diferencia autenticación vs autorización".

Auth (authentication): verificar QUIÉN eres (login). AuthZ (authorization): verificar QUÉ puedes hacer (permisos). Ambas críticas, frecuentemente bien una y mal la otra.

**Pregunta avanzada**: "Diseña sistema de auth seguro".

bcrypt/Argon2 para passwords + rate limiting + MFA opcional + session IDs random + HttpOnly/Secure/SameSite cookies + logout invalida en server + audit logs.

**Pregunta sobre OWASP general**: "Top 5 vulnerabilidades web que más has visto".

Honestamente: A01 broken access control, A03 injection (especialmente XSS), A05 misconfig, A06 outdated components, A07 weak auth.

---

## 15. Trampas típicas

**"Mi framework ya es seguro"**: framework te da defaults razonables. Pero MAL USADO sigue siendo inseguro. Lee security docs específicas.

**"Solo apps grandes son atacadas"**: scanners automatizados atacan TODO lo expuesto a internet. Tu side project es tan vulnerable como cualquiera.

**"Whitelist es paranoia"**: NO. Allowlist es siempre más seguro que blacklist. Atacantes son creativos con bypass de blacklists.

**"HTTPS me protege todo"**: protege en tránsito. No protege contra SQL injection, broken access control, XSS, etc.

**"Validar en frontend basta"**: NUNCA. Cliente puede modificarse (browser dev tools, curl). Validar SIEMPRE en backend también.

**"Mi app no tiene datos sensibles"**: ¿passwords? PII? Acceso a otras apps? Casi todas las apps tienen algo valioso.

**"Solo escaneo deps anualmente"**: vulnerabilidades nuevas salen diariamente. Dependabot diario es estándar moderno.

---

## 16. Preguntas típicas de interview

**OWASP Top 10**: nombrar las 10 con un ejemplo cada una. Saber prevention.

**SQL injection — cómo prevenir**: parameterized queries.

**XSS — qué es y mitigaciones**: output encoding, CSP, sanitización de input.

**CSRF**: tokens + SameSite cookies.

**Broken access control con ejemplo**: IDOR. Verificar ownership en cada query.

**SSRF**: validar URLs server-side, bloquear IPs internas.

**Cómo guardas passwords**: bcrypt/Argon2 con salt.

**Diferencia auth vs authz**: cubierto.

---

## 17. Resumen mental — checklist

Dominas este doc si puedes nombrar y explicar las 10 vulnerabilidades en menos de 5 minutos:

- A01 Broken Access Control (IDOR, escalación)
- A02 Cryptographic Failures (sin HTTPS, MD5 passwords)
- A03 Injection (SQL, command, XSS)
- A04 Insecure Design (workflow inseguros)
- A05 Security Misconfiguration (stack traces, CORS *, defaults)
- A06 Vulnerable Components (deps con CVEs)
- A07 Auth Failures (no rate limit, weak passwords)
- A08 Integrity Failures (deps sin verificar, deserialization)
- A09 Logging Failures (no detectas ataques)
- A10 SSRF (server hace requests por ti)

Si no puedes → relee.

---

## Conexiones

- [[01-tls-handshake-detallado]] — A02 Cryptographic Failures
- [[02-hashing-vs-cifrado]] — passwords y crypto
- [[04-jwt-y-session-management]] — A07 Auth
- [[../04_system_design_patterns/05-rate-limiting]] — A07 mitigation
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **OWASP Top 10 official** (owasp.org/Top10) — la referencia.
- **OWASP Cheatsheets** (cheatsheetseries.owasp.org) — práctico.
- **The Web Application Hacker's Handbook** — clásico de pentesting.
- **PortSwigger Web Security Academy** (portswigger.net/web-security) — gratis, brillante, hands-on.
- **OWASP ZAP** — scanner automatizado.
- **Burp Suite** (community edition free) — el toolset estándar.
- **`pip-audit`, `npm audit`, `Trivy`** — dependency scanning.
