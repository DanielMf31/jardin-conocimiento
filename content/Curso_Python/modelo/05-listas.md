---
title: "Módulo 05 — Listas y comprehensions"
date: 2026-06-16
tags: [programacion/python, programacion/curso, programacion/python/listas]
aliases: [listas python, list comprehension, slicing python]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-python/modelo/05-listas.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-python/modelo/05-listas.md (se regenera con gen_course.py). -->

# Módulo 05 — Listas y comprehensions

## Idea central

En C un array es un bloque fijo de memoria del mismo tipo. En Python una lista (`list`) es una secuencia **dinámica**, heterogénea y de primera clase: puede crecer, encogerse y transformarse con una sola línea de comprehension.

---

## Qué aprendes

| Concepto | Para qué |
|---|---|
| Crear lista literal | Agrupar valores sin declarar tipo ni tamaño |
| Indexar y slicing | Acceder a uno o varios elementos de forma expresiva |
| `append / pop / insert` | Modificar la lista en tiempo de ejecución |
| `len / sorted / sort` | Operaciones de medida y ordenación |
| Recorrido con `for` | Iterar sin índice manual |
| List comprehension | Transformar/filtrar una lista en una sola expresión |
| `in` | Buscar un elemento sin bucle explicito |
| `set()` sobre lista | Eliminar duplicados al instante |

---

## C vs Python

El mismo problema: **dado un array de enteros, construir otro con solo los pares**.

| Aspecto | C | Python |
|---|---|---|
| Declaración | `int nums[] = {1,2,3,4,5};` | `nums = [1, 2, 3, 4, 5]` |
| Tamaño fijo | Sí (`int N = 5;`) | No (dinámica) |
| Filtrar pares (bucle) | `for(int i=0;i<N;i++) if(nums[i]%2==0) pares[j++]=nums[i];` | `pares = [x for x in nums if x % 2 == 0]` |
| Imprimir resultado | `for(int i=0;i<j;i++) printf("%d ",pares[i]);` | `print(pares)` |
| Acceso a último | `nums[N-1]` | `nums[-1]` |
| Invertir | bucle manual o `memcpy` | `nums[::-1]` |

**Código C completo:**
```c
#include <stdio.h>
int main(void) {
    int nums[] = {1, 2, 3, 4, 5};
    int N = 5;
    int pares[5];
    int j = 0;
    for (int i = 0; i < N; i++)
        if (nums[i] % 2 == 0)
            pares[j++] = nums[i];
    for (int i = 0; i < j; i++)
        printf("%d ", pares[i]);
    return 0;
}
```

**Código Python equivalente:**
```python
nums = [1, 2, 3, 4, 5]
pares = [x for x in nums if x % 2 == 0]
print(pares)   # [2, 4]
```

---

## Explicación

### 1. Crear e indexar

```python
frutas = ["manzana", "pera", "uva"]
print(frutas[0])   # manzana   (como C, base 0)
print(frutas[-1])  # uva       (indice negativo: desde el final)
```

**Patrón:** `lista[indice]`. Índices negativos son exclusivos de Python y muy útiles.

### 2. Slicing

```python
nums = [0, 1, 2, 3, 4, 5]
print(nums[1:4])   # [1, 2, 3]   — de indice 1 hasta 3 (4 no incluido)
print(nums[:3])    # [0, 1, 2]   — desde el inicio
print(nums[::2])   # [0, 2, 4]   — cada dos elementos
print(nums[::-1])  # [5, 4, 3, 2, 1, 0] — invertir
```

**Patrón:** `lista[inicio:fin:paso]`. Los tres son opcionales; el paso `-1` invierte.

### 3. Modificar: append, pop, insert

```python
nums = [10, 20, 30]
nums.append(40)      # [10, 20, 30, 40]
nums.pop()           # [10, 20, 30]  — elimina y devuelve el ultimo
nums.pop(0)          # [20, 30]      — elimina por indice
nums.insert(1, 99)   # [20, 99, 30] — inserta en posicion
```

`append` es O(1) amortizado. `insert(0, x)` es O(n) (desplaza todo).

### 4. len, sorted, sort

```python
nums = [3, 1, 4, 1, 5]
print(len(nums))       # 5
print(sorted(nums))    # [1, 1, 3, 4, 5] — nueva lista ordenada
nums.sort()            # ordena EN SITIO, devuelve None
nums.sort(reverse=True)
```

`sorted()` NO modifica la original. `.sort()` SÍ la modifica.

### 5. Recorrido

