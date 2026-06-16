---
title: Bandit Nivel 3 -> 4
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, bandit, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Bandit Nivel 3, Bandit dotfiles, archivos ocultos linux]
---

# Bandit Nivel 3 -> 4

> Referencia oficial: https://overthewire.org/wargames/bandit/bandit4.html
> Marco: OverTheWire Bandit es un wargame **legal y educativo** para aprender a moverte por la terminal Linux.

---

## Objetivo

Encontrar la contraseña del nivel 4 dentro de un **archivo oculto** que se esconde en el directorio `inhere`.

---

## Qué aprendes

- Qué es un **dotfile** (archivo oculto en Linux): cualquier archivo cuyo nombre empieza por `.`
- Por qué `ls` no los muestra por defecto
- `ls -a` — lista **todos** los archivos, incluidos los ocultos (`-a` = *all*)
- `ls -la` — combina `-l` (formato largo con permisos/tamaño) y `-a`
- Cómo referenciar nombres de archivo que empiezan por puntos sin ambiguedad (`./nombre`)
- El atajo de teclado **Tab** para autocompletar nombres raros

---

## Paso a paso

### 1. Conectarte al nivel 3

Abre una terminal y ejecuta:

```bash
ssh bandit3@bandit.labs.overthewire.org -p 2220
```

Te pedirá la contraseña que obtuviste en el nivel anterior (la pegaste al salir del nivel 2). Introduce esa cadena y pulsa Enter.

---

### 2. Ver dónde estás y qué hay

```bash
ls
```

Verás algo como:

```
inhere
```

Hay un directorio llamado `inhere`. Entramos:

```bash
cd inhere
```

---

### 3. Intentar `ls` normal — no muestra nada

```bash
ls
```

Resultado:

```
(vacío — no se imprime nada)
```

El directorio parece vacío. Pero no lo está. El archivo está **oculto**.

---

### 4. Usar `ls -a` para ver los archivos ocultos

```bash
ls -a
```

Resultado:

```
.  ..  ...Hiding-From-You
```

- `.` es el directorio actual (siempre aparece)
- `..` es el directorio padre (siempre aparece)
- `...Hiding-From-You` es el archivo oculto que buscamos

Con formato largo para ver permisos y tamaño:

```bash
ls -la
```

Resultado:

```
total 12
drwxr-xr-x 2 root    root    4096 Apr 23 18:04 .
drwxr-xr-x 3 bandit3 bandit3 4096 Apr 23 18:04 ..
-rw-r----- 1 bandit4 bandit3   33 Apr 23 18:04 ...Hiding-From-You
```

---

### 5. Leer el archivo oculto

El nombre empieza por varios puntos, lo que puede confundir al shell. La forma mas segura es usar `./` delante para indicar explicitamente "este archivo en el directorio actual":

```bash
cat ./...Hiding-From-You
```

Resultado:

```
<cadena_de_~32_caracteres>
```

Esa `<cadena_de_~32_caracteres>` es la **contraseña del nivel 4**. Copiala.

> Tambien funciona sin `./` — `cat ...Hiding-From-You` — pero la forma con `./` es mas robusta con nombres de archivo raros.

**Truco**: escribe `cat ./...` y pulsa **Tab**. El shell autocompleta el nombre completo automaticamente. Muy util cuando el nombre tiene puntos u otros caracteres especiales.

---

## Por qué funciona

En Linux, cualquier archivo o directorio cuyo nombre **empieza por punto** (`.`) es considerado **oculto** (*dotfile*). Esto no es cifrado ni proteccion real — es solo una convencion para que los archivos de configuracion del sistema (como `.bashrc`, `.ssh/`) no saturen la vista por defecto.

El comando `ls` sin opciones omite estos archivos deliberadamente para no molestar. Con `-a` (*all*) se le dice explicitamente que los muestre todos.

La flag `-l` añade una columna con permisos, propietario, tamaño y fecha — informacion util para saber si un archivo es legible por ti antes de intentar abrirlo.

```
-rw-r----- 1 bandit4 bandit3 33 ...Hiding-From-You
  ^           ^       ^
  permisos    dueño   grupo al que perteneces tú (bandit3)
```

En este caso `bandit3` pertenece al grupo `bandit3`, y el grupo tiene permiso de lectura (`r`), por eso `cat` funciona.

---

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| `ls` no muestra nada y te rindes | Olvidaste que los dotfiles son invisibles para `ls` sin flags | Usa siempre `ls -a` cuando busques algo y parezca vacio |
| `cat ...Hiding-From-You` da error de sintaxis | El shell interpreta `...` como operador o ruta relativa ambigua | Prefija con `./`: `cat ./...Hiding-From-You`, o usa Tab para autocompletar |
| Ves el archivo con `ls -a` pero no puedes leerlo | No tienes permiso de lectura (`r` ausente para tu usuario/grupo) | En este nivel no deberia ocurrir; en otros si — comprueba permisos con `ls -la` |
| Copias mal la contraseña (espacios de mas, salto de linea) | Seleccion de texto con el raton incluye caracteres extra | Selecciona solo la cadena, sin espacios ni el `$` del prompt |

---

## Pasar al siguiente nivel

Con la contraseña copiada, abre una nueva terminal (o sal con `exit`) y conéctate al nivel 4:

```bash
ssh bandit4@bandit.labs.overthewire.org -p 2220
```

Introduce `<cadena_de_~32_caracteres>` (la que acabas de obtener) cuando pida la contraseña.

---

## Conexiones

- [[Bandit/00_README]]
- [[MOC_Ciberseguridad]]
- — referencia de `ls`, `cd`, `cat` y flags comunes
- — entender la notacion `rwxr-xr-x` y el modelo usuario/grupo/otros
