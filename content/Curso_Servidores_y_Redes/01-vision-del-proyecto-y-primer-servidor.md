---
title: Sesión 1 — Visión del proyecto y primer servidor
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 1 Servidores, Primer servidor FastAPI]
---

# Sesión 1 — Visión del proyecto y primer servidor

> **Objetivo**: ver el proyecto final funcionando (demo) y levantar el primer servidor
> FastAPI en local con un endpoint `GET /ping` que responde `{"status": "ok"}`.
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: cada alumno arranca su servidor en su portátil y, en
> el navegador, `http://127.0.0.1:8000/ping` le devuelve un JSON. Además descubre `/docs`.

## Requisitos previos

- Haber completado [[00_setup-entorno-y-repo]]: Python 3, repo clonado, `./setup.sh`
  ejecutado y `./bin/sesion.sh 1` funcionando.
- Saber abrir una terminal y activar el entorno: `source .venv/bin/activate` (el prompt
  muestra `(.venv)`).

## El checkpoint de hoy

```bash
source .venv/bin/activate
./bin/sesion.sh 1            # te coloca en 'sesion1-inicio'
```

Trae un `servidor/main.py` casi vacío: la app FastAPI ya está creada, pero el endpoint
`/ping` está marcado con un `# TODO`. **Lo que se rellena hoy** es ese único endpoint. Nada
más. La idea es que el primer día se toque lo mínimo y se vea algo funcionando de punta a
punta.

```python
# servidor/main.py  (estado de partida, sesion1-inicio)
from fastapi import FastAPI

app = FastAPI()

# TODO (Sesión 1): crea un endpoint GET /ping que devuelva {"status": "ok"}
```

## Teoría

Esta es la sesión donde se asienta el **mapa mental** de todo el curso. No hace falta código
todavía; hace falta que entiendan *qué pieza es cuál*.

### 1. Qué es un servidor

Un servidor no es una máquina especial ni una caja en un sótano. Es, simplemente, **un
programa que se queda esperando peticiones y, cuando llega una, responde**. Eso es todo. El
portátil del alumno, mientras corre ese programa, *es* un servidor.

```
        ┌──────────────────────────────────────────┐
        │  SERVIDOR = programa en bucle infinito     │
        │                                            │
        │   while True:                              │
        │       espera una petición  ───────┐        │
        │       procesa lo que pidan         │        │
        │       devuelve una respuesta  ◄────┘        │
        └──────────────────────────────────────────┘
```

### 2. El modelo cliente-servidor (petición → respuesta)

Dos roles. Uno **pide** (cliente), otro **responde** (servidor). Siempre empieza el cliente;
el servidor nunca habla primero.

```
   CLIENTE                                        SERVIDOR
   (navegador, curl,         petición            (tu programa
    la Raspberry...)   ───────────────────►       FastAPI)
                       ◄───────────────────
                            respuesta
```

| Concepto | Quién es en este curso | Qué hace |
|---|---|---|
| Cliente | navegador, `curl`, y luego la Raspberry | Inicia: pide algo |
| Servidor | el programa FastAPI del alumno | Espera y responde |
| Petición | "dame el estado del LED", "enciéndelo" | Lo que el cliente manda |
| Respuesta | un JSON, un código de estado | Lo que el servidor devuelve |

Es importante: **un mismo programa puede ser cliente de uno y servidor de otro**. La
Raspberry será *cliente* del servidor del alumno, pero *ella* manda al LED.

### 3. Qué es HTTP (a alto nivel)

HTTP es el **idioma** que hablan cliente y servidor en la web. Define cómo se escribe una
petición y cómo se escribe una respuesta para que ambos se entiendan, aunque estén escritos
en lenguajes distintos y en máquinas distintas. Hoy basta esta idea:

> El cliente manda un mensaje de texto con un formato pactado (HTTP), el servidor lo lee y
> contesta con otro mensaje de texto con formato pactado.

El detalle (métodos, cabeceras, códigos) entra en la [[02-curl-y-los-verbos-http]]. Hoy solo:
"hay un protocolo común y se llama HTTP".

### 4. `localhost` / `127.0.0.1` y el concepto de puerto

- `127.0.0.1` es una dirección IP especial que significa **"esta misma máquina"**. Su nombre
  amigable es `localhost`. Cuando el navegador pide a `127.0.0.1`, no sale a la red: habla
  con un programa del propio portátil.
- Un **puerto** es un número (0–65535) que distingue *qué programa* dentro de la máquina
  recibe la conexión. Una IP es el edificio; el puerto es el número de puerta.

```
        127.0.0.1  (el edificio = tu portátil)
        ├── puerto 22    → SSH
        ├── puerto 80    → web normal
        ├── puerto 8000  → NUESTRO servidor FastAPI   ◄── aquí escuchamos
        └── puerto 5432  → una base de datos, etc.
```

Por eso la URL será `http://127.0.0.1:8000/ping`: IP + puerto + ruta.

### 5. Uvicorn vs FastAPI (la confusión nº 1 de principiantes)

Son **dos piezas distintas** y conviene separarlas en la pizarra:

| Pieza | Qué es | Su trabajo |
|---|---|---|
| **Uvicorn** | un *servidor ASGI* | Abre el puerto 8000, escucha conexiones, recibe el HTTP crudo y se lo entrega a tu app. Es el "portero" |
| **FastAPI** | un *framework* | Decide, según la ruta y el método, qué función tuya ejecutar y convierte el resultado en respuesta HTTP |

