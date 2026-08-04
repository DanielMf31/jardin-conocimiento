---
title: "LeetCode 76 — Minimum Window Substring"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/sliding-window, patron/conteo-frecuencias, patron/have-need]
type: nota
status: en-progreso
source: claude-code
aliases: [Minimum Window Substring, LC 76, minWindow, Ventana mínima cubre todos]
problem_id: 76
difficulty: hard
patron: sliding-window
neetcode_order: 5
---

# LeetCode 76 — Minimum Window Substring

> **Quinto problema del patrón Sliding Window — primer Hard**. Es **el problema más difícil** de la categoría y **el más útil para entrevistas tecnicas** (lo preguntan muy frecuentemente). Introduce el patrón **`have / need`** (matches counter) que es la generalización de todo lo anterior.
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dadas dos strings `s` y `t`, devuelve la **ventana mínima en `s`** que contiene **todos los caracteres de `t`** (incluyendo duplicados).

Si no existe tal ventana, devuelve `""` (string vacío).

> Importante: la ventana puede contener caracteres extra; lo que importa es que **cubra** los de `t` (con sus frecuencias).

**Ejemplo 1:**
```
Input:  s = "ADOBECODEBANC", t = "ABC"
Output: "BANC"
        Explicación: la ventana mínima que contiene 'A', 'B', 'C' (cada uno una vez) es "BANC".
```

**Ejemplo 2:**
```
Input:  s = "a", t = "a"
Output: "a"
```

**Ejemplo 3:**
```
Input:  s = "a", t = "aa"
Output: ""
        s solo tiene una 'a', t necesita dos.
```

**Restricciones:**
- `m == s.length`, `n == t.length`.
- `1 <= m, n <= 10^5`.
- `s` y `t` son ASCII imprimibles.

> **Follow-up del enunciado**: ¿puedes hacerlo en O(m + n)?

**Plantilla:**
```python
class Solution:
    def minWindow(self, s: str, t: str) -> str:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `str` — la ventana en sí (no su longitud) |
| ¿Substring contiguo? | **Sí, contiguo** |
| ¿Cubrir todos los caracteres de `t` con frecuencias? | **Sí** — si t = "aa", necesitas 2 'a's |
| ¿Qué devuelve si no hay match? | `""` |
| ¿Múltiples ventanas mínimas? | El enunciado dice "la única" garantizada (en práctica, devuelve la primera) |
| ¿Mayúsculas y minúsculas? | **Sí, sensible** |
| Edge case 1 | `t` más larga que `s` → no puede cubrir → `""` |
| Edge case 2 | `s` y `t` iguales → la ventana es `s` entera |

> **El reto**: tienes que mantener una ventana que **siempre cubra** los caracteres de `t`, expandirla cuando no cubre, contraerla cuando sí, y trackear la mejor (más corta).

---

## Solución 1 — Fuerza bruta (NO viable)

Probar todos los substrings, comprobar si cubre `t`.

```python
class Solution:
    def minWindow(self, s: str, t: str) -> str:
        from collections import Counter
        target = Counter(t)
        m = len(s)
        best = ""
        for i in range(m):
            for j in range(i, m):
                if Counter(s[i:j+1]) >= target:    # cubre todos
                    if best == "" or j - i + 1 < len(best):
                        best = s[i:j+1]
        return best
```

**Análisis:**
- **Tiempo: O(m³)** — m² substrings × O(m) construir Counter.
- **Espacio: O(m)**.
- **Veredicto:** [NO] TLE.

---

## Solución 2 — Sliding window con `have / need` (la canónica)

**La idea clave**: dos números mágicos que reemplazan la comparación de Counters:

- **`need`** = número de **caracteres únicos** en `t` que la ventana debe satisfacer.
- **`have`** = cuántos de esos caracteres únicos están actualmente **completos** (con la frecuencia exacta o más) en la ventana.

**Cuando `have == need`**, la ventana cubre `t`. Mientras eso sea cierto, contraer left para minimizar.

```python
from collections import Counter, defaultdict

