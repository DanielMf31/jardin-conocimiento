---
title: "Modulo 04: Funciones en Python"
date: 2026-06-16
tags: [programacion/python, programacion/curso, programacion/funciones]
type: nota
status: en-progreso
source: claude-code
aliases: [funciones python, def python, return python, docstrings]
---

# Modulo 04: Funciones en Python

## Idea central

En Python una funcion se define con `def`, no necesita prototipo, puede devolver varios valores a la vez con una tupla, y los parametros pueden tener valores por defecto. El bloque de la funcion se delimita **solo por indentacion**, no por llaves.

---

## Que aprendes

| Concepto | Para que sirve |
|---|---|
| `def nombre(params):` | Declarar una funcion |
| `return valor` | Devolver un resultado |
| Parametros con valor por defecto | Hacer parametros opcionales |
| Docstring (`"""..."""`) | Documentar la funcion (visible con `help()`) |
| `return a, b` (tupla) | Devolver varios valores en una sola instruccion |
| Sin prototipo | No hay separacion declaracion/definicion |

---

## C vs Python

El MISMO ejemplo — funcion que suma dos enteros y la llama:

| C | Python |
|---|---|
| `int suma(int a, int b) {` | `def suma(a, b):` |
| `    return a + b;` | `    return a + b` |
| `}` | _(fin de bloque por indentacion)_ |
| `int main() {` | _(no hay main obligatorio)_ |
| `    int r = suma(3, 4);` | `r = suma(3, 4)` |
| `    printf("%d\n", r);` | `print(r)` |
| `    return 0;` | — |
| `}` | — |

Diferencias clave:

| Aspecto | C | Python |
|---|---|---|
| Tipo del retorno | `int suma(...)` — obligatorio | ninguno; Python infiere |
| Tipo de parametros | `int a, int b` — obligatorio | solo el nombre |
| Delimitador de bloque | `{ }` | indentacion (4 espacios) |
| Prototipo | necesario si la funcion va despues de `main` | no existe |
| Devolver varios valores | struct o punteros | `return a, b` — tupla automatica |
| Documentacion | comentario manual | docstring `"""..."""` |

---

## Explicacion

### Patron basico

```python
def nombre_funcion(param1, param2):
    """Docstring: una frase que describe que hace."""
    # cuerpo
    return resultado
```

La indentacion **es** la sintaxis. Si olvidas indentar, obtienes `IndentationError`.

### Parametros con valor por defecto

```python
def potencia(base, exp=2):
    """Eleva base a exp; por defecto exp=2."""
    return base ** exp

print(potencia(3))     # 9  (exp usa el default)
print(potencia(3, 3))  # 27
```

Regla: los parametros con default van **siempre al final** de la lista.

### Devolver varios valores

```python
def minmax(lista):
    """Devuelve (minimo, maximo) de la lista."""
    return min(lista), max(lista)

pequeno, grande = minmax([4, 1, 9, 2])
print(pequeno, grande)  # 1 9
```

`return a, b` crea una tupla `(a, b)`. El desempaquetado `x, y = funcion()` es idiomatico en Python.

### Docstring

```python
def es_par(n):
    """Devuelve True si n es par, False si es impar."""
    return n % 2 == 0

help(es_par)   # muestra el docstring en consola
```

---

## Worked example

**Enunciado:** escribe `factorial(n)` que devuelva n! para n >= 0. Luego pide un numero al usuario e imprime su factorial.

**Paso 1 — esquema de la funcion:**

```python
def factorial(n):
    """Devuelve n! (n factorial). n debe ser >= 0."""
```

**Paso 2 — caso base:** si `n == 0`, el resultado es 1.

```python
    if n == 0:
        return 1
```

**Paso 3 — caso general:** multiplicar n por factorial(n-1) (iterativo para evitar recursion por ahora).

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

**Funcion completa:**

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

Ejecucion de ejemplo:
```
Introduce un entero >= 0: 5
5! = 120
```

---

## Errores tipicos de Python

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
   En C el prototipo te salva. En Python el orden de ejecucion del script importa: si llamas a `factorial(5)` en la linea 2 y defines `factorial` en la linea 10, obtienes `NameError`. Solucion: pon las definiciones al principio, o usa el patron `if __name__ == "__main__":`.

---

## Ejercicios

Cada ejercicio tiene dos ficheros en `practica/04-funciones/`:

| N | Enunciado | Dificultad | Salida esperada (ejemplo) |
|---|---|---|---|
| 01 | Escribe `es_par(n)` que devuelva `True`/`False`. Pide un numero al usuario e imprime si es par o impar. | (facil) facil | `8 es par: True` |
| 02 | Escribe `max_de_dos(a, b)` que devuelva el mayor. Pide dos numeros e imprime el mayor (sin usar `max()`). | (facil) facil | `El mayor de 7 y 3 es: 7` |
| 03 | Escribe `factorial(n)` iterativo. Pide n al usuario e imprime n!. | (media) medio | `5! = 120` |
| 04 | Escribe `potencia(base, exp=2)` usando un bucle (sin `**`). Pide base y exponente; si el usuario no da exponente, usa 2. | (media) medio | `3 ^ 4 = 81` |
| 05 | Escribe `es_primo(n)` que devuelva `True`/`False`. Pide un numero e indica si es primo. | (media) medio | `7 es primo: True` |
| 06 | Escribe `minmax(lista)` que devuelva una tupla `(minimo, maximo)`. Pide al usuario 5 numeros separados por espacios, llama a la funcion e imprime el resultado. | (dificil) avanzado | `Min: 1  Max: 9` |

Ficheros:
- `practica/04-funciones/ej01_practica.py` / `ej01_modelo.py`
- `practica/04-funciones/ej02_practica.py` / `ej02_modelo.py`
- `practica/04-funciones/ej03_practica.py` / `ej03_modelo.py`
- `practica/04-funciones/ej04_practica.py` / `ej04_modelo.py`
- `practica/04-funciones/ej05_practica.py` / `ej05_modelo.py`
- `practica/04-funciones/ej06_practica.py` / `ej06_modelo.py`

---

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/03-bucles]]
- [[Curso_Python/modelo/05-listas]]
