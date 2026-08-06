---
title: Curso de Python — índice y guía para impartirlo
date: 2026-08-06
tags: [programacion/python, curso, programacion/fundamentos, meta]
type: nota
status: permanente
source: claude-code
aliases: [Curso Python, Curso de Python, MOC Curso Python]
---

# Curso de Python — índice y guía

Curso de **Python** desde cero, de lo básico a clases y archivos, con **mucho ejercicio** y un puente final a los problemas de NeetCode. Pensado como continuación natural del curso de C: los mismos fundamentos, ahora con una sintaxis más cómoda.

## Cómo está organizado

- **`modelo/`** — la teoría (`.md`) de cada módulo: lo que usas TÚ para enseñar. Cada tema termina con enlaces a todos sus ejercicios.
- **`practica/<modulo>/`** — una **nota web por ejercicio** (enunciado, explicación paso a paso y el código para copiar: esqueleto + solución). El alumno la abre en el navegador y resuelve sin instalar nada.
- Las notas de práctica se **generan** desde el repo del curso (`curso-python/practica/`, la fuente de verdad) con `gen_course.py` del framework Ágora, se espejan a la bóveda y de ahí se publican aquí por `contentSync`.

## Ruta de los módulos

| # | Módulo | Doc |
|---|---|---|
| 00 | Python frente a C: qué cambia | [[Curso_Python/modelo/00-python-vs-c]] |
| 01 | Variables, tipos y entrada/salida | [[Curso_Python/modelo/01-variables]] |
| 02 | Condicionales | [[Curso_Python/modelo/02-condicionales]] |
| 03 | Bucles | [[Curso_Python/modelo/03-bucles]] |
| 04 | Funciones | [[Curso_Python/modelo/04-funciones]] |
| 05 | Listas y comprehensions | [[Curso_Python/modelo/05-listas]] |
| 06 | Cadenas | [[Curso_Python/modelo/06-cadenas]] |
| 07 | Diccionarios y sets | [[Curso_Python/modelo/07-diccionarios-sets]] |
| 08 | Clases y archivos | [[Curso_Python/modelo/08-clases-archivos]] |
| 09 | Puente a NeetCode | [[Curso_Python/modelo/09-puente-neetcode]] |

**Práctica:** [[Curso_Python/practica/00_README|Ejercicios resueltos]] — una nota por ejercicio, para resolver directamente en el navegador (empezando por el módulo 01).

**Extra (cultura):** [[Curso_Python/modelo/historia-de-python|Historia de Python]] — de dónde viene el lenguaje y por qué se ha vuelto omnipresente.

## Cómo impartir cada módulo

1. **Explica la teoría** con el `.md` del módulo (idea central, qué aprendes, ejemplos).
2. **Ejemplo en vivo**: ejecuta con `python3` en la terminal, mostrando el resultado.
3. Los alumnos abren `ejNN_practica.py` y suben de (fácil) a (difícil).
4. **Autocomprueban** con la solución `ejNN_modelo.py` y la explicación de la nota.

## La ruta completa

```
C (explícito, cercano a la máquina)  →  Python (mismos conceptos, más cómodo)  →  Python + NeetCode 150
```

El módulo 09 es el puente: los patrones de entrevista (dos punteros, hash set/dict, sliding window) con los que se entra a NeetCode.

## Conexiones

- [[Curso_C/00_README|Curso de C]] · Programacion · NeetCode 150
