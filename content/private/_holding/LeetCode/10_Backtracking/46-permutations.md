---
title: "LeetCode 46 — Permutations"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/backtracking, patron/used-flag]
type: nota
status: en-progreso
source: claude-code
aliases: [Permutations, LC 46, permute, Permutaciones]
problem_id: 46
difficulty: medium
patron: backtracking
neetcode_order: 3
---

# LeetCode 46 — Permutations

> **Tercer problema del patrón Backtracking**. **Permutaciones**: importa el orden. Truco: array `used[]` o set para marcar elementos ya elegidos.

## Enunciado

Dado un array de enteros únicos, devuelve **todas las permutaciones** posibles.

**Ejemplo:**
```
Input:  [1,2,3]
Output: [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
```

---

## Solución — Backtracking con `used` flag

```python
class Solution:
    def permute(self, nums):
        result = []
        current = []
        used = [False] * len(nums)

        def backtrack():
            if len(current) == len(nums):
                result.append(current.copy())
                return
            for i in range(len(nums)):
                if used[i]: continue
                used[i] = True
                current.append(nums[i])
                backtrack()
                current.pop()
                used[i] = False

        backtrack()
        return result
```

**Análisis:**
- **Tiempo: O(n · n!)** — n! permutaciones × n para copiar.
- **Espacio: O(n)** call stack.

### Diferencia con [[78-subsets]] y [[39-combination-sum]]

| Problema | Orden importa | Repetir | Trampa |
|---|---|---|---|
| 78 Subsets | NO | NO | índice `start` |
| 39 Combination Sum | NO | SÍ | índice `i` (no `i+1`) |
| 46 Permutations | **SÍ** | NO | `used[]` flag |

---

## Conexiones

- [[78-subsets]] · [[39-combination-sum]] — patrones hermanos.
- Próximo: [[90-subsets-ii]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
