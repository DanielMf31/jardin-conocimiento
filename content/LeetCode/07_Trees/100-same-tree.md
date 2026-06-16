---
title: "LeetCode 100 — Same Tree"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/trees, patron/recursion-paralela]
type: nota
status: en-progreso
source: claude-code
aliases: [Same Tree, LC 100, isSameTree, Árboles iguales]
problem_id: 100
difficulty: easy
patron: trees
neetcode_order: 5
---

# LeetCode 100 — Same Tree

> 🎯 **Quinto problema del patrón Trees**. Introduce la **recursión paralela** sobre dos árboles a la vez. Sub-rutina del LC 572 (Subtree of Another Tree).

## Enunciado

Dadas las cabezas de dos árboles binarios `p` y `q`, devuelve `True` si son **estructuralmente idénticos** y todos los nodos correspondientes tienen el mismo valor.

---

## Solución — Recursión paralela (la canónica)

```python
class Solution:
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        if not p and not q:
            return True                          # ambos None → iguales
        if not p or not q:
            return False                         # solo uno None → distintos
        if p.val != q.val:
            return False
        return (self.isSameTree(p.left, q.left)
                and self.isSameTree(p.right, q.right))
```

**Análisis:**
- **Tiempo: O(n)** — visita cada par de nodos una vez.
- **Espacio: O(h)**.
- **Veredicto:** ✅ canónica.

### Los 4 casos

1. Ambos None → iguales.
2. Uno None y el otro no → distintos.
3. Ambos no None pero valores distintos → distintos.
4. Ambos no None con mismo valor → recurse en hijos.

El orden de los if's importa: **chequear None ANTES** de acceder a `.val`.

---

## Auto-test

1. Escribe desde cero.
2. Trace mental con dos árboles iguales y dos distintos.

## Conexiones

- Próximo: [[572-subtree-of-another-tree]] — usa esta función como sub-rutina.

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
