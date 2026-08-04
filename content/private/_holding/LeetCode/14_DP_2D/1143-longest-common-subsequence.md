---
title: "LeetCode 1143 — Longest Common Subsequence"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-2d, patron/lcs]
type: nota
status: en-progreso
source: claude-code
aliases: [LCS, LC 1143, longestCommonSubsequence]
problem_id: 1143
difficulty: medium
patron: dp-2d
neetcode_order: 2
---

# LeetCode 1143 — Longest Common Subsequence

> **Segundo problema de DP 2-D — el LCS clásico**. La base de Edit Distance, Diff algorithms, bioinformática.

## Enunciado

Dadas dos strings `text1` y `text2`, devuelve la **longitud de la subsecuencia común más larga**.

---

## Solución — DP 2-D

```python
class Solution:
    def longestCommonSubsequence(self, text1, text2):
        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        return dp[m][n]
```

**Análisis:** O(m·n).

### Recurrencia

- Si `text1[i-1] == text2[j-1]`: extender LCS añadiendo este char → `dp[i-1][j-1] + 1`.
- Si no: heredar el mejor de los dos vecinos.

---

## Conexiones

- [[72-edit-distance]] — generalización.
- Próximo: [[309-best-time-to-buy-and-sell-stock-with-cooldown]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
