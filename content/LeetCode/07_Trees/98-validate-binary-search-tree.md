---
title: "LeetCode 98 — Validate Binary Search Tree"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/trees, patron/bst, patron/bounds-top-down]
type: nota
status: en-progreso
source: claude-code
aliases: [Validate BST, LC 98, isValidBST, Validar BST]
problem_id: 98
difficulty: medium
patron: trees
neetcode_order: 11
---

# LeetCode 98 — Validate Binary Search Tree

> **Undécimo problema del patrón Trees**. Trampa clásica: "es BST si left.val < node.val < right.val". **Eso NO basta** — el BST exige la propiedad sobre TODO el subárbol, no solo los hijos directos. La solución pasa **bounds (lower, upper)** top-down.

## Enunciado

Determina si un árbol binario es un **BST válido**:
- Subárbol izquierdo: todos los valores **estrictamente menores** que el nodo.
- Subárbol derecho: todos los valores **estrictamente mayores**.
- Recursivamente: ambos subárboles también son BSTs.

**Ejemplo no obvio:**
```
       5
      / \
     1   4
        / \
       3   6

Output: false (el 3 está en el subárbol derecho de 5, pero 3 < 5)
```

Notar: 3 < 4 (parent) y 4 > 1 (sibling), parece OK localmente. **Pero 3 < 5** (ancestro), violando la regla global.

---

## Solución — DFS con bounds (la canónica)

**Idea**: cada nodo tiene un **rango válido** `[lower, upper]`. Para el root, `(-inf, +inf)`. Al ir izquierda, el upper se actualiza al valor del padre. Al ir derecha, el lower se actualiza.

```python
class Solution:
    def isValidBST(self, root) -> bool:
        def valid(node, lower, upper):
            if not node: return True
            if not (lower < node.val < upper):
                return False
            return (valid(node.left, lower, node.val)
                    and valid(node.right, node.val, upper))

        return valid(root, float('-inf'), float('inf'))
```

**Análisis:** O(n) tiempo, O(h) espacio.

### Por qué los bounds son top-down

Cada vez que bajas, **estrechas** el rango válido:
- Bajar a la izquierda: nuevo upper es el valor del padre.
- Bajar a la derecha: nuevo lower es el valor del padre.

Esto **propaga la restricción global** hacia abajo.

---

## Variante — In-order traversal

Un BST recorrido **inorder** produce valores en orden creciente. Recorrer inorder y verificar que cada nuevo valor es mayor que el anterior:

```python
def isValidBST(self, root):
    self.prev = float('-inf')
    def inorder(node):
        if not node: return True
        if not inorder(node.left): return False
        if node.val <= self.prev: return False
        self.prev = node.val
        return inorder(node.right)
    return inorder(root)
```

**Veredicto:** mismo O(n). Más elegante conceptualmente. Ambas son aceptables.

---

## Conexiones

- [[235-lowest-common-ancestor-of-a-bst]] — propiedad BST.
- Próximo: [[230-kth-smallest-element-in-a-bst]] — inorder traversal.

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
