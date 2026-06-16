---
title: "LeetCode 11 — Container With Most Water"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/two-pointers, patron/greedy]
type: nota
status: en-progreso
source: claude-code
aliases: [Container With Most Water, LC 11, maxArea, Contenedor con más agua]
problem_id: 11
difficulty: medium
patron: two-pointers
neetcode_order: 4
---

# LeetCode 11 — Container With Most Water

> 🎯 **Cuarto problema del patrón Two Pointers**. Es el más **conceptual** del bloque: la solución óptima requiere un argumento de **greedy local** que no es obvio. Cuando entiendes por qué se mueve el puntero del menor (y no el del mayor), interiorizas una idea que reaparece en muchos problemas.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un array de enteros `height` de longitud `n`, hay `n` líneas verticales en un plano cartesiano de modo que los dos extremos de la `i`-ésima línea son `(i, 0)` y `(i, height[i])`.

Encuentra dos líneas que, junto con el eje x, formen el **contenedor con la mayor cantidad de agua**.

Devuelve la **cantidad máxima** de agua que el contenedor puede almacenar.

> ⚠️ **No se puede inclinar el contenedor**: el agua se queda al nivel del menor de los dos lados.

**Ejemplo 1:**
```
Input:  height = [1, 8, 6, 2, 5, 4, 8, 3, 7]
Output: 49
        Las líneas en índices 1 y 8 (alturas 8 y 7) forman el mejor contenedor:
        área = min(8, 7) * (8 - 1) = 7 * 7 = 49
```

**Ejemplo 2:**
```
Input:  height = [1, 1]
Output: 1
```

**Restricciones:**
- `n == height.length`.
- `2 <= n <= 10^5`.
- `0 <= height[i] <= 10^4`.

**Plantilla:**
```python
class Solution:
    def maxArea(self, height: List[int]) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` — área máxima |
| ¿Cómo se calcula el área de un contenedor? | `min(height[i], height[j]) * (j - i)` |
| ¿Por qué `min`? | El agua sale por el lado más bajo |
| ¿Está ordenado? | NO |
| ¿Pueden ser ceros? | Sí — un lado de altura 0 da área 0 |
| Edge case 1 | `[1, 1]` → área = 1*1 = 1 |
| Edge case 2 | `[0, 0]` → área = 0 |

---

## Solución 1 — Fuerza bruta (NO óptima)

Probar todos los pares de líneas, calcular el área, quedarse con el máximo.

```python
class Solution:
    def maxArea(self, height: List[int]) -> int:
        n = len(height)
        mejor = 0
        for i in range(n):
            for j in range(i + 1, n):
                area = min(height[i], height[j]) * (j - i)
                mejor = max(mejor, area)
        return mejor
```

**Análisis:**
- **Tiempo: O(n²)** — TLE con n = 10^5 (10^10 operaciones).
- **Espacio: O(1)**.
- **Veredicto:** ❌ rechazada.

---

## Solución 2 — Two pointers con greedy local (la óptima)

**La idea clave**: dos punteros desde extremos. En cada paso, calcular el área actual. Para la siguiente iteración, **mover el puntero de la línea más baja** (la que limita el agua), descartar el otro extremo.

```python
class Solution:
    def maxArea(self, height: List[int]) -> int:
        left, right = 0, len(height) - 1
        mejor = 0
        while left < right:
            ancho = right - left
            altura = min(height[left], height[right])
            mejor = max(mejor, altura * ancho)
            # 🔑 mover el puntero de la línea MENOR
            if height[left] < height[right]:
                left += 1
            else:
                right -= 1
        return mejor
```

**Trace mental con `height = [1, 8, 6, 2, 5, 4, 8, 3, 7]`**:

| Iter | left | right | h[l] | h[r] | ancho | min(h) | área | Acción |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 8 | 1 | 7 | 8 | 1 | 8 | h[l]<h[r] → left++ |
| 2 | 1 | 8 | 8 | 7 | 7 | 7 | **49** | h[l]>h[r] → right-- |
| 3 | 1 | 7 | 8 | 3 | 6 | 3 | 18 | h[l]>h[r] → right-- |
| 4 | 1 | 6 | 8 | 8 | 5 | 8 | 40 | h[l]==h[r] → right-- |
| 5 | 1 | 5 | 8 | 4 | 4 | 4 | 16 | h[l]>h[r] → right-- |
| 6 | 1 | 4 | 8 | 5 | 3 | 5 | 15 | h[l]>h[r] → right-- |
| 7 | 1 | 3 | 8 | 2 | 2 | 2 | 4 | h[l]>h[r] → right-- |
| 8 | 1 | 2 | 8 | 6 | 1 | 6 | 6 | h[l]>h[r] → right-- |
| 9 | 1 | 1 | — | — | — | — | — | left==right → break |

Mejor encontrado: **49** ✅.

**Análisis:**
- **Tiempo: O(n)** — los dos punteros recorren juntos n posiciones.
- **Espacio: O(1)**.
- **Veredicto:** ✅ **la óptima**. La pregunta clave es: **¿por qué mover el menor?**

### El argumento clave — por qué mover el puntero del menor

**Afirmación**: si `height[left] < height[right]`, entonces ningún par `(left, j)` con `j < right` puede mejorar el área actual.

**Demostración (informal)**:

Supongamos que mantengo `left` y muevo `right` hacia adentro a algún `j < right`:
- El **ancho** se reduce: `j - left < right - left`.
- La **altura** del contenedor está limitada por `min(height[left], height[j])`. Como `height[left]` es ya el mínimo de los dos en la posición original, **también será el mínimo o menor** en cualquier nueva posición.

