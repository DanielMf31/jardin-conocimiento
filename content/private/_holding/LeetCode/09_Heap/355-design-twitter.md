---
title: "LeetCode 355 — Design Twitter"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/heap, patron/diseno-clase]
type: nota
status: en-progreso
source: claude-code
aliases: [Design Twitter, LC 355, Twitter]
problem_id: 355
difficulty: medium
patron: heap
neetcode_order: 6
---

# LeetCode 355 — Design Twitter

> **Sexto problema del patrón Heap**. **Diseño de sistema en miniatura**. Combina dict + heap. Buena práctica para entrevistas de "design X".

## Enunciado

Diseña una mini-Twitter:
- `postTweet(userId, tweetId)` — usuario publica tweet.
- `getNewsFeed(userId)` — devuelve los **10 tweets más recientes** del usuario y de quienes sigue.
- `follow(followerId, followeeId)` — sigue.
- `unfollow(followerId, followeeId)` — deja de seguir.

---

## Solución — Hash maps + heap para top-10

```python
import heapq
from collections import defaultdict

class Twitter:
    def __init__(self):
        self.time = 0
        self.tweets = defaultdict(list)             # user -> [(time, tweetId)]
        self.follows = defaultdict(set)             # user -> set of followees

    def postTweet(self, userId, tweetId):
        self.tweets[userId].append((self.time, tweetId))
        self.time += 1                              # ⭐ contador monotónico para orden

    def getNewsFeed(self, userId):
        # Recopilar tweets de uno mismo y de quienes sigue
        users = self.follows[userId] | {userId}
        heap = []
        for u in users:
            for t, tid in self.tweets[u]:
                heapq.heappush(heap, (-t, tid))      # max-heap por tiempo
        return [tid for _, tid in [heapq.heappop(heap) for _ in range(min(10, len(heap)))]]

    def follow(self, followerId, followeeId):
        self.follows[followerId].add(followeeId)

    def unfollow(self, followerId, followeeId):
        self.follows[followerId].discard(followeeId)
```

**Análisis:** `getNewsFeed` es O(N log N) donde N = total tweets relevantes. Optimizable con merge de k listas (heap por usuario).

### `time` como contador monotónico

Para ordenar tweets cronológicamente sin timestamps reales, usamos un contador global que crece. Garantiza orden estricto.

---

## Conexiones

- [[155-min-stack]] — diseño de clase.
- Próximo: [[295-find-median-from-data-stream]] — el Hard del patrón.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
