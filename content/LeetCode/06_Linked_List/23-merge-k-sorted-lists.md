---
title: "LeetCode 23 — Merge K Sorted Lists"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/linked-list, patron/heap, patron/divide-conquer]
type: nota
status: en-progreso
source: claude-code
aliases: [Merge K Sorted Lists, LC 23, mergeKLists, Fusionar K listas]
problem_id: 23
difficulty: hard
patron: linked-list
neetcode_order: 10
---

# LeetCode 23 — Merge K Sorted Lists

> 🎯 **Décimo problema del patrón Linked List — primer Hard del patrón**. Generalización de [[21-merge-two-sorted-lists]] a **K listas**. Dos soluciones óptimas: heap (priority queue) y divide-and-conquer. Ambas O(n log k) — útiles saberlas las dos.

## Enunciado

Te dan un array de `k` linked lists, cada una ordenada de forma creciente.

Fusiónalas en una sola linked list ordenada y devuelve la cabeza.

**Ejemplo:**
```
Input:  [[1,4,5], [1,3,4], [2,6]]
Output: [1,1,2,3,4,4,5,6]
```

**Restricciones:**
- `k == lists.length`, `0 <= k <= 10^4`.
- `0 <= lists[i].length <= 500`.
- Total de nodos hasta `10^4`.

---

## Solución 1 — Heap de cabezas (la canónica)

**La idea**: min-heap con las cabezas actuales de cada lista. Pop la menor, añadirla a la salida, push su `next` (si existe).

```python
import heapq

class Solution:
    def mergeKLists(self, lists):
        # Min-heap con (val, índice, nodo) — el índice rompe empates por val
        heap = []
        for i, head in enumerate(lists):
            if head:
                heapq.heappush(heap, (head.val, i, head))

        dummy = ListNode()
        tail = dummy
        while heap:
            val, i, node = heapq.heappop(heap)
            tail.next = node
            tail = tail.next
            if node.next:
                heapq.heappush(heap, (node.next.val, i, node.next))

        return dummy.next
```

**Análisis:**
- **Tiempo: O(n log k)** — n nodos totales, cada heappush/pop es O(log k).
- **Espacio: O(k)** — heap.
- **Veredicto:** ✅ **la canónica**.

### Por qué `(val, i, node)` y no solo `(val, node)`

Si dos nodos tienen el mismo `val`, Python intentaría **comparar nodos** para desempatar — pero los `ListNode` no implementan `<`. El índice `i` rompe el empate antes de que llegue al nodo.

---

## Solución 2 — Divide and conquer (mergear de a pares)

**La idea**: aplicar [[21-merge-two-sorted-lists]] de a pares, reduciendo k listas a 1 en log(k) iteraciones.

```python
class Solution:
    def mergeKLists(self, lists):
        if not lists: return None

        while len(lists) > 1:
            merged = []
            for i in range(0, len(lists), 2):
                a = lists[i]
                b = lists[i + 1] if i + 1 < len(lists) else None
                merged.append(self.mergeTwo(a, b))
            lists = merged
        return lists[0]

    def mergeTwo(self, a, b):
        dummy = ListNode()
        tail = dummy
        while a and b:
            if a.val <= b.val:
                tail.next = a; a = a.next
            else:
                tail.next = b; b = b.next
            tail = tail.next
        tail.next = a or b
        return dummy.next
```

**Análisis:**
- **Tiempo: O(n log k)** — log(k) "rondas", cada una procesa todos los n nodos.
- **Espacio: O(1)** extra (excluyendo recursión si la usaras; iterativo es O(1)).
- **Veredicto:** ✅ alternativa elegante. **Útil saber ambas** porque en algunos contextos divide-and-conquer es preferible (paralelizable, sin necesidad de heap).

---

## El patrón general — "K-way merge"

**Cuándo aplicar**:

> Cuando necesitas fusionar K colecciones ordenadas, donde el problema bipartito (k=2) es trivial pero generalizar requiere estructura.

**Dos approaches**: heap (O(n log k) tiempo, O(k) espacio) o divide-and-conquer (O(n log k) tiempo, O(1) espacio extra). Usa heap si es streaming; usa D&C si es batch y tienes memoria limitada.

---

## Auto-test

1. Escribe la Solución 1 (heap) desde cero.
2. Justifica el `(val, i, node)` para resolver empates.
3. Implementa la Solución 2 (D&C) desde cero.
4. Compara complejidades.

---

## Conexiones

- [[21-merge-two-sorted-lists]] — caso base k=2.
- [[347-top-k-frequent-elements]] — heap pattern.
- Próximo: [[25-reverse-nodes-in-k-group]].

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 1 (heap) desde cero
- [ ] Implementada Solución 2 (D&C)
- [ ] Resuelto en LeetCode con éxito
