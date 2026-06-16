---
title: Natas Nivel 1 -> 2
date: 2026-06-14
tags: [ciberseguridad, web, owasp, natas, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Natas nivel 1, Natas clic derecho, Natas view-source, client-side control bypass]
---

# Natas Nivel 1 -> 2

> Nivel oficial: http://overthewire.org/wargames/natas/natas2.html

Este nivel introduce la categoria mas fundamental de la seguridad web: **los controles del lado cliente no son seguridad**. La pagina intenta ocultar informacion deshabilitando el clic derecho mediante JavaScript, pero cualquier usuario con conocimientos basicos puede saltarselo en segundos.

> Este wargame es un laboratorio legal y autorizado. Toda practica aqui descrita esta restringida a los servidores de OverTheWire.

---

## Objetivo

Obtener la contrasena de `natas2` oculta en el codigo fuente HTML de `http://natas1.natas.labs.overthewire.org`.

---

## Que aprendes

| Concepto / Comando          | Para que sirve                                                                    |
| --------------------------- | --------------------------------------------------------------------------------- |
| `Ctrl+U` en el navegador    | Ver el codigo fuente HTML de cualquier pagina web sin clic derecho                |
| `curl -u usuario:pass URL`  | Hacer peticiones HTTP autenticadas desde la terminal                              |
| Comentarios HTML `<!-- -->` | Mecanismo comun donde desarrolladores dejan datos sensibles por descuido          |
| Modelo cliente/servidor     | Entender que el HTML ya esta en tu maquina antes de que el navegador lo renderice |

### Concepto clave: controles del lado cliente

Un **control del lado cliente** es cualquier restriccion que se aplica en el navegador del usuario (JavaScript, CSS, atributos HTML). La caracteristica definitoria es que **el atacante controla ese entorno**: puede deshabilitarlo, modificarlo o ignorarlo por completo.

El patron general es:

1. El servidor envia el HTML completo al navegador.
2. JavaScript deshabilita una funcionalidad de la interfaz (clic derecho, seleccion de texto, inspeccion de elementos).
3. El atacante pide el HTML directamente al servidor, sin pasar por el navegador restringido.

La restriccion nunca llega a ejecutarse porque el atacante no usa el canal que el JavaScript vigila. Este es el **Patron de Seguridad del lado equivocado**: proteger la vista, no el dato.

---

## Paso a paso

### 1. Conectarse al nivel 1

Abre el navegador y accede a:

```
http://natas1.natas.labs.overthewire.org
```

El navegador te pedira credenciales HTTP Basic:

- **Usuario**: `natas1`
- **Contrasena**: `<pass_natas1>` (obtenida en el nivel 0)

Veras un mensaje similar a "You can find the password for the next level on this page, but rightclicking has been blocked!" y el clic derecho estara deshabilitado por JavaScript.

---

### 2. Ver el codigo fuente (metodo navegador)

El bloqueo del clic derecho solo suprime el menu contextual del navegador. El atajo de teclado funciona sin ningun impedimento:

```
Ctrl+U
```

Se abre una nueva pestana con el codigo fuente HTML crudo. Busca en el en el contenido un comentario HTML:

```html
<!--The password for natas2 is <pass_natas2>-->
```

Esa cadena es la contrasena del nivel 2.

---

### 3. Ver el codigo fuente (metodo terminal con curl)

Si prefieres no usar el navegador, `curl` hace la peticion HTTP directamente y devuelve el HTML sin ejecutar ningun JavaScript:

```bash
curl -u natas1:<pass_natas1> http://natas1.natas.labs.overthewire.org
```

La salida incluira el comentario HTML con la contrasena visible en texto plano. Puedes filtrarla directamente:

```bash
curl -s -u natas1:<pass_natas1> http://natas1.natas.labs.overthewire.org | grep -i password
```

---

### 4. Anotar la contrasena

Guarda `<pass_natas2>` para el siguiente nivel. No importa si la copiaste del navegador o de la terminal: es el mismo valor.

---

## Por que funciona

El navegador recibe el HTML completo del servidor antes de ejecutar el JavaScript. El orden es invariable:

1. Peticion HTTP al servidor.
2. Servidor responde con el documento HTML (incluyendo el comentario con la contrasena).
3. El navegador parsea el HTML.
4. El navegador ejecuta el JavaScript que deshabilita el clic derecho.

En el paso 2 la informacion ya salio del servidor. No hay ningun mecanismo que impida leerla porque el servidor no tiene forma de saber si el cliente que recibe el HTML es un navegador con JavaScript activo, `curl`, o `wget`. El servidor no distingue: entrega el mismo documento a todos.

La unica forma real de proteger informacion es **no enviarla al cliente**. Si la contrasena no esta en el HTML, no puede extraerse del HTML.

---

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| El navegador pide credenciales pero no acepta la contrasena | Usaste la contrasena de `natas0` en lugar de `natas1` | Cada nivel tiene su propia contrasena; asegurate de usar la del nivel anterior correcto |
| `curl` devuelve `401 Unauthorized` | Las credenciales en `-u` tienen un espacio o caracter extra | Pon la contrasena entre comillas simples: `-u natas1:'<pass_natas1>'` |
| `Ctrl+U` no abre nada | El navegador tiene atajos de teclado distintos (algunos kioscos/entornos bloqueados) | Usa `curl` desde la terminal; nunca dependas solo del navegador |
| El comentario no aparece en el fuente | Buscaste en la pestana de DevTools en lugar del fuente crudo | `Ctrl+U` abre el fuente sin procesar; DevTools muestra el DOM modificado por JS |

---

## Pasar al siguiente nivel

Con `<pass_natas2>`, accede a:

```
http://natas2.natas.labs.overthewire.org
```

Credenciales:

- **Usuario**: `natas2`
- **Contrasena**: `<pass_natas2>`

---

## Conexiones

- [[Natas/00_README]]
- [[MOC_Ciberseguridad]]
- [[04-seguridad-web-owasp]]
- [[13-herramientas-en-detalle]]
