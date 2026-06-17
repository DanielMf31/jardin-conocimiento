---
title: "Módulo 04: Funciones en C"
date: 2026-06-16
tags: [programacion/c, curso, programacion/funciones, programacion/modularidad]
type: nota
status: en-progreso
source: claude-code
aliases: [funciones-c, modulo-04-c, subrutinas-c]
---

# Módulo 04: Funciones en C

## Idea central

Sin funciones, un programa de 200 líneas es un monolito ilegible: todo mezclado, nada reutilizable. Las funciones son el mecanismo de C para **nombrar un bloque de lógica**, darle parámetros de entrada y obtener un resultado de vuelta. Así el programa se divide en piezas pequeñas, cada una verificable por separado.

---

## Qué aprendes

| Concepto | Para qué sirve |
|---|---|
| Definición de función | Empaquetar lógica reutilizable con nombre propio |
| Parámetros por valor | Pasar datos a la función sin afectar las variables originales |
| `return` | Devolver un resultado al llamador |
| Prototipo (declaración) | Informar al compilador antes de definir la función |
| `void` | Funciones que no devuelven valor (o sin parámetros) |
| Ámbito de variables | Variables locales vs. globales; por qué preferir locales |
| Array como parámetro | Pasar un array + su tamaño para operar sobre colecciones |

---

## Explicación

### Categoría: ¿qué ES una función?

Una función es un **subprograma** con:
- Un **tipo de retorno** (el tipo del valor que devuelve, o `void` si no devuelve nada).
- Un **nombre** (identificador).
- Una **lista de parámetros** (puede estar vacía).
- Un **cuerpo** (bloque `{ }`).

```
tipo_retorno nombre(tipo param1, tipo param2, ...) {
    /* cuerpo */
    return valor;   /* obligatorio si tipo_retorno != void */
}
```

### Patrón 1: función que calcula y devuelve

```c
/* Devuelve el mayor de dos enteros */
int max(int a, int b) {
    if (a > b) return a;
    return b;
}
```

Llamada:

```c
int resultado = max(5, 3);   // resultado == 5
```

**Los parámetros son por valor**: `a` y `b` son copias. Cambiar `a` dentro de la función NO cambia la variable original del llamador.

### Patrón 2: función `void` (efecto de lado)

```c
void imprimir_separador(int n) {
    for (int i = 0; i < n; i++) printf("-");
    printf("\n");
}
```

No usa `return` (o usa `return;` sin valor).

### Patrón 3: prototipo

Si defines la función **después** de `main`, el compilador la desconoce cuando llega a la llamada. Solución: declarar el **prototipo** antes de `main`.

```c
#include <stdio.h>

int es_par(int n);          /* prototipo */

int main(void) {
    printf("%d\n", es_par(4));
    return 0;
}

int es_par(int n) {         /* definicion */
    return n % 2 == 0;
}
```

El prototipo es solo la firma + `;`. Es buena práctica ponerlos todos arriba.

### Patrón 4: ámbito de variables

```c
int x = 10;          /* global: visible en todo el fichero */

void funcion(void) {
    int x = 99;      /* local: oculta la global dentro de esta funcion */
    printf("%d\n", x);  /* imprime 99 */
}
```

Regla de oro: **usa variables locales por defecto**. Las globales dificultan la depuración. Solo usa globales si hay una razón muy concreta.

### Patrón 5: array como parámetro

Un array se pasa como **puntero a su primer elemento** (no se copia). Hay que pasar el tamaño aparte:

```c
int maximo_array(int arr[], int n) {
    int max = arr[0];
    for (int i = 1; i < n; i++)
        if (arr[i] > max) max = arr[i];
    return max;
}
```

Llamada:

```c
int v[] = {3, 7, 1, 9, 2};
printf("%d\n", maximo_array(v, 5));   // 9
```

---

## Worked example

**Programa**: calcular el factorial de varios números usando una función.

### Paso 1 — identificar la unidad de lógica

`factorial(n)` es un cálculo independiente. Lo encapsulamos.

### Paso 2 — escribir el prototipo

```c
long factorial(int n);
```

### Paso 3 — definir la función

