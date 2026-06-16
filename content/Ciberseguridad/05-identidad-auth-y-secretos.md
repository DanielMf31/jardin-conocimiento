---
title: "Identidad: autenticacion, autorizacion y secretos"
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, programacion/web, ciberseguridad/identidad, ciberseguridad/auth]
type: nota
status: en-progreso
source: claude-code
aliases: [auth-y-secretos, identidad-digital, autenticacion-autorizacion]
---

# 🔐 Identidad: autenticacion, autorizacion y secretos

## Por que importa este dominio

Casi todo ataque real tiene un vector de identidad: robar credenciales, suplantar usuarios, abusar de tokens, filtrar secretos del codigo. Antes de hablar de firewalls o cifrado, hay que resolver quien eres, que puedes hacer y como guardas las llaves del reino.

El modelo mental: **identidad es la puerta de entrada a todos los demas sistemas**. Si la puerta esta rota, el resto da igual.

---

## 1. Autenticacion vs Autorizacion

Estos dos terminos se confunden constantemente. Son fases distintas y secuenciales:

| Concepto | Pregunta que responde | Ejemplo |
|---|---|---|
| **Autenticacion** (AuthN) | ¿Quien eres? | El usuario introduce su contrasena; el sistema verifica |
| **Autorizacion** (AuthZ) | ¿Que puedes hacer? | El usuario autenticado intenta borrar un recurso; el sistema comprueba si tiene permiso |

Un atacante que pasa la autenticacion como usuario normal todavia puede estar bloqueado por la autorizacion (principio de minimo privilegio). Un bug de autorizacion le da poder lateral aunque no haya robado la identidad de un admin.

**Errores comunes**:
- Asumir que "si esta logueado, puede hacer todo" (falta de authZ).
- Verificar roles solo en el frontend (el backend debe verificar siempre, el frontend es mutable por el usuario).
- Confundir sesion activa con permisos vigentes (los permisos deben revisarse en cada operacion sensible, no solo al login).

---

## 2. Sesiones (cookies) vs Tokens (JWT)

### 2.1 Sesiones con cookies (modelo tradicional)

```
Cliente                     Servidor
  |                             |
  |--- POST /login ------------>|
  |<-- Set-Cookie: sessionId=X  |  (el servidor guarda el estado en DB/Redis)
  |                             |
  |--- GET /dashboard --------->|  Cookie enviada automaticamente
  |    (Cookie: sessionId=X)    |
  |<-- respuesta autorizada ----|  Servidor busca X en almacen de sesiones
```

- El servidor es **stateful**: guarda el estado de la sesion.
- Revocar una sesion es inmediato: borra el registro.
- Vulnerable a **CSRF** (Cross-Site Request Forgery) si no se usan tokens CSRF o el atributo `SameSite` en la cookie.
- Protegerse: `HttpOnly` (JS no puede leer la cookie), `Secure` (solo HTTPS), `SameSite=Strict/Lax`.

### 2.2 Tokens JWT (JSON Web Token)

