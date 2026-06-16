---
title: "LeetCode 424 — Longest Repeating Character Replacement"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/sliding-window, patron/conteo-frecuencias]
type: nota
status: en-progreso
source: claude-code
aliases: [Longest Repeating Character Replacement, LC 424, characterReplacement, Caracteres con reemplazos]
problem_id: 424
difficulty: medium
patron: sliding-window
neetcode_order: 3
---

# LeetCode 424 — Longest Repeating Character Replacement

> 🎯 **Tercer problema del patrón Sliding Window**. Introduce el truco mental más bonito del patrón: la **frecuencia del carácter más común** dentro de la ventana, y usar el dato `len_ventana - max_freq` como "número de caracteres a reemplazar". Si entiendes este truco, entiendes 4-5 problemas más.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un string `s` y un entero `k`, puedes elegir como máximo `k` caracteres del string y cambiarlos por **cualquier otro carácter**.

Devuelve la **longitud del substring más largo con un único carácter repetido** después de los reemplazos.

**Ejemplo 1:**
```
Input:  s = "ABAB", k = 2
Output: 4
        Reemplaza las 2 'A's por 'B' (o las 2 'B's por 'A') → "BBBB" → longitud 4
```

**Ejemplo 2:**
```
Input:  s = "AABABBA", k = 1
Output: 4
        Reemplaza la 'B' del medio por 'A' → "AABAABA"... no, mejor:
        Sub-string "ABBA" → reemplaza 1 char → "AAAA" o "BBBB". Longitud 4.
```

**Restricciones:**
- `1 <= s.length <= 10^5`
- `s` consiste solo en **letras mayúsculas inglesas** (A-Z, 26 caracteres).
- `0 <= k <= s.length`.

**Plantilla:**
```python
class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` — longitud del substring óptimo |
| ¿Substring contiguo? | **Sí, contiguo** — no subsecuencia |
| ¿k puede ser 0? | Sí — entonces buscas el substring más largo de un único carácter sin reemplazos |
| ¿Sensible a mayúsculas? | Solo hay mayúsculas en este problema |
| ¿Cuántos caracteres distintos? | Hasta 26 (alfabeto inglés mayúsculas) |

> 💡 **Reformulación clave**: para una ventana cualquiera, el **carácter más frecuente** dentro de ella es el "objetivo" hacia el que reemplazar. Si la ventana mide `L` y el más frecuente aparece `max_freq` veces, necesitas reemplazar `L - max_freq` caracteres. Si `L - max_freq <= k`, **la ventana es válida**.

---

## La intuición antes del código — por qué la frecuencia es la pieza clave

Antes de mirar el algoritmo, la pregunta más importante es: **¿por qué importa la frecuencia del carácter más común?**

Imagina una ventana cualquiera, por ejemplo `"AABAB"` (5 caracteres). Cuenta cada letra:
- `A`: 3 veces
- `B`: 2 veces

**Estrategia obvia para uniformar la ventana con mínimos reemplazos**: conserva el carácter más frecuente (la `A`, 3 veces) y reemplaza el resto (las 2 `B`):

```
"AABAB"      ← ventana de 5 caracteres
  ↓
 conservar la A (3 veces)
 reemplazar las B (2 veces)
  ↓
"AAAAA"      ← todos iguales
```

**Número de reemplazos necesarios** = `len_ventana - max_freq` = `5 - 3 = 2`.

> 🎯 **Invariante mágica**: una ventana es **válida** si `len_ventana - max_freq <= k`.
>
> En palabras: "el número de caracteres que NO son el dominante es ≤ que mis comodines disponibles".

Esa es la pregunta que el algoritmo se hace en cada paso. **La frecuencia cambia las cosas porque define cuántos reemplazos necesitas**: cuanto más dominante sea el carácter más común, menos comodines te hacen falta para uniformar la ventana.

A partir de aquí, sliding window: extender la ventana por la derecha, encogerla por la izquierda cuando se vuelva inválida (necesite > k reemplazos), trackear la mejor longitud vista.

---

## Solución 1 — Sliding window con Counter (la canónica)

**La idea clave**: ventana variable. Expand `right` siempre. Cuando `len_ventana - max_freq > k` (necesitas más reemplazos de los disponibles), shrink `left`.

```python
from collections import Counter

class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        count = Counter()
        left = 0
        best = 0
        for right, char in enumerate(s):
            count[char] += 1
            # ventana actual = right - left + 1
            # reemplazos necesarios = len - max_freq
            while (right - left + 1) - max(count.values()) > k:
                count[s[left]] -= 1
                left += 1
            best = max(best, right - left + 1)
        return best
```

