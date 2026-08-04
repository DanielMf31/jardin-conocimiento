---
title: HTB Starting Point — guía, patrones y progreso
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, wargame, meta]
type: nota
status: en-progreso
source: claude-code
aliases: [HTB Starting Point, Starting Point README, HTB SP]
---

# HTB Starting Point — guía, patrones y progreso

Las máquinas **Very Easy** tuteladas de Hack The Box: tu **rampa de entrada** a las máquinas reales
después de Bandit/Leviathan/Natas. Aquí tienes el writeup de las 25 máquinas (Tier 0→2) y, lo más
importante para ti, **la síntesis de los patrones y la teoría** que se repiten en todas.

> HTB es un laboratorio **legal y autorizado**. Todo esto es para aprender a **defender y diseñar mejor**.

## Cómo se juega
1. Te conectas a la VPN de HTB (`sudo openvpn starting_point.ovpn`) y lanzas (`Spawn`) la máquina → te da una **IP** (dinámica).
2. Atacas esa IP hasta encontrar la(s) **flag(s)** (`user.txt` / `root.txt`).
3. Las máquinas vienen con writeup oficial guiado; usa estos docs como apoyo y para **ver el patrón**.

> Úsalas así: intenta la máquina tú primero; si te atascas, mira el paso concreto. **No leas el writeup entero de golpe.**

---

## La teoría: el método y los patrones (LO IMPORTANTE)

### El bucle que se repite SIEMPRE
```
Reconocimiento (nmap)  →  Enumeración (cada servicio a fondo)  →  Foothold (acceso inicial)
   →  Shell  →  Escalada de privilegios (privesc)  →  root/SYSTEM  →  loot (flags)
```
El 80% del trabajo es **enumerar bien**. El exploit suele ser obvio cuando has enumerado a fondo.

### Patrón 1 — Servicio expuesto + credencial débil/ausente (Tier 0 casi entero)
Telnet, FTP, SMB, Redis, Mongo, RDP, rsync, MySQL… expuestos **sin auth o con credenciales por defecto**.
- **Lección dev/defensa**: nunca cuentas sin password ni credenciales de fábrica; no expongas puertos de admin/BD a la red; `bind` a localhost + firewall.
- Máquinas: meow, fawn, dancing, redeemer, explosion, mongod, synced, sequel, tactics.

### Patrón 2 — Enumeración de contenido + credenciales filtradas (encadenar)
Fuerza bruta de directorios (`gobuster`), ficheros accesibles, y **credenciales encontradas en un sitio reutilizadas en otro**.
- **Lección**: no dejes credenciales en ficheros accesibles; no reutilices contraseñas; protege/oculta paneles admin.
- Máquinas: preignition, crocodile, three.

### Patrón 3 — Vulnerabilidad web → RCE (el núcleo, lo tuyo como dev)
SQLi, LFI, SSTI, subida de ficheros, XXE, type juggling, deserialización… que acaban en **ejecución de código**.
- **Lección**: consultas parametrizadas (SQLi), whitelist de includes (LFI), validar uploads en servidor + carpeta no ejecutable, deshabilitar entidades XML externas (XXE), comparaciones estrictas `===` (type juggling), no meter input en plantillas (SSTI).
- Máquinas: appointment, responder, ignition, bike, oopsie, markup, base, included, three.

### Patrón 4 — Acceso a un servicio interno (pivoting) y exploits conocidos
Tunneling SSH para llegar a una BD interna; CVEs famosos (Log4Shell); paneles de CI/CD (Jenkins) y BBDD (MSSQL) que dan RCE directo.
- **Lección**: segmenta la red, parchea (gestión de vulnerabilidades), egress filtering, RBAC en herramientas internas.
- Máquinas: funnel, pennyworth, unified, archetype.

### Patrón 5 — Escalada de privilegios (privesc) — el final de Tier 2
Las vías clásicas que verás una y otra vez:
- **`sudo -l` + GTFOBins** (vi, find, etc. ejecutables como root) → vaccine, base.
- **Binario SUID** mal hecho / **PATH hijacking** → oopsie.
- **Credenciales reutilizadas** (en config, en historial de PowerShell) → base, archetype.
- **Grupo peligroso** (lxd/docker) → included.
- **Script programado escribible** → markup.
- **Lección**: principio de mínimo privilegio, `sudo` específico, mínimos SUID, no reutilizar credenciales, permisos correctos en scripts.

> Tu reflejo como dev ante cada máquina: *"¿cómo lo habría evitado yo en el código/config?"* Eso es **purple team** y es lo que te hace escribir software que no se rompe.

---

