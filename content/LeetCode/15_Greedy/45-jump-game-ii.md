---
title: "LeetCode 45 — Jump Game II"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/greedy, patron/bfs-implicit]
type: nota
status: en-progreso
source: claude-code
aliases: [Jump Game II, LC 45, jump]
problem_id: 45
difficulty: medium
patron: greedy
neetcode_order: 3
---

# LeetCode 45 — Jump Game II

> 🎯 **Tercer problema de Greedy**. Como [[55-jump-game]] pero **mínimo número de saltos**. **BFS implícito**: cada salto = un nivel.

## Enunciado

Mismo input que LC 55. Devuelve el **número mínimo de saltos** para llegar al final.

---

## Solución — Greedy "BFS por niveles"

```python
class Solution:
    def jump(self, nums):
        jumps = 0
        curr_end = 0
        farthest = 0
        for i in range(len(nums) - 1):
            farthest = max(farthest, i + nums[i])
            if i == curr_end:                    # final del nivel actual
                jumps += 1
                curr_end = farthest
        return jumps
```

**Análisis:** O(n).

### El truco "niveles BFS"

`curr_end` marca el final del rango alcanzable con `jumps` saltos. Mientras avanzas, actualizas `farthest`. Cuando llegas a `curr_end`, has agotado el nivel → tienes que saltar de nuevo y avanzar `curr_end = farthest`.

---

## Conexiones

- [[55-jump-game]] — base.
- Próximo: [[134-gas-station]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
