---
title: "LeetCode 153 — Find Minimum in Rotated Sorted Array"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/binary-search, patron/array-rotado]
type: nota
status: en-progreso
source: claude-code
aliases: [Find Min Rotated, LC 153, findMin, Mínimo en array rotado]
problem_id: 153
difficulty: medium
patron: binary-search
neetcode_order: 4
---

# LeetCode 153 — Find Minimum in Rotated Sorted Array

> **Cuarto problema del patrón Binary Search**. Introduce el truco de **binary search en arrays rotados**: el array no está completamente ordenado, pero **una mitad siempre lo está**. Aprenderlo aquí te prepara para LC 33 (búsqueda en array rotado) y muchos problemas relacionados.
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Te dan un array `nums` ordenado de forma creciente, **rotado** entre 1 y n veces. Por ejemplo, `[0, 1, 2, 4, 5, 6, 7]` rotado 4 veces queda `[4, 5, 6, 7, 0, 1, 2]`.

Encuentra el **elemento mínimo** del array. Tu solución debe correr en **O(log n)**.

Asume que **todos los elementos son únicos**.

**Ejemplo 1:**
```
Input:  nums = [3, 4, 5, 1, 2]
Output: 1
```

**Ejemplo 2:**
```
Input:  nums = [4, 5, 6, 7, 0, 1, 2]
Output: 0
```

**Ejemplo 3:**
```
Input:  nums = [11, 13, 15, 17]
Output: 11 (no rotado, o rotado n veces que es lo mismo)
```

**Restricciones:**
- `1 <= n <= 5000`
- `-5000 <= nums[i] <= 5000`
- Todos los `nums[i]` son **únicos**.
- `nums` es un array sorted ascendente rotado entre 1 y n veces.

**Plantilla:**
```python
class Solution:
    def findMin(self, nums: List[int]) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` — el valor mínimo (no el índice) |
| ¿Está ordenado? | **Casi**: era ordenado, ahora está rotado |
| ¿Hay duplicados? | NO en este problema (LC 154 sí los permite) |
| ¿Cómo identifico el "punto de rotación"? | El mínimo es el **único elemento donde nums[i] < nums[i-1]** |
| Edge case 1 | Array no rotado (rotado n veces) → min es nums[0] |
| Edge case 2 | Array de 1 elemento → ese elemento |

> **Visualización**: imagina el array como dos secciones ordenadas, donde la primera es "alta" y la segunda es "baja". El mínimo es **el primer elemento de la sección baja**.

```
Original:  [0, 1, 2, 4, 5, 6, 7]
Rotado:    [4, 5, 6, 7, 0, 1, 2]
            └──────┘  └──────┘
            sección   sección
            ALTA      BAJA
                       ↑
                       el mínimo
```

---

## Solución 1 — Linear search O(n) (NO óptima)

```python
class Solution:
    def findMin(self, nums: List[int]) -> int:
        return min(nums)
```

**Análisis:** O(n). Funciona pero ignora la estructura ordenada. [NO] No cumple el follow-up.

---

## Solución 2 — Binary search modificado (la canónica)

**La idea clave**: en cada iteración, comparar `nums[mid]` con `nums[right]`:

- Si `nums[mid] > nums[right]`: el min está **a la derecha** de mid (en la sección baja). Avanzar `left = mid + 1`.
- Si `nums[mid] < nums[right]`: el min está **en mid o a la izquierda** (sección alta termina en mid). `right = mid`.
- (No hay duplicados, así que no hay caso `==`.)

```python
class Solution:
    def findMin(self, nums: List[int]) -> int:
        left, right = 0, len(nums) - 1
        while left < right:
            mid = left + (right - left) // 2
            if nums[mid] > nums[right]:
                left = mid + 1               # min está a la derecha
            else:
                right = mid                   # min está en mid o a la izquierda
        return nums[left]
```

**Trace mental con `nums = [4, 5, 6, 7, 0, 1, 2]`**:

```
Inicial: left=0, right=6

Iter 1: mid=3, nums[3]=7, nums[6]=2
  7 > 2 → min está a la derecha → left = 4

Iter 2: left=4, right=6, mid=5, nums[5]=1, nums[6]=2
  1 < 2 → min está en mid o izq → right = 5

Iter 3: left=4, right=5, mid=4, nums[4]=0, nums[5]=1
  0 < 1 → right = 4

left == right == 4 → exit

Return nums[4] = 0 [OK]
```

**Análisis:**
- **Tiempo: O(log n)** — cada iteración descarta la mitad.
- **Espacio: O(1)**.
- **Veredicto:** [OK] **la canónica**.

### Por qué comparar con `nums[right]` y no con `nums[left]`

Es una decisión sutil pero importante.

**Si comparas con `nums[left]`**:

