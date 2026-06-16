---
title: "LeetCode 238 — Product of Array Except Self"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/arrays-hashing, patron/prefix-suffix]
type: nota
status: en-progreso
source: claude-code
aliases: [Product Except Self, LC 238, productExceptSelf, Prefix-suffix products]
problem_id: 238
difficulty: medium
patron: arrays-hashing
neetcode_order: 7
---

# LeetCode 238 — Product of Array Except Self

> 🎯 **Séptimo problema del NeetCode 150 en Arrays & Hashing**. Es la introducción al patrón **Prefix / Suffix products** (versión multiplicativa de prefix sums). Un patrón fundamental que vuelve a aparecer en sumas de subarrays, ranges queries, y muchísimos problemas Medium/Hard.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un array de enteros `nums`, devuelve un array `answer` tal que `answer[i]` es **el producto de todos los elementos de `nums` excepto `nums[i]`**.

**Tu algoritmo debe correr en O(n) tiempo y NO usar la operación de división.**

**Ejemplo 1:**
```
Input:  nums = [1, 2, 3, 4]
Output: [24, 12, 8, 6]
        Explicación:
        answer[0] = 2*3*4 = 24
        answer[1] = 1*3*4 = 12
        answer[2] = 1*2*4 = 8
        answer[3] = 1*2*3 = 6
```

**Ejemplo 2:**
```
Input:  nums = [-1, 1, 0, -3, 3]
Output: [0, 0, 9, 0, 0]
```

**Restricciones:**
- `2 <= nums.length <= 10^5`
- `-30 <= nums[i] <= 30`
- **El producto de cualquier prefijo o sufijo de `nums` cabe en un `int` de 32 bits**.

> 💡 **Follow-up**: ¿puedes hacerlo en **O(1) espacio extra** (sin contar el array de salida)?

**Plantilla:**
```python
class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `List[int]` de mismo tamaño que `nums` |
| ¿Puede haber ceros? | Sí — y el caso de un solo cero es interesante |
| ¿Y si hay dos ceros? | Todo el output es 0 |
| ¿Está prohibida la división? | Sí, **explícitamente** |
| ¿Por qué prohíben la división? | Para forzar pensar en prefix/suffix. Y porque con ceros la división rompe |
| ¿El array de salida cuenta como espacio extra? | NO en LeetCode (convención) |

---

## Solución 1 — Fuerza bruta (NO cumple restricciones)

Para cada `i`, recorrer todo el array multiplicando excepto `nums[i]`.

```python
class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        answer = []
        for i in range(n):
            prod = 1
            for j in range(n):
                if j != i:
                    prod *= nums[j]
            answer.append(prod)
        return answer
