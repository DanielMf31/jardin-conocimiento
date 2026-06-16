---
title: Privacidad y OPSEC
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, privacidad, opsec, redes/anonimato]
type: nota
status: en-progreso
source: claude-code
aliases: [OPSEC, privacidad digital, anonimato]
---

# 🔏 Privacidad y OPSEC

## Por que importa este dominio

La mayoría de los ataques exitosos no rompen criptografía: explotan información que la víctima dejó expuesta voluntariamente o por descuido. **Privacidad y OPSEC** son la capa humana y operacional de la seguridad: controlan qué datos existe sobre ti, dónde y en qué forma.

Este módulo cierra el ciclo del cluster de ciberseguridad desde el ángulo del defensor personal: no importa cuánto hagas en [[09-devsecops-y-appsec]] si tu cuenta personal está comprometida o tu modelo de amenaza no corresponde a tu realidad.

> Regla de oro: la privacidad no es un estado binario. Es un conjunto de decisiones de ingeniería que reducen superficie de exposición frente a adversarios concretos.

---

## 🗺️ Panorama: privacidad, anonimato y OPSEC no son lo mismo

Antes de entrar en herramientas, calibra los conceptos. Son distintos y se mezclan permanentemente en artículos de internet:

| Concepto | Definición operativa | Protege de... |
|---|---|---|
| **Privacidad** | Controlar quién accede a información personal | Empresas, brechas de datos, data brokers |
| **Anonimato** | Ocultar tu identidad en una acción/comunicación | Vigilancia masiva, correlación de identidades |
| **Pseudonimato** | Usar una identidad alternativa coherente pero no real | Vinculación de identidades online |
| **OPSEC** (Operations Security) | Proceso sistemático de identificar y proteger información crítica antes de que el adversario la use | Depende del threat model |

**OPSEC** viene del ámbito militar: es el conjunto de prácticas para evitar que el adversario use información fragmentada para deducir información sensible. En contexto civil equivale a: ¿qué puedo deducir de ti con datos públicos?

---

## 🎯 Threat model personal — por qué te defiendes IMPORTA

### Qué es un threat model

Un **modelo de amenaza** (*threat model*) es la respuesta explícita a cuatro preguntas:

1. **¿Qué protejo?** (activos: contraseñas, código fuente, historial médico, ubicación)
2. **¿De quién me protejo?** (adversarios: empresa de publicidad, ex pareja, atacante oportunista, estado)
3. **¿Qué probabilidad tiene el adversario de llegar a eso?** (capacidad y motivación)
4. **¿Cuánto daño produciría la exposición?** (consecuencias)

### Por qué es el primer paso

Sin threat model claro, la gente hace una de dos cosas:
- **Sobreproteger** con herramientas complejas que no necesitan, sacrificando usabilidad.
- **Infraproteger** porque "no tengo nada que esconder".

### Ejemplo de dos perfiles distintos

```
Perfil A — Ingeniero en empresa tech:
  Activos críticos: código, credenciales cloud, acceso CI/CD
  Adversarios probables: phishing corporativo, atacante oportunista
  Foco: 2FA fuerte, gestores de contraseñas, no reusar creds

Perfil B — Activista en país con vigilancia estatal:
  Activos críticos: identidad real, comunicaciones, red de contactos
  Adversarios probables: agencias estatales con recursos altos
  Foco: Tor, dispositivos aislados, comunicaciones cifradas E2E, anonimato
```

La mayoría de personas técnicas en contexto occidental caen más cerca de A. Usar Tor para todo cuando tu adversario real es un data broker es sobredimensionar; pero no usar 2FA cuando tus repos son tu trabajo es infradimensionar.

---

## 👣 Huella digital y rastreo

### Tipos de huella

- **Huella activa**: lo que publicas conscientemente (redes sociales, commits en GitHub, foros).
- **Huella pasiva**: lo que se registra sin acción explícita (IP, cookies, fingerprint de navegador, metadatos de archivos).

### Mecanismos de rastreo principales

