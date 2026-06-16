---
title: "LeetCode 763 — Partition Labels"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/greedy, patron/last-occurrence]
type: nota
status: en-progreso
source: claude-code
aliases: [Partition Labels, LC 763, partitionLabels]
problem_id: 763
difficulty: medium
patron: greedy
neetcode_order: 7
---

# LeetCode 763 — Partition Labels

> 🎯 **Séptimo problema de Greedy**. Particionar string tal que cada letra esté en como mucho **una partición**. Greedy: precomputar última posición de cada letra.

## Enunciado

Particiona `s` en el máximo número de pedazos tales que ninguna letra aparezca en más de un pedazo.

---

## Solución — Greedy con last_occurrence

```python
class Solution:
    def partitionLabels(self, s):
        last = {c: i for i, c in enumerate(s)}    # última posición de cada char
        result = []
        start = end = 0
        for i, c in enumerate(s):
            end = max(end, last[c])
            if i == end:
                result.append(end - start + 1)
                start = i + 1
        return result
```

**Análisis:** O(n).

---

## Conexiones

- Próximo: [[678-valid-parenthesis-string]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
