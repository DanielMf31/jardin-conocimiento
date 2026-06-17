---
title: "LeetCode 239 — Sliding Window Maximum"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/sliding-window, patron/deque-monotonica, patron/analisis-amortizado]
type: nota
status: en-progreso
source: claude-code
aliases: [Sliding Window Maximum, LC 239, maxSlidingWindow, Máximo en ventana deslizante]
problem_id: 239
difficulty: hard
patron: sliding-window
neetcode_order: 6
---

# LeetCode 239 — Sliding Window Maximum

> **Sexto y último problema del patrón Sliding Window — segundo Hard**. Introduce la estructura más bonita y útil del patrón: la **deque monotónica decreciente**. Es un truco que reaparece en muchísimos problemas (Largest Rectangle in Histogram, Daily Temperatures, etc.) y aprenderlo aquí te abre toda esa familia.
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un array de enteros `nums` y un entero `k`, hay una **ventana deslizante** de tamaño `k` que se mueve de izquierda a derecha. Solo puedes ver los `k` números dentro de la ventana en cada momento.

Devuelve un array con el **máximo** de cada ventana.

**Ejemplo 1:**
```
Input:  nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3
Output: [3, 3, 5, 5, 6, 7]
        Ventanas:
          [1  3  -1] -3   5   3   6   7   → max = 3
           1 [3  -1  -3]  5   3   6   7   → max = 3
           1  3 [-1  -3   5]  3   6   7   → max = 5
           1  3  -1 [-3   5   3]  6   7   → max = 5
           1  3  -1  -3  [5   3   6]  7   → max = 6
           1  3  -1  -3   5  [3   6   7]  → max = 7
```

**Ejemplo 2:**
```
Input:  nums = [1], k = 1
Output: [1]
```

**Restricciones:**
- `1 <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`
- `1 <= k <= nums.length`

**Plantilla:**
```python
class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `List[int]` con `n - k + 1` elementos |
| ¿Tamaño k fijo? | Sí, fijo. Es una ventana **deslizante** clásica |
| ¿Hay duplicados? | Sí pueden existir |
| ¿Negativos permitidos? | Sí |
| ¿Output incluye todas las ventanas? | Sí, `n - k + 1` ventanas en total |
| Edge case 1 | `k = 1` → output = `nums` |
| Edge case 2 | `k = n` → una sola ventana, una sola salida |

> **El reto**: ¿puedes hacerlo en O(n)? La fuerza bruta da O(n·k); el heap da O(n log n); el deque monotónico da O(n).

---

## Solución 1 — Fuerza bruta O(n·k)

Para cada ventana, calcular el max recorriéndola.

```python
class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        result = []
        for i in range(len(nums) - k + 1):
            result.append(max(nums[i:i+k]))
        return result
```

**Análisis:**
- **Tiempo: O(n·k)** — TLE con n = 10^5 y k grande.
- **Espacio: O(1)** extra.
- **Veredicto:** [NO] TLE para valores grandes de k.

---

## Solución 2 — Heap (max-heap con limpieza perezosa)

**La idea**: max-heap con `(-num, index)`. El máximo siempre está en el top, pero hay que **limpiar elementos que ya están fuera de la ventana** antes de leer.

```python
import heapq

class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        heap = []
        result = []
        for right, num in enumerate(nums):
            heapq.heappush(heap, (-num, right))
            # limpiar elementos fuera de ventana
            while heap[0][1] <= right - k:
                heapq.heappop(heap)
            if right >= k - 1:
                result.append(-heap[0][0])
        return result
