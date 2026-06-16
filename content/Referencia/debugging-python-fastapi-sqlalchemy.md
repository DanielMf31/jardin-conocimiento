---
title: Debugging Python + FastAPI + SQLAlchemy — workflow profesional vs trial-and-error
date: 2026-05-13
tags: [programacion/referencia, programacion/debugging, programacion/python, programacion/herramientas]
type: nota
status: permanente
source: claude-code
aliases: [debugging-tools, mypy-ruff-pyright, python-debugging-workflow]
---

# Debugging Python backend — el workflow profesional completo

> Doc transversal de [[Referencia/00_README|Referencia]]. Cubre TODAS las herramientas para encontrar bugs en código Python (especialmente FastAPI + SQLAlchemy + async) **antes** de que lleguen a producción. El objetivo: reemplazar el ciclo doloroso "edit → restart Docker → leer logs → fix" por workflow profesional con feedback inmediato.

## Por qué importa

El error más común de junior backend developer:

```
Edit código
  → docker compose restart
  → docker compose logs api
  → grep en 200 líneas de traceback
  → encontrar el error
  → fix
  → repeat
```

Cada iteración: 30-60 segundos. Multiplicado por 5-10 typos por sesión = **30-60 minutos perdidos al día**.

El workflow profesional reduce este tiempo a segundos por iteración usando herramientas que detectan errores **sin levantar Docker**. Tras adoptarlo, debugging se vuelve dramatically más rápido y menos frustrante.

## SCHEMA: 3 categorías de errores + qué herramienta atrapa cada uno

| Tipo | Ejemplo | Atrapa por |
|---|---|---|
| **Syntax error** | `def func( :` (faltan paréntesis) | Python parser (`python -m py_compile`) |
| **Type / API error** | `_class=` en vez de `class_=`, `String(True)` cuando espera int, `back_pupulates` (typo en kwarg) | Type checker estático (mypy, pyright, Pylance) |
| **Logic error** | `__tablename__ = "user"` (singular cuando DB tiene plural), `default=False` cuando debería ser True | Tests + ejecución (NO atrapable estáticamente) |

**El insight clave**: ~50% de los bugs son tipo type/API → 100% atrapables por type checker en segundos sin levantar nada.

## PATTERNS — el toolkit completo (cada uno con su rol)

### Tier 1 — IDE en tiempo real (cero coste, máximo ROI)

**Pylance en VS Code**: extension oficial Microsoft que da subrayado rojo MIENTRAS TIPEAS los errores type/API.

Setup:
1. Instalar extension "Python" de Microsoft (incluye Pylance)
2. `Ctrl+,` → buscar "Python Analysis: Type Checking Mode" → set a `basic` (o `strict` si quieres más warnings)
3. Listo

Para que entienda tus librerías: tu venv debe tener instaladas las dependencias. En VS Code:
- `Ctrl+Shift+P` → "Python: Select Interpreter" → elige el venv correcto
- Si trabajas en Docker: instala las mismas deps en venv local con `pip install -r requirements.txt`

**Habría atrapado en tiempo real**:
- `_class=AsyncSession` → red squiggly "no such parameter"
- `String(True)` → "expected int, got bool"
- `back_pupulates` → "no such parameter on relationship"
- `await sync_function()` → "object is not awaitable"

### Tier 2 — Linter rápido (corre en CLI antes de commit)

**Ruff**: linter modernísimo escrito en Rust, ~100x más rápido que flake8.

```bash
# Instalar
pip install ruff

# Lint todo el proyecto
ruff check .

# Auto-fix lo que pueda (importaciones, formateo)
ruff check . --fix

# Format (reemplaza black)
ruff format .
```

Atrapa:
- Imports no usados
- Variables no usadas
- Comparaciones sospechosas (`x == None` en vez de `x is None`)
- Bugs de estilo
- Algunos type issues básicos

NO atrapa typos de kwargs (necesitas mypy para eso).

Config en `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "SIM"]
# E = pycodestyle errors
# F = pyflakes (logical bugs)
# W = warnings
# I = isort (imports)
# B = bugbear (extra bugs)
# UP = pyupgrade (modernization)
# SIM = simplify
ignore = ["E501"]  # line length
```

### Tier 3 — Type checker estático (la herramienta MÁS valiosa)

**mypy**: el estándar del ecosistema. Lee el código, infiere tipos, detecta inconsistencias.

