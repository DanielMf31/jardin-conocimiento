---
title: "LeetCode 518 — Coin Change II"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-2d, patron/unbounded-knapsack]
type: nota
status: en-progreso
source: claude-code
aliases: [Coin Change II, LC 518, change]
problem_id: 518
difficulty: medium
patron: dp-2d
neetcode_order: 4
---

# LeetCode 518 — Coin Change II

> **Cuarto problema de DP 2-D**. Variante de [[322-coin-change]]: en lugar de **mínimo número de monedas**, **cuántas combinaciones** distintas hay para sumar amount.

## Enunciado

`coins` y `amount`. Devuelve **número de combinaciones** que suman amount (cada moneda reusable, orden no importa).

---

## Solución — DP O(amount) espacio

```python
class Solution:
    def change(self, amount, coins):
        dp = [0] * (amount + 1)
        dp[0] = 1                                # una forma de hacer 0: vacío
        for c in coins:                          # ⭐ moneda en bucle EXTERNO
            for a in range(c, amount + 1):
                dp[a] += dp[a - c]
        return dp[amount]
```

**Análisis:** O(amount · n_coins).

### Por qué moneda en bucle externo

Si pones `for c in coins` **dentro**, contarías `[1,2]` y `[2,1]` como combinaciones distintas. Con la moneda fuera, **fijas un orden** y solo cuentas combinaciones únicas.

---

## Conexiones

- [[322-coin-change]] — versión "mínimo".
- Próximo: [[494-target-sum]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