```

**Análisis:**
- **Tiempo: O(n log n)** — cada elemento puede entrar y salir del heap O(n) veces.
- **Espacio: O(n)** — el heap puede tener todos los elementos.
- **Veredicto:** [OK] pasa LeetCode pero **no cumple O(n)**. Aceptable como solución intermedia, no la óptima.

---

## Solución 3 — Deque monotónica decreciente (la canónica O(n))

**La idea brillante**: una **deque** (cola doble) que mantiene los **índices** de los candidatos a ser el máximo de cualquier ventana futura. Mantenida en **orden decreciente** de valores: el frente de la deque es el índice del máximo actual.

**Reglas**:
1. **Antes de añadir** un nuevo `nums[right]`: eliminar de la **cola** (extremo derecho) todos los índices cuyos valores sean `≤ nums[right]`. Esos índices ya no pueden ser máximo (ahora hay uno mayor que llega más tarde).
2. **Después de añadir**: si el índice del **frente** está fuera de la ventana (índice ≤ right - k), eliminarlo.
3. Cuando la ventana está formada (right ≥ k-1), el max es `nums[deque[0]]`.

```python
from collections import deque

class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        dq = deque()                                    # guarda ÍNDICES, no valores
        result = []
        for right, num in enumerate(nums):
            # 1. eliminar de la cola todos los índices con valores menores o iguales
            while dq and nums[dq[-1]] <= num:
                dq.pop()
            dq.append(right)
            # 2. eliminar del frente si está fuera de ventana
            if dq[0] <= right - k:
                dq.popleft()
            # 3. añadir al resultado cuando la ventana esté formada
            if right >= k - 1:
                result.append(nums[dq[0]])
        return result
```

**Trace mental con `nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3`**:

| right | num | dq antes | acción | dq después | result |
|---|---|---|---|---|---|
| 0 | 1 | [] | append 0 | [0] | — (right < k-1) |
| 1 | 3 | [0] | nums[0]=1 ≤ 3 → pop; append 1 | [1] | — |
| 2 | -1 | [1] | nums[1]=3 > -1 → no pop; append 2 | [1, 2] | nums[1]=**3** |
| 3 | -3 | [1, 2] | nums[2]=-1 > -3 → no pop; append 3. Front 1 ≤ 0? NO (3-3=0). | [1, 2, 3] | nums[1]=**3** |
| 4 | 5 | [1, 2, 3] | pop 3 (-3≤5), pop 2 (-1≤5), pop 1 (3≤5); append 4 | [4] | nums[4]=**5** |
| 5 | 3 | [4] | nums[4]=5 > 3 → no pop; append 5 | [4, 5] | nums[4]=**5** |
| 6 | 6 | [4, 5] | pop 5 (3≤6), pop 4 (5≤6); append 6 | [6] | nums[6]=**6** |
| 7 | 7 | [6] | pop 6 (6≤7); append 7 | [7] | nums[7]=**7** |

Resultado: `[3, 3, 5, 5, 6, 7]` [OK].

### Por qué la deque mantiene orden decreciente

Cuando llega un valor mayor, **todos los menores anteriores están "obsoletos"** — nunca podrán ser el máximo de ninguna ventana futura (porque en cualquier ventana donde estén, también está este nuevo mayor). Los eliminamos.

Esto garantiza que la deque siempre está en orden decreciente. El **frente** es el máximo de la ventana actual.

**Análisis:**
- **Tiempo: O(n)** — análisis amortizado: cada índice entra y sale de la deque **a lo sumo una vez**. Total: 2n operaciones.
- **Espacio: O(k)** — la deque tiene como mucho k elementos.
- **Veredicto:** [OK] **la óptima**. La que demuestra dominio del patrón "deque monotónica" en una entrevista.

> **El truco "guardar índices, no valores"** es lo que permite chequear la ventana (`dq[0] <= right - k`) sin perder información. Si guardases solo valores, no sabrías cuándo expirarlos.

---

## Trace exhaustivo de las soluciones 2 y 3 (referencia detallada)

> **Sección de repaso**: explica en profundidad cómo funcionan internamente el **heap** y la **deque monotónica** — qué hace cada operación, por qué se hace así, y un trace paso a paso con números concretos. Útil para revisar cuando hayas olvidado los detalles.

### Parte 1 — Solución 2 (HEAP) en detalle

#### 1.1 Recordatorio sobre heaps

Un **heap binario** es un árbol binario "casi completo" con la invariante: **cada padre ≤ sus hijos** (min-heap). Implementado en un array donde el padre del índice `i` es `(i-1)//2` y los hijos son `2i+1`, `2i+2`.

