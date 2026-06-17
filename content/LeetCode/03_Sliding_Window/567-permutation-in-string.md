---
title: "LeetCode 567 — Permutation in String"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/sliding-window, patron/conteo-frecuencias, patron/ventana-fija]
type: nota
status: en-progreso
source: claude-code
aliases: [Permutation in String, LC 567, checkInclusion, Permutación en string]
problem_id: 567
difficulty: medium
patron: sliding-window
neetcode_order: 4
---

# LeetCode 567 — Permutation in String

> **Cuarto problema del patrón Sliding Window** — y el primer ejemplo de **ventana de tamaño FIJO**, distinto de los anteriores que eran variables. Aprenderlo bien te abre la subfamilia de problemas "sliding window de tamaño k".
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dadas dos strings `s1` y `s2`, devuelve `True` si `s2` **contiene una permutación de `s1`** (es decir, alguno de los anagramas de `s1` aparece como substring de `s2`).

**Ejemplo 1:**
```
Input:  s1 = "ab", s2 = "eidbaooo"
Output: true
        s2 contiene "ba" (permutación de "ab") como substring.
```

**Ejemplo 2:**
```
Input:  s1 = "ab", s2 = "eidboaoo"
Output: false
        Ninguna permutación de "ab" aparece en s2.
```

**Restricciones:**
- `1 <= s1.length, s2.length <= 10^4`
- `s1` y `s2` consisten en **letras minúsculas inglesas**.

**Plantilla:**
```python
class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `bool` |
| ¿Permutación significa? | Misma multiset de caracteres, distinto orden (anagrama) |
| ¿La permutación tiene que aparecer contiguamente en s2? | **Sí, contigua** |
| ¿Si s1 es más larga que s2? | Imposible que quepa → `False` directo |
| ¿Sensible a mayúsculas? | Solo minúsculas según restricciones |
| Edge case 1 | `s1 = "a", s2 = "a"` → `True` |
| Edge case 2 | s1 con duplicados (`"aa"`): solo cuenta como anagrama "aa" |

> **Reformulación**: ¿existe una ventana de tamaño `len(s1)` en `s2` tal que sus frecuencias de caracteres coinciden con las de `s1`?

---

## Solución 1 — Generar todas las permutaciones de s1 (NO óptima)

```python
from itertools import permutations

class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        for p in permutations(s1):
            if ''.join(p) in s2:
                return True
        return False
```

**Análisis:**
- **Tiempo: O(n! · m)** — n! permutaciones × O(m) por búsqueda. Catastrófico con `n = 10^4`.
- **Espacio: O(n!)**.
- **Veredicto:** [NO] TLE absoluta. Solo educativa.

---

## Solución 2 — Sliding window de tamaño fijo + Counter (la canónica)

**La idea clave**: una ventana de tamaño `len(s1)` que se desliza por `s2`. En cada posición, comparar `Counter(ventana)` con `Counter(s1)`. Si coinciden → permutación encontrada.

```python
from collections import Counter

class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        n, m = len(s1), len(s2)
        if n > m:
            return False

        target = Counter(s1)
        window = Counter(s2[:n])                # primera ventana

        if window == target:
            return True

        for right in range(n, m):
            window[s2[right]] += 1              # añadir nuevo
            window[s2[right - n]] -= 1          # quitar el que sale
            if window[s2[right - n]] == 0:      # limpiar 0s para que `==` funcione
                del window[s2[right - n]]
            if window == target:
                return True
        return False
