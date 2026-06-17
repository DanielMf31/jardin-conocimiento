---
title: "LeetCode 104 — Maximum Depth of Binary Tree"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/trees, patron/recursion-postorder]
type: nota
status: en-progreso
source: claude-code
aliases: [Max Depth Binary Tree, LC 104, maxDepth, Profundidad máxima]
problem_id: 104
difficulty: easy
patron: trees
neetcode_order: 2
---

# LeetCode 104 — Maximum Depth of Binary Tree

> **Segundo problema del patrón Trees**. Otro clásico de recursión donde el truco es **devolver información de los hijos al padre** (postorder). Aprenderlo bien es base para LC 110, 543, 124.

## Enunciado

Dado un árbol binario, devuelve su **profundidad máxima** (número de nodos en el camino más largo desde root hasta una hoja).

**Ejemplo:**
```
       3
      / \
     9   20
        /  \
       15   7

Output: 3
```

---

## Solución 1 — Recursivo (postorder, la canónica)

```python
class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        if not root:
            return 0
        return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))
```

**Análisis:**
- **Tiempo: O(n)**.
- **Espacio: O(h)** — call stack.
- **Veredicto:** [OK] la canónica. Ese `1 + max(left, right)` es el patrón mental que vas a repetir.

### Por qué postorder

"Postorder" = procesar hijos antes que padre. Aquí: necesitas conocer profundidades de left y right ANTES de decidir la del nodo actual.

---

## Solución 2 — BFS contando niveles

```python
from collections import deque
class Solution:
    def maxDepth(self, root):
        if not root: return 0
        q = deque([root])
        depth = 0
        while q:
            depth += 1
            for _ in range(len(q)):
                node = q.popleft()
                if node.left: q.append(node.left)
                if node.right: q.append(node.right)
        return depth
```

**Análisis:** mismo O(n). Útil para entender BFS por niveles.

---

## Auto-test

1. Escribe la Solución 1 desde cero.
2. Trace mental con el ejemplo.
3. Justifica el `1 + max(...)`.

## Conexiones

- [[226-invert-binary-tree]] — recursión simple.
- Próximo: [[543-diameter-of-binary-tree]].

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
