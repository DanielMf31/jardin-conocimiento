---
title: "Modulo 07: Punteros en C"
date: 2026-06-16
tags: [programacion/c, programacion/c/punteros, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [punteros C, pointers C, punteros basicos]
---

# Modulo 07: Punteros en C

## Idea central

Un puntero es una variable que guarda una **direccion de memoria**, no un valor directo. Esto permite que una funcion modifique variables del llamador, recorrer arrays de forma eficiente y construir estructuras de datos dinamicas. Sin punteros no hay paso por referencia, no hay arrays dinamicos, no hay C real.

## Que aprendes

| Concepto | Para que sirve |
|---|---|
| Operador `&` (direccion) | Obtener la direccion de memoria de una variable |
| Operador `*` (desreferencia) | Leer o escribir el valor en la direccion guardada |
| Declarar un puntero | `int *p;` — p guarda direcciones de int |
| Pasar por referencia | Que una funcion modifique la variable del llamador |
| Relacion puntero-array | El nombre de un array ES un puntero a su primer elemento |
| Aritmetica de punteros | `p+1` avanza un elemento (no un byte) del tipo apuntado |

---

## Explicacion

### Categoria 1 — Direccion y desreferencia

**Patron conceptual**: cada variable vive en una celda de memoria con una direccion unica. `&x` da esa direccion; `*p` accede al contenido de la celda apuntada.

```c
int x = 42;
int *p = &x;   // p guarda la direccion de x
printf("%p\n", (void *)p);  // imprime la direccion (ej: 0x7ffd...)
printf("%d\n", *p);         // imprime 42 (valor en esa direccion)
*p = 100;                   // modifica x a traves del puntero
printf("%d\n", x);          // imprime 100
```

**Regla de lectura**: lee `int *p` como "p es un puntero a int".

---

### Categoria 2 — Paso por referencia

**Patron**: para que una funcion modifique una variable del llamador, recibe su direccion (`int *`) y usa `*` para acceder.

```c
void doblar(int *n) {
    *n = *n * 2;  // modifica la variable original
}

int main(void) {
    int x = 5;
    doblar(&x);   // pasas la direccion, no el valor
    printf("%d\n", x);  // 10
    return 0;
}
```

Sin `&` en la llamada y sin `*` en la funcion: la funcion recibe una copia y el original no cambia.

---

### Categoria 3 — Relacion puntero-array

**Patron**: `arr` (sin corchetes) es equivalente a `&arr[0]`. Se puede recorrer un array con aritmetica de punteros.

```c
int arr[4] = {10, 20, 30, 40};
int *p = arr;          // equivale a &arr[0]
printf("%d\n", *p);    // 10
printf("%d\n", *(p+2)); // 30
p++;                   // avanza al siguiente int (4 bytes)
printf("%d\n", *p);    // 20
```

`p + i` es la direccion del elemento i-esimo; `*(p+i)` equivale a `arr[i]`.

---

## Worked example

**Problema**: escribir una funcion `swap` que intercambie dos enteros, y otra `rango` que devuelva el maximo y el minimo de un array por referencia. Mostrar ambos resultados.

```c
#include <stdio.h>

/* Intercambia los valores de a y b a traves de punteros */
void swap(int *a, int *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

/*
 * Recorre el array con un puntero.
 * Escribe el maximo en *pmax y el minimo en *pmin.
 */
void rango(int *arr, int n, int *pmax, int *pmin) {
    *pmax = arr[0];
    *pmin = arr[0];
    int *p = arr + 1;          // puntero al segundo elemento
    int *fin = arr + n;        // puntero "pasado el ultimo"
    while (p < fin) {
        if (*p > *pmax) *pmax = *p;
        if (*p < *pmin) *pmin = *p;
        p++;                   // avanza un int hacia adelante
    }
}

int main(void) {
    // --- Paso 1: swap ---
    int x = 3, y = 9;
    printf("Antes:  x=%d  y=%d\n", x, y);
    swap(&x, &y);
    printf("Despues: x=%d  y=%d\n", x, y);

    // --- Paso 2: rango ---
    int datos[6] = {4, 1, 9, 2, 7, 3};
    int maximo, minimo;
    rango(datos, 6, &maximo, &minimo);
    printf("Max=%d  Min=%d\n", maximo, minimo);

    return 0;
}
```

**Traza mental paso a paso**:

1. `swap(&x, &y)` — `a` apunta a x, `b` apunta a.
2. `tmp = *a` guarda 3. `*a = *b` pone 9 en x. `*b = tmp` pone 3 en.
3. `rango` recibe el array como puntero; `p` empieza en `arr+1` = segundo elemento.
4. El bucle compara `*p` contra `*pmax` y `*pmin`, actualizando cuando toca.
5. Al salir, `maximo` y `minimo` tienen los valores correctos porque se pasaron sus direcciones.

**Salida esperada**:
```
Antes:  x=3  y=9
Despues: x=9  y=3
Max=9  Min=1
```

---

## Errores tipicos en C

| # | Error | Ejemplo incorrecto | Por que falla |
|---|---|---|---|
| 1 | Puntero sin inicializar | `int *p; *p = 5;` | `p` contiene basura; escribe en memoria aleatoria → comportamiento indefinido |
| 2 | Olvidar `&` al pasar por referencia | `doblar(x)` en vez de `doblar(&x)` | La funcion recibe copia; el original no cambia |
| 3 | Olvidar `*` al desreferenciar | `*p = p + 1` en vez de `*p = *p + 1` | Suma 1 a la direccion, no al valor; probablemente warning de tipos |
| 4 | Aritmetica fuera del array | `p = arr + 10` con array de 5 | Puntero fuera de rango; leer `*p` es comportamiento indefinido |
| 5 | Confundir `p++` con `(*p)++` | `p++` cuando quieres incrementar el valor | `p++` avanza el puntero (cambia a que celda apunta); `(*p)++` incrementa el valor guardado |

---

## Ejercicios

Todos los ejercicios van en `practica/07-punteros/`. Cada uno tiene esqueleto (`ejNN_practica.c`) y solucion (`ejNN_modelo.c`).

---

**ej01** — (facil) Imprimir direccion y valor
Declara una variable `int n = 77`. Usa un puntero para imprimir su direccion (con `%p`) y su valor (con `%d`). Despues modifica el valor a traves del puntero e imprimelo de nuevo.
Entrada: ninguna.
Salida esperada (la direccion variara):
```
Direccion: 0x7ffd...
Valor original: 77
Valor modificado: 100
```
Ficheros: `practica/07-punteros/ej01_practica.c` | `practica/07-punteros/ej01_modelo.c`

---

**ej02** — (facil) Funcion incrementar por referencia
Escribe `void incrementar(int *p, int delta)` que suma `delta` al entero apuntado. Llama desde `main` con dos variables distintas y muestra los resultados.
Entrada: ninguna (valores fijos en main).
Salida esperada:
```
a=10 -> 15
b=3  -> 8
```
Ficheros: `practica/07-punteros/ej02_practica.c` | `practica/07-punteros/ej02_modelo.c`

---

**ej03** — (facil) Swap de dos enteros
Escribe `void swap(int *a, int *b)` que intercambie dos enteros. Demuestra que funciona imprimiendo antes y despues.
Entrada: ninguna.
Salida esperada:
```
Antes:  a=5 b=20
Despues: a=20 b=5
```
Ficheros: `practica/07-punteros/ej03_practica.c` | `practica/07-punteros/ej03_modelo.c`

---

**ej04** — (media) Recorrer array con puntero
Dado `int arr[] = {3, 1, 4, 1, 5, 9, 2, 6}`, recorre el array usando SOLO un puntero (sin usar `arr[i]`). Imprime cada elemento seguido de su indice (calcula el indice como `p - arr`).
Entrada: ninguna.
Salida esperada:
```
[0] = 3
[1] = 1
[2] = 4
[3] = 1
[4] = 5
[5] = 9
[6] = 2
[7] = 6
```
Ficheros: `practica/07-punteros/ej04_practica.c` | `practica/07-punteros/ej04_modelo.c`

---

**ej05** — (media) Max y min por referencia
Escribe `void rango(int *arr, int n, int *pmax, int *pmin)` que encuentre el maximo y minimo de un array de n enteros. Usa aritmetica de punteros en el recorrido. Llama desde main con un array de 7 elementos.
Entrada: ninguna.
Salida esperada (con `{4, 1, 9, 2, 7, 3, 5}`):
```
Max = 9
Min = 1
```
Ficheros: `practica/07-punteros/ej05_practica.c` | `practica/07-punteros/ej05_modelo.c`

---

**ej06** — (media) Suma de array con puntero
Escribe `int suma_array(int *arr, int n)` que devuelva la suma usando un puntero (sin indexacion `[]`). Llama con un array de 6 enteros leidos por teclado.
Entrada (ejemplo):
```
1 2 3 4 5 6
```
Salida esperada:
```
Suma = 21
```
Ficheros: `practica/07-punteros/ej06_practica.c` | `practica/07-punteros/ej06_modelo.c`

---

**ej07** — (dificil) Invertir array in-place con punteros
Escribe `void invertir(int *arr, int n)` que invierta el array sin array auxiliar, usando DOS punteros: uno al inicio y otro al final, avanzando hacia el centro con swap. Muestra el array antes y despues.
Entrada (ejemplo):
```
5
10 20 30 40 50
```
Salida esperada:
```
Original:  10 20 30 40 50
Invertido: 50 40 30 20 10
```
Ficheros: `practica/07-punteros/ej07_practica.c` | `practica/07-punteros/ej07_modelo.c`

---

## Conexiones

- [[Curso_C/00_README]]
- [[MOC_Linux]]
- [[Curso_C/modelo/06-matrices]] — modulo anterior: arrays y strings
- [[Curso_C/modelo/08-structs]] — modulo siguiente: estructuras
