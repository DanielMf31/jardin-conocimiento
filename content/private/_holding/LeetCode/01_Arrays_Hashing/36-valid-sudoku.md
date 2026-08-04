---
title: "LeetCode 36 — Valid Sudoku"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/arrays-hashing, patron/hash-set, patron/multiple-constraints]
type: nota
status: en-progreso
source: claude-code
aliases: [Valid Sudoku, LC 36, isValidSudoku, Sudoku validación]
problem_id: 36
difficulty: medium
patron: arrays-hashing
neetcode_order: 8
---

# LeetCode 36 — Valid Sudoku

> **Octavo problema del NeetCode 150 en Arrays & Hashing**. Combina lo que sabes de hash sets con **claves compuestas / múltiples restricciones simultáneas**. Es un problema de validación, no de resolución (NO tienes que resolver el sudoku, solo verificar que lo dado es consistente).
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Determina si un tablero **9x9** de Sudoku es **válido**. Solo hay que validar las **celdas rellenadas** (no resolver el sudoku) según estas reglas:

1. Cada **fila** debe contener los dígitos `1-9` sin repetición.
2. Cada **columna** debe contener los dígitos `1-9` sin repetición.
3. Cada **sub-grid 3x3** (de los 9 que componen el tablero) debe contener los dígitos `1-9` sin repetición.

**Nota:**
- Las celdas vacías están representadas por `'.'`.
- Un tablero parcialmente lleno **puede ser válido** aunque no esté completo, siempre que no viole las tres reglas en lo que sí está lleno.

**Ejemplo 1:**
```
Input:  board =
[["5","3",".",".","7",".",".",".","."],
 ["6",".",".","1","9","5",".",".","."],
 [".","9","8",".",".",".",".","6","."],
 ["8",".",".",".","6",".",".",".","3"],
 ["4",".",".","8",".","3",".",".","1"],
 ["7",".",".",".","2",".",".",".","6"],
 [".","6",".",".",".",".","2","8","."],
 [".",".",".","4","1","9",".",".","5"],
 [".",".",".",".","8",".",".","7","9"]]
Output: true
```

**Ejemplo 2** (mismo tablero pero con un `8` añadido en la primera celda):
```
Output: false (la columna 0 ahora tiene dos 8)
```

**Restricciones:**
- `board.length == 9`, `board[i].length == 9`.
- `board[i][j]` es un dígito `1-9` o `'.'`.

