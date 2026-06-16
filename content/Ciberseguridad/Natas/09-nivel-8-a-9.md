---
title: Natas Nivel 8 a 9
date: 2026-06-14
tags: [ciberseguridad, web, owasp, natas, encoding, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Natas 8, Natas nivel 8, natas8]
---

# Natas Nivel 8 a 9

Nivel oficial: http://natas8.natas.labs.overthewire.org

Este nivel es un laboratorio legal y autorizado de OverTheWire — nunca apliques estas tecnicas fuera de entornos de practica con permiso explicito. El reto extiende el patron de Natas 6: en lugar de comparar directamente un secreto en texto plano, el codigo PHP aplica una cadena de transformaciones antes de comparar. Tu tarea es invertir esa cadena.

## Objetivo

Recuperar la contrasena de `natas9` encontrando el `$secret` original a partir del `$encodedSecret` visible en el codigo fuente.

## Que aprendes

| Concepto / Comando | Para que sirve |
|---|---|
| `View Source` / `?source` | Leer el codigo PHP del reto directamente en el navegador |
| `hex2bin()` | Convierte una cadena hexadecimal a bytes binarios |
| `strrev()` | Invierte el orden de los caracteres de una cadena |
| `base64_decode()` | Decodifica Base64 a texto plano |
| `php -r '...'` | Ejecutar PHP en una linea desde la terminal |

### Concepto clave

**Codificar/ofuscar NO es cifrar.** Una funcion de encoding (Base64, hex, rot13...) transforma datos en una representacion diferente, pero el proceso es completamente reversible si conoces el algoritmo — y aqui el algoritmo esta visible en el propio codigo fuente. La seguridad por oscuridad falla en cuanto el atacante lee el codigo.

La cadena de transformaciones aplicada al secreto es:

```
encodedSecret = bin2hex( strrev( base64_encode( secret ) ) )
```

Para invertirla basta con aplicar las funciones inversas en orden contrario:

```
secret = base64_decode( strrev( hex2bin( encodedSecret ) ) )
```

## Paso a paso

1. **Autenticarse en el nivel anterior.** Conectarse a `natas8` con las credenciales obtenidas en el nivel 7:

```bash
# Usuario: natas8
# Contrasena: <pass_natas8>
# URL:       http://natas8.natas.labs.overthewire.org
```

2. **Leer el codigo fuente.** Abrir en el navegador:

```
http://natas8.natas.labs.overthewire.org/index.php?source
```

   Localizar las dos variables clave:

```php
$encodedSecret = "3d3d516343746d4d6d6c315669563362";

function encodeSecret($secret) {
    return bin2hex(strrev(base64_encode($secret)));
}
```

3. **Invertir la transformacion.** Con el valor del `$encodedSecret` visible, ejecutar el one-liner PHP en tu terminal:

```bash
php -r 'echo base64_decode(strrev(hex2bin("3d3d516343746d4d6d6c315669563362")));'
```

   La salida es el secreto original en texto plano. (El valor `3d3d51...` es el que aparece en el codigo fuente del reto; si el servidor lo cambia en alguna edicion futura, sustituyelo por el que veas.)

4. **Enviar el secreto.** Pegar la salida del comando en el campo del formulario y hacer clic en "Submit".

5. **Recoger la contrasena.** El servidor muestra la contrasena de `natas9`:

```
The password for natas9 is: <pass_natas9>
```

## Por que funciona

El codigo compara `encodeSecret($secret) === $encodedSecret`. Si inviertes correctamente cada paso — `hex2bin`, luego `strrev`, luego `base64_decode` — obtienes exactamente el valor que `$secret` debe tener para que la igualdad sea verdadera. No hay nada criptografico aqui: ningun algoritmo de hashing (MD5, SHA-256) ni clave simetrica; solo una recodificacion que cualquiera puede deshacer conociendo el algoritmo, que ademas esta expuesto en el codigo.

## Errores comunes

| Error | Causa | Solucion |
|---|---|---|
| El one-liner no produce salida legible | Orden de funciones invertido | Respetar el orden exacto: `hex2bin` → `strrev` → `base64_decode` |
| `php: command not found` | PHP no esta instalado en la maquina local | Instalar (`sudo apt install php-cli`) o usar un interprete online de confianza |
| Copiar el `encodedSecret` con espacios extra | Seleccion manual en el navegador | Copiar solo la cadena entre comillas del codigo fuente |
| El formulario rechaza el secreto correcto | Se copio con salto de linea al final | `php -r` a veces no anade `\n`; si lo hace, ignorar el caracter final |

## Pasar al siguiente nivel

Conectarse a `natas9` con las credenciales recien obtenidas:

```
URL:      http://natas9.natas.labs.overthewire.org
Usuario:  natas9
Contrasena: <pass_natas9>
```

## Conexiones

- [[Natas/00_README]]
- [[MOC_Ciberseguridad]]
- [[04-seguridad-web-owasp]]
- [[13-herramientas-en-detalle]]