**Trace mental con `s = "AABABBA", k = 1`**:

| right | char | count (después) | max_freq | len | len-max_freq | k | shrink? | left | best |
|---|---|---|---|---|---|---|---|---|---|
| 0 | A | {A:1} | 1 | 1 | 0 | 1 | NO | 0 | 1 |
| 1 | A | {A:2} | 2 | 2 | 0 | 1 | NO | 0 | 2 |
| 2 | B | {A:2, B:1} | 2 | 3 | 1 | 1 | NO | 0 | 3 |
| 3 | A | {A:3, B:1} | 3 | 4 | 1 | 1 | NO | 0 | **4** |
| 4 | B | {A:3, B:2} | 3 | 5 | 2 | 1 | **SÍ** → quitar A, left=1 | 1 | 4 |
| | | {A:2, B:2} | 2 | 4 | 2 | 1 | **SÍ** → quitar A, left=2 | 2 | 4 |
| | | {A:1, B:2} | 2 | 3 | 1 | 1 | NO | 2 | 4 |
| 5 | B | {A:1, B:3} | 3 | 4 | 1 | 1 | NO | 2 | 4 |
| 6 | A | {A:2, B:3} | 3 | 5 | 2 | 1 | **SÍ** → quitar B, left=3 | 3 | 4 |
| | | {A:2, B:2} | 2 | 4 | 2 | 1 | **SÍ** → quitar A, left=4 | 4 | 4 |
| | | {A:1, B:2} | 2 | 3 | 1 | 1 | NO | 4 | 4 |

Resultado: `4` ✅.

**Análisis:**
- **Tiempo: O(n · 26)** = O(n) — el `max(count.values())` es O(26) constante porque el alfabeto es fijo.
- **Espacio: O(26)** = O(1) — Counter de 26 letras.
- **Veredicto:** ✅ correcta. Pero hay una optimización sutil:

### Trace completo de la Solución 1 con `s = "AABABBA", k = 1`

```
Índice:  0  1  2  3  4  5  6
Char:    A  A  B  A  B  B  A
```

Estado inicial: `count = {}`, `left = 0`, `best = 0`.

**right=0, char='A'**:
- count = {A:1}, len=1, max_freq=1
- `1 - 1 = 0 ≤ 1` ✓ válida (0 reemplazos necesarios)
- best = 1

```
[A]
```

**right=1, char='A'**:
- count = {A:2}, len=2, max_freq=2
- `0 ≤ 1` ✓
- best = 2

```
[AA]
```

**right=2, char='B'**:
- count = {A:2, B:1}, len=3, max_freq=2
- `3 - 2 = 1 ≤ 1` ✓ (1 reemplazo: la B)
- best = 3

```
[AAB]            ← reemplazaríamos la B
```

**right=3, char='A'**:
- count = {A:3, B:1}, len=4, max_freq=3
- `4 - 3 = 1 ≤ 1` ✓
- best = 4 ⭐

```
[AABA]           ← 1 reemplazo (la B), válida
```

**right=4, char='B'**:
- count = {A:3, B:2}, len=5, max_freq=3
- `5 - 3 = 2 > 1` ✗ **inválida** (necesitas 2 reemplazos, solo tienes 1)
- **SHRINK con while**:
  - Quitar s[0]='A': count = {A:2, B:2}, left=1, len=4, max_freq=2
  - `4 - 2 = 2 > 1` ✗ aún inválida
  - Quitar s[1]='A': count = {A:1, B:2}, left=2, len=3, max_freq=2
  - `3 - 2 = 1 ≤ 1` ✓ → salir del while
- best = max(4, 3) = 4

```
   [BAB]         ← shrink hasta volver a válida
```

**right=5, char='B'**:
- count = {A:1, B:3}, len=4, max_freq=3
- `4 - 3 = 1 ≤ 1` ✓
- best = max(4, 4) = 4

```
   [BABB]
```

**right=6, char='A'**:
- count = {A:2, B:3}, len=5, max_freq=3
- `5 - 3 = 2 > 1` ✗
- **SHRINK**: quitar s[2]='B' (left=3), quitar s[3]='A' (left=4) → válida con len=3
- best = 4

**Resultado: 4** ✅. El óptimo es `"AABA"` (reemplazar B por A) o `"BABB"` (reemplazar A por B).

---

## Solución 2 — Optimización: max_freq que solo crece (la "trampa" elegante)

**La observación**: una vez que tenemos una ventana de tamaño `L` con `max_freq = m`, encontrar una ventana de tamaño `L+1` con menor `max_freq` **no nos da una mejor solución** (porque `L+1 - menor_freq > L - m` puede pasar pero la mejor sigue siendo `L`).

