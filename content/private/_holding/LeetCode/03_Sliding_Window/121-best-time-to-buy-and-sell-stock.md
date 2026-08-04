---
title: "LeetCode 121 — Best Time to Buy and Sell Stock"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/sliding-window, patron/one-pass-tracking]
type: nota
status: en-progreso
source: claude-code
aliases: [Best Time to Buy and Sell Stock, LC 121, maxProfit, Mejor momento comprar acción]
problem_id: 121
difficulty: easy
patron: sliding-window
neetcode_order: 1
---

# LeetCode 121 — Best Time to Buy and Sell Stock

> **Primer problema del patrón Sliding Window**, aunque la solución óptima es realmente **one-pass tracking** (track del mínimo histórico). Es la introducción más suave al pensamiento de "ventana": una ventana que solo crece, donde mantienes el "mejor punto de partida" visto.
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Te dan un array `prices` donde `prices[i]` es el precio de una acción el día `i`.

Quieres maximizar tu beneficio eligiendo **un día para comprar** y **un día posterior para vender**.

Devuelve el **máximo beneficio** que puedes lograr. Si no puedes obtener beneficio, devuelve `0`.

**Ejemplo 1:**
```
Input:  prices = [7, 1, 5, 3, 6, 4]
Output: 5
        Compra día 2 (precio=1), vende día 5 (precio=6). Beneficio = 6 - 1 = 5.
```

**Ejemplo 2:**
```
Input:  prices = [7, 6, 4, 3, 1]
Output: 0
        Imposible obtener beneficio (precios solo bajan) → 0.
```

**Restricciones:**
- `1 <= prices.length <= 10^5`
- `0 <= prices[i] <= 10^4`

**Plantilla:**
```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` — beneficio máximo |
| ¿Puedo vender antes de comprar? | NO — el día de venta debe ser **estrictamente posterior** al de compra |
| ¿Puedo comprar y vender el mismo día? | NO (no daría beneficio de todas formas) |
| ¿Múltiples transacciones? | NO en este problema. Una compra + una venta. (Para múltiples ver LC 122) |
| ¿Si no hay beneficio posible? | Devolver `0` (no negativos) |
| Edge case 1 | `prices = [5]` → 0 (no se puede vender) |
| Edge case 2 | Precios decrecientes → 0 |

> **Reformulación clave**: para cada día `i`, el mejor beneficio terminando en `i` es `prices[i] - min(prices[0..i-1])`. El resultado es el max de eso sobre todos los días.

---

## Solución 1 — Fuerza bruta O(n²)

Probar todos los pares (i, j) con i < j.

```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        n = len(prices)
        best = 0
        for i in range(n):
            for j in range(i + 1, n):
                best = max(best, prices[j] - prices[i])
        return best
```

**Análisis:**
- **Tiempo: O(n²)** — TLE con n = 10^5.
- **Espacio: O(1)**.
- **Veredicto:** [NO] rechazada por TLE.

---

## Solución 2 — One-pass tracking del mínimo (la canónica)

**La idea clave**: en cada día `i`, para maximizar el beneficio terminando en ese día necesito **el mínimo precio anterior**. Si voy de izquierda a derecha y mantengo "el mínimo visto hasta ahora", calculo el beneficio en O(1) por día.

```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        min_price = float('inf')                # ⭐ mínimo visto hasta ahora
        best = 0
        for price in prices:
            min_price = min(min_price, price)   # actualizar mínimo
            best = max(best, price - min_price) # beneficio si vendo HOY
        return best
```

**Trace mental con `prices = [7, 1, 5, 3, 6, 4]`**:

| Día | price | min_price (después) | profit hoy (`price - min`) | best (después) |
|---|---|---|---|---|
| 0 | 7 | 7 | 0 | 0 |
| 1 | 1 | 1 | 0 | 0 |
| 2 | 5 | 1 | 4 | 4 |
| 3 | 3 | 1 | 2 | 4 |
| 4 | 6 | 1 | **5** | **5** |
| 5 | 4 | 1 | 3 | 5 |

Resultado: `5` [OK]

**Análisis:**
- **Tiempo: O(n)** — un solo recorrido.
- **Espacio: O(1)** — dos variables.
- **Veredicto:** [OK] **la óptima**. La respuesta esperada en entrevista.

### Aclaración a una duda común — "¿qué pasa si el min llega al final sin precios mayores después?"

Una preocupación natural al ver este algoritmo: "si tengo `prices = [3, 100_000_000, 1, 1, 1]` y el `min_price` baja a `1` al final, ¿el algoritmo se 'queda esperando' un precio mayor que ya no llega y pierde el beneficio del 100M?".

**No, no lo pierde.** La razón está en el `max` de `best = max(best, ...)`: `best` es un **acumulador histórico que nunca decrece**.

Trace con `prices = [3, 100_000_000, 1, 1, 1]`:

| Iter | price | min_price (después) | profit hoy | best (después) |
|---|---|---|---|---|
| 1 | 3 | 3 | 0 | 0 |
| 2 | **100M** | 3 | **99_999_997** | **99_999_997** capturado |
| 3 | 1 | 1 | 0 | 99_999_997 [OK] no se pierde |
| 4 | 1 | 1 | 0 | 99_999_997 |
| 5 | 1 | 1 | 0 | 99_999_997 |

