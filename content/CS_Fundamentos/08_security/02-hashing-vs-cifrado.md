# 02 — Hashing vs cifrado

> **Doc 2 del cluster Security**. Las dos primitivas criptográficas más confundidas. Esenciales para passwords, tokens, integridad, transmisión segura.
> **Frecuencia interview**: aparece siempre. "Cómo guardas passwords", "diferencia hash vs encrypt", "qué es bcrypt".
> **Tiempo de lectura estimado**: 35-50 min.

---

## 1. La diferencia fundamental

Confusión #1 en seguridad: tratar hashing y cifrado como sinónimos. Son **completamente distintos**:

**Hashing**: función **one-way**. Input → fingerprint de tamaño fijo. **NO se puede invertir**. Si hasheas "password" no puedes recuperar "password" del hash.

**Cifrado**: función **two-way**. Input + key → ciphertext. **Se puede invertir** con la key correcta. Si ciframos "secret" con key K, podemos descifrar con K para recuperar "secret".

**Cuándo cada uno**:
- Hashing: para **verificar** algo sin guardarlo (passwords) o para **identificar** integridad (checksums, signatures).
- Cifrado: para **proteger en tránsito o reposo** algo que después necesitas leer.

Si alguien te dice "cifré los passwords con SHA-256", está usando lenguaje técnicamente incorrecto. Hash y encrypt son cosas distintas.

---

## 2. Hashing — propiedades

Una función hash criptográfica `H(x)` debe cumplir:

1. **Determinista**: misma input → mismo output, siempre.
2. **Tamaño fijo**: el output siempre tiene el mismo tamaño (e.g. SHA-256 → 256 bits = 32 bytes).
3. **Rápida**: calcular `H(x)` debe ser barato.
4. **Pre-image resistant**: dado `H(x)`, computacionalmente infeasible encontrar `x`.
5. **Second pre-image resistant**: dado `x`, infeasible encontrar `x'` distinto con `H(x) = H(x')`.
6. **Collision resistant**: infeasible encontrar dos inputs distintos con mismo hash.

Las propiedades 4-6 son las que la hacen "criptográfica". Una función hash sin estas (e.g. CRC32) sirve para detectar errores accidentales pero no para seguridad.

---

## 3. Algoritmos de hash modernos

### SHA-256 / SHA-512

**SHA-2 family**. Estándar actual para integridad y signatures. Usado en HTTPS, blockchain (Bitcoin), git, package managers.

- **SHA-256**: 256-bit output. El más común.
- **SHA-512**: 512-bit. Marginal más seguro, más rápido en CPUs 64-bit.

Sin vulnerabilidades prácticas conocidas.

### SHA-3 / Keccak

**Estándar más reciente** (2015). Diseño matemáticamente distinto a SHA-2 (sponge construction). Pensado como respaldo si SHA-2 fuera roto.

En la práctica, SHA-2 sigue siendo la elección por defecto. SHA-3 se usa en algunos contextos específicos.

### Algoritmos deprecated — NO usar

- **MD5**: roto desde 2004. Colisiones triviales. Solo OK para checksums de integridad NO adversarial.
- **SHA-1**: roto desde 2017 (Google demostró colisión). Aún usado en git por inercia (transición a SHA-256 en curso).

**Si ves MD5 o SHA-1 para seguridad en código nuevo, es bug**.

### BLAKE2 / BLAKE3

**Hashes modernos optimizados para velocidad** sin sacrificar seguridad. Más rápidos que SHA-256.

BLAKE3 es ridículamente rápido (~6 GB/s en CPU moderna). Usado en sistemas que necesitan hashear grandes volúmenes (filesystems, dedup).

---

## 4. Hashing para passwords — caso especial CRÍTICO

**Para passwords NO usar SHA-256 directamente**. Razón: SHA-256 es **rápido**, lo que es bueno para integridad pero MALO para passwords.

**Por qué**: si atacante roba tu DB de hashes, puede probar billones de passwords/segundo en GPUs. Diccionarios + rainbow tables crackean passwords débiles en segundos.

**La solución**: funciones **diseñadas para ser lentas** y resistentes a hardware especializado.

### bcrypt

Diseñado en 1999. Aún el estándar más usado.

