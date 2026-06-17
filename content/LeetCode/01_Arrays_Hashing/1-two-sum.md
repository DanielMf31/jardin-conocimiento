---
title: "LeetCode 1 — Two Sum"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/arrays-hashing, patron/hash-map, patron/complemento]
type: nota
status: en-progreso
source: claude-code
aliases: [Two Sum, LC 1, twoSum, El primer LeetCode, El problema 1]
problem_id: 1
difficulty: easy
patron: arrays-hashing
neetcode_order: 3
---

# LeetCode 1 — Two Sum

> **El problema más famoso de LeetCode**. Literalmente el `id=1`. Lo verás referenciado en charlas, memes y entrevistas. Es **el** problema que hay que saber.
> Tercer problema del NeetCode 150 en Arrays & Hashing. Después de [[217-contains-duplicate]] (set) y [[242-valid-anagram]] (dict para contar), ahora **dict para mapear**: el patrón **"el complemento que falta"**.

## Enunciado

Dado un array de enteros `nums` y un entero `target`, devuelve los **índices** de los dos números que suman exactamente `target`.

Puedes asumir que **cada input tiene exactamente una solución**, y que **no se puede usar el mismo elemento dos veces**.

Puedes devolver la respuesta en **cualquier orden**.

**Ejemplo 1:**
```
Input:  nums = [2, 7, 11, 15], target = 9
Output: [0, 1]
Explicación: nums[0] + nums[1] == 9 → devolvemos [0, 1]
```

**Ejemplo 2:**
```
Input:  nums = [3, 2, 4], target = 6
Output: [1, 2]
```

**Ejemplo 3:**
```
Input:  nums = [3, 3], target = 6
Output: [0, 1]
```

**Restricciones:**
- `2 <= nums.length <= 10^4` → al menos 2 elementos, hasta 10.000.
- `-10^9 <= nums[i] <= 10^9` → enteros con signo.
- `-10^9 <= target <= 10^9`.
- **Solo existe una respuesta válida.**

**Plantilla:**
```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `List[int]` con **dos índices** (no los valores) |
| ¿Hay siempre solución? | Sí, garantizado por el enunciado |
| ¿Puedo usar el mismo elemento dos veces? | **NO** — `nums[0]` no puede emparejarse consigo mismo |
| ¿Hay duplicados? | **Sí pueden existir** (ver Ejemplo 3: `[3, 3]`) |
| ¿Está ordenado el array? | **NO** — para la versión ordenada existe LC 167 |
| ¿Hay solución única? | Sí, el enunciado lo garantiza |
| ¿En qué orden devuelvo los índices? | Cualquiera, el grader acepta `[0, 1]` y `[1, 0]` |
| Edge case típico | Números negativos: `[-3, 4, 3, 90], target = 0` → debería devolver `[0, 2]` |

> **Lo que diferencia este problema de Contains Duplicate**: aquí no buscas el mismo elemento, buscas un **elemento distinto** cuya suma con el actual dé el target. Es decir: buscas el **complemento**, no el duplicado.

---

## Solución 1 — Fuerza bruta (la primera idea de cualquiera)

Doble bucle: para cada par `(i, j)` con `i < j`, comprobar si suman target.

```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):           # j siempre > i, evita auto-emparejamiento
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []                                # nunca se alcanza, pero satisface el type hint
```

**Análisis:**
- **Tiempo: O(n²)** — par (i, j) requiere chequear hasta n·(n-1)/2 combinaciones.
- **Espacio: O(1)** — solo dos índices.
- **Veredicto:** **pasa los tests** de LeetCode (n ≤ 10⁴ → 10⁸ ops, justo en el límite). Pero no es la respuesta esperada.

> **Trampa común**: empezar `j` desde `0` en lugar de `i+1` haría que `nums[i] + nums[i] == target` cuente, violando la regla "no usar el mismo elemento dos veces". Empezar desde `i+1` lo evita.

---

## Solución 2 — Hash map en dos pasadas

**La idea**: si tuviera un mapa `valor → índice` precomputado, para cada `num` podría buscar su complemento `target - num` en O(1).

```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Primera pasada: construir el dict valor -> índice
        indices = {num: i for i, num in enumerate(nums)}

        # Segunda pasada: para cada num, buscar el complemento
        for i, num in enumerate(nums):
            complemento = target - num
            if complemento in indices and indices[complemento] != i:
                return [i, indices[complemento]]
        return []
