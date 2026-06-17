---
title: "LeetCode 332 — Reconstruct Itinerary"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/advanced-graphs, patron/eulerian-path]
type: nota
status: en-progreso
source: claude-code
aliases: [Reconstruct Itinerary, LC 332, findItinerary, Eulerian path]
problem_id: 332
difficulty: hard
patron: advanced-graphs
neetcode_order: 4
---

# LeetCode 332 — Reconstruct Itinerary

> **Cuarto problema de Advanced Graphs — Hard**. **Eulerian path** (camino que usa cada arista exactamente una vez). Algoritmo de Hierholzer con DFS post-order.

## Enunciado

Dada una lista de tickets (pares `[from, to]`), reconstruye el itinerario empezando en `JFK`, **usando cada ticket exactamente una vez**. Si hay múltiples válidos, devolver el lexicográficamente menor.

---

## Solución — Hierholzer's con heap (lexicográfico) y postorder

```python
import heapq
from collections import defaultdict

class Solution:
    def findItinerary(self, tickets):
        graph = defaultdict(list)
        for a, b in tickets:
            heapq.heappush(graph[a], b)          # heap → orden lexicográfico

        result = []
        def dfs(node):
            while graph[node]:
                next_node = heapq.heappop(graph[node])
                dfs(next_node)
            result.append(node)                  # postorder

        dfs("JFK")
        return result[::-1]                      # invertir
```

**Análisis:** O(E log E).

### Por qué postorder + reverse

Hierholzer: empieza desde el inicio, sigue aristas voraz hasta atascarse, en el callejón sin salida añade nodo al final, retrocede e intenta otras ramas. La lista resultante (postorder) **invertida** es el camino válido.

---

## Conexiones

- [[207-course-schedule]] — DFS sobre grafos dirigidos.
- Próximo: [[778-swim-in-rising-water]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
