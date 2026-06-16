---
title: "LeetCode 417 — Pacific Atlantic Water Flow"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/multi-source-bfs]
type: nota
status: en-progreso
source: claude-code
aliases: [Pacific Atlantic, LC 417, pacificAtlantic]
problem_id: 417
difficulty: medium
patron: graphs
neetcode_order: 4
---

# LeetCode 417 — Pacific Atlantic Water Flow

> 🎯 **Cuarto problema del patrón Graphs**. Truco brillante: **DFS DESDE los océanos hacia adentro**, no al revés. Reduce el problema a "qué celdas alcanzan ambos océanos".

## Enunciado

Grid de elevaciones. El borde superior e izquierdo limitan con el **Pacífico**, el borde inferior y derecho con el **Atlántico**. El agua fluye de mayor a igual elevación hacia las 4 direcciones.

Devuelve las celdas desde las que el agua puede llegar a **ambos océanos**.

---

## Solución — DFS inverso desde los bordes

**Idea**: en lugar de "puede esta celda llegar a un océano", invertir: "qué celdas pueden ser **alcanzadas** desde un océano (subiendo elevación o igualándola)".

```python
class Solution:
    def pacificAtlantic(self, heights):
        rows, cols = len(heights), len(heights[0])
        pacific = set()
        atlantic = set()

        def dfs(r, c, visited, prev_height):
            if ((r, c) in visited or r < 0 or r >= rows or c < 0 or c >= cols
                    or heights[r][c] < prev_height):
                return
            visited.add((r, c))
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                dfs(r+dr, c+dc, visited, heights[r][c])

        # DFS desde bordes Pacific (top + left)
        for c in range(cols):
            dfs(0, c, pacific, heights[0][c])
            dfs(rows-1, c, atlantic, heights[rows-1][c])
        for r in range(rows):
            dfs(r, 0, pacific, heights[r][0])
            dfs(r, cols-1, atlantic, heights[r][cols-1])

        return [[r, c] for (r, c) in pacific & atlantic]
```

**Análisis:** O(M·N).

### Por qué DFS inverso

Hacer DFS desde cada celda hacia los océanos sería O((M·N)²). Empezar desde los bordes y subir convierte el problema en dos DFS de O(M·N), uno por océano. La intersección da el resultado.

---

## Conexiones

- [[200-number-of-islands]] — DFS en grid.
- Próximo: [[130-surrounded-regions]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
