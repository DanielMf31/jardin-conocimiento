---
title: "LeetCode 3 — Longest Substring Without Repeating Characters"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/sliding-window, patron/hash-set]
type: nota
status: en-progreso
source: claude-code
aliases: [Longest Substring Without Repeating, LC 3, lengthOfLongestSubstring, Substring sin repetidos]
problem_id: 3
difficulty: medium
patron: sliding-window
neetcode_order: 2
---

# LeetCode 3 — Longest Substring Without Repeating Characters

> **Segundo problema del patrón Sliding Window** — y el **prototipo del patrón "ventana de tamaño variable"** que vas a ver muchísimo. Una ventana que crece por la derecha y se contrae por la izquierda cuando se rompe una invariante. Aprenderlo bien desbloquea casi todo el patrón.
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un string `s`, encuentra la **longitud del substring más largo sin caracteres repetidos**.

**Ejemplo 1:**
```
Input:  s = "abcabcbb"
Output: 3
        "abc" tiene longitud 3 (luego se repite la 'a')
```

**Ejemplo 2:**
```
Input:  s = "bbbbb"
Output: 1
        Solo "b" — todos los caracteres son iguales
```

**Ejemplo 3:**
```
Input:  s = "pwwkew"
Output: 3
        "wke" tiene longitud 3. Nota: "pwke" NO vale (no es contiguo)
```

**Restricciones:**
- `0 <= s.length <= 5 * 10^4`
- `s` consiste en letras inglesas, dígitos, símbolos y espacios.

> **Importante**: el substring debe ser **contiguo**, no una subsecuencia.

**Plantilla:**
```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` — longitud, no el substring |
| ¿Substring contiguo o subsecuencia? | **Contiguo** — caracteres consecutivos en el string original |
| ¿Sensible a mayúsculas? | Sí (`'A'` ≠ `'a'`) |
| ¿Strings vacías? | `len = 0` para `""` |
| ¿Strings con un solo char? | Devolver 1 |
| Edge case 1 | `"abcabcbb"` → 3 (no 5 ni 8) |
| Edge case 2 | `"abc"` (sin repetidos) → 3 |
| Edge case 3 | Solo símbolos / espacios → cuentan como caracteres |

---

## Solución 1 — Fuerza bruta O(n³)

Probar todos los substrings y para cada uno verificar si tiene duplicados.

```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        n = len(s)
        best = 0
        for i in range(n):
            for j in range(i, n):
                if len(set(s[i:j+1])) == j - i + 1:    # sin duplicados
                    best = max(best, j - i + 1)
        return best
```

**Análisis:**
- **Tiempo: O(n³)** — n² substrings × O(n) chequeo de duplicados.
- **Espacio: O(n)** por el set.
- **Veredicto:** [NO] TLE.

---

## Solución 2 — Sliding window con set (la canónica)

**La idea clave**: una **ventana** definida por dos punteros `left` y `right`. Mantén un `set` con los caracteres en la ventana actual.

- **Expand right**: añadir cada nuevo carácter al set.
- **Shrink left**: si el nuevo carácter ya estaba (duplicado), avanzar `left` quitando caracteres del set hasta que el duplicado desaparezca.
- En cada paso, actualizar la mejor longitud.

```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        seen = set()
        left = 0
        best = 0
        for right, char in enumerate(s):
            while char in seen:
                seen.remove(s[left])
                left += 1
            seen.add(char)
            best = max(best, right - left + 1)
        return best
```

**Trace mental con `s = "abcabcbb"`**:

| right | char | Acción | seen | left | window | best |
|---|---|---|---|---|---|---|
| 0 | 'a' | add | {'a'} | 0 | "a" | 1 |
| 1 | 'b' | add | {'a','b'} | 0 | "ab" | 2 |
| 2 | 'c' | add | {'a','b','c'} | 0 | "abc" | **3** |
| 3 | 'a' | duplicado → shrink: remove 'a', left=1; add | {'b','c','a'} | 1 | "bca" | 3 |
| 4 | 'b' | duplicado → shrink: remove 'b', left=2; add | {'c','a','b'} | 2 | "cab" | 3 |
| 5 | 'c' | duplicado → shrink: remove 'c', left=3; add | {'a','b','c'} | 3 | "abc" | 3 |
| 6 | 'b' | duplicado → shrink: remove 'a' (left=4), remove 'b' (left=5); add | {'c','b'} | 5 | "cb" | 3 |
| 7 | 'b' | duplicado → shrink: remove 'c' (left=6), remove 'b' (left=7); add | {'b'} | 7 | "b" | 3 |

Resultado: `3` [OK].

