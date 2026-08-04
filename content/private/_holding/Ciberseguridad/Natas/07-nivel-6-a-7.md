---
title: Natas Nivel 6 a 7
date: 2026-06-14
tags: [ciberseguridad, web, owasp, natas, lfi, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Natas nivel 6, Natas 6 a 7, natas-include-secret]
---

# Natas Nivel 6 a 7

Nivel oficial: https://overthewire.org/wargames/natas/natas7.html

Natas es un wargame web **legal y autorizado** de OverTheWire; cada nivel es un entorno de laboratorio aislado diseñado expresamente para practicar hacking ético. No apliques estas técnicas fuera de entornos de práctica o sin permiso explícito.

El reto presenta un formulario que pide un "secret". El código fuente revela que el secret se importa desde un fichero externo. El error de diseño: ese fichero es directamente accesible por URL.

---

## Objetivo

Leer el secret almacenado en el fichero `includes/secret.inc` accediendo a él directamente por URL, e introducirlo en el formulario para obtener la contraseña de natas7.

---

## Qué aprendes

| Concepto / Herramienta | Para qué sirve |
|---|---|
| `View sourcecode` (enlace en la página) | Ver el código PHP del nivel sin herramientas externas |
| `include` de PHP | Cómo PHP incrusta ficheros externos en tiempo de ejecución |
| Navegación directa a rutas de inclusión | Acceder por URL a ficheros `.inc` expuestos en el webroot |
| Inspección de respuesta HTTP | Confirmar el contenido del fichero aunque el servidor no lo renderice como HTML |

### Concepto clave: ficheros de inclusión expuestos en el webroot

La categoría de vulnerabilidad es **exposición de información por recursos accesibles públicamente** (OWASP A05 – Security Misconfiguration / A01 – Broken Access Control).

El patrón es sencillo:

1. La aplicación usa `include 'includes/secret.inc'` para cargar datos sensibles.
2. El fichero vive dentro del `webroot` (la carpeta servida por el servidor HTTP).
3. No existe ningún control de acceso sobre esa ruta: el servidor web la sirve como cualquier otro recurso estático.

Resultado: cualquiera que conozca (o adivine) la ruta puede hacer una petición GET y leer el contenido.

Esto se distingue de un LFI clásico (Local File Inclusion) en que aquí **no se inyecta ninguna ruta** — el fichero simplemente está mal ubicado o mal protegido. Es la forma más básica de exposición de secretos en aplicaciones PHP.

---

## Paso a paso

### 1. Autenticarse en el nivel 6

Abre en el navegador:

```
http://natas6.natas.labs.overthewire.org/
```

El navegador pedirá autenticación HTTP básica. Usa:

- Usuario: `natas6`
- Contraseña: `<pass_natas6>` (la obtenida al resolver el nivel 5)

### 2. Examinar el código fuente del nivel

En la página verás un formulario con un campo de texto y un enlace "View sourcecode". Haz clic en él. El servidor devuelve el PHP del nivel; busca la línea de inclusión:

```php
<?php
include "includes/secret.inc";

if(array_key_exists("submit", $_POST)) {
    if($secret == $_POST['secret']) {
        print "Access granted! The password for natas7 is <censored>";
    } else {
        print "Wrong secret";
    }
}
?>
```

La variable `$secret` se define en `includes/secret.inc`. La aplicación compara directamente lo que envías con esa variable — sin hashing, sin ofuscación.

### 3. Acceder directamente al fichero de inclusión

Construye la URL del fichero sumando la ruta relativa al origen del nivel:

```
http://natas6.natas.labs.overthewire.org/includes/secret.inc
```

Abre esa URL en el navegador (con las mismas credenciales HTTP básicas de natas6). El servidor devuelve el contenido del fichero. Puede que el navegador muestre una página en blanco porque el PHP se ejecuta y no imprime nada visible, pero el secret está en el código fuente de la respuesta.

Pulsa `Ctrl+U` (o "Ver código fuente de la página") para ver el contenido raw. Encontrarás algo como:

```php
<?php
$secret = "<secret_natas6>";
?>
```

### 4. Enviar el secret en el formulario

Vuelve a `http://natas6.natas.labs.overthewire.org/`, pega el valor de `<secret_natas6>` en el campo "Input secret" y pulsa "Submit". La respuesta mostrará:

```
Access granted! The password for natas7 is <pass_natas7>
```

Guarda `<pass_natas7>` para el nivel siguiente.

---

## Por qué funciona

El servidor web sirve **todo lo que está bajo el webroot** a menos que haya una regla explícita que lo prohíba (directiva `Deny` en Apache, bloque `location` en nginx, permisos de sistema de ficheros, etc.). Los ficheros `.inc` de PHP son texto plano desde el punto de vista del servidor HTTP; si no existe una regla que los bloquee, se sirven como cualquier `.txt`.

El diseño correcto sería guardar los secretos **fuera del webroot** (por ejemplo en `/etc/natas/secret.inc`) o proteger la ruta con autenticación/autorización a nivel de servidor web.

---

## Errores comunes

- **La página devuelve blanco y crees que no hay nada**: el PHP se ejecuta pero no imprime nada. Usa `Ctrl+U` para ver el código fuente de la respuesta — el secret está ahí como literal en el código PHP.
- **"Wrong secret" aunque copias el valor**: posibles espacios o saltos de línea en el copy-paste. Copia solo los caracteres entre las comillas, sin incluir `$secret = "` ni `";`.
- **Olvidas las credenciales HTTP básicas al navegar a la URL del `.inc`**: la ruta `/includes/secret.inc` también está bajo el mismo dominio protegido; el navegador debería reutilizar las credenciales si ya autenticaste antes, pero si abre una pestaña nueva tendrás que volver a introducirlas.
- **Buscas el fichero en la raíz del servidor**: la ruta es relativa al directorio del nivel (`natas6`), no al servidor completo. La URL correcta incluye el subdominio `natas6.natas.labs.overthewire.org`.

---

## Pasar al siguiente nivel

Con `<pass_natas7>` en mano, abre:

```
http://natas7.natas.labs.overthewire.org/
```

Autentícate con usuario `natas7` y contraseña `<pass_natas7>`.

---

## Conexiones

- [[Natas/00_README]]
- [[MOC_Ciberseguridad]]
- [[04-seguridad-web-owasp]]
- [[13-herramientas-en-detalle]]
- Página oficial: https://overthewire.org/wargames/natas/natas7.html
