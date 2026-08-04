---
title: Ignition (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, web, magento, vhosts, credenciales-debiles, cms]
type: nota
status: en-progreso
source: claude-code
aliases: [Ignition HTB, htb-ignition, magento-starting-point]
---

# Ignition — HTB Starting Point (Tier 1)

**Tier 1 · SO: Linux · Dificultad: Very Easy · Skills: virtual hosts (vhosts), enumeracion web, credenciales debiles en CMS**

Maquina de laboratorio de Hack The Box (entorno legal, autorizado y aislado). El vector central es doble: primero hay que resolver un problema de resolucion de nombre (virtual host), y luego explotar un panel de administracion de Magento protegido con credenciales triviales.

---

## Objetivo

Acceder al panel de administracion de Magento aprovechando credenciales debiles y capturar la flag ubicada en el dashboard.

---

## Acceso a la maquina (paso previo)

Antes de atacar nada necesitas conectarte a la red de HTB y arrancar la maquina para obtener su **IP**:

1. **Descarga tu VPN** desde el panel de HTB (Starting Point -> *Connect* -> descarga el `.ovpn`).
2. **Conectate a la VPN** y dejala corriendo en una terminal aparte:
   ```bash
   sudo openvpn starting_point_<tu_usuario>.ovpn
   ```
3. **Lanza la maquina** en la web (boton *Spawn Machine*). HTB te dara una **IP** (tipo `10.129.x.x`).
4. Comprueba que llegas a ella:
   ```bash
   ping -c2 <IP>
   ```
5. En el resto de este writeup, **sustituye `<IP>` por la IP que te toque** (es dinamica: cambia cada vez que lanzas la maquina).

> Alternativa sin VPN: el **Pwnbox** (Kali en el navegador que ofrece HTB) ya viene conectado a la red; solo lanzas la maquina y usas su IP directamente.

## Reconocimiento

**Categoria: escaneo de puertos y deteccion de servicios.**

```bash
nmap -sC -sV -oN ignition.nmap <IP>
```

Nmap revela que el puerto **80/tcp** esta abierto con un servidor web (tipicamente nginx). Al intentar acceder a `http://<IP>` directamente, el servidor responde con una redireccion a `http://ignition.htb` — el navegador no puede resolver ese nombre porque no esta en el DNS publico.

Esto indica que el servidor usa un **virtual host**: responde segun el campo `Host` de la cabecera HTTP. Si el nombre no resuelve, no llegas al sitio correcto.

---

## Enumeracion

**Categoria: resolucion de virtual host + identificacion del CMS.**

Paso 1: anadir el virtual host al archivo de hosts del sistema atacante.

```bash
echo "<IP>  ignition.htb" | sudo tee -a /etc/hosts
```

Paso 2: navegar a `http://ignition.htb`. Se carga la tienda Magento (CMS de e-commerce en PHP). Confirmar la tecnologia con las cabeceras o con la URL del panel de admin, que en Magento sigue el patron:

```
http://ignition.htb/admin
```

Paso 3: el panel de login de Magento aparece en `/admin`. Identificar la version si es posible (pie de pagina, cabeceras, ruta `/magento_version` en versiones antiguas). Esto informa sobre CVEs aplicables, aunque en esta maquina el vector es mas simple.

---

## Acceso inicial (foothold)

**Categoria: fuerza bruta ligera / credenciales debiles en panel de administracion.**

El panel `/admin` de Magento solicita usuario y contrasena. La superficie de ataque es la ausencia de rate limiting y el uso de credenciales predecibles.

Estrategia: probar combinaciones comunes antes de lanzar un ataque automatizado completo. Un diccionario corto orientado a CMS (tipo `admin:admin`, `admin:admin123`, `admin:admin@123`) suele ser suficiente en entornos de laboratorio mal configurados.

Opcion manual (navegador): probar directamente en el formulario.

Opcion semi-automatizada con `curl` para validar rapidamente:

