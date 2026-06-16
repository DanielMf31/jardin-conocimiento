---
title: Git por dentro — el modelo de objetos
date: 2026-06-13
tags: [programacion/git, programacion/herramientas, fundamentos]
type: nota
status: permanente
source: claude-code
aliases: [git por dentro, git internals, modelo de objetos git]
---

# Git por dentro — el modelo de objetos

## Idea central
Git es, por debajo, una **base de datos clave→valor direccionada por contenido**: la **clave es el hash (SHA-1) del contenido** y el valor es el contenido comprimido. Todo lo demás (ramas, commits, historia) se construye encima de eso.

> Git es **open source (GPLv2)**, escrito casi todo en **C**, creado por Linus Torvalds en 2005 (ver [[historia-de-linux]]) y mantenido por Junio Hamano. Código en `git.kernel.org` y espejo en `github.com/git/git`.

## El almacén de objetos
Metes contenido → te devuelve su hash. Le das el hash → te devuelve el contenido. Vive en `.git/objects/`.

Como **la clave ES el contenido hasheado**:
- Contenido idéntico → mismo hash → se guarda **una sola vez** (deduplicación).
- Cambia un byte → hash distinto → objeto nuevo.
- El hash **verifica integridad**: garantiza que nada se corrompió.

## Los 4 tipos de objeto
| Objeto | Qué es |
|---|---|
| **blob** | Contenido de un archivo (solo bytes, **sin nombre**) |
| **tree** | Un directorio: nombres → blobs (archivos) y otros trees (subcarpetas), con permisos |
| **commit** | Apunta a **un** tree raíz (foto del proyecto) + commit(s) padre + autor + mensaje |
| **tag** | Puntero con nombre a un objeto (normalmente un commit) + metadatos |

Un **commit** = "esta foto completa (este tree), después de este padre, hecha por X, con este mensaje".

## Snapshots, NO diffs
Git guarda **fotos completas** del árbol en cada commit, no los cambios. Los archivos que no cambiaron **reutilizan el mismo blob** (no se duplican). El `git diff` se **calcula al vuelo** comparando dos fotos. (A bajo nivel comprime con deltas en los *packfiles* para ahorrar disco, pero el modelo lógico son snapshots.)

## Ramas = punteros baratos
Una **rama** es un archivo de 41 bytes en `.git/refs/heads/` con **el hash de un commit**. Crear rama = escribir ese hash → instantáneo. **HEAD** es el puntero a "dónde estás ahora". La historia es un **grafo dirigido acíclico (DAG)** de commits → padres (un *merge* tiene 2 padres).

## Las tres zonas
```
Working directory  --git add-->  Index (staging)  --git commit-->  Repositorio (.git/objects)
(tus archivos)                   (.git/index)                       (historia inmutable)
```
- `git add`: hashea contenido → crea **blobs**, los registra en el index.
- `git commit`: construye **trees** desde el index, crea el **commit** (tree raíz + padre) y **mueve el puntero de la rama**.

## Verlo tú mismo (comandos *plumbing*)
```bash
git cat-file -t <hash>    # tipo (blob/tree/commit)
git cat-file -p <hash>    # contenido legible
git cat-file -p HEAD      # un commit por dentro: tree, parent, author
git ls-tree HEAD          # árbol del último commit (nombres → hashes)
echo "hola" | git hash-object --stdin   # qué hash tendría un contenido
```

## Distribuido
`git clone` se lleva **toda** la base de objetos y el historial completo — cada copia es un repo entero. Por eso no hay servidor central obligatorio (la idea de Linus para el kernel: miles de personas sin cuello de botella).

## Conexiones
- [[historia-de-linux]] — Linus creó Git en 2005
- [[MOC_Linux]] · [[MOC_Programacion]]
