---
title: "LeetCode 125 — Valid Palindrome"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/two-pointers, patron/strings]
type: nota
status: en-progreso
source: claude-code
aliases: [Valid Palindrome, LC 125, isPalindrome, Palíndromo válido]
problem_id: 125
difficulty: easy
patron: two-pointers
neetcode_order: 1
---

# LeetCode 125 — Valid Palindrome

> 🎯 **Primer problema del patrón Two Pointers**. Es la introducción más limpia al patrón: dos punteros desde **extremos opuestos** que convergen hacia el centro, verificando una **propiedad simétrica**. Es la presentación canónica de "two pointers convergentes".
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Una frase es un **palíndromo** si, después de convertir todas las letras a minúscula y eliminar todos los caracteres no alfanuméricos, se lee igual hacia adelante que hacia atrás.

Dado un string `s`, devuelve `True` si es un palíndromo, `False` en caso contrario.

**Ejemplo 1:**
```
Input:  s = "A man, a plan, a canal: Panama"
Output: true
        Después de limpiar: "amanaplanacanalpanama"
```

**Ejemplo 2:**
```
Input:  s = "race a car"
Output: false
        Después de limpiar: "raceacar" — no es palíndromo
```

**Ejemplo 3:**
```
Input:  s = " "
Output: true
        Después de limpiar: "" — string vacío es palíndromo trivialmente
```

**Restricciones:**
- `1 <= s.length <= 2 * 10^5`.
- `s` consiste en caracteres ASCII imprimibles.

**Plantilla:**
```python
class Solution:
    def isPalindrome(self, s: str) -> bool:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `bool` |
| ¿Diferencia mayúsculas/minúsculas? | NO — convertir a lowercase antes |
| ¿Caracteres no alfanuméricos? | Ignorar (espacios, puntuación, símbolos) |
| ¿String vacío después de limpiar? | `True` (palíndromo trivial) |
| ¿Qué cuenta como alfanumérico? | Letras `a-z`, `A-Z`, dígitos `0-9` (no espacios ni símbolos) |
| Edge case 1 | `" "` → limpio queda `""` → `True` |
| Edge case 2 | `"a"` → palíndromo de 1 char → `True` |
| Edge case 3 | Todo no alfanumérico (`",.!?"`) → `""` → `True` |

---

## Solución 1 — Limpiar y comparar con reverse

La forma más directa: limpiar el string (filtrar alfanuméricos, lowercase) y comparar con su inverso.

```python
class Solution:
    def isPalindrome(self, s: str) -> bool:
        limpio = ''.join(c.lower() for c in s if c.isalnum())
        return limpio == limpio[::-1]
```

**Análisis:**
- **Tiempo: O(n)** — un recorrido para limpiar + un recorrido para reversar + comparación lineal.
- **Espacio: O(n)** — el string limpio + el reverse.
- **Veredicto:** ✅ funciona, idiomática y corta. Pero NO usa two pointers (que es lo que el ejercicio quiere enseñar).

> 💡 **`s[::-1]`** es un slice de Python que invierte el string. Crea una nueva string en O(n).

---

## Solución 2 — Two pointers sobre string limpio

Limpiar primero, después dos punteros desde extremos.

```python
class Solution:
    def isPalindrome(self, s: str) -> bool:
        limpio = ''.join(c.lower() for c in s if c.isalnum())
        left, right = 0, len(limpio) - 1
        while left < right:
            if limpio[left] != limpio[right]:
                return False
            left += 1
            right -= 1
        return True
