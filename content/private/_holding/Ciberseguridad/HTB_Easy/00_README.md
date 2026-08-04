---
title: HTB Máquinas Easy — guía, patrones y progreso
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, wargame, meta]
type: nota
status: en-progreso
source: claude-code
aliases: [HTB Easy, HTB maquinas faciles, HTB retiradas easy]
---

# (facil) HTB Máquinas Easy — guía, patrones y progreso

El **paso después de [[HTB_Starting_Point/00_README|Starting Point]]**: máquinas Easy retiradas de la
plataforma principal de Hack The Box. Aquí ya no hay tutela — son **cadenas completas** de ataque
(*foothold → shell → escalada de privilegios*). 15 writeups + la síntesis de patrones que se repiten.

> HTB es un laboratorio **legal y autorizado**. Esto es para aprender a **defender y diseñar mejor**.

## El salto respecto a Starting Point
| | Starting Point | Easy (estas) |
|---|---|---|
| Estructura | 1 servicio → flag | **cadena** foothold → shell → **privesc** |
| Enumeración | obvia | hay que **cavar** (gobuster con extensiones, DNS, configs) |
| Privesc | rara vez | **casi siempre** (sudo, cron, kernel, GTFOBins) |
| Flags | normalmente 1 | **user.txt** (foothold) + **root.txt** (privesc) |

## Cómo se juega
1. Conéctate a la VPN de HTB (`sudo openvpn lab_<usuario>.ovpn`) y deja la terminal abierta.
2. Lanza (*Spawn*) la máquina → IP (las retiradas son `10.10.10.x`). Las **retiradas necesitan VIP**; las activas son gratis.
3. Atacas hasta sacar `user.txt` y `root.txt`. Cada doc trae su sección "Acceso a la máquina".

> Intenta la máquina tú primero; si te atascas, mira el paso concreto. Y apóyate en **IppSec** (vídeo de casi todas) y **0xdf**.

---

## La teoría: patrones que se repiten en TODAS

### Foothold (cómo entras) — 4 vías recurrentes
1. **Servicio desactualizado con CVE conocido** → RCE casi directo. (`lame` Samba, `legacy`/`blue` EternalBlue, `optimum` HFS, `shocker` Shellshock).
2. **Panel/CMS con credenciales débiles o por defecto** → despliegue/upload malicioso. (`jerry` Tomcat, `nibbles` Nibbleblog, `swagshop` Magento).
3. **Credenciales filtradas en ficheros** (FTP/SMB/config) reutilizadas. (`netmon` config PRTG, `sense` users.txt, `beep` reutilización, `friendzone` mysql.conf).
4. **Subida de webshell** (FTP→webroot, upload web, share SMB) → RCE. (`devel`, `bashed`, `friendzone`).

### Escalada de privilegios (cómo llegas a root/SYSTEM) — el catálogo
- **`sudo -l` + GTFOBins** (perl, vi, wget…) → `shocker`, `swagshop`, `sunday`.
- **Cron de root que ejecuta un script escribible** → `bashed`, `nibbles`, `friendzone` (library hijack Python).
- **Kernel/SO sin parchear** (Windows Exploit Suggester / Sherlock) → `devel`, `optimum`.
- **El servicio ya corría como root/SYSTEM** (no hace falta privesc) → `lame`, `jerry`, `blue`, `legacy`, `sense`.
- **Reutilización de credenciales** → `beep`, `netmon`.

### El método (siempre igual)
```
nmap (todos los puertos + versiones)  →  enumerar CADA servicio a fondo
  →  identificar la versión/CVE/credencial  →  foothold  →  shell estable
  →  enumerar como ese usuario (sudo -l, cron, SUID, historial, configs)  →  privesc  →  root
```

> Reflejo dev/purple team: por cada paso, *"¿cómo lo habría evitado en el código/config?"* → parchear, mínimo privilegio, no credenciales en ficheros, validar uploads, sudo específico.

---

## Writeups (dificultad creciente)
**Exploit conocido directo (las más fáciles)**
- [[HTB_Easy/01-lame]] — Samba `usermap_script` (CVE-2007-2447), RCE como root
- [[HTB_Easy/02-legacy]] — SMB MS08-067 / MS17-010 → SYSTEM
- [[HTB_Easy/03-blue]] — EternalBlue (MS17-010)
- [[HTB_Easy/04-jerry]] — Tomcat Manager creds por defecto → WAR → SYSTEM

**Web → shell → escalada de privilegios**
- [[HTB_Easy/05-devel]] — FTP→webroot, webshell ASPX → privesc kernel
- [[HTB_Easy/06-optimum]] — HFS RCE (CVE-2014-6287) → MS16-032
- [[HTB_Easy/07-netmon]] — config PRTG por FTP → RCE CVE-2018-9276
- [[HTB_Easy/08-bashed]] — phpbash expuesto → sudo → cron escribible
- [[HTB_Easy/09-nibbles]] — Nibbleblog upload RCE → sudo script escribible
- [[HTB_Easy/10-shocker]] — Shellshock en cgi-bin → sudo perl
- [[HTB_Easy/11-swagshop]] — Magento exploit → sudo vi

**Enumeración y cadenas (las más completas)**
- [[HTB_Easy/12-sense]] — pfSense: enum de ficheros → creds → RCE
- [[HTB_Easy/13-sunday]] — Solaris: finger → creds débiles → sudo wget
- [[HTB_Easy/14-beep]] — Elastix: LFI + reutilización de credenciales
- [[HTB_Easy/15-friendzone]] — SMB+DNS → LFI → library hijack Python

## Mi progreso (rellena a mano)
| # | Máquina | SO | Técnica clave | user | root |
|---|---|---|---|---|---|
| 01 | lame | Linux | Samba CVE-2007-2447 | | |
| 02 | legacy | Windows | MS08-067/MS17-010 | | |
| 03 | blue | Windows | EternalBlue | | |
| 04 | jerry | Windows | Tomcat WAR | | |
| 05 | devel | Windows | FTP+IIS → kernel | | |
| 06 | optimum | Windows | HFS → MS16-032 | | |
| 07 | netmon | Windows | PRTG | | |
| 08 | bashed | Linux | phpbash → cron | | |
| 09 | nibbles | Linux | Nibbleblog → sudo | | |
| 10 | shocker | Linux | Shellshock → perl | | |
| 11 | swagshop | Linux | Magento → vi | | |
| 12 | sense | BSD | pfSense | | |
| 13 | sunday | Solaris | finger → wget | | |
| 14 | beep | Linux | Elastix LFI | | |
| 15 | friendzone | Linux | LFI → python hijack | | |

## Conexiones
- [[MOC_Ciberseguridad]] · [[12-aprender-y-carrera]] — ruta de aprendizaje
- [[HTB_Starting_Point/00_README]] — el paso anterior · [[Bandit/00_README]] · [[Natas/00_README]]
- [[08-vulnerabilidades-y-explotacion]] — CVEs/exploits · [[06-seguridad-de-sistemas-y-hardening]] — privesc
- [[04-seguridad-web-owasp]] — vías de entrada web · [[13-herramientas-en-detalle]] — nmap, metasploit, gobuster…
- [[07-pentesting-y-ciclo-del-ataque]] — el bucle recon→foothold→privesc
- **IppSec** (YouTube) y **0xdf.gitlab.io** — writeups de referencia de cada máquina
