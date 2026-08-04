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

Practica lo de este módulo. Cada enlace abre el ejercicio con su enunciado, diagrama de flujo, explicación y el código listo para copiar.

- [[Curso_C/practica/07-punteros/ej01|Ej 01 — Imprimir la direccion y el valor de una variable usando un puntero,… (verde)]]
- [[Curso_C/practica/07-punteros/ej02|Ej 02 — Funcion incrementar(int *p, int delta) que suma delta al entero… (verde)]]
- [[Curso_C/practica/07-punteros/ej03|Ej 03 — Funcion swap(int *a, int *b) que intercambia dos enteros por… (verde)]]
- [[Curso_C/practica/07-punteros/ej04|Ej 04 — Recorrer un array con un puntero (amarillo)]]
- [[Curso_C/practica/07-punteros/ej05|Ej 05 — Funcion rango(int *arr, int n, int *pmax, int *pmin) que encuentra… (amarillo)]]
- [[Curso_C/practica/07-punteros/ej06|Ej 06 — Funcion suma_array(int *arr, int n) que devuelve la suma usando… (amarillo)]]
- [[Curso_C/practica/07-punteros/ej07|Ej 07 — Funcion invertir(int *arr, int n) que invierte el array in-place con… (rojo)]]

## Conexiones

- [[Curso_C/00_README]]
- [[MOC_Linux]]
- [[Curso_C/modelo/06-matrices]] — modulo anterior: arrays y strings
- [[Curso_C/modelo/08-structs]] — modulo siguiente: estructuras
