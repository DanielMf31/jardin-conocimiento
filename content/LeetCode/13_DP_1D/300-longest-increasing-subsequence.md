---
title: "LeetCode 300 — Longest Increasing Subsequence"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-1d, patron/lis]
type: nota
status: en-progreso
source: claude-code
aliases: [LIS, LC 300, lengthOfLIS, Longest Increasing Subsequence]
problem_id: 300
difficulty: medium
patron: dp-1d
neetcode_order: 11
---

# LeetCode 300 — Longest Increasing Subsequence

> 🎯 **Undécimo problema de DP 1-D**. **LIS clásico**. DP O(n²) o **patience sorting** con binary search O(n log n).

## Enunciado

Devuelve la **longitud** de la subsecuencia (no contigua) estrictamente creciente más larga.

---

## Solución 1 — DP O(n²)

```python
class Solution:
    def lengthOfLIS(self, nums):
        dp = [1] * len(nums)
        for i in range(1, len(nums)):
            for j in range(i):
                if nums[j] < nums[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        return max(dp)
```

**Análisis:** O(n²).

---

## Solución 2 — Patience sorting + binary search O(n log n)

```python
from bisect import bisect_left
class Solution:
    def lengthOfLIS(self, nums):
        sub = []
        for n in nums:
            i = bisect_left(sub, n)
            if i == len(sub):
                sub.append(n)
            else:
                sub[i] = n                       # reemplazar
        return len(sub)
```

**Análisis:** O(n log n). `sub` no es la subsecuencia real, pero su **longitud** sí lo es.

---

## Conexiones

- Próximo: [[416-partition-equal-subset-sum]].

## Estado

- [ ] Leído
- [ ] Implementadas ambas soluciones
- [ ] Resuelto en LeetCode
