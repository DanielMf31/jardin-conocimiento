---
title: "LeetCode 207 — Course Schedule"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/topological-sort, patron/cycle-detection]
type: nota
status: en-progreso
source: claude-code
aliases: [Course Schedule, LC 207, canFinish, Detección ciclo grafo]
problem_id: 207
difficulty: medium
patron: graphs
neetcode_order: 8
---

# LeetCode 207 — Course Schedule

> **Octavo problema del patrón Graphs**. **Detección de ciclos en un grafo dirigido**. La pregunta de "puedes terminar todos los cursos" se reduce a "¿hay ciclo en el grafo de prerequisites?".

## Enunciado

Hay `numCourses` cursos numerados 0 a numCourses-1. Te dan `prerequisites` donde `[a, b]` significa "necesitas hacer b antes que a".

Devuelve `True` si puedes completar todos los cursos.

---

## Solución 1 — DFS con detección de ciclos (3 estados)

```python
class Solution:
    def canFinish(self, numCourses, prerequisites):
        from collections import defaultdict
        graph = defaultdict(list)
        for a, b in prerequisites:
            graph[a].append(b)

        WHITE, GRAY, BLACK = 0, 1, 2
        color = [WHITE] * numCourses

        def dfs(node):
            if color[node] == GRAY:              # ciclo!
                return False
            if color[node] == BLACK:             # ya procesado, sin ciclo
                return True
            color[node] = GRAY
            for nb in graph[node]:
                if not dfs(nb):
                    return False
            color[node] = BLACK
            return True

        for i in range(numCourses):
            if not dfs(i):
                return False
        return True
```

**Análisis:** O(V + E).

### Los 3 colores

- **WHITE**: no visitado.
- **GRAY**: en camino actual (DFS abierto). **Si lo vuelves a tocar → ciclo**.
- **BLACK**: completamente procesado, sin ciclo aquí.

---

## Solución 2 — Kahn's algorithm (topological sort con BFS)

```python
from collections import defaultdict, deque

class Solution:
    def canFinish(self, numCourses, prerequisites):
        graph = defaultdict(list)
        in_degree = [0] * numCourses
        for a, b in prerequisites:
            graph[b].append(a)
            in_degree[a] += 1

        q = deque(i for i in range(numCourses) if in_degree[i] == 0)
        completed = 0
        while q:
            course = q.popleft()
            completed += 1
            for nb in graph[course]:
                in_degree[nb] -= 1
                if in_degree[nb] == 0:
                    q.append(nb)
        return completed == numCourses
```

**Veredicto:** [OK] alternativa elegante. Si `completed != numCourses`, hay ciclo.

---

## Conexiones

- Próximo: [[210-course-schedule-ii]] — devolver el orden, no solo bool.

## Estado

- [ ] Leído
- [ ] Implementadas ambas soluciones
- [ ] Resuelto en LeetCode
