---
title: "LeetCode 297 — Serialize and Deserialize Binary Tree"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/trees, patron/serializacion, patron/preorder]
type: nota
status: en-progreso
source: claude-code
aliases: [Serialize Deserialize Tree, LC 297, Codec Tree, Serialización árbol]
problem_id: 297
difficulty: hard
patron: trees
neetcode_order: 15
---

# LeetCode 297 — Serialize and Deserialize Binary Tree

> **Decimoquinto y último problema del patrón Trees — el más completo del bloque**. Combina recursión preorder + parsing + recursión inversa. **Conexión directa con [[271-encode-and-decode-strings]]** (mismo patrón de codec). Cierra el patrón Trees.

## Enunciado

Diseña una clase `Codec` con dos métodos:

- `serialize(root)` → devuelve un string que representa el árbol.
- `deserialize(data)` → reconstruye el árbol desde el string.

**Sin restricciones específicas de formato** — cualquiera que sea reversible.

---

## Idea clave — Preorder con marcador de None

Si serializo solo en preorder, dos árboles distintos pueden producir el mismo string (ambiguous). Para deshacerlo: **marco los None explícitamente**.

```
       1
      / \
     2   3
        / \
       4   5

Preorder con N para None:  "1,2,N,N,3,4,N,N,5,N,N"
```

Con esos N, **el preorder reconstruye el árbol unívocamente**.

---

## Solución — Preorder DFS con N como marcador

```python
class Codec:
    def serialize(self, root):
        def dfs(node):
            if not node:
                vals.append("N")
                return
            vals.append(str(node.val))
            dfs(node.left)
            dfs(node.right)

        vals = []
        dfs(root)
        return ",".join(vals)

    def deserialize(self, data):
        vals = data.split(",")
        self.idx = 0

        def dfs():
            if vals[self.idx] == "N":
                self.idx += 1
                return None
            node = TreeNode(int(vals[self.idx]))
            self.idx += 1
            node.left = dfs()
            node.right = dfs()
            return node

        return dfs()
```

**Análisis:**
- **Tiempo: O(n)** ambos.
- **Espacio: O(n)** por el string + recursión.
- **Veredicto:** [OK] la canónica.

### Por qué preorder funciona y no inorder

En **inorder** sin None markers, dos árboles distintos pueden producir la misma secuencia. En **preorder con N**, **siempre hay un orden único** porque empezamos con la raíz y "consumimos" hijos en orden.

---

## Variantes

### BFS-based (como hace LeetCode internamente para visualizar)

```
Tree → BFS por niveles → "1,2,3,N,N,4,5"
```

Más compacto en algunos casos, requiere queue.

---

## Conexión directa con [[271-encode-and-decode-strings]]

Ambos son **codecs**: serialize/deserialize de una estructura compleja en un string. Aquí el "delimitador" es `,` y el "marcador especial" es `N` para None. La idea de "encode + decode con marcadores" es transferible.

---

## Cierre del patrón Trees

| # | Problema | Idea distintiva |
|---|---|---|
| 1 | [[226-invert-binary-tree]] | Recursión simple |
| 2 | [[104-maximum-depth-of-binary-tree]] | `1 + max(left, right)` |
| 3 | [[543-diameter-of-binary-tree]] | Return + tracker global |
| 4 | [[110-balanced-binary-tree]] | Valor centinela `-1` |
| 5 | [[100-same-tree]] | Recursión paralela 2 árboles |
| 6 | [[572-subtree-of-another-tree]] | Doble recursión (search + verify) |
| 7 | [[235-lowest-common-ancestor-of-a-bst]] | Propiedad BST |
| 8 | [[102-binary-tree-level-order-traversal]] | BFS con `deque` |
| 9 | [[199-binary-tree-right-side-view]] | BFS último de cada nivel |
| 10 | [[1448-count-good-nodes-in-binary-tree]] | DFS con acumulador top-down |
| 11 | [[98-validate-binary-search-tree]] | DFS con bounds top-down |
| 12 | [[230-kth-smallest-element-in-a-bst]] | Inorder iterativo |
| 13 | [[105-construct-binary-tree-from-preorder-and-inorder-traversal]] | Reconstrucción con índices |
| 14 | [[124-binary-tree-maximum-path-sum]] | Generalización de 543 con negativos |
| 15 | **Este** | Serialize/deserialize con preorder + N |

**Próximos**: Tries (3, sencillo), Heap (7), Backtracking (9).

---

## Conexiones

- [[271-encode-and-decode-strings]] — patrón codec.
- [[105-construct-binary-tree-from-preorder-and-inorder-traversal]] — reconstrucción con preorder.

## Estado

- [ ] Leído
- [ ] Escritos serialize y deserialize desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón Trees cerrado** [OK]
