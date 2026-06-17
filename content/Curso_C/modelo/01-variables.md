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

Los ficheros están en `practica/01-variables/`. Para cada ejercicio existe un esqueleto (`ejNN_practica.c`) y la solución completa (`ejNN_modelo.c`).

---

### Ej01 — Hola con nombre (facil)
**Enunciado:** Pide al usuario su nombre con `scanf` y saluda con `printf`.
**Salida esperada:**
```
¿Cómo te llamas? Laura
¡Hola, Laura!
```
Ficheros: `practica/01-variables/ej01_practica.c` · `ej01_modelo.c`

---

### Ej02 — Suma, resta y producto de dos enteros (facil)
**Enunciado:** Lee dos enteros `a` y `b`. Muestra su suma, resta y producto.
**Salida esperada:**
```
a = 8, b = 3
Suma: 11
Resta: 5
Producto: 24
```
Ficheros: `practica/01-variables/ej02_practica.c` · `ej02_modelo.c`

---

### Ej03 — Media de tres notas (facil)
**Enunciado:** Lee tres notas (float). Calcula y muestra la media con 2 decimales.
**Salida esperada:**
```
Nota 1: 6.5
Nota 2: 8.0
Nota 3: 7.0
Media: 7.17
```
Ficheros: `practica/01-variables/ej03_practica.c` · `ej03_modelo.c`

---

### Ej04 — Celsius a Fahrenheit (media)
**Enunciado:** Lee una temperatura en Celsius (float). Convierte a Fahrenheit con la fórmula `F = C * 9/5 + 32`. Muestra ambas con 1 decimal.
**Salida esperada:**
```
Temperatura en Celsius: 100.0
En Fahrenheit: 212.0
```
Ficheros: `practica/01-variables/ej04_practica.c` · `ej04_modelo.c`

---

### Ej05 — Área y perímetro de un círculo (media)
**Enunciado:** Lee el radio (float). Calcula área (`PI * r²`) y perímetro (`2 * PI * r`) usando `const float PI = 3.14159f`. Muestra con 2 decimales.
**Salida esperada:**
```
Radio: 5.0
Área: 78.54
Perímetro: 31.42
```
Ficheros: `practica/01-variables/ej05_practica.c` · `ej05_modelo.c`

---

### Ej06 — Intercambiar dos variables (media)
**Enunciado:** Lee dos enteros. Intercámbialos usando una variable auxiliar. Muestra los valores antes y después del intercambio.
**Salida esperada:**
```
Antes: a = 10, b = 20
Después: a = 20, b = 10
```
Ficheros: `practica/01-variables/ej06_practica.c` · `ej06_modelo.c`

---

### Ej07 — Cociente y resto (dificil)
**Enunciado:** Lee dos enteros `dividendo` y `divisor`. Muestra cociente y resto (sin usar `/` ni `%` para el resto — calcúlalo como `dividendo - cociente * divisor`). Maneja el caso divisor = 0 con un mensaje de error.
**Salida esperada (caso normal):**
```
Dividendo: 17
Divisor: 5
Cociente: 3
Resto: 2
```
**Salida esperada (divisor 0):**
```
Dividendo: 8
Divisor: 0
Error: división por cero.
```
Ficheros: `practica/01-variables/ej07_practica.c` · `ej07_modelo.c`

---

## Conexiones

- [[Curso_C/00_README]]
- [[MOC_Linux]]
- Módulo siguiente: `[[Curso_C/modelo/02-condicionales]]`
