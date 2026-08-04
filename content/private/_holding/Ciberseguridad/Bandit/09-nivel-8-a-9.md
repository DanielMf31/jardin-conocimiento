---
title: Bandit Nivel 8 a 9
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, bandit, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Bandit 8-9, bandit nivel 8, sort uniq linux]
---

# Bandit Nivel 8 a 9

Nivel del wargame educativo [OverTheWire Bandit](https://overthewire.org/wargames/bandit/bandit9.html). El objetivo es encontrar la contraseña del nivel 9 dentro de un archivo de texto con miles de líneas.

---

## Objetivo

La contraseña está en el archivo `data.txt`. El truco: ese archivo contiene muchas líneas repetidas, y la contraseña es **la única línea que aparece exactamente una vez**. Todas las demás líneas están duplicadas o más.

---

## Qué aprendes

| Comando / Concepto | Para qué sirve |
|---|---|
| `sort` | Ordena las líneas de un archivo alfabéticamente |
| `uniq` | Filtra líneas consecutivas duplicadas |
| `uniq -u` | Muestra solo las líneas que aparecen **una sola vez** |
| Pipe `\|` | Encadena la salida de un comando como entrada del siguiente |

**Concepto clave — por qué `uniq` necesita `sort` antes:**
`uniq` solo compara líneas **consecutivas**. Si dos líneas idénticas están separadas por otras líneas diferentes, `uniq` no las detecta como duplicadas. Al aplicar `sort` primero, todas las líneas iguales quedan juntas, y entonces `uniq` puede hacer su trabajo correctamente.

---

## Paso a paso

### 1. Conectarse al nivel 8

```bash
ssh bandit8@bandit.labs.overthewire.org -p 2220
```

Cuando pregunte la contraseña, pega la que obtuviste en el nivel anterior (la del nivel 8).

### 2. Verificar que el archivo existe

```bash
ls -lh data.txt
```

Verás algo como:

```
-rw-r----- 1 bandit9 bandit8 33033 Apr 23 18:00 data.txt
```

El archivo pesa unos 33 KB — demasiado para leerlo a mano.

### 3. Curiosear cuántas líneas tiene

```bash
wc -l data.txt
```

Salida esperada:

```
1001 data.txt
```

Más de mil líneas. Buscar visualmente es inviable.

### 4. Ver cómo son las líneas (opcional, para entender el problema)

```bash
head -20 data.txt
```

Verás líneas que parecen cadenas aleatorias, muchas de ellas repetidas:

```
<contrasena>
<contrasena>
<contrasena>
<contrasena>
<contrasena>
...
```

### 5. La solución: ordenar y filtrar únicos

```bash
sort data.txt | uniq -u
```

Salida esperada (una sola línea):

```
<cadena_de_~32_caracteres>
```

Esa cadena es la contraseña del nivel 9. Cópiala.

---

## Por qué funciona

El pipeline `sort data.txt | uniq -u` hace dos cosas en secuencia:

1. **`sort data.txt`** reordena todas las líneas alfabéticamente. El resultado es que las líneas idénticas quedan **pegadas** unas junto a otras.

2. **`uniq -u`** recorre la lista ya ordenada y descarta cualquier línea que aparezca más de una vez en bloques consecutivos. Solo deja pasar las que no tienen vecinas iguales.

Si intentaras ejecutar solo `uniq -u data.txt` (sin `sort`), el resultado sería incorrecto: las líneas repetidas que no están consecutivas pasarían el filtro sin ser eliminadas.

**Analogía:** imagina ordenar un mazo de cartas por valor antes de buscar el comodín. Si las cartas están desordenadas, el comodín podría estar entre dos reyes y no lo reconocerías como único.

---

## Errores comunes

| Error | Causa | Solución |
|---|---|---|
| `uniq -u data.txt` devuelve varias líneas | Se saltó el `sort`; `uniq` no detecta duplicados no consecutivos | Usar siempre `sort \| uniq -u` |
| El resultado está vacío | Se usó `uniq` sin `-u`, que muestra una copia de cada línea sin importar cuántas veces aparece | Añadir la flag `-u` |
| `Permission denied` en `data.txt` | Se intentó leer como el usuario equivocado | Verificar que se conectó como `bandit8` |
| La contraseña copiada tiene espacios extra | Se copió mal al pegar en la terminal | Copiar solo la cadena sin espacios ni saltos de línea |

---

## Pasar al siguiente nivel

Con la contraseña obtenida, conéctate al nivel 9:

```bash
ssh bandit9@bandit.labs.overthewire.org -p 2220
```

Pega `<cadena_de_~32_caracteres>` cuando pida la contraseña.

---

## Conexiones

- [[Bandit/00_README]] — índice general del wargame y cómo empezar
- [[MOC_Ciberseguridad]] — mapa de contenidos de ciberseguridad en la bóveda
- Página oficial del nivel: https://overthewire.org/wargames/bandit/bandit9.html
