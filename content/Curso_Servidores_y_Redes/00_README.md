---
title: Curso de Servidores y Redes — README del clúster
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso, meta]
type: nota
status: en-progreso
source: claude-code
aliases: [Curso Servidores y Redes, Curso FastAPI LED]
---

# Curso de Servidores y Redes — Controla un LED por la red

Segundo bloque del itinerario de la asociación, **después** del curso de Linux, C y Python.
La idea no es "otro curso de teoría": es construir, entre todos y semana a semana, **un
sistema real que enciende un LED físico desde un servidor por la red local**, aprendiendo
los fundamentos (HTTP, redes, APIs) *cuando el proyecto los pide*, no antes.

## Qué se construye (el proyecto)

Un sistema cliente-servidor sobre la red local (LAN):

```
   ┌─────────────────────────┐         red local (LAN)        ┌────────────────────────┐
   │  PORTÁTIL del alumno     │  ◄───────── HTTP ──────────►   │   RASPBERRY PI         │
   │  servidor FastAPI        │                                │   cliente que pregunta │
   │  - GET /led  (estado)    │     192.168.1.50:8000          │   cada X s y enciende  │
   │  - POST /led (cambiar)   │                                │   el LED real (GPIO)   │
   │  - POST /telemetria      │                                │                        │
   │  - panel web + WebSocket │                                │   LED                │
   └─────────────────────────┘                                └────────────────────────┘
```

El **alumno escribe el servidor**. El LED vive en una Raspberry Pi compartida de la sala.
Al final del curso el servidor también tiene panel web, persistencia, tiempo real,
seguridad y va dentro de un contenedor.

### Por qué un LED
Es el actuador más barato que existe (20 céntimos) y da la misma recompensa que un robot
entero: *un programa tuyo cambia algo en el mundo físico*. Es la prueba de que "esto
funciona de verdad". Lo ambicioso (robots, sensores) son extensiones de la Sesión 12.

## El modelo pedagógico (cómo está pensado)

1. **Demo primero.** En la Sesión 1 se enseña el proyecto **ya terminado** funcionando, y
   cómo funciona por encima. Así todos saben a dónde van.
2. **Esqueleto andante.** No se construye "el servidor entero y luego el cliente". Desde la
   primera sesión hay algo de punta a punta que funciona (aunque sea trivial), y cada
   semana se le añade **una rebanada vertical** nueva.
3. **Fundamentos bajo demanda.** Redes, HTTP, etc. no se leen "de primeras". El proyecto
   choca contra un muro ("¿por qué no me responde desde el otro portátil?") y *entonces* se
   explica el concepto, 20 minutos, cuando todos tienen la pregunta en la cabeza.
4. **Una sesión = un entregable visible + un fundamento.** Cada semana algo nuevo funciona.
   Eso es lo que hace que la gente vuelva.

## El LED falso y el LED real (la pieza clave de diseño)

El truco que hace que **todos** trabajen aunque haya pocas Raspberry: el servidor no habla
con un LED concreto, habla con una **interfaz** `Led`. Hay dos implementaciones
intercambiables:

```python
# led.py
class Led:                       # la interfaz: qué sabe hacer un LED
    def encender(self): ...
    def apagar(self): ...

class LedFalso(Led):             # en el PORTÁTIL: solo imprime
    def encender(self): print("💡 LED ON")
    def apagar(self):   print("⚫ LED OFF")

class LedReal(Led):              # en la RASPBERRY: enciende el pin físico
    def __init__(self, pin=17):
        from gpiozero import LED
        self._led = LED(pin)
    def encender(self): self._led.on()
    def apagar(self):   self._led.off()
```

Cambiar de simulado a real es **una línea** (o una variable de entorno). Así:
- Cada alumno tiene el **bucle completo funcionando en su portátil** desde el día 1 con `LedFalso`.
- La **Raspberry compartida** entra cuando toca, y solo cambia esa línea para tener el LED real.
- De paso se enseña, sin decirlo, **inversión de dependencias** (programar contra interfaces).

## Estrategia con pocas Raspberry Pi

- **Todos** trabajan en su portátil con `LedFalso` → nadie espera por hardware.
- **1–2 Raspberry** en la red local, cada una con su IP fija (ej. `192.168.1.60`).
- En las sesiones con Pi se hace **por turnos**: el alumno apunta la Pi a la IP de *su*
  servidor y ve *su* LED encenderse. Dura 2 minutos por persona y todos pasan.
- Todo es **red local**: sin internet, sin abrir puertos al exterior, sin túneles. Las IPs
  privadas (`192.168.x.x`) lo simplifican muchísimo y son, además, un buen tema de redes.

## Modelo y práctica por sesión

El **repositorio del curso** guarda el código en dos carpetas paralelas (igual que el
[[Curso_Python/00_README|Curso de Python]]):

