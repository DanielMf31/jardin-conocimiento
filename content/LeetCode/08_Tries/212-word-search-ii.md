---
title: "LeetCode 212 — Word Search II"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/tries, patron/backtracking, patron/grid]
type: nota
status: en-progreso
source: claude-code
aliases: [Word Search II, LC 212, findWords]
problem_id: 212
difficulty: hard
patron: tries
neetcode_order: 3
---

# LeetCode 212 — Word Search II

> 🎯 **Tercer y último problema del patrón Tries — el Hard**. Combina **Trie + backtracking en grid**. La idea brillante: en lugar de buscar cada palabra en el grid (LC 79), construyes un Trie con todas las palabras y haces **un solo DFS** sobre el grid usando el Trie como guía.

## Enunciado

Dado un grid 2D `board` de letras y una lista `words`, devuelve **todas las palabras** que aparecen en el grid (formadas por celdas adyacentes horizontal/verticalmente, sin reusar celda).

**Ejemplo:**
```
board = [["o","a","a","n"],
         ["e","t","a","e"],
         ["i","h","k","r"],
         ["i","f","l","v"]]
words = ["oath","pea","eat","rain"]

Output: ["oath","eat"]
```

---

## Solución — Trie + DFS con backtracking

**Pasos**:
1. Construir Trie con todas las palabras.
2. Para cada celda del grid, hacer DFS siguiendo el Trie. Si llegas a un `is_end`, añade la palabra al resultado.
3. Backtracking: marca celda como visitada, recurse 4 direcciones, desmarca.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None             # almacena palabra completa al final del camino

class Solution:
    def findWords(self, board, words):
        # Construir Trie
        root = TrieNode()
        for word in words:
            node = root
            for c in word:
                if c not in node.children:
                    node.children[c] = TrieNode()
                node = node.children[c]
            node.word = word

        rows, cols = len(board), len(board[0])
        result = set()

        def dfs(r, c, node):
            if (r < 0 or r >= rows or c < 0 or c >= cols
                    or board[r][c] not in node.children):
                return
            char = board[r][c]
            child = node.children[char]
            if child.word:
                result.add(child.word)

            board[r][c] = '#'                    # marcar visitado
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                dfs(r + dr, c + dc, child)
            board[r][c] = char                   # desmarcar

            # Optimización: poda — si el nodo del Trie ya no tiene hijos, eliminarlo
            if not child.children:
                node.children.pop(char)

        for r in range(rows):
            for c in range(cols):
                dfs(r, c, root)

        return list(result)
```

**Análisis:**
- **Tiempo: O(M·N · 4^L)** donde M·N son celdas del grid y L es palabra más larga.
- **Espacio: O(total chars en words)** para el Trie.
- **Veredicto:** ✅ la canónica.

### El truco "node.word = word" en lugar de "is_end"

En lugar de `is_end = True`, almacenamos **la palabra completa** en el nodo final. Así al detectar fin, ya tenemos la palabra sin reconstruirla.

### La poda al final

```python
if not child.children:
    node.children.pop(char)
```

Si un nodo del Trie ya no tiene hijos (todas sus palabras se encontraron), lo eliminamos. Acelera búsquedas futuras.

---

## Cierre del patrón Tries 🎉

| # | Problema | Idea distintiva |
|---|---|---|
| 1 | [[208-implement-trie-prefix-tree]] | Estructura básica con `is_end` |
| 2 | [[211-design-add-and-search-words-data-structure]] | Trie + DFS con wildcards |
| 3 | **Este** | Trie + backtracking en grid |

**Próximo patrón**: Heap / Priority Queue (7 problemas).

---

## Conexiones

- [[208-implement-trie-prefix-tree]] · [[211-design-add-and-search-words-data-structure]] — base.
- LC 79 (Word Search) — versión sin Trie, una sola palabra.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón Tries cerrado** ✅
