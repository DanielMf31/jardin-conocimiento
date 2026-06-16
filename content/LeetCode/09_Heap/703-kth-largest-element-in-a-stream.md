---
title: "LeetCode 703 — Kth Largest Element in a Stream"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/heap, patron/min-heap, patron/streaming]
type: nota
status: en-progreso
source: claude-code
aliases: [Kth Largest Stream, LC 703, KthLargest]
problem_id: 703
difficulty: easy
patron: heap
neetcode_order: 1
---

# LeetCode 703 — Kth Largest Element in a Stream

> 🎯 **Primer problema del patrón Heap**. Refuerza el patrón "min-heap de tamaño k para top-K" que ya viste en [[347-top-k-frequent-elements]]. Aquí en versión streaming.

## Enunciado

Diseña una clase `KthLargest` que mantiene el **k-ésimo elemento más grande** en un stream:
- `__init__(k, nums)` — inicializa con array `nums`.
- `add(val)` — añade `val` al stream y devuelve el k-ésimo más grande actual.

---

## Solución — Min-heap de tamaño k

```python
import heapq

class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = nums
        heapq.heapify(self.heap)
        while len(self.heap) > k:
            heapq.heappop(self.heap)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]
```

**Análisis:**
- **add: O(log k)**.
- **Espacio: O(k)**.
- **Veredicto:** ✅ canónica.

### Por qué min-heap (de nuevo)

Para top-K más grandes, el **menor de los K candidatos** es el "k-ésimo más grande". Acceder al menor en O(1) → min-heap. Patrón maestro de [[347-top-k-frequent-elements]].

---

## Conexiones

- [[347-top-k-frequent-elements]] — primer encuentro con min-heap top-K.
- Próximo: [[1046-last-stone-weight]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
