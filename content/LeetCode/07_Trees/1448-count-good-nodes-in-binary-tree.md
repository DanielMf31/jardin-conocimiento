---
title: "LeetCode 1448 — Count Good Nodes in Binary Tree"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/trees, patron/dfs, patron/recursion-acumulador]
type: nota
status: en-progreso
source: claude-code
aliases: [Count Good Nodes, LC 1448, goodNodes, Nodos buenos]
problem_id: 1448
difficulty: medium
patron: trees
neetcode_order: 10
---

# LeetCode 1448 — Count Good Nodes in Binary Tree

> 🎯 **Décimo problema del patrón Trees**. Introduce el truco **"pasar contexto hacia abajo"** en la recursión (el max visto en el camino). Es la versión "acumulador top-down" del DFS.

## Enunciado

Un nodo X es **good** si en el camino desde root hasta X, **no hay ningún nodo con valor mayor** que X.

Devuelve el número de good nodes.

**Ejemplo:**
```
        3
       / \
      1   4
     /   / \
    3   1   5

Good: 3 (root), 4, 5, 3-izquierdo (igual a 3 está OK)
Output: 4
```

---

## Solución — DFS pasando max en el camino (la canónica)

```python
class Solution:
    def goodNodes(self, root) -> int:
        def dfs(node, max_so_far):
            if not node: return 0
            count = 1 if node.val >= max_so_far else 0
            new_max = max(max_so_far, node.val)
            count += dfs(node.left, new_max)
            count += dfs(node.right, new_max)
            return count

        return dfs(root, root.val)
```

**Análisis:** O(n) tiempo, O(h) espacio.

### Patrón "acumulador top-down"

A diferencia de [[543-diameter-of-binary-tree]] (donde devuelves info al padre), aquí **pasas info al hijo**: el max visto en el camino. Es DFS con **estado heredado**.

---

## Conexiones

- [[226-invert-binary-tree]] — recursión simple.
- Próximo: [[98-validate-binary-search-tree]] — pasar bounds top-down.

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
