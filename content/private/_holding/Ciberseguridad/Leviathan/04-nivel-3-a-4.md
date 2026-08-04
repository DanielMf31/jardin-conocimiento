---
title: Leviathan Nivel 3 a 4
date: 2026-06-14
tags: [ciberseguridad, linux, setuid, ltrace, leviathan, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Leviathan 3-4, leviathan nivel 3, ltrace strcmp setuid]
---

# Leviathan Nivel 3 a 4

Nivel oficial: https://overthewire.org/wargames/leviathan/leviathan4.html

Este nivel pertenece al wargame legal y educativo [OverTheWire Leviathan](https://overthewire.org/wargames/leviathan/), diseñado exclusivamente para la practica autorizada de habilidades de seguridad ofensiva. Hay un binario SUID que protege el acceso al siguiente nivel con una comprobacion de contrasena en claro; la tecnica es identica a la del nivel 1, lo que refuerza el patron de inspeccion con `ltrace`.

---

## Objetivo

Ejecutar el binario `level3` (propiedad de `leviathan4`, con bit SUID activo), descubrir la contrasena que compara internamente mediante `ltrace`, introducirla para obtener una shell como `leviathan4`, y leer `/etc/leviathan_pass/leviathan4`.

---

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| **Bit SUID** | El ejecutable corre con los privilegios del propietario del archivo, no del usuario que lo invoca. |
| **`ltrace`** | Intercepta y muestra en tiempo real las llamadas a funciones de biblioteca (libc) que hace un proceso. Clave para ver comparaciones de strings en binarios sin codigo fuente. |
| **`strcmp`** | Funcion de libc que compara dos cadenas. Si el binario la usa para validar una contrasena, `ltrace` la expone en claro. |
| **Shell escalada** | Cuando el binario autentica correctamente, lanza `/bin/sh` con UID efectivo del propietario (leviathan4). |
| **`cat /etc/leviathan_pass/leviathan4`** | Lee la contrasena del siguiente nivel desde el archivo protegido. |

### Concepto clave

**Inspeccion dinamica de binarios SUID con `ltrace`**: cuando un binario no tiene codigo fuente disponible y protege el acceso con una contrasena, la forma mas rapida de extraerla es trazar sus llamadas a libc. Si la validacion usa `strcmp(input, "secreto")`, `ltrace` muestra ambos argumentos de la funcion en la salida, revelando la cadena esperada sin necesidad de desensamblar el binario ni aplicar ingenieria inversa estatica.

Este patron — SUID + `strcmp` en claro — es una vulnerabilidad de diseno: las contrasenas nunca deben compararse en claro con funciones de libc directamente accesibles a trazadores de proceso.

---

## Paso a paso

### 1. Conectarse al nivel 3

```bash
ssh leviathan3@leviathan.labs.overthewire.org -p 2223
```

Introduce `<pass_leviathan3>` cuando te lo pida.

---

### 2. Explorar el home y verificar el binario

```bash
ls -la
```

**Lo que veras:**

```
-r-sr-x--- 1 leviathan4 leviathan3 7288 ... level3
```

La `s` en la posicion de ejecucion del propietario indica SUID activo. El propietario es `leviathan4`, asi que cualquier ejecucion del binario correra con ese UID efectivo.

---

### 3. Ejecutar el binario a secas (explorar comportamiento)

```bash
./level3
```

**Lo que veras:**

```
Enter the password>
```

El binario solicita una contrasena por stdin. Prueba cualquier cadena para confirmar que la rechaza:

```
bzzzzzzzzap. WRONG
```

---

### 4. Trazar las llamadas a libc con ltrace

```bash
ltrace ./level3
```

Cuando el binario pida la contrasena, escribe cualquier cadena (p.ej. `test`) y pulsa Enter. `ltrace` mostrara algo similar a:

```
__libc_start_main(...)                           = ...
puts("Enter the password> ")                     = ...
fgets("test\n", 256, 0x...)                      = 0x...
strcmp("test\n", "snlprintf\n")                  = ...
puts("bzzzzzzzzap. WRONG")                       = ...
+++ exited (status 1) +++
```

El segundo argumento de `strcmp` es la contrasena esperada por el binario. En el ejemplo de arriba seria `snlprintf` (el valor real puede diferir; usa el que aparezca en tu sesion en vivo).

---

### 5. Introducir la contrasena correcta

Ejecuta de nuevo el binario sin `ltrace` y escribe la cadena descubierta (sin el `\n` que muestra ltrace, que es solo la representacion del salto de linea):

```bash
./level3
```

```
Enter the password> snlprintf
```

**Lo que veras si la contrasena es correcta:**

```
[You've got shell]!
$
```

El binario lanza una shell. El prompt `$` indica que ya estas dentro con el UID efectivo de `leviathan4`.

---

### 6. Leer la contrasena del siguiente nivel

```bash
cat /etc/leviathan_pass/leviathan4
```

**Lo que veras:**

```
<pass_leviathan4>
```

Copia esa cadena; es la contrasena para conectarte al nivel 4.

---

### 7. Salir de la shell escalada

```bash
exit
```

Vuelves a la sesion original de `leviathan3`.

---

## Por que funciona

El flujo completo de privilegios es:

1. `level3` tiene SUID activo y propietario `leviathan4`.
2. El kernel lanza el proceso con UID efectivo = `leviathan4`, aunque quien lo invoca sea `leviathan3`.
3. Internamente el binario llama a `strcmp(input_usuario, contrasena_hardcodeada)`.
4. `ltrace` intercepta esa llamada **antes** de que el kernel la resuelva, mostrando ambos argumentos en claro: el input que escribiste y la contrasena correcta que el binario guarda en su segmento de datos.
5. Una vez autenticado, el binario llama a `system("/bin/sh")` o equivalente; esa shell hereda el UID efectivo de `leviathan4`.
6. Desde esa shell, `/etc/leviathan_pass/leviathan4` es legible porque el proceso tiene permisos de `leviathan4`.

La raiz del problema es doble: (a) comparar en claro con `strcmp` en lugar de un mecanismo de desafio-respuesta o hash, y (b) que el UID efectivo del proceso es suficiente para que `ltrace` lo trace (en sistemas reales con hardening, los binarios SUID pueden bloquear ptrace).

---

## Errores comunes

### ltrace no muestra el strcmp

En algunas versiones del sistema, `ltrace` sobre binarios SUID puede requerir privilegios adicionales o puede estar restringido. Si no aparecen las llamadas de libc, prueba con `strace -e trace=read,write ./level3` para ver al menos el flujo de I/O, o aplica ingenieria inversa estatica con `strings ./level3` para buscar literales de cadena en el binario.

```bash
strings ./level3 | grep -v "^\..*"
```

Esto puede revelar la contrasena directamente si esta hardcodeada como literal ASCII.

---

### Escribir la contrasena con el `\n` incluido

`ltrace` representa el salto de linea como `\n` en la salida. No escribas `\n` literalmente al introducir la contrasena; pulsa simplemente Enter al final, que es el salto de linea que el binario espera del fgets.

---

### Cerrar la shell escalada antes de leer la contrasena

Si escribes `exit` nada mas obtener la shell, vuelves a la sesion de `leviathan3` sin haber leido la contrasena. La shell escalada dura mientras no la cierres; aprovechala para ejecutar todos los comandos que necesites.

---

### Confundir ltrace con strace

`ltrace` traza llamadas a **funciones de biblioteca** (libc): `strcmp`, `fgets`, `puts`, etc. `strace` traza **llamadas al sistema** (syscalls del kernel): `read`, `write`, `open`, etc. Para este nivel, `ltrace` es la herramienta correcta porque la logica de validacion esta en libc, no en syscalls directas.

---

## Pasar al siguiente nivel

Con la contrasena obtenida en el paso 6:

```bash
ssh leviathan4@leviathan.labs.overthewire.org -p 2223
```

Introduce `<pass_leviathan4>` cuando te lo pida.

---

## Conexiones

- [[Leviathan/00_README]] — indice general del wargame y convenciones de la serie
- [[MOC_Ciberseguridad]] — mapa de contenido de ciberseguridad en la boveda
- [[06-seguridad-de-sistemas-y-hardening]] — contexto sobre SUID, permisos y hardening de sistemas Linux
- [[13-herramientas-en-detalle]] — referencia extendida de ltrace, strace y otras herramientas de inspeccion dinamica
