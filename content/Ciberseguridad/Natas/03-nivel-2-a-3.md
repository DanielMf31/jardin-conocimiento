---
title: Natas Nivel 2 a 3
date: 2026-06-14
tags: [ciberseguridad, web, owasp, natas, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [natas2, natas nivel 2, directory listing natas]
---

# Natas Nivel 2 a 3

Nivel oficial: [http://natas2.natas.labs.overthewire.org](http://natas2.natas.labs.overthewire.org)

Este nivel ilustra uno de los errores mas frecuentes en servidores web mal configurados: dejar accesible un directorio con listado habilitado. La pagina no muestra nada util, pero el codigo fuente revela una ruta que el servidor sirve sin restriccion.

> Este ejercicio pertenece a OverTheWire Natas, un laboratorio legal y autorizado para practicar seguridad web de forma etica.

## Objetivo

Obtener la contrasena de `natas3` leyendo un archivo expuesto en un directorio accesible publicamente en el servidor web.

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| Inspeccion de codigo fuente HTML | Descubrir recursos cargados que no se muestran en pantalla |
| Directory listing | Listar ficheros de un directorio cuando el servidor no tiene `index.html` y la opcion esta habilitada |
| `curl -u usuario:pass URL` | Hacer peticiones HTTP con autenticacion Basic desde la terminal |
| Enumeracion de rutas | Explorar subdirectorios a partir de pistas en el codigo o en los recursos |

### Concepto clave

**Directory listing** es una mala configuracion del servidor web (Apache, Nginx, etc.) que permite ver el contenido de un directorio como si fuera un explorador de archivos, cuando no existe un archivo `index.html` o `index.php` que sirva de pagina por defecto. Categoria OWASP: **Security Misconfiguration** (A05:2021).

El patron es:
1. El servidor tiene un directorio `/files/` (o similar) que aloja recursos.
2. No hay archivo de indice en ese directorio.
3. El servidor tiene `Options +Indexes` activo (Apache) o equivalente.
4. Cualquier visitante puede navegar a esa URL y ver todos los archivos listados.

Los ficheros no necesitan estar enlazados en la interfaz para ser accesibles; basta con conocer la ruta.

## Paso a paso

**1. Autenticarse en el nivel con las credenciales anteriores**

```bash
# Abre en el navegador o verifica con curl
curl -u natas2:<pass_natas2> http://natas2.natas.labs.overthewire.org/
```

La pagina devuelve: *"There is nothing on this page"*.

**2. Inspeccionar el codigo fuente HTML**

En el navegador: `Ctrl+U` (o `Ver codigo fuente`). Busca referencias a recursos.

Encontraras esta linea:

```html
<img src="files/pixel.png">
```

Esto revela que existe el directorio `files/` en el servidor.

**3. Acceder al directorio y comprobar si tiene listado habilitado**

```bash
curl -u natas2:<pass_natas2> http://natas2.natas.labs.overthewire.org/files/
```

El servidor devuelve un listado HTML con los archivos del directorio. Entre ellos aparece `users.txt`.

**4. Leer el archivo users.txt**

```bash
curl -u natas2:<pass_natas2> http://natas2.natas.labs.overthewire.org/files/users.txt
```

El archivo contiene un listado de usuarios con sus contrasenas en texto plano. Localiza la entrada `natas3` y copia su valor: `<pass_natas3>`.

## Por que funciona

El servidor tiene habilitado el directory listing para el directorio `/files/`. Cuando un cliente solicita esa URL, Apache (u otro servidor) genera automaticamente una pagina HTML con los ficheros presentes, ya que no encuentra un `index.html` que sirva en su lugar. El archivo `users.txt` nunca fue enlazado desde la interfaz, pero al estar dentro de un directorio servido publicamente, es completamente accesible para cualquiera que conozca o adivine la ruta.

La autenticacion HTTP Basic (`-u natas2:<pass>`) solo protege el acceso al dominio completo con esas credenciales; no impide la navegacion interna una vez autenticado.

## Errores comunes

1. **Olvidar la autenticacion Basic en curl**: sin `-u natas2:<pass_natas2>` el servidor devuelve `401 Unauthorized`. Incluye siempre las credenciales del nivel actual.

2. **Buscar solo en la interfaz visible**: el contenido de la pagina dice que no hay nada, lo que lleva a abandonar. La inspeccion del codigo fuente es el primer paso sistematico antes de concluir que un nivel esta vacio.

3. **Asumir que un archivo no accesible porque no esta enlazado**: la falta de enlace no es control de acceso. Si el servidor sirve el directorio, cualquier fichero en el es publico.

4. **No explorar subdirectorios revelados**: cuando el codigo fuente menciona una ruta (`files/`, `images/`, `uploads/`), siempre vale la pena navegar al directorio padre para ver si el listado esta activo.

## Pasar al siguiente nivel

Usa la contrasena obtenida (`<pass_natas3>`) para acceder a:

```
http://natas3.natas.labs.overthewire.org
```

Con usuario `natas3` y la contrasena encontrada en `users.txt`.

## Conexiones

- [[Natas/00_README]]
- [[MOC_Ciberseguridad]]
- [[04-seguridad-web-owasp]]
- [[13-herramientas-en-detalle]]
