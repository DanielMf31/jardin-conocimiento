---
title: "LeetCode 252 — Meeting Rooms"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/intervals]
type: nota
status: en-progreso
source: claude-code
aliases: [Meeting Rooms, LC 252, canAttendMeetings]
problem_id: 252
difficulty: easy
patron: intervals
neetcode_order: 4
---

# LeetCode 252 — Meeting Rooms

> 🎯 **Cuarto problema de Intervals — Easy**. ¿Puede una persona asistir a todas las reuniones? Sort + check de solapamiento.

## Enunciado

Intervalos de meetings. Devuelve `True` si no hay dos que solapen.

---

## Solución — Sort + check vecinos

```python
class Solution:
    def canAttendMeetings(self, intervals):
        intervals.sort(key=lambda x: x[0])
        for i in range(1, len(intervals)):
            if intervals[i][0] < intervals[i-1][1]:
                return False
        return True
```

**Análisis:** O(n log n).

---

## Conexiones

- Próximo: [[253-meeting-rooms-ii]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
