---
title: "LeetCode 42 — Trapping Rain Water"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/two-pointers, patron/prefix-suffix, patron/greedy]
type: nota
status: en-progreso
source: claude-code
aliases: [Trapping Rain Water, LC 42, trap, Agua atrapada, Lluvia atrapada]
problem_id: 42
difficulty: hard
patron: two-pointers
neetcode_order: 5
---

# LeetCode 42 — Trapping Rain Water

> 🎯 **Quinto y último problema de Two Pointers — primer Hard del NeetCode 150**. Es el problema más famoso de "puzzle algorítmico": parece imposible al principio, hay **3 soluciones distintas** según el nivel de optimización, y la final con two pointers es **alucinante**. Dominar este problema es un gran paso.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un array `height` de `n` enteros no negativos representando un mapa de elevación donde el ancho de cada barra es 1, calcula **cuánta agua puede ser atrapada** después de la lluvia.

**Ejemplo 1:**
```
Input:  height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
Output: 6

Visualización (agua en azul):
                #
        #  ~~~  # # ~ #
    #~~~# #~~~# # # # #
0 1 0 2 1 0 1 3 2 1 2 1
```

**Ejemplo 2:**
```
Input:  height = [4, 2, 0, 3, 2, 5]
Output: 9
```

**Restricciones:**
- `n == height.length`.
- `1 <= n <= 2 * 10^4`.
- `0 <= height[i] <= 10^5`.

**Plantilla:**
```python
class Solution:
    def trap(self, height: List[int]) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta                                            | Respuesta                                                              |
| --------------------------------------------------- | ---------------------------------------------------------------------- |
| ¿Qué tipo devuelve?                                 | `int` — total de unidades de agua atrapadas                            |
| ¿Cómo se calcula el agua atrapada en un índice `i`? | `agua[i] = min(maxLeft[i], maxRight[i]) - height[i]` (si > 0, si no 0) |
| ¿Qué es `maxLeft[i]`?                               | El máximo de `height[0..i-1]` (la "pared" más alta a la izquierda)     |
| ¿Qué es `maxRight[i]`?                              | El máximo de `height[i+1..n-1]` (la "pared" más alta a la derecha)     |
| ¿Por qué `min`?                                     | El agua sale por la pared más baja                                     |
| ¿Por qué `- height[i]`?                             | Lo que queda después de "rellenar" la barra existente                  |
| Edge case 1                                         | Array de 1 o 2 elementos → 0 (no se atrapa agua sin dos paredes)       |
| Edge case 2                                         | Array decreciente o creciente → 0 (no hay paredes a ambos lados)       |

> 💡 **El insight más importante**: el agua sobre el índice `i` está limitada por el **mínimo de las dos paredes** que la rodean (la más alta a la izquierda y la más alta a la derecha). No te confundas: las paredes inmediatas no bastan, hay que mirar **el máximo total** a cada lado.

---

## Solución 1 — Fuerza bruta (la "obvia")

Para cada índice `i`, buscar maxLeft y maxRight recorriendo el array.

```python
class Solution:
    def trap(self, height: List[int]) -> int:
        n = len(height)
        total = 0
        for i in range(n):
            max_left = max(height[:i+1]) if i > 0 else height[i]
            max_right = max(height[i:]) if i < n - 1 else height[i]
            agua = min(max_left, max_right) - height[i]
            total += max(0, agua)
        return total
```

**Análisis:**
- **Tiempo: O(n²)** — `max(height[:i+1])` cuesta O(n) por cada `i`.
- **Espacio: O(1)**.
- **Veredicto:** ❌ TLE con n = 2*10^4 (4*10^8 ops). Pero la idea es correcta.

---

## Solución 2 — Prefix max + Suffix max arrays (intuitivo, O(n) tiempo, O(n) espacio)

**Optimización**: precomputar `maxLeft` y `maxRight` en **dos pasadas**, luego una pasada final que suma.

```python
class Solution:
    def trap(self, height: List[int]) -> int:
        n = len(height)
        if n == 0:
            return 0

        max_left = [0] * n
        max_right = [0] * n

        # Pasada 1: max acumulado de izquierda
        max_left[0] = height[0]
        for i in range(1, n):
            max_left[i] = max(max_left[i-1], height[i])

        # Pasada 2: max acumulado de derecha
        max_right[n-1] = height[n-1]
        for i in range(n-2, -1, -1):
            max_right[i] = max(max_right[i+1], height[i])

        # Pasada 3: sumar agua
        total = 0
        for i in range(n):
            total += min(max_left[i], max_right[i]) - height[i]
        return total
