---
title: "Módulo 03: Bucles en Python"
date: 2026-06-16
tags: [programacion/python, programacion/curso, programacion/bucles]
aliases: [bucles python, for range, while python, enumerate python]
type: espejo
status: espejo
source: mirror-generado
mirror: true
mirror_source: curso-python/modelo/03-bucles.md
---

<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: curso-python/modelo/03-bucles.md (se regenera con gen_course.py). -->

# Módulo 03: Bucles en Python

## Idea central

En C los bucles giran alrededor del índice. En Python hay dos modos: iterar **sobre una secuencia** (sin índice manual) o iterar **N veces con `range`**. El 90 % del tiempo usas `for`; `while` se reserva para condiciones no numéricas.

---

## Qué aprendes

| Concepto | Para que |
|---|---|
| `for i in range(n)` | Repetir N veces con índice disponible |
| `for x in lista` | Recorrer cada elemento (estilo for-each de C++) |
| `while condicion` | Bucle con condición arbitraria (igual que C) |
| `break` / `continue` | Salir o saltar iteración (idéntico a C) |
| `enumerate(lista)` | Obtener índice Y valor a la vez, sin contador manual |
| `for … else` | Bloque que se ejecuta si el bucle termina SIN `break` |

---

## C vs Python

| Tarea | C | Python |
|---|---|---|
| Contar 0..4 | `for(int i=0; i<5; i++)` | `for i in range(5):` |
| Contar 1..N | `for(int i=1; i<=n; i++)` | `for i in range(1, n+1):` |
| Paso de 2 | `for(int i=0; i<10; i+=2)` | `for i in range(0, 10, 2):` |
| For-each sobre array | `for(int i=0; i<N; i++) { x=arr[i]; }` | `for x in lista:` |
| Índice + valor | `for(int i=0; i<N; i++) { arr[i] ... }` | `for i, x in enumerate(lista):` |
| While | `while(cond) { … }` | `while cond:` |
| Break / continue | `break;` / `continue;` | `break` / `continue` |

**Diferencia clave**: en C el `for` es azúcar sintáctica de un `while`; en Python `for` recorre objetos iterables (no solo rangos numéricos).

---

## Explicación

### `range(inicio, fin, paso)`

`range` genera números enteros **sin crear una lista en memoria**. Es perezoso (lazy).

```python
range(5)          # 0, 1, 2, 3, 4
range(1, 6)       # 1, 2, 3, 4, 5
range(0, 10, 2)   # 0, 2, 4, 6, 8
range(5, 0, -1)   # 5, 4, 3, 2, 1
```

### `for x in lista` — iteración directa

```python
frutas = ["manzana", "pera", "uva"]
for f in frutas:
    print(f)
```

No necesitas índice. Si además necesitas el índice, usa `enumerate`:

```python
for i, f in enumerate(frutas):
    print(i, f)   # 0 manzana  /  1 pera  /  2 uva
```

### `while`

```python
n = 10
while n > 0:
    print(n)
    n -= 1
```

Idéntico a C salvo que no hay paréntesis en la condición ni llaves.

### `break` y `continue`

```python
for i in range(10):
    if i == 5:
        break       # sale del bucle
    if i % 2 == 0:
        continue    # salta al siguiente i
    print(i)        # imprime 1, 3
```

### `for … else` (peculiaridad de Python)

El bloque `else` **solo** se ejecuta si el bucle terminó sin `break`. Útil para búsquedas:

```python
for i in range(2, 10):
    if 10 % i == 0:
        print(f"10 no es primo, divisor: {i}")
        break
else:
    print("10 es primo")   # no se ejecuta aqui
```

---

## Worked example

**Problema**: dado un entero N, imprimir todos los números primos entre 2 y N inclusive.

**Paso 1 — entender el esquema**: para cada candidato `p` de 2 a N, probamos si algún número entre 2 y `sqrt(p)` lo divide. Si ninguno lo divide, es primo.

**Paso 2 — en C mentalmente**:
```c
for(int p=2; p<=n; p++) {
    int primo = 1;
    for(int d=2; d*d<=p; d++) {
        if(p % d == 0) { primo = 0; break; }
    }
    if(primo) printf("%d\n", p);
}
```

**Paso 3 — traducción directa a Python**:

```python
n = int(input("Hasta que numero: "))

for p in range(2, n + 1):
    es_primo = True
    for d in range(2, int(p**0.5) + 1):
        if p % d == 0:
            es_primo = False
            break
    if es_primo:
        print(p)
```

**Paso 4 — versión con `for … else`** (más Pythónica):

```python
n = int(input("Hasta que numero: "))

for p in range(2, n + 1):
    for d in range(2, int(p**0.5) + 1):
        if p % d == 0:
            break
    else:
        print(p)   # solo si el inner-for termino sin break
```

El `else` del bucle interno se activa cuando ningún divisor fue encontrado — es decir, `p` es primo. Más compacto, sin bandera booleana.

---

## Errores típicos de Python

1. **Indentación incorrecta dentro del bucle**
   ```python
   for i in range(3):
   print(i)   # IndentationError: falta un nivel de sangria
   ```
   Todo lo que pertenece al cuerpo del bucle debe tener 4 espacios más que el `for`.

2. **`input()` devuelve cadena, no entero**
   ```python
   n = input("N: ")
   for i in range(n):   # TypeError: range() espera int, recibio str
       print(i)
   ```
   Solución: `n = int(input("N: "))`.

3. **Modificar una lista mientras la recorres**
   ```python
   nums = [1, 2, 3, 4]
   for x in nums:
       if x % 2 == 0:
           nums.remove(x)   # comportamiento inesperado
   ```
   Recorre una copia: `for x in nums[:]` o construye una lista nueva con comprensión.

4. **`range(n)` empieza en 0, no en 1**
   ```python
   for i in range(5):
       print(i)   # imprime 0 1 2 3 4, no 1 2 3 4 5
   ```
   Si quieres 1..N usa `range(1, n+1)`.

5. **Bucle infinito por olvidar actualizar la variable de `while`**
   ```python
   n = 5
   while n > 0:
       print(n)
       # falta n -= 1  →  bucle infinito
   ```
   En C el compilador no te avisa; en Python tampoco. Revisa siempre que la condición evoluciona.

---

## Ejercicios

- [[Curso_Python/practica/03-bucles/ej01|Ej 01 — Pide un entero N e imprime los números del 1 al N, uno por línea (verde)]]
- [[Curso_Python/practica/03-bucles/ej02|Ej 02 — Pide N e imprime la suma acumulada de 1 + 2 + .. (verde)]]
- [[Curso_Python/practica/03-bucles/ej03|Ej 03 — Pide N e imprime N! (factorial) (amarillo)]]
- [[Curso_Python/practica/03-bucles/ej04|Ej 04 — Pide un número N e imprime su tabla de multiplicar del 1 al 10 (verde)]]
- [[Curso_Python/practica/03-bucles/ej05|Ej 05 — Pide N e imprime todos los primos entre 2 y N (amarillo)]]
- [[Curso_Python/practica/03-bucles/ej06|Ej 06 — Pide N e imprime los primeros N terminos de Fibonacci (amarillo)]]
- [[Curso_Python/practica/03-bucles/ej07|Ej 07 — Dada una lista de numeros separados por espacios, imprime su suma (rojo)]]

## Conexiones

- [[Curso_Python/00_README]]
- [[MOC_NeetCode_150]]
- [[Curso_Python/modelo/02-condicionales]]
- [[Curso_Python/modelo/04-funciones]]
