---
title: "LeetCode 97 — Interleaving String"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-2d]
type: nota
status: en-progreso
source: claude-code
aliases: [Interleaving String, LC 97, isInterleave]
problem_id: 97
difficulty: medium
patron: dp-2d
neetcode_order: 6
---

# LeetCode 97 — Interleaving String

> **Sexto problema de DP 2-D**. ¿Es `s3` un interleave de `s1` y `s2`? DP donde `dp[i][j] = True` si `s3[0:i+j]` es interleave de `s1[0:i]` y `s2[0:j]`.

## Enunciado

¿`s3` se forma intercalando `s1` y `s2` (cada uno en orden)?

**Ejemplo:** s1="aabcc", s2="dbbca", s3="aadbbcbcac" → True.

---

## Solución — DP 2-D

```python
class Solution:
    def isInterleave(self, s1, s2, s3):
        if len(s1) + len(s2) != len(s3): return False
        m, n = len(s1), len(s2)
        dp = [[False] * (n+1) for _ in range(m+1)]
        dp[0][0] = True
        for i in range(m+1):
            for j in range(n+1):
                if i > 0 and s1[i-1] == s3[i+j-1]:
                    dp[i][j] |= dp[i-1][j]
                if j > 0 and s2[j-1] == s3[i+j-1]:
                    dp[i][j] |= dp[i][j-1]
        return dp[m][n]
```

**Análisis:** O(m·n).

---

## Conexiones

- Próximo: [[72-edit-distance]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
