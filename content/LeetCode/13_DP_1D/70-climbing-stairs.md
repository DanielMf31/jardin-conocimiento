---
title: "LeetCode 70 — Climbing Stairs"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/dp-1d, patron/fibonacci]
type: nota
status: en-progreso
source: claude-code
aliases: [Climbing Stairs, LC 70, climbStairs]
problem_id: 70
difficulty: easy
patron: dp-1d
neetcode_order: 1
---

# LeetCode 70 — Climbing Stairs

> 🎯 **Primer problema de DP 1-D — el Hello World del DP**. Es **Fibonacci disfrazado**: para llegar al peldaño `n`, solo puedes llegar desde `n-1` (subiendo 1) o `n-2` (subiendo 2). Por tanto `f(n) = f(n-1) + f(n-2)`.

## Enunciado

Subes una escalera de `n` peldaños. Cada paso es 1 o 2 peldaños. ¿De cuántas formas distintas puedes llegar arriba?

---

## Solución — DP iterativa O(1) espacio

```python
class Solution:
    def climbStairs(self, n):
        if n <= 2: return n
        a, b = 1, 2                              # f(1), f(2)
        for _ in range(3, n + 1):
            a, b = b, a + b
        return b
```

**Análisis:** O(n) tiempo, O(1) espacio.

### El patrón "Fibonacci with memo"

Casi cualquier problema 1-D DP donde el estado depende de los **2 anteriores** se reduce a este patrón:

```python
prev2, prev1 = base0, base1
for i in range(2, n+1):
    curr = combine(prev2, prev1, i)
    prev2, prev1 = prev1, curr
return prev1
```

---

## Conexiones

- Próximo: [[746-min-cost-climbing-stairs]] — variante con costes.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
