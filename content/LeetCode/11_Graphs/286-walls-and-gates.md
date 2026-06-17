---
title: "LeetCode 286 — Walls and Gates"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/multi-source-bfs]
type: nota
status: en-progreso
source: claude-code
aliases: [Walls and Gates, LC 286, wallsAndGates]
problem_id: 286
difficulty: medium
patron: graphs
neetcode_order: 7
---

# LeetCode 286 — Walls and Gates

> **Séptimo problema del patrón Graphs**. **Multi-source BFS** otra vez. Esta vez, computar la **distancia al gate más cercano** para cada celda vacía.

## Enunciado

Grid donde:
- `-1` = pared.
- `0` = puerta (gate).
- `INF` (= 2147483647) = celda vacía.

Para cada celda vacía, computa la distancia al **gate más cercano**. Modificar in-place.

---

## Solución — Multi-source BFS desde todos los gates a la vez

```python
from collections import deque
INF = 2147483647

class Solution:
    def wallsAndGates(self, rooms):
        rows, cols = len(rooms), len(rooms[0])
        q = deque()
        for r in range(rows):
            for c in range(cols):
                if rooms[r][c] == 0:
                    q.append((r, c))            # todas las puertas a la vez

        while q:
            r, c = q.popleft()
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r+dr, c+dc
                if (0 <= nr < rows and 0 <= nc < cols
                        and rooms[nr][nc] == INF):
                    rooms[nr][nc] = rooms[r][c] + 1
                    q.append((nr, nc))
```

**Análisis:** O(M·N).

### Por qué multi-source funciona

Si haces BFS desde **todos** los gates a la vez, cada celda se "alcanza" en orden de distancia. La primera vez que alcanzas una celda con BFS, es por la distancia mínima — desde **algún** gate, que es necesariamente el más cercano por la naturaleza de BFS.

---

## Conexiones

- [[994-rotting-oranges]] — mismo patrón multi-source.
- Próximo: [[207-course-schedule]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