```

**Análisis:**
- **Tiempo: O(n²)** — viola la restricción.
- **Espacio: O(1)** extra.
- **Veredicto:** ❌ TLE con n = 10^5.

---

## Solución 2 — Con división (PROHIBIDA pero útil de comentar)

Calcular el producto total, luego dividir por cada `nums[i]`.

```python
# ❌ NO usar — solo educativa
def productExceptSelf(self, nums):
    total = 1
    for n in nums:
        total *= n
    return [total // n for n in nums]
```

**Por qué se prohíbe:**

1. **División entera con ceros**: si hay un 0 en `nums`, `total // 0` da error.
2. **Manejar ceros caso por caso es feo**: hay que distinguir 0 ceros / 1 cero / ≥2 ceros.
3. **División es operación cara** comparada con suma/multiplicación a nivel de hardware.

> 📌 **Lección**: cuando un enunciado prohíbe una operación, casi siempre es porque (a) revela un patrón más interesante, o (b) la operación falla en un edge case crítico.

---

## Solución 3 — Prefix * Suffix products (la canónica)

**La idea clave**: para cada `i`, el resultado es el producto de:
- Todos los elementos **a la izquierda** de `i` (prefix product) ×
- Todos los elementos **a la derecha** de `i` (suffix product).

Calcular dos arrays auxiliares: `prefix[i]` y `suffix[i]`. Luego `answer[i] = prefix[i] * suffix[i]`.

```python
class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        prefix = [1] * n
        suffix = [1] * n

        # prefix[i] = producto de nums[0..i-1]
        for i in range(1, n):
            prefix[i] = prefix[i-1] * nums[i-1]

        # suffix[i] = producto de nums[i+1..n-1]
        for i in range(n-2, -1, -1):
            suffix[i] = suffix[i+1] * nums[i+1]

        return [prefix[i] * suffix[i] for i in range(n)]
```

**Trace mental con `nums = [1, 2, 3, 4]`**:

| i | prefix[i] | suffix[i] | answer[i] |
|---|---|---|---|
| 0 | 1 (nada a la izquierda) | 2*3*4 = 24 | 24 |
| 1 | 1 | 3*4 = 12 | 12 |
| 2 | 1*2 = 2 | 4 | 8 |
| 3 | 1*2*3 = 6 | 1 (nada a la derecha) | 6 |

**Análisis:**
- **Tiempo: O(n)** — tres recorridos lineales.
- **Espacio: O(n)** extra (los dos arrays auxiliares).
- **Veredicto:** ✅ correcta y clara. Cumple O(n) tiempo pero no el follow-up de O(1) espacio.

### Desglose detallado de la Solución 3 — paso por paso con índices

#### Qué representan `prefix` y `suffix` (la visión geométrica)

Para un índice `i`, queremos `result[i] = producto_de_todos_los_otros`. Eso es:

```
nums = [a, b, c, d, e]    (n=5)

result[2] = a * b *  _  * d * e   (todo menos c)
            └─────┘    └─────┘
           prefix[2]   suffix[2]
            "lo que   "lo que
           hay a la   hay a la
          izquierda" derecha"
```

**Definiciones precisas**:
- `prefix[i]` = producto de **todos los elementos estrictamente a la izquierda** de `i` (sin incluir `nums[i]`).
- `suffix[i]` = producto de **todos los elementos estrictamente a la derecha** de `i` (sin incluir `nums[i]`).

**Casos borde**:
- `prefix[0] = 1` (no hay nada a la izquierda → producto vacío = 1).
- `suffix[n-1] = 1` (no hay nada a la derecha → producto vacío = 1).

Por eso inicializamos ambos con `[1] * n` (la primera entrada de prefix y la última de suffix ya están correctas; las demás se calculan).

#### Recurrencia y dirección de cada bucle

**Prefix — de izquierda a derecha**:

```
prefix[i] = prefix[i-1] * nums[i-1]
            └─────┬────┘   └────┬───┘
        "lo que ya tenía     "el último
         a la izquierda      elemento que
         del índice i-1"     se queda a la
                            izquierda de i"
```

Como necesita `prefix[i-1]` (el de la izquierda), tienes que ir **de izquierda a derecha**. Por eso `for i in range(1, n)`: empiezas en 1 (porque `prefix[0]` ya es 1) y avanzas hacia adelante.

**Suffix — de derecha a izquierda**:

```
suffix[i] = suffix[i+1] * nums[i+1]
            └─────┬────┘   └────┬───┘
         "lo que ya tenía    "el primer
          a la derecha        elemento que
          del índice i+1"    se queda a la
                            derecha de i"
```

Aquí hay un giro: necesita `suffix[i+1]` (el de la **derecha**). Para que esté disponible cuando calcules `suffix[i]`, **tienes que haber calculado `suffix[i+1]` antes**. Por eso vas **de derecha a izquierda**. Eso es lo que hace ese `range(n-2, -1, -1)`.

#### `range(n-2, -1, -1)` desmenuzado

`range(start, stop, step)` tiene **tres argumentos**:

| Argumento | Significado |
|---|---|
| `start` | Por dónde empezar (incluido) |
| `stop` | Dónde parar (NO incluido) |
| `step` | Cuánto avanzar en cada paso (puede ser negativo) |

Ejemplos sencillos:

```python
list(range(5))               # [0, 1, 2, 3, 4]               step=1 implícito
list(range(2, 5))            # [2, 3, 4]                      empieza en 2
list(range(0, 10, 2))        # [0, 2, 4, 6, 8]                step=2
list(range(5, 0, -1))        # [5, 4, 3, 2, 1]                step=-1: hacia atrás
list(range(5, -1, -1))       # [5, 4, 3, 2, 1, 0]             ojo: stop=-1 incluye 0
```

> ⚠️ **Para descender hasta `0` inclusive** tienes que usar `stop=-1`, no `stop=0`. Porque `stop` **no se incluye**: si pusieras `range(5, 0, -1)` te quedas en 1, no llegas a 0.

Aplicado al código: con `n = 4`,

```python
range(n-2, -1, -1) = range(2, -1, -1)
```

produce: `[2, 1, 0]` (los tres índices que faltan por calcular en suffix).

**Por qué cada número**:
- `start = n-2`: empezamos en el penúltimo índice. El último (n-1) ya tiene `suffix[n-1] = 1`.
- `stop = -1`: queremos llegar hasta `0` inclusive. Como `range` no incluye `stop`, ponemos -1.
- `step = -1`: vamos hacia atrás de 1 en 1.

#### Trace completo con `nums = [1, 2, 3, 4]`

`n = 4`. Inicialización: `prefix = [1, 1, 1, 1]`, `suffix = [1, 1, 1, 1]`.

**Pasada 1 — prefix forward (`range(1, 4)` → `[1, 2, 3]`)**:

```
Índice nums:  0  1  2  3
nums:        [1, 2, 3, 4]

i=1: prefix[1] = prefix[0] * nums[0]
              =    1       *    1     = 1
                                            prefix = [1, 1, 1, 1]
                                                        ↑
                                                     no cambia (era 1)

i=2: prefix[2] = prefix[1] * nums[1]
              =    1       *    2     = 2
                                            prefix = [1, 1, 2, 1]
                                                           ↑

i=3: prefix[3] = prefix[2] * nums[2]
              =    2       *    3     = 6
                                            prefix = [1, 1, 2, 6]
                                                              ↑
```

**Lectura de `prefix` final**:
- `prefix[0] = 1` (nada a la izquierda de índice 0)
- `prefix[1] = 1` (a la izquierda de 1 solo está nums[0]=1, producto=1)
- `prefix[2] = 2` (a la izquierda de 2: nums[0]*nums[1] = 1*2 = 2)
- `prefix[3] = 6` (a la izquierda de 3: nums[0]*nums[1]*nums[2] = 1*2*3 = 6)

**Pasada 2 — suffix backward (`range(2, -1, -1)` → `[2, 1, 0]`)**:

```
Índice nums:  0  1  2  3
nums:        [1, 2, 3, 4]

i=2: suffix[2] = suffix[3] * nums[3]
              =    1       *    4     = 4
                                            suffix = [1, 1, 4, 1]
                                                            ↑

i=1: suffix[1] = suffix[2] * nums[2]
              =    4       *    3     = 12
                                            suffix = [1, 12, 4, 1]
                                                         ↑

i=0: suffix[0] = suffix[1] * nums[1]
              =   12       *    2     = 24
                                            suffix = [24, 12, 4, 1]
                                                       ↑
```

**Lectura de `suffix` final**:
- `suffix[3] = 1` (nada a la derecha del último)
- `suffix[2] = 4` (a la derecha de 2 solo está nums[3]=4)
- `suffix[1] = 12` (a la derecha de 1: nums[2]*nums[3] = 3*4 = 12)
- `suffix[0] = 24` (a la derecha de 0: nums[1]*nums[2]*nums[3] = 2*3*4 = 24)

**Pasada 3 — combinar**:

```
Índice:        0    1    2    3
prefix:       [1,   1,   2,   6]
suffix:      [24,  12,   4,   1]
result:      [24,  12,   8,   6]
              │    │    │    │
              1*24 1*12 2*4  6*1
```

**Verificación**:
- `result[0] = 24 = 2*3*4` ✅
- `result[1] = 12 = 1*3*4` ✅
- `result[2] = 8 = 1*2*4` ✅
- `result[3] = 6 = 1*2*3` ✅

#### Regla mental — cuándo bucle hacia adelante, cuándo hacia atrás

La dirección del bucle viene determinada por **la dirección de la dependencia**.

| Tipo | Recurrencia | Dependencia | Dirección |
|---|---|---|---|
| `prefix[i] = prefix[i-1] * ...` | depende de **i-1** (izquierda) | hay que tener i-1 listo antes que i | **adelante** (i = 1, 2, 3...) |
| `suffix[i] = suffix[i+1] * ...` | depende de **i+1** (derecha) | hay que tener i+1 listo antes que i | **atrás** (i = n-2, n-3, ..., 0) |

**Cuándo lo veas en otros problemas**: cualquier acumulador que dependa del vecino derecho **necesita ir hacia atrás**. Es la misma idea que en [[42-trapping-rain-water]] (max_left va hacia adelante, max_right va hacia atrás), y reaparecerá en muchos problemas de patrón DP, Trees y Linked Lists.

---

## Solución 4 — Prefix * Suffix in-place O(1) espacio (la óptima)

**La idea clave del follow-up**: el array `answer` puede servir simultáneamente como prefix array. Después, en una segunda pasada de derecha a izquierda, se multiplica in-place por el suffix usando una **sola variable** acumuladora.

```python
class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        answer = [1] * n

        # Pasada 1: answer[i] = producto de todos los anteriores (prefix)
        prefix = 1
        for i in range(n):
            answer[i] = prefix
            prefix *= nums[i]

        # Pasada 2: multiplicar por suffix de derecha a izquierda
        suffix = 1
        for i in range(n-1, -1, -1):
            answer[i] *= suffix
            suffix *= nums[i]

        return answer
```

### La intuición del truco

A diferencia de la Solución 3, aquí **NO hay arrays auxiliares**. El array `answer` se "rellena por capas":

- **Pasada 1 (forward)**: en `answer[i]` guardas el **prefix product** correspondiente. Al terminar, `answer` contiene los prefix products (no el resultado final).
- **Pasada 2 (backward)**: multiplicas cada `answer[i]` por el **suffix product** correspondiente, calculado on-the-fly con una sola variable.

Las dos variables `prefix` y `suffix` son **acumuladoras de un solo número** — sustituyen los arrays auxiliares de la Solución 3.

### Trace visual completo con `nums = [1, 2, 3, 4]`

`n = 4`. Inicialización: `answer = [1, 1, 1, 1]`, `prefix = 1`.

#### Pasada 1 — prefix forward (`range(0, 4)` → `[0, 1, 2, 3]`)

```
Estado inicial:
  Índice:     0  1  2  3
  nums:      [1, 2, 3, 4]
  answer:    [1, 1, 1, 1]
  prefix = 1

i=0:
  (a) answer[0] = prefix → answer[0] = 1

      Índice:     0  1  2  3
      answer:    [1, 1, 1, 1]    ← no cambia (era 1)
                  ↑

  (b) prefix *= nums[0] → prefix = 1 * 1 = 1

i=1:
  (a) answer[1] = prefix → answer[1] = 1

      Índice:     0  1  2  3
      answer:    [1, 1, 1, 1]    ← no cambia (era 1)
                     ↑

  (b) prefix *= nums[1] → prefix = 1 * 2 = 2

i=2:
  (a) answer[2] = prefix → answer[2] = 2

      Índice:     0  1  2  3
      answer:    [1, 1, 2, 1]    ← era 1, ahora 2
                        ↑

  (b) prefix *= nums[2] → prefix = 2 * 3 = 6

i=3:
  (a) answer[3] = prefix → answer[3] = 6

      Índice:     0  1  2  3
      answer:    [1, 1, 2, 6]    ← era 1, ahora 6
                           ↑

  (b) prefix *= nums[3] → prefix = 6 * 4 = 24    (ya no se usa)

Estado tras pasada 1:
  Índice:     0  1  2  3
  answer:    [1, 1, 2, 6]   ← contiene los prefix products
                              (lo que hay a la izquierda de cada índice)
```

> 💡 **Observación clave**: tras la pasada 1, `answer[i]` es el producto de **todo lo que está estrictamente a la izquierda** de `i`. Para `i=0`, no hay nada a la izquierda → 1. Para `i=3`, hay 1*2*3 = 6.

#### Pasada 2 — suffix backward (`range(3, -1, -1)` → `[3, 2, 1, 0]`)

```
Estado inicial pasada 2:
  Índice:     0  1  2  3
  nums:      [1, 2, 3, 4]
  answer:    [1, 1, 2, 6]    ← lo que dejó pasada 1
  suffix = 1

i=3:
  (a) answer[3] *= suffix → answer[3] = 6 * 1 = 6

      Índice:     0  1  2  3
      answer:    [1, 1, 2, 6]    ← no cambia (6*1=6)
                           ↑

  (b) suffix *= nums[3] → suffix = 1 * 4 = 4

i=2:
  (a) answer[2] *= suffix → answer[2] = 2 * 4 = 8

      Índice:     0  1  2  3
      answer:    [1, 1, 8, 6]    ← era 2, ahora 8
                        ↑

  (b) suffix *= nums[2] → suffix = 4 * 3 = 12

i=1:
  (a) answer[1] *= suffix → answer[1] = 1 * 12 = 12

      Índice:     0   1  2  3
      answer:    [1, 12, 8, 6]   ← era 1, ahora 12
                      ↑

  (b) suffix *= nums[1] → suffix = 12 * 2 = 24

i=0:
  (a) answer[0] *= suffix → answer[0] = 1 * 24 = 24

      Índice:      0   1  2  3
      answer:    [24, 12, 8, 6]  ← era 1, ahora 24
                  ↑

  (b) suffix *= nums[0] → suffix = 24 * 1 = 24    (ya no se usa)

Estado final:
  Índice:      0   1  2  3
  answer:    [24, 12, 8, 6]    ✅
```

**Verificación**:
- `answer[0] = 24 = 2*3*4` ✅
- `answer[1] = 12 = 1*3*4` ✅
- `answer[2] = 8 = 1*2*4` ✅
- `answer[3] = 6 = 1*2*3` ✅

### Resumen visual: cómo evoluciona `answer` en las dos pasadas

```
Inicio:                Índice:    0  1  2  3
                       answer:   [1, 1, 1, 1]

Tras pasada 1:                   [1, 1, 2, 6]
                                  ─────────────
                                  estos son los prefix products

Tras pasada 2:                   [24, 12, 8, 6]
                                  ─────────────
                                  prefix * suffix = resultado final

Cada answer[i] al final = prefix_i × suffix_i
       answer[0] = 1 × 24 = 24
       answer[1] = 1 × 12 = 12
       answer[2] = 2 × 4  = 8
       answer[3] = 6 × 1  = 6
```

### Por qué `answer[i] = prefix` se hace ANTES de `prefix *= nums[i]`

Es un detalle sutil pero crítico:

```python
for i in range(n):
    answer[i] = prefix          # (a) ← primero asignar el prefix ACTUAL
    prefix *= nums[i]           # (b) ← luego incorporar nums[i]
```

**Por qué este orden**: cuando asignas `answer[i]`, el prefix **no debe incluir `nums[i]`** todavía (recuerda: prefix[i] = producto de los anteriores, **sin** `nums[i]`). Por eso primero usas `prefix` y después lo multiplicas por `nums[i]` (preparándolo para la siguiente iteración).

Si invirtieras el orden:

```python
for i in range(n):
    prefix *= nums[i]           # ❌ ya incluye nums[i]
    answer[i] = prefix          # answer[i] tendría producto que SÍ incluye nums[i] — INCORRECTO
```

El mismo razonamiento aplica a la pasada 2 con `suffix`: primero multiplicas `answer[i]` por el `suffix` actual, después incorporas `nums[i]`.

**Análisis:**
- **Tiempo: O(n)** — dos pasadas lineales.
- **Espacio: O(1)** extra — solo dos variables `prefix` y `suffix`.
- **Veredicto:** ✅ **la óptima**. Cumple las dos restricciones (O(n) tiempo, O(1) espacio extra). Es la respuesta esperada en entrevistas tecnicas.

---

## El patrón general — "Prefix / Suffix accumulator"

**Cuándo aplicar**:

> Cuando necesitas, para cada índice `i`, una **agregación (suma, producto, max, ...) de todos los elementos excepto `nums[i]`**, o de los elementos en uno o ambos lados de `i`.

**Plantilla mental** (versión más general — sumas):

```python
def patron_prefix_suffix(nums):
    n = len(nums)
    prefix = [identidad] * n            # 0 para suma, 1 para producto
    suffix = [identidad] * n
    for i in range(1, n):
        prefix[i] = combinar(prefix[i-1], nums[i-1])
    for i in range(n-2, -1, -1):
        suffix[i] = combinar(suffix[i+1], nums[i+1])
    return [combinar(prefix[i], suffix[i]) for i in range(n)]
```

Donde `combinar` puede ser `+`, `*`, `max`, `min`, etc., y `identidad` es el elemento neutro (`0`, `1`, `-inf`, `+inf`).

**Tres señales** del patrón:

1. Output `answer[i]` depende de "todo menos `nums[i]`" o "lados separados".
2. La operación de combinación es **asociativa** (puede partirse en izquierda + derecha).
3. La fuerza bruta es O(n²) y se ve obvio que se puede precomputar.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **303. Range Sum Query - Immutable** | Prefix sum clásico → consultas O(1) |
| **560. Subarray Sum Equals K** | Prefix sum + hash map → conexión con [[1-two-sum]] |
| **42. Trapping Rain Water** | Prefix max + suffix max → "altura del agua" |
| **84. Largest Rectangle in Histogram** | Prefix-stack (siguiente menor a izquierda/derecha) |
| **152. Maximum Product Subarray** | Producto **continuo** con tracking de min/max |

> 🎯 **Patrón maestro**: prefix/suffix arrays + sumas acumulativas son la base de **decenas** de problemas Medium y Hard. Los tres patrones de prefix más útiles: prefix sum, prefix max/min, prefix product. Cuando los interiorices, muchos problemas se vuelven mecánicos.

---

## Conceptos a interiorizar

### Prefix sums (la versión más común)

```python
nums = [1, 2, 3, 4]
prefix = [0]
for n in nums:
    prefix.append(prefix[-1] + n)    # [0, 1, 3, 6, 10]

# Suma del rango [i, j] (inclusivo) = prefix[j+1] - prefix[i]
# Por ejemplo, suma de nums[1..2] = prefix[3] - prefix[1] = 6 - 1 = 5
```

**Lección**: el prefix array suele tener **n+1 elementos** con `prefix[0] = 0` (identidad). Eso evita casos especiales en los bordes.

### Iteración hacia atrás

```python
for i in range(n-1, -1, -1):    # n-1, n-2, ..., 1, 0
    ...

for i in reversed(range(n)):    # equivalente, más pythonic
    ...
```

### Variable acumuladora vs array auxiliar

Cuando solo necesitas el "estado actual" del prefix (no toda la historia), una variable basta:

```python
# Con array auxiliar (espacio O(n))
prefix = [1] * n
for i in range(1, n):
    prefix[i] = prefix[i-1] * nums[i-1]

# Con variable acumuladora (espacio O(1))
prefix = 1
for i in range(n):
    answer[i] = prefix          # usar antes de actualizar
    prefix *= nums[i]
```

---

## Comparación final de las 4 soluciones

| Solución | Tiempo | Espacio extra | Cumple restricciones | Veredicto |
|---|---|---|---|---|
| 1. Fuerza bruta | O(n²) | O(1) | ❌ TLE | No |
| 2. Con división | O(n) | O(1) | ❌ Prohibida | Solo discusión |
| 3. **Prefix + Suffix arrays** | O(n) | O(n) | ✅ tiempo, ❌ espacio | ✅ Aceptable |
| 4. **Prefix + Suffix in-place** | **O(n)** | **O(1)** | ✅✅ | ✅ La óptima |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 4** (in-place, O(1) espacio) desde cero.
2. Justifica:
   - Por qué `prefix = 1` y no `0`.
   - Por qué la asignación `answer[i] = prefix` se hace **antes** de actualizar `prefix *= nums[i]`.
   - Por qué se hacen **dos pasadas** y no una.
3. Trace mental con `nums = [-1, 1, 0, -3, 3]`. ¿Por qué el resultado es `[0, 0, 9, 0, 0]`?
4. **Bonus** — implementa una variante donde calculas `answer[i] = SUMA de todos excepto nums[i]`. ¿Cambia el patrón?
5. **Bonus 2** — ¿qué pasaría con tu solución si `nums = [0, 0]`? ¿Y `nums = [0, 1, 2]`?

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué prohíben la división?"** → (a) Falla con ceros sin tratamiento especial. (b) Fuerza el patrón prefix/suffix, que es genéricamente más útil. (c) División es cara.
- **"Y si te permitieran la división, ¿cuál sería tu solución y cómo manejarías ceros?"** → Contar ceros: 0 ceros = total/nums[i]; 1 cero = solo answer[indice_cero] = producto del resto; ≥2 ceros = todo cero.
- **"Cuál es el caso peor de tu Solución 4?"** → siempre O(n) tiempo, O(1) espacio. No tiene caso peor distinto del promedio.
- **"¿Y si en lugar de excluir solo `nums[i]` quisieras excluir un rango `[l, r]`?"** → Prefix products + segment tree o similar.

---

## Conexiones

- [[1-two-sum]] — patrón "el complemento" para pares.
- Próximo: [[36-valid-sudoku]] — claves compuestas en sets.
- LC 560 (Subarray Sum Equals K) usa prefix sum + hash map: combina el patrón de este problema con el de Two Sum.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 4 (in-place) desde cero
- [ ] Justificado el orden de operaciones (`answer[i] = prefix` antes de `prefix *= nums[i]`)
- [ ] Implementada variante con sumas (Bonus 1)
- [ ] Resuelto en LeetCode con éxito
- [ ] Hecho 1 vez más a la semana siguiente