```bash
# Instalar
pip install mypy

# Run
mypy app/

# Más estricto
mypy --strict app/
```

**Habría atrapado en 1 segundo SIN levantar Docker**:
```
app/db.py:30: error: Unexpected keyword argument "_class" for "async_sessionmaker"  [call-arg]
app/db.py:32: error: Unexpected keyword argument "autflush" for "async_sessionmaker"  [call-arg]
app/models/hotel.py:46: error: Unexpected keyword argument "back_pupulates" for "relationship"  [call-arg]
app/models/user.py:31: error: Argument 1 to "String" has incompatible type "bool"; expected "int"  [arg-type]
```

Config en `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.12"
warn_unused_configs = true
warn_redundant_casts = true
no_implicit_optional = true
check_untyped_defs = true
disallow_incomplete_defs = true
ignore_missing_imports = true   # para libs sin type stubs

[[tool.mypy.overrides]]
module = "tests.*"
disallow_incomplete_defs = false  # tests más relajados
```

**pyright** (Microsoft): alternativa más rápida, lo que usa Pylance internamente. Misma función. Elige uno (mypy más establecido, pyright más rápido).

### Tier 4 — Smoke test (1 segundo, dice "¿al menos importa?")

```bash
docker compose exec api python -c "from app.main import app; print('Imports OK')"
```

Esto:
- Importa todos los módulos transitivamente (app.main → routers → services → models → db)
- Si algún archivo tiene typo de class creation (como `back_pupulates`) → falla AQUÍ con traceback corto
- Tarda ~1 segundo
- NO levanta uvicorn ni server

**Hazlo siempre tras editar models o configs**. Catch rápido del 30% de bugs.

### Tier 5 — Tests (la red de seguridad final)

```bash
# Todos
docker compose exec api pytest -v

# Solo un archivo
docker compose exec api pytest tests/test_auth.py -v

# Stop al primer fail (útil mientras debuggeas)
docker compose exec api pytest -x

# Verbose con prints visibles
docker compose exec api pytest -vsx tests/test_auth.py
```

Tests atrapan los **logical bugs** que static analysis no puede:
- `__tablename__ = "user"` → test_register fallaría con "table 'user' doesn't exist"
- `default=False` para is_active → test_register_creates_user assertion fail
- Falta `created_at` → test que verifica response_model fallaría

Ver para detalle pytest.

### Tier 6 — Pre-commit hooks (zero olvidar)

**pre-commit**: framework que corre las herramientas anteriores automáticamente antes de cada `git commit`. Imposible commitear código con bugs catchable.

Setup:
```bash
pip install pre-commit
pre-commit install   # registra hooks en .git/hooks/
```

Config en `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        files: ^backend/app/
        additional_dependencies:
          - sqlalchemy[asyncio]==2.0.36
          - pydantic==2.9.2
          - fastapi==0.115.0
```

Tras `pre-commit install`, cada `git commit` corre ruff + mypy. Si fallan, commit blocked. Te ahorra 100% de typos catchable que llegarían a CI/staging.

Manual run sin commit: `pre-commit run --all-files`.

## SPECIFICS — el workflow ideal vs el doloroso

### El ciclo profesional (rápido)

```
┌─────────────────────────────────────────┐
│ 1. Edit código en VS Code               │
│    (Pylance marca errors red en vivo)   │ ← 0s feedback
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 2. Save + ruff auto-format              │ ← <1s
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 3. mypy app/ (en CLI o save trigger)    │ ← 2-5s
│    Atrapa typos de kwargs               │
└──────────────┬──────────────────────────┘
               ↓ (todo OK)
┌─────────────────────────────────────────┐
│ 4. Smoke test:                          │ ← 1s
│    docker compose exec api python -c    │
│    "from app.main import app"           │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 5. pytest -x (stop first fail)          │ ← 5-30s
│    Atrapa logical bugs                  │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│ 6. docker compose restart api           │ ← 5s
│    Verificación end-to-end con curl     │
└─────────────────────────────────────────┘
```

**Total feedback en cada iteración: <1 minuto**. La mayoría de bugs nunca llegan al paso 6.

### El ciclo doloroso (que vas a evitar)

