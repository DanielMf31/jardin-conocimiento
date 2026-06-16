---
title: "LeetCode 695 — Max Area of Island"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/grid-dfs]
type: nota
status: en-progreso
source: claude-code
aliases: [Max Area of Island, LC 695, maxAreaOfIsland]
problem_id: 695
difficulty: medium
patron: graphs
neetcode_order: 3
---

# LeetCode 695 — Max Area of Island

> 🎯 **Tercer problema del patrón Graphs**. Variante directa de [[200-number-of-islands]] — en lugar de **contar** islas, devuelve el **tamaño** de la isla más grande.

## Enunciado

Dado un grid 2D de 0/1, devuelve el **área** (número de celdas) de la isla más grande.

---

## Solución — DFS devolviendo área

```python
class Solution:
    def maxAreaOfIsland(self, grid):
        rows, cols = len(grid), len(grid[0])
        best = 0

        def dfs(r, c):
            if (r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != 1):
                return 0
            grid[r][c] = 0
            return 1 + dfs(r+1,c) + dfs(r-1,c) + dfs(r,c+1) + dfs(r,c-1)

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 1:
                    best = max(best, dfs(r, c))
        return best
```

**Veredicto:** ✅ canónica. La diferencia con LC 200: el DFS **devuelve el área** (no es void).

---

## Conexiones

- [[200-number-of-islands]] — base.
- Próximo: [[417-pacific-atlantic-water-flow]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
