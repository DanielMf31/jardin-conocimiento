---
title: "Módulo 06: Matrices (arrays 2D) en C"
date: 2026-06-16
tags: [programacion/c, curso, programacion/arrays, programacion/bucles]
type: nota
status: en-progreso
source: claude-code
aliases: [matrices C, arrays 2D C, array bidimensional C]
---

# Módulo 06: Matrices (arrays 2D)

## Idea central

Un array 1D guarda una fila de valores. Una **matriz** (array 2D) guarda una cuadrícula de valores: filas × columnas. El problema que resuelve es organizar datos con dos índices naturales (píxeles de imagen, celdas de hoja de cálculo, tablero de juego, resultados de alumnos por asignatura).

---

## Qué aprendes

| Concepto | Para qué sirve |
|---|---|
| Declarar `int m[F][C]` | Reservar una cuadrícula fija en memoria |
| Doble bucle `for (i) for (j)` | Recorrer todas las celdas fila a fila |
| Leer con `scanf` en 2D | Introducir datos celda a celda |
| Imprimir con formato | Mostrar la cuadrícula alineada |
| Suma de matrices | Sumar elemento a elemento |
| Suma por filas / columnas | Reducir la matriz a vectores |
| Transpuesta | Intercambiar filas y columnas |
| Diagonal principal | Recorrer solo donde `i == j` |
| Máximo global | Buscar el mayor valor en la cuadrícula |
| Matriz identidad | Construir una cuadrícula con patrón |

---

## Explicación

### Categoría: estructura de datos 2D

Una matriz en C es un array de arrays. La memoria es contigua: primero toda la fila 0, luego toda la fila 1, etc.

```
m[0][0]  m[0][1]  m[0][2]
m[1][0]  m[1][1]  m[1][2]
m[2][0]  m[2][1]  m[2][2]
```

### Patrón: declarar y recorrer

```c
#define FILAS 3
#define COLS  4

int m[FILAS][COLS];          // declaracion

// Recorrer TODAS las celdas
for (int i = 0; i < FILAS; i++) {
    for (int j = 0; j < COLS; j++) {
        // usar m[i][j]
    }
}
```

El índice exterior `i` selecciona la **fila**, el interior `j` selecciona la **columna**.

### Sintaxis: leer e imprimir

```c
// Leer
scanf("%d", &m[i][j]);   // OBLIGATORIO el &

// Imprimir con separacion
printf("%4d", m[i][j]);  // %4d: campo de 4 caracteres, queda alineado
printf("\n");             // salto de linea al acabar cada fila (bucle exterior)
```

### Patrón: suma de matrices

```c
for (int i = 0; i < F; i++)
    for (int j = 0; j < C; j++)
        r[i][j] = a[i][j] + b[i][j];
```

### Patrón: suma por filas

```c
for (int i = 0; i < F; i++) {
    int suma = 0;
    for (int j = 0; j < C; j++)
        suma += m[i][j];
    printf("Fila %d: %d\n", i, suma);
}
```

### Patrón: transpuesta (requiere matriz destino de dimensiones invertidas)

```c
// m es F x C  ->  t es C x F
for (int i = 0; i < F; i++)
    for (int j = 0; j < C; j++)
        t[j][i] = m[i][j];
```

### Patrón: diagonal principal (solo cuadradas, i == j)

```c
int diag = 0;
for (int i = 0; i < N; i++)
    diag += m[i][i];
```

### Patrón: máximo global

```c
int max = m[0][0];
for (int i = 0; i < F; i++)
    for (int j = 0; j < C; j++)
        if (m[i][j] > max)
            max = m[i][j];
```

---

## Worked example

**Problema:** leer una matriz 3×3 de enteros e imprimir la suma de cada columna.

### Paso 1 — entender la tarea

Tenemos 3 columnas. Para la columna `j` hay que sumar `m[0][j] + m[1][j] + m[2][j]`, es decir, el bucle exterior recorre columnas y el interior filas.

### Paso 2 — código

```c
#include <stdio.h>

#define N 3

int main(void) {
    int m[N][N];

    // Paso A: leer la matriz
    printf("Introduce los %d valores fila a fila:\n", N * N);
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            scanf("%d", &m[i][j]);   // <- & es obligatorio

    // Paso B: imprimir la matriz para confirmar
    printf("\nMatriz introducida:\n");
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++)
            printf("%4d", m[i][j]);
        printf("\n");
    }

    // Paso C: suma por columnas (bucle exterior = columna)
    printf("\nSuma por columnas:\n");
    for (int j = 0; j < N; j++) {
        int suma = 0;
        for (int i = 0; i < N; i++)
            suma += m[i][j];
        printf("  Col %d: %d\n", j, suma);
    }

    return 0;
}
```

### Paso 3 — traza con entrada `1 2 3 / 4 5 6 / 7 8 9`

```
Matriz:
   1   2   3
   4   5   6
   7   8   9

Col 0: 1+4+7 = 12
Col 1: 2+5+8 = 15
Col 2: 3+6+9 = 18
```

### Por qué funciona

