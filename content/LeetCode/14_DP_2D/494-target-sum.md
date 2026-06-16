---
title: "LeetCode 494 — Target Sum"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-2d, patron/0-1-knapsack]
type: nota
status: en-progreso
source: claude-code
aliases: [Target Sum, LC 494, findTargetSumWays]
problem_id: 494
difficulty: medium
patron: dp-2d
neetcode_order: 5
---

# LeetCode 494 — Target Sum

> 🎯 **Quinto problema de DP 2-D**. ¿De cuántas formas asignar `+` o `-` a cada número para sumar `target`? **0-1 knapsack** con dict como DP.

## Enunciado

Dado `nums` y `target`, asigna `+` o `-` a cada número. Cuenta cuántas asignaciones suman exactamente `target`.

---

## Solución — DP con dict

```python
class Solution:
    def findTargetSumWays(self, nums, target):
        dp = {0: 1}                              # suma -> número de formas
        for n in nums:
            new_dp = {}
            for s, count in dp.items():
                new_dp[s + n] = new_dp.get(s + n, 0) + count
                new_dp[s - n] = new_dp.get(s - n, 0) + count
            dp = new_dp
        return dp.get(target, 0)
```

**Análisis:** O(n · S) donde S = rango de sumas posibles.

---

## Conexiones

- [[416-partition-equal-subset-sum]] — 0-1 knapsack hermano.
- Próximo: [[97-interleaving-string]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