**Análisis:**
- **Tiempo: O(n)** — análisis amortizado: `left` y `right` cada uno avanzan ≤ n veces.
- **Espacio: O(min(n, alfabeto))** — el set tiene como mucho |alfabeto| caracteres.
- **Veredicto:** [OK] la respuesta canónica.

### Desglose detallado de la Solución 2 — qué es la ventana y por qué los dos punteros

Si "sliding window con dos punteros" te resulta confuso al principio, esta es la explicación pieza por pieza.

#### Qué es una "ventana" aquí

Una **ventana** es un trozo contiguo del string definido por dos índices: `left` (incluido) y `right` (incluido). Es decir, los caracteres en `s[left:right+1]`.

Visualmente, sobre `s = "abcabcbb"`:

```
Índice:  0  1  2  3  4  5  6  7
Char:    a  b  c  a  b  c  b  b
                ↑      ↑
              left=2 right=4

Ventana = s[2..4] = "cab"
Longitud = right - left + 1 = 4 - 2 + 1 = 3
```

#### Para qué los dos punteros

- **`right`** es el "explorador": avanza siempre, una posición por iteración del `for`. Lleva el ritmo. Va **probando incluir cada nuevo carácter** en la ventana.
- **`left`** es el "limpiador": solo avanza cuando hay un problema. Su trabajo es **mantener la ventana válida** (= sin duplicados).

La idea: vamos extendiendo la ventana por la derecha. Si ese nuevo carácter rompe la regla "sin duplicados", **encogemos la ventana por la izquierda** hasta que se vuelva válida otra vez. La ventana **se desliza** así por el string.

#### La invariante que mantiene todo el algoritmo

> **En cada momento del bucle**, la ventana `s[left..right]` no tiene caracteres duplicados, y `seen` contiene exactamente esos caracteres.

Esa invariante se mantiene siempre. Lo único que hace el algoritmo es **respetarla**.

#### El set: ¿por qué hace falta?

`seen` es el set de caracteres **que están actualmente en la ventana**. Sirve para responder rápido a la pregunta: "¿el nuevo carácter ya está en la ventana?". Sin set tendrías que mirar cada carácter de la ventana → O(n) por consulta. Con set → O(1).

> **Comparación de complejidades según qué uses**:
> - **Sin ventana, fuerza bruta** (probando todos los substrings): O(n³) — n² substrings × O(n) verificar duplicados.
> - **Ventana pero con `list` en vez de `set`** para `seen`: O(n²) — el loop sigue siendo lineal pero `char in list` es O(n).
> - **Ventana + `set`**: O(n) — la solución de aquí.

#### Trace visual completo con `s = "abcabcbb"`

Estado inicial: `seen = {}`, `left = 0`, `best = 0`.

**Iter 1**: `right = 0`, `char = 'a'`

- ¿`'a'` en `seen`? NO → no entra al while.
- `seen.add('a')` → `{a}`.
- Ventana: `s[0..0] = "a"`. Longitud = 1. `best = 1`.

```
Índice:  0  1  2  3  4  5  6  7
         ↑
       L=R=0
        [a]
```

**Iter 2**: `right = 1`, `char = 'b'`

- ¿`'b'` en `seen`? NO. Add. `seen = {a, b}`.
- Ventana: `"ab"`. Longitud = 2. `best = 2`.

```
Índice:  0  1  2  3  4  5  6  7
         ↑  ↑
         L  R
        [a  b]
```

**Iter 3**: `right = 2`, `char = 'c'`

- NO en seen. Add. `seen = {a, b, c}`.
- Ventana: `"abc"`. Longitud = 3. `best = 3`.

```
Índice:  0  1  2  3  4  5  6  7
         ↑     ↑
         L     R
        [a  b  c]
```

**Iter 4**: `right = 3`, `char = 'a'` ← **¡aquí entra el while!**

- ¿`'a'` en `seen`? **SÍ** → while:
  - `seen.remove(s[0]='a')` → `{b, c}`.
  - `left = 1`.
  - ¿`'a'` en seen? NO → salir.
- Add `'a'`. `seen = {b, c, a}`.
- Ventana: `s[1..3] = "bca"`. Longitud = 3. `best = 3`.

```
Índice:  0  1  2  3  4  5  6  7
            ↑     ↑
            L     R
            [b  c  a]
```

> **Aquí ves al `left` haciendo su trabajo**: el `'a'` nuevo entra en conflicto con el `'a'` en posición 0. El `while` "limpia" la ventana avanzando `left` y eliminando del set hasta que el conflicto desaparezca.

**Iter 5**: `right = 4`, `char = 'b'`

- En seen → while: `remove('b')`, `left=2`. Salir.
- Add. `seen = {c, a, b}`. Ventana `"cab"`. Longitud 3.

