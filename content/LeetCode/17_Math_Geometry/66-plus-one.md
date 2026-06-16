---
title: "LeetCode 66 — Plus One"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/math]
type: nota
status: en-progreso
source: claude-code
aliases: [Plus One, LC 66, plusOne]
problem_id: 66
difficulty: easy
patron: math
neetcode_order: 2
---

# LeetCode 66 — Plus One

> 🎯 **Segundo problema de Math & Geometry — Easy**. Sumar 1 a un número representado como array de dígitos. Manejo de carry.

## Enunciado

`digits` representa un entero (cabeza = más significativo). Suma 1 y devuelve el array.

---

## Solución — Iterar de derecha a izquierda

```python
class Solution:
    def plusOne(self, digits):
        for i in range(len(digits) - 1, -1, -1):
            if digits[i] < 9:
                digits[i] += 1
                return digits
            digits[i] = 0
        return [1] + digits                       # caso "999" → "1000"
```

**Análisis:** O(n).

---

## Conexiones

- [[2-add-two-numbers]] — patrón carry similar.
- Próximo: [[48-rotate-image]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
