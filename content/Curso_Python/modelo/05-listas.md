---
title: "Modulo 05 — Listas y comprehensions"
date: 2026-06-16
tags: [programacion/python, programacion/curso, programacion/python/listas]
type: nota
status: en-progreso
source: claude-code
aliases: [listas python, list comprehension, slicing python]
---

# Modulo 05 — Listas y comprehensions

## Idea central

En C un array es un bloque fijo de memoria del mismo tipo. En Python una lista (`list`) es una secuencia **dinamica**, heterogenea y de primera clase: puede crecer, encogerse y transformarse con una sola linea de comprehension.

---

## Que aprendes

| Concepto | Para que |
|---|---|
| Crear lista literal | Agrupar valores sin declarar tipo ni tamano |
| Indexar y slicing | Acceder a uno o varios elementos de forma expresiva |
| `append / pop / insert` | Modificar la lista en tiempo de ejecucion |
| `len / sorted / sort` | Operaciones de medida y ordenacion |
| Recorrido con `for` | Iterar sin indice manual |
| List comprehension | Transformar/filtrar una lista en una sola expresion |
| `in` | Buscar un elemento sin bucle explicito |
| `set()` sobre lista | Eliminar duplicados al instante |

---

## C vs Python

El mismo problema: **dado un array de enteros, construir otro con solo los pares**.

| Aspecto | C | Python |
|---|---|---|
| Declaracion | `int nums[] = {1,2,3,4,5};` | `nums = [1, 2, 3, 4, 5]` |
| Tamano fijo | Si (`int N = 5;`) | No (dinamica) |
| Filtrar pares (bucle) | `for(int i=0;i<N;i++) if(nums[i]%2==0) pares[j++]=nums[i];` | `pares = [x for x in nums if x % 2 == 0]` |
| Imprimir resultado | `for(int i=0;i<j;i++) printf("%d ",pares[i]);` | `print(pares)` |
| Acceso a ultimo | `nums[N-1]` | `nums[-1]` |
| Invertir | bucle manual o `memcpy` | `nums[::-1]` |

**Codigo C completo:**
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

**Codigo Python equivalente:**
```python
nums = [1, 2, 3, 4, 5]
pares = [x for x in nums if x % 2 == 0]
print(pares)   # [2, 4]
```

---

## Explicacion

### 1. Crear e indexar

```python
frutas = ["manzana", "pera", "uva"]
print(frutas[0])   # manzana   (como C, base 0)
print(frutas[-1])  # uva       (indice negativo: desde el final)
```

**Patron:** `lista[indice]`. Indices negativos son exclusivos de Python y muy utiles.

### 2. Slicing

```python
nums = [0, 1, 2, 3, 4, 5]
print(nums[1:4])   # [1, 2, 3]   — de indice 1 hasta 3 (4 no incluido)
print(nums[:3])    # [0, 1, 2]   — desde el inicio
print(nums[::2])   # [0, 2, 4]   — cada dos elementos
print(nums[::-1])  # [5, 4, 3, 2, 1, 0] — invertir
```

**Patron:** `lista[inicio:fin:paso]`. Los tres son opcionales; el paso `-1` invierte.

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

`sorted()` NO modifica la original. `.sort()` SI la modifica.

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

La condicion `if` es opcional.

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

`in` recorre la lista linealmente (O(n)). Para busquedas frecuentes, usar `set`.

### 8. Eliminar duplicados con set

```python
nums = [3, 1, 4, 1, 5, 3, 2]
unicos = list(set(nums))   # orden NO garantizado
print(sorted(unicos))      # [1, 2, 3, 4, 5] — ordenar para salida reproducible
```

`set()` convierte la lista en un conjunto (sin duplicados). El orden original se pierde.

---

## Worked example

**Problema:** dada una lista de notas enteras, calcular media, nota maxima, nota minima, y devolver las notas aprobadas (>= 5) ordenadas de mayor a menor.

