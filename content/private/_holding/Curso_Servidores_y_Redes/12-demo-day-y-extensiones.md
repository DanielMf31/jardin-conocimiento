---
title: Sesión 12 — Demo day y extensiones
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 12 Demo Day, Cierre del Curso]
---

# Sesión 12 — Demo day y extensiones

> **Objetivo**: **consolidar** todo lo aprendido, que **cada alumno enseñe su variante** del
> sistema funcionando, y **abrir caminos** para seguir aprendiendo (y para guiar el curso el
> año que viene).
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: una **mini-feria de demos**. Cada uno arranca su servidor
> (a estas alturas, en contenedor), enciende el LED real por turnos en la Raspberry de la sala,
> enseña la pieza de la que está orgulloso (su panel, su tiempo real, su seguridad) y cuenta una
> extensión que le gustaría hacer.

## Requisitos previos

- Sesiones 1–11 hechas: tienes el sistema **completo** — servidor FastAPI con `GET/POST /led`,
  telemetría, panel web, SQLite, WebSockets, API key con `.env`, cliente resiliente y todo
  empaquetado en Docker ([[11-empaquetar-con-docker]]).
- Tu servidor **arranca** (con `uvicorn` o `docker run`) y la Pi puede apuntarle.
- Una idea, aunque sea vaga, de **qué te gustaría seguir construyendo**.

> Hoy **no se escribe código nuevo**. Es la sesión de cierre: repasar, enseñar y proyectar.

## Recorrido del curso

De `localhost` a un contenedor portable, una rebanada vertical por semana. Cada sesión añadió
algo visible **y** un fundamento de redes/software:

| # | Sesión | Qué quedó funcionando | El fundamento que entró |
|---|---|---|---|
| 0 | [[00_setup-entorno-y-repo]] | entorno, repo y `./bin/sesion.sh` | terminal, venv, git básico |
| 1 | [[01-vision-del-proyecto-y-primer-servidor]] | demo final + tu `GET /ping` en local | cliente/servidor, localhost, puerto |
| 2 | [[02-curl-y-los-verbos-http]] | enciendes el LedFalso con `curl` | HTTP, GET/POST, headers, body |
| 3 | [[03-json-y-validacion-pydantic]] | el server recibe y **valida** JSON | JSON, Pydantic, códigos de estado |
| 4 | [[04-salir-del-localhost-la-red-local]] | un compañero te llama por tu IP | IP, LAN, `0.0.0.0`, TCP/IP, firewall |
| 5 | [[05-la-raspberry-como-cliente-y-el-led-real]] | el **LED físico** obedece al servidor | GPIO, SSH, polling, la interfaz `Led` |
| 6 | [[06-panel-web-en-el-navegador]] | una web con botones controla el LED | frontend, navegador como cliente, `fetch` |
| 7 | [[07-persistencia-con-sqlite]] | el histórico sobrevive a reiniciar | bases de datos, SQL, estado durable |
| 8 | [[08-tiempo-real-con-websockets]] | el LED reacciona al instante | polling vs push, WebSockets, latencia |
| 9 | [[09-seguridad-y-secretos]] | solo quien tiene la clave manda | autenticación, secretos, `.env`, `.gitignore` |
| 10 | [[10-resiliencia-y-manejo-de-errores]] | se recupera solo cuando algo falla | timeouts, reintentos, logging |
| 11 | [[11-empaquetar-con-docker]] | arranca **igual en cualquier máquina** | contenedores, imágenes, reproducibilidad |

Mira la tabla en perspectiva: empezaste con un servidor que solo se hablaba a sí mismo y has
terminado con un sistema cliente-servidor en red, seguro, en tiempo real, persistente,
resiliente y portable, que enciende un LED de verdad. Eso es un proyecto real.

## Ideas de extensión

Caminos para quien quiera seguir. Cada uno **reusa un fundamento del curso** y añade uno nuevo:

| Extensión | Qué fundamento del curso toca | Qué añade de nuevo |
|---|---|---|
| **Varios LEDs y brillo (PWM)** | la interfaz `Led` (Sesión 5), `POST /led` | PWM, control analógico de un pin, modelar varios actuadores |
| **Leer un sensor real y graficarlo** | telemetría + panel web (Sesiones 3, 6) | un `GET /sensor`, leer hardware de entrada, graficar en el navegador |
| **Mover un servo** | la interfaz `Led` → interfaz `Actuador`, `POST` (Sesión 5) | control de ángulo/posición, generalizar el patrón a otro actuador |
| **Varios nodos Raspberry** | el cliente de polling (Sesiones 5, 10) | varios clientes a la vez, identificar cada nodo, coordinarlos |
| **Autenticación de usuarios de verdad** | la API key y `.env` (Sesión 9) | login con usuario/contraseña, sesiones/tokens, roles |
| **Sacar el sistema fuera de la LAN (con cuidado)** | `0.0.0.0` y red (Sesión 4), Docker (Sesión 11) | registry, despliegue, HTTPS, **mucha** atención a la seguridad → [[MOC_GCP]] |
| **Tests automáticos del servidor** | toda la API (Sesiones 2–9) | `pytest`, testear endpoints, no romper lo que ya funciona → [[MOC_Desarrollo_Software]] |

