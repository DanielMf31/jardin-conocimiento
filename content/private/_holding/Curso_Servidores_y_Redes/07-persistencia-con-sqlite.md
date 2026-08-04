---
title: Sesión 7 — Persistencia con SQLite
date: 2026-06-17
tags: [programacion/redes, programacion/servidores, fastapi, curso]
type: nota
status: en-progreso
source: claude-code
aliases: [Sesion 7 SQLite, Persistencia telemetria SQLite]
---

# Sesión 7 — Persistencia con SQLite

> **Objetivo**: guardar el histórico de telemetría en una base de datos para que **sobreviva
> a reiniciar el servidor**. Hasta hoy todo vivía en una variable en memoria y se perdía con
> cada `Ctrl+C`.
> **Duración**: ~90 min.
> **Qué se ve funcionando al final**: el servidor recibe telemetría y la guarda en un fichero
> `datos.db`. Se para el servidor, se vuelve a arrancar, se pide `GET /historial` y **los
> datos siguen ahí**. La persistencia se *demuestra* apagando y encendiendo.

## Requisitos previos

- Haber completado hasta [[06-panel-web-en-el-navegador]]: el servidor ya tiene
  `GET/POST /led`, `POST/GET /telemetria` con Pydantic, es accesible en la LAN, la Raspberry
  hace polling y existe un panel web.
- Entorno activado: `source .venv/bin/activate` (el prompt muestra `(.venv)`).
- Entender qué es un endpoint y un modelo Pydantic (se vio en [[03-json-y-validacion-pydantic]]).

## El checkpoint de hoy

```bash
source .venv/bin/activate
./bin/sesion.sh 7            # te coloca en 'sesion7-inicio'
```

El esqueleto trae el `POST /telemetria` y un `GET /historial` con **dos `# TODO`**: la
consulta de `INSERT` (guardar una medida) y la de `SELECT` (leer las últimas N). La función
que crea la tabla al arrancar ya viene hecha, para que el foco de hoy sea **SQL**, no
fontanería.

```python
# servidor/db.py  (estado de partida, sesion7-inicio)
import sqlite3

RUTA_DB = "datos.db"

def conectar():
    return sqlite3.connect(RUTA_DB)

def crear_tablas():
    con = conectar()
    con.execute(
        "CREATE TABLE IF NOT EXISTS telemetria ("
        " id INTEGER PRIMARY KEY,"
        " temperatura REAL,"
        " ts TEXT)"
    )
    con.commit()
    con.close()
```

## Teoría

### 1. Por qué una variable en memoria no basta

Hasta ahora la telemetría se acumulaba en una lista de Python (`historial = []`). Esa lista
vive en la **RAM del proceso**. Cuando el proceso muere —`Ctrl+C`, un crash, un reinicio del
portátil—, la RAM se libera y **la lista desaparece**. No es un bug: es la naturaleza de la
memoria de un programa.

```
   PROCESO VIVO                         PROCESO MUERTO (Ctrl+C)
   ┌──────────────────┐                 ┌──────────────────┐
   │ historial = [    │                 │                  │
   │   22.1, 22.3,    │   ──reinicio──► │   (vacío)        │
   │   22.0, ...      │                 │                  │
   │ ]                │                 │                  │
   └──────────────────┘                 └──────────────────┘
        en RAM                            la RAM se libera
```

Para que un dato sobreviva hay que escribirlo en **almacenamiento persistente**: el disco.
Un fichero, o mejor, una **base de datos**.

### 2. Qué es una base de datos

> Una base de datos es un programa (o una librería) especializado en **guardar datos de forma
> ordenada, consultarlos eficientemente y no corromperlos** aunque haya muchos accesos a la vez.

Podríamos guardar en un `.txt` o un `.json`, pero a la que quieres *"dame las últimas 10
medidas ordenadas por fecha"* sin leer el fichero entero, una BD lo hace por ti. Organiza los
datos en **tablas**.

| Concepto BD | Analogía hoja de cálculo | En nuestro caso |
|---|---|---|
| Tabla | una hoja | `telemetria` |
| Columna | una columna | `id`, `temperatura`, `ts` |
| Fila (registro) | una fila | una medida concreta: `(1, 22.1, "2026-06-17T10:00:00")` |
| Clave primaria | identificador único de fila | `id` (autoincremental) |

### 3. SQLite: una BD en un solo fichero

Hay BD que corren como **servidor aparte** (PostgreSQL, MySQL): otro programa, otro puerto,
hay que instalarlo y administrarlo. Para este proyecto sería matar moscas a cañonazos.

