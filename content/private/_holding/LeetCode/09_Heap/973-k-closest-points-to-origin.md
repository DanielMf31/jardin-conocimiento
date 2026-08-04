---
title: "LeetCode 973 — K Closest Points to Origin"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/heap, patron/top-k]
type: nota
status: en-progreso
source: claude-code
aliases: [K Closest Points, LC 973, kClosest]
problem_id: 973
difficulty: medium
patron: heap
neetcode_order: 3
---

# LeetCode 973 — K Closest Points to Origin

> **Tercer problema del patrón Heap**. **Top-K más cercanos**: usa **max-heap de tamaño k** (echar al peor candidato cuando se llena).

## Enunciado

Dado un array de puntos `[x, y]` y un entero `k`, devuelve los **k puntos más cercanos al origen** (distancia euclidiana).

---

## Solución — Max-heap de tamaño k (negando distancias)

```python
import heapq

class Solution:
    def kClosest(self, points, k):
        heap = []
        for x, y in points:
            d = -(x*x + y*y)                    # negado: max-heap
            if len(heap) < k:
                heapq.heappush(heap, (d, x, y))
            else:
                heapq.heappushpop(heap, (d, x, y))
        return [[x, y] for _, x, y in heap]
```

**Análisis:**
- **Tiempo: O(n log k)**.
- **Espacio: O(k)**.

### `heappushpop` — atómico y más rápido

`heappushpop(h, x)` hace push+pop en una operación, más rápido que llamarlas por separado.

### Sobre `x*x + y*y` (no `sqrt`)

No necesitamos la distancia real, solo comparar. Saltar la `sqrt` ahorra tiempo y evita errores de precisión.

---

## Variante — Quickselect O(n) promedio

`quickselect` (variante de quicksort) encuentra el k-ésimo en O(n) promedio. Más complicado pero óptimo.

---

## Conexiones

- [[347-top-k-frequent-elements]] — patrón top-K.
- [[703-kth-largest-element-in-a-stream]] — top-K en streaming.
- Próximo: [[215-kth-largest-element-in-an-array]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
