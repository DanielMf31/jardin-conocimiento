---
title: "LeetCode 242 — Valid Anagram"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/arrays-hashing, patron/hash-map, patron/conteo-frecuencias]
type: nota
status: en-progreso
source: claude-code
aliases: [Valid Anagram, LC 242, isAnagram, Anagrama válido]
problem_id: 242
difficulty: easy
patron: arrays-hashing
neetcode_order: 2
---


# LeetCode 242 — Valid Anagram

> 🎯 **Segundo problema del NeetCode 150**. Sigue al [[217-contains-duplicate]] y sube de complejidad: pasa de **set** ("¿he visto X antes?") a **dict** ("¿cuántas veces he visto X?"). Es la transición clave del patrón Arrays & Hashing.
> 📚 Mismo formato de aprendizaje: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dadas dos strings `s` y `t`, devuelve `True` si `t` es un **anagrama** de `s`, y `False` en caso contrario.

> 💡 **Anagrama** = misma multiset de caracteres, distinto orden. Por ejemplo `"anagram"` y `"nagaram"` son anagramas; `"rat"` y `"car"` no.

**Ejemplo 1:**
```
Input:  s = "anagram", t = "nagaram"
Output: True
```

**Ejemplo 2:**
```
Input:  s = "rat", t = "car"
Output: False
```

**Restricciones:**
- `1 <= s.length, t.length <= 5 * 10^4` → no hay strings vacías.
- `s` y `t` constan de **letras minúsculas inglesas**. Esto es importante: el alfabeto es finito y conocido (26 letras).

**Plantilla:**
```python
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `bool` |
| ¿Las longitudes deben ser iguales? | **Sí, obligatoriamente** — un anagrama conserva el número de letras |
| ¿Importa el orden? | NO — los anagramas son los mismos caracteres reordenados |
| ¿Importa el case (mayús/minús)? | NO en este problema (solo minúsculas según restricción). En entrevista real, **preguntar siempre** |
| ¿Hay caracteres no-ASCII? | NO en este problema. En entrevista, **preguntar** ("follow-up: y si fuera Unicode?") |
| Edge case 1 | Longitudes distintas → `False` directo, sin contar nada |
| Edge case 2 | Mismo string en sí mismo (`s == t`) → `True` (es anagrama de sí mismo) |
| Edge case 3 | Strings de un solo carácter → si son iguales `True`, si no `False` |

**El check de longitud es la primera línea de cualquier solución eficiente.** Ahorrarse el conteo cuando ya sabes que es imposible es señal de que entiendes el problema.

---

## Solución 1 — Ordenar ambos y comparar

La idea más obvia: si reordeno alfabéticamente ambas strings, los anagramas dan strings idénticas.

```python
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        return sorted(s) == sorted(t)
```

`sorted("anagram")` devuelve `['a', 'a', 'a', 'g', 'm', 'n', 'r']` (lista de chars). `sorted("nagaram")` devuelve la misma lista. Comparar listas es elemento a elemento.

**Análisis:**
- **Tiempo: O(n log n)** — el sort domina.
- **Espacio: O(n)** — `sorted()` crea una lista nueva (no modifica las strings, que son inmutables en Python).
- **Veredicto:** funciona y pasa. Es la respuesta "rápida y honesta" si la presión te bloquea. Pero NO es la idiomática.

> 💡 **Detalle Python**: `s.sort()` no existe para strings (son inmutables). Solo `sorted(s)` que devuelve **lista**, no string. Si quisieras un string ordenado, harías `''.join(sorted(s))`.

---

## Solución 2 — Dos diccionarios de frecuencia

**La idea**: cuento cuántas veces aparece cada carácter en `s` y en `t`. Si los dos conteos son iguales (mismas claves, mismos valores), son anagramas.

```python
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False                    # ✂️ corte temprano

        count_s, count_t = {}, {}
        for char in s:
            count_s[char] = count_s.get(char, 0) + 1
        for char in t:
            count_t[char] = count_t.get(char, 0) + 1
        return count_s == count_t
