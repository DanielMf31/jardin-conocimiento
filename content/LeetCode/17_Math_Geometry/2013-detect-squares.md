---
title: "LeetCode 2013 — Detect Squares"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/math, patron/diseno-clase]
type: nota
status: en-progreso
source: claude-code
aliases: [Detect Squares, LC 2013, DetectSquares]
problem_id: 2013
difficulty: medium
patron: math
neetcode_order: 8
---

# LeetCode 2013 — Detect Squares

> 🎯 **Octavo y último problema de Math & Geometry**. **Diseño** + cálculo geométrico. Diagonal del cuadrado define los otros 2 vértices.

## Enunciado

Diseña una clase con `add(point)` y `count(point)` (cuántos cuadrados con lados paralelos a los ejes pueden formarse con ese punto + 3 puntos previamente añadidos).

---

## Solución — Counter de puntos + búsqueda por diagonal

```python
from collections import defaultdict

class DetectSquares:
    def __init__(self):
        self.count = defaultdict(int)

    def add(self, point):
        self.count[tuple(point)] += 1

    def count(self, point):
        px, py = point
        total = 0
        for (x, y), c in list(self.count.items()):
            # diagonal: |dx| == |dy| y > 0
            if abs(x - px) != abs(y - py) or x == px:
                continue
            # Otros 2 vértices del cuadrado: (px, y) y (x, py)
            total += c * self.count[(px, y)] * self.count[(x, py)]
        return total
```

**Análisis:** `add` O(1), `count` O(N).

---

## Cierre Math & Geometry 🎉

| # | Problema | Idea |
|---|---|---|
| 1 | [[202-happy-number]] | Cycle detection |
| 2 | [[66-plus-one]] | Carry de derecha a izquierda |
| 3 | [[48-rotate-image]] | Transpose + reverse rows |
| 4 | [[54-spiral-matrix]] | 4 boundaries |
| 5 | [[73-set-matrix-zeroes]] | First row/col como markers |
| 6 | [[50-pow-x-n]] | Fast power O(log n) |
| 7 | [[43-multiply-strings]] | Multiplicación posicional |
| 8 | **Este** | Counter + búsqueda diagonal |

---

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón Math & Geometry cerrado** ✅
