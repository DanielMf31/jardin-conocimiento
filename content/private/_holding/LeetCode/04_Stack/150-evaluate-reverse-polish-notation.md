---
title: "LeetCode 150 — Evaluate Reverse Polish Notation"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/stack, patron/evaluacion-expresiones]
type: nota
status: en-progreso
source: claude-code
aliases: [Evaluate RPN, LC 150, evalRPN, Notación polaca inversa]
problem_id: 150
difficulty: medium
patron: stack
neetcode_order: 3
---

# LeetCode 150 — Evaluate Reverse Polish Notation

> **Tercer problema del patrón Stack** — la aplicación clásica para **evaluar expresiones aritméticas**. RPN (Reverse Polish Notation) es el formato natural de los stacks: cada operador consume los **dos elementos más recientes**, perfectamente LIFO.
> Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Te dan un array de strings `tokens` que representa una expresión aritmética en **Reverse Polish Notation** (notación polaca inversa).

Evalúa la expresión y devuelve un entero que representa su valor.

**Las operaciones permitidas son** `+`, `-`, `*`, `/`. La división entre enteros **trunca hacia cero** (no hacia menos infinito).

**Ejemplo 1:**
```
Input:  tokens = ["2", "1", "+", "3", "*"]
Output: 9
        Equivale a (2 + 1) * 3 = 9
```

**Ejemplo 2:**
```
Input:  tokens = ["4", "13", "5", "/", "+"]
Output: 6
        Equivale a 4 + (13 / 5) = 4 + 2 = 6
```

**Ejemplo 3:**
```
Input:  tokens = ["10","6","9","3","+","-11","*","/","*","17","+","5","+"]
Output: 22
        Expresión convencional: ((10 * (6 / ((9+3) * -11))) + 17) + 5
```

**Restricciones:**
- `1 <= tokens.length <= 10^4`
- `tokens[i]` es un operador `+ - * /` o un entero (puede ser negativo, hasta 32 bits).
- La expresión es siempre **válida**.

**Plantilla:**
```python
class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `int` |
| ¿Qué es RPN? | Notación donde el operador va **DESPUÉS** de sus operandos: `2 1 +` = `2 + 1` |
| ¿Por qué stack es natural? | Cada operador consume los 2 valores más recientes (LIFO) |
| ¿División entera trunca cómo? | **Hacia cero** (no hacia abajo). `-7 // 2 = -4` (truncar hacia abajo) ≠ `int(-7 / 2) = -3` (truncar hacia cero) |
| ¿Operandos negativos? | Sí, llegan como string `"-11"`. `int("-11")` funciona |
| ¿Orden de operandos? | El primero pop es el **derecho**, el segundo es el **izquierdo** |

> **La trampa más común**: la división. En Python, `//` redondea hacia menos infinito. Para "truncar hacia cero" hay que usar `int(a / b)` o `int(a/b)`.

---

## Entender RPN antes de codear (sección de fondo)

> **Si la notación misma te resulta liosa, lee esto antes de las soluciones**. Una vez entiendes RPN como notación, el algoritmo se cae solo.

### De dónde viene RPN y por qué existe

- **Notación polaca** (Jan Łukasiewicz, lógico polaco, 1924): operador **ANTES** de operandos: `+ 2 1` en vez de `2 + 1`.
- **Reverse Polish Notation** (Burks, Warren, Wright, 1954): operador **DESPUÉS** de operandos: `2 1 +`. Inventada específicamente para que se pueda evaluar **con un stack en una sola pasada**.
- Las **calculadoras HP** (HP-35 en 1972, HP-12C que aún se vende) la usan nativamente. Los ingenieros senior la prefieren porque no hay paréntesis que recordar.

**¿Por qué se inventó?** La notación normal (infija, `2 + 1`) tiene dos problemas serios para una máquina:

1. **Necesita paréntesis** para resolver ambigüedades de precedencia: `2 + 3 * 4` puede ser `(2+3)*4=20` o `2+(3*4)=14`.
2. **No se evalúa de izquierda a derecha sin lookahead**: cuando ves el `+`, no puedes ejecutarlo todavía porque puede venir un `*` después.

RPN elimina los dos:
- **Nunca necesita paréntesis** — el orden de tokens YA codifica la precedencia.
- **Se evalúa en una sola pasada izquierda-a-derecha**, con un stack, sin lookahead.

### La regla de oro de RPN

> **Cada operador actúa sobre los DOS números inmediatamente anteriores en el orden de lectura.** Esos dos números desaparecen y son reemplazados por el resultado.

Ejemplo:

```
2 1 +
^ ^ ^
| | └── operador: actúa sobre los 2 anteriores → 2 + 1 = 3
| └──── número
└────── número
```

