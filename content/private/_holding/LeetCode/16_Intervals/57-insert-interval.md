---
title: "LeetCode 57 — Insert Interval"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/intervals]
type: nota
status: en-progreso
source: claude-code
aliases: [Insert Interval, LC 57, insert]
problem_id: 57
difficulty: medium
patron: intervals
neetcode_order: 1
---

# LeetCode 57 — Insert Interval

> **Primer problema de Intervals**. Insertar un nuevo intervalo en una lista ordenada y fusionar solapamientos. Patrón: **3 fases** (antes, fusión, después).

## Enunciado

Lista ordenada de intervalos no solapados. Insertar `newInterval` y fusionar si solapan.

---

## Solución — 3 fases

```python
class Solution:
    def insert(self, intervals, newInterval):
        result = []
        i, n = 0, len(intervals)
        # Fase 1: antes
        while i < n and intervals[i][1] < newInterval[0]:
            result.append(intervals[i]); i += 1
        # Fase 2: fusión
        while i < n and intervals[i][0] <= newInterval[1]:
            newInterval[0] = min(newInterval[0], intervals[i][0])
            newInterval[1] = max(newInterval[1], intervals[i][1])
            i += 1
        result.append(newInterval)
        # Fase 3: después
        while i < n:
            result.append(intervals[i]); i += 1
        return result
```

**Análisis:** O(n).

---

## Conexiones

- Próximo: [[56-merge-intervals]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
