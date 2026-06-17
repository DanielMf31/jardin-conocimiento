---
title: "LeetCode 136 — Single Number"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/bit-manipulation, patron/xor]
type: nota
status: en-progreso
source: claude-code
aliases: [Single Number, LC 136, singleNumber]
problem_id: 136
difficulty: easy
patron: bit-manipulation
neetcode_order: 1
---

# LeetCode 136 — Single Number

> **Primer problema de Bit Manipulation — el clásico**. **XOR de todos**: `a ^ a = 0`, `a ^ 0 = a`. Los duplicados se cancelan, queda el único.

## Enunciado

Array donde cada número aparece 2 veces excepto uno. Encuentra el único.

---

## Solución — XOR de todos

```python
class Solution:
    def singleNumber(self, nums):
        result = 0
        for n in nums:
            result ^= n
        return result
```

**Análisis:** O(n) tiempo, O(1) espacio.

### Por qué funciona

`a ^ a = 0` (cualquier número XOR consigo mismo es 0). `a ^ 0 = a`. Aplicado a `[2,2,1]`: `0 ^ 2 ^ 2 ^ 1 = 1`.

---

## Conexiones

- Próximo: [[191-number-of-1-bits]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
