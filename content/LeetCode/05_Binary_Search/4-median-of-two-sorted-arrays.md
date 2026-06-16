---
title: "LeetCode 4 — Median of Two Sorted Arrays"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/binary-search, patron/particion]
type: nota
status: en-progreso
source: claude-code
aliases: [Median of Two Sorted Arrays, LC 4, findMedianSortedArrays, Mediana dos arrays ordenados]
problem_id: 4
difficulty: hard
patron: binary-search
neetcode_order: 7
---

# LeetCode 4 — Median of Two Sorted Arrays

> 🎯 **Séptimo y último problema del patrón Binary Search — el Hard del patrón** y uno de los problemas **más difíciles conceptualmente** de NeetCode 150. La solución óptima requiere un truco no obvio: **binary search sobre la partición** de los dos arrays. No te frustres si tarda en cuajar — incluso ingenieros experimentados lo encuentran difícil.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dados dos arrays ordenados `nums1` y `nums2` de tamaños `m` y `n`, devuelve la **mediana** de los dos arrays combinados.

**Tu solución debe correr en O(log(min(m, n)))**.

**Ejemplo 1:**
```
Input:  nums1 = [1, 3], nums2 = [2]
Output: 2.0
        Combinado: [1, 2, 3]. Mediana = 2.
```

**Ejemplo 2:**
```
Input:  nums1 = [1, 2], nums2 = [3, 4]
Output: 2.5
        Combinado: [1, 2, 3, 4]. Mediana = (2+3)/2 = 2.5.
```

**Restricciones:**
- `nums1.length == m`, `nums2.length == n`.
- `0 <= m, n <= 1000`.
- `1 <= m + n <= 2000`.
- `-10^6 <= nums1[i], nums2[i] <= 10^6`.

