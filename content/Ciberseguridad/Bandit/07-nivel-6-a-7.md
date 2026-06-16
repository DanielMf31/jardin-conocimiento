---
title: Bandit Nivel 6 a 7
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, bandit, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Bandit nivel 6, bandit6 a bandit7, find servidor entero]
---

# Bandit Nivel 6 a 7

Walkthrough didactico del nivel 6 al 7 del wargame [Bandit de OverTheWire](https://overthewire.org/wargames/bandit/). Bandit es un juego legal y educativo pensado para aprender a usar la terminal Linux desde cero.

---

## Objetivo

La contraseña del siguiente nivel (bandit7) esta escondida **en algun lugar del servidor entero**, no solo en el directorio home. El archivo cumple tres condiciones simultaneas:

- Es propiedad del **usuario** `bandit7`
- Pertenece al **grupo** `bandit6`
- Tiene un tamaño exacto de **33 bytes**

---

## Que aprendes

### Comandos

| Comando / Sintaxis | Para que sirve |
|---|---|
| `find /` | Busca recursivamente desde la raiz del sistema de archivos (todo el servidor) |
| `-user <nombre>` | Filtra archivos cuyo propietario sea ese usuario |
| `-group <nombre>` | Filtra archivos cuyo grupo sea ese |
| `-size 33c` | Filtra por tamaño exacto: `c` = bytes (characters); otras unidades: `k`, `M`, `G` |
| `2>/dev/null` | Redirige los mensajes de error (descriptor 2) al "agujero negro" `/dev/null` |

### Conceptos clave

**Descriptores de fichero en Linux**

Cada proceso Linux tiene tres flujos de datos estandar:

- `0` — stdin (entrada)
- `1` — stdout (salida normal)
- `2` — stderr (mensajes de error)

Cuando haces `find /` como usuario sin privilegios, el comando intenta leer directorios a los que no tienes acceso y imprime cientos de lineas `Permission denied` en stderr. Eso ensucia la salida y hace imposible ver el resultado util.

`2>/dev/null` dice: "redirige el descriptor 2 (stderr) al archivo `/dev/null`", que es un dispositivo especial que descarta todo lo que recibe. Resultado: solo ves la salida normal (stdout), que es el archivo que buscas.

**Propiedad de archivos en Linux**

Todo archivo tiene dos identificadores de propiedad:
- **Usuario propietario** (owner): quien creo el archivo o a quien se lo asignaron con `chown`.
- **Grupo propietario**: el grupo al que pertenece el archivo, controlado con `chgrp`.

Esto permite esquemas de permisos mas finos: por ejemplo, que solo los miembros del grupo `bandit6` puedan leer el archivo, aunque el propietario sea `bandit7`.

---

## Paso a paso

### 1. Conectarse como bandit6

```bash
ssh bandit6@bandit.labs.overthewire.org -p 2220
```

Introduce la contraseña que obtuviste en el nivel anterior (la que encontraste en el nivel 5→6).

Veras algo como:

```
bandit6@bandit:~$
```

### 2. Comprobar que el home no tiene nada util

```bash
ls -la
```

```
total 20
drwxr-xr-x  2 root root 4096 Apr 23 18:04 .
drwxr-xr-x 70 root root 4096 Apr 23 18:04 ..
-rw-r--r--  1 root root  220 Jan  6  2022 .bash_logout
-rw-r--r--  1 root root 3526 Jan  6  2022 .bashrc
-rw-r--r--  1 root root  807 Jan  6  2022 .profile
```

El directorio home esta vacio de contenido util. La pista dice que el archivo esta "en algun lugar del servidor entero", asi que hay que buscar en `/` (la raiz).

### 3. Buscar en todo el servidor con los tres filtros

```bash
find / -user bandit7 -group bandit6 -size 33c 2>/dev/null
```

Desglose del comando:

- `find /` — empieza la busqueda desde la raiz, recorriendo todo el sistema de archivos
- `-user bandit7` — el propietario del archivo debe ser `bandit7`
- `-group bandit6` — el grupo debe ser `bandit6`
- `-size 33c` — el tamaño debe ser exactamente 33 bytes
- `2>/dev/null` — descarta los errores "Permission denied" para que la salida sea legible

Veras algo como:

```
/var/lib/dpkg/info/bandit7.password
```

Solo aparece una ruta. Ese es el archivo.

### 4. Leer el archivo

```bash
cat /var/lib/dpkg/info/bandit7.password
```

Veras:

```
<cadena_de_~32_caracteres>
```

Esa cadena ES la contraseña del siguiente nivel (bandit7). Copiala.

---

## Por que funciona

`find` es una herramienta de busqueda que recorre el arbol de directorios evaluando condiciones sobre cada archivo que encuentra. Cuando le dices `find /` le dices que empiece desde la raiz, lo que significa que revisara absolutamente todos los archivos del servidor.

Los filtros `-user`, `-group` y `-size` se combinan con AND logico por defecto: el archivo debe cumplir las tres condiciones a la vez. Esto reduce dramaticamente el numero de resultados hasta dejar uno solo.

Sin `2>/dev/null`, la salida seria algo como:

```
find: '/root': Permission denied
find: '/home/bandit28-git': Permission denied
find: '/home/bandit29-git': Permission denied
... (cientos de lineas) ...
/var/lib/dpkg/info/bandit7.password
find: '/lost+found': Permission denied
... (mas lineas) ...
```

El resultado util queda enterrado entre errores. Con la redireccion, solo ves la linea que importa.

La ubicacion `/var/lib/dpkg/info/` es el directorio interno que usa el gestor de paquetes `dpkg` para almacenar metadatos de paquetes instalados. El archivo esta "escondido" ahi a proposito: no es un lugar donde buscaras a mano, pero `find` lo encuentra sin importar donde este.

---

## Errores comunes

**No usar `2>/dev/null` y perderse en el ruido**

Si ejecutas `find / -user bandit7 -group bandit6 -size 33c` sin la redireccion, veras cientos de mensajes de error y puede que no veas el resultado. Siempre añade `2>/dev/null` cuando busques en directorios a los que no tienes permisos.

**Usar `-size 33` sin la unidad `c`**

`-size 33` sin unidad usa bloques de 512 bytes por defecto en algunos sistemas (o bloques de 1024 bytes). Para especificar bytes exactos, siempre usa el sufijo `c` (de *characters*): `-size 33c`.

**Empezar la busqueda desde `~` en lugar de `/`**

Si usas `find ~ ...` o `find . ...`, buscas solo en el directorio home, que esta vacio. El enunciado dice "en algun lugar del servidor entero", lo que significa que hay que buscar desde `/`.

**Confundir `-user` con `-owner`**

En `find`, el flag correcto es `-user`, no `-owner`. Usar `-owner` dara un error de opcion no reconocida.

---

## Pasar al siguiente nivel

Usa la cadena obtenida como contraseña para conectarte como bandit7:

```bash
ssh bandit7@bandit.labs.overthewire.org -p 2220
```

Cuando el prompt pida la password, pega la cadena que leiste del archivo (`<cadena_de_~32_caracteres>`).

---

## Conexiones

- [[Bandit/00_README]] — indice del wargame y convenciones de la serie
- [[MOC_Ciberseguridad]] — mapa de contenido de ciberseguridad en la boveda
- — referencia ampliada de `find` y sus opciones
- Nivel anterior: [[06-nivel-5-a-6]] — busqueda con multiples atributos en el directorio home
- Nivel siguiente: [[08-nivel-7-a-8]] — buscar dentro del contenido de archivos con `grep`
