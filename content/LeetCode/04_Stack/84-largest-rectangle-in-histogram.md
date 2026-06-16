---
title: "LeetCode 84 — Largest Rectangle in Histogram"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/hard, patron/stack, patron/stack-monotonica, patron/analisis-amortizado]
type: nota
status: en-progreso
source: claude-code
aliases: [Largest Rectangle in Histogram, LC 84, largestRectangleArea, Rectángulo más grande histograma]
problem_id: 84
difficulty: hard
patron: stack
neetcode_order: 7
---

# LeetCode 84 — Largest Rectangle in Histogram

> 🎯 **Séptimo y último problema del patrón Stack — el Hard del patrón**. Es **el problema más difícil de Stack** y **uno de los más importantes** porque la técnica de "stack monotónico para áreas" se generaliza a problemas 2D (LC 85 Maximal Rectangle). Aprendelo bien y desbloqueas una familia entera de problemas.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un array de enteros `heights` representando las alturas de las barras de un **histograma** (ancho de cada barra = 1), encuentra el **área del rectángulo más grande** que cabe dentro del histograma.

**Ejemplo 1:**
```
Input:  heights = [2, 1, 5, 6, 2, 3]
Output: 10

Visualización:
                 ___
                |  |___
                |  |  |
                |  |  |
                |  |  |   ___
            ___ |  |  |__|  |
        ___|   ||  |  |  |  |
       |   |   ||  |  |  |  |
        2   1   5   6   2   3

  El rectángulo de área 10 cubre las barras de altura 5 y 6:
  altura mínima = 5, ancho = 2 → área = 10
```

**Ejemplo 2:**
```
Input:  heights = [2, 4]
Output: 4 (la barra 2 da 2x2=4, la barra 4 da 1x4=4)
```

**Restricciones:**
- `1 <= heights.length <= 10^5`
- `0 <= heights[i] <= 10^4`

**Plantilla:**
```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` — área máxima |
| ¿Las barras son adyacentes (sin huecos)? | Sí, ancho 1 cada una |
| ¿Cómo se calcula el área de un rectángulo dentro? | `min(alturas_en_rango) * (índice_derecho - índice_izquierdo + 1)` |
| ¿Para cada barra `i`, cuál es el mejor rectángulo que la **incluye** y la usa como ALTURA? | `heights[i] * (right_bound - left_bound + 1)` donde left/right son los índices de barras estrictamente menores |
| Edge case 1 | Una sola barra → área = `heights[0]` |
| Edge case 2 | Todas iguales → área = `n * heights[0]` |

> 💡 **El insight clave**: para cada barra `i`, el rectángulo más alto que la usa como altura mínima se extiende desde la primera barra **estrictamente menor a su izquierda** hasta la primera barra **estrictamente menor a su derecha** (ambas exclusivas). Si encontramos esos dos índices para cada `i`, el área de cada candidato se calcula en O(1).

---

## Solución 1 — Fuerza bruta O(n²)

Para cada par (i, j), calcular `min(heights[i..j]) * (j - i + 1)`.

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n = len(heights)
        best = 0
        for i in range(n):
            min_h = heights[i]
            for j in range(i, n):
                min_h = min(min_h, heights[j])
                best = max(best, min_h * (j - i + 1))
        return best
```

**Análisis:**
- **Tiempo: O(n²)** — TLE con n = 10^5.
- **Espacio: O(1)**.
- **Veredicto:** ❌ TLE.

---

## Solución 2 — Para cada barra, expandir hasta encontrar menor (O(n²) peor caso)

Para cada `i`, expandir izquierda y derecha mientras altura ≥ `heights[i]`. Calcular área.

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        n = len(heights)
        best = 0
        for i in range(n):
            # expandir izquierda
            left = i
            while left > 0 and heights[left - 1] >= heights[i]:
                left -= 1
            # expandir derecha
            right = i
            while right < n - 1 and heights[right + 1] >= heights[i]:
                right += 1
            best = max(best, heights[i] * (right - left + 1))
        return best
```

**Análisis:**
- **Tiempo: O(n²)** peor caso (array todo iguales).
- **Espacio: O(1)**.
- **Veredicto:** ❌ TLE pero más cerca conceptualmente de la solución óptima.

---

## Solución 3 — Stack monotónico (la canónica O(n))

**La idea brillante**: usar un stack monotónico **creciente** de índices. Mientras la altura actual sea menor que la del top del stack, **calcular el área** que tiene como altura el top que se va a sacar.

