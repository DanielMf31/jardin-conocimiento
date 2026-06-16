---
title: Leviathan Nivel 1 a 2
date: 2026-06-14
tags: [ciberseguridad, linux, setuid, ltrace, leviathan, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Leviathan 1, Leviathan nivel 1, leviathan1 a 2]
---

# Leviathan Nivel 1 a 2

Nivel oficial: https://overthewire.org/wargames/leviathan/leviathan2.html

Este nivel introduce dos conceptos fundamentales del hacking Linux: los binarios con el bit SUID activado y el uso de `ltrace` para interceptar llamadas a funciones de biblioteca en tiempo de ejecucion. La combinacion de ambos permite leer la contrasena del siguiente nivel sin necesidad de ningun exploit de memoria.

> Este es un laboratorio de seguridad legal y autorizado (OverTheWire). Practica esto unicamente en entornos de wargame o sistemas propios.

## Objetivo

Conectarse como `leviathan1`, analizar el binario `check` del directorio home, extraer la contrasena que usa internamente y obtener una shell con privilegios de `leviathan2` para leer `/etc/leviathan_pass/leviathan2`.

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| `ls -la` | Ver permisos del archivo, incluyendo el bit setuid (`s`) |
| `file <binario>` | Identificar tipo de ejecutable y arquitectura |
| `ltrace <binario>` | Trazar llamadas a funciones de biblioteca compartida (libc, etc.) |
| `strcmp` (en ltrace) | Funcion de C que compara dos cadenas; revela la contrasena esperada |
| Bit SUID (`s`) | Ejecuta el binario con los privilegios del propietario, no del invocador |
| `cat /etc/leviathan_pass/leviathan2` | Leer la contrasena del siguiente nivel dentro de la shell privilegiada |

### Concepto clave

**Binarios SUID + ltrace** es una categoria de vulnerabilidad de **escalada de privilegios local por configuracion insegura**. El patron es:

1. Un binario pertenece a un usuario privilegiado y tiene el bit `s` en sus permisos (`-rwsr-x---`).
2. El binario ejecuta alguna comprobacion interna (como verificar una contrasena) usando funciones de libc como `strcmp`, `strcpy` o `getenv`.
3. `ltrace` intercepta esas llamadas *antes* de que el kernel las ejecute, mostrando los argumentos en claro: la contrasena queda expuesta.

La raiz del problema es que el binario toma una decision de seguridad (autenticar al usuario) basandose en una cadena hardcodeada, y no protege ese secreto en absoluto.

## Paso a paso

**1. Conectarse como leviathan1**

```bash
ssh leviathan1@leviathan.labs.overthewire.org -p 2223
# Contrasena: <pass_leviathan1>
```

**2. Inspeccionar el directorio home**

```bash
ls -la ~/
```

Busca la linea de `check`. El permiso relevante es el bit `s` en la posicion del ejecutable del propietario:

```
-rwsr-x--- 1 leviathan2 leviathan1  <size> <fecha> check
```

La `s` en lugar de `x` para el propietario indica SUID: cuando cualquier miembro del grupo `leviathan1` ejecute `check`, el proceso correra con UID efectivo de `leviathan2`.

**3. Confirmar el tipo de binario**

```bash
file ~/check
```

Salida esperada: ELF 32-bit LSB executable, dynamically linked. El enlazado dinamico es el requisito para que `ltrace` funcione; si fuera estatico, habria que usar otras tecnicas.

**4. Trazar las llamadas a biblioteca con ltrace**

```bash
ltrace ~/check
```

El programa pedira una contrasena. Escribe cualquier texto (por ejemplo `test`) y pulsa Enter. La salida de `ltrace` mostrara algo similar a:

```
__libc_start_main(...)
printf("password: ")                        = 10
gets(0xffffd580)                            = 0xffffd580
strcmp("test", "sex")                       = <valor_no_cero>
puts("Wrong password, Good Bye ...")
```

El segundo argumento de `strcmp` es la contrasena real hardcodeada en el binario. En este nivel es una palabra concreta que `ltrace` expone en claro.

**5. Ejecutar check con la contrasena correcta**

```bash
~/check
```

Cuando el programa pida `password:`, introduce la palabra que viste en `ltrace`. Si es correcta, el proceso no termina: abre una shell interactiva con privilegios de `leviathan2`.

**6. Verificar el usuario efectivo y leer la contrasena**

```bash
whoami
# leviathan2

cat /etc/leviathan_pass/leviathan2
# <pass_leviathan2>
```

Copia esa contrasena para el siguiente nivel.

## Por que funciona

El binario `check` es propietario de `leviathan2` y tiene el bit SUID activado. Cuando un miembro de `leviathan1` lo ejecuta, el kernel eleva el UID efectivo del proceso a `leviathan2`. El binario entonces compara la entrada del usuario con una cadena literal compilada dentro del ejecutable usando `strcmp`.

`ltrace` actua como un intermediario entre el binario y la libc: instala hooks en la tabla de enlace dinamico (PLT/GOT) y registra cada llamada antes de pasarla a la biblioteca real. Como `strcmp` recibe ambos argumentos en texto claro, `ltrace` los imprime sin necesidad de desensamblar ni parchear nada.

El error de diseno es doble: guardar un secreto hardcodeado en el binario y confiar en que el usuario no pueda inspeccionarlo. Ambas suposiciones son falsas en un sistema donde el atacante tiene acceso de lectura-ejecucion al archivo.

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| `ltrace: command not found` | No esta instalado en el sistema objetivo | Usar `strace` o `strings ./check` como alternativa para encontrar la cadena |
| La shell que se abre es la misma UID | No se ejecuto `check` sino otro binario, o el SUID no estaba activo | Confirmar con `ls -la` que la `s` esta en la posicion correcta y ejecutar exactamente `~/check` |
| `ltrace` no muestra `strcmp` | El binario esta compilado estaticamente o usa `strncmp` / funcion propia | Probar `strace -e trace=read,write ./check` o `strings ./check \| grep -i pass` |
| La contrasena con `ltrace` sale vacia o truncada | La entrada interactiva de `ltrace` puede requerir pasar la contrasena por pipe | Ejecutar: `echo "texto" \| ltrace ./check` para ver la llamada sin interaccion |

## Pasar al siguiente nivel

Con la contrasena obtenida de `/etc/leviathan_pass/leviathan2`, conectarse a:

```bash
ssh leviathan2@leviathan.labs.overthewire.org -p 2223
# Contrasena: <pass_leviathan2>
```

## Conexiones

- [[Leviathan/00_README]]
- [[MOC_Ciberseguridad]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[13-herramientas-en-detalle]]
