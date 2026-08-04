---
title: Sesión 3 — JSON y validación con Pydantic
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 3 Servidores, Validacion con Pydantic]
---

# Sesión 3 — JSON y validación con Pydantic

> **Objetivo**: recibir y **validar** datos JSON con Pydantic. Añadir un endpoint de
> telemetría que solo acepta datos con el tipo correcto, y entender de dónde sale el `422`.
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: el servidor acepta `POST /telemetria` con un JSON
> válido (200) y **rechaza** uno inválido (`422`) automáticamente, sin que el alumno escriba
> ni un solo `if`. Y `/docs` muestra el formato esperado solo.

## Requisitos previos

- [[02-curl-y-los-verbos-http]] completada: maneja `GET`/`POST` y `curl`; ha visto el server
  reventar con un `POST` de basura (el muro de la Sesión 2).
- Entorno activado: `source .venv/bin/activate`.

## El checkpoint de hoy

```bash
source .venv/bin/activate
./bin/sesion.sh 3            # 'sesion3-inicio'
```

Trae el `main.py` de la Sesión 2 ya funcionando, más un hueco para la telemetría: hay un
`import` de Pydantic preparado y dos endpoints (`POST /telemetria`, `GET /telemetria`)
marcados con `# TODO`, junto con un sitio para guardar la última lectura.

**Lo que se rellena hoy**: el modelo `Telemetria(BaseModel)` y los dos endpoints.

```python
# servidor/main.py  (estado de partida, sesion3-inicio — fragmento nuevo)
from pydantic import BaseModel

# TODO (Sesión 3): define el modelo Telemetria con un campo temperatura: float
#                  y un timestamp opcional.

ultima_lectura = {}   # aquí guardaremos la última telemetría recibida

# TODO (Sesión 3): POST /telemetria que reciba un Telemetria y lo guarde,
#                  y GET /telemetria que devuelva la última lectura.
```

## Teoría

### 1. Qué es JSON

**JSON** (JavaScript Object Notation) es el formato estándar para **intercambiar datos** entre
programas por la red. Es texto plano, legible, y casi todos los lenguajes lo entienden.

Tipos que tiene JSON (y poco más):

| Tipo JSON | Ejemplo | Equivalente en Python |
|---|---|---|
| objeto | `{"clave": "valor"}` | `dict` |
| array | `[1, 2, 3]` | `list` |
| string | `"hola"` | `str` |
| número | `21.5`, `7` | `float` / `int` |
| booleano | `true` / `false` | `True` / `False` |
| nulo | `null` | `None` |

Detalle que muerde a la gente: en JSON los booleanos son `true`/`false` en **minúscula**, y
las claves van **siempre entre comillas dobles**.

### 2. Serializar y deserializar

```
   objeto en memoria            texto JSON (lo que viaja por la red)
   {"temperatura": 21.5}  ──serializar──►   '{"temperatura": 21.5}'
   {"temperatura": 21.5}  ◄─deserializar──  '{"temperatura": 21.5}'
```

- **Serializar**: pasar de objeto del lenguaje → texto JSON (para mandarlo).
- **Deserializar**: pasar de texto JSON → objeto del lenguaje (al recibirlo).

Por la red **solo viaja texto**. FastAPI serializa/deserializa por ti; hay que saber que pasa
por debajo.

### 3. Por qué validar (la regla de oro)

> **Nunca te fíes del cliente.** Cualquiera puede mandarte cualquier cosa.

El cliente puede mandar un campo que falta, un texto donde esperabas un número, un JSON roto,
o datos maliciosos. En la Sesión 2 vimos que un cuerpo inesperado **reventaba el servidor con
un 500**. Validar es: comprobar que lo que entra tiene la forma correcta **antes** de usarlo,
y si no, rechazarlo con un error limpio (un `4xx`), no petar.

### 4. Pydantic: validación declarativa

Pydantic deja **declarar la forma de los datos** como una clase con tipos. No escribes la
lógica de comprobación; la *declaras*.