Cuando llegas al `100M`, `min_price` aún es `3` (el `1` no ha llegado todavía). El cálculo `100M - 3 = 99_999_997` se almacena en `best`. Después, cuando aparece el `1`:
- `min_price` baja a `1`.
- `1 - 1 = 0`, que NO supera al `99_999_997` ya guardado.
- `best` se mantiene gracias al `max(...)`.

**La idea mental**: el algoritmo simula "para cada día, ¿cuál sería el mejor beneficio si vendiera HOY?". El resultado global es el máximo sobre todos los días. **No espera a saber el futuro** — en cada día anota el mejor cálculo posible y se queda con él.

**Caso degenerado** (sin oportunidad de beneficio):

```
prices = [5, 4, 3, 2, 1]   (decreciente)
```

| Iter | price | min | profit hoy | best |
|---|---|---|---|---|
| 1 | 5 | 5 | 0 | 0 |
| 2 | 4 | 4 | 0 | 0 |
| 3 | 3 | 3 | 0 | 0 |
| 4 | 2 | 2 | 0 | 0 |
| 5 | 1 | 1 | 0 | 0 |

Devuelve `0` correctamente. El algoritmo NO se confunde por el min final.

### Extensión: devolver TAMBIÉN los índices de compra y venta

Si en lugar del beneficio quieres saber **qué día comprar y qué día vender**, basta con trackear dos índices más:

```python
class Solution:
    def maxProfitWithDays(self, prices: List[int]) -> tuple:
        min_price = float('inf')
        min_idx = 0                          # día del min visto hasta ahora
        best = 0
        buy_day = sell_day = 0               # mejor par encontrado

        for i, price in enumerate(prices):
            # Actualizar min PRIMERO
            if price < min_price:
                min_price = price
                min_idx = i

            # Si vender HOY supera el mejor, actualizar
            if price - min_price > best:
                best = price - min_price
                buy_day = min_idx
                sell_day = i

        return (best, buy_day, sell_day)
```

**Trace con `prices = [3, 100_000_000, 1, 1, 1]`**:

| Iter | price | min_price | min_idx | profit | best | buy_day | sell_day |
|---|---|---|---|---|---|---|---|
| 0 | 3 | 3 | 0 | 0 | 0 | 0 | 0 |
| 1 | 100M | 3 | 0 | 99_999_997 | **99_999_997** | **0** | **1** |
| 2 | 1 | 1 | 2 | 0 | 99_999_997 | 0 | 1 |
| 3 | 1 | 1 | 2 | 0 | 99_999_997 | 0 | 1 |
| 4 | 1 | 1 | 2 | 0 | 99_999_997 | 0 | 1 |

Devuelve `(99_999_997, 0, 1)` — comprar día 0, vender día 1.

> **El truco clave**: `min_idx` se actualiza **siempre** (sigue al `min_price`), pero `buy_day` y `sell_day` SOLO se actualizan **cuando hay un nuevo `best`**. Esto separa "día del mínimo actual" (que cambia con cada nuevo mínimo) de "día del mejor par hasta ahora" (que solo cambia cuando aparece un par realmente mejor).

> **Cuidado con el orden de los chequeos**: actualizar `min_price` ANTES de calcular `profit`. Si lo haces al revés, perderías la oportunidad de "comprar y vender el mismo día" (que da 0, lo cual no es un problema aquí, pero conceptualmente importa).

---

## Solución 3 — Two pointers / sliding window explícito

Misma lógica pero formulada como dos punteros: `left` apunta al "día de compra" candidato, `right` al "día de venta" actual. Si encontramos un `right` con precio menor que `left`, "compramos" en `right`.

```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        left, right = 0, 1
        best = 0
        while right < len(prices):
            if prices[left] < prices[right]:
                best = max(best, prices[right] - prices[left])
            else:
                left = right                    # comprar más barato AHORA
            right += 1
        return best
```

**Análisis:** mismo O(n) tiempo, O(1) espacio.

**Veredicto:** funciona y muestra el patrón "ventana" más explícitamente. Pero la Solución 2 es más limpia.

---

## El patrón general — "One-pass tracking de extremo histórico"

**Cuándo aplicar**:

> Cuando el problema se reduce a, en cada paso, comparar el elemento actual con un **extremo (min/max/cualquier estadístico)** de los anteriores. La fuerza bruta es O(n²) probando pares; la versión optimizada mantiene el extremo mientras recorres.

**Plantilla mental**:

```python
def patron_track_extremo(arr):
    extremo = elemento_neutro              # inf, -inf, 0, etc.
    mejor = 0
    for x in arr:
        # opción 1: el mejor terminando en x
        mejor = max(mejor, comparar(x, extremo))
        # opción 2: actualizar extremo
        extremo = combinar(extremo, x)
    return mejor
```

**Tres señales** del patrón:

