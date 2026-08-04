---
title: Sesión 9 — Seguridad y secretos
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 9 Seguridad, API key y secretos]
---

# Sesión 9 — Seguridad y secretos

> **Objetivo**: que **solo quien tenga la clave** pueda mandar comandos al LED, y **sacar los
> secretos del código** para no exponerlos. Hasta hoy cualquiera en la red podía encenderlo.
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: un `POST /led` sin la cabecera correcta devuelve `401`
> (rechazado); con la cabecera `X-API-Key` correcta, funciona. La clave vive en un fichero
> `.env` que **no está en git**.

## Requisitos previos

- Haber completado hasta [[08-tiempo-real-con-websockets]]: WebSockets funcionando, `POST /led`
  cambia el estado y hace broadcast.
- Entorno activado: `source .venv/bin/activate`.
- Tener a mano la terminal con `curl` (se usó en [[02-curl-y-los-verbos-http]]).

## El checkpoint de hoy

```bash
source .venv/bin/activate
./bin/sesion.sh 9            # te coloca en 'sesion9-inicio'
```

El esqueleto trae `python-dotenv` ya en las dependencias y la carga del `.env` al arrancar.
Quedan **dos `# TODO`**: escribir la **dependencia de autenticación** (compara la cabecera con
el secreto) y **aplicarla** al `POST /led`.

```python
# servidor/auth.py  (estado de partida, sesion9-inicio)
import os
from fastapi import Security
from fastapi.security import APIKeyHeader

cabecera_api_key = APIKeyHeader(name="X-API-Key")

# TODO (Sesión 9): función verificar_clave(...) que compare la cabecera
#                  con os.environ["API_KEY"] y lance 401 si no coincide
```

## Teoría

### 1. Superficie de ataque

> La **superficie de ataque** es todo lo que un atacante puede tocar de tu sistema.

Desde la [[04-salir-del-localhost-la-red-local]], el servidor escucha en la LAN. Eso significa
que **cualquier dispositivo de la red** —no solo el alumno— puede mandarle peticiones. Hoy,
sin protección, **cualquiera puede encender el LED**. Cada endpoint expuesto es parte de la
superficie de ataque.

```
   ANTES (localhost)              AHORA (LAN, Sesión 4+)
   solo yo ──► mi server         yo ───┐
                                  vecino┤──► mi server  (¡todos pueden!)
                                  móvil ┘
```

No hay que asustarse, hay que **poner una puerta con llave** en lo que cambia el estado.

### 2. Autenticación vs autorización

Se confunden constantemente. Dos preguntas distintas:

| | Pregunta | Ejemplo |
|---|---|---|
| **Autenticación** (authn) | *¿Quién eres?* ¿Tienes credencial válida? | "enséñame la clave" |
| **Autorización** (authz) | *¿Qué te dejo hacer?* ¿Tienes permiso para esto? | "tú puedes leer pero no borrar" |

Hoy hacemos **autenticación** sencilla: o tienes la clave (entras) o no (fuera). No hay roles
ni permisos finos; eso sería autorización, materia más avanzada.

### 3. Una API key en una cabecera

El mecanismo más simple: una **clave secreta compartida**. El cliente la manda en una
**cabecera HTTP** llamada `X-API-Key`, y el servidor comprueba que coincide.

```
   CLIENTE                                    SERVIDOR
     │  POST /led                               │
     │  X-API-Key: CAMBIA_ESTA_CLAVE  ────────► │  ¿coincide con la mía?
     │                                          │   sí → procesa
     │  ◄──────────── 200 OK ─────────────────  │   no → 401
```

Va en una cabecera (no en la URL) para que **no quede en logs ni en el historial del
navegador**. Es básico pero suficiente para un proyecto en LAN. Más mecanismos (tokens, OAuth)
en [[MOC_Ciberseguridad]].

### 4. NUNCA hardcodear un secreto

La tentación es escribir la clave en el código:

```python
# ☠️ MAL
API_KEY = "CAMBIA_ESTA_CLAVE"   # en el código → acaba en git → la ve todo el mundo
```

