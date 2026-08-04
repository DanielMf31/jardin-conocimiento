---
title: "LeetCode 435 — Non-overlapping Intervals"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/intervals, patron/greedy]
type: nota
status: en-progreso
source: claude-code
aliases: [Non-overlapping Intervals, LC 435, eraseOverlapIntervals]
problem_id: 435
difficulty: medium
patron: intervals
neetcode_order: 3
---

# LeetCode 435 — Non-overlapping Intervals

> **Tercer problema de Intervals**. **Greedy con sort por end**. El que termina antes deja más espacio para los siguientes.

## Enunciado

Mínimo número de intervalos a **eliminar** para que el resto no solape.

---

## Solución — Greedy sort por end

```python
class Solution:
    def eraseOverlapIntervals(self, intervals):
        intervals.sort(key=lambda x: x[1])       # por END
        end = float('-inf')
        kept = 0
        for s, e in intervals:
            if s >= end:
                end = e
                kept += 1
        return len(intervals) - kept
```

**Análisis:** O(n log n).

### Por qué sort por end (no por start)

Si ordenas por end, el primero que termina deja **el máximo espacio posible** para los siguientes. Tomarlo greedy es óptimo (interval scheduling).

---

## Conexiones

- Próximo: [[252-meeting-rooms]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
