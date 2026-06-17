# 05 — TLS y HTTPS

> **Doc 5 (último) del cluster Networking**. Cierra el ciclo: cómo se cifra todo el tráfico moderno.
> **Frecuencia interview**: aparece en system design (HTTPS, certificate pinning, MITM) y en preguntas de seguridad.
> **Tiempo de lectura estimado**: 45-65 min.

---

## 1. Por qué necesitamos TLS

**El problema sin TLS**: HTTP es texto plano. Cualquiera en el camino (ISP, hotel WiFi, gobierno, atacante en tu LAN) puede:

1. **Leer** tus datos (passwords, cookies, contenido).
2. **Modificar** los datos en tránsito.
3. **Suplantar** el server y hacerse pasar por google.com.

**Ejemplo histórico**: antes de HTTPS universal (~2015), iniciar sesión en cualquier web desde una WiFi pública = entregar tus credenciales al primer curioso con Wireshark.

**La solución es TLS**, que aporta tres garantías:
- **Confidencialidad** → terceros no pueden LEER (cifrado).
- **Integridad** → terceros no pueden MODIFICAR sin detectarse (MAC).
- **Autenticación** → confirmas que el server ES quien dice ser (certs).

**HTTPS = HTTP + TLS**. Es el mismo HTTP, encapsulado dentro de un canal TLS cifrado. Por eso 99% de lo que sabes de HTTP aplica igual a HTTPS.

---

## 2. Conceptos previos — criptografía mínima

### Cifrado simétrico

Misma clave para cifrar y descifrar. `texto + clave → algoritmo → texto cifrado`. Y `texto cifrado + MISMA clave → algoritmo → texto`.

**Ventaja**: muy rápido (AES en hardware = 10+ GB/s).
**Desventaja**: ¿cómo compartes la clave de forma segura primero?

**Algoritmos modernos**:
- **AES-256-GCM** — estándar actual, autenticado (cifrado + MAC).
- **ChaCha20-Poly1305** — alternativa, más rápido en CPUs sin AES hardware.

### Cifrado asimétrico (clave pública)

Dos claves: PÚBLICA (conocida por todos) y PRIVADA (solo tú la tienes). Lo cifrado con UNA clave solo se descifra con la OTRA.

**Uso 1 — confidencialidad**: Alice cifra con la PÚBLICA de Bob. Solo Bob puede descifrar (con su PRIVADA).

**Uso 2 — autenticación / firma**: Bob firma con su PRIVADA. Cualquiera con la PÚBLICA de Bob puede verificar que fue Bob.

**Ventaja**: resuelve el problema de compartir clave.
**Desventaja**: muy lento (1000x más lento que simétrico).

**Algoritmos**:
- **RSA** — clásico, claves 2048-4096 bits, lento.
- **ECDSA / Ed25519** — curvas elípticas, claves 256 bits, más rápido + seguro.

### Hashing

Función one-way: input → hash de tamaño fijo (e.g. 256 bits). NO se puede invertir (en teoría — fuerza bruta es la única vía).

**Usos**: integridad ("este mensaje no ha sido modificado"), firma digital (firmas el HASH del mensaje, no el mensaje entero), passwords (NUNCA guardas password, guardas hash).

**Algoritmos**:
- **SHA-256, SHA-512** — estándar moderno.
- **SHA-1, MD5** — DEPRECATED (rotos).
- **bcrypt, argon2** — para passwords (slow on purpose, anti-bruteforce).

### Diffie-Hellman key exchange

**El truco que lo resuelve todo**: dos partes pueden ACORDAR una clave compartida sin que pasen esa clave por el cable. Solo intercambian valores públicos (que un atacante puede ver) y derivan una clave compartida.

**Analogía del color**: Alice y Bob acuerdan un color público (amarillo). Alice mezcla amarillo + secreto (rojo) = naranja. Manda naranja. Bob mezcla amarillo + secreto (azul) = verde. Manda verde. Alice mezcla verde + su rojo = marrón. Bob mezcla naranja + su azul = marrón. **¡Mismo marrón!** Atacante vio amarillo, naranja, verde — pero no puede separar los componentes. Marrón es secreto compartido.

**En práctica**: ECDHE (Elliptic Curve Diffie-Hellman Ephemeral) — el moderno. "Ephemeral" = clave temporal por cada conexión. **Forward secrecy**: si te roban la clave de hoy, NO pueden descifrar conversaciones pasadas (porque eran con claves distintas).

