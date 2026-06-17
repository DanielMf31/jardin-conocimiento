---
title: "Modulo 09 — Lectura y escritura de archivos en C"
date: 2026-06-16
tags: [programacion/c, curso, programacion/archivos, programacion/io]
type: nota
status: en-progreso
source: claude-code
aliases: ["archivos C", "fopen fclose", "ficheros C", "file IO C"]
---

# Modulo 09 — Lectura y escritura de archivos en C

## Idea central

Hasta ahora todos los datos vivian en RAM: al terminar el programa, desaparecian. Los archivos resuelven eso: permiten que un programa **persista datos** entre ejecuciones y **comparta informacion** con otros programas. La API de archivos de C es sencilla: abrir → operar → cerrar.

## Que aprendes

| Concepto | Para que sirve |
|---|---|
| `fopen(ruta, modo)` | Abrir un archivo; devuelve un puntero `FILE *` |
| Modos `"r"`, `"w"`, `"a"` | Leer / escribir (crea/trunca) / anadir al final |
| Comprobar `NULL` | Detectar error al abrir (archivo no existe, sin permisos…) |
| `fprintf(fp, ...)` | Escribir en archivo con el mismo formato que `printf` |
| `fscanf(fp, ...)` | Leer datos formateados desde archivo |
| `fgets(buf, n, fp)` | Leer una linea completa (con espacios) de forma segura |
| `fclose(fp)` | Cerrar el archivo y volcar los buffers a disco |

## Explicacion

### Patron general (siempre el mismo)

```
1. Declarar  FILE *fp;
2. Abrir     fp = fopen("ruta", "modo");
3. Comprobar if (fp == NULL) { /* error */ }
4. Operar    fprintf / fscanf / fgets / ...
5. Cerrar    fclose(fp);
```

### Modos de apertura

| Modo | Lee | Escribe | Crea si no existe | Trunca si existe |
|---|---|---|---|---|
| `"r"` | si | no | no | no |
| `"w"` | no | si | si | si |
| `"a"` | no | si (solo final) | si | no |
| `"r+"` | si | si | no | no |

### Sintaxis minima

```c
#include <stdio.h>

FILE *fp = fopen("datos.txt", "w");
if (fp == NULL) {
    printf("Error al abrir el archivo\n");
    return 1;          // salir con codigo de error
}

fprintf(fp, "Hola, archivo!\n");
fclose(fp);
```

### Leer lineas con fgets

```c
char linea[256];
FILE *fp = fopen("datos.txt", "r");
if (fp == NULL) return 1;

while (fgets(linea, sizeof(linea), fp) != NULL) {
    printf("%s", linea);   // linea ya incluye '\n'
}
fclose(fp);
```

`fgets` devuelve `NULL` al llegar al final del archivo (EOF), lo que hace el bucle `while` natural.

### Leer numeros con fscanf

```c
int n;
while (fscanf(fp, "%d", &n) == 1) {   // == 1: leyo un entero correctamente
    printf("%d\n", n);
}
```

## Worked example

**Problema**: Pedir al usuario 3 nombres, guardarlos en `nombres.txt`, volver a abrirlo y mostrarlos numerados.

```c
#include <stdio.h>
#include <string.h>

int main(void) {
    // --- PASO 1: escribir 3 nombres ---
    FILE *fw = fopen("nombres.txt", "w");
    if (fw == NULL) {
        printf("No se pudo crear el archivo\n");
        return 1;
    }

    char nombre[64];
    for (int i = 0; i < 3; i++) {
        printf("Nombre %d: ", i + 1);
        scanf("%63s", nombre);
        fprintf(fw, "%s\n", nombre);   // una linea por nombre
    }
    fclose(fw);   // SIEMPRE cerrar antes de volver a abrir

    // --- PASO 2: leer y mostrar numerados ---
    FILE *fr = fopen("nombres.txt", "r");
    if (fr == NULL) {
        printf("No se pudo leer el archivo\n");
        return 1;
    }

    printf("\n--- Contenido del archivo ---\n");
    int linea = 1;
    char buf[64];
    while (fgets(buf, sizeof(buf), fr) != NULL) {
        // fgets conserva el '\n'; quitarlo para mostrar limpio
        buf[strcspn(buf, "\n")] = '\0';
        printf("%d. %s\n", linea++, buf);
    }
    fclose(fr);
    return 0;
}
```

