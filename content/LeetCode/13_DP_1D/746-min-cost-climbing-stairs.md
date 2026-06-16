---
title: "LeetCode 746 — Min Cost Climbing Stairs"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/dp-1d]
type: nota
status: en-progreso
source: claude-code
aliases: [Min Cost Climbing Stairs, LC 746, minCostClimbingStairs]
problem_id: 746
difficulty: easy
patron: dp-1d
neetcode_order: 2
---

# LeetCode 746 — Min Cost Climbing Stairs

> 🎯 **Segundo problema de DP 1-D**. Variante de [[70-climbing-stairs]] con **costes**: cada peldaño tiene un coste y queremos llegar al final con coste mínimo.

## Enunciado

Array `cost` donde `cost[i]` es el coste del peldaño `i`. Puedes empezar en peldaño 0 o 1. Cada paso sube 1 o 2 peldaños. Devuelve el coste mínimo para llegar al final (más allá del último peldaño).

---

## Solución — DP iterativa O(1)

```python
class Solution:
    def minCostClimbingStairs(self, cost):
        # dp[i] = coste mínimo para llegar al peldaño i
        # dp[i] = min(dp[i-1] + cost[i-1], dp[i-2] + cost[i-2])
        a, b = 0, 0                              # dp[0], dp[1]: empezar en 0 o 1
        for i in range(2, len(cost) + 1):
            a, b = b, min(b + cost[i-1], a + cost[i-2])
        return b
```

**Análisis:** O(n) tiempo, O(1) espacio.

---

## Conexiones

- [[70-climbing-stairs]] — base.
- Próximo: [[198-house-robber]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
