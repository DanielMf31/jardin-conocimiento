---
title: Sesión 8 — Tiempo real con WebSockets
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 8 WebSockets, Tiempo real push]
---

# Sesión 8 — Tiempo real con WebSockets

> **Objetivo**: sustituir el **polling** (preguntar cada X segundos) por **push**: el servidor
> avisa al instante cuando el estado del LED cambia. El panel web y la Raspberry reaccionan
> sin esperar.
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: dos pestañas con el panel web abiertas; pulsas el botón
> en una y el LED de la otra (y el LED real de la Raspberry) cambian **inmediatamente**, sin
> recargar y sin el retraso del polling.

## Requisitos previos

- Haber completado hasta [[07-persistencia-con-sqlite]]: `GET/POST /led`, telemetría
  persistida, panel web y cliente Pi con polling funcionando.
- Entorno activado: `source .venv/bin/activate`.
- Tener claro qué es el polling actual: el cliente hace `GET /led` repetidamente.

## El checkpoint de hoy

```bash
source .venv/bin/activate
./bin/sesion.sh 8            # te coloca en 'sesion8-inicio'
```

El esqueleto trae un gestor de conexiones casi vacío y un endpoint `/ws` con **tres `# TODO`**:
aceptar/registrar la conexión, quitarla cuando se cierra, y el **broadcast** cuando cambia el
LED. El panel web ya trae el JavaScript que abre el WebSocket, comentado, para activarlo.

```python
# servidor/ws.py  (estado de partida, sesion8-inicio)
class GestorConexiones:
    def __init__(self):
        self.activas = []           # lista de WebSocket conectados

    # TODO (Sesión 8): registrar(ws), quitar(ws), broadcast(mensaje)

gestor = GestorConexiones()
```

## Teoría

### 1. Medir el problema del polling

El polling es: *"el cliente pregunta una y otra vez por si acaso"*. Tiene dos costes.

**Latencia.** Si pregunto cada 4 segundos, un cambio que ocurre justo después de preguntar
no lo veo hasta la siguiente. De media, el retraso es **intervalo / 2**.

```
   intervalo de polling = 4 s
   cambio aquí ▼
   ──┬───────┬───●───┬───────┬──►  tiempo
     pregunta    │   pregunta
                 └── el cliente se entera AQUÍ (hasta 4 s tarde)
```

**Tráfico desperdiciado.** La mayoría de preguntas reciben *"nada nuevo"*. Con muchos clientes
y un intervalo corto, son miles de peticiones inútiles.

| Intervalo | Latencia media | Peticiones/min por cliente |
|---|---|---|
| 4 s | ~2 s | 15 |
| 1 s | ~0.5 s | 60 |
| 0.2 s (para "tiempo real") | ~0.1 s | 300 (¡brutal!) |

Bajar la latencia con polling **dispara** el tráfico. No escala. Necesitamos otra cosa.

### 2. Pull vs Push

| | **Pull (polling)** | **Push (WebSocket)** |
|---|---|---|
| Quién inicia | el cliente, repetidamente | el servidor, cuando hay algo |
| Latencia | hasta un intervalo | inmediata |
| Tráfico | constante (preguntando) | solo cuando cambia |
| Analogía | mirar el buzón cada 5 min | que el cartero llame al timbre |

```
   PULL                                 PUSH
   cliente: ¿algo? ─►                    cliente: (abre conexión y espera)
   server:  no    ◄─                     server:  (calla hasta que cambie)
   cliente: ¿algo? ─►                    ───────── el LED cambia ─────────
   server:  no    ◄─                     server:  ¡el LED está ON! ─►
   cliente: ¿algo? ─►                    cliente: (lo recibe al instante)
   server:  ¡sí!  ◄─
```

### 3. Qué es un WebSocket

> Un WebSocket es una **conexión persistente y bidireccional** entre cliente y servidor, sobre
> TCP. Una vez abierta, **queda abierta** y ambos pueden enviarse mensajes en cualquier momento.

Contrasta con HTTP normal, donde cada petición abre, responde y cierra. El WebSocket:

