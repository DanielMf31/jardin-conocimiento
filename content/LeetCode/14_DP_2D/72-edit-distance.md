---
title: "LeetCode 72 — Edit Distance"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-2d, patron/edit-distance]
type: nota
status: en-progreso
source: claude-code
aliases: [Edit Distance, LC 72, minDistance, Levenshtein]
problem_id: 72
difficulty: medium
patron: dp-2d
neetcode_order: 7
---

# LeetCode 72 — Edit Distance

> 🎯 **Séptimo problema de DP 2-D — el más importante**. **Distancia de Levenshtein**. Aplicaciones: spell checking, diff algorithms, bioinformática (secuencias DNA).

## Enunciado

Mínimo número de **operaciones** (insertar/borrar/reemplazar 1 char) para convertir `word1` en `word2`.

---

## Solución — DP 2-D clásico

```python
class Solution:
    def minDistance(self, word1, word2):
        m, n = len(word1), len(word2)
        dp = [[0] * (n+1) for _ in range(m+1)]
        for i in range(m+1): dp[i][0] = i
        for j in range(n+1): dp[0][j] = j

        for i in range(1, m+1):
            for j in range(1, n+1):
                if word1[i-1] == word2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j],      # delete
                                        dp[i][j-1],     # insert
                                        dp[i-1][j-1])   # replace
        return dp[m][n]
```

**Análisis:** O(m·n).

### Las 3 operaciones

- `dp[i-1][j]`: borrar de word1.
- `dp[i][j-1]`: insertar en word1 (= avanzar en word2).
- `dp[i-1][j-1]`: reemplazar.

Si los chars coinciden, no hay coste extra → `dp[i-1][j-1]`.

---

## Conexiones

- [[1143-longest-common-subsequence]] — patrón hermano.
- Próximo: [[329-longest-increasing-path-in-a-matrix]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
