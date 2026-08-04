---
title: "Modulo 08: Clases, dataclasses y archivos"
date: 2026-06-16
tags: [programacion/python, programacion/python/curso, programacion/oop, programacion/archivos]
type: nota
status: en-progreso
source: claude-code
aliases: [clases python, dataclasses, archivos python, OOP python desde C]
---

# Modulo 08: Clases, dataclasses y archivos

## Idea central

En C agrupas datos con `struct`; Python va mas lejos: una **clase** agrupa datos *y* las funciones que los operan. `@dataclass` es un atajo para clases que son principalmente contenedores de datos. Los archivos se manejan con `open()` dentro de un bloque `with`, que garantiza cierre automatico.

---

## Que aprendes

| Concepto | Para que sirve |
|---|---|
| `class` + `__init__` + `self` | Definir un tipo propio con datos y metodos |
| `@dataclass` | Crear clases contenedor sin escribir `__init__` a mano |
| `open()` + `with` | Abrir y cerrar archivos de forma segura |
| Modos `r`, `w`, `a` | Leer, sobreescribir o ampliar un archivo |
| `.read()`, `.readlines()`, `.write()` | Operaciones basicas de I/O sobre el archivo |

---

## C vs Python

### Struct vs clase basica

| C | Python |
|---|---|
| `struct Punto { float x; float y; };` | `class Punto:` |
| `Punto p; p.x = 3.0; p.y = 4.0;` | `p = Punto(3.0, 4.0)` |
| Funcion libre: `float dist(Punto a, Punto b)` | Metodo: `def distancia(self, otro):` |
| Sin cierre automatico de recursos | `with open(...) as f:` cierra solo |

```c
// C — struct + funcion libre
#include <stdio.h>
#include <math.h>

typedef struct { float x; float y; } Punto;

float dist(Punto a, Punto b) {
    return sqrt((a.x-b.x)*(a.x-b.x) + (a.y-b.y)*(a.y-b.y));
}

int main(void) {
    Punto p = {3.0, 4.0};
    Punto q = {0.0, 0.0};
    printf("%.2f\n", dist(p, q));
    return 0;
}
```

```python
# Python — clase con metodo
import math

class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distancia(self, otro):
        return math.sqrt((self.x - otro.x)**2 + (self.y - otro.y)**2)

p = Punto(3.0, 4.0)
q = Punto(0.0, 0.0)
print(f"{p.distancia(q):.2f}")   # 5.00
```

### Archivos

| C | Python |
|---|---|
| `FILE *f = fopen("a.txt","r");` | `with open("a.txt", "r") as f:` |
| `fclose(f);` — manual, olvidable | El `with` lo cierra automaticamente |
| `fgets(buf, 256, f);` | `f.read()` / `f.readlines()` |
| `fprintf(f, "%s", s);` | `f.write(s)` |

---

## Explicacion

### 1. Clase basica

```
class NombreClase:
    def __init__(self, param1, param2):   # constructor
        self.atrib1 = param1              # self = el propio objeto
        self.atrib2 = param2

    def mi_metodo(self):
        return self.atrib1
```

- `__init__` se llama automaticamente al hacer `NombreClase(...)`.
- `self` es siempre el primer parametro de todo metodo (equivale al puntero implicito en C++).
- Los atributos no se declaran; se crean con `self.nombre = valor` dentro de `__init__`.

### 2. @dataclass

Para clases que son principalmente contenedores de campos, `@dataclass` genera `__init__`, `__repr__` y `__eq__` automaticamente:

```python
from dataclasses import dataclass

@dataclass
class Persona:
    nombre: str
    edad: int

p = Persona("Ana", 30)
print(p)          # Persona(nombre='Ana', edad=30)
print(p.nombre)   # Ana
```

Equivale a una clase normal con `__init__` escrito a mano, pero mas corta y legible.

### 3. Archivos con open() y with

```python
# Leer todo el contenido
with open("datos.txt", "r") as f:
    contenido = f.read()          # string completo

# Leer linea a linea (lista de strings)
with open("datos.txt", "r") as f:
    lineas = f.readlines()        # ["linea1\n", "linea2\n", ...]

# Escribir (sobreescribe si existe)
with open("salida.txt", "w") as f:
    f.write("hola\n")

# Anadir al final sin sobreescribir
with open("log.txt", "a") as f:
    f.write("nueva entrada\n")
```

| Modo | Efecto |
|---|---|
| `"r"` | Leer; error si no existe |
| `"w"` | Escribir desde cero (borra si existe) |
| `"a"` | Anadir al final |

---

## Worked example

**Enunciado**: lee un archivo `numeros.txt` donde cada linea es un entero, suma todos y muestra el resultado.

```
# numeros.txt (contenido de ejemplo)
10
20
30
```

**Paso 1** — Abrir y leer lineas:
```python
with open("numeros.txt", "r") as f:
    lineas = f.readlines()
# lineas = ["10\n", "20\n", "30\n"]
```

