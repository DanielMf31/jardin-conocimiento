---
title: "LeetCode 128 — Longest Consecutive Sequence"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/arrays-hashing, patron/hash-set, patron/analisis-amortizado]
type: nota
status: en-progreso
source: claude-code
aliases: [Longest Consecutive Sequence, LC 128, longestConsecutive, Secuencia consecutiva más larga]
problem_id: 128
difficulty: medium
patron: arrays-hashing
neetcode_order: 9
---

# LeetCode 128 — Longest Consecutive Sequence

> **Noveno y último problema del NeetCode 150 en Arrays & Hashing**. Es **el más conceptualmente exigente** del bloque. Demuestra el truco más bonito del patrón: un algoritmo que **parece O(n²) pero es O(n)** por análisis amortizado. Cuando lo entiendes, te queda un patrón que reaparece muchas veces.
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un array de enteros **no ordenado** `nums`, devuelve la **longitud de la secuencia consecutiva de enteros más larga**.

**Tu algoritmo debe correr en O(n) tiempo.**

**Ejemplo 1:**
```
Input:  nums = [100, 4, 200, 1, 3, 2]
Output: 4
        Explicación: la secuencia [1, 2, 3, 4] tiene longitud 4
```

**Ejemplo 2:**
```
Input:  nums = [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]
Output: 9
        Explicación: la secuencia [0, 1, 2, 3, 4, 5, 6, 7, 8] tiene longitud 9
```

**Restricciones:**
- `0 <= nums.length <= 10^5`.
- `-10^9 <= nums[i] <= 10^9`.

**Plantilla:**
```python
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` — solo la longitud, no la secuencia |
| ¿Los números deben estar contiguos en el array? | **NO** — solo deben formar una secuencia de enteros consecutivos en valor |
| ¿Hay duplicados? | Sí pueden existir — no contribuyen al largo (un set los elimina) |
| ¿Está ordenado? | NO. Si lo estuviera sería trivial |
| ¿Cuál es el mejor ratio O()? | O(n) — el follow-up es la dificultad real |
| Edge case 1 | Array vacío → 0 |
| Edge case 2 | Un solo elemento → 1 |
| Edge case 3 | Todos iguales → 1 (el set tiene un único elemento) |

---

## Solución 1 — Sort + linear scan (NO cumple O(n))

Ordenar y contar secuencias consecutivas.

```python
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        if not nums:
            return 0
        nums = sorted(set(nums))                # set para eliminar duplicados
        longest = 1
        current = 1
        for i in range(1, len(nums)):
            if nums[i] == nums[i-1] + 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest
```

**Análisis:**
- **Tiempo: O(n log n)** — el sort domina.
- **Espacio: O(n)** — el set.
- **Veredicto:** correcta pero **no cumple el O(n)** del enunciado. Aceptable como warm-up; un entrevistador estricto pedirá optimizar.

---

## Solución 2 — Hash set + check de "soy inicio" (la canónica O(n))

**La idea clave**: para hacer O(n), **no tiene sentido empezar a contar desde cualquier número**. Solo desde el **inicio** de cada secuencia. Un número `n` es inicio de una secuencia si `n - 1` no está en el set (no hay nadie por debajo).

Una vez sabes que `n` es inicio, cuentas hacia adelante: `n+1, n+2, ...` mientras estén en el set.

```python
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        nums_set = set(nums)
        longest = 0

        for n in nums_set:
            if n - 1 not in nums_set:           # n es inicio de secuencia
                length = 1
                while n + length in nums_set:
                    length += 1
                longest = max(longest, length)

        return longest
```

**Trace mental con `nums = [100, 4, 200, 1, 3, 2]`**:

| `n` (del set) | ¿n-1 en set? | ¿Es inicio? | Cuenta hacia adelante | Longitud |
|---|---|---|---|---|
| 100 | NO (99 no está) | Sí | 100 (101 no está) | 1 |
| 4 | SÍ (3 sí) | NO | (skip) | — |
| 200 | NO (199 no está) | Sí | 200 (201 no está) | 1 |
| 1 | NO (0 no está) | **Sí** | 1, 2, 3, 4 (5 no) | **4** |
| 3 | SÍ (2 sí) | NO | (skip) | — |
| 2 | SÍ (1 sí) | NO | (skip) | — |

Resultado: `longest = 4`. [OK]

### Por qué esto es O(n) y no O(n²)

A primera vista parece O(n²): hay un bucle externo de n iteraciones, y dentro un `while` que puede recorrer hasta n elementos.

