---
title: "Módulo 01: Variables, tipos y E/S en Python"
date: 2026-06-16
tags: [programacion/python, programacion/curso-python, programacion/fundamentos]
aliases: ["Python variables", "tipos Python", "entrada salida Python", "print input Python"]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-python/modelo/01-variables.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-python/modelo/01-variables.md (se regenera con gen_course.py). -->

# Módulo 01: Variables, tipos y E/S

## Idea central

En C debes declarar el tipo de cada variable antes de usarla. En Python el tipo **vive en el valor, no en la variable**: puedes asignar cualquier cosa a cualquier nombre sin declarar nada. La entrada de usuario (`input()`) **siempre devuelve `str`**; si necesitas un número debes convertirlo explícitamente.

---

## Qué aprendes

| Concepto | Para qué sirve |
|---|---|
| Tipado dinámico | Escribir menos; el tipo lo decide Python en tiempo de ejecución |
| `print()` | Mostrar información en pantalla |
| `input()` | Leer una línea del teclado (devuelve `str`) |
| `int()`, `float()`, `str()`, `bool()` | Convertir entre tipos explícitamente |
| f-strings (`f"..."`) | Interpolar variables en texto de forma legible |
| `//`, `**`, `%` | División entera, potencia, resto |
| `type()` | Inspeccionar el tipo de un valor en tiempo de ejecución |
| `a, b = b, a` | Intercambiar dos variables sin variable auxiliar |

---

## C vs Python

El mismo programa que pide un número y calcula su cuadrado:

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

- **Sin `main()`**: el código se ejecuta de arriba a abajo directamente.
- **Sin declaración de tipo**: `x = 5` crea la variable y le asigna tipo `int` al mismo tiempo.
- **`input()` siempre devuelve `str`**: `x = input()` da `"5"`, no `5`. Hay que escribir `x = int(input())`.
- **Indentación obligatoria**: donde C usa `{}`, Python usa sangría (4 espacios por convención).

---

## Explicación

### Patrón de asignación

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

### Conversión de tipos

```python
edad = int(input("Edad: "))       # str -> int
precio = float(input("Precio: ")) # str -> float
texto = str(42)                   # int -> str
```

Si el usuario escribe algo que no es un número y pides `int()`, Python lanza `ValueError`. Por ahora asumimos entrada correcta.

### Operadores aritméticos importantes

| Operador | Significado | Ejemplo | Resultado |
|---|---|---|---|
| `//` | División entera | `7 // 2` | `3` |
| `**` | Potencia | `2 ** 10` | `1024` |
| `%` | Resto (módulo) | `7 % 2` | `1` |

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

En C necesitarías una variable temporal `tmp`. Python lo resuelve con asignacion multiple.

---

## Worked example

**Enunciado**: el programa pide nombre y año de nacimiento, calcula la edad aproximada y muestra un saludo personalizado.

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

Ejecución de ejemplo:

```
Nombre: Maria
Anno de nacimiento: 1995
Hola, Maria! Tienes aproximadamente 31 anios.
```

Por qué funciona:
1. `input()` devuelve `"1995"` (str). Sin `int()`, la resta fallaría con `TypeError`.
2. La f-string interpola directamente las variables calculadas.
3. No hay `printf` con `%d`; la f-string infiere el formato por el tipo.

---

## Errores típicos de Python

### 1. Olvidar `int()` con `input()`

```python
# MAL
x = input("Dame un numero: ")
print(x + 1)    # TypeError: can only concatenate str (not "int") to str

# BIEN
x = int(input("Dame un numero: "))
print(x + 1)
```

### 2. Indentación incorrecta

```python
# MAL (IndentationError)
if True:
print("hola")   # falta sangria

# BIEN
if True:
    print("hola")
```

Python no usa `{}`; la sangría **es** la estructura. Un espacio de diferencia entre bloques del mismo nivel causa `IndentationError` o lógica incorrecta silenciosa.

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

### 4. División `/` devuelve `float`, no `int`

```python
print(7 / 2)    # 3.5  (float, no 3 como en C con int/int)
print(7 // 2)   # 3    (division entera, equivalente a int/int de C)
```

Si venías de C y esperas `3` de `7/2`, usad `//`.

### 5. Las variables no existen hasta que se asignan

```python
# MAL
print(z)    # NameError: name 'z' is not defined

# BIEN
z = 0
print(z)
```

En C el compilador detecta esto; en Python es un error en tiempo de ejecución.

---

## Ejercicios

- [[Curso_Python/practica/01-variables/ej01|Ej 01 — Pide el nombre del usuario y muestra un saludo personalizado (verde)]]
- [[Curso_Python/practica/01-variables/ej02|Ej 02 — Pide dos enteros y muestra su suma (verde)]]
- [[Curso_Python/practica/01-variables/ej03|Ej 03 — Pide tres notas (float) y muestra la media con 2 decimales (verde)]]
- [[Curso_Python/practica/01-variables/ej04|Ej 04 — Pide temperatura en Celsius y convierte a Fahrenheit (verde)]]
- [[Curso_Python/practica/01-variables/ej05|Ej 05 — Pide radio (float) y muestra area y perimetro del circulo (amarillo)]]
- [[Curso_Python/practica/01-variables/ej06|Ej 06 — Pide dos enteros, los intercambia e imprime valores antes y después (amarillo)]]
- [[Curso_Python/practica/01-variables/ej07|Ej 07 — Pide dividendo y divisor, muestra cociente entero y resto (amarillo)]]

## Conexiones

- [[Curso_Python/modelo/00-python-vs-c]]
- [[Curso_Python/modelo/02-condicionales]]
- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