```bash
# Primero obtener el form_key (Magento lo requiere como CSRF token)
curl -s http://ignition.htb/admin/ | grep -o 'form_key[^"]*"[^"]*"' | head -1
```

> Nota: Magento incluye un `form_key` como proteccion CSRF. Para un ataque real con herramienta (Hydra, Burp Intruder), hay que extraer ese token en cada intento. En la practica del Starting Point, probar manualmente con unas pocas contrasenas es suficiente — la contrasena correcta es del estilo `qwerty123` o `admin@123` (ajustar contra la maquina en vivo; HTB puede variar la credencial exacta entre resets).

Credenciales tipicas a probar (usuario `admin`):

| Contrasena    |
|---------------|
| admin         |
| admin123      |
| admin@123     |
| qwerty123     |
| 123456        |

Al entrar con las credenciales correctas, el **dashboard de Magento** muestra la flag directamente en la interfaz.

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente en el dashboard del panel de administracion tras el login exitoso. No hay segunda fase de escalada en esta maquina.

---

## Flags

| Flag     | Ubicacion                                              |
|----------|--------------------------------------------------------|
| unica    | Dashboard de Magento tras login como admin (`/admin`) |

La flag aparece visible en la pagina principal del panel de administracion. Copiarla tal cual: `<flag>`.

> Esta maquina tiene una sola flag (no hay separacion user/root porque el acceso es directo via web, sin shell del sistema).

---

## Patron y teoria

**Esta seccion es la mas importante. Aprende el patron, no solo los comandos.**

### 1. Virtual Hosts (Host header routing)

**Categoria: configuracion de infraestructura web.**

Un servidor puede alojar multiples sitios en la misma IP. El servidor decide cual servir segun la cabecera `Host` de la peticion HTTP. Si el cliente no resuelve el nombre, nunca llega al sitio correcto — aunque la IP este accesible.

```http
GET / HTTP/1.1
Host: ignition.htb        <-- esto determina que sitio ve el cliente
```

Patron de reconocimiento: si `http://<IP>` redirige a un nombre de dominio que no resuelve, es un vhost. Solucion: `/etc/hosts` en el atacante (o en pentesting real, DNS interno del cliente).

Como dev/sysadmin: **nunca confies en que el nombre de dominio sea secreto**. La IP puede descubrirse por otros medios (certificados TLS, registros DNS historicos, Shodan). El vhost no es una medida de seguridad.

### 2. Credenciales debiles en panel de administracion de CMS

**Categoria: autenticacion debil (OWASP A07:2021 — Identification and Authentication Failures).**

El patron se repite en Magento, WordPress, Joomla, phpMyAdmin, Jenkins, etc.:
- El CMS se instala con credenciales por defecto o el administrador elige una contrasena simple.
- El panel de admin es accesible desde internet (o desde la red del atacante).
- No hay rate limiting ni 2FA.
- Resultado: acceso completo al backend con unos pocos intentos.

### Defensa (perspectiva dev / purple team)

| Capa                  | Medida concreta                                                                 |
|-----------------------|---------------------------------------------------------------------------------|
| Contrasena            | Minimo 16 caracteres, aleatoria, generada por gestor de contrasenas             |
| Rate limiting         | Bloquear IP tras N intentos fallidos (fail2ban, WAF, middleware propio)         |
| 2FA                   | TOTP obligatorio en todos los accesos de admin                                  |
| Exposicion del panel  | Restringir `/admin` por IP de origen o ponerlo detras de VPN                   |
| Actualizaciones       | Mantener el CMS parcheado; Magento tiene historial de RCE pre-auth en versiones antiguas |
| Monitorizacion        | Alertas en logins fallidos y en primer login desde IP nueva                     |

### Flujo del ataque resumido

```
nmap -> puerto 80 -> redireccion a ignition.htb
-> /etc/hosts -> sitio Magento accesible
-> /admin -> formulario login
-> credenciales debiles -> dashboard
-> flag en pantalla
```

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]]
