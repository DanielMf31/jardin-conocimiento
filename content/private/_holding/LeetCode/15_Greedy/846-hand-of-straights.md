---
title: "LeetCode 846 — Hand of Straights"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/greedy, patron/sorted-counter]
type: nota
status: en-progreso
source: claude-code
aliases: [Hand of Straights, LC 846, isNStraightHand]
problem_id: 846
difficulty: medium
patron: greedy
neetcode_order: 5
---

# LeetCode 846 — Hand of Straights

> **Quinto problema de Greedy**. ¿Se pueden formar grupos consecutivos de tamaño k? Greedy: empezar siempre desde el **menor disponible**.

## Enunciado

Mano de cartas. `groupSize`. ¿Se puede dividir en grupos consecutivos de `groupSize`?

---

## Solución — Counter + min-heap

```python
import heapq
from collections import Counter

class Solution:
    def isNStraightHand(self, hand, groupSize):
        if len(hand) % groupSize != 0: return False
        count = Counter(hand)
        heap = list(count.keys())
        heapq.heapify(heap)

        while heap:
            smallest = heap[0]
            for i in range(groupSize):
                v = smallest + i
                if count[v] == 0: return False
                count[v] -= 1
                if count[v] == 0:
                    if v != heap[0]: return False
                    heapq.heappop(heap)
        return True
```

**Análisis:** O(n log n).

---

## Conexiones

- Próximo: [[1899-merge-triplets-to-form-target-triplet]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
