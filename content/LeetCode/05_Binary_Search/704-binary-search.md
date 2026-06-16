---
title: "LeetCode 704 — Binary Search"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/binary-search]
type: nota
status: en-progreso
source: claude-code
aliases: [Binary Search, LC 704, search, Búsqueda binaria]
problem_id: 704
difficulty: easy
patron: binary-search
neetcode_order: 1
---

# LeetCode 704 — Binary Search

> 🎯 **Primer problema del patrón Binary Search** y **el algoritmo más fundamental** que vas a usar. Es la versión "vainilla" — un array ordenado, busca un valor. Lo importante NO es el algoritmo en sí (lo conoces) sino **escribirlo sin off-by-one errors**, que es la trampa más común.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un array `nums` de enteros **ordenado de forma creciente** y un entero `target`, escribe una función para buscar `target` en `nums`.

Si existe, devuelve su **índice**. Si no existe, devuelve `-1`.

**Tu solución debe correr en O(log n)** (eso descarta linear search).

**Ejemplo 1:**
```
Input:  nums = [-1, 0, 3, 5, 9, 12], target = 9
Output: 4
```

**Ejemplo 2:**
```
Input:  nums = [-1, 0, 3, 5, 9, 12], target = 2
Output: -1 (no existe)
```

**Restricciones:**
- `1 <= nums.length <= 10^4`
- `-10^4 < nums[i], target < 10^4`
- Todos los `nums[i]` son **únicos**.
- `nums` está **ordenado en orden creciente**.

**Plantilla:**
```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` — índice o -1 |
| ¿Está ordenado? | **Sí, ascendente** — clave del problema |
| ¿Hay duplicados? | NO — el enunciado garantiza únicos |
| ¿Tiene que ser O(log n)? | **Sí** — el enunciado lo pide explícitamente |
| Edge case 1 | Array de 1 elemento: o coincide o devuelve -1 |
| Edge case 2 | Target menor que min o mayor que max → -1 |

> 💡 **La idea de binary search**: comparar con el medio. Si igual → encontrado. Si target menor → mitad izquierda. Si target mayor → mitad derecha. Cada paso descarta la mitad del espacio.

---

## Solución 1 — Linear search (NO óptima)

```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        for i, num in enumerate(nums):
            if num == target:
                return i
        return -1
```

**Análisis:**
- **Tiempo: O(n)** — viola la restricción de O(log n).
- **Veredicto:** ❌ no cumple la restricción.

---

## Solución 2 — Binary search clásico (la canónica)

```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        left, right = 0, len(nums) - 1
        while left <= right:
            mid = left + (right - left) // 2     # ⭐ evita overflow
            if nums[mid] == target:
                return mid
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return -1
```

**Trace mental con `nums = [-1, 0, 3, 5, 9, 12], target = 9`**:

```
Inicial: left=0, right=5

Iter 1:
  mid = 0 + (5-0)//2 = 2
  nums[2] = 3
  3 < 9 → buscar derecha → left = mid + 1 = 3

Iter 2:
  left=3, right=5
  mid = 3 + (5-3)//2 = 4
  nums[4] = 9
  9 == 9 → return 4 ✅
```

**Análisis:**
- **Tiempo: O(log n)** — cada iteración descarta la mitad.
- **Espacio: O(1)** — dos índices.
- **Veredicto:** ✅ **la canónica**.

### Las 4 trampas del binary search

#### Trampa 1 — `mid = (left + right) // 2` puede causar overflow

En Python no hay overflow porque los ints son arbitrariamente grandes. Pero **en C++/Java sí**, y los entrevistadores lo saben. La forma segura:

```python
mid = left + (right - left) // 2     # ✅ siempre válida
mid = (left + right) // 2            # ⚠️ en Python OK, otros lenguajes overflow
```

Ambas dan el mismo resultado en Python. Usa la primera por hábito.

#### Trampa 2 — `while left <= right` (con `<=`, no `<`)

```python
while left <= right:                 # ✅ correcto: incluye left==right
    ...
```

Si solo queda **un elemento** (left == right), aún hay que comprobarlo. Si pones `<` en lugar de `<=`, te saltas el último elemento.

#### Trampa 3 — `left = mid + 1` y `right = mid - 1` (con el +1/-1)

```python
left = mid + 1                       # ✅ ya sabemos que mid != target
right = mid - 1
```

Si solo hicieras `left = mid` o `right = mid`, podrías entrar en un **bucle infinito** cuando `left == right`. El `+1`/`-1` garantiza que la ventana decrece estrictamente.

#### Trampa 4 — Confundir `<` con `<=` en la comparación

```python
if nums[mid] < target:               # ✅ buscar derecha si mid es menor
    left = mid + 1
```

Si pones `<=`, mueves `left` aunque `nums[mid] == target` — lo que descartaría la respuesta correcta.

---

## Solución 3 — `bisect` module (la pythonic)

Python tiene un módulo nativo `bisect` que implementa binary search:

```python
from bisect import bisect_left

class Solution:
    def search(self, nums: List[int], target: int) -> int:
        i = bisect_left(nums, target)
        if i < len(nums) and nums[i] == target:
            return i
        return -1
```

**Análisis:**
- **Tiempo: O(log n)**.
- **Espacio: O(1)**.
- **Veredicto:** ✅ funciona, pero **NO la uses en entrevista**. El entrevistador quiere ver que escribes binary search, no que conoces `bisect`. Úsalo solo en problemas donde es accesorio (LC 981).

> 📚 **Funciones útiles de `bisect`**:
> - `bisect_left(arr, x)` → índice donde insertar `x` manteniendo orden, ANTES de duplicados.
> - `bisect_right(arr, x)` (alias `bisect`) → índice DESPUÉS de duplicados.
> - `insort_left(arr, x)` → inserta in-place (O(n) por el shift, pero binary search para localizar).

