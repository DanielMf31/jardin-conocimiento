---
title: "LeetCode 167 — Two Sum II - Input Array Is Sorted"
date: 2026-05-07
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/two-pointers]
type: nota
status: en-progreso
source: claude-code
aliases: [Two Sum II, LC 167, twoSum sorted, Two pointers ordenado]
problem_id: 167
difficulty: medium
patron: two-pointers
neetcode_order: 2
---

# LeetCode 167 — Two Sum II - Input Array Is Sorted

> 🎯 **Segundo problema del patrón Two Pointers**. Es **el problema hermano** de [[1-two-sum]] con una sola diferencia: el array está **ordenado**. Esa diferencia cambia completamente la solución óptima: **two pointers O(1) espacio** en lugar de hash map O(n).
> 📚 Es uno de los problemas más útiles para interiorizar **cuándo usar two pointers vs hash map**.

## Enunciado

Dado un array de enteros `numbers` **ordenado de forma no decreciente** (1-indexed) y un entero `target`, encuentra dos números que sumen `target`.

Devuelve los **índices** (1-indexed) de los dos números en orden creciente, como `[index1, index2]`.

**Tu solución debe usar solo espacio extra constante O(1).**

**Ejemplo 1:**
```
Input:  numbers = [2, 7, 11, 15], target = 9
Output: [1, 2]
        Explicación: numbers[1] + numbers[2] = 2 + 7 = 9 (1-indexed)
```

**Ejemplo 2:**
```
Input:  numbers = [2, 3, 4], target = 6
Output: [1, 3]
```

**Ejemplo 3:**
```
Input:  numbers = [-1, 0], target = -1
Output: [1, 2]
```

**Restricciones:**
- `2 <= numbers.length <= 3 * 10^4`.
- `-1000 <= numbers[i] <= 1000`.
- `numbers` está **ordenado de forma no decreciente**.
- `-1000 <= target <= 1000`.
- **Existe exactamente una solución**.
- **No puedes usar el mismo elemento dos veces**.

**Plantilla:**
```python
class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `List[int]` con **dos índices 1-indexed** |
| ⚠️ ¿1-indexed o 0-indexed? | **1-indexed** (cuidado, distinto de [[1-two-sum]]) |
| ¿Está ordenado? | **SÍ — clave del problema** |
| ¿Hay duplicados? | Sí pueden existir |
| ¿Pueden ser negativos? | Sí (rango -1000 a 1000) |
| ¿Solución única? | Sí, garantizada |
| Restricción nueva | **O(1) espacio extra** — descarta hash map |

> 💡 **El detalle "ordenado" cambia todo**: con array ordenado, dos punteros pueden navegar por el espacio de pares en O(n) usando la **monotonía** del orden, sin necesitar memoria auxiliar.

---

## Solución 1 — Hash map (la de [[1-two-sum]])

Funciona pero **NO cumple** la restricción O(1) espacio.

```python
class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        visto = {}
        for i, num in enumerate(numbers):
            comp = target - num
            if comp in visto:
                return [visto[comp] + 1, i + 1]    # 1-indexed
            visto[num] = i
        return []
```

**Análisis:**
- **Tiempo: O(n)**.
- **Espacio: O(n)** — viola la restricción.
- **Veredicto:** ❌ No es la respuesta esperada. **Ignora la información clave del problema** (que está ordenado).

---

## Solución 2 — Two pointers convergentes (la canónica)

**La idea clave**: dos punteros, uno al inicio (`left`) y otro al final (`right`).

- Si `numbers[left] + numbers[right] == target` → encontrado.
- Si la suma es **menor** que target → necesito un número mayor → `left += 1` (avanzar hacia números mayores).
- Si la suma es **mayor** que target → necesito un número menor → `right -= 1` (retroceder hacia números menores).

```python
class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        left, right = 0, len(numbers) - 1
        while left < right:
            suma = numbers[left] + numbers[right]
            if suma == target:
                return [left + 1, right + 1]       # 1-indexed
            elif suma < target:
                left += 1
            else:
                right -= 1
        return []                                   # nunca alcanzado por garantía