```

**Trace mental con `s1 = "ab", s2 = "eidbaooo"`** (n=2):

| Paso | right | window (después) | target | ¿==? |
|---|---|---|---|---|
| init | — | Counter("ei") = {e:1, i:1} | {a:1, b:1} | NO |
| 1 | 2 | quitar 'e', añadir 'd' → {i:1, d:1} | | NO |
| 2 | 3 | quitar 'i', añadir 'b' → {d:1, b:1} | | NO |
| 3 | 4 | quitar 'd', añadir 'a' → {b:1, a:1} | | **SÍ** → return True |

Resultado: `True` [OK].

**Análisis:**
- **Tiempo: O(m + (m-n)·26)** = O(m) — cada comparación `==` entre Counters de tamaño máximo 26 es O(26).
- **Espacio: O(26)** = O(1).
- **Veredicto:** [OK] correcta. La sutileza del `del window[char]` cuando llega a 0 es **necesaria** para que `==` no falle por claves residuales con valor 0.

---

## Solución 3 — Sliding window con array de 26 (la óptima)

Misma idea pero con array fijo de 26 enteros (más rápido en práctica, sin necesidad de `del`).

```python
class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        n, m = len(s1), len(s2)
        if n > m:
            return False

        target = [0] * 26
        window = [0] * 26
        for c in s1:
            target[ord(c) - ord('a')] += 1
        for c in s2[:n]:
            window[ord(c) - ord('a')] += 1

        if window == target:
            return True

        for right in range(n, m):
            window[ord(s2[right]) - ord('a')] += 1
            window[ord(s2[right - n]) - ord('a')] -= 1
            if window == target:
                return True
        return False
```

**Análisis:** mismo O(m) tiempo, O(1) espacio. **La diferencia clave**: `window == target` entre listas de tamaño fijo 26 es O(26), sin tener que limpiar 0s (porque las listas siempre tienen 26 entradas).

**Veredicto:** [OK] **la idiomática para alfabeto pequeño**. Es la respuesta esperada.

---

## Solución 4 — Optimización con "matches counter" (la fineza)

En lugar de comparar las dos listas enteras (26 ops) en cada paso, mantén un **contador de cuántas posiciones del array están "ok"**. Cuando llega a 26, hay match.

```python
class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        n, m = len(s1), len(s2)
        if n > m:
            return False

        target = [0] * 26
        window = [0] * 26
        for c in s1:
            target[ord(c) - ord('a')] += 1
        for c in s2[:n]:
            window[ord(c) - ord('a')] += 1

        matches = sum(1 for i in range(26) if window[i] == target[i])
        if matches == 26:
            return True

        for right in range(n, m):
            i_in = ord(s2[right]) - ord('a')
            i_out = ord(s2[right - n]) - ord('a')

            # añadir char nuevo
            if window[i_in] == target[i_in]:
                matches -= 1
            window[i_in] += 1
            if window[i_in] == target[i_in]:
                matches += 1

            # quitar char saliente
            if window[i_out] == target[i_out]:
                matches -= 1
            window[i_out] -= 1
            if window[i_out] == target[i_out]:
                matches += 1

            if matches == 26:
                return True
        return False
```

**Análisis:**
- **Tiempo: O(m)** — cada paso hace solo O(1) de trabajo (no compara 26 entradas).
- **Espacio: O(1)**.
- **Veredicto:** [OK] **la óptima absoluta**. No hace falta en LeetCode (la 3 ya pasa) pero es el patrón "matches counter" que vale la pena conocer porque aparece en LC 76 y similares.

---

## El patrón general — "Sliding window de tamaño FIJO"

**Cuándo aplicar**:

> Cuando el problema fija la ventana en un tamaño concreto `k` (o lo deriva del input) y pide algo (existe / cuántos / cuál) sobre todas las ventanas de ese tamaño.

**Plantilla mental**:

```python
def sliding_window_fijo(arr, k):
    state = inicializar_state(arr[:k])           # primera ventana
    if condicion(state):
        return early_match
    for right in range(k, len(arr)):
        # añadir el nuevo
        actualizar_state_anyadir(state, arr[right])
        # quitar el que sale
        actualizar_state_quitar(state, arr[right - k])
        if condicion(state):
            return early_match
    return default