Aviso sobre "sacar el sistema fuera de la LAN": durante todo el curso vivimos a propósito en
red local (`192.168.1.x`, sin internet) porque es más simple y más seguro. Abrir un servidor a
internet sin saber lo que haces es **peligroso**; es un proyecto serio en sí mismo, no un
"añadir una línea". Hazlo con cabeza y revisando seguridad primero.

## Cómo seguir aprendiendo

Según lo que te haya enganchado del curso, por dónde profundizar:

- **Te gustó la parte de redes / HTTP / cómo viajan los datos** → fundamentos de redes y
  sistemas en [[MOC_CS_Fundamentos]].
- **Te gustó programar el servidor / Python / la API** → más backend y patrones en
  [[MOC_Programacion]]; cómo trabajar en equipo y por entregables en [[MOC_Desarrollo_Software]].
- **Te picó la curiosidad la API key, los secretos y "¿y si alguien ataca esto?"** →
  seguridad en [[MOC_Ciberseguridad]].
- **Te gustó manejar la Pi, los procesos, los logs** → terminal y sistema en [[MOC_Linux]].

No hace falta seguirlos todos. Elige el que te haya dado más curiosidad y tira de ese hilo.

## El relevo

El mejor sitio para consolidar lo que sabes es **enseñárselo a alguien**. Quien ha hecho el
curso este año puede **guiar** a los nuevos el año que viene, y no es un favor altruista: **se
aprende enseñando**. Explicar por qué `0.0.0.0` y no `127.0.0.1`, o por qué un timeout salva al
cliente, te obliga a entenderlo de verdad — descubres los huecos justo cuando intentas contarlo.

Además, este proyecto es la **base del siguiente bloque** del itinerario de la asociación: un
sistema cliente-servidor en red, con un actuador físico, seguro y empaquetado, es el cimiento
sobre el que montar cosas más ambiciosas (más sensores, más nodos, robots de verdad). Los
veteranos no solo guían: arrancan ese siguiente bloque con ventaja.

El modelo del curso lo facilita: roles que se rotan entre cuatrimestres (quien guía, quien
gestiona las Raspberry, quien apunta dudas). El demo day de hoy es, de hecho, la audición
natural para los guías del año que viene.

## Guion del demo day

Tiempos orientativos (~90 min). La clave: **demos cortas y que el LED real pase por las manos
de todos**.

| Bloque | Tiempo | Qué pasa |
|---|---|---|
| **Montaje** | 0–15 | cada uno arranca su servidor (uvicorn/Docker), prepara las Raspberry y se anuncian las IPs en el canal de la sala |
| **Rondas de demos** | 15–60 | turnos de **3–5 min por persona**: enseña tu sistema y la pieza de la que estás orgulloso (tu panel, tu tiempo real, tu seguridad) |
| **Turnos del LED real** | (durante las demos) | por turnos, la Pi apunta a TU servidor y enciendes el LED **físico** delante de todos — 2 min por persona |
| **Foto de grupo** | 60–70 | con las Pi y los LEDs encendidos; cierre del bloque |
| **Retro** | 70–90 | qué funcionó, qué mejorar, quién quiere guiar el año que viene |

La **retro** del final, breve y honesta, recoge: ¿qué sesión costó más? ¿qué muro fue el más
satisfactorio de superar? ¿qué cambiarías del curso? ¿quién se anima a guiar? Apunta las
respuestas: son el material para mejorar el bloque y para arrancar el relevo.

### Consejos para que el demo day salga bien

- **Demos cortas.** 3–5 min y al siguiente. Mejor que todos enseñen algo a que dos se eternicen.
- **Todo en red local.** Igual que siempre: `192.168.1.x`, sin internet, sin sorpresas de
  conectividad el día clave.
- **Prepara las Pi por turnos** y con orden. Una sola Pi pasando por todos cunde si hay una
  lista de turnos clara; no improvises el reparto del hardware sobre la marcha.
- **Ten lista la red de seguridad.** Si a alguien no le arranca su servidor en el momento,
  `./bin/sesion.sh 11 --solucion` y a enseñar igualmente: el objetivo es que cada uno presente,
  no dejar a nadie fuera por un fallo de última hora.
- **Que el LED real lo encienda cada persona.** Es la recompensa de todo el curso: un programa
  tuyo cambia algo en el mundo físico. Que nadie se vaya sin ese momento.

## Conexiones
- [[11-empaquetar-con-docker]] — la sesión anterior (servidor portable)
- [[Curso_Servidores_y_Redes/00_README]] — la visión completa del curso y su modelo pedagógico
- [[01-vision-del-proyecto-y-primer-servidor]] — dónde empezó todo (la demo y el primer server)
- [[MOC_CS_Fundamentos]] — seguir con redes y fundamentos
- [[MOC_Programacion]] — seguir con backend y programación
- [[MOC_Ciberseguridad]] — seguir con seguridad
- [[MOC_Linux]] — seguir con sistema y terminal
- [[MOC_Desarrollo_Software]] — tests, equipo, iterar por entregables
- [[MOC_GCP]] — a dónde escalaría si saliera de la red local
