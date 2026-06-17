---
title: "LeetCode 647 — Palindromic Substrings"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-1d, patron/expand-around-center]
type: nota
status: en-progreso
source: claude-code
aliases: [Palindromic Substrings, LC 647, countSubstrings]
problem_id: 647
difficulty: medium
patron: dp-1d
neetcode_order: 6
---

# LeetCode 647 — Palindromic Substrings

> **Sexto problema de DP 1-D**. Variante directa de [[5-longest-palindromic-substring]]: **contar** palíndromos en lugar de devolver el más largo.

## Enunciado

Cuenta cuántos substrings palindrómicos hay (contando duplicados por posición).

---

## Solución — Expand around center contando

```python
class Solution:
    def countSubstrings(self, s):
        count = 0

        def expand(left, right):
            nonlocal count
            while left >= 0 and right < len(s) and s[left] == s[right]:
                count += 1
                left -= 1; right += 1

        for i in range(len(s)):
            expand(i, i)                         # impares
            expand(i, i+1)                       # pares

        return count
```

**Análisis:** O(n²).

---

## Conexiones

- [[5-longest-palindromic-substring]] — base.
- Próximo: [[91-decode-ways]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
