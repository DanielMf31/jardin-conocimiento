---
title: Natas Nivel 0 a 1
date: 2026-06-14
tags: [ciberseguridad, web, owasp, natas, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Natas 0, Natas Nivel 0, natas0 a natas1]
---

# Natas Nivel 0 a 1

Nivel oficial: https://overthewire.org/wargames/natas/

Este es el nivel introductorio de Natas, el wargame de OverTheWire dedicado a seguridad web del lado del servidor. La vulnerabilidad es deliberadamente obvia para ensenar el principio mas fundamental: el servidor entrega al cliente todo el HTML, incluyendo los comentarios.

> Este ejercicio forma parte de OverTheWire Natas, un laboratorio legal y autorizado para la practica etica de seguridad web.

---

## Objetivo

Encontrar la contrasena de `natas1` oculta en el codigo fuente HTML de la pagina de `natas0`.

- URL: `http://natas0.natas.labs.overthewire.org`
- Credenciales de entrada: usuario `natas0`, contrasena `natas0`

---

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| Ver codigo fuente en el navegador (`Ctrl+U`) | Inspeccionar el HTML crudo que el servidor envia al cliente |
| `curl -u usuario:pass <URL>` | Realizar peticiones HTTP con autenticacion Basic desde la terminal |
| `grep -i pass` | Filtrar lineas que contengan la palabra "pass" (sin distinguir mayusculas) |
| Comentarios HTML `<!-- ... -->` | Anotaciones que el navegador ignora pero que son visibles en el codigo fuente |

### Concepto clave

**Categoria: Exposicion de informacion sensible en el cliente (Information Disclosure)**

Patron: el desarrollador incluye un secreto (contrasena, token, clave API) directamente en el HTML que se envia al navegador. Aunque el secreto no se *muestra* en la pagina renderizada, cualquier usuario puede leerlo con "Ver codigo fuente". Esto es equivalente a escribir la clave en un post-it pegado en el escaparate.

La regla de oro: **todo lo que llega al cliente es publico.** HTML, JavaScript, CSS, comentarios. El servidor es el unico lugar donde los secretos pueden estar a salvo.

Este patron aparece en el [[04-seguridad-web-owasp]] bajo *A05: Security Misconfiguration* y *A01: Broken Access Control*.

---

## Paso a paso

**1. Conectarse al nivel**

Abre el navegador y navega a:

```
http://natas0.natas.labs.overthewire.org
```

Introduce las credenciales cuando el navegador lo solicite (autenticacion HTTP Basic):
- Usuario: `natas0`
- Contrasena: `natas0`

La pagina muestra el mensaje "You can find the password for the next level on this page."

**2a. Opcion navegador: ver el codigo fuente**

Pulsa `Ctrl+U` (o clic derecho > "Ver codigo fuente de la pagina"). Busca en el HTML un comentario similar a:

```html
<!--The password for natas1 is <pass_natas1> -->
```

Esa cadena entre las etiquetas de comentario es la contrasena de `natas1`.

**2b. Opcion CLI: curl + grep**

Si prefieres la terminal o quieres automatizarlo:

```bash
curl -s -u natas0:natas0 http://natas0.natas.labs.overthewire.org/ | grep -i pass
```

- `-s`: modo silencioso (suprime la barra de progreso).
- `-u natas0:natas0`: envia cabecera `Authorization: Basic` con las credenciales.
- `grep -i pass`: filtra las lineas que contienen "pass" en cualquier capitalizacion.

La salida mostrara la linea del comentario HTML con la contrasena en texto claro.

**3. Anotar la contrasena**

Guarda el valor `<pass_natas1>` que obtuviste. Lo necesitaras para acceder a `http://natas1.natas.labs.overthewire.org`.

---

## Por que funciona

HTTP es un protocolo de texto plano entre cliente y servidor. Cuando el servidor responde a tu peticion GET, envia el fichero HTML completo, incluyendo comentarios. El navegador *renderiza* solo el contenido visible, pero los comentarios siguen presentes en la respuesta y son accesibles con cualquier herramienta (Ctrl+U, curl, Burp Suite, DevTools).

Poner un secreto en un comentario HTML es equivalente a no ocultarlo: no hay mecanismo tecnico que impida al cliente leer el codigo fuente. La unica proteccion real es no poner secretos alli.

---

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| El navegador pide usuario y contrasena en bucle | Escribir mal las credenciales del nivel actual | Asegurate de usar `natas0` / `natas0` en el nivel 0 |
| `curl` devuelve `401 Unauthorized` | Olvidar el flag `-u` o usar credenciales equivocadas | Añadir `-u natas0:natas0` explicitamente |
| "Ver fuente" no muestra nada util | Estas viendo el inspector de DevTools (DOM en vivo) en lugar del HTML crudo | Usar `Ctrl+U` para el codigo fuente original, no `F12` |
| Confundir la contrasena de entrada con la de salida | `natas0` es la pass para entrar al nivel; la que buscas es la de `natas1` | La contrasena objetivo esta en el comentario HTML, no es `natas0` |

---

## Pasar al siguiente nivel

Accede a:

```
http://natas1.natas.labs.overthewire.org
```

- Usuario: `natas1`
- Contrasena: `<pass_natas1>` (la que encontraste en el comentario HTML)

---

## Conexiones

- [[Natas/00_README]]
- [[MOC_Ciberseguridad]]
- [[04-seguridad-web-owasp]]
- [[13-herramientas-en-detalle]]
