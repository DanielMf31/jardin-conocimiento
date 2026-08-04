---
title: Sesión 5 — La Raspberry como cliente y el LED real
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 5 Servidores, LED Real GPIO]
---

# Sesión 5 — La Raspberry como cliente y el LED real

> **Objetivo**: que una **Raspberry Pi** de la sala, actuando como cliente, pregunte por la
> red al servidor del alumno y, según la respuesta, encienda o apague un **LED físico** por
> un pin GPIO. Se hace **por turnos** con las Pi compartidas.
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: cambias el estado con `curl` en tu portátil y, dos
> segundos después, el LED de la Raspberry se enciende de verdad.

## Requisitos previos

- Sesión 4 hecha: tu servidor escucha en `0.0.0.0:8000` y un compañero te alcanza por tu IP
  ([[04-salir-del-localhost-la-red-local]]).
- Tener anunciada **tu IP** (`192.168.1.50`) y conocer la **IP de la Pi** (`192.168.1.60`).
- La interfaz `Led` con `LedFalso`/`LedReal` ya está en el repo desde el diseño del curso
  (ver [[Curso_Servidores_y_Redes/00_README]]).

## El checkpoint de hoy

```bash
./bin/sesion.sh 5
./bin/sesion.sh 5 --solucion
```

Hoy el código está en `cliente_pi/cliente.py`, **no** en el servidor. Los `# TODO`:
1. el **bucle de polling** (`while True:` + `time.sleep`),
2. **leer la respuesta** del servidor (`requests.get(...).json()["encendido"]`),
3. llamar a `led.encender()` / `led.apagar()` según ese estado.

## Teoría

El servidor ya está expuesto. Ahora aparece un actor nuevo: un **cliente que vive en otra
máquina** y que, además, toca el mundo físico.

### GPIO: pines que tocan el mundo

La Raspberry tiene una fila de pines **GPIO** (General Purpose Input/Output): patillas
digitales que el programa puede poner a "alto" (3.3 V, ON) o "bajo" (0 V, OFF). Un LED se
conecta a un pin con una **resistencia en serie (~220 Ω)** para limitar la corriente y no
quemarlo:

```
   Pin GPIO 17 ──[ resistencia 220Ω ]──►|── GND
                                       LED
                                  (pata larga = +)
```

- Pin a ON  → pasa corriente → LED encendido.
- Pin a OFF → sin corriente → LED apagado.

La librería **`gpiozero`** envuelve todo esto en una API limpia: `LED(17).on()` / `.off()`.
Solo existe de verdad en la Pi; en el portátil no hay pines.

### Recuperar la interfaz `Led`: `LedReal` vs `LedFalso`

Aquí cobra sentido la pieza de diseño del curso. El cliente **no sabe** si habla con un LED
real o falso: solo conoce la **interfaz** `Led` (`encender()` / `apagar()`).

```python
class Led:                      # el CONTRATO: qué sabe hacer un LED
    def encender(self): ...
    def apagar(self):  ...

class LedFalso(Led):            # portátil: solo imprime
    def encender(self): print("💡 LED ON")
    def apagar(self):   print("⚫ LED OFF")

class LedReal(Led):             # Raspberry: mueve el pin físico
    def __init__(self, pin=17):
        from gpiozero import LED
        self._led = LED(pin)
    def encender(self): self._led.on()
    def apagar(self):   self._led.off()
```

Cambiar de simulado a real es **una línea** (o una variable de entorno):

```python
led = LedFalso()          # en el portátil
led = LedReal(pin=17)     # en la Raspberry
```

Esto es **programar contra interfaces / inversión de dependencias**: el código que usa el
LED depende de la *abstracción* `Led`, no de la *implementación* concreta. Por eso el mismo
`cliente.py` corre tal cual en tu portátil (con `LedFalso`, para depurar el bucle) y en la
Pi (con `LedReal`, para el LED de verdad). Probar la lógica sin hardware y luego "enchufar"
el real sin tocar nada más es el premio gordo de este patrón.

### Polling: preguntar cada X segundos

El cliente no es un servidor; **no recibe avisos**. Para enterarse de los cambios,
**pregunta** una y otra vez (*polling*):

```
   bucle:  GET /led ──► servidor ──► {"encendido": true}
           aplicar al LED
           dormir 2 s
           repetir
```

| Parámetro | Efecto si lo subes | Efecto si lo bajas |
|---|---|---|
| `sleep(2)` | menos tráfico, **más retardo** percibido | reacción más rápida, **martilleas** la red/servidor |

El `time.sleep(2)` **no es opcional**: sin él, el bucle dispara miles de peticiones por
segundo y satura todo. El polling es sencillo pero "tonto": siempre hay retardo y se
pregunta aunque no haya cambios. Esa limitación es la que arreglaremos con WebSockets en la
Sesión 8.

### SSH: entrar y arrancar el cliente en la Pi

La Pi no tiene (o no usas) teclado/pantalla: entras por **SSH** desde tu portátil, como una
terminal remota:

```bash
ssh usuario@192.168.1.60
```

Te pide la contraseña de la Pi y caes en su terminal. Desde ahí editas/arrancas
`cliente.py`. Detalles de SSH (claves, `scp`, sesiones) en [[MOC_Linux]].

## Manos a la obra

