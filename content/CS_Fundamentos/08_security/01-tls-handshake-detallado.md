# 01 — TLS handshake detallado

> 📚 **Doc 1 del cluster Security**. La versión profunda del TLS handshake. Qué pasa exactamente paso a paso, las matemáticas detrás, por qué TLS 1.3 es más seguro y rápido.
> 🔥 **Frecuencia interview**: aparece en preguntas de seguridad senior, infraestructura, compliance.
> ⏱️ **Tiempo de lectura estimado**: 40-55 min.

> 💡 Este doc complementa [[../01_networking/05-tls-https]] que da el overview. Aquí entramos en el "cómo" matemático.

---

## 1. Por qué TLS 1.3 es notable

TLS 1.3 (RFC 8446, 2018) es **el primer rediseño mayor desde 1995**. Comparado con TLS 1.2:

- **Más rápido**: 1 RTT (round-trip) vs 2 RTT del 1.2. 0-RTT en reconexiones.
- **Más seguro**: elimina algoritmos viejos (RC4, MD5, SHA-1, RSA key exchange sin forward secrecy).
- **Más simple**: la spec es más corta. Menos opciones = menos bugs.
- **Mandatory forward secrecy**: cada conexión usa claves efímeras únicas.

Después de Heartbleed, POODLE, BEAST, FREAK, Logjam (todos atacks contra versiones viejas TLS), la industria apretó. TLS 1.3 es el resultado.

**Hoy (2026)**: 80%+ del tráfico web usa TLS 1.3. Las versiones 1.0, 1.1 están deprecated. 1.2 sigue usándose pero degradado.

---

## 2. Recordatorio rápido — los problemas que TLS resuelve

TLS provee 3 garantías sobre comunicación entre cliente y servidor:

1. **Confidencialidad**: terceros no pueden leer (cifrado).
2. **Integridad**: terceros no pueden modificar sin detectarse (MAC).
3. **Autenticación**: confirmas que el server ES quien dice ser (certificados).

Cada parte del handshake implementa una de estas. La belleza de TLS 1.3 es que lo hace en **un solo round-trip** combinando las primitivas eficientemente.

---

## 3. Las primitivas criptográficas que usa

### Cifrado simétrico (AEAD)

TLS 1.3 usa solo cifrados **AEAD** (Authenticated Encryption with Associated Data). Esto significa que **cifrado e integridad son una sola primitiva** — no se pueden separar (evita bugs históricos donde alguien implementaba uno sin otro).

Cipher suites soportadas en TLS 1.3:
- **AES-128-GCM** y **AES-256-GCM** — el default en hardware con AES-NI (Intel/AMD/ARM modernos).
- **ChaCha20-Poly1305** — alternativa para CPUs sin AES hardware (móviles low-end, ARM antiguos).
- **AES-128-CCM** y **AES-128-CCM-8** — para constrained devices (IoT).

Solo 5 cipher suites posibles. Comparado con TLS 1.2 que tenía cientos (muchas inseguras), simplificación brutal.

### Key exchange — ECDHE only

TLS 1.3 **eliminó** RSA key exchange (que no daba forward secrecy). Solo permite:

- **ECDHE** (Elliptic Curve Diffie-Hellman Ephemeral) — la opción por defecto.
- **DHE** (Diffie-Hellman Ephemeral con grupos finitos) — alternativa.

"Ephemeral" significa que la clave se genera nueva en cada handshake. Esto da **forward secrecy**: si en el futuro alguien roba la clave privada del server, NO puede descifrar conversaciones pasadas (porque las claves de sesión eran efímeras y ya no existen).

Curvas soportadas: **X25519** (la moderna, más rápida), P-256, P-384, P-521.

### Firma digital

Para autenticar al server (probar que tiene la clave privada del cert), TLS 1.3 usa firmas:

- **ECDSA** con curvas P-256/P-384/P-521.
- **RSA-PSS** (RSA con padding moderno).
- **EdDSA** con Ed25519 (la opción más moderna).

### Hash

Para integridad y derivación de claves: **SHA-256** y **SHA-384**. SHA-1 está deprecated en TLS 1.3.

### Key derivation function (KDF)

**HKDF** (HMAC-based KDF). Deriva múltiples claves a partir del secret compartido (claves para cifrado, IVs, MAC keys, etc.).

---

## 4. El handshake paso a paso (TLS 1.3)

### Antes del handshake — supuestos

- Cliente tiene la lista de root CAs en los que confía (~150 hardcoded en el OS/browser).
- Server tiene su certificate (firmado por CA en la chain de trust del cliente) y su clave privada.
- Cliente ya hizo DNS lookup del dominio y abrió conexión TCP al server.