```

**Análisis:**
- **Tiempo: O(n)** — dos recorridos, lookups O(1).
- **Espacio: O(n)** — el dict almacena n entradas.
- **Veredicto:** correcta, pero **tiene una sutileza**:

> **Cuidado con duplicados**: si `nums = [3, 3], target = 6`, la dict comprehension hace `{3: 0}` y luego `{3: 1}` (sobrescribe). Cuando buscamos el complemento `3` en el primer `num=3` (i=0), `indices[3]` es `1`, diferente de `0` → devuelve `[0, 1]`. Por eso la guarda `indices[complemento] != i` es **crítica**: evita emparejar un elemento consigo mismo.

---

## Solución 3 — Hash map en una sola pasada (LA idiomática)

**La idea clave**: no necesito **todo** el mapa antes de empezar a buscar. A medida que recorro, **voy guardando cada elemento junto con su índice**. Cuando llego a un elemento `num`, su complemento puede estar:
- **Atrás (ya guardado)** → lo encuentro en el dict, devuelvo.
- **Delante (no llegué)** → todavía no lo veo, lo guardo y sigo.

```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        visto = {}                              # valor -> índice donde lo vi
        for i, num in enumerate(nums):
            complemento = target - num
            if complemento in visto:
                return [visto[complemento], i]  # complemento (anterior) primero, num (actual) después
            visto[num] = i                      # guardo después de chequear, no antes
        return []
```

**Análisis:**
- **Tiempo: O(n)** — un solo recorrido, lookups y inserts O(1).
- **Espacio: O(n)** — el dict crece hasta n-1 elementos en el peor caso.
- **Veredicto:** [OK] **la respuesta esperada en entrevista**. Demuestra que entiendes el patrón.

### Por qué la one-pass funciona y NO necesita la guarda `!= i`

Comparado con la Solución 2: aquí guardamos `num` **después** de chequear su complemento. Por construcción, cuando chequeamos `complemento in visto`, el dict solo contiene elementos con índice `< i`. Es **imposible** que `visto[complemento] == i`, porque `i` aún no está en `visto`. Por eso no necesitamos la guarda extra.

### Trace mental con `nums = [2, 7, 11, 15], target = 9`

| Iteración | `i` | `num` | `complemento = 9 - num` | `visto` antes | ¿Encontrado? | Acción |
|---|---|---|---|---|---|---|
| 1 | 0 | 2 | 7 | `{}` | No | `visto = {2: 0}` |
| 2 | 1 | 7 | 2 | `{2: 0}` | **Sí, en índice 0** | `return [0, 1]` |

Encuentra la solución en **2 iteraciones** sin haber recorrido todo. Es estrictamente mejor que la Solución 2.

---

## Solución 4 — Two pointers (NO aplica aquí, pero es importante saberlo)

> **Esta solución NO funciona para Two Sum (LC 1)**. La incluyo porque es el patrón natural para la **variante ordenada** y es importante distinguir cuándo aplica.

Si `nums` estuviera **ordenado**, podrías usar dos punteros (uno al principio, otro al final) y moverlos según la suma sea menor o mayor que el target. Pero ordenar **destruye los índices originales**, que es lo que pide devolver el problema.

```python
# ❌ Esta solución NO es correcta para LC 1 porque destruye los índices.
def twoSum_ORDENADO(self, nums, target):
    nums_ordenado = sorted(enumerate(nums), key=lambda x: x[1])
    left, right = 0, len(nums) - 1
    while left < right:
        suma = nums_ordenado[left][1] + nums_ordenado[right][1]
        if suma == target:
            return sorted([nums_ordenado[left][0], nums_ordenado[right][0]])
        elif suma < target:
            left += 1
        else:
            right -= 1
```

**Cuándo SÍ aplica two-pointers**: en [LC 167 — Two Sum II - Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/), donde el array ya está ordenado. En ese problema two-pointers da O(n) tiempo y **O(1) espacio** (mejor que el hash map en espacio). Pero requiere que el array esté ordenado de origen.

> **Lección general**: dos patrones distintos para problemas hermanos. Hash map cuando el array es **arbitrario**; two pointers cuando es **ordenado**. Saber elegir el correcto en función del input es señal de seniority.

---

## El patrón general — "El complemento que falta"

Esta es la abstracción que generaliza el problema. **Cuándo aplicar este patrón**:

> Cuando el problema te pide encontrar **un par (o tripleta, etc.) que cumpla una relación aritmética entre elementos**, y la estructura te permite calcular qué "te falta" a partir de lo que tienes.

**Plantilla mental** (memorízala):

```python
def patron_complemento(coleccion, target):
    visto = {}                                  # info_clave -> info_a_devolver
    for i, elemento in enumerate(coleccion):
        lo_que_falta = funcion(target, elemento)
        if lo_que_falta in visto:
            return resultado(visto[lo_que_falta], i)
        visto[elemento] = i
    return None