1. **Arranca con un handshake HTTP**: el cliente pide *"quiero hablar por WebSocket"* (una
   petición HTTP normal con la cabecera `Upgrade: websocket`).
2. El servidor acepta (`101 Switching Protocols`) y **la misma conexión TCP** deja de ser HTTP
   y pasa a ser un canal abierto.
3. A partir de ahí, mensajes en ambos sentidos hasta que alguien cierra.

```
   CLIENTE                                   SERVIDOR
     │  ── GET /ws  (Upgrade: websocket) ──►   │   handshake HTTP
     │  ◄── 101 Switching Protocols ─────────  │
     │ ═══════ canal abierto y persistente ════│
     │  ◄────────── "LED: ON" ───────────────  │   push del server
     │  ───────────  ping  ──────────────────► │   bidireccional
     │ ═══════════════════════════════════════ │
```

Por la URL se distingue: `ws://` (o `wss://` cifrado) en vez de `http://`.

### 4. Cuándo usarlo y cuándo no

| Úsalo cuando | NO hace falta cuando |
|---|---|
| Hay cambios en tiempo real (estado, chat, posiciones) | Pides un dato una vez y ya |
| El servidor necesita avisar él (push) | Operaciones puntuales (login, subir un fichero) |
| Muchos clientes mirando el mismo estado | El estado cambia muy rara vez |

Para nuestro LED encaja perfecto: muchos miran, cambia de golpe, queremos verlo al instante.

### 5. Patrón de broadcast

Hay **varios** clientes conectados (dos pestañas, la Raspberry...). Cuando el LED cambia, hay
que avisar a **todos**. Eso es un *broadcast*: el servidor guarda una **lista de conexiones
activas** y, al cambiar el estado, recorre la lista y manda el mensaje a cada una.

```
                        ┌─► pestaña 1
   POST /led cambia ──► broadcast ──┼─► pestaña 2
   el estado           (recorre     └─► Raspberry (LED real)
                        la lista)
```

Tres operaciones sobre la lista: **registrar** (al conectar), **quitar** (al desconectar) y
**broadcast** (mandar a todos). Más sobre redes y TCP en [[MOC_CS_Fundamentos]].

## Manos a la obra

**1) Colocarse en el checkpoint:**

```bash
source .venv/bin/activate
./bin/sesion.sh 8
```

**2) Completar el gestor de conexiones (registrar / quitar / broadcast):**

```python
# servidor/ws.py  (solución)
class GestorConexiones:
    def __init__(self):
        self.activas = []

    async def registrar(self, ws):
        await ws.accept()              # completa el handshake
        self.activas.append(ws)

    def quitar(self, ws):
        if ws in self.activas:
            self.activas.remove(ws)    # ¡clave! si no, la lista crece

    async def broadcast(self, mensaje: dict):
        muertas = []
        for ws in self.activas:
            try:
                await ws.send_json(mensaje)
            except Exception:
                muertas.append(ws)     # socket caído: márcalo
        for ws in muertas:
            self.quitar(ws)            # límpialo de la lista

gestor = GestorConexiones()
```

- `ws.accept()` completa el handshake (acepta el `Upgrade`).
- `quitar` evita que la lista crezca con conexiones muertas.
- En `broadcast`, enviar a un socket cerrado lanza excepción: lo capturamos y lo retiramos en
  vez de petar.

**3) El endpoint `/ws`:**

```python
# servidor/main.py  (solución, fragmento)
from fastapi import WebSocket, WebSocketDisconnect
from servidor.ws import gestor

@app.websocket("/ws")
async def ws_led(ws: WebSocket):
    await gestor.registrar(ws)
    try:
        while True:
            await ws.receive_text()    # mantiene la conexión viva
    except WebSocketDisconnect:
        gestor.quitar(ws)              # se desconectó: límpialo
```

El `while True` con `receive_text()` mantiene la corrutina viva escuchando. Cuando el cliente
cierra, salta `WebSocketDisconnect` y quitamos la conexión.

