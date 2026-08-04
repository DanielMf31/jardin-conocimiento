---
title: Bandit Nivel 5 a 6
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, bandit, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Bandit 5→6, bandit nivel 6, find bytes linux]
---

# Bandit Nivel 5 a 6

Wargame legal y educativo disponible en https://overthewire.org/wargames/bandit/

---

## Objetivo

Encontrar la contraseña del nivel 6 dentro del directorio `inhere/`, que contiene múltiples subcarpetas con múltiples archivos. El archivo correcto tiene **tres propiedades simultáneas**:

- Es legible por humanos (readable)
- Tiene exactamente **1033 bytes** de tamaño
- **No** es ejecutable

---

## Qué aprendes

### Comandos principales

| Comando | Para qué sirve |
|---|---|
| `find` | Buscar archivos por nombre, tamaño, permisos, tipo... |
| `cat` | Leer el contenido de un archivo |

### Flags de `find` que se usan aquí

| Flag | Significado |
|---|---|
| `-size 1033c` | Archivos de exactamente 1033 **bytes** (la `c` = *characters* = bytes) |
| `-readable` | El archivo puede ser leído por el usuario actual |
| `! -executable` | El archivo **no** es ejecutable (`!` = negación lógica) |

### Conceptos clave

- **Bytes vs bloques**: `find -size` puede trabajar en bloques (512 B), kilobytes, etc. El sufijo `c` es el único que representa bytes exactos, imprescindible aquí.
- **Permisos de Unix**: cada archivo tiene bits de lectura (`r`), escritura (`w`) y ejecución (`x`). `-readable` filtra por el bit de lectura; `! -executable` descarta los que tienen el bit de ejecución activo.
- **Negación con `!`**: en `find`, `!` invierte el predicado que le sigue. Debe ir separado por espacio.

---

## Paso a paso

### 1. Conectarse al nivel 5

```bash
ssh bandit5@bandit.labs.overthewire.org -p 2220
```

Cuando pregunte la contraseña, pega la que obtuviste al resolver el nivel 4 (`<cadena_de_~32_caracteres>`).

Lo que verás al conectarte:

```
bandit5@bandit:~$
```

### 2. Confirmar que existe `inhere/`

```bash
ls
```

Salida esperada:

```
inhere
```

### 3. Ver qué hay dentro (opcional, para entender el problema)

```bash
ls inhere/
```

Salida esperada (verás varias subcarpetas):

```
maybehere00  maybehere02  maybehere04  maybehere06  maybehere08  maybehere10
maybehere12  maybehere14  maybehere16  maybehere18  maybehere01  maybehere03
maybehere05  maybehere07  maybehere09  maybehere11  maybehere13  maybehere15
maybehere17  maybehere19
```

Son 20 subcarpetas, cada una con varios archivos. Buscar a mano sería costoso — aquí es donde `find` brilla.

### 4. Buscar el archivo con las tres condiciones

```bash
find inhere/ -size 1033c -readable ! -executable
```

Salida esperada (una sola línea):

```
inhere/maybehere07/.file2
```

`find` ha recorrido las 20 subcarpetas y encontró exactamente un archivo que cumple los tres criterios.

### 5. Leer el archivo

```bash
cat inhere/maybehere07/.file2
```

Salida esperada:

```
<cadena_de_~32_caracteres>

```

La contraseña es la cadena que aparece en la primera línea. El resto son espacios en blanco que completan los 1033 bytes — ignóralos.

### 6. Desconectarse

```bash
exit
```

---

## Por qué funciona

`find` trabaja de forma recursiva: parte del directorio que le indicas (`inhere/`) y desciende a todas las subcarpetas automáticamente. Luego evalúa cada archivo contra los predicados que le das, aplicándolos con **AND implícito** — un archivo solo aparece en el resultado si cumple *todos* a la vez.

El flujo es:

```
inhere/ (raíz de búsqueda)
  └─ para cada archivo encontrado:
       ¿tamaño == 1033 bytes?   → si no, descarta
       ¿readable por bandit5?   → si no, descarta
       ¿ejecutable?             → si SÍ, descarta (porque usamos ! -executable)
       → si pasa los tres filtros: imprime la ruta
```

El sufijo `c` en `-size 1033c` es crítico: sin él, `find` interpreta el número en bloques de 512 bytes, y no encontraría el archivo correcto.

---

## Errores comunes

### Olvidar la `c` en `-size`

```bash
find inhere/ -size 1033   # INCORRECTO — busca archivos de 1033 bloques (≈ 515 KB)
```

Resultado: no encuentra nada, o encuentra archivos equivocados.

### Escribir `!-executable` sin espacio

```bash
find inhere/ -size 1033c -readable !-executable   # ERROR de sintaxis
```

`find` requiere que `!` esté separado del predicado por un espacio.

### Confundir `-readable` con `-perm`

`-readable` verifica si el usuario actual **puede** leer el archivo (tiene en cuenta ACLs y el usuario efectivo). `-perm /444` comprueba si el bit de lectura está activo para *alguien*. Para este nivel ambos funcionan, pero `-readable` es más semántico.

### Intentar entrar a `inhere/` con `cd` y buscar manualmente

Técnicamente posible pero ineficiente. Con 20 carpetas y varios archivos cada una, `find` resuelve el problema en milisegundos.

---

## Pasar al siguiente nivel

Con la contraseña obtenida, conéctate como `bandit6`:

```bash
ssh bandit6@bandit.labs.overthewire.org -p 2220
```

Cuando pida la contraseña, pega la cadena que obtuviste con `cat` en el paso 5 (`<cadena_de_~32_caracteres>`).

---

## Conexiones

- [[Bandit/00_README]] — índice general del wargame y cómo empezar
- [[MOC_Ciberseguridad]] — mapa de contenido de seguridad
- [[05-nivel-4-a-5]] — nivel anterior (find con -type f y archivos ocultos)
- [[07-nivel-6-a-7]] — nivel siguiente (find con -user y -group, búsqueda en todo el sistema)
