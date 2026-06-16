---
title: Natas Nivel 5 a 6
date: 2026-06-14
tags: [ciberseguridad, web, owasp, natas, cookies, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Natas nivel 5, Natas 5 a 6, natas-cookie-manipulation]
---

# Natas Nivel 5 a 6

> Página oficial del nivel: http://natas5.natas.labs.overthewire.org
> Marco: OverTheWire Natas es un wargame **legal y autorizado** diseñado para aprender seguridad web de forma ética. No es hacking malicioso.

---

## Objetivo

Acceder a `http://natas5.natas.labs.overthewire.org` y obtener la contraseña del nivel 6. El servidor responde con el mensaje *"Access disallowed. You are not logged in"* aunque hayas introducido las credenciales HTTP correctas (Basic Auth). Hay que identificar por qué el servidor cree que no estás autenticado y corregirlo.

---

## Qué aprendes

| Concepto / Comando | Para qué sirve |
|---|---|
| Cookie HTTP | Par clave-valor que el servidor envía al navegador para almacenar estado entre peticiones |
| DevTools → Application → Cookies | Inspeccionar y editar cookies en el navegador sin instalar nada |
| `curl -b 'clave=valor'` | Enviar una cookie concreta en una petición desde la terminal |
| `curl -u usuario:pass` | Autenticación HTTP Basic desde la terminal |
| Control de acceso basado en cookie de cliente | Anti-patrón de seguridad: el servidor delega la decisión de autorización en un valor que el cliente puede modificar libremente |

### Concepto clave: cookies como decisión de autorización

Las cookies son datos que el **cliente** almacena y envía al servidor en cada petición. El servidor puede escribirlas, pero no puede impedir que el usuario las lea o las modifique. Usar el valor de una cookie para decidir si alguien tiene acceso (sin verificarlo en servidor) es equivalente a preguntar *"¿eres mayor de edad?"* y fiarse de lo que responde el propio usuario.

La categoría de vulnerabilidad es **Broken Access Control** (OWASP A01:2021): el servidor asume que el estado de autorización es fiable cuando proviene del cliente.

---

## Paso a paso

### 1. Conectarse al nivel 5

Abre el navegador y navega a:

```
http://natas5.natas.labs.overthewire.org
```

El servidor pedirá autenticación HTTP Basic. Introduce:

- Usuario: `natas5`
- Contraseña: `<pass_natas5>` (obtenida al resolver el nivel 4)

Verás el mensaje:

```
Access disallowed. You are not logged in
```

---

### 2. Inspeccionar las cookies

**Opción A — DevTools del navegador (recomendada para entender el flujo)**

1. Abre DevTools: `F12` o `Ctrl+Shift+I`.
2. Ve a la pestaña **Application** (Chrome/Edge) o **Storage** (Firefox).
3. En el panel izquierdo, despliega **Cookies** y selecciona la URL del nivel.
4. Verás una cookie llamada `loggedin` con valor `0`.
5. Haz doble clic sobre el valor `0` y cámbialo a `1`.
6. Recarga la página (`F5`).

El servidor ahora lee `loggedin=1` y muestra la contraseña del nivel 6.

**Opción B — `curl` desde la terminal (reproducible y scriptable)**

```bash
curl -u natas5:<pass_natas5> \
     -b 'loggedin=1' \
     http://natas5.natas.labs.overthewire.org/
```

Desglose:

- `-u natas5:<pass_natas5>` — autenticación HTTP Basic.
- `-b 'loggedin=1'` — envía la cookie `loggedin` con valor `1` en la cabecera `Cookie:`.

La respuesta contendrá la contraseña de `natas6` en el HTML devuelto.

---

### 3. Verificar la cabecera de respuesta (opcional, didáctico)

Para ver exactamente qué cookie establece el servidor en la respuesta original (antes de modificarla):

```bash
curl -u natas5:<pass_natas5> \
     -v \
     http://natas5.natas.labs.overthewire.org/ 2>&1 | grep -i 'set-cookie\|cookie'
```

Verás algo como:

```
< Set-Cookie: loggedin=0; path=/
```

Eso confirma que el servidor emite `loggedin=0` y luego confía en que el cliente lo devuelva sin modificar.

---

## Por qué funciona

El servidor establece la cookie `loggedin=0` cuando el usuario llega sin sesión activa. En cada petición posterior, lee ese valor de la cabecera `Cookie:` y lo usa directamente para decidir el acceso. No hay ninguna verificación en servidor (firma criptográfica, sesión en base de datos, token opaco) que impida que el cliente cambie el valor de `0` a `1`.

El patrón seguro es que el servidor **nunca confíe en datos que el cliente puede alterar** sin verificación. Las alternativas correctas son:

- **Cookie de sesión opaca**: el servidor almacena el estado (autenticado/no) en su propio almacén (BD, memoria, Redis) y la cookie solo contiene un identificador aleatorio e impredecible.
- **Cookie firmada / JWT**: el servidor firma criptográficamente el contenido; si el cliente altera el valor, la firma no coincide y el servidor rechaza la petición.

---

## Errores comunes

- **Se recarga la página y el mensaje no cambia**: el navegador puede haber restaurado la cookie original. Edítala de nuevo en DevTools y recarga sin caché (`Ctrl+Shift+R`).
- **`curl` devuelve error 401**: las credenciales Basic Auth están mal. Asegúrate de usar exactamente `natas5` como usuario y la contraseña correcta del nivel 4.
- **`curl` devuelve el mensaje "not logged in" aun con `-b 'loggedin=1'`**: verifica que no haya espacios extraños en la cadena de la cookie y que el flag sea `-b` (minúscula), no `-B`.
- **DevTools no muestra la pestaña Application**: en Firefox se llama **Storage**; el flujo es el mismo.

---

## Pasar al siguiente nivel

La página te mostrará la contraseña de `natas6`. Guárdala y conéctate al nivel 6:

```
http://natas6.natas.labs.overthewire.org
```

- Usuario: `natas6`
- Contraseña: `<pass_natas6>`

---

## Conexiones

- [[Natas/00_README]]
- [[MOC_Ciberseguridad]]
- [[04-seguridad-web-owasp]]
- [[13-herramientas-en-detalle]]
- Página oficial del nivel: http://natas5.natas.labs.overthewire.org
- OWASP A01:2021 Broken Access Control: https://owasp.org/Top10/A01_2021-Broken_Access_Control/
- MDN — HTTP cookies: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