- **Adaptive cost**: parámetro `cost` (típico 10-12) ajusta la lentitud. Subes cost cuando hardware mejora.
- Cada hash es **único** porque incluye un **salt** aleatorio.
- Output incluye el salt y el cost embebidos.

Ejemplo de hash bcrypt:
```
$2b$12$LrI8VLfKxqjcnkV1nYXyZeA8KwlF4mXcUjNzL4.kjqQLGu7N.OwEC
└┬┘ └┬┘ └────────────────────┬────────────────────┘└──────────────┘
algo cost          salt (22 chars)              hash
```

Pros: probado, ubicuo, soporte universal.
Contras: limitado a 72 bytes de input. No usa mucha RAM (vulnerable a hardware especializado moderno).

### Argon2

**Ganador de la Password Hashing Competition (2015)**. El estándar moderno para nuevos sistemas.

- Variantes: Argon2i (resistente a side-channel), Argon2d (más rápido), **Argon2id** (híbrido, recomendado).
- Configurable en 3 dimensiones: time cost, memory cost, parallelism.
- **Memory-hard**: usa MUCHA RAM. Esto frena ataques con GPU/FPGA/ASIC (que tienen poca memoria por unidad).

Ejemplo:
```
$argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>
```

m=65536 KB = 64 MB de RAM por hash. Hace que crackear sea mucho más caro que bcrypt.

**Recomendación 2026**: Argon2id para nuevos sistemas. bcrypt si necesitas compat con sistemas viejos.

### scrypt

Otro memory-hard hash. Bueno pero menos adoptado que Argon2.

### PBKDF2

Más viejo (2000). Solo CPU-hard, no memory-hard. Aceptable pero inferior a bcrypt/Argon2 hoy. Usado por estándar para FIPS compliance.

### NUNCA usar para passwords

- MD5, SHA-1, SHA-256, SHA-3 directamente. Demasiado rápidos.
- Hashing custom "casero". Casi seguro tiene bugs.

---

## 5. Salt — el ingrediente crítico

Sin salt: dos usuarios con misma password tienen mismo hash. Atacante con rainbow tables (precomputadas) las crackea instantáneamente.

**Salt** = string aleatorio único por usuario, mezclado con la password antes de hashear.

```
hash_storage = hash(password + salt)
```

bcrypt y Argon2 manejan el salt automáticamente. Solo asegúrate de NO usar el mismo salt para todos (sería como no tener salt).

**Salt debe ser**:
- Único por usuario.
- Aleatorio (no predecible).
- Suficientemente largo (16+ bytes).
- Almacenado junto al hash (es OK que sea visible, no es secreto).

---

## 6. Pepper — añadiendo otra capa

**Pepper** = secret estático añadido a todas las passwords antes de hashear, **no almacenado en la DB**.

```
hash_storage = hash(password + salt + pepper)
```

Pepper se guarda en config del server (no en DB). Si atacante roba la DB pero NO el server, no puede crackear hashes (le falta el pepper).

Pepper es **defensa en profundidad** opcional. Implementaciones:
- **Pre-hash con HMAC**: `hash(HMAC(password, pepper) + salt)`.
- **Pepper como parte del salt**: gestión más simple.

No reemplaza a salt. **Suma**.

---

## 7. Cifrado simétrico

**Misma key para cifrar y descifrar**. Rápido y eficiente.

### AES — el estándar

**AES (Advanced Encryption Standard)** es prácticamente el único cifrado simétrico que necesitas conocer.

- **AES-128**: clave de 128 bits. Suficiente para todo lo que harás en tu vida.
- **AES-256**: clave de 256 bits. Marginal más seguro, marginalmente más lento.

Hardware moderno (Intel/AMD AES-NI, ARM Crypto Extensions) acelera AES masivamente. ~10 GB/s.

### Modos de operación — críticos

AES per se solo cifra **bloques de 128 bits**. Para mensajes más largos, hay que combinarlos en un "modo":

- **ECB (Electronic Codebook)**: cifra cada bloque independientemente. **NUNCA usar**: bloques iguales → ciphertext igual → patrones visibles.
- **CBC (Cipher Block Chaining)**: cada bloque XOR con el anterior. Mejor pero secuencial (no paralelizable).
- **CTR (Counter)**: convierte AES en stream cipher. Paralelizable.
- **GCM (Galois/Counter Mode)**: CTR + autenticación (AEAD). **El default moderno**.

