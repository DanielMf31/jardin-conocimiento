---
title: "Modulo 01: Variables, tipos y E/S en Python"
date: 2026-06-16
tags: [programacion/python, programacion/curso-python, programacion/fundamentos]
type: nota
status: en-progreso
source: claude-code
aliases: ["Python variables", "tipos Python", "entrada salida Python", "print input Python"]
---

# Modulo 01: Variables, tipos y E/S

## Idea central

En C debes declarar el tipo de cada variable antes de usarla. En Python el tipo **vive en el valor, no en la variable**: puedes asignar cualquier cosa a cualquier nombre sin declarar nada. La entrada de usuario (`input()`) **siempre devuelve `str`**; si necesitas un numero debes convertirlo explicitamente.

---

## Que aprendes

| Concepto | Para que sirve |
|---|---|
| Tipado dinamico | Escribir menos; el tipo lo decide Python en tiempo de ejecucion |
| `print()` | Mostrar informacion en pantalla |
| `input()` | Leer una linea del teclado (devuelve `str`) |
| `int()`, `float()`, `str()`, `bool()` | Convertir entre tipos explicitamente |
| f-strings (`f"..."`) | Interpolar variables en texto de forma legible |
| `//`, `**`, `%` | Division entera, potencia, resto |
| `type()` | Inspeccionar el tipo de un valor en tiempo de ejecucion |
| `a, b = b, a` | Intercambiar dos variables sin variable auxiliar |

---

## C vs Python

El mismo programa que pide un numero y calcula su cuadrado:

| C | Python |
|---|---|
| `#include <stdio.h>` | *(no hace falta nada)* |
| `int main() {` | *(no hace falta main)* |
| `int x;` | *(no se declara)* |
| `printf("Dame un numero: ");` | `print("Dame un numero: ", end="")` |
| `scanf("%d", &x);` | `x = int(input())` |
| `printf("Cuadrado: %d\n", x*x);` | `print(f"Cuadrado: {x**2}")` |
| `return 0; }` | *(no hace falta)* |

Diferencias clave:

- **Sin `main()`**: el codigo se ejecuta de arriba a abajo directamente.
- **Sin declaracion de tipo**: `x = 5` crea la variable y le asigna tipo `int` al mismo tiempo.
- **`input()` siempre devuelve `str`**: `x = input()` da `"5"`, no `5`. Hay que escribir `x = int(input())`.
- **Indentacion obligatoria**: donde C usa `{}`, Python usa sangria (4 espacios por convencion).

---

## Explicacion

### Patron de asignacion

```python
nombre = valor          # crea (o reasigna) la variable
```

No hay `int`, `float`, `char *`... antes del nombre. El tipo lo lleva el valor:

```python
x = 42          # int
pi = 3.14159    # float
saludo = "Hola" # str
activo = True   # bool  (True/False, con mayuscula)
```

### `print()` y `input()`

```python
print("Hola, mundo")           # imprime y salta de linea
print("x =", x)                # separa con espacio automaticamente
print(f"x = {x}")              # f-string: lo mismo, mas legible
nombre = input("Tu nombre: ")  # muestra el prompt y espera; devuelve str
```

### Conversion de tipos

```python
edad = int(input("Edad: "))       # str -> int
precio = float(input("Precio: ")) # str -> float
texto = str(42)                   # int -> str
```

Si el usuario escribe algo que no es un numero y pides `int()`, Python lanza `ValueError`. Por ahora asumimos entrada correcta.

### Operadores aritmeticos importantes

| Operador | Significado | Ejemplo | Resultado |
|---|---|---|---|
| `//` | Division entera | `7 // 2` | `3` |
| `**` | Potencia | `2 ** 10` | `1024` |
| `%` | Resto (modulo) | `7 % 2` | `1` |

### f-strings

```python
nombre = "Ana"
edad = 30
print(f"Hola, {nombre}. Tienes {edad} anios.")
# -> Hola, Ana. Tienes 30 anios.

radio = 3.5
print(f"Radio = {radio:.2f}")   # 2 decimales -> 3.50
```

### `type()` para inspeccionar

```python
x = "5"
print(type(x))        # <class 'str'>
x = int(x)
print(type(x))        # <class 'int'>
```

