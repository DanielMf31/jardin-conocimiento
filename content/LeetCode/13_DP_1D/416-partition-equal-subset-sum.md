---
title: "LeetCode 416 — Partition Equal Subset Sum"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-1d, patron/0-1-knapsack]
type: nota
status: en-progreso
source: claude-code
aliases: [Partition Equal Subset Sum, LC 416, canPartition]
problem_id: 416
difficulty: medium
patron: dp-1d
neetcode_order: 12
---

# LeetCode 416 — Partition Equal Subset Sum

> **Duodécimo y último problema de DP 1-D**. **0-1 knapsack** clásico: ¿podemos llenar exactamente `sum/2` con los elementos? Cada elemento se usa **a lo sumo una vez**.

## Enunciado

Dado un array de enteros positivos, devuelve `True` si se puede dividir en **dos subconjuntos con la misma suma**.

---

## Solución — DP con set

```python
class Solution:
    def canPartition(self, nums):
        total = sum(nums)
        if total % 2 != 0: return False
        target = total // 2

        dp = {0}                                 # sumas alcanzables
        for n in nums:
            dp |= {s + n for s in dp}            # añadir nuevas sumas
            if target in dp:
                return True
        return False
```

**Análisis:** O(n · target).

### Por qué set

`dp` mantiene **todas las sumas alcanzables** con algún subconjunto. Para cada nuevo número, las nuevas sumas posibles son las antiguas + n. Si alcanzamos `target`, listo.

---

## Cierre DP 1-D

| # | Problema | Idea distintiva |
|---|---|---|
| 1 | [[70-climbing-stairs]] | Fibonacci |
| 2 | [[746-min-cost-climbing-stairs]] | Fib con costes |
| 3 | [[198-house-robber]] | Take or skip |
| 4 | [[213-house-robber-ii]] | Circular: dos pasadas |
| 5 | [[5-longest-palindromic-substring]] | Expand around center |
| 6 | [[647-palindromic-substrings]] | Contar palíndromos |
| 7 | [[91-decode-ways]] | Fib con condicional |
| 8 | [[322-coin-change]] | Unbounded knapsack |
| 9 | [[152-maximum-product-subarray]] | Track min y max |
| 10 | [[139-word-break]] | DP sobre split de string |
| 11 | [[300-longest-increasing-subsequence]] | LIS — DP o patience sort |
| 12 | **Este** | 0-1 knapsack con set |

---

## Conexiones

- Próximo patrón: 2-D DP comienza con [[62-unique-paths]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón DP 1-D cerrado** [OK]
