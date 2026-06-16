---
title: "LeetCode 1584 — Min Cost to Connect All Points"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/advanced-graphs, patron/mst, patron/prim]
type: nota
status: en-progreso
source: claude-code
aliases: [Min Cost Connect Points, LC 1584, MST, Prim's algorithm]
problem_id: 1584
difficulty: medium
patron: advanced-graphs
neetcode_order: 1
---

# LeetCode 1584 — Min Cost to Connect All Points

> 🎯 **Primer problema de Advanced Graphs**. **Minimum Spanning Tree (MST)** clásico. Dos algoritmos: **Prim's** (greedy + heap) y **Kruskal's** (sort + Union-Find).

## Enunciado

Dados `n` puntos en plano 2D, conéctalos todos minimizando el coste total. Coste de conectar `(x1,y1)` y `(x2,y2)` = `|x1-x2| + |y1-y2|` (Manhattan).

---

## Solución — Prim's algorithm con heap

```python
import heapq

class Solution:
    def minCostConnectPoints(self, points):
        n = len(points)
        visited = set()
        heap = [(0, 0)]                          # (cost, point_idx) — empezar en 0
        total = 0

        while len(visited) < n:
            cost, i = heapq.heappop(heap)
            if i in visited: continue
            visited.add(i)
            total += cost
            x1, y1 = points[i]
            for j in range(n):
                if j not in visited:
                    x2, y2 = points[j]
                    d = abs(x1-x2) + abs(y1-y2)
                    heapq.heappush(heap, (d, j))
        return total
```

**Análisis:** O(N² log N).

### Prim's en una frase

"Empezando en un punto arbitrario, **siempre extiende el árbol con la arista más barata** que conecta un nodo dentro al exterior. Hasta cubrir todos."

---

## Conexiones

- [[684-redundant-connection]] — Union-Find para Kruskal.
- Próximo: [[743-network-delay-time]] — Dijkstra.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