**Plantilla:**
```python
class Solution:
    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `float` |
| ¿Qué es la mediana? | Si total es impar: el del medio. Si es par: promedio de los dos del medio |
| ¿Tengo que reordenar? | NO en la solución óptima — los arrays ya están ordenados |
| ¿Pueden ser de distinto tamaño? | Sí (incluso uno vacío) |
| ¿Cuál es la solución obvia? | Merge los dos arrays → O(m+n). Pero el enunciado pide O(log) |
| ¿Cómo se hace en O(log)? | Binary search sobre la **partición** de uno de los arrays |
| Edge case 1 | Uno de los arrays vacío → mediana es del otro solo |
| Edge case 2 | Total impar vs par — manejo distinto |

> ⚠️ **Avisa**: este problema tiene **muchos casos borde** (arrays vacíos, particiones extremas, total par/impar). La solución óptima es elegante pero **fácil de implementar mal**.

---

## Solución 1 — Merge y devolver mediana O(m+n)

```python
class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        merged = sorted(nums1 + nums2)
        n = len(merged)
        if n % 2 == 1:
            return float(merged[n // 2])
        return (merged[n // 2 - 1] + merged[n // 2]) / 2
```

**Análisis:**
- **Tiempo: O((m+n) log(m+n))** — sort domina.
- **Espacio: O(m+n)**.
- **Veredicto:** funciona pero **NO cumple O(log(min(m,n)))**. Pasa LeetCode pero el entrevistador no lo aceptaría.

---

## Solución 2 — Merge two pointers O(m+n)

```python
class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        merged = []
        i = j = 0
        while i < len(nums1) and j < len(nums2):
            if nums1[i] < nums2[j]:
                merged.append(nums1[i]); i += 1
            else:
                merged.append(nums2[j]); j += 1
        merged += nums1[i:]
        merged += nums2[j:]
        n = len(merged)
        if n % 2 == 1:
            return float(merged[n // 2])
        return (merged[n // 2 - 1] + merged[n // 2]) / 2
```

**Análisis:**
- **Tiempo: O(m+n)** — un solo recorrido.
- **Espacio: O(m+n)**.
- **Veredicto:** mejor que la 1 pero todavía no cumple O(log).

---

## Solución 3 — Binary search sobre la partición (la canónica O(log))

**La idea brillante**: la mediana **divide** los datos en dos mitades de igual tamaño. Si encontramos un punto de **partición** en cada array tal que:

1. La parte izquierda combinada tiene exactamente `(m+n+1) // 2` elementos.
2. **Todos los elementos de la izquierda son ≤ todos los elementos de la derecha**.

...entonces la mediana es:
- Si `m+n` impar: `max(left_part)`.
- Si `m+n` par: `(max(left_part) + min(right_part)) / 2`.

**Binary search sobre dónde partir el array más pequeño** (lo hace O(log(min(m,n)))).

```python
class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        # Asegurar que nums1 sea el más pequeño
        if len(nums1) > len(nums2):
            nums1, nums2 = nums2, nums1

        m, n = len(nums1), len(nums2)
        total = m + n
        half = (total + 1) // 2          # tamaño de la mitad izquierda

        left, right = 0, m
        while left <= right:
            i = (left + right) // 2      # partición en nums1
            j = half - i                  # partición correspondiente en nums2

            # Bordes: usar -inf y inf para casos extremos
            nums1_left  = nums1[i - 1] if i > 0 else float('-inf')
            nums1_right = nums1[i]     if i < m else float('inf')
            nums2_left  = nums2[j - 1] if j > 0 else float('-inf')
            nums2_right = nums2[j]     if j < n else float('inf')

            # ¿Partición correcta?
            if nums1_left <= nums2_right and nums2_left <= nums1_right:
                # Encontramos la partición. Calcular mediana.
                if total % 2 == 1:
                    return float(max(nums1_left, nums2_left))
                return (max(nums1_left, nums2_left) + min(nums1_right, nums2_right)) / 2
            elif nums1_left > nums2_right:
                right = i - 1            # mover partición de nums1 a la izquierda
            else:
                left = i + 1             # mover partición de nums1 a la derecha
```

**Trace mental con `nums1 = [1, 3], nums2 = [2]`** (m=2, n=1, total=3, half=2):

```
nums1 = [1, 3] (no swap)

Iter 1: left=0, right=2
  i = 1, j = 2 - 1 = 1
  nums1_left = nums1[0] = 1
  nums1_right = nums1[1] = 3
  nums2_left = nums2[0] = 2
  nums2_right = nums2[1] = ... fuera de rango → +inf

  ¿1 <= +inf y 2 <= 3? SÍ y SÍ → partición correcta
  total impar (3) → return max(1, 2) = 2.0 ✅
```

**Análisis:**
- **Tiempo: O(log(min(m, n)))** — binary search sobre el array más pequeño.
- **Espacio: O(1)**.
- **Veredicto:** ✅ **la óptima**. La que demuestra dominio del problema.

### Por qué binary search sobre el array más pequeño

Si hicieras binary search sobre el más grande, las particiones podrían ser inválidas (no cumplir `j ≥ 0` y `j ≤ n`). Forzar que `nums1` sea el pequeño garantiza `0 ≤ i ≤ m` y `0 ≤ j = half - i ≤ n`.

### Las particiones extremas con `±inf`

Cuando `i = 0`, no hay elementos a la izquierda en nums1 → `nums1_left = -inf` (cualquier valor del otro array es ≥). Análogamente con `i = m` → `nums1_right = +inf`. Esto evita casos especiales con if's.

---

## El patrón general — "Binary search sobre partición"

**Cuándo aplicar**:

> Cuando dos (o más) estructuras ordenadas necesitan combinarse y buscas un **punto de equilibrio** entre ellas. Binary search sobre dónde partir una de ellas, deduciendo la otra.

**Plantilla mental**:

```python
def particion_binaria(arr1, arr2, target_size):
    if len(arr1) > len(arr2):
        arr1, arr2 = arr2, arr1
    left, right = 0, len(arr1)
    while left <= right:
        i = (left + right) // 2
        j = target_size - i
        if particion_valida(i, j, arr1, arr2):
            return calcular(i, j, arr1, arr2)
        elif arr1_excede(i, j, arr1, arr2):
            right = i - 1
        else:
            left = i + 1
```

**Tres señales** del patrón:

1. Dos colecciones ordenadas que deben combinarse.
2. Buscas un valor que depende de la **combinación**, no de cada una por separado.
3. La fuerza bruta requiere mergear (O(m+n)) y necesitas O(log).

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **295. Find Median from Data Stream** | Mediana en streaming (dos heaps) |
| **378. Kth Smallest Element in a Sorted Matrix** | K-ésimo en matriz ordenada |
| **719. Find K-th Smallest Pair Distance** | K-ésimo de pares con menor distancia (binary search on answer) |

---

## Conceptos a interiorizar

### `float('inf')` y `float('-inf')`

Útil para evitar casos especiales en bordes:

```python
nums1_left = nums1[i - 1] if i > 0 else float('-inf')
nums1_right = nums1[i] if i < m else float('inf')
```

Cualquier número real es `> -inf` y `< +inf`. Esto hace que las comparaciones funcionen sin if's adicionales.

### Tuple swap en una línea

```python
if len(nums1) > len(nums2):
    nums1, nums2 = nums2, nums1            # swap pythonic
```

### `(total + 1) // 2` para "mitad izquierda incluyendo medio si impar"

```python
total = 4 → half = 2 (par)
total = 5 → half = 3 (medio incluido en la izquierda)
```

Esto garantiza que la izquierda contiene el "medio" en arrays de tamaño impar, que es lo que la mediana necesita.

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Merge + sort | O((m+n) log(m+n)) | O(m+n) | ❌ No óptimo |
| 2. Merge two pointers | O(m+n) | O(m+n) | Acepta, no cumple O(log) |
| 3. **Binary search sobre partición** | **O(log(min(m,n)))** | **O(1)** | ✅ La óptima |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** primero (merge two pointers). Es manejable.
2. Escribe la **Solución 3** desde cero. **Date 1+ hora sin frustrarte** — es el problema más difícil de Binary Search.
3. Justifica:
   - Por qué hacer swap si nums1 es el más grande.
   - Por qué `j = half - i` (no calcularlo independientemente).
   - Por qué `±inf` en los bordes.
   - Por qué la condición `nums1_left <= nums2_right and nums2_left <= nums1_right` significa "partición correcta".
4. Trace mental con `nums1 = [1, 2], nums2 = [3, 4]`. ¿Resultado y partición encontrada?
5. **Bonus** — implementa LC 295 (Find Median from Data Stream) — usa dos heaps en lugar de binary search.

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué binary search sobre el más pequeño?"** → Para garantizar que `j = half - i` esté siempre en rango válido `[0, n]`.
- **"Demuestra que la condición de partición correcta es suficiente."** → Si todos en izq son ≤ todos en der **y** los tamaños son los correctos, entonces los `max(left)` y `min(right)` son los elementos del centro del array combinado → mediana.
- **"¿Cómo lo extiendes a 3+ arrays?"** → Mucho más complejo. Una opción: heap k-way merge → O((m+n) log k). Otra: divide-and-conquer recursivo.
- **"¿Y si los arrays no estuvieran ordenados?"** → Tendrías que ordenarlos primero → O(n log n). Pierdes el beneficio del log.

---

## Cierre del patrón Binary Search 🎉

Has llegado al **último problema del quinto patrón del NeetCode 150**. Resumen de los **7 problemas**:

| # | Problema | Variante | Idea distintiva |
|---|---|---|---|
| 1 | [[704-binary-search]] | Clásico | El template básico; cuidado con off-by-one |
| 2 | [[74-search-a-2d-matrix]] | Matriz como 1D virtual | `divmod(mid, n)` para conversión |
| 3 | [[875-koko-eating-bananas]] | Binary search on answer | Buscar k mínimo con función monotónica |
| 4 | [[153-find-minimum-in-rotated-sorted-array]] | Array rotado | Comparar con `nums[right]` |
| 5 | [[33-search-in-rotated-sorted-array]] | Buscar target rotado | "Una mitad ordenada" + 4 ramas |
| 6 | [[981-time-based-key-value-store]] | Diseño + binary search | `bisect_right` para "último ≤ x" |
| 7 | **Este** | Binary search sobre partición | El más difícil; particiones de dos arrays |

**Después de Binary Search**, los siguientes patrones se apoyan en intuición distinta:
- **Linked List** (6) — más mecánico (slow/fast, reverse).
- **Trees** (7) — recursión + BFS (con `deque`).
- **Heap / Priority Queue** (9) — ya viste heap en LC 347.

---

## Conexiones

- [[704-binary-search]] · [[74-search-a-2d-matrix]] · [[875-koko-eating-bananas]] · [[153-find-minimum-in-rotated-sorted-array]] · [[33-search-in-rotated-sorted-array]] · [[981-time-based-key-value-store]] — todos los problemas del patrón.
- [[239-sliding-window-maximum]] — análisis amortizado en algoritmos elegantes.
- [[MOC_NeetCode_150]] — índice general.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 (merge) desde cero
- [ ] Escrita Solución 3 desde cero (esto te llevará tiempo)
- [ ] Justificada cada parte de la condición de partición
- [ ] Trace mental con varios ejemplos (par, impar, uno vacío)
- [ ] Resuelto en LeetCode con éxito
- [ ] **Patrón Binary Search cerrado** ✅
