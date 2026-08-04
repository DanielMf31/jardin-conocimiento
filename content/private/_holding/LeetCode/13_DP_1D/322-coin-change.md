---
title: "LeetCode 322 — Coin Change"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-1d, patron/unbounded-knapsack]
type: nota
status: en-progreso
source: claude-code
aliases: [Coin Change, LC 322, coinChange]
problem_id: 322
difficulty: medium
patron: dp-1d
neetcode_order: 8
---

# LeetCode 322 — Coin Change

> **Octavo problema de DP 1-D**. **Unbounded knapsack**: cuántas monedas mínimas para sumar amount, monedas reusables. Es **el problema más típico** de "DP por valor objetivo".

## Enunciado

Array `coins` y `amount`. Devuelve **mínimo número de monedas** para sumar amount. `-1` si imposible.

---

## Solución — DP bottom-up

```python
class Solution:
    def coinChange(self, coins, amount):
        dp = [float('inf')] * (amount + 1)
        dp[0] = 0
        for a in range(1, amount + 1):
            for c in coins:
                if a - c >= 0:
                    dp[a] = min(dp[a], dp[a-c] + 1)
        return dp[amount] if dp[amount] != float('inf') else -1
```

**Análisis:** O(amount · n_coins).

### Recurrencia

`dp[a] = min(dp[a-c] + 1) para cada moneda c ≤ a`. **Probamos todas las monedas** que cabrían como "última moneda usada", y nos quedamos con el mínimo +1.

---

## Conexiones

- Próximo: [[152-maximum-product-subarray]].
- [[518-coin-change-ii]] — versión "cuántas combinaciones".

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
