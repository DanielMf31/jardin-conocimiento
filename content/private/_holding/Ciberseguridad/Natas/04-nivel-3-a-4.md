---
title: Natas Nivel 3 a 4
date: 2026-06-14
tags: [ciberseguridad, web, owasp, natas, wargame, reconocimiento, robots-txt, security-by-obscurity]
type: nota
status: en-progreso
source: claude-code
aliases: [Natas nivel 3, Natas robots.txt, Natas s3cr3t]
---

# Natas Nivel 3 a 4

> Nivel oficial: https://overthewire.org/wargames/natas/natas4.html

Este nivel demuestra una de las falacias mas extendidas en seguridad web: creer que ocultar una ruta del indexado publico equivale a protegerla. El archivo `robots.txt`, pensado para guiar a los crawlers, puede convertirse en un mapa de rutas sensibles.

> Este es un laboratorio legal y autorizado. Toda practica se realiza en los servidores de OverTheWire, con permiso explicito.

---

## Objetivo

Encontrar el archivo `users.txt` que contiene la contrasena de `natas4`, localizado en una ruta no enlazada pero descubierta a traves de `robots.txt`.

---

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| `robots.txt` | Protocolo de exclusion de robots: indica a crawlers que rutas no indexar |
| `Disallow:` | Directiva que prohíbe el acceso a bots... pero no a humanos |
| Acceso directo a rutas | Un navegador (o `curl`) puede acceder a cualquier ruta si sabe la URL |
| `curl -u user:pass URL` | Peticion HTTP con autenticacion Basic desde la terminal |
| Security by obscurity | Anti-patron: asumir que lo no publicado esta protegido |

### Concepto clave: security by obscurity

La categoria de vulnerabilidad es **exposicion de informacion sensible por mal diseno de control de acceso** (OWASP A01 - Broken Access Control / A05 - Security Misconfiguration).

El patron es:
1. El desarrollador crea un recurso sensible en una ruta "dificil de adivinar" (`/s3cr3t/`).
2. Para evitar que Google lo indexe, lo incluye en `robots.txt` con `Disallow:`.
3. Resultado: en vez de ocultar la ruta, la publica en texto plano en un archivo estandar que cualquiera conoce.

`robots.txt` es una convencion voluntaria para bots bien comportados. No es un mecanismo de autenticacion ni de autorizacion. Cualquier navegador o herramienta puede ignorarlo e ir directamente a la ruta.

---

## Paso a paso

### 1. Acceder al nivel 3

Abre el navegador o usa `curl`. Sustituye `<pass_natas3>` por la contrasena que obtuviste en el nivel anterior.

```bash
curl -u natas3:<pass_natas3> http://natas3.natas.labs.overthewire.org/
```

La pagina muestra el mensaje: *"There is nothing on this page"* y en el codigo fuente aparece la pista:

```html
<!-- No more information leaks!! Not even Google will find it this time... -->
```

La referencia a Google es la clave: el desarrollador uso `robots.txt` para ocultarlo.

---

### 2. Consultar robots.txt

```bash
curl -u natas3:<pass_natas3> http://natas3.natas.labs.overthewire.org/robots.txt
```

Respuesta esperada:

```
User-agent: *
Disallow: /s3cr3t/
```

La directiva `Disallow: /s3cr3t/` revela la ruta que el desarrollador queria mantener oculta.

---

### 3. Acceder directamente a la ruta prohibida

```bash
curl -u natas3:<pass_natas3> http://natas3.natas.labs.overthewire.org/s3cr3t/
```

El servidor devuelve el listado del directorio (directory listing habilitado), que muestra un archivo `users.txt`.

---

### 4. Leer users.txt

```bash
curl -u natas3:<pass_natas3> http://natas3.natas.labs.overthewire.org/s3cr3t/users.txt
```

Salida esperada:

```
natas4:<pass_natas4>
```

Esa es la contrasena del siguiente nivel.

---

## Por que funciona

`robots.txt` opera sobre el **protocolo de exclusion de robots** (RFC informal, no un estandar de seguridad). Los motores de busqueda como Google respetan la directiva `Disallow` por convencion para no indexar esas rutas. Sin embargo:

- El archivo es publico y accesible sin autenticacion por convencion historica.
- No existe ningun mecanismo tecnico que impida a un humano o a un bot malicioso leer `robots.txt` y luego acceder directamente a las rutas listadas.
- En la practica, `robots.txt` actua como un **directorio inverso**: anuncia exactamente las rutas que el administrador considera sensibles.

El recurso `/s3cr3t/users.txt` tampoco tiene control de acceso propio: cualquiera que conozca la URL puede descargarlo con la autenticacion Basic del nivel (que es compartida por todo el dominio de natas).

---

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| `401 Unauthorized` al acceder a `/s3cr3t/` | Falta la autenticacion Basic del nivel | Incluye `-u natas3:<pass_natas3>` en el comando `curl` |
| No ves el listado de directorio, solo una pagina en blanco | El navegador no muestra HTML de listado simple | Revisa el codigo fuente (Ctrl+U) o usa `curl` |
| Buscas `robots.txt` en la raiz del dominio `natas.labs.overthewire.org` | Cada nivel tiene su propio subdominio | La URL correcta empieza por `natas3.natas.labs...` |
| Copias la contrasena con espacios o salto de linea | Error habitual al copiar desde terminal | Copia solo los caracteres visibles; con `curl` puedes redirigir la salida a un archivo y revisarla |

---

## Pasar al siguiente nivel

Con `<pass_natas4>` obtenida, accede al nivel 4:

```bash
curl -u natas4:<pass_natas4> http://natas4.natas.labs.overthewire.org/
```

O en el navegador: `http://natas4.natas.labs.overthewire.org/` con las credenciales `natas4` / `<pass_natas4>`.

---

## Conexiones

- [[Natas/00_README]]
- [[MOC_Ciberseguridad]]
- [[04-seguridad-web-owasp]]
- [[13-herramientas-en-detalle]]
