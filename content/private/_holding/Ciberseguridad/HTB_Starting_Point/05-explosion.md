---
title: Explosion (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, rdp, windows, credenciales-debiles, reconocimiento]
type: nota
status: en-progreso
source: claude-code
aliases: [Explosion HTB, HTB Explosion, RDP sin password]
---

# Explosion — HTB Starting Point (Tier 0)

**Tier 0 · SO: Windows · Dificultad: Very Easy · Skills: nmap, xfreerdp, RDP enumeration**

Maquina de laboratorio autorizado de Hack The Box (Starting Point). Objetivo: conectarse via RDP a un Windows Server con credenciales debiles o ausentes y leer la flag del escritorio.

---

## Objetivo

Obtener acceso al sistema Windows explotando un servicio RDP (Remote Desktop Protocol) expuesto publicamente con la cuenta `Administrator` sin contrasena (o contrasena en blanco).

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

**Categoria: escaneo de puertos / fingerprinting de servicios**

Patron: identificar que puertos TCP estan abiertos y que servicio corre en cada uno antes de intentar cualquier interaccion.

```bash
nmap -sV -sC -p- --min-rate 5000 <IP>
```

Flags relevantes:
- `-sV` — detecta versiones de servicio
- `-sC` — lanza scripts NSE por defecto
- `-p-` — escanea los 65535 puertos
- `--min-rate 5000` — acelera el escaneo (adecuado en laboratorio)

Lo que revela nmap en esta maquina:

```
3389/tcp open  ms-wbt-server  Microsoft Terminal Services (RDP)
```

El puerto 3389 con el servicio `ms-wbt-server` (Windows RDP) abierto es la superficie de ataque. Puede que nmap tambien devuelva otros puertos abiertos (135, 445, etc.) tipicos de Windows; el vector relevante aqui es el 3389.

---

## Enumeracion

**Categoria: reconocimiento de credenciales / autenticacion debil**

Patron: antes de atacar, comprobar si el servicio acepta autenticacion sin contrasena. En RDP esto se traduce en intentar conectarse como `Administrator` con campo de contrasena vacio.

No hace falta un enumerador complejo: la propia herramienta de conexion (`xfreerdp`) reporta si la autenticacion falla o tiene exito.

Si quieres verificar que el host acepta conexiones antes de lanzar el cliente grafico:

```bash
nmap -p 3389 --script rdp-enum-encryption <IP>
```

Esto revela el nivel de cifrado y si NLA (Network Level Authentication) esta habilitado. Si NLA esta desactivado, se puede intentar conectar sin autenticarse primero en la capa de red — lo que facilita el acceso con credenciales debiles.

---

## Acceso inicial (foothold)

**Categoria: autenticacion debil / RDP con cuenta sin contrasena**

Patron: cuenta privilegiada (`Administrator`) con contrasena en blanco. El atacante solo necesita conocer el nombre de usuario.

Herramienta: `xfreerdp` (cliente RDP para Linux, habitualmente en `freerdp2-x11` o `freerdp3-x11`).

```bash
xfreerdp /v:<IP> /u:Administrator /p:'' +clipboard /dynamic-resolution
```

Flags de xfreerdp usados:
- `/v:<IP>` — IP del objetivo (la que HTB asigna al lanzar la maquina)
- `/u:Administrator` — usuario a autenticar
- `/p:''` — contrasena vacia (cadena vacia)
- `+clipboard` — permite copiar/pegar entre host y sesion remota
- `/dynamic-resolution` — ajusta la resolucion de pantalla dinamicamente

Si la conexion tiene exito, se abrira un escritorio Windows remoto con sesion de `Administrator`. En algunos entornos HTB puede aparecer un aviso de certificado; acepta con `/cert:ignore`:

```bash
xfreerdp /v:<IP> /u:Administrator /p:'' /cert:ignore +clipboard
```

> **Nota:** el comportamiento exacto (si pide o no pide contrasena, si da error de certificado) puede variar segun la version del laboratorio activa. Ajusta los flags segun el mensaje de error que devuelva `xfreerdp`.

