---
title: "LeetCode 217 — Contains Duplicate"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/arrays-hashing, patron/hash-set]
type: nota
status: en-progreso
source: claude-code
aliases: [Contains Duplicate, LC 217, hasDuplicate]
problem_id: 217
difficulty: easy
patron: arrays-hashing
neetcode_order: 1
---

# LeetCode 217 — Contains Duplicate

> 🎯 **Primer problema del NeetCode 150**. Patrón: **Arrays & Hashing**, sub-patrón **Hash Set / "lo he visto antes"**.
> 📚 Este archivo sigue tu estilo de aprendizaje: solución primero, patrón abstraído, replicar sin mirar al final.

## Enunciado

Dado un array de enteros `nums`, devuelve `True` si **algún valor aparece más de una vez** en el array. En caso contrario devuelve `False`.

**Ejemplo 1:**
```
Input:  nums = [1, 2, 3, 3]
Output: True
```

**Ejemplo 2:**
```
Input:  nums = [1, 2, 3, 4]
Output: False
```

**Restricciones:**
- `0 <= nums.length <= 10^5` → array vacío permitido, hasta 100.000 elementos.
- `-10^9 <= nums[i] <= 10^9` → enteros con signo, valores grandes (pero caben en `int` de Python sin problema).

**Plantilla:**
```python
class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        ...
```

---

## Lectura del problema antes de codear (el paso que más se salta)

Antes de teclear **una sola línea**, hay que decodificar lo que pide:

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `bool` — `True` o `False` |
| ¿Cuándo `True`? | Existe **al menos un** valor que aparece **≥ 2 veces** |
| ¿Tengo que decir cuál es el duplicado? | NO. Solo si existe o no |
| ¿Tengo que contar cuántos hay? | NO |
| ¿El array está ordenado? | NO se garantiza (asume desordenado) |
| Edge case 1 | Array vacío → no hay duplicados → `False` |
| Edge case 2 | Array de 1 elemento → no hay duplicados posibles → `False` |
| Edge case 3 | Todos iguales → `True` (duplicados claros) |

**Por qué importa este paso:** entender qué pide el problema es la mitad del trabajo. En entrevistas reales, **preguntar** estas cosas al entrevistador antes de codear es señal positiva (no negativa) de seniority.

---

## Solución 1 — Fuerza bruta (NO usar, pero útil para comparar)

La idea más obvia: para cada elemento, mirar si aparece más adelante en el array. Doble bucle.

```python
class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):
                if nums[i] == nums[j]:
                    return True
        return False
```

**Análisis:**
- **Tiempo: O(n²)** — el bucle externo va n veces, el interno hasta n-1 veces.
- **Espacio: O(1)** — no usamos estructuras auxiliares.
- **Veredicto:** rechazado en entrevista para este problema. Con `n = 10^5`, son hasta **10^10 operaciones** → ~100 segundos. LeetCode te da `Time Limit Exceeded`.

> 💡 **Lección:** "funcionar" no es lo mismo que "ser aceptable". Casi todos los problemas LeetCode admiten una solución brute force; el ejercicio es encontrar la **idiomática**.

---

## Solución 2 — Ordenar primero, comparar adyacentes

Si ordeno el array, los duplicados quedan **pegados** (`[1, 2, 3, 3, 4]`). Recorro y comparo cada elemento con el siguiente.

```python
class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        nums.sort()                          # O(n log n), modifica nums in-place
        for i in range(1, len(nums)):
            if nums[i] == nums[i - 1]:
                return True
        return False
```

**Análisis:**
- **Tiempo: O(n log n)** — dominado por el sort.
- **Espacio: O(1)** auxiliar (Python `.sort()` ordena in-place; si usaras `sorted(nums)` sería O(n)).
- **Veredicto:** aceptable. Pasa los tests de LeetCode. Pero **modifica el input** (efecto secundario), lo cual a veces no se quiere.

> ⚠️ **Trampa**: `nums.sort()` muta `nums`. `sorted(nums)` crea una copia. Saber la diferencia es la clase de detalle que un entrevistador te puede preguntar.

---

## Solución 3 — Hash Set (la idiomática, la que tienes que interiorizar)

**La idea**: voy recorriendo el array. En un set llamado `vistos`, guardo cada elemento que veo. **Antes** de añadirlo, compruebo si ya está. Si ya está → duplicado → `True`. Si llegué al final sin colisión → `False`.

```python
class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        vistos = set()
        for num in nums:
            if num in vistos:
                return True
            vistos.add(num)
        return False
```

