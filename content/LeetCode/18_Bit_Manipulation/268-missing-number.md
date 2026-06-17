---
title: "LeetCode 268 — Missing Number"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/bit-manipulation, patron/xor]
type: nota
status: en-progreso
source: claude-code
aliases: [Missing Number, LC 268, missingNumber]
problem_id: 268
difficulty: easy
patron: bit-manipulation
neetcode_order: 5
---

# LeetCode 268 — Missing Number

> **Quinto problema de Bit Manipulation**. En `[0, n]` falta uno. Tres soluciones: suma de Gauss, XOR, set.

## Enunciado

Array de `n` distintos números en [0, n]. Devuelve el número faltante.

---

## Solución 1 — Suma de Gauss

```python
class Solution:
    def missingNumber(self, nums):
        n = len(nums)
        return n * (n + 1) // 2 - sum(nums)
```

O(n) tiempo, O(1) espacio.

---

## Solución 2 — XOR (alternativa "sin overflow")

```python
class Solution:
    def missingNumber(self, nums):
        result = len(nums)
        for i, n in enumerate(nums):
            result ^= i ^ n
        return result
```

XOR de `[0, n]` con XOR de `nums` cancela todos excepto el faltante.

---

## Conexiones

- [[136-single-number]] — XOR pattern.
- Próximo: [[371-sum-of-two-integers]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