Una vez dentro del escritorio, la flag esta en `C:\Users\Administrator\Desktop\flag.txt` o directamente visible como archivo en el escritorio.

---

## Escalada de privilegios

No requiere privesc: la sesion RDP se obtiene directamente como `Administrator` (cuenta con maximos privilegios en Windows). La flag se lee desde esa misma sesion.

---

## Flags

Esta maquina tiene **una sola flag** (Starting Point Tier 0 no siempre separa `user.txt` / `root.txt`):

| Archivo | Ubicacion tipica | Descripcion |
|---|---|---|
| `flag.txt` | `C:\Users\Administrator\Desktop\flag.txt` | Flag unica del nivel |

Para leerla desde la sesion RDP: abre el archivo con el Bloc de notas o desde PowerShell:

```powershell
Get-Content C:\Users\Administrator\Desktop\flag.txt
```

El valor es del tipo `<flag>` (32 caracteres hexadecimales, formato estandar HTB).

---

## Patron y teoria

Esta es la seccion mas importante del writeup: el patron que se repite en sistemas reales.

### Patron: RDP expuesto a internet con credenciales debiles o ausentes

**Categoria de vulnerabilidad: misconfiguracion de autenticacion en servicio de administracion remota**

El problema no es RDP en si — es una combinacion de tres decisiones de configuracion incorrectas:

1. **RDP accesible desde internet** (o desde red no confiable) sin restriccion de IP.
2. **NLA desactivado**: sin Network Level Authentication, el servidor establece la sesion de escritorio completa antes de pedir credenciales, ampliando la superficie de ataque.
3. **Cuenta `Administrator` con contrasena vacia o trivial**: el atacante no necesita ni bruteforcear.

Este patron aparece con frecuencia en instancias Windows mal configuradas en la nube (AWS, Azure, GCP) donde el grupo de seguridad abre 0.0.0.0/0:3389 "temporalmente" y se queda asi.

### Como se defiende / como disenarlo bien (purple team / dev)

**No exponer RDP directamente a internet.** Opciones:

```
Internet → VPN (WireGuard/OpenVPN) → red interna → RDP solo en red interna
Internet → Bastion/Jump host → RDP al servidor destino
Internet → Azure Bastion / AWS Systems Manager Session Manager (sin abrir puertos)
```

**Habilitar NLA obligatoriamente.** Con NLA, el cliente debe autenticarse a nivel de red (Kerberos/NTLM) antes de que el servidor despliegue el escritorio completo. Reduce superficie ante ataques de denegacion de servicio y exploits pre-autenticacion.

```powershell
# Verificar estado NLA (como admin en el servidor)
Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name UserAuthentication
# 1 = NLA habilitado (correcto), 0 = NLA deshabilitado (vulnerable)
```

**Contrasenas fuertes + MFA.** Ninguna cuenta de servicio o administradora debe tener contrasena vacia ni trivial. Anade MFA con soluciones como Duo Security, Microsoft Authenticator (via Azure AD), o similares.

**Monitoriza intentos de conexion RDP.** En el Event Log de Windows, el ID `4625` (failed logon) y `4624` (successful logon) con `Logon Type 10` (RemoteInteractive) son las senales clave. Exporta a un SIEM y alerta ante multiples `4625` desde la misma IP.

**Lista blanca de IPs si RDP debe estar expuesto.** Si por alguna razon operativa RDP tiene que ser accesible, restringe el acceso a rangos de IP corporativos en el firewall / grupo de seguridad.

### Por que esto importa para un desarrollador

Si desarrollas aplicaciones que se despliegan en servidores Windows (IIS, SQL Server, aplicaciones .NET), la configuracion del servidor es parte de tu superficie de ataque aunque no seas el sysadmin. Revisar que RDP no esta expuesto y que las cuentas tienen credenciales solidas es una check basica de hardening antes de poner un servidor en produccion.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- — si existe nota atomica sobre RDP/NLA
- — patron general de autenticacion debil
- — checklist de configuracion segura en Windows

---

*Fuente: laboratorio oficial Hack The Box Starting Point — uso etico y autorizado.*