**Análisis amortizado**: el `while` interior **solo se ejecuta para los `n` que son inicio de secuencia**. Cada elemento del set se visita:
- **1 vez** como `n` en el bucle externo.
- **A lo sumo 1 vez** como parte del `while` interior (porque solo se cuenta hacia adelante desde el inicio de su secuencia).

Total: **2n visitas máximo** → O(n).

**Análisis:**
- **Tiempo: O(n)** amortizado.
- **Espacio: O(n)** — el set.
- **Veredicto:** [OK] **la respuesta esperada en entrevista**. Cumple O(n) y revela el truco amortizado.

> **Lección de análisis amortizado**: no siempre el peor caso por iteración determina la complejidad total. A veces el "trabajo total" se distribuye desigualmente y el promedio es lineal. Este patrón aparece en otros sitios: stack monotónico, sliding window con dos punteros, etc.

---

## Solución 3 — Union-Find (alternativa más compleja)

Usar Union-Find (Disjoint Set Union) para unir cada número con su sucesor si está en el set. Al final, encontrar el conjunto más grande.

```python
class UnionFind:
    def __init__(self):
        self.parent = {}
        self.size = {}

    def add(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.size[x] = 1

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]    # path compression
            x = self.parent[x]
        return x

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self.size[px] < self.size[py]:
            px, py = py, px
        self.parent[py] = px
        self.size[px] += self.size[py]

class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        if not nums:
            return 0
        uf = UnionFind()
        for n in set(nums):
            uf.add(n)
        for n in set(nums):
            if n + 1 in uf.parent:
                uf.union(n, n + 1)
        return max(uf.size.values())
```

**Análisis:**
- **Tiempo: O(n · α(n))** ≈ O(n) (α es la inversa de Ackermann, prácticamente constante).
- **Espacio: O(n)**.
- **Veredicto:** funciona pero **mucho más complejo** que la Solución 2. Útil saber que existe; en entrevista nadie la espera para este problema. Union-Find brilla en problemas de conectividad (LC 200, 305, 547).

---

## El patrón general — "Hash set + análisis amortizado / búsqueda desde anclas"

**Cuándo aplicar**:

> Cuando el problema parece pedir O(n²) por la fuerza bruta, pero puedes evitar trabajo redundante identificando **anclas** (puntos de inicio que no han sido cubiertos por iteraciones anteriores) y procesando cada elemento un número constante de veces.

**Plantilla mental**:

```python
def patron_anclas(elementos):
    s = set(elementos)
    mejor = 0
    for elem in s:
        if es_inicio(elem, s):              # check de ancla
            longitud = 1
            siguiente = funcion_siguiente(elem)
            while siguiente in s:
                longitud += 1
                siguiente = funcion_siguiente(siguiente)
            mejor = max(mejor, longitud)
    return mejor
```

**Tres señales** del patrón:

1. El problema pide la **secuencia/cadena/run más largo** de algo.
2. La fuerza bruta es O(n²) o O(n log n) por sort + scan.
3. Hay una **relación de orden o sucesión** que permite identificar "puntos de inicio" naturales.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **300. Longest Increasing Subsequence** | No consecutivos sino **estrictamente crecientes** → DP O(n log n) |
| **674. Longest Continuous Increasing Subsequence** | Consecutivos en el array (no en valor) → linear scan trivial |
| **485. Max Consecutive Ones** | Mismo patrón con bool en vez de int |
| **1004. Max Consecutive Ones III** | Sliding window con tolerancia |

---

## Conceptos a interiorizar

### Análisis amortizado — la idea

A veces el trabajo "por iteración" varía pero el **trabajo total** está acotado. La complejidad amortizada es **trabajo total / número de iteraciones**.

**Ejemplos clásicos**:
- **Dynamic array (Python list, C++ vector)**: append es O(1) **amortizado** aunque a veces requiera reallocation O(n).
- **Stack monotónico**: cada elemento entra y sale del stack como mucho 1 vez → O(n) total.
- **Two pointers / sliding window**: cada puntero avanza como mucho n veces → O(n).
- **Este problema**: cada elemento se "toca" en un `while` como mucho 1 vez → O(n).

> **Si ves "doble bucle pero cada elemento se procesa una vez"**, sospecha amortización. Es una idea repetida.

### Iterar sobre `set` vs `list`

```python
nums = [1, 2, 3, 1, 2]
nums_set = set(nums)              # {1, 2, 3}

for x in nums_set:                # itera 3 veces (sin duplicados)
    ...

for x in nums:                    # itera 5 veces (con duplicados)
    ...
```

