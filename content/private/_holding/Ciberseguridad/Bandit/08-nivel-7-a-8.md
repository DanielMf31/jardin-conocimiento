---
title: Bandit Nivel 7 a 8
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, bandit, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Bandit 7-8, bandit nivel 7, grep bandit]
---

# Bandit Nivel 7 a 8

Wargame educativo y legal disponible en https://overthewire.org/wargames/bandit/

## Objetivo

La contraseña del siguiente nivel (bandit8) está guardada en el archivo `data.txt`, en la línea que aparece **junto a la palabra `millionth`**. El archivo contiene decenas de miles de líneas, por lo que buscar manualmente es imposible: necesitas una herramienta para filtrar texto.

## Qué aprendes

### Comando principal

| Comando | Qué hace |
|---------|----------|
| `grep` | Busca líneas que contienen un patrón de texto dentro de uno o varios archivos |

### Conceptos clave

- **Búsqueda de patrones (pattern matching)**: encontrar líneas que coinciden con una cadena o expresión dentro de un archivo de texto.
- **Stdin vs archivo**: `grep` puede leer de un archivo directamente o recibir datos desde una tubería (`|`), lo que lo hace muy componible.
- **Salida filtrada**: en lugar de mostrar todo el archivo, `grep` devuelve únicamente las líneas que coinciden.

### Sintaxis básica de grep

```
grep <patron> <archivo>
```

- `<patron>`: la cadena que quieres buscar (sensible a mayúsculas por defecto).
- `<archivo>`: el archivo donde buscar.

## Paso a paso

### 1. Conéctate al servidor como bandit7

```bash
ssh bandit7@bandit.labs.overthewire.org -p 2220
```

Cuando te pida la contraseña, introduce la que obtuviste en el nivel anterior (bandit7).

**Lo que verás:**

```
bandit7@bandit:~$
```

### 2. Confirma que data.txt existe y observa su tamaño

```bash
ls -lh data.txt
```

**Lo que verás (aproximado):**

```
-rw-r----- 1 root bandit7 4.0M May  7 20:14 data.txt
```

El archivo pesa varios megabytes. Intentar leerlo completo con `cat` o `less` sería tedioso: hay miles de líneas.

### 3. Mira cómo es el formato del archivo (opcional, primeras líneas)

```bash
head -5 data.txt
```

**Lo que verás:**

```
vlro    yVbdbRTNGPRWXPDYBpDnwGN
algorithm       mCbhniqRRFWcNhIOlPDf
trustful        BsBZNrxeyvIPHaVBNNJMq
centrifugal     cRAZnhRFONjpUhROPDFhN
millionth       <cadena_de_~32_caracteres>
```

El formato es: `<palabra><tabulador><cadena>`. Cada línea tiene una palabra clave y, separada por un tabulador, una cadena de caracteres. Solo una línea tiene la palabra `millionth`.

### 4. Usa grep para encontrar la línea correcta

```bash
grep millionth data.txt
```

**Lo que verás:**

```
millionth       <cadena_de_~32_caracteres>
```

La cadena que aparece a la derecha de `millionth` es la **contraseña del nivel 8 (bandit8)**. Copiala.

### 5. Cierra la sesión

```bash
exit
```

## Por qué funciona

`grep` lee el archivo línea a línea y evalúa si cada línea contiene el patrón indicado. Cuando encuentra una coincidencia, la imprime en pantalla y descarta el resto. Es una operación O(n) sobre el número de líneas, pero extremadamente rápida incluso para archivos de millones de líneas gracias a que opera en modo streaming (no carga el archivo entero en RAM de una vez).

En este caso el patrón `millionth` es una cadena literal, sin caracteres especiales, por lo que `grep` hace una búsqueda simple de subcadena. Solo hay una línea que la contiene, así que la salida es única.

### Opciones útiles de grep que no necesitas aquí pero conviene conocer

| Opción | Efecto |
|--------|--------|
| `-i` | Ignora mayúsculas/minúsculas |
| `-n` | Muestra el número de línea junto al resultado |
| `-c` | Cuenta el número de líneas que coinciden |
| `-r` | Busca de forma recursiva en directorios |
| `-v` | Invierte la búsqueda: muestra las líneas que NO coinciden |

## Errores comunes

**Error 1: escribir mal la palabra clave**

```bash
grep Millionth data.txt   # mayuscula: no devuelve nada
grep mllionth data.txt    # typo: no devuelve nada
```

`grep` distingue mayusculas de minusculas por defecto. Si no obtienes resultado, revisa el patron. Usa `-i` solo si no recuerdas el case exacto.

**Error 2: olvidar el nombre del archivo**

```bash
grep millionth   # se queda esperando input de teclado (stdin)
```

Si ejecutas `grep` sin archivo, espera que le escribas texto. Pulsa `Ctrl+C` para cancelar y vuelve a escribir el comando con `data.txt`.

**Error 3: buscar desde el directorio incorrecto**

```bash
grep millionth /home/bandit7/data.txt   # ruta absoluta: funciona tambien
```

Si ya estas en el home de bandit7 (`~`), puedes usar `data.txt` directamente. Si por algun motivo cambiaste de directorio, usa la ruta absoluta.

**Error 4: copiar la palabra "millionth" junto con el tabulador**

La contraseña es solo la cadena de caracteres, no la palabra `millionth` ni el espacio/tabulador que la precede. Copia solo lo que viene después.

## Pasar al siguiente nivel

Con la contraseña obtenida (la cadena que aparecio junto a `millionth`), conéctate como bandit8:

```bash
ssh bandit8@bandit.labs.overthewire.org -p 2220
```

Introduce `<cadena_de_~32_caracteres>` cuando te pida la contraseña.

## Conexiones

- [[Bandit/00_README]] — indice del wargame y convenciones de la serie
- [[MOC_Ciberseguridad]] — mapa de contenido de ciberseguridad
- — referencia de comandos de terminal Linux
