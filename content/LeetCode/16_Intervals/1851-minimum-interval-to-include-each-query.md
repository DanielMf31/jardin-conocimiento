---
title: "LeetCode 1851 — Minimum Interval to Include Each Query"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/intervals, patron/heap, patron/offline-queries]
type: nota
status: en-progreso
source: claude-code
aliases: [Minimum Interval Query, LC 1851, minInterval]
problem_id: 1851
difficulty: hard
patron: intervals
neetcode_order: 6
---

# LeetCode 1851 — Minimum Interval to Include Each Query

> 🎯 **Sexto y último problema de Intervals — Hard**. **Offline processing**: ordenar queries, procesarlos junto con intervalos en orden de start.

## Enunciado

Para cada query `q`, encuentra el intervalo más pequeño que contiene `q`. Si ninguno, `-1`.

---

## Solución — Sort queries + min-heap

```python
import heapq

class Solution:
    def minInterval(self, intervals, queries):
        intervals.sort()
        sorted_q = sorted(enumerate(queries), key=lambda x: x[1])
        result = [-1] * len(queries)
        heap = []                                # (size, end)
        i = 0
        for q_idx, q in sorted_q:
            while i < len(intervals) and intervals[i][0] <= q:
                l, r = intervals[i]
                heapq.heappush(heap, (r - l + 1, r))
                i += 1
            while heap and heap[0][1] < q:
                heapq.heappop(heap)              # expirar intervalos cerrados
            if heap:
                result[q_idx] = heap[0][0]
        return result
```

**Análisis:** O((n + q) log (n + q)).

---

## Cierre Intervals 🎉

| # | Problema | Idea distintiva |
|---|---|---|
| 1 | [[57-insert-interval]] | 3 fases |
| 2 | [[56-merge-intervals]] | Sort + scan |
| 3 | [[435-non-overlapping-intervals]] | Greedy sort por end |
| 4 | [[252-meeting-rooms]] | Sort + check vecinos |
| 5 | [[253-meeting-rooms-ii]] | Min-heap o two arrays |
| 6 | **Este** | Offline queries + heap |

---

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón Intervals cerrado** ✅
