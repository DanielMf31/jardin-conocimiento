---
title: "LeetCode 130 — Surrounded Regions"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/grid-borde]
type: nota
status: en-progreso
source: claude-code
aliases: [Surrounded Regions, LC 130, solve, Regiones rodeadas]
problem_id: 130
difficulty: medium
patron: graphs
neetcode_order: 5
---

# LeetCode 130 — Surrounded Regions

> **Quinto problema del patrón Graphs**. Mismo truco de "DFS desde los bordes" que [[417-pacific-atlantic-water-flow]]. Aquí se aplica para identificar las `'O'` **NO rodeadas** y dejarlas en paz, capturando el resto.

## Enunciado

Dado un grid de `'X'` y `'O'`, **captura** todas las regiones rodeadas (cambiar `'O'` por `'X'`). Una región está rodeada si **todas** sus `'O'` están conectadas y **ninguna toca el borde**.

---

## Solución — DFS desde el borde marca "seguras", luego flip resto

**Pasos**:
1. DFS desde cada `'O'` del borde, marcar `'#'` (temporal).
2. Recorrer grid: las `'O'` restantes (no llegaron al borde) → capturar (cambiar a `'X'`).
3. Las `'#'` (eran seguras) → restaurar a `'O'`.

```python
class Solution:
    def solve(self, board):
        if not board: return
        rows, cols = len(board), len(board[0])

        def dfs(r, c):
            if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != 'O':
                return
            board[r][c] = '#'                    # marcador "seguro"
            dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1)

        # Paso 1: DFS desde bordes
        for r in range(rows):
            dfs(r, 0); dfs(r, cols-1)
        for c in range(cols):
            dfs(0, c); dfs(rows-1, c)

        # Paso 2 + 3: flip
        for r in range(rows):
            for c in range(cols):
                if board[r][c] == 'O':
                    board[r][c] = 'X'           # capturar
                elif board[r][c] == '#':
                    board[r][c] = 'O'           # restaurar
```

**Análisis:** O(M·N).

---

## Conexiones

- [[417-pacific-atlantic-water-flow]] — mismo patrón "borde".
- Próximo: [[994-rotting-oranges]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
