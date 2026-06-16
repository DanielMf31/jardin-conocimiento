---
title: "LeetCode 10 — Regular Expression Matching"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/dp-2d, patron/regex]
type: nota
status: en-progreso
source: claude-code
aliases: [Regular Expression Matching, LC 10, isMatch]
problem_id: 10
difficulty: hard
patron: dp-2d
neetcode_order: 11
---

# LeetCode 10 — Regular Expression Matching

> 🎯 **Undécimo y último problema de DP 2-D — Hard**. Matchear regex con `'.'` (cualquier char) y `'*'` (0+ del previo). DP 2-D con casuística.

## Enunciado

`s` es una cadena, `p` un patrón con caracteres normales, `'.'` y `'*'`. Devuelve `True` si `p` matchea **toda** `s`.

---

## Solución — DP 2-D

```python
class Solution:
    def isMatch(self, s, p):
        m, n = len(s), len(p)
        dp = [[False] * (n+1) for _ in range(m+1)]
        dp[0][0] = True

        # Patrón vacío matches s vacío. Patrones tipo a*, a*b*, etc. matchean s vacío
        for j in range(1, n+1):
            if p[j-1] == '*':
                dp[0][j] = dp[0][j-2]

        for i in range(1, m+1):
            for j in range(1, n+1):
                if p[j-1] == '.' or p[j-1] == s[i-1]:
                    dp[i][j] = dp[i-1][j-1]
                elif p[j-1] == '*':
                    dp[i][j] = dp[i][j-2]                            # 0 ocurrencias
                    if p[j-2] == '.' or p[j-2] == s[i-1]:
                        dp[i][j] |= dp[i-1][j]                       # ≥1 ocurrencia

        return dp[m][n]
```

**Análisis:** O(m·n).

### Las 3 ramas

- **Match directo** (char o `.`): heredar `dp[i-1][j-1]`.
- **`*` con 0 ocurrencias**: heredar `dp[i][j-2]` (saltar `x*`).
- **`*` con ≥1 ocurrencia**: si `p[j-2]` matchea `s[i-1]`, heredar `dp[i-1][j]` (consumir un char de s, mantener `x*`).

---

## Cierre DP 2-D 🎉

| # | Problema | Idea distintiva |
|---|---|---|
| 1 | [[62-unique-paths]] | Caminos en grid |
| 2 | [[1143-longest-common-subsequence]] | LCS clásico |
| 3 | [[309-best-time-to-buy-and-sell-stock-with-cooldown]] | State machine 3 estados |
| 4 | [[518-coin-change-ii]] | Combinaciones (moneda en bucle externo) |
| 5 | [[494-target-sum]] | 0-1 knapsack con dict |
| 6 | [[97-interleaving-string]] | Interleave check con DP |
| 7 | [[72-edit-distance]] | Levenshtein clásico |
| 8 | [[329-longest-increasing-path-in-a-matrix]] | DFS + memo en grid |
| 9 | [[115-distinct-subsequences]] | DP similar a LCS |
| 10 | [[312-burst-balloons]] | Interval DP "al final" |
| 11 | **Este** | Regex matching DP |

---

## Conexiones

- [[1143-longest-common-subsequence]] · [[72-edit-distance]] — los dos pilares.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón DP 2-D cerrado** ✅
