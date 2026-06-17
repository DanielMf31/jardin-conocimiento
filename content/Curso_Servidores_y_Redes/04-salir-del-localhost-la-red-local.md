---
title: Sesión 4 — Salir del localhost a la red local
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 4 Servidores, Red Local LAN]
---

# Sesión 4 — Salir del localhost a la red local

> **Objetivo**: dejar de servir "solo para tu máquina" y exponer el servidor en la red
> local, de modo que **otro portátil** (o, más adelante, la Raspberry) lo alcance escribiendo
> tu IP en el navegador o en `curl`.
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: un compañero, desde su portátil, hace
> `curl http://192.168.1.50:8000/led` y recibe la respuesta de **tu** servidor.

## Requisitos previos

- Sesiones 1–3 hechas: tienes un servidor FastAPI con `GET /led`, `POST /led` y validación
  Pydantic ([[03-json-y-validacion-pydantic]]).
- Saber arrancar el servidor con `uvicorn` y probarlo con `curl` en local
  ([[02-curl-y-los-verbos-http]]).
- Estar **en la misma red local** que el resto de la sala (mismo router/switch).

## El checkpoint de hoy

```bash
./bin/sesion.sh 4             # esqueleto de la Sesión 4
./bin/sesion.sh 4 --solucion  # si te atascas
```

Hoy casi no se escribe código: el cambio es de **una línea de arranque**. El `# TODO` está
en cómo lanzas `uvicorn` (en qué interfaz escucha) y en averiguar y compartir tu IP. El
servidor en sí no cambia.

## Teoría

Esta es la sesión-núcleo de **redes**. El proyecto acaba de chocar contra un muro real: "en
mi máquina funciona, pero mi compañero no me ve". Toca explicar por qué.

### `127.0.0.1` / `localhost` vs `0.0.0.0`

