---
title: "LeetCode 235 — Lowest Common Ancestor of a BST"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/trees, patron/bst]
type: nota
status: en-progreso
source: claude-code
aliases: [LCA BST, LC 235, lowestCommonAncestor, Ancestro común BST]
problem_id: 235
difficulty: medium
patron: trees
neetcode_order: 7
---

# LeetCode 235 — Lowest Common Ancestor of a Binary Search Tree

> 🎯 **Séptimo problema del patrón Trees**. Aprovecha la **propiedad BST** (left.val < node.val < right.val) para resolver el LCA en O(log n) en lugar de O(n) (que sería en árbol genérico, LC 236).

## Enunciado

Dado un BST y dos nodos `p` y `q`, devuelve su **ancestro común más bajo** (LCA).

> 💡 **BST**: Binary Search Tree. Para cada nodo: todos los valores del subárbol izquierdo son **menores**, todos los del derecho son **mayores**.

---

## Solución — Recursión usando la propiedad BST (la canónica)

**Idea**: si ambos `p` y `q` son **menores** que el nodo actual, el LCA está a la izquierda. Si son mayores, a la derecha. Si **uno está a cada lado** (o uno es el nodo), el nodo actual es el LCA.

```python
class Solution:
    def lowestCommonAncestor(self, root, p, q):
        if p.val < root.val and q.val < root.val:
            return self.lowestCommonAncestor(root.left, p, q)
        if p.val > root.val and q.val > root.val:
            return self.lowestCommonAncestor(root.right, p, q)
        return root                               # punto de divergencia
```

**Análisis:**
- **Tiempo: O(h)** = O(log n) en BST balanceado.
- **Espacio: O(h)**.
- **Veredicto:** ✅ canónica.

### Versión iterativa (igual de elegante)

```python
def lowestCommonAncestor(self, root, p, q):
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            return root
```

O(1) espacio extra.

---

## Conexiones

- [[100-same-tree]] — recursión sobre árbol.
- Próximo: [[102-binary-tree-level-order-traversal]] — primer BFS.
- LC 236 (Hard version): LCA en árbol genérico, sin propiedad BST.

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
