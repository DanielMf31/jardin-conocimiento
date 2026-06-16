---
title: "Python Syntax Cheatsheet — Referencia para LeetCode / NeetCode 150"
date: 2026-05-08
tags: [programacion/python, programacion/leetcode, programacion/algoritmos, referencia, cheatsheet, sintaxis]
type: nota
status: permanente
source: claude-code
aliases: [Python LeetCode Cheatsheet, Sintaxis Python LeetCode, Referencia Python algoritmos, Cheatsheet LeetCode]
---

# Python Syntax Cheatsheet — Referencia para LeetCode / NeetCode 150

> 🎯 **Objetivo**: archivo de consulta rápida con la sintaxis Python que **realmente** aparece en LeetCode. Por cada estructura: qué es, cuándo usarla, métodos clave con complejidad, ejemplos cortos, **y enlaces a los problemas NeetCode donde aparece**.
>
> 📚 **Cómo usar este archivo**: NO se lee de corrida. Se consulta cuando estás resolviendo un problema y dudas de algo concreto. Tenlo abierto en una pestaña mientras trabajas.

## Mapa rápido (clica para saltar)

1. [Listas (`list`)](#listas-list) — el array dinámico básico
2. [Tuplas (`tuple`)](#tuplas-tuple) — listas inmutables, hashables
3. [Sets (`set`)](#sets-set) — colección sin duplicados, lookup O(1)
4. [Diccionarios (`dict`)](#diccionarios-dict) — clave→valor, lookup O(1)
5. [Strings (`str`)](#strings-str) — texto inmutable
6. [`collections.Counter`](#counter) — dict para contar
7. [`collections.defaultdict`](#defaultdict) — dict con default automático
8. [`collections.deque`](#deque) — cola doblemente acabada O(1) en ambos extremos
9. [`heapq`](#heap-heapq) — min-heap (priority queue)
10. [Iteración y comprehensions](#iteración-y-comprehensions)
11. [Funciones built-in útiles](#funciones-built-in)
12. [Sintaxis pythonic común](#sintaxis-pythonic)
13. [Type hints en LeetCode](#type-hints-leetcode)
14. [Trampas y errores comunes](#trampas-comunes)
15. [Patrones de código por tipo de problema](#patrones-de-código)

---

## Listas (`list`)

> **Qué es**: array dinámico (auto-redimensionable). Ordenado, mutable, admite duplicados, indexable.
>
> **Cuándo usarla**: cuando necesitas una secuencia de elementos en orden, con acceso por índice. Es la estructura por defecto si no hay razón para otra.

### Crear
```python
nums = []                       # vacía
nums = [1, 2, 3]                # con elementos
nums = [0] * 5                  # [0, 0, 0, 0, 0] — patrón muy común
nums = list(range(5))           # [0, 1, 2, 3, 4]
nums = list("hola")             # ['h', 'o', 'l', 'a']
matriz = [[0] * 3 for _ in range(2)]   # 2x3 de ceros — ⚠️ NO uses [[0]*3]*2
```

### Métodos clave

| Operación | Coste | Ejemplo | Uso típico |
|---|---|---|---|
| `nums[i]` | O(1) | `nums[0]` | Acceso por índice |
| `nums[i] = x` | O(1) | `nums[0] = 5` | Mutar |
| `nums.append(x)` | O(1) amort. | `nums.append(7)` | Añadir al final |
| `nums.pop()` | O(1) | `nums.pop()` | Quitar y devolver el último |
| `nums.pop(0)` | **O(n)** ❌ | `nums.pop(0)` | Quitar primero — usa `deque` en su lugar |
| `nums.insert(i, x)` | O(n) | `nums.insert(0, 5)` | Insertar — caro |
| `len(nums)` | O(1) | `len(nums)` | Tamaño |
| `x in nums` | O(n) ❌ | `5 in nums` | Pertenencia — usa `set` si es frecuente |
| `nums.sort()` | O(n log n) | `nums.sort()` | Ordenar in-place |
| `sorted(nums)` | O(n log n) | `sorted(nums)` | Devuelve copia ordenada |
| `nums.reverse()` | O(n) | `nums.reverse()` | Invertir in-place |
| `nums[::-1]` | O(n) | `nums[::-1]` | Devuelve copia invertida |
| `nums.count(x)` | O(n) | `nums.count(5)` | Cuántas veces aparece |
| `nums.index(x)` | O(n) | `nums.index(5)` | Primera posición de x |

### Slicing (rebanado)

```python
nums = [0, 1, 2, 3, 4, 5]
nums[2:5]        # [2, 3, 4]      — desde 2, hasta 5 (excluido)
nums[:3]         # [0, 1, 2]      — desde principio
nums[3:]         # [3, 4, 5]      — hasta el final
nums[-2:]        # [4, 5]         — los últimos 2
nums[::-1]       # [5, 4, 3, 2, 1, 0]   — invertido
nums[::2]        # [0, 2, 4]      — uno sí, uno no
```

> ⚠️ **Slice crea una nueva lista** (O(k) donde k = tamaño del slice). No es una "vista".

### En problemas NeetCode

- [[1-two-sum]] · [[217-contains-duplicate]] · [[15-3sum]] — uso básico, iteración con `enumerate`.
- [[238-product-of-array-except-self]] — array de salida `answer = [1] * n`.
- [[49-group-anagrams]] — `list(grupos.values())` para devolver dict.values como lista.

---

## Tuplas (`tuple`)

> **Qué es**: como una lista pero **inmutable**. Una vez creada no se puede modificar. **Hashable** si todos sus elementos lo son (importante para usarla como clave de dict o elemento de set).
>
> **Cuándo usarla**: cuando agrupas valores que NO van a cambiar (un punto x,y; una clave compuesta de set; valores empaquetados de una función).

### Crear
```python
t = ()                       # vacía
t = (1,)                     # ⚠️ con un elemento, COMA obligatoria
t = (1, 2, 3)                # con varios
t = 1, 2, 3                  # paréntesis opcionales
t = tuple([1, 2, 3])         # desde lista
```

### Operaciones

```python
t = (1, 2, 3)
t[0]                         # 1
len(t)                       # 3
1 in t                       # True
a, b, c = t                  # unpacking
```

> 🎯 **El uso más típico en LeetCode**: claves compuestas en sets/dicts.

```python
seen = set()
seen.add((row, col))         # ✅ tupla hashable
seen.add([row, col])         # ❌ TypeError: list no hashable
```

### En problemas NeetCode

- [[36-valid-sudoku]] — claves compuestas `("row", r, val)` en un set.
- [[49-group-anagrams]] — `tuple(count)` como clave canónica.
- [[347-top-k-frequent-elements]] — `(freq, num)` en heap.

---

## Sets (`set`)

> **Qué es**: colección **sin duplicados** y **sin orden**. Lookup, inserción y eliminación en O(1) promedio gracias a hashing interno.
>
> **Cuándo usarla**: cuando solo te importa la **presencia** de elementos (no su cantidad ni su orden). Es **la estructura más usada** en problemas Arrays & Hashing.

### Crear
```python
s = set()                    # ⚠️ vacío. NO {} (eso es dict vacío)
s = {1, 2, 3}                # con elementos
s = set([1, 2, 2, 3])        # {1, 2, 3} — deduplica
s = set("abc")               # {'a', 'b', 'c'}
```

### Métodos clave

| Operación | Coste | Ejemplo |
|---|---|---|
| `s.add(x)` | O(1) avg | `s.add(5)` |
| `x in s` | O(1) avg | `5 in s` |
| `s.remove(x)` | O(1) avg | `s.remove(5)` — KeyError si no existe |
| `s.discard(x)` | O(1) avg | `s.discard(5)` — sin error si no existe |
| `s.pop()` | O(1) | quita un elemento arbitrario |
| `len(s)` | O(1) | tamaño |
| `s1 \| s2` | O(n+m) | unión |
| `s1 & s2` | O(min) | intersección |
| `s1 - s2` | O(n) | diferencia |

### En problemas NeetCode

- [[217-contains-duplicate]] — el caso canónico: "¿he visto X antes?".
- [[128-longest-consecutive-sequence]] — set como memoria + check de "soy inicio".
- [[36-valid-sudoku]] — set con claves compuestas.

---

## Diccionarios (`dict`)

> **Qué es**: mapa **clave → valor** con lookup O(1) promedio. Las claves deben ser hashables (immutables); los valores pueden ser cualquier cosa.
>
> **Cuándo usarlo**: cuando necesitas asociar **información** a cada elemento (no solo presencia). Ejemplos: índice, frecuencia, lista de posiciones, predecesor.

### Crear
```python
d = {}                       # vacío (sí, esto es dict, NO set)
d = {"a": 1, "b": 2}         # con elementos
d = dict(a=1, b=2)           # equivalente
d = {x: x*x for x in range(3)}   # comprehension: {0:0, 1:1, 2:4}
```

### Métodos clave

| Operación | Coste | Ejemplo |
|---|---|---|
| `d[k]` | O(1) avg | `d["a"]` — **KeyError si no existe** |
| `d.get(k, default)` | O(1) avg | `d.get("a", 0)` — sin error |
| `d.setdefault(k, default)` | O(1) avg | inserta default si k no existe Y devuelve d[k] |
| `d[k] = v` | O(1) avg | `d["a"] = 1` |
| `k in d` | O(1) avg | mira solo claves |
| `del d[k]` | O(1) avg | KeyError si no existe |
| `d.pop(k, default)` | O(1) avg | quita y devuelve |
| `len(d)` | O(1) | |
| `d.keys()` / `d.values()` / `d.items()` | iteradores | |

### `dict.get(k, default)` — el método más útil del cheatsheet

> **Qué hace**: devuelve `d[k]` si la clave existe, o `default` si no existe. **Sin lanzar error**, **sin modificar el dict**.

Tres comportamientos:

```python
d = {"a": 1, "b": 2}

d.get("a")           # 1       — clave existe → devuelve valor
d.get("a", 99)       # 1       — clave existe → ignora el default
d.get("z")           # None    — clave NO existe + sin default → None
d.get("z", 0)        # 0       — clave NO existe + default → default
```

**Compara con acceso directo**:

```python
d = {"a": 1}
d["z"]               # ❌ KeyError: 'z'
d.get("z")           # ✅ None  (no rompe)
d.get("z", 0)        # ✅ 0     (default explícito)
```

**Patrón típico en LeetCode (conteo de frecuencias)**:

```python
# Sin .get() — falla la primera vez con cada clave nueva
count = {}
for c in s:
    count[c] += 1                  # ❌ KeyError la primera vez

# Con .get() — idiomático
count = {}
for c in s:
    count[c] = count.get(c, 0) + 1     # "lo que había, o 0 si nada, +1"
```

Léelo así: **"dame `count[c]`, y si no hay nada todavía dame 0, y a eso le sumo 1"**.

> ⚠️ **`.get()` NO modifica el dict**. Si lees `d.get("z", 0)` cuando "z" no está, el dict **sigue sin tener "z"**. Si lo que querías era "léelo o insértalo si no estaba", eso es `setdefault()`:
>
> ```python
> d = {}
> d.get("z", 0)               # devuelve 0, d sigue siendo {}
> d.setdefault("z", 0)        # devuelve 0, AHORA d = {"z": 0}
> ```
>
> En LeetCode `setdefault()` casi nunca se usa — es más limpio usar `defaultdict` (sección siguiente).

### Patrón "incremental" para conteos

```python
# ❌ Falla con KeyError la primera vez
d[k] += 1

# ✅ Tres formas equivalentes
d[k] = d.get(k, 0) + 1                     # idiomática (sin imports)

from collections import defaultdict
d = defaultdict(int)
d[k] += 1                                  # con defaultdict

from collections import Counter
d = Counter(iterable)                      # más rápido si construyes desde colección
```

### En problemas NeetCode

- [[1-two-sum]] — dict como mapa valor→índice.
- [[242-valid-anagram]] — dict para frecuencias.
- [[49-group-anagrams]] — `defaultdict(list)` para agrupar.
- [[36-valid-sudoku]] — `defaultdict(set)` para múltiples constraints.

---

## Strings (`str`)

> **Qué es**: secuencia de caracteres **inmutable**. Como un tuple de chars, pero con métodos especializados.
>
> **Importante**: Python no tiene un tipo `char` separado. Un carácter es un string de longitud 1.

### Crear
```python
s = ""
s = "hola"
s = 'hola'                   # comillas dobles o simples, da igual
s = str(42)                  # "42"
s = ''.join(['h','o','l','a'])   # "hola" — patrón importante
```

### Operaciones (iguales que list, porque str es secuencia)

```python
s = "abcdef"
s[0]                         # 'a'
s[2:5]                       # 'cde'
s[::-1]                      # 'fedcba'
len(s)                       # 6
"bc" in s                    # True
```

### Métodos específicos de string

| Método                                        | Ejemplo                   | Resultado       |
| --------------------------------------------- | ------------------------- | --------------- |
| `s.lower()`                                   | `"Hola".lower()`          | `"hola"`        |
| `s.upper()`                                   | `"hola".upper()`          | `"HOLA"`        |
| `s.strip()`                                   | `"  hi  ".strip()`        | `"hi"`          |
| `s.split(sep)`                                | `"a,b,c".split(",")`      | `['a','b','c']` |
| `sep.join(lista)`                             | `",".join(['a','b'])`     | `"a,b"`         |
| `s.replace(a, b)`                             | `"hola".replace("a","á")` | `"holá"`        |
| `s.find(sub, start)`                          | `"abcabc".find("c", 3)`   | `5` (-1 si no)  |
| `s.startswith(p)` / `s.endswith(s)`           | check de prefijo/sufijo   | bool            |
| `s.isalnum()` / `s.isalpha()` / `s.isdigit()` | check de tipo             | bool            |
| `s.count(sub)`                                | `"abab".count("a")`       | `2`             |
| `f"valor: {x}"`                               | f-string                  | interpolación   |

### `str.find(sub, start)` — buscar a partir de un índice

> **Qué hace**: busca la primera aparición de `sub` (carácter o substring) dentro de `s`, **empezando desde el índice `start`**. Devuelve el **índice** donde lo encuentra, o **-1 si no existe**.

```python
texto = "hola#mundo#fin"

texto.find('#')          # 4   (primera aparición desde el inicio)
texto.find('#', 5)       # 10  (busca desde índice 5 → segundo #)
texto.find('#', 11)      # -1  (no hay # desde 11 en adelante)
texto.find('z')          # -1  (no existe)
```

**El segundo argumento `start` es opcional**. Sin él, busca desde el principio.

**Tres argumentos disponibles**:
```python
s.find(sub)              # busca en s entero
s.find(sub, start)       # busca desde índice start hasta el final
s.find(sub, start, end)  # busca solo en s[start:end]
```

**Versión que lanza error en lugar de devolver -1**: `s.index(sub, start)` lanza `ValueError` si no encuentra. Para LeetCode prefiere `find()` porque es más fácil chequear `if pos == -1` que envolver en try/except.

> 🎯 **Patrón típico LeetCode**: parsing de strings con separadores. Cuando estás en un índice `i` y quieres encontrar el siguiente separador, `s.find(sep, i)` es la herramienta. Aparece en [[271-encode-and-decode-strings]] (length-prefix decoding).

**Ejemplo del patrón "decodificar bloques con length-prefix"**:

```python
s = "5#hello5#world"
i = 0
while i < len(s):
    j = s.find('#', i)              # encuentra siguiente #
    length = int(s[i:j])            # parsea longitud: dígitos antes del #
    chunk = s[j+1 : j+1+length]     # lee 'length' caracteres después del #
    print(chunk)
    i = j + 1 + length              # avanza al siguiente bloque
# imprime: hello, world
```

**La intuición de los `+1`**: el `#` ocupa 1 carácter, así que `j+1` te lleva al primer carácter del dato. `j+1+length` te lleva al final del dato (sin incluirlo).

### Convertir entre char y código

```python
ord('a')        # 97
ord('z')        # 122
chr(97)         # 'a'

# Truco: índice 0-25 para letras minúsculas
ord('c') - ord('a')   # 2
```

### Inmutabilidad

```python
s = "hola"
s[0] = 'H'              # ❌ TypeError: 'str' object does not support item assignment

# Para "modificar" hay que crear nueva
s = 'H' + s[1:]         # "Hola"
# o convertir a list, modificar, join
chars = list(s)
chars[0] = 'H'
s = ''.join(chars)
```

### En problemas NeetCode

- [[242-valid-anagram]] — iteración carácter a carácter.
- [[49-group-anagrams]] — `''.join(sorted(s))` como clave canónica.
- [[125-valid-palindrome]] — `.isalnum()`, `.lower()`, two pointers sobre string.
- [[271-encode-and-decode-strings]] — `f"{len(s)}#{s}"`, `s.find('#', i)`, slicing.

---

## `Counter`

> **Qué es**: subclase de `dict` especializada en **contar frecuencias** de elementos en una colección. Está en `collections.Counter`.
>
> **Cuándo usarla**: cuando lo único que quieres es saber cuántas veces aparece cada elemento.

### Crear y usar
```python
from collections import Counter

c = Counter("aabbc")            # Counter({'a': 2, 'b': 2, 'c': 1})
c = Counter([1, 1, 2, 3, 3])    # Counter({1: 2, 3: 2, 2: 1})
c = Counter()                   # vacío

c['a']                          # 2
c['z']                          # 0 — NO da KeyError, devuelve 0 si no existe
c['a'] += 1                     # OK, ahora vale 3
```

### Métodos especiales

```python
c.most_common()                 # [('a', 2), ('b', 2), ('c', 1)] — ordenado por freq
c.most_common(2)                # top 2

# Aritmética entre Counters
c1 + c2                         # suma frecuencias
c1 - c2                         # resta (sin negativos)
c1 & c2                         # min de cada (intersección)
c1 | c2                         # max de cada (unión)

c1 == c2                        # True si tienen mismas claves y valores → ¡comparación de multisets!
```

### En problemas NeetCode

- [[242-valid-anagram]] — `Counter(s) == Counter(t)` resuelve el problema en 1 línea.
- [[347-top-k-frequent-elements]] — `Counter(nums).most_common(k)` o como base para heap/bucket.

---

## `defaultdict`

> **Qué es**: subclase de `dict` que **crea automáticamente** un valor por defecto cuando accedes a una clave inexistente. Está en `collections.defaultdict`.
>
> **Cuándo usarla**: cuando vas a hacer `dict[k].append(...)` o `dict[k] += 1` muchas veces y no quieres chequear `if k not in dict` cada vez.

### Crear y usar
```python
from collections import defaultdict

d = defaultdict(int)             # default = 0
d['a'] += 1                      # OK, no hay KeyError. d = {'a': 1}

d = defaultdict(list)            # default = []
d['x'].append(1)                 # OK. d = {'x': [1]}
d['x'].append(2)                 # d = {'x': [1, 2]}

d = defaultdict(set)             # default = set()
d['key'].add('value')            # OK
```

> ⚠️ **Acceder con `d[k]` crea la entrada** aunque no quisieras. Usa `d.get(k)` si solo quieres leer sin crear.

### En problemas NeetCode

- [[49-group-anagrams]] — `defaultdict(list)` para agrupar strings por clave canónica.
- [[36-valid-sudoku]] — `defaultdict(set)` para mantener tres conjuntos (rows, cols, boxes).
- [[242-valid-anagram]] — alternativa a `Counter` y a `dict.get(c, 0)`.

---

## `deque`

> **Qué es**: **double-ended queue** (cola doblemente acabada). Como una lista pero con O(1) al añadir/quitar **en ambos extremos**. Está en `collections.deque`.
>
> **Cuándo usarla**: cuando necesitas una cola FIFO (BFS), una pila LIFO con buen performance, o sliding window de tamaño variable.

### Crear y usar
```python
from collections import deque

q = deque()                       # vacía
q = deque([1, 2, 3])              # con elementos
q = deque([1, 2, 3], maxlen=5)    # con tamaño máximo (descarta automático)
```

### Métodos clave (O(1) en ambos extremos)

| Operación | Coste | Equivalente list |
|---|---|---|
| `q.append(x)` | O(1) | igual |
| `q.appendleft(x)` | **O(1)** | `list.insert(0, x)` es O(n) |
| `q.pop()` | O(1) | igual |
| `q.popleft()` | **O(1)** | `list.pop(0)` es O(n) |
| `q[i]` | O(n) ❌ | acceso aleatorio caro |
| `len(q)` | O(1) | igual |

### Patrón BFS típico (lo verás en patrón Trees y Graphs)

```python
from collections import deque

def bfs(start):
    visited = {start}
    q = deque([start])
    while q:
        node = q.popleft()
        for neighbor in get_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                q.append(neighbor)
```

### En problemas NeetCode (futuros)

- Patrón **Trees** (LC 102 Level Order Traversal) — BFS clásico.
- Patrón **Graphs** (LC 200 Number of Islands) — BFS sobre grid.
- Patrón **Sliding Window** (LC 239 Sliding Window Maximum) — deque monotónica.

---

## Heap (`heapq`)

> **Qué es**: **priority queue** implementada como min-heap binario. Te da el mínimo en O(1), inserción y extracción en O(log n). Está en `heapq` (no `collections`).
>
> **Cuándo usarla**: cuando necesitas extraer **el mínimo (o máximo)** repetidamente. Top-K elementos, scheduling, mediana en stream, Dijkstra.

### Concepto importante

`heapq` opera **directamente sobre una `list`**. No es una clase distinta — es un conjunto de funciones que **mantienen la propiedad de heap** sobre una lista.

```python
import heapq

heap = []                        # una list normal, vacía
heapq.heappush(heap, 3)          # heap = [3]
heapq.heappush(heap, 1)          # heap = [1, 3]
heapq.heappush(heap, 2)          # heap = [1, 3, 2]  ← layout de heap, NO ordenado
heapq.heappop(heap)              # devuelve 1, heap = [2, 3]
heap[0]                          # 2 — el mínimo, sin extraer
```

### Funciones principales

| Función | Coste | Descripción |
|---|---|---|
| `heapq.heappush(heap, x)` | O(log n) | Inserta x manteniendo invariante |
| `heapq.heappop(heap)` | O(log n) | Extrae y devuelve el mínimo |
| `heapq.heapify(lista)` | O(n) | Convierte una lista en heap in-place |
| `heap[0]` | O(1) | Mira el mínimo sin extraer |
| `heapq.heappushpop(h, x)` | O(log n) | push + pop atómico (más rápido que separados) |
| `heapq.nsmallest(k, lista)` | O(n log k) | Los k más pequeños |
| `heapq.nlargest(k, lista)` | O(n log k) | Los k más grandes |

### Min-heap por defecto, ¿cómo hacer max-heap?

```python
# heapq es MIN-heap. Para max-heap, NEGAR los valores:
heap = []
heapq.heappush(heap, -3)         # guardas -3
heapq.heappush(heap, -1)
heapq.heappush(heap, -2)
-heapq.heappop(heap)             # devuelve 3 (negado de vuelta)
```

### Tuplas en heap (multi-criterio)

```python
# heapq ordena por el primer elemento de la tupla, luego segundo, etc.
heap = []
heapq.heappush(heap, (5, 'tarea_a'))    # prioridad 5
heapq.heappush(heap, (1, 'tarea_b'))    # prioridad 1
heapq.heappush(heap, (3, 'tarea_c'))
heapq.heappop(heap)              # (1, 'tarea_b') — la de menor prioridad
```

### En problemas NeetCode

- [[347-top-k-frequent-elements]] — Counter + min-heap de tamaño k para top-K en O(n log k).
- Patrón **Heap / Priority Queue** (futuros): LC 215, 295, 703, 1046, 973...

---

## Iteración y comprehensions

### `for` con iteradores comunes

```python
# Lista
for x in [1, 2, 3]:
    print(x)                     # 1, 2, 3

# Rango
for i in range(5):
    print(i)                     # 0, 1, 2, 3, 4

for i in range(2, 8, 2):         # start, stop, step
    print(i)                     # 2, 4, 6

for i in range(5, 0, -1):        # hacia atrás
    print(i)                     # 5, 4, 3, 2, 1

for i in range(5, -1, -1):       # hacia atrás incluyendo 0
    print(i)                     # 5, 4, 3, 2, 1, 0

# Índice + valor: enumerate ⭐
for i, x in enumerate(nums):
    print(f"nums[{i}] = {x}")

# Dos colecciones a la vez: zip
for a, b in zip([1, 2, 3], ['a', 'b', 'c']):
    print(a, b)                  # 1 a, 2 b, 3 c
```

### `range(start, stop, step)` — la sintaxis con paso negativo

> **Qué hace**: genera una secuencia de enteros desde `start` (incluido) hasta `stop` (NO incluido), avanzando de `step` en `step`. **El step puede ser negativo** para ir hacia atrás.

**Tres argumentos** (1, 2 o 3 según necesites):

| Forma | Significado | Ejemplo |
|---|---|---|
| `range(stop)` | desde 0 hasta stop-1 | `range(5)` → `[0, 1, 2, 3, 4]` |
| `range(start, stop)` | desde start hasta stop-1 | `range(2, 5)` → `[2, 3, 4]` |
| `range(start, stop, step)` | desde start, sumando step, hasta stop (no incluido) | `range(0, 10, 2)` → `[0, 2, 4, 6, 8]` |

**Reglas clave**:
- `start` se **incluye**, `stop` **NO se incluye**.
- `step` puede ser positivo (hacia adelante) o negativo (hacia atrás), pero **no 0** (lanza `ValueError`).
- La longitud de la secuencia es `(stop - start) / step` redondeado hacia abajo.

**Ejemplos con paso negativo** (lo que confunde más):

```python
list(range(5, 0, -1))        # [5, 4, 3, 2, 1]                NO incluye 0
list(range(5, -1, -1))       # [5, 4, 3, 2, 1, 0]             SÍ incluye 0
list(range(10, 0, -2))       # [10, 8, 6, 4, 2]               saltos de 2 hacia atrás
list(range(0, 5, -1))        # []                              vacío (start < stop con step negativo)
```

> ⚠️ **Trampa más común**: para descender hasta `0` inclusive, usa `stop=-1`, no `stop=0`. Porque `stop` no se incluye:
>
> - `range(5, 0, -1)` produce `[5, 4, 3, 2, 1]` (te quedas en 1).
> - `range(5, -1, -1)` produce `[5, 4, 3, 2, 1, 0]` (llegas a 0).

**Patrón típico LeetCode — bucle hacia atrás sobre todo el array**:

```python
n = len(arr)
for i in range(n - 1, -1, -1):       # i = n-1, n-2, ..., 1, 0
    ...
```

**Patrón típico — bucle hacia atrás desde penúltimo hasta 0** (suffix accumulator):

```python
for i in range(n - 2, -1, -1):       # i = n-2, n-3, ..., 1, 0
    suffix[i] = suffix[i+1] * nums[i+1]
```

> 🎯 **Cuándo lo necesitas**: cualquier recurrencia donde `dp[i]` depende de `dp[i+1]` (vecino derecho). Aparece en [[238-product-of-array-except-self]], [[42-trapping-rain-water]], y muchos problemas DP, Trees y Linked Lists.

**Equivalentes pythonic más legibles**:

```python
# Hacia atrás sin range con paso negativo
for x in reversed(arr):              # solo el VALOR, no el índice
    ...

for i in reversed(range(n)):         # solo el ÍNDICE: n-1, n-2, ..., 0
    ...

# Si necesitas índice y valor invertidos
for i, x in reversed(list(enumerate(arr))):
    ...
```

`reversed(range(n))` es más legible que `range(n-1, -1, -1)` y produce lo mismo. Úsalo cuando solo necesitas iterar al revés sin saltos especiales.

### `enumerate(iterable, start=0)` — el built-in más usado en LeetCode

> **Qué hace**: toma un iterable y devuelve un iterador que produce **tuplas `(índice, valor)`** sobre la marcha. Te da índice y valor a la vez sin escribir `range(len(...))`.

**Comparación lado a lado**:

```python
nums = [10, 20, 30]

# ❌ Anti-patrón: verboso, no pythonic, propenso a off-by-one
for i in range(len(nums)):
    num = nums[i]
    print(i, num)

# ✅ Idiomático
for i, num in enumerate(nums):
    print(i, num)
# 0 10
# 1 20
# 2 30
```

**Cómo "lee" la sintaxis**:

`enumerate(nums)` produce las tuplas `(0, 10), (1, 20), (2, 30)`. El `for i, num in ...` hace **unpacking** de cada tupla en dos variables. Si pones una sola variable, recibes la tupla:

```python
for par in enumerate(nums):
    print(par)
# (0, 10)
# (1, 20)
# (2, 30)
```

**Parámetro `start`** (opcional, default 0):

```python
for i, c in enumerate("abc", start=1):
    print(i, c)
# 1 a
# 2 b
# 3 c
```

Útil cuando el problema es **1-indexed** (como [[167-two-sum-ii-input-array-is-sorted]]).

**Funciona con cualquier iterable**, no solo listas:

```python
for i, c in enumerate("hola"):       # string
    ...
for i, x in enumerate((1, 2, 3)):    # tupla
    ...
for i, x in enumerate(range(5)):     # range
    ...
```

> 💡 **Detalle técnico**: `enumerate` devuelve un **iterador perezoso**, no una lista. No gasta memoria extra. Si necesitas la lista completa, conviértela explícitamente:
>
> ```python
> list(enumerate(nums))           # [(0, 10), (1, 20), (2, 30)]
> dict(enumerate(nums))           # {0: 10, 1: 20, 2: 30}  ← truco útil
> ```

> 🎯 **Patrón típico LeetCode**: `for i, num in enumerate(nums):` en cualquier problema que necesite guardar el índice (Two Sum, Contains Duplicate, Sliding Window). Aparece literalmente en **la mayoría** de soluciones.

### Otros iteradores comunes

```python
# Diccionario: claves, valores o pares
for k, v in d.items():
    print(k, v)

# Recorrer al revés sin crear copia (a diferencia de [::-1])
for x in reversed([1, 2, 3]):
    print(x)                     # 3, 2, 1

# Combinar enumerate + reversed: índices originales, recorrido inverso
for i, x in reversed(list(enumerate(nums))):
    ...
```

### Comprehensions

```python
# Lista
squares = [x**2 for x in range(5)]                 # [0, 1, 4, 9, 16]
evens = [x for x in nums if x % 2 == 0]            # filtro
matrix = [[0] * 3 for _ in range(3)]               # matriz 3x3

# Set
unique = {x for x in nums}                         # deduplica
chars = {c for c in s if c.isalpha()}              # solo letras

# Dict
d = {x: x**2 for x in range(5)}                    # {0:0, 1:1, 2:4, 3:9, 4:16}
inverted = {v: k for k, v in d.items()}            # invertir un dict

# Generator (no almacena, calcula on-demand)
gen = (x**2 for x in range(1000000))               # eficiente en memoria
```

> 💡 **Cuando NO hay un return concreto, usa `_` como variable**: `for _ in range(n):` deja claro que la variable no importa.

### En problemas NeetCode

Aparece en TODOS. Es el pan diario.

---

## Funciones built-in

### Las que vas a usar todo el tiempo

```python
# Numéricas
min(1, 2, 3)                # 1
max([1, 2, 3])              # 3
min(nums, key=lambda x: x[1])    # min por clave
sum(nums)                   # suma
abs(-5)                     # 5
divmod(17, 5)               # (3, 2) — cociente y resto
round(2.7)                  # 3

# Sobre iterables
len(seq)                    # tamaño
sorted(nums)                # devuelve copia ordenada
sorted(nums, reverse=True)  # descendente
sorted(words, key=len)      # por longitud
all(x > 0 for x in nums)    # ¿todos positivos?
any(x < 0 for x in nums)    # ¿alguno negativo?

# Tipos
list("abc")                 # ['a', 'b', 'c']
tuple([1, 2, 3])            # (1, 2, 3)
set([1, 1, 2])              # {1, 2}
str(42)                     # "42"
int("42")                   # 42
int("ff", 16)               # 255 — hex a int

# Iteración
range(5)                    # 0..4
enumerate(nums)             # (0, n0), (1, n1), ...
zip(a, b)                   # pares
reversed(nums)              # iterador en reverso
```

### En problemas NeetCode

- `enumerate` aparece en **TODOS** los problemas que iteran array con índice.
- `min`/`max` con key: [[11-container-with-most-water]] (área máxima).
- `sorted`: [[15-3sum]] (ordenar antes de two pointers).
- `sum`: cualquier problema de suma de elementos.

---

## Sintaxis pythonic

### f-strings (interpolación de strings)

```python
nombre = "Daniel"
edad = 22
print(f"Hola {nombre}, tienes {edad} años")
print(f"El doble es {edad * 2}")           # expresiones
print(f"{nombre:>10}")                     # alineado derecha, ancho 10
print(f"{3.14159:.2f}")                    # "3.14" — 2 decimales
print(f"{42:04d}")                         # "0042" — con padding
print(f"{42:08b}")                         # "00101010" — binario
```

### Unpacking (asignación múltiple)

```python
a, b = 1, 2                       # asignación múltiple
a, b = b, a                       # swap, sin temporal

x, *rest = [1, 2, 3, 4]           # x=1, rest=[2,3,4]
*head, tail = [1, 2, 3, 4]        # head=[1,2,3], tail=4
a, _, c = [1, 2, 3]               # ignora con _

# En funciones que devuelven tuplas
def divmod(a, b):
    return a // b, a % b
quot, rem = divmod(17, 5)
```

### Operador walrus `:=` (Python 3.8+)

```python
# Asignar y usar en la misma expresión
if (n := len(nums)) > 10:
    print(f"Demasiados: {n}")

# En comprehensions / while
while (line := input()) != "stop":
    process(line)
```

### Truthy / falsy

```python
# Estos son falsy:
if not nums:                     # lista vacía
if not s:                        # string vacío
if not d:                        # dict vacío
if not n:                        # n == 0
if x is None:                    # None

# Idiomático:
if not nums:                     # ✅ pythonic
if len(nums) == 0:               # ❌ no pythonic
```

### Encadenamiento de comparaciones

```python
if 0 <= i < len(nums):           # ✅ pythonic
if i >= 0 and i < len(nums):     # ❌ no pythonic
```

### Multiple assignment con `=`

```python
a = b = c = 0                    # las tres a 0
left, right = 0, len(nums) - 1   # tupla unpacking
```

---

## Type hints en LeetCode

LeetCode siempre te da una plantilla con type hints. Es útil entenderlos:

```python
from typing import List, Dict, Set, Tuple, Optional

def funcion(
    nums: List[int],              # lista de ints
    target: int,                  # int
    s: str,                       # string
    grid: List[List[int]],        # matriz (lista de listas)
    d: Dict[str, int],            # dict str -> int
    seen: Set[int],               # set de ints
    point: Tuple[int, int],       # tupla de 2 ints
    node: Optional['TreeNode']    # puede ser TreeNode o None
) -> bool:                        # devuelve bool
    ...
```

> 💡 **En LeetCode no necesitas escribir los type hints tú** — los pone la plantilla. Pero entenderlos te ayuda a saber qué espera la función.

> ⚠️ **`List[int]` es `typing.List` (mayúscula)**, no `list`. En Python 3.9+ se puede usar `list[int]` directamente, pero LeetCode aún usa la versión con import.

---

## Trampas comunes

### `{}` es dict vacío, NO set vacío

```python
s = {}                  # ❌ dict
s = set()               # ✅ set vacío
```

### `list.sort()` muta, `sorted(list)` no

```python
nums = [3, 1, 2]
nums.sort()             # nums ahora es [1, 2, 3]. Devuelve None.

nums = [3, 1, 2]
new = sorted(nums)      # new = [1, 2, 3]. nums sigue siendo [3, 1, 2].
```

### Slice crea copia, no es vista

```python
a = [1, 2, 3]
b = a[:]                # COPIA. modificar b no afecta a a.
b.append(4)             # a = [1, 2, 3], b = [1, 2, 3, 4]

c = a                   # NO copia, mismo objeto
c.append(5)             # a = [1, 2, 3, 5], c = [1, 2, 3, 5]
```

### `==` vs `is`

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b                  # True (mismos contenidos)
a is b                  # False (objetos distintos)

x = None
if x is None:           # ✅ pythonic para None
if x == None:           # ❌ funciona pero no idiomático
```

### Mutable default arguments

```python
# ❌ Mal
def f(lst=[]):
    lst.append(1)
    return lst
f()      # [1]
f()      # [1, 1] — !!!!

# ✅ Bien
def f(lst=None):
    if lst is None:
        lst = []
    lst.append(1)
    return lst
```

### Matriz 2D mal inicializada

```python
# ❌ Mal: las 3 filas son la MISMA lista
matriz = [[0] * 3] * 3
matriz[0][0] = 1
# matriz = [[1, 0, 0], [1, 0, 0], [1, 0, 0]]   ← !!!

# ✅ Bien
matriz = [[0] * 3 for _ in range(3)]
matriz[0][0] = 1
# matriz = [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
```

### `pop(0)` es O(n), no O(1)

```python
# ❌ Mal en BFS
nums = [1, 2, 3, 4, 5]
nums.pop(0)             # O(n): copia todo

# ✅ Bien
from collections import deque
q = deque([1, 2, 3, 4, 5])
q.popleft()             # O(1)
```

### `+=` en strings es O(n) por iteración

```python
# ❌ Mal: O(n²) total
result = ""
for c in chars:
    result += c

# ✅ Bien: O(n) total
result = ''.join(chars)
```

---

## Patrones de código por tipo de problema

### Two pointers convergentes

```python
left, right = 0, len(arr) - 1
while left < right:
    # procesar arr[left] y arr[right]
    if condicion:
        return ...
    elif suma < target:
        left += 1
    else:
        right -= 1
```

Aparece en: [[125-valid-palindrome]] · [[167-two-sum-ii-input-array-is-sorted]] · [[15-3sum]] · [[11-container-with-most-water]] · [[42-trapping-rain-water]].

### Hash map "he visto X antes"

```python
visto = {}                       # o set() si solo presencia
for i, num in enumerate(nums):
    if num in visto:
        # encontrado
        return ...
    visto[num] = i               # o visto.add(num) para set
```

Aparece en: [[217-contains-duplicate]] · [[1-two-sum]] · [[128-longest-consecutive-sequence]].

### Conteo de frecuencias

```python
from collections import Counter
freq = Counter(nums)             # automatico
# o manual:
freq = {}
for x in nums:
    freq[x] = freq.get(x, 0) + 1
```

Aparece en: [[242-valid-anagram]] · [[347-top-k-frequent-elements]] · [[49-group-anagrams]].

### Top-K con heap

```python
import heapq
heap = []
for x in nums:
    heapq.heappush(heap, x)
    if len(heap) > k:
        heapq.heappop(heap)      # echa el menor
return heap                       # los k mayores (orden no garantizado)
```

Aparece en: [[347-top-k-frequent-elements]].

### Prefix / Suffix accumulator

```python
n = len(nums)
prefix = 1
result = [0] * n
for i in range(n):
    result[i] = prefix
    prefix *= nums[i]            # acumular después de usar

suffix = 1
for i in range(n - 1, -1, -1):
    result[i] *= suffix
    suffix *= nums[i]
```

Aparece en: [[238-product-of-array-except-self]] · [[42-trapping-rain-water]].

### BFS con deque (futuro, patrón Trees / Graphs)

```python
from collections import deque
def bfs(start):
    visited = {start}
    q = deque([start])
    while q:
        node = q.popleft()
        for nb in neighbors(node):
            if nb not in visited:
                visited.add(nb)
                q.append(nb)
```

### DFS recursivo (futuro, patrón Trees)

```python
def dfs(node):
    if not node:
        return
    # preorder: procesar antes de hijos
    dfs(node.left)
    dfs(node.right)
```

### Backtracking (futuro, patrón Backtracking)

```python
def backtrack(state, choices):
    if is_solution(state):
        results.append(state.copy())
        return
    for choice in choices:
        if valid(state, choice):
            state.append(choice)
            backtrack(state, choices)
            state.pop()              # deshacer (backtrack)
```

---

## Tabla maestra de complejidades por estructura

| Operación | `list` | `tuple` | `set` | `dict` | `deque` | `heap` |
|---|---|---|---|---|---|---|
| Acceso por índice | O(1) | O(1) | ❌ | ❌ | O(n) | ❌ |
| Acceso por clave | ❌ | ❌ | ❌ | O(1) avg | ❌ | ❌ |
| Buscar elemento (`in`) | O(n) | O(n) | O(1) avg | O(1) avg | O(n) | O(n) |
| Insertar al final | O(1) amort | inmutable | O(1) avg | O(1) avg | O(1) | O(log n) |
| Insertar al principio | O(n) | inmutable | O(1) avg | O(1) avg | **O(1)** | ❌ |
| Borrar del final | O(1) | inmutable | — | — | O(1) | — |
| Borrar del principio | O(n) | inmutable | — | — | **O(1)** | — |
| Mínimo | O(n) | O(n) | O(n) | O(n) | O(n) | **O(1)** |
| Ordenar | O(n log n) | inmutable | — | — | O(n log n) | ya parcial |

---

## Imports estándar para LeetCode

Estos son los imports que **siempre** vas a tener disponibles en LeetCode (sin necesidad de instalar nada):

```python
# Built-in
from typing import List, Dict, Set, Tuple, Optional

# collections — los más usados
from collections import Counter, defaultdict, deque, OrderedDict

# heapq — priority queue
import heapq

# math — funciones numéricas
import math
math.inf                         # infinito (útil para min comparisons)
math.gcd(12, 18)                 # 6
math.sqrt(16)                    # 4.0
math.floor(2.7)                  # 2
math.ceil(2.3)                   # 3

# bisect — binary search en arrays ordenados (futuro)
import bisect
bisect.bisect_left(arr, target)  # primer índice donde insertar manteniendo orden

# functools — caching automático (DP)
from functools import lru_cache, cache
@cache
def fib(n):
    ...

# itertools — combinatoria
from itertools import combinations, permutations, product
```

---

## Conexiones

- [[MOC_NeetCode_150]] — índice general de problemas (este cheatsheet referenciado allí).
- [[MOC_Programacion]] — área padre.
- Memoria asociada: `feedback_learning_style_algorithmic.md` (estilo worked-example).
- Todos los problemas resueltos del NeetCode 150 referencian este cheatsheet implícitamente.
