---
title: "LeetCode 5 — Longest Palindromic Substring"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-1d, patron/expand-around-center]
type: nota
status: en-progreso
source: claude-code
aliases: [Longest Palindromic Substring, LC 5, longestPalindrome]
problem_id: 5
difficulty: medium
patron: dp-1d
neetcode_order: 5
---

# LeetCode 5 — Longest Palindromic Substring

> **Quinto problema de DP 1-D**. **Expand around center** es el approach más elegante: O(n²) tiempo, O(1) espacio. Más rápido que DP en práctica.

## Enunciado

Dado un string `s`, devuelve el substring palindrómico más largo.

---

## Solución — Expand around center

```python
class Solution:
    def longestPalindrome(self, s):
        result = ""

        def expand(left, right):
            while left >= 0 and right < len(s) and s[left] == s[right]:
                left -= 1; right += 1
            return s[left+1:right]

        for i in range(len(s)):
            odd = expand(i, i)                   # centros impares
            even = expand(i, i+1)                # centros pares
            for cand in (odd, even):
                if len(cand) > len(result):
                    result = cand

        return result
```

**Análisis:** O(n²) tiempo, O(1) espacio.

### Por qué dos casos (odd / even)

Palíndromo "aba" tiene centro impar (la b). Palíndromo "abba" tiene centro **par** (entre las dos b's). Hay que probar ambos.

---

## Conexiones

- [[125-valid-palindrome]] — check de palíndromo simple.
- Próximo: [[647-palindromic-substrings]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
