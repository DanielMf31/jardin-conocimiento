---
title: "Modulo 06 — Cadenas: transformar y formatear"
date: 2026-06-16
tags: [programacion/python, programacion/curso, programacion/python/cadenas]
type: nota
status: en-progreso
source: claude-code
aliases: [cadenas python, strings python, formatear strings, slugify python]
---

# Modulo 06 — Cadenas: transformar y formatear

## Idea central

En C un string es un `char[]` terminado en `\0` que manipulas caracter a caracter con `<string.h>`. En Python `str` es un tipo de primera clase, inmutable, que trae decenas de metodos de transformacion (`.upper()`, `.split()`, `.replace()`...) listos para usar en una linea.

---

## Que aprendes

| Concepto | Para que |
|---|---|
| Indexar y slicing de strings | Acceder a un caracter o a un trozo (`s[0]`, `s[::-1]`) |
| `.upper() / .lower() / .title() / .capitalize()` | Cambiar el caso de las letras |
| `.strip() / .replace()` | Limpiar espacios al borde y sustituir subcadenas |
| `.split() / .join()` | Partir un string en lista y unir una lista en string |
| `.find()` / `in` | Buscar una subcadena o comprobar si existe |
| f-strings y formato (`:.2f`, `:,`, `:>10`, `ljust`, `rjust`) | Componer y alinear texto con valores |
| `.isdigit() / .isalpha()` | Validar el contenido de un string |
| Recorrer con `for c in s` | Iterar caracter a caracter sin indice |

---

## C vs Python

El mismo problema: **pasar una frase a mayusculas y contar sus vocales**.

| Aspecto | C | Python |
|---|---|---|
| Tipo | `char s[] = "hola mundo";` | `s = "hola mundo"` |
| Mayusculas | bucle con `toupper(s[i])` | `s.upper()` |
| Longitud | `strlen(s)` | `len(s)` |
| Recorrer caracteres | `for(int i=0;s[i];i++)` | `for c in s:` |
| Contar vocales | `if` por cada caracter | `sum(c in "aeiou" for c in s)` |
| Mutabilidad | mutable (modificas el buffer) | inmutable (devuelve copia) |

**Codigo C completo:**
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

**Codigo Python equivalente:**
```python
s = "hola mundo"
mayus = s.upper()                              # devuelve copia nueva
vocales = sum(c in "aeiou" for c in s.lower()) # comprehension + sum
print(mayus)            # HOLA MUNDO
print(f"Vocales: {vocales}")   # Vocales: 4
```

---

## Explicacion

### 1. Inmutabilidad e indexar/slicing

```python
s = "python"
print(s[0])      # p     (base 0, como C)
print(s[-1])     # n     (indice negativo: desde el final)
print(s[0:3])    # pyt   (de 0 hasta 2, el 3 no se incluye)
print(s[::-1])   # nohtyp  (invertir con paso -1)
# s[0] = "P"     # ERROR: los str son inmutables
```

**Patron:** `s[inicio:fin:paso]`, igual que en listas. No puedes asignar a un indice: para "cambiar" un string creas uno nuevo.

### 2. Mayusculas, minusculas y titulo

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

`in` para "¿existe?". `.find()` para "¿en que posicion?" (`-1` si no esta). `.count()` para contar.

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

`{valor:formato}` dentro de la f-string. `.2f` decimales, `,` miles, `>`/`<`/`^` alineacion con ancho. `ljust`/`rjust` hacen lo mismo como metodos.

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

Utiles para validar `input()` antes de convertir a `int`.

### 8. Recorrer caracter a caracter

```python
s = "abc"
for c in s:
    print(c)        # a, luego b, luego c

# Con indice si lo necesitas
for i, c in enumerate(s):
    print(i, c)     # 0 a / 1 b / 2 c
```

Un `for` sobre un string itera sus caracteres directamente, sin manejar indices ni `\0`.

---

## Worked example

**Problema (slugify):** convertir un titulo como `"  Hola Mundo en Python  "` en `hola-mundo-en-python`. Un "slug" es el texto apto para una URL: minusculas, sin espacios al borde, espacios convertidos en guiones.

**Paso 1 — quitar espacios del borde:**
```python
titulo = "  Hola Mundo en Python  "
limpio = titulo.strip()
print(repr(limpio))   # 'Hola Mundo en Python'
```