**Estructura**: tres partes separadas por `.`, codificadas en Base64URL (no cifradas por defecto):

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9   <- HEADER  (algoritmo + tipo)
.
eyJzdWIiOiIxMjM0NTY3ODkwIiwicm9sZSI6ImFkbWluIn0  <- PAYLOAD (claims: sub, iat, exp, roles...)
.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c   <- SIGNATURE (HMAC o RSA del header+payload)
```

El servidor firma el token; el cliente lo guarda (localStorage o cookie) y lo envia en cada peticion. El servidor solo verifica la firma — no guarda estado.

**Ventajas**: escalabilidad horizontal (cualquier servidor valida sin consultar DB), util para microservicios y APIs.

**Riesgos y ataques clasicos**:

| Riesgo | Que pasa | Como prevenirlo |
|---|---|---|
| `alg: none` | Servidor acepta token sin firma si no valida el campo `alg` | Fijar el algoritmo esperado en el servidor, rechazar `none` |
| Robo de token (XSS) | Si el token esta en `localStorage`, JS malicioso lo lee | Guardar en cookie `HttpOnly`; nunca en `localStorage` para tokens sensibles |
| No verificar `exp` | Token caducado sigue siendo valido | Verificar siempre `exp` (expiracion) y `nbf` (not before) |
| Payload visible | Los datos del payload son legibles por cualquiera (solo Base64) | No meter datos sensibles en el payload (contrasenas, secretos) |
| Sin revocacion | Un JWT valido no se puede invalidar facilmente antes de que expire | Usar tokens de vida corta + refresh tokens; mantener una blacklist si necesitas revocacion inmediata |

---

## 3. OAuth 2.0 y OpenID Connect

### El problema que resuelven

Antes de OAuth, si una app queria acceder a tus datos de Google, te pedia tu contrasena de Google. Eso es catastrofico: la app recibe credenciales maestras que puede guardar o reutilizar.

OAuth 2.0 resuelve **delegacion de acceso**: "Permito a la App X leer mis contactos de Google, sin darle mi contrasena".

### Roles en OAuth 2.0

```
Resource Owner  ->  el usuario (tu)
Client          ->  la aplicacion que quiere acceso (App X)
Authorization Server  ->  quien emite tokens (Google, tu propio servidor)
Resource Server       ->  donde viven los datos protegidos (API de contactos)
```

### Flujo Authorization Code (el mas seguro para web):

```
Usuario -> App: click "Login con Google"
App -> Google AuthServer: redirige con client_id, scope, redirect_uri, state
Google -> Usuario: pagina de consentimiento ("App X quiere leer tus contactos")
Usuario -> Google: aprueba
Google -> App: redirige con `code` (de un solo uso, corta vida)
App -> Google (backend): intercambia `code` por `access_token` (y `refresh_token`)
App -> ResourceServer: usa `access_token` para llamar a la API
```

El parametro `state` previene CSRF en el flujo OAuth. Siempre debe validarse.

### OpenID Connect (OIDC)

Es una **capa de identidad sobre OAuth 2.0**. OAuth dice "tienes permiso para X"; OIDC ademas dice "y el usuario es Y" (emite un `id_token` JWT con datos del usuario como email, nombre, sub).

- OAuth 2.0 → autorizacion (acceso a recursos)
- OIDC → autenticacion (quien es el usuario)

Cuando ves "Login con Google/GitHub" en una app, es OIDC en accion.

---

## 4. MFA y Passkeys

### MFA (Multi-Factor Authentication)

La seguridad de "algo que sabes" (contrasena) se complementa con:

| Factor | Tipo | Ejemplos | Resistencia a phishing |
|---|---|---|---|
| Algo que sabes | Conocimiento | PIN, contrasena | Baja |
| Algo que tienes | Posesion | App TOTP (Google Authenticator), SMS, llave hardware | Media (TOTP) / Alta (hardware) |
| Algo que eres | Inherencia | Huella dactilar, FaceID | Alta (pero local) |

**SMS como segundo factor**: comodisimo pero debil. Vulnerable a SIM swapping (el atacante convence a la operadora de portar tu numero) y a intercepciones SS7. Mejor que nada, pero usa TOTP o llaves hardware si puedes.

**TOTP** (Time-based One-Time Password, RFC 6238): genera un codigo de 6 digitos cada 30 segundos usando una clave compartida + el tiempo actual. No requiere red. Implementado por apps como Aegis (Android), Raivo (iOS).

**Llaves hardware** (YubiKey, etc.): implementan el protocolo FIDO2/WebAuthn. El atacante necesita el dispositivo fisico. Inmune a phishing remoto.

### Passkeys

Son la evolucion post-contrasena. Usan criptografia de clave publica (par de claves generado en el dispositivo):

```
Registro:
  Dispositivo genera par de claves (privada queda en dispositivo/TPM, publica va al servidor)

Autenticacion:
  Servidor envia un "challenge" aleatorio
  Dispositivo firma el challenge con la clave privada (desbloqueada con biometria local)
  Servidor verifica la firma con la clave publica almacenada