```python
# Sin indice (Pythonic)
for fruta in frutas:
    print(fruta)

# Con indice cuando lo necesitas
for i, fruta in enumerate(frutas):
    print(f"{i}: {fruta}")
```

### 6. List comprehension

**Patron:** `[expresion for elemento in iterable if condicion]`

La condición `if` es opcional.

```python
cuadrados = [x**2 for x in range(6)]          # [0, 1, 4, 9, 16, 25]
pares      = [x for x in range(10) if x%2==0] # [0, 2, 4, 6, 8]
dobles     = [x*2 for x in [1,2,3]]           # [2, 4, 6]
```

### 7. Buscar con `in`

```python
colores = ["rojo", "verde", "azul"]
print("verde" in colores)   # True
print("negro" in colores)   # False
```

`in` recorre la lista linealmente (O(n)). Para búsquedas frecuentes, usar `set`.

### 8. Eliminar duplicados con set

```python
nums = [3, 1, 4, 1, 5, 3, 2]
unicos = list(set(nums))   # orden NO garantizado
print(sorted(unicos))      # [1, 2, 3, 4, 5] — ordenar para salida reproducible
```

`set()` convierte la lista en un conjunto (sin duplicados). El orden original se pierde.

---

## Worked example

**Problema:** dada una lista de notas enteras, calcular media, nota máxima, nota mínima, y devolver las notas aprobadas (>= 5) ordenadas de mayor a menor.

**Paso 1 — Datos:**
```python
notas = [3, 7, 5, 2, 9, 6, 4]
```

**Paso 2 — Media:**
```python
media = sum(notas) / len(notas)
print(f"Media: {media:.2f}")   # Media: 5.14
```

`sum()` es función builtin; `len()` da el número de elementos.

**Paso 3 — Maximo y minimo:**
```python
print(f"Max: {max(notas)}, Min: {min(notas)}")   # Max: 9, Min: 2
```

**Paso 4 — Aprobados con comprehension:**
```python
aprobadas = [n for n in notas if n >= 5]
aprobadas.sort(reverse=True)
print(f"Aprobadas: {aprobadas}")   # Aprobadas: [9, 7, 6, 5]
```

**Programa completo:**
```python
notas = [3, 7, 5, 2, 9, 6, 4]
media = sum(notas) / len(notas)
print(f"Media: {media:.2f}")
print(f"Max: {max(notas)}, Min: {min(notas)}")
aprobadas = sorted([n for n in notas if n >= 5], reverse=True)
print(f"Aprobadas: {aprobadas}")
```

---

## Errores típicos de Python

| # | Error | Ejemplo malo | Correcto |
|---|---|---|---|
| 1 | `input()` devuelve `str`, no `int` | `n = input(); total = n + 1` | `n = int(input()); total = n + 1` |
| 2 | Índice fuera de rango | `lista[len(lista)]` | `lista[len(lista)-1]` o `lista[-1]` |
| 3 | `.sort()` devuelve `None` | `ordenada = lista.sort()` | `lista.sort()` (in-place) o `ordenada = sorted(lista)` |
| 4 | Copiar lista por referencia | `b = a; b.append(99)` modifica `a` | `b = a[:]` o `b = list(a)` |
| 5 | Modificar lista mientras se itera | `for x in lista: if ...: lista.remove(x)` | Iterar sobre una copia: `for x in lista[:]` |

---

## Ejercicios

- [[Curso_Python/practica/05-listas/ej01|Ej 01 — Pide al usuario N números enteros y calcula su suma y media (verde)]]
- [[Curso_Python/practica/05-listas/ej02|Ej 02 — Dada una lista hardcodeada, imprime el mayor y el menor SIN usar… (verde)]]
- [[Curso_Python/practica/05-listas/ej03|Ej 03 — Pide una lista de palabras separadas por espacio e imprimela al reves (verde)]]
- [[Curso_Python/practica/05-listas/ej04|Ej 04 — Dada una lista de enteros del 1 al 20, extrae solo los pares con… (verde)]]
- [[Curso_Python/practica/05-listas/ej05|Ej 05 — El usuario introduce N (amarillo)]]
- [[Curso_Python/practica/05-listas/ej06|Ej 06 — Pide una lista de nombres y un nombre a buscar (amarillo)]]
- [[Curso_Python/practica/05-listas/ej07|Ej 07 — El usuario ingresa enteros con repetidos (amarillo)]]

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/04-funciones]]
- [[Curso_Python/modelo/06-cadenas]]
