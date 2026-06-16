---
title: "LeetCode 743 — Network Delay Time"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/advanced-graphs, patron/dijkstra]
type: nota
status: en-progreso
source: claude-code
aliases: [Network Delay Time, LC 743, networkDelayTime, Dijkstra]
problem_id: 743
difficulty: medium
patron: advanced-graphs
neetcode_order: 2
---

# LeetCode 743 — Network Delay Time

> 🎯 **Segundo problema de Advanced Graphs**. **Dijkstra** clásico — shortest path desde un nodo a todos los demás en un grafo dirigido con pesos no negativos.

## Enunciado

Dado un grafo dirigido con pesos (tiempos), un nodo de inicio `k` y `n` nodos, devuelve el **tiempo mínimo** para que la señal llegue a todos los nodos. Si imposible, `-1`.

---

## Solución — Dijkstra con heap

```python
import heapq
from collections import defaultdict

class Solution:
    def networkDelayTime(self, times, n, k):
        graph = defaultdict(list)
        for u, v, w in times:
            graph[u].append((v, w))

        dist = {}                                # node -> shortest dist
        heap = [(0, k)]                          # (dist, node)
        while heap:
            d, node = heapq.heappop(heap)
            if node in dist: continue
            dist[node] = d
            for nb, w in graph[node]:
                if nb not in dist:
                    heapq.heappush(heap, (d + w, nb))

        return max(dist.values()) if len(dist) == n else -1
```

**Análisis:** O((V + E) log V).

### Dijkstra en una frase

"Min-heap por distancia acumulada. Extrae el nodo más cercano no procesado, marca su distancia final, relaja vecinos."

---

## Conexiones

- [[1584-min-cost-to-connect-all-points]] — heap-based graph algo.
- Próximo: [[787-cheapest-flights-within-k-stops]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
