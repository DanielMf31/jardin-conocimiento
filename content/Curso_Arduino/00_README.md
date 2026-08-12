---
title: Curso de Arduino — índice y guía para impartirlo
date: 2026-08-12
tags: [programacion/arduino, curso, electronica, meta]
type: nota
status: permanente
source: claude-code
aliases: [Curso Arduino, Curso de Arduino, MOC Curso Arduino, Arduino ESP32]
---

# Curso de Arduino + ESP32 — índice y guía

Curso práctico de electrónica y programación de microcontroladores: **Arduino UNO** en los módulos 01
a 08 y **ESP32** en el 09 y el 10, con un proyecto integrador pendiente. La diferencia con el resto de
cursos del jardín es que aquí el código no se compila y se ejecuta: se **simula** con Wokwi, así que
puedes hacer el curso entero **sin comprar una placa**.

**Empieza por aquí:** [[Curso_Arduino/modelo/00-onboarding|Onboarding — montar el entorno]] — cómo
simular en el navegador en un minuto, o montar VS Code con la extensión de Wokwi si vas en serio.

## Cómo está organizado
- **`modelo/`** — la teoría de cada módulo: el modelo mental, los conceptos y los errores típicos.
- **`practica/<modulo>/`** — una **nota web por ejercicio**: enunciado, montaje, explicación, el código
  para copiar (esqueleto y solución) y el circuito en `diagram.json` para pegarlo en Wokwi.
- Las notas de práctica se **generan** desde el repo del curso (`curso-arduino/practica/`, la fuente de
  verdad) con `gen_course.py` del framework Ágora, se espejan a la bóveda y de ahí se publican aquí por
  `contentSync`; no se editan a mano en el jardín (la explicación se edita en el repo del curso).

## Ruta de los módulos
| # | Módulo | Placa | Doc |
|---|---|---|---|
| 00 | Onboarding: VS Code, Wokwi y la licencia | — | [[Curso_Arduino/modelo/00-onboarding]] |
| 01 | Fundamentos y GPIO digital | UNO | [[Curso_Arduino/modelo/01-fundamentos]] |
| 02 | Entradas digitales | UNO | [[Curso_Arduino/modelo/02-entradas-digitales]] |
| 03 | Salidas analógicas (PWM) | UNO | [[Curso_Arduino/modelo/03-salidas-analogicas-pwm]] |
| 04 | Entradas analógicas | UNO | [[Curso_Arduino/modelo/04-entradas-analogicas]] |
| 05 | Comunicación serie | UNO | [[Curso_Arduino/modelo/05-comunicacion-serie]] |
| 06 | Sensores comunes | UNO | [[Curso_Arduino/modelo/06-sensores-comunes]] |
| 07 | Actuadores y potencia | UNO | [[Curso_Arduino/modelo/07-actuadores-y-potencia]] |
| 08 | Pantallas | UNO | [[Curso_Arduino/modelo/08-pantallas]] |
| 09 | Salto a ESP32 + WiFi | ESP32 | [[Curso_Arduino/modelo/09-esp32-wifi]] |
| 10 | ESP32 IoT (MQTT / API) | ESP32 | [[Curso_Arduino/modelo/10-esp32-iot-mqtt]] |
| 11 | Proyecto integrador | ESP32 | *en camino* |

**Práctica:** [[Curso_Arduino/practica/00_README|Ejercicios resueltos]] — una nota por ejercicio, con
su circuito listo para simular.

## Cómo impartir cada módulo
1. **El esquema primero**, antes de tocar código: qué hace el micro, qué es un pin, qué se repite.
2. **Worked-example en vivo** con el simulador proyectado: se ve el LED encenderse, y eso engancha.
3. Los alumnos abren `ejNN_practica.ino` y suben de dificultad (verde → amarillo → rojo).
4. **Autocomprueban** simulando: si el circuito hace lo que pide el enunciado, está bien. La solución
   de referencia es `ejNN_modelo.ino`.

## Seguridad transversal
- Resistencia **siempre** en serie con cada LED (220 Ω); sin ella se degrada el LED y sufre el pin.
- Motores y relés con driver y fuente aparte: **nunca** alimentados desde un pin.
- El ESP32 trabaja a **3.3 V**: no le metas 5 V a un GPIO.

## Conexiones
- [[Curso_C/00_README|Curso de C]] · [[Curso_Python/00_README|Curso de Python]]
