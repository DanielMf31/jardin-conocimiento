---
title: "LeetCode 226 — Invert Binary Tree"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/trees, patron/recursion]
type: nota
status: en-progreso
source: claude-code
aliases: [Invert Binary Tree, LC 226, invertTree, Invertir árbol]
problem_id: 226
difficulty: easy
patron: trees
neetcode_order: 1
---

# LeetCode 226 — Invert Binary Tree

> **Primer problema del patrón Trees**. La introducción más limpia a la **recursión sobre árboles**. Famoso por la anécdota del creador de Homebrew rechazado por Google por no saberlo escribir en una pizarra. Hoy: lo escribes con los ojos cerrados.

## Recordatorio: la estructura `TreeNode`

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

Visualización:

```
        1
       / \
      2   3
     / \   \
    4   5   6
```

## Enunciado

Dada la cabeza (`root`) de un árbol binario, **invierte el árbol** y devuelve la cabeza.

**Invertir** = intercambiar el subárbol izquierdo con el derecho en cada nodo.

**Ejemplo:**
```
Input:        4                Output:       4
            /   \                          /   \
           2     7                        7     2
          / \   / \                      / \   / \
         1   3 6   9                    9   6 3   1
```

---

## Solución 1 — Recursivo (la canónica)

```python
class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        if not root:
            return None
        root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)
        return root
```

**Análisis:**
- **Tiempo: O(n)** — visita cada nodo una vez.
- **Espacio: O(h)** donde h es altura — call stack. Peor caso O(n) (árbol degenerado), promedio O(log n) (balanceado).
- **Veredicto:** [OK] la canónica. **Tres líneas.**

> El truco es el **swap pythonic** `root.left, root.right = root.right, root.left` haciéndolo recursivamente.

---

## Solución 2 — Iterativo con BFS

```python
from collections import deque

class Solution:
    def invertTree(self, root):
        if not root: return None
        q = deque([root])
        while q:
            node = q.popleft()
            node.left, node.right = node.right, node.left
            if node.left: q.append(node.left)
            if node.right: q.append(node.right)
        return root
```

**Análisis:** mismo O(n). Útil saber porque **BFS es la base** de level-order traversal (LC 102) y muchos problemas de árboles.

---

## El patrón general — "Recursión sobre árbol binario"

**Plantilla mental**:

```python
def funcion_arbol(node):
    if not node:
        return base_case
    # 1. trabajo con left
    left_result = funcion_arbol(node.left)
    # 2. trabajo con right
    right_result = funcion_arbol(node.right)
    # 3. combinar
    return combinar(node, left_result, right_result)
```

**El 80% de problemas de árbol siguen esta estructura**. La pregunta es siempre: ¿qué retorno? ¿qué hago en cada nodo?

---

## Auto-test

1. Escribe la Solución 1 desde cero.
2. Identifica los 3 elementos: caso base, llamadas recursivas, combinación.

## Solución en C++ — contraste con Python

> Añadido para ver las diferencias de lenguaje. Recursión sobre árbol con punteros. Código compilable en [`226-invert-binary-tree.cpp`](226-invert-binary-tree.cpp).

```cpp
struct TreeNode { int val; TreeNode* left; TreeNode* right; };

class Solution {
 public:
  TreeNode* invertTree(TreeNode* root) {
    if (root == nullptr) return nullptr;   // caso base
    std::swap(root->left, root->right);    // intercambiar hijos
    invertTree(root->left);                // recursión
    invertTree(root->right);
    return root;
  }
};
```

**Análisis:** Tiempo O(n), Espacio O(h) por la pila de recursión — igual que el Python.

**Diferencias clave Python ↔ C++:**
- Nodo = `TreeNode*`; `root.left` → `root->left`. `None` → `nullptr`.
- `root.left, root.right = root.right, root.left` (tuple swap de Python) → `std::swap(root->left, root->right)` (no hay swap por desempaquetado de tuplas).
- Mismo esqueleto recursivo (caso base + 2 llamadas); la diferencia es semántica de puntero, no el algoritmo.
- Gestión de memoria: aquí los nodos se liberarían con `delete` (o `unique_ptr` en producción); en Python lo hace el GC.

## Conexiones

- [[MOC_NeetCode_150]].
- Próximo: [[104-maximum-depth-of-binary-tree]].

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
