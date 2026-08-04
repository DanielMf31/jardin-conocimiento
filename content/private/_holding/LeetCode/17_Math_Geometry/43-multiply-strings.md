---
title: "LeetCode 43 — Multiply Strings"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/math]
type: nota
status: en-progreso
source: claude-code
aliases: [Multiply Strings, LC 43, multiply]
problem_id: 43
difficulty: medium
patron: math
neetcode_order: 7
---

# LeetCode 43 — Multiply Strings

> **Séptimo problema de Math & Geometry**. Multiplicación a mano de números enormes. Sin convertir a int directamente.

## Enunciado

Dados dos números como strings (no negativos), devuelve su producto como string.

---

## Solución — Multiplicación posicional

```python
class Solution:
    def multiply(self, num1, num2):
        if num1 == "0" or num2 == "0": return "0"
        m, n = len(num1), len(num2)
        result = [0] * (m + n)

        for i in range(m - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                product = int(num1[i]) * int(num2[j])
                p1, p2 = i + j, i + j + 1
                total = product + result[p2]
                result[p2] = total % 10
                result[p1] += total // 10

        # Quitar ceros leading
        i = 0
        while i < len(result) - 1 and result[i] == 0:
            i += 1
        return ''.join(str(d) for d in result[i:])
```

**Análisis:** O(m·n).

---

## Conexiones

- Próximo: [[2013-detect-squares]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
