---
title: OverTheWire Bandit — guía y progreso
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, bandit, wargame, meta]
type: nota
status: en-progreso
source: claude-code
aliases: [Bandit README, Bandit guia, OverTheWire Bandit]
---

# OverTheWire Bandit — guía y progreso

Wargame **legal y educativo** para aprender terminal/Linux jugando. En cada nivel encuentras una
**contraseña escondida** que te deja entrar por SSH al siguiente. Aquí tienes el walkthrough paso a
paso de **todos los niveles (0→33)** + tu tabla de progreso.

## Cómo se juega
1. Te conectas al nivel N:
```bash
ssh bandit<N>@bandit.labs.overthewire.org -p 2220
```
   (El nivel 0 usa la contraseña `bandit0`.)
2. Resuelves el reto → obtienes la **contraseña del nivel N+1**.
3. `exit` y entras al siguiente con esa contraseña. Y así hasta el 33 (el final actual).
4. Páginas oficiales con pistas: https://overthewire.org/wargames/bandit/

> Úsalos así: intenta el nivel tú primero; si te atascas, mira el paso concreto. **No leas la solución entera de golpe.**

> **Terminal Kitty (`Error opening terminal: xterm-kitty`).** Si usas **Kitty** como terminal, al abrir un programa interactivo **dentro del servidor** (`nano`, `vi`, `more`, `less`, y el paginador de `git log`/`git show`) verás ese error: el servidor no tiene el "terminfo" de Kitty. Solución: `export TERM=xterm` (una vez por sesión SSH) o prefijando el comando (`TERM=xterm nano archivo`). Afecta sobre todo a **16→17, 23→24, 25→26, 26→27** y a los **niveles git (28→32)**. (Si entras desde tu portátil no pasa: kitty sí tiene su terminfo ahí.)

> **Cambio de OverTheWire (2025-2026) — `localhost` bloqueado para SSH.** Ahora **bloquean conectarte al puerto SSH 2220 desde `localhost`** (`Connecting from localhost is blocked to conserve resources`). Afecta a los niveles que hacen `ssh -i ...@localhost`: **13→14, 16→17, 25→26**. Solución: usa el **hostname real** `bandit.labs.overthewire.org` (mismo puerto 2220), o copia la clave a tu portátil y conéctate desde ahí. **NO afecta** a `nc`/`openssl` contra puertos del juego (30000/30001/31xxx/30002 en 14→15, 15→16, 16→17, 24→25) ni, de momento, a los clones git por `localhost` (27→32, ver nota en [[28-nivel-27-a-28]]).

## Walkthroughs (todos los niveles)
**Básicos — manejo de archivos (0→5)**
- [[01-nivel-0-a-1]] — SSH + `ls`, `cat`
- [[02-nivel-1-a-2]] — archivo `-` (stdin vs `./-`)
- [[03-nivel-2-a-3]] — nombres con espacios (comillas/escape)
- [[04-nivel-3-a-4]] — archivos ocultos (`ls -a`)
- [[05-nivel-4-a-5]] — tipo de archivo (`file`)

**Buscar y procesar texto / decodificar (5→13)**
- [[06-nivel-5-a-6]] — `find` (tamaño/permisos)
- [[07-nivel-6-a-7]] — `find /` (usuario/grupo) + `2>/dev/null`
- [[08-nivel-7-a-8]] — `grep`
- [[09-nivel-8-a-9]] — `sort` + `uniq -u`
- [[10-nivel-9-a-10]] — `strings`
- [[11-nivel-10-a-11]] — `base64 -d`
- [[12-nivel-11-a-12]] — ROT13 con `tr`
- [[13-nivel-12-a-13]] — `xxd -r` + descompresión en cadena (gzip/bzip2/tar)

**Claves SSH y red cifrada (13→17)**
- [[14-nivel-13-a-14]] — clave privada SSH (`ssh -i`)
- [[15-nivel-14-a-15]] — `nc` a un puerto
- [[16-nivel-15-a-16]] — `openssl s_client` (TLS)
- [[17-nivel-16-a-17]] — `nmap` + openssl + clave

