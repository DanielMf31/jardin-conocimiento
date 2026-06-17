---
title: "LeetCode 56 — Merge Intervals"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/intervals, patron/sort]
type: nota
status: en-progreso
source: claude-code
aliases: [Merge Intervals, LC 56, merge]
problem_id: 56
difficulty: medium
patron: intervals
neetcode_order: 2
---

# LeetCode 56 — Merge Intervals

> **Segundo problema de Intervals — el más fundamental**. **Sort + scan linear**. Patrón maestro de todo el bloque.

## Enunciado

Array de intervalos. Fusiona los solapados y devuelve la lista resultante.

---

## Solución — Sort + scan

```python
class Solution:
    def merge(self, intervals):
        intervals.sort(key=lambda x: x[0])
        result = [intervals[0]]
        for start, end in intervals[1:]:
            if start <= result[-1][1]:           # solapan
                result[-1][1] = max(result[-1][1], end)
            else:
                result.append([start, end])
        return result
```

**Análisis:** O(n log n).

---

## Conexiones

- Próximo: [[435-non-overlapping-intervals]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