```

**Análisis:**
- **Tiempo: O(n)** — dos recorridos lineales + comparación de dicts O(k) donde k es el número de claves únicas.
- **Espacio: O(k)** — k ≤ 26 si solo letras minúsculas, o ≤ 256 si ASCII completo.
- **Veredicto:** correcta y clara. Aceptable en entrevista si la explicas bien.

> 📌 **`dict.get(clave, default)`** es la forma idiomática de evitar `KeyError`. La alternativa `count_s[char] += 1` falla si la clave no existe todavía (vienes de C/firmware donde inicializas a 0; en Python no se inicializa automático en dicts normales).

---

## Solución 3 — Un solo diccionario (incrementar/decrementar)

**La idea**: en vez de contar dos veces, hago **una sola** cuenta. Subo cada carácter de `s`, bajo cada carácter de `t`. Al final, si todos los contadores son **0**, son anagramas.

```python
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False

        count = {}
        for char in s:
            count[char] = count.get(char, 0) + 1
        for char in t:
            if char not in count or count[char] == 0:
                return False                # apareció en t pero no en s, o ya agotado
            count[char] -= 1
        return True
```

**Análisis:**
- **Tiempo: O(n)** — un solo dict, dos recorridos.
- **Espacio: O(k)** — el dict tiene como mucho k claves.
- **Veredicto:** ligeramente más eficiente que la Solución 2 (la mitad de operaciones de escritura), y no necesita comparación final. Es la que muchos entrevistadores esperan.

> 💡 **Por qué la guarda `count[char] == 0`**: si `s = "aab"` y `t = "abb"`, sin esa guarda al ver el segundo `'b'` de `t` el contador de `'b'` se quedaría en `-1`. Con la guarda detectas el desequilibrio antes.

---

## Solución 4 — `Counter` (la pythonica)

`collections.Counter` es un dict especializado en contar frecuencias. Hace lo de la Solución 2 en una línea cada uno.

```python
from collections import Counter

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        return Counter(s) == Counter(t)
```

**Análisis:**
- **Tiempo: O(n)**.
- **Espacio: O(k)**.
- **Veredicto:** la más concisa y elegante. En entrevista, **escríbela después de explicar la lógica de la Solución 2 o 3**, para mostrar que sabes lo que pasa por debajo. Si la sueltas tal cual sin contexto, parece "memorizado".

> 📚 **`Counter` también soporta**:
> - `Counter("aabbc").most_common(2)` → `[('a', 2), ('b', 2)]` — top-K frecuencias.
> - `Counter(s) - Counter(t)` → diferencia de multisets.
> - Es subclase de `dict`, así que todo lo que hace un dict también funciona aquí.

---

## Solución 5 — Array de tamaño fijo (la óptima en espacio para alfabetos pequeños)

Cuando el alfabeto es **conocido y pequeño** (e.g. 26 letras minúsculas), un dict es overkill. Usa un array de 26 enteros indexados por `ord(char) - ord('a')`.

```python
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False

        count = [0] * 26
        for i in range(len(s)):
            count[ord(s[i]) - ord('a')] += 1
            count[ord(t[i]) - ord('a')] -= 1

        return all(c == 0 for c in count)