```

Ventajas: sin contrasena que robar, sin phishing posible (la clave publica es especifica del dominio), sin reutilizacion. El estandar es **FIDO2/WebAuthn** (W3C + FIDO Alliance).

---

## 5. Hashing de contrasenas (repaso)

> Ver [[02-criptografia]] para la teoria de hash completa.

**Nunca guardes contrasenas en texto plano, ni cifradas, ni con hash generico (MD5, SHA-1, SHA-256)**. Estos son rapidos por diseno, lo que los hace perfectos para ataques de diccionario/fuerza bruta con GPUs.

Usa algoritmos diseñados especificamente para contrasenas, que son **lentos y con parametros de coste ajustables**:

| Algoritmo | Recomendacion | Parametros clave |
|---|---|---|
| **bcrypt** | Solido, ampliamente soportado | `cost` (10-12 para la mayoria) |
| **Argon2id** | Recomendado actual (vencedor PHC 2015) | `memory`, `iterations`, `parallelism` |
| **scrypt** | Buena opcion, algo mas complejo de tunear | `N`, `r`, `p` |
| **PBKDF2** | Aceptable, obligatorio en algunos estandares FIPS | `iterations` alto (>600k para SHA-256) |

El **salt** (valor aleatorio unico por usuario, generado automaticamente por estas librerias) previene rainbow tables y hace que dos usuarios con la misma contrasena tengan hashes distintos.

En Python (ejemplo conceptual con `passlib` o `bcrypt`):
```python
# Registro
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("contrasena_usuario")  # incluye salt automaticamente

# Verificacion
is_valid = pwd_context.verify("contrasena_introducida", hashed)
```

---

## 6. Gestion de secretos 🔑

Este es el punto donde mas proyectos fallan, incluyendo proyectos propios. Un secreto es cualquier valor que, si se expone, compromete la seguridad: contrasenas de DB, API keys, claves privadas, tokens de servicio.

### 6.1 El pecado capital: hardcodear o commitear secretos

```python
# MAL — jamas hagas esto
DATABASE_URL = "mongodb://usuario:<password>@db:27017/miapp"
SECRET_KEY = "supersecretkey"
```

Una vez commiteado, el secreto esta en el historial de Git **para siempre** (incluso si lo borras en un commit posterior). Herramientas como `git log -S`, `truffleHog` o `gitleaks` lo encontraran.

**Si ya ocurrio**: rotar el secreto inmediatamente (no en paralelo, primero rotar), y considera el secreto comprometido aunque el repo sea privado.

### 6.2 Variables de entorno

El nivel minimo aceptable. Los secretos viven en el entorno del proceso, no en el codigo:

```bash
# .env  (NUNCA commitear este archivo)
DATABASE_URL=mongodb://usuario:<password>@db:27017/miapp
JWT_SECRET=una-clave-larga-y-aleatoria
```

```python
# config.py
import os
DATABASE_URL = os.environ["DATABASE_URL"]  # falla si no esta definida (bueno)
```

Reglas:
- `.env` siempre en `.gitignore`.
- Commitea `.env.example` (con valores de placeholder) para documentar que variables se necesitan.
- En produccion/CI, inyectar los secretos via variables de entorno del sistema (Docker secrets, GitHub Actions secrets, etc.), nunca via archivo `.env` copiado.

### 6.3 Vaults y gestores de secretos

Para proyectos serios, las variables de entorno simples no son suficientes: no tienen auditoria, rotacion automatica, ni control de acceso granular.

| Herramienta | Caso de uso | Notas |
|---|---|---|
| **HashiCorp Vault** | Self-hosted, muy potente | Soporta rotacion dinamica de credenciales de DB |
| **AWS Secrets Manager / Parameter Store** | Si ya estas en AWS | Rotacion automatica, IAM integrado |
| **Azure Key Vault / GCP Secret Manager** | Equivalentes en otras nubes | Similar a AWS |
| **Doppler / Infisical** | SaaS mas sencillo | Buena DX, util para equipos pequenos |
| **SOPS + git** | Secretos cifrados en repo | Util para IaC/GitOps; secretos cifrados con GPG/KMS |

El flujo con un vault: la app autentica contra el vault al arrancar (con un token o identidad de maquina) y recupera los secretos en memoria. Los secretos nunca tocan el sistema de archivos ni el repo.

### 6.4 Deteccion proactiva: pre-commit hooks y escaneo

Herramienta `gitleaks`: escanea el historial de git buscando patrones de secretos (API keys, tokens, contrasenas).

```bash
# Instalar y escanear el repo actual
gitleaks detect --source . --verbose
```

Pre-commit hook para bloquearlo antes de que llegue al historial:
```bash
# .git/hooks/pre-commit  (o via pre-commit framework)
gitleaks protect --staged
```

En CI/CD: ejecutar `gitleaks` o `truffleHog` en cada PR es una practica DevSecOps basica (ver [[09-devsecops-y-appsec]]).

### 6.5 Auditoria: secretos en tus proyectos actuales

Pasos para auditar un proyecto existente:

```bash
# Buscar patrones obvios en el codigo fuente
grep -rE "(password|secret|token|api_key)\s*=\s*['\"][^'\"]{4,}" --include="*.py" .

