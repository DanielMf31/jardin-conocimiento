---
title: "LeetCode 684 — Redundant Connection"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/union-find]
type: nota
status: en-progreso
source: claude-code
aliases: [Redundant Connection, LC 684, findRedundantConnection, Union-Find]
problem_id: 684
difficulty: medium
patron: graphs
neetcode_order: 10
---

# LeetCode 684 — Redundant Connection

> **Décimo problema del patrón Graphs**. Introducción al **Union-Find** (Disjoint Set Union — DSU). Estructura clave para conectividad en grafos.

## Enunciado

Te dan un grafo conexo de `n` nodos con `n` aristas (un árbol con UNA arista extra que crea ciclo). Devuelve la arista que, si se elimina, deja un árbol válido (la que **completó el ciclo**, la última en el input que ya conectaba dos nodos del mismo componente).

---

## Solución — Union-Find

```python
class Solution:
    def findRedundantConnection(self, edges):
        n = len(edges)
        parent = list(range(n + 1))               # 1-indexed
        rank = [1] * (n + 1)

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]    # path compression
                x = parent[x]
            return x

        def union(x, y):
            px, py = find(x), find(y)
            if px == py:
                return False                      # ya están conectados → arista redundante
            if rank[px] < rank[py]:
                px, py = py, px
            parent[py] = px
            rank[px] += rank[py]
            return True

        for u, v in edges:
            if not union(u, v):
                return [u, v]
```

**Análisis:** O(N · α(N)) ≈ O(N) (α es la función inversa de Ackermann, prácticamente constante).

### Union-Find — la idea

- `parent[x]`: el "padre" de x. Si `parent[x] == x`, x es la raíz de su componente.
- `find(x)`: sube hasta la raíz.
- `union(x, y)`: une dos componentes haciendo que una raíz apunte a la otra.

**Path compression** (`parent[x] = parent[parent[x]]`) y **union by rank** son las dos optimizaciones que dan O(α(N)).

---

## Conexiones

- Próximo: [[323-number-of-connected-components-in-an-undirected-graph]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