**Análisis:**
- **Tiempo: O(n)** — un solo recorrido. `in` y `add` sobre set son O(1) promedio.
- **Espacio: O(n)** — el set puede llegar a tener n elementos en el peor caso.
- **Veredicto:** óptima. Es la respuesta esperada en una entrevista. Es la **plantilla** del patrón "lo he visto antes".

### Por qué `set` y no `list`

```python
vistos = []         # ❌ Mal: 'in' sobre list es O(n)
vistos = set()      # ✅ Bien: 'in' sobre set es O(1) promedio
```

`5 in mi_lista` recorre la lista hasta encontrar el 5 → O(n). `5 in mi_set` calcula el hash de 5 y va directo → O(1). Esta diferencia es lo que convierte una solución O(n²) en O(n).

---

## Solución 4 — One-liner pythonico (para entender Python, no para entrevista)

```python
class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        return len(set(nums)) < len(nums)
```

**La idea**: si convierto el array a set, los duplicados desaparecen. Si el set es **más corto** que la lista, había duplicados.

**Análisis:**
- **Tiempo: O(n)** — construir el set recorre todo el array.
- **Espacio: O(n)** — el set guarda todos los únicos.
- **Veredicto:** la solución más corta y elegante. **Pero**: en una entrevista, escribirla como one-liner sin explicar nada antes hace que parezca que la "memorizaste". Mejor escribir la Solución 3 (que muestra que entiendes la lógica paso a paso) y mencionar esta como variante.

---

## El patrón general — "He visto este elemento antes"

Esta es la abstracción que te tienes que llevar. **Cuándo aplicar este patrón**:

> Cuando el problema te pide detectar **presencia, ausencia, repetición o frecuencia** de elementos en una colección, y la búsqueda directa con bucle anidado daría O(n²).

**Plantilla mental** (memorízala):

```python
def patron_he_visto_antes(coleccion):
    vistos = set()                  # o dict() si necesito guardar info extra
    for elemento in coleccion:
        if elemento in vistos:
            # ¡Detecté el caso! Decidir qué hacer (return, contar, etc.)
            ...
        vistos.add(elemento)
    # Si llegué hasta aquí, no se cumplió la condición
    ...
```

**Tres señales** que te avisan de que es este patrón:

1. El problema habla de **duplicados, repetidos, únicos, primera aparición**.
2. La solución obvia tiene **doble bucle** anidado.
3. El elemento clave es **comparable directamente** (números, strings, tuplas — cosas que Python puede meter en un set).

---

## Variaciones del problema (las verás más adelante)

Todas usan el **mismo patrón base** con pequeñas variantes:

| Problema LeetCode | Variación |
|---|---|
| **219. Contains Duplicate II** | `True` si hay duplicados a distancia ≤ k → guardas el **índice** en un dict, no solo el valor |
| **220. Contains Duplicate III** | `True` si hay duplicados a distancia ≤ k **con valores cercanos** ≤ t → bucket sort o sorted set, ya es Hard |
| **1. Two Sum** | "He visto antes el complemento" — mismo patrón, con dict en lugar de set |
| **242. Valid Anagram** | "Misma cuenta de cada letra" — usas dict en vez de set para contar |
| **49. Group Anagrams** | "Agrupar por clave canónica" — dict de listas |
| **347. Top K Frequent Elements** | "Frecuencia + top K" — Counter + heap |

> 📌 **Patrón maestro**: Arrays & Hashing es el patrón **fundacional**. Cuando lo dominas, una buena parte de los problemas Easy y Medium se reducen a "¿qué guardo en mi dict/set para responder esta pregunta?".

---

## Conceptos a interiorizar

Estos son los detalles de Python y CS que el problema te enseña, además del patrón:

### Sobre `set` en Python

| Operación | Coste | Ejemplo |
|---|---|---|
| `s = set()` — crear vacío | O(1) | |
| `s = {1, 2, 3}` — crear con literal | O(k) donde k = nº elementos | ⚠️ `{}` solo es **dict vacío**, NO set vacío |
| `x in s` | O(1) promedio | clave del patrón |
| `s.add(x)` | O(1) promedio | |
| `s.remove(x)` | O(1) promedio | error si no existe |
| `s.discard(x)` | O(1) promedio | sin error si no existe |
| `len(s)` | O(1) | |

### Por qué los sets son O(1)

Internamente Python hace **hash table**: calcula `hash(x)` (O(1) para int/str), va a la posición correspondiente. Las colisiones son raras → "promedio" O(1). En el peor caso teórico podría degradar, pero en práctica nunca.

### Hashable vs no hashable

```python
s = set()
s.add(5)                # ✅ int es hashable
s.add("hola")           # ✅ str es hashable
s.add((1, 2))           # ✅ tuple de hashables es hashable
s.add([1, 2])           # ❌ TypeError: unhashable type: 'list'
s.add({1: 2})           # ❌ TypeError: unhashable type: 'dict'
```

