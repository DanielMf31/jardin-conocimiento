---
title: Sesión 10 — Resiliencia y manejo de errores
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 10 Resiliencia, Timeouts y Reintentos]
---

# Sesión 10 — Resiliencia y manejo de errores

> **Objetivo**: que el cliente de la Raspberry y el servidor **aguanten fallos de red** y se
> recuperen solos, sin que nadie tenga que reiniciar nada a mano.
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: con el cliente Pi corriendo, **apagas el servidor**; el
> cliente avisa "no llego, reintento en 1s… 2s… 4s…" y sigue vivo. Cuando **vuelves a
> arrancar** el servidor, el cliente **retoma solo** y el LED vuelve a obedecer. Nadie tocó la Pi.

## Requisitos previos

- Sesiones 1–9 hechas: tienes el sistema completo (servidor con `GET/POST /led`, telemetría,
  panel web, SQLite, WebSockets y API key en `.env`).
- El **cliente de la Raspberry** funcionando con su bucle de *polling* ([[05-la-raspberry-como-cliente-y-el-led-real]]):
  pregunta cada X segundos por `GET /led` y enciende/apaga el LED real.
- Saber distinguir cliente (la Pi que pregunta) de servidor (tu portátil que responde)
  ([[Curso_Servidores_y_Redes/00_README]]).

## El checkpoint de hoy

```bash
./bin/sesion.sh 10             # esqueleto de la Sesión 10
./bin/sesion.sh 10 --solucion  # si te atascas
```

Hoy **no añadimos una funcionalidad nueva visible**: añadimos *robustez*. El `# TODO` está
en el bucle de *polling* del cliente: envolverlo en manejo de errores, ponerle **timeout**,
**reintentos con espera** y cambiar los `print` por `logging`. El servidor casi no cambia.

## Teoría

Esta es la sesión donde el proyecto deja de ser "una demo bonita" y se vuelve un sistema que
no se cae al primer estornudo de la red.

### En redes, TODO falla (y a propósito)

Hasta ahora el cliente asumía un mundo perfecto: el servidor siempre está, la red siempre
responde, la respuesta siempre es la esperada. En cuanto sales del `localhost`, eso es
mentira. Estas son las formas típicas en que una llamada de red puede irse al traste:

| Fallo | Qué pasa de verdad | Qué excepción/señal verás |
|---|---|---|
| **Timeout** | la otra máquina tarda demasiado o no contesta | `requests.exceptions.Timeout` |
| **Conexión rechazada** | nadie escucha en ese puerto (servidor caído) | `ConnectionError` (`Connection refused`) |
| **Servidor caído a media respuesta** | se corta la conexión | `ConnectionError` / `ChunkedEncodingError` |
| **Respuesta inesperada** | llega un `500`, o un body que no es el JSON que esperabas | `HTTPError`, `JSONDecodeError`, `KeyError` |
| **Red intermitente** | el wifi parpadea, el cable se mueve | cualquiera de los anteriores, a ráfagas |

La pregunta de diseño no es *"¿y si falla?"* sino *"¿qué hace el cliente CUANDO falle?"*.

### `try/except` alrededor de la llamada de red

La herramienta base de Python: rodear **solo** la operación que puede fallar (la petición de
red) y capturar el error en vez de morir. La regla de oro: **captura excepciones concretas**,
no `except Exception` a saco (eso oculta bugs reales, como un `KeyError` por un typo).

```python
import requests

try:
    r = requests.get(url, timeout=3)
    r.raise_for_status()          # convierte un 4xx/5xx en excepción
    estado = r.json()["encendido"]
except requests.exceptions.RequestException as e:
    # captura timeout, connection refused, http error... pero NO un bug tuyo
    log.warning("No pude hablar con el servidor: %s", e)
```

`RequestException` es la clase padre de todos los fallos de red de `requests`: captura el
grupo correcto sin tragarse de paso un error de programación.

### Timeouts explícitos: sin ellos, el cliente se cuelga PARA SIEMPRE

El error nº 1 de los principiantes: `requests.get(url)` **sin timeout**. Si el servidor está
encendido pero "congelado" (no rechaza la conexión, simplemente no responde), tu cliente se
queda esperando **indefinidamente**. El bucle de polling se para en seco y el LED se queda
como estaba. No es que falle: es que **no vuelve nunca**.

```
   SIN timeout                              CON timeout=3
   ┌──────────┐  GET /led                   ┌──────────┐  GET /led
   │ cliente  │ ───────────► (silencio)     │ cliente  │ ───────────► (silencio)
   │          │      ∞  colgado            │          │    3s → Timeout
   │  (muerto)│                              │  reintenta│ ◄── sigue vivo
   └──────────┘                              └──────────┘
```