### Mensaje 1 — ClientHello

El cliente envía el primer mensaje:

```
ClientHello {
    legacy_version: TLS 1.2,           // por compatibilidad
    random: <32 bytes random>,          // entropía
    cipher_suites: [...]                // qué algoritmos soporto
    extensions: {
        supported_versions: [TLS 1.3],  // realmente quiero 1.3
        supported_groups: [X25519, P-256, ...],
        key_share: {                     // ya envío mi pubkey ECDHE!
            X25519: <my ECDHE public key>
        },
        server_name: "google.com",       // SNI
        signature_algorithms: [ECDSA_SECP256R1_SHA256, ...],
        ...
    }
}
```

Notable:
- **`supported_versions: [TLS 1.3]`** porque el campo `legacy_version` es siempre TLS 1.2 por compatibilidad con middleboxes viejos.
- **`key_share: {X25519: <pubkey>}`**: el cliente YA envía su clave pública ECDHE en el primer mensaje. Esto es lo que ahorra un RTT vs TLS 1.2.

### Mensaje 2 — ServerHello + EncryptedExtensions + Certificate + Finished

El server responde con un solo round-trip que incluye múltiples mensajes encadenados:

```
ServerHello {
    random: <32 bytes random>,
    cipher_suite: TLS_AES_128_GCM_SHA256,  // elegí este
    extensions: {
        supported_versions: TLS 1.3,
        key_share: {                        // mi pubkey ECDHE
            X25519: <my ECDHE public key>
        }
    }
}

// A partir de aquí, todo cifrado con la clave derivada de ECDHE

EncryptedExtensions {
    ...                                    // extensiones que no van en plaintext
}

Certificate {
    cert_chain: [server_cert, intermediate_ca_cert, ...]
}

CertificateVerify {
    signature: <signature of transcript with server's private key>
    // Esto demuestra que el server TIENE la clave privada del cert
}

Finished {
    verify_data: <HMAC of all handshake messages so far>
    // Garantiza integridad del handshake completo
}
```

**Después del ServerHello**, ambas partes pueden calcular la clave compartida ECDHE (los dos tienen la otra pubkey + su propia privkey). De ahí derivan claves de sesión via HKDF.

**El resto del Mensaje 2 va cifrado** con esas claves derivadas. Esto es nuevo en TLS 1.3 — antes el certificado iba en claro.

### Mensaje 3 — Cliente verifica + Finished

El cliente recibe Mensaje 2 y hace:

1. **Verifica el certificate chain** contra sus root CAs.
2. **Verifica CertificateVerify**: usa la pubkey del cert para descifrar la firma. Si match con el hash del transcript → el server SÍ tiene la privkey correspondiente al cert.
3. **Verifica Finished**: el HMAC matches → el handshake no fue manipulado en el camino.

Si todo OK, cliente envía:

```
Finished {
    verify_data: <HMAC of transcript with client's view>
}
```

A partir de aquí, **Application Data cifrada fluye libremente**.

### Resumen visual

```
Cliente                                    Server
  |                                          |
  | ----- ClientHello + key_share ---------> |
  |                                          |
  | <---- ServerHello + key_share ---------- |
  | <---- {EncryptedExtensions} ------------ |  (cifrado)
  | <---- {Certificate} -------------------- |  (cifrado)
  | <---- {CertificateVerify} -------------- |  (cifrado)
  | <---- {Finished} ----------------------- |  (cifrado)
  |                                          |
  | ----- {Finished} ----------------------> |  (cifrado)
  |                                          |
  | <==== Application Data (cifrada) ======> |
  |                                          |

Total: 1 RTT antes de poder enviar Application Data.
```

---

## 5. ECDHE matemáticamente (versión simplificada)

ECDHE = Diffie-Hellman sobre curvas elípticas.

**Setup**: ambas partes acuerdan una curva elíptica (e.g. X25519) con un punto base G.

**Cliente**:
- Genera privkey aleatoria `a` (256 bits).
- Calcula pubkey `A = a · G` (multiplicación escalar de punto en curva).
- Envía `A` al server.

**Server**:
- Genera privkey aleatoria `b`.
- Calcula pubkey `B = b · G`.
- Envía `B` al cliente.

**Ambos calculan secret compartido**:
- Cliente: `S = a · B = a · b · G`.
- Server: `S = b · A = b · a · G = a · b · G`.
- **Mismo `S`**, calculado por ambos sin haberlo enviado por el cable.

**Por qué es seguro**: dado `A` y `B` (públicos), un atacante no puede calcular `S` sin conocer `a` o `b`. Es el problema "Discrete Log Problem en Curvas Elípticas" (ECDLP), considerado computacionalmente intratable.

