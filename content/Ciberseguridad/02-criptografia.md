---
title: Criptografia
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, criptografia, redes/tls, autenticacion]
type: nota
status: en-progreso
source: claude-code
aliases: [cripto, cryptography, cifrado]
---

# Criptografia

## ¿Por que existe? — El problema que resuelve

Imagina que mandas un paquete por correo ordinario: cualquiera que lo intercepte puede abrirlo y leerlo. La criptografia es el sistema de cajas con candados que permite que solo el destinatario pueda abrirlo, y que ademas el receptor sepa que tu eres quien dice ser.

En seguridad, la criptografia cubre tres necesidades fundamentales (el trio CIA mas autenticacion):

| Necesidad | Pregunta | Herramienta |
|---|---|---|
| **Confidencialidad** | ¿Solo lo lee quien debe? | Cifrado simetrico/asimetrico |
| **Integridad** | ¿El contenido no fue alterado? | Hashing, firmas digitales |
| **Autenticacion** | ¿El remitente es quien dice ser? | Firmas digitales, certificados |
| **No repudio** | ¿No puede negar haberlo enviado? | Firmas digitales |

La criptografia no resuelve TODOS los problemas de seguridad — si el sistema esta comprometido o las claves se filtran, falla igualmente. Es una capa, no una bala de plata.

---

## Cifrado simetrico — Una sola llave para todo

**Concepto:** emisor y receptor comparten la misma clave secreta. La misma llave cifra y descifra.

```
Mensaje claro → [cifrar con clave K] → Ciphertext → [descifrar con clave K] → Mensaje claro
```

**Algoritmo principal: AES (Advanced Encryption Standard)**
- Estandar actual (desde 2001, reemplaza a DES).
- Tamaños de clave: 128, 192 o 256 bits. AES-256 se considera seguro para uso general.
- Opera en bloques de 128 bits; el modo de operacion importa:
  - **ECB** (Electronic Codebook) — EVITAR: bloques identicos producen ciphertext identico (famoso ejemplo: imagen del pingüino de Linux cifrada en ECB sigue viendose).
  - **CBC, GCM** — preferidos. GCM ademas ofrece autenticacion integrada (AEAD).

**Ventaja:** muy rapido (hardware acelera AES con instrucciones dedicadas AES-NI).
**Problema critico:** ¿como compartes la clave secreta de forma segura con alguien que no conoces?

---

## Cifrado asimetrico — Par de claves publica/privada

**Concepto:** cada parte tiene DOS claves matematicamente vinculadas:
- **Clave publica:** puedes compartirla con el mundo.
- **Clave privada:** solo tu la conoces, nunca sale de tu maquina.

Lo que se cifra con la publica solo se puede descifrar con la privada, y viceversa.

```
Alice quiere enviar algo secreto a Bob:
  Alice cifra con [clave publica de Bob] → Solo Bob puede descifrar con [su clave privada]
```

**Algoritmos principales:**

| Algoritmo | Base matematica | Uso tipico | Estado |
|---|---|---|---|
| **RSA** | Factorizacion de grandes numeros | TLS, firma de emails | Vigente; clave ≥2048 bits |
| **ECC** (curva eliptica) | Logaritmo discreto en curvas | TLS moderno, SSH, criptomonedas | Preferido actualmente (claves mas cortas, igual seguridad) |
| **DSA/ECDSA** | Logaritmo discreto | Firmas digitales | ECDSA preferido sobre DSA |

**Ventaja:** resuelve el problema de distribucion de claves.
**Problema:** es ordenes de magnitud mas lento que AES. No se usa para cifrar datos masivos.

---

## Diffie-Hellman — Como acordar una clave sin compartirla directamente

**El problema clasico:** Alice y Bob quieren usar cifrado simetrico (rapido), pero necesitan acordar una clave. ¿Como lo hacen en un canal inseguro sin que un espía (Eve) se entere?

**Diffie-Hellman (DH)** resuelve esto con matematica de aritmetica modular. La intuicion:

