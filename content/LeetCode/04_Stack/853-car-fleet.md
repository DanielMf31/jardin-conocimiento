---
title: "LeetCode 853 — Car Fleet"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/stack, patron/sort-then-process]
type: nota
status: en-progreso
source: claude-code
aliases: [Car Fleet, LC 853, carFleet, Flota de coches]
problem_id: 853
difficulty: medium
patron: stack
neetcode_order: 6
---

# LeetCode 853 — Car Fleet

> 🎯 **Sexto problema del patrón Stack**. Aplica el truco de **sort + procesar en orden** combinado con stack. La clave conceptual está en el modelo físico del problema: cuando un coche más rápido alcanza a uno más lento, **se ralentiza al mismo paso** y forman una "flota". Es un problema más matemático que algorítmico.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Hay `n` coches en una carretera de un solo carril yendo al destino `target` (millas).

`position[i]` es la posición inicial del coche `i` y `speed[i]` es su velocidad. Los coches no pueden adelantarse: si un coche más rápido alcanza a uno más lento, **se ralentiza al ritmo del lento**, formando una **flota**.

Una flota es uno o más coches que viajan juntos a la misma posición y velocidad. Un coche solo también es una flota de tamaño 1.

Si un coche **alcanza al destino exactamente al mismo instante** que otro, también forman una flota.

Devuelve el **número de flotas** que llegarán al destino.

**Ejemplo 1:**
```
Input:  target = 12, position = [10, 8, 0, 5, 3], speed = [2, 4, 1, 1, 3]
Output: 3

Explicación:
  Coche en pos=10 (vel=2): llega a target en (12-10)/2 = 1 hora
  Coche en pos=8 (vel=4):  llega en (12-8)/4 = 1 hora → mismo instante → fleet
  Coche en pos=0 (vel=1):  llega en (12-0)/1 = 12 horas
  Coche en pos=5 (vel=1):  llega en (12-5)/1 = 7 horas
  Coche en pos=3 (vel=3):  llega en (12-3)/3 = 3 horas

  Procesando de más adelante a más atrás:
    pos=10: ETA 1 → fleet 1
    pos=8:  ETA 1 → mismo que pos=10 → mismo fleet
    pos=5:  ETA 7 → llega después → nuevo fleet 2
    pos=3:  ETA 3 → llega antes que pos=5, lo alcanza → mismo fleet 2
    pos=0:  ETA 12 → llega después → nuevo fleet 3

  Total: 3 flotas
```

**Restricciones:**
- `n == position.length == speed.length`
- `1 <= n <= 10^5`
- `0 < target <= 10^6`
- `0 <= position[i] < target`
- Todas las posiciones son **únicas**.
- `0 < speed[i] <= 10^6`.

**Plantilla:**
```python
class Solution:
    def carFleet(self, target: int, position: List[int], speed: List[int]) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` — número de flotas |
| ¿Cómo calculo cuándo llega un coche? | ETA = `(target - position) / speed` |
| ¿Cuándo dos coches forman flota? | Cuando el de **atrás** alcanza al de **delante**. Esto pasa si su ETA es **menor o igual** |
| ¿Por qué procesar de delante a atrás? | El coche más adelantado dicta el ritmo. Si el de atrás llega antes, lo alcanza |
| ¿Importa el orden del input? | NO — hay que ordenarlos por posición |

> 💡 **El insight clave**: en lugar de simular físicamente, calcular **el tiempo que cada coche tardaría en llegar al destino sin obstáculos** (ETA). Procesar de adelante a atrás (mayor a menor posición). Si el coche actual tiene ETA ≤ el coche de delante, **lo alcanza** y forma la misma flota.

---

## Solución 1 — Sort + iterar con tracking de "ETA del fleet actual"

**La idea**: ordenar coches por posición descendente (los más adelantados primero). Calcular ETA de cada uno. Si la ETA del actual es **mayor** que la del fleet actual, es un nuevo fleet (no alcanza al de delante). Si es menor o igual, se une al fleet existente.

