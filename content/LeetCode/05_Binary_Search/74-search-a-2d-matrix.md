---
title: "LeetCode 74 — Search a 2D Matrix"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/binary-search, patron/matriz-2d]
type: nota
status: en-progreso
source: claude-code
aliases: [Search a 2D Matrix, LC 74, searchMatrix, Buscar en matriz 2D]
problem_id: 74
difficulty: medium
patron: binary-search
neetcode_order: 2
---

# LeetCode 74 — Search a 2D Matrix

> **Segundo problema del patrón Binary Search**. Aplica el binary search clásico a una matriz 2D, con el truco de **tratar la matriz como un array 1D virtual**. Es la introducción al pensamiento "convertir índices entre representaciones".
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Te dan una matriz `m × n` con dos propiedades:
1. **Cada fila está ordenada** de forma creciente (de izquierda a derecha).
2. **El primer elemento de cada fila es mayor que el último de la fila anterior**.

Devuelve `True` si `target` está en la matriz, `False` si no.

> **La segunda propiedad es clave**: significa que si "aplanas" la matriz fila por fila, queda como un array 1D ordenado.

**Ejemplo 1:**
```
Input:  matrix = [[1,  3,  5,  7],
                  [10, 11, 16, 20],
                  [23, 30, 34, 60]]
        target = 3
Output: true
```

**Ejemplo 2:**
```
Input:  matrix = [[1,  3,  5,  7],
                  [10, 11, 16, 20],
                  [23, 30, 34, 60]]
        target = 13
Output: false
```

**Restricciones:**
- `m == matrix.length`, `n == matrix[i].length`.
- `1 <= m, n <= 100`.
- `-10^4 <= matrix[i][j], target <= 10^4`.

**Plantilla:**
```python
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `bool` |
| ¿Cómo está ordenada? | Fila por fila, con primera de cada fila > última de anterior |
| ¿Es un array 1D ordenado disfrazado? | **Sí** — esa es la observación clave |
| ¿Existe LC 240 (parecido)? | Sí, pero distinto: en LC 240 cada fila/columna está ordenada pero no hay relación entre filas → patrón staircase, no binary search |
| Edge case 1 | Matriz 1x1: comparar directamente |
| Edge case 2 | Target menor que matrix[0][0] o mayor que matrix[m-1][n-1] → False |

---

## Solución 1 — Búsqueda lineal O(m·n)

```python
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        for row in matrix:
            for x in row:
                if x == target:
                    return True
        return False
```

**Análisis:** O(m·n). Ignora completamente que está ordenado. [NO] No es lo que el problema espera.

---

## Solución 2 — Dos binary searches (la natural)

Primero binary search **en la primera columna** para encontrar la fila correcta. Luego binary search dentro de esa fila.

```python
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False

        # Paso 1: binary search en la primera columna para localizar la fila
        top, bottom = 0, len(matrix) - 1
        while top <= bottom:
            mid_row = top + (bottom - top) // 2
            if target < matrix[mid_row][0]:
                bottom = mid_row - 1
            elif target > matrix[mid_row][-1]:
                top = mid_row + 1
            else:
                # target podría estar en esta fila
                # Paso 2: binary search dentro de la fila
                left, right = 0, len(matrix[mid_row]) - 1
                while left <= right:
                    mid_col = left + (right - left) // 2
                    if matrix[mid_row][mid_col] == target:
                        return True
                    elif matrix[mid_row][mid_col] < target:
                        left = mid_col + 1
                    else:
                        right = mid_col - 1
                return False

        return False
```

**Análisis:**
- **Tiempo: O(log m + log n)** = O(log(m·n)) — dos binary searches independientes.
- **Espacio: O(1)**.
- **Veredicto:** [OK] correcta, demuestra dos binary searches en serie.

---

## Solución 3 — Binary search 1D virtual (la elegante)

**La idea brillante**: como la matriz aplanada es un array 1D ordenado, hacer **un solo binary search** sobre los índices `0..m·n-1`, convirtiendo cada índice virtual a `(row, col)`.

```python
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        m, n = len(matrix), len(matrix[0])
        left, right = 0, m * n - 1

        while left <= right:
            mid = left + (right - left) // 2
            row, col = divmod(mid, n)              # ⭐ índice 1D → (fila, col)
            value = matrix[row][col]

            if value == target:
                return True
            elif value < target:
                left = mid + 1
            else:
                right = mid - 1

        return False