class Solution:
    def minWindow(self, s: str, t: str) -> str:
        if len(t) > len(s):
            return ""

        target = Counter(t)
        need = len(target)                          # nº de chars únicos en t
        have = 0                                    # cuántos están completos

        window = defaultdict(int)
        left = 0
        best = (-1, 0, 0)                           # (longitud, l, r); -1 = sin solución todavía

        for right, char in enumerate(s):
            window[char] += 1
            if char in target and window[char] == target[char]:
                have += 1

            # contraer mientras siga válida
            while have == need:
                # actualizar mejor
                if best[0] == -1 or (right - left + 1) < best[0]:
                    best = (right - left + 1, left, right)

                # eliminar s[left] de la ventana
                window[s[left]] -= 1
                if s[left] in target and window[s[left]] < target[s[left]]:
                    have -= 1
                left += 1

        if best[0] == -1:
            return ""
        l, r = best[1], best[2]
        return s[l:r+1]
```

**Trace mental con `s = "ADOBECODEBANC", t = "ABC"`**:

`target = {A:1, B:1, C:1}`, `need = 3`.

| right | char | window añade | have (después) | == need? | shrink | best |
|---|---|---|---|---|---|---|
| 0 | A | A:1 | 1 | NO | — | — |
| 1 | D | D:1 | 1 | NO | — | — |
| 2 | O | O:1 | 1 | NO | — | — |
| 3 | B | B:1 | 2 | NO | — | — |
| 4 | E | E:1 | 2 | NO | — | — |
| 5 | C | C:1 | **3** | **SÍ** | shrink: ventana "ADOBEC" (len 6), best=(6,0,5). Quitar A → have=2 | (6,0,5) |
| 6 | O | O:2 | 2 | NO | — | (6,0,5) |
| 7 | D | D:2 | 2 | NO | — | (6,0,5) |
| 8 | E | E:2 | 2 | NO | — | (6,0,5) |
| 9 | B | B:2 | 2 | NO | — | (6,0,5) |
| 10 | A | A:1 | **3** | **SÍ** | shrink: "DOBECODEBA" (len 10), peor; quitar D → have=3; quitar O,B (have=2 al quitar B) → ... | va contrayendo |
| ... | | | | | termina con best=(4,9,12) | (4,9,12) |
| 11 | N | N:1 | 2 | NO | — | (4,9,12) |
| 12 | C | C:2 | 3 | SÍ | shrink: "BANC" (len 4) — best ya es 4 → empate, no actualiza | (4,9,12) |

Resultado: `s[9:13]` = `"BANC"` [OK].

**Análisis:**
- **Tiempo: O(m + n)** — O(n) para construir target, O(m) amortizado para el sliding window.
- **Espacio: O(n + alfabeto)**.
- **Veredicto:** [OK] **la canónica de entrevista**.

### Por qué `have / need` y no comparar Counters

Comparar dos Counter es O(k) donde k = chars únicos. Hacerlo en cada iteración del while sería O(m·k) total. Con `have/need`, cada actualización es **O(1)** y solo cambia cuando un carácter "completa" o "rompe" su requisito. Total: O(m) amortizado.

**Las dos condiciones críticas**:
- `if char in target and window[char] == target[char]: have += 1` — solo cuando **alcanza exactamente** el requisito, no cuando lo excede.
- `if s[left] in target and window[s[left]] < target[s[left]]: have -= 1` — solo cuando **baja por debajo** del requisito.

---

## El patrón general — "Sliding window con cobertura (have / need)"

**Cuándo aplicar**:

> Cuando el problema pide la **ventana mínima que cumple una condición de cobertura** (tener N elementos con ciertas restricciones, contener todos los caracteres de otra string, etc.).

**Plantilla mental**:

```python
def sliding_window_have_need(s, requisitos):
    need = len(requisitos)                       # cuántos requisitos distintos
    have = 0
    state = inicializar()
    left = 0
    best = inicial
    for right, x in enumerate(s):
        # expand
        actualizar_state_anyadir(state, x)
        if x es-requisito and state-completa-x:
            have += 1
        # contraer mientras válido
        while have == need:
            best = mejor(best, ventana_actual)
            actualizar_state_quitar(state, s[left])
            if s[left] es-requisito and state-rompe-x:
                have -= 1
            left += 1
    return best
