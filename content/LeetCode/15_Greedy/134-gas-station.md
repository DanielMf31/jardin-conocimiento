---
title: "LeetCode 134 — Gas Station"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/greedy, patron/circular]
type: nota
status: en-progreso
source: claude-code
aliases: [Gas Station, LC 134, canCompleteCircuit]
problem_id: 134
difficulty: medium
patron: greedy
neetcode_order: 4
---

# LeetCode 134 — Gas Station

> 🎯 **Cuarto problema de Greedy**. Estaciones en círculo. Encontrar punto de inicio para completar el circuito. Truco greedy: si te quedas sin gasolina en `i`, **el inicio no puede estar en ningún punto entre el inicio actual e i**.

## Enunciado

Arrays `gas[i]` (gasolina disponible) y `cost[i]` (gasolina para ir a i+1, circular). Devuelve el índice de inicio para completar el circuito, o `-1` si imposible.

---

## Solución — Greedy O(n)

```python
class Solution:
    def canCompleteCircuit(self, gas, cost):
        if sum(gas) < sum(cost): return -1       # imposible

        start = 0
        tank = 0
        for i in range(len(gas)):
            tank += gas[i] - cost[i]
            if tank < 0:
                start = i + 1                    # reiniciar desde después
                tank = 0
        return start
```

**Análisis:** O(n).

### Por qué reiniciar desde `i+1`

Si te quedaste sin gasolina en `i` empezando en `start`, **ningún punto entre `start` e `i` puede ser solución** (porque si fuera, hubieras llegado a `i` con tanque ≥ 0). Reiniciar en `i+1`.

---

## Conexiones

- Próximo: [[846-hand-of-straights]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