```

**Trace mental con `numbers = [2, 7, 11, 15], target = 9`**:

| Iter | left | right | numbers[left] | numbers[right] | suma | Acción |
|---|---|---|---|---|---|---|
| 1 | 0 | 3 | 2 | 15 | 17 | suma > target → right-- |
| 2 | 0 | 2 | 2 | 11 | 13 | suma > target → right-- |
| 3 | 0 | 1 | 2 | 7 | 9 | ✅ encontrado, return [1, 2] |

**Análisis:**
- **Tiempo: O(n)** — cada puntero se mueve como mucho n veces.
- **Espacio: O(1)** — solo dos índices.
- **Veredicto:** ✅ **la óptima**. Cumple las restricciones del problema.

### Por qué funciona — argumento de corrección

**Invariante**: después de descartar un puntero, el target **no se puede formar** con ese índice descartado.

- Si `numbers[left] + numbers[right] < target`: como el array está ordenado, **cualquier emparejamiento de left con un índice menor que right** dará una suma todavía más pequeña. Por tanto, left no puede formar el target con ningún índice ≤ right. Lo descartamos avanzando `left`.
- Análogamente para el otro caso.

Esto es **prueba por descarte**: cada movimiento elimina un candidato sin posibilidad de error.

---

## El patrón general — "Two pointers en array ordenado"

**Cuándo aplicar**:

> Cuando el problema involucra **pares (o más) en un array ordenado** que cumplen una relación de magnitud (suma, producto, distancia). El orden permite descartar candidatos en O(1) por iteración.

**Plantilla mental**:

```python
def two_pointers_ordenado(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        valor = combinar(arr[left], arr[right])
        if valor == target:
            return resultado(left, right)
        elif valor < target:
            left += 1                  # necesito mayor
        else:
            right -= 1                 # necesito menor
    return None
```

**Tres señales** del patrón:

1. El array está **ordenado** (o el problema permite ordenarlo).
2. Buscas pares (o tripletas, fixeando uno) que cumplen relación aritmética.
3. La solución hash map funcionaría pero hay restricción de espacio O(1).

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **1. Two Sum** | Mismo problema pero array **NO ordenado** → hash map |
| **15. 3Sum** ⭐ | Triplete que suma 0 → ordenar + fix uno + two pointers |
| **16. 3Sum Closest** | Triplete con suma más cercana al target |
| **18. 4Sum** | Cuarteto que suma target → 2 fixes + two pointers |
| **611. Valid Triangle Number** | Triángulos válidos en array ordenado → two pointers |

> 🎯 **3Sum, 4Sum se reducen a este patrón fixeando elementos** y aplicando two pointers en el resto. Esta es **la base** de toda la familia "K-Sum".

---

## Conceptos a interiorizar

### Two pointers vs Binary search

Dos técnicas O(log n)/O(n) sobre arrays ordenados, distintas:

| Técnica | Uso típico | Cómo |
|---|---|---|
| **Binary search** | Encontrar **un** elemento | Descartar mitad del array por iteración |
| **Two pointers** | Encontrar **par/k-tuple** | Descartar un candidato por iteración |

Binary search es O(log n) total. Two pointers es O(n) total.

### Cuándo conviene cada estrategia para "two sum"

| Caso | Mejor solución | Razón |
|---|---|---|
| Array ordenado, restricción de espacio | **Two pointers** | O(1) espacio |
| Array desordenado | **Hash map** | O(n) tiempo sin sort |
| Array desordenado + restricción espacio | Sort + two pointers | O(n log n) tiempo, O(1) espacio (modifica input) |

### 1-indexed vs 0-indexed

LeetCode normalmente usa 0-indexed. Este problema **explícitamente** pide 1-indexed (extraño, pero es así). Trampa común: olvidar el `+ 1`.

---

## Comparación final de las 2 soluciones

| Solución | Tiempo | Espacio | Cumple restricción | Veredicto |
|---|---|---|---|---|
| 1. Hash map | O(n) | O(n) | ❌ | Funciona pero no usa la información de orden |
| 2. **Two pointers** | **O(n)** | **O(1)** | ✅ | ✅ La óptima |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** (two pointers) desde cero.
2. Justifica:
   - Por qué `left += 1` cuando `suma < target` (no `right -= 1`).
   - Por qué este algoritmo es correcto: invariante y prueba por descarte.
   - Cuál es la complejidad temporal y espacial, y por qué cumple las restricciones.
3. Trace mental con `numbers = [-1, 0]`, `target = -1`. ¿Cuántas iteraciones?
4. Trace mental con `numbers = [2, 3, 4]`, `target = 6`.
5. **Bonus** — extensión: ¿cómo lo cambiarías para devolver TODOS los pares que sumen target en un array que puede tener duplicados?

---

## Cosas que te pueden preguntar en entrevista

- **"Compara con LC 1 Two Sum. ¿Por qué allá hash map y aquí two pointers?"** → LC 1 array desordenado, no hay monotonía → hash map. LC 167 ordenado, monotonía → two pointers con O(1) espacio.
- **"Y si el array NO estuviera ordenado pero la restricción de espacio fuera O(1)?"** → Sort + two pointers. O(n log n) tiempo, O(1) espacio (in-place). Pero **modifica el input**, hay que aclararlo.
- **"¿Y si quisieras todos los pares (no solo uno)?"** → Two pointers continúa, pero hay que saltar duplicados con cuidado (ver [[15-3sum]]).
- **"Demuestra que tu algoritmo termina."** → `right - left` decrece estrictamente en cada iteración (left++ o right--). Por tanto `left == right` en O(n) iteraciones máximo.

---

## Conexiones

- [[1-two-sum]] — versión NO ordenada con hash map.
- [[125-valid-palindrome]] — primer problema del patrón.
- Próximo: [[15-3sum]] — extiende a tripletas, combina sort + fix + two pointers.
- [[MOC_NeetCode_150]] — índice general.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Justificada la prueba por descarte (corrección del algoritmo)
- [ ] Trace mental hecho
- [ ] Resuelto en LeetCode con éxito
- [ ] Articulada la diferencia con LC 1 (hash map vs two pointers)