- El `&` en `scanf("%d", &m[i][j])` pasa la **dirección** de la celda, no su valor.
- Invertir el orden de los bucles (j exterior, i interior) es la clave para iterar por columnas en vez de por filas.
- Inicializar `suma = 0` dentro del bucle de columna la resetea para cada columna.

---

## Errores típicos en C

| # | Error | Consecuencia | Corrección |
|---|---|---|---|
| 1 | `scanf("%d", m[i][j])` sin `&` | Comportamiento indefinido, casi siempre segfault | Siempre `&m[i][j]` |
| 2 | Declarar `int m[3][3]` y acceder a `m[3][0]` | Buffer overflow, datos corruptos | Los índices van de `0` a `N-1` |
| 3 | `int suma;` sin inicializar antes del bucle | Suma basura (valor indeterminado) | `int suma = 0;` |
| 4 | Confundir filas y columnas al pasar a función | La función recibe dimensiones cruzadas | Documentar siempre cuál es F y cuál es C |
| 5 | Usar `==` con `float` en la diagonal | Comparación inexacta para floats | Usar enteros o comparar con tolerancia `fabs(a-b) < EPS` |

---

## Ejercicios

Los ficheros de práctica están en `practica/06-matrices/`. Cada ejercicio tiene:
- `ejNN_practica.c` — esqueleto con TODOs para rellenar.
- `ejNN_modelo.c` — solución completa para comparar **después** de intentarlo.

---

### ej01 — Leer e imprimir una matriz (facil)

**Enunciado:** Lee una matriz de enteros de tamaño M×N (M filas, N columnas, ambos introducidos por el usuario, máximo 10×10) e imprímela con formato alineado.

**Entrada de ejemplo:**
```
M=2 N=3
1 2 3
4 5 6
```
**Salida esperada:**
```
   1   2   3
   4   5   6
```
→ `practica/06-matrices/ej01_practica.c` / `ej01_modelo.c`

---

### ej02 — Suma por filas y columnas (facil)

**Enunciado:** Dado una matriz 3×3 introducida por el usuario, imprime la suma de cada fila y la suma de cada columna.

**Entrada de ejemplo:**
```
1 2 3
4 5 6
7 8 9
```
**Salida esperada:**
```
Sumas por fila:   6  15  24
Sumas por columna: 12  15  18
```
→ `practica/06-matrices/ej02_practica.c` / `ej02_modelo.c`

---

### ej03 — Suma de dos matrices (facil)

**Enunciado:** Lee dos matrices 3×3 de enteros e imprime su suma elemento a elemento.

**Entrada de ejemplo:**
```
Matriz A:  1 0 0 / 0 1 0 / 0 0 1
Matriz B:  2 3 4 / 5 6 7 / 8 9 0
```
**Salida esperada:**
```
   3   3   4
   5   7   7
   8   9   1
```
→ `practica/06-matrices/ej03_practica.c` / `ej03_modelo.c`

---

### ej04 — Máximo de la matriz (media)

**Enunciado:** Lee una matriz 4×4 e imprime el valor máximo y su posición (fila, columna).

**Entrada de ejemplo:**
```
 3  1  4  1
 5  9  2  6
 5  3  5  8
 9  7  9  3
```
**Salida esperada:**
```
Maximo: 9 en posicion [1][1]
```
*(Si hay empate, se acepta cualquiera de las posiciones.)*

→ `practica/06-matrices/ej04_practica.c` / `ej04_modelo.c`

---

### ej05 — Transpuesta (media)

**Enunciado:** Lee una matriz de enteros 3×4 e imprime su transpuesta (que será 4×3).

**Entrada de ejemplo:**
```
1 2 3 4
5 6 7 8
9 10 11 12
```
**Salida esperada:**
```
   1   5   9
   2   6  10
   3   7  11
   4   8  12
```
→ `practica/06-matrices/ej05_practica.c` / `ej05_modelo.c`

---

### ej06 — Suma de la diagonal principal (media)

**Enunciado:** Lee una matriz cuadrada N×N (N introducido por el usuario, máximo 8) y calcula la suma de los elementos de la diagonal principal (donde `i == j`).

**Entrada de ejemplo:**
```
N=3
1 2 3
4 5 6
7 8 9
```
**Salida esperada:**
```
Suma diagonal: 15
```
→ `practica/06-matrices/ej06_practica.c` / `ej06_modelo.c`

---

### ej07 — Generar matriz identidad (dificil)

**Enunciado:** Dado N introducido por el usuario (máximo 8), genera e imprime la matriz identidad N×N: 1 en la diagonal, 0 en el resto.

**Entrada de ejemplo:**
```
N=4
```
**Salida esperada:**
```
   1   0   0   0
   0   1   0   0
   0   0   1   0
   0   0   0   1
```
→ `practica/06-matrices/ej07_practica.c` / `ej07_modelo.c`

---

## Conexiones

- [[Curso_C/00_README]]
- [[MOC_Linux]]
- [[Curso_C/modelo/05-arrays-cadenas]] — módulo anterior: arrays unidimensionales
- [[Curso_C/modelo/07-punteros]] — módulo siguiente: funciones y paso de arrays
