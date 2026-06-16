---
title: "LeetCode 347 — Top K Frequent Elements"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/arrays-hashing, patron/heap, patron/bucket-sort]
type: nota
status: en-progreso
source: claude-code
aliases: [Top K Frequent, LC 347, topKFrequent, K más frecuentes]
problem_id: 347
difficulty: medium
patron: arrays-hashing
neetcode_order: 5
---

# LeetCode 347 — Top K Frequent Elements

> 🎯 **Quinto problema del NeetCode 150 en Arrays & Hashing**. Es el **primer roce con heap (priority queue)**, una estructura que volverás a ver muchísimo. También introduce **bucket sort**, una técnica brillante cuando la "frecuencia" tiene rango acotado.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un array de enteros `nums` y un entero `k`, devuelve los **`k` elementos más frecuentes**. Puedes devolver la respuesta en cualquier orden.

**Ejemplo 1:**
```
Input:  nums = [1, 1, 1, 2, 2, 3], k = 2
Output: [1, 2]
```

**Ejemplo 2:**
```
Input:  nums = [1], k = 1
Output: [1]
```

**Restricciones:**
- `1 <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`
- `k` está en el rango `[1, número de elementos únicos]`.
- **Se garantiza** que la respuesta es única.

> 💡 **Follow-up del enunciado**: tu algoritmo debe correr **mejor que O(n log n)**. Eso descarta el sort directo.

**Plantilla:**
```python
class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `List[int]` con k elementos |
| ¿Importa el orden? | NO |
| ¿Hay duplicados en nums? | Sí (es de eso de lo que va el problema) |
| ¿Pueden empatar dos elementos en frecuencia? | El enunciado garantiza unicidad de respuesta, pero en general sí |
| ¿Cuál es el rango de la frecuencia? | De **1 a n** (`n = len(nums)`) — esto es **clave** para bucket sort |
| Edge case 1 | k = número de elementos únicos → devolver todos |
| Edge case 2 | n = 1, k = 1 → devolver el único elemento |

---

## Solución 1 — Sort directo (no cumple el follow-up)

Contar frecuencias, ordenar las claves por frecuencia descendente, devolver las primeras k.

```python
from collections import Counter

class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        count = Counter(nums)
        return sorted(count.keys(), key=lambda x: count[x], reverse=True)[:k]
```

**Análisis:**
- **Tiempo: O(n log n)** — el sort domina.
- **Espacio: O(n)**.
- **Veredicto:** funciona pero el enunciado pide **mejor que O(n log n)**. Aceptado en LeetCode pero no en entrevista estricta.

---

## Solución 2 — `Counter.most_common(k)` (la pythonica)

`Counter` tiene un método específico que internamente usa heap.

```python
from collections import Counter

class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        return [num for num, _ in Counter(nums).most_common(k)]
```

**Análisis:**
- **Tiempo: O(n log k)** — internamente, `most_common(k)` usa un heap de tamaño k.
- **Espacio: O(n + k)**.
- **Veredicto:** ✅ pasa, idiomática, pero **demasiado mágica** para entrevista. Mejor implementar el heap a mano (Solución 3) y mencionar esta como atajo.

---

## Solución 3 — Counter + min-heap (la canónica de entrevista)

**La idea**: en vez de ordenar todo, mantener un **min-heap de tamaño k**. Recorrer el Counter; si el heap es más pequeño que k, push; si no, comparar con el mínimo y reemplazar si es mayor. Al final el heap tiene los k más frecuentes.

```python
import heapq
from collections import Counter

class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        count = Counter(nums)
        heap = []                                     # min-heap por frecuencia
        for num, freq in count.items():
            heapq.heappush(heap, (freq, num))
            if len(heap) > k:
                heapq.heappop(heap)                   # echa al menos frecuente
        return [num for freq, num in heap]
```

**Análisis:**
- **Tiempo: O(n log k)** — n inserts, cada heappush/heappop sobre heap de tamaño k es O(log k).
- **Espacio: O(n + k)** — el dict O(n) + el heap O(k).
- **Veredicto:** ✅ **la respuesta de entrevista**. Demuestra que conoces heaps.

> 💡 **`heapq` es min-heap por defecto** en Python. Para max-heap, se negan los valores: `heapq.heappush(heap, -freq)`. Aquí usamos min-heap **a propósito**: queremos echar los menos frecuentes, que están arriba del min-heap.

> 📌 **Tuplas en heaps**: `heapq` ordena por el primer elemento de la tupla, luego por el segundo, etc. `(freq, num)` ordena primero por frecuencia.

---

## Solución 4 — Bucket sort (la óptima O(n))

**La idea brillante**: la frecuencia de cualquier número está en el rango `[1, n]` (porque hay como mucho n elementos en total). Crear un array `buckets` donde `buckets[f]` es la lista de números con frecuencia exactamente `f`. Recorrer del más alto al más bajo y juntar los primeros k.

```python
from collections import Counter

class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        count = Counter(nums)
        buckets = [[] for _ in range(len(nums) + 1)]    # índice = frecuencia
        for num, freq in count.items():
            buckets[freq].append(num)

        result = []
        for f in range(len(buckets) - 1, 0, -1):        # de mayor a menor frecuencia
            for num in buckets[f]:
                result.append(num)
                if len(result) == k:
                    return result
        return result
