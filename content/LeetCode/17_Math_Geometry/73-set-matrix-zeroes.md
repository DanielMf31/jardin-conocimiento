---
title: "LeetCode 73 — Set Matrix Zeroes"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/math, patron/matriz, patron/in-place]
type: nota
status: en-progreso
source: claude-code
aliases: [Set Matrix Zeroes, LC 73, setZeroes]
problem_id: 73
difficulty: medium
patron: math
neetcode_order: 5
---

# LeetCode 73 — Set Matrix Zeroes

> 🎯 **Quinto problema de Math & Geometry**. Si una celda es 0, poner toda su fila y columna a 0. Truco: **usar la primera fila y columna como markers**.

## Enunciado

Modifica la matriz in-place: si `matrix[i][j] == 0`, poner toda la fila i y columna j a 0.

---

## Solución — First row/col como markers, O(1) espacio

```python
class Solution:
    def setZeroes(self, matrix):
        m, n = len(matrix), len(matrix[0])
        first_row_zero = any(matrix[0][j] == 0 for j in range(n))
        first_col_zero = any(matrix[i][0] == 0 for i in range(m))

        # Marcar
        for i in range(1, m):
            for j in range(1, n):
                if matrix[i][j] == 0:
                    matrix[i][0] = 0
                    matrix[0][j] = 0

        # Aplicar
        for i in range(1, m):
            for j in range(1, n):
                if matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0

        # Primera fila y columna (los markers)
        if first_row_zero:
            for j in range(n): matrix[0][j] = 0
        if first_col_zero:
            for i in range(m): matrix[i][0] = 0
```

**Análisis:** O(m·n) tiempo, O(1) espacio.

---

## Conexiones

- Próximo: [[50-pow-x-n]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
