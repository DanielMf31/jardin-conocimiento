---
title: "LeetCode 371 — Sum of Two Integers"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/bit-manipulation, patron/half-adder]
type: nota
status: en-progreso
source: claude-code
aliases: [Sum of Two Integers, LC 371, getSum]
problem_id: 371
difficulty: medium
patron: bit-manipulation
neetcode_order: 6
---

# LeetCode 371 — Sum of Two Integers

> 🎯 **Sexto problema de Bit Manipulation**. Sumar sin usar `+` ni `-`. **Half-adder de hardware**: XOR para suma sin carry, AND+shift para carry.

## Enunciado

Suma `a + b` sin usar operadores aritméticos. **Familiar para perfil HW**: es exactamente cómo lo hace una ALU.

---

## Solución — Half-adder iterativo

```python
class Solution:
    def getSum(self, a, b):
        mask = 0xFFFFFFFF
        while b & mask:
            carry = ((a & b) << 1) & mask
            a = (a ^ b) & mask
            b = carry
        return a if a <= 0x7FFFFFFF else ~(a ^ mask)
```

**Análisis:** O(1) (32 bits máximo).

### Lógica

- `a ^ b`: suma sin carry.
- `(a & b) << 1`: el carry desplazado.
- Repetir hasta que carry sea 0.

`mask` y la negación final son por el manejo de **negativos en Python** (que tiene ints arbitrarios, no 32-bit).

---

## Conexiones

- Próximo: [[7-reverse-integer]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
