---
title: "LeetCode 90 — Subsets II"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/backtracking, patron/skip-duplicados]
type: nota
status: en-progreso
source: claude-code
aliases: [Subsets II, LC 90, subsetsWithDup]
problem_id: 90
difficulty: medium
patron: backtracking
neetcode_order: 4
---

# LeetCode 90 — Subsets II

> 🎯 **Cuarto problema del patrón Backtracking**. Como [[78-subsets]] **pero el array tiene duplicados**. Truco: **sort primero + saltar duplicados consecutivos**.

## Enunciado

Como [[78-subsets]] pero `nums` puede tener duplicados. Devuelve subsets únicos.

**Ejemplo:**
```
Input:  [1,2,2]
Output: [[], [1], [2], [1,2], [2,2], [1,2,2]]
```

---

## Solución — Sort + skip duplicados

```python
class Solution:
    def subsetsWithDup(self, nums):
        nums.sort()                              # ⭐ ordenar para que duplicados queden contiguos
        result = []
        current = []

        def backtrack(start):
            result.append(current.copy())
            for i in range(start, len(nums)):
                if i > start and nums[i] == nums[i - 1]:
                    continue                     # saltar duplicado
                current.append(nums[i])
                backtrack(i + 1)
                current.pop()

        backtrack(0)
        return result
```

### Por qué `i > start` (no `i > 0`)

Solo saltamos duplicados **dentro del mismo nivel** de recursión. `i > start` indica "no es el primero en este nivel". Saltar con `i > 0` también descartaría duplicados legítimos en niveles más profundos.

Ejemplo: con `[1,2,2]`, queremos generar `[1,2,2]` (dos 2's). Con `i > 0` lo perderíamos.

---

## Conexiones

- [[78-subsets]] — versión sin duplicados.
- [[15-3sum]] — mismo patrón "sort + skip dups".
- Próximo: [[40-combination-sum-ii]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
