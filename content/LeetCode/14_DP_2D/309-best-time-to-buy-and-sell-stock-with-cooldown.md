---
title: "LeetCode 309 — Best Time to Buy and Sell Stock with Cooldown"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-2d, patron/state-machine]
type: nota
status: en-progreso
source: claude-code
aliases: [Stock with Cooldown, LC 309, maxProfit cooldown]
problem_id: 309
difficulty: medium
patron: dp-2d
neetcode_order: 3
---

# LeetCode 309 — Best Time to Buy and Sell Stock with Cooldown

> **Tercer problema de DP 2-D**. **DP con state machine** (3 estados: hold / sold / rest). Después de vender, cooldown de 1 día.

## Enunciado

Como [[121-best-time-to-buy-and-sell-stock]] pero múltiples transacciones permitidas, con cooldown de 1 día tras cada venta.

---

## Solución — State machine 3 estados

```python
class Solution:
    def maxProfit(self, prices):
        # Estados: hold (con stock), sold (acabo de vender, cooldown), rest (sin stock)
        hold = -prices[0]                        # comprar el día 0
        sold = 0
        rest = 0
        for p in prices[1:]:
            prev_sold = sold
            sold = hold + p                      # vender hoy
            hold = max(hold, rest - p)           # mantener o comprar (desde rest)
            rest = max(rest, prev_sold)          # quedarse sin stock
        return max(sold, rest)
```

**Análisis:** O(n) tiempo, O(1) espacio.

### Las transiciones

```
rest → hold (comprar)
hold → sold (vender)
sold → rest (cooldown obligatorio 1 día)
rest → rest (no hago nada)
```

---

## Conexiones

- [[121-best-time-to-buy-and-sell-stock]] — base sin cooldown.
- Próximo: [[518-coin-change-ii]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
