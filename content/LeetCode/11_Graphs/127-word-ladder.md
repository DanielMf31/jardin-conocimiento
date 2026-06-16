---
title: "LeetCode 127 — Word Ladder"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/graphs, patron/bfs, patron/shortest-path]
type: nota
status: en-progreso
source: claude-code
aliases: [Word Ladder, LC 127, ladderLength]
problem_id: 127
difficulty: hard
patron: graphs
neetcode_order: 13
---

# LeetCode 127 — Word Ladder

> 🎯 **Decimotercero y último problema del patrón Graphs — el Hard**. Un grafo **implícito**: las palabras son nodos, conectados si difieren en una letra. **BFS para shortest path** sobre ese grafo.

## Enunciado

Dadas `beginWord`, `endWord` y `wordList`, encuentra la **longitud de la transformación más corta** (cada paso cambia una letra y resulta en palabra de wordList). Devuelve 0 si imposible.

**Ejemplo:**
```
beginWord = "hit", endWord = "cog"
wordList = ["hot","dot","dog","lot","log","cog"]
Output: 5  (hit → hot → dot → dog → cog)
```

---

## Solución — BFS sobre grafo implícito + patrones wildcard

**Truco**: en lugar de comparar cada palabra con cada otra (O(N²·L)), agrupar palabras por **patrones wildcard**:

`"hot"` → patrones `"*ot"`, `"h*t"`, `"ho*"`. Dos palabras conectadas si comparten algún patrón wildcard.

```python
from collections import defaultdict, deque

class Solution:
    def ladderLength(self, beginWord, endWord, wordList):
        if endWord not in wordList:
            return 0

        # Construir mapa pattern → lista de palabras
        L = len(beginWord)
        patterns = defaultdict(list)
        for word in wordList:
            for i in range(L):
                pattern = word[:i] + '*' + word[i+1:]
                patterns[pattern].append(word)

        # BFS
        q = deque([(beginWord, 1)])
        visited = {beginWord}
        while q:
            word, level = q.popleft()
            if word == endWord:
                return level
            for i in range(L):
                pattern = word[:i] + '*' + word[i+1:]
                for nb in patterns[pattern]:
                    if nb not in visited:
                        visited.add(nb)
                        q.append((nb, level + 1))
        return 0
```

**Análisis:** O(N · L²) tiempo (N palabras × L posiciones × L para construir pattern).

### Por qué patterns wildcards

Sin ellos, comparar cada par de palabras letra a letra es O(N² · L). Con patterns, agrupamos palabras conectadas en O(N · L) y consultamos vecinos en O(1) amortizado.

---

## Cierre del patrón Graphs 🎉

| # | Problema | Idea distintiva |
|---|---|---|
| 1 | [[200-number-of-islands]] | DFS en grid + componentes |
| 2 | [[133-clone-graph]] | DFS + hash map para deep copy |
| 3 | [[695-max-area-of-island]] | DFS devuelve área |
| 4 | [[417-pacific-atlantic-water-flow]] | DFS desde bordes (inverso) |
| 5 | [[130-surrounded-regions]] | DFS desde bordes + flip |
| 6 | [[994-rotting-oranges]] | Multi-source BFS con tiempo |
| 7 | [[286-walls-and-gates]] | Multi-source BFS para distancias |
| 8 | [[207-course-schedule]] | DFS con 3 colores o Kahn |
| 9 | [[210-course-schedule-ii]] | Topological sort completo |
| 10 | [[684-redundant-connection]] | Union-Find básico |
| 11 | [[323-number-of-connected-components-in-an-undirected-graph]] | DFS o UF para componentes |
| 12 | [[261-graph-valid-tree]] | UF + check de aristas |
| 13 | **Este** | BFS shortest path sobre grafo implícito |

**Próximo patrón**: Advanced Graphs (6 problemas: Dijkstra, MST, etc.).

---

## Conexiones

- Trees BFS [[102-binary-tree-level-order-traversal]] — base de BFS.
- Próximo: Advanced Graphs.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón Graphs cerrado** ✅
