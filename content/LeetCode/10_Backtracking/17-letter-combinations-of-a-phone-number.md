---
title: "LeetCode 17 — Letter Combinations of a Phone Number"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/backtracking, patron/cartesian]
type: nota
status: en-progreso
source: claude-code
aliases: [Letter Combinations Phone, LC 17, letterCombinations]
problem_id: 17
difficulty: medium
patron: backtracking
neetcode_order: 8
---

# LeetCode 17 — Letter Combinations of a Phone Number

> 🎯 **Octavo problema del patrón Backtracking**. **Producto cartesiano** de letras de cada dígito. Backtracking simple (o `itertools.product`).

## Enunciado

Dado un string de dígitos del teclado de un teléfono (2-9), devuelve **todas las combinaciones de letras** que el dígito podría representar.

```
2: abc, 3: def, 4: ghi, 5: jkl, 6: mno, 7: pqrs, 8: tuv, 9: wxyz
```

**Ejemplo:**
```
Input:  "23"
Output: ["ad","ae","af","bd","be","bf","cd","ce","cf"]
```

---

## Solución — Backtracking

```python
class Solution:
    def letterCombinations(self, digits):
        if not digits: return []

        mapping = {'2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
                   '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'}
        result = []

        def backtrack(i, current):
            if i == len(digits):
                result.append(current)
                return
            for c in mapping[digits[i]]:
                backtrack(i + 1, current + c)

        backtrack(0, "")
        return result
```

**Análisis:** O(4^n · n) donde n = longitud de digits, 4 = max letras por dígito (7 y 9).

### Versión one-liner con `itertools.product`

```python
from itertools import product
class Solution:
    def letterCombinations(self, digits):
        if not digits: return []
        mapping = {'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}
        return [''.join(p) for p in product(*(mapping[d] for d in digits))]
```

**Veredicto:** elegante. **No la uses en entrevista** — quieren ver que sabes backtracking.

---

## Conexiones

- [[78-subsets]] — backtracking básico.
- Próximo: [[51-n-queens]] — Hard del patrón.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
