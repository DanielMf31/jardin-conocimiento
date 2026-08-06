---
title: "Python Básico — Módulo 02: Condicionales"
date: 2026-06-16
tags: [programacion/python, programacion/python/curso, programacion/python/condicionales]
aliases: [condicionales python, if elif else python, truthiness python]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-python/modelo/02-condicionales.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-python/modelo/02-condicionales.md (se regenera con gen_course.py). -->

# Python Básico — Módulo 02: Condicionales

## Idea central

En Python los condicionales funcionan igual que en C (if / else), pero sin llaves: la **indentación** define los bloques. Además, Python tiene operadores en inglés (`and`, `or`, `not`) y un concepto llamado *truthiness* que convierte cualquier valor en booleano implícitamente.

---

## Qué aprendes

| Concepto | Para que |
|---|---|
| `if / elif / else` | Bifurcar la ejecución según una condición |
| `and / or / not` | Combinar condiciones logicas |
| `==` vs `is` | Igualdad de valor vs identidad de objeto |
| Truthiness | Usar valores no booleanos como condición directamente |
| Ternario `x if cond else y` | Asignación condicional en una línea |
| `match-case` (3.10+) | Alternativa limpia al if/elif encadenado |
| Indentación obligatoria | Delimitar bloques sin llaves |

---

## C vs Python

El mismo programa: leer un número y decir si es positivo, negativo o cero.

| C | Python |
|---|---|
| `int n;` | `n = int(input("n: "))` |
| `scanf("%d", &n);` | *(incluido arriba)* |
| `if (n > 0) {` | `if n > 0:` |
| `    printf("positivo\n");` | `    print("positivo")` |
| `} else if (n < 0) {` | `elif n < 0:` |
| `    printf("negativo\n");` | `    print("negativo")` |
| `} else {` | `else:` |
| `    printf("cero\n");` | `    print("cero")` |
| `}` | *(nada: el bloque termina al desidentar)* |

Diferencias clave:
- **Sin paréntesis** en la condición (opcionales, pero el estilo Python los omite).
- **Dos puntos** `:` al final de cada cabecera de bloque.
- **`elif`** en vez de `else if`.
- **Indentación = llaves**: 4 espacios por nivel, siempre.

---

## Explicación

### Estructura básica

```python
if condicion:
    # bloque si True
elif otra_condicion:
    # bloque si la primera fallo y esta es True
else:
    # bloque si ninguna fue True
```

### Operadores lógicos

| C | Python | Significado |
|---|---|---|
| `&&` | `and` | ambas verdaderas |
| `\|\|` | `or` | al menos una verdadera |
| `!` | `not` | negación |

```python
edad = 20
carnet = True
if edad >= 18 and carnet:
    print("puede conducir")
```

### Operadores de comparación

Iguales que en C (`==`, `!=`, `<`, `>`, `<=`, `>=`). Diferencia importante:

```python
a = [1, 2]
b = [1, 2]
print(a == b)   # True  → mismo contenido
print(a is b)   # False → distinto objeto en memoria
```

Usa `==` para comparar valores. Reserva `is` para `None`: `if x is None:`.

### Truthiness

Python evalúa **cualquier valor** como booleano en un contexto condicional:

| Falsy (equivale a False) | Truthy (equivale a True) |
|---|---|
| `0`, `0.0` | cualquier número != 0 |
| `""` (cadena vacía) | cualquier cadena no vacía |
| `[]`, `{}`, `()` | colección con elementos |
| `None` | cualquier objeto no listado |

```python
nombre = input("Nombre: ")
if nombre:                   # True si el usuario escribio algo
    print(f"Hola, {nombre}")
else:
    print("No escribiste nada")
```

En C tendrías que escribir `if (strlen(nombre) > 0)`.

### Ternario

```python
# Python
resultado = "par" if numero % 2 == 0 else "impar"

# C equivalente
// resultado = (numero % 2 == 0) ? "par" : "impar";
```

### match-case (Python 3.10+)

Alternativa limpia al `if/elif` encadenado cuando comparas un valor contra constantes:

