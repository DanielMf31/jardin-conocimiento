---
title: Sesión 0 — Setup del entorno y el repositorio
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, curso, setup]
type: nota
status: en-progreso
source: claude-code
aliases: [Setup Curso Servidores, Sesion 0 Servidores]
---

# Sesión 0 — Setup del entorno y el repositorio

> **Objetivo**: que cada alumno llegue a la Sesión 1 con Python, git y el repo del curso
> listos, y sepa usar `./bin/sesion.sh`. Se asume una máquina **desde cero**. Mejor hacerlo
> en la primera media hora del curso (o como tarea guiada previa) para no quemar tiempo de
> red/HTTP peleando con instalaciones.

## Qué necesita cada alumno

- Un portátil con Linux, macOS o Windows (en Windows, **WSL2** con Ubuntu es lo más cómodo
  y lo que asumen estos apuntes; ver [[MOC_Linux]]).
- Conexión a la **misma red local** que las Raspberry de la sala.
- Una cuenta en el GitLab/GitHub donde viva el repo del curso.

## Instalación (script de cero)

El repo trae un `setup.sh` que deja todo listo. La idea es **un solo comando**:

```bash
git clone <URL-del-repo-del-curso> curso-servidores
cd curso-servidores
./setup.sh
```

Qué hace `setup.sh` por dentro (y por qué), para que se pueda explicar:

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1) Comprobar que hay python3 (si no, avisar de cómo instalarlo según el SO)
python3 --version

# 2) Crear un entorno virtual aislado del sistema (no ensuciar el Python global)
python3 -m venv .venv
source .venv/bin/activate

# 3) Instalar las dependencias fijadas del curso
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Entorno listo. Actívalo en cada sesión con:  source .venv/bin/activate"
```

> **Por qué un entorno virtual (`venv`)**: aísla las librerías del curso del Python del
> sistema. Cada proyecto con su `venv` evita el clásico "en mi máquina funciona". Es la
> primera buena práctica del curso. Hay que **activarlo al empezar cada sesión**:
> `source .venv/bin/activate` (el prompt mostrará `(.venv)`).

`requirements.txt` mínimo del curso:

```
fastapi
uvicorn[standard]
requests
gpiozero       # solo se usa de verdad en la Raspberry; en el portátil no estorba
```

## El repositorio del curso

Estructura (la verás crecer sesión a sesión):

```
curso-servidores/
├── bin/
│   └── sesion.sh            # copia una sesión a  trabajo/
├── modelo/                  # CÓDIGO COMPLETO de cada sesión (referencia / lo que enseñas)
│   ├── s01/ ... s11/
│   └── s12/                 # el proyecto FINAL completo (demo de la Sesión 1)
│       ├── servidor/        # FastAPI: led, telemetría, sqlite, websockets, auth, web
│       ├── cliente_pi/      # cliente que corre EN la Raspberry (enciende el LED)
│       └── web/             # panel web (HTML + JS)
├── practica/                # ESQUELETO + TODOs de cada sesión (lo que rellena el alumno)
│   └── s01/ ... s12/
├── trabajo/                 # (se crea solo) donde trabajas la sesión actual
├── requirements.txt         # dependencias del servidor y el cliente
├── requirements-pi.txt      # SOLO la Raspberry (gpiozero)
├── setup.sh
└── README.md
```

## El sistema de checkpoints (`./bin/sesion.sh`)

Cada sesión vive en dos carpetas paralelas: `modelo/sNN` (código completo) y
`practica/sNN` (esqueleto con `# TODO`). El script **copia** la elegida a `trabajo/`,
donde el alumno escribe. Así nadie pelea con git todavía y siempre se parte de algo que
arranca:

```bash
./bin/sesion.sh 1             # copia practica/s01 → trabajo/  (TODOs de hoy)
./bin/sesion.sh 1 --modelo    # copia modelo/s01   → trabajo/  (resuelto, por si te atascas)
```

Implementación de referencia del script (resumida):

```bash
#!/usr/bin/env bash
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
N="${1:?Uso: ./bin/sesion.sh <1-12> [--modelo]}"
NN="$(printf '%02d' "$N")"
CARPETA="practica"; [ "${2:-}" = "--modelo" ] && CARPETA="modelo"
ORIGEN="$RAIZ/$CARPETA/s${NN}"
DEST="$RAIZ/trabajo"
rm -rf "$DEST"; mkdir -p "$DEST"; cp -r "$ORIGEN/." "$DEST/"
echo "✅ Sesión ${NN} (${CARPETA}) en trabajo/."
```

> **Cómo preparar el repo (para el que imparte)**: desarrolla el proyecto completo una vez
> (es `modelo/s12`), y deriva, para cada sesión, su `modelo/sNN` (el código acumulado hasta
> esa sesión) y su `practica/sNN` (ese modelo con las líneas clave del día sustituidas por
> `# TODO: ...`). Así el alumno parte de algo que arranca y solo escribe lo nuevo.

## Comprobación final (todos deben pasar esto antes de la Sesión 1)

```bash
source .venv/bin/activate
python -c "import fastapi, uvicorn, requests; print('OK librerías')"
./bin/sesion.sh 1
```

Si imprime `OK librerías` y te copia la Sesión 1 en `trabajo/`, estás listo.

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `command not found: python3` | Python no instalado | Instálalo (en Ubuntu/WSL: `sudo apt install python3 python3-venv`) |
| `externally-managed-environment` al hacer pip | Estás instalando en el Python del sistema | Activa el `venv` primero: `source .venv/bin/activate` |
| El prompt no muestra `(.venv)` | El entorno no está activado | `source .venv/bin/activate` en esa terminal |
| `./bin/sesion.sh` da "Permission denied" | Falta permiso de ejecución | `chmod +x bin/sesion.sh` |
| `Tienes cambios sin guardar` | Editaste el código y cambias de sesión | `git stash` (guarda aparte) o haz commit |

## Conexiones
- [[Curso_Servidores_y_Redes/00_README]] — visión y diseño del curso
- [[01-vision-del-proyecto-y-primer-servidor]] — la primera sesión
- [[MOC_Linux]] · [[MOC_GitLab]] — terminal, paquetes y git