```
Índice:  0  1  2  3  4  5  6  7
               ↑     ↑
               L     R
               [c  a  b]
```

**Iter 6**: `right = 5`, `char = 'c'`

- En seen → while: `remove('c')`, `left=3`. Salir.
- Add. `seen = {a, b, c}`. Ventana `"abc"`. Longitud 3.

```
Índice:  0  1  2  3  4  5  6  7
                  ↑     ↑
                  L     R
                  [a  b  c]
```

**Iter 7**: `right = 6`, `char = 'b'` ← **el while corre 2 veces aquí**

- En seen → while:
  - `remove(s[3]='a')` → `{b, c}`. `left=4`. ¿`'b'` en seen? **SÍ aún** → seguir.
  - `remove(s[4]='b')` → `{c}`. `left=5`. ¿`'b'`? NO → salir.
- Add. `seen = {c, b}`. Ventana `s[5..6] = "cb"`. Longitud 2.

```
Índice:  0  1  2  3  4  5  6  7
                        ↑  ↑
                        L  R
                        [c  b]
```

> Aquí el while hizo **dos avances** del `left`. Tuvo que limpiar dos caracteres porque hubo que "saltarse" el `'a'` para llegar al `'b'` que duplicaba.

**Iter 8**: `right = 7`, `char = 'b'`

- En seen → while:
  - `remove(s[5]='c')` → `{b}`. `left=6`. ¿`'b'`? Aún SÍ.
  - `remove(s[6]='b')` → `{}`. `left=7`. ¿`'b'`? NO.
- Add. `seen = {b}`. Ventana `"b"`. Longitud 1.

**Resultado final**: `best = 3` [OK] (substrings óptimos: `"abc"`, `"bca"`, `"cab"`, `"abc"`).

#### La animación: cómo rueda la ventana

```
"abcabcbb"

Iter:  Ventana
1:     [a]
2:     [ab]
3:     [abc]                ← longitud 3 (best)
4:        [bca]             ← longitud 3
5:           [cab]          ← longitud 3
6:              [abc]       ← longitud 3
7:                 [cb]
8:                    [b]
```

La ventana **rueda** por el string. En cada momento contiene **el mejor candidato terminando en `right`** que cumple la invariante "sin duplicados". `right` y `left` **nunca retroceden** — esto es lo que da el O(n) amortizado.

#### Por qué O(n) (no O(n²) como podría parecer)

A pesar del while dentro del for: **`left` solo avanza, nunca retrocede**. A lo largo de toda la ejecución, `left` avanza ≤ n veces (no n por iteración). `right` también avanza n veces. **Total: ≤ 2n operaciones** → O(n).

Es el mismo argumento amortizado que ya viste en [[125-valid-palindrome]] y [[128-longest-consecutive-sequence]]. Cuando veas un while interno donde "los punteros solo avanzan", piensa amortización.

---

## Solución 3 — Sliding window con dict de últimos índices (optimización)

**La idea**: en lugar de avanzar `left` un paso por iteración del while, **saltar directamente** al índice después del duplicado. Necesitas guardar **el índice** del último visto, no solo presencia.

```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        last = {}                                      # char -> último índice
        left = 0
        best = 0
        for right, char in enumerate(s):
            if char in last and last[char] >= left:
                left = last[char] + 1                  # salto directo
            last[char] = right
            best = max(best, right - left + 1)
        return best
```

**Análisis:**
- **Tiempo: O(n)** — un solo recorrido sin while interno.
- **Espacio: O(min(n, alfabeto))**.
- **Veredicto:** [OK] ligeramente más eficiente (constantes mejores). Es la respuesta "óptima" en entrevista.

> **`last[char] >= left`**: la guarda evita saltos hacia atrás. Si `last[char] < left`, ese duplicado **ya no está en la ventana actual**, así que no hay conflicto.

**Trace con `s = "abba"`** (caso donde la guarda importa):

| right | char | last antes | left antes | last[char] >= left? | left después | last después | best |
|---|---|---|---|---|---|---|---|
| 0 | 'a' | {} | 0 | NO (no en last) | 0 | {a:0} | 1 |
| 1 | 'b' | {a:0} | 0 | NO (no en last) | 0 | {a:0, b:1} | 2 |
| 2 | 'b' | {a:0, b:1} | 0 | SÍ (1 ≥ 0) | 2 | {a:0, b:2} | 1 |
| 3 | 'a' | {a:0, b:2} | 2 | NO (0 < 2) | 2 | {a:3, b:2} | 2 |

Sin la guarda, en `right=3` left saltaría a `1`, lo cual sería incorrecto (rompería la ventana).

---

## El patrón general — "Sliding window de tamaño variable"

**Cuándo aplicar**:

