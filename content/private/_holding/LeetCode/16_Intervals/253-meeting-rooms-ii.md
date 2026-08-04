---
title: "LeetCode 253 — Meeting Rooms II"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/intervals, patron/heap]
type: nota
status: en-progreso
source: claude-code
aliases: [Meeting Rooms II, LC 253, minMeetingRooms]
problem_id: 253
difficulty: medium
patron: intervals
neetcode_order: 5
---

# LeetCode 253 — Meeting Rooms II

> **Quinto problema de Intervals**. ¿Cuántas salas mínimas necesarias? **Min-heap por end times**.

## Enunciado

Intervalos. Devuelve **número mínimo de salas** para asistir a todas.

---

## Solución — Min-heap de ends

```python
import heapq

class Solution:
    def minMeetingRooms(self, intervals):
        intervals.sort(key=lambda x: x[0])
        heap = []                                # ends de salas activas
        for s, e in intervals:
            if heap and heap[0] <= s:
                heapq.heappop(heap)              # liberar sala
            heapq.heappush(heap, e)
        return len(heap)
```

**Análisis:** O(n log n).

### Lógica

Para cada meeting nueva, si la sala que termina antes ya está libre (`heap[0] <= s`), reutilízala. Si no, abre nueva. Tamaño final del heap = salas necesarias.

---

## Solución 2 — Two arrays (start/end)

```python
class Solution:
    def minMeetingRooms(self, intervals):
        starts = sorted(i[0] for i in intervals)
        ends = sorted(i[1] for i in intervals)
        rooms = end_idx = 0
        for s in starts:
            if s < ends[end_idx]:
                rooms += 1
            else:
                end_idx += 1
        return rooms
```

Igual O(n log n) sin heap.

---

## Conexiones

- Próximo: [[1851-minimum-interval-to-include-each-query]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
