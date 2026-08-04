---
title: "LeetCode 269 — Alien Dictionary"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/advanced-graphs, patron/topological-sort]
type: nota
status: en-progreso
source: claude-code
aliases: [Alien Dictionary, LC 269, alienOrder]
problem_id: 269
difficulty: hard
patron: advanced-graphs
neetcode_order: 6
---

# LeetCode 269 — Alien Dictionary

> **Sexto y último problema de Advanced Graphs — Hard**. Combina **construcción de grafo a partir de string comparison** + **topological sort**.

## Enunciado

Dada una lista de palabras de un alfabeto desconocido en orden lexicográfico, devuelve el orden de los caracteres en ese alfabeto. Si imposible, `""`.

---

## Solución — Construir grafo + Kahn's

```python
from collections import defaultdict, deque

class Solution:
    def alienOrder(self, words):
        graph = defaultdict(set)
        in_degree = {c: 0 for word in words for c in word}

        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i+1]
            min_len = min(len(w1), len(w2))
            if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
                return ""                        # caso inválido: prefijo más largo antes
            for j in range(min_len):
                if w1[j] != w2[j]:
                    if w2[j] not in graph[w1[j]]:
                        graph[w1[j]].add(w2[j])
                        in_degree[w2[j]] += 1
                    break

        # Kahn's
        q = deque(c for c in in_degree if in_degree[c] == 0)
        result = []
        while q:
            c = q.popleft()
            result.append(c)
            for nb in graph[c]:
                in_degree[nb] -= 1
                if in_degree[nb] == 0:
                    q.append(nb)

        return ''.join(result) if len(result) == len(in_degree) else ""
```

**Análisis:** O(C) donde C = total de chars.

---

## Cierre Advanced Graphs

| # | Problema | Algoritmo |
|---|---|---|
| 1 | [[1584-min-cost-to-connect-all-points]] | Prim's MST |
| 2 | [[743-network-delay-time]] | Dijkstra |
| 3 | [[787-cheapest-flights-within-k-stops]] | Bellman-Ford con K iteraciones |
| 4 | [[332-reconstruct-itinerary]] | Hierholzer (Eulerian path) |
| 5 | [[778-swim-in-rising-water]] | Dijkstra min-max |
| 6 | **Este** | Topological sort sobre grafo construido |

---

## Conexiones

- [[207-course-schedule]] — topological sort base.
- [[210-course-schedule-ii]] — Kahn's.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón Advanced Graphs cerrado** [OK]
