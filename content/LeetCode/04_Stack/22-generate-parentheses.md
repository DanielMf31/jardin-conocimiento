---
title: "LeetCode 22 — Generate Parentheses"
date: 2026-05-08
tags: [programacion/leetcode, programacion/algoritmos, programacion/python, leetcode/medium, patron/stack, patron/backtracking]
type: nota
status: en-progreso
source: claude-code
aliases: [Generate Parentheses, LC 22, generateParenthesis, Generar paréntesis válidos]
problem_id: 22
difficulty: medium
patron: stack
neetcode_order: 4
---

# LeetCode 22 — Generate Parentheses

> 🎯 **Cuarto problema del patrón Stack**, aunque la solución óptima es realmente **backtracking**. NeetCode lo ubica aquí porque la lógica de "abrir/cerrar" tiene estructura de stack mental. Es la **introducción suave al backtracking** que verás en profundidad en el patrón 10.
> 📚 Mismo formato: solución primero, patrón abstraído, replicar sin mirar.

## Enunciado

Dado `n` pares de paréntesis, **genera todas las combinaciones de paréntesis bien formadas**.

**Ejemplo 1:**
```
Input:  n = 3
Output: ["((()))", "(()())", "(())()", "()(())", "()()()"]
```

**Ejemplo 2:**
```
Input:  n = 1
Output: ["()"]
```

**Restricciones:**
- `1 <= n <= 8`.

**Plantilla:**
```python
class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        ...
```

---

## Lectura del problema antes de codear

| Pregunta | Respuesta |
|---|---|
| ¿Qué tipo devuelve? | `List[str]` con todas las combinaciones |
| ¿Importa el orden de salida? | NO |
| ¿Cuántas combinaciones para n? | El **n-ésimo número de Catalan**: `C(n) = (2n choose n) / (n+1)`. Para n=8 son 1430 |
| ¿Qué hace válida una combinación? | (1) En cualquier prefix, los `(` ≥ los `)`. (2) Al final, `(` = `)` = n |

> 💡 **La invariante clave**: en cualquier momento durante la construcción, **no podemos cerrar más paréntesis de los que hemos abierto**.

---

## Solución 1 — Generar todas las cadenas de 2n y filtrar (NO viable)

```python
class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        # Generar TODAS las cadenas binarias de longitud 2n
        # Filtrar las válidas
        from itertools import product
        result = []
        for combo in product('()', repeat=2*n):
            s = ''.join(combo)
            if self.is_valid(s):
                result.append(s)
        return result

    def is_valid(self, s):
        balance = 0
        for c in s:
            balance += 1 if c == '(' else -1
            if balance < 0:
                return False
        return balance == 0
```

**Análisis:**
- **Tiempo: O(2^(2n) · n)** — 2^(2n) cadenas posibles × O(n) validar.
- **Veredicto:** ❌ ineficiente. La idea correcta es no generar las inválidas.

---

## Solución 2 — Backtracking con conteo de aperturas y cierres (la canónica)

**La idea clave**: construir el string carácter a carácter, en cada posición decidiendo si añadir `(` o `)`. Mantener dos contadores:

- `open_count`: cuántos `(` he añadido.
- `close_count`: cuántos `)` he añadido.

**Reglas de poda**:
- **Puedo añadir `(`** si `open_count < n`.
- **Puedo añadir `)`** si `close_count < open_count` (no cerrar más de lo abierto).
- **Solución encontrada** cuando `len(string) == 2n`.

```python
class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        result = []

        def backtrack(current: str, open_count: int, close_count: int):
            if len(current) == 2 * n:
                result.append(current)
                return
            if open_count < n:
                backtrack(current + '(', open_count + 1, close_count)
            if close_count < open_count:
                backtrack(current + ')', open_count, close_count + 1)

        backtrack("", 0, 0)
        return result
```

**Trace mental para `n = 2`** (árbol de decisión):

```
                            ""  (0,0)
                              │
                              │ +(
                              ▼
                            "("  (1,0)
                          ┌──┴──┐
                       +( │     │ +)
                          ▼     ▼
                       "(("  (2,0)    "()"  (1,1)
                          │             │ +(
                       +) │             ▼
                          ▼          "()("  (2,1)
                       "(()"  (2,1)     │ +)
                          │ +)          ▼
                          ▼          "()()"  ✅
                       "(())"  ✅

Result: ["(())", "()()"]
```

**Análisis:**
- **Tiempo: O(4^n / √n)** — el n-ésimo número de Catalan, asintóticamente.
- **Espacio: O(n)** stack de recursión + O(catalan_n · n) para el output.
- **Veredicto:** ✅ **la canónica**. Backtracking puro y limpio.

---

## Solución 3 — Backtracking con lista mutable (optimización menor)

Usar una lista en lugar de concatenar strings (concat es O(n) cada vez).

```python
class Solution:
    def generateParenthesis(self, n: int) -> List[str]:
        result = []
        current = []

        def backtrack(open_count: int, close_count: int):
            if len(current) == 2 * n:
                result.append(''.join(current))
                return
            if open_count < n:
                current.append('(')
                backtrack(open_count + 1, close_count)
                current.pop()                       # ⭐ deshacer
            if close_count < open_count:
                current.append(')')
                backtrack(open_count, close_count + 1)
                current.pop()                       # ⭐ deshacer

        backtrack(0, 0)
        return result
```

**Análisis:** mismo O(catalan), pero **constantes mejores** (evita rebuild de string en cada llamada).