```python
from pydantic import BaseModel

class Telemetria(BaseModel):
    temperatura: float
```

A partir de eso, cuando un endpoint recibe un `Telemetria`, FastAPI:

1. Lee el JSON del cuerpo.
2. Comprueba que `temperatura` existe y es (o se puede convertir a) `float`.
3. Si encaja → te entrega un objeto `Telemetria` ya validado.
4. Si **no** encaja → responde solo con un **`422`** y un mensaje que explica qué falló.

```
        JSON entra
            │
            ▼
   ┌──────────────────┐   encaja   ┌─────────────────────────┐
   │ Pydantic valida  │ ─────────► │ tu función recibe el     │
   │ contra Telemetria│            │ objeto Telemetria limpio │
   └──────────────────┘            └─────────────────────────┘
            │ NO encaja
            ▼
   422 Unprocessable Entity  (automático, sin escribir un solo if)
```

### 5. De dónde sale el 422

`422 Unprocessable Entity` es un `4xx`: significa *"entendí el JSON, pero los datos no cumplen
lo que pide este endpoint"*. **No es un fallo del servidor** (eso sería 5xx) — es el servidor
defendiéndose bien de una entrada mala. Que aparezca un `422` en clase es **señal de éxito**:
la validación funciona.

| Caso | Código | Quién tiene la culpa |
|---|---|---|
| JSON válido y completo | `200` | — |
| Falta un campo o tipo equivocado | `422` | el cliente |
| El JSON está roto (ni siquiera parsea) | `400` | el cliente |
| Un bug dentro de tu función | `500` | el servidor |

### 6. Los type hints hacen doble trabajo

Lo elegante de FastAPI: el **mismo** `temperatura: float` se usa para **dos** cosas.

```
        class Telemetria(BaseModel):
            temperatura: float
                  │
        ┌─────────┴──────────┐
        ▼                    ▼
   VALIDA la entrada    GENERA la documentación
   (rechaza lo malo)    (OpenAPI → /docs)
```

Por eso `/docs` "sabía" en la Sesión 1 qué endpoints había: FastAPI construye un esquema
**OpenAPI** leyendo tus tipos. Declaras una vez; obtienes validación *y* docs *y* el
formulario de prueba en `/docs`.

### 7. Modelos de request y de response

- **Request model**: la forma de lo que el cliente **manda** (lo que validas al entrar).
- **Response model**: la forma de lo que el servidor **devuelve** (FastAPI lo serializa).

Hoy basta con el de request (`Telemetria`). En sesiones futuras se separan más, pero conviene
nombrar la distinción ahora: *qué espero recibir* vs *qué prometo devolver*.

## Manos a la obra

**1) Colocarse y arrancar:**

```bash
source .venv/bin/activate
./bin/sesion.sh 3
uvicorn servidor.main:app --reload
```

**2) Definir el modelo y los endpoints (rellenar los `# TODO`).** Solución de hoy:

```python
# servidor/main.py  (solución de la Sesión 3 — fragmento)
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Telemetria(BaseModel):
    temperatura: float
    ts: Optional[datetime] = None     # opcional; default None (NO un default mutable)

ultima_lectura = {}

@app.post("/telemetria")
def recibir_telemetria(lectura: Telemetria):
    # 'lectura' ya viene validado: temperatura es float seguro
    ultima_lectura["dato"] = lectura
    return {"recibido": True, "temperatura": lectura.temperatura}

@app.get("/telemetria")
def leer_telemetria():
    if not ultima_lectura:
        return {"mensaje": "aun no hay lecturas"}
    return ultima_lectura["dato"]
```

Puntos a remarcar en pizarra:
- El parámetro `lectura: Telemetria` es lo que dispara la validación. No hay `if`.
- `ts: Optional[datetime] = None`: el campo es opcional. El default es `None`, **nunca** una
  estructura mutable como `[]` o `{}` (eso comparte estado entre llamadas: bug clásico).
- FastAPI serializa el `datetime` a texto ISO solo al devolverlo (`"2026-06-17T10:30:00"`).