> Cuando el problema pide el **subarray / substring óptimo** (más largo, más corto, con cierta propiedad), y **expand/shrink** mantiene una invariante que se puede chequear en O(1) o O(k) por movimiento.

**Plantilla mental** (la que más vas a usar):

```python
def sliding_window_variable(arr):
    state = estado_inicial                       # set, Counter, sum, etc.
    left = 0
    best = 0
    for right, x in enumerate(arr):
        # 1. expand: añadir x al estado
        actualizar_estado_para_anyadir(state, x)
        # 2. shrink: mientras se viole invariante, quitar arr[left] y avanzar
        while not invariante_valida(state):
            actualizar_estado_para_quitar(state, arr[left])
            left += 1
        # 3. actualizar mejor
        best = max(best, right - left + 1)
    return best
```

**Tres señales** del patrón:

1. Quieres el **subarray/substring** (contiguo) más largo o más corto que cumple algo.
2. La invariante es monotónica: **añadir** elementos puede romperla, **quitar** la restablece (o viceversa).
3. La fuerza bruta es O(n²) o más.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **159. Longest Substring with At Most 2 Distinct Characters** | Mismo pero permite hasta 2 caracteres únicos |
| **340. Longest Substring with At Most K Distinct Characters** | Generalización con K |
| **424. Longest Repeating Character Replacement** | Permite K reemplazos |
| **567. Permutation in String** | Sliding window de tamaño FIJO |
| **76. Minimum Window Substring** | Mínima en lugar de máxima |
| **438. Find All Anagrams in a String** | Todos los inicios donde cabe un anagrama |

> **Patrón maestro**: cuando dominas Sliding Window variable, los Hard del patrón se vuelven viables. Son todos variantes con distintas invariantes.

---

## Conceptos a interiorizar

### Análisis amortizado en sliding window

Aunque hay un `while` dentro del `for`, la complejidad es **O(n)** porque:
- `right` avanza n veces total.
- `left` avanza **a lo sumo n veces total** (no por iteración).

Cada elemento entra y sale de la ventana **a lo sumo una vez**. Total: 2n operaciones → O(n). **Mismo análisis amortizado que en [[125-valid-palindrome]] y [[128-longest-consecutive-sequence]]**.

### Sliding window con `set` vs con `dict`

- **`set`**: solo presencia. Útil cuando el shrink avanza char a char.
- **`dict` (índice)**: permite saltos directos al posicionar `left`. Más eficiente.
- **`Counter` (frecuencia)**: para problemas con tolerancia a duplicados (LC 424).

### Cuándo usar `last[char] >= left` (la guarda)

Un `char` puede estar en `last` pero **fuera de la ventana actual** (si ya lo "abandonamos" antes). Sin la guarda, harías saltar `left` hacia atrás, **rompiendo** el invariante de que la ventana solo crece monotónicamente.

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Fuerza bruta | O(n³) | O(n) | [NO] TLE |
| 2. **Sliding window con set** | **O(n)** amort. | O(k) | [OK] La canónica |
| 3. **Sliding window con dict** | **O(n)** | O(k) | [OK] La óptima |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** (con set) desde cero.
2. Justifica el O(n) amortizado: ¿cuántas veces avanza `left` total?
3. Implementa la **Solución 3** (con dict). Trace mental con `s = "abba"` para entender la guarda `last[char] >= left`.
4. Trace mental con `s = "pwwkew"`. Identifica los substrings de tamaño 3 sin duplicados.
5. **Bonus** — modifica la Solución 3 para devolver **el substring**, no solo su longitud.

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué O(n) si hay bucles anidados?"** → Análisis amortizado: `right` y `left` cada uno avanzan ≤ n veces.
- **"¿Y si el alfabeto fuera unicode?"** → No cambia. El set/dict crecen pero la complejidad sigue siendo O(n) tiempo (con constantes mayores).
- **"Diferencia entre las dos versiones (set vs dict)?"** → Set: avanza `left` paso a paso. Dict: salta `left` directamente al índice posterior al duplicado. Ambos O(n), dict mejor en práctica.
- **"¿Cómo lo extenderías a 'al menos K diferentes'?"** → Diferente patrón: necesitas tracker de cuántos caracteres únicos hay (LC 340).

---

## Conexiones

- [[121-best-time-to-buy-and-sell-stock]] — patrón anterior, ventana que solo crece.
- [[217-contains-duplicate]] — el set como memoria, primer encuentro.
- Próximo: [[424-longest-repeating-character-replacement]] — sliding window con tolerancia.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 (set) desde cero
- [ ] Implementada Solución 3 (dict) desde cero
- [ ] Justificado el O(n) amortizado
- [ ] Trace mental con `"abba"` (caso de la guarda)
- [ ] Resuelto en LeetCode con éxito