`.strip()` elimina los espacios del principio y del final (los internos se quedan).

**Paso 2 — pasar a minusculas:**
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

**Paso 4 — encadenar en una linea:**
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

## Errores tipicos de Python

| # | Error | Ejemplo malo | Correcto |
|---|---|---|---|
| 1 | Los strings son inmutables | `s[0] = "x"` lanza `TypeError` | crear copia: `s = "x" + s[1:]` |
| 2 | `input()` siempre devuelve `str` | `edad = input(); edad + 1` | `edad = int(input()); edad + 1` |
| 3 | `.replace()` devuelve copia, no muta | `s.replace("a","b")` sin asignar | `s = s.replace("a", "b")` |
| 4 | `.strip()` no quita espacios internos | esperar que `"a b".strip()` de `"ab"` | usar `.replace(" ", "")` para internos |
| 5 | Comparar sin normalizar el caso | `"Ana" == "ana"` da `False` | `a.lower() == b.lower()` |

---

## Ejercicios

Los archivos de practica estan en `practica/06-cadenas/`.

1. **Invertir cadena** — Lee una palabra e imprimela al reves usando slicing `[::-1]`.
   - Dificultad: (facil)
   - Salida esperada (entrada: `python`): `nohtyp`
   - Practica: `practica/06-cadenas/ej01_practica.py` | Modelo: `ej01_modelo.py`

2. **Palindromo** — Di si una palabra es palindromo ignorando mayusculas/minusculas (normaliza con `.lower()`).
   - Dificultad: (facil)
   - Salida esperada (entrada: `reconocer`): `reconocer ES palindromo`
   - Practica: `practica/06-cadenas/ej02_practica.py` | Modelo: `ej02_modelo.py`

3. **Contar vocales** — Cuenta las vocales de una frase (mayusculas y minusculas) recorriendo caracter a caracter.
   - Dificultad: (facil)
   - Salida esperada (entrada: `Hola Mundo`): `Vocales: 4`
   - Practica: `practica/06-cadenas/ej03_practica.py` | Modelo: `ej03_modelo.py`

4. **Title + limpiar espacios** — Dado un texto con espacios sobrantes al borde, devuelvelo en formato Titulo limpio (`.strip()` + `.title()`).
   - Dificultad: (media)
   - Salida esperada (entrada: `  hola mundo cruel  `): `Hola Mundo Cruel`
   - Practica: `practica/06-cadenas/ej04_practica.py` | Modelo: `ej04_modelo.py`

5. **Slugify** — Convierte un titulo a slug: minusculas, sin espacios al borde, espacios convertidos en `-`.
   - Dificultad: (media)
   - Salida esperada (entrada: `  Mi Primer Post  `): `mi-primer-post`
   - Practica: `practica/06-cadenas/ej05_practica.py` | Modelo: `ej05_modelo.py`

6. **Formatear nombre** — Pide nombre y apellido por separado y devuelve `APELLIDO, Nombre` (apellido en mayusculas, nombre capitalizado).
   - Dificultad: (media)
   - Salida esperada (entrada: `juan` / `perez`): `PEREZ, Juan`
   - Practica: `practica/06-cadenas/ej06_practica.py` | Modelo: `ej06_modelo.py`

7. **Censurar palabra** — Reemplaza todas las apariciones de una palabra por asteriscos de su misma longitud con `.replace()`.
   - Dificultad: (media)
   - Salida esperada (frase `esto es tonto y muy tonto`, palabra `tonto`): `esto es ***** y muy *****`
   - Practica: `practica/06-cadenas/ej07_practica.py` | Modelo: `ej07_modelo.py`

8. **Tabla bonita / formateo numerico** — Dada una lista hardcodeada de pares (producto, precio), imprime una tabla alineada: nombre a la izquierda con `ljust(12)` y precio a la derecha con 2 decimales y separador de miles (`f"{precio:>10,.2f}"`).
   - Dificultad: (dificil)
   - Salida esperada:
     ```
     Manzana           1.50
     Leche             0.99
     Portatil      1,299.00
     ```
   - Practica: `practica/06-cadenas/ej08_practica.py` | Modelo: `ej08_modelo.py`

---

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/05-listas]]
- [[Curso_Python/modelo/07-diccionarios-sets]]
