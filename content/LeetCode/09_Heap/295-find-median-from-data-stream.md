---
title: "LeetCode 295 — Find Median from Data Stream"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/heap, patron/two-heaps]
type: nota
status: en-progreso
source: claude-code
aliases: [Find Median Stream, LC 295, MedianFinder]
problem_id: 295
difficulty: hard
patron: heap
neetcode_order: 7
---

# LeetCode 295 — Find Median from Data Stream

> 🎯 **Séptimo y último problema del patrón Heap — el Hard del patrón**. Es **el problema más bonito de heaps**: dos heaps (un max-heap para mitad inferior + un min-heap para mitad superior) mantienen la mediana en O(1) y la inserción en O(log n).

## Enunciado

Diseña una estructura para un stream de números que mantiene la **mediana** en O(1):
- `addNum(num)` — añade número al stream.
- `findMedian()` — devuelve la mediana actual.

> 💡 Si total impar: la mediana es el del medio. Si par: promedio de los dos del medio.

---

## Solución — Two heaps (la canónica)

**Idea**: dividir el stream en dos mitades:
- **`low` (max-heap)**: la mitad **inferior**. El máximo está arriba (= mayor de la mitad baja).
- **`high` (min-heap)**: la mitad **superior**. El mínimo está arriba (= menor de la mitad alta).

**Invariantes**:
1. Todo de `low` ≤ todo de `high`.
2. `len(low) == len(high)` o `len(low) == len(high) + 1`.

Mediana:
- Si tamaños iguales → promedio de los topes.
- Si `low` tiene 1 más → top de `low`.

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.low = []                            # max-heap (negado)
        self.high = []                           # min-heap

    def addNum(self, num):
        # 1. Push al low (max-heap)
        heapq.heappush(self.low, -num)
        # 2. Mover el top de low al high (mantener orden entre mitades)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        # 3. Rebalancear si high se hizo más grande
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def findMedian(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2
```

**Análisis:**
- **addNum: O(log n)**.
- **findMedian: O(1)**.
- **Espacio: O(n)**.

### Por qué los 3 pasos en `addNum`

1. **Push a low siempre**: garantiza que el nuevo num pase por max-heap → si pertenece a la mitad superior, será expulsado en el paso 2.
2. **Mover top de low a high**: garantiza la invariante "todo de low ≤ todo de high".
3. **Rebalancear**: tras el paso 2, high pudo crecer 1 más. Si supera el balance permitido, devolver uno a low.

Con esos 3 pasos siempre tienes la estructura correcta.

---

## Cierre del patrón Heap 🎉

| # | Problema | Idea distintiva |
|---|---|---|
| 1 | [[703-kth-largest-element-in-a-stream]] | Min-heap de tamaño k en streaming |
| 2 | [[1046-last-stone-weight]] | Max-heap simulando con negación |
| 3 | [[973-k-closest-points-to-origin]] | Max-heap de tamaño k para top-K cercanos |
| 4 | [[215-kth-largest-element-in-an-array]] | 3 soluciones: sort, heap, quickselect |
| 5 | [[621-task-scheduler]] | Heap + queue de cooldown |
| 6 | [[355-design-twitter]] | Diseño con dict + heap |
| 7 | **Este** | Two-heaps para mediana en streaming |

**Próximo patrón**: Backtracking (9 problemas).

---

## Conexiones

- [[347-top-k-frequent-elements]] — primer encuentro con heap.
- Próximo: Backtracking comienza con [[78-subsets]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón Heap cerrado** ✅
