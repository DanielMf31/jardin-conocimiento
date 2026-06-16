---
title: "LeetCode 48 — Rotate Image"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/math, patron/matriz]
type: nota
status: en-progreso
source: claude-code
aliases: [Rotate Image, LC 48, rotate]
problem_id: 48
difficulty: medium
patron: math
neetcode_order: 3
---

# LeetCode 48 — Rotate Image

> 🎯 **Tercer problema de Math & Geometry**. Rotar matriz `n×n` 90° **in-place**. Truco: **transponer + invertir filas**.

## Enunciado

Rota matriz cuadrada 90° en sentido horario, in-place.

---

## Solución — Transponer + reverse de filas

```python
class Solution:
    def rotate(self, matrix):
        n = len(matrix)
        # 1. Transponer (intercambiar matrix[i][j] con matrix[j][i])
        for i in range(n):
            for j in range(i+1, n):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        # 2. Invertir cada fila
        for row in matrix:
            row.reverse()
```

**Análisis:** O(n²) tiempo, O(1) espacio.

### Por qué transpose + reverse rows = rotación 90° horaria

Geometría: transponer es reflejar por la diagonal `\`. Reflejar luego horizontalmente (reverse de filas) = rotación 90° horaria.

---

## Conexiones

- Próximo: [[54-spiral-matrix]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
