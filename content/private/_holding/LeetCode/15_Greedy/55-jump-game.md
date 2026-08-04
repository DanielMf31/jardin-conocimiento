---
title: "LeetCode 55 — Jump Game"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/greedy]
type: nota
status: en-progreso
source: claude-code
aliases: [Jump Game, LC 55, canJump]
problem_id: 55
difficulty: medium
patron: greedy
neetcode_order: 2
---

# LeetCode 55 — Jump Game

> **Segundo problema de Greedy**. ¿Puedo llegar desde 0 al final con saltos de longitud variable? **Trackear el "máximo alcance" mientras avanzas**.

## Enunciado

Array `nums` donde `nums[i]` es el salto máximo desde i. Empiezas en 0. ¿Puedes llegar al último índice?

---

## Solución — Greedy max reach

```python
class Solution:
    def canJump(self, nums):
        max_reach = 0
        for i, n in enumerate(nums):
            if i > max_reach:
                return False                     # no puedo alcanzar i
            max_reach = max(max_reach, i + n)
        return True
```

**Análisis:** O(n).

---

## Conexiones

- Próximo: [[45-jump-game-ii]] — minimizar número de saltos.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