```python
class Solution:
    def carFleet(self, target: int, position: List[int], speed: List[int]) -> int:
        # Combinar posiciones y velocidades, ordenar por posición descendente
        cars = sorted(zip(position, speed), reverse=True)

        fleets = 0
        current_fleet_eta = 0                        # ETA del fleet "delantero"

        for pos, spd in cars:
            eta = (target - pos) / spd
            if eta > current_fleet_eta:
                fleets += 1
                current_fleet_eta = eta
            # else: lo alcanza → mismo fleet, no actualizar ETA

        return fleets
```

**Trace mental con `target=12, position=[10,8,0,5,3], speed=[2,4,1,1,3]`**:

```
sorted(zip(pos, spd), reverse=True):
  [(10, 2), (8, 4), (5, 1), (3, 3), (0, 1)]

Inicial: fleets=0, current_fleet_eta=0

(10, 2): eta = (12-10)/2 = 1.0
  1.0 > 0 → nuevo fleet
  fleets=1, current_fleet_eta=1.0

(8, 4): eta = (12-8)/4 = 1.0
  1.0 > 1.0? NO (igual) → mismo fleet
  fleets=1, current_fleet_eta=1.0

(5, 1): eta = (12-5)/1 = 7.0
  7.0 > 1.0 → nuevo fleet
  fleets=2, current_fleet_eta=7.0

(3, 3): eta = (12-3)/3 = 3.0
  3.0 > 7.0? NO → mismo fleet (lo alcanza)
  fleets=2, current_fleet_eta=7.0

(0, 1): eta = (12-0)/1 = 12.0
  12.0 > 7.0 → nuevo fleet
  fleets=3, current_fleet_eta=12.0

Return 3 ✅
```

**Análisis:**
- **Tiempo: O(n log n)** — sort domina.
- **Espacio: O(n)** — el zip + sort.
- **Veredicto:** ✅ **la canónica**. Limpia y eficiente.

---

## Solución 2 — Versión con stack explícito (más visual)

Misma lógica pero con un stack de ETAs. El stack mantiene las ETAs de los fleets actuales en orden creciente. Si un nuevo coche tiene ETA ≤ top del stack, se une (no se hace push). Si es mayor, push.

```python
class Solution:
    def carFleet(self, target: int, position: List[int], speed: List[int]) -> int:
        cars = sorted(zip(position, speed), reverse=True)
        stack = []
        for pos, spd in cars:
            eta = (target - pos) / spd
            if not stack or eta > stack[-1]:
                stack.append(eta)
            # si eta <= stack[-1], se fusiona con el fleet actual (no push)
        return len(stack)
```

**Análisis:** mismo O(n log n).

**Veredicto:** ✅ funcionalmente equivalente. Más explícita en el patrón "stack". Es la que NeetCode usa en su explicación.

> 💡 **El stack guarda los "líderes" de cada fleet**. Su tamaño al final es el número de fleets.

---

## El patrón general — "Sort + iterar con tracking"

**Cuándo aplicar**:

> Cuando el problema involucra elementos en una línea (1D) con interacciones direccionales (uno alcanza a otro, uno bloquea a otro) y la solución requiere **procesar en orden espacial** con tracking del estado del "frente".

**Plantilla mental**:

```python
def patron_sort_track(elementos):
    elementos.sort(key=funcion_orden, reverse=True)    # delante a atrás
    state = inicial
    count = 0
    for elem in elementos:
        valor = calcular(elem)
        if valor cumple_condicion(state):
            count += 1
            state = actualizar(state, valor)
        # else: se "fusiona" con el actual
    return count
```

**Tres señales** del patrón:

