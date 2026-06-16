---
title: "LeetCode 261 — Graph Valid Tree"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/graphs, patron/union-find, patron/tree-properties]
type: nota
status: en-progreso
source: claude-code
aliases: [Graph Valid Tree, LC 261, validTree]
problem_id: 261
difficulty: medium
patron: graphs
neetcode_order: 12
---

# LeetCode 261 — Graph Valid Tree

> 🎯 **Duodécimo problema del patrón Graphs**. **¿Es un grafo un árbol?** Definición: un árbol es **conexo** y **sin ciclos**. Equivalente: tiene exactamente `n-1` aristas y es conexo.

## Enunciado

Grafo no dirigido con `n` nodos y aristas. Devuelve `True` si es un árbol válido.

---

## Solución — Union-Find detectando ciclos + check conectividad

```python
class Solution:
    def validTree(self, n, edges):
        if len(edges) != n - 1:
            return False                          # condición necesaria

        parent = list(range(n))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for u, v in edges:
            pu, pv = find(u), find(v)
            if pu == pv:
                return False                      # ciclo!
            parent[pu] = pv

        return True                               # sin ciclos + n-1 aristas → árbol
```

**Análisis:** O(N · α(N)).

### Las dos condiciones

1. **n-1 aristas**: condición **necesaria** para árbol con n nodos.
2. **Sin ciclos**: si hay alguna unión que conecta nodos ya unidos, hay ciclo.

Si ambas se cumplen, es árbol (también garantiza conexión por inducción: n-1 aristas + sin ciclos ⇒ conexo).

---

## Conexiones

- [[684-redundant-connection]] · [[323-number-of-connected-components-in-an-undirected-graph]] — Union-Find.
- Próximo: [[127-word-ladder]] — el Hard del patrón.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