```

**Análisis:**
- **Tiempo: O(n)** — tres pasadas lineales.
- **Espacio: O(n)** — los dos arrays auxiliares.
- **Veredicto:** ✅ correcta y aceptable. Es la solución que demuestra que **entiendes el problema**. Sin embargo, no es la óptima en espacio.

> 🎯 **Conexión directa con [[238-product-of-array-except-self]]**: el patrón prefix/suffix accumulator. Misma técnica, distinta operación (`max` en lugar de `*`).

---

## Solución 3 — Two pointers (la óptima O(1) espacio)

**La idea brillante**: en lugar de calcular maxLeft y maxRight para cada `i`, observar que con dos punteros podemos ir calculando el agua **en el lado más bajo** sin saber el max total del otro lado.

**Invariante**: en cada paso, sabemos que la pared del lado opuesto es **al menos** tan alta como `max_left` o `max_right` actuales. El lado "más bajo" determina el agua local.

```python
class Solution:
    def trap(self, height: List[int]) -> int:
        if not height:
            return 0

        left, right = 0, len(height) - 1
        max_left, max_right = height[left], height[right]
        total = 0

        while left < right:
            if max_left < max_right:
                left += 1
                max_left = max(max_left, height[left])
                total += max_left - height[left]            # agua sobre 'left'
            else:
                right -= 1
                max_right = max(max_right, height[right])
                total += max_right - height[right]          # agua sobre 'right'
        return total
```

### Trace mental con `height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]`

Estado inicial: `left=0, right=11, max_left=0, max_right=1, total=0`.

| Paso | left | right | max_left | max_right | Acción | Agua añadida |
|---|---|---|---|---|---|---|
| Inicio | 0 | 11 | 0 | 1 | max_left < max_right → mover left | — |
| 1 | 1 | 11 | max(0,1)=1 | 1 | total += 1-1=0 | 0 |
| Decidir: max_left==max_right → mover right | | | | | | |
| 2 | 1 | 10 | 1 | max(1,2)=2 | total += 2-2=0 | 0 |
| 3 | 1 | 9 | 1 | max(2,1)=2 | total += 2-1=1 | 1 |
| Decidir: max_left < max_right → mover left | | | | | | |
| 4 | 2 | 9 | max(1,0)=1 | 2 | total += 1-0=1 | 2 |
| 5 | 3 | 9 | max(1,2)=2 | 2 | total += 2-2=0 | 2 |
| 6 | 4 | 9 | max(2,1)=2 | 2 | total += 2-1=1 | 3 |
| ... | ... | ... | ... | ... | ... | ... |

Resultado final: `total = 6` ✅

### Por qué funciona — el argumento clave

**Observación**: cuando `max_left < max_right`, el agua sobre `left+1` está limitada por `min(max_left, max_right) = max_left` (porque `max_right` es al menos `max_right` y `max_left` es menor).

Aunque desconocemos el **futuro** `max_right` (puede crecer al avanzar right hacia dentro), **no importa**: ya es ≥ `max_right` actual ≥ `max_left`. La pared limitante sigue siendo `max_left`.

Por tanto, podemos calcular `agua_local = max_left - height[left+1]` sin tener `maxRight` exacto del lado derecho.

> 🎯 Este argumento es **profundo** y se repite en muchos problemas: a veces no necesitas información completa, solo saber que hay un **lower bound** que basta para tomar la decisión.

**Análisis:**
- **Tiempo: O(n)** — los dos punteros recorren n posiciones juntos.
- **Espacio: O(1)** — solo cuatro variables.
- **Veredicto:** ✅✅ **la óptima absoluta**. La que demuestra dominio del problema en una entrevista.

---

## El patrón general — "Two pointers con tracking de máximos"

**Cuándo aplicar**:

> Cuando un problema requiere conocer **el máximo (o mínimo) en cada lado** de un índice, pero no necesitas el valor exacto en cada momento, solo asegurarte de cuál es el **limitante**.

**Plantilla mental**:

```python
def two_pointers_max_track(arr):
    left, right = 0, len(arr) - 1
    max_l, max_r = arr[left], arr[right]
    resultado = 0
    while left < right:
        if max_l < max_r:
            left += 1
            max_l = max(max_l, arr[left])
            resultado += contribucion(max_l, arr[left])
        else:
            right -= 1
            max_r = max(max_r, arr[right])
            resultado += contribucion(max_r, arr[right])
    return resultado