```
Cookies de terceros
  └─ Anunciante X pone una cookie en web A, la ve en web B, C, D
     → construye perfil de navegación cross-site

Browser fingerprinting
  └─ Tu combinación de: OS + browser + resolución + fuentes + zona horaria + plugins
     → es estadísticamente única en ~83% de usuarios (EFF Panopticlick)
     → NO necesita cookies; no lo borras limpiando historial

Metadatos de archivos (EXIF)
  └─ Una foto puede contener: GPS exacto, modelo de cámara, fecha/hora, software de edición

Correlación de identidades
  └─ Mismo nick en tres plataformas + misma foto de perfil + mismo estilo de escritura
     → un adversario puede linkear identidades que creías separadas
```

### Herramientas de rastreo que usan las empresas

| Técnica | Qué rastrea | Cómo mitigar |
|---|---|---|
| Píxeles de seguimiento (email) | Si abriste el email, cuándo, desde qué IP | Cliente de email que bloquea imágenes externas |
| UTM parameters | De dónde vienes, qué campaña te atrajo | Extensiones como ClearURLs |
| CNAME cloaking | El tracker aparece como subdominio first-party | uBlock Origin + DNS resolver alternativo |
| Device fingerprint | Tu combinación única de características del dispositivo | Brave o Firefox con resistencia a fingerprinting |
| Data brokers | Compran/venden datos de múltiples fuentes para crear perfiles | Proceso manual de opt-out; servicios como DeleteMe |

---

## 🧅 Anonimato: Tor y sus límites

### Cómo funciona Tor (The Onion Router)

Tor cifra tu tráfico en **tres capas** y lo enruta por **tres nodos** voluntarios:

```
Tu dispositivo
    │  [cifra con clave del nodo 3, luego 2, luego 1]
    ▼
Nodo de entrada (Guard node)
    Sabe: tu IP real
    No sabe: destino ni contenido
    │
    ▼
Nodo intermedio (Middle node)
    Sabe: que el paquete viene del guard, va al exit
    No sabe: ni origen real ni destino final
    │
    ▼
Nodo de salida (Exit node)
    Sabe: el destino final y el contenido (si no va por HTTPS)
    No sabe: quién eres tú
    │
    ▼
Servidor destino
    Sabe: que alguien desde el exit node pidió algo
    No sabe: tu IP real
```

El modelo es el de una **cebolla** (*onion*): cada nodo solo puede descifrar su capa, no las demás.

### Qué protege Tor (y qué NO)

| Tor protege de... | Tor NO protege de... |
|---|---|
| Tu ISP vea qué sitios visitas | Login en tu cuenta real (Google, banco) desde Tor |
| El servidor vea tu IP real | JavaScript que filtra info del dispositivo |
| Vigilancia masiva de tráfico | Comportamiento que te identifica (mismo nick, estilo de escritura) |
| Correlación básica de visitas | Nodo de salida malicioso + tráfico no cifrado (sin HTTPS) |

> Principio crítico: **Tor protege la capa de red. No protege la capa de aplicación ni la capa humana.** Si te logueas en tu Gmail desde Tor, Google te conoce aunque no sepa tu IP.

### Servicios .onion (hidden services)

Los sitios `.onion` no son "la dark web maliciosa" por definición: son servicios que existened dentro de la red Tor donde **ningún nodo conoce la IP del servidor**. El cifrado es bidireccional completo. Los usa el New York Times, la BBC, SecureDrop (filtración de documentos), y sí, también infraestructura criminal. La tecnología es neutral.

---

## 🔌 VPNs — qué son y cuáles son sus límites reales

### Lo que una VPN hace

Una VPN (*Virtual Private Network*) crea un túnel cifrado entre tu dispositivo y el servidor VPN. El tráfico sale desde la IP del servidor VPN, no la tuya.

```
Sin VPN:
  Tú → ISP → Internet → Servidor
  (ISP ve todo el tráfico)

Con VPN:
  Tú → [túnel cifrado] → Servidor VPN → Internet → Servidor
  (ISP ve que te conectas al VPN, no a dónde)
```

### Lo que una VPN NO hace

- No te hace anónimo: el proveedor VPN sí conoce tu IP real. Ahora **confías en el VPN en lugar del ISP**.
- No cifra el contenido más allá del servidor VPN: entre el VPN y el servidor destino, HTTPS sigue siendo necesario.
- No protege contra fingerprinting o cookies.
- No protege contra cuentas en las que estés logueado.

