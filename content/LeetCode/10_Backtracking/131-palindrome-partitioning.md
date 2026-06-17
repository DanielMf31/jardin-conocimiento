---
title: "LeetCode 131 — Palindrome Partitioning"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/backtracking, patron/string-partition]
type: nota
status: en-progreso
source: claude-code
aliases: [Palindrome Partitioning, LC 131, partition]
problem_id: 131
difficulty: medium
patron: backtracking
neetcode_order: 7
---

# LeetCode 131 — Palindrome Partitioning

> **Séptimo problema del patrón Backtracking**. Particionar string en palíndromos. Combina backtracking + check de palíndromo.

## Enunciado

Dado un string `s`, **particiona** `s` de modo que **cada substring** sea un palíndromo. Devuelve **todas las particiones posibles**.

**Ejemplo:**
```
Input:  s = "aab"
Output: [["a","a","b"], ["aa","b"]]
```

---

## Solución — Backtracking probando cortes

```python
class Solution:
    def partition(self, s):
        result = []
        current = []

        def is_palin(left, right):
            while left < right:
                if s[left] != s[right]:
                    return False
                left += 1; right -= 1
            return True

        def backtrack(i):
            if i == len(s):
                result.append(current.copy())
                return
            for j in range(i, len(s)):
                if is_palin(i, j):
                    current.append(s[i:j+1])
                    backtrack(j + 1)
                    current.pop()

        backtrack(0)
        return result
```

**Análisis:** O(n · 2^n) peor caso (cada par "es o no es punto de corte" + check palíndromo).

### El bucle `for j in range(i, len(s))`

Itera sobre **todos los posibles "fines de substring"** desde i. Si `s[i:j+1]` es palíndromo, lo añade y recurre desde `j+1`.

---

## Conexiones

- [[125-valid-palindrome]] — check de palíndromo.
- Próximo: [[17-letter-combinations-of-a-phone-number]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
