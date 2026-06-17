---
title: "LeetCode 152 — Maximum Product Subarray"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-1d, patron/track-min-max]
type: nota
status: en-progreso
source: claude-code
aliases: [Max Product Subarray, LC 152, maxProduct]
problem_id: 152
difficulty: medium
patron: dp-1d
neetcode_order: 9
---

# LeetCode 152 — Maximum Product Subarray

> **Noveno problema de DP 1-D**. Variante de Kadane (Max Subarray Sum) pero con producto: trampa de **negativos** que pueden voltear min en max. Solución: **trackear min y max** en cada paso.

## Enunciado

Dado un array de enteros, devuelve el **producto máximo** de un subarray contiguo.

---

## Solución — Track min y max simultáneamente

```python
class Solution:
    def maxProduct(self, nums):
        result = curr_max = curr_min = nums[0]
        for n in nums[1:]:
            tmp = curr_max
            curr_max = max(n, n * curr_max, n * curr_min)
            curr_min = min(n, n * tmp, n * curr_min)
            result = max(result, curr_max)
        return result
```

**Análisis:** O(n) tiempo, O(1) espacio.

### Por qué trackear min

Si `n` es negativo, `n * curr_min` (un negativo grande) podría dar el **máximo**. Sin trackear min, perderías esa posibilidad. Por eso ambos.

---

## Conexiones

- LC 53 (Maximum Subarray) — Kadane con suma.
- Próximo: [[139-word-break]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