| Operación | Coste | Qué hace |
|---|---|---|
| `heappush(heap, x)` | O(log n) | Inserta y burbujea hacia arriba hasta cumplir invariante |
| `heappop(heap)` | O(log n) | Extrae el mínimo, pone el último arriba y burbujea hacia abajo |
| `heap[0]` | O(1) | Lee el mínimo **sin extraer** |

**En Python (`heapq`) solo existe min-heap.** Para max-heap se usa el truco de **negar valores**: el "más negativo" es el mínimo del heap → corresponde al máximo real.

#### 1.2 Por qué tuplas `(-num, right)`

```python
heapq.heappush(heap, (-num, right))
```

Dos motivos críticos:

1. **`-num`** simula max-heap. `heap[0]` da el más negativo → recuperamos el original con `-heap[0][0]`.
2. **`right` (índice)** se guarda junto al valor para detectar **cuándo expira** (cuando `índice ≤ right_actual - k`). Sin él no sabríamos qué elementos están fuera.

Las tuplas en Python se comparan **lexicográficamente** (primero por primer elemento, en empate por segundo). El heap ordena por `-num`; si dos son iguales, por índice.

#### 1.3 Qué es la "limpieza perezosa"

Eliminar un elemento arbitrario de un heap es O(n) (hay que buscarlo). Para evitarlo:

- **Dejamos los elementos viejos dentro hasta que estorben** (es decir, hasta que sean el top).
- **Solo entonces** los sacamos con `heappop`.
- Mientras tanto, el heap puede contener "basura" (elementos fuera de ventana), pero **nos da igual** porque solo leemos el top y lo verificamos antes.

Es "perezoso" porque pospone trabajo hasta que es estrictamente necesario.

#### 1.4 Trace paso a paso — `nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3`

Convención: muestro el heap como **lista interna de Python**. Las tuplas son `(-num, idx)`. El top es `heap[0]`.

**right=0, num=1**
```
heappush((-1, 0)) → heap = [(-1, 0)]
top = (-1, 0)  →  representa nums[0]=1
Limpieza: 0 ≤ 0-3=-3? NO.
right=0 < k-1=2 → no emite.
```

**right=1, num=3**
```
heappush((-3, 1)) → heap = [(-3, 1), (-1, 0)]
   Burbujeo: -3 < -1, sube al top.
top = (-3, 1)  →  nums[1]=3
Limpieza: 1 ≤ -2? NO.
right=1 < 2 → no emite.
```

**right=2, num=-1**
```
heappush((1, 2)) → heap = [(-3, 1), (-1, 0), (1, 2)]
top = (-3, 1)  →  nums[1]=3
Limpieza: 1 ≤ -1? NO.
right=2 ≥ 2 → EMITE: -(-3) = 3.   result = [3]
```

**right=3, num=-3**
```
heappush((3, 3)) → heap = [(-3, 1), (-1, 0), (1, 2), (3, 3)]
top = (-3, 1)
Limpieza: 1 ≤ 0? NO. (nums[1] sigue en ventana [1,2,3]).
EMITE: 3.   result = [3, 3]
```

**right=4, num=5**
```
heappush((-5, 4)) → tras burbujeo:
  heap = [(-5, 4), (-3, 1), (1, 2), (3, 3), (-1, 0)]
top = (-5, 4)  →  nums[4]=5
Limpieza: 4 ≤ 1? NO.

 El elemento (-3, 1) ya está fuera de la ventana actual [2,3,4]
   PERO no estorba (no es el top), así que no lo limpiamos.
   Ahí está la "pereza" — viejo dentro, pero invisible.

EMITE: 5.   result = [3, 3, 5]
```

