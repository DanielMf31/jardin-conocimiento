---
title: "LeetCode 312 — Burst Balloons"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/dp-2d, patron/interval-dp]
type: nota
status: en-progreso
source: claude-code
aliases: [Burst Balloons, LC 312, maxCoins]
problem_id: 312
difficulty: hard
patron: dp-2d
neetcode_order: 10
---

# LeetCode 312 — Burst Balloons

> **Décimo problema de DP 2-D — Hard**. **Interval DP**. Truco contra-intuitivo: en lugar de pensar "qué globo reviento PRIMERO", pensar "qué globo reviento al FINAL del intervalo".

## Enunciado

Globos con valores. Reventar el globo `i` da `nums[i-1] · nums[i] · nums[i+1]` puntos (vecinos virtuales 1 al borde). Maximiza puntos totales.

---

## Solución — Interval DP

```python
class Solution:
    def maxCoins(self, nums):
        nums = [1] + nums + [1]                  # padding
        n = len(nums)
        dp = [[0] * n for _ in range(n)]

        for length in range(2, n):
            for left in range(n - length):
                right = left + length
                for k in range(left + 1, right):
                    # Reventar k al FINAL del intervalo (left, right)
                    dp[left][right] = max(dp[left][right],
                        dp[left][k] + dp[k][right] + nums[left]*nums[k]*nums[right])

        return dp[0][n-1]
```

**Análisis:** O(n³).

### Por qué "reventar al final"

Si reventaras k **primero**, los valores de los vecinos cambiarían cuando revientes los demás → recursión imposible. Pensar al revés (k es **el último**) → cuando lo revientes, los vecinos son los originales `nums[left]` y `nums[right]` → recursión limpia.

---

## Conexiones

- Próximo: [[10-regular-expression-matching]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
