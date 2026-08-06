---
title: "Módulo 04: Funciones en Python"
date: 2026-06-16
tags: [programacion/python, programacion/curso, programacion/funciones]
aliases: [funciones python, def python, return python, docstrings]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-python/modelo/04-funciones.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-python/modelo/04-funciones.md (se regenera con gen_course.py). -->

# Módulo 04: Funciones en Python

## Idea central

En Python una función se define con `def`, no necesita prototipo, puede devolver varios valores a la vez con una tupla, y los parámetros pueden tener valores por defecto. El bloque de la función se delimita **solo por indentación**, no por llaves.

---

## Qué aprendes

| Concepto | Para qué sirve |
|---|---|
| `def nombre(params):` | Declarar una función |
| `return valor` | Devolver un resultado |
| Parámetros con valor por defecto | Hacer parámetros opcionales |
| Docstring (`"""..."""`) | Documentar la función (visible con `help()`) |
| `return a, b` (tupla) | Devolver varios valores en una sola instrucción |
| Sin prototipo | No hay separación declaración/definición |

---

## C vs Python

El MISMO ejemplo — función que suma dos enteros y la llama:

| C | Python |
|---|---|
| `int suma(int a, int b) {` | `def suma(a, b):` |
| `    return a + b;` | `    return a + b` |
| `}` | _(fin de bloque por indentación)_ |
| `int main() {` | _(no hay main obligatorio)_ |
| `    int r = suma(3, 4);` | `r = suma(3, 4)` |
| `    printf("%d\n", r);` | `print(r)` |
| `    return 0;` | — |
| `}` | — |

Diferencias clave:

| Aspecto | C | Python |
|---|---|---|
| Tipo del retorno | `int suma(...)` — obligatorio | ninguno; Python infiere |
| Tipo de parámetros | `int a, int b` — obligatorio | solo el nombre |
| Delimitador de bloque | `{ }` | indentación (4 espacios) |
| Prototipo | necesario si la función va después de `main` | no existe |
| Devolver varios valores | struct o punteros | `return a, b` — tupla automática |
| Documentación | comentario manual | docstring `"""..."""` |

---

## Explicación

### Patrón básico

```python
def nombre_funcion(param1, param2):
    """Docstring: una frase que describe que hace."""
    # cuerpo
    return resultado
```

La indentación **es** la sintaxis. Si olvidas indentar, obtienes `IndentationError`.

### Parámetros con valor por defecto

```python
def potencia(base, exp=2):
    """Eleva base a exp; por defecto exp=2."""
    return base ** exp

print(potencia(3))     # 9  (exp usa el default)
print(potencia(3, 3))  # 27
```

Regla: los parámetros con default van **siempre al final** de la lista.

### Devolver varios valores

```python
def minmax(lista):
    """Devuelve (minimo, maximo) de la lista."""
    return min(lista), max(lista)

pequeno, grande = minmax([4, 1, 9, 2])
print(pequeno, grande)  # 1 9
```

`return a, b` crea una tupla `(a, b)`. El desempaquetado `x, y = funcion()` es idiomático en Python.

### Docstring

```python
def es_par(n):
    """Devuelve True si n es par, False si es impar."""
    return n % 2 == 0

help(es_par)   # muestra el docstring en consola
```

---

## Worked example

**Enunciado:** escribe `factorial(n)` que devuelva n! para n >= 0. Luego pide un número al usuario e imprime su factorial.

**Paso 1 — esquema de la función:**

```python
def factorial(n):
    """Devuelve n! (n factorial). n debe ser >= 0."""
```

**Paso 2 — caso base:** si `n == 0`, el resultado es 1.

```python
    if n == 0:
        return 1
```

**Paso 3 — caso general:** multiplicar n por factorial(n-1) (iterativo para evitar recursión por ahora).

```python
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado
```

**Paso 4 — llamada con input:**

```python
numero = int(input("Introduce un entero >= 0: "))
print(f"{numero}! = {factorial(numero)}")
```

**Función completa:**

```python
def factorial(n):
    """Devuelve n! (n factorial). n debe ser >= 0."""
    if n == 0:
        return 1
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado

numero = int(input("Introduce un entero >= 0: "))
print(f"{numero}! = {factorial(numero)}")
```

Ejecución de ejemplo:
```
Introduce un entero >= 0: 5
5! = 120
```

---

## Errores típicos de Python

1. **IndentationError por mezclar tabs y espacios.**
   Python 3 no permite mezclarlos. Usa siempre 4 espacios. Configura tu editor para insertar espacios al pulsar Tab.

2. **Olvidar `return` y usar el resultado.**
   ```python
   def doble(x):
       x * 2          # calcula pero NO devuelve nada

   print(doble(5))    # None  <-- sorpresa
   ```
   En C el compilador avisa; en Python el `None` silencioso pasa desapercibido.

3. **Parametros con default mutables (trampa clasica).**
   ```python
   def agregar(item, lista=[]):   # MAL: lista compartida entre llamadas
       lista.append(item)
       return lista

   # Correcto:
   def agregar(item, lista=None):
       if lista is None:
           lista = []
       lista.append(item)
       return lista
   ```

4. **No convertir `input()` antes de operar.**
   ```python
   n = input("Numero: ")
   print(factorial(n))   # TypeError: range() integer argument expected, not str
   ```
   Siempre `int(input(...))` o `float(input(...))`.

5. **Llamar a la funcion antes de definirla (en script).**
   En C el prototipo te salva. En Python el orden de ejecución del script importa: si llamas a `factorial(5)` en la línea 2 y defines `factorial` en la línea 10, obtienes `NameError`. Solución: pon las definiciones al principio, o usa el patrón `if __name__ == "__main__":`.

---

## Ejercicios

- [[Curso_Python/practica/04-funciones/ej01|Ej 01 — Escribe es_par(n) que devuelva True/False (verde)]]
- [[Curso_Python/practica/04-funciones/ej02|Ej 02 — Escribe max_de_dos(a, b) que devuelva el mayor (verde)]]
- [[Curso_Python/practica/04-funciones/ej03|Ej 03 — Escribe factorial(n) iterativo (amarillo)]]
- [[Curso_Python/practica/04-funciones/ej04|Ej 04 — Escribe potencia(base, exp=2) usando un bucle (sin **) (amarillo)]]
- [[Curso_Python/practica/04-funciones/ej05|Ej 05 — Escribe es_primo(n) que devuelva True/False (amarillo)]]
- [[Curso_Python/practica/04-funciones/ej06|Ej 06 — Escribe minmax(lista) que devuelva una tupla (mínimo, máximo) (rojo)]]

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/03-bucles]]
- [[Curso_Python/modelo/05-listas]]