**diff y SSH no interactivo (17→19)**
- [[18-nivel-17-a-18]] — `diff`
- [[19-nivel-18-a-19]] — comando por SSH sin shell interactiva

**setuid y cron (19→24)**
- [[20-nivel-19-a-20]] — binario setuid
- [[21-nivel-20-a-21]] — `nc` listener + setuid
- [[22-nivel-21-a-22]] — cron (`/etc/cron.d/`)
- [[23-nivel-22-a-23]] — cron + `md5sum`/`cut`
- [[24-nivel-23-a-24]] — cron que ejecuta tu script

**Bucles y shells restringidos (24→27)**
- [[25-nivel-24-a-25]] — fuerza bruta (bucle `for` + `nc`)
- [[26-nivel-25-a-26]] — escapar de `more`/`vi` (truco del tamaño de ventana)
- [[27-nivel-26-a-27]] — shell por `vi` + setuid

**Git (27→32)**
- [[28-nivel-27-a-28]] — `git clone` por SSH
- [[29-nivel-28-a-29]] — `git log`/`git show` (historial)
- [[30-nivel-29-a-30]] — ramas (`git branch`/`checkout`)
- [[31-nivel-30-a-31]] — tags (`git tag`/`show`)
- [[32-nivel-31-a-32]] — `git add -f` + `push`

**Truco de shell / final**
- [[33-nivel-32-a-33]] — escapar del "uppercase shell" con `$0` (nivel 33 = final)

## Mi progreso (rellena a mano)
> Bajo riesgo (es un juego), pero por hábito: **no subas este archivo con contraseñas a un repo público**.

| Nivel | Qué aprendí | | Contraseña obtenida |
| ----- | ----------------------- | --- | -------------------------------- |
| 0→1   | ssh, ls, cat            |     |                                  |
| 1→2   | archivo `-`             |     |                                  |
| 2→3   | espacios/escape         |     | <contrasena> |
| 3→4   | `ls -a`                 |     | <contrasena> |
| 4→5   | `file`                  |     | <contrasena> |
| 5→6   | `find` props            |     | <contrasena> |
| 6→7   | `find /` user/group     |     | <contrasena> |
| 7→8   | `grep`                  |     | <contrasena> |
| 8→9   | `sort`+`uniq -u`        |     | <contrasena> |
| 9→10  | `strings`               |     | <contrasena> |
| 10→11 | `base64`                |     | <contrasena> |
| 11→12 | ROT13 `tr`              |     | <contrasena> |
| 12→13 | `xxd`+descompresión     |     | <contrasena> |
| 13→14 | `ssh -i`                |     | <contrasena> |
| 14→15 | `nc`                    |     | <contrasena> |
| 15→16 | `openssl s_client`      |     | <contrasena> |
| 16→17 | `nmap`+key              |     |                                  |
| 17→18 | `diff`                  |     | <contrasena> |
| 18→19 | ssh no interactivo      |     | <contrasena> |
| 19→20 | setuid                  |     | <contrasena> |
| 20→21 | `nc -l`+setuid          |     | <contrasena> |
| 21→22 | cron                    |     | <contrasena> |
| 22→23 | cron+`md5sum`           |     | <contrasena> |
| 23→24 | cron ejecuta tu script  |     | <contrasena> |
| 24→25 | fuerza bruta `for`+`nc` |     | <contrasena> |
| 25→26 | escapar `more`/`vi`     |     |                                  |
| 26→27 | `vi` shell+setuid       |     |                                  |
| 27→28 | `git clone`             |     |                                  |
| 28→29 | `git log`/`show`        |     |                                  |
| 29→30 | ramas git               |     |                                  |
| 30→31 | tags git                |     |                                  |
| 31→32 | `git add -f`+push       |     |                                  |
| 32→33 | `$0` (uppercase shell)  |     |                                  |

## Conexiones
- [[MOC_Ciberseguridad]] · [[12-aprender-y-carrera]] — práctica y labs
- [[13-herramientas-en-detalle]] — las herramientas que vas usando
- [[git-en-detalle]] — refuerza los niveles 27-32 (git)
- Clúster de **Linux** — chuleta de comandos/atajos de terminal