```
Analogia de colores:
  - Alice y Bob acuerdan un color base publico (digamos: amarillo).
  - Alice mezcla su color secreto (rojo)   → naranja. Envia naranja a Bob.
  - Bob mezcla su color secreto (azul)     → verde.   Envia verde a Alice.
  - Alice toma el verde de Bob + su rojo secreto → color final.
  - Bob toma el naranja de Alice + su azul secreto → mismo color final.
  - Eve ve amarillo, naranja y verde, pero no puede derivar el color final.
```

El "color final" es la **clave de sesion simetrica** que usan para cifrar la comunicacion con AES.

**ECDH (Elliptic Curve Diffie-Hellman)** es la variante moderna sobre curvas elipticas, usada en TLS 1.3.

**Perfect Forward Secrecy (PFS):** si se usa una clave DH nueva por sesion (efimera), comprometer la clave privada a largo plazo no compromete sesiones pasadas. TLS 1.3 lo requiere.

---

## #⃣ Hashing — Huella digital de datos

**Concepto:** una funcion hash toma datos de cualquier tamaño y produce una cadena de longitud fija (digest). Es una **funcion de una sola via**: no se puede revertir.

```
"hola mundo"    → SHA-256 → a591a6d40bf420...  (64 hex chars)
"hola mundo."   → SHA-256 → b94d27b9934d3e...  (completamente distinto)
```

**Propiedades de un buen hash criptografico:**

| Propiedad | Significado |
|---|---|
| **Determinista** | Misma entrada → siempre mismo hash |
| **Efecto avalancha** | Cambio minimo → hash totalmente distinto |
| **Pre-imagen resistente** | Dado hash H, imposible encontrar M tal que hash(M)=H |
| **Colision resistente** | Imposible encontrar dos M distintos con el mismo hash |
| **Irreversible** | No existe operacion inversa |

**Algoritmos:**
- **SHA-2** (SHA-256, SHA-512): estandar actual, ampliamente usado. SHA-1 esta obsoleto (colisiones demostradas).
- **SHA-3**: alternativa con diseño diferente (Keccak), util si se sospecha debilidad en SHA-2.
- **MD5**: ROTO. No usar para seguridad, solo para checksums no criticos.

**Para que SIRVE:**
- Verificar integridad de archivos (descargas, paquetes).
- Almacenar credenciales (de forma segura, ver abajo).
- Firmas digitales (se firma el hash, no el mensaje entero).
- Identificadores de commits en Git.

**Para que NO SIRVE el hash a secas:**
- Cifrar datos para recuperarlos (no es reversible).
- Almacenar contraseñas sin mas (vulnerable a rainbow tables y fuerza bruta si el hash es rapido).

---

## Firmas digitales — Autenticidad e integridad juntas

**Problema que resuelve:** como sabes que un mensaje fue realmente escrito por Alice y no fue alterado en transito?

**Mecanismo:**
```
Alice firma:
  1. hash(mensaje)                        → digest
  2. cifrar digest con [clave PRIVADA de Alice] → firma

Bob verifica:
  1. Descifra firma con [clave PUBLICA de Alice] → digest_alice
  2. Calcula hash(mensaje recibido)              → digest_local
  3. digest_alice == digest_local → [OK] integro y autentico
```

Si el mensaje fue alterado, los hashes no coinciden. Si alguien mas firmo, la clave publica de Alice no descifra correctamente.

**Usos reales:** commits de Git firmados con GPG, emails (S/MIME, PGP), software (firmado por el fabricante), certificados TLS.

---

## TLS, PKI y Certificados — La cadena de confianza

### TLS (Transport Layer Security)

Es el protocolo que asegura las conexiones en internet (HTTPS = HTTP + TLS). Combina todo lo anterior:

```
Handshake TLS 1.3 (simplificado):
  1. Cliente → Servidor: "Hola, soporto estos algoritmos, aqui mi clave DH efimera"
  2. Servidor → Cliente: "Usemos este algoritmo, aqui mi clave DH efimera + certificado firmado"
  3. Ambos derivan la clave de sesion simetrica (via ECDH)
  4. El resto de la comunicacion va cifrada con AES-GCM
```

