---
title: "LeetCode 51 — N-Queens"
date: 2026-05-09
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/backtracking, patron/multiple-constraints]
type: nota
status: en-progreso
source: claude-code
aliases: [N-Queens, LC 51, solveNQueens, Reinas]
problem_id: 51
difficulty: hard
patron: backtracking
neetcode_order: 9
---

# LeetCode 51 — N-Queens

> 🎯 **Noveno y último problema del patrón Backtracking — el Hard**. Problema clásico de IA/algoritmos. Coloca `n` reinas en un tablero `n×n` sin que se ataquen. Combina backtracking + **múltiples constraints simultáneas** (filas, columnas, diagonales).

## Enunciado

Coloca `n` reinas en un tablero `n×n` tal que **ninguna ataque a otra** (filas, columnas, diagonales). Devuelve **todas las disposiciones** únicas, cada una como lista de strings (`'Q'` reina, `'.'` vacío).

**Ejemplo:**
```
Input:  n = 4
Output: [[".Q..","...Q","Q...","..Q."], ["..Q.","Q...","...Q",".Q.."]]
```

---

## Solución — Backtracking con sets de constraints

**Idea**: probar fila por fila, columna a columna. En cada fila, probar cada columna. Si la columna no está bloqueada por una reina anterior (misma columna, diagonal `\`, diagonal `/`), colocar y recurrir.

**Truco**: representar las restricciones con sets:
- `cols`: columnas ocupadas.
- `pos_diag`: diagonales `/` (donde `r + c` es constante).
- `neg_diag`: diagonales `\` (donde `r - c` es constante).

```python
class Solution:
    def solveNQueens(self, n):
        cols = set()
        pos_diag = set()                         # r + c
        neg_diag = set()                         # r - c
        result = []
        board = [["."] * n for _ in range(n)]

        def backtrack(r):
            if r == n:
                result.append(["".join(row) for row in board])
                return
            for c in range(n):
                if c in cols or (r + c) in pos_diag or (r - c) in neg_diag:
                    continue
                cols.add(c); pos_diag.add(r + c); neg_diag.add(r - c)
                board[r][c] = "Q"
                backtrack(r + 1)
                cols.remove(c); pos_diag.remove(r + c); neg_diag.remove(r - c)
                board[r][c] = "."

        backtrack(0)
        return result
```

**Análisis:**
- **Tiempo: O(n!)** — n! disposiciones máximo.
- **Espacio: O(n²)** para el tablero + O(n) para sets.

### Por qué `r + c` y `r - c` representan diagonales

- En una diagonal `/` (sube hacia la derecha), todas las celdas tienen `r + c` igual.
- En una diagonal `\` (baja hacia la derecha), todas tienen `r - c` igual.

Truco aritmético clásico. Memorízalo.

---

## Cierre del patrón Backtracking 🎉

| # | Problema | Idea distintiva |
|---|---|---|
| 1 | [[78-subsets]] | "Incluir / no incluir" |
| 2 | [[39-combination-sum]] | Repetir, índice `i` (no `i+1`) |
| 3 | [[46-permutations]] | `used[]` flag |
| 4 | [[90-subsets-ii]] | Sort + skip dups |
| 5 | [[40-combination-sum-ii]] | `i+1` + skip dups |
| 6 | [[79-word-search]] | DFS en grid + marcar/desmarcar |
| 7 | [[131-palindrome-partitioning]] | Particiones + check palíndromo |
| 8 | [[17-letter-combinations-of-a-phone-number]] | Producto cartesiano |
| 9 | **Este** | Múltiples constraints con sets |

**Próximo patrón**: Graphs (13 problemas).

---

## Conexiones

- [[36-valid-sudoku]] — múltiples constraints (sin recursión, solo validar).
- [[22-generate-parentheses]] — backtracking básico.

## Estado

- [ ] Leído
- [ ] Implementado desde cero
- [ ] Resuelto en LeetCode
- [ ] **Patrón Backtracking cerrado** ✅
