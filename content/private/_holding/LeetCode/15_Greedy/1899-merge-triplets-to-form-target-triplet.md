---
title: "LeetCode 1899 — Merge Triplets to Form Target Triplet"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/greedy]
type: nota
status: en-progreso
source: claude-code
aliases: [Merge Triplets, LC 1899, mergeTriplets]
problem_id: 1899
difficulty: medium
patron: greedy
neetcode_order: 6
---

# LeetCode 1899 — Merge Triplets to Form Target Triplet

> **Sexto problema de Greedy**. Combinar triplets via `max` componente a componente para formar `target`. Greedy: descartar triplets que **excedan** target en cualquier componente.

## Enunciado

Triplets `[a,b,c]`. Operación: combinar dos triplets → componente-wise max. ¿Se puede llegar a `target`?

---

## Solución — Greedy

```python
class Solution:
    def mergeTriplets(self, triplets, target):
        good = [False] * 3                        # ¿hemos visto target[i]?
        for a, b, c in triplets:
            if a <= target[0] and b <= target[1] and c <= target[2]:
                if a == target[0]: good[0] = True
                if b == target[1]: good[1] = True
                if c == target[2]: good[2] = True
        return all(good)
```

**Análisis:** O(n).

### Lógica

Solo nos importan triplets que **no exceden** target en ninguna componente (los que sí exceden, contaminarían el resultado al hacer max). De los buenos, basta con que **entre todos** cubran `target[0]`, `target[1]`, `target[2]` exactamente.

---

## Conexiones

- Próximo: [[763-partition-labels]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
