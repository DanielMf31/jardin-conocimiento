---
title: "Módulo 07: Diccionarios y Sets"
date: 2026-06-16
tags: [programacion/python, programacion/python/curso, programacion/estructuras-datos]
type: nota
status: en-progreso
source: claude-code
aliases: [dict Python, set Python, hash map Python, modulo-07-python]
---

# Módulo 07: Diccionarios y Sets

## Idea central

Un **diccionario** (`dict`) es una tabla hash que mapea claves a valores en tiempo O(1). Un **set** es una colección de claves únicas sin valores. Son las estructuras más importantes para resolver problemas de tipo NeetCode/LeetCode: contar frecuencias, detectar duplicados, agrupar, buscar en O(1).

---

## Qué aprendes

| Concepto | Para qué sirve |
|---|---|
| `dict` — crear y acceder | Almacenar pares clave→valor, buscar en O(1) |
| `.get(clave, default)` | Acceder sin lanzar `KeyError` |
| `.keys()` / `.values()` / `.items()` | Iterar sobre partes del dict |
| `clave in dict` | Comprobar existencia en O(1) |
| Añadir / actualizar entradas | Construir dicts dinámicamente |
| `set` — elementos únicos | Eliminar duplicados, test de pertenencia O(1) |
| `|` (unión) y `&` (intersección) | Operaciones de conjuntos |
| `collections.Counter` | Contar frecuencias de forma idiomática |

---

## C vs Python

El equivalente en C de un diccionario es una **tabla hash manual** (o un array paralelo clave-valor), que requiere ~40 líneas. Python lo da en una línea.

| Operación | C | Python |
|---|---|---|
| Crear tabla clave→valor | `struct Entry { char *key; int val; };` (implementación manual) | `d = {"a": 1, "b": 2}` |
| Leer valor | `hash_get(table, "a")` (función propia) | `d["a"]` o `d.get("a", 0)` |
| Escribir/actualizar | `hash_set(table, "a", 3)` | `d["a"] = 3` |
| Comprobar existencia | `hash_contains(table, "a")` | `"a" in d` |
| Iterar pares | bucle sobre array de `Entry` | `for k, v in d.items():` |
| Conjunto sin duplicados | array + búsqueda lineal O(n) | `s = {1, 2, 3}` — O(1) test |
| Unión / intersección | bucles manuales | `s1 \| s2`, `s1 & s2` |
| Contar frecuencias | `freq[c - 'a']++` (solo chars) | `Counter(lista)` — cualquier tipo |

---

## Explicación

### Dict — patrón y sintaxis

```python
# Crear
d = {}                        # dict vacío
d = {"nombre": "Ana", "edad": 25}

# Leer — dos formas
print(d["nombre"])            # KeyError si no existe
print(d.get("altura", 0))     # devuelve 0 si no existe (nunca lanza error)

# Escribir / actualizar
d["edad"] = 26                # actualiza si existe, crea si no
d["ciudad"] = "Madrid"        # nueva clave

# Comprobar existencia
if "nombre" in d:
    print("tiene nombre")

# Iterar
for clave in d:               # itera claves
    print(clave, d[clave])

for clave, valor in d.items():  # itera pares (más legible)
    print(f"{clave}: {valor}")

print(list(d.keys()))         # ["nombre", "edad", "ciudad"]
print(list(d.values()))       # ["Ana", 26, "Madrid"]
```

**Patrón frecuencia** (el más usado en entrevistas):

```python
# Contar sin Counter
freq = {}
for x in ["a", "b", "a", "c", "b", "a"]:
    freq[x] = freq.get(x, 0) + 1
# freq == {"a": 3, "b": 2, "c": 1}
```

### Set — patrón y sintaxis

```python
s = {1, 2, 3}        # set literal  (¡{} solo crea dict vacío, no set!)
s = set()            # set vacío — OBLIGATORIO usar set()

s.add(4)             # añadir
s.remove(4)          # eliminar (KeyError si no existe)
s.discard(99)        # eliminar sin error

print(2 in s)        # True — O(1)

a = {1, 2, 3}
b = {2, 3, 4}
print(a | b)         # {1, 2, 3, 4}  unión
print(a & b)         # {2, 3}        intersección
print(a - b)         # {1}           diferencia
```

### collections.Counter