```

**Tres señales** del patrón:

1. La ventana tiene **tamaño fijo** (dado o derivado del input).
2. El estado de la ventana es agregable y se puede mantener incrementalmente.
3. Hay que evaluar todas las ventanas de ese tamaño.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **438. Find All Anagrams in a String** | Devolver **todos los inicios** donde aparece un anagrama (no solo bool) |
| **30. Substring with Concatenation of All Words** | Generalización con palabras en vez de chars |
| **76. Minimum Window Substring** | Ventana variable con cobertura completa |
| **187. Repeated DNA Sequences** | Ventana fija de 10 caracteres + hash set |

---

## Conceptos a interiorizar

### Sliding window FIJO vs VARIABLE

| Variable (LC 3, 424, 76) | Fijo (LC 567, 438) |
|---|---|
| Loop con `while` para shrink | Cada paso: 1 add + 1 remove |
| Tamaño cambia dinámicamente | Tamaño constante |
| Suele buscar "el más largo" o "el más corto" | Suele buscar "existe" o "todos los" |

Saber distinguir entre los dos te ahorra tiempo en entrevista: la plantilla cambia.

### `del d[k]` para limpiar Counter

Si comparas dos `Counter` con `==`, las claves residuales con valor 0 hacen que **no sean iguales**. Tienes que borrarlas. Por eso la Solución 2 hace `del window[char]` cuando llega a 0.

Con array fijo de 26 (Solución 3) no tienes este problema.

### `matches counter` (Solución 4)

Cuando el costo de comparar dos estados es alto (e.g. dos arrays de N entradas), mantener un contador externo "cuántas entradas coinciden" reduce cada paso de O(N) a O(1). Esto es el truco de **"have/need"** del LC 76, generalizado.

---

## Comparación final de las 4 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Generar permutaciones | O(n! · m) | O(n!) | [NO] TLE |
| 2. Sliding window con `Counter` + `del` | O(m) | O(26) | [OK] Funciona |
| 3. **Sliding window con array de 26** | **O(m)** | O(1) | [OK] La idiomática |
| 4. **Sliding window con matches counter** | **O(m)** | O(1) | [OK] La óptima absoluta |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 3** (array de 26) desde cero.
2. Justifica:
   - Por qué `if n > m: return False` al inicio.
   - Por qué se compara la primera ventana ANTES del loop principal.
   - Cuál es la complejidad temporal y espacial.
3. Trace mental con `s1 = "abc", s2 = "bbbcabba"`. ¿En qué iteración `window == target`?
4. Implementa la **Solución 4** (matches counter). Es más laboriosa pero entender los 4 if-cases es valioso.
5. **Bonus** — modifica para devolver el **índice** del primer match (en vez de bool).

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué tu sliding window es O(m) y no O(m·n)?"** → Cada paso del sliding hace 2 actualizaciones de array (O(1)) + comparación O(26). Total O(m·26) = O(m).
- **"Diferencia entre ventana fija y variable?"** → Fija: cada paso es 1 add + 1 remove. Variable: while loop para shrink hasta restablecer invariante.
- **"¿Y si el alfabeto fuera Unicode?"** → Las soluciones con array de 26 fallan; volver a Counter (Solución 2) que es O(m·k) donde k = caracteres únicos.
- **"¿Cómo lo extenderías a 'todos los inicios donde hay anagrama' (LC 438)?"** → Mismo algoritmo, pero en lugar de `return True` añades el índice a un array de resultados y sigues.

---

## Conexiones

- [[242-valid-anagram]] — comparar frecuencias entre dos strings.
- [[424-longest-repeating-character-replacement]] — sliding window con tolerancia.
- [[3-longest-substring-without-repeating-characters]] — sliding window variable.
- Próximo: [[76-minimum-window-substring]] — sliding window variable con cobertura.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 3 (array 26) desde cero
- [ ] Implementada Solución 4 (matches counter)
- [ ] Justificada la diferencia ventana fija vs variable
- [ ] Resuelto en LeetCode con éxito