Problema: el código **se versiona en git** y, si el repo se comparte o publica, **la clave se
filtra**. Los secretos no son código: son **configuración** que cambia por máquina y debe
quedarse fuera del repositorio.

### 5. Variables de entorno y ficheros `.env`

Una **variable de entorno** es un valor que vive en el sistema, fuera del código. El programa
la lee con `os.environ["API_KEY"]`. Así, el mismo código corre con claves distintas en
distintas máquinas sin tocar una línea.

Para no exportarlas a mano cada vez, se usa un fichero **`.env`** (texto plano,
`CLAVE=valor`) y la librería **`python-dotenv`** lo carga al arrancar:

```bash
# .env  (NO se versiona)
API_KEY=CAMBIA_ESTA_CLAVE
```

```python
from dotenv import load_dotenv
load_dotenv()                       # mete lo del .env en os.environ
```

### 6. El patrón `.env` + `.env.example`

| Fichero | ¿Va a git? | Contiene |
|---|---|---|
| `.env` | **NO** (en `.gitignore`) | la clave **real** |
| `.env.example` | **SÍ** | la **plantilla**, con placeholders, sin valores reales |

El `.env.example` documenta *qué* variables hacen falta sin revelar sus valores. Quien clona
el repo lo copia a `.env` y rellena su clave.

```bash
# .env.example  (SÍ se versiona — solo placeholders)
API_KEY=CAMBIA_ESTA_CLAVE
```

```
   .gitignore
   ───────────
   .env            ◄── la real, ignorada
   *.db
```

### 7. Si subes una clave a git, se queda en el historial

Esto hay que recalcarlo. Git **guarda toda la historia**. Si haces commit de un `.env` con la
clave real y luego la borras en otro commit, **la clave sigue en el historial** y cualquiera
con acceso al repo puede recuperarla de un commit antiguo.

```
   commit A: añade .env con la clave   ◄── la clave está AQUÍ para siempre
   commit B: "ups, borro el .env"      ◄── borrar ahora NO la elimina del historial
```

Por eso la regla es **no dejar que entre nunca** (`.gitignore` desde el principio). Si ya
entró, no basta con borrarla: hay que **rotar la clave** (cambiarla por una nueva) y, si hace
falta, limpiar el historial. Detalles de `.gitignore` e historial en [[MOC_GitLab]].

## Manos a la obra

**1) Colocarse en el checkpoint:**

```bash
source .venv/bin/activate
./bin/sesion.sh 9
```

**2) Escribir la dependencia de autenticación:**

```python
# servidor/auth.py  (solución)
import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

cabecera_api_key = APIKeyHeader(name="X-API-Key")

def verificar_clave(clave: str = Security(cabecera_api_key)):
    if clave != os.environ["API_KEY"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave API no valida",
        )
    return clave
```

- `APIKeyHeader(name="X-API-Key")` le dice a FastAPI que lea esa cabecera.
- `Security(...)` la inyecta como argumento (es como `Depends`, pero para seguridad).
- Si no coincide, `401 Unauthorized`. Si coincide, deja pasar.

**3) Proteger `POST /led` aplicando la dependencia:**

```python
# servidor/main.py  (solución, fragmento)
from fastapi import Depends
from servidor.auth import verificar_clave

@app.post("/led", dependencies=[Depends(verificar_clave)])
async def cambiar_led(comando: ComandoLed):
    estado_actual = comando.encendido
    await gestor.broadcast({"encendido": estado_actual})
    return {"encendido": estado_actual}
```

`dependencies=[Depends(verificar_clave)]` ejecuta la comprobación **antes** de entrar a la
función. Si falla, ni se llega a tocar el LED. (Se protege `POST /led` —cambia estado—; `GET`
de lectura puede quedar abierto.)

**4) Configurar los secretos:**

```bash
echo "API_KEY=CAMBIA_ESTA_CLAVE" > .env          # tu clave real (ficticia aquí)
echo "API_KEY=CAMBIA_ESTA_CLAVE" > .env.example  # plantilla versionada
echo ".env" >> .gitignore                         # que la real NUNCA entre a git
```

