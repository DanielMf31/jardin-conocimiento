---
title: "00 — Python vs C: el puente"
date: 2026-06-16
tags: [programacion/python, curso, programacion/fundamentos]
type: nota
status: en-progreso
source: claude-code
aliases: [Python vs C, Introducción a Python, Puente C Python]
---

# 00 — Python vs C: el puente

## Idea central
Ya sabes programar (lo aprendiste en C). Python es **los mismos conceptos con mucha menos ceremonia**: no declaras tipos, no compilas, no pones `;` ni `{}` — la **indentación** marca los bloques. Aprenderlo es sobre todo **traducir** lo que ya sabes.

## Qué aprendes
| Concepto | Para qué sirve |
|---|---|
| Interpretado vs compilado | Por qué Python se ejecuta directo (sin `gcc`) |
| Tipado dinámico | Por qué no declaras `int`/`float` |
| Indentación como bloque | Lo que en C eran `{ }` |
| REPL y `python3 archivo.py` | Las dos formas de ejecutar |

## C ↔ Python (mismo programa, lado a lado)
**Hola Mundo + una variable + condicional + bucle + función:**

| En C | En Python |
|---|---|
| `#include <stdio.h>` | *(nada)* |
| `int main(void) {` | *(el código va directo)* |
| `int x = 5;` | `x = 5` |
| `printf("%d\n", x);` | `print(x)` |
| `if (x > 3) { ... }` | `if x > 3:` *(indentado)* |
| `for (int i=0;i<5;i++)` | `for i in range(5):` |
| `int suma(int a,int b){return a+b;}` | `def suma(a, b): return a + b` |
| `return 0; }` | *(nada)* |
| compilar: `gcc x.c -o x && ./x` | ejecutar: `python3 x.py` |

## Diferencias clave (al venir de C)
- **No declaras tipos**: `x = 5` (Python deduce que es `int`). Una variable puede cambiar de tipo.
- **Indentación obligatoria**: los bloques se marcan con **sangría** (4 espacios), no con `{ }`. Si la sangría está mal, el programa falla.
- **Sin `;`** al final de línea (cada línea es una sentencia).
- **`input()` siempre devuelve texto (`str`)**: si quieres un número, conviértelo con `int(input())`.
- **No hay punteros ni gestión de memoria**: Python lo maneja por ti (te quitas `*`, `&`, `malloc`).
- **Estructuras potentes de serie**: listas dinámicas, **diccionarios** y **sets** (lo que en C te costaba) vienen incluidos — y son la base de NeetCode.

## Cómo ejecutar
```bash
python3 archivo.py      # ejecutar un script
python3                 # REPL interactivo (probar líneas sueltas)
```
No necesitas instalar nada (Python 3 viene en Ubuntu). Para proyectos, un entorno aislado:
```bash
python3 -m venv .venv && source .venv/bin/activate
```

## Por qué este orden (C → Python → NeetCode)
- **C** te dio lo **explícito** (tipos, memoria, cómo funciona la máquina).
- **Python** te da la **productividad**: los mismos conceptos, rápido y cómodo.
- Con listas/dicts/sets dominados → **NeetCode** (algoritmos) es el siguiente paso natural.

## Cómo está organizado este curso
Igual que el de C: `modelo/` (teoría + soluciones) y `practica/<modulo>/` con, por ejercicio, `ejNN_modelo.py` (resuelto) y `ejNN_practica.py` (esqueleto con `# TODO`). Cada `.py` lleva cabecera y se ejecuta con `python3`.

## Conexiones
- [[Curso_Python/00_README]] — índice del curso
- [[MOC_NeetCode_150]] — a donde lleva esto
- [[Curso_Python/modelo/01-variables]] — primer módulo