### 1. El cliente (rellena los `# TODO`)

`cliente_pi/cliente.py` — esqueleto del checkpoint:

```python
import time
import requests
from led import LedFalso, LedReal

SERVIDOR = "192.168.1.50"        # ← IP del servidor del alumno de turno
PUERTO   = 8000

# En la Pi: LedReal(pin=17).  En el portátil para probar: LedFalso()
led = LedReal(pin=17)
estado_anterior = None

while True:
    # TODO: pedir el estado al servidor y leer "encendido" de la respuesta JSON
    # TODO: si cambió respecto al anterior, encender o apagar el LED
    # TODO: dormir un par de segundos antes de volver a preguntar
    pass
```

Solución de referencia:

```python
import time
import requests
from led import LedFalso, LedReal

SERVIDOR = "192.168.1.50"
PUERTO   = 8000

led = LedReal(pin=17)
estado_anterior = None

while True:
    try:
        r = requests.get(f"http://{SERVIDOR}:{PUERTO}/led", timeout=3)
        encendido = r.json()["encendido"]
    except requests.RequestException as e:
        print("No alcanzo el servidor:", e)
        time.sleep(2)
        continue

    if encendido != estado_anterior:          # solo actuar si cambió
        led.encender() if encendido else led.apagar()
        estado_anterior = encendido

    time.sleep(2)                              # ← polling: NO quitar
```

> Comparar con `estado_anterior` evita reescribir el pin en cada vuelta; no es obligatorio,
> pero es buen estilo y suaviza el LED.

### 2. Probarlo primero en TU portátil (sin Pi)

Cambia una línea a `led = LedFalso()` y ejecútalo en tu portátil:

```bash
python cliente_pi/cliente.py
# (en otra terminal o desde otro PC)
curl -X POST http://192.168.1.50:8000/led -H "Content-Type: application/json" -d '{"encendido": true}'
```

Verás el `LedFalso` imprimir ` LED ON`. Así depuras el bucle **sin gastar turno de Pi**.

### 3. Pasarlo a la Raspberry (por turnos)

```bash
ssh usuario@192.168.1.60                 # entra en la Pi
# dentro de la Pi: ajusta SERVIDOR a TU IP y usa LedReal(pin=17)
python cliente_pi/cliente.py
```

Desde tu portátil cambia el estado con `curl` y mira el LED de la Pi: enciende ~2 s después.
Cuando termines, `Ctrl-C` para parar el cliente y dejar la Pi al siguiente.

## El muro

"Funciona, pero hay dos molestias: el polling cada 2 s siempre va con retraso, y controlar
todo a base de `curl` es incomodísimo y nada visual." Lo primero (tiempo real) se resuelve
en la Sesión 8; lo segundo, ya: vamos a darle **botones en una página web** servida por tu
propio FastAPI. → [[06-panel-web-en-el-navegador]].

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| El LED nunca enciende, sin error | IP del servidor mal puesta en `SERVIDOR` | Pon **tu** IP (`192.168.1.50`); pruébala con `curl` desde la Pi |
| `requests.exceptions.ConnectionError` | Servidor caído / no en `0.0.0.0` / firewall | Revisa Sesión 4: bind `0.0.0.0`, puerto abierto, misma red |
| `gpiozero ... permission denied` | El usuario no tiene acceso al GPIO | Añadir el usuario al grupo `gpio` (o ejecutar según la guía de la Pi) |
| El LED no luce o luce raro | Sin resistencia, pin equivocado o LED al revés | Resistencia ~220 Ω en serie; confirma pin 17; pata larga al + |
| La red se satura / el server peta | Olvidaste el `time.sleep(2)` | El bucle **debe** dormir entre peticiones |
| `ssh: Connection refused` | SSH no activo o IP de la Pi mal | Activa SSH en la Pi; verifica `192.168.1.60` con `ping` |

## Guion de la sesión

- **0–10** Recoge el muro de la Sesión 4: "te alcanzan por la red, pero el LED es de mentira".
  Enseña la Pi físicamente y el LED apagado: hoy se enciende de verdad.
- **10–30** Pizarra: GPIO + resistencia, `gpiozero`, y sobre todo la interfaz `Led` →
  inversión de dependencias (mismo cliente, dos LEDs). Explica polling y por qué el `sleep`.
- **30–80** `./bin/sesion.sh 5`, rellenar los TODO del bucle, **probar con `LedFalso` en el
  portátil** (todos a la vez), y luego **turnos de Pi**: SSH, ajustar IP y pin, `LedReal`,
  encender con `curl` desde el portátil. 2 min por persona, que gestione los turnos el rol
  encargado de las Raspberry.
- **80–90** Puesta en común: el mismo `cliente.py` corrió en dos sitios sin cambios de lógica
  (esa es la lección). Plantea el muro hacia la web.

## Conexiones
- [[04-salir-del-localhost-la-red-local]] — la sesión anterior (red local lista)
- [[06-panel-web-en-el-navegador]] — la siguiente: botones en el navegador
- [[08-tiempo-real-con-websockets]] — donde se elimina el retardo del polling
- [[Curso_Servidores_y_Redes/00_README]] — la interfaz Led y la estrategia con pocas Raspberry
- [[MOC_Linux]] — SSH, permisos, grupos
