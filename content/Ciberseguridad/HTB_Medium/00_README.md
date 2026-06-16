---
title: HTB Máquinas Medium — 5 ejemplos detallados
date: 2026-06-15
tags: [ciberseguridad, htb, pentesting, medium, meta]
type: nota
status: en-progreso
source: claude-code
aliases: [HTB Medium, HTB medium ejemplos]
---

# 🟡 HTB Máquinas Medium — 5 ejemplos ultra-detallados

**5 máquinas Medium** resueltas paso a paso para **ver cómo se hacen** y absorber la metodología. No es
una colección exhaustiva (el resto de Medium se aprenden haciéndolas con IppSec/0xdf) — son ejemplos
elegidos para cubrir el **máximo de técnicas distintas**, incluida la primera de **Active Directory**.

> ⚖️ HTB es un laboratorio **legal y autorizado**. Esto es para aprender a **defender y diseñar mejor**.

## El salto Easy → Medium
En Easy era *1 vulnerabilidad + 1 privesc*. En Medium **encadenas 4-6 piezas** y la dificultad está en
la **enumeración fina**: la puerta la abre un detalle que hay que *cazar* (un certificado TLS, un puerto
interno, un share anónimo, un fichero de config). El exploit rara vez es lo difícil; **encontrarlo** sí.

## 📚 Las 5 máquinas
| # | Máquina | SO | Cadena (qué técnicas verás) |
|---|---|---|---|
| 01 | [[HTB_Medium/01-mango]] | Linux | cert TLS (vhosts) → **NoSQL injection** ($ne/$regex) → extracción ciega → SUID `jjs` |
| 02 | [[HTB_Medium/02-magic]] | Linux | SQLi login → **upload polyglot imagen-PHP** → `mysqldump` creds → **SUID PATH hijack** |
| 03 | [[HTB_Medium/03-openadmin]] | Linux | **CVE RCE** (OpenNetAdmin) → reuso creds → servicio interno filtra **clave SSH** → crack passphrase → `sudo nano` |
| 04 | [[HTB_Medium/04-solidstate]] | Linux | **Apache James** admin por defecto → leer correos → escape **rbash** → cron escribible |
| 05 | [[HTB_Medium/05-active]] | Windows | **Active Directory**: SMB anónimo → GPP `cpassword` (MS14-025) → **Kerberoasting** → Domain Admin |

## 🧠 Los patrones que se repiten (la teoría)
- **Enumeración fina = la llave**: certificados TLS (vhosts), puertos internos (`netstat`/`ss`), shares anónimos, ficheros de config. Mira *todo*.
- **Inyección por no validar tipos/entrada**: NoSQLi (`mango`), SQLi (`magic`) — el servidor confía en lo que llega.
- **Subida de ficheros mal validada**: polyglots que pasan `getimagesize` (`magic`).
- **Credenciales que viajan**: en config, en correos, reutilizadas entre servicio↔SSH (`magic`, `openadmin`, `solidstate`).
- **Privesc recurrente**: SUID peligroso (`jjs`), **PATH hijacking** de SUID con rutas relativas (`magic`), `sudo` + GTFOBins (`openadmin` nano), **cron escribible** (`solidstate`).
- **Active Directory** (el núcleo profesional): SMB anónimo → secretos en SYSVOL (GPP) → **Kerberoasting** (pedir TGS de cuentas con SPN y crackearlos offline) → Domain Admin.

> 💡 Reflejo dev/purple team en cada paso: *prepared statements* (inyección), validar uploads en servidor + carpeta no ejecutable, **no reutilizar credenciales**, rutas absolutas y mínimos SUID, contraseñas largas en cuentas de servicio (mata el Kerberoasting), parche MS14-025.

## 📋 Mi progreso
| Máquina | user | root | Notas |
|---|---|---|---|
| mango | | | |
| magic | | | |
| openadmin | | | |
| solidstate | | | |
| active | | | |

## Cómo seguir con el resto de Medium (sin estos docs)
1. Elige una máquina de la **lista TJnull** (OSCP-like) o el camino de HTB.
2. Intenta tú primero; cronométrate enumerando a fondo antes de mirar nada.
3. Si te atascas >30-45 min en un punto, mira **solo ese paso** en **IppSec** (vídeo) o **0xdf** (escrito).
4. Después de rootearla, **escribe tú el writeup** (tu propio doc): es donde de verdad se fija el patrón.

## Conexiones
- [[MOC_Ciberseguridad]] · [[12-aprender-y-carrera]] — ruta y certificaciones
- [[HTB_Easy/00_README]] — el paso anterior · [[HTB_Starting_Point/00_README]]
- [[05-identidad-auth-y-secretos]] — credenciales/Kerberos · [[06-seguridad-de-sistemas-y-hardening]] — privesc
- [[04-seguridad-web-owasp]] — inyecciones/upload · [[08-vulnerabilidades-y-explotacion]] — CVEs
- [[07-pentesting-y-ciclo-del-ataque]] · [[13-herramientas-en-detalle]] — impacket, hashcat, ssh2john…
- **IppSec** (YouTube) y **0xdf.gitlab.io** — referencia de cada máquina