```python
dia = 3
match dia:
    case 1: print("lunes")
    case 2: print("martes")
    case 3: print("miercoles")
    case _: print("otro dia")   # _ es el default
```

Equivale al `switch` de C. Para casos compuestos: `case 1 | 2 | 7: print("fin de semana o lunes")`.

---

## Worked example

**Enunciado**: Dado un número de nota (0-10), imprimir la letra correspondiente: A (9-10), B (7-8), C (5-6), D (3-4), F (0-2). Si está fuera de rango, avisar.

**Paso 1 — leer entrada y convertir a int**

```python
entrada = input("Nota (0-10): ")
nota = int(entrada)           # input() siempre devuelve str → hay que convertir
```

**Paso 2 — validar rango antes de clasificar**

```python
if nota < 0 or nota > 10:
    print("Nota fuera de rango")
```

**Paso 3 — clasificar con elif encadenado**

```python
elif nota >= 9:
    letra = "A"
elif nota >= 7:
    letra = "B"
elif nota >= 5:
    letra = "C"
elif nota >= 3:
    letra = "D"
else:
    letra = "F"
print(f"Letra: {letra}")
```

**Código completo**:

```python
nota = int(input("Nota (0-10): "))

if nota < 0 or nota > 10:
    print("Nota fuera de rango")
elif nota >= 9:
    letra = "A"
elif nota >= 7:
    letra = "B"
elif nota >= 5:
    letra = "C"
elif nota >= 3:
    letra = "D"
else:
    letra = "F"
    print(f"Letra: {letra}")
```

Truco: ordenar los `elif` de mayor a menor evita condiciones dobles como `nota >= 7 and nota < 9`.

---

## Errores típicos de Python

1. **Indentación inconsistente**
   ```python
   if x > 0:
   print("positivo")   # IndentationError: falta sangria
   ```
   Solución: 4 espacios siempre, nunca mezcles tabs y espacios.

2. **`input()` devuelve `str`, no `int`**
   ```python
   n = input("Numero: ")
   if n > 5:            # TypeError: '>' not supported between str and int
       print("grande")
   ```
   Solución: `n = int(input("Numero: "))`.

3. **`=` en vez de `==` dentro del `if`**
   ```python
   if x = 5:   # SyntaxError en Python (en C compilaria y haria algo raro)
   ```
   Python lo detecta como error de sintaxis. Bien.

4. **Olvidar los dos puntos `:`**
   ```python
   if x > 0    # SyntaxError: expected ':'
       print("ok")
   ```
   Cada cabecera de bloque (`if`, `elif`, `else`, `for`, `def`…) termina en `:`.

5. **Comparar con `==` en vez de `is` para `None`**
   ```python
   x = None
   if x == None:   # funciona, pero es estilo incorrecto
       ...
   if x is None:   # correcto: None es un singleton
       ...
   ```

---

## Ejercicios

- [[Curso_Python/practica/02-condicionales/ej01|Ej 01 — Pide un entero e indica si es par o impar (verde)]]
- [[Curso_Python/practica/02-condicionales/ej02|Ej 02 — Pide dos enteros e indica cual es mayor, o si son iguales (verde)]]
- [[Curso_Python/practica/02-condicionales/ej03|Ej 03 — Pide tres enteros e imprime el mayor de los tres (amarillo)]]
- [[Curso_Python/practica/02-condicionales/ej04|Ej 04 — Pide un flotante e imprime su signo (positivo, negativo o cero) (verde)]]
- [[Curso_Python/practica/02-condicionales/ej05|Ej 05 — Convierte una nota numerica (0-10) a letra A/B/C/D/F (amarillo)]]
- [[Curso_Python/practica/02-condicionales/ej06|Ej 06 — Calculadora simple: dos números y un operador (+,-,*,/) (amarillo)]]
- [[Curso_Python/practica/02-condicionales/ej07|Ej 07 — Determina si un ano es bisiesto (div (rojo)]]

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/01-variables]]
- [[Curso_Python/modelo/03-bucles]]