**3) Probar un JSON VÁLIDO (espera 200):**

```bash
curl -X POST http://127.0.0.1:8000/telemetria \
     -H "Content-Type: application/json" \
     -d '{"temperatura": 21.5}'
# → {"recibido":true,"temperatura":21.5}
```

**4) Probar un JSON INVÁLIDO (espera 422):**

```bash
curl -i -X POST http://127.0.0.1:8000/telemetria \
     -H "Content-Type: application/json" \
     -d '{"temperatura": "hola"}'
# → HTTP/1.1 422 Unprocessable Entity
#   ...detalle: "Input should be a valid number..."
```

Que vean el `-i`: el código de la primera línea es `422`. **Eso es lo que queríamos.** El
server no petó; rechazó educadamente.

**5) Verlo en `/docs`:** abre `http://127.0.0.1:8000/docs`. El endpoint `/telemetria` ahora
muestra el **esquema** `Telemetria` con `temperatura (number)`. Pulsa *Try it out*, mete
`"hola"` en temperatura y mira cómo el propio formulario y la respuesta marcan el error. Esa
documentación salió **gratis** del modelo.

**6) Leer la última lectura:**

```bash
curl http://127.0.0.1:8000/telemetria
# → la última telemetría válida que mandaste
```

## El muro

Todo esto —`/ping`, el LED, la telemetría validada— **solo vive en el portátil del alumno**,
en `127.0.0.1`. Pregunta natural: *"si la Raspberry de la sala, u otro compañero, quiere
mandarme telemetría o leer mi LED… ¿cómo llega hasta mi servidor si `127.0.0.1` significa
'solo yo'?"*. Ese es el muro que abre la [[04-salir-del-localhost-la-red-local]]: salir de
localhost a la red local (IPs `192.168.1.x`, `0.0.0.0`, firewall).

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| "El server da un 422 y creo que está roto" | Se confunde 422 (rechazo de entrada mala) con un fallo del server | El `422` es éxito: la validación rechazó datos inválidos (es 4xx, no 5xx) |
| Estado compartido raro entre peticiones | Un default mutable (`ts: list = []`) | Usa `None` como default y crea el valor dentro si hace falta |
| `422` aunque el dato parece bien | Tipo mal declarado o JSON con tipo equivocado (`"21.5"` con comillas es string) | Manda número sin comillas; revisa el tipo del modelo |
| `Object of type datetime is not JSON serializable` (en código propio) | Intentar serializar `datetime` a mano | Devuelve el modelo Pydantic y deja que FastAPI lo serialice |
| Campo opcional que da error si falta | Olvidaste el `= None` (sin default, Pydantic lo exige) | `ts: Optional[datetime] = None` |

## Guion de la sesión

| Tramo | Qué hacer |
|---|---|
| **0–10** | Repaso del muro de la Sesión 2: mandar basura rompía el server. Hoy: blindar la entrada. |
| **10–30** | Teoría en pizarra: JSON y sus tipos, serializar/deserializar, "no te fíes del cliente", Pydantic `BaseModel`, de dónde sale el 422, type hints → validación + `/docs`. |
| **30–80** | `./bin/sesion.sh 3`, definir `Telemetria`, los endpoints, probar JSON válido (200) e inválido (422) con `curl` y en `/docs`. |
| **80–90** | Puesta en común y **el muro**: "todo vive en mi localhost; ¿cómo me alcanza la Raspberry o un compañero?" → Sesión 4. |

## Conexiones

- [[Curso_Servidores_y_Redes/00_README]] — visión y diseño del curso
- [[02-curl-y-los-verbos-http]] — la sesión anterior: HTTP, GET/POST y `curl`
- [[04-salir-del-localhost-la-red-local]] — la siguiente: salir de localhost a la red local
- [[MOC_Programacion]] — área padre
- [[MOC_CS_Fundamentos]] — formatos de datos, validación y códigos de estado
- [[MOC_Desarrollo_Software]] — "no te fíes del cliente" y contratos de datos