Cuando un servidor arranca, elige **en qué interfaz de red escucha** (a qué "puerta de la
casa" se asoma):

| Dirección de bind | Significa | Quién te alcanza |
|---|---|---|
| `127.0.0.1` (= `localhost`) | la interfaz de *loopback*, interna | **solo** procesos de tu propia máquina |
| `0.0.0.0` | "todas mis interfaces de red" | cualquiera que llegue por tu IP en la LAN |

Hasta ahora servíamos en `127.0.0.1`: comodísimo para desarrollar, pero **invisible** para
el resto. `127.0.0.1` es una calle privada dentro de tu casa; nadie de fuera puede entrar
aunque sepa que existe. `0.0.0.0` no es "una IP a la que conectarse", es una forma de decirle
al servidor *"acepta conexiones que entren por cualquiera de mis direcciones"*.

```
   Servidor en 127.0.0.1:8000              Servidor en 0.0.0.0:8000
   ┌──────────────────┐                    ┌──────────────────┐
   │  tu máquina       │                   │  tu máquina       │
   │  ┌────┐           │                   │  ┌────┐           │
   │  │curl│──► 8000 [OK] │                   │  │curl│──► 8000 [OK] │
   │  └────┘           │                   │  └────┘           │
   └──────────────────┘                    └────────▲─────────┘
        compañero  ──► [NO] (no existe                  │ 192.168.1.50:8000
                        para él)              compañero ──► [OK]
```

### IP: la dirección de tu máquina

Una **IP** es la dirección de un equipo en una red, como un número de portal. Dos familias:

| Tipo | Para qué | Ejemplos | Visible desde |
|---|---|---|---|
| **Privada** | dentro de una red local (LAN) | `192.168.x.x`, `10.x.x.x`, `172.16–31.x.x` | solo la propia LAN |
| **Pública** | en internet, única en el mundo | la que da tu operador al router | todo internet |

En el curso vivimos **enteros en IPs privadas** `192.168.1.x`: sin internet, sin abrir
puertos al exterior, sin túneles. Más simple y más seguro. Tu portátil tendrá algo como
`192.168.1.50`; la Raspberry, `192.168.1.60`.

### Puerto: la "puerta" dentro de la máquina

La IP lleva el paquete **a la máquina**; el **puerto** decide **qué programa** dentro de ella
lo recibe. Una máquina tiene 65.535 puertas numeradas. Nuestro servidor escucha en el `8000`.
`192.168.1.50:8000` se lee como *"casa 50, puerta 8000"*.

### TCP/IP por capas (alto nivel, lo justo)

No hace falta el modelo OSI entero. Tres ideas:

```
   ┌──────────────────────────────────────────────┐
   │  HTTP        ← lo que ya conoces: GET /led     │
   ├──────────────────────────────────────────────┤
   │  TCP   = conexión fiable (entrega ordenada,    │
   │          reintenta lo perdido) + PUERTO        │
   ├──────────────────────────────────────────────┤
   │  IP    = direccionar y enrutar paquetes        │
   │          (la DIRECCIÓN de la máquina)          │
   └──────────────────────────────────────────────┘
```

- **IP** pone la dirección en el sobre y lo lleva por la red.
- **TCP** garantiza que llega completo, en orden, y abre una "conversación" fiable; aquí
  viven los **puertos**.
- **HTTP** es la carta que va dentro. Todo lo de las sesiones 2–3 viajaba ya sobre TCP/IP
  sin que lo notaras (porque era todo dentro de tu máquina).

### Cómo ver tu IP

| Sistema | Comando | Dónde mirar |
|---|---|---|
| Linux / WSL | `ip a` (o `ip addr`) | la línea `inet 192.168.1.xx` de tu interfaz wifi/eth |
| macOS | `ifconfig` | `inet` bajo `en0` |
| Windows | `ipconfig` | "Dirección IPv4" del adaptador activo |

Ignora `127.0.0.1` (loopback) y direcciones `169.254.x.x` (significa "no conseguí IP"). La
buena es la `192.168.1.x`. Ver `ip` y `ping` en [[MOC_Linux]].

### `ping`: ¿me llega siquiera el paquete?

Antes de culpar al servidor, comprueba la **conectividad** pura:

```bash
ping 192.168.1.50      # ¿responde la máquina del compañero?
```

Si `ping` responde pero `curl` no, el problema está por encima de IP (puerto, firewall,
servidor en `127.0.0.1`). Si `ping` **no** responde, ni siquiera os veis en la red:
distinta red, wifi de invitados, cable, etc.

### El firewall puede bloquear el puerto

Aunque el servidor escuche en `0.0.0.0`, el **firewall** del sistema operativo puede tirar
los paquetes que llegan al puerto 8000. Es la causa nº 1 de "ping sí, curl no". En la sala,
para desarrollo en LAN, basta permitir el puerto temporalmente (Linux/UFW:
`sudo ufw allow 8000`; Windows: regla de entrada para el puerto 8000). En Windows el primer
arranque suele lanzar un diálogo: hay que decir **"permitir en redes privadas"**.

### ¿Por qué IPs y no nombres? (DNS, de pasada)

En internet escribes `ejemplo.com` y un servicio llamado **DNS** lo traduce a una IP. En
nuestra LAN no montamos DNS, así que usamos la **IP directa**. Más adelante molesta que la
IP cambie; por eso a las Raspberry les damos IP fija. (Profundizar redes/DNS en
[[MOC_CS_Fundamentos]].)

## Manos a la obra

### 1. Cambiar el bind a `0.0.0.0` (el `# TODO`)

Hasta ahora arrancabas así (solo tú te ves):

```bash
# ANTES — invisible para la red
uvicorn servidor.main:app --reload --host 127.0.0.1 --port 8000
```

El cambio de hoy:

```bash
# DESPUÉS — escucha en todas las interfaces de la máquina
uvicorn servidor.main:app --host 0.0.0.0 --port 8000
```

> Nota: `--reload` (recarga al guardar) es para desarrollar; puedes dejarlo. Lo único
> imprescindible hoy es `--host 0.0.0.0`.

### 2. Averiguar tu IP y anunciarla

```bash
ip a | grep "inet 192.168"     # Linux/WSL → algo como  inet 192.168.1.50/24
```

Apúntala en el canal de la sala: *"servidor de Ana → 192.168.1.50"*. Esa es la IP que tus
compañeros (y la Raspberry en la Sesión 5) usarán.

### 3. Que un compañero te llame por tu IP

Desde **otra** máquina de la sala:

```bash
curl http://192.168.1.50:8000/led
# {"encendido": false}

curl -X POST http://192.168.1.50:8000/led \
     -H "Content-Type: application/json" \
     -d '{"encendido": true}'
```

Si en tu terminal ves el `LedFalso` imprimir ` LED ON` provocado por **otra** máquina:
objetivo cumplido. Tu servidor ya vive en la red.

### 4. Diagnosticar cuando no responde

```bash
ping 192.168.1.50            # 1) ¿llego a la máquina?       → si no, misma-red/firewall
curl http://192.168.1.50:8000/led   # 2) ¿responde el puerto?  → si no, bind/firewall
```

Y en la máquina servidor, confirma que escucha en `0.0.0.0`:

```bash
ss -tlnp | grep 8000         # debe mostrar  0.0.0.0:8000  (NO 127.0.0.1:8000)
```

## El muro

"Ya me alcanzan por la red local, pero sigo encendiendo un LED *de mentira* que solo imprime
en mi terminal." El siguiente salto es físico: que una **Raspberry Pi** de la sala, hablando
por esta misma red, encienda un **LED real** obedeciendo a tu servidor.
→ [[05-la-raspberry-como-cliente-y-el-led-real]].

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| Compañero recibe `Connection refused` | Sigues escuchando en `127.0.0.1` | Arranca con `--host 0.0.0.0`; verifica con `ss -tlnp \| grep 8000` |
| `ping` va pero `curl` no | Firewall bloquea el puerto 8000 | Permite el puerto (UFW: `sudo ufw allow 8000`; Windows: "permitir en red privada") |
| `ping` no responde | No estáis en la misma red | Misma wifi/switch, no wifi de invitados; comprueba que ambos sois `192.168.1.x` |
| Funcionaba y dejó de ir | La IP cambió (DHCP la reasigna) | Vuelve a mirar `ip a` y reanuncia; para la Pi, usar IP fija |
| `169.254.x.x` al mirar tu IP | No conseguiste IP del router | Reconecta a la red; revisa cable/wifi |

## Guion de la sesión

- **0–10** Repaso: con `curl` local ya enciendes el LedFalso. Pregunta trampa: "¿puede tu
  compañero hacerlo?" → no. Ese es el muro de hoy.
- **10–30** Teoría en pizarra: dibuja `127.0.0.1` vs `0.0.0.0`, el sobre IP + puerta puerto,
  las tres capas TCP/IP. Que cada uno saque su IP con `ip a`/`ipconfig` en vivo.
- **30–80** `./bin/sesion.sh 4`, cambiar el bind a `0.0.0.0`, anunciar IPs en el canal, y por
  parejas llamarse mutuamente con `curl`. Quien falle: `ping` → puerto → firewall, en ese
  orden. Que vean al menos un LedFalso ajeno encenderse en su pantalla.
- **80–90** Puesta en común de qué bloqueaba a cada uno (casi siempre firewall). Plantea el
  muro: "mañana, en vez de un compañero, será una Raspberry, y el LED será de verdad".

## Conexiones
- [[03-json-y-validacion-pydantic]] — la sesión anterior (el server que ahora exponemos)
- [[05-la-raspberry-como-cliente-y-el-led-real]] — la siguiente: LED físico por esta red
- [[Curso_Servidores_y_Redes/00_README]] — visión y diseño del curso
- [[MOC_CS_Fundamentos]] — redes, TCP/IP, DNS (la teoría de fondo)
- [[MOC_Linux]] — `ip`, `ping`, `ss`, firewall
