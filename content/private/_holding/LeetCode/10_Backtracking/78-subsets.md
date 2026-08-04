---
title: "LeetCode 78 — Subsets"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/backtracking]
type: nota
status: en-progreso
source: claude-code
aliases: [Subsets, LC 78, subsets, Subconjuntos]
problem_id: 78
difficulty: medium
patron: backtracking
neetcode_order: 1
---

# LeetCode 78 — Subsets

> **Primer problema del patrón Backtracking**. **El "Hello World" del backtracking**. La idea: en cada nivel, **decides incluir o no incluir** el elemento actual. 2^n subconjuntos.

## Enunciado

Dado un array de enteros `nums` con elementos únicos, devuelve **todos los subconjuntos** posibles.

**Ejemplo:**
```
Input:  [1,2,3]
Output: [[], [1], [2], [1,2], [3], [1,3], [2,3], [1,2,3]]   (cualquier orden)
```

---

## Solución — Backtracking "incluir / no incluir"

```python
class Solution:
    def subsets(self, nums):
        result = []
        current = []

        def backtrack(i):
            if i == len(nums):
                result.append(current.copy())   # ⭐ COPIA, no la lista en sí
                return
            # Opción 1: NO incluir nums[i]
            backtrack(i + 1)
            # Opción 2: incluir nums[i]
            current.append(nums[i])
            backtrack(i + 1)
            current.pop()                        # deshacer

        backtrack(0)
        return result
```

**Análisis:**
- **Tiempo: O(n · 2^n)** — 2^n subsets, cada uno hasta n elementos para copiar.
- **Espacio: O(n)** — call stack.

### Por qué `current.copy()` y no `current`

`current` es la **misma lista** que se mutará. Sin la copia, todos los items en `result` apuntarían a la misma lista (que al final estaría vacía).

### Patrón "append → recurse → pop"

```python
current.append(x)
backtrack(...)
current.pop()                   # deshacer
```

Esta tríada es el corazón de **todo backtracking**. Memorízala.

---

## Conexiones

- [[22-generate-parentheses]] — primer encuentro con backtracking.
- Próximo: [[39-combination-sum]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
