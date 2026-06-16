---
title: "LeetCode 739 — Daily Temperatures"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/stack, patron/stack-monotonica, patron/analisis-amortizado]
type: nota
status: en-progreso
source: claude-code
aliases: [Daily Temperatures, LC 739, dailyTemperatures, Días hasta temperatura mayor]
problem_id: 739
difficulty: medium
patron: stack
neetcode_order: 5
---

# LeetCode 739 — Daily Temperatures

> 🎯 **Quinto problema del patrón Stack** y la introducción canónica al **stack monotónico**, una estructura mental que reaparece en MUCHOS problemas (LC 84, LC 496, LC 84, LC 901). Si entendiste la deque monotónica de [[239-sliding-window-maximum]], esto es la versión "stack" del mismo concepto.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un array `temperatures` representando temperaturas diarias, devuelve un array `answer` donde `answer[i]` es el **número de días que tienes que esperar** para una temperatura **estrictamente más cálida**. Si tal día no existe, `answer[i] = 0`.

**Ejemplo 1:**
```
Input:  temperatures = [73, 74, 75, 71, 69, 72, 76, 73]
Output:                [ 1,  1,  4,  2,  1,  1,  0,  0]
```

Explicación de algunos:
- Día 0 (73°): día 1 ya hay 74° → espera 1 día.
- Día 2 (75°): días 3,4,5 no superan 75°. Día 6 hay 76° → espera 4 días.
- Día 6 (76°): nunca se supera → 0.
- Día 7 (73°): no hay nada después → 0.

**Ejemplo 2:**
```
Input:  [30, 40, 50, 60]
Output: [ 1,  1,  1, 0]
```

**Restricciones:**
- `1 <= temperatures.length <= 10^5`
- `30 <= temperatures[i] <= 100`

**Plantilla:**
```python
class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `List[int]` de longitud n |
| ¿Estrictamente mayor? | **Sí** — temperatura igual NO cuenta |
| ¿Qué pongo si no hay día más cálido? | `0` |
| ¿Resultado es **número de días** o **índice del día**? | Número de días = `j - i` (no índice absoluto) |
| Edge case 1 | Array decreciente (e.g. `[5,4,3,2,1]`) → todos 0 |
| Edge case 2 | Array creciente → todos 1 |

---

## Solución 1 — Fuerza bruta O(n²)

Para cada día, buscar hacia adelante el siguiente día más cálido.

```python
class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        n = len(temperatures)
        answer = [0] * n
        for i in range(n):
            for j in range(i + 1, n):
                if temperatures[j] > temperatures[i]:
                    answer[i] = j - i
                    break
        return answer
```

**Análisis:**
- **Tiempo: O(n²)** — TLE con n = 10^5 (10^10 operaciones).
- **Espacio: O(1)** extra (excluyendo output).
- **Veredicto:** ❌ TLE.

---

## Solución 2 — Stack monotónico decreciente (la canónica O(n))

**La idea brillante**: mantener un stack de **índices** cuyas temperaturas están en **orden decreciente** (de abajo hacia arriba en el stack). Cuando llega un día más cálido, sabemos que **todos los índices del stack con temperatura menor** han encontrado su "siguiente más cálido".

```python
class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        n = len(temperatures)
        answer = [0] * n
        stack = []                                          # guarda ÍNDICES

        for i, temp in enumerate(temperatures):
            while stack and temperatures[stack[-1]] < temp:
                prev_i = stack.pop()
                answer[prev_i] = i - prev_i                 # días esperados
            stack.append(i)

        return answer
```

**Trace mental con `[73, 74, 75, 71, 69, 72, 76, 73]`**:

```
Inicial: stack=[], answer=[0,0,0,0,0,0,0,0]

i=0, temp=73:
  stack vacío → no while
  push 0                    stack=[0]

i=1, temp=74:
  stack=[0], top temp=73 < 74 → pop 0
    answer[0] = 1 - 0 = 1   answer=[1,0,0,0,0,0,0,0]
  stack vacío → exit while
  push 1                    stack=[1]

i=2, temp=75:
  stack=[1], top temp=74 < 75 → pop 1
    answer[1] = 2 - 1 = 1   answer=[1,1,0,0,0,0,0,0]
  push 2                    stack=[2]

i=3, temp=71:
  stack=[2], top temp=75 ≥ 71 → no pop
  push 3                    stack=[2, 3]

i=4, temp=69:
  stack=[2,3], top temp=71 ≥ 69 → no pop
  push 4                    stack=[2, 3, 4]

i=5, temp=72:
  stack=[2,3,4], top temp=69 < 72 → pop 4
    answer[4] = 5 - 4 = 1   answer=[1,1,0,0,1,0,0,0]
  top temp=71 < 72 → pop 3
    answer[3] = 5 - 3 = 2   answer=[1,1,0,2,1,0,0,0]
  top temp=75 ≥ 72 → no pop
  push 5                    stack=[2, 5]

i=6, temp=76:
  pop 5: answer[5] = 6-5 = 1   answer=[1,1,0,2,1,1,0,0]
  pop 2: answer[2] = 6-2 = 4   answer=[1,1,4,2,1,1,0,0]
  push 6                    stack=[6]

i=7, temp=73:
  stack=[6], top temp=76 ≥ 73 → no pop
  push 7                    stack=[6, 7]