Conclusión: **`max_freq` solo necesita actualizarse al crecer**. Nunca al shrink.

```python
from collections import Counter

class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        count = Counter()
        left = 0
        max_freq = 0
        best = 0
        for right, char in enumerate(s):
            count[char] += 1
            max_freq = max(max_freq, count[char])         # solo crece
            if (right - left + 1) - max_freq > k:
                count[s[left]] -= 1
                left += 1                                   # avanza 1 cuando no es válido
            best = max(best, right - left + 1)
        return best
```

> 🎯 **Detalle muy importante**: aquí `if`, no `while`. Cuando `len - max_freq > k`, avanzamos `left` UNA vez. La ventana **mantiene su tamaño** (right también acaba de avanzar). Solo crece cuando encuentra una buena combinación.

**Análisis:**
- **Tiempo: O(n)** — una pasada lineal.
- **Espacio: O(26)** = O(1).
- **Veredicto:** ✅ **la óptima**. El truco "max_freq solo crece" es **señal de seniority** en entrevista.

### Por qué la Solución 2 funciona aunque `max_freq` esté "desactualizado"

Esto es lo más sutil del problema. Después de un shrink, `max_freq` **podría** ser mayor que el verdadero máximo de la ventana actual. **No importa**:

- Si `max_freq` está desactualizado (sobreestimado) → `len - max_freq_estimado` es **menor** que `len - max_freq_real` → el check estimado es **más permisivo**. Pero como `max_freq_estimado ≥ max_freq_real`, si el check estimado dice "≤ k", el real **también** lo dice → la ventana es realmente válida.
- La ventana **nunca se hace más pequeña** porque el `if` hace solo 1 shrink, y simultáneamente `right` ha avanzado 1 → la ventana mantiene su tamaño.
- **Solo crece cuando un nuevo char hace `max_freq` crecer realmente** — en ese momento el estimado y el real coinciden.

El resultado: `best` solo se actualiza con ventanas legítimamente válidas, y solo crece cuando aparece un máximo nuevo (que actualiza ambos estimado y real).

### Trace de la Solución 2 con el mismo input

`s = "AABABBA", k = 1`. Las primeras 4 iteraciones son idénticas a la Solución 1 (no hay shrinks aún). Voy directo a las que cambian:

**right=4, char='B'** (la primera vez que se necesita shrink):
- count = {A:3, B:2}, max_freq = max(3, 2) = **3**
- len = 5 (right=4, left=0): `5 - 3 = 2 > 1` ✗ → SHRINK **un solo paso** con `if`:
  - Quitar s[0]='A' → count = {A:2, B:2}, left=1
- Ahora la ventana es `s[1..4] = "ABAB"`, len = 4
- ⚠️ `max_freq` sigue siendo **3** aunque el real ahora es 2 (las dos A's y dos B's empatan)
- best = max(4, 4) = 4

```
Estado tras iter 4:
   [ABAB]        ← max_freq estimado = 3 (desactualizado), real = 2
```

**right=5, char='B'**:
- count = {A:2, B:3}, max_freq = max(3, 3) = 3 (esta vez el real coincide con el estimado)
- len = 5: `5 - 3 = 2 > 1` ✗ → SHRINK 1 paso:
  - Quitar s[1]='A' → count = {A:1, B:3}, left=2
- best = max(4, 4) = 4

```
   [BABB]
```

**right=6, char='A'**:
- count = {A:2, B:3}, max_freq = max(3, 2) = **3** (B sigue siendo el máximo real)
- len = 5: `5 - 3 = 2 > 1` ✗ → SHRINK:
  - Quitar s[2]='B' → count = {A:2, B:2}, left=3
- ⚠️ `max_freq` sigue siendo 3 aunque ahora el real es 2 (empate A=B=2) ← **desactualizado**
- best = max(4, 4) = 4

```
   [BBA]         ← max_freq estimado = 3, real = 2
```

**Resultado: 4** ✅. **Mismo resultado que Solución 1**, con un `max_freq` "mintiendo" en algunas iteraciones — pero sin afectar al `best`.

### Visualización del invariante en Solución 2

```
                         max_freq_estimado    max_freq_real    válida?
                         (lo que el algo ve)   (lo verdadero)
Iter 4 (tras shrink):           3                    2          (estimado dice no, real dice sí)
                                                                pero NO importa: el if no expande
                                                                la ventana — solo la "desplazó"
Iter 6 (tras shrink):           3                    2          mismo escenario
```