# Comprobar que .env no esta trackeado
git ls-files | grep -i "\.env"

# Ver si hay secretos en el historial
gitleaks detect --source . --no-git=false
```

---

## Diagrama: flujo completo de una peticion autenticada

```
[Usuario]
    |
    | 1. POST /auth/login  {email, password}
    v
[API Backend]
    |-- Busca usuario en DB
    |-- Verifica hash de contrasena (bcrypt.verify)
    |-- Si MFA activado: pide codigo TOTP
    |-- Genera JWT (payload: sub=userId, roles, exp=+15min)
    |-- Genera refresh_token (opaco, guardado en DB, exp=+7dias)
    |
    | 2. Responde: {access_token: JWT, refresh_token: ...}
    |    (refresh_token en cookie HttpOnly; access_token en memoria de la app)
    v
[Cliente]
    |
    | 3. GET /api/perfil
    |    Authorization: Bearer <JWT>
    v
[API Backend]
    |-- Verifica firma JWT con SECRET_KEY (de variable de entorno)
    |-- Verifica exp, nbf
    |-- Extrae roles del payload
    |-- Comprueba authZ: ¿tiene el rol necesario para /api/perfil?
    |-- Procesa y responde
```

---

## Errores comunes en proyectos propios

1. **JWT en localStorage**: vulnerable a XSS. Si hay un solo campo de texto sin sanitizar en tu app, un atacante puede robar todos los tokens.
2. **SECRET_KEY hardcodeada en config.py**: el secreto esta en git. Rotalo y muevelo a variable de entorno.
3. **No verificar authZ en el backend**: el rol "admin" solo se comprueba en el frontend. Un atacante llama directamente a la API con su token normal.
4. **Tokens de larga vida sin refresh**: un JWT que expira en 30 dias es practicamente una contrasena. Usa 15min + refresh token.
5. **Misma SECRET_KEY en todos los entornos**: si el entorno de desarrollo (con codigo de debug) tiene la misma clave que produccion, un leak de dev compromete prod.
6. **Sin rotacion de secretos**: las API keys y contrasenas de servicio deben tener una politica de rotacion (cada 90 dias es comun).

---

## Aplícalo / Practica 🧪

### En tus proyectos (app web y similares)

- [ ] Audita `backend/app/config.py` y `docker-compose.yml`: ningun secreto hardcodeado, todo desde `os.environ`.
- [ ] Verifica que `.env` esta en `.gitignore` y que `.env.example` existe con placeholders.
- [ ] Ejecuta `gitleaks detect` sobre el repo de la app.
- [ ] Implementa MFA TOTP en el endpoint de login (libreria `pyotp` en Python).
- [ ] Revisa el tiempo de vida de tus JWTs: si es >1 hora, implementa refresh tokens.
- [ ] Comprueba que los endpoints de admin verifican el rol en el backend, no solo en el frontend.

### CTFs y laboratorios

- **PortSwigger Web Security Academy** — modulo "Authentication" (gratuito, con labs interactivos): JWT attacks, MFA bypass, OAuth flaws.
- **HackTheBox / TryHackMe** — maquinas con desafios de autenticacion rota, escalada de privilegios por authZ deficiente.
- **OWASP WebGoat / Juice Shop** — apps intencionalmente vulnerables para practicar localmente (via Docker).
- **jwt.io** — decodifica y modifica JWTs manualmente para entender la estructura y los riesgos.

### Lectura y referencias

- OWASP Authentication Cheat Sheet
- RFC 7519 (JWT), RFC 6749 (OAuth 2.0), OpenID Connect Core 1.0
- NIST SP 800-63B: Digital Identity Guidelines (el estandar de referencia para niveles de autenticacion)

---

## Conexiones

- [[MOC_Ciberseguridad]]
- [[01-fundamentos-y-mentalidad]]
- [[02-criptografia]]
- [[04-seguridad-web-owasp]]
- [[09-devsecops-y-appsec]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[11-privacidad-y-opsec]]
- [[MOC_Desarrollo_Software]]
