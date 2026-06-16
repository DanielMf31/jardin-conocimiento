---
title: "LeetCode 329 — Longest Increasing Path in a Matrix"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/dp-2d, patron/dfs-memo]
type: nota
status: en-progreso
source: claude-code
aliases: [Longest Increasing Path Matrix, LC 329, longestIncreasingPath]
problem_id: 329
difficulty: hard
patron: dp-2d
neetcode_order: 8
---

# LeetCode 329 — Longest Increasing Path in a Matrix

> 🎯 **Octavo problema de DP 2-D — Hard**. **DFS + memoization** sobre grid. El camino más largo siguiendo valores crecientes.

## Enunciado

Grid `m × n` de enteros. Desde cualquier celda, mover a vecina (4 dirs) si su valor es **estrictamente mayor**. Devuelve la longitud del camino más largo.

---

## Solución — DFS + memo

```python
class Solution:
    def longestIncreasingPath(self, matrix):
        m, n = len(matrix), len(matrix[0])
        memo = {}

        def dfs(r, c):
            if (r, c) in memo: return memo[(r, c)]
            best = 1
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < m and 0 <= nc < n and matrix[nr][nc] > matrix[r][c]:
                    best = max(best, 1 + dfs(nr, nc))
            memo[(r, c)] = best
            return best

        return max(dfs(r, c) for r in range(m) for c in range(n))
```

**Análisis:** O(m·n) — cada celda se procesa una vez.

### Por qué no hay caso de visited explícito

El camino debe ser **estrictamente creciente** → no puedes volver a una celda ya visitada (su valor sería menor o igual). Garantiza que no hay ciclos.

---

## Conexiones

- Próximo: [[115-distinct-subsequences]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
