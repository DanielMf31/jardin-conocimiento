---
title: "Módulo 06 — Cadenas: transformar y formatear"
date: 2026-06-16
tags: [programacion/python, programacion/curso, programacion/python/cadenas]
aliases: [cadenas python, strings python, formatear strings, slugify python]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-python/modelo/06-cadenas.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-python/modelo/06-cadenas.md (se regenera con gen_course.py). -->

# Módulo 06 — Cadenas: transformar y formatear

## Idea central

En C un string es un `char[]` terminado en `\0` que manipulas carácter a carácter con `<string.h>`. En Python `str` es un tipo de primera clase, inmutable, que trae decenas de métodos de transformación (`.upper()`, `.split()`, `.replace()`...) listos para usar en una línea.

---

## Qué aprendes

| Concepto | Para qué |
|---|---|
| Indexar y slicing de strings | Acceder a un carácter o a un trozo (`s[0]`, `s[::-1]`) |
| `.upper() / .lower() / .title() / .capitalize()` | Cambiar el caso de las letras |
| `.strip() / .replace()` | Limpiar espacios al borde y sustituir subcadenas |
| `.split() / .join()` | Partir un string en lista y unir una lista en string |
| `.find()` / `in` | Buscar una subcadena o comprobar si existe |
| f-strings y formato (`:.2f`, `:,`, `:>10`, `ljust`, `rjust`) | Componer y alinear texto con valores |
| `.isdigit() / .isalpha()` | Validar el contenido de un string |
| Recorrer con `for c in s` | Iterar carácter a carácter sin índice |

---

## C vs Python

El mismo problema: **pasar una frase a mayúsculas y contar sus vocales**.

| Aspecto | C | Python |
|---|---|---|
| Tipo | `char s[] = "hola mundo";` | `s = "hola mundo"` |
| Mayúsculas | bucle con `toupper(s[i])` | `s.upper()` |
| Longitud | `strlen(s)` | `len(s)` |
| Recorrer caracteres | `for(int i=0;s[i];i++)` | `for c in s:` |
| Contar vocales | `if` por cada carácter | `sum(c in "aeiou" for c in s)` |
| Mutabilidad | mutable (modificas el buffer) | inmutable (devuelve copia) |

**Código C completo:**
```c
#include <stdio.h>
#include <ctype.h>
int main(void) {
    char s[] = "hola mundo";
    int vocales = 0;
    for (int i = 0; s[i] != '\0'; i++) {
        char c = tolower(s[i]);
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u')
            vocales++;
        s[i] = toupper(s[i]);   // mutamos el buffer en sitio
    }
    printf("%s\n", s);          // HOLA MUNDO
    printf("Vocales: %d\n", vocales);  // Vocales: 4
    return 0;
}
```

**Código Python equivalente:**
```python
s = "hola mundo"
mayus = s.upper()                              # devuelve copia nueva
vocales = sum(c in "aeiou" for c in s.lower()) # comprehension + sum
print(mayus)            # HOLA MUNDO
print(f"Vocales: {vocales}")   # Vocales: 4
```

---

## Explicación

### 1. Inmutabilidad e indexar/slicing

```python
s = "python"
print(s[0])      # p     (base 0, como C)
print(s[-1])     # n     (indice negativo: desde el final)
print(s[0:3])    # pyt   (de 0 hasta 2, el 3 no se incluye)
print(s[::-1])   # nohtyp  (invertir con paso -1)
# s[0] = "P"     # ERROR: los str son inmutables
```

**Patrón:** `s[inicio:fin:paso]`, igual que en listas. No puedes asignar a un índice: para "cambiar" un string creas uno nuevo.

### 2. Mayúsculas, minúsculas y título

```python
s = "hola mundo cruel"
print(s.upper())        # HOLA MUNDO CRUEL
print(s.lower())        # hola mundo cruel
print(s.title())        # Hola Mundo Cruel  (primera letra de cada palabra)
print(s.capitalize())   # Hola mundo cruel  (solo la primera del todo)
```

Todos devuelven una **copia nueva**; el original no cambia.

### 3. strip y replace

```python
s = "   hola mundo   "
print(s.strip())            # "hola mundo"  (quita espacios al borde, no internos)
print("xxholaxx".strip("x"))# "hola"        (quita los caracteres indicados)

texto = "me gusta C, C es rapido"
print(texto.replace("C", "Python"))  # "me gusta Python, Python es rapido"
```

`.strip()` solo quita del principio y del final. `.replace(viejo, nuevo)` sustituye TODAS las apariciones y devuelve copia.

### 4. split y join

```python
frase = "uno dos tres"
partes = frase.split()        # ["uno", "dos", "tres"]   (por espacios)
csv = "a,b,c".split(",")      # ["a", "b", "c"]           (por un separador)

palabras = ["hola", "mundo"]
print(" ".join(palabras))     # "hola mundo"
print("-".join(palabras))     # "hola-mundo"
```

`split()` string -> lista. `sep.join(lista)` lista -> string. El separador es el string sobre el que llamas `.join`.

### 5. Buscar: in, find, count

```python
frase = "el gato y el perro"
print("gato" in frase)    # True   (forma mas comun y legible)
print(frase.find("perro"))# 11     (indice de la primera aparicion)
print(frase.find("pez"))  # -1     (no encontrado: devuelve -1, no error)
print(frase.count("el"))  # 2      (cuantas veces aparece)
```

