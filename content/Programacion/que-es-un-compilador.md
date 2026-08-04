---
title: Qué es un compilador
date: 2026-08-04
tags: [programacion, programacion/fundamentos]
type: nota
status: permanente
source: manual
aliases: [compilador]
---

# Qué es un compilador

## Idea central
Un compilador es un programa que traduce el código fuente que escribe una persona (en un lenguaje de
alto nivel como C) al código máquina que la CPU sabe ejecutar, comprobando de paso que el programa
está bien formado.

## Desarrollo
El proceso ocurre en fases: análisis léxico (trocear el texto en tokens), análisis sintáctico
(construir el árbol según la gramática del lenguaje), análisis semántico (comprobar tipos y reglas),
generación de código intermedio, optimización y emisión del código máquina final.

A diferencia de un intérprete, que ejecuta el código sobre la marcha, el compilador produce un
ejecutable independiente: se traduce una vez y se ejecuta muchas, lo que suele dar programas más
rápidos a cambio de un paso previo de compilación. En C, ese compilador es típicamente `gcc` o
`clang`.

## Conexiones
- [[indice-programacion|Índice de Programación]]