```
┌────────────────────────────┐
│ 1. Edit código             │
└──────────┬─────────────────┘
           ↓
┌────────────────────────────┐
│ 2. docker compose restart  │ ← 10-30s
└──────────┬─────────────────┘
           ↓
┌────────────────────────────┐
│ 3. curl http://...         │ ← 1s
│    → 500 Internal Error    │
└──────────┬─────────────────┘
           ↓
┌────────────────────────────┐
│ 4. docker compose logs api │ ← 5s + scroll
│    grep en 200+ líneas     │   buscando el error
└──────────┬─────────────────┘
           ↓
┌────────────────────────────┐
│ 5. Encontrar trace real    │ ← 1-5 min reading
│    (cortado por terminal,  │
│    necesitas más logs)     │
└──────────┬─────────────────┘
           ↓
┌────────────────────────────┐
│ 6. Fix + repeat            │
└────────────────────────────┘
```

**Total: 5-10 minutos por bug**. Multiplicado por 5-10 bugs/sesión = horas perdidas.

## Common error decoder — los traceback más comunes y qué significan

Cuando levantes Docker y veas error, esta tabla te ahorra tiempo de Google:

### Errores de SQLAlchemy

| Error | Causa probable | Fix |
|---|---|---|
| `TypeError: ... got an unexpected keyword argument 'X'` | Typo en kwarg de relationship/mapped_column/sessionmaker | Verifica nombre exacto del kwarg |
| `IntegrityError: duplicate key value violates unique constraint` | Insertando duplicado en columna UNIQUE | Catch exception → return 409 |
| `IntegrityError: violates not-null constraint` | NULL en columna NOT NULL | Verifica que pasas valor o tienes default |
| `IntegrityError: violates foreign key constraint` | FK pointing a row que no existe | Verifica orden de inserts |
| `DetachedInstanceError: ... is not bound to a Session` | Accedes a objeto fuera de session | `expire_on_commit=False` o re-fetch |
| `MissingGreenlet: greenlet_spawn has not been called` | Async query desde sync context | Usa AsyncSession + await |
| `LookupError: No such table 'X'` | Migration no aplicada | `alembic upgrade head` |
| `Mapper failed to initialize` | Typo en `back_populates` o relationship inválida | Smoke test al import |

### Errores de FastAPI / Pydantic

| Error | Causa probable | Fix |
|---|---|---|
| `422 Unprocessable Entity` | Body no matchea schema Pydantic | Verifica field names + types en payload |
| `Input should be a valid string` | Campo recibido tipo equivocado | Casting / validar |
| `Field required` | Falta campo en request | Default value o request correcto |
| `Object of type X is not JSON serializable` | Pydantic no sabe serializar tipo custom | Define `model_dump()` custom o usar `from_attributes=True` |
| `dependency function did not yield` | Generator dependency mal escrito | Verifica que `yield` está en `try/finally` |
| `'NoneType' object has no attribute 'X'` | Asumes objeto existe pero `db.get()` retornó None | Check antes de usar |

### Errores de async / event loop

| Error | Causa probable | Fix |
|---|---|---|
| `RuntimeError: Event loop is closed` | Engine creado en loop diferente al test | `loop_scope="session"` en pytest-asyncio |
| `RuntimeWarning: coroutine 'X' was never awaited` | Olvidaste `await` | Añade await o `asyncio.run()` |
| `RuntimeError: This event loop is already running` | Llamando `asyncio.run()` dentro de async context | Usa `await` directo |
| `task was destroyed but it is pending` | Cancelaste task sin esperar cleanup | `await task` antes de cancel |

### Errores de Alembic

| Error | Causa probable | Fix |
|---|---|---|
| `Target database is not up to date` | Migrations pendientes vs DB | `alembic upgrade head` |
| `Can't locate revision identified by 'X'` | Mismatch versión DB vs filesystem | `alembic stamp head` (peligroso) o restore |
| `Multiple head revisions are present` | Branches no resueltos | `alembic merge -m "merge"` |
| `Cannot autogenerate ... no changes detected` | Models == DB schema (correcto), o tabla no detectada | Verifica `target_metadata` en env.py |

## Workflow Docker — comandos efectivos para debug

### Logs sin ruido del pasado

```bash
# Solo los últimos 30 segundos
docker compose logs api --since 30s

# Follow en tiempo real (deja en una terminal, haz request en otra)
docker compose logs -f api

# Buscar en logs históricos
docker compose logs api 2>&1 | grep -A 20 "POST /auth/register"

# Solo error level
docker compose logs api 2>&1 | grep -i "error\|exception\|traceback"
```

### Inspeccionar dentro del container