**Plantilla:**
```python
class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Hay que resolver el sudoku? | **NO**. Solo validar lo que ya está |
| ¿Qué hacer con `'.'`? | Saltarse, no entra en validación |
| ¿Tablero siempre 9x9? | Sí, fijo |
| ¿Cómo identifico el sub-grid 3x3 de una celda `(r, c)`? | `(r // 3, c // 3)` |
| ¿Es O(n²) un problema con n=9? | NO. n=9 es **constante**, todo el algoritmo es O(1) técnicamente |
| ¿Por qué entonces es Medium si n es constante? | Por la **idea** de modelar 3 restricciones simultáneamente con elegancia |

---

## Solución 1 — Tres recorridos separados (la verbosa)

Un recorrido para filas, otro para columnas, otro para boxes.

```python
class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        # Filas
        for r in range(9):
            seen = set()
            for c in range(9):
                v = board[r][c]
                if v == '.':
                    continue
                if v in seen:
                    return False
                seen.add(v)

        # Columnas
        for c in range(9):
            seen = set()
            for r in range(9):
                v = board[r][c]
                if v == '.':
                    continue
                if v in seen:
                    return False
                seen.add(v)

        # Boxes 3x3
        for box_r in range(3):
            for box_c in range(3):
                seen = set()
                for r in range(box_r * 3, box_r * 3 + 3):
                    for c in range(box_c * 3, box_c * 3 + 3):
                        v = board[r][c]
                        if v == '.':
                            continue
                        if v in seen:
                            return False
                        seen.add(v)

        return True
```

**Análisis:**
- **Tiempo: O(81)** = O(1) constante.
- **Espacio: O(9)** = O(1).
- **Veredicto:** funciona, pero verbosa y con código duplicado tres veces. En entrevista preferirías la Solución 2.

---

## Solución 2 — Recorrido único con tres dicts/sets (la idiomática)

**La idea clave**: un solo recorrido `for r in 0..8: for c in 0..8`. Mantener tres "memorias":
- `rows[r]` = set de dígitos vistos en la fila `r`.
- `cols[c]` = set de dígitos vistos en la columna `c`.
- `boxes[(r//3, c//3)]` = set de dígitos vistos en el box correspondiente.

Para cada celda `(r, c)` con valor `v`, chequear las tres memorias. Si `v` ya está en alguna, return `False`. Si no, añadir.

```python
from collections import defaultdict

class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        rows = defaultdict(set)
        cols = defaultdict(set)
        boxes = defaultdict(set)

        for r in range(9):
            for c in range(9):
                v = board[r][c]
                if v == '.':
                    continue
                box_key = (r // 3, c // 3)
                if v in rows[r] or v in cols[c] or v in boxes[box_key]:
                    return False
                rows[r].add(v)
                cols[c].add(v)
                boxes[box_key].add(v)
        return True
```

**Análisis:**
- **Tiempo: O(81)** = O(1).
- **Espacio: O(81)** = O(1) — máximo 81 entradas distribuidas.
- **Veredicto:** [OK] **la respuesta esperada en entrevista**. Clara, sin duplicación, modela las tres restricciones uniformemente.

> **`r // 3, c // 3` para box ID**: si `r = 5, c = 7`, entonces `r // 3 = 1, c // 3 = 2`, que identifica el box "fila 1, columna 2" (de los 3x3 = 9 boxes). Cualquier celda en ese box da el mismo `(1, 2)`.

---

## Solución 3 — Un solo set con claves compuestas (la elegante)

**La idea muy clara**: en vez de tres estructuras, **una sola** con claves que codifican **el tipo de restricción**. Cada celda con valor `v` genera **3 claves**:
- `("row", r, v)` — "el valor `v` apareció en la fila `r`".
- `("col", c, v)` — "el valor `v` apareció en la columna `c`".
- `("box", r//3, c//3, v)` — "el valor `v` apareció en el box `(r//3, c//3)`".

Si alguna de las tres ya está en el set → violación.

```python
class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        seen = set()
        for r in range(9):
            for c in range(9):
                v = board[r][c]
                if v == '.':
                    continue
                claves = (
                    ("row", r, v),
                    ("col", c, v),
                    ("box", r // 3, c // 3, v),
                )
                for clave in claves:
                    if clave in seen:
                        return False
                    seen.add(clave)
        return True
```

**Análisis:** mismo O(1) tiempo y espacio. **Más conciso**. La elegancia está en colapsar tres conceptos en una sola estructura mediante **claves tipadas**.

> **Patrón importante**: cuando tienes múltiples restricciones del mismo tipo, una **sola estructura con claves compuestas** suele ser más limpia que múltiples estructuras separadas.

### Desglose detallado de la Solución 3 — tuplas heterogéneas y claves tipadas

Si la sintaxis `("row", r, v)` y la estructura general te resultan extrañas, esta es la explicación pieza por pieza.

#### Recordatorio: tuplas pueden tener más de 2 elementos

Las tuplas en Python **no son solo pares**. Pueden tener cualquier número de elementos:

```python
t1 = ()                       # 0 elementos
t2 = (5,)                     # 1 elemento (la coma es OBLIGATORIA)
t3 = (5, 7)                   # 2 elementos (un par)
t4 = (5, 7, 9)                # 3 elementos (una "tripleta")
t5 = (5, 7, 9, 11)            # 4 elementos
t6 = ("hola", 5, True, 3.14)  # 4 elementos de TIPOS MEZCLADOS
```

Lo que las hace tuplas son los **paréntesis y las comas**. Y a diferencia de las listas, son **inmutables** (no se modifican después de crearlas).

#### Las tuplas son heterogéneas por defecto

Mezclar tipos dentro de una tupla **no es raro** en Python. Las tuplas son heterogéneas por naturaleza:

```python
mezclada = ("row", 5, "8")     # string, int, string
otra = ("box", 1, 2, "3")      # string, int, int, string
```

La única regla para meterlas en un `set` (o usarlas como clave de `dict`) es que **todos sus elementos sean hashables**:

| Tipo | ¿Hashable? | ¿Puede ir en una tupla que va a un set? |
|---|---|---|
| `int`, `float`, `bool` | [OK] | Sí |
| `str` | [OK] | Sí |
| `tuple` (de hashables) | [OK] | Sí |
| `frozenset` | [OK] | Sí |
| `list` | [NO] | NO — la tupla deja de ser hashable |
| `dict` | [NO] | NO |
| `set` | [NO] | NO (pero `frozenset` sí) |

Strings e ints son hashables → `("row", 5, "8")` es perfectamente hashable y puede ir en un set.

#### Es un set, NO un dict (la confusión principal)

```python
seen = set()                          # ← esto es un SET
seen.add(("row", r, v))               # añadimos una TUPLA al set
```

`seen` es un **set**. Los **elementos** de ese set son **tuplas**. No hay claves ni valores — solo elementos.

Compara los tres tipos:

```python
# Set: solo elementos. NO hay "key" ni "value".
seen = set()
seen.add(("row", 5, "8"))             # añadir un elemento
("row", 5, "8") in seen               # True — chequear pertenencia

# Dict: pares clave → valor. Hay "key" y "value".
mapa = {}
mapa[("row", 5)] = "8"                # asignar value a una key
mapa[("row", 5)]                      # "8" — leer el value de esa key

# List: secuencia ordenada. Acceso por índice.
lista = []
lista.append(("row", 5, "8"))         # añadir al final
lista[0]                              # ("row", 5, "8")
```

**Pista visual** para distinguirlos:
- Set: `{...}` o `set()`. Solo elementos.
- Dict: `{...: ...}` con `:` entre key y value.
- List: `[...]` con corchetes.

En esta solución **NO HAY DICT NUNCA** — solo set. Los paréntesis que ves alrededor de los grupos de 3 o 4 valores son **paréntesis de tupla**.

#### Por qué se mete tanta info en una sola tupla

¿Por qué `("row", r, v)` y no, por ejemplo, dos sets separados (`rows_set`, `cols_set`)?

Porque **una sola estructura es más uniforme**. Si guardáramos solo `(r, v)`, no podríamos distinguir si **el valor `v` apareció en la fila `r`** o **en la columna `r`** — son cosas distintas.

La string `"row"` / `"col"` / `"box"` actúa como **etiqueta de tipo** que separa los espacios:

```python
# Sin etiqueta: ambigüedad total
seen.add((5, "8"))      # ¿significa fila 5 con 8? ¿columna 5 con 8?

# Con etiqueta: cada uno es único
seen.add(("row", 5, "8"))   # CLARO: fila 5 tiene un 8
seen.add(("col", 5, "8"))   # CLARO: columna 5 tiene un 8
```

Es el equivalente a tener tres compartimentos (rows, cols, boxes) **dentro de una sola caja**, distinguidos por la etiqueta.

#### Trace concreto detectando una violación

Imagina que el tablero tiene este aspecto al inicio:

```
Fila 0: 5 . .
Fila 1: . 5 .
```

**Procesamos `board[0][0] = '5'`:**

```python
r, c, v = 0, 0, '5'
box_key = (r // 3, c // 3) = (0, 0)

claves = (
    ("row", 0, '5'),         # "el 5 apareció en fila 0"
    ("col", 0, '5'),         # "el 5 apareció en columna 0"
    ("box", 0, 0, '5'),      # "el 5 apareció en box (0,0)"
)

# Comprobamos cada una
for clave in claves:
    if clave in seen:
        return False         # alguna ya existe → repetido
    seen.add(clave)

# Estado de seen tras procesar (0, 0, '5'):
seen = {
    ("row", 0, '5'),
    ("col", 0, '5'),
    ("box", 0, 0, '5'),
}
```

**Procesamos `board[1][1] = '5'`:**

```python
r, c, v = 1, 1, '5'
box_key = (1 // 3, 1 // 3) = (0, 0)

claves = (
    ("row", 1, '5'),         # ¿está en seen? NO (es row 1, no row 0)
    ("col", 1, '5'),         # ¿está en seen? NO (es col 1, no col 0)
    ("box", 0, 0, '5'),      # ¿está en seen? SÍ ⚠️
)

# Detecta conflicto: el 5 ya estaba en el mismo box
return False
```

La tupla `("box", 0, 0, '5')` **ya existía** porque el `'5'` de la fila 0 estaba en el box (0,0), y el `'5'` de la fila 1 también está en el box (0,0). **Eso es lo que viola la regla del sudoku.**

Las etiquetas (`"row"`, `"col"`, `"box"`) garantizan que las restricciones de fila, columna y box **no se confundan entre sí** dentro del mismo set.

#### La estructura `claves = (...)` que ves en el código

```python
claves = (
    ("row", r, v),
    ("col", c, v),
    ("box", r // 3, c // 3, v),
)
```

**Eso es una TUPLA DE TUPLAS** (3 tuplas dentro de una tupla externa).

- La tupla externa `(...)` agrupa las 3 internas.
- Cada interna `("row", r, v)` es una clave para el set.

Es solo una forma compacta de tener 3 valores para iterar:

```python
# Equivalente sin tupla externa (con lista):
claves = [
    ("row", r, v),
    ("col", c, v),
    ("box", r // 3, c // 3, v)]

for clave in claves:
    if clave in seen:
        return False
    seen.add(clave)
```

Funcionalmente idéntico. Pero usar una **tupla externa** en vez de lista deja claro que es un grupo fijo de exactamente 3 elementos — no se va a modificar.

#### Resumen visual

```
┌─────────────────────────────────────────────────┐
│  seen   (es un SET, no un dict)                 │
│  ┌─────────────────────────────────────────┐    │
│  │ ("row", 0, '5')        ←─ tupla 3 elems │    │
│  │ ("col", 0, '5')        ←─ tupla 3 elems │    │
│  │ ("box", 0, 0, '5')     ←─ tupla 4 elems │    │
│  │ ("row", 2, '7')                          │    │
│  │ ...                                      │    │
│  └─────────────────────────────────────────┘    │
│         ↑                                       │
│  Cada elemento es una tupla heterogénea         │
│  (mezcla de strings e ints).                    │
│  La string al principio actúa como ETIQUETA     │
│  para separar los 3 espacios de restricciones.  │
└─────────────────────────────────────────────────┘
```

#### Otros sitios donde aparece este patrón

El truco de "tuplas heterogéneas como elementos de set" reaparece en muchos problemas:

- **Backtracking sobre grids** (LC 79 Word Search, LC 51 N-Queens): guardar `(r, c)` o `(r, c, depth)` en un set de "visitados".
- **Modelado de estados** en BFS/DFS sobre grafos: `(node, time, energy)` como estado completo.
- **Dedup en grafos**: aristas como tuplas `(min(u, v), max(u, v))` para evitar contar la misma arista dos veces.
- **LC 49 Group Anagrams**: la clave canónica es una tupla de 26 conteos (caso similar).

Cuando veas tuplas con 3 o 4 elementos heterogéneos en un set, casi siempre es esta misma idea: **multi-dimensión codificada en una clave plana**.

---

## El patrón general — "Múltiples restricciones con claves compuestas"

**Cuándo aplicar**:

> Cuando un problema te pide validar / detectar **simultáneamente** varias condiciones del mismo tipo (e.g. "no repetidos en estas N dimensiones"), y todas pueden expresarse como una **clave única** en un set.

**Plantilla mental**:

```python
def patron_multi_constraints(elementos):
    seen = set()
    for elem in elementos:
        for restriccion in restricciones(elem):
            clave = (tipo_de_restriccion, contexto, valor)
            if clave in seen:
                return False  # violación
            seen.add(clave)
    return True
```

**Tres señales** del patrón:

1. El problema lista varias reglas del tipo "no repetidos en X".
2. Todas las reglas se aplican a los mismos elementos.
3. Cada regla tiene un "contexto" identificable (fila, columna, box, ...).

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **37. Sudoku Solver** | Lo mismo pero **resolver** el sudoku (backtracking) |
| **51. N-Queens** | "No dos reinas en la misma fila/columna/diagonal" → mismo patrón con 4 restricciones |
| **48. Rotate Image** | Mismo nivel de "manejar matriz 2D" sin restricciones de unicidad |
| **289. Game of Life** | Reglas locales sobre matriz |

---

## Conceptos a interiorizar

### División entera para boxes

```python
# Mapear celda (r, c) a box (br, bc):
br, bc = r // 3, c // 3

# Mapear box (br, bc) a rango de celdas:
rows = range(br * 3, br * 3 + 3)
cols = range(bc * 3, bc * 3 + 3)
```

Truco general: **división entera reduce un espacio continuo a uno discreto** (e.g. agrupar timestamps en buckets, agrupar coordenadas en celdas de grilla, etc.).

### Tuplas como claves de set (recordatorio de [[49-group-anagrams]])

```python
seen = set()
seen.add(("row", 5, "8"))            # OK, tupla hashable
seen.add(("box", 1, 2, "3"))         # OK
"row", 5, "8" in seen                 # ⚠️ esto es ((), seen), no lo que quieres

# Forma correcta:
("row", 5, "8") in seen               # True
```

### `defaultdict(set)` vs `dict()` con chequeo

```python
# Verboso
if r not in rows:
    rows[r] = set()
rows[r].add(v)

# Idiomático
rows = defaultdict(set)
rows[r].add(v)
```

---

## Comparación final de las 3 soluciones

| Solución | Líneas | Claridad | Veredicto |
|---|---|---|---|
| 1. Tres recorridos separados | ~30 | Baja (código duplicado) | Funciona, no idiomática |
| 2. **Recorrido único con 3 dicts** | ~15 | Alta | [OK] La idiomática |
| 3. **Un set con claves compuestas** | ~12 | Muy alta | [OK] La elegante |

Todas son O(1) en tiempo y espacio.

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** (3 dicts) desde cero.
2. Justifica:
   - Por qué `(r // 3, c // 3)` identifica unívocamente el box.
   - Por qué el orden de los chequeos `if v in rows[r] or v in cols[c] or v in boxes[...]` es eficiente (short-circuit).
3. Implementa la **Solución 3** (claves compuestas) desde cero.
4. Trace mental: si modificas `board[0][0]` de `'5'` a `'.'` ¿qué pasa con `rows[0]`, `cols[0]`, `boxes[(0,0)]` después del recorrido completo?
5. **Bonus** — extiende el problema: en vez de devolver `bool`, devuelve la **lista de celdas conflictivas** (la primera violación que se detecte).

---

## Cosas que te pueden preguntar en entrevista

- **"¿Cómo extenderías esto a un sudoku 16x16 o NxN (con boxes √N x √N)?"** → Lo único que cambia es los rangos y el divisor de box (`r // sqrt(N)`). El patrón es idéntico.
- **"Y si el tablero pudiera no estar completo, ¿qué cambia?"** → Nada: el algoritmo solo valida lo presente, ya maneja `'.'` (lo salta).
- **"Cuál es la diferencia entre validar un sudoku y resolverlo?"** → Validar es O(n²); resolver es NP-completo (en general; para sudoku 9x9 hay backtracking razonable). LC 37 es el solver.
- **"Por qué tu Solución 3 es 'más elegante' que la 2?"** → Modelar las 3 restricciones uniformemente como un solo concepto ("apareció antes esta combinación de tipo+contexto+valor"). Reduce duplicación conceptual.

---

## Conexiones

- [[217-contains-duplicate]] — el patrón "he visto X antes" base.
- [[49-group-anagrams]] — primera vez que usas tuplas como claves.
- [[238-product-of-array-except-self]] — patrón anterior.
- Próximo: [[128-longest-consecutive-sequence]] — el último Arrays & Hashing del NeetCode 150.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Implementada Solución 3 desde cero
- [ ] Justificada `(r // 3, c // 3)` como identificador de box
- [ ] Resuelto en LeetCode con éxito
- [ ] Hecho 1 vez más a la semana siguiente
