---
title: "LeetCode 110 — Balanced Binary Tree"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/trees, patron/recursion-postorder]
type: nota
status: en-progreso
source: claude-code
aliases: [Balanced Binary Tree, LC 110, isBalanced, Árbol balanceado]
problem_id: 110
difficulty: easy
patron: trees
neetcode_order: 4
---

# LeetCode 110 — Balanced Binary Tree

> **Cuarto problema del patrón Trees**. Truco clave: **devolver dos cosas a la vez** desde la recursión (altura + es_balanceado), o usar un valor "centinela" como -1.

## Enunciado

Un árbol binario está **balanceado** si para cada nodo, las alturas de los subárboles izquierdo y derecho **difieren en como mucho 1**.

Devuelve `True` si el árbol está balanceado.

**Ejemplo:**
```
Balanceado:        3                NO balanceado:    1
                 /   \                                /
                9    20                              2
                    /  \                            /
                   15   7                          3
```

---

## Solución — Recursión devolviendo altura, -1 si desbalanceado (la canónica)

**Idea**: la recursión devuelve la altura del subárbol. Si en algún momento detecta desbalance, devuelve `-1` como señal. El padre propaga `-1`.

```python
class Solution:
    def isBalanced(self, root: Optional[TreeNode]) -> bool:
        def height(node):
            if not node:
                return 0
            left = height(node.left)
            if left == -1: return -1
            right = height(node.right)
            if right == -1: return -1
            if abs(left - right) > 1:
                return -1
            return 1 + max(left, right)

        return height(root) != -1
```

**Análisis:**
- **Tiempo: O(n)** — single pass, las "early returns" lo mantienen lineal.
- **Espacio: O(h)**.
- **Veredicto:** [OK] la canónica.

### Truco "valor centinela"

`-1` no es una altura válida (todas las alturas son ≥ 0). Eso lo convierte en un **flag de error** que se propaga hacia arriba. Limpio y eficiente.

### Variante: tupla `(height, is_balanced)`

```python
def height(node):
    if not node: return (0, True)
    lh, lb = height(node.left)
    rh, rb = height(node.right)
    balanced = lb and rb and abs(lh - rh) <= 1
    return (1 + max(lh, rh), balanced)
```

Más explícita, pero **devolver -1 es más conciso**.

---

## Auto-test

1. Escribe la solución desde cero.
2. Justifica por qué `-1` funciona como señal de desbalance.
3. Trace mental con un árbol balanceado y otro desbalanceado.

## Conexiones

- [[104-maximum-depth-of-binary-tree]] — la altura básica.
- Próximo: [[100-same-tree]].

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Resuelto en LeetCode