```

`ord('a')` es 97. `ord('c') - ord('a')` es 2 → `'c'` va al índice 2. Es como hacer hash manual con conocimiento previo del rango.

**Análisis:**
- **Tiempo: O(n)** — un solo bucle que toca s y t simultáneamente.
- **Espacio: O(1)** — el array tiene **siempre 26 enteros**, sea n=10 o n=10^5. Por eso es **espacio constante**.
- **Veredicto:** la **óptima teórica** para este problema con la restricción dada. Demuestra que sabes pensar en términos del enunciado, no del caso general.

> 🎯 **Esta técnica reaparece** en muchos problemas de strings con alfabeto limitado: substring problems, sliding window de caracteres, etc. Familiarízate con `ord()` y `chr()`.

> ⚠️ **Trampa importante**: si en un follow-up el entrevistador dice "y si fuera Unicode", esta solución se cae (Unicode tiene >1M de codepoints; un array de ese tamaño es absurdo). Tendrías que volver a `dict` / `Counter`. Esto es **una pregunta de entrevista real**.

---

## El patrón general — "Conteo de frecuencias"

Esta es la abstracción que generaliza el problema. **Cuándo aplicar este patrón**:

> Cuando el problema te pide comparar **multisets** (colecciones donde importa el número de apariciones pero no el orden), o detectar si dos colecciones tienen "los mismos elementos en distinta cantidad/disposición".

**Plantilla mental** (memorízala):

```python
def patron_conteo_frecuencias(coleccion_a, coleccion_b):
    if len(coleccion_a) != len(coleccion_b):
        return False                        # check temprano

    count = {}                              # o defaultdict, Counter, o array fijo
    for elem in coleccion_a:
        count[elem] = count.get(elem, 0) + 1
    for elem in coleccion_b:
        if elem not in count or count[elem] == 0:
            return False
        count[elem] -= 1
    return True
```

**Tres señales** que te avisan de que es este patrón:

1. El problema habla de **anagrama, permutación, rearrangement, multiset, frecuencia**.
2. El orden **no importa** pero la cantidad de cada elemento **sí**.
3. Las dos colecciones a comparar tienen **misma longitud requerida** (o si no, condición a chequear primero).

---

## Variaciones del problema (las verás más adelante)

| Problema LeetCode | Variación |
|---|---|
| **49. Group Anagrams** | "Agrupa anagramas en una lista de strings" → dict de listas, clave = sorted(string) o tupla de conteos |
| **438. Find All Anagrams in a String** | "Encuentra todos los índices donde aparece un anagrama de p en s" → sliding window + Counter |
| **567. Permutation in String** | "¿s2 contiene una permutación de s1?" → sliding window de tamaño fijo + array de 26 |
| **383. Ransom Note** | "¿Puedes formar la nota con las letras de la revista?" → mismo conteo, pero direccional |

> 📌 **Patrón maestro**: cuando lleves la noción de "Counter / array fijo de frecuencias" interiorizada, problemas Medium de strings se vuelven sustancialmente más fáciles. Esta técnica es la base de buena parte del patrón Sliding Window.

---

## Conceptos a interiorizar

### Sobre `dict` en Python (lo que ya sabes de [[217-contains-duplicate]] + nuevo)

| Operación | Coste | Notas |
|---|---|---|
| `d = {}` — crear vacío | O(1) | Esto sí es dict (a diferencia de set) |
| `d[k]` — acceder | O(1) promedio | **`KeyError` si no existe** |
| `d.get(k, default)` | O(1) promedio | **Sin error, devuelve default** |
| `d[k] = v` — asignar | O(1) promedio | |
| `k in d` — chequeo | O(1) promedio | Solo mira las claves |
| `len(d)` | O(1) | |
| `d == d2` — comparar | O(min(n, m)) | Iguales si mismas claves y valores |

### Patrón "incremental" para conteos

```python
# ❌ Esto falla con KeyError la primera vez
count[char] += 1

# ✅ Tres formas equivalentes:
count[char] = count.get(char, 0) + 1                  # idiomática

from collections import defaultdict
count = defaultdict(int)
count[char] += 1                                      # con defaultdict

from collections import Counter
count = Counter(s)                                    # más rápido y directo
```

### `ord()` y `chr()`

```python
ord('a')        # 97
ord('z')        # 122
ord('A')        # 65
chr(97)         # 'a'
chr(65)         # 'A'

# Truco: índice 0-25 para letras minúsculas
ord('c') - ord('a')   # 2
```

### `defaultdict` (vs dict normal)

```python
from collections import defaultdict