### Intercambio sin auxiliar

```python
a, b = 10, 20
a, b = b, a           # Python evalua el lado derecho antes de asignar
print(a, b)           # 20 10
```

En C necesitarias una variable temporal `tmp`. Python lo resuelve con asignacion multiple.

---

## Worked example

**Enunciado**: el programa pide nombre y anno de nacimiento, calcula la edad aproximada y muestra un saludo personalizado.

```python
# Paso 1: pedir datos (input devuelve str siempre)
nombre = input("Nombre: ")
anno_nac = int(input("Anno de nacimiento: "))   # convertir a int

# Paso 2: calcular
anno_actual = 2026
edad = anno_actual - anno_nac

# Paso 3: mostrar con f-string
print(f"Hola, {nombre}! Tienes aproximadamente {edad} anios.")
```

Ejecucion de ejemplo:

```
Nombre: Maria
Anno de nacimiento: 1995
Hola, Maria! Tienes aproximadamente 31 anios.
```

Por que funciona:
1. `input()` devuelve `"1995"` (str). Sin `int()`, la resta fallaría con `TypeError`.
2. La f-string interpola directamente las variables calculadas.
3. No hay `printf` con `%d`; la f-string infiere el formato por el tipo.

---

## Errores tipicos de Python

### 1. Olvidar `int()` con `input()`

```python
# MAL
x = input("Dame un numero: ")
print(x + 1)    # TypeError: can only concatenate str (not "int") to str

# BIEN
x = int(input("Dame un numero: "))
print(x + 1)
```

### 2. Indentacion incorrecta

```python
# MAL (IndentationError)
if True:
print("hola")   # falta sangria

# BIEN
if True:
    print("hola")
```

Python no usa `{}`; la sangria **es** la estructura. Un espacio de diferencia entre bloques del mismo nivel causa `IndentationError` o lógica incorrecta silenciosa.

### 3. Concatenar `str` con `int` sin convertir

```python
edad = 25
# MAL
print("Tienes " + edad + " anios")      # TypeError

# BIEN (opcion 1: f-string)
print(f"Tienes {edad} anios")

# BIEN (opcion 2: str())
print("Tienes " + str(edad) + " anios")
```

### 4. Division `/` devuelve `float`, no `int`

```python
print(7 / 2)    # 3.5  (float, no 3 como en C con int/int)
print(7 // 2)   # 3    (division entera, equivalente a int/int de C)
```

Si venias de C y esperas `3` de `7/2`, usad `//`.

### 5. Las variables no existen hasta que se asignan

```python
# MAL
print(z)    # NameError: name 'z' is not defined

# BIEN
z = 0
print(z)
```

En C el compilador detecta esto; en Python es un error en tiempo de ejecucion.

---

## Ejercicios

Cada ejercicio tiene un archivo modelo (resuelto) y un esqueleto de practica en `practica/01-variables/`.

| N | Enunciado | Dificultad | Salida de ejemplo |
|---|---|---|---|
| 01 | Pide nombre y muestra saludo personalizado | (facil) facil | `Hola, Ana! Bienvenida al curso.` |
| 02 | Pide dos enteros y muestra su suma | (facil) facil | `Suma: 17` |
| 03 | Pide tres notas (float) y muestra la media con 2 decimales | (facil) facil | `Media: 7.33` |
| 04 | Pide temperatura en Celsius y convierte a Fahrenheit | (facil) facil | `37.0 C = 98.6 F` |
| 05 | Pide radio (float) y muestra area y perimetro del circulo | (media) medio | `Area: 78.54  Perimetro: 31.42` |
| 06 | Pide dos enteros, los intercambia e imprime los valores antes y despues | (media) medio | `Antes: a=10 b=20  Despues: a=20 b=10` |
| 07 | Pide dividendo y divisor, muestra cociente entero y resto | (media) medio | `17 // 5 = 3, resto 2` |

- Modelos: `practica/01-variables/ejNN_modelo.py`
- Esqueletos: `practica/01-variables/ejNN_practica.py`

---

## Conexiones

- [[Curso_Python/modelo/00-python-vs-c]]
- [[Curso_Python/modelo/02-condicionales]]
- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