**right=5, num=3**
```
heappush((-3, 5)) → heap reordenado:
  [(-5, 4), (-3, 1), (-3, 5), (3, 3), (-1, 0), (1, 2)]
top = (-5, 4)
Limpieza: 4 ≤ 2? NO.
EMITE: 5.   result = [3, 3, 5, 5]
```

**right=6, num=6**
```
heappush((-6, 6)) → tras burbujeo:
  [(-6, 6), (-5, 4), (-3, 5), (-3, 1), (-1, 0), (1, 2), (3, 3)]
top = (-6, 6)
Limpieza: 6 ≤ 3? NO.
EMITE: 6.   result = [3, 3, 5, 5, 6]
```

**right=7, num=7**
```
heappush((-7, 7)) → top = (-7, 7).
Limpieza: 7 ≤ 4? NO.
EMITE: 7.   result = [3, 3, 5, 5, 6, 7] [OK]
```

#### 1.5 Caso donde la limpieza perezosa SÍ se activa — `nums = [5, 4, 3, 2, 1], k = 2`

```
right=0, num=5: heap=[(-5,0)]. No emite (right<1).
right=1, num=4: heap=[(-5,0),(-4,1)]. top=(-5,0).
                Limpieza: 0 ≤ -1? NO. EMITE: 5. result=[5].
right=2, num=3: heap=[(-5,0),(-4,1),(-3,2)]. top=(-5,0).
                Limpieza: 0 ≤ 0? SÍ → heappop saca (-5,0).
                heap=[(-4,1),(-3,2)]. top=(-4,1). Re-chequeo: 1 ≤ 0? NO. Para.
                EMITE: 4. result=[5, 4].
right=3, num=2: heap=[(-4,1),(-3,2),(-2,3)]. top=(-4,1).
                Limpieza: 1 ≤ 1? SÍ → heappop saca (-4,1).
                heap=[(-3,2),(-2,3)]. Re-chequeo: 2 ≤ 1? NO.
                EMITE: 3. result=[5, 4, 3].
right=4, num=1: heap=[(-3,2),(-2,3),(-1,4)]. top=(-3,2).
                Limpieza: 2 ≤ 2? SÍ → heappop saca (-3,2).
                heap=[(-2,3),(-1,4)]. Re-chequeo: 3 ≤ 2? NO.
                EMITE: 2. result=[5, 4, 3, 2].
```

Aquí ves el `while` de limpieza activarse cada paso (caso degradado).

#### 1.6 Por qué O(n log n) y no O(n)

Cada elemento entra al heap una vez (`heappush` en O(log n)) y puede salir una vez (`heappop` en O(log n)). Total ≤ 2n × log n = **O(n log n)**.

El heap **no puede ser O(n)** porque su naturaleza ordenada cuesta log n por operación. La deque monotónica logra O(n) porque renuncia al "ordenamiento global" — solo mantiene candidatos vivos.

---

### Parte 2 — Solución 3 (DEQUE MONOTÓNICA) en detalle

#### 2.1 Recordatorio sobre deques

Una **deque** (double-ended queue) permite insertar/extraer por ambos extremos en O(1).

| Operación | Coste | Significado |
|---|---|---|
| `dq.append(x)` | O(1) | Insertar por la derecha |
| `dq.appendleft(x)` | O(1) | Insertar por la izquierda |
| `dq.pop()` | O(1) | Sacar por la derecha |
| `dq.popleft()` | O(1) | Sacar por la izquierda |
| `dq[0]` | O(1) | Leer el frente (izquierda) |
| `dq[-1]` | O(1) | Leer la cola (derecha) |

`from collections import deque`. Implementada como lista doblemente enlazada por bloques.

#### 2.2 Qué significa "monotónica decreciente"

Mantenemos la invariante: **los valores correspondientes a los índices guardados están en orden estrictamente decreciente** de izquierda a derecha.

