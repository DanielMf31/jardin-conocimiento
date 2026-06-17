---
title: "LeetCode 49 — Group Anagrams"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/arrays-hashing, patron/hash-map, patron/clave-canonica]
type: nota
status: en-progreso
source: claude-code
aliases: [Group Anagrams, LC 49, groupAnagrams, Agrupar anagramas]
problem_id: 49
difficulty: medium
patron: arrays-hashing
neetcode_order: 4
---

# LeetCode 49 — Group Anagrams

> **Cuarto problema del NeetCode 150 en Arrays & Hashing**. Es el primer **Medium** del patrón. Continúa la línea de [[242-valid-anagram]] pero ahora en lugar de comparar **dos** strings, agrupas **N** strings que sean anagramas entre sí. La técnica clave: **clave canónica** (canonical key).
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un array de strings `strs`, agrupa los **anagramas** juntos. Puedes devolver la respuesta en cualquier orden.

**Ejemplo 1:**
```
Input:  strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
Output: [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]
```

**Ejemplo 2:**
```
Input:  strs = [""]
Output: [[""]]
```

**Ejemplo 3:**
```
Input:  strs = ["a"]
Output: [["a"]]
```

**Restricciones:**
- `1 <= strs.length <= 10^4`
- `0 <= strs[i].length <= 100`
- `strs[i]` solo contiene **letras minúsculas inglesas**.

**Plantilla:**
```python
class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `List[List[str]]` — lista de grupos |
| ¿Importa el orden de los grupos? | NO |
| ¿Importa el orden dentro de cada grupo? | NO |
| ¿Hay duplicados (mismo string varias veces)? | Posible — cada uno va a su grupo (mismo grupo si son anagramas) |
| ¿String vacío "" cuenta? | Sí, va en su propio grupo (anagrama de sí mismo) |
| ¿Solo minúsculas? | Sí en este problema. En entrevista, **preguntar** |
| Edge case típico | `[""]` → `` (no ``) |

> La clave del problema: **¿qué define que dos strings sean anagramas?**. Misma multiset de caracteres. Si encuentras una **representación canónica** que dos anagramas comparten y dos no-anagramas no, puedes usarla como clave de un dict.

---

## Solución 1 — Fuerza bruta (NO recomendada)

Para cada string, comparar contra todas las anteriores. Si es anagrama de algún grupo, añadir; si no, crear grupo nuevo.

```python
class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        grupos = []
        for s in strs:
            colocado = False
            for g in grupos:
                if sorted(s) == sorted(g[0]):       # ← compara con el representante
                    g.append(s)
                    colocado = True
                    break
            if not colocado:
                grupos.append([s])
        return grupos
```

**Análisis:**
- **Tiempo: O(n² · k log k)** — n strings, comparar con hasta n grupos, cada comparación cuesta O(k log k) por el sort.
- **Espacio: O(n·k)** — almacenar todos los strings.
- **Veredicto:** [NO] TLE en LeetCode con n=10^4. La idea es correcta pero la búsqueda lineal entre grupos mata el rendimiento.

---

## Solución 2 — Dict con clave = string ordenado (la idiomática)

**La idea**: si dos strings son anagramas, **al ordenar sus caracteres** producen exactamente el mismo string. Eso es una **clave canónica**: un identificador único de la "clase de equivalencia".

```python
from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        grupos = defaultdict(list)
        for s in strs:
            clave = ''.join(sorted(s))              # canonical form
            grupos[clave].append(s)
        return list(grupos.values())
