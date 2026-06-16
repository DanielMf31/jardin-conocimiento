---
title: "LeetCode 208 — Implement Trie (Prefix Tree)"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/tries, patron/diseno-clase]
type: nota
status: en-progreso
source: claude-code
aliases: [Implement Trie, LC 208, Trie, Prefix Tree]
problem_id: 208
difficulty: medium
patron: tries
neetcode_order: 1
---

# LeetCode 208 — Implement Trie (Prefix Tree)

> 🎯 **Primer problema del patrón Tries**. Un **Trie** (árbol de prefijos) es una estructura especializada para strings. Cada nodo tiene un dict de hijos por carácter y un flag `is_end`. Aprende este patrón aquí; los 2 problemas siguientes son extensiones directas.

## Concepto del Trie

Almacena palabras compartiendo prefijos. Para "apple" y "app":

```
        root
         |
         a
         |
         p
         |
         p   ← is_end = True (fin de "app")
         |
         l
         |
         e   ← is_end = True (fin de "apple")
```

## Enunciado

Implementa un Trie con tres operaciones:
- `insert(word)` — añade palabra.
- `search(word)` — devuelve `True` si la palabra exacta está en el Trie.
- `startsWith(prefix)` — devuelve `True` si **algún** palabra del Trie empieza por `prefix`.

---

## Solución — Trie con dict de hijos

```python
class TrieNode:
    def __init__(self):
        self.children = {}              # char -> TrieNode
        self.is_end = False              # marca fin de palabra

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for c in word:
            if c not in node.children:
                node.children[c] = TrieNode()
            node = node.children[c]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, s):
        node = self.root
        for c in s:
            if c not in node.children:
                return None
            node = node.children[c]
        return node
```

**Análisis:**
- **Tiempo: O(L)** por operación (L = longitud de la palabra).
- **Espacio: O(N · L)** donde N = número de palabras.
- **Veredicto:** ✅ canónica.

### `is_end` — la diferencia entre `search` y `startsWith`

Sin `is_end`, no podrías distinguir "app" de "appendage" si solo añadiste "appendage" — el camino "a→p→p" existiría pero no marcaría fin.

---

## Auto-test

1. Implementa Trie + TrieNode desde cero.
2. Justifica el `is_end`.
3. Trace mental: insert("app"), insert("apple"), search("app"), search("appl"), startsWith("app").

## Conexiones

- Próximo: [[211-design-add-and-search-words-data-structure]] — extiende con wildcards.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
