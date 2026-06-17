---
title: "Modulo 03: Bucles en C"
date: 2026-06-16
tags: [programacion/c, curso, programacion/control-flujo]
type: nota
status: en-progreso
source: claude-code
aliases: [bucles-c, while-c, for-c, do-while-c]
---

# Modulo 03: Bucles en C

## Idea central

Un bucle ejecuta un bloque de codigo **repetidamente** mientras se cumpla una condicion. Sin bucles, sumar 1..1000 requeriria 1000 lineas. Con un bucle, tres. Los bucles son el mecanismo principal para procesar colecciones, calcular series y construir menus interactivos.

---

## Que aprendes

| Concepto | Para que sirve |
|---|---|
| `while` | Repetir mientras una condicion sea verdadera (0 o mas iteraciones) |
| `do-while` | Igual que `while` pero garantiza al menos UNA ejecucion |
| `for` | Repetir un numero conocido de veces; contador integrado |
| `break` | Salir del bucle inmediatamente |
| `continue` | Saltar el resto de la iteracion actual y pasar a la siguiente |
| Bucles anidados | Un bucle dentro de otro; para tablas, matrices, triangulos |

---

## Explicacion

### Categoria: bucles con condicion de entrada

**Patron `while`**: comprobar → ejecutar → comprobar → ...
Si la condicion es falsa desde el inicio, el cuerpo no se ejecuta nunca.

```c
// Sintaxis
while (condicion) {
    // cuerpo
}

// Ejemplo: contar de 1 a 5
int i = 1;
while (i <= 5) {
    printf("%d\n", i);
    i++;            // sin esto: bucle infinito
}
```

### Categoria: bucles con condicion de salida

**Patron `do-while`**: ejecutar → comprobar → ejecutar → ...
Util para menus: siempre se muestra al menos una vez.

```c
// Sintaxis
do {
    // cuerpo
} while (condicion);   // <-- punto y coma obligatorio

// Ejemplo: pedir un numero positivo
int n;
do {
    printf("Introduce un numero positivo: ");
    scanf("%d", &n);
} while (n <= 0);
```

### Categoria: bucles con contador conocido

**Patron `for`**: inicializar; condicion; actualizar — todo en una sola linea.

```c
// Sintaxis
for (inicio; condicion; actualizacion) {
    // cuerpo
}

// Ejemplo: suma de 1 a N
int suma = 0;
for (int i = 1; i <= N; i++) {
    suma += i;
}
```

### Patron: `break` y `continue`

```c
// break: abandona el bucle al encontrar el primero multiplo de 7
for (int i = 1; i <= 100; i++) {
    if (i % 7 == 0) {
        printf("Primer multiplo de 7: %d\n", i);
        break;
    }
}

// continue: imprime solo los impares
for (int i = 1; i <= 10; i++) {
    if (i % 2 == 0) continue;   // salta pares
    printf("%d\n", i);
}
```

### Patron: bucles anidados

El bucle externo controla filas; el interno controla columnas.

```c
// Tabla de multiplicar del 2 y del 3
for (int fila = 2; fila <= 3; fila++) {
    for (int col = 1; col <= 5; col++) {
        printf("%d x %d = %d\n", fila, col, fila * col);
    }
}
```

---

## Worked example

**Problema**: Calcular si un numero N (leido por teclado) es primo.

**Razonamiento paso a paso**:

1. Un numero es primo si solo es divisible por 1 y por si mismo.
2. Basta comprobar divisores desde 2 hasta N-1 (o hasta sqrt(N) para optimizar, pero aqui usamos N-1 para claridad).
3. Si encontramos un divisor, ya no es primo: usamos `break` para salir antes.
4. Necesitamos una variable bandera `es_primo` para recordar si hubo divisor.

