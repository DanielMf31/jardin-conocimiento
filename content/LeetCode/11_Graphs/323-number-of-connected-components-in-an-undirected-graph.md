---
title: "LeetCode 323 — Number of Connected Components in an Undirected Graph"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/union-find, patron/connected-components]
type: nota
status: en-progreso
source: claude-code
aliases: [Number Connected Components, LC 323, countComponents]
problem_id: 323
difficulty: medium
patron: graphs
neetcode_order: 11
---

# LeetCode 323 — Number of Connected Components in an Undirected Graph

> 🎯 **Undécimo problema del patrón Graphs**. **Contar componentes conexos**. Dos vías: DFS/BFS sobre el grafo, o Union-Find (más elegante).

## Enunciado

Grafo no dirigido con `n` nodos y aristas `edges`. Devuelve el número de componentes conexos.

---

## Solución 1 — DFS

```python
class Solution:
    def countComponents(self, n, edges):
        from collections import defaultdict
        graph = defaultdict(list)
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)

        visited = set()
        count = 0

        def dfs(node):
            visited.add(node)
            for nb in graph[node]:
                if nb not in visited:
                    dfs(nb)

        for i in range(n):
            if i not in visited:
                count += 1
                dfs(i)
        return count
```

---

## Solución 2 — Union-Find (más elegante)

```python
class Solution:
    def countComponents(self, n, edges):
        parent = list(range(n))
        components = n

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for u, v in edges:
            pu, pv = find(u), find(v)
            if pu != pv:
                parent[pu] = pv
                components -= 1                   # cada union reduce componentes en 1

        return components
```

**Veredicto:** ambas son O(V + E). Union-Find más natural si el problema escala con consultas dinámicas.

---

## Conexiones

- [[200-number-of-islands]] — DFS components.
- [[684-redundant-connection]] — Union-Find básico.
- Próximo: [[261-graph-valid-tree]].

## Estado

- [ ] Leído
- [ ] Implementadas ambas soluciones
- [ ] Resuelto en LeetCode
