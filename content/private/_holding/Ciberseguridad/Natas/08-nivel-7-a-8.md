---
title: Natas Nivel 7 a 8
date: 2026-06-14
tags: [ciberseguridad, web, owasp, natas, lfi, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Natas7, Natas nivel 7, LFI natas]
---

# Natas Nivel 7 a 8

Nivel oficial: http://natas7.natas.labs.overthewire.org/

Este nivel introduce una de las vulnerabilidades web mas clasicas: **Local File Inclusion (LFI)**. La aplicacion expone un parametro de navegacion que acepta rutas de archivo sin ningun tipo de validacion, permitiendo leer ficheros arbitrarios del servidor. Este es un laboratorio legal y autorizado; practicarlo fuera de OverTheWire sin permiso es ilegal.

## Objetivo

Obtener la contrasena de `natas8` leyendo el archivo `/etc/natas_webpass/natas8` a traves del parametro vulnerable `page`.

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| `?page=home` / `?page=about` | Parametro de navegacion que el servidor usa para incluir archivos PHP |
| LFI (Local File Inclusion) | Leer ficheros del servidor manipulando rutas en parametros sin validar |
| `/etc/natas_webpass/natasN` | Convencion de OverTheWire: cada nivel guarda su pass en este path |
| `curl -u natas7:<pass_natas7> "URL"` | Autenticacion HTTP Basic desde la terminal para automatizar peticiones |

### Concepto clave

**Local File Inclusion** es una vulnerabilidad de la categoria [[04-seguridad-web-owasp]] (OWASP A01 — Broken Access Control / A03 — Injection, segun edicion). Ocurre cuando el servidor construye una ruta de archivo concatenando directamente la entrada del usuario:

```php
// Codigo vulnerable tipico
include($_GET['page']);
```

Si `page` no se filtra ni se restringe a una lista blanca, el atacante puede sustituir `home` por cualquier ruta absoluta del sistema, como `/etc/passwd` o —en este caso— el archivo de contrasena del siguiente nivel.

El patron es: **parametro controlable → funcion de inclusion PHP (include/require) → ruta arbitraria → lectura de fichero**.

## Paso a paso

1. **Conectarse al nivel** con las credenciales de natas7:

```bash
curl -u natas7:<pass_natas7> "http://natas7.natas.labs.overthewire.org/"
```

2. **Observar el comportamiento normal.** El menu tiene dos enlaces:

```
http://natas7.natas.labs.overthewire.org/index.php?page=home
http://natas7.natas.labs.overthewire.org/index.php?page=about
```

Cada enlace carga un contenido diferente segun el valor de `page`. Esto indica que el servidor incluye un archivo cuyo nombre viene del parametro.

3. **Identificar la vulnerabilidad.** El codigo del servidor hace algo equivalente a `include("./pages/" . $_GET['page'])` o directamente `include($_GET['page'])`. Si acepta rutas absolutas (sin restriccion de directorio), podemos salir del directorio de la aplicacion.

4. **Explotar LFI apuntando al archivo de contrasena:**

```bash
curl -u natas7:<pass_natas7> \
  "http://natas7.natas.labs.overthewire.org/index.php?page=/etc/natas_webpass/natas8"
```

5. **Leer la salida.** El servidor devuelve la pagina HTML con el contenido del archivo incluido. Busca la cadena alfanumerica de 32 caracteres que aparece en el cuerpo: esa es `<pass_natas8>`.

6. **Verificar acceso al siguiente nivel:**

```bash
curl -u natas8:<pass_natas8> "http://natas8.natas.labs.overthewire.org/"
```

## Por que funciona

PHP ejecuta `include()` (y `require()`, `include_once()`, `require_once()`) en tiempo de ejecucion usando la ruta que recibe. Si esa ruta empieza por `/`, PHP la trata como absoluta y accede directamente al sistema de ficheros, ignorando cualquier directorio base que el desarrollador pensara que estaba usando. El servidor web corre con permisos suficientes para leer `/etc/natas_webpass/natas8`, y el resultado del archivo se inyecta en la respuesta HTML como si fuera contenido de la aplicacion.

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| La pagina devuelve el mismo contenido que `home` | El codigo concatena un prefijo de directorio o sufijo `.php` fijo | Probar `....//....//etc/natas_webpass/natas8` o `php://filter/` si hay extension forzada |
| `403 Forbidden` o pagina en blanco | El proceso PHP no tiene permisos de lectura sobre ese archivo | Poco probable en Natas; verificar que la URL este bien formada y sin espacios |
| Credenciales rechazadas | Se uso la pass de natas6 en vez de natas7 | Confirmar que se avanzaron todos los niveles anteriores |
| No se ve la contrasena en el HTML | El contenido llega pero esta embebido en etiquetas; usar `grep` o `curl | grep -oP '[a-zA-Z0-9]{32}'` | Filtrar la salida con expresion regular |

## Pasar al siguiente nivel

La contrasena obtenida es la de `natas8`. Acceder en:

```
http://natas8.natas.labs.overthewire.org/
Usuario: natas8
Contrasena: <pass_natas8>
```

El siguiente nivel introduce **codificacion/ofuscacion de secretos en codigo fuente PHP**: se expone el codigo y hay que revertir la transformacion aplicada a la contrasena.

## Conexiones

- [[Natas/00_README]]
- [[MOC_Ciberseguridad]]
- [[04-seguridad-web-owasp]]
- [[13-herramientas-en-detalle]]