```

**Análisis:**
- **Tiempo: O(n · k log k)** — n strings, cada uno ordenado en O(k log k).
- **Espacio: O(n·k)** — claves + valores.
- **Veredicto:** [OK] **la respuesta esperada en entrevista**. Limpia, idiomática, fácil de explicar.

> **`''.join(sorted(s))`**: `sorted("eat")` da `['a', 'e', 't']` (lista). `''.join(...)` la concatena en `"aet"`. Necesitas string (no lista) para usarla como clave del dict (las listas no son hashables).

---

## Solución 3 — Dict con clave = tupla de conteos (la óptima)

**La idea**: en lugar de ordenar (que cuesta O(k log k)), usar un **array de 26 enteros** con la frecuencia de cada letra. Como las listas no son hashables, convertir a **tupla**.

```python
from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        grupos = defaultdict(list)
        for s in strs:
            count = [0] * 26
            for c in s:
                count[ord(c) - ord('a')] += 1
            grupos[tuple(count)].append(s)          # tupla = hashable
        return list(grupos.values())
```

**Análisis:**
- **Tiempo: O(n · k)** — n strings, cada uno recorrido lineal de longitud k.
- **Espacio: O(n·k)** — almacenar.
- **Veredicto:** [OK] **óptima dada la restricción** (alfabeto fijo de 26 letras). Es el siguiente paso natural si el entrevistador te pregunta "¿puedes hacerlo más rápido?".

> **Misma técnica que en [[242-valid-anagram]] Solución 5**: aprovechar que el alfabeto es pequeño y conocido para usar array fijo en lugar de dict. El "salto" aquí es convertir la lista a **tupla** para usarla como clave.

---

## El patrón general — "Clave canónica" (Canonical key / Bucket pattern)

Esta es la abstracción que generaliza el problema. **Cuándo aplicar**:

> Cuando el problema te pide **agrupar elementos que cumplen una propiedad de equivalencia** (anagramas, isomorfos, congruentes, ...), y existe una **transformación f(x)** que devuelve el mismo valor para todos los elementos equivalentes.

**Plantilla mental**:

```python
def patron_clave_canonica(coleccion):
    grupos = defaultdict(list)
    for elem in coleccion:
        clave = funcion_canonica(elem)              # f: elem -> representante de su clase
        grupos[clave].append(elem)
    return list(grupos.values())
```

**Tres señales** que avisan de este patrón:

1. El problema habla de **agrupar, agrupar por X, partition into groups**.
2. Existe una relación de equivalencia clara entre los elementos.
3. Puedes calcular una representación que dos elementos equivalentes comparten.

**Ejemplos de funciones canónicas comunes:**

| Tipo de equivalencia | Función canónica |
|---|---|
| Anagramas | `sorted(s)` o tupla de conteos |
| Strings isomórficos | mapeo posicional canónico |
| Números con misma cifra raíz | `n % k` |
| Strings hasta rotación | rotación lexicográficamente mínima |
| Pares con misma suma | `min + max` (o `sum`) |

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **242. Valid Anagram** | Caso degenerado: solo dos strings, ¿son del mismo grupo? |
| **438. Find All Anagrams in a String** | Busca anagramas en una **ventana deslizante** sobre un string |
| **567. Permutation in String** | "¿s2 contiene una permutación de s1?" → versión booleana de 438 |
| **205. Isomorphic Strings** | Otra clave canónica distinta (mapeo posicional) |
| **249. Group Shifted Strings** | Agrupar strings que sean rotaciones cíclicas (ROT-N) |

---

## Conceptos a interiorizar

### `defaultdict(list)` — el patrón pythonic para agrupar

```python
from collections import defaultdict

# ❌ Verboso, requiere chequeo manual
grupos = {}
for s in strs:
    clave = ''.join(sorted(s))
    if clave not in grupos:
        grupos[clave] = []
    grupos[clave].append(s)

# ✅ Idiomático
grupos = defaultdict(list)
for s in strs:
    grupos[''.join(sorted(s))].append(s)
