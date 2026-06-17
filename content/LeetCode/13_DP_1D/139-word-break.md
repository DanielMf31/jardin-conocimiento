---
title: "LeetCode 139 — Word Break"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-1d, patron/string-split]
type: nota
status: en-progreso
source: claude-code
aliases: [Word Break, LC 139, wordBreak]
problem_id: 139
difficulty: medium
patron: dp-1d
neetcode_order: 10
---

# LeetCode 139 — Word Break

> **Décimo problema de DP 1-D**. ¿Se puede dividir un string en palabras del diccionario? DP donde `dp[i] = True` si `s[0:i]` se puede particionar.

## Enunciado

Dado un string `s` y una lista `wordDict` de palabras, devuelve `True` si `s` puede segmentarse en una secuencia de palabras del diccionario.

---

## Solución — DP bottom-up

```python
class Solution:
    def wordBreak(self, s, wordDict):
        word_set = set(wordDict)
        dp = [False] * (len(s) + 1)
        dp[0] = True                             # string vacío es válido
        for i in range(1, len(s) + 1):
            for j in range(i):
                if dp[j] and s[j:i] in word_set:
                    dp[i] = True
                    break
        return dp[len(s)]
```

**Análisis:** O(n² · L).

### Recurrencia

`dp[i] = True` si **existe j < i** tal que `dp[j] == True` y `s[j:i]` es una palabra. Equivale a: "puedo descomponer hasta i si existe alguna descomposición previa hasta j que se complete con una palabra del dict".

---

## Conexiones

- Próximo: [[300-longest-increasing-subsequence]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