```
deque (índices):  [4,    7,    9]
nums en esos:    [10,   6,    3]   ← decreciente
                  ↑                 ↑
                  frente            cola
                  = MAX actual
```

**Por qué decreciente**: queremos que el frente sea siempre el máximo. Cuando llega un valor mayor, todos los menores anteriores son **inútiles para el futuro** (en cualquier ventana donde estén, también está el nuevo, que es mayor → ellos nunca volverán a ser máximo).

#### 2.3 Por qué guardar ÍNDICES y no valores

Necesitamos saber **cuándo un elemento sale de la ventana**: índice `i` está en ventana actual `[right-k+1, right]` ⟺ `i > right - k`. Si guardáramos solo valores, no podríamos detectar la expiración. Con el índice consultamos `nums[idx]` cuando necesitamos el valor.

#### 2.4 Las tres reglas

```
REGLA 1 — Mantener orden decreciente (limpia por la cola):
   Mientras la deque tenga elementos Y nums[dq[-1]] <= num:
       dq.pop()                        # quita por la derecha
   dq.append(right)                    # añade el nuevo índice por la derecha

REGLA 2 — Expirar el frente si está fuera de ventana:
   Si dq[0] <= right - k:
       dq.popleft()                    # quita por la izquierda

REGLA 3 — Emitir resultado cuando ventana esté formada:
   Si right >= k - 1:
       result.append(nums[dq[0]])      # el frente es el máximo
```

> ℹ **Sobre `<=` en Regla 1**: usamos `<=` (no `<`) para manejar duplicados — si ya hay un valor igual y entra otro nuevo, sacamos el viejo porque expirará antes y el nuevo durará más.

#### 2.5 Trace paso a paso — `nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3`

**right=0, num=1**
```
nums:  [ 1   3  -1  -3   5   3   6   7 ]
        ^right
Regla 1: dq vacía → append. dq=[0].
Regla 2: 0 ≤ -3? NO.
Regla 3: right=0 < 2 → no emite.

dq = [0]   nums[dq] = [1]   
```

**right=1, num=3**
```
nums:  [ 1   3  -1  -3   5   3   6   7 ]
            ^right
Regla 1: nums[0]=1 ≤ 3? SÍ → pop. dq vacía. append(1). dq=[1].
   ↑ Tiramos el 0 porque en cualquier ventana que lo contenga,
     también está el 1 (mayor) → el 0 nunca será máximo.
Regla 2: 1 ≤ -2? NO.
Regla 3: 1 < 2 → no emite.

dq = [1]   nums[dq] = [3]   
```

**right=2, num=-1**
```
nums:  [ 1   3  -1  -3   5   3   6   7 ]
                ^right    ventana = [1, 3, -1]
Regla 1: nums[1]=3 ≤ -1? NO. append(2). dq=[1, 2].
   ↑ Mantenemos el 3 (es candidato actual) y AÑADIMOS el -1 detrás
     (puede ser máximo en ventanas futuras donde el 3 ya haya expirado).
Regla 2: 1 ≤ -1? NO.
Regla 3: EMITE nums[1] = 3.

dq = [1, 2]   nums[dq] = [3, -1]   
result = [3]
```

**right=3, num=-3**
```
nums:  [ 1   3  -1  -3   5   3   6   7 ]
                    ^right    ventana = [3, -1, -3]
Regla 1: nums[2]=-1 ≤ -3? NO. append(3). dq=[1, 2, 3].
Regla 2: 1 ≤ 0? NO. (Índice 1 sigue en ventana [1,3]).
Regla 3: EMITE nums[1] = 3.

dq = [1, 2, 3]   nums[dq] = [3, -1, -3]   
result = [3, 3]
```