```

`defaultdict(list)` crea una lista vacía automáticamente la primera vez que accedes a una clave nueva.

### Tuplas como claves de dict

```python
d = {}
d[[1, 2, 3]] = "x"          # ❌ TypeError: list no hashable
d[(1, 2, 3)] = "x"          # ✅ tuple hashable
```

**Regla**: cualquier estructura de datos en Python es hashable solo si es **inmutable** y todos sus elementos son hashables. Tuplas de ints sí, listas no, sets no (pero `frozenset` sí).

### `dict.values()` y `list(...)`

```python
d = {"a": [1, 2], "b": [3]}
d.values()                   # dict_values([[1, 2], [3]]) — view object
list(d.values())             # [[1, 2], [3]] — lista real
```

LeetCode espera `List[List[str]]`, así que `list(grupos.values())` cierra el problema.

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Fuerza bruta (búsqueda lineal entre grupos) | O(n² · k log k) | O(n·k) | [NO] TLE |
| 2. Dict con clave `sorted(s)` | O(n · k log k) | O(n·k) | [OK] La idiomática |
| 3. Dict con clave tupla de 26 conteos | **O(n · k)** | O(n·k) | [OK] La óptima |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** desde cero.
2. Justifica:
   - Por qué `''.join(sorted(s))` y no solo `sorted(s)` como clave.
   - Cuál es la complejidad temporal y por qué.
   - Por qué `defaultdict(list)` es más limpio que `dict()` con chequeo manual.
3. Reescribe usando la Solución 3 (tupla de conteos). Compara con la 2: ¿cuándo conviene cada una?
4. Trace mental con `strs = ["eat", "tea", "tan", "ate"]`. Estado del dict tras procesar cada string.
5. **Bonus** — ¿qué cambiarías si el alfabeto fuera Unicode (no solo a-z)?

---

## Cosas que te pueden preguntar en entrevista

- **"¿Y si te pidieran solo el grupo más grande, no todos?"** → mismo dict + `max(grupos.values(), key=len)`.
- **"¿Y si tuvieras streaming de strings (no array completo)?"** → ir actualizando el dict a medida que llegan, devolver snapshot bajo demanda.
- **"¿Qué tienen en común tu solución y la de Two Sum?"** → ambas usan dict con una **clave derivada** (canonical key vs complemento) para evitar O(n²).
- **"Tu solución 3 es O(n·k). ¿Puedes hacerlo más rápido?"** → No teóricamente, porque tienes que **leer cada carácter al menos una vez** (lower bound Ω(n·k)).

---

## Solución en C++ — contraste con Python

> Añadido para ver las diferencias de lenguaje. Código compilable en [`49-group-anagrams.cpp`](49-group-anagrams.cpp).

```cpp
class Solution {
 public:
  std::vector<std::vector<std::string>> groupAnagrams(
      std::vector<std::string>& strs) {
    std::unordered_map<std::string, std::vector<std::string>> groups;
    for (const std::string& s : strs) {
      std::string key = s;
      std::sort(key.begin(), key.end());     // clave = string ordenado
      groups[key].push_back(s);
    }
    std::vector<std::vector<std::string>> out;
    for (auto& [key, group] : groups) out.push_back(std::move(group));
    return out;
  }
};
```

**Análisis:** Tiempo O(n·k log k), Espacio O(n·k) — igual que el Python con clave ordenada.

**Diferencias clave Python ↔ C++:**
- `defaultdict(list)` → `std::unordered_map<std::string, std::vector<std::string>>`; `groups[key]` ya crea el vector vacío si no existe (como `defaultdict`).
- `"".join(sorted(s))` → copiar el string y `std::sort(key.begin(), key.end())` (ordena in-place; el string ya es la clave).
- `dict.values()` → recorrer con structured bindings `for (auto& [k, g] : groups)` y `std::move(g)` para no copiar los vectores.
- Una alternativa O(n·k) sin ordenar: clave = histograma de 26 chars en un `std::array<int,26>`.

---

## Conexiones

- [[242-valid-anagram]] — caso bipartito del mismo concepto (multisets de caracteres).
- [[1-two-sum]] — otro caso de "clave derivada en dict" (complemento en vez de canonical form).
- Próximo problema: [[347-top-k-frequent-elements]] — Counter + heap, primer roce con priority queue.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Reescrita con tupla de conteos (Solución 3)
- [ ] Justificada cuándo conviene cada una
- [ ] Resuelto en LeetCode con éxito
- [ ] Hecho 1 vez más a la semana siguiente