```bash
# Shell interactivo dentro del container
docker compose exec api bash

# Una vez dentro:
python -c "from app.main import app"   # smoke test
mypy app/                               # type check
pytest -v                               # tests
alembic current                         # current migration
psql ${DATABASE_URL/postgresql+asyncpg/postgresql} -c "\dt"   # list tables

# Salir: exit
```

### Ver estado de containers

```bash
# Status simple
docker compose ps

# Logs + status combinados
docker compose ps && docker compose logs api --tail 5

# Recursos (CPU, memoria) en tiempo real
docker stats
```

### Reset si todo se rompe

```bash
# Apagar SIN borrar data
docker compose down

# Apagar Y borrar volúmenes (DB se resetea)
docker compose down -v

# Rebuild desde cero
docker compose down -v
docker compose up --build -d
```

## Database debugging — psql shortcuts

Acceso directo a Postgres dentro del container:

```bash
docker compose exec db psql -U booking -d booking
```

Comandos esenciales dentro de psql:

```sql
\dt                          -- list tables
\d users                     -- describe tabla users (columns, types, indexes)
\di                          -- list indexes
\df                          -- list functions
\du                          -- list users
\l                           -- list databases
\c booking                   -- connect to booking db

-- Queries
SELECT * FROM users LIMIT 5;
SELECT count(*) FROM hotels;

-- EXPLAIN ANALYZE para diagnosticar lentitud
EXPLAIN ANALYZE SELECT * FROM hotels WHERE city = 'Madrid';

-- Ver tablas + tamaño
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables WHERE schemaname='public';

-- Salir
\q
```

Ver [[sql-y-bases-de-datos-fundamentos]] para SQL profundo.

## Runtime debugging — pdb y breakpoint()

Cuando necesitas pausar la ejecución y inspeccionar variables:

```python
# En cualquier lugar del código
def my_endpoint():
    user = await db.get(User, user_id)
    breakpoint()              # ← pausa AQUÍ cuando se ejecute
    return user
```

Cuando llegue al `breakpoint()`, Python entra en pdb (debugger interactivo):
```
(Pdb) user                    # imprime variable user
(Pdb) print(user.email)       # imprime atributo
(Pdb) p user.is_admin         # short for print
(Pdb) l                       # show 11 lines around current
(Pdb) n                       # next line
(Pdb) s                       # step into function
(Pdb) c                       # continue execution
(Pdb) q                       # quit
```

**En Docker**: para que `breakpoint()` funcione, necesitas correr container con `-it` (interactive). Más simple en local venv. En Docker prefiero `print(...)` o logging.

### Logging estructurado en lugar de print

Mejor que `print()`:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("user fetched", extra={"user_id": user.id, "email": user.email})
```

Si tienes structlog (proyecto 04+), aún mejor:
```python
log = structlog.get_logger()
log.info("user_fetched", user_id=user.id, email=user.email)
```

Ver `04_phone_book_cache_observability/docs/04-structured-logging-con-structlog` para detalles.

## VS Code setup óptimo (si lo usas)

### Settings recomendados (`.vscode/settings.json` en tu proyecto)

```json
{
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,
  "python.analysis.diagnosticMode": "workspace",

  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": "explicit",
    "source.organizeImports.ruff": "explicit"
  },

  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  },

  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

### Extensions críticas

| Extension | Para qué |
|---|---|
| **Python** (Microsoft) | Pylance + debugging + Jupyter |
| **Ruff** (Astral) | Linter integration |
| **Mypy Type Checker** | mypy integration |
| **Docker** (Microsoft) | Manage containers desde VS Code |
| **Even Better TOML** | pyproject.toml syntax highlighting |
| **Thunder Client** | Reemplaza curl con UI dentro VS Code |

## Profiling (cuando algo es LENTO, no roto)

Cuando el código funciona pero es lento:

```bash
# cProfile básico
python -m cProfile -s cumulative my_script.py | head -30

# Para servidores web: py-spy (sample profiler, no requiere modificar código)
pip install py-spy
py-spy record -o profile.svg --pid <process_id>
# Genera flame graph SVG visualizable en browser
```

Para Booking, profiling no es prioritario en v0.1 pero será relevante en v0.6 (Caching + Performance).

## Anti-patterns que ahogan tu productividad

