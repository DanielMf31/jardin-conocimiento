---
title: "LeetCode 79 — Word Search"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/backtracking, patron/grid-dfs]
type: nota
status: en-progreso
source: claude-code
aliases: [Word Search, LC 79, exist, Búsqueda palabra grid]
problem_id: 79
difficulty: medium
patron: backtracking
neetcode_order: 6
---

# LeetCode 79 — Word Search

> 🎯 **Sexto problema del patrón Backtracking**. **Backtracking en un grid 2D**. Es la versión sin Trie de [[212-word-search-ii]] — busca **una sola palabra** moviéndote 4-direccionalmente.

## Enunciado

Dado un grid 2D de letras y un `word`, devuelve `True` si la palabra existe formada por celdas adyacentes (horizontal/vertical, **sin reusar celda**).

---

## Solución — DFS + backtracking marcando visitadas

```python
class Solution:
    def exist(self, board, word):
        rows, cols = len(board), len(board[0])

        def dfs(r, c, i):
            if i == len(word):
                return True
            if (r < 0 or r >= rows or c < 0 or c >= cols
                    or board[r][c] != word[i]):
                return False

            tmp = board[r][c]
            board[r][c] = '#'                    # marcar visitada
            found = (dfs(r+1, c, i+1) or dfs(r-1, c, i+1)
                     or dfs(r, c+1, i+1) or dfs(r, c-1, i+1))
            board[r][c] = tmp                    # desmarcar (backtrack)
            return found

        for r in range(rows):
            for c in range(cols):
                if dfs(r, c, 0):
                    return True
        return False
```

**Análisis:**
- **Tiempo: O(M·N · 4^L)** donde M·N celdas, L = longitud de word.
- **Espacio: O(L)** call stack.

### El truco de marcar con `'#'` y restaurar

Para evitar reusar celdas, **marcamos** el carácter como `'#'` antes de recurrir. Al volver, **restauramos** (backtrack). Esto evita usar un `visited` set adicional.

---

## Conexiones

- [[212-word-search-ii]] — versión Hard con Trie y múltiples palabras.
- Próximo: [[131-palindrome-partitioning]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
