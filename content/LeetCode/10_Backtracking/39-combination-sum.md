---
title: "LeetCode 39 — Combination Sum"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/backtracking, patron/sin-duplicados]
type: nota
status: en-progreso
source: claude-code
aliases: [Combination Sum, LC 39, combinationSum]
problem_id: 39
difficulty: medium
patron: backtracking
neetcode_order: 2
---

# LeetCode 39 — Combination Sum

> 🎯 **Segundo problema del patrón Backtracking**. **Repetición permitida** del mismo elemento. La trampa: evitar duplicados sin perder combinaciones.

## Enunciado

Dado un array de enteros distintos `candidates` y un `target`, devuelve **todas las combinaciones únicas** que suman `target`. Cada elemento puede usarse **múltiples veces**.

**Ejemplo:**
```
Input:  candidates = [2,3,6,7], target = 7
Output: [[2,2,3], [7]]
```

---

## Solución — Backtracking con índice "from"

**Truco para evitar duplicados**: pasar un índice `start` que marca **desde dónde** considerar candidatos. Esto evita generar `[2,3]` y `[3,2]` por separado.

```python
class Solution:
    def combinationSum(self, candidates, target):
        result = []
        current = []

        def backtrack(start, remaining):
            if remaining == 0:
                result.append(current.copy())
                return
            if remaining < 0:
                return
            for i in range(start, len(candidates)):
                current.append(candidates[i])
                backtrack(i, remaining - candidates[i])    # ⭐ i, no i+1 (repetir permitido)
                current.pop()

        backtrack(0, target)
        return result
```

**Análisis:**
- **Tiempo: O(2^target)** peor caso.

### `backtrack(i, ...)` no `backtrack(i+1, ...)`

Pasar `i` (no `i+1`) permite reutilizar el mismo candidato. Pasar `i+1` lo prohibiría (que sería LC 40).

---

## Conexiones

- [[78-subsets]] — base.
- Próximo: [[46-permutations]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
