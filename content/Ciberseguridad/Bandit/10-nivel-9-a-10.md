---
title: Bandit Nivel 9 a 10
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, bandit, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Bandit 9-10, bandit nivel 9, strings grep binario]
---

# Bandit Nivel 9 → 10

Nivel del wargame **Bandit** de [OverTheWire](https://overthewire.org/wargames/bandit/), un juego legal y educativo diseñado para aprender terminal Linux y conceptos de ciberseguridad desde cero.

---

## Objetivo

La contraseña del siguiente nivel (bandit10) está almacenada en el archivo `data.txt`. El problema: el archivo es **mayormente binario** (datos ilegibles), y la contraseña se esconde entre las pocas cadenas de texto legible, precedida por varios caracteres `=`.

Página oficial del nivel: https://overthewire.org/wargames/bandit/bandit10.html

---

## Qué aprendes

| Herramienta / Concepto | Para qué sirve |
|---|---|
| `strings` | Extrae todas las cadenas de texto imprimible de un archivo, ignorando los bytes binarios |
| `grep` | Filtra líneas que contienen un patrón de texto |
| Pipe `|` | Encadena la salida de un comando como entrada del siguiente |
| Archivos binarios | Archivos cuyo contenido no es texto legible (imágenes, ejecutables, datos comprimidos…) |

### Conceptos clave

**Archivo binario vs. archivo de texto**: un archivo de texto contiene solo caracteres imprimibles (letras, números, símbolos). Un archivo binario contiene bytes arbitrarios — muchos de ellos no corresponden a ningún carácter visible. Si intentas abrir un binario con `cat`, verás caracteres extraños y basura.

**`strings`**: herramienta estándar de Unix/Linux. Recorre el archivo byte a byte y extrae secuencias de caracteres imprimibles de longitud mínima (por defecto 4 caracteres). Muy usada en análisis de malware y CTFs para localizar texto oculto en binarios.

**`grep`**: filtra líneas. `grep ==` devuelve solo las líneas que contienen al menos dos signos `=` consecutivos, que es la pista que da el enunciado.

---

## Paso a paso

### 1. Conectarse como bandit9

```bash
ssh bandit9@bandit.labs.overthewire.org -p 2220
```

Introduce la contraseña que obtuviste en el nivel anterior cuando te la pida.

### 2. Confirmar que el archivo existe y es binario

```bash
ls -lh data.txt
```

Verás algo como:

```
-rw-r----- 1 bandit10 bandit9 19K Jun  4 15:58 data.txt
```

Intenta leerlo directamente para comprobar que es ilegible:

```bash
cat data.txt
```

Verás una mezcla caótica de caracteres extraños, símbolos y basura binaria. Eso confirma que no es un archivo de texto plano.

### 3. Extraer cadenas legibles con `strings`

```bash
strings data.txt
```

Obtendrás una lista de todas las cadenas de texto imprimible que hay dentro del archivo. Habrá bastantes, mezcladas con fragmentos sin sentido. Ejemplo de salida (truncada):

```
========== the
Z[Z[
========== passwordis
r3b7Kh
========== <cadena_de_~32_caracteres>
...
```

### 4. Filtrar por el patrón `==`

El enunciado dice que la contraseña va precedida por varios `=`. Filtramos con `grep`:

```bash
strings data.txt | grep ==
```

Salida esperada:

```
========== the
========== passwordis
========== <cadena_de_~32_caracteres>
```

La línea que empieza por `==========` y muestra una cadena larga de caracteres aleatorios es la contraseña de bandit10.

> `<cadena_de_~32_caracteres>` es un placeholder. La cadena real que verás tú es la contraseña — cópiala tal cual.

---

## Por qué funciona

`data.txt` fue generado intencionadamente como un binario con texto embebido para forzar el uso de `strings`. La herramienta `cat` o `less` muestran basura porque no filtran bytes no imprimibles. `strings` sí lo hace: busca secuencias de N caracteres imprimibles consecutivos (por defecto N=4) y los muestra línea a línea.

Al pasar la salida de `strings` por `grep ==`, aprovechamos la pista del enunciado (varios `=` antes de la password) para reducir decenas de líneas a las 3 relevantes. El pipe `|` es lo que encadena ambos comandos: la salida de `strings` se convierte automáticamente en la entrada de `grep`, sin crear archivos intermedios.

Flujo resumido:

```
data.txt → [strings] → todas las cadenas legibles → [grep ==] → líneas con "=="
```

---

## Errores comunes

**Usar `cat` o `less` directamente**: no sirve para este archivo porque muestra el contenido binario sin filtrar. No es un fallo tuyo — es el diseño del nivel.

**`grep =` con un solo `=`**: puede devolver demasiados resultados o resultados incorrectos. El enunciado especifica *varios* `=`, así que `grep ==` (dos o más `=` consecutivos) es más preciso.

**Copiar la línea entera en lugar de solo la cadena**: la contraseña es solo la parte alfanumérica, no los `==========` que la preceden. Copia únicamente la cadena de caracteres que aparece después de los signos `=`.

**Mayúsculas/minúsculas en la cadena**: la contraseña es sensible a mayúsculas. Cópiala exactamente como aparece.

---

## Pasar al siguiente nivel

Una vez tengas la cadena de ~32 caracteres, sal de la sesión actual:

```bash
exit
```

Conéctate como bandit10:

```bash
ssh bandit10@bandit.labs.overthewire.org -p 2220
```

Introduce como contraseña la cadena que obtuviste con `strings data.txt | grep ==`.

---

## Conexiones

- [[Bandit/00_README]] — índice general del wargame y cómo empezar
- [[MOC_Ciberseguridad]] — mapa de contenidos de ciberseguridad en la bóveda
