---
title: Sesión 11 — Empaquetar con Docker
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 11 Docker, Contenedores del Servidor]
---

# Sesión 11 — Empaquetar con Docker

> **Objetivo**: meter el servidor en un **contenedor** para que arranque **igual en cualquier
> máquina**, sin instalar Python ni dependencias a mano. Se acabó el "en mi máquina funciona".
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: construyes una **imagen** con `docker build`, lanzas el
> servidor con un solo `docker run -p 8000:8000`, y desde otra máquina (o la Pi) llamas a
> `curl http://192.168.1.50:8000/led` y responde **exactamente igual** que cuando corría con
> `uvicorn` a pelo. Pero ahora no hay venv ni `pip install` por medio.

## Requisitos previos

- Sesiones 1–10 hechas: tienes el servidor completo y resiliente, con `.env`, `requirements.txt`
  y todo arrancando con `uvicorn` ([[10-resiliencia-y-manejo-de-errores]]).
- Docker instalado en el portátil (en la sala se prepara antes; comprobar con `docker --version`).
- Tener clara la diferencia entre `127.0.0.1` y `0.0.0.0` ([[04-salir-del-localhost-la-red-local]]):
  hoy vuelve a ser clave.

## El checkpoint de hoy

```bash
./bin/sesion.sh 11             # esqueleto: un Dockerfile a medias
./bin/sesion.sh 11 --solucion  # si te atascas
```

El `# TODO` de hoy **no es código Python**: es escribir el `Dockerfile` (la receta de la
imagen) y un `.dockerignore`. El servidor FastAPI no se toca.

## Teoría

### El problema "en mi máquina funciona"

Tu servidor arranca en tu portátil porque tú, durante 10 sesiones, fuiste instalando: una
versión concreta de Python, un venv, FastAPI, Uvicorn, `requests`… Si le pasas el código a un
compañero, le falta todo eso. Si lo llevas a una máquina nueva, a reinstalar y rezar por las
versiones. Eso **no es repetible**. Un contenedor resuelve esto empaquetando *el código + sus
dependencias + el Python correcto* en una sola caja que arranca igual en cualquier sitio.

### ¿Qué es un contenedor? (y en qué se diferencia de una VM)

A alto nivel: un contenedor es **tu app más todo lo que necesita para correr**, aislada del
resto de la máquina, pero **compartiendo el núcleo (kernel) del sistema anfitrión**. No es un
ordenador entero simulado.

```
   MÁQUINA VIRTUAL (pesada)              CONTENEDOR (ligero)
   ┌───────────────────────┐            ┌───────────────────────┐
   │ tu app                │            │ tu app                │
   │ librerías             │            │ librerías             │
   │ SISTEMA OPERATIVO     │ ← cada VM  │ (NADA de SO completo) │
   │ entero (GBs)          │   trae el  └───────────┬───────────┘
   ├───────────────────────┤   suyo       comparte  │ kernel del host
   │ Hypervisor            │            ┌───────────▼───────────┐
   ├───────────────────────┤            │  Docker Engine        │
   │ Sistema anfitrión     │            │  Sistema anfitrión    │
   └───────────────────────┘            └───────────────────────┘
   arranca en minutos, GBs              arranca en segundos, MBs
```

| | Máquina virtual | Contenedor |
|---|---|---|
| Qué incluye | un SO completo + tu app | solo tu app + sus dependencias |
| Peso | gigabytes | megabytes |
| Arranque | minutos | segundos |
| Aislamiento | total (otro kernel) | a nivel de proceso (comparte kernel) |

Para nuestro objetivo (un servidor que arranca igual en todos lados) el contenedor es justo
lo que necesitamos: ligero y reproducible.

### Imagen vs contenedor (la confusión clásica)

- Una **imagen** es la *plantilla congelada*: el resultado de seguir la receta del `Dockerfile`.
  Es como una clase, o una foto del disco. No corre; está guardada.
- Un **contenedor** es una *instancia en marcha* de una imagen: lo que aparece cuando haces
  `docker run`. Es como un objeto de esa clase, o la película de esa foto.

```
   Dockerfile  ──docker build──►  IMAGEN  ──docker run──►  CONTENEDOR (corriendo)
   (la receta)                  (plantilla)              (instancia viva)
```