```
   navegador ──HTTP──►  UVICORN  ──►  FastAPI  ──►  tu función  →  {"status":"ok"}
                       (escucha)     (enruta)      (tu código)
```

Por eso se arranca con `uvicorn servidor.main:app`: le dices a Uvicorn *dónde está* tu app
de FastAPI para que le pase las peticiones.

### 6. Qué es un framework (en una frase)

> Un framework es código que te llama a ti, no al revés. Esto se llama **inversión de
> control**.

Tú no escribes el bucle "espera petición, mírala, decide". Tú solo **declaras** rutas:

```python
@app.get("/ping")
def ping():
    return {"status": "ok"}
```

…y FastAPI se encarga de llamar a `ping()` cuando llega un `GET /ping`. El `@app.get(...)`
es un **decorador**: registra tu función en una tabla de rutas que el framework consulta.

### 7. Regalo de FastAPI: `/docs`

FastAPI lee tus rutas y genera **documentación interactiva automática** en
`http://127.0.0.1:8000/docs`. Es una web donde se ven todos los endpoints y se pueden probar
con un botón, sin escribir `curl`. Hoy se enseña como "mira lo que te dan gratis"; en la
[[03-json-y-validacion-pydantic]] se entiende *de dónde sale* (de los tipos).

## Manos a la obra

**1) Activar el entorno y colocarse en el checkpoint:**

```bash
source .venv/bin/activate
./bin/sesion.sh 1
```

**2) Rellenar el `# TODO` en `servidor/main.py`:**

```python
# servidor/main.py  (solución de la Sesión 1)
from fastapi import FastAPI

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "ok"}
```

Línea por línea, para explicarlo:
- `app = FastAPI()` crea la aplicación. Es el objeto que guarda la tabla de rutas.
- `@app.get("/ping")` registra la función de debajo como respuesta a `GET /ping`.
- `return {"status": "ok"}` devuelve un diccionario; FastAPI lo convierte solo a JSON.

**3) Arrancar el servidor:**

```bash
uvicorn servidor.main:app --reload
```

Desglose del comando:
- `servidor.main` → módulo `servidor/main.py`.
- `:app` → el objeto `app` dentro de ese módulo.
- `--reload` → reinicia solo el server cada vez que guardas un cambio (comodísimo en clase).

Debería aparecer algo como:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**4) Probar en el navegador:**

- Abre `http://127.0.0.1:8000/ping` → debe mostrar `{"status":"ok"}`.
- Abre `http://127.0.0.1:8000/docs` → la documentación interactiva con `/ping` listado.
  Pulsa *Try it out* → *Execute* y ve la respuesta sin tocar la terminal.

> Truco para impartir: que cada alumno cambie el `"ok"` por su nombre, guarde, y vea cómo
> `--reload` recarga solo. Así *sienten* el bucle editar-recargar-probar.

## El muro

Funciona, pero salta la pregunta natural: *"solo me responde a mí, en mi navegador, y solo
sé verlo escribiendo la URL a mano. ¿Cómo lo pruebo bien, y cómo le digo que **encienda
algo** en vez de solo saludar?"*.

Eso abre la [[02-curl-y-los-verbos-http]]: aprender a hablar con el servidor desde la
terminal con `curl` y a mandarle órdenes (no solo a leer).

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `Address already in use` / `[Errno 98]` | El puerto 8000 ya está ocupado (otro server abierto) | Cierra el otro server (`CTRL+C`) o arranca en otro puerto: `--port 8001` |
| `ModuleNotFoundError` o `pip: command not found` | El `venv` no está activado | `source .venv/bin/activate` (el prompt debe mostrar `(.venv)`) |
| `Error loading ASGI app. Could not import module "main"` | Ruta del módulo mal escrita | Es `servidor.main:app`, con punto, y se arranca desde la raíz del repo |
| Cambias el código y la respuesta no cambia | Falta `--reload` o no guardaste el archivo | Arranca con `--reload` y guarda el archivo |
| `404 Not Found` en el navegador | URL mal escrita (typo en `/ping`) | Revisa la ruta; mira `/docs` para ver las rutas reales |

## Guion de la sesión

| Tramo | Qué hacer |
|---|---|
| **0–10** | Demo del proyecto **terminado**: el LED de la Raspberry encendiéndose desde un servidor. "A esto vamos; hoy damos el primer paso." |
| **10–30** | Teoría en pizarra: servidor, cliente-servidor, HTTP a alto nivel, localhost+puerto, Uvicorn vs FastAPI, framework = inversión de control. |
| **30–80** | `./bin/sesion.sh 1`, rellenar `/ping`, arrancar Uvicorn, probar en navegador y en `/docs`. Cada uno cambia la respuesta y ve el `--reload`. |
| **80–90** | Puesta en común y **el muro**: "solo me veo yo y solo saludo" → presentar la Sesión 2. |

## Conexiones

- [[Curso_Servidores_y_Redes/00_README]] — visión y diseño del curso
- [[00_setup-entorno-y-repo]] — el entorno y `./bin/sesion.sh` (requisito de hoy)
- [[02-curl-y-los-verbos-http]] — la sesión siguiente: hablar con el servidor y darle órdenes
- [[MOC_Programacion]] — área padre
- [[MOC_CS_Fundamentos]] — HTTP, redes y el modelo cliente-servidor
- [[MOC_Linux]] — terminal, procesos y puertos
