---
title: "LeetCode 202 — Happy Number"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/math, patron/cycle-detection]
type: nota
status: en-progreso
source: claude-code
aliases: [Happy Number, LC 202, isHappy]
problem_id: 202
difficulty: easy
patron: math
neetcode_order: 1
---

# LeetCode 202 — Happy Number

> **Primer problema de Math & Geometry**. ¿Llega n a 1 sumando cuadrados de sus dígitos? **Detección de ciclos** con set o Floyd.

## Enunciado

`n` es happy si iterando "suma de cuadrados de dígitos" llega a 1. Si no, entra en ciclo. Devuelve `True` si happy.

---

## Solución 1 — Set de visitados

```python
class Solution:
    def isHappy(self, n):
        seen = set()
        while n != 1 and n not in seen:
            seen.add(n)
            n = sum(int(d)**2 for d in str(n))
        return n == 1
```

**Análisis:** O(log n) por iteración × número de iteraciones.

---

## Solución 2 — Floyd cycle detection (sin set)

```python
class Solution:
    def isHappy(self, n):
        def next_n(x): return sum(int(d)**2 for d in str(x))
        slow = n
        fast = next_n(n)
        while fast != 1 and slow != fast:
            slow = next_n(slow)
            fast = next_n(next_n(fast))
        return fast == 1
```

O(1) espacio. Mismo Floyd de [[141-linked-list-cycle]] aplicado a una secuencia numérica.

---

## Conexiones

- [[141-linked-list-cycle]] — Floyd.
- Próximo: [[66-plus-one]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