---

## 3. Certificate chain — cómo confías en un server

**Problema**: cuando conectas a `google.com`, te mandan una clave pública. ¿Cómo sabes que es realmente Google y no un atacante con su propia clave?

**Solución**: **Public Key Infrastructure (PKI)** con **Certificate Authorities (CAs)**.

```
[Tu navegador / SO]
      │
      │ confía en lista hardcoded de ROOT CAs
      │ (Let's Encrypt, DigiCert, Sectigo, GlobalSign, ~150 CAs)
      ↓
[Root CA cert]              ← self-signed, máxima confianza
      │
      │ firma
      ↓
[Intermediate CA cert]      ← capa intermedia (seguridad operacional)
      │
      │ firma
      ↓
[Certificado de google.com] ← el que te manda google
```

### Qué contiene un certificado X.509

Un cert es un archivo (formato PEM o DER) que contiene:
- **Sujeto** (subject): `CN=google.com` (o wildcard `*.google.com`).
- **Issuer**: quién firmó este cert (la CA superior).
- **Clave pública**: la del server (la usas para cifrar).
- **Válido desde/hasta**: fechas (típicamente 90 días con Let's Encrypt).
- **Algoritmo de firma**: SHA-256 con RSA, ECDSA, etc.
- **Firma**: hash del cert firmado por el issuer.
- **SAN (Subject Alt Names)**: lista de dominios para los que vale el cert.
- **Extensiones**: usage permitido (server auth, client auth, etc.).

### Verificación paso a paso

Cuando tu browser recibe el cert de google.com:

1. **¿La firma del cert es válida?** Calcula hash del cert. Descifra la firma con clave pública del issuer. Compara. Si match → el issuer firmó este cert.
2. **¿El issuer es alguien en quien YO confío?** Recursivamente verifica el chain hasta llegar al root CA.
3. **¿El cert no ha expirado?** Comparar fechas. Si pasado → reject.
4. **¿El subject (o SAN) coincide con el dominio al que conecto?** Conecto a google.com → cert dice CN=google.com → OK. Conecto a hacker.com → cert dice CN=google.com → REJECT.
5. **¿El cert no está revocado?** CRL (Certificate Revocation List) o OCSP (Online Certificate Status Protocol). En la práctica esto es problemático (latencia, privacidad). Browsers modernos usan listas comprimidas (CRLite, CRLSets).

Si TODO pasa → estableces la conexión TLS confiando en que el server es legítimo.

---

## 4. TLS handshake (TLS 1.3) — paso a paso

TLS tuvo varias versiones. **TLS 1.3 (2018) es el moderno**. Más rápido, más seguro, menos complejidad. Lo que verás hoy.

```
CLIENTE                                              SERVIDOR
   │                                                    │
   │ ────────  ClientHello  ──────────────────────→     │
   │  - TLS version (1.3)                               │
   │  - Cipher suites soportadas                        │
   │  - Random bytes                                    │
   │  - Key share (ECDHE pubkey efímera)               │
   │  - SNI: "para qué dominio? google.com"            │
   │                                                    │
   │ ←─────── ServerHello + EncryptedExtensions ─────   │
   │  - TLS version aceptada                            │
   │  - Cipher suite elegida                            │
   │  - Random bytes                                    │
   │  - Key share (ECDHE pubkey efímera servidor)      │
   │  -- aquí ya pueden derivar clave compartida --    │
   │  - Certificate (firmado por CA)                    │
   │  - CertificateVerify (server demuestra que tiene  │
   │    la clave privada del cert)                     │
   │  - Finished                                        │
   │                                                    │
   │ ────────  Finished  ─────────────────────────→     │
   │                                                    │
   │ ════════  Application Data (cifrada AES)  ═══════  │
```

**Pasos en detalle**:

**Paso 1 — ClientHello**: cliente abre con: "hablo TLS 1.3, soporto estos algoritmos, aquí mi key share pública ECDHE, conecto a google.com (SNI)."

**Paso 2 — ServerHello**: server elige algoritmos del cliente. Manda su key share pública. Ahora ambos lados pueden DERIVAR la clave compartida (ECDHE magic). Server manda su CERTIFICATE para autenticarse. Server FIRMA un mensaje con su clave privada (CertificateVerify) para demostrar que la clave privada le pertenece (no solo tiene un cert que copió de internet).

**Paso 3 — Cliente verifica**:
- Firma del certificate chain (sección 3).
- CertificateVerify: descifra con la pubkey del cert. Si match → el server tiene la privada del cert. Es legítimo.
- Manda su Finished cifrado con la clave compartida.

**Paso 4 — Application Data**: a partir de aquí, todo va CIFRADO con AES-256-GCM (o ChaCha20). El cliente envía la HTTP request. Server responde.

**Latencia**: 1 RTT (round trip) en TLS 1.3. TLS 1.2 era 2 RTT — TLS 1.3 es notablemente más rápido.

**Extra: 0-RTT**: en reconexiones, TLS 1.3 puede mandar datos en el mismo paquete del ClientHello. 0 RTT extra. Pero hay caveat de replay attacks — solo para datos idempotentes.

---

## 5. SNI — Server Name Indication

**Problema histórico**: en 1 IP puedes alojar muchos dominios (virtual hosting). Pero TLS handshake empieza ANTES del HTTP request. Sin SNI, el server no sabe QUÉ certificate enviar (¿el de google.com? ¿el de gmail.com? Solo tiene 1 IP).

**Solución: SNI**. El cliente, en el ClientHello, dice "voy a hablar con google.com". El server elige el cert correcto.

**Caveat de privacidad**: SNI va EN PLANO en el ClientHello (no cifrado todavía). Cualquiera en el camino ve QUÉ dominios visitas, aunque el contenido esté cifrado.

**ESNI (Encrypted SNI)** y **ECH (Encrypted ClientHello)**: cifran el SNI también. Adopción reciente, no universal. Cloudflare lo lidera.

---

## 6. Let's Encrypt — democratizó HTTPS

Hasta 2016, conseguir un cert HTTPS:
- Costaba $50-500/año.
- Burocracia con CAs comerciales.
- Renovación manual.

**Let's Encrypt (2016)** cambió todo:
- **Gratis**.
- **Automático** vía protocolo ACME.
- **90 días de validez**, renovación automatizada.

**Flow ACME (simplificado)**:
1. Tu server pide cert para `example.com` a Let's Encrypt.
2. LE dice: "demuéstrame que controlas example.com".
3. Tu server prueba con CHALLENGE:
   - **HTTP-01**: pones un archivo en `http://example.com/.well-known/...`.
   - **DNS-01**: pones un TXT record en DNS.
   - **TLS-ALPN-01**: respondes en TLS con cert especial.
4. LE verifica.
5. Si OK, te emite el cert (válido 90 días).
6. Tu server (Caddy, certbot, traefik) renueva automático antes de expirar.

**Hoy**: 80%+ de la web usa HTTPS gracias a Let's Encrypt. Tools: Caddy (built-in, automático), Traefik (built-in), certbot (manual).

---

## 7. mTLS — mutual TLS

Por defecto TLS solo autentica al **server** (el cliente verifica el cert del server). En **mTLS**, también el cliente tiene un cert y el server lo verifica.

**Casos de uso**:
- Microservices internos (zero-trust): cada servicio tiene su cert, se autentican mutuamente. No basta con estar en la red privada.
- APIs B2B sensibles: cliente debe presentar cert (no solo API key).
- VPN modernas (WireGuard usa concepto similar).

**Alternativa a username/password**: en vez de tokens/passwords, usas certs. Más seguro y revocable. Pero más complejo de operar (gestión de certs cliente).

---

## 8. Certificate pinning

**Problema**: si una CA es comprometida (DigiNotar 2011), un atacante puede emitir cert válido para cualquier dominio. Tu navegador lo aceptaría.

**Solución: pinning**. Tu app (típicamente mobile) hardcodea la huella esperada del cert o la clave pública del server. Si recibe un cert distinto (aunque firmado por CA válida), REJECT.

**Dónde se usa**:
- Apps bancarias mobile.
- Apps con datos sensibles.
- Algunos browsers para sitios críticos (Chrome HSTS+pinning para google.com históricamente).

**Caveat**: si pierdes el control de la clave pinneada, te quedas sin acceso. Por eso se pinea con expiraciones cortas y backup keys.

---

## 9. HSTS — Strict Transport Security

**Problema**: usuario teclea "google.com" sin `https://`. Browser conecta primero por HTTP plano. Atacante MITM intercepta y nunca redirige a HTTPS. Usuario no sabe.

**Solución: HSTS**. Servidor manda header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`. Browser recuerda: "siempre HTTPS para este dominio durante 1 año". Próxima vez que teclees el dominio, browser va directo a HTTPS sin probar HTTP.

**HSTS preload**: lista hardcoded en el browser de dominios que SIEMPRE son HTTPS. google.com, wikipedia.org, gmail.com están preloaded. Tú puedes añadir tu dominio en hstspreload.org.

---

## 10. Aplicación al perfil del usuario

### En el Phone Book FastAPI

- En **local**, usas `http://localhost:8000` — sin TLS, no necesario.
- Cuando hagas T1.4 (deploy a Fly.io / Cloud Run), automáticamente tendrás HTTPS:
  - Fly.io: emite cert automático con Let's Encrypt.
  - Cloud Run: gestionado por Google.
  - Caddy si self-host: built-in Let's Encrypt automático.
- Reverse proxy (Caddy/nginx/Traefik) maneja TLS, tu FastAPI sigue siendo HTTP plano internamente.

### En entrevistas tecnicas

**Pregunta**: "Explica HTTPS"

**Respuesta**: HTTP encapsulado en TLS. TLS provee confidencialidad (cifrado), integridad (MAC) y autenticación (certs). Handshake típico TLS 1.3 es 1 RTT. Cliente envía ClientHello con cipher suites + key share ECDHE. Server responde con su cert + key share. Ambos derivan clave compartida sin pasarla por el cable (Diffie-Hellman). Cert se valida contra CA chain de confianza. A partir de ahí, todo cifrado simétrico (AES o ChaCha20).

**Pregunta**: "¿Cómo verifica tu navegador que google.com es realmente Google?"

**Respuesta**: cert chain. Google manda su cert firmado por intermediate CA, firmado por root CA. Mi browser tiene los root CAs hardcoded. Verifica firmas recursivamente. También verifica que CN/SAN del cert coincide con el dominio, que no ha expirado, y que no está revocado.

**Pregunta**: "¿Qué es forward secrecy?"

**Respuesta**: si un atacante captura tráfico TLS hoy y mañana le roban la clave privada del server, NO puede descifrar el tráfico capturado. Porque las claves de sesión son efímeras (ECDHE) y no derivan de la clave del cert.

### Por qué importa para tu carrera

Cuando hagas tu CV con `https://miembebido.app`, debes saber por qué hay HTTPS y cómo se obtiene. Es el CV de un.

---

## 11. Trampas típicas

**"HTTPS protege los HEADERS y la URL completa"**: sí Y no. La URL path + query parameters ESTÁN cifrados (van en HTTP body). Pero el DOMAIN va en SNI EN PLANO en el ClientHello. Y el DNS lookup previo también va en plano (a menos que DoH/DoT).

**"TLS y SSL son lo mismo"**: históricamente SSL fue el predecesor (SSL 1, 2, 3). TLS es la evolución (TLS 1.0, 1.1, 1.2, 1.3). Mucha gente dice "SSL" coloquialmente refiriéndose a TLS. Técnicamente SSL está deprecated desde 2015.

**"Renovar certs es manual"**: era cierto antes de Let's Encrypt. Hoy es automático con cualquier tool moderna (Caddy, certbot). Si tu cert expiró, problema operacional.

**"HTTPS hace tu API más lenta"**: sí, hay handshake (1 RTT en TLS 1.3, antes 2 RTT en TLS 1.2). Pero el cifrado simétrico AES en hardware moderno es prácticamente gratis. Y connection pooling reusa la conexión TLS. En la práctica, la diferencia es <1% para APIs reales. El argumento "performance" contra HTTPS es de hace 10 años.

**"El cert protege mi server"**: el cert AUTENTICA tu server al cliente. NO protege contra ataques AL server (DDoS, exploits). Para eso necesitas firewall, WAF, rate limiting.

**"Wildcard cert *.example.com cubre example.com"**: NO. `*.example.com` cubre subdominios (a.example.com, b.example.com). No cubre example.com directo (apex). Necesitas SAN extra para eso.

**"Self-signed cert es mejor que nada"**: para producción NO — los browsers lo rechazan, los usuarios ven warning aterrador. Para development local SÍ — `mkcert` te genera certs trusted localmente. Para producción siempre Let's Encrypt o CA comercial.

---

## 12. Cosas típicas que preguntan en interview

**"Explica el TLS handshake"** — sección 4 de este doc. Mencionar 1 RTT, ECDHE, cert chain, Finished.

**"Diferencia entre cifrado simétrico y asimétrico"** — simétrico: misma clave (rápido, problema de compartir). Asimétrico: pubkey/privkey (lento, resuelve compartir). TLS usa AMBOS: asimétrico para acordar clave + autenticar, simétrico para cifrar el grueso de datos.

**"¿Por qué hay CAs?"** — para escalar la confianza. Sin CAs, cada server tendría que conocerse con cada cliente previamente. Con CAs, cada cliente confía en ~150 CAs raíz, y eso le da confianza en millones de servers transitivamente.

**"¿Qué pasa si la clave privada del server se filtra?"** — atacante puede suplantar el server. Si NO había forward secrecy, también puede descifrar tráfico pasado. Acciones: revocar el cert (CRL/OCSP), emitir nuevo cert con nueva clave, rotar todos los secrets que pudieron pasar por esa conexión.

**"¿Por qué Let's Encrypt es gratis?"** — patrocinado por Linux Foundation, EFF, Mozilla, etc. Su misión es HTTPS universal. Costes operativos cubiertos por sponsors. Modelo: la web es más segura para todos.

**"¿Cómo prevendrías MITM en una app móvil?"** — HTTPS obligatorio (no permitir HTTP fallback). Certificate pinning (hardcodear hash del cert esperado). HSTS si aplica. mTLS para APIs internas.

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué TLS existe (3 propiedades: confidencialidad, integridad, autenticación).
- Diferencia entre cifrado simétrico, asimétrico y hashing.
- Por qué TLS usa ambos (asimétrico para handshake, simétrico para datos).
- Diffie-Hellman: cómo se acuerda clave sin compartirla.
- Cert chain y verificación (firma + chain + dates + name + revocation).
- TLS 1.3 handshake en 1 RTT (ClientHello → ServerHello → Finished → Data).
- SNI: para qué sirve y por qué importa privacidad.
- Let's Encrypt + ACME: cómo se obtiene cert automático.
- Forward secrecy: qué es y por qué importa.
- mTLS, HSTS, certificate pinning: cuándo usar cada uno.

Si no puedes → relee la sección.

---

## ¡Cluster Networking completado!

Has terminado los 5 docs de Networking. Resumen de lo que ahora dominas:

- **`01-tcp-ip-osi`** — modelo en capas, encapsulación, three-way handshake.
- **`02-http-y-evolucion`** — HTTP 1.1/2/3, métodos, status codes, headers, CORS.
- **`03-dns-resolucion`** — resolución jerárquica, TTL, caches, DoH.
- **`04-sockets-y-puertos`** — API socket, lifecycle, I/O models, port exhaustion.
- **`05-tls-https`** — cifrado, certs, handshake TLS 1.3, Let's Encrypt.

**Próximo cluster sugerido**: `02_operating_systems/` (procesos, threads, memoria, scheduling). Es el segundo Tier 1 más urgente.

**Repaso recomendado**: vuelve a leer cada doc 2-3 días después de la primera lectura. Active recall: intenta explicar las secciones de "Resumen mental" sin mirar.

---

## Conexiones

- [[01-tcp-ip-osi]] — TLS corre sobre TCP
- [[02-http-y-evolucion]] — HTTPS = HTTP + TLS
- [[03-dns-resolucion-nombres]] — DNS valida indirectamente lo que TLS protege
- [[04-sockets-y-puertos]] — TLS añade capa encima del socket TCP
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]
- — HTTPS en producción con reverse proxy
- [[../08_security/01-tls-handshake-detallado]] — versión más profunda con math
- [[../08_security/02-hashing-vs-cifrado]] — algoritmos en detalle

## Recursos externos

- **Bulletproof TLS and PKI** (Ivan Ristić, 2nd ed) — la biblia moderna de TLS, denso pero excelente.
- **High Performance Browser Networking** capítulo TLS (hpbn.co — gratis online).
- **TLS 1.3 RFC 8446** (rfc-editor.org) — la fuente, denso.
- **Cloudflare Learning Center SSL/TLS** (cloudflare.com/learning/ssl/) — buen intro visual.
- **SSL Labs Test** (ssllabs.com/ssltest/) — analiza la config TLS de cualquier server público.
- **`openssl s_client -connect google.com:443`** — inspeccionar TLS desde CLI.
- **mkcert** — generar certs trusted para development local.
- **Cómo funciona HTTPS** (howhttps.works) — visual interactivo, recomendado.