Final: stack=[6,7] (estos índices NUNCA encontraron mayor)
answer=[1, 1, 4, 2, 1, 1, 0, 0] ✅
```

**Análisis:**
- **Tiempo: O(n)** — análisis amortizado: cada índice entra y sale del stack **a lo sumo una vez**. Total ≤ 2n operaciones.
- **Espacio: O(n)** — el stack puede tener todos los índices en el peor caso (array decreciente).
- **Veredicto:** ✅ **la canónica**.

---

## El patrón general — "Stack monotónico decreciente / creciente"

**Cuándo aplicar**:

> Cuando el problema pide, para cada índice, **el siguiente (o anterior) elemento mayor (o menor)**. La fuerza bruta es O(n²); el stack monotónico es O(n).

**Plantilla mental** (siguiente mayor a la derecha):

```python
def next_greater(arr):
    n = len(arr)
    answer = [-1] * n                       # o 0, según convención
    stack = []                              # índices, monotónico decreciente
    for i, x in enumerate(arr):
        while stack and arr[stack[-1]] < x:
            j = stack.pop()
            answer[j] = i                   # o i - j si quieres distancia
        stack.append(i)
    return answer
```

**Variantes**:

| Buscas | Dirección de iteración | Stack es |
|---|---|---|
| Siguiente mayor a la derecha | left → right | decreciente |
| Siguiente menor a la derecha | left → right | creciente |
| Anterior mayor a la izquierda | right → left | decreciente |
| Anterior menor a la izquierda | right → left | creciente |

**Tres señales** del patrón:

1. Quieres **el siguiente (o anterior) elemento que cumple una propiedad** (mayor/menor).
2. La fuerza bruta es O(n²) y necesitas O(n).
3. Hay una idea de "candidatos pendientes" que se descartan cuando llega un mejor.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **496. Next Greater Element I** | Próximo mayor en otro array |
| **503. Next Greater Element II** | Array circular (módulo n) |
| **84. Largest Rectangle in Histogram** | Stack monotónico para áreas |
| **42. Trapping Rain Water** | Stack monotónico (alternativa al two pointers) |
| **901. Online Stock Span** | Stack monotónico en streaming |

---

## Conceptos a interiorizar

### Análisis amortizado (otra vez)

Mismo argumento que en [[125-valid-palindrome]], [[128-longest-consecutive-sequence]], [[3-longest-substring-without-repeating-characters]] y [[239-sliding-window-maximum]]. Cada elemento entra ≤ 1 vez al stack y sale ≤ 1 vez. **Total ≤ 2n operaciones**, aunque parezca O(n²) por los bucles anidados.

### Por qué guardar índices y no valores

Mismo motivo que en [[239-sliding-window-maximum]]: para calcular **distancias** o saber posiciones absolutas, necesitas índices. Si guardases solo valores, perderías la información de "cuánto tiempo lleva ahí".

### Stack monotónico vs Deque monotónica

| Estructura | Operaciones | Cuándo |
|---|---|---|
| **Stack monotónico** | append + pop (un extremo) | Próximo mayor / menor en un sentido |
| **Deque monotónica** | append + pop ambos extremos | Sliding window (ventana fija o variable) |

Stack es un caso especial de deque (sin la restricción de ventana).

---

## Comparación final de las 2 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Fuerza bruta | O(n²) | O(1) | ❌ TLE |
| 2. **Stack monotónico decreciente** | **O(n)** | O(n) | ✅ La canónica |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** desde cero.
2. Justifica:
   - Por qué guardamos índices, no valores.
   - Por qué `<` y no `<=` en el while (qué pasa con duplicados).
   - El argumento amortizado: ¿cuántas veces total puede ejecutarse el cuerpo del while?
3. Trace mental con `[5, 4, 3, 2, 1]`. ¿Resultado y por qué stack queda con todos los índices?
4. Trace mental con `[1, 2, 3, 4, 5]`. ¿Cómo evoluciona el stack?
5. **Bonus** — adapta para "siguiente menor a la derecha" (cambiar el `<` por `>`).
6. **Bonus 2** — adapta para "siguiente mayor a la izquierda" (iterar de derecha a izquierda).

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué O(n) si hay un while interno?"** → Análisis amortizado. Cada índice entra y sale del stack a lo sumo una vez.
- **"Diferencia entre stack monotónico y deque monotónica?"** → Stack: solo un extremo (LIFO). Deque: ambos extremos. Stack se usa para "siguiente X"; deque para sliding window.
- **"¿Y si quisieras `temperaturas iguales o mayores`?"** → Cambiar `<` por `<=` en el while. Cuidado con la lógica de duplicados.
- **"¿Cómo lo extenderías a streaming (online stock span)?"** → LC 901. El stack se mantiene a través de múltiples llamadas.

---

## Conexiones

- [[239-sliding-window-maximum]] — deque monotónica, primo cercano del stack monotónico.
- [[20-valid-parentheses]] — patrón base de stack.
- Próximo: [[853-car-fleet]] — stack con sort + ETAs.
- [[84-largest-rectangle-in-histogram]] — stack monotónico para áreas (Hard).

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Justificado el O(n) amortizado
- [ ] Trace mental con array decreciente y creciente
- [ ] Adaptado para "siguiente menor" (Bonus 1)
- [ ] Resuelto en LeetCode con éxito