### AEAD — el modo correcto moderno

**AEAD (Authenticated Encryption with Associated Data)** combina cifrado e integridad en una primitiva. Si el ciphertext se modifica, el descifrado falla.

Sin AEAD: cifras con AES-CBC, calculas HMAC separado para integridad. Fácil de implementar mal (orden importa, padding oracle attacks).

Con AEAD: una sola primitiva hace ambas cosas. **Imposible** olvidarse de uno o hacer mal el orden.

Modos AEAD:
- **AES-GCM**: el más usado. Hardware-accelerated.
- **ChaCha20-Poly1305**: alternativa más rápida en CPUs sin AES-NI.
- **AES-CCM**: usado en IoT (Bluetooth, ZigBee).

**Recomendación**: AES-GCM para todo cifrado simétrico moderno.

---

## 8. Cifrado asimétrico (clave pública)

**Dos claves**: pública (compartes) y privada (guardas). Lo cifrado con una solo se descifra con la otra.

**Operaciones**:
- **Cifrar para X**: usar la pubkey de X. Solo X (con su privkey) puede descifrar.
- **Firmar como X**: usar la privkey de X. Cualquiera con la pubkey puede verificar que fue X.

### Algoritmos

- **RSA**: el clásico. Claves de 2048-4096 bits. Lento pero universal.
- **ECC (Elliptic Curve Cryptography)**: más eficiente. Claves de 256 bits dan equivalente seguridad a RSA-3072. Variantes: ECDSA (firma), ECDH (key exchange), Ed25519 (firmas modernas).

**Recomendación 2026**:
- Firmas: **Ed25519** (el más moderno y rápido).
- Key exchange: **X25519** (idem).
- Si necesitas RSA por compat: 2048+ bits.

### Trade-off vs simétrico

Asimétrico es **mucho más lento** que simétrico (1000x). Por eso casi nunca se usa para grandes volúmenes de data.

**Patrón típico (TLS, PGP, etc.)**: asimétrico para acordar una key simétrica + simétrico para cifrar el contenido real.

---

## 9. Aplicaciones reales

### Passwords

`bcrypt(password + salt, cost=12)` o `argon2id(password, salt)`. Almacenar el resultado.

Verificar: `verify(password, stored_hash)`.

```python
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
# almacenar hashed

# verificar
if bcrypt.checkpw(provided_password.encode(), hashed):
    # ok
```

### API tokens / session IDs

Generar token aleatorio (e.g. 32 bytes random hex) y guardar **hash** del token en DB. Cuando el cliente lo presenta, hasheamos y comparamos. Si la DB es robada, los tokens no pueden ser usados directamente.

### File integrity (checksums)

`SHA-256(file)` para verificar que un descarga no fue corrompida. Si el sitio publica el hash y tú descargas + hasheas → si match, file íntegro.

### Digital signatures

Firmar = hash + cifrar el hash con tu privkey. Verificar = descifrar la firma con tu pubkey y comparar con hash recalculado.

Usado en: certificados (X.509), software signing (apt, npm), git commits firmados, JWT con RS256.

### Cifrado de datos en reposo (DB columns sensibles)

`AES-GCM(data, key, nonce)`. Key gestionada con KMS (AWS KMS, Google Cloud KMS, HashiCorp Vault).

Patrón típico: **envelope encryption**. Generas data key aleatoria por record, cifras data con data key, cifras data key con master key del KMS. Almacenas data cifrada + data key cifrada.

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Si añades auth (T1.2 build): bcrypt o Argon2 para passwords. JWT con HS256 o RS256 para tokens (ver doc 04).

Si almacenas info sensible (PINs, etc.): AES-GCM con key del KMS.

### En entrevistas tecnicas

**Pregunta clásica**: "Cómo guardas passwords".

bcrypt o Argon2id con salt único por usuario. Cost ajustado para tomar ~100ms por hash. Nunca SHA-256 directamente (demasiado rápido). Considerar pepper en config.

**Pregunta sobre diferencia**: "Hash vs encrypt".

