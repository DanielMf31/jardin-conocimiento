---
title: "LeetCode 155 — Min Stack"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/stack, patron/diseno-clase, patron/auxiliar-data-structure]
type: nota
status: en-progreso
source: claude-code
aliases: [Min Stack, LC 155, MinStack, Stack con mínimo]
problem_id: 155
difficulty: medium
patron: stack
neetcode_order: 2
---

# LeetCode 155 — Min Stack

> **Segundo problema del patrón Stack** — y el primer **problema de diseño** del NeetCode 150 (te piden implementar una clase, no una función). Introduce el truco de "stack auxiliar para mantener un agregado en O(1)" que reaparece en problemas más complejos.
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Diseña una clase `MinStack` que soporte las siguientes operaciones, **todas en O(1)**:

- `push(val)` — añade un valor al stack.
- `pop()` — quita el top del stack.
- `top()` — devuelve el top sin quitarlo.
- `getMin()` — devuelve el **mínimo** actual del stack.

**Ejemplo:**
```
MinStack minStack = new MinStack()
minStack.push(-2)
minStack.push(0)
minStack.push(-3)
minStack.getMin()    # -3
minStack.pop()
minStack.top()       # 0
minStack.getMin()    # -2
```

**Restricciones:**
- `-2^31 <= val <= 2^31 - 1`.
- Métodos `pop`, `top`, `getMin` solo se llaman cuando el stack **NO está vacío**.
- Hasta 3*10^4 llamadas en total.

**Plantilla:**
```python
class MinStack:
    def __init__(self):
        ...
    def push(self, val: int) -> None:
        ...
    def pop(self) -> None:
        ...
    def top(self) -> int:
        ...
    def getMin(self) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué hace difícil el `getMin()` en O(1)? | Si solo guardas el mínimo en una variable, al hacer `pop()` puede que ese mínimo desaparezca → necesitas saber el "siguiente mínimo" |
| ¿`pop()` puede dejar el stack vacío? | Sí, pero `getMin/top/pop` no se llaman si está vacío |
| ¿Hay duplicados? | Sí pueden existir (cuidado al gestionar el min stack) |
| ¿Valores negativos? | Sí (rango int32) |

> **El reto**: cuando haces `pop()`, **si el valor que sales era el mínimo**, ¿cuál es el nuevo mínimo? Recorrer el stack para encontrarlo sería O(n). Necesitas mantener historia del mínimo.

---

## Solución 1 — Dos stacks (la canónica)

**La idea**: un stack principal `stack` con todos los valores, y un stack auxiliar `min_stack` que mantiene **el mínimo actual** en cada posición.

- En `push(val)`: push a stack siempre. Push a min_stack `min(val, min_stack[-1])` (o `val` si está vacío).
- En `pop()`: pop ambos.
- En `getMin()`: devolver `min_stack[-1]`.

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []                      # paralelo: min en cada altura

    def push(self, val: int) -> None:
        self.stack.append(val)
        if not self.min_stack:
            self.min_stack.append(val)
        else:
            self.min_stack.append(min(val, self.min_stack[-1]))

    def pop(self) -> None:
        self.stack.pop()
        self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]
```

**Trace mental** (push -2, 0, -3, getMin, pop, top, getMin):

```
Estado inicial: stack=[], min_stack=[]

push(-2):
  stack = [-2]
  min_stack = [-2]    (vacío antes → push val tal cual)

push(0):
  stack = [-2, 0]
  min_stack = [-2, -2]   (min(0, -2) = -2)

push(-3):
  stack = [-2, 0, -3]
  min_stack = [-2, -2, -3]   (min(-3, -2) = -3)

getMin() → min_stack[-1] = -3 [OK]

pop():
  stack = [-2, 0]
  min_stack = [-2, -2]

top() → stack[-1] = 0 [OK]

getMin() → min_stack[-1] = -2 [OK]
```

**Análisis:**
- **Tiempo: O(1)** todas las operaciones.
- **Espacio: O(n)** — dos stacks de tamaño n.
- **Veredicto:** [OK] **la canónica de entrevista**. Limpia y fácil de explicar.

---

## Solución 2 — Stack de tuplas `(val, current_min)`

Misma idea pero con un solo stack que guarda tuplas.

```python
class MinStack:
    def __init__(self):
        self.stack = []                          # cada elemento: (val, current_min)

    def push(self, val: int) -> None:
        current_min = val if not self.stack else min(val, self.stack[-1][1])
        self.stack.append((val, current_min))

    def pop(self) -> None:
        self.stack.pop()

    def top(self) -> int:
        return self.stack[-1][0]

    def getMin(self) -> int:
        return self.stack[-1][1]
```

**Veredicto:** [OK] funcionalmente equivalente, ligeramente más memoria (overhead de tupla) pero más compacta de código. Es cuestión de gusto.

---

## Solución 3 — Min stack "comprimido" (la optimización)

**Observación**: si el nuevo `val` es **mayor** que el min actual, no necesitamos guardarlo en min_stack (no aporta info). Solo guardamos en min_stack cuando `val <= min_actual`.

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self) -> None:
        val = self.stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]