> En clase, la clave de ejemplo es `CAMBIA_ESTA_CLAVE` a propósito: un placeholder obvio. En
> un proyecto real generarías una clave larga y aleatoria, pero **eso jamás se escribe en
> notas, docs ni en el `.env.example`**.

**5) Probar el rechazo y el acceso:**

```bash
uvicorn servidor.main:app --reload

# Sin cabecera → 401 rechazado:
curl -i -X POST http://127.0.0.1:8000/led \
  -H "Content-Type: application/json" -d '{"encendido": true}'
# → HTTP/1.1 401 Unauthorized

# Con la cabecera correcta → funciona:
curl -i -X POST http://127.0.0.1:8000/led \
  -H "Content-Type: application/json" \
  -H "X-API-Key: CAMBIA_ESTA_CLAVE" \
  -d '{"encendido": true}'
# → HTTP/1.1 200 OK
```

El primero rebota con `401`; el segundo enciende el LED. La puerta tiene llave.

> Recuerda actualizar el panel web y el cliente Pi para que **manden** la cabecera `X-API-Key`
> en sus peticiones a `POST /led`, o dejarán de funcionar (y eso enseña que la protección
> realmente actúa).

## El muro

La API ya está protegida. Pero alguien plantea la siguiente fragilidad: *"vale, pero ¿qué pasa
si se cae el wifi, o apago el servidor justo mientras la Raspberry le está preguntando? El
cliente se queda colgado o **revienta con una excepción**. No aguanta un fallo."*.

Cierto: falta **resiliencia**. Eso es la [[10-resiliencia-y-manejo-de-errores]].

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| La clave aparece en `git log` / en el repo | Se hizo commit del `.env` (o se hardcodeó) | `.env` en `.gitignore` desde el inicio; si ya entró, **rotar la clave** y limpiar historial |
| `KeyError: 'API_KEY'` al arrancar | El `.env` no se cargó o no existe | `load_dotenv()` antes de leer; crear el `.env` con `API_KEY=...` |
| Devuelve 401 cuando debería dejar pasar | Cabecera mal escrita o clave que no coincide | Cabecera exacta `X-API-Key`; verificar que el valor coincide con el `.env` |
| Confundir 401 y 403 | No distinguir authn de authz | `401` = no autenticado (no sé quién eres); `403` = autenticado pero sin permiso |
| La clave se ve en los logs del servidor | Se loguea la cabecera o la URL con el secreto | No registrar cabeceras de auth; mandar la clave por cabecera, nunca en la URL |
| El panel/Pi dejan de funcionar | No mandan la cabecera `X-API-Key` | Añadir la cabecera en sus peticiones a `POST /led` |

## Guion de la sesión

| Tramo | Qué hacer |
|---|---|
| **0–10** | Demostrar el problema: desde otro dispositivo de la red, `POST /led` enciende el LED sin permiso. "Esto hay que cerrarlo." |
| **10–35** | Teoría: superficie de ataque, authn vs authz, API key en cabecera, por qué NUNCA hardcodear, variables de entorno y `.env`. |
| **35–45** | **El punto clave**: si subes una clave a git, se queda en el historial. `.env` ignorado + `.env.example` versionado. |
| **45–80** | `./bin/sesion.sh 9`, escribir la dependencia de auth, protegerla en `POST /led`, crear `.env`/`.env.example`, `.gitignore`. |
| **80–88** | Probar 401 sin clave y 200 con clave. Actualizar panel/Pi para mandar la cabecera. |
| **88–90** | **El muro**: "¿y si se cae el wifi mientras la Pi pregunta?" → presentar Sesión 10. |

## Conexiones

- [[08-tiempo-real-con-websockets]] — sesión anterior: el push que ahora protegemos
- [[10-resiliencia-y-manejo-de-errores]] — sesión siguiente: aguantar fallos de red
- [[04-salir-del-localhost-la-red-local]] — exponer en la LAN amplia la superficie de ataque
- [[02-curl-y-los-verbos-http]] — cabeceras HTTP y códigos de estado (401/403)
- [[MOC_Ciberseguridad]] — autenticación, secretos y superficie de ataque
- [[MOC_GitLab]] — `.gitignore` y por qué un secreto se queda en el historial
- [[MOC_Programacion]] — área padre