```

**Tres señales** que te avisan de que es este patrón:

1. El problema te da un **target** y te pide encontrar **dos cosas que sumen / resten / multipliquen** hasta llegar a él.
2. El array **no está ordenado** (si estuviera, mira si two pointers aplica primero).
3. La solución obvia es doble bucle O(n²) y necesitas bajar a O(n).

---

## Variaciones del problema

Two Sum es el problema **fundacional**. Sus variaciones aparecen por todas partes:

| Problema LeetCode | Variación |
|---|---|
| **167. Two Sum II - Input Array Is Sorted** | Array ordenado → **two pointers**, O(1) espacio |
| **170. Two Sum III - Data structure design** | Diseña una clase con `add(num)` y `find(value)` → estructura de soporte continuo |
| **653. Two Sum IV - Input is a BST** | El input es un árbol binario de búsqueda → in-order traversal + hash set |
| **15. 3Sum** | Triplete que suma 0 → ordenar + fix uno + two pointers para los otros dos |
| **18. 4Sum** | Cuatro elementos que suman target → extiende 3Sum con bucle exterior |
| **454. 4Sum II** | Suma de elementos de **4 arrays distintos** = 0 → hash map de pares |
| **1. Two Sum (Closest)** | Variante en algunas empresas: pareja cuya suma sea **lo más cercana** a target |
| **560. Subarray Sum Equals K** | Subarray contiguo que suma K → **prefix sum** + hash map (mismo patrón mental aplicado a sumas acumulativas) |

> **Patrón maestro**: Two Sum es la base del patrón "complemento". 3Sum y 4Sum son combinaciones de Two Sum con bucles externos. Subarray Sum Equals K es Two Sum sobre **sumas acumulativas** en lugar de elementos directos. Cuando lo interiorizas, **muchos problemas Medium/Hard se resuelven en minutos**.

---

## Conceptos a interiorizar

### `enumerate()` — el patrón Pythonic para "índice + valor"

```python
# ❌ Verboso, contra-pythonic
for i in range(len(nums)):
    num = nums[i]
    ...

# ✅ Idiomático
for i, num in enumerate(nums):
    ...