```c
long factorial(int n) {
    if (n < 0) return -1;   /* error: factorial no definido para negativos */
    long resultado = 1;
    for (int i = 2; i <= n; i++)
        resultado *= i;
    return resultado;
}
```

### Paso 4 — usar la función en `main`

```c
#include <stdio.h>

long factorial(int n);   /* prototipo */

int main(void) {
    int nums[] = {0, 1, 5, 10};
    int tam = 4;
    for (int i = 0; i < tam; i++) {
        printf("%d! = %ld\n", nums[i], factorial(nums[i]));
    }
    return 0;
}

long factorial(int n) {
    if (n < 0) return -1;
    long resultado = 1;
    for (int i = 2; i <= n; i++)
        resultado *= i;
    return resultado;
}
```

### Salida

```
0! = 1
1! = 1
5! = 120
10! = 3628800
```

### Por qué funciona

- `factorial` no sabe nada de `nums` ni del bucle de `main`. Es una caja negra reutilizable.
- El tipo `long` evita desbordamiento para valores grandes.
- El prototipo antes de `main` permite que el compilador valide la llamada.

---

## Errores típicos en C

1. **Olvidar el prototipo y definir la función después de `main`**
   El compilador asume que la función devuelve `int` (en C89) o da error (C11). Pon siempre el prototipo.

2. **No poner `return` en una función no-`void`**
   ```c
   int suma(int a, int b) { int r = a + b; }  /* falta return r; */
   ```
   Compila con warning; el valor de retorno es basura.

3. **Creer que los parámetros son por referencia**
   ```c
   void incrementa(int x) { x++; }
   int n = 5;
   incrementa(n);
   printf("%d\n", n);   /* imprime 5, NO 6 */
   ```
   Los parámetros son copias. Para modificar el original se necesitan punteros (módulo posterior).

4. **Pasar un array sin su tamaño**
   Dentro de la función no puedes usar `sizeof(arr)` para obtener el número de elementos: el array ya es un puntero. Pasa el tamaño siempre como parámetro extra.

5. **Variable local usada sin inicializar**
   ```c
   int calcular(void) {
       int resultado;
       /* ... olvidas asignar resultado ... */
       return resultado;   /* basura */
   }
   ```
   Inicializa siempre: `int resultado = 0;`.

---

## Ejercicios

Carpeta de práctica: `practica/04-funciones/`

| # | Enunciado | Dificultad | Salida de ejemplo |
|---|---|---|---|
| 01 | Escribe `es_par(n)` que devuelve 1 si `n` es par, 0 si no. Pruébala con los números del 1 al 10. | (facil) Fácil | `1: impar   2: par   3: impar ...` |
| 02 | Escribe `max(a,b)` y `min(a,b)`. Pide dos enteros al usuario e imprime el mayor y el menor. | (facil) Fácil | `Max: 8   Min: 3` |
| 03 | Escribe `factorial(n)`. Pide un número entre 0 y 12 e imprime su factorial. | (facil) Fácil | `5! = 120` |
| 04 | Escribe `potencia(base, exp)` (enteros, exp >= 0) sin usar `pow`. Prueba con varios pares. | (media) Medio | `2^10 = 1024` |
| 05 | Escribe `es_primo(n)` que devuelve 1 si `n` es primo. Imprime todos los primos entre 2 y 50. | (media) Medio | `2 3 5 7 11 13 17 19 23 29 31 37 41 43 47` |
| 06 | Escribe `imprimir_tabla(n)` que imprime la tabla de multiplicar de `n` (del 1 al 10). Pide `n` al usuario. | (media) Medio | `3 x 1 = 3  ...  3 x 10 = 30` |
| 07 | Escribe `maximo_array(arr, n)` y `minimo_array(arr, n)`. Lee 8 enteros en un array e imprime el máximo y el mínimo. | (dificil) Difícil | `Max: 99   Min: -4` |

- Esqueleto alumno: `practica/04-funciones/ejNN_practica.c`
- Solución completa: `practica/04-funciones/ejNN_modelo.c`

---

## Conexiones

- [[Curso_C/00_README]]
- [[MOC_Linux]]
- [[Curso_C/modelo/03-bucles]] — módulo anterior: bucles for/while
- [[Curso_C/modelo/05-arrays-cadenas]] — módulo siguiente: punteros y paso por referencia
