---
title: "LeetCode 40 — Combination Sum II"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/backtracking, patron/skip-duplicados]
type: nota
status: en-progreso
source: claude-code
aliases: [Combination Sum II, LC 40, combinationSum2]
problem_id: 40
difficulty: medium
patron: backtracking
neetcode_order: 5
---

# LeetCode 40 — Combination Sum II

> **Quinto problema del patrón Backtracking**. Como [[39-combination-sum]] **pero NO se permite repetir**, y `candidates` tiene duplicados. Combina el truco de [[90-subsets-ii]] (sort + skip dups) con `i+1` en la recursión.

## Enunciado

Como LC 39 pero cada candidato puede usarse **una sola vez**, y `candidates` puede tener duplicados.

---

## Solución — Sort + skip dups + `i+1` en recursión

```python
class Solution:
    def combinationSum2(self, candidates, target):
        candidates.sort()
        result = []
        current = []

        def backtrack(start, remaining):
            if remaining == 0:
                result.append(current.copy())
                return
            if remaining < 0:
                return
            for i in range(start, len(candidates)):
                if i > start and candidates[i] == candidates[i - 1]:
                    continue                     # skip duplicado
                current.append(candidates[i])
                backtrack(i + 1, remaining - candidates[i])     # ⭐ i+1 (no repetir)
                current.pop()

        backtrack(0, target)
        return result
```

### Combinación de los dos trucos

- **`i+1` en recursión** (de LC 40): no repetir el mismo elemento.
- **`if i > start ...`** (de LC 90): no repetir combinaciones idénticas.

---

## Conexiones

- [[39-combination-sum]] — versión con repetición.
- [[90-subsets-ii]] — patrón skip dups.
- Próximo: [[79-word-search]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
