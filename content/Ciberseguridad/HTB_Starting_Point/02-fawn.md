---
title: Fawn (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, ftp, reconocimiento, linux]
type: nota
status: en-progreso
source: claude-code
aliases: [Fawn HTB, fawn starting point, ftp-anonymous-htb]
---

# Fawn — HTB Starting Point (Tier 0)

Tier 0 · SO: Linux · Dificultad: Very Easy · Skills: FTP, reconocimiento con nmap

> Hack The Box Starting Point es un laboratorio **legal, ético y autorizado**. Toda la actividad descrita aquí se realiza dentro del entorno controlado de HTB.

Fawn es la segunda máquina del Tier 0. Introduce el protocolo FTP y el error clásico de dejar el acceso anónimo habilitado: sin contraseña, cualquiera puede listar y descargar archivos del servidor.

---

## Objetivo

Conectarte al servidor FTP de la máquina como usuario `anonymous`, localizar la flag y descargarla.

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

**Categoría: escaneo de puertos y detección de servicios.**

El primer paso en cualquier pentest es saber qué puertas están abiertas y qué servicio hay detrás.

```bash
nmap -sV <IP>
```

Flags usados:
- `-sV` — detección de versión de servicio; nmap no solo dice "puerto abierto" sino también qué programa escucha y qué versión.

Salida esperada (simplificada):

```
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
```

Lo que revela: el puerto 21 está abierto y corre **vsftpd** (Very Secure FTP Daemon), un servidor FTP común en Linux. La versión exacta puede variar en tu instancia; lo importante es identificar **FTP en el 21**.

---

## Enumeracion

**Categoría: identificación de configuración insegura (acceso anónimo FTP).**

FTP define un usuario especial llamado `anonymous` que muchos servidores aceptan sin contraseña (o con cualquier string como contraseña). Es una función pensada para distribución pública de archivos, pero si se deja activa en un servidor que no debería ser público, se convierte en una vulnerabilidad directa.

Para confirmar si el servidor lo admite, simplemente intentamos conectarnos:

```bash
ftp <IP>
```

El cliente FTP pedirá usuario y contraseña:

```
Name (<IP>:tu_usuario): anonymous
331 Please specify the password.
Password:
```

Introduce cualquier string como contraseña (convención: tu email, o simplemente pulsa Enter). Si el servidor acepta la conexión, verás:

```
230 Login successful.
ftp>
```

Una vez dentro, listar los archivos:

```bash
ls
```

Salida esperada:

```
-rw-r--r--    1 0        0              32 Jun 04  2021 flag.txt
```

Hay un archivo `flag.txt` en el directorio raíz del FTP.

---

## Acceso inicial (foothold)

**Categoría: extracción de archivo via FTP anónimo.**

No hay explotación de vulnerabilidad de software aquí: el "foothold" es el propio acceso anónimo. El servidor entrega el archivo sin más.

Descarga la flag con el comando `get`:

```bash
get flag.txt
```

FTP descargará `flag.txt` a tu directorio local. Sal del cliente:

```bash
bye
```

Lee la flag en tu máquina:

```bash
cat flag.txt
```

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente desde el acceso FTP anónimo. No hay acceso a shell ni usuarios que escalar.

---

## Flags

| Archivo | Ubicación típica | Descripción |
|---|---|---|
| `flag.txt` | Directorio raíz del servidor FTP | Única flag de la máquina |

La flag tiene el formato estándar de HTB: `<flag>`. Cópiala y pégala en la plataforma para validar la máquina.

---

## Patron y teoria

### El patron: FTP anónimo habilitado en servidor no público

**Categoría de vulnerabilidad: misconfiguration / exposed service.**

El patrón es uno de los más frecuentes en CTFs y en el mundo real: un servicio configurado para un caso de uso legítimo (distribución pública de archivos) se deja activo en un entorno donde no debería estarlo. No hay CVE, no hay exploit: el "ataque" es simplemente usar el servicio tal como está configurado.

Flujo del ataque:

```
nmap -sV <IP>          # 1. Descubro que el puerto 21 está abierto
ftp <IP>               # 2. Me conecto
usuario: anonymous     # 3. Uso el usuario especial sin contraseña
ls / get flag.txt      # 4. Listo y descargo lo que hay
```

### FTP: por qué es peligroso por diseño

FTP (File Transfer Protocol, RFC 959, 1985) tiene dos problemas estructurales:

1. **Transmisión en claro**: usuario, contraseña y datos viajan sin cifrar. Cualquiera con acceso a la red intermedia puede capturarlos con un sniffer (Wireshark, tcpdump).
2. **Autenticación anónima opcional**: el protocolo define el usuario `anonymous` como mecanismo de acceso público. Si el administrador no lo desactiva explícitamente, muchos servidores lo admiten por defecto.

### Como se defiende / como se disena para evitarlo (clave dev/purple team)

**Desactivar FTP anónimo:**

En vsftpd (`/etc/vsftpd.conf`):
```
anonymous_enable=NO
```

En cualquier servidor FTP: revisar la configuración y asegurarse de que `anonymous` o `ftp` no son usuarios válidos.

**Reemplazar FTP por protocolos cifrados:**

| Protocolo | Cifrado | Alternativa a |
|---|---|---|
| SFTP | Sí (SSH) | FTP |
| FTPS | Sí (TLS) | FTP |
| SCP | Sí (SSH) | FTP |

SFTP es la recomendación estándar: reutiliza la infraestructura SSH (mismo puerto 22, mismas claves), no requiere puertos adicionales y cifra todo el canal.

**Principio de mínimo privilegio aplicado a servicios de red:**

- Si no necesitas que nadie acceda sin autenticarse, no habilites acceso anónimo.
- Si no necesitas FTP en absoluto, cierra el puerto 21 en el firewall.
- Audita periodicamente los puertos abiertos (`nmap -sV` sobre tus propios servidores) y cuestiona cada servicio: ¿quién lo usa? ¿está cifrado? ¿tiene acceso anónimo?

**Como desarrollador:** si tu aplicación mueve archivos entre servicios, usa SFTP/SCP o directamente HTTPS con autenticación. Nunca FTP plano, especialmente en entornos con credenciales o datos sensibles.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[03-seguridad-de-redes]] — protocolos de red, cifrado en tránsito
- [[07-pentesting-y-ciclo-del-ataque]] — reconocimiento y enumeracion
- [[06-seguridad-de-sistemas-y-hardening]] — hardening de servicios, principio de minimo privilegio
- Página oficial del Tier 0: https://app.hackthebox.com/starting-point