De una imagen puedes arrancar muchos contenedores idénticos.

### El `Dockerfile`: la receta de la imagen

Un fichero de texto, instrucción por línea, que describe cómo construir la imagen:

| Instrucción | Qué hace | Cuándo se ejecuta |
|---|---|---|
| `FROM` | imagen base de la que partimos | build |
| `WORKDIR` | carpeta de trabajo dentro de la imagen | build |
| `COPY` | copia ficheros del proyecto a la imagen | build |
| `RUN` | ejecuta un comando **al construir** (instalar deps) | **build** |
| `CMD` | el comando que arranca **al lanzar** el contenedor | **run** |

```dockerfile
FROM python:3.12-slim          # base: Python ya instalado, versión "slim" (ligera)
WORKDIR /app                   # trabajamos en /app dentro de la imagen
COPY requirements.txt .        # copiamos primero las deps (aprovecha la caché)
RUN pip install --no-cache-dir -r requirements.txt   # se instalan AL CONSTRUIR
COPY . .                       # ahora el resto del código
CMD ["uvicorn", "servidor.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`RUN` vs `CMD` es la confusión más típica: `RUN pip install` ocurre **una vez, al construir
la imagen** (queda "horneado" dentro). `CMD uvicorn` es lo que se ejecuta **cada vez que
arrancas un contenedor**. Construir ≠ arrancar.

### Mapeo de puertos y por qué `0.0.0.0` (otra vez)

El contenedor tiene su propia red interna, aislada. Aunque dentro escuche en el `8000`, desde
fuera **no llegas** a menos que **mapees** el puerto del host al del contenedor:

```
   docker run -p 8000:8000 ...
                │    └── puerto DENTRO del contenedor
                └─────── puerto en TU máquina (host)

   tu máquina :8000  ─────►  contenedor :8000  ─────►  uvicorn en 0.0.0.0:8000
        (host)                  (interno)
```

Y aquí vuelve la lección de la Sesión 4: dentro del contenedor uvicorn **debe escuchar en
`0.0.0.0`**, no en `127.0.0.1`. Si escucha en `127.0.0.1`, solo se oye a sí mismo *dentro* del
contenedor; el mapeo `-p` no le llega y desde fuera ves `Connection refused`. Por eso el `CMD`
lleva `--host 0.0.0.0`.

### `.dockerignore`: qué NO meter en la imagen

Igual que `.gitignore`, pero para la imagen. Sin él, `COPY . .` mete *todo*: el venv (cientos
de MB inútiles), la base de datos, los logs y —peligroso— tu `.env` con secretos. Lo excluimos:

```
.venv/
__pycache__/
*.db
*.log
.env
.git/
```

El `.env` lo pasaremos al arrancar (`--env-file`), **no** horneado en la imagen. Una imagen con
secretos dentro es una imagen que no puedes compartir.

### Por qué esto da reproducibilidad

La imagen fija *exactamente* la versión de Python, las dependencias y el código. `docker build`
en tu portátil y en la máquina de un compañero produce el **mismo** entorno. Se acabó el "a mí
me va y a ti no": la caja es idéntica en todos lados.

### Si algún día saliera de la LAN (solo de pasada)

Una imagen se puede subir a un **registry** (un repositorio de imágenes) y desde ahí
descargarla y arrancarla en un servidor en la nube. Es el puente natural hacia desplegar fuera
de casa. **Nosotros NO lo hacemos**: el curso vive entero en la red local, `192.168.1.x`, sin
internet. Solo para que sepas a dónde escalaría → [[MOC_GCP]].

## Manos a la obra

### 1. Escribir el `Dockerfile` (el `# TODO`)

En la raíz del proyecto del servidor, completa el `Dockerfile` del checkpoint:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "servidor.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Escribir el `.dockerignore`

En la misma carpeta, crea `.dockerignore`:

```
.venv/
__pycache__/
*.db
*.log
.env
.git/
```

### 3. Construir la imagen

```bash
docker build -t curso-servidor .
#            └── nombre (tag) de la imagen        └── el "." es el contexto (esta carpeta)
```

La primera vez tarda (descarga la base y `pip install`); las siguientes usan caché y van
rapidísimo.

### 4. Arrancar el contenedor

