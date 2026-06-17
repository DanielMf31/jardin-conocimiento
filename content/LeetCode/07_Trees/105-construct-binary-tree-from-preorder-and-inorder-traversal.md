---
title: "LeetCode 105 — Construct Binary Tree from Preorder and Inorder Traversal"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/trees, patron/recursion-divide]
type: nota
status: en-progreso
source: claude-code
aliases: [Construct Tree Preorder Inorder, LC 105, buildTree, Reconstruir árbol]
problem_id: 105
difficulty: medium
patron: trees
neetcode_order: 13
---

# LeetCode 105 — Construct Binary Tree from Preorder and Inorder Traversal

> **Decimotercero problema del patrón Trees**. Reconstrucción a partir de dos recorridos. Combina **propiedad del preorder** (primer elemento es root) y **propiedad del inorder** (root divide en izquierda y derecha).

## Enunciado

Te dan dos arrays: `preorder` (recorrido preorder) e `inorder` (recorrido inorder) de un árbol binario. Reconstruye el árbol.

**Ejemplo:**
```
preorder = [3, 9, 20, 15, 7]
inorder  = [9, 3, 15, 20, 7]

Árbol:    3
         / \
        9   20
           /  \
          15   7
```

**Asume**: todos los valores son únicos.

---

## Idea clave

- **Preorder**: root, left, right. **El primer elemento es siempre la raíz.**
- **Inorder**: left, root, right. **La posición de la raíz divide** los elementos en izquierda y derecha.

```
preorder = [3, | 9, | 20, 15, 7]
            root  left   right

inorder = [9, | 3, | 15, 20, 7]
          left  root  right
```

Encontrando la raíz (3) en inorder, sabemos que `[9]` son los nodos del subárbol izquierdo y `[15, 20, 7]` los del derecho. Recurse.

---

## Solución 1 — Recursiva con slicing

```python
class Solution:
    def buildTree(self, preorder, inorder):
        if not preorder or not inorder:
            return None
        root = TreeNode(preorder[0])
        mid = inorder.index(preorder[0])
        root.left = self.buildTree(preorder[1:mid+1], inorder[:mid])
        root.right = self.buildTree(preorder[mid+1:], inorder[mid+1:])
        return root
```

**Análisis:** O(n²) por los slices y `inorder.index`.

---

## Solución 2 — Optimizada con hash de inorder

```python
class Solution:
    def buildTree(self, preorder, inorder):
        idx = {v: i for i, v in enumerate(inorder)}
        self.pre_idx = 0

        def build(left, right):
            if left > right: return None
            root_val = preorder[self.pre_idx]
            self.pre_idx += 1
            root = TreeNode(root_val)
            mid = idx[root_val]
            root.left = build(left, mid - 1)
            root.right = build(mid + 1, right)
            return root

        return build(0, len(inorder) - 1)
```

**Análisis:** O(n) tiempo (lookup O(1)), O(n) espacio.

**Veredicto:** [OK] la óptima. La que esperan en entrevista.

---

## Conexiones

- Próximo: [[124-binary-tree-maximum-path-sum]] — Hard del patrón.

## Estado

- [ ] Leído
- [ ] Escrita Solución 2 desde cero
- [ ] Resuelto en LeetCode
