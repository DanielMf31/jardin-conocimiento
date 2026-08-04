---
title: "Módulo 01 — Variables, tipos y entrada/salida en C"
date: 2026-06-16
tags: [programacion/c, curso/c, programacion/fundamentos]
type: nota
status: en-progreso
source: claude-code
aliases: [variables-c, tipos-c, printf-scanf, modulo-01-c]
---

# Módulo 01 — Variables, tipos y entrada/salida en C

## Idea central

Todo programa útil necesita **guardar datos**, **recibirlos del usuario** y **mostrar resultados**. En C, los datos viven en variables con un tipo fijo determinado en tiempo de compilación. El compilador no adivina: si dices `int`, guarda un entero; si dices `float`, guarda un decimal. Ese contrato rígido es lo que hace a C predecible y rápido.

---

## Qué aprendes

| Concepto | Para qué sirve |
|---|---|
| `int`, `float`, `double`, `char` | Declarar el tipo correcto para cada dato |
| Declaración e inicialización | Reservar memoria y asignar valor inicial |
| `printf` con `%d %f %c %s` | Mostrar datos formateados en pantalla |
| `scanf` con `&` | Leer datos desde el teclado |
| Operadores aritméticos y `%` | Calcular: suma, resta, producto, división, resto |
| `const` | Constantes que el compilador no deja cambiar |
| Casting `(int)` / `(float)` | Convertir entre tipos explícitamente |

---

## Explicación

### Categoría: tipos de dato

C tiene tipos primitivos con tamaño fijo (en plataformas de 32/64 bits típicas):

| Tipo | Tamaño típico | Rango aproximado | Formato `printf`/`scanf` |
|---|---|---|---|
| `int` | 4 bytes | −2 147 483 648 … 2 147 483 647 | `%d` |
| `float` | 4 bytes | ~6 cifras significativas | `%f` |
| `double` | 8 bytes | ~15 cifras significativas | `%lf` en scanf, `%f` en printf |
| `char` | 1 byte | 0 … 255 (un carácter ASCII) | `%c` / `%s` para cadenas |

### Patrón: declarar e inicializar

```c
// Declarar (reserva memoria, valor indeterminado)
int edad;

// Inicializar en la misma línea (recomendado)
int edad = 25;
float nota = 7.5f;
double pi = 3.14159265358979;
char inicial = 'A';
```

> **Regla de oro:** inicializa siempre. Una variable sin inicializar contiene basura de memoria.

### Patrón: printf

```c
printf("Hola, %s. Tienes %d años y una nota de %.2f\n", nombre, edad, nota);
```

- `%d` → entero
- `%f` / `%.2f` → flotante (`.2` = 2 decimales)
- `%c` → carácter
- `%s` → cadena de caracteres
- `\n` → salto de línea

### Patrón: scanf

```c
int x;
scanf("%d", &x);   // SIEMPRE & delante de la variable
```

Para cadenas cortas sin espacios:
```c
char nombre[50];
scanf("%49s", nombre);  // sin & porque nombre ya es puntero al array
```

### Patrón: operadores aritméticos

```c
int a = 17, b = 5;
int suma    = a + b;   // 22
int resta   = a - b;   // 12
int producto = a * b;  // 85
int cociente = a / b;  // 3  (división entera entre enteros)
int resto    = a % b;  // 2  (módulo)
float division = (float)a / b;  // 3.4  (casting fuerza división real)
```

### Patrón: const

```c
const float PI = 3.14159f;
// PI = 3.0f;  → error de compilación: no se puede modificar
```

### Patrón: casting explícito

```c
int n = 7;
float mitad = (float)n / 2;   // 3.5  (sin cast: 3)
int truncado = (int)3.99;     // 3    (trunca, no redondea)
```

---

## Worked example

**Problema:** pedir al usuario su nombre y su año de nacimiento, y mostrar cuántos años tiene en 2026.

```c
/*
 * Worked example — Módulo 01
 * Edad a partir del año de nacimiento.
 * Compilar: gcc -std=c11 -Wall ejemplo_edad.c -o ejemplo_edad && ./ejemplo_edad
 */
#include <stdio.h>

int main(void) {
    /* 1. Declarar variables */
    char nombre[50];
    int anio_nacimiento;
    const int ANIO_ACTUAL = 2026;

    /* 2. Pedir datos al usuario */
    printf("Introduce tu nombre: ");
    scanf("%49s", nombre);               // sin & en arrays

    printf("Introduce tu año de nacimiento: ");
    scanf("%d", &anio_nacimiento);       // & obligatorio en int

    /* 3. Calcular */
    int edad = ANIO_ACTUAL - anio_nacimiento;

    /* 4. Mostrar resultado */
    printf("Hola, %s. En %d tienes %d años.\n",
           nombre, ANIO_ACTUAL, edad);

    return 0;
}
```

**Paso a paso:**
1. `char nombre[50]` reserva 50 bytes para la cadena — suficiente para un nombre normal.
2. `scanf("%49s", nombre)` lee hasta 49 caracteres (el 50º es el `\0` terminador automático).
3. `const int ANIO_ACTUAL = 2026` impide que alguien cambie el año por error.
4. `edad = ANIO_ACTUAL - anio_nacimiento` es aritmética entera pura: no necesitamos float.
5. `%s` en printf imprime la cadena; `%d` imprime enteros.

**Ejemplo de ejecución:**
```
Introduce tu nombre: Ana
Introduce tu año de nacimiento: 1998
Hola, Ana. En 2026 tienes 28 años.
```

---

## Errores típicos en C

| Error | Código incorrecto | Código correcto |
|---|---|---|
| Olvidar `&` en scanf | `scanf("%d", x);` | `scanf("%d", &x);` |
| Variable sin inicializar | `int suma; printf("%d", suma);` | `int suma = 0;` |
| División entera inesperada | `float m = 7 / 2;` → `3.0` | `float m = 7.0f / 2;` → `3.5` |
| Modificar una constante | `const int N = 5; N = 10;` | No se puede: usar variable normal |
| Overflow silencioso | `int x = 3000000000;` | Usar `long` o `long long` |

---

## Ejercicios

Practica lo de este módulo. Cada enlace abre el ejercicio con su enunciado, diagrama de flujo, explicación y el código listo para copiar.

- [[Curso_C/practica/01-variables/ej01|Ej 01 — Pedir nombre al usuario y saludar con printf (verde)]]
- [[Curso_C/practica/01-variables/ej02|Ej 02 — Leer dos enteros y mostrar suma, resta y producto (verde)]]
- [[Curso_C/practica/01-variables/ej03|Ej 03 — Leer tres notas (float) y mostrar la media con 2 decimales (verde)]]
- [[Curso_C/practica/01-variables/ej04|Ej 04 — Leer temperatura en Celsius y convertir a Fahrenheit (amarillo)]]
- [[Curso_C/practica/01-variables/ej05|Ej 05 — Leer el radio y calcular area y perimetro de un circulo (amarillo)]]
- [[Curso_C/practica/01-variables/ej06|Ej 06 — Leer dos enteros e intercambiarlos con una variable auxiliar (amarillo)]]
- [[Curso_C/practica/01-variables/ej07|Ej 07 — Cociente y resto sin usar % para el resto (rojo)]]

## Conexiones

- [[Curso_C/00_README]]
- Linux
- Módulo siguiente: `[[Curso_C/modelo/02-condicionales]]`
