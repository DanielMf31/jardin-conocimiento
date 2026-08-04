---
title: "LeetCode 102 — Binary Tree Level Order Traversal"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/trees, patron/bfs, patron/deque]
type: nota
status: en-progreso
source: claude-code
aliases: [Level Order, LC 102, levelOrder, Recorrido por niveles]
problem_id: 102
difficulty: medium
patron: trees
neetcode_order: 8
---

# LeetCode 102 — Binary Tree Level Order Traversal

> **Octavo problema del patrón Trees**. **El BFS canónico** sobre árboles binarios. Es la base de LC 199 (Right Side View), LC 1448 (Count Good Nodes), LC 297 (Serialize). Si lo dominas, desbloqueas un montón de problemas.

## Enunciado

Devuelve el recorrido por niveles del árbol (nivel 0, nivel 1, ...) como **lista de listas**.

**Ejemplo:**
```
       3
      / \
     9   20
        /  \
       15   7

Output: [[3], [9, 20], [15, 7]]
```

---

## Solución — BFS con deque, agrupando por nivel (la canónica)

```python
from collections import deque

class Solution:
    def levelOrder(self, root):
        if not root:
            return []

        result = []
        q = deque([root])

        while q:
            level = []
            for _ in range(len(q)):                 # ⭐ snapshot del tamaño
                node = q.popleft()
                level.append(node.val)
                if node.left: q.append(node.left)
                if node.right: q.append(node.right)
            result.append(level)

        return result
```

**Análisis:**
- **Tiempo: O(n)**.
- **Espacio: O(n)** — la queue.
- **Veredicto:** [OK] la canónica.

### Por qué `for _ in range(len(q))` y no `for node in q`

`len(q)` se evalúa **una vez** al inicio del nivel, "fotografiando" cuántos nodos hay en este nivel. Después del bucle interno, q tiene los del siguiente nivel.

Sin esa congelación, un solo while procesaría todos los niveles juntos sin separar.

---

## Auto-test

1. Escribe desde cero.
2. Justifica el `for _ in range(len(q))`.
3. Trace mental con el ejemplo (3 niveles).

## Conexiones

- [[239-sliding-window-maximum]] · [[141-linked-list-cycle]] — primeros encuentros con `deque`.
- Próximo: [[199-binary-tree-right-side-view]] — usa BFS por niveles.
- [[1448-count-good-nodes-in-binary-tree]] — DFS variante.

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
