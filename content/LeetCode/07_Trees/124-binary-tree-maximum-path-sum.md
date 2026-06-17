---
title: "LeetCode 124 — Binary Tree Maximum Path Sum"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/trees, patron/recursion-global-tracker]
type: nota
status: en-progreso
source: claude-code
aliases: [Max Path Sum, LC 124, maxPathSum, Suma camino máximo]
problem_id: 124
difficulty: hard
patron: trees
neetcode_order: 14
---

# LeetCode 124 — Binary Tree Maximum Path Sum

> **Decimocuarto problema del patrón Trees — primer Hard**. Generalización de [[543-diameter-of-binary-tree]]: la **misma estructura mental** (recursión que devuelve algo + tracker global) pero ahora con valores que pueden ser negativos. Aprenderlo aquí te da el **patrón maestro** de "DP en árbol".

## Enunciado

Un **path** en un árbol es una secuencia de nodos donde cada par adyacente está conectado por una arista. **El path debe pasar por al menos un nodo y NO repite nodos.**

Dado un árbol, devuelve la **suma máxima** de cualquier path.

**Ejemplo:**
```
       -10
       /  \
      9   20
          / \
         15  7

Output: 42 (15 → 20 → 7)
```

**Restricciones:**
- `1 <= n <= 3*10^4`
- `-1000 <= node.val <= 1000` (pueden ser negativos)

---

## Idea clave

Para cada nodo, hay dos cantidades distintas:

1. **Lo que devuelvo a mi padre**: el path que **incluye este nodo y se extiende hacia un solo lado** (porque mi padre podría seguir extendiéndolo). Es `node.val + max(left_gain, right_gain, 0)`.
2. **Lo que registro como candidato global**: el path que **pasa POR este nodo usando ambos lados**. Es `node.val + left_gain + right_gain`.

El truco del **`max(..., 0)`** es: si una rama tiene gain negativo, **mejor no usarla** (suma 0 = ignorarla).

---

## Solución — Recursión + tracker global (la canónica)

```python
class Solution:
    def maxPathSum(self, root) -> int:
        self.best = float('-inf')

        def gain(node):
            if not node: return 0
            left = max(gain(node.left), 0)         # ignorar negativos
            right = max(gain(node.right), 0)
            self.best = max(self.best, node.val + left + right)
            return node.val + max(left, right)

        gain(root)
        return self.best
```

**Análisis:**
- **Tiempo: O(n)**.
- **Espacio: O(h)**.
- **Veredicto:** [OK] la canónica.

### Lo que devuelvo vs lo que actualizo (el truco mental)

| Cantidad | Fórmula | Para qué |
|---|---|---|
| **Return** | `node.val + max(left, right)` | El padre lo extiende, tiene que ser un **path lineal** (un solo lado) |
| **Update best** | `node.val + left + right` | Path interno que cubre ambos lados, **no extensible** |

Misma idea que en [[543-diameter-of-binary-tree]] pero con suma en vez de cuenta y con tratamiento de negativos.

---

## Auto-test

1. Escribe desde cero. **Date 1+ hora** — es Hard.
2. Justifica el `max(..., 0)`.
3. Justifica por qué `return` y `update best` son **distintos**.
4. Trace mental con árbol con todos los valores negativos. ¿Devuelve el menos negativo?

## Conexiones

- [[543-diameter-of-binary-tree]] — versión "fácil" del mismo patrón.
- Próximo: [[297-serialize-and-deserialize-binary-tree]] — el último Hard.

## Estado

- [ ] Leído
- [ ] Escrito desde cero
- [ ] Justificado return vs update
- [ ] Resuelto en LeetCode
