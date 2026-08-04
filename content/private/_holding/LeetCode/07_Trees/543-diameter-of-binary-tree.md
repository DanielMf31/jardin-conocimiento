---
title: "LeetCode 543 — Diameter of Binary Tree"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/trees, patron/recursion-global-tracker]
type: nota
status: en-progreso
source: claude-code
aliases: [Diameter Binary Tree, LC 543, diameterOfBinaryTree, Diámetro árbol]
problem_id: 543
difficulty: easy
patron: trees
neetcode_order: 3
---

# LeetCode 543 — Diameter of Binary Tree

> **Tercer problema del patrón Trees**. Introduce el truco **"recursión que devuelve algo PERO actualiza un tracker global"**. Aparece también en LC 124 (path sum), LC 1373 (max BST sum). Aprenderlo aquí lo desbloquea.

## Enunciado

El **diámetro** de un árbol binario es la **longitud del camino más largo entre cualesquiera dos nodos** del árbol. Este camino puede o no pasar por la raíz.

La longitud se mide en **número de aristas** entre los nodos.

**Ejemplo:**
```
       1
      / \
     2   3
    / \
   4   5

Output: 3 (camino 4-2-1-3 o 5-2-1-3, longitud 3 aristas)
```

---

## Solución — Recursión + tracker global (la canónica)

**El truco**: la recursión devuelve la **altura desde un nodo**. Pero internamente, en cada nodo actualizamos un `self.diameter` con la suma de alturas izq + der (que es el "diámetro pasando por este nodo").

```python
class Solution:
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        self.diameter = 0

        def height(node):
            if not node:
                return 0
            left = height(node.left)
            right = height(node.right)
            self.diameter = max(self.diameter, left + right)   # diámetro EN este nodo
            return 1 + max(left, right)                          # altura desde este nodo

        height(root)
        return self.diameter
```

**Análisis:**
- **Tiempo: O(n)**.
- **Espacio: O(h)**.
- **Veredicto:** [OK] la canónica.

### Por qué funciona — separación de "qué retorno" y "qué actualizo"

- **Lo que retorno**: altura desde el nodo (lo que el padre necesita).
- **Lo que actualizo**: el diámetro pasando por este nodo (`left + right`).

El diámetro global es el máximo de "diámetro pasando por X" sobre todos los X. Como visitamos todos los nodos, lo capturamos.

> **Patrón maestro**: cuando un problema pregunta por algo "global" sobre el árbol pero la recursión natural devuelve algo "local", **separa los dos con un tracker**. Vas a usar este patrón en LC 124 y LC 1373.

---

## Auto-test

1. Escribe la solución desde cero.
2. Justifica por qué `left + right` (no `1 + left + right`).
3. **Bonus** — implementa LC 124 (Maximum Path Sum) usando esta misma técnica.

## Conexiones

- [[104-maximum-depth-of-binary-tree]] — la base.
- Próximo: [[110-balanced-binary-tree]].
- [[124-binary-tree-maximum-path-sum]] — extensión Hard del mismo patrón.

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