```c
#include <stdio.h>

int main(void) {
    int n;
    printf("Introduce un numero entero positivo (>1): ");
    scanf("%d", &n);

    int es_primo = 1;           // asumimos que es primo

    for (int i = 2; i < n; i++) {
        if (n % i == 0) {       // encontramos un divisor
            es_primo = 0;       // no es primo
            break;              // no hace falta seguir
        }
    }

    if (es_primo && n > 1) {
        printf("%d ES primo.\n", n);
    } else {
        printf("%d NO es primo.\n", n);
    }

    return 0;
}
```

**Traza con n = 7**:
- i=2: 7%2=1 → no divisor
- i=3: 7%3=1 → no divisor
- i=4: 7%4=3 → no divisor
- i=5: 7%5=2 → no divisor
- i=6: 7%6=1 → no divisor
- Bucle termina, `es_primo=1` → imprime "7 ES primo."

**Traza con n = 6**:
- i=2: 6%2=0 → divisor encontrado, `es_primo=0`, break
- Imprime "6 NO es primo."

---

## Errores tipicos en C

1. **Bucle infinito por no actualizar el contador**
   ```c
   // MAL
   int i = 1;
   while (i <= 10) {
       printf("%d\n", i);
       // olvide i++
   }
   // BIEN: anadir i++ al final del cuerpo
   ```

2. **Olvidar el punto y coma en do-while**
   ```c
   // MAL
   do { ... } while (condicion)   // falta ;
   // BIEN
   do { ... } while (condicion);
   ```

3. **Condicion de bucle con = en lugar de ==**
   ```c
   // MAL: asignacion, siempre verdadero si x != 0
   while (x = 5) { ... }
   // BIEN
   while (x == 5) { ... }
   ```

4. **Indice fuera de rango en bucles con arrays (anticipacion)**
   ```c
   int arr[5];
   for (int i = 0; i <= 5; i++) {   // i=5 accede fuera del array
       arr[i] = i;
   }
   // BIEN: condicion i < 5
   ```

5. **`break` en `switch` anidado dentro de bucle no sale del bucle**
   ```c
   for (...) {
       switch (opcion) {
           case 1: break;   // sale del switch, NO del for
       }
   }
   // Para salir del for, usar una variable bandera o goto (avanzado)
   ```

---

## Ejercicios

Los ficheros estan en `practica/03-bucles/`.

| # | Enunciado | Dificultad | Salida de ejemplo |
|---|---|---|---|
| 01 | Leer N y mostrar los numeros del 1 al N, uno por linea. | (facil) Verde | `1 2 3 ... N` (uno por linea) |
| 02 | Leer N y calcular la suma 1+2+...+N. Mostrar el resultado. | (facil) Verde | `Suma de 1 a 5 = 15` |
| 03 | Leer N y calcular N! (factorial). Usar `long long`. | (facil) Verde | `5! = 120` |
| 04 | Leer un numero y mostrar su tabla de multiplicar del 1 al 10. | (media) Amarillo | `3 x 1 = 3` ... `3 x 10 = 30` |
| 05 | Leer N y mostrar los N primeros terminos de Fibonacci. | (media) Amarillo | `0 1 1 2 3 5 8` (N=7) |
| 06 | Mostrar un triangulo de asteriscos de altura N (leida por teclado). | (dificil) Rojo | Ver ej06 |
| 07 | Menu do-while con 3 opciones: contar pares 1..N, contar impares 1..N, salir. Pedir N al elegir 1 o 2. | (dificil) Rojo | Ver ej07 |

- Enunciado detallado, esqueleto y solucion en:
  - `practica/03-bucles/ejNN_practica.c`
  - `practica/03-bucles/ejNN_modelo.c`

---

## Conexiones

- [[Curso_C/00_README]]
- [[MOC_Linux]]
- [[Curso_C/modelo/02-condicionales]] — modulo anterior: if/else/switch
- [[Curso_C/modelo/04-funciones]] — modulo siguiente: definir y llamar funciones propias