```

**El truco de la conversión** `divmod(mid, n)`:

```python
# n = 4 (4 columnas)
# mid = 7 → divmod(7, 4) = (1, 3) → matrix[1][3]
# mid = 5 → divmod(5, 4) = (1, 1) → matrix[1][1]
# mid = 0 → divmod(0, 4) = (0, 0) → matrix[0][0]
```

`divmod(mid, n)` es atajo para `(mid // n, mid % n)`. La fila es `mid // n` (cuántas filas completas caben antes), la columna es `mid % n` (la posición dentro de la fila actual).

**Análisis:**
- **Tiempo: O(log(m·n))** — un solo binary search.
- **Espacio: O(1)**.
- **Veredicto:** [OK] **la canónica**. La que demuestra dominio del concepto "matriz como 1D virtual".

**Trace mental con `matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 11`**:

```
m=3, n=4, m*n=12
Inicial: left=0, right=11

Iter 1:
  mid = 0 + (11-0)//2 = 5
  divmod(5, 4) = (1, 1) → matrix[1][1] = 11
  11 == 11 → return True [OK]
```

---

## Solución 4 — Staircase desde top-right (NO óptima aquí, pero útil saberla)

Empezar en la esquina top-right. Si target < actual → izquierda. Si target > actual → abajo.

```python
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        m, n = len(matrix), len(matrix[0])
        row, col = 0, n - 1

        while row < m and col >= 0:
            if matrix[row][col] == target:
                return True
            elif matrix[row][col] < target:
                row += 1
            else:
                col -= 1
        return False
```

**Análisis:**
- **Tiempo: O(m + n)** — peor que log(m·n).
- **Veredicto:** [OK] funciona pero **menos eficiente que la 3** para este problema. Sin embargo, **es la óptima en LC 240** (variante donde cada fila/columna está ordenada pero las filas no están "encadenadas"). En LC 240, log no aplica → staircase es lo mejor.

> **Saber cuándo cada uno**: si las filas están "encadenadas" (LC 74), binary search 1D. Si solo cada fila/columna está ordenada por separado (LC 240), staircase.

---

## El patrón general — "Convertir índice 1D a 2D"

**Cuándo aplicar**:

> Cuando tienes una **matriz 2D que se comporta como 1D ordenado** (filas concatenadas), y quieres aplicar binary search sin tener que hacer dos pasos.

**Plantilla mental**:

```python
def search_1d_in_2d(matrix, target):
    m, n = len(matrix), len(matrix[0])
    left, right = 0, m * n - 1
    while left <= right:
        mid = left + (right - left) // 2
        row, col = divmod(mid, n)
        value = matrix[row][col]
        if value == target:
            return True
        elif value < target:
            left = mid + 1
        else:
            right = mid - 1
    return False
```

**Tres señales** del patrón:

1. Matriz 2D ordenada con relación entre filas (la última de fila i < primera de fila i+1).
2. Quieres O(log(m·n)) en lugar de O(m+n) o O(m·n).
3. Necesitas conversión de índices.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **240. Search a 2D Matrix II** | Filas/columnas ordenadas independientemente → staircase O(m+n) |
| **378. Kth Smallest Element in a Sorted Matrix** | K-ésimo elemento; heap o binary search por valor |
| **378. Kth Smallest in Sorted Matrix** | Binary search sobre el rango de valores |

---

## Conceptos a interiorizar

### `divmod(a, b)`

Devuelve la tupla `(a // b, a % b)`:

```python
divmod(7, 4)             # (1, 3)
divmod(10, 3)            # (3, 1)
divmod(20, 4)            # (5, 0)
```

Útil cuando necesitas cociente y resto a la vez. **Más rápido y más legible** que calcularlos por separado.

### Conversión índice 1D ↔ 2D

```python
# 1D → 2D (con n columnas)
row, col = divmod(idx, n)

# 2D → 1D
idx = row * n + col
```

Patrón que aparece en muchos problemas de matriz.

### Cuándo binary search vs staircase en matrices

| Caso | Mejor | Complejidad |
|---|---|---|
| Filas encadenadas (LC 74) | Binary search 1D | O(log(m·n)) |
| Filas/columnas ordenadas independientes (LC 240) | Staircase top-right | O(m+n) |

---

## Comparación final de las 4 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Búsqueda lineal | O(m·n) | O(1) | [NO] No aprovecha el orden |
| 2. Dos binary searches | O(log m + log n) | O(1) | [OK] Correcta |
| 3. **Binary search 1D virtual** | **O(log(m·n))** | O(1) | [OK] La elegante |
| 4. Staircase top-right | O(m+n) | O(1) | Funciona, óptima en LC 240 |

> **Nota**: O(log m + log n) y O(log(m·n)) son **prácticamente equivalentes** (recordemos que log(a·b) = log(a) + log(b)). Soluciones 2 y 3 son equivalentes en complejidad.

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 3** (binary search 1D) desde cero.
2. Justifica:
   - Por qué `divmod(mid, n)` y no `divmod(mid, m)`.
   - Por qué `m * n - 1` como `right` inicial.
   - Cómo se conserva el orden total al "aplanar" la matriz.
3. Trace mental con `matrix = [[1,3],[5,7]], target = 5`. ¿Qué `mid` se calcula?
4. **Bonus** — implementa la Solución 4 (staircase) y compara con la 3. ¿Cuándo cada una?
5. **Bonus 2** — modifica para devolver `(row, col)` en lugar de bool.

---

## Cosas que te pueden preguntar en entrevista

- **"Diferencia con LC 240?"** → En 74, las filas están "encadenadas" → es 1D virtual. En 240, no hay relación entre filas → staircase.
- **"¿Por qué `mid // n` y no `mid // m`?"** → Porque queremos saber **cuántas filas completas caben antes** de `mid`. Cada fila tiene `n` elementos.
- **"¿Cuál es el peor caso de la Solución 3?"** → Siempre O(log(m·n)), independientemente del input.
- **"¿Y si la matriz no fuera densa (algunas celdas vacías)?"** → El algoritmo no aplica directamente. Necesitarías otra representación.

---

## Conexiones

- [[704-binary-search]] — binary search 1D, base de este problema.
- Próximo: [[875-koko-eating-bananas]] — binary search sobre la respuesta (no sobre un array).

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 3 desde cero
- [ ] Justificada `divmod(mid, n)`
- [ ] Trace mental hecho
- [ ] Implementada Solución 4 y articulada la diferencia
- [ ] Resuelto en LeetCode con éxito
