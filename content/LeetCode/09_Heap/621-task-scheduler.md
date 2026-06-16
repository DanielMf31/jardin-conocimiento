---
title: "LeetCode 621 — Task Scheduler"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/heap, patron/greedy, patron/scheduling]
type: nota
status: en-progreso
source: claude-code
aliases: [Task Scheduler, LC 621, leastInterval]
problem_id: 621
difficulty: medium
patron: heap
neetcode_order: 5
---

# LeetCode 621 — Task Scheduler

> 🎯 **Quinto problema del patrón Heap**. Combina **max-heap + queue de cooldown**. Es un problema de **scheduling clásico** con cooldown entre tareas iguales.

## Enunciado

Dado un array de tareas (caracteres) y `n` (cooldown entre tareas iguales), devuelve el **mínimo número de unidades de tiempo** para completarlas todas. Puedes hacer "idle" cuando no haya tarea válida.

**Ejemplo:**
```
Input:  tasks = ["A","A","A","B","B","B"], n = 2
Output: 8 (A B idle A B idle A B)
```

---

## Solución — Max-heap (frecuencias) + queue cooldown

**Idea**: en cada paso, ejecutar la tarea **más frecuente** disponible. Las que están en cooldown van a una queue con su tiempo de readmisión.

```python
import heapq
from collections import Counter, deque

class Solution:
    def leastInterval(self, tasks, n):
        count = Counter(tasks)
        heap = [-c for c in count.values()]      # max-heap (negado)
        heapq.heapify(heap)
        queue = deque()                          # (count_negado, ready_time)
        time = 0

        while heap or queue:
            time += 1
            if heap:
                c = heapq.heappop(heap) + 1      # ejecutar (cuenta sube hacia 0)
                if c < 0:
                    queue.append((c, time + n))
            if queue and queue[0][1] == time:
                heapq.heappush(heap, queue.popleft()[0])

        return time
```

**Análisis:** O(N · log K) donde N = total tareas, K = tipos únicos.

### Lógica del cooldown

Cuando ejecutas una tarea, si aún quedan instancias, va a la queue con `time + n` como "ready time". Cada paso, si la primera de la queue está lista, vuelve al heap.

---

## Conexiones

- [[347-top-k-frequent-elements]] — Counter + heap.
- Próximo: [[355-design-twitter]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