**4) Hacer broadcast al cambiar el LED:**

```python
# servidor/main.py  (solución, fragmento)
@app.post("/led")
async def cambiar_led(comando: ComandoLed):
    estado_actual = comando.encendido          # lógica existente
    await gestor.broadcast({"encendido": estado_actual})   # ◄── avisar a todos
    return {"encendido": estado_actual}
```

**5) Suscribirse desde el panel web:**

```javascript
// panel/app.js  (fragmento) — usa la IP del servidor en la LAN
const ws = new WebSocket("ws://192.168.1.50:8000/ws");

ws.onmessage = (evento) => {
    const datos = JSON.parse(evento.data);
    actualizarLed(datos.encendido);     // refresca la UI al instante
};
```

La Raspberry hace lo mismo desde Python (suscribirse a `/ws` y encender el LED real con el
mensaje recibido), reemplazando su bucle de polling.

**6) Comparar latencias (el momento de la verdad):**

Abre **dos pestañas** del panel. Pulsa el botón en una y observa la otra: cambia al instante.
Compáralo mentalmente con el polling de la [[06-panel-web-en-el-navegador]], donde había que
esperar al siguiente sondeo. Y el LED real de la Raspberry cambia ya, sin el retraso de antes.

## El muro

Es satisfactorio... hasta que alguien dice: *"un momento. Ahora **cualquiera** conectado a la
red puede abrir la web, o mandar un `POST /led`, y encender o apagar mi LED. No hay nada que
lo impida. Eso es un problema de seguridad."*.

Tiene toda la razón. Eso es lo que aborda la [[09-seguridad-y-secretos]]: que solo quien tenga
la clave pueda mandar comandos.

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| La memoria sube con el tiempo / clientes "fantasma" | No se quitan las conexiones cerradas | Llamar a `quitar(ws)` en `WebSocketDisconnect` y en el broadcast |
| El broadcast peta a mitad | Se intenta enviar a un socket muerto | Envolver el `send` en `try/except` y retirar el socket caído |
| El navegador da error de conexión / mixed content | Se mezcla `ws://` con `http://` (o `wss://` con `https://`) | Usar `ws://` si la web es `http://`; deben ir a juego |
| La app entera se congela al hacer broadcast | Código bloqueante dentro del event loop (`time.sleep`, I/O síncrona) | Usar `async`/`await`; no bloquear la corrutina |
| `WebSocket connection failed` | URL/IP/puerto mal, o el server no escucha en la LAN | Revisar `ws://192.168.1.50:8000/ws` y que Uvicorn use `--host 0.0.0.0` |
| El handshake no se completa | Falta `await ws.accept()` | Aceptar la conexión antes de usarla |

## Guion de la sesión

| Tramo | Qué hacer |
|---|---|
| **0–10** | Recordar el polling de la Sesión 6. Medir el problema: latencia ≈ intervalo/2 y tráfico desperdiciado. Tabla en pizarra. |
| **10–35** | Teoría: pull vs push, qué es un WebSocket (handshake HTTP → canal persistente), cuándo usarlo, patrón broadcast. |
| **35–75** | `./bin/sesion.sh 8`, completar gestor (registrar/quitar/broadcast), endpoint `/ws`, broadcast en `POST /led`, activar el JS del panel. |
| **75–85** | Demo: dos pestañas + LED real reaccionando al instante. Comparar con el polling. |
| **85–90** | **El muro**: "cualquiera en la red puede encender mi LED" → presentar Sesión 9. |

## Conexiones

- [[07-persistencia-con-sqlite]] — sesión anterior: histórico persistido
- [[06-panel-web-en-el-navegador]] — el panel y el polling que hoy sustituimos
- [[09-seguridad-y-secretos]] — sesión siguiente: proteger quién puede mandar comandos
- [[04-salir-del-localhost-la-red-local]] — escuchar en la LAN (`--host 0.0.0.0`)
- [[MOC_CS_Fundamentos]] — TCP, conexiones persistentes y redes
- [[MOC_Programacion]] — área padre
