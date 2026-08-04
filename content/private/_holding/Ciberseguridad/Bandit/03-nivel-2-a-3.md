---
title: Bandit Nivel 2 -> 3
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, bandit, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [bandit nivel 2 3, bandit espacios filename, bandit quoting]
---

# Bandit Nivel 2 -> 3

> Nivel oficial: https://overthewire.org/wargames/bandit/bandit3.html
> Marco: OverTheWire Bandit es un **wargame legal y educativo** para aprender a usar la terminal de Linux. No se aplica ninguna técnica de hacking real.

---

## Objetivo

Leer el archivo llamado `spaces in this filename` que está en el directorio home, y obtener la contraseña para el nivel 3.

---

## Qué aprendes

- Por qué el **espacio** es especial en la shell: separa argumentos
- Dos formas de proteger un nombre de archivo con espacios:
  - **Quoting** (comillas dobles o simples): `"nombre con espacios"`
  - **Escaping** (barra invertida): `nombre\ con\ espacios`
- Usar **Tab para autocompletar** y dejar que la shell resuelva el escaping por ti
- El concepto de **argumento** vs **nombre de archivo**

---

## Paso a paso

### 1. Conectarse al nivel 2

```bash
ssh bandit2@bandit.labs.overthewire.org -p 2220
```

Introduce la contraseña que obtuviste en el nivel anterior cuando te la pida. Verás el prompt:

```
bandit2@bandit:~$
```

### 2. Ver qué hay en el directorio

```bash
ls
```

Salida esperada:

```
spaces in this filename
```

Eso es un único archivo. Su nombre contiene espacios, lo cual nos va a dar problemas ahora mismo.

### 3. Intentar leerlo directamente (lo que NO funciona)

```bash
cat spaces in this filename
```

Salida:

```
cat: spaces: No such file or directory
cat: in: No such file or directory
cat: this: No such file or directory
cat: filename: No such file or directory
```

La shell ha interpretado cada palabra separada por espacio como un archivo distinto. Ha buscado cuatro archivos: `spaces`, `in`, `this` y `filename`. Ninguno existe.

### 4. Solución A — Comillas dobles (recomendada)

```bash
cat "spaces in this filename"
```

Salida:

```
<cadena_de_~32_caracteres>
```

> La cadena que ves en pantalla ES la contraseña para el nivel 3. Copiala.

### 5. Solución B — Backslash (escapar cada espacio)

```bash
cat spaces\ in\ this\ filename
```

La salida es la misma. Cada `\ ` (backslash seguido de espacio) le dice a la shell: "este espacio es parte del nombre, no un separador".

### 6. Solución C — Tab autocomplete (la mas rapida en la practica)

Escribe solo el comienzo y pulsa `Tab`:

```bash
cat sp<TAB>
```

La shell completa el nombre y escapa los espacios automáticamente. El comando que aparece en pantalla sera algo como:

```bash
cat spaces\ in\ this\ filename
```

Pulsa `Enter` y obtienes la contraseña.

---

## Por qué funciona

La shell de Linux (bash, zsh) usa el espacio como **delimitador de argumentos**. Cuando escribes:

```
cat foo bar baz
```

La shell lo descompone en: comando `cat`, argumento 1 `foo`, argumento 2 `bar`, argumento 3 `baz`. Son tres archivos distintos para `cat`.

Para que un espacio forme parte de un nombre en lugar de actuar como delimitador, tienes dos mecanismos:

| Mecanismo | Sintaxis | Cómo funciona |
|---|---|---|
| Quoting doble | `"mi archivo"` | Todo lo que esta dentro de las comillas se trata como un unico token. Las comillas no aparecen en el nombre. |
| Quoting simple | `'mi archivo'` | Igual que doble, pero ademas desactiva la expansion de variables (`$VAR`) y de comandos. |
| Escaping | `mi\ archivo` | El `\` le dice a la shell que el siguiente caracter (el espacio) es literal, no especial. |

El autocomplete con `Tab` aplica escaping automaticamente, por eso es tan util.

---

## Errores comunes

**Olvidar cerrar las comillas:**
```bash
cat "spaces in this filename
```
La shell espera que cierres la comilla y muestra un prompt secundario (`>`). Pulsa `Ctrl+C` para cancelar y vuelve a intentarlo con las comillas cerradas.

**Usar comillas dentro del nombre equivocado:**
```bash
cat 'spaces in this "filename"'
```
Esto buscaria un archivo llamado `spaces in this "filename"` (con las comillas como parte del nombre), que no existe.

**Escribir la barra al reves:**
```bash
cat spaces/ in/ this/ filename
```
La `/` es el separador de directorios, no el escape. El escape es `\` (backslash).

**Confundir backslash con forward slash:**
- `/` — separador de rutas (`/home/bandit2/`)
- `\` — caracter de escape en la shell

---

## Pasar al siguiente nivel

Una vez que tienes la contraseña (la cadena de ~32 caracteres que te devolvio el comando `cat`), conectate al nivel 3:

```bash
ssh bandit3@bandit.labs.overthewire.org -p 2220
```

Introduce `<cadena_de_~32_caracteres>` como contraseña cuando te la pida.

---

## Conexiones

- [[Bandit/00_README]]
- [[MOC_Ciberseguridad]]
