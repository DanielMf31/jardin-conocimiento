---
title: "LeetCode 981 — Time Based Key-Value Store"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/binary-search, patron/diseno-clase, patron/bisect]
type: nota
status: en-progreso
source: claude-code
aliases: [Time Based KV Store, LC 981, TimeMap, Diseño key-value con tiempo]
problem_id: 981
difficulty: medium
patron: binary-search
neetcode_order: 6
---

# LeetCode 981 — Time Based Key-Value Store

> **Sexto problema del patrón Binary Search**. Es **diseño de clase** (como [[155-min-stack]]) combinado con binary search. Buen ejemplo de cuándo el módulo `bisect` SÍ se usa en entrevistas (a diferencia de LC 704). Aplicación práctica: **versionado temporal** (Git internals, time-series databases, snapshot isolation en DBs).
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Diseña una estructura de datos `TimeMap` con dos operaciones:

- `set(key, value, timestamp)` — almacena la pareja `(key, value)` con timestamp.
- `get(key, timestamp)` — devuelve el valor asociado a `key` con el **timestamp más reciente ≤ timestamp dado**. Si no existe ninguno, devuelve `""`.

**Garantía**: todos los timestamps de `set` para una misma key son **estrictamente crecientes**.

**Ejemplo:**
```
TimeMap obj = new TimeMap()
obj.set("foo", "bar", 1)
obj.get("foo", 1)         # "bar"
obj.get("foo", 3)         # "bar" (último ≤ 3 es timestamp 1)
obj.set("foo", "bar2", 4)
obj.get("foo", 4)         # "bar2"
obj.get("foo", 5)         # "bar2"
```

**Restricciones:**
- `1 <= key.length, value.length <= 100`.
- `1 <= timestamp <= 10^7`.
- Hasta 2*10^5 llamadas a `set` y `get`.
- Los timestamps de cada key son crecientes.

**Plantilla:**
```python
class TimeMap:
    def __init__(self):
        ...
    def set(self, key: str, value: str, timestamp: int) -> None:
        ...
    def get(self, key: str, timestamp: int) -> str:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué estructura es lógica para `key → ...`? | Un `dict` |
| ¿Qué guardamos como value de cada key? | Una **lista de (timestamp, value)** ordenada por timestamp |
| ¿Por qué está ordenada? | Porque el enunciado garantiza que `set` se llama con timestamps crecientes |
| ¿Cómo encuentro el "último timestamp ≤ t"? | **Binary search** sobre la lista — específicamente, un **upper bound** de t (luego retroceder 1) |
| Edge case 1 | `get` con timestamp menor que todos los `set` → `""` |
| Edge case 2 | `get` con key que nunca tuvo `set` → `""` |

> **El insight**: para cada key, los `set` ya producen una lista ordenada de timestamps. `get` es esencialmente "encontrar el último timestamp ≤ t" → binary search clásico (con cuidado en los endpoints).

---

## Solución 1 — Linear search en `get` (NO óptima)

```python
class TimeMap:
    def __init__(self):
        self.store = {}                          # key -> list of (timestamp, value)

    def set(self, key, value, timestamp):
        if key not in self.store:
            self.store[key] = []
        self.store[key].append((timestamp, value))

    def get(self, key, timestamp):
        if key not in self.store:
            return ""
        # buscar el último timestamp <= timestamp dado
        result = ""
        for ts, val in self.store[key]:
            if ts <= timestamp:
                result = val                     # actualizar el "más reciente válido"
            else:
                break                            # como está ordenada, no hay más
        return result
```

**Análisis:**
- **set: O(1)**.
- **get: O(n)** donde n = número de set para esa key. [NO] Lento si hay muchas operaciones.
- **Veredicto:** funciona pero ineficiente con muchos set para una misma key.

---

## Solución 2 — Binary search manual en `get` (la canónica)

```python
class TimeMap:
    def __init__(self):
        self.store = {}

    def set(self, key, value, timestamp):
        if key not in self.store:
            self.store[key] = []
        self.store[key].append((timestamp, value))

    def get(self, key, timestamp):
        if key not in self.store:
            return ""
        arr = self.store[key]

        # Binary search: encontrar el mayor índice i tal que arr[i][0] <= timestamp
        left, right = 0, len(arr) - 1
        result = ""
        while left <= right:
            mid = left + (right - left) // 2
            if arr[mid][0] <= timestamp:
                result = arr[mid][1]             # candidato válido
                left = mid + 1                    # buscar uno aún más reciente
            else:
                right = mid - 1
        return result
```

**Trace mental** después de:

```
set("foo", "a", 1)
set("foo", "b", 3)
set("foo", "c", 5)
# store = {"foo": [(1,"a"), (3,"b"), (5,"c")]}

get("foo", 4):
  arr = [(1,"a"), (3,"b"), (5,"c")]
  left=0, right=2

  Iter 1: mid=1, arr[1]=(3,"b"), 3 <= 4 
    result = "b", left = 2

  Iter 2: left=2, right=2, mid=2, arr[2]=(5,"c"), 5 <= 4? NO
    right = 1

  left=2 > right=1 → exit

  Return "b" [OK]
```

**Análisis:**
- **set: O(1)**.
- **get: O(log n)**.
- **Veredicto:** [OK] **la canónica**.

---

## Solución 3 — `bisect` module (la pythonic)

```python
from bisect import bisect_right

