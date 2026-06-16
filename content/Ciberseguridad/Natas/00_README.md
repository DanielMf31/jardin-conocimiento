---
title: OverTheWire Natas — guía y progreso
date: 2026-06-14
tags: [ciberseguridad, web, owasp, natas, wargame, meta]
type: nota
status: en-progreso
source: claude-code
aliases: [Natas README, Natas guia, OverTheWire Natas]
---

# 🕸️ OverTheWire Natas — guía y progreso

Wargame **legal y educativo** de **seguridad web** (0→34). El de **más retorno para ti como dev**:
cada nivel es una vulnerabilidad web real (las del [[04-seguridad-web-owasp|OWASP Top 10]]) que aprendes
a explotar y, por tanto, a **defender** en tus propias apps. No usa SSH: se juega en el **navegador**.

## Cómo se juega
1. Abres en el navegador:
```
http://natasN.natas.labs.overthewire.org
```
   Usuario `natasN`, contraseña la que conseguiste en el nivel anterior. **`natas0` / `natas0`** para empezar.
2. Cada nivel esconde la contraseña del siguiente (`/etc/natas_webpass/natasN+1` en el servidor, o en la página).
3. Muchísimos retos se resuelven más cómodo con **`curl`** (cabeceras, cookies, POST) o **Burp Suite**.
4. Página oficial: https://overthewire.org/wargames/natas/

> Úsalos así: intenta el nivel tú primero; si te atascas, mira el paso concreto. **No leas la solución entera de golpe.**

> ⚖️ Ético: es un laboratorio autorizado. Lo aprendido es para **proteger** tus propias webs.

## 📚 Walkthroughs (por bloques temáticos)
**Lo básico — fuente, ficheros, cabeceras, cookies (0→7)**
- [[Natas/01-nivel-0-a-1]] — secreto en el código fuente HTML
- [[Natas/02-nivel-1-a-2]] — el clic derecho no es seguridad
- [[Natas/03-nivel-2-a-3]] — directory listing (`/files/`)
- [[Natas/04-nivel-3-a-4]] — `robots.txt` filtra rutas
- [[Natas/05-nivel-4-a-5]] — falsificar cabecera `Referer`
- [[Natas/06-nivel-5-a-6]] — cookie `loggedin` manipulable
- [[Natas/07-nivel-6-a-7]] — fichero `include` accesible

**Inclusión, codificación e inyección de comandos (7→11)**
- [[Natas/08-nivel-7-a-8]] — LFI (`?page=/etc/...`)
- [[Natas/09-nivel-8-a-9]] — ofuscar ≠ cifrar (base64/strrev/hex)
- [[Natas/10-nivel-9-a-10]] — command injection (`passthru` + grep)
- [[Natas/11-nivel-10-a-11]] — filtro insuficiente; abusar de grep

**Cripto de juguete y subida de ficheros (11→14)**
- [[Natas/12-nivel-11-a-12]] — cookie XOR con clave reutilizada
- [[Natas/13-nivel-12-a-13]] — subir `.php` y ejecutarlo (RCE)
- [[Natas/14-nivel-13-a-14]] — bypass de `exif_imagetype` (magic bytes)

**SQL injection (14→18)**
- [[Natas/15-nivel-14-a-15]] — SQLi en login
- [[Natas/16-nivel-15-a-16]] — blind SQLi booleana
- [[Natas/17-nivel-16-a-17]] — inyección de comandos como oráculo
- [[Natas/18-nivel-17-a-18]] — blind SQLi por tiempo (`SLEEP`)

**Sesiones (18→22)**
- [[Natas/19-nivel-18-a-19]] — session id predecible (1-640)
- [[Natas/20-nivel-19-a-20]] — session id en hex predecible
- [[Natas/21-nivel-20-a-21]] — inyección de saltos de línea en sesión
- [[Natas/22-nivel-21-a-22]] — apps que comparten sesión