**Paso 1 — Datos:**
```python
notas = [3, 7, 5, 2, 9, 6, 4]
```

**Paso 2 — Media:**
```python
media = sum(notas) / len(notas)
print(f"Media: {media:.2f}")   # Media: 5.14
```

`sum()` es funcion builtin; `len()` da el numero de elementos.

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

## Errores tipicos de Python

| # | Error | Ejemplo malo | Correcto |
|---|---|---|---|
| 1 | `input()` devuelve `str`, no `int` | `n = input(); total = n + 1` | `n = int(input()); total = n + 1` |
| 2 | Indice fuera de rango | `lista[len(lista)]` | `lista[len(lista)-1]` o `lista[-1]` |
| 3 | `.sort()` devuelve `None` | `ordenada = lista.sort()` | `lista.sort()` (in-place) o `ordenada = sorted(lista)` |
| 4 | Copiar lista por referencia | `b = a; b.append(99)` modifica `a` | `b = a[:]` o `b = list(a)` |
| 5 | Modificar lista mientras se itera | `for x in lista: if ...: lista.remove(x)` | Iterar sobre una copia: `for x in lista[:]` |

---

## Ejercicios

Los archivos de practica estan en `practica/05-listas/`.

1. **Suma y media** — Pide al usuario N numeros enteros y calcula su suma y media.
   - Dificultad: (facil)
   - Salida esperada (entrada: `3 7 2`): `Suma: 12  Media: 4.00`
   - Practica: `practica/05-listas/ej01_practica.py` | Modelo: `ej01_modelo.py`

2. **Maximo y minimo** — Dada una lista hardcodeada, imprime el mayor y el menor sin usar `max()`/`min()` (usa un bucle manual).
   - Dificultad: (facil)
   - Salida esperada (lista `[4, 1, 9, 3, 7]`): `Max: 9  Min: 1`
   - Practica: `practica/05-listas/ej02_practica.py` | Modelo: `ej02_modelo.py`

3. **Invertir con slicing** — Pide una lista de palabras separadas por espacio e imprimela al reves.
   - Dificultad: (facil)
   - Salida esperada (entrada: `hola mundo python`): `['python', 'mundo', 'hola']`
   - Practica: `practica/05-listas/ej03_practica.py` | Modelo: `ej03_modelo.py`

4. **Filtrar pares** — Dada una lista de enteros del 1 al 20, usa una comprehension para extraer solo los pares.
   - Dificultad: (facil)
   - Salida esperada: `[2, 4, 6, 8, 10, 12, 14, 16, 18, 20]`
   - Practica: `practica/05-listas/ej04_practica.py` | Modelo: `ej04_modelo.py`

5. **Cuadrados con comprehension** — El usuario introduce N; imprime la lista de cuadrados de 1 a N.
   - Dificultad: (media)
   - Salida esperada (N=5): `[1, 4, 9, 16, 25]`
   - Practica: `practica/05-listas/ej05_practica.py` | Modelo: `ej05_modelo.py`

6. **Buscar elemento** — Pide una lista de nombres y un nombre a buscar; informa si esta o no, y en que posicion (usa `in` e `index()`).
   - Dificultad: (media)
   - Salida esperada (lista `ana luis maria`, buscar `luis`): `"luis" encontrado en posicion 1`
   - Practica: `practica/05-listas/ej06_practica.py` | Modelo: `ej06_modelo.py`

7. **Eliminar duplicados** — El usuario ingresa una lista de enteros con repetidos; imprime la lista sin duplicados, ordenada.
   - Dificultad: (media)
   - Salida esperada (entrada: `3 1 4 1 5 3 2`): `[1, 2, 3, 4, 5]`
   - Practica: `practica/05-listas/ej07_practica.py` | Modelo: `ej07_modelo.py`

---

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/04-funciones]]
- [[Curso_Python/modelo/06-cadenas]]
