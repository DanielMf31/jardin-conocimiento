---
title: "LeetCode 787 — Cheapest Flights Within K Stops"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/advanced-graphs, patron/bellman-ford]
type: nota
status: en-progreso
source: claude-code
aliases: [Cheapest Flights, LC 787, findCheapestPrice, Bellman-Ford]
problem_id: 787
difficulty: medium
patron: advanced-graphs
neetcode_order: 3
---

# LeetCode 787 — Cheapest Flights Within K Stops

> **Tercer problema de Advanced Graphs**. **Bellman-Ford modificado** para shortest path con **límite de aristas**. Dijkstra no funciona bien aquí porque el límite de stops puede llevar a soluciones subóptimas globales pero óptimas con K stops.

## Enunciado

Encuentra el **vuelo más barato** desde `src` a `dst` con como mucho `k` paradas (= `k+1` aristas).

---

## Solución — Bellman-Ford (k+1 iteraciones)

```python
class Solution:
    def findCheapestPrice(self, n, flights, src, dst, k):
        INF = float('inf')
        prices = [INF] * n
        prices[src] = 0

        for _ in range(k + 1):                   # k+1 aristas máximo
            tmp = prices.copy()                  # ⭐ usar snapshot, no in-place
            for u, v, w in flights:
                if prices[u] != INF and prices[u] + w < tmp[v]:
                    tmp[v] = prices[u] + w
            prices = tmp

        return prices[dst] if prices[dst] != INF else -1
```

**Análisis:** O(K · E).

### Por qué `tmp = prices.copy()` (snapshot)

Si actualizamos `prices` in-place dentro de la iteración, una arista podría usarse **dos veces** en la misma "vuelta", violando el límite de stops. Con snapshot (`tmp`), garantizamos que cada iteración usa solo aristas de la iteración anterior.

---

## Conexiones

- [[743-network-delay-time]] — Dijkstra (sin límite de stops).
- Próximo: [[332-reconstruct-itinerary]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
