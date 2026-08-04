---
title: "LeetCode 572 — Subtree of Another Tree"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/trees, patron/recursion]
type: nota
status: en-progreso
source: claude-code
aliases: [Subtree Another Tree, LC 572, isSubtree, Subárbol]
problem_id: 572
difficulty: easy
patron: trees
neetcode_order: 6
---

# LeetCode 572 — Subtree of Another Tree

> **Sexto problema del patrón Trees**. Combina [[100-same-tree]] como sub-rutina con búsqueda recursiva. **Doble recursión**: una para buscar el nodo candidato, otra (`isSameTree`) para verificar.

## Enunciado

Dadas las cabezas de dos árboles `root` y `subRoot`, devuelve `True` si **algún subárbol de `root`** es estructuralmente idéntico a `subRoot`.

---

## Solución — Doble recursión (la canónica)

```python
class Solution:
    def isSubtree(self, root, subRoot):
        if not root: return False
        if self.isSameTree(root, subRoot):
            return True
        return self.isSubtree(root.left, subRoot) or self.isSubtree(root.right, subRoot)

    def isSameTree(self, p, q):
        if not p and not q: return True
        if not p or not q: return False
        if p.val != q.val: return False
        return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)
```

**Análisis:**
- **Tiempo: O(m * n)** — peor caso, m = nodos en root, n = nodos en subRoot.
- **Espacio: O(h)**.
- **Veredicto:** [OK] canónica.

### El patrón "buscar Y verificar"

- `isSubtree`: **busca** un nodo candidato (recorre todo root).
- `isSameTree`: **verifica** estructura exacta cuando encuentra candidato.

Aparece también en LC 28 (Find Substring) y muchos problemas de búsqueda.

---

## Auto-test

1. Escribe desde cero (ambas funciones).
2. Trace mental con un caso simple.

## Conexiones

- [[100-same-tree]] — sub-rutina central.
- Próximo: [[235-lowest-common-ancestor-of-a-bst]].

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
