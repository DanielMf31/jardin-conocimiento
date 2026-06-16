---
title: "LeetCode 191 — Number of 1 Bits"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/bit-manipulation]
type: nota
status: en-progreso
source: claude-code
aliases: [Number of 1 Bits, LC 191, hammingWeight, popcount]
problem_id: 191
difficulty: easy
patron: bit-manipulation
neetcode_order: 2
---

# LeetCode 191 — Number of 1 Bits

> 🎯 **Segundo problema de Bit Manipulation**. Cuenta bits 1 en un entero. **Truco Brian Kernighan**: `n & (n-1)` apaga el bit 1 más bajo.

## Enunciado

Cuenta el número de bits 1 en un unsigned int.

---

## Solución — Brian Kernighan

```python
class Solution:
    def hammingWeight(self, n):
        count = 0
        while n:
            n &= n - 1                           # apaga el bit 1 más bajo
            count += 1
        return count
```

**Análisis:** O(k) donde k = número de bits 1 (mejor que O(log n) iterando todos los bits).

### Por qué `n & (n-1)` apaga el bit 1 más bajo

`n-1` invierte todos los bits desde el 1 más bajo hacia abajo. AND con n preserva todo lo demás pero apaga ese bit.

---

## Conexiones

- Próximo: [[338-counting-bits]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