```bash
docker run -p 8000:8000 --env-file .env curso-servidor
#          └ mapea el puerto       └ pasa los secretos SIN hornearlos en la imagen
```

Verás los logs de uvicorn igual que cuando lo lanzabas a mano.

### 5. Comprobar que responde IGUAL

Desde otra terminal (o desde la máquina de un compañero / la Pi):

```bash
curl http://192.168.1.50:8000/led
# {"encendido": false}        ← idéntico a antes, pero ahora sale de un contenedor
```

Mismo comportamiento, mismo `curl`, misma respuesta. La diferencia es que ya **no dependes de
tu venv**: la app va dentro de una caja portable.

Comandos útiles para ver qué pasa:

```bash
docker ps                 # contenedores corriendo
docker images             # imágenes construidas
docker logs <id>          # logs del contenedor
docker stop <id>          # pararlo
```

## Cierre

El servidor ya es **portable**: una sola imagen que arranca igual en tu portátil, en el de un
compañero o en cualquier máquina con Docker, sin tocar Python a mano. Con esto cerramos la
construcción del sistema: de un `GET /ping` en `localhost` (Sesión 1) a un servidor
contenedorizado, seguro, en tiempo real y resiliente. Solo queda **enseñarlo y abrir caminos**:
→ [[12-demo-day-y-extensiones]].

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `curl` da `Connection refused` desde fuera | Falta el mapeo de puerto | Añade `-p 8000:8000` al `docker run` |
| El contenedor arranca pero nadie le llega | uvicorn escucha en `127.0.0.1` dentro | En el `CMD`, usa `--host 0.0.0.0` |
| La imagen pesa cientos de MB / build lentísimo | Se copió el `.venv` y basura | Crea un `.dockerignore` que excluya `.venv`, `*.db`, `.git` |
| Secretos viajan dentro de la imagen | El `.env` se coló en `COPY . .` | Ignora `.env` y pásalo con `--env-file .env` al arrancar |
| `pip install` no se ejecuta al arrancar | Lo pusiste en `CMD` en vez de `RUN` | Instalar deps es `RUN` (build); arrancar es `CMD` (run) |
| Cambias el código y el contenedor no lo refleja | La imagen es una foto congelada | Vuelve a hacer `docker build` para regenerar la imagen |

## Guion de la sesión

- **0–10** Repaso: el sistema entero funciona y aguanta fallos. Pregunta trampa: "si le paso
  esto a tu compañero, ¿le arranca?" → no, le falta el venv y las deps. Ese es el muro: hacerlo
  repetible.
- **10–30** Teoría en pizarra: el problema "en mi máquina funciona", el dibujo VM vs contenedor,
  imagen vs contenedor, y leer el `Dockerfile` línea a línea (resaltando `RUN` build vs `CMD`
  run, y por qué `--host 0.0.0.0` —enlaza con la Sesión 4—).
- **30–80** `./bin/sesion.sh 11`. Cada uno completa su `Dockerfile` y `.dockerignore`, hace
  `docker build -t curso-servidor .` y `docker run -p 8000:8000 --env-file .env curso-servidor`.
  Verifican con `curl` desde otra máquina que responde igual. Por turnos, la Pi apunta a un
  servidor contenedorizado y enciende el LED real.
- **80–90** Puesta en común: ¿quién olvidó el `-p`? ¿quién metió el `.venv` y construyó una
  imagen de 800 MB? Cierre: "el sistema ya está completo y es portable; la próxima sesión es la
  feria de demos y a dónde seguir".

## Conexiones
- [[10-resiliencia-y-manejo-de-errores]] — la sesión anterior (cliente robusto)
- [[04-salir-del-localhost-la-red-local]] — de dónde viene el `0.0.0.0` y el mapeo de puertos
- [[09-seguridad-y-secretos]] — el `.env` que NO horneamos en la imagen
- [[12-demo-day-y-extensiones]] — la siguiente: demo day y caminos para seguir
- [[Curso_Servidores_y_Redes/00_README]] — visión y diseño del curso
- [[MOC_Desarrollo_Software]] — reproducibilidad, empaquetado, contenedores
- [[MOC_Linux]] — procesos, puertos, imágenes y el kernel compartido
- [[MOC_GCP]] — a dónde escalaría (registry / nube) si saliera de la LAN
