---
title: "LeetCode 211 — Design Add and Search Words Data Structure"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/tries, patron/dfs, patron/wildcards]
type: nota
status: en-progreso
source: claude-code
aliases: [Add and Search Word, LC 211, WordDictionary]
problem_id: 211
difficulty: medium
patron: tries
neetcode_order: 2
---

# LeetCode 211 — Design Add and Search Words Data Structure

> 🎯 **Segundo problema del patrón Tries**. Extiende [[208-implement-trie-prefix-tree]] con **wildcards**: el carácter `'.'` matchea cualquier letra. La búsqueda se vuelve **DFS** sobre el Trie.

## Enunciado

Diseña una estructura con dos operaciones:
- `addWord(word)` — añade palabra (igual que LC 208).
- `search(word)` — `True` si **alguna** palabra coincide. `'.'` matchea cualquier carácter.

**Ejemplo:**
```
addWord("bad"), addWord("dad"), addWord("mad")
search("pad")    → False
search("bad")    → True
search(".ad")    → True (cualquiera de los 3)
search("b..")    → True (matchea "bad")
```

---

## Solución — Trie + DFS para búsqueda con wildcards

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word):
        node = self.root
        for c in word:
            if c not in node.children:
                node.children[c] = TrieNode()
            node = node.children[c]
        node.is_end = True

    def search(self, word):
        def dfs(i, node):
            if i == len(word):
                return node.is_end
            c = word[i]
            if c == '.':
                # probar TODOS los hijos
                for child in node.children.values():
                    if dfs(i + 1, child):
                        return True
                return False
            else:
                if c not in node.children:
                    return False
                return dfs(i + 1, node.children[c])

        return dfs(0, self.root)
```

**Análisis:**
- **addWord: O(L)**.
- **search:**
  - Sin wildcards: O(L).
  - Con wildcards: hasta O(26^L) peor caso (todos `.`), pero típicamente mucho menos.

### Por qué DFS y no iterativo

El `'.'` requiere **explorar múltiples ramas**. La iteración con un solo puntero no basta — necesitas backtracking implícito (o stack), que recursión + DFS hace natural.

---

## Auto-test

1. Implementa desde cero.
2. Justifica el DFS para `'.'`.
3. Trace mental con `search("..d")` tras añadir `bad`, `dad`, `mad`.

## Conexiones

- [[208-implement-trie-prefix-tree]] — base.
- Próximo: [[212-word-search-ii]] — Hard, busca múltiples palabras en grid.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