- `modelo/sNN` → el código **completo** de esa sesión (lo que enseñas / la referencia).
- `practica/sNN` → el **esqueleto con `# TODO`** de esa sesión (lo que rellena el alumno).

Un script copia el estado elegido a una carpeta de trabajo (`trabajo/`):

```bash
./bin/sesion.sh 3            # copia la PRÁCTICA de la Sesión 3 a  trabajo/  (con # TODO)
./bin/sesion.sh 3 --modelo   # copia el MODELO de la Sesión 3 (resuelto, si te atascas)
```

Así se separa **"entender la red/HTTP"** (el objetivo) de la fontanería del repo. El
proyecto **completo y funcional** es `modelo/s12` (la demo de la Sesión 1).
El detalle del repo, el script y el entorno está en [[00_setup-entorno-y-repo]].

## Índice de sesiones

| # | Sesión | Qué se ve funcionando al final | Fundamento que entra |
|---|---|---|---|
| 0 | [[00_setup-entorno-y-repo]] | Entorno listo, repo clonado, `./bin/sesion.sh` | terminal, venv, git básico |
| 1 | [[01-vision-del-proyecto-y-primer-servidor]] | Demo final + tu primer `GET /ping` en local | cliente/servidor, localhost, puerto |
| 2 | [[02-curl-y-los-verbos-http]] | Enciendes el LedFalso con `curl` | HTTP, GET/POST, headers, body, curl |
| 3 | [[03-json-y-validacion-pydantic]] | El server recibe y valida datos JSON | JSON, Pydantic, códigos de estado |
| 4 | [[04-salir-del-localhost-la-red-local]] | Un compañero llama a TU servidor por tu IP | IP, LAN, 0.0.0.0, TCP/IP, firewall |
| 5 | [[05-la-raspberry-como-cliente-y-el-led-real]] | El LED **físico** obedece a tu servidor | GPIO, SSH, polling, la interfaz Led |
| 6 | [[06-panel-web-en-el-navegador]] | Una web con botones controla el LED | frontend, navegador como cliente, fetch |
| 7 | [[07-persistencia-con-sqlite]] | El histórico sobrevive a reiniciar | bases de datos, SQL básico, estado durable |
| 8 | [[08-tiempo-real-con-websockets]] | El LED reacciona al instante | polling vs push, WebSockets, latencia |
| 9 | [[09-seguridad-y-secretos]] | Solo quien tiene la clave manda | autenticación, secretos, `.env`, `.gitignore` |
| 10 | [[10-resiliencia-y-manejo-de-errores]] | Se recupera solo cuando algo falla | timeouts, reintentos, logging |
| 11 | [[11-empaquetar-con-docker]] | El server arranca igual en cualquier máquina | contenedores, imágenes, reproducibilidad |
| 12 | [[12-demo-day-y-extensiones]] | Cada uno enseña su variante | consolidación + cómo seguir |

## Cómo se imparte (el ritual semanal)

Sesión fija, mismo día y hora. Estructura recomendada (~90 min):

```
0–10 min   Demo / repaso: qué construimos hoy y por qué (el muro de la semana pasada)
10–30 min  Teoría just-in-time: el fundamento que el proyecto pide hoy (pizarra)
30–80 min  Manos a la obra: ./bin/sesion.sh N, rellenar los TODO, probar con curl/navegador
80–90 min  Puesta en común + el muro que abre la sesión siguiente
```

Roles que conviene repartir (y rotar entre cuatrimestres):
- **Quien guía** la sesión (al principio tú; luego, alumnos veteranos).
- **Quien gestiona las Raspberry** y los turnos del LED real.
- **Quien apunta dudas** en un canal común para resolverlas en la puesta en común.

## Stack y material

- **Software**: Python 3, FastAPI, Uvicorn, `requests`/`httpx`, SQLite, `gpiozero` (en la Pi), Docker (Sesión 11).
- **Hardware**: portátiles de los alumnos + 1–2 Raspberry Pi con un LED y una resistencia (~220 Ω) en un pin GPIO. Un router/switch para la red local.
- **Repo del curso**: con las carpetas `modelo/` y `practica/` por sesión (ver [[00_setup-entorno-y-repo]]).

## Conexiones
- [[MOC_Programacion]] — el área padre
- [[MOC_CS_Fundamentos]] — redes, HTTP, bases de datos (la teoría de fondo de cada sesión)
- [[MOC_Linux]] — terminal, IPs, SSH, procesos (se usa en todas las sesiones)
- [[MOC_GitLab]] — git y el repositorio del curso
- [[MOC_Desarrollo_Software]] — trabajar en equipo, iterar por entregables
- [[MOC_GCP]] — a dónde escalaría esto si algún día sale de la red local
