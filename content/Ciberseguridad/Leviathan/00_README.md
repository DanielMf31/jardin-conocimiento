---
title: OverTheWire Leviathan — guía y progreso
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, leviathan, wargame, meta]
type: nota
status: en-progreso
source: claude-code
aliases: [Leviathan README, Leviathan guia, OverTheWire Leviathan]
---

# OverTheWire Leviathan — guía y progreso

Wargame **legal y educativo**, el paso natural **después de Bandit**. Más corto (8 niveles, 0→7) y
con un foco claro: **binarios setuid mal programados** y cómo abusarlos para escalar de un usuario al
siguiente. Aquí tienes el walkthrough de todos los niveles + tu tabla de progreso.

## Cómo se juega
1. Te conectas al nivel N:
```bash
ssh leviathanN@leviathan.labs.overthewire.org -p 2223
```
   (El nivel 0 usa la contraseña `leviathan0`. Ojo: **puerto 2223**, no el 2220 de Bandit.)
2. Resuelves el reto → la contraseña del siguiente nivel suele estar en `/etc/leviathan_pass/leviathanN+1`.
3. `exit` y entras al siguiente. El **nivel 7 es el final** (mensaje de felicitación).
4. Páginas oficiales con pistas: https://overthewire.org/wargames/leviathan/

> Úsalos así: intenta el nivel tú primero; si te atascas, mira el paso concreto. **No leas la solución entera de golpe.**

> Concepto transversal: casi todos los niveles giran en torno a un **binario SUID** (corre con los
> privilegios de su dueño). Tus dos herramientas estrella: `ltrace` (ver qué llamadas hace el binario,
> p.ej. con qué cadena compara tu contraseña) y los **symlinks** (engañar a un binario para que lea un
> fichero protegido). Conecta con [[06-seguridad-de-sistemas-y-hardening]].

## Walkthroughs (todos los niveles)
- [[Leviathan/01-nivel-0-a-1]] — archivos ocultos (`.backup/`) + `grep`
- [[Leviathan/02-nivel-1-a-2]] — binario setuid + `ltrace` (1)
- [[Leviathan/03-nivel-2-a-3]] — `system()` sin comillas: truco del espacio + symlink
- [[Leviathan/04-nivel-3-a-4]] — binario setuid + `ltrace` (2)
- [[Leviathan/05-nivel-4-a-5]] — salida en binario → ASCII (`perl pack`)
- [[Leviathan/06-nivel-5-a-6]] — symlink a fichero protegido (`/tmp/file.log`)
- [[Leviathan/07-nivel-6-a-7]] — fuerza bruta de PIN de 4 dígitos (nivel 7 = final)

## Mi progreso (rellena a mano)
> Bajo riesgo (es un juego), pero por hábito: **no subas este archivo con contraseñas a un repo público**.

| Nivel | Qué aprendí | | Contraseña obtenida |
| ----- | ------------------------------- | --- | ------------------- |
| 0→1   | archivos ocultos + `grep`       |     |                     |
| 1→2   | setuid + `ltrace`               |     |                     |
| 2→3   | `system()` + espacio + symlink  |     |                     |
| 3→4   | setuid + `ltrace`               |     |                     |
| 4→5   | binario → ASCII                 |     |                     |
| 5→6   | symlink a fichero protegido     |     |                     |
| 6→7   | fuerza bruta PIN 4 dígitos      |     |                     |

## Conexiones
- [[MOC_Ciberseguridad]] · [[Bandit/00_README]] — el wargame anterior
- [[06-seguridad-de-sistemas-y-hardening]] — setuid, privesc, hardening
- [[13-herramientas-en-detalle]] — `ltrace` y compañía
- Clúster de **Linux** — permisos, symlinks, terminal
