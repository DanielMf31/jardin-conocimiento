---
title: "LeetCode 213 — House Robber II"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-1d, patron/circular]
type: nota
status: en-progreso
source: claude-code
aliases: [House Robber II, LC 213, rob, Robber circular]
problem_id: 213
difficulty: medium
patron: dp-1d
neetcode_order: 4
---

# LeetCode 213 — House Robber II

> 🎯 **Cuarto problema de DP 1-D**. Como [[198-house-robber]] **pero circular** (la primera y última casa son adyacentes). Truco: dos llamadas separadas excluyendo cada extremo.

## Enunciado

Como LC 198 pero las casas están en círculo: la primera y la última son adyacentes.

---

## Solución — Dos pasadas excluyendo los extremos

```python
class Solution:
    def rob(self, nums):
        if len(nums) == 1: return nums[0]

        def rob_linear(houses):
            prev2, prev1 = 0, 0
            for n in houses:
                prev2, prev1 = prev1, max(prev1, prev2 + n)
            return prev1

        # Excluir primera o excluir última
        return max(rob_linear(nums[1:]), rob_linear(nums[:-1]))
```

**Análisis:** O(n).

### El truco

Si robas la primera, **no puedes** robar la última. Y viceversa. Resolver dos LC 198 separados (excluyendo cada extremo) y devolver el mejor.

---

## Conexiones

- [[198-house-robber]] — base.
- Próximo: [[5-longest-palindromic-substring]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
