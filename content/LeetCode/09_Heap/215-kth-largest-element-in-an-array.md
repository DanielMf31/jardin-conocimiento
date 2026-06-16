---
title: "LeetCode 215 — Kth Largest Element in an Array"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/heap, patron/quickselect]
type: nota
status: en-progreso
source: claude-code
aliases: [Kth Largest Array, LC 215, findKthLargest]
problem_id: 215
difficulty: medium
patron: heap
neetcode_order: 4
---

# LeetCode 215 — Kth Largest Element in an Array

> 🎯 **Cuarto problema del patrón Heap**. Encontrar **solo el k-ésimo** (no top-K). Tres opciones: sort O(n log n), heap O(n log k), quickselect O(n) promedio.

## Enunciado

Devuelve el **k-ésimo elemento más grande** del array.

> ⚠️ "K-ésimo más grande" 1-indexed: en `[3,2,1,5,6,4]`, k=2 → `5` (5 es el 2º más grande).

---

## Solución 1 — Sort

```python
class Solution:
    def findKthLargest(self, nums, k):
        nums.sort()
        return nums[-k]
```

**O(n log n)**. Funciona, no óptima.

---

## Solución 2 — Min-heap de tamaño k (la canónica práctica)

```python
import heapq
class Solution:
    def findKthLargest(self, nums, k):
        heap = []
        for num in nums:
            heapq.heappush(heap, num)
            if len(heap) > k:
                heapq.heappop(heap)
        return heap[0]                          # el menor del top-k = k-ésimo más grande
```

**O(n log k)**. La que se espera en entrevista típica.

---

## Solución 3 — Quickselect (la óptima O(n) promedio)

Variante de quicksort: en cada paso particiona alrededor de un pivot, **descarta la mitad** que no contiene el k-ésimo.

```python
import random
class Solution:
    def findKthLargest(self, nums, k):
        # Buscar el (n-k)-ésimo más PEQUEÑO
        target = len(nums) - k

        def quickselect(left, right):
            pivot = nums[random.randint(left, right)]
            # Partition (Hoare's): mover < pivot a izq, > a der
            l, r = left, right
            while l <= r:
                while nums[l] < pivot: l += 1
                while nums[r] > pivot: r -= 1
                if l <= r:
                    nums[l], nums[r] = nums[r], nums[l]
                    l += 1; r -= 1
            if target <= r:
                return quickselect(left, r)
            elif target >= l:
                return quickselect(l, right)
            else:
                return nums[target]

        return quickselect(0, len(nums) - 1)
```

**O(n)** promedio. **O(n²)** peor caso (mitigado con pivot aleatorio).

---

## Conexiones

- [[347-top-k-frequent-elements]] — top-K (no k-ésimo).
- Próximo: [[621-task-scheduler]].

## Estado

- [ ] Leído
- [ ] Implementadas las 3 soluciones
- [ ] Resuelto en LeetCode
