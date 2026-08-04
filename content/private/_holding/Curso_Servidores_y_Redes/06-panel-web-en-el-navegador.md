---
title: Sesión 6 — Panel web en el navegador
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 6 Servidores, Panel Web LED]
---

# Sesión 6 — Panel web en el navegador

> **Objetivo**: servir desde el propio FastAPI una página web con botones **ON/OFF** y la
> telemetría, de modo que se controle el LED desde el navegador sin tocar `curl`.
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: abres `http://192.168.1.50:8000/` en el navegador,
> pulsas un botón y el LED (falso o real) obedece; en pantalla se ve el estado actualizándose.

## Requisitos previos

- Sesión 5 hecha: el cliente de la Pi enciende el LED real por polling
  ([[05-la-raspberry-como-cliente-y-el-led-real]]).
- El servidor tiene `GET /led`, `POST /led` y, idealmente, un `GET /telemetria` (estado +
  algún dato como última hora de cambio). Si no, hoy añadimos un endpoint mínimo.
- Nociones básicas de HTML (se dan al vuelo).

## El checkpoint de hoy

```bash
./bin/sesion.sh 6
./bin/sesion.sh 6 --solucion
```

Hoy se toca **el servidor** (servir la página) y se crea **`web/index.html`**. Los `# TODO`:
1. en el servidor, una ruta `GET /` que **devuelve el HTML**;
2. en el HTML, los `fetch()` de los **botones** (`POST /led`) y el de **refrescar**
   (`GET /telemetria`).

## Teoría

El cliente de la Sesión 5 era un script de Python. Hoy el cliente es el actor más universal
que existe: el **navegador**.

### Un frontend mínimo y el navegador como cliente HTTP

Un **frontend** es la parte que ve y toca el usuario. El nuestro será mínimo: un `.html` con
dos botones y un texto, sin frameworks (**vanilla** JS). La clave conceptual:

> El navegador es, literalmente, **otro cliente HTTP**, como `curl` o como el script de la
> Pi. Cuando pulsas un botón, JavaScript hace exactamente las mismas peticiones
> `GET /led` / `POST /led` que ya hacías a mano.

```
   ┌──────────────────────────┐   HTTP    ┌─────────────────────────┐
   │  NAVEGADOR (cliente)      │ ───────►  │  TU FastAPI (servidor)   │
   │  - pinta el HTML          │  fetch()  │  - GET /  → devuelve HTML│
   │  - botón ON → POST /led   │ ◄───────  │  - POST /led → cambia    │
   │  - cada 2s → GET /telem.  │   JSON    │  - GET /telemetria       │
   └──────────────────────────┘           └─────────────────────────┘
```

### `fetch()`: llamar a tu propia API desde el navegador

`fetch()` es la función de JavaScript para hacer peticiones HTTP. Es **asíncrona**: devuelve
una *promesa*, no el resultado ya. Hay que **esperarla** con `await` (o `.then()`):

```javascript
// GET
const r = await fetch("/led");
const datos = await r.json();      // {"encendido": true}

// POST con cuerpo JSON  ← ojo al Content-Type
await fetch("/led", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ encendido: true })
});
```

Olvidar el `await`/`.then` o el `Content-Type` son los dos fallos clásicos (tabla de
errores).

### Servir HTML/estáticos desde FastAPI

Dos formas, de menor a mayor:

| Forma | Cuándo | Cómo |
|---|---|---|
| `HTMLResponse` | una página suelta, rápido | devolver el HTML como string en una ruta |
| `StaticFiles` | varios ficheros (css, js, imgs) | montar una carpeta entera como estática |

Para hoy basta `HTMLResponse` (o leer el `index.html` del disco y devolverlo). El detalle:
servir la web **desde el mismo servidor** que la API tiene una gran ventaja, y se llama
**mismo origen**.

### CORS: qué es y por qué (casi) no nos afecta

Un **origen** = esquema + host + puerto (`http://192.168.1.50:8000`). Por seguridad, el
navegador bloquea que una página de un origen llame por `fetch` a **otro** origen distinto,
salvo que ese otro lo permita explícitamente. Ese mecanismo es **CORS** (Cross-Origin
Resource Sharing).

```
   página servida por  http://192.168.1.50:8000
        └─ fetch("/led") → http://192.168.1.50:8000   [OK] MISMO ORIGEN, sin CORS
        └─ fetch a       → http://192.168.1.99:5500   [NO] otro origen → el navegador lo bloquea
```

> **Truco de hoy**: como servimos el HTML **desde el mismo FastAPI** (mismo host y puerto que
> la API), todo es *mismo origen* y **CORS no aparece**. Solo necesitarías configurarlo
> (`CORSMiddleware`) si abrieras el `.html` con un servidor aparte (p. ej. la "Live Preview"
> del editor en otro puerto) o desde `file://`. Más sobre la política de mismo origen en
> [[MOC_Ciberseguridad]].

### Refrescar el estado: `setInterval` (polling, otra vez)

La web no recibe avisos del servidor (igual que la Pi): para mantener la pantalla al día,
pregunta cada pocos segundos con `setInterval`. Es **el mismo polling** de la Sesión 5, ahora
en JavaScript:

