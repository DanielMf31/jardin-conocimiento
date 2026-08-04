---
title: Sesión 2 — curl y los verbos HTTP
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 2 Servidores, GET y POST con curl]
---

# Sesión 2 — curl y los verbos HTTP

> **Objetivo**: controlar el `LedFalso` por HTTP desde la terminal. Leer su estado con
> `GET /led` y cambiarlo con `POST /led`, viendo el `` aparecer en la consola del servidor.
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: el alumno escribe un `curl` y, en la otra terminal
> (donde corre Uvicorn), aparece ` LED ON`. Su programa *hace algo* a una orden externa.

## Requisitos previos

- [[01-vision-del-proyecto-y-primer-servidor]] completada: sabe arrancar Uvicorn y tiene un
  `GET /ping` funcionando.
- Entorno activado: `source .venv/bin/activate`.

## El checkpoint de hoy

```bash
source .venv/bin/activate
./bin/sesion.sh 2            # 'sesion2-inicio'
```

Trae dos cosas nuevas:

1. `servidor/led.py` **ya completo** con la interfaz `Led` y `LedFalso` (no se escribe hoy;
   se explica y se usa).
2. `servidor/main.py` con un estado en memoria y el `GET /led` ya hecho, pero el `POST /led`
   marcado con `# TODO`.

**Lo que se rellena hoy**: el handler `POST /led` y la llamada a `led.encender()` /
`led.apagar()`.

```python
# servidor/led.py  (ya viene hecho)
class Led:                       # la interfaz: QUÉ sabe hacer un LED
    def encender(self): ...
    def apagar(self): ...

class LedFalso(Led):             # en el PORTÁTIL: solo imprime
    def encender(self): print("💡 LED ON")
    def apagar(self):   print("⚫ LED OFF")
```

```python
# servidor/main.py  (estado de partida, sesion2-inicio)
from fastapi import FastAPI
from servidor.led import LedFalso

app = FastAPI()

led = LedFalso()                       # en el portátil SIEMPRE el falso
estado_led = {"encendido": False}      # el estado vive en memoria

@app.get("/led")
def leer_led():
    return estado_led

# TODO (Sesión 2): POST /led que reciba {"encendido": true/false},
#                  actualice estado_led y llame a led.encender()/led.apagar()
```

## Teoría

Hoy se abre la caja de HTTP que en la Sesión 1 quedó "a alto nivel".

### 1. Anatomía de una petición HTTP

Una petición es texto con una estructura fija:

```
POST /led HTTP/1.1                ← línea de petición: MÉTODO  RUTA  versión
Host: 127.0.0.1:8000              ┐
Content-Type: application/json    │ ← CABECERAS (metadatos: tipo, longitud, auth...)
Content-Length: 21               ┘
                                  ← línea en blanco: separa cabeceras del cuerpo
{"encendido": true}               ← CUERPO (body): los datos (no siempre lo hay)
```

| Parte | Qué es | Ejemplo |
|---|---|---|
| Método | el *verbo*: qué quiero hacer | `GET`, `POST` |
| Ruta | *sobre qué* recurso | `/led`, `/ping` |
| Cabeceras | metadatos clave-valor | `Content-Type: application/json` |
| Cuerpo | los datos que mando | `{"encendido": true}` |

### 2. Anatomía de una respuesta HTTP

Misma idea, en sentido contrario:

```
HTTP/1.1 200 OK                   ← código de estado + texto
Content-Type: application/json    ← cabeceras
                                  ← línea en blanco
{"encendido": true}               ← cuerpo de la respuesta
```

### 3. GET vs POST

| | **GET** | **POST** |
|---|---|---|
| Intención | **leer** | **provocar un cambio** |
| ¿Lleva cuerpo? | normalmente no | sí (los datos del cambio) |
| ¿Es *seguro*? | sí: no debería cambiar nada | no: tiene efectos |
| ¿Es *idempotente*? | sí | en general, no |

Dos propiedades que conviene nombrar en pizarra:

