---
title: "LeetCode 50 — Pow(x, n)"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/math, patron/divide-conquer]
type: nota
status: en-progreso
source: claude-code
aliases: [Pow x n, LC 50, myPow]
problem_id: 50
difficulty: medium
patron: math
neetcode_order: 6
---

# LeetCode 50 — Pow(x, n)

> 🎯 **Sexto problema de Math & Geometry**. **Exponentiation by squaring** (fast power). Reduce O(n) → O(log n).

## Enunciado

Implementa `pow(x, n)` en O(log n).

---

## Solución — Fast power recursivo

```python
class Solution:
    def myPow(self, x, n):
        if n < 0:
            x = 1 / x; n = -n
        result = 1
        while n:
            if n & 1:                            # n impar
                result *= x
            x *= x
            n >>= 1                              # n // 2
        return result
```

**Análisis:** O(log n).

### La idea

`x^n = (x^(n/2))^2 si n par`. Cada iteración cuadra x y divide n entre 2.

---

## Conexiones

- Próximo: [[43-multiply-strings]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