### Criterios para elegir un VPN (si lo necesitas)

1. **No-logs policy auditada** por terceros independientes (no basta con que lo digan ellos).
2. **Kill switch** que corta el tráfico si el VPN cae (evita que tu IP real se exponga).
3. **Sede en jurisdicción favorable** (fuera de 5/9/14 Eyes si tu threat model lo requiere).
4. Open source o al menos código del cliente auditable.

> Para la mayoría de ingenieros: un VPN de calidad sirve para redes WiFi públicas y para no exponer tráfico al ISP. Para anonimato real frente a adversarios con recursos, Tor es más adecuado.

---

## 🛡️ Hardening personal — lo que ya deberías tener

Este bloque reutiliza prácticas del [[05-identidad-auth-y-secretos]] y del trabajo que ya haces en [[09-devsecops-y-appsec]]. No se repiten los conceptos en profundidad; aquí el enfoque es la aplicación personal.

### Contraseñas

| Practica | Implementacion |
|---|---|
| Una contraseña única por cuenta | Gestor de contraseñas: Bitwarden (open source, auditable) o KeePassXC (local) |
| Contraseñas de >= 16 caracteres aleatorios | El gestor las genera; tú no las memorizas |
| Contraseña maestra fuerte y memorable | Diceware: 5-6 palabras aleatorias del diccionario (ej: correcto-caballo-bateria-grapa) |
| Auditoría de contraseñas filtradas | Have I Been Pwned (HIBP) integrado en Bitwarden o manual en haveibeenpwned.com |

### Autenticación de dos factores (2FA)

Jerarquía de más a menos seguro:

```
Hardware token (YubiKey, FIDO2/WebAuthn)   ← más fuerte; phishing-resistant
    ↓
App TOTP (Aegis en Android, Tofu en iOS)   ← buena opción, sin SMS
    ↓
SMS / email OTP                             ← vulnerable a SIM swapping y SS7
    ↓
Sin 2FA                                     ← no hacer esto en cuentas críticas
```

> El SIM swapping es un ataque en el que el atacante convence a tu operadora de que transfiera tu número a una SIM que controla él. A partir de ahí, cualquier 2FA por SMS que tengas queda comprometido.

### Alias de email

En lugar de dar tu email real en registros, usas alias que reenvían a tu bandeja:

- **SimpleLogin** (open source, adquirido por Proton) o **AnonAddy**: generas `compra-steam-abc123@simplelogin.com` → reenvía a tu email real.
- Si la cuenta es comprometida o empieza a hacer spam, desactivas ese alias específico. Tu email real nunca queda expuesto.
- Útil también para saber **qué servicio vendió o filtró tu email**.

### Cifrado de disco

- **Linux**: LUKS (Linux Unified Key Setup) — cifrado de partición completo integrado en el instalador de la mayoría de distros. Si ya tienes Hyprland instalado y elegiste cifrado en la instalación, ya lo tienes.
- **macOS**: FileVault 2 (activar en System Preferences).
- **Windows**: BitLocker (Pro/Enterprise) o VeraCrypt (open source, multiplataforma).
- Para volúmenes individuales o contenedores portables: **VeraCrypt** funciona en todas las plataformas.

> El cifrado de disco protege si te roban el dispositivo físico. No protege contra un sistema operativo ya comprometido (malware en ejecución ve los datos descifrados).

### Navegador

```
Recomendado para la mayoría de usos:
  Firefox + uBlock Origin (modo medium) + extensión "ClearURLs"

Para mayor resistencia a fingerprinting:
  Brave (basado en Chromium; resistencia a fingerprinting por defecto)

Para sesiones sensibles puntuales:
  Tor Browser (cada sesión es limpia; sin persistencia)
```

No usar Chrome para nada sensible: Google tiene intereses comerciales directos en tu historial de navegación.

---

## 📋 GDPR y datos personales — nociones mínimas

El **GDPR** (*General Data Protection Regulation*, UE 2018) establece derechos sobre tus datos personales. Como ingeniero que construye apps (ej:), también tienes obligaciones.

### Tus derechos como ciudadano (UE o datos de ciudadanos UE)

