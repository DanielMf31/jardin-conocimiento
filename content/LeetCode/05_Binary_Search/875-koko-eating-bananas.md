---
title: "LeetCode 875 — Koko Eating Bananas"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/binary-search, patron/binary-search-on-answer]
type: nota
status: en-progreso
source: claude-code
aliases: [Koko Eating Bananas, LC 875, minEatingSpeed, Velocidad Koko bananas]
problem_id: 875
difficulty: medium
patron: binary-search
neetcode_order: 3
---

# LeetCode 875 — Koko Eating Bananas

> 🎯 **Tercer problema del patrón Binary Search** y la introducción a un sub-patrón muy poderoso: **Binary Search on Answer**. En vez de buscar un elemento en un array ordenado, **buscas el valor mínimo (o máximo) que cumple una condición**, asumiendo que la condición es **monotónica** (si k funciona, k+1 también; si k no funciona, k-1 tampoco).
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Koko ama las bananas. Hay `n` pilas de bananas, donde la pila `i` tiene `piles[i]` bananas. Los guardas se irán en `h` horas.

Koko puede decidir su **velocidad de comer** `k` (bananas/hora). Cada hora elige una pila y come `k` bananas de ella. Si la pila tiene menos de `k`, come todas las restantes y **no come más** esa hora.

Encuentra el **valor mínimo de `k`** tal que Koko se las come todas en `h` horas.

**Ejemplo 1:**
```
Input:  piles = [3, 6, 7, 11], h = 8
Output: 4
        Con k=4: piles consumen ceil(3/4) + ceil(6/4) + ceil(7/4) + ceil(11/4)
                                = 1 + 2 + 2 + 3 = 8 horas ✓
        Con k=3: 1 + 2 + 3 + 4 = 10 horas (más de 8) ✗
```

**Ejemplo 2:**
```
Input:  piles = [30, 11, 23, 4, 20], h = 5
Output: 30 (necesita comer la pila más grande en 1 hora)
```

**Ejemplo 3:**
```
Input:  piles = [30, 11, 23, 4, 20], h = 6
Output: 23
```

**Restricciones:**
- `1 <= piles.length <= 10^4`
- `piles.length <= h <= 10^9`
- `1 <= piles[i] <= 10^9`

**Plantilla:**
```python
class Solution:
    def minEatingSpeed(self, piles: List[int], h: int) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` — velocidad mínima k |
| ¿Cuál es el rango posible de k? | De 1 (mínimo) a max(piles) (más rápido inútil) |
| ¿Es monotónica la "comestibilidad"? | **Sí**: si k funciona, cualquier k' > k también funciona. Si k no, ningún k' < k tampoco |
| ¿Cómo calculo horas para k dado? | `sum(ceil(p / k) for p in piles)` |
| Edge case 1 | h == len(piles): k debe ser max(piles) |
| Edge case 2 | h muy grande: k = 1 podría bastar |

> 💡 **El insight**: la función "k → ¿se come todo en h horas?" es **monotónica** (False...False True...True a medida que k crece). Binary search encuentra el primer True.

---

## Solución 1 — Linear search desde 1 (NO óptima)

```python
import math
class Solution:
    def minEatingSpeed(self, piles: List[int], h: int) -> int:
        max_pile = max(piles)
        for k in range(1, max_pile + 1):
            horas = sum(math.ceil(p / k) for p in piles)
            if horas <= h:
                return k
        return max_pile
```

**Análisis:**
- **Tiempo: O(max(piles) · n)** — TLE con max(piles) = 10^9.
- **Veredicto:** ❌ TLE.

---

## Solución 2 — Binary search on answer (la canónica)

**La idea**: en lugar de buscar un elemento en un array ordenado, **buscamos el valor mínimo k que cumple la condición** "k permite comer todo en h horas". Como la condición es monotónica, podemos hacer binary search sobre el **rango de k posibles** [1, max(piles)].

```python
import math

class Solution:
    def minEatingSpeed(self, piles: List[int], h: int) -> int:
        def horas_necesarias(k):
            return sum(math.ceil(p / k) for p in piles)

        left, right = 1, max(piles)
        while left < right:
            mid = left + (right - left) // 2
            if horas_necesarias(mid) <= h:
                right = mid                       # mid podría ser la respuesta, no descartar
            else:
                left = mid + 1
        return left
```

**Trace mental con `piles = [3, 6, 7, 11], h = 8`**:

```
Inicial: left=1, right=11

Iter 1: mid = 6
  horas(6) = ceil(3/6)+ceil(6/6)+ceil(7/6)+ceil(11/6) = 1+1+2+2 = 6 ≤ 8 ✓
  right = 6 (podría ser respuesta)

Iter 2: left=1, right=6, mid=3
  horas(3) = 1+2+3+4 = 10 > 8 ✗
  left = 4

Iter 3: left=4, right=6, mid=5
  horas(5) = 1+2+2+3 = 8 ≤ 8 ✓
  right = 5

Iter 4: left=4, right=5, mid=4
  horas(4) = 1+2+2+3 = 8 ≤ 8 ✓
  right = 4

left == right == 4 → exit loop

Return 4 ✅
```

**Análisis:**
- **Tiempo: O(n · log(max(piles)))** — log(10^9) ≈ 30 iteraciones, cada una O(n).
- **Espacio: O(1)**.
- **Veredicto:** ✅ **la canónica**. La óptima.