---

## 6. 0-RTT — la optimización para reconexiones

Si el cliente ya hizo handshake con el server antes (en una sesión reciente), TLS 1.3 permite **enviar application data en el primer mensaje**, sin esperar al ServerHello.

**Cómo**: durante la primera conexión, el server envió un **session ticket** (estado serializado + cifrado con clave que solo el server conoce). En reconexión, el cliente lo presenta. El server lo descifra y restaura el estado de sesión.

**Caveat**: 0-RTT data es **vulnerable a replay attacks**. Un atacante que capture los bytes 0-RTT puede reenviar y la operación se ejecutaría dos veces.

**Implicación**: 0-RTT solo para operaciones **idempotentes** (GET requests). Nunca para POST/PUT/DELETE.

Cloudflare, Google y otros usan 0-RTT en producción con esta restricción.

---

## 7. Certificate verification en detalle

Cuando el cliente verifica el cert que recibió:

### Paso 1: chain validation

El cliente sigue la chain: `server_cert ← intermediate_cert ← root_cert`.

Verifica para cada cert:
- La firma es válida (calculada por el issuer's privkey, verifica con su pubkey).
- No ha expirado (`Not After` field).
- El issuer del cert hijo es el subject del cert padre.
- El root final está en la trust store del cliente.

### Paso 2: hostname matching

El cert tiene un campo **Subject Alternative Names (SAN)** con la lista de dominios para los que vale. Cliente verifica que el hostname al que conectó (e.g. `google.com`) esté en SAN.

Wildcards: `*.google.com` cubre `mail.google.com` pero NO `google.com` mismo (ni `foo.bar.google.com`).

### Paso 3: revocation check (opcional)

Idealmente, el cliente verifica que el cert no esté revocado:
- **CRL** (Certificate Revocation List): listas distribuidas por las CAs. Lentas, viejas.
- **OCSP** (Online Certificate Status Protocol): cliente pregunta a la CA "¿está válido este cert?". Adds latency.
- **OCSP stapling**: el server incluye la respuesta OCSP firmada por la CA (válida horas/días). El cliente la verifica sin contactar la CA.

En la práctica, browsers modernos usan **soft-fail** (si no pueden verificar, asumen que vale). Esto es debate de seguridad.

**CRLite** (Mozilla) y **CRLSets** (Chrome) son enfoques modernos: listas comprimidas distribuidas con el browser.

### Paso 4: certificate transparency (CT)

Desde 2018, todos los certificados emitidos por CAs del CA/Browser Forum **deben aparecer en logs públicos** (CT logs). El cliente puede verificar que el cert que recibe está en logs.

**Por qué importa**: si una CA emite cert fraudulento (e.g. comprometida), aparecerá en CT logs y el dueño del dominio puede detectarlo. Sistema de "transparencia retroactiva".

---

## 8. Forward secrecy explicado

**Sin forward secrecy** (TLS 1.2 con RSA key exchange):
- La clave de sesión se cifra con la pubkey del cert y se envía.
- Si después roban la privkey del server, pueden descifrar **todas** las sesiones pasadas que capturaron.

**Con forward secrecy** (TLS 1.3 con ECDHE):
- Cada sesión genera claves efímeras (a, b en sección 5).
- Esas claves se borran de la RAM al cerrar la sesión.
- Si después roban la clave del cert, NO pueden descifrar sesiones pasadas (las claves efímeras ya no existen).

Forward secrecy es **propiedad de la sesión**, no del cert. Por eso TLS 1.3 lo hace mandatory.

---

## 9. mTLS — mutual authentication

Por defecto TLS autentica solo al **server** (el cliente verifica el cert del server). En **mTLS**, también el cliente tiene un cert y el server lo verifica.

**Cómo funciona**: en el handshake, el server pide `CertificateRequest`. El cliente envía su cert + CertificateVerify (firmado con su privkey).

**Casos de uso**:
- Microservicios internos (zero-trust networking).
- APIs B2B sensibles (cert client en lugar de API key).
- VPNs modernas (WireGuard usa concepto similar).
- IoT devices que se autentican al cloud con certs.

**Trade-off**: más complejo operativamente (gestión de certs cliente). Pero más seguro y revocable que API keys.

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Local: HTTP plano, sin TLS. Cuando despliegues a cloud:
- Caddy/Cloudflare maneja TLS automáticamente con Let's Encrypt.
- Internamente FastAPI sigue siendo HTTP. La terminación TLS está en el proxy.

### En entrevistas tecnicas

**Pregunta clásica**: "Explica TLS handshake".

Tu respuesta para 1.3:
1. Cliente envía ClientHello con su key share ECDHE.
2. Server responde con ServerHello + key share + cert + CertificateVerify + Finished (todo cifrado tras key derivation).
3. Cliente verifica cert chain + verify + Finished. Envía su Finished.
4. Application Data cifrada fluye. 1 RTT total.

**Pregunta sobre forward secrecy**: "Qué es y por qué importa".

Cada sesión usa claves efímeras. Si roban la privkey del cert mañana, NO pueden descifrar sesiones de hoy capturadas. Property of session, not cert. TLS 1.3 lo hace mandatory via ECDHE.

**Pregunta avanzada**: "Diferencia TLS 1.2 vs 1.3".

1.3 más rápido (1 RTT vs 2). Eliminó algoritmos vulnerables (RC4, MD5, SHA-1, RSA key exchange). Solo AEAD ciphers. Forward secrecy mandatory. Cert va cifrado. 0-RTT en reconexiones.

**Pregunta sobre cert verification**: "Qué pasos hace el browser para verificar un cert".

Chain validation (firmas + dates + issuer match). Hostname matching contra SAN. Revocation check (OCSP, CRL). Certificate transparency log check.

---

## 11. Trampas típicas

**"TLS = HTTPS"**: HTTPS es HTTP sobre TLS. TLS también se usa para SMTP (STARTTLS), IMAP, gRPC, MQTT, etc.

**"TLS protege todo el tráfico"**: el SNI (Server Name Indication) va en plaintext en el ClientHello. ESNI/ECH lo cifran pero no es universal todavía.

**"Self-signed certs son válidos"**: técnicamente sí (el matemáticas funciona). Pero browsers/clientes los rechazan porque no están en su trust store. Solo OK para development local con `mkcert`.

**"Cert chain de 1 nivel basta"**: en producción, root CA NO firma directamente certs de servidores. Usa intermediate CAs (security: si comprometen una intermediate, no compromete el root).

**"OCSP siempre se verifica"**: muchos browsers usan soft-fail (si no responde OCSP, asume válido). Atacantes pueden bloquear OCSP queries para evitar detección.

**"0-RTT es siempre seguro"**: vulnerable a replay attacks. Solo para operaciones idempotentes.

**"Forward secrecy = no pueden romper TLS"**: protege contra robo FUTURO de privkey. NO contra ataque activo actual o quantum computers (PQC, post-quantum cryptography, es otra batalla).

---

## 12. Preguntas típicas de interview

**TLS 1.3 vs 1.2**: cubierto sección 11.

**Forward secrecy**: clave efímera por sesión. Roban privkey futura → no descifran pasado.

**Cert chain validation**: pasos sección 7.

**SNI**: cliente dice qué dominio en ClientHello. Permite varios sites en 1 IP. Va en plaintext.

**0-RTT trade-off**: más rápido pero replay attacks → solo para idempotent.

**mTLS — cuándo**: zero-trust microservices, B2B APIs sensibles, IoT.

**OCSP stapling**: server incluye respuesta OCSP en handshake. Cliente verifica sin contactar CA.

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- TLS 1.3 mejoras sobre 1.2 (1 RTT, mandatory FS, simplificación, AEAD only).
- ECDHE: cómo dos partes acuerdan secret sin enviarlo.
- 1-RTT handshake: ClientHello con key_share → ServerHello + cert → Finished bidireccional.
- Forward secrecy: claves efímeras por sesión.
- Cert verification: chain + hostname + revocation + CT.
- 0-RTT: rápido pero solo idempotent.
- mTLS: autenticación mutua.

Si no puedes → relee.

---

## Conexiones

- [[02-hashing-vs-cifrado]] — primitivas que TLS usa
- [[03-owasp-top-10]] — vulnerabilidades web
- [[04-jwt-y-session-management]] — auth post-handshake
- [[../01_networking/05-tls-https]] — overview, lectura previa
- [[../01_networking/02-http-y-evolucion]] — HTTPS = HTTP + TLS
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Bulletproof TLS and PKI** (Ivan Ristić, 2nd ed) — la biblia. Ya recomendada.
- **TLS 1.3 RFC 8446** — la fuente.
- **Cloudflare blog: TLS 1.3** — explicación accesible.
- **SSL Labs Test** (ssllabs.com/ssltest) — analiza tu config TLS.
- **`openssl s_client -connect google.com:443 -tls1_3`** — inspeccionar handshakes reales.
- **Wireshark** — capturar y desmenuzar handshakes.
- **High Performance Browser Networking** capítulo TLS — moderno, gratis online.
