---
title: "LeetCode 778 — Swim in Rising Water"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/advanced-graphs, patron/dijkstra-variant]
type: nota
status: en-progreso
source: claude-code
aliases: [Swim in Rising Water, LC 778, swimInWater]
problem_id: 778
difficulty: hard
patron: advanced-graphs
neetcode_order: 5
---

# LeetCode 778 — Swim in Rising Water

> **Quinto problema de Advanced Graphs — Hard**. **Dijkstra modificado**: en lugar de minimizar suma de distancias, minimizar el **máximo** de elevaciones en el camino.

## Enunciado

Grid `n×n` con elevaciones. Empezando en `(0,0)`, ir a `(n-1, n-1)`. Solo puedes mover a una celda adyacente. El "tiempo" en que puedes pasar por una celda es su elevación. Devuelve el tiempo mínimo de llegada.

---

## Solución — Dijkstra con max acumulado

```python
import heapq

class Solution:
    def swimInWater(self, grid):
        n = len(grid)
        heap = [(grid[0][0], 0, 0)]              # (max_elevación_camino, r, c)
        visited = set()
        while heap:
            t, r, c = heapq.heappop(heap)
            if (r, c) == (n-1, n-1):
                return t
            if (r, c) in visited: continue
            visited.add((r, c))
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in visited:
                    heapq.heappush(heap, (max(t, grid[nr][nc]), nr, nc))
        return -1
```

**Análisis:** O(N² log N).

### "Min-max path" — variante de Dijkstra

En Dijkstra clásico minimizas suma. Aquí minimizas el **máximo** de las elevaciones a lo largo del camino. Cambia el operador de relajación de `+` a `max`.

---

## Conexiones

- [[743-network-delay-time]] — Dijkstra clásico.
- Próximo: [[269-alien-dictionary]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