Después de aplicar `+`, los tres tokens `2 1 +` se convierten en **un solo valor: `3`**. Ese 3 puede ser usado por el siguiente operador.

Otro ejemplo más largo:

```
2 1 + 3 *

Lectura mental:
  "2"  → guardo el 2.
  "1"  → guardo el 1.
  "+"  → cojo los DOS últimos (2 y 1), hago 2+1=3. Reemplazo → tengo "3".
  "3"  → guardo el 3 (ahora tengo 3 y 3).
  "*"  → cojo los DOS últimos (3 y 3), hago 3*3=9. Reemplazo → tengo "9".
```

Resultado: 9, equivalente a `(2+1) * 3`.

### Por qué un stack es la única estructura posible

La regla "los DOS números inmediatamente anteriores" significa: **los dos últimos que aún no han sido consumidos**. Eso es exactamente lo que hace un stack — te da el último en entrar (LIFO).

**Analogía física**: pila de platos.

```
Cada NÚMERO   → pones un plato encima de la pila
Cada OPERADOR → coges los 2 platos de arriba, los combinas en uno
                (con la operación), y lo pones encima
```

Es físicamente imposible saltarse el orden. **Esa restricción física es lo que RPN aprovecha**: los operadores siempre se aplican a los dos últimos valores generados.

### RPN como recorrido postorder de un árbol (la intuición que lo aclara TODO)

Toda expresión aritmética se puede dibujar como **árbol binario**. Por ejemplo, `(2 + 1) * 3`:

```
        *
       / \
      +   3
     / \
    2   1
```

Hay tres formas de recorrer este árbol:

| Recorrido | Orden | Resultado | Notación |
|---|---|---|---|
| **Preorder** (raíz, izq, der) | * + 2 1 3 | `* + 2 1 3` | Polaca (prefija) |
| **Inorder** (izq, raíz, der) | 2 + 1 * 3 | `2 + 1 * 3` | Infija (la normal) |
| **Postorder** (izq, der, raíz) | 2 1 + 3 * | `2 1 + 3 *` | **RPN (postfija)** |

**RPN ES literalmente un postorder traversal de un árbol de expresión**. Por eso siempre evalúa los operandos antes de aplicar el operador — propiedad estructural del postorder.

Esta intuición de árbol te ayuda con cualquier expresión RPN larga: en tu cabeza estás reconstruyendo el árbol de abajo hacia arriba.

### Conversión mental infija → RPN

Para entender RPN, sirve poder traducir mentalmente. La regla:

> **Cada operador se mueve a la posición donde estaría su `=` si calcularas esa subexpresión.**

Ejemplo: `(2 + 1) * 3`
- `(2 + 1)` primero: el `+` va al final → `2 1 +`
- Eso es ahora "un valor". Luego `* 3`: el `*` va al final → `[2 1 +] 3 *`
- RPN: `2 1 + 3 *`

Ejemplo: `4 + 13 / 5`
- `13 / 5` primero (precedencia mayor): `13 5 /`
- Eso es "un valor". Luego `4 +`: el `+` va al final → `4 [13 5 /] +`
- RPN: `4 13 5 / +`

### Trace COMPLETO del ejemplo difícil (13 tokens, resultado 22)

Este es el del enunciado que probablemente más lía:

```
tokens = ["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]
expected = 22
```

Paso a paso, con el stack en cada momento (el frente está a la derecha):

```
estado inicial: stack = []

token "10"  → push 10              stack = [10]
token "6"   → push 6               stack = [10, 6]
token "9"   → push 9               stack = [10, 6, 9]
token "3"   → push 3               stack = [10, 6, 9, 3]

token "+"   → pop b=3, pop a=9     stack = [10, 6]
              push (9 + 3) = 12    stack = [10, 6, 12]

token "-11" → push -11             stack = [10, 6, 12, -11]
               "-11" es número, NO operador.
                 Por eso el código usa len(token)==1 para distinguir.

token "*"   → pop b=-11, pop a=12  stack = [10, 6]
              push (12 * -11) = -132   stack = [10, 6, -132]

token "/"   → pop b=-132, pop a=6  stack = [10]
              push int(6 / -132) = 0   stack = [10, 0]
               aquí entra la trampa de la división:
                 6 / -132 = -0.0454...
                 int(-0.0454) = 0   (truncar hacia cero )
                 6 // -132        = -1 (truncar hacia menos inf )

token "*"   → pop b=0, pop a=10    stack = []
              push (10 * 0) = 0    stack = [0]

token "17"  → push 17              stack = [0, 17]

token "+"   → pop b=17, pop a=0    stack = []
              push (0 + 17) = 17   stack = [17]

token "5"   → push 5               stack = [17, 5]

token "+"   → pop b=5, pop a=17    stack = []
              push (17 + 5) = 22   stack = [22]

final: stack[0] = 22 [OK]
```