> 🎯 **El patrón "append + recurse + pop"** es la estructura típica de backtracking. El `current.pop()` es el "deshacer" que permite explorar la siguiente rama desde el mismo estado.

---

## El patrón general — "Backtracking con poda"

**Cuándo aplicar**:

> Cuando quieres generar **todas** las soluciones de un problema combinatorio, y existen **reglas de poda** que evitan ramas inútiles. La fuerza bruta enumera todo (2^n o más); el backtracking poda y reduce a la cardinalidad real de soluciones.

**Plantilla mental**:

```python
def backtrack(state, ...):
    if es_solucion(state):
        results.append(state.copy())
        return
    for choice in choices(state):
        if valid(state, choice):
            apply(state, choice)
            backtrack(state, ...)
            undo(state, choice)         # ⭐ deshacer al volver
```

**Tres señales** del patrón:

1. Quieres TODAS las soluciones (no solo una).
2. Hay reglas de validez que permiten descartar ramas tempranamente.
3. La fuerza bruta es exponencial pero la cardinalidad real es mucho menor.

> 📌 **Patrón maestro**: backtracking es el caballo de batalla de muchos problemas Medium/Hard. NeetCode tiene un patrón entero (10 - Backtracking) dedicado.

---

## Variaciones del problema

| Problema LeetCode | Variación |
|---|---|
| **78. Subsets** | Generar todos los subconjuntos |
| **39. Combination Sum** | Combinaciones que suman target |
| **46. Permutations** | Permutaciones (todas las reordenaciones) |
| **51. N-Queens** | Backtracking complejo |
| **301. Remove Invalid Parentheses** | Inverso: dado un string inválido, mínimas eliminaciones |

---

## Conceptos a interiorizar

### Backtracking vs Stack explícito

Los problemas de "todas las combinaciones" se pueden hacer con:
- **Recursión + backtracking** (lo más común): el call stack ES el stack.
- **Stack explícito + iteración**: viable pero más complicado de codear.

LeetCode generalmente espera la versión recursiva.

### `current.append + recurse + current.pop`

El patrón "append-recurse-pop" simula explorar una rama y luego deshacerla. Es lo que diferencia backtracking de simple recursión:

```python
# Backtracking idiomático
current.append(x)
backtrack(...)
current.pop()                # deshacer

# vs versión "no destructiva" (más memoria)
backtrack(current + [x], ...)
```

La primera reusa el mismo `current` (ahorra memoria), la segunda crea copias (más fácil de razonar).

### Por qué número de Catalan

El número de paréntesis válidos de longitud 2n es el **n-ésimo número de Catalan**:
- C(0) = 1
- C(1) = 1
- C(2) = 2
- C(3) = 5
- C(4) = 14
- C(5) = 42

Aparecen en muchos problemas de combinatoria (BSTs distintos, triangulaciones de polígonos, etc.).

---

## Comparación final de las 3 soluciones

| Solución | Tiempo | Espacio | Veredicto |
|---|---|---|---|
| 1. Brute force + filtro | O(2^(2n) · n) | O(n) | ❌ Muy ineficiente |
| 2. **Backtracking con string** | O(catalan_n · n) | O(n) | ✅ La canónica |
| 3. **Backtracking con list** | O(catalan_n · n) | O(n) | ✅ Constantes mejores |

---

## Auto-test (para ti, sin mirar el archivo)

1. Escribe la **Solución 2** desde cero.
2. Justifica:
   - Las dos reglas de poda (`open_count < n` y `close_count < open_count`).
   - Por qué no necesitas comprobar validez al final (la poda lo garantiza).
   - Cuándo se añade al `result`.
3. Implementa la **Solución 3** con `current.pop()` después de cada recurse. Asegúrate de hacer ambos `pop` en sus sitios.
4. Trace mental dibujando el árbol de decisión para `n = 3` (5 hojas esperadas).
5. **Bonus** — modifica para devolver SOLO la primera solución (cualquiera de las válidas).

---

## Cosas que te pueden preguntar en entrevista

- **"¿Por qué backtracking y no DP?"** → DP funciona si hay subproblemas con solución reutilizable. Aquí cada estado depende del prefix construido, no es reutilizable. Backtracking enumera con poda.
- **"¿Cuál es la complejidad exacta?"** → O(C(n) · n) donde C(n) es el n-ésimo Catalan. Para n=8: 1430 strings × longitud 16 ≈ 23k operaciones.
- **"¿Cómo lo extenderías a múltiples tipos de paréntesis (`{}`, `[]`, `()`)?"** → Cada par tiene su contador de apertura y cierre. La complejidad explota (no es un solo Catalan).
- **"¿Diferencia entre backtracking y DFS?"** → Backtracking ES DFS sobre un espacio de estados, con la propiedad de que se "deshace" al volver.

---

## Conexiones

- [[20-valid-parentheses]] — validar paréntesis (este es generar).
- Próximo: [[739-daily-temperatures]] — stack monotónico, otro uso clásico.
- Patrón futuro: **Backtracking** (10) — verás muchos primos de este problema.

## Estado de progreso personal

- [ ] Leído con comprensión
- [ ] Escrita Solución 2 desde cero
- [ ] Implementada Solución 3 con append/pop manual
- [ ] Justificadas las 2 reglas de poda
- [ ] Trace mental hecho dibujando el árbol para n=3
- [ ] Resuelto en LeetCode con éxito
