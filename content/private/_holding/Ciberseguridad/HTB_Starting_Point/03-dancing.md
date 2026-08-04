---
title: Dancing (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, smb, windows, enumeracion, null-session]
type: nota
status: en-progreso
source: claude-code
aliases: [Dancing HTB, HTB Dancing, smb-null-session, dancing-starting-point]
---

# Dancing — HTB Starting Point (Tier 0)

Tier 0 · SO: Windows · Dificultad: Very Easy · Skills: enumeracion SMB, sesion nula, smbclient

> Hack The Box es un laboratorio de ciberseguridad **legal y autorizado**. Estas maquinas estan disenadas para ser atacadas; todo lo descrito aqui es etico dentro de ese entorno.

Dancing introduce el protocolo **SMB** (Server Message Block) y la tecnica de la **sesion nula**: conectarse a un recurso compartido de red sin usuario ni contrasena y obtener informacion sensible directamente de las shares mal configuradas.

---

## Objetivo

Acceder a una maquina Windows que expone recursos compartidos SMB publicamente, localizar la share que contiene la flag y descargarla sin autenticacion.

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

Categoria: **escaneo de puertos / fingerprinting de servicios**.

```bash
nmap -sV <IP>
```

Salida relevante esperada:

```
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds  Windows 10 / Server 2019 Microsoft-DS
```

El puerto **445** es SMB moderno (sin depender de NetBIOS). Es el objetivo.

> Ajusta el escaneo en vivo: `-sV` hace fingerprinting de version. Si la maquina es lenta, agrega `--min-rate 1000` para acelerar.

---

## Enumeracion

Categoria: **enumeracion SMB — listado de shares con sesion nula**.

Una *sesion nula* (null session) es una conexion SMB sin credenciales. En configuraciones por defecto antiguas (o mal configuradas) el servidor responde igualmente y lista los recursos compartidos disponibles.

```bash
smbclient -L //<IP>/ -N
```

- `-L` — lista las shares del servidor (equivale a "mostrar recursos compartidos").
- `-N` — no pedir contrasena (null session).

Salida esperada (los nombres exactos pueden variar; lo importante es la lista de shares):

```
        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        WorkShares      Disk
```

- `ADMIN$`, `C$`, `IPC$` son shares administrativas de Windows; normalmente requieren privilegios.
- `WorkShares` no tiene descripcion: es la candidata a explorar.

---

## Acceso inicial (foothold)

Categoria: **acceso sin autenticacion a share SMB**.

Conectate a la share `WorkShares` tambien sin contrasena:

```bash
smbclient //<IP>/WorkShares -N
```

Veras el prompt interactivo de smbclient:

```
smb: \>
```

Navega y localiza la flag:

```bash
# Dentro del prompt smb:
ls                  # listar contenido raiz de la share
ls <carpeta>/       # si hay subdirectorios, exploralos
get flag.txt        # descargar el archivo al directorio local
```

> El nombre exacto y la ubicacion del archivo dentro de la share pueden variar. Si no ves `flag.txt` directamente, usa `ls` recursivo o explora subdirectorios. El patron es siempre el mismo: `ls` para orientarte, `get` para bajar el archivo.

Una vez descargado, sal del prompt con `exit` y lee la flag:

```bash
cat flag.txt
```

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente desde la share SMB sin necesidad de escalar privilegios en el sistema operativo.

---

## Flags

| Flag | Archivo | Ubicacion |
|---|---|---|
| Unica flag | `flag.txt` | Dentro de la share `WorkShares` en el servidor SMB |

La flag tiene el formato `<flag>` (cadena hexadecimal/alfanumerica tipica de HTB). No hay `user.txt` ni `root.txt` separados en las maquinas Tier 0: una sola flag confirma el compromiso.

---

## Patron y teoria

### El patron: SMB con sesion nula -> fuga de informacion

**Categoria de vulnerabilidad**: configuracion incorrecta de servicio de red (misconfiguration) + control de acceso ausente.

**Como funciona**:

1. SMB es el protocolo de Windows para compartir archivos e impresoras en red. Expone "shares" (recursos compartidos) a las que se accede por nombre (`\\servidor\share`).
2. Windows permite configurar shares con acceso anonimo o de invitado. Si no se restringe, cualquier cliente puede conectarse sin credenciales (*null session* o *guest session*).
3. El atacante primero enumera las shares disponibles (`-L`), identifica las que no son administrativas estandar, y luego se conecta directamente.

**Por que es peligroso mas alla de una flag de CTF**:
- En entornos reales, shares mal configuradas exponen backups, scripts con credenciales en texto plano, documentos internos o configuraciones de aplicaciones.
- SMB sobre puerto 445 es frecuentemente accesible dentro de redes corporativas (lateral movement).
- Historicamente, null sessions en SMB han sido el vector de ataques masivos (ej: gusanos de red en los 2000).

### Como se defiende / Como lo disenas bien (purple team / dev)

**En el servidor Windows (hardening)**:
```powershell
# Deshabilitar null sessions (registro)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" `
    -Name "RestrictAnonymous" -Value 2

# Deshabilitar SMBv1 (version antigua, sin cifrado, mas vulnerable)
Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force
```

**En el diseno de shares**:
- Permisos minimos necesarios: nunca `Everyone: Full Control`.
- Separar shares por proposito y audiencia; no mezclar datos publicos con sensibles en la misma share.
- Auditar shares existentes periodicamente: `Get-SmbShare | Get-SmbShareAccess`.

**En la red**:
- Bloquear el puerto 445 en el perimetro (no debe salir a internet salvo VPN controlada).
- Segmentar la red interna para que SMB solo sea accesible entre hosts que lo necesitan (no toda la LAN).

**Como desarrollador**:
- Nunca almacenes secretos (API keys, contrasenas, .env) en shares de red o directorios compartidos sin cifrado y control de acceso estricto.
- En pipelines CI/CD, evita montar shares SMB sin autenticacion; usa secretos del sistema de CI o un vault (HashiCorp Vault, AWS Secrets Manager, etc.).

### Herramienta: smbclient

`smbclient` es el cliente SMB de Linux (paquete `samba-client`). Su interfaz imita a FTP:

| Comando smb | Equivalente | Para que |
|---|---|---|
| `ls` | `dir` | Listar contenido |
| `get <archivo>` | `cp remoto local` | Descargar un archivo |
| `put <archivo>` | `cp local remoto` | Subir un archivo (si tienes permiso) |
| `cd <dir>` | `cd` | Cambiar directorio |
| `exit` | — | Salir |

Para enumeracion mas avanzada (con credenciales, RPC, politicas), ver [[13-herramientas-en-detalle]] y la herramienta `enum4linux` / `enum4linux-ng`.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[03-seguridad-de-redes]] — SMB, puertos, segmentacion de red
- [[05-identidad-auth-y-secretos]] — control de acceso, autenticacion, gestion de secretos
- [[06-seguridad-de-sistemas-y-hardening]] — hardening Windows, null sessions, SMBv1
- [[07-pentesting-y-ciclo-del-ataque]] — enumeracion como fase del ciclo ofensivo
- [[13-herramientas-en-detalle]] — smbclient, enum4linux