La ventana **nunca decrece**. En el peor caso "se desplaza" sin crecer. Y solo crece cuando aparece un carácter que aumenta `max_freq` legítimamente (estimado y real coinciden en ese momento). Por eso `best` siempre captura ventanas válidas.

---

## El patrón general — "Sliding window con frecuencia + tolerancia"

**Cuándo aplicar**:

> Cuando el problema permite **K excepciones / reemplazos / tolerancia** dentro de una ventana, y la "calidad" de la ventana se mide por la frecuencia del elemento más común.

**Plantilla mental**:

```python
def sliding_window_tolerance(arr, k):
    count = Counter()
    left = 0
    max_freq = 0
    best = 0
    for right, x in enumerate(arr):
        count[x] += 1
        max_freq = max(max_freq, count[x])
        if (right - left + 1) - max_freq > k:
            count[arr[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
```

**Tres señales** del patrón:

1. Hay un parámetro `k` que representa "cuántas excepciones permitidas".
2. La invariante involucra el conteo del elemento dominante en la ventana.
3. Buscas el subarray/substring más largo que cumple la condición.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **3. Longest Substring Without Repeating Characters** | k = 0 reemplazos; busca sin duplicados |
| **567. Permutation in String** | Ventana de tamaño FIJO con matching de frecuencias |
| **159. Longest Substring with At Most 2 Distinct Characters** | Tolerancia en "número de caracteres únicos" |
| **1004. Max Consecutive Ones III** | Sliding window con K ceros permitidos |
| **904. Fruit Into Baskets** | Substring con ≤ 2 tipos de "frutas" |

---

## Conceptos a interiorizar

### `max(count.values())` es O(26) constante

Cuando el alfabeto es fijo y pequeño (ASCII, 26 letras), iterar sobre todos los valores del Counter es O(constante) en términos de complejidad asintótica. Pero **es lento en práctica**, por eso la Solución 2 mantiene `max_freq` actualizado externamente.

### `if` vs `while` en sliding window

- **`while`** (Solución 1): el shrink continúa hasta restablecer la invariante. La ventana puede colapsar.
- **`if`** (Solución 2): un solo paso de shrink. La ventana **nunca decrece** — solo "se desplaza" cuando no puede crecer.

Cuándo cada uno: depende del problema. Para "el más largo", `if` suele bastar (no necesitas reducir si ya tienes el best). Para "el más corto", típicamente `while`.

### El truco de "max_freq solo crece"

Es contraintuitivo pero correcto. Sirve como **invariante débil** que basta para el problema: garantiza que solo expandimos la ventana cuando es válida con un `max_freq` real (no estimado).

---

## Comparación final de las 2 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Sliding window con `max(count.values())` | O(n · 26) | O(26) | Funciona, costantes peores |
| 2. **Sliding window con `max_freq` mantenido** | **O(n)** | O(26) | ✅ La óptima |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** desde cero.
2. Justifica:
   - Por qué `if` y no `while`.
   - Por qué `max_freq` puede estar "desactualizado" sin afectar el resultado.
   - Por qué `max_freq = max(max_freq, count[char])` solo se actualiza al expandir.
3. Trace mental con `s = "ABAB", k = 2`. ¿Cuándo se actualiza `max_freq`?
4. Trace mental con `s = "AAAA", k = 0`. ¿Resultado y por qué?
5. **Bonus** — ¿qué pasa si `k = 0`? ¿Cómo se reduce el problema?

---

## Cosas que te pueden preguntar en entrevista

- **"Demuestra por qué tu Solución 2 es correcta aunque `max_freq` no se actualice al shrink."** → Argumento: la ventana solo crece, y solo la consideramos válida cuando `len - max_freq <= k`. Si `max_freq` está desactualizado (menor que el real), `len - max_freq` es **mayor**, así que **no expandimos** una ventana que sí podría ser válida — pero ese best ya lo tendríamos de antes con la misma o mayor longitud.
- **"¿Y si k pudiera ser negativo?"** → No tendría sentido (no permitiría ningún reemplazo). El enunciado garantiza k ≥ 0.
- **"¿Cómo lo extenderías a alfabeto Unicode?"** → Counter sigue funcionando. La constante "26" se vuelve "número de caracteres únicos posibles", pero la complejidad sigue siendo O(n) si mantienes max_freq externamente.

---

## Conexiones

- [[3-longest-substring-without-repeating-characters]] — caso k=0 (sin tolerancia).
- [[242-valid-anagram]] — primer encuentro con `Counter`.
- Próximo: [[567-permutation-in-string]] — sliding window de tamaño FIJO.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Justificado por qué `max_freq` desactualizado no rompe el algoritmo
- [ ] Trace mental hecho
- [ ] Resuelto en LeetCode con éxito
