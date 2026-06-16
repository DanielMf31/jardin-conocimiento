---
title: "LeetCode 198 — House Robber"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-1d, patron/take-or-skip]
type: nota
status: en-progreso
source: claude-code
aliases: [House Robber, LC 198, rob, El ladrón]
problem_id: 198
difficulty: medium
patron: dp-1d
neetcode_order: 3
---

# LeetCode 198 — House Robber

> 🎯 **Tercer problema de DP 1-D**. **El patrón "take or skip"**: para cada elemento, decidir si tomarlo (sumar valor pero saltar el siguiente) o no (continuar). Es la base de muchos DP.

## Enunciado

Casas en línea con valor `nums[i]`. Robar dos casas adyacentes activa la alarma. Devuelve el máximo botín.

---

## Solución — DP "take or skip" O(1)

```python
class Solution:
    def rob(self, nums):
        prev2, prev1 = 0, 0
        for num in nums:
            prev2, prev1 = prev1, max(prev1, prev2 + num)
            #                       ^ skip       ^ take + saltar el anterior
        return prev1
```

**Análisis:** O(n) tiempo, O(1) espacio.

### Recurrencia

`dp[i] = max(dp[i-1], dp[i-2] + nums[i])`:
- **Skip** (no robo casa i): heredo lo mejor que tenía hasta `i-1`.
- **Take** (robo casa i): sumo `nums[i]` a lo que tenía dos casas atrás (`dp[i-2]`).

---

## Conexiones

- Próximo: [[213-house-robber-ii]] — versión circular.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