**SQLite** es distinto: es una **librería**, no un servidor. Toda la base de datos es **un
único fichero** (`datos.db`). No hay proceso que arrancar, ni puerto, ni usuario/contraseña.
Tu programa abre el fichero, lee/escribe, lo cierra. Viene **incluido en Python** (`sqlite3`),
así que no hay nada que instalar.

```
   PostgreSQL                          SQLite
   ┌─────────────────┐                 ┌─────────────────┐
   │ proceso aparte  │                 │  tu proceso     │
   │ escucha puerto  │◄──red/socket──  │   sqlite3 ──►   │  datos.db
   │ 5432            │                 │                 │  (un fichero)
   └─────────────────┘                 └─────────────────┘
   potente, multiusuario               simple, perfecto para esto
```

### 4. SQL básico

SQL es el **idioma** para hablar con la BD. Cuatro frases bastan hoy:

| Frase SQL | Qué hace | Ejemplo |
|---|---|---|
| `CREATE TABLE` | define una tabla y sus columnas | `CREATE TABLE telemetria (id INTEGER PRIMARY KEY, temperatura REAL, ts TEXT)` |
| `INSERT` | añade una fila | `INSERT INTO telemetria (temperatura, ts) VALUES (?, ?)` |
| `SELECT` | lee filas | `SELECT temperatura, ts FROM telemetria` |
| `ORDER BY ... LIMIT` | ordena y recorta | `SELECT ... ORDER BY id DESC LIMIT 10` |

`ORDER BY id DESC LIMIT 10` significa *"las 10 filas más recientes primero"*: ordena por `id`
descendente (la última insertada arriba) y se queda con 10.

### 5. Tipos en SQLite

SQLite tiene pocos tipos: `INTEGER`, `REAL` (decimal), `TEXT`, `BLOB`. **No tiene un tipo
fecha/hora.** Por eso `ts` es `TEXT`: guardamos la fecha como cadena en formato **ISO 8601**
(`"2026-06-17T10:00:00"`). Ese formato tiene una propiedad mágica: **ordenar alfabéticamente
fechas ISO equivale a ordenarlas cronológicamente**. Por eso `ORDER BY ts` también funciona.

### 6. Consultas parametrizadas (NUNCA concatenar)

Esto es lo más importante de la sesión y hay que clavarlo. Existe la tentación de construir
el SQL pegando trozos:

```python
# ☠️ MAL — JAMÁS hagáis esto
con.execute("INSERT INTO telemetria (temperatura) VALUES (" + str(valor) + ")")
```

El problema: si `valor` viene de fuera (un cliente, la red), un atacante puede mandar texto
que **se cuele como SQL** y borre o lea tablas. Eso es **inyección SQL**.

```
   El cliente manda como "temperatura":   22 ); DROP TABLE telemetria; --
   Si concatenas, el SQL final ejecuta el DROP. Adiós tabla.
```

La forma correcta es **parametrizar**: pones `?` donde va el dato y pasas los valores aparte.
La librería los **escapa** por ti y nunca los trata como código:

```python
# ✅ BIEN
con.execute(
    "INSERT INTO telemetria (temperatura, ts) VALUES (?, ?)",
    (temperatura, ts),          # tupla de valores, va separada
)
```

> Regla de oro: **los `?` van en el SQL, los valores van en la tupla.** Nunca metas un valor
> dentro de la cadena del SQL con `+` o f-strings.

### 7. Cuándo pasarías a PostgreSQL (mención)

SQLite es perfecto cuando hay **un proceso** escribiendo y los datos caben holgadamente. Si
mañana hubiera muchos servidores escribiendo a la vez, miles de usuarios o necesidad de
réplicas, se migra a algo como **PostgreSQL**. La buena noticia: el SQL que se aprende hoy es
casi el mismo. Los *internals* (índices, transacciones, cómo no se corrompe) se ven en
[[MOC_CS_Fundamentos]].

## Manos a la obra

**1) Colocarse en el checkpoint:**

```bash
source .venv/bin/activate
./bin/sesion.sh 7
```

**2) Rellenar el `INSERT` parametrizado en `POST /telemetria`:**

```python
# servidor/main.py  (solución, fragmento)
from datetime import datetime
from servidor.db import conectar

@app.post("/telemetria")
def recibir_telemetria(medida: Telemetria):
    ts = datetime.now().isoformat()      # "2026-06-17T10:00:00.123"
    con = conectar()
    con.execute(
        "INSERT INTO telemetria (temperatura, ts) VALUES (?, ?)",
        (medida.temperatura, ts),
    )
    con.commit()                          # sin commit, no se guarda
    con.close()
    return {"guardado": True, "ts": ts}
```

- `datetime.now().isoformat()` genera la marca de tiempo como texto ISO.
- Los `?` y la tupla `(...)` → consulta parametrizada, a prueba de inyección.
- `con.commit()` confirma la escritura en disco. **Si se olvida, el dato se pierde.**
- `con.close()` cierra la conexión y libera el fichero.

