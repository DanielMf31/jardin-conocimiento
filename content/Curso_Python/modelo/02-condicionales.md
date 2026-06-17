---
title: "Python Basico — Modulo 02: Condicionales"
date: 2026-06-16
tags: [programacion/python, programacion/python/curso, programacion/python/condicionales]
type: nota
status: en-progreso
source: claude-code
aliases: [condicionales python, if elif else python, truthiness python]
---

# Python Basico — Modulo 02: Condicionales

## Idea central

En Python los condicionales funcionan igual que en C (if / else), pero sin llaves: la **indentacion** define los bloques. Ademas, Python tiene operadores en ingles (`and`, `or`, `not`) y un concepto llamado *truthiness* que convierte cualquier valor en booleano implicitamente.

---

## Que aprendes

| Concepto | Para que |
|---|---|
| `if / elif / else` | Bifurcar la ejecucion segun una condicion |
| `and / or / not` | Combinar condiciones logicas |
| `==` vs `is` | Igualdad de valor vs identidad de objeto |
| Truthiness | Usar valores no booleanos como condicion directamente |
| Ternario `x if cond else y` | Asignacion condicional en una linea |
| `match-case` (3.10+) | Alternativa limpia al if/elif encadenado |
| Indentacion obligatoria | Delimitar bloques sin llaves |

---

## C vs Python

El mismo programa: leer un numero y decir si es positivo, negativo o cero.

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
- **Sin parentesis** en la condicion (opcionales, pero el estilo Python los omite).
- **Dos puntos** `:` al final de cada cabecera de bloque.
- **`elif`** en vez de `else if`.
- **Indentacion = llaves**: 4 espacios por nivel, siempre.

---

## Explicacion

### Estructura basica

```python
if condicion:
    # bloque si True
elif otra_condicion:
    # bloque si la primera fallo y esta es True
else:
    # bloque si ninguna fue True
```

### Operadores logicos

| C | Python | Significado |
|---|---|---|
| `&&` | `and` | ambas verdaderas |
| `\|\|` | `or` | al menos una verdadera |
| `!` | `not` | negacion |

```python
edad = 20
carnet = True
if edad >= 18 and carnet:
    print("puede conducir")
```

### Operadores de comparacion

Iguales que en C (`==`, `!=`, `<`, `>`, `<=`, `>=`). Diferencia importante:

```python
a = [1, 2]
b = [1, 2]
print(a == b)   # True  → mismo contenido
print(a is b)   # False → distinto objeto en memoria
```

Usa `==` para comparar valores. Reserva `is` para `None`: `if x is None:`.

### Truthiness

Python evalua **cualquier valor** como booleano en un contexto condicional:

| Falsy (equivale a False) | Truthy (equivale a True) |
|---|---|
| `0`, `0.0` | cualquier numero != 0 |
| `""` (cadena vacia) | cualquier cadena no vacia |
| `[]`, `{}`, `()` | coleccion con elementos |
| `None` | cualquier objeto no listado |

```python
nombre = input("Nombre: ")
if nombre:                   # True si el usuario escribio algo
    print(f"Hola, {nombre}")
else:
    print("No escribiste nada")
```

En C tendrias que escribir `if (strlen(nombre) > 0)`.

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

**Enunciado**: Dado un numero de nota (0-10), imprimir la letra correspondiente: A (9-10), B (7-8), C (5-6), D (3-4), F (0-2). Si esta fuera de rango, avisar.

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

**Codigo completo**:

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

## Errores tipicos de Python

1. **Indentacion inconsistente**
   ```python
   if x > 0:
   print("positivo")   # IndentationError: falta sangria
   ```
   Solucion: 4 espacios siempre, nunca mezcles tabs y espacios.

2. **`input()` devuelve `str`, no `int`**
   ```python
   n = input("Numero: ")
   if n > 5:            # TypeError: '>' not supported between str and int
       print("grande")
   ```
   Solucion: `n = int(input("Numero: "))`.

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

Archivos en `practica/02-condicionales/`.

| N | Enunciado | Dificultad | Salida esperada (ejemplo) |
|---|---|---|---|
| 01 | Par o impar: pide un entero e indica si es par o impar | verde | `Introduce un numero: 7` → `7 es impar` |
| 02 | Mayor de dos: pide dos enteros e indica cual es mayor (o si son iguales) | verde | `a=5, b=3` → `El mayor es 5` |
| 03 | Mayor de tres: pide tres enteros e imprime el mayor | amarillo | `a=4, b=9, c=2` → `El mayor es 9` |
| 04 | Signo: pide un flotante e imprime `positivo`, `negativo` o `cero` | verde | `n=-3.5` → `negativo` |
| 05 | Nota a letra: nota 0-10 → letra A/B/C/D/F; fuera de rango → aviso | amarillo | `nota=8` → `Letra: B` |
| 06 | Calculadora simple: pide dos numeros y un operador (+,-,*,/); imprime resultado; maneja division por cero | amarillo | `5 / 2` → `Resultado: 2.5` |
| 07 | Ano bisiesto: pide un ano y dice si es bisiesto (divisible por 4, excepto siglos no divisibles por 400) | rojo | `ano=2000` → `2000 es bisiesto` / `ano=1900` → `1900 NO es bisiesto` |

Cada ejercicio tiene dos archivos:
- `ejNN_modelo.py` — solucion completa y comentada.
- `ejNN_practica.py` — esqueleto con `# TODO` para que lo rellenes.

---

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/01-variables]]
- [[Curso_Python/modelo/03-bucles]]