| Derecho | Qué significa en la práctica |
|---|---|
| Acceso | Puedes pedir a cualquier empresa qué datos tienen de ti |
| Rectificación | Pueden corregir datos inexactos |
| Supresión ("derecho al olvido") | Puedes pedir que borren tus datos (con excepciones) |
| Portabilidad | Recibir tus datos en formato legible por máquina |
| Oposición | Oponerte al procesamiento para marketing directo |

### Como desarrollador: obligaciones mínimas

- **Consentimiento explícito** antes de recolectar datos no esenciales.
- **Datos mínimos necesarios** (*data minimization*): no pedir más de lo que usas.
- **Cifrar datos en reposo y en tránsito**.
- **Notificación de brecha** en <= 72 horas a la autoridad competente si hay un incidente.
- **DPA** (*Data Processing Agreement*) con terceros que manejen datos en tu nombre (ej: tu proveedor de analytics).

> Las multas del GDPR pueden llegar al 4% de la facturación global anual. No es solo un tema ético.

---

## ⚠️ Errores comunes en privacidad personal

1. **"No tengo nada que esconder"** — La privacidad no trata de ocultar delitos; trata de mantener autonomía sobre tu propia narrativa.
2. **Confundir VPN con anonimato** — Un VPN solo desplaza la confianza al proveedor VPN.
3. **Instalar apps de privacidad pero loguarte en Google en el mismo dispositivo** — La capa de aplicación destruye el trabajo de la capa de red.
4. **Usar el mismo nick/avatar en plataformas que quieres separadas** — La correlación de identidades es trivial con metabúsquedas.
5. **No actualizar el threat model** — Lo que necesitabas proteger hace 2 años puede haber cambiado.
6. **Privacidad por oscuridad** — "Nadie me va a atacar a mí" es una apuesta, no una defensa.
7. **Olvidar los metadatos** — El contenido cifrado no oculta con quién te comunicas, cuándo, ni con qué frecuencia (metadatos de comunicación).

---

## Aplícalo / practica

### Para tu setup personal (nivel inmediato)

- [ ] Audita tus cuentas en [haveibeenpwned.com](https://haveibeenpwned.com) — ¿alguna credencial tuya filtrada?
- [ ] Instala Bitwarden o KeePassXC; migra tus contraseñas.
- [ ] Activa 2FA con app TOTP (Aegis) en tus cuentas críticas: GitHub, email, banco, cloud providers.
- [ ] Configura SimpleLogin para separar identidades en registros futuros.
- [ ] Revisa si LUKS estaba activo en tu instalación de Hyprland.
- [ ] Instala uBlock Origin en Firefox y activa el modo medium block.

### Para entender Tor / anonimato

- [ ] Descarga Tor Browser; visita [check.torproject.org](https://check.torproject.org) para verificar que funciona.
- [ ] Visita [coveryourtracks.eff.org](https://coveryourtracks.eff.org) con tu navegador habitual y con Tor Browser — compara los fingerprints.
- [ ] Lee el [Threat Modeling guide de EFF](https://ssd.eff.org/module/your-security-plan) (Surveillance Self-Defense).

### CTFs y labs

- **PicoCTF** y **CTFtime** tienen challenges de OSINT que te enseñan a encontrar (y evitar dejar) huellas digitales.
- **OSINT Framework** ([osintframework.com](https://osintframework.com)): explora las fuentes que un atacante usaría para perfilarte. Hacerlo sobre ti mismo es legal y muy revelador.
- Lab en VM: instala Whonix (sistema diseñado para rutear todo por Tor) y practica navegación anónima en un entorno aislado — sin riesgo para tu sistema principal.

### Para tus proyectos (app web, etc.)

- Audita qué datos personales recoge tu app y si tienes un `privacy policy` aunque sea mínimo.
- Asegúrate de que las variables de entorno con datos de usuarios no están en el repo (ver).
- Implementa expiración de tokens y mínimo privilegio en tus JWTs (ver [[05-identidad-auth-y-secretos]]).

---

## Conexiones

- [[MOC_Ciberseguridad]]
- [[01-fundamentos-y-mentalidad]]
- [[05-identidad-auth-y-secretos]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[09-devsecops-y-appsec]]
- [[10-blue-team-y-respuesta-incidentes]]
- [[03-seguridad-de-redes]]
- [[MOC_Desarrollo_Software]]
