---
title: "LeetCode 678 — Valid Parenthesis String"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/greedy, patron/range]
type: nota
status: en-progreso
source: claude-code
aliases: [Valid Parenthesis String, LC 678, checkValidString]
problem_id: 678
difficulty: medium
patron: greedy
neetcode_order: 8
---

# LeetCode 678 — Valid Parenthesis String

> 🎯 **Octavo y último problema de Greedy**. Como [[20-valid-parentheses]] pero con **wildcards `'*'`** (puede ser `(`, `)` o vacío). Greedy: trackear **rango** de posibles open counts.

## Enunciado

`s` con `'('`, `')'` y `'*'`. Devuelve `True` si puede ser válido.

---

## Solución — Track range [low, high] de open count

```python
class Solution:
    def checkValidString(self, s):
        low = high = 0                           # rango de open count posible
        for c in s:
            if c == '(':
                low += 1; high += 1
            elif c == ')':
                low -= 1; high -= 1
            else:                                 # '*'
                low -= 1                          # treat as ')'
                high += 1                         # treat as '('
            if high < 0: return False             # demasiados ')'
            low = max(low, 0)                     # no permitir negativos
        return low == 0
```

**Análisis:** O(n) tiempo, O(1) espacio.

### El truco "rango"

Como `*` puede ser cualquiera, mantenemos el **rango** `[low, high]` de "open counts" posibles tras cada char. Si `high < 0` → ni el mejor caso lo salva. Si al final `low == 0` es alcanzable → válido.

---

## Cierre Greedy 🎉

| # | Problema | Idea distintiva |
|---|---|---|
| 1 | [[53-maximum-subarray]] | Kadane |
| 2 | [[55-jump-game]] | Max reach |
| 3 | [[45-jump-game-ii]] | BFS por niveles implícito |
| 4 | [[134-gas-station]] | Reiniciar desde i+1 |
| 5 | [[846-hand-of-straights]] | Greedy desde menor + Counter |
| 6 | [[1899-merge-triplets-to-form-target-triplet]] | Filtrar triplets válidos |
| 7 | [[763-partition-labels]] | Last occurrence de cada char |
| 8 | **Este** | Track `[low, high]` con wildcards |

---

## Conexiones

- [[121-best-time-to-buy-and-sell-stock]] · [[42-trapping-rain-water]] — patrón one-pass tracking.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón Greedy cerrado** ✅
