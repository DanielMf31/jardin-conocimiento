---
title: "LeetCode 7 — Reverse Integer"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/bit-manipulation, patron/overflow]
type: nota
status: en-progreso
source: claude-code
aliases: [Reverse Integer, LC 7, reverse]
problem_id: 7
difficulty: medium
patron: bit-manipulation
neetcode_order: 7
---

# LeetCode 7 — Reverse Integer

> 🎯 **Séptimo y último problema de Bit Manipulation**. Invertir dígitos de un int 32 bits. La trampa: **detectar overflow** sin usar 64 bits.

## Enunciado

Invierte los dígitos de un signed 32-bit int. Si overflowa el rango [-2^31, 2^31-1], devuelve 0.

---

## Solución — Iterativa con check de overflow

```python
class Solution:
    def reverse(self, x):
        sign = -1 if x < 0 else 1
        x = abs(x)
        result = 0
        while x:
            digit = x % 10
            x //= 10
            result = result * 10 + digit
        result *= sign
        if result < -2**31 or result > 2**31 - 1:
            return 0
        return result
```

**Análisis:** O(log x).

---

## Cierre Bit Manipulation 🎉

| # | Problema | Idea |
|---|---|---|
| 1 | [[136-single-number]] | XOR cancela duplicados |
| 2 | [[191-number-of-1-bits]] | `n & (n-1)` Brian Kernighan |
| 3 | [[338-counting-bits]] | DP con `i >> 1` |
| 4 | [[190-reverse-bits]] | Shift y OR |
| 5 | [[268-missing-number]] | Gauss o XOR |
| 6 | [[371-sum-of-two-integers]] | Half-adder |
| 7 | **Este** | Reverse + check overflow |

> 🎯 **Para tu perfil HW**: esta categoría te resultará la más familiar de todo el NeetCode 150. XOR, máscaras, shifts son lenguaje habitual de firmware.

---

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón Bit Manipulation cerrado** ✅
- [ ] **NEETCODE 150 COMPLETO** 🎉🎉🎉