d = defaultdict(int)            # default 0
d['a'] += 1                     # OK, se inicializa a 0 y suma 1

d2 = defaultdict(list)          # default []
d2['key'].append(1)             # OK, inicializa lista vacía
```

Útil cuando vas a incrementar/append sin saber si la clave existe ya.

---

## Comparación final de las 5 soluciones

| Solución | Tiempo | Espacio | Pythonic | Veredicto |
|---|---|---|---|---|
| 1. `sorted()` y comparar | O(n log n) | O(n) | ⭐⭐ | Aceptable, fácil |
| 2. Dos dicts de conteo | O(n) | O(k) | ⭐⭐⭐ | Clara, didáctica |
| 3. Un dict (incrementar/decrementar) | O(n) | O(k) | ⭐⭐⭐⭐ | La esperada en entrevista |
| 4. `Counter == Counter` | O(n) | O(k) | ⭐⭐⭐⭐⭐ | La elegante (explica antes) |
| 5. Array fijo de 26 | O(n) | **O(1)** | ⭐⭐⭐⭐ | Óptima dada la restricción |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 3** (un solo dict) desde cero, en un editor en blanco. Sin copiar.
2. Justifica:
   - Por qué la guarda `count[char] == 0` antes de decrementar.
   - Cuál es la complejidad temporal y espacial.
   - Por qué el check de longitud al inicio puede ahorrar trabajo.
3. Reescribe la solución usando `defaultdict(int)` en lugar de `dict.get(char, 0)`. ¿Cambia la complejidad?
4. Mental run-through con `s = "anagram"`, `t = "nagaram"`. Estado del dict tras procesar `s`: `{...}`. Estado tras procesar `t`: `{...}`. ¿Devuelve True?
5. **Bonus** — extiende el problema: en vez de devolver `bool`, devuelve **el mínimo número de cambios de carácter** que harían `t` anagrama de `s` (si las longitudes coinciden). Pista: cuenta cuántas posiciones del dict resultante quedan en negativo o positivo y divide.

Si fallaste en el 5 no pasa nada — es de nivel Medium y mucho más allá. Sirve solo para mostrarte cómo el mismo patrón da extensibilidad.

---

## Cosas que te pueden preguntar en entrevista sobre este problema

- **"Y si las strings fueran Unicode (no solo a-z)?"** → Cae la Solución 5 (array de 26). Vuelves a dict / Counter. Son O(n) y O(k) donde k = chars únicos.
- **"Y si las strings fueran enormes (gigabytes) y no cupieran en memoria?"** → Streaming + conteo distribuido (map-reduce). No es algo de entrevista junior pero es la respuesta correcta.
- **"Y si el case fuera relevante? Y los espacios?"** → Preprocesar (`s.lower()`, `s.replace(" ", "")`) antes del conteo.
- **"Cuál es el coste de `Counter(s) == Counter(t)`?"** → O(n) para construir + O(k) para comparar = O(n) total.
- **"Diferencia entre dict y set en Python?"** → set guarda solo claves (sin valor); dict guarda claves con valores asociados. Ambos hashed → O(1) lookup.

---

## Conexiones

- [[217-contains-duplicate]] — problema previo del patrón. La transición es: set ("¿he visto X?") → dict ("¿cuántas veces he visto X?").
- Próximo problema: [[1-two-sum]] — añade la idea de **complemento** (no buscas el mismo elemento, buscas el que falta).

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 3 (un solo dict) desde cero sin mirar
- [ ] Reescrita con `defaultdict(int)` correctamente
- [ ] Justificadas complejidades temporal y espacial
- [ ] Resuelto en LeetCode con éxito (Accepted en una sola submission)
- [ ] Implementadas las 5 soluciones (al menos esbozadas mentalmente) y entendido cuándo usar cuál
- [ ] Hecho el problema 1 vez más a la semana siguiente