```

**Análisis:**
- **Tiempo: O(n)** — limpieza + recorrido con dos punteros.
- **Espacio: O(n)** — el string limpio.
- **Veredicto:** ✅ buena. Hace explícito el patrón two pointers, pero todavía necesita el espacio auxiliar.

---

## Solución 3 — Two pointers sin espacio auxiliar (la óptima)

**La idea clave**: aplicar dos punteros directamente sobre la string original, **saltándose** los caracteres no alfanuméricos sin construir un string limpio.

```python
class Solution:
    def isPalindrome(self, s: str) -> bool:
        left, right = 0, len(s) - 1
        while left < right:
            # avanzar left mientras no sea alfanumérico
            while left < right and not s[left].isalnum():
                left += 1
            # avanzar right mientras no sea alfanumérico
            while left < right and not s[right].isalnum():
                right -= 1
            # comparar caracteres (lowercase)
            if s[left].lower() != s[right].lower():
                return False
            left += 1
            right -= 1
        return True
```

**Trace mental con `s = "A man, a plan, a canal: Panama"`**:

| Iteración | left | right | s[left] | s[right] | ¿Match? |
|---|---|---|---|---|---|
| 1 | 0 | 29 | 'A' | 'a' | ✅ (lowercase) |
| 2 | 1 (avanza saltando ' ') → 2 | 28 (retrocede) → 27 | 'm' | 'm' | ✅ |
| 3 | 3 | 26 | 'a' | 'a' | ✅ |
| ... | ... | ... | ... | ... | ... |

**Análisis:**
- **Tiempo: O(n)** — cada carácter se visita como mucho una vez (los inner whiles avanzan punteros que ya no vuelven atrás).
- **Espacio: O(1)** — solo dos índices y una variable temporal.
- **Veredicto:** ✅ **la respuesta esperada en entrevista**. Cumple O(1) espacio extra.

> 💡 **Análisis amortizado** (igual que en [[128-longest-consecutive-sequence]]): aunque hay bucles dentro de bucles, cada índice solo se mueve en una dirección y nunca vuelve atrás → O(n) total.

---

## El patrón general — "Two pointers convergentes"

**Cuándo aplicar**:

> Cuando el problema involucra una colección **lineal** (array, string) y necesitas verificar una **propiedad simétrica** o buscar pares que cumplen una condición. Los punteros parten de **extremos opuestos** y avanzan hacia el centro.

**Plantilla mental**:

```python
def two_pointers_convergentes(coleccion):
    left, right = 0, len(coleccion) - 1
    while left < right:
        # opcional: saltar elementos que no aplican
        while left < right and skip(coleccion[left]):
            left += 1
        while left < right and skip(coleccion[right]):
            right -= 1
        # procesar el par actual
        if condicion(coleccion[left], coleccion[right]):
            ...
        left += 1
        right -= 1
    return resultado
```

**Tres señales** del patrón:

1. El problema habla de **palíndromo, simétrico, par desde extremos**.
2. El array tiene **una estructura simétrica o ordenada** que aprovechar.
3. La fuerza bruta sería O(n²) probando todos los pares.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **680. Valid Palindrome II** | Permitir borrar **un carácter** y aún ser palíndromo |
| **5. Longest Palindromic Substring** | El más largo dentro del string (DP o expand around center) |
| **131. Palindrome Partitioning** | Particionar string en palíndromos (backtracking) |
| **234. Palindrome Linked List** | Mismo concepto en listas enlazadas (slow/fast + reverse) |

---

## Conceptos a interiorizar

### Métodos de string para chequeo de carácter

```python
'a'.isalnum()        # True (letra)
'5'.isalnum()        # True (dígito)
'!'.isalnum()        # False
' '.isalnum()        # False

'A'.isalpha()        # True (solo letra)
'5'.isalpha()        # False

'5'.isdigit()        # True (solo dígito)