Regla: **inmutables hashables, mutables no**. Si necesitas meter una lista en un set, conviértela a tupla.

### `set` vs `dict` — cuándo cada uno

- **`set`**: solo necesitas saber **si vi un elemento o no** (presencia binaria).
- **`dict`**: necesitas asociar **información extra** al elemento (índice, frecuencia, lista de posiciones). Many problemas Medium suben de set a dict.

---

## Comparación final de las 4 soluciones

| Solución | Tiempo | Espacio | Modifica input | Veredicto |
|---|---|---|---|---|
| 1. Fuerza bruta | O(n²) | O(1) | No | ❌ TLE en LeetCode |
| 2. Ordenar | O(n log n) | O(1) | **Sí** | ⚠️ Aceptable, efecto secundario |
| 3. Hash set | **O(n)** | O(n) | No | ✅ **La idiomática** |
| 4. `len(set(nums))` | O(n) | O(n) | No | ✅ Elegante, mejor explicar antes |

---

## Auto-test (para ti, sin mirar el archivo)

Cuando hayas leído lo de arriba con calma, intenta esto **sin volver a abrir este archivo**:

1. Escribe la Solución 3 (hash set) desde cero, en un editor en blanco. Sin copiar.
2. Justifica en voz alta (o por escrito):
   - Por qué `set` y no `list`.
   - Cuál es la complejidad temporal y por qué.
   - Cuál es la complejidad espacial y por qué.
   - Cuál es el caso más temprano en que el algoritmo puede devolver `True`.
3. Modifica tu solución para que en vez de devolver `bool`, **devuelva el primer elemento duplicado que encuentre** (o `None` si no hay). Cambio mínimo.
4. Haz una mental run-through del array `[1, 2, 3, 1, 4]`: ¿qué tiene `vistos` paso a paso? ¿En qué iteración devuelve `True`?

Si fallaste algo, vuelve aquí, identifica qué fue (¿la complejidad? ¿el detalle de `set` vs `dict`? ¿olvidaste el `add`?), relé esa sección y repite el auto-test mañana.

---

## Cosas que te pueden preguntar en entrevista sobre este problema

- "¿Y si el array fuera una stream infinita y tuvieras memoria limitada?" → Bloom filter, probabilístico.
- "¿Y si los elementos pudieran ser objetos no hashables?" → tendrías que ordenarlos con un comparador o serializar a string.
- "¿Y si quisieras devolver TODOS los duplicados, no solo saber si existen?" → cambias el set por un dict de frecuencias y filtras al final.
- "¿Cómo cambiaría tu solución si supieras que el array está **casi ordenado** (cada elemento está a ≤ k posiciones de su lugar correcto)?" → ventana deslizante con set de tamaño k.

Estas variantes son las que vas a ver explícitamente en problemas posteriores. Cada una añade un giro al patrón base.

---

## Solución en C++ — contraste con Python

> 📘 Añadido para ver las diferencias de lenguaje. Mismo algoritmo, distinta semántica. Código compilable en [`217-contains-duplicate.cpp`](217-contains-duplicate.cpp).

```cpp
class Solution {
 public:
  bool hasDuplicate(std::vector<int>& nums) {
    std::unordered_set<int> seen;            // Python: vistos = set()
    for (int n : nums) {
      if (!seen.insert(n).second) return true;  // insert.second=false si ya estaba
    }
    return false;
  }
};
```

**Análisis:** Tiempo O(n), Espacio O(n) — igual que el Python idiomático.

**Diferencias clave Python ↔ C++:**
- `set()` → `std::unordered_set<int>` (hash set; `std::set` sería árbol O(log n)).
- `if num in vistos` → `seen.count(n)` o el idioma `seen.insert(n).second` (true si era nuevo), que combina comprobar+insertar en una pasada.
- `vistos.add(num)` → `seen.insert(n)`.
- El parámetro es `std::vector<int>&` (referencia, no copia); en Python la lista ya se pasa por referencia implícita.

---

## Conexiones

- [[MOC_Programacion]] — punto de entrada al área (cuando se cree).
- Próximo problema en el patrón: **LeetCode 242 — Valid Anagram** (mismo patrón con dict en lugar de set).

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrito Solución 3 desde cero sin mirar
- [ ] Justificada complejidad temporal y espacial
- [ ] Resueltas las 4 preguntas del auto-test
- [ ] Resuelto en LeetCode con éxito (Accepted en una sola submission)
- [ ] Hecho el problema 1 vez más a la semana siguiente (memoria a largo plazo)