Hash: one-way, fingerprint, NO reversible. Para passwords, integridad, identifiers.
Encrypt: two-way con key, REVERSIBLE. Para proteger datos en tránsito/reposo.

**Pregunta avanzada**: "Diseña sistema de password reset seguro".

1. Usuario pide reset.
2. Server genera token random (32 bytes).
3. Almacena hash(token) + expiry timestamp en DB.
4. Envía email con link conteniendo el token plano.
5. Usuario clicka, server hashea token y compara con DB.
6. Si match y no expiró, permite resetear password.
7. Invalida el token (one-shot).

**Pregunta sobre AEAD**: "Por qué GCM y no CBC".

GCM combina cifrado + auth en una primitiva (AEAD). CBC requiere HMAC separado. Orden importa (encrypt-then-MAC). GCM es paralelizable y hardware-accelerated.

---

## 11. Trampas típicas

**"Hashing protege passwords"**: solo si usas bcrypt/Argon2 con salt. SHA-256 directo NO. Crackeable en GPU rápidamente.

**"AES-256 es 2x más seguro que AES-128"**: NO. AES-128 es seguro contra todo lo conocido. AES-256 es marginalmente más resistente teóricamente. La elección suele ser por compliance, no seguridad real.

**"Implementaré mi propio cifrado"**: ABSOLUTO NO. Ni siquiera expertos. Usa librerías validadas (libsodium, cryptography Python, BoringSSL). DIY crypto es cómo se hacen sistemas inseguros.

**"MD5/SHA-1 sirven para passwords si añado salt"**: NO. Demasiado rápidos. GPUs los crackean masivamente.

**"Encrypto con key embebida en el código"**: SI alguien obtiene el binario, encuentra la key. Keys deben venir de KMS o env vars (con KMS detrás).

**"Salt debe ser secreto"**: NO. Salt va junto al hash, es público. Solo necesita ser único y aleatorio.

**"ECB mode es OK para datos pequeños"**: NO. ECB filtra patrones. Imagen de pingüino cifrada con ECB se sigue viendo. Nunca.

**"HTTPS me protege todo"**: HTTPS protege en tránsito. Datos en disco siguen sin cifrar a menos que cifres at-rest también.

---

## 12. Preguntas típicas de interview

**Hash vs encrypt**: cubierto sección 1.

**Cómo guardar passwords**: bcrypt/Argon2 con salt único. Cost adjustado.

**Por qué AES-GCM y no CBC**: AEAD combinado, paralelizable, no hay padding oracle attacks.

**Salt y para qué**: aleatorio único por hash, evita rainbow tables y hashes idénticos para passwords iguales.

**Forward secrecy en cifrado simétrico**: claves efímeras por sesión, no derivadas de pubkey persistente.

**Cifrado asimétrico — para qué**: key exchange (acordar key simétrica) + signatures (autenticar identidad). NO para cifrar grandes volúmenes (lento).

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Diferencia hash vs encrypt (one-way vs two-way).
- Por qué SHA-256 NO sirve para passwords (demasiado rápido).
- bcrypt y Argon2id como soluciones para passwords.
- Por qué salt es necesario (rainbow tables, dedup).
- AES-GCM como modo simétrico moderno (AEAD).
- Cifrado asimétrico: para key exchange y signatures, no bulk data.
- Por qué nunca implementes crypto custom.
- Algoritmos deprecated (MD5, SHA-1, ECB).

Si no puedes → relee.

---

## Conexiones

- [[01-tls-handshake-detallado]] — usa todas estas primitivas
- [[03-owasp-top-10]] — passwords y crypto en OWASP
- [[04-jwt-y-session-management]] — uso práctico
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Cryptography Engineering** (Schneier, Ferguson, Kohno) — el libro accesible.
- **Bulletproof TLS** (Ristić) — para TLS específicamente.
- **OWASP Password Storage Cheatsheet** — práctico.
- **`bcrypt`, `argon2-cffi`, `cryptography`** (Python) — librerías a usar.
- **libsodium** — librería moderna recomendada.
- **HashiCorp Vault, AWS KMS, GCP KMS** — gestión de keys.
- **`hashcat`** — herramienta para entender qué tan rápido se crackea cada hash.