Cuando hacemos pop de un índice `i`:
- El **límite derecho** del rectángulo es `current_index - 1` (la barra actual, que es menor, lo "cierra").
- El **límite izquierdo** es `stack[-1] + 1` después del pop (la nueva top del stack es la primera barra menor a la izquierda).
- El **ancho** es `current_index - stack[-1] - 1` (o `current_index` si stack queda vacío).

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        stack = []                                          # índices, alturas crecientes
        best = 0
        n = len(heights)

        for i in range(n):
            # mientras el top del stack tenga altura mayor que la actual,
            # podemos cerrar el rectángulo del top
            while stack and heights[stack[-1]] > heights[i]:
                top = stack.pop()
                width = i if not stack else i - stack[-1] - 1
                best = max(best, heights[top] * width)
            stack.append(i)

        # procesar lo que queda en el stack al final (límite derecho = n)
        while stack:
            top = stack.pop()
            width = n if not stack else n - stack[-1] - 1
            best = max(best, heights[top] * width)

        return best
```

**Trace mental con `heights = [2, 1, 5, 6, 2, 3]`**:

```
Inicial: stack=[], best=0

i=0, h=2:
  stack vacío → no while
  push 0                    stack=[0]

i=1, h=1:
  top heights[0]=2 > 1 → pop 0
    width = 1 (stack vacío) → 1
    area = 2 * 1 = 2
    best = 2
  stack vacío → exit while
  push 1                    stack=[1]

i=2, h=5:
  top heights[1]=1 ≤ 5 → no pop
  push 2                    stack=[1, 2]

i=3, h=6:
  top heights[2]=5 ≤ 6 → no pop
  push 3                    stack=[1, 2, 3]

i=4, h=2:
  top heights[3]=6 > 2 → pop 3
    width = 4 - 2 - 1 = 1
    area = 6 * 1 = 6
    best = 6
  top heights[2]=5 > 2 → pop 2
    width = 4 - 1 - 1 = 2
    area = 5 * 2 = 10
    best = 10
  top heights[1]=1 ≤ 2 → no pop
  push 4                    stack=[1, 4]

i=5, h=3:
  top heights[4]=2 ≤ 3 → no pop
  push 5                    stack=[1, 4, 5]

Final del primer for. Procesar lo que queda:

pop 5: width = 6 - 4 - 1 = 1, area = 3 * 1 = 3, best=10
pop 4: width = 6 - 1 - 1 = 4, area = 2 * 4 = 8, best=10
pop 1: width = 6 (stack vacío), area = 1 * 6 = 6, best=10

Return 10 ✅
```

**Análisis:**
- **Tiempo: O(n)** — análisis amortizado: cada índice entra y sale del stack a lo sumo una vez.
- **Espacio: O(n)**.
- **Veredicto:** ✅ **la canónica**. La que demuestra dominio del patrón.

---

## Solución 4 — Stack monotónico con "sentinel" (versión más limpia)

Añadir una barra de altura 0 al final del array. Esto fuerza a que el stack se vacíe naturalmente al final, eliminando el segundo while.

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        heights.append(0)                                    # sentinel
        stack = []
        best = 0

        for i, h in enumerate(heights):
            while stack and heights[stack[-1]] > h:
                top = stack.pop()
                width = i if not stack else i - stack[-1] - 1
                best = max(best, heights[top] * width)
            stack.append(i)

        heights.pop()                                        # restaurar
        return best
```

**Análisis:** mismo O(n).

**Veredicto:** ✅ más limpia. **Trick de "sentinel"** — añadir un valor que fuerza el cierre. Útil en muchos problemas de stack.

---

## El patrón general — "Stack monotónico para áreas / extensiones"

**Cuándo aplicar**:

> Cuando el problema pide **el rectángulo / región máxima** donde cada elemento "puede extenderse" hasta el primer elemento que lo bloquea por izquierda y derecha. La fuerza bruta es O(n²); el stack monotónico es O(n).

**Plantilla mental**:

```python
def stack_monotonica_areas(arr):
    stack = []                              # índices, valores crecientes
    best = 0
    for i, x in enumerate(arr + [0]):       # sentinel
        while stack and arr[stack[-1]] > x:
            top = stack.pop()
            width = i if not stack else i - stack[-1] - 1
            best = max(best, arr[top] * width)
        stack.append(i)
    return best
```

**Tres señales** del patrón:

1. Quieres el **rectángulo / región más grande** que cumple alguna propiedad.
2. Cada elemento "limita" la altura del rectángulo que puede formar.
3. La fuerza bruta es O(n²) y existe estructura monotónica explotable.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **85. Maximal Rectangle** | Versión 2D: matriz binaria, mayor rectángulo de 1s → reducir a LC 84 fila por fila |
| **42. Trapping Rain Water** | "Inverso": agua atrapada (stack monotónica decreciente) |
| **901. Online Stock Span** | Stack monotónico en streaming |

> 🎯 **LC 85 (Maximal Rectangle)** se resuelve aplicando LC 84 a cada fila tratada como histograma. Es el "siguiente nivel" de este problema.

---

## Conceptos a interiorizar

### "Sentinel" como técnica

Añadir un valor centinela (e.g. 0 al final, -inf al principio) para evitar casos especiales:

