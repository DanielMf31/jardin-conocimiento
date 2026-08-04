---
title: "LeetCode 994 — Rotting Oranges"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/multi-source-bfs]
type: nota
status: en-progreso
source: claude-code
aliases: [Rotting Oranges, LC 994, orangesRotting]
problem_id: 994
difficulty: medium
patron: graphs
neetcode_order: 6
---

# LeetCode 994 — Rotting Oranges

> **Sexto problema del patrón Graphs**. **BFS multi-source**: empezar la BFS desde **todas las fuentes a la vez** (todas las naranjas podridas iniciales). Patrón crucial para "tiempo mínimo para alcanzar todo".

## Enunciado

Grid de:
- `0` = celda vacía.
- `1` = naranja fresca.
- `2` = naranja podrida.

Cada minuto, las naranjas podridas pudren las naranjas frescas adyacentes (4-direccionalmente).

Devuelve el **número de minutos** hasta que TODAS las naranjas estén podridas. Si imposible, `-1`.

---

## Solución — BFS multi-source

```python
from collections import deque

class Solution:
    def orangesRotting(self, grid):
        rows, cols = len(grid), len(grid[0])
        q = deque()
        fresh = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 2:
                    q.append((r, c, 0))         # (r, c, time)
                elif grid[r][c] == 1:
                    fresh += 1

        time = 0
        while q:
            r, c, t = q.popleft()
            time = t
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    q.append((nr, nc, t + 1))

        return time if fresh == 0 else -1
```

**Análisis:** O(M·N) tiempo y espacio.

### Multi-source BFS

A diferencia de single-source BFS (un solo punto de partida), aquí **inicializamos la queue con TODAS las celdas iniciales** (todas las naranjas podridas). El BFS las expande **simultáneamente**, dando el tiempo mínimo correcto.

---

## Conexiones

- [[286-walls-and-gates]] — multi-source BFS también.
- [[102-binary-tree-level-order-traversal]] — BFS con tiempo/niveles.
- Próximo: [[286-walls-and-gates]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