**right=4, num=5** ← BARRIDO TOTAL POR LA COLA
```
nums:  [ 1   3  -1  -3   5   3   6   7 ]
                        ^right    ventana = [-1, -3, 5]
Regla 1 (iterativa):
  iter 1: nums[3]=-3 ≤ 5? SÍ → pop. dq=[1,2].
  iter 2: nums[2]=-1 ≤ 5? SÍ → pop. dq=[1].
  iter 3: nums[1]=3  ≤ 5? SÍ → pop. dq=[].
  append(4). dq=[4].
   ↑ El 5 es tan grande que invalida a TODOS los anteriores.
     Cualquier ventana que lo contenga será dominada por él.
Regla 2: 4 ≤ 1? NO.
Regla 3: EMITE nums[4] = 5.

dq = [4]   nums[dq] = [5]   
result = [3, 3, 5]
```

**right=5, num=3**
```
nums:  [ 1   3  -1  -3   5   3   6   7 ]
                            ^right    ventana = [-3, 5, 3]
Regla 1: nums[4]=5 ≤ 3? NO. append(5). dq=[4, 5].
Regla 2: 4 ≤ 2? NO.
Regla 3: EMITE nums[4] = 5.

dq = [4, 5]   nums[dq] = [5, 3]   
result = [3, 3, 5, 5]
```

**right=6, num=6** ← OTRO BARRIDO TOTAL
```
nums:  [ 1   3  -1  -3   5   3   6   7 ]
                                ^right    ventana = [5, 3, 6]
Regla 1:
  iter 1: nums[5]=3 ≤ 6? SÍ → pop. dq=[4].
  iter 2: nums[4]=5 ≤ 6? SÍ → pop. dq=[].
  append(6). dq=[6].
Regla 2: 6 ≤ 3? NO.
Regla 3: EMITE nums[6] = 6.

dq = [6]   nums[dq] = [6]   
result = [3, 3, 5, 5, 6]
```

**right=7, num=7**
```
nums:  [ 1   3  -1  -3   5   3   6   7 ]
                                    ^right    ventana = [3, 6, 7]
Regla 1: nums[6]=6 ≤ 7? SÍ → pop. dq=[]. append(7). dq=[7].
Regla 2: 7 ≤ 4? NO.
Regla 3: EMITE nums[7] = 7.

dq = [7]   nums[dq] = [7]
result = [3, 3, 5, 5, 6, 7] [OK]
```

#### 2.6 Caso donde se activa la Regla 2 (expirar por frente) — `nums = [5, 4, 3, 2, 1], k = 3`

En el ejemplo anterior la Regla 2 nunca disparó porque el máximo siempre llegaba "fresco". Aquí sí:

```
right=0, num=5: dq=[0]. Regla 2: 0 ≤ -3? NO. No emite.
right=1, num=4: nums[0]=5 > 4. append. dq=[0,1]. Regla 2: 0 ≤ -2? NO. No emite.
right=2, num=3: nums[1]=4 > 3. append. dq=[0,1,2].
                Regla 2: 0 ≤ -1? NO. EMITE nums[0]=5. result=[5].
right=3, num=2: nums[2]=3 > 2. append. dq=[0,1,2,3].
                Regla 2: 0 ≤ 0? SÍ → popleft. dq=[1,2,3].
                EMITE nums[1]=4. result=[5, 4].
right=4, num=1: nums[3]=2 > 1. append. dq=[1,2,3,4].
                Regla 2: 1 ≤ 1? SÍ → popleft. dq=[2,3,4].
                EMITE nums[2]=3. result=[5, 4, 3].
```

Aquí se ve cómo la Regla 2 expira por la izquierda cuando el máximo "envejece" sin ser superado.

#### 2.7 Por qué O(n) — análisis amortizado

Mirando el algoritmo aislado parece O(n·k) (un `while` dentro del `for`). Pero:

- **Cada índice entra a la deque como mucho una vez** (un `append` por iteración del for, n total).
- **Cada índice sale como mucho una vez** (sea por `pop` derecho en Regla 1, sea por `popleft` en Regla 2).