- **Seguro (safe)**: leer no cambia el estado. Pedir `GET /led` mil veces deja el LED igual.
- **Idempotente**: repetir la misma petición da el mismo resultado final. `GET` lo es.
  `POST {"encendido": true}` resulta idempotente *en este caso* (encender lo encendido lo
  deja encendido), pero en general `POST` no se asume idempotente (p. ej. "crear un registro"
  repetido crea varios). Regla práctica: **GET para leer, POST para ordenar un cambio.**

### 4. Códigos de estado

El servidor resume en un número cómo le fue. Por familias:

| Familia | Significado | Ejemplos típicos |
|---|---|---|
| **2xx** | Éxito | `200 OK`, `201 Created`, `204 No Content` |
| **3xx** | Redirección | `301 Moved`, `304 Not Modified` |
| **4xx** | Error **del cliente** (mandó algo mal) | `400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity` |
| **5xx** | Error **del servidor** (peté yo) | `500 Internal Server Error` |

Idea clave para todo el curso: **4xx = culpa de quien pide; 5xx = culpa del servidor.** El
`422` (validación) de la [[03-json-y-validacion-pydantic]] es un 4xx: el cliente mandó datos
inválidos.

### 5. curl a fondo

`curl` es un cliente HTTP de terminal. Es la navaja suiza para probar APIs. Banderas que se
usan hoy:

| Bandera | Qué hace | Ejemplo |
|---|---|---|
| (nada) | hace un `GET` a la URL | `curl http://127.0.0.1:8000/led` |
| `-X` | fija el método | `-X POST` |
| `-d` | manda un cuerpo (e implica `POST`) | `-d '{"encendido": true}'` |
| `-H` | añade una cabecera | `-H "Content-Type: application/json"` |
| `-i` | muestra **cabeceras + cuerpo** de la respuesta | `curl -i ...` |
| `-v` | modo *verbose*: enseña petición Y respuesta crudas | `curl -v ...` |

> En clase, `curl -v` es oro: enseña en pantalla la petición tal cual sale y la respuesta
> tal cual vuelve. Conecta directamente con la teoría de anatomía de arriba.

### 6. El servidor tiene estado

`estado_led = {"encendido": False}` es una variable normal de Python que **vive en la
memoria del proceso**. Mientras el server esté arrancado, recuerda si el LED está encendido.
Cada `POST` la modifica; cada `GET` la lee.

```
        ┌─ proceso Uvicorn (en memoria) ─┐
        │   estado_led = {"encendido":F} │
        │            ▲        │           │
        │   POST ────┘        └──── GET   │
        └────────────────────────────────┘
```

Ojo: es memoria volátil. Si reinicias el server (o `--reload` recarga), **vuelve a
`False`**. Eso no es un bug hoy; es el muro de una sesión futura (persistencia, Sesión 7).

### 7. La interfaz `Led` (por qué `LedFalso`)

El servidor **no llama a un LED concreto**: llama a un objeto `led` que cumple la interfaz
`Led` (`encender` / `apagar`). En el portátil ese objeto es un `LedFalso` que solo imprime;
en la Raspberry será un `LedReal` que mueve un pin físico. **Cambiar de uno a otro es una
línea.** Así todos trabajan hoy sin hardware. (Esto es inversión de dependencias; se nombra,
no hace falta más teoría.)

## Manos a la obra

**1) Arrancar el servidor (en una terminal):**

```bash
source .venv/bin/activate
./bin/sesion.sh 2
uvicorn servidor.main:app --reload
```

**2) Probar primero el `GET /led` (en OTRA terminal):**

```bash
curl http://127.0.0.1:8000/led
# → {"encendido":false}
```

**3) Rellenar el `# TODO`: el `POST /led`.** Solución de hoy:

```python
# servidor/main.py  (solución de la Sesión 2)
@app.post("/led")
def cambiar_led(nuevo: dict):
    estado_led["encendido"] = nuevo["encendido"]
    if estado_led["encendido"]:
        led.encender()
    else:
        led.apagar()
    return estado_led
```

