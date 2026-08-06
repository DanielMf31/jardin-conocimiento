---
title: "Módulo 08: Clases, dataclasses y archivos"
date: 2026-06-16
tags: [programacion/python, programacion/python/curso, programacion/oop, programacion/archivos]
aliases: [clases python, dataclasses, archivos python, OOP python desde C]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-python/modelo/08-clases-archivos.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-python/modelo/08-clases-archivos.md (se regenera con gen_course.py). -->

# Módulo 08: Clases, dataclasses y archivos

## Idea central

En C agrupas datos con `struct`; Python va más lejos: una **clase** agrupa datos *y* las funciones que los operan. `@dataclass` es un atajo para clases que son principalmente contenedores de datos. Los archivos se manejan con `open()` dentro de un bloque `with`, que garantiza cierre automático.

---

## Qué aprendes

| Concepto | Para qué sirve |
|---|---|
| `class` + `__init__` + `self` | Definir un tipo propio con datos y métodos |
| `@dataclass` | Crear clases contenedor sin escribir `__init__` a mano |
| `open()` + `with` | Abrir y cerrar archivos de forma segura |
| Modos `r`, `w`, `a` | Leer, sobreescribir o ampliar un archivo |
| `.read()`, `.readlines()`, `.write()` | Operaciones básicas de I/O sobre el archivo |

---

## C vs Python

### Struct vs clase básica

| C | Python |
|---|---|
| `struct Punto { float x; float y; };` | `class Punto:` |
| `Punto p; p.x = 3.0; p.y = 4.0;` | `p = Punto(3.0, 4.0)` |
| Función libre: `float dist(Punto a, Punto b)` | Método: `def distancia(self, otro):` |
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

## Explicación

### 1. Clase básica

```
class NombreClase:
    def __init__(self, param1, param2):   # constructor
        self.atrib1 = param1              # self = el propio objeto
        self.atrib2 = param2

    def mi_metodo(self):
        return self.atrib1
```

- `__init__` se llama automáticamente al hacer `NombreClase(...)`.
- `self` es siempre el primer parámetro de todo método (equivale al puntero implícito en C++).
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

Equivale a una clase normal con `__init__` escrito a mano, pero más corta y legible.

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

**Enunciado**: lee un archivo `numeros.txt` donde cada línea es un entero, suma todos y muestra el resultado.

```
# numeros.txt (contenido de ejemplo)
10
20
30
```

**Paso 1** — Abrir y leer líneas:
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

**Código completo**:
```python
with open("numeros.txt", "r") as f:
    total = sum(int(linea.strip()) for linea in f)
print(f"Suma: {total}")
```

---

## Errores típicos de Python

1. **Indentación inconsistente** — Python usa la indentación como sintaxis; mezclar tabs y espacios provoca `IndentationError`. Usa siempre 4 espacios.

2. **Olvidar `self` en los métodos** — `def metodo(x):` en vez de `def metodo(self, x):` provoca `TypeError` al llamarlo como `obj.metodo(5)` porque Python pasa el objeto como primer argumento automáticamente.

3. **Atributo creado fuera de `__init__`** — Si creas un atributo en un método que no se llama primero, otros métodos lo verán como inexistente (`AttributeError`). Inicializa todo en `__init__`.

4. **`open()` sin `with` y sin `close()`** — El archivo puede quedar abierto si hay una excepción antes de `f.close()`. Usa siempre `with open(...)`.

5. **`readlines()` incluye `\n`** — Cada línea termina con `\n`; hay que hacer `.strip()` o `.rstrip()` antes de convertir o comparar.

---

## Ejercicios

- [[Curso_Python/practica/08-clases-archivos/ej01|Ej 01 — Define una clase Punto(x, y) con un metodo distancia(otro) que devuelva… (verde)]]
- [[Curso_Python/practica/08-clases-archivos/ej02|Ej 02 — Usa @dataclass para definir Persona(nombre, edad) (verde)]]
- [[Curso_Python/practica/08-clases-archivos/ej03|Ej 03 — Pide el nombre de un archivo al usuario, leelo y muestra cuantas lineas… (amarillo)]]
- [[Curso_Python/practica/08-clases-archivos/ej04|Ej 04 — Pide frutas al usuario (línea vacía para terminar) y guárdalas en… (amarillo)]]
- [[Curso_Python/practica/08-clases-archivos/ej05|Ej 05 — Lee números de numeros.txt (uno por línea) y muestra suma, mínimo y… (amarillo)]]
- [[Curso_Python/practica/08-clases-archivos/ej06|Ej 06 — Implementa la clase Contador con metodos sumar(n), restar(n), reset() y… (rojo)]]

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/07-diccionarios-sets]]
- [[Curso_Python/modelo/09-puente-neetcode]]