**Por qué iterar sobre el set**: evita procesar duplicados varias veces. En este problema, si iterases sobre `nums` y hubiera muchos duplicados de un número que es inicio de secuencia, contarías la misma secuencia muchas veces. Iterar sobre el set lo evita por construcción.

### `set(nums)` deduplica — efecto secundario útil

```python
nums = [1, 1, 2, 3, 3, 4]
set(nums)                         # {1, 2, 3, 4}
```

Esto es exactamente lo que quieres: las secuencias consecutivas no se "alargan" por duplicados.

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Cumple O(n) | Veredicto |
|---|---|---|---|---|
| 1. Sort + scan | O(n log n) | O(n) | [NO] | Acepta pero no entrevista |
| 2. **Hash set + ancla** | **O(n)** amort. | O(n) | [OK] | [OK] La canónica |
| 3. Union-Find | O(n·α(n)) | O(n) | [OK] | Demasiado para este problema |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** (set + ancla) desde cero.
2. **Justifica el O(n) amortizado** con tus propias palabras. Si tienes que dudar, vuelve aquí y reléelo.
3. Trace mental con `nums = [100, 4, 200, 1, 3, 2]` enumerando para cada `n` del set:
   - ¿Es inicio? (¿está `n-1`?)
   - Si es inicio, longitud final.
4. Trace mental con `nums = [0, 0, 0, 0, 0]`. ¿Resultado?
5. **Bonus** — modifica para que devuelva la **secuencia misma**, no solo su longitud. ¿Cuánto cambia?
6. **Bonus 2** — ¿qué pasa si los enteros son enormes (e.g. 10^18)? ¿Sigue siendo O(n)?

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué iteras sobre `nums_set` y no sobre `nums`?"** → Para evitar procesar duplicados (que no afectan al largo de la secuencia) y para tener la complejidad correcta.
- **"¿Por qué solo cuentas hacia adelante y no en ambos sentidos?"** → Si contaras en ambos sentidos desde cualquier `n`, **la misma secuencia se contaría desde cada uno de sus elementos** → O(n²). El check de "soy inicio" es lo que rompe esa redundancia.
- **"¿Cuál es la complejidad amortizada y por qué?"** → O(n) porque el `while` interior solo se ejecuta para inicios, y cada elemento aparece a lo sumo en una secuencia.
- **"¿Cómo lo harías sin hash set (e.g. en un lenguaje sin sets nativos)?"** → Sort + scan O(n log n). Hash set es lo que da el O(n).

---

## Cierre del patrón Arrays & Hashing

Has llegado al **último problema del primer patrón del NeetCode 150**. Resumen de los **9 problemas** y la "info clave en el dict":

| # | Problema | Estructura | Info clave | Idea distintiva |
|---|---|---|---|---|
| 1 | [[217-contains-duplicate]] | set | nada (presencia binaria) | "He visto X antes" |
| 2 | [[242-valid-anagram]] | dict / Counter / array 26 | frecuencia | "He visto X cuántas veces" |
| 3 | [[1-two-sum]] | dict | índice | "He visto el complemento de X" |
| 4 | [[49-group-anagrams]] | defaultdict(list) | clave canónica | Agrupar por equivalencia |
| 5 | [[347-top-k-frequent-elements]] | Counter + heap / bucket | top-K | Heap O(n log k) o bucket O(n) |
| 6 | [[271-encode-and-decode-strings]] | length-prefix | — | Diseño de protocolo |
| 7 | [[238-product-of-array-except-self]] | prefix/suffix | acumulador | Un acumulador por dirección |
| 8 | [[36-valid-sudoku]] | set + claves compuestas | restricción tipada | Múltiples constraints en una estructura |
| 9 | **Este** | set + ancla | inicio de secuencia | Análisis amortizado |

**Después de Arrays & Hashing**, el siguiente patrón es **Two Pointers**, que extiende muchas de estas ideas a arrays ordenados. Avísame cuando estés listo y lo arrancamos.

---

## Conexiones

- [[217-contains-duplicate]] · [[242-valid-anagram]] · [[1-two-sum]] · [[49-group-anagrams]] · [[347-top-k-frequent-elements]] · [[271-encode-and-decode-strings]] · [[238-product-of-array-except-self]] · [[36-valid-sudoku]] — todos los problemas del patrón.
- Próximo patrón: **Two Pointers** (avísame cuando quieras arrancarlo).

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Justificado el O(n) amortizado en mis propias palabras
- [ ] Trace mental hecho con caso de duplicados (Bonus 4)
- [ ] Resuelto en LeetCode con éxito
- [ ] Hecho 1 vez más a la semana siguiente
- [ ] **Patrón Arrays & Hashing cerrado** [OK]