```python
if nums[mid] > nums[left]:
    # ¿el min está a la izq o derecha?
    # depende: si todo el lado izq está ordenado, min sigue a la derecha
    # PERO si el array NO está rotado, mid > left siempre y min sería left
    # → ambigüedad
```

Hace falta más casuística porque `nums[mid] > nums[left]` puede significar dos cosas distintas.

**Comparar con `nums[right]`** es más limpio:

- Si `nums[mid] > nums[right]`: hay rotación entre mid y right, min está allí. Sin ambigüedad.
- Si `nums[mid] <= nums[right]`: la mitad derecha está ordenada, min está en izq o es mid.

Por eso la convención canónica usa `nums[right]`.

---

## El patrón general — "Binary search en array rotado"

**Cuándo aplicar**:

> Cuando tienes un array que sería ordenado pero ha sufrido alguna transformación (rotación, etc.) y necesitas O(log n) para encontrar algo (mínimo, target específico, etc.).

**Plantilla mental** (encontrar mínimo):

```python
def find_min_rotated(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    return nums[left]
```

**Tres señales** del patrón:

1. El array es "ordenado pero rotado" o tiene una propiedad casi monotónica.
2. La fuerza bruta es O(n) y necesitas O(log n).
3. Comparar `mid` con un extremo (left o right) revela qué mitad descartar.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **154. Find Minimum in Rotated Sorted Array II** | Permite duplicados → manejar caso `nums[mid] == nums[right]` con `right -= 1` |
| **33. Search in Rotated Sorted Array** | Buscar un target específico, no solo el min |
| **81. Search in Rotated Sorted Array II** | LC 33 con duplicados |

> LC 33 (siguiente problema) extiende este al caso "buscar target". La idea de "una mitad siempre está ordenada" es la misma.

---

## Conceptos a interiorizar

### `while left < right` con `right = mid`

Cuando no descartas `mid` (porque podría ser la respuesta), usa `<` y `right = mid`. La salida es cuando `left == right` (un solo candidato).

### Comparar con extremo (left o right) — convención

Para problemas en arrays rotados, **comparar con el extremo del lado donde "podría haber rotación"** evita ambigüedad. Aquí: rotación causa que el segmento izquierdo sea "alto" y el derecho "bajo"; comparar con `right` revela en cuál está el min.

### Sin caso `==` cuando no hay duplicados

Como el enunciado garantiza unicidad, `nums[mid]` y `nums[right]` siempre son distintos. Si hubiera duplicados (LC 154), añadirías:

```python
elif nums[mid] == nums[right]:
    right -= 1                          # decrementar uno: peor caso O(n)
```

Esto degrada a O(n) en el peor caso (todo iguales), pero pasa correctamente.

---

## Comparación final de las 2 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. `min(nums)` | O(n) | O(1) | [NO] No cumple O(log n) |
| 2. **Binary search modificado** | **O(log n)** | O(1) | [OK] La canónica |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** desde cero.
2. Justifica:
   - Por qué comparar con `nums[right]` y no con `nums[left]`.
   - Por qué `right = mid` (no `right = mid - 1`).
   - Por qué `while left < right` (no `<=`).
3. Trace mental con `nums = [3, 4, 5, 1, 2]`. ¿Cuántas iteraciones?
4. Trace mental con `nums = [11, 13, 15, 17]` (no rotado). ¿Funciona también?
5. **Bonus** — extiende a LC 154 (con duplicados). Pista: añade el caso `nums[mid] == nums[right]`.

---

## Cosas que te pueden preguntar en entrevista

- **"Demuestra la corrección."** → Invariante: el min siempre está en la ventana `[left, right]`. Cada paso, comparamos `nums[mid]` con `nums[right]`. Si es mayor, el min no puede estar a la izquierda de mid (esa zona está ordenada en orden no creciente respecto a right) → descarta izq.
- **"¿Por qué no comparar con `nums[0]` (extremo fijo)?"** → Funcionaría pero es menos elegante: tendrías que distinguir caso "no rotado" especialmente.
- **"¿Y si el array no estuviera garantizado de ser sorted-then-rotated?"** → No funciona — necesitas la propiedad de "una mitad ordenada" que la rotación garantiza.
- **"¿Cómo lo extenderías a duplicados (LC 154)?"** → Caso `nums[mid] == nums[right]`: `right -= 1`. Peor caso O(n).

---

## Conexiones

- [[704-binary-search]] — binary search clásico.
- [[875-koko-eating-bananas]] — binary search on answer.
- Próximo: [[33-search-in-rotated-sorted-array]] — extensión: buscar target en array rotado.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Justificada la elección de comparar con `nums[right]`
- [ ] Trace mental con array rotado y no rotado
- [ ] Resuelto en LeetCode con éxito
