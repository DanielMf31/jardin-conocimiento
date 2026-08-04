---
title: "Modulo 08: Structs en C"
date: 2026-06-16
tags: [programacion/c, curso, programacion/c/structs, programacion/tipos-compuestos]
type: nota
status: en-progreso
source: claude-code
aliases: [structs en C, struct C, typedef struct]
---

# Modulo 08: Structs en C

## Idea central

Los arrays agrupan valores **del mismo tipo**. Un `struct` agrupa valores de **tipos distintos** bajo un solo nombre. Es la herramienta basica de C para modelar entidades del mundo real (un punto, una persona, una fecha) sin mezclar variables sueltas que se pierden.

Sin struct:
```c
char nombre[50];
int edad;
float nota;
// ... y si tienes 30 alumnos?
```

Con struct:
```c
typedef struct { char nombre[50]; int edad; float nota; } Alumno;
Alumno grupo[30];   // limpio, manejable
```

---

## Que aprendes

| Concepto | Para que sirve |
|---|---|
| `struct` literal | Definir un tipo compuesto con campos de distinto tipo |
| Acceso con `.` | Leer o escribir un campo de una variable struct |
| `typedef struct` | Dar un alias corto para no escribir `struct X` cada vez |
| Struct como parametro | Pasar una entidad completa a una funcion |
| Array de structs | Manejar colecciones de entidades (tabla de alumnos, etc.) |

---

## Explicacion

### Patron 1 — Definir y usar un struct

**Categoria**: tipo compuesto en C
**Patron**: definir la plantilla, declarar variable, acceder con punto
**Sintaxis**:

```c
struct NombreTipo {
    tipo1 campo1;
    tipo2 campo2;
};

struct NombreTipo var;
var.campo1 = valor1;
```

Ejemplo minimo:

```c
struct Punto {
    double x;
    double y;
};

struct Punto p;
p.x = 3.0;
p.y = 4.0;
printf("(%g, %g)\n", p.x, p.y);
```

---

### Patron 2 — typedef para simplificar

**Categoria**: alias de tipo
**Patron**: combinar `typedef` con la definicion del struct

```c
typedef struct {
    double x;
    double y;
} Punto;            // ahora Punto es el nombre del tipo

Punto p = {3.0, 4.0};   // inicializador de llaves
printf("x=%.2f\n", p.x);
```

Con `typedef` ya no necesitas escribir `struct Punto` cada vez.

---

### Patron 3 — Struct como parametro de funcion

**Categoria**: paso por valor vs. por puntero
**Patron**: pasar el struct completo (copia) o su direccion (`&`)

```c
// Paso por valor — la funcion trabaja sobre una copia
double area(Rectangulo r) {
    return r.ancho * r.alto;
}

// Paso por puntero — puede modificar el original
void cumpleanios(Persona *p) {
    p->edad++;      // flecha -> para punteros a struct
}
```

> Regla practica: para structs grandes o cuando necesitas modificar el original, usa puntero (`*`). Para structs pequenos de solo lectura, por valor esta bien.

---

### Patron 4 — Array de structs

```c
#define N 5
Alumno grupo[N];

for (int i = 0; i < N; i++) {
    scanf("%s %f", grupo[i].nombre, &grupo[i].nota);
}
```

Acceso: `grupo[i].campo` — primero el indice del array, luego el punto.

---

## Worked example

**Problema**: Representar dos puntos en 2D y calcular la distancia euclidea entre ellos.

```c
#include <stdio.h>
#include <math.h>

/* Paso 1: definir el tipo Punto con typedef */
typedef struct {
    double x;
    double y;
} Punto;

/* Paso 2: funcion que recibe dos Punto por valor y devuelve double */
double distancia(Punto a, Punto b) {
    double dx = a.x - b.x;   // diferencia en x
    double dy = a.y - b.y;   // diferencia en y
    return sqrt(dx*dx + dy*dy);
}

int main(void) {
    /* Paso 3: declarar e inicializar con llaves */
    Punto p1 = {0.0, 0.0};
    Punto p2 = {3.0, 4.0};

    /* Paso 4: llamar a la funcion y mostrar resultado */
    printf("Distancia: %.2f\n", distancia(p1, p2));
    // Salida: Distancia: 5.00

    return 0;
}
```

**Traza paso a paso**:
1. `Punto p1 = {0.0, 0.0}` — inicializa los dos campos en orden de declaracion.
2. `distancia(p1, p2)` — C copia los dos structs en los parametros `a` y `b`.
3. `dx = 0-3 = -3`, `dy = 0-4 = -4`, `sqrt(9+16) = sqrt(25) = 5.0`.
4. `printf` imprime `5.00`.

> Nota: para compilar con `sqrt` necesitas `-lm`: `gcc -std=c11 -Wall ej.c -lm -o ej`

---

## Errores tipicos en C

| # | Error | Por que ocurre | Como evitarlo |
|---|---|---|---|
| 1 | `scanf("%s", &persona.nombre)` | `nombre` ya es un array = puntero; el `&` extra es incorrecto | Escribe `scanf("%s", persona.nombre)` (sin `&`) |
| 2 | `struct` sin `;` al final de la definicion | La llave de cierre `}` necesita `;` en C | `} NombreTipo;` o `};` con typedef separado |
| 3 | Usar `.` con un puntero a struct | `ptr.campo` falla; debes usar `ptr->campo` o `(*ptr).campo` | Recuerda: variable → punto, puntero → flecha |
| 4 | Campo `char[]` asignado con `=` | `p.nombre = "Ana"` no compila; los arrays no son asignables | Usa `strcpy(p.nombre, "Ana")` de `<string.h>` |
| 5 | Comparar structs con `==` | C no compara structs campo a campo automaticamente | Escribe una funcion que compare campo por campo |

---

## Ejercicios

Practica lo de este módulo. Cada enlace abre el ejercicio con su enunciado, diagrama de flujo, explicación y el código listo para copiar.

- [[Curso_C/practica/08-structs/ej01|Ej 01 — Define Punto {x, y}, lee dos puntos del usuario e imprimelos con… (verde)]]
- [[Curso_C/practica/08-structs/ej02|Ej 02 — Funcion distancia(Punto a, Punto b) que calcula la distancia euclidea… (verde)]]
- [[Curso_C/practica/08-structs/ej03|Ej 03 — Define Persona {nombre[50], edad}, lee datos del usuario e imprimelos… (verde)]]
- [[Curso_C/practica/08-structs/ej04|Ej 04 — Define Rectangulo {ancho, alto}, calcula area y perimetro con… (amarillo)]]
- [[Curso_C/practica/08-structs/ej05|Ej 05 — Define Fecha {dia, mes, anio} y compara dos fechas indicando cual es… (amarillo)]]
- [[Curso_C/practica/08-structs/ej06|Ej 06 — Array de 4 Alumno {nombre, nota}, muestra lista, calcula media e… (amarillo)]]
- [[Curso_C/practica/08-structs/ej07|Ej 07 — Agenda de 5 contactos hardcodeados (rojo)]]

## Conexiones

- [[Curso_C/00_README]]
- [[MOC_Linux]]
- [[Curso_C/modelo/07-punteros]] — modulo anterior: arrays y strings
- [[Curso_C/modelo/09-archivos]] — modulo siguiente: punteros (necesarios para modificar structs en funciones)
