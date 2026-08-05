---
title: Curso de C — índice y guía para impartirlo
date: 2026-06-16
tags: [programacion/c, curso, programacion/fundamentos, meta]
type: nota
status: permanente
source: claude-code
aliases: [Curso C, Curso de C, MOC Curso C]
---

# Curso de C (puro) — índice y guía

Curso de **C puro** (no C++), de lo básico a archivos, con **mucho ejercicio**. Pensado para impartirse
apoyado en la terminal de Linux y como **on-ramp** hacia Python y los problemas de NeetCode.

## Cómo está organizado
- **`modelo/`** — la teoría (`.md`) de cada módulo: lo que usas TÚ para enseñar.
- **`practica/<modulo>/`** — una **nota web por ejercicio** (enunciado, diagrama de flujo,
  explicación y el código para copiar). El alumno la abre en el navegador y resuelve sin descargar nada.
- Las notas de práctica se **generan** desde el repo del curso (`curso-c/practica/`, la fuente de
  verdad) con `gen_course.py` del framework Ágora, se espejan a la bóveda y de ahí se publican aquí
  por `contentSync`; no se editan a mano en el jardín (la explicación se edita en el repo del curso).

## Ruta de los módulos
| # | Módulo | Doc |
|---|---|---|
| 00 | Qué es C, el compilador, historia y contexto | [[Curso_C/modelo/00-que-es-c]] |
| 01 | Variables, tipos y E/S | [[Curso_C/modelo/01-variables]] |
| 02 | Condicionales | [[Curso_C/modelo/02-condicionales]] |
| 03 | Bucles | [[Curso_C/modelo/03-bucles]] |
| 04 | Funciones | [[Curso_C/modelo/04-funciones]] |
| 05 | Arrays y cadenas | [[Curso_C/modelo/05-arrays-cadenas]] |
| 06 | Matrices (2D) | [[Curso_C/modelo/06-matrices]] |
| 07 | Punteros | [[Curso_C/modelo/07-punteros]] |
| 08 | Structs | [[Curso_C/modelo/08-structs]] |
| 09 | Lectura/escritura de archivos | [[Curso_C/modelo/09-archivos]] |

**Práctica:** [[Curso_C/practica/00_README|Ejercicios resueltos]] — una nota por ejercicio, para resolver directamente en el navegador (empezando por el módulo 01).

**Extra (cultura):** [[Curso_C/modelo/historia-de-c|Historia de C]] — de dónde viene el lenguaje, su evolución a lo largo de los años y las cosas increíbles que se han construido con él.

## Cómo impartir cada módulo
1. **Explica la teoría** (schema-first: categoría → patrón → sintaxis) con el `.md` del módulo.
2. **Worked-example en vivo**: compila con `gcc -std=c11 -Wall` (o `entr` para recompilar al guardar).
3. Los alumnos abren `ejNN_practica.c` y suben de (facil) a (dificil).
4. **Autocomprueban** con la *salida esperada* del `.md`; la solución es `ejNN_modelo.c`.

## Setup (Ubuntu desde cero)
```bash
bash setup.sh   # instala gcc/make/gdb + entr (auto-recompila), y verifica
```

## La ruta completa (más allá de C)
```
Linux (terminal, gcc)  →  C (explícito)  →  Python (mismos conceptos, cómodo)  →  Python + NeetCode
```
- Anclado en los primeros apuntes del Linux (compilar en terminal).
- Después: puente **C → Python** (misma lógica, otra sintaxis) → NeetCode 150.

## Conexiones
- Linux · Programacion · NeetCode 150
