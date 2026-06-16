---
title: "LeetCode 20 — Valid Parentheses"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/easy, patron/stack, patron/matching-delimitadores]
type: nota
status: en-progreso
source: claude-code
aliases: [Valid Parentheses, LC 20, isValid, Paréntesis válidos]
problem_id: 20
difficulty: easy
patron: stack
neetcode_order: 1
---

# LeetCode 20 — Valid Parentheses

> 🎯 **Primer problema del patrón Stack** y la introducción más limpia al patrón. La idea: un stack es **memoria LIFO** (Last In First Out) que recuerda **lo más reciente sin terminar**. Cuando ves un cierre, lo que esperas casarlo es lo más reciente que esté abierto.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado un string `s` que contiene solo los caracteres `'('`, `')'`, `'{'`, `'}'`, `'['` y `']'`, determina si el string es **válido**.

Un string es válido si:
1. Los paréntesis abiertos están **cerrados** por el mismo tipo de paréntesis.
2. Los paréntesis abiertos se cierran **en el orden correcto** (el último abierto se cierra primero).
3. Cada paréntesis de cierre tiene un paréntesis de apertura **del mismo tipo** que le precede.

**Ejemplo 1:**
```
Input:  s = "()"
Output: true
```

**Ejemplo 2:**
```
Input:  s = "()[]{}"
Output: true
```

**Ejemplo 3:**
```
Input:  s = "(]"
Output: false (cierre del tipo equivocado)
```

**Ejemplo 4:**
```
Input:  s = "([)]"
Output: false (orden equivocado)
```

**Ejemplo 5:**
```
Input:  s = "{[]}"
Output: true (anidamiento correcto)
```

**Restricciones:**
- `1 <= s.length <= 10^4`
- `s` solo contiene `()[]{}`.

**Plantilla:**
```python
class Solution:
    def isValid(self, s: str) -> bool:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `bool` |
| ¿Qué significa "orden correcto"? | LIFO: lo último abierto se cierra primero |
| ¿String vacío? | `True` (vacuamente válido) — pero el enunciado garantiza length ≥ 1 |
| ¿Solo cierre sin apertura? | `False` directo |
| ¿Solo apertura sin cierre? | `False` (queda algo "colgando") |
| Edge case 1 | `"]"` → `False` (cierre solitario) |
| Edge case 2 | `"["` → `False` (apertura solitaria) |
| Edge case 3 | `"(){}[]"` → `True` (todos pares secuenciales) |

> 💡 **La estructura natural** del problema es LIFO: cuando ves un cierre, lo que tienes que casarlo es **la última apertura que vino**. Stack lo modela exactamente.

---

## Solución 1 — Stack con dict de mapeo (la canónica)

**La idea**: recorrer caracteres. Si es **apertura** (`(`, `[`, `{`), push al stack. Si es **cierre** (`)`, `]`, `}`), comprobar que el top del stack coincide con la apertura correspondiente. Al final, el stack debe estar vacío.

```python
class Solution:
    def isValid(self, s: str) -> bool:
        # mapeo cierre -> apertura
        pairs = {')': '(', ']': '[', '}': '{'}
        stack = []

        for char in s:
            if char in pairs:                       # es cierre
                if not stack or stack[-1] != pairs[char]:
                    return False
                stack.pop()
            else:                                   # es apertura
                stack.append(char)

        return not stack                            # válido si stack vacío
```

**Trace mental con `s = "{[]}"`**:

```
Estado inicial: stack = []

char='{' (apertura) → push          stack = ['{']
char='[' (apertura) → push          stack = ['{', '[']
char=']' (cierre)
       → top='[' == pairs[']']='[' ✅
       → pop                        stack = ['{']
char='}' (cierre)
       → top='{' == pairs['}']='{' ✅
       → pop                        stack = []

Final: stack vacío → return True ✅
```

**Trace mental con `s = "([)]"`**:

```
Estado inicial: stack = []

char='(' (apertura) → push          stack = ['(']
char='[' (apertura) → push          stack = ['(', '[']
char=')' (cierre)
       → top='[' != pairs[')']='(' ❌
       → return False
```

**Análisis:**
- **Tiempo: O(n)** — un recorrido lineal.
- **Espacio: O(n)** — el stack puede llegar a tener n/2 caracteres en el peor caso.
- **Veredicto:** ✅ **la canónica de entrevista**. Limpia y eficiente.

---

## Solución 2 — Stack con if encadenados (sin dict)

Misma idea pero comparando carácter por carácter. Más verbosa, igual de eficiente.

```python
class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        for char in s:
            if char in "([{":
                stack.append(char)
            else:
                if not stack:
                    return False
                top = stack.pop()
                if (char == ')' and top != '(') or \
                   (char == ']' and top != '[') or \
                   (char == '}' and top != '{'):
                    return False
        return not stack
```

**Veredicto:** funciona pero **menos limpia**. La Solución 1 con dict es la que se espera en entrevista.

---

## Solución 3 — Truco "replace" iterativo (NO usar, pero educativa)

Reemplazar `()`, `[]`, `{}` repetidamente hasta que no se pueda.

```python
class Solution:
    def isValid(self, s: str) -> bool:
        while '()' in s or '[]' in s or '{}' in s:
            s = s.replace('()', '').replace('[]', '').replace('{}', '')
        return s == ''
