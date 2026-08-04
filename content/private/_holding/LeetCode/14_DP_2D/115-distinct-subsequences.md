---
title: "LeetCode 115 — Distinct Subsequences"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/dp-2d]
type: nota
status: en-progreso
source: claude-code
aliases: [Distinct Subsequences, LC 115, numDistinct]
problem_id: 115
difficulty: hard
patron: dp-2d
neetcode_order: 9
---

# LeetCode 115 — Distinct Subsequences

> **Noveno problema de DP 2-D — Hard**. ¿Cuántas formas hay de obtener `t` como **subsecuencia** de `s`? DP 2-D similar a LCS.

## Enunciado

Dado strings `s` y `t`, devuelve el número de subsecuencias distintas de `s` que igualan a `t`.

---

## Solución — DP 2-D

```python
class Solution:
    def numDistinct(self, s, t):
        m, n = len(s), len(t)
        dp = [[0] * (n+1) for _ in range(m+1)]
        for i in range(m+1):
            dp[i][0] = 1                         # forma vacía: 1

        for i in range(1, m+1):
            for j in range(1, n+1):
                dp[i][j] = dp[i-1][j]            # no usar s[i-1]
                if s[i-1] == t[j-1]:
                    dp[i][j] += dp[i-1][j-1]     # usar s[i-1] como match

        return dp[m][n]
```

**Análisis:** O(m·n).

---

## Conexiones

- [[1143-longest-common-subsequence]] — base.
- Próximo: [[312-burst-balloons]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
