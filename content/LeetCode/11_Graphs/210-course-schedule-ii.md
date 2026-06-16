---
title: "LeetCode 210 — Course Schedule II"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/topological-sort]
type: nota
status: en-progreso
source: claude-code
aliases: [Course Schedule II, LC 210, findOrder, Topological sort]
problem_id: 210
difficulty: medium
patron: graphs
neetcode_order: 9
---

# LeetCode 210 — Course Schedule II

> 🎯 **Noveno problema del patrón Graphs**. Extensión de [[207-course-schedule]]: en lugar de bool, devolver **el orden en que tomar los cursos**. Es **topological sort** clásico.

## Enunciado

Como LC 207 pero devuelve un **orden válido** de cursos, o `[]` si imposible.

---

## Solución — Kahn's algorithm

```python
from collections import defaultdict, deque

class Solution:
    def findOrder(self, numCourses, prerequisites):
        graph = defaultdict(list)
        in_degree = [0] * numCourses
        for a, b in prerequisites:
            graph[b].append(a)
            in_degree[a] += 1

        q = deque(i for i in range(numCourses) if in_degree[i] == 0)
        order = []
        while q:
            course = q.popleft()
            order.append(course)
            for nb in graph[course]:
                in_degree[nb] -= 1
                if in_degree[nb] == 0:
                    q.append(nb)
        return order if len(order) == numCourses else []
```

**Análisis:** O(V + E).

### Topological sort en una frase

"Procesa los nodos sin prerequisites pendientes; al hacerlo, **decrementa el in-degree de los nodos que dependen de él**; si alguno llega a 0, está listo".

Funciona porque BFS por niveles de in-degree garantiza que un nodo solo se procesa **después de todos sus prerrequisitos**.

---

## Conexiones

- [[207-course-schedule]] — base.
- Próximo: [[684-redundant-connection]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