Un timeout convierte "esperar para siempre" en "esperar como mucho 3 segundos y luego decidir
qué hago". **Toda** llamada de red debe llevar `timeout=`. Siempre.

### Reintentos con espera (backoff): no martillees la red

Cuando una petición falla, lo lógico es **reintentar**. Pero reintentar *inmediatamente*, en
bucle cerrado, es un error: si el servidor está caído, tu cliente le lanzaría cientos de
peticiones por segundo (le *"martillea"*), satura la red y la CPU de la Pi sin conseguir nada.

La solución es **esperar entre reintentos, y esperar cada vez más** (*exponential backoff*):

```
   intento 1 falla → espera 1 s
   intento 2 falla → espera 2 s
   intento 3 falla → espera 4 s
   intento 4 falla → espera 8 s   (con un TOPE, p.ej. 30 s)
```

Cada espera dobla la anterior, hasta un máximo. Así, mientras el servidor está caído, el
cliente pregunta con calma (cada 30 s) en vez de freír la red; y en cuanto el servidor vuelve,
la siguiente petición funciona y el contador se reinicia a 1 s.

| Estrategia | Carga en la red | ¿Se recupera? |
|---|---|---|
| Reintentar sin pausa | brutal (martillea) | sí, pero a costa de saturar todo |
| Reintentar con espera fija (cada 5 s) | constante, moderada | sí, razonable |
| **Backoff exponencial con tope** | baja y se adapta | **sí, y es amable con la red** [OK] |

### `GET /led` es idempotente → reintentar es SEGURO

¿Por qué podemos reintentar tan tranquilos? Porque `GET /led` es **idempotente**: pedirlo una
vez o cinco veces da el mismo resultado y **no cambia nada** en el servidor. Preguntar "¿cómo
está el LED?" tres veces no enciende tres LEDs. Por eso reintentar un `GET` no tiene efectos
secundarios. (Cuidado con reintentar un `POST` que *cambia estado*: ahí sí podrías repetir una
acción. En el polling del cliente solo hacemos `GET`, así que estamos a salvo.)

### `logging` en vez de `print`

`print` vale para un script de juguete. Para algo que corre solo en una Pi durante horas,
necesitas `logging`: niveles de gravedad, marca de tiempo automática, y poder mandarlo a un
**fichero** que puedes revisar después.

| Nivel | Para qué | Ejemplo en el cliente |
|---|---|---|
| `DEBUG` | detalle fino, solo al depurar | "petición enviada a 192.168.1.50:8000" |
| `INFO` | el curso normal de las cosas | "LED encendido", "servidor recuperado" |
| `WARNING` | algo raro pero recuperable | "timeout, reintento en 2s" |
| `ERROR` | un fallo serio | "agotados los reintentos" |

```python
import logging
logging.basicConfig(
    filename="cliente.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("cliente-led")
```

Con esto, en vez de un terminal lleno de prints que se pierden, tienes `cliente.log` con
fecha y nivel de cada evento. Mañana puedes ver *cuándo* se cayó el servidor.

## Manos a la obra

Partimos del bucle de polling del cliente Pi, que hoy está "ingenuo" (asume que todo va bien):

```python
# ANTES — frágil: sin timeout, sin manejo de errores, con print
while True:
    r = requests.get(f"http://{SERVIDOR}/led")   # ⚠ puede colgarse o petar
    if r.json()["encendido"]:
        led.encender()
    else:
        led.apagar()
    print("ok")
    time.sleep(2)
```

### 1. Poner `timeout=` a la petición (el primer `# TODO`)

```python
r = requests.get(f"http://{SERVIDOR}/led", timeout=3)
```

Tres segundos es de sobra en una LAN. Sin esto, nada de lo demás importa.

### 2. Envolver en `try/except` con la excepción concreta

```python
try:
    r = requests.get(f"http://{SERVIDOR}/led", timeout=3)
    r.raise_for_status()
    encendido = r.json()["encendido"]
except requests.exceptions.RequestException as e:
    log.warning("Fallo de red: %s", e)
    # ... (aquí entra el reintento, paso 3)
else:
    if encendido:
        led.encender()
    else:
        led.apagar()
```

### 3. Reintento con espera creciente y tope (el `# TODO` gordo)

La idea: un contador de espera que empieza en 1 s, se dobla en cada fallo seguido y se reinicia
al primer éxito.

```python
ESPERA_INICIAL = 1
ESPERA_MAX = 30
espera = ESPERA_INICIAL

while True:
    try:
        r = requests.get(f"http://{SERVIDOR}/led", timeout=3)
        r.raise_for_status()
        encendido = r.json()["encendido"]
    except requests.exceptions.RequestException as e:
        log.warning("No llego al servidor (%s). Reintento en %ss", e, espera)
        time.sleep(espera)
        espera = min(espera * 2, ESPERA_MAX)   # backoff con tope
        continue
    # éxito: aplico estado y reseteo la espera
    led.encender() if encendido else led.apagar()
    espera = ESPERA_INICIAL
    time.sleep(2)        # ritmo normal de polling
```