**Paso 2** — Limpiar espacios/saltos y convertir a entero:
```python
numeros = [int(linea.strip()) for linea in lineas]
# numeros = [10, 20, 30]
```

**Paso 3** — Sumar:
```python
total = sum(numeros)
print(f"Suma: {total}")   # Suma: 60
```

**Codigo completo**:
```python
with open("numeros.txt", "r") as f:
    total = sum(int(linea.strip()) for linea in f)
print(f"Suma: {total}")
```

---

## Errores tipicos de Python

1. **Indentacion inconsistente** — Python usa la indentacion como sintaxis; mezclar tabs y espacios provoca `IndentationError`. Usa siempre 4 espacios.

2. **Olvidar `self` en los metodos** — `def metodo(x):` en vez de `def metodo(self, x):` provoca `TypeError` al llamarlo como `obj.metodo(5)` porque Python pasa el objeto como primer argumento automaticamente.

3. **Atributo creado fuera de `__init__`** — Si creas un atributo en un metodo que no se llama primero, otros metodos lo veran como inexistente (`AttributeError`). Inicializa todo en `__init__`.

4. **`open()` sin `with` y sin `close()`** — El archivo puede quedar abierto si hay una excepcion antes de `f.close()`. Usa siempre `with open(...)`.

5. **`readlines()` incluye `\n`** — Cada linea termina con `\n`; hay que hacer `.strip()` o `.rstrip()` antes de convertir o comparar.

---

## Ejercicios

> Los archivos de practica estan en `practica/08-clases-archivos/`.
> Cada ejercicio tiene un esqueleto `ejNN_practica.py` y la solucion `ejNN_modelo.py`.

---

**Ej01** — Clase `Punto` con metodo `distancia`
- Dificultad: verde
- Enunciado: Define una clase `Punto(x, y)` con un metodo `distancia(otro)` que devuelva la distancia euclidea entre dos puntos.
- Salida esperada:
  ```
  Distancia entre (3,4) y (0,0): 5.00
  Distancia entre (1,1) y (4,5): 5.00
  ```
- Archivos: `practica/08-clases-archivos/ej01_practica.py` · `ej01_modelo.py`

---

**Ej02** — `@dataclass Persona`
- Dificultad: verde
- Enunciado: Usa `@dataclass` para definir `Persona(nombre, edad)`. Crea dos instancias y muestralas con `print()` y accediendo a sus atributos.
- Salida esperada:
  ```
  Persona(nombre='Ana', edad=30)
  Persona(nombre='Luis', edad=25)
  Ana tiene 30 anos.
  Luis tiene 25 anos.
  ```
- Archivos: `practica/08-clases-archivos/ej02_practica.py` · `ej02_modelo.py`

---

**Ej03** — Contar lineas de un archivo
- Dificultad: amarillo
- Enunciado: Pide al usuario el nombre de un archivo (asume que existe), leelo y muestra cuantas lineas tiene.
- Salida esperada (para un archivo con 5 lineas):
  ```
  Nombre del archivo: datos.txt
  El archivo tiene 5 lineas.
  ```
- Archivos: `practica/08-clases-archivos/ej03_practica.py` · `ej03_modelo.py`

---

**Ej04** — Escribir lista de lineas a un archivo
- Dificultad: amarillo
- Enunciado: Pide al usuario varias frutas (una por linea, termina con linea vacia) y guardalas en `frutas.txt`. Confirma cuantas se guardaron.
- Salida esperada:
  ```
  Fruta (Enter para terminar): manzana
  Fruta (Enter para terminar): pera
  Fruta (Enter para terminar):
  Guardadas 2 frutas en frutas.txt.
  ```
- Archivos: `practica/08-clases-archivos/ej04_practica.py` · `ej04_modelo.py`

---

**Ej05** — Leer numeros de un archivo y sumarlos
- Dificultad: amarillo
- Enunciado: Dado un archivo `numeros.txt` con un entero por linea (el ejercicio lo crea primero), leelo y muestra la suma, el minimo y el maximo.
- Salida esperada:
  ```
  Suma: 60  |  Min: 10  |  Max: 30
  ```
- Archivos: `practica/08-clases-archivos/ej05_practica.py` · `ej05_modelo.py`

---

**Ej06** — Clase `Contador` con metodos
- Dificultad: rojo
- Enunciado: Implementa una clase `Contador` con un valor inicial (por defecto 0) y metodos `sumar(n)`, `restar(n)`, `reset()` y `valor()`. Demuestra su uso con varias operaciones.
- Salida esperada:
  ```
  Valor inicial: 0
  Tras sumar 5: 5
  Tras sumar 3: 8
  Tras restar 2: 6
  Tras reset: 0
  ```
- Archivos: `practica/08-clases-archivos/ej06_practica.py` · `ej06_modelo.py`

---

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/07-diccionarios-sets]]
- [[Curso_Python/modelo/09-puente-neetcode]]