TLS 1.2 y 1.3 son las versiones actuales. TLS 1.0 y 1.1 estan deprecados.

### El problema del "hombre en el medio" (MitM)

Si Alice se conecta a "banco.com", ¿como sabe que no hay alguien en el medio haciendose pasar por el banco con su propia clave publica? Necesitas saber que la clave publica que recibes es REALMENTE del banco.

### PKI (Public Key Infrastructure) — La solucion

**Cadena de confianza:**

```
Root CA (Autoridad de Certificacion Raiz)
  └─ Intermediate CA (CA Intermedia)
       └─ Certificado del servidor (banco.com)
```

- La **CA Raiz** es una entidad de confianza preinstalada en tu sistema operativo/navegador (DigiCert, Let's Encrypt, etc.).
- El certificado de `banco.com` esta **firmado** por la CA Intermedia.
- La CA Intermedia esta **firmada** por la CA Raiz.
- Tu navegador verifica la cadena: si todo encaja y la CA Raiz es de confianza → candado verde.

**Que contiene un certificado X.509:**
- Nombre del dominio (CN / Subject Alternative Names).
- Clave publica del servidor.
- Fecha de expiracion.
- Firma de la CA que lo emitio.

**Certificate Transparency (CT):** logs publicos donde las CAs deben registrar certificados emitidos. Permite detectar certificados fraudulentos.

**HSTS (HTTP Strict Transport Security):** cabecera que le dice al navegador "nunca te conectes a mi por HTTP, siempre HTTPS". Previene ataques de downgrade.

---

## Hashing de contraseñas — El caso especial

Almacenar contraseñas en texto plano es un error clasico y critico. Si la base de datos es robada, todas las contraseñas quedan expuestas.

**Solucion basica (insuficiente):** guardar `hash(contraseña)`.
**Problema:** los hashes rapidos (SHA-256, MD5) permiten ataques de fuerza bruta a miles de millones de intentos por segundo con GPUs modernas. Las **rainbow tables** son tablas precalculadas de hash→contraseña.

**Solucion correcta: funciones de hash lentas con salt**

### Salt (sal)

Un valor aleatorio unico generado para cada usuario, que se concatena a la contraseña antes de hashear:

```
hash = bcrypt(contraseña + salt_aleatorio)
```

- El salt se guarda en la BD junto al hash (no es secreto).
- Hace que dos usuarios con la misma contraseña tengan hashes distintos.
- Invalida las rainbow tables (habria que precalcular una tabla por cada salt).

### Algoritmos adecuados para contraseñas

| Algoritmo | Caracteristica clave | Recomendacion |
|---|---|---|
| **bcrypt** | Ajustable en coste; maximo 72 bytes de entrada | Buena opcion; ampliamente soportado |
| **Argon2** (id) | Ganador PHC 2015; ajustable en tiempo, memoria y paralelismo | **Mejor opcion actual** |
| **scrypt** | Memory-hard; mas dificil de configurar bien | Aceptable |
| **PBKDF2** | FIPS-aprobado; menos resistente que los anteriores | Solo si se requiere por compliance |

**NUNCA usar MD5, SHA-1, SHA-256 a secas para contraseñas.**

### Conexion con tu gestion de contraseñas

En tu proyecto de app web (FastAPI + MongoDB), si tienes usuarios con contraseña: ver [[05-identidad-auth-y-secretos]] para la implementacion con `passlib` + Argon2/bcrypt en el contexto de FastAPI.

---

## SSH — Criptografia asimetrica en la practica del dia a dia

SSH usa exactamente los conceptos anteriores:
- **Autenticacion por clave publica:** tu clave privada (`~/.ssh/id_ed25519`) nunca sale de tu maquina. El servidor tiene tu clave publica en `~/.ssh/authorized_keys`.
- El servidor genera un reto, tu lo firmas con tu clave privada, el servidor verifica con tu publica.
- El transporte usa DH para acordar clave de sesion, luego AES.
- **Ed25519** (variante de ECC) es el tipo de clave recomendado actualmente sobre RSA-2048/4096.

---

## Errores comunes — Lo que NO debes hacer

| Error | Por que es peligroso | Correccion |
|---|---|---|
| **Rolear tu propia criptografia** | Imposible implementar bien sin años de especialidad; siempre hay fallos sutiles | Usa librerias auditadas: `cryptography` (Python), `libsodium`, `OpenSSL` |
| **Usar ECB como modo de AES** | Patrones visibles en el ciphertext | Usa AES-GCM o AES-CBC con IV aleatorio |
| **MD5/SHA1 para contraseñas** | Vulnerable a fuerza bruta GPU | bcrypt / Argon2 |
| **Clave privada en el repositorio** | Expuesta a cualquiera con acceso al repo | Variables de entorno, secrets manager, `.gitignore` |
| **Certificado autofirmado en produccion** | Los clientes no confian en el; invita a ignorar advertencias | Let's Encrypt (gratis) o CA reconocida |
| **No verificar la cadena de certificados** | Vulnerable a MitM | No deshabilitar validacion TLS en clientes HTTP (ej: `verify=False` en requests Python) |
| **Reutilizar IV/nonce en AES-GCM** | Rompe la confidencialidad y la autenticacion | Genera IV aleatorio de 12 bytes por mensaje |
| **Usar TLS 1.0/1.1** | Protocoles con vulnerabilidades conocidas (POODLE, BEAST) | Forzar TLS 1.2 minimo, preferir 1.3 |

---

## Aplicalo / Practica

### Laboratorio conceptual (sin instalar nada extra)
```bash
# Hashing con Python stdlib
python3 -c "import hashlib; print(hashlib.sha256(b'hola mundo').hexdigest())"

# Generar par de claves SSH Ed25519
ssh-keygen -t ed25519 -C "mi-laboratorio"

# Inspeccionar un certificado TLS real
openssl s_client -connect google.com:443 -showcerts 2>/dev/null | openssl x509 -noout -text | head -50
```

### CTFs y plataformas con retos de cripto
- **CryptoHack** (cryptohack.org) — dedicado exclusivamente a criptografia, excelente calidad didactica.
- **PicoCTF** — categoria Cryptography; buena para empezar.
- **HackTheBox / TryHackMe** — retos con componente cripto en maquinas reales.
- **CryptoPals** (cryptopals.com) — serie de retos programaticos clasicos (romper CBC, padding oracle, etc.) en tu lenguaje favorito.

### Asegurar tu propio codigo
- En tu app web: audita como se almacenan contraseñas → ver [[05-identidad-auth-y-secretos]].
- Verifica que tus endpoints HTTPS no deshabiliten verificacion TLS.
- Si usas JWT: entiende que el secreto de firma es critico; usar RS256 (asimetrico) en produccion es mas robusto que HS256.
- Revisa que ningun secreto este en el repositorio: ver [[09-devsecops-y-appsec]].

### Legalidad y etica
Los conceptos de criptografia son neutrales y educativos. Las herramientas de analisis (como romper cifrado propio en un CTF) son legales en contextos autorizados. Interceptar trafico ajeno o romper cifrado de sistemas sin permiso es ilegal en la mayoria de jurisdicciones (Espana: art. 197 CP). Practica siempre en entornos propios o con permiso explicito.

---

## Referencias

- NIST SP 800-175B — Cryptographic Standards and Guidelines.
- RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3.
- *Serious Cryptography* — Jean-Philippe Aumasson (libro recomendado para profundizar).
- CryptoHack (cryptohack.org) — plataforma de practica.

---

## Conexiones

- [[MOC_Ciberseguridad]]
- [[01-fundamentos-y-mentalidad]]
- [[03-seguridad-de-redes]]
- [[04-seguridad-web-owasp]]
- [[05-identidad-auth-y-secretos]]
- [[09-devsecops-y-appsec]]
- [[MOC_Desarrollo_Software]]
