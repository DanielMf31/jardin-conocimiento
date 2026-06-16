---
title: Bandit Nivel 4 -> 5
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, bandit, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Bandit 4, Bandit nivel 4 5, bandit file command]
---

# Bandit Nivel 4 -> 5

> Recurso oficial: https://overthewire.org/wargames/bandit/bandit5.html

## Objetivo

Identificar cuál de los 10 archivos dentro del directorio `inhere/` contiene texto legible por humanos (ASCII) y leer su contenido para obtener la contraseña del nivel 5.

---

## Qué aprendes

- **`file`** — identifica el tipo de contenido de un archivo analizando sus bytes internos, no por su extensión.
- **`./`** delante de nombres de archivo que empiezan por `-` — evita que el shell interprete el nombre como una opción de comando.
- **`*` (glob/wildcard)** — expande todos los archivos de un directorio de una sola vez.
- Por qué los archivos binarios generan caracteres ilegibles si los lees con `cat`.

---

## Paso a paso

### 1. Conectarte al nivel 4

Usa la contraseña que obtuviste en el nivel anterior:

```bash
ssh bandit4@bandit.labs.overthewire.org -p 2220
```

Escribe (o pega) la contraseña cuando la pida y pulsa Enter. Verás el banner de bienvenida de OverTheWire.

---

### 2. Ver qué hay en el directorio home

```bash
ls
```

Salida esperada:

```
inhere
```

Hay una sola carpeta llamada `inhere`.

---

### 3. Entrar a `inhere` y listar los archivos

```bash
cd inhere
ls
```

Salida esperada:

```
-file00  -file01  -file02  -file03  -file04
-file05  -file06  -file07  -file08  -file09
```

Diez archivos, todos con nombres que empiezan por `-`. Ninguno tiene extensión que nos dé una pista.

---

### 4. Identificar el archivo de texto con `file`

```bash
file ./-file*
```

> Por que `./-file*` y no `-file*` o `file*`: se explica en detalle en la sección "Por qué funciona". Por ahora, acepta que `./-file*` es la forma segura.

Salida esperada (los tipos binarios varían, pero habrá exactamente uno con `ASCII text`):

```
./-file00: data
./-file01: data
./-file02: data
./-file03: data
./-file04: data
./-file05: data
./-file06: data
./-file07: ASCII text
./-file08: data
./-file09: data
```

El archivo que pone `ASCII text` es el que contiene la contraseña. En este ejemplo es `-file07`, pero puede ser cualquiera en tu sesión.

---

### 5. Leer el archivo con `cat`

Sustituye `07` por el número que aparezca en tu salida:

```bash
cat ./-file07
```

Salida esperada:

```
<cadena_de_~32_caracteres>
```

Esa cadena (una secuencia de letras y dígitos de unos 32 caracteres) **es la contraseña para el nivel 5**. Cópiala ahora.

---

### 6. Salir de la sesión

```bash
exit
```

---

## Por qué funciona

### El comando `file` mira dentro del archivo, no la extensión

En Linux, la extensión de un fichero (`.txt`, `.jpg`…) es puramente decorativa. El sistema no la usa para nada funcional. El comando `file` analiza los primeros bytes del contenido real (la "firma" o *magic bytes*) y determina de qué tipo es:

- Un archivo que empieza por bytes con valores entre 32 y 126 (el rango imprimible de ASCII) se clasifica como `ASCII text`.
- Un archivo con bytes fuera de ese rango se clasifica como `data`, `ELF`, `JPEG image`, etc.

Esto es exactamente lo que necesitamos aquí: ignorar el nombre y preguntar "¿qué hay dentro?".

### Por qué `./-file07` y no `-file07`

Cuando escribes un comando como:

```bash
file -file07
```

El shell ve que el argumento empieza por `-` y lo trata como una **opción** del comando `file`, no como un nombre de fichero. `file` entonces responde con un error porque `-f` o `-i` son opciones reales de `file`, pero `-file07` no existe como opción válida.

La solución es anteponer `./`, que significa "en el directorio actual". Así el shell entiende que es una ruta relativa a un archivo, no una opción:

```bash
file ./-file07   # correcto: "el archivo llamado -file07 que está aquí"
```

La misma regla aplica a `cat`, `rm`, y cualquier otro comando de terminal.

### Por qué `file ./-file*` funciona en bloque

El asterisco `*` es un **glob** (comodín) que el shell expande antes de pasar los argumentos al comando. Cuando escribes `./-file*`, el shell lo convierte en la lista completa de archivos que coinciden: `./-file00 ./-file01 … ./-file09`. El comando `file` recibe todos a la vez y muestra el tipo de cada uno. Es mucho más rápido que ejecutar `file` diez veces.

---

## Errores comunes

| Error | Causa | Solución |
|---|---|---|
| `file: invalid option -- 'f'` (o similar) | Usaste `file -file*` sin el `./` | Añade `./` delante: `file ./-file*` |
| `file *` no muestra los archivos con `-` | El glob `*` expande los nombres, que empiezan por `-`, y `file` los confunde con opciones | Usa `./*` o `./-file*` en su lugar |
| `cat ./-file07` muestra caracteres extraños | Has elegido un archivo de tipo `data`, no el `ASCII text` | Vuelve a la salida de `file` y busca el que diga exactamente `ASCII text` |
| La contraseña tiene espacios o saltos de línea extra al copiar | Al copiar desde la terminal se arrastran espacios | Copia solo los 32 caracteres visibles, sin espacios al inicio o al final |

---

## Pasar al siguiente nivel

Con la contraseña que acabas de obtener (`<cadena_de_~32_caracteres>`), conéctate al nivel 5:

```bash
ssh bandit5@bandit.labs.overthewire.org -p 2220
```

Introduce la contraseña cuando la pida. Estarás dentro de la sesión de `bandit5`.

---

## Conexiones

- [[Bandit/00_README]]
- [[MOC_Ciberseguridad]]
