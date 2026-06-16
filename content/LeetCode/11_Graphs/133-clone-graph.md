---
title: "LeetCode 133 — Clone Graph"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/dfs, patron/hash-map]
type: nota
status: en-progreso
source: claude-code
aliases: [Clone Graph, LC 133, cloneGraph]
problem_id: 133
difficulty: medium
patron: graphs
neetcode_order: 2
---

# LeetCode 133 — Clone Graph

> 🎯 **Segundo problema del patrón Graphs**. **Deep copy de un grafo** con DFS + hash map. Mismo patrón que [[138-copy-list-with-random-pointer]] pero sobre grafo en lugar de linked list.

## Enunciado

Dado un nodo de un grafo conexo no dirigido, devuelve una **deep copy** del grafo. Cada nodo tiene `val` y `neighbors` (lista de nodos).

---

## Solución — DFS + hash map old → new

```python
class Solution:
    def cloneGraph(self, node):
        if not node: return None
        old_to_new = {}

        def dfs(n):
            if n in old_to_new:
                return old_to_new[n]
            copy = Node(n.val)
            old_to_new[n] = copy
            for nb in n.neighbors:
                copy.neighbors.append(dfs(nb))
            return copy

        return dfs(node)
```

**Análisis:**
- **Tiempo: O(V + E)**.
- **Espacio: O(V)**.

### El truco: `old_to_new` como memoria + detector de ciclos

El mapa hace dos cosas:
1. **Memoria** para no clonar dos veces el mismo nodo.
2. **Detector de ciclos**: si lo visitas otra vez, devuelves el clon ya creado en lugar de bucle infinito.

---

## Conexiones

- [[138-copy-list-with-random-pointer]] — mismo patrón en linked list.
- Próximo: [[695-max-area-of-island]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