**Reconstruyendo el árbol** que esto representa:

```
                    +
                   / \
                  +   5
                 / \
                *   17
               / \
              10  /
                 / \
                6   *
                   / \
                  +   -11
                 / \
                9   3
```

Lectura: `((10 * (6 / ((9+3) * -11))) + 17) + 5` = `((10 * (6 / (12 * -11))) + 17) + 5` = `((10 * (6/-132)) + 17) + 5` = `((10 * 0) + 17) + 5` = `(0 + 17) + 5` = `22`.

### La trampa del orden de operandos — explicada

```python
b = stack.pop()       # PRIMERO
a = stack.pop()       # DESPUÉS
stack.append(a OP b)  # NOTA: a a la izquierda, b a la derecha
```

**¿Por qué `b` primero?** Porque al apilar, el **último número apilado** corresponde al **operando derecho** de la operación.

Pensemos en `5 - 3`:
- En infija: `5` izquierdo (a), `3` derecho (b). Resultado: `5 - 3 = 2`.
- En RPN: `5 3 -`. Apilas 5, luego apilas 3. Stack: `[5, 3]`.
- Cuando llega `-`, el **top** del stack es `3` (último apilado) → operando **derecho**.
- `pop()` saca `3` primero → `b` (derecho).
- `pop()` saca `5` después → `a` (izquierdo).
- Aplicas `a - b` = `5 - 3 = 2`.

**Si lo hicieras al revés** (`b - a`), `3 - 5 = -2`. Mal.

Para `+` y `*` da igual (conmutativos), pero para `-` y `/` el orden te jode el resultado.

```
Regla mental fija:
   último apilado = operando derecho = primer pop = b
```

### Resumen mental para no liarte nunca más

Cuando veas RPN, piensa así en orden:

1. **"Es un postorder traversal de un árbol de expresión"** → reconstruyo el árbol de abajo hacia arriba.
2. **"Recorro tokens de izquierda a derecha"** → cada número va a una pila mental.
3. **"Cada operador come los DOS últimos números y los reemplaza con su resultado."**
4. **"Al hacer pop: primero el derecho, luego el izquierdo. Aplicar `a OP b`, no `b OP a`."**
5. **"División: `int(a / b)`, NUNCA `a // b`."** Truncar hacia cero, no hacia menos infinito.

Si estos 5 puntos están sólidos, RPN es **mecánico**, sin sorpresas.

---

## Solución 1 — Stack con dispatch por operador (la canónica)

**La idea**: recorrer tokens. Si es número, push. Si es operador, pop dos veces (b primero, a después), aplicar operación, push resultado.

```python
class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        stack = []
        for token in tokens:
            if token in "+-*/" and len(token) == 1:    # operador
                b = stack.pop()                         # ⚠️ derecho primero
                a = stack.pop()                         # izquierdo después
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                else:
                    stack.append(int(a / b))            # ⚠️ truncar hacia cero
            else:                                       # número
                stack.append(int(token))
        return stack[0]
```

> **`len(token) == 1`** evita confundir `"-11"` (entero negativo, longitud 3) con el operador `"-"` (longitud 1).

**Trace mental con `["2", "1", "+", "3", "*"]`**:

```
Estado inicial: stack = []

token="2" (número) → push 2          stack = [2]
token="1" (número) → push 1          stack = [2, 1]
token="+" (operador):
       b = 1, a = 2
       push (2 + 1) = 3              stack = [3]
token="3" (número) → push 3          stack = [3, 3]
token="*" (operador):
       b = 3, a = 3
       push (3 * 3) = 9              stack = [9]

Final: stack[0] = 9 [OK]
```

**Análisis:**
- **Tiempo: O(n)** — un recorrido lineal.
- **Espacio: O(n)** — el stack puede tener hasta n/2 + 1 elementos.
- **Veredicto:** [OK] **la canónica**.

---

## Solución 2 — Stack con dict de funciones (más pythonic)

Usar un dict que mapea operador → función para evitar el if encadenado.

```python
import operator

class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': lambda a, b: int(a / b),       # truncar hacia cero
        }
        stack = []
        for token in tokens:
            if token in ops:
                b, a = stack.pop(), stack.pop()
                stack.append(ops[token](a, b))
            else:
                stack.append(int(token))
        return stack[0]
```

**Análisis:** mismo O(n). **Más elegante**, demuestra que conoces `operator` y lambdas. Buena impresión en entrevista.

---

## Sobre la trampa de la división