| Anti-pattern | Por qué malo | Mejor approach |
|---|---|---|
| Editar y restart Docker sin smoke test previo | Ciclo lento + frustración | Smoke test (1s) primero |
| Ignorar warnings de Pylance "porque el código funciona" | Acumulación de bugs latentes | Cada warning es una pista |
| `try/except: pass` para silenciar errores | Encubre bugs reales | Catch specific exception + log |
| Print debugging dejado en producción | Logs ruidosos + leak info | Usa logger con levels |
| Tests que mockean TODO | Pasan tests, falla producción | Mock solo external dependencies (Stripe, email), NO DB ni FastAPI |
| Commits gigantes sin lint check | Mezclas bugs reales con typos en review | pre-commit hooks |
| `docker compose logs` sin `--tail` o `--since` | 1000s de líneas de scroll | Filtrar con `--since 30s` o `-f` |
| Asumir que el log que ves es el actual | Logs son cumulativos, te confunden | Restart + logs frescos, o `--since` |

## El playbook completo "tengo un bug, qué hago"

Cuando algo no funciona:

```
1. ¿Qué error específico veo?
   - Si syntax error → fix obvio
   - Si TypeError "unexpected kwarg" → typo, mira pyproject + mypy
   - Si IntegrityError → constraint violation, mira la columna
   - Si AttributeError → falta atributo, posible desync ORM/schema

2. ¿Pasa el smoke test?
   docker compose exec api python -c "from app.main import app"
   - Si falla → el error es de IMPORT TIME (typo en class definition)
   - Si pasa → el error es de RUNTIME (request handling)

3. ¿Pasa mypy?
   docker compose exec api mypy app/
   - Si te lista errores → fixea esos primero

4. ¿Pasan los tests relevantes?
   docker compose exec api pytest tests/test_auth.py -x
   - Si falla un test específico → el test te dice qué está mal

5. Solo si lo anterior está OK pero E2E falla:
   docker compose logs api --since 30s
```

Aplicar este orden te ahorra horas vs entrar directamente a leer logs.

## Conexiones

- [[Referencia/00_README]] — área padre
- [[archetipos-funciones-backend]] — relacionado para pattern recognition
- [[sql-y-bases-de-datos-fundamentos]] — para errores de DB específicos
- (Booking) — pytest detalle
- (Booking) — el async testing gotcha

## Recursos canónicos para profundizar

- **mypy docs** — https://mypy.readthedocs.io/ (cuando dudes config)
- **ruff docs** — https://docs.astral.sh/ruff/ (rules + config)
- **"Python Tricks"** (Dan Bader) — para error patterns idiomáticos
- **"Fluent Python" 2nd ed** (Luciano Ramalho) — Python deep, incluye sección debugging
- **PostgreSQL EXPLAIN docs** — https://www.postgresql.org/docs/current/sql-explain.html
- **pdb cheatsheet** — https://docs.python.org/3/library/pdb.html

## Resumen mental

> "3 categorías errores: syntax (Python parser atrapa), type/API (mypy/pyright/Pylance atrapa), logic (solo tests atrapan). ~50% de bugs son type/API → 100% atrapables sin levantar Docker. Stack mínimo: Pylance VS Code (live red squigglies) + ruff (linter rápido) + mypy (type checker — ATRAPA typos kwargs) + pytest (logic). Tier extra: pre-commit hooks block commits con bugs catchable. Smoke test universal: `docker compose exec api python -c 'from app.main import app'` (1s, atrapa import errors). Workflow profesional: edit con Pylance live → save (ruff format) → mypy → smoke test → pytest -x → restart Docker (verificación E2E). NO el ciclo doloroso edit→restart→logs→grep→fix. Common errors decoder con tabla SQLAlchemy/FastAPI/Pydantic/async/Alembic. Logs Docker efectivos: `--since 30s` (sin ruido pasado), `-f` (live follow). Database debugging: `docker compose exec db psql -U X -d Y` + comandos psql `\dt`, `\d users`, EXPLAIN ANALYZE. Runtime debug: `breakpoint()` para pdb interactivo, structured logging mejor que print. VS Code config: typeCheckingMode=basic, formatOnSave=true, ruff fixAll. Anti-patterns: editar y restart sin smoke test (lento), ignorar warnings Pylance, try/except pass (encubre bugs), tests que mockean TODO (pasan tests, falla prod). Playbook 'tengo bug': identifica error específico → smoke test → mypy → pytest relevante → solo después logs Docker. Aplicar este orden ahorra horas vs leer logs primero."