```

**Análisis:**
- **Tiempo: O(n²)** — cada `replace` es O(n), y se ejecuta hasta n/2 veces.
- **Espacio: O(n)**.
- **Veredicto:** ⚠️ es un "truco" que pasa LeetCode pero **NUNCA escribas esto en entrevista**. No demuestra que entiendes el patrón stack.

---

## El patrón general — "Stack para emparejamiento LIFO"

**Cuándo aplicar**:

> Cuando el problema requiere recordar **la apertura más reciente sin terminar** y emparejarla con su cierre. La estructura LIFO del stack lo modela directamente.

**Plantilla mental**:

```python
def stack_matching(s, pairs_close_to_open):
    stack = []
    for char in s:
        if char es_cierre:
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
        else:                           # es apertura
            stack.append(char)
    return not stack                    # vacío al final = válido
```

**Tres señales** del patrón:

1. Hay elementos que **abren** algo y elementos que **cierran** algo.
2. Los cierres deben emparejarse con la apertura **más reciente** (LIFO).
3. La fuerza bruta sería O(n²) buscando matches; con stack es O(n).

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **22. Generate Parentheses** | Generar TODAS las combinaciones válidas de n pares |
| **32. Longest Valid Parentheses** | El substring válido más largo (DP o stack) |
| **921. Minimum Add to Make Parentheses Valid** | Cuántos chars añadir para validar |
| **1249. Minimum Remove to Make Valid Parentheses** | Cuántos chars quitar para validar |

---

## Conceptos a interiorizar

### Stack en Python

Python no tiene un tipo `stack` separado. Se usa una `list`:

```python
stack = []
stack.append(x)              # push (O(1))
stack.pop()                  # pop top (O(1))
stack[-1]                    # ver top sin sacar (O(1))
not stack                    # vacío? (idiomático)
len(stack) == 0              # vacío? (equivalente)
```

> ⚠️ **NO uses `stack.pop(0)`** — eso es `popleft` y es O(n) en list. Para FIFO (queue), usa `collections.deque`.

### `not stack` — el chequeo idiomático de vacío

```python
if not stack:                # ✅ pythonic
if len(stack) == 0:          # ❌ menos idiomático
if stack == []:              # ❌ no idiomático
```

Una list vacía es "falsy" en Python. Lo mismo aplica a string vacío, dict vacío, set vacío, None y 0.

### El patrón "look before pop"

```python
# ❌ Mal: si el stack está vacío, .pop() lanza IndexError
if char en cierres:
    top = stack.pop()
    if top != pairs[char]:
        return False

# ✅ Bien: chequear vacío ANTES de pop
if char en cierres:
    if not stack or stack[-1] != pairs[char]:
        return False
    stack.pop()
```

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. **Stack con dict de mapeo** | **O(n)** | O(n) | ✅ La canónica |
| 2. Stack con if encadenados | O(n) | O(n) | Funciona, menos limpia |
| 3. Replace iterativo | O(n²) | O(n) | ⚠️ Truco; no usar en entrevista |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 1** desde cero.
2. Justifica:
   - Por qué chequear `not stack` antes de comparar con `stack[-1]`.
   - Por qué al final hay que verificar `not stack` (qué pasa con `"((("`).
   - Cuál es la complejidad espacial peor caso.
3. Trace mental con `s = "{[()]}"`. ¿Estado del stack en cada paso?
4. Trace mental con `s = "(("`. ¿Por qué devuelve `False`?
5. **Bonus** — extiéndelo: además de bool, devolver el **índice del primer error** (o -1 si es válido).

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué stack y no contar paréntesis?"** → Contar funciona si solo hay un tipo, pero no detecta `"([)]"` (orden incorrecto). Con stack sí.
- **"¿Cómo lo extenderías a expresiones aritméticas (sumar contenido)?"** → Combinar este patrón con el de [[150-evaluate-reverse-polish-notation]].
- **"Y si el alfabeto fuera arbitrario (e.g. tags HTML `<b>...</b>`)?"** → Mismo algoritmo con dict que mapea cierre→apertura, solo que el mapeo es más complejo.
- **"Demuestra el O(n)."** → Cada char se procesa una vez. Push y pop son O(1). Total O(n).

---

## Solución en C++ — contraste con Python

> 📘 Añadido para ver las diferencias de lenguaje. Código compilable en [`20-valid-parentheses.cpp`](20-valid-parentheses.cpp).

```cpp
class Solution {
 public:
  bool isValid(std::string s) {
    std::unordered_map<char, char> close_to_open = {
        {')', '('}, {']', '['}, {'}', '{'}};
    std::stack<char> st;
    for (char c : s) {
      if (c == '(' || c == '[' || c == '{') st.push(c);
      else {
        if (st.empty() || st.top() != close_to_open[c]) return false;
        st.pop();
      }
    }
    return st.empty();
  }
};
```

**Análisis:** Tiempo O(n), Espacio O(n) — igual que el Python idiomático.

**Diferencias clave Python ↔ C++:**
- Pila: lista usada como stack (`append`/`pop`) → `std::stack<char>` dedicado (`push`/`pop`/`top`/`empty`).
- Ojo: `st.pop()` en C++ **no devuelve** el elemento (es `void`); lees con `st.top()` y luego `st.pop()`. En Python `lst.pop()` sí devuelve.
- `dict` literal → `std::unordered_map<char,char>` con lista de inicialización.
- `char` es un entero de 1 byte (comparas con `'('` directamente); en Python son strings de longitud 1.

---

## Conexiones

- [[MOC_NeetCode_150]] — índice general.
- [[239-sliding-window-maximum]] — usa **deque monotónica**, primo cercano del stack monotónico.
- Próximo: [[155-min-stack]] — diseñar un stack con operación getMin O(1).

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 1 desde cero
- [ ] Justificadas las 2 condiciones (chequeo de vacío y de mismatch)
- [ ] Trace mental hecho con `"{[()]}"`
- [ ] Resuelto en LeetCode con éxito
