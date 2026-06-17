---
title: "Modulo 05: Arrays y cadenas en C"
date: 2026-06-16
tags: [programacion/c, curso, programacion/arrays, programacion/cadenas]
type: nota
status: en-progreso
source: claude-code
aliases: [arrays en C, cadenas en C, char array, string.h C]
---

# Modulo 05: Arrays y cadenas en C

## Idea central

Sin arrays no puedes almacenar mas de un dato del mismo tipo sin inventar una variable por cada elemento. Un array es un bloque contiguo de memoria donde guardas N valores del mismo tipo y accedes a cada uno por indice. Las cadenas en C son simplemente arrays de `char` con un centinela `'\0'` al final; entender eso elimina el 90 % de los bugs de cadenas.

---

## Que aprendes

| Concepto | Para que sirve |
|---|---|
| Declarar e inicializar un array | Guardar una coleccion de valores del mismo tipo |
| Recorrer con `for` | Leer o modificar cada elemento en orden |
| Calcular suma, media, max, min | Operaciones estadisticas basicas sobre datos |
| Invertir un array in-place | Patron swap con dos indices |
| Busqueda lineal | Encontrar si un valor existe en la coleccion |
| `char[]` terminado en `'\0'` | Representar texto en C sin biblioteca externa |
| `strlen`, `strcpy` de `string.h` | Medir y copiar cadenas de forma segura |
| Leer cadenas con `fgets` | Evitar desbordamiento al leer texto del usuario |
| Longitud sin `strlen` | Entender el recorrido hasta `'\0'` manualmente |

---

## Explicacion

### Categoria 1: Arrays de enteros

**Patron**: declarar → inicializar → recorrer con indice.

```c
// Patron basico
int a[5];                  // declara 5 enteros (indices 0..4)
int b[3] = {10, 20, 30};  // inicializa directamente
int n = 5;

// Recorrido lectura
for (int i = 0; i < n; i++) {
    printf("%d ", b[i]);
}

// Recorrido escritura
for (int i = 0; i < n; i++) {
    scanf("%d", &a[i]);    // & porque scanf necesita la direccion
}
```

**Regla de oro**: el indice valido va de `0` a `n-1`. Acceder a `a[n]` es comportamiento indefinido (no compila con error, simplemente crashea o da basura).

---

### Categoria 2: Cadenas (`char[]` + `'\0'`)

**Patron**: una cadena es un array de `char` cuyo ultimo elemento util es `'\0'` (byte cero, valor ASCII 0).

```c
char saludo[20] = "Hola";   // {'H','o','l','a','\0', ... }
char nombre[50];

// Leer cadena (USAR fgets, NO gets)
fgets(nombre, sizeof(nombre), stdin);
// fgets incluye el '\n' al final; si lo quieres quitar:
// nombre[strcspn(nombre, "\n")] = '\0';

printf("Hola, %s\n", nombre);
```

**`string.h` basico**:

```c
#include <string.h>

strlen(s)           // numero de chars antes del '\0'
strcpy(dst, src)    // copia src en dst (dst debe ser suficientemente grande)
```

---

### Categoria 3: Trabajar con cadenas sin `strlen`

Recorrer hasta `'\0'` manualmente es la forma de entender como funciona internamente:

```c
int longitud = 0;
while (s[longitud] != '\0') {
    longitud++;
}
```

---

## Worked example

**Problema**: Dado un array de N enteros leidos por teclado, mostrar el maximo, el minimo y la media.

### Paso 1 — definir el array y leer datos

```c
#include <stdio.h>

int main(void) {
    int n;
    printf("Cuantos numeros? ");
    scanf("%d", &n);

    int a[100];                       // limite maximo razonable
    for (int i = 0; i < n; i++) {
        printf("a[%d] = ", i);
        scanf("%d", &a[i]);
    }
```

### Paso 2 — inicializar max y min con el primer elemento

```c
    int max = a[0];
    int min = a[0];
    long suma = 0;
```

Inicializar con `a[0]` es correcto porque ya sabemos que existe al menos un elemento. Inicializar `max` con `0` o `-1` podria dar resultados erroneos si todos los valores son negativos.

### Paso 3 — recorrer y actualizar

```c
    for (int i = 0; i < n; i++) {
        suma += a[i];
        if (a[i] > max) max = a[i];
        if (a[i] < min) min = a[i];
    }
```

### Paso 4 — mostrar resultados

```c
    printf("Max: %d\n", max);
    printf("Min: %d\n", min);
    printf("Media: %.2f\n", (double)suma / n);

    return 0;
}
```

**Salida de ejemplo** (entrada: 4 numeros: 3 7 1 5):
```
Max: 7
Min: 1
Media: 4.00
```

---

## Errores tipicos en C

1. **Olvidar `&` en `scanf` para arrays**: `scanf("%d", a[i])` en lugar de `scanf("%d", &a[i])`. El compilador puede avisarte con `-Wall`.

2. **Indice fuera de rango**: acceder a `a[n]` cuando el array tiene indices `0..n-1`. No da error de compilacion; da comportamiento indefinido en ejecucion.

3. **Array no inicializado**: declarar `int a[10];` y leer `a[0]` sin haber escrito nada — contiene basura. Inicializa siempre o rellena antes de leer.

4. **Olvidar el `'\0'` al construir cadenas manualmente**: si rellenas un `char[]` caracter a caracter y no pones `s[len] = '\0'`, `printf` seguira leyendo memoria hasta encontrar un byte cero aleatorio.

5. **Usar `gets` en lugar de `fgets`**: `gets` no limita la longitud y es un clasico desbordamiento de buffer. Siempre `fgets(buf, sizeof(buf), stdin)`.

---

## Ejercicios

Los ficheros estan en `practica/05-arrays-cadenas/`.

| # | Enunciado | Dificultad | Salida esperada (ejemplo) |
|---|---|---|---|
| 01 | Leer N enteros (N<=20) y mostrarlos en orden inverso. Entrada: `4` / `3 7 1 5`. | verde | `5 1 7 3` |
| 02 | Calcular la suma y la media de un array de N enteros. Entrada: `5` / `2 4 6 8 10`. | verde | `Suma: 30  Media: 6.00` |
| 03 | Encontrar el maximo y el minimo de un array. Entrada: `5` / `4 -2 9 1 0`. | verde | `Max: 9  Min: -2` |
| 04 | Invertir un array IN-PLACE (sin array auxiliar) y mostrarlo. Entrada: `5` / `1 2 3 4 5`. | amarillo | `5 4 3 2 1` |
| 05 | Busqueda lineal: leer un array y un valor buscado; indicar si existe y en que posicion (primera ocurrencia). Entrada: `5` / `10 20 30 40 50` / buscar `30`. | amarillo | `Encontrado en posicion 2` |
| 06 | Contar vocales (a e i o u, mayusculas y minusculas) en una cadena leida con fgets. Entrada: `"Hola Mundo"`. | amarillo | `Vocales: 4` |
| 07 | Calcular la longitud de una cadena SIN usar strlen (recorriendo hasta `'\0'`). Entrada: `"Programar"`. | rojo | `Longitud: 9` |

- Practica: `practica/05-arrays-cadenas/ejNN_practica.c`
- Solucion: `practica/05-arrays-cadenas/ejNN_modelo.c`

---

## Conexiones

- [[Curso_C/00_README]]
- [[MOC_Linux]]
- [[Curso_C/modelo/04-funciones]] — modulo anterior: bucles for/while que usamos para recorrer arrays
- [[Curso_C/modelo/06-matrices]] — modulo siguiente: pasar arrays a funciones, punteros basicos
