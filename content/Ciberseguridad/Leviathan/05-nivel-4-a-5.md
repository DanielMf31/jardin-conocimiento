---
title: Leviathan Nivel 4 a 5
date: 2026-06-14
tags: [ciberseguridad, linux, encoding, setuid, leviathan, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Leviathan4, Leviathan nivel 4, leviathan4to5]
---

# Leviathan Nivel 4 a 5

Nivel oficial: https://overthewire.org/wargames/leviathan/leviathan5.html

Este nivel introduce la **codificacion como ofuscacion**: la contrasena no esta cifrada, sino representada en binario puro. El reto no es romper un cifrado sino reconocer la representacion y convertirla a texto legible. Ejercicio legal y autorizado en el entorno de laboratorio de OverTheWire.

## Objetivo

Encontrar el binario setuid oculto en `.trash/`, ejecutarlo, interpretar su salida en binario y extraer la contrasena de `leviathan5`.

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| Directorios ocultos (`ls -la`) | Revelar entradas que empiezan por `.` y que `ls` omite por defecto |
| Binario setuid | Ejecutable que corre con los privilegios del propietario (aqui, `leviathan5`) para leer archivos restringidos |
| Codificacion binario → ASCII | Convertir grupos de 8 bits (`01000001` = `A`) al caracter que representan |
| `perl -lape '$_=pack("(B8)*",@F)'` | One-liner que convierte tokens de 8 bits a bytes ASCII en un pipeline |
| `python3 -c` inline | Alternativa portable para la misma conversion |

### Concepto clave

**Codificacion ≠ cifrado.** La codificacion (binario, base64, hex) transforma la representacion de los datos sin clave secreta: cualquiera que conozca el esquema puede revertirla. Aqui el binario `bin` simplemente imprime cada byte de la contrasena como 8 digitos `0`/`1` separados por espacios. La "proteccion" es solo oscuridad: si sabes leer binario, la contrasena es trivial de extraer.

El bit setuid (`-rwsr-x---`) es el mecanismo que permite al binario leer `/etc/leviathan_pass/leviathan5` aunque tu sesion sea `leviathan4`. Sin el setuid, la ejecucion fallaria con "Permission denied".

## Paso a paso

**1. Conectarse como leviathan4**

```bash
ssh leviathan4@leviathan.labs.overthewire.org -p 2223
# contrasena: <pass_leviathan4>
```

**2. Descubrir el directorio oculto**

```bash
ls -la ~
```

Veras una entrada `.trash/`. Los directorios ocultos (nombre con `.` inicial) no aparecen con `ls` sin la flag `-a`.

**3. Inspeccionar el binario**

```bash
ls -la ~/.trash/
```

Salida relevante:

```
-rwsr-x--- 1 leviathan5 leviathan4  ... bin
```

El bit `s` en el campo de permisos del propietario indica **setuid**: al ejecutarse, el proceso adopta la identidad de `leviathan5`.

**4. Ejecutar el binario y observar la salida**

```bash
~/.trash/bin
```

La salida sera algo similar a:

```
01001000 01100101 01101100 01101100 ...
```

Cada grupo de 8 digitos es la representacion binaria de un byte ASCII.

**5. Convertir binario a ASCII — opcion Perl (recomendada)**

```bash
~/.trash/bin | perl -lape '$_=pack("(B8)*",@F)'
```

- `pack("(B8)*", @F)` toma cada token de 8 bits del array `@F` (campos del input) y los empaqueta como bytes.
- `-l` anade newline automatico; `-p` imprime `$_` tras cada linea; `-a` hace el split en `@F`.

**5b. Convertir binario a ASCII — opcion Python**

```bash
~/.trash/bin | python3 -c "
import sys
bits = sys.stdin.read().split()
print(''.join(chr(int(b, 2)) for b in bits))
"
```

Ambas opciones producen la contrasena en texto claro: `<pass_leviathan5>`.

## Por que funciona

El binario tiene privilegios de `leviathan5` por el bit setuid, por lo que puede abrir `/etc/leviathan_pass/leviathan5`. En lugar de imprimir el texto directamente, lo convierte a representacion binaria bit a bit — una capa de oscuridad, no de seguridad. La conversion inversa es determinista y sin clave: cualquier herramienta que entienda binario-a-ASCII la revierte en un pipeline de una sola linea.

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| `ls ~` no muestra `.trash/` | Se uso `ls` sin `-a` | Usar siempre `ls -la` o `ls -a` para ver ocultos |
| `Permission denied` al ejecutar `bin` | Se intenta ejecutar como usuario incorrecto o se copio el binario a otra ruta (pierde el setuid) | Ejecutar **desde la ruta original** `~/.trash/bin`; no copies el binario |
| La salida de Perl parece corrupta | Espacios extra o saltos de linea inesperados en la salida del binario | Verificar con `~/.trash/bin | xxd` si la salida incluye caracteres no esperados; ajustar el split en el script Python |
| Se confunde codificacion con cifrado | Conceptual | Recordar: codificacion es reversible sin clave; cifrado requiere clave secreta |

## Pasar al siguiente nivel

Con la contrasena obtenida, conectarse a `leviathan5`:

```bash
ssh leviathan5@leviathan.labs.overthewire.org -p 2223
# contrasena: <pass_leviathan5>
```

## Conexiones

- [[Leviathan/00_README]]
- [[MOC_Ciberseguridad]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[13-herramientas-en-detalle]]
