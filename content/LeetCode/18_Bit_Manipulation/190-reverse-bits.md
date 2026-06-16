---
title: "LeetCode 190 — Reverse Bits"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/bit-manipulation]
type: nota
status: en-progreso
source: claude-code
aliases: [Reverse Bits, LC 190, reverseBits]
problem_id: 190
difficulty: easy
patron: bit-manipulation
neetcode_order: 4
---

# LeetCode 190 — Reverse Bits

> 🎯 **Cuarto problema de Bit Manipulation**. Invertir los 32 bits de un entero.

## Enunciado

Invierte los 32 bits de un unsigned int.

---

## Solución — Bit shift

```python
class Solution:
    def reverseBits(self, n):
        result = 0
        for _ in range(32):
            result = (result << 1) | (n & 1)
            n >>= 1
        return result
```

**Análisis:** O(32) = O(1).

### Lógica

En cada iteración: shift result a la izquierda, añadir el bit más bajo de n, shift n a la derecha. 32 veces.

---

## Conexiones

- Próximo: [[268-missing-number]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