> Nota para impartir: aquí el cuerpo se recibe como `dict` "a pelo" a propósito. Es frágil
> (si falta la clave, peta). Ese dolor es justo **el muro** que motiva Pydantic en la
> Sesión 3. No lo arregles hoy.

**4) Encender el LedFalso con `curl`:**

```bash
curl -X POST http://127.0.0.1:8000/led \
     -H "Content-Type: application/json" \
     -d '{"encendido": true}'
# respuesta: {"encendido":true}
```

En la **terminal del servidor** debe aparecer:

```
 LED ON
```

Apagarlo:

```bash
curl -X POST http://127.0.0.1:8000/led \
     -H "Content-Type: application/json" \
     -d '{"encendido": false}'
# en la consola del server: ⚫ LED OFF
```

**5) Mirar la respuesta cruda con `-i` y `-v`:**

```bash
curl -i http://127.0.0.1:8000/led      # ves la línea "HTTP/1.1 200 OK" + cabeceras
curl -v -X POST http://127.0.0.1:8000/led \
     -H "Content-Type: application/json" -d '{"encendido": true}'
```

Con `-v`, señala en pantalla las líneas `> POST /led` (lo que sale) y `< HTTP/1.1 200 OK`
(lo que vuelve) y conéctalas con los diagramas de la teoría.

## El muro

*"¿Y si mando basura?"* Pruébalo en clase:

```bash
curl -X POST http://127.0.0.1:8000/led \
     -H "Content-Type: application/json" -d '{"otra_cosa": 5}'
```

El servidor revienta con un `500` feo (falta la clave `encendido`). El cliente le coló datos
que el código no esperaba. Pregunta: *"¿cómo me protejo de la entrada mala sin llenar el
código de `if`?"* → eso abre la [[03-json-y-validacion-pydantic]].

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| El cuerpo "no llega" / `422`/`400` raro | Falta `-H "Content-Type: application/json"` | Añade siempre esa cabecera en peticiones con JSON |
| `curl: (3) URL using bad/illegal format` o JSON roto | Comillas mal: el JSON va entre comillas **simples** y las internas dobles | `-d '{"encendido": true}'` |
| Hace un `GET` cuando querías `POST` | Pusiste `-d` pero también `-X GET`, o te falta `-X POST` | `-d` ya implica POST; no lo contradigas con `-X GET` |
| `Connection refused` | El servidor no está arrancado o es otro puerto | Arranca Uvicorn; revisa que sea `:8000` |
| El LED "se apaga solo" entre pruebas | `--reload` reinició el proceso y `estado_led` volvió a `False` | Es esperado: el estado vive en memoria (se resuelve en la Sesión 7) |

## Guion de la sesión

| Tramo | Qué hacer |
|---|---|
| **0–10** | Repaso del muro de la Sesión 1: "solo saludo y solo desde el navegador". Hoy: dar órdenes desde la terminal. |
| **10–30** | Teoría en pizarra: anatomía petición/respuesta, GET vs POST (safe/idempotente), tabla de códigos, banderas de `curl`, estado en memoria, la interfaz `Led`. |
| **30–80** | `./bin/sesion.sh 2`, `GET /led`, rellenar `POST /led`, encender/apagar el `LedFalso` con `curl`, inspeccionar con `-i`/`-v`. |
| **80–90** | Puesta en común y **el muro**: mandar JSON con basura rompe el server → Sesión 3 (validación). |

## Conexiones

- [[Curso_Servidores_y_Redes/00_README]] — visión y diseño del curso (incluye la interfaz `Led` completa)
- [[01-vision-del-proyecto-y-primer-servidor]] — la sesión anterior: primer servidor y `/ping`
- [[03-json-y-validacion-pydantic]] — la siguiente: validar la entrada con Pydantic
- [[MOC_Programacion]] — área padre
- [[MOC_CS_Fundamentos]] — HTTP, métodos y códigos de estado
- [[MOC_Linux]] — la terminal y `curl`