→ Total de operaciones sobre la deque ≤ **2n** → tiempo total **O(n)**.

El `while` puede iterar mucho en una sola iteración del for, pero esas iteraciones se "compensan" con iteraciones futuras del for que harán cero trabajo. **No puedes pagar dos veces la misma expulsión.**

---

### Comparación final intuitiva — Heap vs Deque

| Aspecto | Heap | Deque monotónica |
|---|---|---|
| **Estructura** | Árbol binario ordenado por valor | Lista doble con invariante de orden |
| **Qué guarda** | TODOS los elementos vistos | Solo los **candidatos vivos** |
| **Expiración** | Perezosa (al llegar al top) | Inmediata por ambos extremos |
| **Lectura del max** | `heap[0]` (top) | `dq[0]` (frente) |
| **Coste por op** | O(log n) | O(1) amortizado |
| **Total** | O(n log n) | **O(n)** |

**Intuición clave**: el heap mantiene **información que no necesitas** (elementos invalidados que siguen ahí porque sacar de un heap arbitrariamente es caro). La deque monotónica **descarta información en cuanto deja de ser útil**, por eso es más rápida.

---

## El patrón general — "Deque monotónica"

**Cuándo aplicar**:

> Cuando necesitas el **máximo (o mínimo) de una ventana deslizante** o equivalente: "el siguiente menor a la derecha", "el siguiente mayor", "rectángulo más grande en histograma", etc.

**Plantilla mental** (max sobre ventana de tamaño k):

```python
from collections import deque

def deque_monotonica_max(arr, k):
    dq = deque()                                    # guarda ÍNDICES
    result = []
    for right, x in enumerate(arr):
        # 1. mantener orden decreciente
        while dq and arr[dq[-1]] <= x:
            dq.pop()
        dq.append(right)
        # 2. expirar el frente si está fuera de ventana
        if dq[0] <= right - k:
            dq.popleft()
        # 3. emitir cuando ventana llena
        if right >= k - 1:
            result.append(arr[dq[0]])
    return result
```

**Tres señales** del patrón:

1. Buscas el **max o min de una ventana** (deslizante o no).
2. La fuerza bruta da O(n·k) y necesitas O(n).
3. Hay una idea de "candidatos" que se pueden descartar cuando llega uno mejor.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **496. Next Greater Element I** | "Siguiente mayor" en un array → stack monotónico |
| **739. Daily Temperatures** | "Cuántos días hasta temperatura mayor" → stack monotónico |
| **84. Largest Rectangle in Histogram** | Stack monotónico para áreas |
| **862. Shortest Subarray with Sum at Least K** | Deque monotónica con sumas acumulativas (Hard) |
| **1696. Jump Game VI** | Deque monotónica + DP |

> **Patrón maestro**: stack monotónico y deque monotónica son la **misma idea estructural**. Stack si el problema es "el siguiente/anterior X", deque si hay también una restricción de ventana.

---

## Conceptos a interiorizar

### Análisis amortizado en deque monotónica

Aunque hay un `while` interno, cada índice se inserta y elimina **a lo sumo una vez**. La suma de todas las operaciones es `2n` máximo. Esto es **el mismo argumento** que en:
- [[125-valid-palindrome]] (saltar no-alfanuméricos).
- [[128-longest-consecutive-sequence]] (check de "soy inicio").
- [[3-longest-substring-without-repeating-characters]] (sliding window).

Cada vez que veas un while interno donde "los punteros solo avanzan, nunca retroceden", piensa amortización.

### Por qué guardar índices y no valores

Para saber cuándo un elemento "expira" (sale de la ventana), necesitas su posición. Si guardas solo el valor, pierdes esa información. Patrón general: **cuando el tiempo importa, guarda índice + (opcionalmente) valor**.

### Diferencia entre Stack y Deque monotónica

