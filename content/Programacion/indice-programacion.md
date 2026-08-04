---
title: Programación — notas publicadas
date: 2026-08-04
tags: [programacion, meta]
type: moc
status: permanente
source: manual
aliases: [indice programacion, programacion publicada]
---

# Programación

Punto de entrada a las notas de programación que publico en el jardín. Esta carpeta de la bóveda
(`50_Areas/Programacion/Publicable/`) se sincroniza al jardín; lo que no cuelgue de aquí no se publica.

## Notas
- [[que-es-un-compilador|Qué es un compilador]]

## Cómo funciona la publicación
Escribo aquí, en la bóveda, con wikilinks normales. Un `make sync` copia esta carpeta a
`content/Programacion/` del jardín y Quartz la publica. Para despublicar una nota, se mueve a una
subcarpeta que empiece por `_` (p. ej. `_archivados/`).
