---
title: "LeetCode 54 — Spiral Matrix"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/math, patron/matriz, patron/boundaries]
type: nota
status: en-progreso
source: claude-code
aliases: [Spiral Matrix, LC 54, spiralOrder]
problem_id: 54
difficulty: medium
patron: math
neetcode_order: 4
---

# LeetCode 54 — Spiral Matrix

> **Cuarto problema de Math & Geometry**. Recorrer matriz en espiral. Truco: **4 boundaries** que se contraen.

## Enunciado

Devuelve los elementos de una matriz `m × n` en orden espiral (desde top-left, sentido horario).

---

## Solución — Boundaries

```python
class Solution:
    def spiralOrder(self, matrix):
        result = []
        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1

        while top <= bottom and left <= right:
            # Top row
            for c in range(left, right + 1):
                result.append(matrix[top][c])
            top += 1
            # Right col
            for r in range(top, bottom + 1):
                result.append(matrix[r][right])
            right -= 1
            # Bottom row (si queda)
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    result.append(matrix[bottom][c])
                bottom -= 1
            # Left col (si queda)
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    result.append(matrix[r][left])
                left += 1
        return result
```

**Análisis:** O(m·n).

---

## Conexiones

- Próximo: [[73-set-matrix-zeroes]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