### Por qué `right = mid` y no `right = mid - 1`

En binary search **clásico** (LC 704), cuando `nums[mid] == target`, devuelves directamente. Aquí no — `mid` cumple la condición pero **podría haber un k menor que también cumpla**. Por eso `right = mid` (no descartas mid).

Esto cambia la condición del while a `while left < right` (no `<=`), porque `right = mid` puede no decrecer estrictamente.

---

## Variante — Usar división entera en lugar de `math.ceil`

`math.ceil(p / k)` con división de floats puede tener problemas de precisión con números grandes. Más seguro:

```python
def horas_necesarias(k):
    return sum((p + k - 1) // k for p in piles)
    # equivalente a ceil(p/k) usando solo enteros
```

**Trick aritmético**: `(a + b - 1) // b` = `ceil(a / b)` cuando a, b son enteros positivos. Lo verás en muchos problemas.

---

## El patrón general — "Binary Search on Answer"

**Cuándo aplicar**:

> Cuando buscas el **valor mínimo (o máximo)** que cumple una condición, y la condición es **monotónica** sobre el dominio de búsqueda.

**Plantilla mental** (mínimo que cumple):

```python
def binary_search_answer(low, high, ok):
    while low < high:
        mid = low + (high - low) // 2
        if ok(mid):
            high = mid                    # mid podría ser respuesta
        else:
            low = mid + 1
    return low
```

Donde `ok(x)` es la función que devuelve True si x cumple la condición.

**Tres señales** del patrón:

1. Buscas el **valor mínimo (o máximo)** de un parámetro.
2. La función "valor → cumple condición" es **monotónica**.
3. La fuerza bruta probaría todos los valores → demasiado lento.

> 🎯 **Patrón muy potente**: cuando lo interiorizas, problemas que parecen requerir DP o greedy se resuelven en 10 líneas con binary search.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **1011. Capacity to Ship Packages Within D Days** | Capacidad mínima de barco para enviar todo en D días |
| **410. Split Array Largest Sum** | Partir array en m subarrays minimizando max sum |
| **1482. Minimum Number of Days to Make m Bouquets** | Días mínimos para hacer m ramos |
| **2226. Maximum Candies Allocated to K Children** | Versión max (en lugar de min) |

> 📌 Todos siguen la misma estructura: definir `ok(x)`, binary search sobre el dominio.

---

## Conceptos a interiorizar

### Monotonicidad — el requisito clave

Para que binary search on answer funcione, la función `ok(x)` debe ser monotónica:

```
x:        1  2  3  4  5  6  7  8  9  10
ok(x):    F  F  F  T  T  T  T  T  T  T   ← monotónica (F → T una vez)
```

Si fuera `F T F T F T`, **binary search no aplica**. Tendrías que probar todos los valores.

### `math.ceil` vs trick `(a + b - 1) // b`

```python
import math
math.ceil(7 / 3)              # 3.0  (luego int(...))
(7 + 3 - 1) // 3              # 3    (entero directo, sin floats)
```

Con números enormes, `(a + b - 1) // b` evita problemas de precisión flotante.

### `while left < right` vs `while left <= right`

Depende de cómo actualices:

| Update | Condición while |
|---|---|
| `right = mid - 1` (descartar mid) | `while left <= right` |
| `right = mid` (mid podría ser la respuesta) | `while left < right` |

Recuerda esta tabla. Es la fuente de bugs más común en binary search.

---

## Comparación final de las 2 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Linear search | O(max · n) | O(1) | ❌ TLE |
| 2. **Binary search on answer** | **O(n · log(max))** | O(1) | ✅ La canónica |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** desde cero.
2. Justifica:
   - Por qué `right = mid` (no `right = mid - 1`).
   - Por qué `while left < right` (no `<=`).
   - Por qué el rango es `[1, max(piles)]`.
3. Implementa `horas_necesarias` con `(p + k - 1) // k` en lugar de `math.ceil`.
4. Trace mental con `piles = [30, 11, 23, 4, 20], h = 6`. ¿Cuántas iteraciones?
5. **Bonus** — extiende a "encontrar el K **máximo** tal que la condición se mantiene". Cambia min→max.

---

## Cosas que te pueden preguntar en entrevista

- **"Demuestra la monotonicidad."** → Si Koko come a velocidad k en H horas, comer a k+1 toma H' ≤ H (con más velocidad, no más lento). Por tanto: ok(k) → ok(k+1).
- **"¿Por qué no buscar k a partir de un promedio?"** → Sería un atajo, pero el promedio NO es el k mínimo. Necesitas binary search para ser preciso.
- **"¿Cuál es el rango correcto de k?"** → mínimo 1 (debe ser ≥1), máximo max(piles) (más rápido es inútil porque solo come una pila por hora).
- **"¿Y si las pilas pudieran ser 0?"** → Las saltarías. El enunciado garantiza ≥1.

---

## Conexiones

- [[704-binary-search]] — binary search clásico.
- [[74-search-a-2d-matrix]] — binary search en 2D.
- Próximo: [[153-find-minimum-in-rotated-sorted-array]] — binary search en array rotado.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Justificadas las dos diferencias con binary search clásico (`right = mid`, `while left < right`)
- [ ] Implementada función `horas_necesarias` con trick aritmético
- [ ] Trace mental hecho
- [ ] Resuelto en LeetCode con éxito