`in` para "¿existe?". `.find()` para "¿en qué posición?" (`-1` si no está). `.count()` para contar.

### 6. f-strings y formateo

```python
precio = 1299.5
print(f"Total: {precio:.2f}")    # Total: 1299.50     (2 decimales)
print(f"Total: {precio:,.2f}")   # Total: 1,299.50    (separador de miles)

nombre = "Ana"
print(f"[{nombre:>10}]")         # [       Ana]   (alinear a la derecha, ancho 10)
print(f"[{nombre:<10}]")         # [Ana       ]   (alinear a la izquierda)
print(f"[{nombre:^10}]")         # [   Ana    ]   (centrar)

# Equivalente con metodos
print(nombre.ljust(10) + "|")    # "Ana       |"
print(nombre.rjust(10) + "|")    # "       Ana|"
```

`{valor:formato}` dentro de la f-string. `.2f` decimales, `,` miles, `>`/`<`/`^` alineación con ancho. `ljust`/`rjust` hacen lo mismo como métodos.

### 7. Comprobaciones: isdigit, isalpha

```python
print("123".isdigit())    # True   (solo digitos)
print("12a".isdigit())    # False
print("hola".isalpha())   # True   (solo letras)
print("hola1".isalpha())  # False

edad = input("Edad: ")
if edad.isdigit():
    print(int(edad) + 1)
else:
    print("Eso no es un numero")
```

Útiles para validar `input()` antes de convertir a `int`.

### 8. Recorrer carácter a carácter

```python
s = "abc"
for c in s:
    print(c)        # a, luego b, luego c

# Con indice si lo necesitas
for i, c in enumerate(s):
    print(i, c)     # 0 a / 1 b / 2 c
```

Un `for` sobre un string itera sus caracteres directamente, sin manejar índices ni `\0`.

---

## Worked example

**Problema (slugify):** convertir un título como `"  Hola Mundo en Python  "` en `hola-mundo-en-python`. Un "slug" es el texto apto para una URL: minúsculas, sin espacios al borde, espacios convertidos en guiones.

**Paso 1 — quitar espacios del borde:**
```python
titulo = "  Hola Mundo en Python  "
limpio = titulo.strip()
print(repr(limpio))   # 'Hola Mundo en Python'
```

`.strip()` elimina los espacios del principio y del final (los internos se quedan).

**Paso 2 — pasar a minúsculas:**
```python
minus = limpio.lower()
print(minus)   # hola mundo en python
```

**Paso 3 — reemplazar espacios por guiones:**
```python
slug = minus.replace(" ", "-")
print(slug)    # hola-mundo-en-python
```

`.replace(" ", "-")` cambia todos los espacios internos por `-`.

**Paso 4 — encadenar en una línea:**
Como cada metodo devuelve un string nuevo, puedes encadenarlos:
```python
slug = titulo.strip().lower().replace(" ", "-")
```

**Programa completo:**
```python
titulo = "  Hola Mundo en Python  "
slug = titulo.strip().lower().replace(" ", "-")
print(slug)    # hola-mundo-en-python
```

---

## Errores típicos de Python

| # | Error | Ejemplo malo | Correcto |
|---|---|---|---|
| 1 | Los strings son inmutables | `s[0] = "x"` lanza `TypeError` | crear copia: `s = "x" + s[1:]` |
| 2 | `input()` siempre devuelve `str` | `edad = input(); edad + 1` | `edad = int(input()); edad + 1` |
| 3 | `.replace()` devuelve copia, no muta | `s.replace("a","b")` sin asignar | `s = s.replace("a", "b")` |
| 4 | `.strip()` no quita espacios internos | esperar que `"a b".strip()` dé `"ab"` | usar `.replace(" ", "")` para internos |
| 5 | Comparar sin normalizar el caso | `"Ana" == "ana"` da `False` | `a.lower() == b.lower()` |

---

## Ejercicios

- [[Curso_Python/practica/06-cadenas/ej01|Ej 01 — Lee una palabra e imprimela al reves usando slicing (verde)]]
- [[Curso_Python/practica/06-cadenas/ej02|Ej 02 — Di si una palabra es palíndromo ignorando mayúsculas/minúsculas (verde)]]
- [[Curso_Python/practica/06-cadenas/ej03|Ej 03 — Cuenta las vocales de una frase (mayúsculas y minúsculas) (verde)]]
- [[Curso_Python/practica/06-cadenas/ej04|Ej 04 — Dado un texto con espacios sobrantes al borde, devuelvelo en formato… (amarillo)]]
- [[Curso_Python/practica/06-cadenas/ej05|Ej 05 — Convierte un titulo a slug (minusculas, sin espacios al borde, espacios… (amarillo)]]
- [[Curso_Python/practica/06-cadenas/ej06|Ej 06 — Pide nombre y apellido y devuelve APELLIDO, Nombre (amarillo)]]
- [[Curso_Python/practica/06-cadenas/ej07|Ej 07 — Reemplaza todas las apariciones de una palabra por asteriscos de su… (amarillo)]]
- [[Curso_Python/practica/06-cadenas/ej08|Ej 08 — Imprime una tabla alineada de productos y precios con formato numérico (rojo)]]

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/05-listas]]
- [[Curso_Python/modelo/07-diccionarios-sets]]