**3) Rellenar el `SELECT` en `GET /historial`:**

```python
# servidor/main.py  (solución, fragmento)
@app.get("/historial")
def historial(limite: int = 10):
    con = conectar()
    filas = con.execute(
        "SELECT temperatura, ts FROM telemetria ORDER BY id DESC LIMIT ?",
        (limite,),                        # ojo: tupla de un solo elemento
    ).fetchall()
    con.close()
    return [{"temperatura": t, "ts": ts} for (t, ts) in filas]
```

- `ORDER BY id DESC LIMIT ?` → las `limite` más recientes primero.
- `(limite,)` es una tupla de **un** elemento (la coma es obligatoria).
- `.fetchall()` trae todas las filas resultantes como lista de tuplas.

**4) Probar la persistencia (el momento clave):**

```bash
uvicorn servidor.main:app --reload      # arranca el server
# en otra terminal, mete unas medidas:
curl -X POST http://127.0.0.1:8000/telemetria -H "Content-Type: application/json" -d '{"temperatura": 22.1}'
curl -X POST http://127.0.0.1:8000/telemetria -H "Content-Type: application/json" -d '{"temperatura": 22.4}'
curl http://127.0.0.1:8000/historial     # ves las dos medidas
```

Ahora **el truco docente**: `Ctrl+C` para matar el servidor, vuélvelo a arrancar y repite el
`GET /historial`. **Los datos siguen.** Eso es persistencia, y se ve, no se cuenta.

**5) Proteger el `.db` en git:**

```bash
echo "*.db" >> .gitignore
```

El fichero `datos.db` son **datos**, no código. No va al repositorio (cambia constantemente,
puede pesar y puede tener información que no quieres publicar).

## El muro

El histórico ya sobrevive a los reinicios y se puede consultar. Pero alguien lo nota:
*"vale, pero el LED y la web siguen actualizándose **con retraso**: la Raspberry pregunta
cada X segundos (polling) y entre pregunta y pregunta no se entera de nada. ¿No puede el
servidor **avisar** cuando algo cambia, en vez de que el cliente pregunte todo el rato?"*.

Exacto: eso es lo que arregla la [[08-tiempo-real-con-websockets]] con WebSockets.

## Errores comunes

| Síntoma | Causa | Solución |
|---|---|---|
| Funciona pero al ratito da error de seguridad / borra datos raros | SQL construido concatenando valores (inyección) | **Siempre** parametrizar con `?` y tupla de valores |
| `INSERT` no falla pero no se guarda nada | Falta `con.commit()` | Llamar a `con.commit()` antes de `con.close()` |
| `database is locked` o conexiones que se acumulan | Abrir y no cerrar (`con.close()`) | Cerrar la conexión en cada petición (o usar `with`) |
| El historial sale desordenado | Falta `ORDER BY` o se ordena ascendente | `ORDER BY id DESC LIMIT N` para las más recientes |
| Aparece `datos.db` en `git status` | No se ignoró | `echo "*.db" >> .gitignore`; si ya estaba trackeado, `git rm --cached datos.db` |
| Las fechas no ordenan bien | `ts` guardado en formato no ISO | Guardar siempre con `.isoformat()` (texto ISO 8601) |

## Guion de la sesión

| Tramo | Qué hacer |
|---|---|
| **0–10** | Recordatorio: "la telemetría se pierde al reiniciar". Demostrarlo en vivo: meter datos, `Ctrl+C`, rearrancar, vacío. Plantear el problema. |
| **10–35** | Teoría en pizarra: variable en RAM vs disco, qué es una BD, SQLite = un fichero, tabla/fila/columna, las 4 frases SQL. |
| **35–50** | **El punto clave**: inyección SQL y consultas parametrizadas. Mostrar el ejemplo malo y por qué es peligroso. |
| **50–80** | `./bin/sesion.sh 7`, rellenar los dos `# TODO` (`INSERT` y `SELECT`), probar con `curl`. |
| **80–88** | Demo de persistencia: apagar y encender, los datos siguen. Añadir `*.db` al `.gitignore`. |
| **88–90** | **El muro**: el polling sigue dando retraso → presentar Sesión 8. |

## Conexiones

- [[06-panel-web-en-el-navegador]] — sesión anterior: el panel y el polling actual
- [[08-tiempo-real-con-websockets]] — sesión siguiente: eliminar el retraso del polling
- [[03-json-y-validacion-pydantic]] — los modelos Pydantic que validan la telemetría
- [[MOC_CS_Fundamentos]] — internals de bases de datos, índices, transacciones
- [[MOC_Programacion]] — área padre
