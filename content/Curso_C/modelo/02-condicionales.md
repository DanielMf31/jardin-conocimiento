---
title: "Modulo 02: Condicionales en C"
date: 2026-06-16
tags: [programacion/c, programacion/curso-c, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [condicionales-c, if-else-c, switch-c, ternario-c]
---

# Modulo 02: Condicionales en C

## Idea central

Un programa sin condicionales ejecuta siempre las mismas instrucciones. Los condicionales permiten que el programa **tome decisiones**: ejecutar un bloque de codigo u otro dependiendo de si una condicion es verdadera o falsa. En C, `0` es falso y cualquier valor distinto de `0` es verdadero.

---

## Que aprendes

| Concepto | Para que sirve |
|---|---|
| `if / else if / else` | Elegir entre dos o mas ramas de ejecucion segun una condicion |
| `switch / case` | Elegir entre muchos casos discretos de forma limpia (sin anidamientos) |
| Operadores relacionales `== != < > <= >=` | Comparar dos valores; producen `1` (verdadero) o `0` (falso) |
| Operadores logicos `&& \|\| !` | Combinar o negar condiciones |
| Operador ternario `?:` | Forma compacta de un `if-else` de una sola expresion |

---

## Explicacion

### Patron 1 — `if / else if / else`

**Categoria**: decision secuencial; se evaluan las condiciones de arriba hacia abajo y solo se ejecuta el primer bloque cuya condicion sea verdadera.

**Sintaxis**:
```c
if (condicion1) {
    // bloque A
} else if (condicion2) {
    // bloque B
} else {
    // bloque por defecto
}
```

**Ejemplo corto**:
```c
int x = 7;
if (x > 0) {
    printf("positivo\n");
} else if (x < 0) {
    printf("negativo\n");
} else {
    printf("cero\n");
}
// Imprime: positivo
```

Regla practica: el `else` es opcional, pero si lo omites y ninguna condicion se cumple, no se ejecuta nada. Eso puede ser lo que quieres o puede ser un bug silencioso; piensalo antes.

---

### Patron 2 — `switch / case`

**Categoria**: seleccion por valor entero (o caracter); mas legible que una cadena de `if-else` cuando los casos son discretos y conocidos.

**Sintaxis**:
```c
switch (expresion_entera) {
    case VALOR_A:
        // codigo
        break;
    case VALOR_B:
        // codigo
        break;
    default:
        // si ningun case coincide
        break;
}
```

**Importante**: sin `break`, la ejecucion "cae" al siguiente `case` (*fall-through*). A veces es intencional; casi siempre es un error.

**Ejemplo corto**:
```c
char op = '+';
switch (op) {
    case '+': printf("suma\n");   break;
    case '-': printf("resta\n");  break;
    default:  printf("otro\n");   break;
}
// Imprime: suma
```

---

### Patron 3 — Operadores relacionales y logicos

| Operador | Significado | Ejemplo (`a=3, b=5`) | Resultado |
|---|---|---|---|
| `==` | igual | `a == 3` | `1` (verdad) |
| `!=` | distinto | `a != b` | `1` |
| `<` | menor que | `a < b` | `1` |
| `>` | mayor que | `a > b` | `0` |
| `<=` | menor o igual | `b <= 5` | `1` |
| `>=` | mayor o igual | `a >= 4` | `0` |
| `&&` | AND logico | `a > 0 && b > 0` | `1` |
| `\|\|` | OR logico | `a > 4 \|\| b > 4` | `1` |
| `!` | NOT logico | `!(a == 3)` | `0` |

**Cortocircuito**: en `A && B`, si `A` es falso, `B` nunca se evalua. En `A || B`, si `A` es verdadero, `B` nunca se evalua. Util para evitar divisiones por cero o accesos invalidos.

---

### Patron 4 — Operador ternario `?:`

**Categoria**: expresion (no sentencia), produce un valor; util para asignaciones condicionales en una linea.

**Sintaxis**:
```c
variable = (condicion) ? valor_si_verdad : valor_si_falso;
```

**Ejemplo corto**:
```c
int n = 8;
char *paridad = (n % 2 == 0) ? "par" : "impar";
printf("%s\n", paridad);   // par
```

Cuando la logica es mas compleja que una asignacion simple, usa `if-else` para mayor claridad.

---

## Worked example

**Enunciado**: Dado un entero leido por teclado, indica si es par o impar, si es positivo/negativo/cero, y si es divisible por 3.

**Razonamiento paso a paso**:

1. Leer el entero con `scanf`.
2. Paridad: `n % 2 == 0` es par.
3. Signo: tres casos excluyentes -> `if / else if / else`.
4. Divisibilidad por 3: `n % 3 == 0`.

```c
#include <stdio.h>

int main(void) {
    int n;
    printf("Introduce un entero: ");
    scanf("%d", &n);                        // &n: scanf necesita la DIRECCION

    // --- Paridad ---
    if (n % 2 == 0) {
        printf("%d es par\n", n);
    } else {
        printf("%d es impar\n", n);
    }

    // --- Signo ---
    if (n > 0) {
        printf("Es positivo\n");
    } else if (n < 0) {
        printf("Es negativo\n");
    } else {
        printf("Es cero\n");
    }

    // --- Divisibilidad ---
    if (n % 3 == 0) {
        printf("Es divisible por 3\n");
    } else {
        printf("No es divisible por 3\n");
    }

    return 0;
}
```

**Traza con n = -6**:
- `-6 % 2 == 0` -> par
- `-6 < 0` -> negativo
- `-6 % 3 == 0` -> divisible por 3

Salida esperada:
```
-6 es par
Es negativo
Es divisible por 3
```

---

## Errores tipicos en C

1. **`=` en lugar de `==` en la condicion**
   ```c
   if (x = 5) { ... }   // ASIGNA 5 a x, siempre verdadero
   if (x == 5) { ... }  // CORRECTO: compara
   ```
   Truco: escribe `5 == x` (yoda condition); si pones `=` el compilador da error.

2. **Olvidar `break` en `switch`**
   Sin `break`, el flujo cae al siguiente `case`. El compilador no avisa por defecto; `-Wall` ayuda poco aqui. Pon siempre `break` salvo que el *fall-through* sea deliberado y lo documentes.

3. **`scanf` sin `&`**
   ```c
   scanf("%d", n);    // undefined behavior: pasa el VALOR, no la direccion
   scanf("%d", &n);   // correcto: pasa la DIRECCION de n
   ```

4. **Comparar floats con `==`**
   Los numeros de punto flotante tienen error de representacion. Nunca hagas `if (f == 0.0)`; usa `if (fabs(f) < 1e-9)` (requiere `math.h`). En este modulo trabajamos con enteros, pero conviene saberlo.

5. **`else` colgante** (*dangling else*)
   ```c
   if (a > 0)
       if (b > 0)
           printf("ambos positivos\n");
   else               // pertenece al segundo if, NO al primero
       printf("a negativo\n");
   ```
   Usa siempre llaves `{}` para evitar ambiguedad, aunque el cuerpo sea una sola linea.

---

## Ejercicios

Practica lo de este módulo. Cada enlace abre el ejercicio con su enunciado, diagrama de flujo, explicación y el código listo para copiar.

- [[Curso_C/practica/02-condicionales/ej01|Ej 01 — Lee un entero e indica si es par o impar (verde)]]
- [[Curso_C/practica/02-condicionales/ej02|Ej 02 — Lee dos enteros e imprime el mayor (verde)]]
- [[Curso_C/practica/02-condicionales/ej03|Ej 03 — Lee un entero e indica si es positivo, negativo o cero (verde)]]
- [[Curso_C/practica/02-condicionales/ej04|Ej 04 — Lee una nota entera (0-10) e imprime la letra (amarillo)]]
- [[Curso_C/practica/02-condicionales/ej05|Ej 05 — Lee dos numeros reales y un operador (amarillo)]]
- [[Curso_C/practica/02-condicionales/ej06|Ej 06 — Lee un ano e indica si es bisiesto (amarillo)]]
- [[Curso_C/practica/02-condicionales/ej07|Ej 07 — Lee un entero y clasificalo en rangos (rojo)]]

---

## Conexiones

- [[Curso_C/00_README]]
- Linux
- [[Curso_C/modelo/01-variables]] — modulo anterior: variables, tipos y E/S basica
- [[Curso_C/modelo/03-bucles]] — modulo siguiente: `while`, `for`, `do-while`