```python
from collections import Counter

palabras = ["sol", "luna", "sol", "sol", "luna"]
c = Counter(palabras)
print(c)                    # Counter({'sol': 3, 'luna': 2})
print(c["sol"])             # 3
print(c.most_common(1))     # [('sol', 3)]
```

`Counter` es un `dict` con comportamiento extra: devuelve 0 para claves inexistentes (no `KeyError`).

---

## Worked example

**Problema:** dada una frase, agrupar las palabras por su primera letra y mostrarlas ordenadas.

```
Entrada: "oso ardilla abeja ballena aguila"
Salida:
a: abeja, aguila, ardilla
b: ballena
o: oso
```

**Paso 1 — pensar la estructura:**
Necesito `dict` donde cada clave es una letra y el valor es una lista de palabras.

**Paso 2 — código:**

```python
frase = "oso ardilla abeja ballena aguila"
palabras = frase.split()           # ["oso", "ardilla", ...]

grupos = {}
for palabra in palabras:
    inicial = palabra[0]           # primera letra
    if inicial not in grupos:
        grupos[inicial] = []       # crear lista vacía la primera vez
    grupos[inicial].append(palabra)

# Ordenar el dict por clave para salida limpia
for letra in sorted(grupos):
    palabras_ordenadas = sorted(grupos[letra])
    print(f"{letra}: {', '.join(palabras_ordenadas)}")
```

**Paso 3 — trazado mental:**

- `"oso"` → inicial `"o"` → `grupos["o"] = ["oso"]`
- `"ardilla"` → `"a"` → `grupos["a"] = ["ardilla"]`
- `"abeja"` → `"a"` → `grupos["a"] = ["ardilla", "abeja"]`
- ...

**Paso 4 — salida:**
```
a: abeja, aguila, ardilla
b: ballena
o: oso
```

---

## Errores típicos de Python

| # | Error | Ejemplo incorrecto | Corrección |
|---|---|---|---|
| 1 | `KeyError` al leer clave inexistente | `d["x"]` cuando `"x"` no está | `d.get("x", valor_por_defecto)` |
| 2 | Crear set vacío con `{}` | `s = {}` → es un `dict`, no set | `s = set()` |
| 3 | Olvidar que `input()` devuelve `str` | `n = input()` luego `freq[n + 1]` | convertir primero si es número |
| 4 | Iterar el dict mientras se modifica | `for k in d: del d[k]` → `RuntimeError` | iterar `list(d.keys())` o construir nuevo dict |
| 5 | Indentación dentro del `for` | cuerpo del bucle al nivel 0 | todo el cuerpo debe estar sangrado 4 espacios |

---

## Ejercicios

Todos los archivos están en `practica/07-diccionarios-sets/`.

| # | Enunciado | Dificultad | Salida de ejemplo |
|---|---|---|---|
| 01 | Cuenta la frecuencia de cada palabra en una frase introducida por el usuario. Muestra cada palabra y su cuenta. | (facil) Verde | `hola: 2`, `mundo: 1` |
| 02 | Comprueba si dos palabras son anagramas comparando sus frecuencias de letras (usa `Counter` o dict manual). | (media) Amarillo | `"amor" y "roma" → SÍ son anagramas` |
| 03 | Dada una lista de números con duplicados (hardcoded), devuelve los elementos únicos usando un `set`. | (facil) Verde | `Únicos: {1, 2, 3, 5}` |
| 04 | Pide dos frases al usuario. Muestra las palabras que aparecen en AMBAS frases (intersección de sets). | (media) Amarillo | `Palabras comunes: {'el', 'gato'}` |
| 05 | Two-sum básico: dada una lista de enteros y un objetivo `target`, encuentra los dos índices cuya suma es `target` usando un dict. | (dificil) Rojo | `[2, 7, 11, 15], target=9 → [0, 1]` |
| 06 | Agrupa palabras de una frase por su primera letra y muéstralas ordenadas (igual que el worked example pero el usuario introduce la frase). | (media) Amarillo | `a: abeja, aguila` / `b: ballena` |

- Esqueleto de práctica: `practica/07-diccionarios-sets/ejNN_practica.py`
- Solución modelo: `practica/07-diccionarios-sets/ejNN_modelo.py`

---

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/06-cadenas]]
- [[Curso_Python/modelo/08-clases-archivos]]
