---
title: "LeetCode 230 — Kth Smallest Element in a BST"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/trees, patron/bst, patron/inorder-traversal]
type: nota
status: en-progreso
source: claude-code
aliases: [Kth Smallest BST, LC 230, kthSmallest, K-ésimo más pequeño BST]
problem_id: 230
difficulty: medium
patron: trees
neetcode_order: 12
---

# LeetCode 230 — Kth Smallest Element in a BST

> **Duodécimo problema del patrón Trees**. **Propiedad clave del BST**: inorder traversal produce los valores en orden creciente. Por tanto, el k-ésimo nodo visitado en inorder es el k-ésimo más pequeño.

## Enunciado

Dada la raíz de un BST y un entero `k`, devuelve el k-ésimo valor más pequeño (1-indexed).

---

## Solución 1 — Inorder con lista (intuitivo)

```python
class Solution:
    def kthSmallest(self, root, k) -> int:
        result = []
        def inorder(node):
            if not node: return
            inorder(node.left)
            result.append(node.val)
            inorder(node.right)
        inorder(root)
        return result[k - 1]
```

**Análisis:** O(n) tiempo, O(n) espacio.

---

## Solución 2 — Inorder con early exit (la óptima)

```python
class Solution:
    def kthSmallest(self, root, k) -> int:
        self.count = 0
        self.result = None
        def inorder(node):
            if not node or self.result is not None: return
            inorder(node.left)
            self.count += 1
            if self.count == k:
                self.result = node.val
                return
            inorder(node.right)
        inorder(root)
        return self.result
```

**Análisis:** O(h + k) tiempo (no recorre todo el árbol).

---

## Solución 3 — Iterativa con stack

```python
def kthSmallest(self, root, k):
    stack = []
    curr = root
    while stack or curr:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        k -= 1
        if k == 0: return curr.val
        curr = curr.right
```

**Veredicto:** O(h + k) sin recursión. **Es la canónica de entrevista** porque demuestra dominio del inorder iterativo.

---

## Conexiones

- [[98-validate-binary-search-tree]] — inorder propiedad.
- Próximo: [[105-construct-binary-tree-from-preorder-and-inorder-traversal]].

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