1. Quieres maximizar (o minimizar) algo que depende de **dos puntos** de la secuencia.
2. La fuerza bruta es O(n²).
3. Para cada punto, el "mejor compañero" anterior es siempre el extremo (min, max, etc.) — no necesitas conocer toda la historia.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **122. Best Time to Buy and Sell Stock II** | **Múltiples** transacciones permitidas → suma de subidas |
| **123. Best Time to Buy and Sell Stock III** | **Máximo 2** transacciones → DP |
| **309. Best Time to Buy and Sell Stock with Cooldown** | Cooldown entre transacciones → DP |
| **714. Best Time to Buy and Sell Stock with Transaction Fee** | Fee por transacción → DP |
| **53. Maximum Subarray** | Mismo patrón pero con sumas (Kadane's algorithm) |

---

## Conceptos a interiorizar

### `float('inf')` y `float('-inf')`

Para inicializar mínimos / máximos cuando no hay valor inicial razonable:

```python
min_seen = float('inf')                    # cualquier valor será menor
max_seen = float('-inf')                   # cualquier valor será mayor

# Equivalente con math
import math
math.inf
-math.inf
```

> **Cuándo usarlo**: en cualquier loop donde mantengas un min/max y quieras que la **primera comparación** funcione sin caso especial.

### Tracking en una sola pasada vs múltiples

Cuando el problema "parece" requerir mirar "todo" para cada elemento, **piensa si te basta con un agregado** (min/max/sum/count) en lugar de la lista completa. Si sí, una pasada con tracking de ese agregado da O(n) en vez de O(n²).

### Conexión con Kadane's algorithm (LC 53)

Kadane (max subarray sum) es la **versión sumatoria** de este problema:
- En lugar de "min visto antes", lleva "suma máxima terminando aquí".
- En cada paso decides extender o reiniciar.

Mismo patrón, distinta cantidad rastreada.

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Fuerza bruta | O(n²) | O(1) | [NO] TLE |
| 2. **One-pass tracking del min** | **O(n)** | O(1) | [OK] La canónica |
| 3. Two pointers explícito | O(n) | O(1) | Funciona, menos limpia que la 2 |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** desde cero.
2. Justifica:
   - Por qué se actualiza `min_price` ANTES de calcular el profit del día actual.
   - Por qué inicializar `min_price = float('inf')` y no `prices[0]`.
   - Cuál es la complejidad temporal y espacial.
3. Trace mental con `prices = [2, 4, 1, 7]`. ¿En qué día se compraría y se vendería?
4. Trace mental con `prices = [7, 6, 4, 3, 1]`. ¿Por qué el resultado es 0?
5. **Bonus** — extiende el problema: en vez de un solo par, devolver el **par óptimo** (índices de compra y venta), no solo el beneficio.
6. **Bonus 2** — versión LC 122 (múltiples transacciones permitidas). Pista: cualquier subida cuenta.

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué no usas un sort?"** → Sort daría O(n log n) y perdería información de orden temporal (necesitas comprar ANTES de vender). El orden importa.
- **"¿Cómo lo extenderías a múltiples transacciones?"** → LC 122. Sumas todas las subidas consecutivas.
- **"¿Y si pudieras hacer 2 transacciones máximo?"** → LC 123. DP con estados (no comprado, comprado-1, vendido-1, comprado-2, vendido-2).
- **"¿Y si los precios pudieran ser negativos?"** → No cambia, el algoritmo funciona igual con `float('inf')` como inicialización.

---

## Solución en C++ — contraste con Python

> Añadido para ver las diferencias de lenguaje. Código compilable en [`121-best-time-to-buy-and-sell-stock.cpp`](121-best-time-to-buy-and-sell-stock.cpp).

```cpp
class Solution {
 public:
  int maxProfit(std::vector<int>& prices) {
    int min_price = INT_MAX;                  // Python: float('inf')
    int best = 0;
    for (int p : prices) {
      min_price = std::min(min_price, p);
      best = std::max(best, p - min_price);
    }
    return best;
  }
};
```

**Análisis:** Tiempo O(n), Espacio O(1) — igual que el Python idiomático.

**Diferencias clave Python ↔ C++:**
- `float('inf')` → `INT_MAX` de `<climits>` (aquí trabajas con `int`, no flotantes; usar infinito flotante mezclaría tipos).
- `min(a,b)` / `max(a,b)` builtins → `std::min` / `std::max` de `<algorithm>`.
- `for price in prices` → `for (int p : prices)` (range-for; sin `enumerate` porque no necesitas el índice).
- Sin diferencias de complejidad: el patrón "mínimo visto + mejor beneficio" es idéntico.

---

## Conexiones

- [[MOC_NeetCode_150]] — índice general.
- Patrón anterior: [[42-trapping-rain-water]] — también usa tracking de extremos pero por ambos lados.
- Próximo: [[3-longest-substring-without-repeating-characters]] — sliding window de tamaño variable real.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Justificada la inicialización con `float('inf')`
- [ ] Trace mental hecho
- [ ] Resuelto en LeetCode con éxito
- [ ] Hecho 1 vez más a la semana siguiente