### 4. Cambiar los `print` por `logging` (el último `# TODO`)

Sustituye cada `print(...)` por `log.info(...)` / `log.warning(...)` según corresponda, y
añade el `basicConfig` de arriba al inicio del script.

### 5. Probar el fallo y la recuperación (la prueba reina)

```bash
# 1) En la Pi: arranca el cliente y enciende el LED desde el panel/curl. Funciona.
# 2) En tu portátil: APAGA el servidor (Ctrl-C en uvicorn).
#    → en cliente.log verás:  WARNING No llego al servidor... Reintento en 1s / 2s / 4s
#    → el cliente NO muere.
# 3) Vuelve a ARRANCAR el servidor:
uvicorn servidor.main:app --host 0.0.0.0 --port 8000
#    → la siguiente petición del cliente funciona, el LED vuelve a obedecer, espera→1s.
tail -f cliente.log     # míralo en vivo mientras apagas y enciendes el servidor
```

Si apagas el servidor y el cliente sigue vivo, reintentando con calma, y se recupera solo al
volver: **objetivo cumplido**. Has construido resiliencia.

## El muro

"Genial, ahora aguanta fallos de red. Pero todo esto **funciona en mi portátil** porque tengo
Python, el venv, FastAPI, `requests` y mil dependencias instaladas justo en su versión. Si
quiero llevar el servidor a otra máquina (o a la de un compañero), tengo que **reinstalar
Python y todas las dependencias a mano**, rezar para que las versiones cuadren… ¿cómo hago que
esto arranque **igual en cualquier sitio**, de forma repetible?"
→ Eso es empaquetar con [[11-empaquetar-con-docker]].

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| El cliente se "cuelga" y deja de actualizar el LED | `requests.get` **sin** `timeout=` y servidor congelado | Pon `timeout=3` en **todas** las llamadas de red |
| Al apagar el servidor, el cliente muere con un traceback | No hay `try/except` rodeando la petición | Envuelve la llamada y captura `RequestException` |
| La red/CPU de la Pi se dispara con el servidor caído | Reintentos **sin pausa** (bucle cerrado) | Añade `time.sleep(espera)` con backoff y un tope |
| Un typo (`KeyError`) pasa desapercibido | `except Exception` demasiado amplio se lo traga | Captura solo `requests.exceptions.RequestException` |
| "Funcionaba pero no sé qué pasó anoche" | Usabas `print`, que no deja rastro | Usa `logging` a fichero con nivel y `asctime` |
| Reintenta para siempre sin avisar | No hay `WARNING`/`ERROR` ni tope | Loguea cada reintento y pon `ESPERA_MAX` |

## Guion de la sesión

- **0–10** Repaso: el cliente Pi enciende el LED por polling. Pregunta trampa: "¿qué pasa si
  ahora **apago** el servidor?" Apágalo en vivo → el cliente ingenuo se cuelga o revienta. Ese
  es el muro de hoy: la red falla y hay que sobrevivir.
- **10–30** Teoría en pizarra: la tabla de "todo falla", `try/except` con excepción concreta,
  el dibujo del cuelgue sin timeout, y el backoff 1→2→4→8 con tope. Recalca la idempotencia de
  `GET` como permiso para reintentar.
- **30–80** `./bin/sesion.sh 10`. Por orden: (1) `timeout=`, (2) `try/except`, (3) backoff,
  (4) `logging`. Cada uno corre el cliente con `tail -f cliente.log` y el profe **apaga y
  enciende** el servidor central para que todos vean su cliente reintentar y recuperarse.
- **80–90** Puesta en común: ¿quién capturó `except Exception` y por qué es mala idea? Plantea
  el muro: "esto va en TU portátil con TU venv; la semana que viene lo metemos en una caja que
  arranca igual en cualquier máquina".

## Conexiones
- [[09-seguridad-y-secretos]] — la sesión anterior (API key y `.env`)
- [[05-la-raspberry-como-cliente-y-el-led-real]] — el cliente cuyo bucle endurecemos hoy
- [[11-empaquetar-con-docker]] — la siguiente: hacer el servidor portable y repetible
- [[Curso_Servidores_y_Redes/00_README]] — visión y diseño del curso
- [[MOC_CS_Fundamentos]] — fiabilidad en redes, TCP, idempotencia
- [[MOC_Linux]] — procesos, logs, `tail -f`
- [[MOC_Desarrollo_Software]] — manejo de errores y logging como buenas prácticas
