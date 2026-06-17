---
title: Curso de Python (puente desde C) — índice y guía
date: 2026-06-16
tags: [programacion/python, curso, programacion/fundamentos, meta]
type: nota
status: en-progreso
source: claude-code
aliases: [Curso Python, Curso de Python, MOC Curso Python]
---

# Curso de Python (puente desde C) — índice y guía

Curso de **Python básico** pensado como **puente desde C**: los mismos conceptos, sin la ceremonia, con
comparación **C ↔ Python** en cada tema. Termina apuntando a **NeetCode** (algoritmos).

## Cómo está organizado
- **`modelo/`** — teoría (`.md`) + soluciones: lo que usas TÚ para enseñar.
- **`practica/<modulo>/`** — por ejercicio: `ejNN_modelo.py` (resuelto) + `ejNN_practica.py` (esqueleto con `# TODO`).
- Cada `.py` lleva **cabecera** (módulo, nº, enunciado, dificultad, `python3 ejNN.py`).
- **Sin compilar**: Python se ejecuta directo (`python3 archivo.py`) — no hace falta carpeta de "compilados".

## Ruta de los módulos
| # | Módulo | Doc |
|---|---|---|
| 00 | Python vs C (el puente) | [[Curso_Python/modelo/00-python-vs-c]] |
| 01 | Variables, tipos y E/S | [[Curso_Python/modelo/01-variables]] |
| 02 | Condicionales | [[Curso_Python/modelo/02-condicionales]] |
| 03 | Bucles | [[Curso_Python/modelo/03-bucles]] |
| 04 | Funciones | [[Curso_Python/modelo/04-funciones]] |
| 05 | Listas y comprehensions | [[Curso_Python/modelo/05-listas]] |
| 06 | **Cadenas: transformar y formatear** | [[Curso_Python/modelo/06-cadenas]] |
| 07 | Diccionarios y sets (hash maps) | [[Curso_Python/modelo/07-diccionarios-sets]] |
| 08 | Clases, dataclasses y archivos | [[Curso_Python/modelo/08-clases-archivos]] |
| 09 | Puente a NeetCode | [[Curso_Python/modelo/09-puente-neetcode]] |

## Cómo impartir cada módulo
1. Enseña la teoría con la **tabla C↔Python** (conecta con lo que ya saben).
2. Worked-example en vivo: `python3 ejNN_modelo.py` (resultado al instante).
3. Los alumnos abren `ejNN_practica.py` y rellenan los `# TODO`, de (facil) a (dificil).
4. Autocomprueban con la *salida esperada* del `.md`.

## La ruta completa
```
C (explícito)  →  Python (mismos conceptos, cómodo)  →  Python + NeetCode (algoritmos)
```
- Viene del [[Curso_C/00_README|Curso de C]].
- Los módulos 05-07 (listas, **cadenas**, dicts/sets) dan justo las herramientas de [[MOC_NeetCode_150]].

## Conexiones
- [[MOC_NeetCode_150]] · [[MOC_Programacion]] · [[Curso_Python/modelo/00-python-vs-c]]
