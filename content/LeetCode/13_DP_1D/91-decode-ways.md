---
title: "LeetCode 91 — Decode Ways"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/dp-1d]
type: nota
status: en-progreso
source: claude-code
aliases: [Decode Ways, LC 91, numDecodings]
problem_id: 91
difficulty: medium
patron: dp-1d
neetcode_order: 7
---

# LeetCode 91 — Decode Ways

> **Séptimo problema de DP 1-D**. Cómo decodificar strings tipo `"12"` que pueden ser `"AB"` (1, 2) o `"L"` (12). DP "Fibonacci con condicional".

## Enunciado

`'A'` = 1, `'B'` = 2, ..., `'Z'` = 26. Dado un string de dígitos, ¿cuántas formas hay de decodificarlo?

**Ejemplo:**
```
"226" → "BBF" (2,2,6), "BZ" (2,26), "VF" (22,6) → 3 formas
```

---

## Solución — DP O(1) espacio

```python
class Solution:
    def numDecodings(self, s):
        if s[0] == '0': return 0
        prev2, prev1 = 1, 1                      # dp[-1], dp[0]
        for i in range(1, len(s)):
            curr = 0
            if s[i] != '0':
                curr += prev1                    # decodificar 1 dígito
            two = int(s[i-1:i+1])
            if 10 <= two <= 26:
                curr += prev2                    # decodificar 2 dígitos
            prev2, prev1 = prev1, curr
        return prev1
```

**Análisis:** O(n).

### Las 2 transiciones

- **1 dígito** (s[i]): si no es '0', heredamos `dp[i-1]`.
- **2 dígitos** (s[i-1:i+1]): si está en 10-26, sumamos `dp[i-2]`.

---

## Conexiones

- Próximo: [[322-coin-change]].

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