```

**Análisis:**
- **Tiempo: O(n)** — todos los recorridos son lineales en el peor caso.
- **Espacio: O(n)**.
- **Veredicto:** ✅ **la óptima teórica**. Si el entrevistador te empuja a "más rápido que O(n log k)", esta es la respuesta. Aprovecha que el rango de frecuencias está acotado por n.

> 🎯 **Bucket sort es una técnica clásica**: cuando el espacio de claves es **conocido y acotado**, puedes usar un array indexado por la clave en vez de un sort comparativo. Funciona aquí porque las frecuencias son enteros pequeños.

---

## El patrón general — "Top-K con heap" + "Bucket sort cuando hay rango acotado"

**Cuándo usar heap (top-K)**:

> Cuando necesitas los **K mejores/peores** elementos de una colección y **K es pequeño comparado con n**. El min-heap de tamaño K te da O(n log K) en lugar de O(n log n).

**Plantilla mental** (top-K con min-heap):

```python
import heapq
def top_k(coleccion, k, score_fn):
    heap = []
    for elem in coleccion:
        heapq.heappush(heap, (score_fn(elem), elem))
        if len(heap) > k:
            heapq.heappop(heap)
    return [elem for score, elem in heap]
```

**Cuándo usar bucket sort**:

> Cuando la "clave de orden" es un **entero pequeño con rango conocido y acotado**. En este problema, frecuencias ∈ [1, n].

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **692. Top K Frequent Words** | Top K palabras (string) en lugar de números, con desempate alfabético |
| **973. K Closest Points to Origin** | Top K puntos por distancia → mismo patrón con heap |
| **215. Kth Largest Element in an Array** | Solo el k-ésimo (no top k) → quickselect O(n) en promedio |
| **451. Sort Characters By Frequency** | Reordenar string por frecuencia → bucket sort + concatenación |

---

## Conceptos a interiorizar

### `heapq` en Python (min-heap por defecto)

```python
import heapq

heap = []
heapq.heappush(heap, 3)              # [3]
heapq.heappush(heap, 1)              # [1, 3]
heapq.heappush(heap, 2)              # [1, 3, 2]
heapq.heappop(heap)                  # 1, heap = [2, 3]

# Para max-heap, negar los valores:
heapq.heappush(max_heap, -3)
-heapq.heappop(max_heap)             # 3

# Top-K en una llamada:
heapq.nlargest(3, [1, 5, 2, 4, 3])   # [5, 4, 3]
heapq.nsmallest(3, [1, 5, 2, 4, 3])  # [1, 2, 3]

# Heapificar lista existente:
nums = [3, 1, 2]
heapq.heapify(nums)                  # in-place, O(n)
```

### `Counter.most_common(k)`

```python
from collections import Counter

c = Counter([1, 1, 1, 2, 2, 3])
c.most_common()                      # [(1, 3), (2, 2), (3, 1)] — ordenado todo
c.most_common(2)                     # [(1, 3), (2, 2)] — solo top 2
```

### Bucket sort (la idea)

Ordenar **sin comparar** elementos entre sí, usando el valor mismo como índice. Solo aplica cuando los valores son enteros con rango acotado.

```python
# Ejemplo: ordenar [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5] (valores en 0..9)
buckets = [0] * 10
for x in nums:
    buckets[x] += 1
result = []
for value, count in enumerate(buckets):
    result.extend([value] * count)
# O(n + k) donde k es el rango (10 aquí)
```

---

## Comparación final de las 4 soluciones

| Solución | Tiempo | Espacio | Cumple follow-up | Veredicto |
|---|---|---|---|---|
| 1. Sort directo | O(n log n) | O(n) | ❌ | Aceptable, no entrevista |
| 2. `most_common(k)` | O(n log k) | O(n+k) | ✅ | Pythonic, demasiado mágica |
| 3. **Counter + min-heap** | O(n log k) | O(n+k) | ✅ | ✅ La canónica entrevista |
| 4. **Bucket sort** | **O(n)** | O(n) | ✅✅ | ✅ La óptima |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 3** (Counter + heap) desde cero.
2. Justifica:
   - Por qué min-heap y no max-heap.
   - Por qué la complejidad es O(n log k) y no O(n log n).
   - Cuándo conviene Solución 3 vs Solución 4.
3. Implementa la **Solución 4** (bucket sort) sin mirar.
4. Trace mental con `nums = [1, 1, 1, 2, 2, 3], k = 2`:
   - Estado del Counter.
   - En la Solución 4: contenido de cada bucket.
5. **Bonus** — ¿qué pasaría si k fuera muy grande (cercano a n)? ¿Qué solución gana?

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué min-heap y no max-heap si quieres los más frecuentes?"** → Porque mantienes un heap de **tamaño k**, y echas los menos frecuentes. El "menor" del heap es el candidato a echar; un min-heap te lo da en O(1).
- **"¿Y si k = n/2? ¿Cuál solución usarías?"** → Bucket sort siempre es O(n); el heap es O(n log k). Para k grandes, bucket gana.
- **"¿Qué pasa si los valores no son enteros sino floats?"** → No puedes hacer bucket sort directamente. Volver a heap.
- **"¿Cómo lo harías en streaming?"** → Mantener Counter incremental + min-heap de tamaño k que se actualiza con cada nuevo elemento. O(log k) por elemento.

---

## Conexiones

- [[242-valid-anagram]] — primer encuentro con `Counter`.
- [[49-group-anagrams]] — clave canónica para agrupar.
- Próximo: [[271-encode-and-decode-strings]] — diseño de protocolo de serialización.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 3 (Counter + heap) desde cero
- [ ] Implementada Solución 4 (bucket sort)
- [ ] Entendido cuándo conviene cada una (depende de k vs n)
- [ ] Resuelto en LeetCode con éxito
- [ ] Hecho 1 vez más a la semana siguiente
