---
title: "LeetCode 62 — Unique Paths"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-2d, patron/grid]
type: nota
status: en-progreso
source: claude-code
aliases: [Unique Paths, LC 62, uniquePaths]
problem_id: 62
difficulty: medium
patron: dp-2d
neetcode_order: 1
---

# LeetCode 62 — Unique Paths

> 🎯 **Primer problema de DP 2-D**. **Caminos en un grid** moviéndose solo derecha o abajo. `dp[i][j] = dp[i-1][j] + dp[i][j-1]`.

## Enunciado

Robot en grid `m × n`. Empieza en top-left, llega a bottom-right. Solo puede mover **derecha o abajo**. ¿Cuántos caminos únicos hay?

---

## Solución — DP 2-D O(n) espacio

```python
class Solution:
    def uniquePaths(self, m, n):
        dp = [1] * n
        for i in range(1, m):
            for j in range(1, n):
                dp[j] += dp[j-1]
        return dp[-1]
```

**Análisis:** O(m·n) tiempo, O(n) espacio (rolling array).

### Recurrencia

`dp[i][j] = dp[i-1][j] + dp[i][j-1]` — formas de llegar a (i,j) = formas de llegar desde arriba + desde la izquierda. Primera fila/columna todo 1s.

---

## Conexiones

- Próximo: [[1143-longest-common-subsequence]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