```

`enumerate()` devuelve un iterador de tuplas `(índice, valor)`. Es **siempre** preferible para LeetCode.

### `dict` como "memoria de lo visto" (variantes)

| Caso | Qué guardas | Ejemplo |
|---|---|---|
| ¿He visto X? | nada (usa `set`) | Contains Duplicate |
| ¿Cuántas veces he visto X? | contador | Valid Anagram |
| **Dónde vi X (índice)** | **índice** | **Two Sum** |
| ¿Qué venía antes que X? | predecesor | LC 121 (Best Time to Buy Stock) |

Esta tabla resume **toda la familia** de patrones Arrays & Hashing. La diferencia entre problemas es **qué información asocias** a cada elemento que ves.

### Por qué guardamos índice en lugar de valor

El problema pide **índices** como salida, no valores. Si guardáramos solo valores no podríamos reconstruir las posiciones. **Lección general**: el `value` del dict debe ser **lo que necesitas devolver al final**, no necesariamente el elemento mismo.

### One-pass vs two-pass

En general, una sola pasada es más eficiente, pero **no siempre es posible**. La one-pass funciona aquí porque la pregunta es simétrica: si A y B suman target, da igual quién sea visto antes. En problemas asimétricos (e.g. "el siguiente más grande") puede que necesites two-pass o estrategias diferentes.

---

## Comparación final de las 4 soluciones

| Solución | Tiempo | Espacio | Funciona aquí | Veredicto |
|---|---|---|---|---|
| 1. Fuerza bruta | O(n²) | O(1) | Sí (TLE en Hard) | Pasa los tests pero no la entrevista |
| 2. Hash map two-pass | O(n) | O(n) | Sí | Funcional, sutil con duplicados |
| 3. **Hash map one-pass** | **O(n)** | **O(n)** | **Sí** | [OK] **La idiomática** |
| 4. Two pointers | O(n log n) | O(1) | **NO** (destruye índices) | Aplica solo a LC 167 |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 3** (one-pass) desde cero sin copiar.
2. Justifica:
   - Por qué guardamos en `visto` **después** de chequear, no antes.
   - Por qué la solución no necesita el chequeo `visto[complemento] != i` (cuando la two-pass sí).
   - Cuál es la complejidad espacial.
3. Trace mental con `nums = [3, 3], target = 6`. ¿Qué devuelve y por qué?
4. Trace mental con `nums = [-3, 4, 3, 90], target = 0`. ¿Qué tiene `visto` paso a paso?
5. **Bonus** — ¿podrías resolverlo si **no** se garantizara que existe solución? ¿Qué cambia?
6. **Bonus extendido** — ¿cómo cambiaría tu solución si el problema pidiera devolver **todos los pares** distintos (no solo uno)? Pista: el dict tiene que guardar listas de índices, no índices únicos.

---

## Cosas que te pueden preguntar en entrevista sobre este problema

- **"Y si el array estuviera ordenado?"** → Two pointers, O(1) espacio. **Esta es la pregunta favorita** de muchos entrevistadores como follow-up de Two Sum.
- **"Y si pudiera haber múltiples respuestas válidas?"** → Devolver lista de listas. Cambiar dict a dict de listas.
- **"Y si en lugar de pares quisieras tripletas (3Sum)?"** → Ordenar + bucle externo + two pointers (O(n²)). Es LC 15.
- **"Y si el array fuera infinito (stream)?"** → Diseñar una estructura `add()` + `find()`. Es LC 170.
- **"Cuál es el peor caso espacial de tu solución?"** → O(n) cuando la solución está en los dos últimos elementos: hemos guardado n-1 antes de encontrarla.
- **"Por qué hash map y no `Counter`?"** → Counter cuenta frecuencias; aquí no nos interesan frecuencias sino **posiciones (índices)**. El value del dict tiene que ser el índice, no la cuenta.

---

## Solución en C++ — contraste con Python

> Añadido para ver las diferencias de lenguaje. Mismo algoritmo, distinta semántica. Código compilable en [`1-two-sum.cpp`](1-two-sum.cpp).

```cpp
class Solution {
 public:
  std::vector<int> twoSum(std::vector<int>& nums, int target) {
    std::unordered_map<int, int> seen;       // valor -> índice (Python: dict)
    for (int i = 0; i < (int)nums.size(); ++i) {
      int need = target - nums[i];
      auto it = seen.find(need);
      if (it != seen.end()) return {it->second, i};
      seen[nums[i]] = i;
    }
    return {};
  }
};
```

**Análisis:** Tiempo O(n), Espacio O(n) — igual que el Python idiomático.

**Diferencias clave Python ↔ C++:**
- `dict` → `std::unordered_map<int,int>`.
- `if need in seen` → `seen.find(need)` devuelve un **iterador**; comparar con `seen.end()` es el "no está" (no hay `in`).
- `enumerate(nums)` → índice manual `for (int i=0; ...)`; C++ no tiene `enumerate`.
- Devolver `[i, j]` → `return {it->second, i};` (lista de inicialización; el tipo de retorno fija que es `vector<int>`).

---

## Conexiones

- [[217-contains-duplicate]] — set: "¿he visto X?".
- [[242-valid-anagram]] — dict para frecuencias: "¿cuántas veces he visto X?".
- **Este problema** — dict para índices: "¿dónde vi el complemento de X?".
- Próximo recomendado: **LC 49 — Group Anagrams** (dict de listas) o **LC 347 — Top K Frequent Elements** (Counter + heap, primer roce con priority queue).

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 3 (one-pass) desde cero sin mirar
- [ ] Trace mental hecho con array `[3, 3]` y entendido por qué funciona
- [ ] Justificada la diferencia one-pass vs two-pass (la guarda `!= i`)
- [ ] Resuelto en LeetCode con éxito (Accepted en una sola submission)
- [ ] Sé explicar por qué Two Pointers NO aplica aquí pero sí en LC 167
- [ ] Hecho el problema 1 vez más a la semana siguiente