```

**Tres señales** del patrón:

1. Buscas algo que depende de **máximos a ambos lados** de cada índice.
2. La fuerza bruta da O(n²) y el approach prefix/suffix da O(n) tiempo + O(n) espacio.
3. Existe un argumento de "el menor de los dos lados es el limitante", que permite descartar info no esencial.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **11. Container With Most Water** ⭐ | El problema "hermano" más simple |
| **407. Trapping Rain Water II** | Versión 2D (sobre grid) — necesita **heap**, mucho más complejo |
| **84. Largest Rectangle in Histogram** | Mayor rectángulo que cabe → stack monotónico |
| **85. Maximal Rectangle** | Versión 2D del 84 |
| **238. Product of Array Except Self** | Mismo patrón prefix/suffix con multiplicación |

---

## Conceptos a interiorizar

### Tres niveles de optimización en problemas de array

| Nivel | Técnica | Complejidad típica |
|---|---|---|
| 1 | Fuerza bruta con doble bucle | O(n²) |
| 2 | Prefix/Suffix arrays auxiliares | O(n) tiempo, O(n) espacio |
| 3 | Two pointers con tracking | O(n) tiempo, O(1) espacio |

Este es **un patrón mental recurrente** en LeetCode Hard. Aprender a saltar entre los tres niveles es uno de los aprendizajes más rentables.

### Cuándo el "max_left actual ≥ max_left futuro" basta

En la Solución 3, no actualizas `max_right` cuando avanzas `left`. Pero como **`max_right` solo puede crecer** al avanzar right (no decrecer), sabes que **el max_right futuro ≥ max_right actual**. Si ya `max_left < max_right`, también `max_left < max_right_futuro`. Es **un upper bound suficiente**.

### Diferencia con [[11-container-with-most-water]]

| Aspecto | Container With Most Water (LC 11) | Trapping Rain Water (LC 42) |
|---|---|---|
| Pregunta | Mejor par único | Suma total de agua |
| Output | Un número (área máxima) | Un número (suma) |
| Complejidad lógica | Greedy local | Dos máximos rastreados |
| Dificultad | Medium | Hard |

Mismo patrón estructural (two pointers convergentes), distinta cantidad de información rastreada.

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Fuerza bruta | O(n²) | O(1) | ❌ TLE |
| 2. Prefix + Suffix max arrays | O(n) | O(n) | ✅ Correcta y didáctica |
| 3. **Two pointers** | **O(n)** | **O(1)** | ✅ La óptima absoluta |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** (prefix/suffix arrays) desde cero. Es la más fácil de entender; debes poder reproducirla sin titubear.
2. Escribe la **Solución 3** (two pointers) desde cero. Esta requiere comprensión profunda del invariante.
3. Justifica:
   - Por qué `min(max_left, max_right) - height[i]` da el agua sobre `i`.
   - Por qué en la Solución 3 puedes ignorar el max del lado opuesto.
   - Cuándo conviene Solución 2 vs Solución 3.
4. Trace mental con `height = [4, 2, 0, 3, 2, 5]` (ejemplo 2). ¿Coincide con el output 9?
5. **Bonus** — implementa la Solución 3 con un solo bucle (sin `max(...)` separado). Hint: chequear antes de actualizar.

---

## Cosas que te pueden preguntar en entrevista

- **"Por qué `min(max_left, max_right)` y no `min(immediate_left, immediate_right)`?"** → Las paredes inmediatas pueden ser más bajas; lo que limita el agua es la pared **más alta total** a cada lado.
- **"Demuestra que tu Solución 3 es correcta."** → Argumento del invariante: `max_left < max_right_actual ≤ max_right_futuro` → el limitante es `max_left`. Reproducir.
- **"¿Cómo lo extenderías a 2D (un grid de elevaciones)?"** → LC 407. La generalización requiere un **heap** (priority queue) para procesar las "fronteras" del grid en orden de altura. Mucho más complejo.
- **"¿Cuál es la diferencia entre este y Container With Most Water?"** → Container busca el mejor par; Trapping suma agua atrapada por **todas** las "vasijas" formadas por el perfil.

---

## Cierre del patrón Two Pointers 🎉

Has llegado al **último problema del segundo patrón del NeetCode 150**. Resumen de los **5 problemas**:

| # | Problema | Variante | Idea distintiva |
|---|---|---|---|
| 1 | [[125-valid-palindrome]] | Convergentes simples | Verificar simetría con saltos de no-alfanuméricos |
| 2 | [[167-two-sum-ii-input-array-is-sorted]] | Convergentes en array ordenado | Monotonía permite descartar candidato por iteración |
| 3 | [[15-3sum]] | Sort + fix + two pointers | Reducir k-Sum a (k-1)-Sum |
| 4 | [[11-container-with-most-water]] | Greedy local | Mover el menor (no puede mejorar fijo) |
| 5 | **Este** | Two pointers + tracking de máximos | Argumento de "lado limitante" |

**Después de Two Pointers**, el siguiente patrón es **Sliding Window**, que extiende la idea de dos punteros a "ventanas" de tamaño variable o fijo. Avísame cuando estés listo y lo arrancamos.

---

## Conexiones

- [[125-valid-palindrome]] · [[167-two-sum-ii-input-array-is-sorted]] · [[15-3sum]] · [[11-container-with-most-water]] — todos los problemas del patrón Two Pointers.
- [[238-product-of-array-except-self]] — mismo patrón prefix/suffix accumulator (multiplicación en lugar de max).
- [[MOC_NeetCode_150]] — índice general.
- Próximo patrón: **Sliding Window** (avísame cuando quieras arrancarlo).

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 (prefix/suffix) desde cero
- [ ] Escrita Solución 3 (two pointers) desde cero
- [ ] Justificado el invariante de la Solución 3
- [ ] Trace mental hecho con ambos ejemplos
- [ ] Resuelto en LeetCode con éxito
- [ ] **Patrón Two Pointers cerrado** ✅
