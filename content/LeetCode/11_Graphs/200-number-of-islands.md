---
title: "LeetCode 200 — Number of Islands"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/grid-bfs-dfs, patron/connected-components]
type: nota
status: en-progreso
source: claude-code
aliases: [Number of Islands, LC 200, numIslands, Islas]
problem_id: 200
difficulty: medium
patron: graphs
neetcode_order: 1
---

# LeetCode 200 — Number of Islands

> 🎯 **Primer problema del patrón Graphs** y el más típico. **Conteo de componentes conexos** en un grid 2D. Aprende este patrón aquí; los próximos 5 problemas son variantes directas.

## Enunciado

Dado un grid 2D de `'1'` (tierra) y `'0'` (agua), cuenta el **número de islas**. Una isla es un grupo de `'1'` conectados horizontal/vertical (no diagonal).

**Ejemplo:**
```
Input:  [["1","1","0","0","0"],
         ["1","1","0","0","0"],
         ["0","0","1","0","0"],
         ["0","0","0","1","1"]]
Output: 3
```

---

## Solución — DFS marcando visitadas

```python
class Solution:
    def numIslands(self, grid):
        if not grid: return 0
        rows, cols = len(grid), len(grid[0])
        count = 0

        def dfs(r, c):
            if (r < 0 or r >= rows or c < 0 or c >= cols
                    or grid[r][c] != '1'):
                return
            grid[r][c] = '0'                    # marcar visitada (hundir)
            dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == '1':
                    count += 1
                    dfs(r, c)                    # hundir toda la isla

        return count
```

**Análisis:**
- **Tiempo: O(M·N)**.
- **Espacio: O(M·N)** call stack peor caso.

### Patrón "iterar grid + DFS sobre componente"

Aparece en LC 200, 695, 130, 994, 286, 417. Es **el patrón maestro** de grid problems.

### BFS variante (más segura para call stack grande)

```python
from collections import deque
def bfs(r, c):
    q = deque([(r, c)])
    grid[r][c] = '0'
    while q:
        r, c = q.popleft()
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':
                grid[nr][nc] = '0'
                q.append((nr, nc))
```

---

## Conexiones

- [[79-word-search]] — DFS en grid.
- Próximo: [[133-clone-graph]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