1. Elementos con posiciones espaciales y propiedades dinámicas.
2. La fuerza bruta (simulación) sería compleja o lenta.
3. Sort + procesamiento lineal con un tracker simple basta.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **1776. Car Fleet II** | Tiempos exactos de colisión (no solo "alcanza al final") |
| **1834. Single-Threaded CPU** | Tasks con tiempos de llegada y duración → priority queue |
| **207. Course Schedule** | Sort topológico (otro tipo de "orden" en grafos) |

---

## Conceptos a interiorizar

### `sorted(zip(a, b), reverse=True)` — patrón pythonic

```python
position = [10, 8, 0, 5, 3]
speed = [2, 4, 1, 1, 3]

zip(position, speed)               # [(10,2), (8,4), (0,1), (5,1), (3,3)]
sorted(zip(position, speed))       # [(0,1), (3,3), (5,1), (8,4), (10,2)] — ascendente
sorted(zip(position, speed), reverse=True)
                                   # [(10,2), (8,4), (5,1), (3,3), (0,1)]
```

`sorted` ordena tuplas por su primera componente, luego segunda, etc. Para ordenar por la segunda, usar `key=lambda x: x[1]`.

### División flotante vs entera

```python
12 / 5             # 2.4    (float division)
12 // 5            # 2      (integer floor division)
```

**En este problema usamos `/`** porque las ETAs pueden no ser enteras y la comparación necesita precisión.

### Por qué tracking simple basta (no se necesita doble bucle)

La pregunta es: si el coche `i+1` se fusiona con `i`, ¿qué pasa si el coche `i+2` quiere fusionarse con `i+1`? Como `i+1` se fusionó con `i`, su ETA real es la de `i` (más lenta). Para fusionarse con eso, basta comparar `eta_{i+2}` con `eta_i`.

Por eso **`current_fleet_eta` solo se actualiza cuando hay un nuevo fleet** — y eso captura la ETA real del fleet de delante.

---

## Comparación final de las 2 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. **Sort + tracking de ETA** | **O(n log n)** | O(n) | ✅ La directa |
| 2. **Sort + stack explícito** | **O(n log n)** | O(n) | ✅ Más visual del patrón |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** (con stack) desde cero.
2. Justifica:
   - Por qué `reverse=True` (orden descendente por posición).
   - Por qué `>` (estricto) y no `>=` en la condición.
   - Por qué `current_fleet_eta` no se actualiza cuando hay fusión.
3. Trace mental con `position=[0,2,4], speed=[4,2,1], target=10`. Identifica las flotas.
4. Trace mental con `position=[3], speed=[3], target=10`. ¿Qué devuelve?
5. **Bonus** — extiende para devolver no solo el número de flotas sino la lista de flotas (cada una con sus coches).

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué procesar de adelante a atrás?"** → Porque el coche más adelantado dicta la velocidad del fleet. Procesar al revés requeriría saber cosas del futuro.
- **"¿Y si los coches pudieran adelantarse?"** → Cambia el problema completamente. La solución actual asume "no overtaking" (un coche atrás se ralentiza al alcanzar uno delante).
- **"¿Y si las posiciones pudieran repetirse?"** → El enunciado garantiza posiciones únicas. Si pudieran repetirse, hay que decidir el comportamiento (probablemente forman fleet inmediato).
- **"¿Por qué O(n log n) y no O(n)?"** → El sort es el cuello de botella. La fase de procesamiento es O(n).

---

## Conexiones

- [[20-valid-parentheses]] · [[155-min-stack]] · [[150-evaluate-reverse-polish-notation]] · [[22-generate-parentheses]] · [[739-daily-temperatures]] — patrón Stack.
- [[15-3sum]] — sort + procesar (en otro patrón).
- Próximo: [[84-largest-rectangle-in-histogram]] — el Hard del patrón.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 (con stack) desde cero
- [ ] Justificado por qué procesar de adelante a atrás
- [ ] Trace mental hecho
- [ ] Resuelto en LeetCode con éxito
