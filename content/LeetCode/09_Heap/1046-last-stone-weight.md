---
title: "LeetCode 1046 — Last Stone Weight"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/heap, patron/max-heap, patron/simulacion]
type: nota
status: en-progreso
source: claude-code
aliases: [Last Stone Weight, LC 1046, lastStoneWeight]
problem_id: 1046
difficulty: easy
patron: heap
neetcode_order: 2
---

# LeetCode 1046 — Last Stone Weight

> 🎯 **Segundo problema del patrón Heap**. Simulación con **max-heap**. Como Python solo tiene min-heap, el truco es **negar valores**.

## Enunciado

Tienes piedras con pesos. En cada paso:
1. Tomas las **dos más pesadas** `x ≤ y`.
2. Si `x == y`, ambas se destruyen.
3. Si `x < y`, la nueva piedra de peso `y - x` reemplaza a las dos.

Devuelve el peso de la última piedra (o 0 si no queda ninguna).

**Ejemplo:**
```
Input:  [2,7,4,1,8,1]
Output: 1
```

---

## Solución — Max-heap (negando valores)

```python
import heapq

class Solution:
    def lastStoneWeight(self, stones):
        heap = [-s for s in stones]
        heapq.heapify(heap)
        while len(heap) > 1:
            y = -heapq.heappop(heap)            # mayor (des-negar)
            x = -heapq.heappop(heap)            # segundo mayor
            if y > x:
                heapq.heappush(heap, -(y - x))
        return -heap[0] if heap else 0
```

**Análisis:**
- **Tiempo: O(n log n)** — n iteraciones, cada heap op O(log n).
- **Espacio: O(n)**.

### Truco max-heap

Python `heapq` solo es min-heap. Para max-heap: **negar al push, des-negar al pop**.

---

## Conexiones

- Próximo: [[973-k-closest-points-to-origin]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