```

**Tres señales** del patrón:

1. Buscas la **ventana más corta** (no la más larga, esa es otra variante).
2. La condición es **cobertura** de un conjunto fijo de requisitos.
3. La fuerza bruta es O(m²·n) y necesitas O(m+n).

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **567. Permutation in String** | Ventana FIJA con matching exacto |
| **438. Find All Anagrams in a String** | Todos los matches, ventana fija |
| **209. Minimum Size Subarray Sum** | Ventana mínima con suma ≥ target (numérico) |
| **727. Minimum Window Subsequence** | Subsecuencia, no substring contiguo (DP, distinto patrón) |
| **632. Smallest Range Covering Elements from K Lists** | Generalización a múltiples listas |

---

## Conceptos a interiorizar

### `have / need` como invariante

Es **el truco más importante** de sliding window con cobertura. Reduce comparaciones O(k) a O(1) por iteración.

**Plantilla**:
- `need` = total de requisitos distintos.
- `have` = cuántos están "satisfechos" actualmente.
- Solo incrementas `have` cuando un requisito **se completa exactamente**.
- Solo decrementas `have` cuando un requisito **se rompe** (baja debajo del threshold).

### `defaultdict(int)` vs `Counter()`

Aquí usamos `defaultdict(int)` para `window` y `Counter()` para `target` porque:
- `target` se construye una vez de un iterable → `Counter(t)` es directo.
- `window` se modifica continuamente → `defaultdict(int)` evita `KeyError` al hacer `window[char] += 1`.

Funcionalmente equivalentes, idiomáticamente distintos.

### Tracking del best por tupla

```python
best = (-1, 0, 0)            # (longitud, l, r)
if best[0] == -1 or new_len < best[0]:
    best = (new_len, l, r)
```

Patrón típico para no construir el substring antes de tiempo. Solo al final hace el slice. Ahorra memoria y tiempo si hay muchas actualizaciones.

---

## Comparación final de las 2 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Fuerza bruta | O(m³) | O(m) | [NO] TLE |
| 2. **Sliding window con `have / need`** | **O(m + n)** | O(n) | [OK] La canónica |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** desde cero. Es laboriosa, no te frustres si tarda 30+ minutos la primera vez.
2. Justifica:
   - Por qué `have += 1` solo cuando `window[char] == target[char]` (exactamente, no ≥).
   - Por qué `have -= 1` solo cuando `window[char] < target[char]` después de decrementar.
   - Por qué se contrae mientras `have == need` y no solo una vez.
3. Trace mental con `s = "AAAABBBC", t = "ABC"`. ¿Cuál es la ventana mínima?
4. Trace mental con `s = "a", t = "aa"`. ¿Por qué devuelve `""`?
5. **Bonus** — modifica para devolver la longitud (no el substring). ¿Cuánto cambia?

---

## Cosas que te pueden preguntar en entrevista

- **"Demuestra el O(m+n) de tu solución."** → `right` avanza m veces, `left` avanza ≤ m veces. Cada paso es O(1) gracias a `have/need`. Total O(m). Construcción de `target` es O(n). Total O(m+n).
- **"¿Por qué `have == need` y no `have >= need`?"** → `have` cuenta requisitos satisfechos exactamente. No puede exceder `need` (es un contador acotado). `==` es lo correcto.
- **"¿Cuál es el peor caso espacial?"** → O(n + alfabeto), donde alfabeto es el número de caracteres únicos en s.
- **"¿Cómo lo extenderías a 'todas las ventanas mínimas (no solo una)'?"** → Trackear lista en lugar de single best.
- **"¿Y si t pudiera ser muy larga (mayor que s)?"** → El check inicial `if len(t) > len(s): return ""` lo cubre.

---

## Conexiones

- [[567-permutation-in-string]] — versión con ventana fija.
- [[424-longest-repeating-character-replacement]] — sliding window con tolerancia (relacionado pero distinto).
- [[242-valid-anagram]] — comparar frecuencias entre dos strings.
- Próximo: [[239-sliding-window-maximum]] — el otro Hard del patrón, con deque monotónica.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero (date 30+ min, es Hard)
- [ ] Justificadas las dos condiciones de `have += 1` y `have -= 1`
- [ ] Trace mental hecho con el ejemplo principal
- [ ] Resuelto en LeetCode con éxito
- [ ] Hecho 1 vez más a la semana siguiente
