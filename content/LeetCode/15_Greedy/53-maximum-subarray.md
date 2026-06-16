---
title: "LeetCode 53 — Maximum Subarray"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/greedy, patron/kadane]
type: nota
status: en-progreso
source: claude-code
aliases: [Maximum Subarray, LC 53, maxSubArray, Kadane]
problem_id: 53
difficulty: medium
patron: greedy
neetcode_order: 1
---

# LeetCode 53 — Maximum Subarray

> 🎯 **Primer problema de Greedy — Kadane's algorithm**. **El "fib" del greedy**. La idea: en cada posición, decidir si "extender el subarray actual" o "reiniciar desde aquí".

## Enunciado

Devuelve la **suma máxima** de un subarray contiguo no vacío.

---

## Solución — Kadane O(n)

```python
class Solution:
    def maxSubArray(self, nums):
        curr = best = nums[0]
        for n in nums[1:]:
            curr = max(n, curr + n)              # extender o reiniciar
            best = max(best, curr)
        return best
```

**Análisis:** O(n) tiempo, O(1) espacio.

### Decisión greedy

`curr = max(n, curr + n)`:
- Si `curr + n < n`, conviene **reiniciar** desde n.
- Si no, **extender** el subarray actual.

---

## Conexiones

- [[121-best-time-to-buy-and-sell-stock]] — patrón one-pass tracking similar.
- Próximo: [[55-jump-game]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