**Por que funciona paso a paso**:
1. Abrimos con `"w"` → crea/trunca `nombres.txt`.
2. `fprintf(fw, "%s\n", nombre)` escribe cada nombre seguido de salto de linea.
3. `fclose(fw)` vuelca los buffers; sin esto el archivo puede quedar vacio.
4. Abrimos con `"r"` → el archivo ya tiene datos.
5. `fgets` lee hasta `\n` o `sizeof(buf)-1` caracteres; al llegar a EOF devuelve `NULL` y el `while` termina.
6. `strcspn(buf, "\n")` devuelve el indice del primer `\n`; ponerlo a `'\0'` lo elimina.

**Salida ejemplo**:
```
Nombre 1: Ana
Nombre 2: Bruno
Nombre 3: Carla

--- Contenido del archivo ---
1. Ana
2. Bruno
3. Carla
```

## Errores tipicos en C

| # | Error | Por que falla |
|---|---|---|
| 1 | No comprobar `fopen == NULL` | El programa peta con segfault si el archivo no existe |
| 2 | Olvidar `fclose` | Los datos pueden no llegar a disco (el buffer se descarta) |
| 3 | Usar `"w"` cuando quieres anadir | Modo `"w"` trunca: pierdes todo el contenido previo |
| 4 | `fscanf` sin `&` en variables escalares | Lee a direccion invalida → comportamiento indefinido |
| 5 | `fgets` con buffer demasiado pequeno | Trunca la linea; el `\n` queda en el stream para la siguiente lectura |

## Ejercicios

Los archivos de practica estan en `practica/09-archivos/`. Cada ejercicio tiene un esqueleto (`ejNN_practica.c`) que debes completar y una solucion (`ejNN_modelo.c`) para comparar despues.

| # | Enunciado | Dificultad | Salida esperada (ejemplo) |
|---|---|---|---|
| 01 | Escribe un programa que pida 5 frases al usuario y las guarde en `frases.txt`, una por linea. Luego abrelo y muestralas numeradas. | (facil) Facil | `1. Hola mundo` / `2. C es util` … |
| 02 | Lee el archivo `frases.txt` (creado antes) y cuenta cuantas lineas tiene. Imprime el total. | (facil) Facil | `El archivo tiene 5 lineas.` |
| 03 | Lee un archivo `numeros.txt` con enteros (uno por linea) y muestra su suma y su media. El archivo puede tener cualquier cantidad de numeros. | (media) Medio | Entrada: `3 7 2` → `Suma: 12  Media: 4.00` |
| 04 | Copia el contenido de `origen.txt` a `copia.txt` linea a linea. Imprime cuantas lineas copiaste. | (media) Medio | `Copiadas 8 lineas.` |
| 05 | Lee un archivo de texto y cuenta el numero total de palabras (separadas por espacios/saltos). | (media) Medio | `El archivo tiene 23 palabras.` |
| 06 | Guarda un array de 5 structs `Producto {nombre[32], precio float}` en `productos.txt` (uno por linea con `fprintf`). Luego leelos con `fscanf` y muestralos. | (dificil) Dificil | `Manzana 1.20` / `Leche 0.85` … |
| 07 | Abre un archivo de texto en modo append y permite al usuario anadir lineas indefinidamente hasta que escriba `"FIN"`. Al final muestra todo el archivo. | (dificil) Dificil | (las lineas anteriores + las nuevas) |

Referencias de archivos:
- Ejercicio 01: `practica/09-archivos/ej01_practica.c` / `modelo/09-archivos/ej01_modelo.c` (este modulo usa la carpeta de practica para los .c; la teoria esta aqui)
- Ejercicio 02: `practica/09-archivos/ej02_practica.c` — `ej02_modelo.c`
- Ejercicio 03: `practica/09-archivos/ej03_practica.c` — `ej03_modelo.c`
- Ejercicio 04: `practica/09-archivos/ej04_practica.c` — `ej04_modelo.c`
- Ejercicio 05: `practica/09-archivos/ej05_practica.c` — `ej05_modelo.c`
- Ejercicio 06: `practica/09-archivos/ej06_practica.c` — `ej06_modelo.c`
- Ejercicio 07: `practica/09-archivos/ej07_practica.c` — `ej07_modelo.c`

## Conexiones

- [[Curso_C/00_README]]
- [[MOC_Linux]]
- [[Curso_C/modelo/08-structs]] — modulo anterior: structs que ahora podras persistir en disco
- *(Modulo 10 por definir)* — siguiente paso
