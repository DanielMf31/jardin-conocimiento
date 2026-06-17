---
title: "LeetCode 199 — Binary Tree Right Side View"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/trees, patron/bfs]
type: nota
status: en-progreso
source: claude-code
aliases: [Right Side View, LC 199, rightSideView, Vista lateral derecha]
problem_id: 199
difficulty: medium
patron: trees
neetcode_order: 9
---

# LeetCode 199 — Binary Tree Right Side View

> **Noveno problema del patrón Trees**. Variante directa de [[102-binary-tree-level-order-traversal]]: devolver solo el **último nodo de cada nivel** (el visible desde la derecha).

## Enunciado

Imagina que estás de pie a la **derecha** del árbol. Devuelve los valores de los nodos que verías de arriba a abajo.

**Ejemplo:**
```
       1
      / \
     2   3
      \   \
       5   4

Output: [1, 3, 4]
```

---

## Solución — BFS, último nodo de cada nivel (la canónica)

```python
from collections import deque

class Solution:
    def rightSideView(self, root):
        if not root: return []
        result = []
        q = deque([root])
        while q:
            n = len(q)
            for i in range(n):
                node = q.popleft()
                if i == n - 1:                   # último de este nivel
                    result.append(node.val)
                if node.left: q.append(node.left)
                if node.right: q.append(node.right)
        return result
```

**Análisis:** O(n) tiempo y espacio. Mismo BFS de LC 102 con un check extra.

### Variante DFS (preorder right-first)

```python
def rightSideView(self, root):
    result = []
    def dfs(node, depth):
        if not node: return
        if depth == len(result):
            result.append(node.val)              # primero que llega a esta profundidad
        dfs(node.right, depth + 1)               # ⭐ derecha primero
        dfs(node.left, depth + 1)
    dfs(root, 0)
    return result
```

Visitar **derecha primero** garantiza que el primer nodo de cada profundidad es el de la derecha.

---

## Conexiones

- [[102-binary-tree-level-order-traversal]] — patrón BFS base.
- Próximo: [[1448-count-good-nodes-in-binary-tree]].

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
