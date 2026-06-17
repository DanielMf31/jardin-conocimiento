---
title: "Curso C — Modulo 08: Structs"
date: 2026-06-16
tags: [programacion/c, curso, programacion/c/structs, programacion/tipos-compuestos]
type: nota
status: en-progreso
source: claude-code
aliases: [structs en C, struct C, typedef struct]
---

# Modulo 08 — Structs

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

Los ficheros estan en `practica/08-structs/`. Cada ejercicio tiene un esqueleto `ejNN_practica.c` que debes completar y una solucion `ejNN_modelo.c`.

---

### Ejercicio 01 — Punto y coordenadas (facil)
**Enunciado**: Define un `typedef struct` llamado `Punto` con campos `x` e `y` (ambos `double`). En `main`, crea dos puntos, pidelelos al usuario e imprimelos con formato `(x, y)`.
**Entrada de ejemplo**:
```
1.5 2.0
-3.0 4.5
```
**Salida esperada**:
```
Punto 1: (1.50, 2.00)
Punto 2: (-3.00, 4.50)
```
Ficheros: `practica/08-structs/ej01_practica.c` / `ej01_modelo.c`

---

### Ejercicio 02 — Distancia entre dos puntos (facil)
**Enunciado**: Ampliar el ejercicio anterior. Escribe una funcion `double distancia(Punto a, Punto b)` que calcule la distancia euclidea. Muestra el resultado con dos decimales.
**Nota**: compila con `-lm` para `sqrt`.
**Entrada de ejemplo**:
```
0.0 0.0
3.0 4.0
```
**Salida esperada**:
```
Distancia: 5.00
```
Ficheros: `practica/08-structs/ej02_practica.c` / `ej02_modelo.c`

---

### Ejercicio 03 — Persona: mostrar datos (facil)
**Enunciado**: Define `typedef struct Persona` con `nombre[50]` (char) y `edad` (int). Pide datos al usuario y escribe una funcion `void mostrar_persona(Persona p)` que imprime nombre y edad con formato.
**Entrada de ejemplo**:
```
Ana 28
```
**Salida esperada**:
```
Nombre: Ana, Edad: 28
```
Ficheros: `practica/08-structs/ej03_practica.c` / `ej03_modelo.c`

---

### Ejercicio 04 — Rectangulo y area (media)
**Enunciado**: Define `typedef struct Rectangulo` con `ancho` y `alto` (ambos `double`). Escribe funciones `double area(Rectangulo r)` y `double perimetro(Rectangulo r)`. Lee datos del usuario y muestra area y perimetro.
**Entrada de ejemplo**:
```
5.0 3.0
```
**Salida esperada**:
```
Area: 15.00
Perimetro: 16.00
```
Ficheros: `practica/08-structs/ej04_practica.c` / `ej04_modelo.c`

---

### Ejercicio 05 — Comparar fechas (media)
**Enunciado**: Define `typedef struct Fecha` con `dia`, `mes`, `anio` (int). Escribe una funcion `int fecha_anterior(Fecha a, Fecha b)` que devuelve 1 si `a` es anterior a `b`, 0 si son iguales, -1 si `a` es posterior. Lee dos fechas e imprime cual es anterior.
**Entrada de ejemplo**:
```
15 6 2025
20 3 2025
```
**Salida esperada**:
```
La primera fecha es posterior.
```
Ficheros: `practica/08-structs/ej05_practica.c` / `ej05_modelo.c`

---

### Ejercicio 06 — Array de alumnos y media (media)
**Enunciado**: Define `typedef struct Alumno` con `nombre[50]` y `nota` (float). Lee 4 alumnos, muestra la lista y calcula la media de notas. Indica tambien el alumno con la nota mas alta.
**Entrada de ejemplo**:
```
Luis 7.5
Marta 9.0
Pedro 6.0
Sofia 8.5
```
**Salida esperada**:
```
Lista de alumnos:
  Luis    : 7.50
  Marta   : 9.00
  Pedro   : 6.00
  Sofia   : 8.50
Media: 7.75
Mejor nota: Marta (9.00)
```
Ficheros: `practica/08-structs/ej06_practica.c` / `ej06_modelo.c`

---

### Ejercicio 07 — Agenda de contactos con busqueda (dificil)
**Enunciado**: Define `typedef struct Contacto` con `nombre[50]` y `telefono[20]`. Crea un array de 5 contactos con datos hardcodeados (inicializador de llaves). Escribe una funcion `int buscar(Contacto agenda[], int n, char *nombre)` que devuelve el indice del contacto o -1 si no existe. Pide un nombre al usuario, busca y muestra el resultado.
**Salida esperada (nombre "Elena")**:
```
Nombre: Elena
Telefono: 612345678
```
**Salida esperada (nombre "Nadie")**:
```
Contacto no encontrado.
```
Ficheros: `practica/08-structs/ej07_practica.c` / `ej07_modelo.c`

---

## Conexiones

- [[Curso_C/00_README]]
- [[MOC_Linux]]
- [[Curso_C/modelo/07-punteros]] — modulo anterior: arrays y strings
- [[Curso_C/modelo/09-archivos]] — modulo siguiente: punteros (necesarios para modificar structs en funciones)