```python
# Truncar hacia ABAJO (Python por defecto)
-7 // 2          # -4

# Truncar hacia CERO (lo que pide el problema)
int(-7 / 2)      # -3
math.trunc(-7 / 2)  # -3 (equivalente)
```

**Diferencia con números positivos**: ninguna. `7 // 2 = 3`, `int(7/2) = 3`.

**Con negativos**: `-7 // 2 = -4` (más bajo), `int(-7/2) = -3` (hacia cero).

LeetCode espera **hacia cero**, así que **siempre `int(a / b)` para este problema**.

---

## El patrón general — "Stack para evaluación de expresiones"

**Cuándo aplicar**:

> Cuando el problema involucra **evaluar / parsear** una expresión donde los operadores actúan sobre los **operandos más recientes**. RPN es el caso natural; expresiones infijas también pero requieren conversión previa (Shunting Yard).

**Plantilla mental**:

```python
def eval_rpn(tokens):
    stack = []
    for token in tokens:
        if es_operador(token):
            b = stack.pop()
            a = stack.pop()
            stack.append(aplicar(token, a, b))
        else:
            stack.append(parse_operando(token))
    return stack[0]
```

**Tres señales** del patrón:

1. La expresión está en formato post-fijo (RPN) o se parsea token a token.
2. Cada operador consume un número fijo de operandos previos.
3. La salida es el último valor en el stack.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **224. Basic Calculator** | Expresión infija con `+ -` y paréntesis |
| **227. Basic Calculator II** | Expresión infija con `+ - * /` (precedencia) |
| **772. Basic Calculator III** | Combinación con paréntesis (Hard) |
| **394. Decode String** | Decodificación con stack (similar pero strings) |

> **Las variantes con expresiones infijas son mucho más complicadas** porque requieren manejar precedencia. La RPN ya tiene la precedencia "incorporada" en el orden de tokens.

---

## Conceptos a interiorizar

### `int(a / b)` vs `a // b`

```python
int(7 / 2)        # 3
7 // 2            # 3                       (iguales con positivos)

int(-7 / 2)       # -3                      (truncar hacia cero)
-7 // 2           # -4                      (truncar hacia menos infinito)
```

**LeetCode RPN espera "hacia cero"** → usa `int(a / b)`.

### `operator` module

```python
import operator
operator.add(2, 3)            # 5  (equivale a 2 + 3)
operator.sub(5, 2)            # 3
operator.mul(2, 3)            # 6
operator.truediv(7, 2)        # 3.5
operator.floordiv(7, 2)       # 3
```

Útil cuando quieres pasar operaciones como first-class functions (e.g. en map, filter, reduce, dicts de operadores).

### Pop dos veces: el orden importa

```python
b = stack.pop()       # ← el derecho (último insertado)
a = stack.pop()       # ← el izquierdo (penúltimo)
result = a OP b       # ⚠️ NO b OP a
```

Para `+` y `*` es conmutativo y da igual. Para `-` y `/` el orden importa.

---

## Comparación final de las 2 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. **Stack con if encadenados** | **O(n)** | O(n) | [OK] La directa |
| 2. **Stack con dict de funciones** | **O(n)** | O(n) | [OK] Más pythonic |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 1** desde cero.
2. Justifica:
   - Por qué `b = stack.pop()` antes que `a = stack.pop()`.
   - Por qué `len(token) == 1` para distinguir operador de "-11".
   - Por qué `int(a / b)` y no `a // b`.
3. Trace mental con `["4", "13", "5", "/", "+"]`. Estado del stack en cada paso.
4. Trace mental con `["-7", "2", "/"]`. ¿Qué resultado? Compara con `-7 // 2`.
5. **Bonus** — implementa la Solución 2 con `operator` module.

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué stack es natural para RPN?"** → Cada operador consume los 2 más recientes (LIFO). Stack los pop directamente.
- **"¿Cómo extenderías a operadores unarios (e.g. negación, raíz cuadrada)?"** → Tratar diferenciado: pop solo 1 elemento, push resultado.
- **"¿Y si tuvieras que parsear notación INFIJA?"** → Algoritmo Shunting Yard (Dijkstra) para convertir infija a RPN, luego este algoritmo.
- **"¿Y si hubiera funciones (sin, cos, log, ...)?"** → Tratar cada función como operador unario; el parsing tokeniza palabras.

---

## Conexiones

- [[20-valid-parentheses]] — patrón base de stack.
- [[155-min-stack]] — stack como diseño de clase.
- Próximo: [[22-generate-parentheses]] — stack mental + backtracking.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 1 desde cero
- [ ] Justificado el orden de pop (derecho antes que izquierdo)
- [ ] Justificado `int(a/b)` vs `a // b`
- [ ] Resuelto en LeetCode con éxito