'A'.isupper()        # True
'A'.lower()          # 'a'
'a'.upper()          # 'A'
```

### Slicing reverso

```python
s = "hello"
s[::-1]              # "olleh"
s[2:5]               # "llo"
s[:3]                # "hel"
s[3:]                # "lo"
```

### Two pointers convergentes vs paralelos

| Variante | Inicio | Avance |
|---|---|---|
| **Convergentes** (este problema) | `left=0, right=n-1` | `left += 1, right -= 1` |
| **Paralelos** (e.g. fast/slow) | `left=0, right=0` | distintas velocidades |
| **Sliding window** | `left=0, right=0` | `right` siempre, `left` condicional |

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Two pointers | Veredicto |
|---|---|---|---|---|
| 1. Limpiar + reverse | O(n) | O(n) | NO | Idiomática, no demuestra el patrón |
| 2. Limpiar + two pointers | O(n) | O(n) | Sí | Aceptable |
| 3. **Two pointers in-place** | **O(n)** | **O(1)** | Sí | ✅ La óptima |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 3** (in-place) desde cero.
2. Justifica:
   - Por qué los inner `while` no rompen la complejidad O(n).
   - Por qué el chequeo `left < right` está dentro de los inner while además del outer.
   - Por qué `.lower()` se aplica al comparar y no antes (pista: ahorrar memoria).
3. Trace mental con `s = "race a car"`. ¿En qué iteración devuelve `False`?
4. Trace mental con `s = " "` y `s = ".,!"`. ¿Resultado?
5. **Bonus** — modifica para LC 680 (Valid Palindrome II): permitir borrar **un** carácter.

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué tu Solución 3 es O(n) si tiene bucles anidados?"** → Análisis amortizado: cada índice se mueve en una sola dirección, nunca vuelve. Total: 2n movimientos máximo.
- **"¿Cómo extenderías a Unicode?"** → `isalnum()` ya funciona con Unicode en Python 3. Sin cambios. Si fuera otro lenguaje, depende.
- **"¿Cuándo usarías la Solución 1 (reverse) en lugar de Solución 3?"** → Si el código debe ser muy legible y el espacio O(n) es aceptable. La 3 es solo cuando el espacio importa.
- **"¿Qué pasa con caracteres especiales como `é`, `ñ`?"** → Son alfanuméricos en Python (`'é'.isalnum() == True`). Se incluyen y comparan tal cual. Si quisieras igualarlos a `e`, tendrías que normalizar Unicode (`unicodedata.normalize`).

---

## Solución en C++ — contraste con Python

> 📘 Añadido para ver las diferencias de lenguaje. Código compilable en [`125-valid-palindrome.cpp`](125-valid-palindrome.cpp).

```cpp
class Solution {
 public:
  bool isPalindrome(std::string s) {
    int i = 0, j = (int)s.size() - 1;
    while (i < j) {
      while (i < j && !std::isalnum((unsigned char)s[i])) ++i;
      while (i < j && !std::isalnum((unsigned char)s[j])) --j;
      if (std::tolower((unsigned char)s[i]) != std::tolower((unsigned char)s[j]))
        return false;
      ++i; --j;
    }
    return true;
  }
};
```

**Análisis:** Tiempo O(n), Espacio O(1) — igual que el Python in-place con dos punteros.

**Diferencias clave Python ↔ C++:**
- `c.isalnum()` → `std::isalnum((unsigned char)c)` (el cast a `unsigned char` es **obligatorio**: pasar un `char` con signo a `<cctype>` es UB — detalle real de C++).
- `c.lower()` → `std::tolower(...)`.
- No hay slicing barato (`s[::-1]`); el patrón idiomático es **dos índices** moviéndose hacia el centro.
- `s` se pasa por valor aquí (copia) para no requerir un buffer aparte; con `const std::string&` ahorrarías la copia.

---

## Conexiones

- [[MOC_NeetCode_150]] — índice general.
- [[128-longest-consecutive-sequence]] — análisis amortizado (mismo principio).
- Próximo: [[167-two-sum-ii-input-array-is-sorted]] — two pointers en array ordenado para encontrar pares.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 3 (in-place) desde cero
- [ ] Justificado el O(n) amortizado de la Solución 3
- [ ] Trace mental hecho con caso `"race a car"`
- [ ] Resuelto en LeetCode con éxito
- [ ] Hecho 1 vez más a la semana siguiente