```python
arr = [3, 1, 4]
arr_with_sentinels = [-inf] + arr + [-inf]    # para próximo mayor a izq y der
arr_with_zero = arr + [0]                     # para vaciar stack al final
```

Se usa en stack monotónico, sliding window, prefix sums, etc.

### Análisis amortizado (de nuevo)

Mismo argumento que en LC 739 y LC 239: cada índice entra y sale del stack ≤ 1 vez. Total ≤ 2n operaciones.

### Cálculo del width — la fórmula crítica

Cuando hago pop de `top`, el rectángulo de altura `heights[top]` se extiende:
- **Por la derecha**: hasta `i - 1` (la barra actual `i` lo "corta").
- **Por la izquierda**: hasta `stack[-1] + 1` (la barra menor en el stack lo "corta") — o desde el principio si el stack quedó vacío.

```
width = (i - 1) - (stack[-1] + 1) + 1 = i - stack[-1] - 1
```

Si el stack queda vacío después del pop, no hay límite izquierdo → `width = i` (desde el principio).

---

## Comparación final de las 4 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Fuerza bruta doble bucle | O(n²) | O(1) | ❌ TLE |
| 2. Expandir desde cada barra | O(n²) | O(1) | ❌ TLE peor caso |
| 3. **Stack monotónico clásico** | **O(n)** | O(n) | ✅ La canónica |
| 4. **Stack monotónico con sentinel** | **O(n)** | O(n) | ✅ Más limpia |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 3** desde cero. Es difícil — date 30+ min sin frustrarte.
2. Justifica:
   - La fórmula `width = i - stack[-1] - 1`.
   - Por qué `width = i` cuando el stack está vacío.
   - Por qué stack monotónico **creciente** (no decreciente).
3. Trace mental con `heights = [2, 4, 2]`. ¿Cuál es el rectángulo máximo?
4. Implementa la **Solución 4** con sentinel. Compara la lógica.
5. **Bonus** — ¿cómo lo extenderías a LC 85 (Maximal Rectangle)? Pista: aplica LC 84 a cada fila tratada como histograma de 1s acumulados.

---

## Cosas que te pueden preguntar en entrevista

- **"Demuestra el O(n)."** → Análisis amortizado: cada índice push y pop ≤ 1 vez. Total ≤ 2n.
- **"¿Por qué stack creciente y no decreciente?"** → Quieres saber, para cada barra, dónde están las barras menores (a izq y der). Stack creciente mantiene "candidatos" hasta que llega uno menor que los cierra.
- **"¿Y si las alturas pudieran ser negativas?"** → El problema cambia de naturaleza; rectángulos con altura negativa no tienen sentido físico.
- **"¿Cómo lo aplicarías a 2D?"** → LC 85: para cada fila, calcular la "altura acumulada de 1s" y aplicar LC 84.
- **"¿Cuál es el caso peor?"** → Array creciente: el stack acumula todos los elementos y se vacía al final.

---

## Cierre del patrón Stack 🎉

Has llegado al **último problema del cuarto patrón del NeetCode 150**. Resumen de los **7 problemas**:

| # | Problema | Variante | Idea distintiva |
|---|---|---|---|
| 1 | [[20-valid-parentheses]] | Stack matching | LIFO para emparejar delimitadores |
| 2 | [[155-min-stack]] | Diseño de clase | Stack auxiliar para min en O(1) |
| 3 | [[150-evaluate-reverse-polish-notation]] | Evaluación expresiones | Operadores consumen 2 últimos |
| 4 | [[22-generate-parentheses]] | Backtracking | Construcción con poda; intro al patrón 10 |
| 5 | [[739-daily-temperatures]] | Stack monotónico decreciente | "Próximo mayor a la derecha" |
| 6 | [[853-car-fleet]] | Sort + stack | Procesar en orden con tracking |
| 7 | **Este** | Stack monotónico creciente | "Áreas máximas" y rectángulos |

**Después de Stack**, los siguientes patrones se apoyan en lo que has visto:
- **Binary Search** (5) — algoritmo clásico, distinto pero corto.
- **Linked List** (6) — más mecánico (slow/fast, reverse).
- **Trees** (7) — recursión + BFS con `deque` (que ya viste en patrón 3).

---

## Conexiones

- [[20-valid-parentheses]] · [[155-min-stack]] · [[150-evaluate-reverse-polish-notation]] · [[22-generate-parentheses]] · [[739-daily-temperatures]] · [[853-car-fleet]] — todos los problemas del patrón.
- [[239-sliding-window-maximum]] — deque monotónica, primo cercano.
- [[42-trapping-rain-water]] — stack monotónico es solución alternativa.
- [[MOC_NeetCode_150]] — índice general.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 3 (stack monotónico clásico) desde cero
- [ ] Implementada Solución 4 (con sentinel)
- [ ] Justificada la fórmula de width
- [ ] Trace mental con array decreciente y creciente
- [ ] Resuelto en LeetCode con éxito
- [ ] **Patrón Stack cerrado** ✅