- **Stack monotónica**: solo necesitas operar en el extremo (LIFO). "Próximo mayor", "rectángulo mayor".
- **Deque monotónica**: necesitas operar en **ambos extremos**: añadir/eliminar atrás según orden, expirar adelante por ventana.

Stack es un caso especial de deque (sin la restricción de ventana).

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Fuerza bruta | O(n·k) | O(1) | [NO] TLE |
| 2. Heap con limpieza | O(n log n) | O(n) | [OK] Pasa, no óptima |
| 3. **Deque monotónica** | **O(n)** | O(k) | [OK] La óptima |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 3** (deque monotónica) desde cero.
2. Justifica:
   - Por qué guardamos índices, no valores.
   - Por qué `nums[dq[-1]] <= num` y no `<` (qué pasa con duplicados).
   - Por qué el `if dq[0] <= right - k` y no `< right - k`.
   - Cuál es la complejidad amortizada y por qué.
3. Trace mental con `nums = [7, 2, 4], k = 2`. ¿Cuál es el output?
4. Trace mental con `nums = [1, 1, 1, 1], k = 2`. ¿Cómo se manejan los duplicados?
5. **Bonus** — modifica para mantener el **mínimo** de cada ventana en lugar del máximo. ¿Qué cambia?
6. **Bonus 2** — extiéndelo a "el segundo máximo" de cada ventana.

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué O(n) si hay un while dentro de un for?"** → Análisis amortizado: cada índice entra/sale de la deque ≤ 1 vez. Total ≤ 2n.
- **"Diferencia entre stack monotónico y deque monotónica?"** → Stack: LIFO, sin restricción de ventana. Deque: ambos extremos, con expiración por ventana.
- **"¿Cómo lo modificarías para mínimo en vez de máximo?"** → Cambiar el `<=` por `>=` en el while interno. La deque se vuelve creciente.
- **"¿Y si k pudiera ser mayor que n?"** → El enunciado garantiza k ≤ n, pero si pudiera, devuelve `[max(nums)]` o caso especial.
- **"¿Cuál es el peor caso espacial?"** → O(k), cuando la ventana entera está en orden decreciente y nadie se elimina.

---

## Cierre del patrón Sliding Window

Has llegado al **último problema del tercer patrón del NeetCode 150**. Resumen de los **6 problemas**:

| # | Problema | Variante | Idea distintiva |
|---|---|---|---|
| 1 | [[121-best-time-to-buy-and-sell-stock]] | Tracking de mínimo histórico | One-pass con var "min visto" |
| 2 | [[3-longest-substring-without-repeating-characters]] | Ventana variable + set | Expand/shrink con duplicado |
| 3 | [[424-longest-repeating-character-replacement]] | Variable + tolerancia | `len - max_freq <= k` |
| 4 | [[567-permutation-in-string]] | Ventana fija + Counter | Match de frecuencias |
| 5 | [[76-minimum-window-substring]] | Variable + cobertura | `have / need` (matches counter) |
| 6 | **Este** | Variable + estructura auxiliar | Deque monotónica decreciente |

**Después de Sliding Window**, el siguiente patrón es **Stack** (7 problemas), que comparte mucha intuición con la deque monotónica que acabas de ver. Va a parecerte familiar.

---

## Conexiones

- [[121-best-time-to-buy-and-sell-stock]] · [[3-longest-substring-without-repeating-characters]] · [[424-longest-repeating-character-replacement]] · [[567-permutation-in-string]] · [[76-minimum-window-substring]] — los demás del patrón.
- [[MOC_NeetCode_150]] — índice general.
- Próximo patrón: **Stack** (avísame cuando quieras arrancarlo).

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 3 (deque monotónica) desde cero
- [ ] Justificado el análisis amortizado O(n)
- [ ] Justificado por qué guardar índices y no valores
- [ ] Trace mental hecho con duplicados
- [ ] Resuelto en LeetCode con éxito
- [ ] **Patrón Sliding Window cerrado** [OK]
