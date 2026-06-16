---
title: "LeetCode 338 — Counting Bits"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/bit-manipulation, patron/dp]
type: nota
status: en-progreso
source: claude-code
aliases: [Counting Bits, LC 338, countBits]
problem_id: 338
difficulty: easy
patron: bit-manipulation
neetcode_order: 3
---

# LeetCode 338 — Counting Bits

> 🎯 **Tercer problema de Bit Manipulation**. Para todo i en [0, n], cuenta bits 1. **DP con bit shift**: `dp[i] = dp[i >> 1] + (i & 1)`.

## Enunciado

Devuelve array donde `result[i]` = popcount(i), para i en [0, n].

---

## Solución — DP

```python
class Solution:
    def countBits(self, n):
        dp = [0] * (n + 1)
        for i in range(1, n + 1):
            dp[i] = dp[i >> 1] + (i & 1)
        return dp
```

**Análisis:** O(n).

### La recurrencia

`i >> 1` es i/2 (deshecha el bit más bajo). `i & 1` es 1 si i impar, 0 si par. Por tanto: bits de i = bits de (i/2) + bit más bajo de i.

---

## Conexiones

- [[191-number-of-1-bits]] — popcount de un solo número.
- Próximo: [[190-reverse-bits]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