```javascript
setInterval(refrescar, 2000);   // cada 2 s → GET /telemetria → pinta el estado
```

## Manos a la obra

### 1. Servir la página desde FastAPI (`# TODO`)

En `servidor/main.py`:

```python
from fastapi.responses import HTMLResponse
from pathlib import Path

@app.get("/", response_class=HTMLResponse)
def panel():
    # TODO: leer web/index.html y devolverlo
    return Path("web/index.html").read_text(encoding="utf-8")
```

### 2. La página con botones y telemetría (`web/index.html`)

Esqueleto con los `# TODO` en los `fetch`:

```html
<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><title>Panel LED</title></head>
<body>
  <h1>Control del LED</h1>
  <button id="on">Encender</button>
  <button id="off">Apagar</button>
  <p>Estado: <span id="estado">—</span></p>

  <script>
    async function cambiar(encendido) {
      // TODO: POST /led con {encendido} y Content-Type application/json
    }
    async function refrescar() {
      // TODO: GET /telemetria y volcar el estado en #estado
    }

    document.getElementById("on").onclick  = () => cambiar(true);
    document.getElementById("off").onclick = () => cambiar(false);
    refrescar();
    setInterval(refrescar, 2000);   // polling del estado
  </script>
</body>
</html>
```

Solución de los `fetch`:

```javascript
async function cambiar(encendido) {
  await fetch("/led", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ encendido })
  });
  refrescar();                       // pinta el nuevo estado al instante
}

async function refrescar() {
  const r = await fetch("/telemetria");
  const t = await r.json();
  document.getElementById("estado").textContent = t.encendido ? "ON 💡" : "OFF ⚫";
}
```

### 3. Probarlo

Arranca el servidor (en `0.0.0.0`, como en la Sesión 4) y abre en el navegador:

```
http://192.168.1.50:8000/
```

Pulsa **Encender**: el `LedFalso` imprime en tu terminal (o el LED real de la Pi se enciende,
porque su cliente sigue haciendo polling al mismo `/led`). El texto de estado se refresca
solo cada 2 s. Desde otra máquina de la sala se entra con esa misma URL.

## El muro

"El panel pregunta cada 2 s para refrescar, igual que la Pi: si otra persona cambia el LED,
mi pantalla tarda hasta 2 s en enterarse, y enciende y apaga con un retardo perceptible. Eso
no es *tiempo real*." Para que el servidor **empuje** los cambios al instante a todos los
navegadores y a la Pi, se usan **WebSockets**. → [[08-tiempo-real-con-websockets]].
(Antes, en la Sesión 7, le damos memoria al sistema con SQLite:
[[07-persistencia-con-sqlite]].)

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `405 Method Not Allowed` o el body llega vacío | Falta `Content-Type: application/json` o `JSON.stringify` en el POST | Manda ambos; revisa el `fetch` de `cambiar()` |
| El botón "no hace nada", la consola muestra `Promise` | Olvidaste `await`/`.then` | `fetch` es asíncrono: usa `await` (función `async`) |
| Error de **CORS** en la consola del navegador | Abriste el HTML desde otro origen (Live Preview, `file://`) | Sírvelo desde **tu** FastAPI (`/`); o configura `CORSMiddleware` |
| `GET /` da 404 o `FileNotFoundError` | Ruta a `index.html` mal o arrancas desde otra carpeta | Lanza uvicorn desde la raíz del repo; revisa la ruta `web/index.html` |
| Estado nunca se actualiza | `setInterval`/`refrescar` mal o endpoint `/telemetria` inexistente | Verifica el `GET /telemetria` con `curl` y el id `#estado` |

## Guion de la sesión

- **0–10** Muro de la Sesión 5: "controlar con `curl` es incómodo". Abre la demo final (el
  panel ya hecho) 30 segundos para que vean a dónde van hoy.
- **10–30** Pizarra: el navegador **es otro cliente HTTP**; `fetch` asíncrono (`await`,
  `Content-Type`); servir HTML desde FastAPI; **mismo origen → sin CORS** (y cuándo sí
  aparecería); `setInterval` = polling otra vez.
- **30–80** `./bin/sesion.sh 6`, servir `index.html` desde `/`, rellenar los `fetch` de
  botones y refresco, abrir el panel y controlar el LedFalso. Quien tenga turno de Pi: ver el
  LED real obedecer a los botones de la web.
- **80–90** Puesta en común. Resalta que el polling del JS es **el mismo patrón** que el de la
  Pi, con su mismo defecto. Plantea el muro de tiempo real (Sesión 8) tras el rodeo por
  persistencia (Sesión 7).

## Conexiones
- [[05-la-raspberry-como-cliente-y-el-led-real]] — la sesión anterior (LED real por polling)
- [[07-persistencia-con-sqlite]] — la siguiente: dar memoria durable al sistema
- [[08-tiempo-real-con-websockets]] — donde el panel deja de hacer polling
- [[Curso_Servidores_y_Redes/00_README]] — visión y diseño del curso
- [[MOC_Desarrollo_Software]] — frontend/backend, iterar por entregables
- [[MOC_Ciberseguridad]] — política de mismo origen y CORS
