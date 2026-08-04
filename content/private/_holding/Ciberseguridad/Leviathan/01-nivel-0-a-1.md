---
title: Leviathan Nivel 0 -> 1
date: 2026-06-14
tags: [ciberseguridad, linux, terminal, leviathan, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Leviathan nivel 0, Leviathan 0 a 1, leviathan-archivos-ocultos]
---

# Leviathan Nivel 0 -> 1

> Nivel oficial: https://overthewire.org/wargames/leviathan/leviathan1.html
> Marco: OverTheWire Leviathan es un wargame **legal y autorizado** con fines exclusivamente educativos. No es hacking malicioso.

Leviathan es una serie corta centrada en binarios SUID y enumeracion basica de Linux. El nivel 0 es el punto de entrada: demuestra que la informacion sensible a veces esta oculta a la vista, no protegida por permisos.

---

## Objetivo

Conectarte al servidor como `leviathan0`, localizar un archivo con informacion sensible dentro de un directorio oculto y extraer de el la contrasena de `leviathan1`.

---

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| `ssh -p <puerto>` | Conectarse a un servidor remoto en un puerto no estandar |
| `ls -la` | Listar **todos** los archivos, incluidos los ocultos (prefijados con `.`) |
| `grep -i <patron> <archivo>` | Buscar lineas que contengan un patron, ignorando mayusculas/minusculas |
| Directorio oculto (`.nombre/`) | Carpeta cuyo nombre empieza con punto; `ls` sin flags no la muestra |
| Bookmarks / HTML como vector | Archivos de configuracion de aplicaciones pueden contener secretos filtrados |

### Concepto clave: archivos ocultos y secretos filtrados

**Categoria de tecnica:** enumeracion / busqueda de informacion sensible en texto plano.

**Patron:** las aplicaciones de escritorio (navegadores, clientes de correo, IDEs) guardan configuracion en directorios ocultos del home del usuario. Si alguien pega una contrasena en la URL de un marcador, queda almacenada en texto claro en `bookmarks.html`. Esta es una forma real de fuga de credenciales en entornos mal gestionados.

**Mecanismo de deteccion:** `grep` permite buscar un patron (`password`, `pass`, `secret`...) sobre el archivo sin tener que leerlo entero. El flag `-i` hace la busqueda insensible a mayusculas, cubriendo `Password`, `PASSWORD`, etc.

---

## Paso a paso

### 1. Conectarte al servidor como leviathan0

Leviathan usa el puerto 2223 (distinto al 22 por defecto y al 2220 de Bandit).

```bash
ssh leviathan0@leviathan.labs.overthewire.org -p 2223
```

La contrasena inicial del nivel 0 es publica: `leviathan0`.

Tras autenticarte veras el prompt:

```
leviathan0@leviathan:~$
```

### 2. Listar todos los archivos del home, incluidos los ocultos

```bash
ls -la
```

Salida esperada (simplificada):

```
drwxr-xr-x  3 leviathan0 leviathan0 4096 ...
drwxr-xr-x 10 root       root       4096 ...
-rw-r--r--  1 leviathan0 leviathan0  220 ... .bash_logout
-rw-r--r--  1 leviathan0 leviathan0 3526 ... .bashrc
drwxr-x---  2 leviathan1 leviathan0 4096 ... .backup
-rw-r--r--  1 leviathan0 leviathan0  675 ... .profile
```

El directorio `.backup/` pertenece a `leviathan1` pero el grupo es `leviathan0`, lo que te permite entrar. Sin `-la` jamas lo habrias visto.

### 3. Entrar al directorio oculto y ver su contenido

```bash
ls -la ~/.backup/
```

Veras un archivo `bookmarks.html`: los marcadores de un navegador exportados en formato HTML.

### 4. Buscar la contrasena con grep

El archivo es largo. En lugar de leerlo entero, busca directamente el patron relevante:

```bash
grep -i password ~/.backup/bookmarks.html
```

Salida esperada (fragmento):

```html
<A HREF="http://leviathan.labs.overthewire.org/passwordforthenextlevel=<pass_leviathan1>" ...>...
```

La contrasena de `leviathan1` aparece embebida en la URL de uno de los marcadores. Copiala.

---

## Por que funciona

Los navegadores exportan los marcadores como HTML estatico, donde las URLs se escriben literalmente. Si alguien guardo una contrasena dentro de una URL (por ejemplo, para no olvidarla o por error al pegar), queda en texto plano en ese archivo. No hay cifrado, no hay proteccion de permisos especiales: el propietario del home puede leerlo sin privilegios adicionales.

`grep` actua como un filtro de senial: en vez de procesar manualmente cientos de lineas de HTML, delega la busqueda al sistema. Este patron (buscar cadenas como `password`, `token`, `secret`, `key` en archivos de configuracion) es la base de herramientas de reconocimiento como `trufflehog` o `gitleaks` en auditorias reales.

---

## Errores comunes

- **`ls` no muestra `.backup/`**: olvidaste el flag `-a`. Los archivos y directorios ocultos solo aparecen con `ls -a` o `ls -la`.
- **`Permission denied` al entrar a `.backup/`**: comprueba que estas conectado como `leviathan0` y no como otro usuario. El directorio es legible por el grupo `leviathan0`.
- **`grep` no devuelve nada**: verifica que la ruta es correcta (`~/.backup/bookmarks.html`) y que escribiste el patron sin comillas de tipografia curva (usa comillas rectas ASCII).
- **Confundir el directorio `.backup/` con un archivo**: es un directorio, no un archivo. Usa `ls ~/.backup/` para ver su contenido antes de intentar leerlo con `cat`.

---

## Pasar al siguiente nivel

Con la contrasena obtenida, sal del servidor:

```bash
exit
```

Conéctate como `leviathan1`:

```bash
ssh leviathan1@leviathan.labs.overthewire.org -p 2223
```

Introduce `<pass_leviathan1>` cuando se solicite. En el nivel 1 encontraras un binario SUID que introduce el tema central de Leviathan.

---

## Conexiones

- [[Leviathan/00_README]]
- [[MOC_Ciberseguridad]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[13-herramientas-en-detalle]]
- Nivel oficial: https://overthewire.org/wargames/leviathan/leviathan1.html