class TimeMap:
    def __init__(self):
        self.timestamps = {}                     # key -> lista de timestamps
        self.values = {}                         # key -> lista de values (paralela)

    def set(self, key, value, timestamp):
        if key not in self.timestamps:
            self.timestamps[key] = []
            self.values[key] = []
        self.timestamps[key].append(timestamp)
        self.values[key].append(value)

    def get(self, key, timestamp):
        if key not in self.timestamps:
            return ""
        # bisect_right: índice donde insertar timestamp+1 → último <= timestamp es i-1
        i = bisect_right(self.timestamps[key], timestamp)
        if i == 0:
            return ""                            # no hay nada <= timestamp
        return self.values[key][i - 1]
```

**Análisis:** mismo O(log n).

**Veredicto:** [OK] **la pythonic**. Usar `bisect` aquí es **aceptable** en entrevista (a diferencia de [[704-binary-search]]) porque el problema es de diseño y `bisect` es accesorio, no el algoritmo principal.

> **`bisect_right(arr, x)`** devuelve el índice donde insertar `x+epsilon` para mantener el orden, o equivalentemente: el primer índice cuyo valor sea `> x`. El último valor `<= x` está en `i-1`.

---

## El patrón general — "Diseño con búsqueda temporal"

**Cuándo aplicar**:

> Cuando una clase necesita responder consultas del tipo "valor en el momento T" sobre datos que se acumulan ordenadamente en el tiempo. Ejemplos: bases de datos versionadas, time-series, snapshots.

**Plantilla mental**:

```python
class TimeIndex:
    def __init__(self):
        self.data = {}                           # key -> list[(time, value)]

    def set(self, key, value, time):
        self.data.setdefault(key, []).append((time, value))

    def get(self, key, time):
        if key not in self.data:
            return default
        arr = self.data[key]
        # binary search del mayor index con arr[i][0] <= time
        ...
```

**Tres señales** del patrón:

1. Las inserciones llegan en orden cronológico.
2. Las consultas piden "el más reciente válido en T".
3. La fuerza bruta es O(n) y existe orden explotable.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **1146. Snapshot Array** | Snapshot completo del array en cada momento |
| **716. Max Stack** | Diseño con max query en O(log n) |

---

## Conceptos a interiorizar

### `dict.setdefault(key, default)`

Si la key no existe, la crea con el default y devuelve el default. Si existe, devuelve el value sin tocar nada.

```python
d.setdefault('foo', []).append(1)
# Equivalente a:
# if 'foo' not in d: d['foo'] = []
# d['foo'].append(1)
```

### `bisect_right` vs `bisect_left`

```python
arr = [1, 3, 3, 5]

bisect_left(arr, 3)              # 1 (índice del PRIMER 3)
bisect_right(arr, 3)             # 3 (índice DESPUÉS del último 3)

# Para "último valor <= x":
i = bisect_right(arr, x)
last_le = arr[i - 1] if i > 0 else None

# Para "primer valor >= x":
i = bisect_left(arr, x)
first_ge = arr[i] if i < len(arr) else None
```

Memoriza estas dos recetas. Las verás en muchos problemas.

### Cuándo usar `bisect` en entrevista

- [OK] **Aceptable**: cuando el problema es de **diseño** o **complejo** y `bisect` es una herramienta auxiliar (LC 981).
- [NO] **NO recomendado**: cuando el problema es **explícitamente sobre binary search** (LC 704). Ahí quieren ver que sabes implementarlo.

---

## Comparación final de las 3 soluciones

| Solución | set | get | Veredicto |
|---|---|---|---|
| 1. Linear search | O(1) | O(n) | Funciona, lenta |
| 2. **Binary search manual** | O(1) | **O(log n)** | [OK] La canónica |
| 3. **`bisect` module** | O(1) | **O(log n)** | [OK] La pythonic (aceptable aquí) |

---

## Auto-test (para ti, sin mirar el archivo)

1. Implementa la **Solución 2** desde cero.
2. Justifica:
   - Por qué `result = arr[mid][1]` se actualiza incluso cuando hay match (no se devuelve directo).
   - Por qué `left = mid + 1` después del match (en lugar de `right = mid - 1`).
   - Por qué se devuelve `""` cuando key no existe.
3. Implementa la **Solución 3** con `bisect_right`. Justifica el `i - 1`.
4. Trace mental con: set("foo", "a", 1), set("foo", "b", 5), get("foo", 3), get("foo", 0).
5. **Bonus** — extiende para `delete(key, timestamp)` que borra el value en ese timestamp exacto.

---

## Cosas que te pueden preguntar en entrevista

- **"Por qué guardar lista por key en lugar de un solo dict (key, time) → value?"** → Para hacer binary search por timestamp. Un dict no preserva orden ni permite búsqueda binaria.
- **"Y si los timestamps no fueran crecientes?"** → Insertar con `bisect.insort` mantiene el orden, pero set se vuelve O(n) por el shift. Trade-off.
- **"¿Cuánta memoria usa peor caso?"** → O(n) donde n = total de operaciones set. Con muchas keys distintas, es como mucho n entradas distribuidas.
- **"¿Y si quisieras `get` en O(1)?"** → No es posible en general, pero con índices precomputados (e.g. para timestamps específicos predefinidos) sí.

---

## Conexiones

- [[155-min-stack]] — diseño de clase con stack auxiliar.
- [[704-binary-search]] — binary search clásico.
- [[33-search-in-rotated-sorted-array]] — patrón anterior.
- Próximo: [[4-median-of-two-sorted-arrays]] — el Hard del patrón.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Implementada Solución 2 desde cero
- [ ] Implementada Solución 3 con `bisect_right`
- [ ] Justificado el `i - 1` en bisect_right
- [ ] Resuelto en LeetCode con éxito