Por tanto: nuevo área = `min(height[left], height[j]) * (j - left) ≤ height[left] * (j - left) < height[left] * (right - left)`.

**Conclusión**: no puede mejorar manteniendo `left`. Es **seguro descartar `left`** y avanzar.

> 🎯 Este es **un argumento de greedy local**: en cada paso descartas un candidato sabiendo que no puede llevar a una solución mejor que la actual.

---

## El patrón general — "Two pointers con greedy local"

**Cuándo aplicar**:

> Cuando puedes argumentar que **uno de los dos extremos no puede contribuir a una solución mejor que la actual** y por tanto se puede descartar. La regla de avance se deriva de una propiedad estructural del problema.

**Plantilla mental**:

```python
def two_pointers_greedy(arr):
    left, right = 0, len(arr) - 1
    mejor = elemento_neutro
    while left < right:
        actual = calcular(arr[left], arr[right])
        mejor = combinar(mejor, actual)
        # criterio de avance basado en greedy local
        if condicion_mover_left(arr[left], arr[right]):
            left += 1
        else:
            right -= 1
    return mejor
```

**Tres señales** del patrón:

1. Buscas un **óptimo** (max/min) sobre pares de elementos.
2. Hay una propiedad estructural (limitante) que permite descartar candidatos.
3. La fuerza bruta es O(n²) y el problema sugiere que se puede mejor.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **42. Trapping Rain Water** ⭐ | Calcular el agua **total** atrapada (no solo entre dos líneas) |
| **407. Trapping Rain Water II** | Versión 2D (sobre un grid) — más complejo, requiere heap |

> 📌 **Container With Most Water** y **Trapping Rain Water** se confunden en entrevistas. La diferencia: aquí buscas un solo contenedor (max área entre dos líneas); allá calculas el total de agua atrapada considerando todas las "vasijas" formadas por el perfil completo.

---

## Conceptos a interiorizar

### Greedy local — la idea

Decisión local óptima sin reconsiderar. Funciona cuando puedes **probar** que ninguna decisión futura puede beneficiarse del descarte.

Ejemplos clásicos:
- **Container With Most Water** (este problema).
- **Trapping Rain Water** (extensión natural).
- **Jump Game** (LC 55).
- **Gas Station** (LC 134).

Todos comparten la estructura: "demuestro que descartar X no me hará perder ninguna solución mejor".

### Por qué no funciona "mover ambos punteros simultáneamente"

Si en cada paso movieras left **y** right, perderías la mitad de las posibilidades. El argumento de greedy local solo permite descartar **uno** a la vez.

### Diferencia con two pointers de [[167-two-sum-ii-input-array-is-sorted]]

| Aspecto | Two Sum II (sorted) | Container With Most Water |
|---|---|---|
| ¿Array ordenado? | Sí | NO |
| Criterio de avance | Suma vs target | Altura del menor |
| Argumento | Monotonía del orden | Greedy local |
| Buscando | Igualdad | Máximo |

Mismo patrón estructural (two pointers convergentes), distinto razonamiento de avance.

---

## Comparación final de las 2 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Fuerza bruta | O(n²) | O(1) | ❌ TLE |
| 2. **Two pointers + greedy** | **O(n)** | O(1) | ✅ La óptima |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** desde cero.
2. Justifica:
   - Por qué se mueve el puntero del menor (no del mayor, no ambos).
   - Reproduce el argumento de greedy local con tus palabras.
   - Por qué la complejidad es O(n) y no O(n²).
3. Trace mental con `height = [1, 1]`. ¿Cuántas iteraciones?
4. Trace mental con `height = [4, 3, 2, 1, 4]`. ¿Cuál es el mejor par y por qué?
5. **Bonus** — ¿qué cambiaría si en lugar de min(h[l], h[r]) el contenedor admitiera **inclinación**? Pista: cambia el patrón completamente (ya no es two pointers limpio).

---

## Cosas que te pueden preguntar en entrevista

- **"Demuestra formalmente por qué mover el menor es correcto."** → Argumentación por descarte: si dejas el menor fijo y mueves el mayor hacia adentro, el área no puede aumentar (ancho disminuye, altura limitada por el mismo menor o aún más bajo).
- **"¿Y si los dos punteros tienen la misma altura?"** → Da igual cuál muevas; ambos lados son simétricos. Convención: mover cualquiera de los dos (o el right por simplicidad de código).
- **"¿Y si quisieras devolver los índices, no el área?"** → Trackear `(mejor_left, mejor_right)` además del valor.
- **"¿Cómo lo extenderías a 'agua atrapada total'?"** → Cambia el problema completamente: hay que calcular agua entre **cada** par adyacente, no solo el máximo. Lleva a [[42-trapping-rain-water]].

---

## Conexiones

- [[125-valid-palindrome]] — two pointers convergentes simple.
- [[167-two-sum-ii-input-array-is-sorted]] — two pointers en array ordenado.
- [[15-3sum]] — sort + fix + two pointers.
- Próximo: [[42-trapping-rain-water]] — versión "agua total" del mismo problema, mucho más difícil (Hard).
- [[MOC_NeetCode_150]] — índice general.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Justificado el argumento de greedy local con mis palabras
- [ ] Trace mental hecho
- [ ] Resuelto en LeetCode con éxito
- [ ] Articulada la diferencia con [[167-two-sum-ii-input-array-is-sorted]] (monotonía vs greedy)