**Lógica PHP y type juggling (22→25)**
- [[Natas/23-nivel-22-a-23]] — `header()` no detiene la ejecución
- [[Natas/24-nivel-23-a-24]] — type juggling (`"11iloveyou" > 10`)
- [[Natas/25-nivel-24-a-25]] — `strcmp` con array → NULL

**Avanzado — RCE, deserialización, cripto, Perl (25→34)**
- [[Natas/26-nivel-25-a-26]] — LFI + log poisoning
- [[Natas/27-nivel-26-a-27]] — PHP object injection (`unserialize`)
- [[Natas/28-nivel-27-a-28]] — truncamiento de columnas SQL
- [[Natas/29-nivel-28-a-29]] — AES-ECB maleable (cut & paste de bloques)
- [[Natas/30-nivel-29-a-30]] — Perl `open()` con pipe
- [[Natas/31-nivel-30-a-31]] — SQLi en Perl DBI (params como array)
- [[Natas/32-nivel-31-a-32]] — Perl `ARGV`/diamante `<>`
- [[Natas/33-nivel-32-a-33]] — Perl: de leer ficheros a RCE
- [[Natas/34-nivel-33-a-34]] — PHAR deserialization (nivel 34 = final)

> ⚠️ Del **25 en adelante** las técnicas son intrincadas (deserialización, ECB, Perl). Los docs explican
> bien *la técnica*, pero el payload exacto puede necesitar ajuste fino contra el reto en vivo. Trátalos
> como guía conceptual y verifica jugando.

## 📋 Mi progreso (rellena a mano)
> ⚠️ Bajo riesgo (es un juego), pero por hábito: **no subas este archivo con contraseñas a un repo público**.

| Nivel | Tema                          | ✓   | Contraseña obtenida |
| ----- | ----------------------------- | --- | ------------------- |
| 0→1   | fuente HTML                   |     |                     |
| 1→2   | clic derecho                  |     |                     |
| 2→3   | directory listing             |     |                     |
| 3→4   | `robots.txt`                  |     |                     |
| 4→5   | `Referer`                     |     |                     |
| 5→6   | cookie `loggedin`             |     |                     |
| 6→7   | `include` accesible           |     |                     |
| 7→8   | LFI                           |     |                     |
| 8→9   | ofuscación reversible         |     |                     |
| 9→10  | command injection             |     |                     |
| 10→11 | abusar de grep                |     |                     |
| 11→12 | cookie XOR                    |     |                     |
| 12→13 | subir `.php`                  |     |                     |
| 13→14 | bypass magic bytes            |     |                     |
| 14→15 | SQLi login                    |     |                     |
| 15→16 | blind SQLi booleana           |     |                     |
| 16→17 | oráculo de comandos           |     |                     |
| 17→18 | blind SQLi por tiempo         |     |                     |
| 18→19 | session id 1-640              |     |                     |
| 19→20 | session id hex                |     |                     |
| 20→21 | salto de línea en sesión      |     |                     |
| 21→22 | sesión compartida             |     |                     |
| 22→23 | `header()` sin `exit`         |     |                     |
| 23→24 | type juggling `>`             |     |                     |
| 24→25 | `strcmp` array                |     |                     |
| 25→26 | LFI + log poisoning           |     |                     |
| 26→27 | object injection              |     |                     |
| 27→28 | truncamiento SQL              |     |                     |
| 28→29 | AES-ECB                       |     |                     |
| 29→30 | Perl `open()`                 |     |                     |
| 30→31 | Perl DBI array                |     |                     |
| 31→32 | Perl `ARGV`/`<>`              |     |                     |
| 32→33 | Perl RCE                      |     |                     |
| 33→34 | PHAR deserialization          |     |                     |

## Conexiones
- [[MOC_Ciberseguridad]] · [[04-seguridad-web-owasp]] — la teoría de cada vulnerabilidad
- [[13-herramientas-en-detalle]] — `curl`, Burp Suite, etc.
- [[Bandit/00_README]] · [[Leviathan/00_README]] — los otros wargames
- **PortSwigger Web Security Academy** — complemento perfecto de Natas (gratis)
