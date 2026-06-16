---
title: Natas Nivel 4 a 5
date: 2026-06-14
tags: [ciberseguridad, web, owasp, natas, http-headers, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Natas4, Natas nivel 4, natas4 referer]
---

# Natas Nivel 4 a 5

Nivel oficial: http://natas4.natas.labs.overthewire.org/

Este nivel introduce la falsificacion de cabeceras HTTP desde el cliente. El servidor restringe el acceso basandose en la cabecera `Referer`, asumiendo que solo puede llegar trafico desde una URL concreta — un supuesto incorrecto con implicaciones de seguridad reales.

> Este wargame es un laboratorio legal y autorizado por OverTheWire. Practica estas tecnicas unicamente en entornos con permiso explicito.

---

## Objetivo

Acceder a la pagina de natas4 para que el servidor muestre la contrasena de natas5. El servidor rechaza la peticion si el `Referer` no es `http://natas5.natas.labs.overthewire.org/`.

---

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| Cabecera HTTP `Referer` | Indica al servidor desde que pagina viene la peticion |
| `curl -H 'Header: valor'` | Inyecta cabeceras arbitrarias en una peticion HTTP |
| `curl -u usuario:pass` | Autenticacion HTTP Basic desde la linea de comandos |
| Control de acceso basado en cabeceras | Patron de seguridad debil — el cliente controla el valor |

### Concepto clave

La cabecera `Referer` (escrita asi, con un solo 'r', por error historico en el RFC) es enviada por el navegador para informar al servidor de donde viene el usuario. Es un campo **completamente controlado por el cliente**: cualquiera puede enviar el valor que quiera.

Usarla como mecanismo de control de acceso cae en la categoria **OWASP A01:2021 - Broken Access Control**: la logica de autorizacion depende de datos que el atacante puede manipular libremente. El servidor nunca puede confiar en cabeceras que no ha generado el.

---

## Paso a paso

**1. Observa el mensaje de error**

Abre http://natas4.natas.labs.overthewire.org/ con credenciales `natas4 / <pass_natas4>`. El servidor responde algo similar a:

```
Access disallowed. You are visiting from "" while authorized users should come only from "http://natas5.natas.labs.overthewire.org/"
```

El campo entre comillas es el valor de tu cabecera `Referer` actual (vacio desde curl, o la pagina anterior desde el navegador).

**2. Envia la peticion con el Referer falsificado**

```bash
curl -u natas4:<pass_natas4> \
     -H 'Referer: http://natas5.natas.labs.overthewire.org/' \
     http://natas4.natas.labs.overthewire.org/
```

**3. Lee la respuesta**

El HTML devuelto contendra un mensaje de acceso concedido junto con la contrasena del siguiente nivel:

```
Access granted. The password for natas5 is <pass_natas5>
```

**4. (Alternativa con navegador)** Puedes usar la extension *ModHeader* (Chrome/Firefox) para sobreescribir el `Referer` sin salir del navegador. Util para explorar la respuesta HTML renderizada.

---

## Por que funciona

El servidor lee `$_SERVER['HTTP_REFERER']` (PHP) o el equivalente en su lenguaje, y compara el valor con la URL esperada. Esa variable refleja directamente la cabecera que manda el cliente: no hay firma, no hay token de sesion, no hay verificacion criptografica. Cualquier cliente puede poner el string que quiera.

El patron correcto para restringir acceso es la autenticacion de sesion (cookies firmadas, JWT, tokens OAuth) — mecanismos donde el servidor emite y verifica el token, no el cliente.

---

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| Sigue mostrando "Access disallowed" | URL del Referer mal escrita (falta `/` final, typo) | Copia exactamente `http://natas5.natas.labs.overthewire.org/` |
| `curl` pide contrasena interactiva | Se omitio `-u natas4:<pass>` o se uso solo `-u natas4` | Incluye la contrasena en el flag o dejala en blanco para que curl la pida |
| Respuesta en HTML crudo ilegible | Normal en curl; busca el string "password" con `grep` | `curl ... \| grep -i password` |
| Error de autenticacion 401 | Contrasena de natas4 incorrecta | Verificala en el nivel anterior (natas3) |

---

## Pasar al siguiente nivel

Usa la contrasena `<pass_natas5>` obtenida para acceder a:

- URL: http://natas5.natas.labs.overthewire.org/
- Usuario: `natas5`

---

## Conexiones

- [[Natas/00_README]]
- [[MOC_Ciberseguridad]]
- [[04-seguridad-web-owasp]]
- [[13-herramientas-en-detalle]]