## Writeups por tier
**Tier 0 — un solo servicio, sin privesc (la mecánica básica)**
- [[HTB_Starting_Point/01-meow]] — Telnet sin password
- [[HTB_Starting_Point/02-fawn]] — FTP anónimo
- [[HTB_Starting_Point/03-dancing]] — SMB sesión nula
- [[HTB_Starting_Point/04-redeemer]] — Redis sin auth
- [[HTB_Starting_Point/05-explosion]] — RDP credenciales débiles
- [[HTB_Starting_Point/06-preignition]] — gobuster + creds por defecto
- [[HTB_Starting_Point/07-mongod]] — MongoDB sin auth
- [[HTB_Starting_Point/08-synced]] — rsync abierto

**Tier 1 — primeras cadenas (web, pivoting, paneles)**
- [[HTB_Starting_Point/09-appointment]] — SQLi bypass de login
- [[HTB_Starting_Point/10-sequel]] — MySQL root sin password
- [[HTB_Starting_Point/11-crocodile]] — creds por FTP → web
- [[HTB_Starting_Point/12-responder]] — LFI → robo de hash NTLM → WinRM
- [[HTB_Starting_Point/13-three]] — bucket S3 → RCE
- [[HTB_Starting_Point/14-ignition]] — vhost + creds débiles (Magento)
- [[HTB_Starting_Point/15-bike]] — SSTI (Handlebars/Node)
- [[HTB_Starting_Point/16-funnel]] — túnel SSH a Postgres interno
- [[HTB_Starting_Point/17-pennyworth]] — Jenkins Script Console RCE
- [[HTB_Starting_Point/18-tactics]] — SMB admin + impacket psexec

**Tier 2 — foothold + escalada de privilegios (máquina completa)**
- [[HTB_Starting_Point/19-archetype]] — MSSQL xp_cmdshell → creds en historial
- [[HTB_Starting_Point/20-oopsie]] — IDOR + upload → SUID privesc
- [[HTB_Starting_Point/21-vaccine]] — crack zip → SQLi → sudo GTFOBins
- [[HTB_Starting_Point/22-unified]] — Log4Shell (CVE-2021-44228)
- [[HTB_Starting_Point/23-included]] — LFI + TFTP → RCE; lxd privesc
- [[HTB_Starting_Point/24-markup]] — XXE → clave SSH → script escribible
- [[HTB_Starting_Point/25-base]] — type juggling PHP → upload → sudo GTFOBins

## Mi progreso (rellena a mano)
| # | Máquina | Tier | Skill principal | |
|---|---|---|---|---|
| 01 | meow | 0 | telnet | |
| 02 | fawn | 0 | ftp | |
| 03 | dancing | 0 | smb | |
| 04 | redeemer | 0 | redis | |
| 05 | explosion | 0 | rdp | |
| 06 | preignition | 0 | gobuster | |
| 07 | mongod | 0 | mongodb | |
| 08 | synced | 0 | rsync | |
| 09 | appointment | 1 | sqli | |
| 10 | sequel | 1 | mysql | |
| 11 | crocodile | 1 | ftp→web | |
| 12 | responder | 1 | lfi/ntlm | |
| 13 | three | 1 | s3/rce | |
| 14 | ignition | 1 | vhost/cms | |
| 15 | bike | 1 | ssti | |
| 16 | funnel | 1 | ssh tunnel | |
| 17 | pennyworth | 1 | jenkins | |
| 18 | tactics | 1 | impacket | |
| 19 | archetype | 2 | mssql/privesc | |
| 20 | oopsie | 2 | idor/suid | |
| 21 | vaccine | 2 | sqli/gtfobins | |
| 22 | unified | 2 | log4shell | |
| 23 | included | 2 | lfi/lxd | |
| 24 | markup | 2 | xxe | |
| 25 | base | 2 | type juggling | |

## Recursos que valen oro
- **IppSec** (YouTube) — vídeo-writeup de casi toda máquina HTB retirada.
- **0xdf.gitlab.io** — writeups escritos, muy didácticos.
- **HackTricks** (book.hacktricks.xyz) — referencia "cómo hago X".
- **GTFOBins** / **PayloadsAllTheThings** — privesc y payloads.

## Conexiones
- [[MOC_Ciberseguridad]] · [[12-aprender-y-carrera]] — ruta de aprendizaje
- [[Bandit/00_README]] · [[Leviathan/00_README]] · [[Natas/00_README]] — los wargames previos
- [[04-seguridad-web-owasp]] — teoría de las vulns web · [[06-seguridad-de-sistemas-y-hardening]] — privesc/hardening
- [[13-herramientas-en-detalle]] — nmap, gobuster, impacket, sqlmap, evil-winrm…
- [[07-pentesting-y-ciclo-del-ataque]] — el bucle recon→foothold→privesc