```

**Análisis:**
- **Tiempo: O(1)**.
- **Espacio: O(n)** peor caso, **O(k)** donde k = número de "nuevos mínimos" vistos. En la práctica suele ser mucho menos que n.
- **Veredicto:** [OK] optimización elegante. **Cuidado con el `<=`**: si solo usas `<`, los duplicados del mínimo desaparecen del min_stack y luego al hacer pop te quedas sin min correcto.

> **Trampa con `<` vs `<=`**: imagina push(1), push(1). Con `<`: min_stack = [1]. Pop → min_stack = []. ¡Pero el stack principal aún tiene un 1! Con `<=`: min_stack = [1, 1]. Pop → min_stack = [1] correcto.

---

## El patrón general — "Stack auxiliar para mantener agregado en O(1)"

**Cuándo aplicar**:

> Cuando una clase de tipo stack/queue necesita devolver un **agregado** (min, max, suma, mediana, etc.) en O(1), pero el agregado puede cambiar al hacer pop.

**Plantilla mental**:

```python
class StructConAgregado:
    def __init__(self):
        self.main = []
        self.aux = []                            # mantiene el agregado actual
    def push(self, val):
        self.main.append(val)
        new_agg = combinar(val, self.aux[-1] if self.aux else val)
        self.aux.append(new_agg)
    def pop(self):
        self.main.pop()
        self.aux.pop()
    def get_agg(self):
        return self.aux[-1]
```

**Tres señales** del patrón:

1. La clase debe responder a una pregunta de **agregado** (min/max/...) en O(1).
2. El agregado puede cambiar con cada pop, así que necesitas "historia".
3. Una variable única no basta — necesitas un stack paralelo.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **716. Max Stack** | Mismo pero con max + `popMax()` adicional |
| **232. Implement Queue using Stacks** | Diseño de queue con dos stacks |
| **225. Implement Stack using Queues** | Inverso del 232 |
| **295. Find Median from Data Stream** | Dos heaps para mediana en O(log n) |

---

## Conceptos a interiorizar

### Cuándo conviene cada solución

| Solución | Memoria | Claridad | Cuándo usar |
|---|---|---|---|
| 1. Dos stacks paralelos | O(n) + O(n) | | Por defecto; la más fácil de explicar |
| 2. Stack de tuplas | O(n) con overhead | | Si te gustan datos compactados |
| 3. Min stack comprimido | O(k) ≤ O(n) | | Si te preguntan optimización de espacio |

### Diseño de clase en Python

LeetCode te da la plantilla con `def __init__(self):`. Recuerda que `self.x` declara atributos accesibles en otros métodos:

```python
class MyClass:
    def __init__(self):
        self.atributo = []         # accesible en otros métodos como self.atributo
    def metodo(self):
        self.atributo.append(1)    # OK
```

### `not self.min_stack` para chequear vacío

Igual que en [[20-valid-parentheses]], el chequeo idiomático.

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. **Dos stacks paralelos** | O(1) | O(n) | [OK] La canónica |
| 2. Stack de tuplas | O(1) | O(n) + overhead | [OK] Compacta |
| 3. Min stack comprimido | O(1) | O(k) ≤ O(n) | [OK] La óptima en espacio |

---

## Auto-test (para ti, sin mirar el archivo)

1. Implementa la **Solución 1** desde cero.
2. Justifica:
   - Por qué necesitas un stack auxiliar y no una variable única.
   - Por qué `min(val, min_stack[-1])` y no comparar contra el min global.
   - Cuál es la complejidad espacial.
3. Implementa la **Solución 3** (comprimida). Justifica el `<=` en lugar de `<`.
4. Trace mental con la secuencia: push(2), push(0), push(3), push(0), getMin, pop, getMin, pop, getMin.
5. **Bonus** — extiéndelo a `MaxStack` (con max en O(1)).

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué no una variable `current_min` única?"** → Si haces pop del valor que era el mínimo, no sabes cuál es el siguiente sin recorrer el stack (O(n)).
- **"¿Cuándo conviene la Solución 3 vs la 1?"** → Si los duplicados del mínimo son raros, la 3 ahorra mucho espacio. Si son frecuentes, ambas son O(n).
- **"¿Y si quisieras `getMedian()` en O(1)?"** → No es posible con stacks simples. Necesitas dos heaps (LC 295) o estructura más compleja.
- **"¿Cómo lo extenderías a thread-safe?"** → Locks en cada método. Trade-off de performance.

---

## Conexiones

- [[20-valid-parentheses]] — primer encuentro con stack.
- [[347-top-k-frequent-elements]] — primera estructura auxiliar (heap), idea similar.
- Próximo: [[150-evaluate-reverse-polish-notation]] — stack para evaluar expresiones.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Implementada Solución 1 desde cero
- [ ] Implementada Solución 3 con `<=` correcto
- [ ] Justificada por qué variable única no basta
- [ ] Resuelto en LeetCode con éxito