---

## El patrón general — "Binary search clásico"

**Cuándo aplicar**:

> Cuando tienes una colección **ordenada** y buscas un elemento específico (o el primer/último que cumple una condición). La estructura ordenada permite descartar la mitad del espacio en O(1) por iteración → O(log n) total.

**Plantilla mental**:

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

**Tres señales** del patrón:

1. La colección está **ordenada** (o se puede ordenar).
2. Buscas un valor específico o un punto donde cambia una propiedad.
3. La fuerza bruta es O(n) y necesitas O(log n).

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **35. Search Insert Position** | Si no existe, devolver dónde se insertaría |
| **34. Find First and Last Position of Element in Sorted Array** | Primer y último índice de target (lower/upper bound) |
| **278. First Bad Version** | Binary search sobre boolean monotónico |
| **374. Guess Number Higher or Lower** | Binary search interactivo |

---

## Conceptos a interiorizar

### `mid = left + (right - left) // 2` — el patrón seguro

Calcular `mid` como punto medio entre dos índices. La forma segura es restar primero, dividir después. Memorízala.

### `while left <= right` con `+1` / `-1` — las dos invariantes

- **Condición de salida**: `left > right` significa "ventana vacía" (no encontrado).
- **Movimientos**: `left = mid + 1` o `right = mid - 1` garantizan progreso.

Estas dos reglas juntas evitan los off-by-one y bucles infinitos.

### Lower bound vs upper bound (preview)

- **Lower bound**: primera posición donde un valor ≥ target podría insertarse manteniendo orden.
- **Upper bound**: primera posición donde un valor > target podría insertarse.
- Para encontrar **primer** target: lower_bound.
- Para encontrar **último** target: upper_bound - 1.

Lo verás en LC 34 y otros.

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Linear search | O(n) | O(1) | ❌ No cumple restricción |
| 2. **Binary search clásico** | **O(log n)** | O(1) | ✅ La canónica |
| 3. `bisect_left` | O(log n) | O(1) | ✅ Pythonic, no para entrevista |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** desde cero **5 veces** sin equivocarte. Es el algoritmo que **más se asienta con repetición**.
2. Justifica:
   - Por qué `while left <= right` y no `while left < right`.
   - Por qué `left = mid + 1` (no `left = mid`).
   - Por qué `mid = left + (right - left) // 2` (no `(left + right) // 2`).
3. Trace mental con `nums = [1, 3, 5, 7, 9], target = 5`. ¿Cuántas iteraciones?
4. Trace mental con `nums = [1, 3], target = 2`. ¿Por qué devuelve -1?
5. **Bonus** — modifica para devolver `lower_bound` (primer índice ≥ target) en lugar de match exacto.
6. **Bonus 2** — implementa lo mismo pero **recursivamente**.

---

## Cosas que te pueden preguntar en entrevista

- **"Demuestra el O(log n)."** → Cada iteración divide la ventana entre 2. log₂(n) iteraciones máximo.
- **"¿Qué pasa con duplicados?"** → Devuelve **un** índice válido, no garantizado el primero. Para primero/último usar lower/upper bound.
- **"¿Y si el array fuera enorme y no cupiera en memoria?"** → External binary search: usar disk seek con misma idea, pero cada acceso es caro.
- **"¿Por qué es importante `mid = left + (right - left) // 2`?"** → En lenguajes con int de 32 bits, `(left + right)` puede causar overflow si ambos son cercanos a INT_MAX. La fórmula segura no.
- **"¿Cuándo NO usar binary search?"** → Cuando no hay orden o cuando n es pequeño (overhead innecesario).

---

## Solución en C++ — contraste con Python

> 📘 Añadido para ver las diferencias de lenguaje. Código compilable en [`704-binary-search.cpp`](704-binary-search.cpp).

```cpp
class Solution {
 public:
  int search(std::vector<int>& nums, int target) {
    int lo = 0, hi = (int)nums.size() - 1;
    while (lo <= hi) {
      int mid = lo + (hi - lo) / 2;          // evita overflow vs (lo+hi)/2
      if (nums[mid] == target) return mid;
      if (nums[mid] < target) lo = mid + 1;
      else hi = mid - 1;
    }
    return -1;
  }
};
```

**Análisis:** Tiempo O(log n), Espacio O(1) — igual que el Python idiomático.

**Diferencias clave Python ↔ C++:**
- `mid = (lo + hi) // 2` → `lo + (hi - lo) / 2`. En Python los enteros son bignum (no desbordan); en C++ `lo + hi` **puede desbordar `int`**, por eso el idioma `lo + (hi-lo)/2`. Detalle real de C++/sistemas.
- `len(nums)` devuelve `int` en Python; `nums.size()` devuelve `size_t` (sin signo) → castea a `int` antes de restar 1 (si no, `0u - 1` es enorme).
- Hay `std::lower_bound` en `<algorithm>` que hace binary search de la STL; aquí se implementa a mano para ver el patrón.

---

## Conexiones

- [[MOC_NeetCode_150]] — índice general.
- [[167-two-sum-ii-input-array-is-sorted]] — two pointers en array ordenado (alternativa cuando buscas pares).
- Próximo: [[74-search-a-2d-matrix]] — binary search en matriz.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero **5 veces** sin equivocarme
- [ ] Justificadas las 4 trampas (overflow, `<=`, `+1`/`-1`, `<` no `<=`)
- [ ] Trace mental hecho
- [ ] Implementada lower_bound (Bonus)
- [ ] Resuelto en LeetCode con éxito
