---
title: "00 — Qué es C, el compilador y cómo funciona"
date: 2026-06-16
tags: [programacion/c, curso, programacion/fundamentos]
type: nota
status: en-progreso
source: claude-code
aliases: [Qué es C, Introducción a C, Contexto C]
---

# 00 — Qué es C, el compilador y cómo funciona

## Idea central
C es un lenguaje **compilado** y **cercano a la máquina**: tú escribes texto, un **compilador** lo traduce a un **ejecutable binario** que la CPU corre directamente. Aprender C te obliga a entender lo que otros lenguajes esconden (tipos, memoria, punteros) — por eso es la mejor base antes de Python.

## Qué aprendes
| Concepto | Para qué sirve |
|---|---|
| Lenguaje compilado vs interpretado | Entender por qué C necesita "compilar" y Python no |
| El pipeline del compilador | Saber qué pasa entre tu `.c` y el ejecutable |
| `gcc` | La herramienta que compila en Linux |
| Estructura mínima de un programa | El esqueleto `main()` que repetirás siempre |

## Un poco de historia (para tener contexto)
- C lo creó **Dennis Ritchie** en **Bell Labs (~1972)** para escribir el sistema operativo **Unix**. Por eso C y Unix/Linux están entrelazados.
- El libro **"The C Programming Language" (K&R)** de Kernighan y Ritchie es la biblia histórica.
- Estándares: **C89/C90** (ANSI C), **C99**, **C11**, **C17**. Nosotros usamos **C11** básico.
- Por qué sigue importando hoy: el **kernel de Linux**, drivers, **sistemas embebidos** (tu terreno: microcontroladores, firmware), bases de datos y hasta otros lenguajes (Python está escrito en C). Si entiendes C, entiendes **cómo funciona la máquina por debajo**.

## Compilado vs interpretado (clave para el puente a Python)
- **C (compilado)**: el código fuente `.c` → se **traduce una vez** a un binario nativo → lo ejecutas. Rápido y explícito, pero hay que recompilar al cambiar.
- **Python (interpretado)**: un intérprete lee y ejecuta el código **al vuelo**, sin paso de compilación. Más cómodo, menos control.
- Mismo razonamiento lógico (variables, bucles, condicionales); cambia la **ceremonia**. Por eso: primero C (entiendes lo explícito), luego Python (lo mismo, cómodo).

## Cómo funciona el compilador (el pipeline)
Cuando ejecutas `gcc programa.c -o programa`, pasan 4 fases (gcc las hace todas seguidas):
```
programa.c
  │  1) PREPROCESADOR  → resuelve #include, #define (pega cabeceras, sustituye macros)
  │  2) COMPILADOR     → traduce C a ensamblador
  │  3) ENSAMBLADOR    → ensamblador a código máquina (.o, objeto)
  │  4) ENLAZADOR      → une tu .o con librerías (p.ej. printf) → EJECUTABLE
  ▼
programa  (binario que la CPU corre: ./programa)
```

## Cómo compilar y ejecutar (lo que harás todo el curso)
```bash
gcc -std=c11 -Wall programa.c -o programa   # compilar (con avisos -Wall)
./programa                                   # ejecutar
```
- `-std=c11`: usa el estándar C11. `-Wall`: activa **todos los avisos** (te chiva errores comunes). `-o programa`: nombre del ejecutable.
- Truco para no recompilar a mano (auto al guardar): `echo programa.c | entr -cr sh -c 'gcc -std=c11 -Wall programa.c -o programa && ./programa'`

## Estructura mínima de un programa C
```c
#include <stdio.h>   /* trae printf, scanf... */

int main(void) {     /* el programa empieza aquí */
    printf("Hola, mundo\n");
    return 0;        /* 0 = todo fue bien */
}
```
Línea a línea:
- `#include <stdio.h>` → el preprocesador pega la cabecera de **entrada/salida estándar** (para usar `printf`).
- `int main(void)` → la **función principal**; todo programa C empieza aquí. Devuelve un `int` al sistema.
- `printf("...\n")` → imprime texto; `\n` es salto de línea.
- `return 0;` → termina; `0` significa "sin errores".

## Cómo está organizado este curso
- `modelo/` → la **teoría** (estos `.md`) y las **soluciones**: lo que usas para enseñar.
- `practica/<modulo>/` → por cada ejercicio, dos `.c`: **`ejNN_modelo.c`** (resuelto) y **`ejNN_practica.c`** (esqueleto con `// TODO` para el alumno).
- Cada `.c` lleva una **cabecera** con módulo, número, enunciado, dificultad y cómo compilar.

## Conexiones
- [[Curso_C/00_README]] — índice del curso
- [[MOC_Linux]] — la terminal y `gcc` viven aquí
- [[Curso_C/modelo/01-variables]] — primer módulo
