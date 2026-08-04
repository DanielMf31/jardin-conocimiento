---
title: Bandit Nivel 1 -> 2
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, bandit, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Bandit nivel 1, Bandit guion, Bandit dashed filename]
---

# Bandit Nivel 1 -> 2

> Recurso oficial: https://overthewire.org/wargames/bandit/bandit2.html

---

## Objetivo

Leer el contenido del archivo llamado `-` (un solo guion) que está en el directorio home de `bandit1` para obtener la contraseña del nivel 2.

---

## Qué aprendes

- **Nombre de archivo especial**: cómo manejar archivos cuyo nombre colisiona con flags de comandos (`-`).
- **Convención `-` = stdin**: muchos programas Unix interpretan `-` como "leer desde la entrada estándar" en lugar de un archivo real.
- **Ruta `./`**: usar `./` como prefijo fuerza al shell a tratar el argumento como una ruta, no como una opción.
- Comandos implicados: `cat`, `ls`, `ssh`.

---

## Paso a paso

### 1. Conectarse al nivel 1

Usa la contraseña que obtuviste en el nivel 0. Abre una terminal y ejecuta:

```bash
ssh bandit1@bandit.labs.overthewire.org -p 2220
```

Introduce la contraseña del nivel 1 cuando se te pida. Verás el banner de OverTheWire y el prompt cambiará a:

```
bandit1@bandit:~$
```

---

### 2. Comprobar qué hay en el home

```bash
ls
```

Salida esperada:

```
-
```

Hay un único archivo y su nombre es literalmente un guion. Curioso, ¿verdad?

---

### 3. El intento ingenuo (y por qué falla)

Si intentas leer el archivo con `cat -` tal cual:

```bash
cat -
```

El terminal se queda... esperando. No vuelve el prompt. Eso es porque `cat` ha interpretado `-` como "lee de la entrada estándar" (el teclado). No ha abierto ningún archivo.

Para salir de ese estado sin hacer nada, pulsa `Ctrl+C` o `Ctrl+D`:

```
^C
bandit1@bandit:~$
```

---

### 4. La solución: referenciar el archivo por su ruta

Añade `./` delante del nombre para indicarle al shell que es una ruta relativa al directorio actual, no una opción de comando:

```bash
cat ./-
```

También funciona con la ruta absoluta:

```bash
cat /home/bandit1/-
```

Salida esperada (la contraseña del nivel 2):

```
<cadena_de_~32_caracteres>
```

Esa cadena es la contraseña del siguiente nivel. Copiala.

---

## Por qué funciona

### La convención Unix de `-`

En los programas de la línea de comandos Unix, el argumento `-` tiene un significado especial por convención: indica "usa la entrada estándar (stdin) en lugar de un archivo". Esto no lo impone el shell, lo implementa cada programa individualmente. `cat`, `grep`, `sort`, `tar` y muchos otros lo respetan.

Cuando escribes `cat -`, `cat` ve un guion y piensa: "el usuario quiere que lea del teclado". El programa se bloquea esperando que teclees algo.

### Por qué `./` rompe la ambigüedad

Cuando escribes `cat ./-`, el argumento ya no es `-` a secas: es la cadena `"./-"`. Esto ya no coincide con la convención de stdin. El programa lo trata como una ruta de archivo normal, que el sistema operativo resuelve como "el archivo llamado `-` en el directorio actual".

El sistema de archivos no tiene ningún problema con guiones en nombres de archivo; la limitación es solo interpretativa, en los programas que usan esa convención.

---

## Errores comunes

| Error | Causa | Solución |
|---|---|---|
| `cat -` se queda colgado sin hacer nada | `cat` interpreta `-` como stdin | Pulsa `Ctrl+C` y usa `cat ./-` |
| `cat: -: No such file or directory` | Escribiste una ruta incorrecta | Comprueba con `ls` que estás en el home correcto |
| `Permission denied` | Intentas acceder con el usuario equivocado | Verifica que conectaste como `bandit1`, no `bandit0` |
| La contraseña parece no funcionar en el siguiente nivel | Copiaste espacios o el salto de línea | Copia solo los caracteres visibles, sin espacios al final |

---

## Pasar al siguiente nivel

Con la contraseña obtenida (`<cadena_de_~32_caracteres>`), abre una nueva sesión para el nivel 2:

```bash
ssh bandit2@bandit.labs.overthewire.org -p 2220
```

Introduce la cadena que copiaste cuando se te pida la contraseña.

---

## Conexiones

- [[Bandit/00_README]]
- [[MOC_Ciberseguridad]]
