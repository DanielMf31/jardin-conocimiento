---
title: Archetypes de funciones en backend — catálogo de reconocimiento
date: 2026-05-12
tags: [programacion/referencia, programacion/patterns, aprendizaje/chunking]
type: nota
status: permanente
source: claude-code
aliases: [archetipos-funciones, function-archetypes, patterns-funciones-backend]
---

# Archetypes de funciones en backend — catálogo de reconocimiento

## Por qué importa

Cuando lees código línea a línea, tu cerebro consume working memory en CADA token: nombre de variable, tipo, llamada, return. Saturas en ~5 segundos por función no trivial. Resultado: lees una hora, te acuerdas de poco, no construyes modelo mental del sistema.

Cuando reconoces que una función es un **handler** ANTES de leer su body:

1. Predices su signature (recibe `request` o un payload tipado, devuelve un response model)
2. Sabes qué efectos secundarios esperar (DB write, cache invalidate, log)
3. Sabes qué errores puede lanzar (HTTP 4xx, integrity error, auth failure)
4. Sabes con qué OTRAS funciones se relaciona (dependencies inyectadas, services, schemas)

Eso es **chunk recognition de capa 1**: leer la forma de un patrón sin re-derivar nada. El senior ve `@router.post(...)` y ya tiene un schema esperando que se rellene; tú lees 30 líneas. Ese gap es la diferencia entre Dreyfus Competent y Proficient.

Este catálogo te entrena el reconocimiento. Veintidós archetypes que vas a encontrar en CUALQUIER backend (FastAPI, Express, Django, Rails, Spring, ASP.NET). Memoriza la **forma** — la sintaxis del lenguaje es secundaria.

## Cómo usar este catálogo

- **Drill diario** (5 min): abre cualquier `.py` del proyecto, antes de leer cada función PREDICE su archetype mirando solo el decorador + signature. Comprueba leyendo el body. 80%+ de aciertos = ya cruzaste el threshold para ese tipo de archivo.
- **Cross-project**: cuando encuentres un archetype nuevo (no listado), añádelo aquí con ejemplo. Si tras 1 mes hay >25, plantea bifurcar el doc.
- **Senior reading**: el senior NO lee línea a línea. Ve archetype → infiere body al 80% → lee solo lo que difiere de la expectativa. Esa es la velocidad 10x.

## Tabla resumen — los 22 archetypes

| # | Archetype | Signature pattern (1 línea) | Cuándo aparece |
|---|---|---|---|
| 1 | Handler / Route handler | `@router.METHOD(path) async def fn(payload, deps) -> Schema` | Entry point HTTP, top de cualquier router |
| 2 | Dependency / Provider | `async def get_X(...) -> X` (consumido vía `Depends`) | Inyección de DB, user, config en handlers |
| 3 | Validator | `def fn(value) -> value` (raises si inválido) | Pre-check de input antes de procesarlo |
| 4 | Transformer / Mapper | `def fn(A) -> B` (sin side effects) | Pydantic ↔ ORM, dict ↔ model, DTO ↔ entity |
| 5 | Getter / Reader / Query | `async def get_X(id, db) -> X \| None` | Lectura DB, sin mutación |
| 6 | Setter / Writer / Mutator | `async def create/update/delete_X(...) -> ...` | Persiste o cambia state |
| 7 | Predicate / Checker / Guard | `def is_X / has_X / can_X(...) -> bool` | Decisión binaria reusable |
| 8 | Side-effect handler | `async def send_X / publish_X(...) -> None` | Comunicación con mundo externo |
| 9 | Wrapper / Decorator / Middleware | `def fn(handler) -> handler'` o `async dispatch(req, call_next)` | Lógica transversal alrededor del core |
| 10 | Factory / Builder | `def make_X / build_X / create_X(...) -> X` | Construcción de objeto complejo |
| 11 | Helper / Utility / Pure | `def fn(args) -> result` (pequeña, pura) | Cálculo reusable sin estado |
| 12 | Initializer / Setup / Bootstrap | `def configure_X / init_X(...) -> None` | Setup ejecutado UNA vez al startup |
| 13 | Lifecycle hook | `@asynccontextmanager async def lifespan(app)` | Startup + shutdown del proceso |
| 14 | Cleanup / Teardown / Close | `async def close_X / shutdown_X() -> None` | Liberación de recursos al final |
| 15 | Adapter / Bridge | `class XAdapter` o `def to_X / from_X` | Traducción entre 2 interfaces incompatibles |
| 16 | Strategy / Policy | `def strategy_A / strategy_B` con misma firma | Variante intercambiable de comportamiento |
| 17 | Pipeline stage / Processor | `def stage(input) -> output` (componible) | Cadena de transformaciones |
| 18 | Aggregator / Reducer | `def fn(items) -> single` | Combinar muchos en uno |
| 19 | Iterator / Generator / Stream | `def fn(...) -> Iterator/AsyncGenerator` | Yield perezoso de items |
| 20 | Coordinator / Orchestrator / Service | `async def do_X(deps...) -> result` | Capa que llama a múltiples primitives |
| 21 | Repository | `class XRepo` con `get/list/save/delete` | Acceso a datos encapsulado |
| 22 | Healthcheck | `@app.get("/health") -> dict` | Liveness/readiness para orquestador |

## Detalle de cada archetype

### 1. Handler / Route handler / Controller

**Sinónimos**: endpoint, action (Rails), view (Django), controller (Spring/Express).

**Signature pattern**:

```python
@router.METHOD("/path", response_model=Schema, status_code=20X)
async def name(payload: PayloadSchema, dep1: T1 = Depends(...), dep2: T2 = Depends(...)) -> Schema:
    ...
```

**Cómo identificarlo visualmente**:

- Decorador HTTP (`@app.get`, `@router.post`, `@app.route`, `app.MethodMapping` en Spring)
- Argumentos = combinación de `payload tipado + dependencies inyectadas + path/query params`
- Return type es un schema/DTO (no entity raw)
- Vive en `routers/`, `controllers/`, `views/`, `api/`

**Qué hace**: traduce HTTP → dominio → HTTP. Recibe request, valida (vía Pydantic/serializer), llama a service o hace la lógica inline (en apps pequeñas), devuelve response.

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/routers/contacts.py
@router.post("", response_model=Contact, status_code=status.HTTP_201_CREATED)
async def create_contact(
    payload: ContactCreate,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContactORM:
    new_contact = ContactORM(**payload.model_dump(), user_id=current_user.id)
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    await cache.invalidate_pattern(f"contacts:user:{current_user.id}:*")
    log.info("contact_created", contact_id=new_contact.id, user_id=current_user.id)
    return new_contact
```

**Variantes**:
- **Thin handler** (recomendado): solo orquesta, delega a service. Tu `04` aún tiene business logic en el handler — fine para CRUD, refactor a service cuando crezca.
- **Fat handler**: toda la lógica inline. Smell si la función pasa 40 líneas.
- **Async vs sync handler**: en FastAPI ambos válidos; async cuando tocas I/O.

**Archetypes relacionados**: [Dependency](#2-dependency--provider), [Validator](#3-validator) (Pydantic actúa como validator implícito), [Coordinator](#20-coordinator--orchestrator--service).

**Anti-pattern**: handler con 5 niveles de `if/else` y 80 líneas. Indica que falta capa de service. También: handler que devuelve ORM raw sin pasar por response_model — leak de columnas internas (hashed_password, is_admin).

---

### 2. Dependency / Provider

**Sinónimos**: provider (NestJS), DI bean (Spring), service (Angular DI).

**Signature pattern**:

```python
async def get_X(other_dep: Y = Depends(other)) -> X:
    ...
# Consumido como:  param: X = Depends(get_X)
```

**Cómo identificarlo visualmente**:

- Nombre suele empezar por `get_` (`get_db`, `get_current_user`, `get_settings`)
- Vive en `dependencies.py` o `deps/`
- NO tiene decorador HTTP
- Es consumido vía `Depends(get_X)` en handlers (FastAPI), `@Inject` (NestJS), constructor injection (Spring)
- A menudo es un **async generator** (con `yield`) cuando gestiona recurso con cleanup

**Qué hace**: prepara y entrega un recurso al handler. Centraliza lógica que se repetiría en N endpoints (apertura de session, decode de JWT, lectura de config).

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/dependencies.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async generator que yield una AsyncSession por request."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    # decodifica JWT, valida, busca user en DB, lo devuelve
    ...
```

**Variantes**:
- **Generator dependency** (`yield` + cleanup post-yield): para recursos con scope de request (DB session).
- **Plain dependency** (`return value`): para cosas inmutables (config, settings).
- **Sub-dependency**: dependency que consume otra dependency (`get_current_user` consume `get_db`).
- **Class-based dependency**: clase con `__call__` para parametrizar (e.g. `RoleChecker("admin")`).

**Archetypes relacionados**: [Initializer](#12-initializer--setup--bootstrap) (a menudo Initializer prepara el singleton que la Dependency entrega), [Validator](#3-validator) (`get_current_user` valida implícitamente).

**Anti-pattern**: dependency con side effects no idempotentes (incrementar contador, escribir log de auditoría) — se ejecuta UNA vez por request, no por endpoint, fácil sorpresa.

---

### 3. Validator

**Sinónimos**: guard, sanity check, precondition.

**Signature pattern**:

```python
def validate_X(value: T) -> T:        # devuelve normalizado o raises
    ...
def assert_X(value: T) -> None:       # raises si inválido
    ...
```

En Pydantic los validators son métodos de clase decorados con `@field_validator` o `@model_validator`.

**Cómo identificarlo visualmente**:

- Nombre con `validate_`, `check_`, `assert_`, `ensure_`
- Devuelve el mismo tipo que recibe (o `None` si solo levanta)
- Cuerpo dominado por `if ... raise ...`
- En Pydantic: dentro de un `BaseModel` con decorator `@field_validator("field")`

**Qué hace**: rechaza input inválido lo antes posible. "Fail fast" en la frontera del sistema para que el resto del código asuma datos sanos.

**Ejemplo de tus proyectos** (Pydantic validation implícita en schemas):

```python
# 02_phone_book_postgres/server/schemas.py
class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=1, max_length=30)
    email: EmailStr   # ← validator implícito: rechaza emails malformed
```

Validator imperativo dentro del CLI cliente:

```python
# 02_phone_book_postgres/client/cli.py
def ask_id(prompt: str = "ID: ") -> int | None:
    raw = input(prompt).strip()
    if not raw.isdigit():
        print(f"⚠️  ID debe ser un número, recibí {raw!r}")
        return None
    return int(raw)
```

Validator de tipo de token dentro del decode:

```python
# 04_phone_book_cache_observability/server/app/auth.py
def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if expected_type is not None and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(...)   # ← validator embebido
    return payload
```

**Variantes**:
- **Throwing validator** (`raise` si mal): canónico en Python/Java.
- **Returning validator** (`-> tuple[bool, str]` o `Result`): canónico en Rust/Go.
- **Schema-level vs field-level**: Pydantic `@field_validator` vs `@model_validator`.

**Archetypes relacionados**: [Predicate](#7-predicate--checker--guard) (validator devuelve `None`/raises, predicate devuelve bool), [Transformer](#4-transformer--mapper) (validator a veces normaliza = mini-transform).

**Anti-pattern**: validators que escriben a DB o llaman APIs externas. Validator debe ser **puro o casi puro**; lo demás se llama check/verification y va en otra capa.

---

### 4. Transformer / Mapper

**Sinónimos**: converter, marshaller, serializer, DTO mapper.

**Signature pattern**:

```python
def to_X(a: A) -> X:           # de un tipo a otro
def from_X(x: X) -> A:         # inverso
def X_to_dict(x: X) -> dict:   # frontera de serialización
```

**Cómo identificarlo visualmente**:

- Nombre empieza con `to_`, `from_`, `as_`, `serialize_`, `parse_`
- Entrada: 1 argumento de tipo A. Salida: tipo B distinto.
- **Sin side effects**: no I/O, no mutación
- Suele vivir en `mappers/`, `serializers/`, o como método de clase (`Pydantic.model_validate`)

**Qué hace**: convierte entre representaciones. Es el **pegamento entre capas**: HTTP JSON ↔ Pydantic ↔ ORM ↔ SQL row.

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/routers/contacts.py
# Transform ORM → Pydantic dict para guardar en cache
serialized = [Contact.model_validate(c).model_dump(mode="json") for c in contacts]
```

`Contact.model_validate(c)` = transformer ORM → Pydantic. `.model_dump(mode="json")` = transformer Pydantic → dict JSON-safe. Dos transformers encadenados.

Otro caso, en `schemas.py`:

```python
class Contact(ContactCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)   # habilita transform ORM → Pydantic
```

`from_attributes=True` activa el transformer implícito que lee atributos de objeto en lugar de keys de dict.

**Variantes**:
- **Bidirectional pair** (`to_X` + `from_X`): común en mapping ORM ↔ DTO.
- **Auto-mapper** (Pydantic, MapStruct, AutoMapper en .NET): transform por convención de nombres.
- **Codec** (encode/decode): JSON codec, JWT codec.

**Archetypes relacionados**: [Adapter](#15-adapter--bridge) (adapter es transformer + interfaz richer), [Helper](#11-helper--utility--pure-function).

**Anti-pattern**: transformer que dispara queries DB ("lazy loading" oculto). Te crashea en async porque acaba siendo sync I/O dentro del transform. Por eso en tu `db.py` usas `expire_on_commit=False`.

---

### 5. Getter / Reader / Query

**Sinónimos**: finder, fetcher, retriever, accessor, query.

**Signature pattern**:

```python
async def get_X_by_id(id: int, db: Session) -> X | None
async def list_Xs(filters..., db: Session) -> list[X]
async def find_X_by_email(email: str, db: Session) -> X | None
```

**Cómo identificarlo visualmente**:

- Nombre `get_`, `find_`, `fetch_`, `list_`, `search_`, `query_`
- Devuelve datos (1 entidad, lista, o `None`)
- **Sin mutación**: solo lee
- Body típico: construye query → ejecuta → devuelve resultado

**Qué hace**: lee del store (DB, cache, API externa). Idempotente: llamarlo N veces da el mismo resultado (módulo cambios externos).

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/routers/contacts.py
@router.get("/{contact_id}", response_model=Contact)
async def get_contact(
    contact_id: int,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    cache_key = f"contact:{contact_id}"
    cached = await cache.get_json(cache_key)
    if cached is not None:
        if cached.get("user_id") != current_user.id:
            raise HTTPException(status_code=404, ...)
        return cached
    contact = await db.get(ContactORM, contact_id)
    ...
```

Es un Handler que ENVUELVE un Getter (`db.get(ContactORM, contact_id)`).

Y el Getter puro de la cache:

```python
# 04_phone_book_cache_observability/server/app/services/cache.py
async def get_json(key: str) -> Any | None:
    client = get_redis()
    if client is None:
        return None
    try:
        raw = await client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except (RedisError, json.JSONDecodeError) as e:
        log.warning("cache_get_failed", key=key, error=str(e))
        return None
```

**Variantes**:
- **By-id getter** (devuelve `X | None`): el más común.
- **List/search query** (devuelve `list[X]`, posiblemente vacía): nunca `None`, lista vacía.
- **Aggregating query** (`count_`, `sum_`, `max_`): devuelve escalar.

**Archetypes relacionados**: [Repository](#21-repository) (encapsula múltiples getters), [Cache layer](#11-helper--utility--pure-function) (cache.get_json es getter sobre Redis).

**Anti-pattern**: getter que MUTA (e.g. "get_or_create_user" que crea si no existe). Mejor split: `get_user` + `create_user_if_missing`. El nombre miente.

---

### 6. Setter / Writer / Mutator / Command

**Sinónimos**: command (CQRS), action, mutation (GraphQL), persister.

**Signature pattern**:

```python
async def create_X(payload, db) -> X
async def update_X(id, payload, db) -> X
async def delete_X(id, db) -> None
```

**Cómo identificarlo visualmente**:

- Nombre `create_`, `update_`, `delete_`, `save_`, `insert_`, `set_`, `apply_`
- Modifica state (DB, cache, file, external API)
- Suele requerir transaction (`commit`/`rollback`)
- Devuelve la entidad post-cambio (o `None` para delete)

**Qué hace**: cambia el mundo. NO idempotente por defecto (crear 2 veces = 2 entidades; salvo que la primary key constraint lo impida).

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/routers/contacts.py
@router.put("/{contact_id}", response_model=Contact)
async def update_contact(
    contact_id: int,
    payload: ContactUpdate,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContactORM:
    contact = await db.get(ContactORM, contact_id)
    if contact is None or contact.user_id != current_user.id:
        raise HTTPException(status_code=404, ...)

    contact.name = payload.name
    contact.phone = payload.phone
    contact.email = payload.email
    await db.commit()
    await db.refresh(contact)

    await cache.invalidate(f"contact:{contact_id}")
    await cache.invalidate_pattern(f"contacts:user:{current_user.id}:*")
    return contact
```

Tres setters encadenados: ORM mutation, cache invalidate single, cache invalidate pattern.

**Variantes**:
- **Create** (`POST`): crea, devuelve nuevo entity con id asignado.
- **Update** (`PUT` reemplaza completo / `PATCH` parcial): muta existente.
- **Delete** (`DELETE`): borra. Devuelve `None` (HTTP 204) o el entity borrado.
- **Upsert** (`MERGE` SQL, `set with overwrite`): create o update según exista.

**Archetypes relacionados**: [Side-effect handler](#8-side-effect-handler) (setter que escribe a sistema externo), [Cleanup](#14-cleanup--teardown--close).

**Anti-pattern**: setter sin invalidar cache asociado → reads stale. Tu `update_contact` lo hace bien; un junior se olvidaría del `invalidate_pattern`.

---

### 7. Predicate / Checker / Guard

**Sinónimos**: tester, predicate function, boolean returner.

**Signature pattern**:

```python
def is_X(value) -> bool
def has_X(value) -> bool
def can_X(actor, resource) -> bool
```

**Cómo identificarlo visualmente**:

- Nombre `is_`, `has_`, `can_`, `should_`, `matches_`, `contains_`
- Return type estricto `bool` (no `bool | None`)
- Sin side effects (idealmente)
- Body suele ser un solo `return expr` o `if/return`

**Qué hace**: responde una pregunta sí/no sobre un dato. Reusable en `if`, `filter`, `assert`.

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/auth.py
def verify_password(plain: str, hashed: str) -> bool:
    """Compara plaintext con hash. Resistente a timing attacks."""
    return pwd_context.verify(plain, hashed)
```

Y el check inline en handler:

```python
# 04_phone_book_cache_observability/server/app/routers/contacts.py
if contact is None or contact.user_id != current_user.id:
    raise HTTPException(status_code=404, ...)
```

Esa expresión es un predicate compuesto inline. En un proyecto más grande lo extraerías a `def can_user_access_contact(user, contact) -> bool`.

**Variantes**:
- **Pure predicate** (sin I/O): `is_valid_email`, `is_palindrome`.
- **I/O predicate** (`async def`): `await user_exists_in_db(email)`. A veces signo de mal diseño (mejor un getter + check).
- **Authorization predicate**: `can_user_edit(user, resource)` — base del patrón policy.

**Archetypes relacionados**: [Validator](#3-validator) (validator raises, predicate returns bool), [Strategy](#16-strategy--policy) (policy = predicate sobre permisos).

**Anti-pattern**: predicate que devuelve `bool | None` (3-state). Hace ambiguo el `if not is_X(...)`. Refactor a 2 funciones o a un Enum.

---

### 8. Side-effect handler

**Sinónimos**: emitter, publisher, sender, notifier, dispatcher.

**Signature pattern**:

```python
async def send_email(to, subject, body) -> None
async def publish_event(topic, payload) -> None
async def write_log(level, message) -> None
def emit_metric(name, value) -> None
```

**Cómo identificarlo visualmente**:

- Verbo de acción externa: `send_`, `publish_`, `emit_`, `notify_`, `dispatch_`, `log_`, `track_`
- Return type `None` (a veces `bool` para success/fail)
- Cuerpo toca I/O externo (red, FS, cola, métrica)

**Qué hace**: comunica cambios al mundo fuera del proceso. Por definición no es puro.

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/routers/auth.py
log.warning("register_duplicate_email", email=payload.email)
log.info("user_registered", user_id=new_user.id, email=new_user.email)
log.warning("login_failed", email=form_data.username)
```

Cada call a `log.X` es un Side-effect handler que escribe a stdout (vía structlog → JSON o pretty). En producción esos logs los recoge tu agregador (Loki/ELK).

Otro: el correlation middleware bindea contextvars (side effect):

```python
# 04_phone_book_cache_observability/server/app/observability/middleware.py
structlog.contextvars.bind_contextvars(request_id=request_id)
```

**Variantes**:
- **Fire-and-forget**: no espera ack (`background_tasks.add_task` en FastAPI).
- **Synchronous side effect**: bloquea hasta confirmación (write a DB).
- **Idempotent side effect**: repetirlo no daña (set Redis key with same value).

**Archetypes relacionados**: [Setter](#6-setter--writer--mutator--command) (setter es side effect sobre tu DB), [Coordinator](#20-coordinator--orchestrator--service) (suele encadenar varios side effects).

**Anti-pattern**: side effect dentro de un getter. Hace logs/métricas/emails NO determinísticos respecto al call graph. "Just fixed a bug, why is it sending double emails?" → porque el getter envía email.

---

### 9. Wrapper / Decorator / Middleware

**Sinónimos**: interceptor, filter (Servlet), aspect (AOP), HOF (higher-order function).

**Signature pattern** (3 formas equivalentes):

```python
# Decorator clásico Python
def deco(fn): @wraps(fn) def wrapper(*a, **kw): ...; return wrapper

# Middleware HTTP (FastAPI/Starlette)
async def dispatch(self, request: Request, call_next) -> Response

# Functional composition (Go-style)
func mw(next http.Handler) http.Handler
```

**Cómo identificarlo visualmente**:

- Recibe una función/handler como argumento, devuelve otra función
- En FastAPI: clase que hereda `BaseHTTPMiddleware` con método `dispatch(request, call_next)`
- En Python plain: función con `@functools.wraps(fn)` interno
- Vive en `middleware.py`, `decorators.py`, `interceptors/`

**Qué hace**: añade comportamiento ANTES y/o DESPUÉS de la función envuelta sin contaminarla. Lógica transversal: logging, auth, rate limit, metrics. Ver para profundizar.

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/observability/middleware.py
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.monotonic()
        response = await call_next(request)
        latency_ms = round((time.monotonic() - start) * 1000, 2)
        log.info("http_request",
                 method=request.method,
                 path=request.url.path,
                 status_code=response.status_code,
                 latency_ms=latency_ms)
        return response
```

Patrón cebolla: antes (medir tiempo) → `call_next` (ejecutar resto) → después (log).

Decorator clásico: `@limiter.limit(LIMIT_LOGIN)` en `routers/auth.py` envuelve el handler login añadiendo rate-check.

**Variantes**:
- **HTTP middleware** (global): se aplica a todas las requests.
- **Decorator** (per-function): solo en handlers marcados.
- **Interceptor** (gRPC, Java): equivalente fuera de HTTP.

**Archetypes relacionados**: [Side-effect handler](#8-side-effect-handler) (lo que el middleware hace en el "antes/después"), [Lifecycle hook](#13-lifecycle-hook).

**Anti-pattern**: middleware con business logic ("si es admin, X; si es user normal, Y"). Eso es responsabilidad del handler/service, no del plumbing.

---

### 10. Factory / Builder / Constructor helper

**Sinónimos**: maker, creator, instance method `create`.

**Signature pattern**:

```python
def make_X(args...) -> X
def build_X(args...) -> X
def X.from_Y(y: Y) -> X     # alternative constructor
class XBuilder: def with_a(...).with_b(...).build() -> X
```

**Cómo identificarlo visualmente**:

- Nombre `make_`, `build_`, `create_` (cuando NO escribe a DB), `from_*`
- Devuelve una INSTANCIA (no un side effect)
- Encapsula lógica de construcción no trivial (defaults, validación, polimorfismo)

**Qué hace**: simplifica creación de objetos complejos. Esconde detalles del constructor (params opcionales, polimorfismo según input).

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/auth.py
def _create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    """Helper común para crear tokens. Devuelve el JWT firmado."""
    expire = datetime.now(UTC) + expires_delta
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(UTC).timestamp()),
        "type": token_type,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(subject: str | int) -> str:
    return _create_token(
        subject=str(subject),
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )
```

`_create_token` es Factory genérico; `create_access_token` y `create_refresh_token` son Factories especializadas que delegan en él. Patrón común: factory privado + factories públicos curados.

**Variantes**:
- **Simple factory function**: `def make_X(args) -> X`.
- **Builder pattern** (encadenable): `Builder().with_a().with_b().build()`. Útil cuando hay 10+ params opcionales.
- **Abstract Factory**: factory que devuelve UNO de varios tipos según input.
- **Alternative constructor** (`from_dict`, `from_yaml`): clasmethod que parsea otro formato.

**Archetypes relacionados**: [Transformer](#4-transformer--mapper) (`from_dict` es factory + transformer), [Initializer](#12-initializer--setup--bootstrap) (factory crea, initializer prepara estado global).

**Anti-pattern**: factory que también persiste a DB. Mezcla creación con setter — confuso. Separa: `build_X(...) -> X` puro + `repo.save(x)` setter.

---

### 11. Helper / Utility / Pure function

**Sinónimos**: util, helper, common.

**Signature pattern**:

```python
def fn(a, b, c) -> result   # generalmente pequeña, sin side effects
```

**Cómo identificarlo visualmente**:

- Vive en `utils.py`, `helpers/`, `common/`
- 1-15 líneas de cuerpo
- Sin I/O, sin estado mutable
- Reusable desde muchos sitios

**Qué hace**: cálculo o transformación de uso general que no merece un módulo propio.

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/auth.py
def hash_password(plain: str) -> str:
    """Hashea un password en plaintext. Devuelve el hash (incluye salt + params)."""
    return pwd_context.hash(plain)
```

Una línea, sin estado, reusable. Helper canónico.

```python
# 02_phone_book_postgres/client/cli.py
def print_table(contacts: list[dict]) -> None:
    if not contacts:
        print("(no contacts)")
        return
    print(f"{'ID':<4} | {'NAME':<25} | ...")
    ...
```

Helper de presentación. Hace I/O (`print`) pero es trivial y reusable.

**Variantes**:
- **Pure helper** (sin I/O): canónico.
- **Effectful helper** (print, log): aceptable si el side effect es trivial.
- **Generic helper** (typing genérico): `def first[T](items: list[T]) -> T | None`.

**Archetypes relacionados**: [Transformer](#4-transformer--mapper) (transformer es un helper especializado), [Predicate](#7-predicate--checker--guard).

**Anti-pattern**: módulo `utils.py` con 50 funciones inconexas. Cuando crece, particiona por tema (`text_utils.py`, `time_utils.py`).

---

### 12. Initializer / Setup / Bootstrap

**Sinónimos**: configure, setup, init, bootstrap.

**Signature pattern**:

```python
def configure_X() -> None
async def init_X() -> X
def setup_X(app) -> None
```

**Cómo identificarlo visualmente**:

- Nombre `configure_`, `init_`, `setup_`, `bootstrap_`
- Llamado UNA vez al startup
- Modifica estado global o devuelve singleton
- Suele estar en `main.py` cerca del top-level

**Qué hace**: deja el sistema listo para operar. Crea singletons, registra handlers, lee config, valida pre-requisitos.

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/observability/logging.py
def configure_logging() -> None:
    """Inicializa structlog. Llamado UNA vez en main.py al startup."""
    processors_shared = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        ...
    ]
    structlog.configure(processors=processors_shared + [renderer], ...)
```

Y la inicialización del cliente Redis:

```python
# 04_phone_book_cache_observability/server/app/infra/redis.py
async def init_redis() -> aioredis.Redis:
    global _redis_client
    _redis_client = aioredis.from_url(REDIS_URL, ...)
    await _redis_client.ping()   # sanity check
    return _redis_client
```

Llamado desde el lifespan al startup.

**Variantes**:
- **Sync init** (`configure_logging`): cuando no toca I/O.
- **Async init** (`init_redis`): cuando hay handshake con servicio externo.
- **Idempotent init** (DB schema create_all): seguro re-llamar.
- **One-shot init** (set global var): explota si llamado 2 veces.

**Archetypes relacionados**: [Lifecycle hook](#13-lifecycle-hook) (lifespan llama a Initializers), [Factory](#10-factory--builder--constructor-helper), [Cleanup](#14-cleanup--teardown--close) (su contraparte).

**Anti-pattern**: initializer con efectos sobre import del módulo (top-level code que toca DB). Imposible testear. Hazlo función explícita.

---

### 13. Lifecycle hook

**Sinónimos**: lifespan, on_startup/on_shutdown, hook, event handler (en framework lifecycle).

**Signature pattern**:

```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    ...
    yield
    # shutdown
    ...
```

**Cómo identificarlo visualmente**:

- Decorador `@asynccontextmanager` en FastAPI moderno
- Argumento es la app/contexto
- Generador con UN solo `yield` separando startup/shutdown
- Vive en `main.py` o `app.py`

**Qué hace**: ejecuta código en momentos especiales del ciclo de vida del proceso (arranque, parada, primera request, etc.). Antes era `@app.on_event("startup")` y `@app.on_event("shutdown")`; ahora un solo `lifespan`.

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log.info("startup", service="phone-book", version="0.4.0")
    await init_redis()
    log.info("redis_initialized")
    yield
    log.info("shutdown")
    await close_redis()
```

Estructura canónica: log → initializers → `yield` → log → cleanups.

**Variantes**:
- **FastAPI lifespan** (async context manager): moderno.
- **Decorador `@app.on_event("startup")`**: legacy FastAPI.
- **Spring `@PostConstruct` / `@PreDestroy`**: equivalente Java.
- **Per-request lifecycle** (`before_request` Flask, middleware): ver [Middleware](#9-wrapper--decorator--middleware).

**Archetypes relacionados**: [Initializer](#12-initializer--setup--bootstrap) (lifespan los orquesta), [Cleanup](#14-cleanup--teardown--close).

**Anti-pattern**: lifespan que falla silencioso. Si `init_redis()` raises y no lo capturas, FastAPI igual arranca pero los handlers explotan. Mejor: `init_redis()` con `ping` que crashea explícito al startup.

---

### 14. Cleanup / Teardown / Close

**Sinónimos**: dispose, shutdown, finalize, release.

**Signature pattern**:

```python
async def close_X() -> None
def dispose_X() -> None
def __exit__(...) -> None        # context manager
async def __aexit__(...) -> None # async context manager
```

**Cómo identificarlo visualmente**:

- Nombre `close_`, `shutdown_`, `dispose_`, `release_`, `cleanup_`
- Return `None`
- Body: cierra socket, libera lock, vacía buffer, llama `.close()` en algo
- Llamado desde lifespan shutdown o `finally:` o `__aexit__`

**Qué hace**: libera recursos. Sin esto: connection leak, file descriptors agotados, locks colgados.

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/infra/redis.py
async def close_redis() -> None:
    """Cierra la conexión Redis. Llamado en lifespan shutdown."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
```

Defensivo: chequea no-None antes de cerrar (idempotente).

Y el cleanup implícito del `get_db` (después del yield):

```python
# 04_phone_book_cache_observability/server/app/dependencies.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        # ← cleanup automático aquí: __aexit__ del async with cierra session
```

**Variantes**:
- **Manual close** (`close_X()`): hay que llamarlo explícito.
- **Context manager** (`with`/`async with`): cleanup automático al salir del bloque.
- **Finalizer** (`__del__`): no fiable en Python, evítalo.

**Archetypes relacionados**: [Initializer](#12-initializer--setup--bootstrap) (su par), [Lifecycle hook](#13-lifecycle-hook).

**Anti-pattern**: cleanup que asume estado válido. Si init falló a medias y luego se llama close, suele explotar. Defensivo: `if x is not None: x.close()`.

---

### 15. Adapter / Bridge / Anti-corruption layer

**Sinónimos**: adapter (GoF), wrapper, bridge, ACL (DDD).

**Signature pattern**:

```python
class XAdapter:
    def __init__(self, third_party_lib): ...
    def my_clean_method(self, ...) -> MyType:
        return self._lib.weird_legacy_call(...)   # traducción
```

**Cómo identificarlo visualmente**:

- Clase con nombre `XAdapter`, `XClient`, `XGateway`, `XBridge`
- Wraps una librería externa o sistema legacy
- Expone API limpia que oculta la fea de adentro
- Vive en `adapters/`, `infra/`, `clients/`

**Qué hace**: traduce entre TU modelo de dominio y un sistema externo (API de terceros, DB legacy, librería con API hostil). Defiende tu codebase de cambios externos.

**Ejemplo de tus proyectos**:

Tu `app/services/cache.py` actúa como adapter sobre `redis.asyncio`:

```python
# 04_phone_book_cache_observability/server/app/services/cache.py
async def get_json(key: str) -> Any | None:
    client = get_redis()
    if client is None:
        return None
    try:
        raw = await client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except (RedisError, json.JSONDecodeError) as e:
        log.warning("cache_get_failed", key=key, error=str(e))
        return None
```

Tu code llama `cache.get_json(key)` — una API limpia tipada. Internamente traduce: bytes Redis → JSON → Python dict, y mapea fallos Redis a `None` (degradación graciosa). Si mañana migras a Memcached, solo cambia este módulo.

`oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")` también es un adapter — adapta el `Authorization: Bearer X` header a un argumento de dependency.

**Variantes**:
- **Object adapter** (composition): el adapter contiene la dependency externa.
- **Class adapter** (inheritance): el adapter HEREDA de la dependency externa. Menos común, frágil.
- **Anti-corruption layer** (DDD): adapter rico que protege bounded context entero.

**Archetypes relacionados**: [Transformer](#4-transformer--mapper) (adapter usa transformers internos), [Repository](#21-repository) (repo es adapter sobre la DB).

**Anti-pattern**: adapter que filtra tipos de la librería externa (return type es `redis.Response`). Defeats the purpose — cualquier consumidor depende de Redis igualmente.

---

### 16. Strategy / Policy

**Sinónimos**: policy (sec/auth), algorithm, behavior.

**Signature pattern**:

```python
class StrategyA: def execute(self, input) -> output: ...
class StrategyB: def execute(self, input) -> output: ...   # misma firma

# o funcional:
def strategy_a(input) -> output
def strategy_b(input) -> output
chosen = strategy_a if condition else strategy_b
```

**Cómo identificarlo visualmente**:

- Múltiples implementaciones con MISMA signature
- Selección runtime (a veces vía dict de strategies, a veces dependency injection)
- Nombre con `Policy`, `Strategy`, `Algorithm`, sufijos `Renderer`, `Encoder`

**Qué hace**: encapsula UNA forma de hacer algo, intercambiable con otras formas. El llamador no sabe cuál tiene; le da igual.

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/observability/logging.py
if APP_ENV == "prod":
    renderer = structlog.processors.JSONRenderer()
else:
    renderer = structlog.dev.ConsoleRenderer(colors=True)
```

`JSONRenderer` y `ConsoleRenderer` son strategies de renderizado de logs, intercambiables. Se selecciona runtime según `APP_ENV`. El resto del código no sabe cuál se está usando.

Otro: `pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")` — passlib selecciona la strategy de hashing. Si mañana añades `["argon2", "bcrypt"]`, soporta verificación con ambas.

**Variantes**:
- **OO strategy** (clases con interfaz común): canónico GoF.
- **Functional strategy** (funciones de primera clase): más Pythónico.
- **Plug-in strategy** (registro dinámico): `strategies.register("foo", FooStrategy)`.

**Archetypes relacionados**: [Predicate](#7-predicate--checker--guard) (auth policy = predicate), [Adapter](#15-adapter--bridge) (a veces overlap).

**Anti-pattern**: 15 strategies con `if isinstance(s, FooStrategy):` en el caller. Eso defeats polymorphism — refactor a método virtual.

---

### 17. Pipeline stage / Processor

**Sinónimos**: stage, step, processor, transformer (en sentido de pipeline).

**Signature pattern**:

```python
def stage(input: Input) -> Output    # output del stage N = input del stage N+1
```

**Cómo identificarlo visualmente**:

- Cada stage tiene MISMA "shape" (entra X, sale Y) para componer
- Suelen vivir en una lista o ser invocados en orden por un coordinator
- Nombre relacionado con la fase: `parse_`, `validate_`, `enrich_`, `render_`

**Qué hace**: una transformación atómica que se compone con otras para formar un pipeline (ETL, request processing, build chain).

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/observability/logging.py
processors_shared = [
    structlog.contextvars.merge_contextvars,    # stage 1: añadir contextvars
    structlog.processors.add_log_level,         # stage 2: añadir nivel
    structlog.processors.TimeStamper(fmt="iso", utc=True),  # stage 3: timestamp
    structlog.processors.StackInfoRenderer(),   # stage 4: stack si hay
    structlog.processors.format_exc_info,       # stage 5: format exception
]
structlog.configure(processors=processors_shared + [renderer], ...)
```

Cada processor es un Pipeline stage. structlog ejecuta la lista en orden, pasando el dict de log entre ellos. Misma forma: `def processor(logger, method_name, event_dict) -> event_dict`.

**Variantes**:
- **Linear pipeline** (lista plana): canónico.
- **DAG pipeline** (Airflow, Dagster): stages con dependencias en grafo.
- **Streaming pipeline** (Kafka, Flink): cada stage procesa un flujo continuo.

**Archetypes relacionados**: [Transformer](#4-transformer--mapper) (cada stage es transformer), [Middleware](#9-wrapper--decorator--middleware) (middleware = pipeline stage HTTP).

**Anti-pattern**: stages con side effects ocultos que rompen reordenado. Los stages deben ser declarativos (orden importa pero por DATA, no por hidden coupling).

---

### 18. Aggregator / Reducer

**Sinónimos**: collector, summarizer, fold, reduce.

**Signature pattern**:

```python
def fn(items: Iterable[X]) -> Y     # combina muchos en uno
```

**Cómo identificarlo visualmente**:

- Input plural (lista, iterable, queryset), output singular
- Nombre `count_`, `sum_`, `total_`, `aggregate_`, `summarize_`, `combine_`, `merge_`
- A menudo usa `functools.reduce`, `sum`, `max`, `min`, group-by

**Qué hace**: colapsa una colección en un valor (escalar, struct, otra lista más corta).

**Ejemplo de tus proyectos**:

No tienes aggregators puros explícitos en estos proyectos (CRUD no los necesita), pero el patrón aparece implícito en cualquier `COUNT(*)` query SQL. Ejemplo conceptual sobre tus contacts:

```python
# Hipotético service en future state
async def count_contacts_by_user(db: AsyncSession) -> dict[int, int]:
    stmt = select(ContactORM.user_id, func.count()).group_by(ContactORM.user_id)
    result = await db.execute(stmt)
    return dict(result.all())
```

Y un caso real, pero no en backend: `print_table` recibe lista de contactos y produce **una representación textual única** — es un aggregator de strings.

```python
# 02_phone_book_postgres/client/cli.py
def print_table(contacts: list[dict]) -> None:
    ...
```

**Variantes**:
- **Pure reducer**: `sum`, `max`, `min`.
- **Group-by aggregator**: devuelve dict `{key: aggregated}`.
- **Streaming aggregator**: actualiza estado por cada nuevo item (online stats).

**Archetypes relacionados**: [Iterator](#19-iterator--generator--stream) (genera los items que reducer combina), [Transformer](#4-transformer--mapper).

**Anti-pattern**: aggregator que ordena toda la lista en memoria cuando solo necesitas el max. `max(items)` en streaming, no `sorted(items)[-1]`.

---

### 19. Iterator / Generator / Stream

**Sinónimos**: yielder, lazy sequence, cursor.

**Signature pattern**:

```python
def fn(...) -> Iterator[X]               # generator function (usa yield)
async def fn(...) -> AsyncGenerator[X, None]
```

**Cómo identificarlo visualmente**:

- Cuerpo contiene `yield` (Python) o `yield return` (C#)
- Return type es `Iterator`, `Generator`, `AsyncGenerator`, `AsyncIterator`
- Caller la consume con `for x in fn()` o `async for x in fn()`

**Qué hace**: produce items perezosamente. No carga todos en memoria. Útil para streams grandes, paginación, generación infinita.

**Ejemplo de tus proyectos**:

`get_db` es técnicamente un async generator (yield una vez, pero la firma lo es):

```python
# 04_phone_book_cache_observability/server/app/dependencies.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

FastAPI lo consume como dependency con cleanup automático post-yield.

Y un async iterator real, en cache invalidation:

```python
# 04_phone_book_cache_observability/server/app/services/cache.py
async def invalidate_pattern(pattern: str) -> int:
    keys = []
    async for key in client.scan_iter(match=pattern):   # ← async iterator
        keys.append(key)
    if keys:
        return await client.delete(*keys)
```

`client.scan_iter(...)` es un async iterator que pagina internamente Redis SCAN, evitando cargar millones de keys en memoria.

**Variantes**:
- **Sync generator** (`yield`): clásico.
- **Async generator** (`async def` + `yield`): para I/O.
- **Generator expression** (`(x for x in items if cond)`): inline lazy.
- **Coroutine-as-iterator** (async generator dependency en FastAPI).

**Archetypes relacionados**: [Pipeline stage](#17-pipeline-stage--processor) (generator es source de pipeline), [Dependency](#2-dependency--provider) (async generator dependency con cleanup).

**Anti-pattern**: `list(generator())` para todo. Pierdes el beneficio de lazy. Solo materializa cuando lo necesitas (e.g. response model espera lista).

---

### 20. Coordinator / Orchestrator / Service

**Sinónimos**: service, use case, application service, interactor (Clean Architecture), workflow.

**Signature pattern**:

```python
async def do_X(input, db, cache, ...) -> result:
    # 1. validate
    # 2. fetch entities
    # 3. apply business rules
    # 4. persist
    # 5. fire events
```

**Cómo identificarlo visualmente**:

- Nombre del verbo de negocio (no técnico): `register_user`, `process_order`, `cancel_subscription`
- Cuerpo llama a 3+ otras funciones (getters, setters, validators, side effects)
- Vive en `services/`, `use_cases/`, `application/`
- Más larga que un handler (puede ser 30-80 líneas legítimas)

**Qué hace**: orquesta el caso de uso. Es el "verbo de tu dominio". Llama primitivas, mantiene la transactionalidad, decide el flujo.

**Ejemplo de tus proyectos**:

En `04_phone_book_cache_observability` la lógica de negocio aún vive en handlers (es un proyecto pequeño), pero el handler `update_contact` ya hace de mini-coordinator:

```python
# 04_phone_book_cache_observability/server/app/routers/contacts.py
async def update_contact(
    contact_id: int,
    payload: ContactUpdate,
    current_user: UserORM = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContactORM:
    contact = await db.get(ContactORM, contact_id)               # 1. fetch
    if contact is None or contact.user_id != current_user.id:    # 2. authorize
        raise HTTPException(status_code=404, ...)

    contact.name = payload.name                                  # 3. mutate
    contact.phone = payload.phone
    contact.email = payload.email
    await db.commit()
    await db.refresh(contact)

    await cache.invalidate(f"contact:{contact_id}")              # 4. invalidate cache
    await cache.invalidate_pattern(f"contacts:user:{current_user.id}:*")
    log.info("contact_updated", contact_id=contact_id, user_id=current_user.id)  # 5. emit
    return contact
```

5 pasos, 5 responsabilidades. En un proyecto bigger, esto vive en `services/contacts.py::update_contact_for_user(...)` y el handler solo invoca el service y traduce excepciones a HTTP.

**Variantes**:
- **Service object** (clase con state): `class UserService: ...`
- **Use case function** (función pura coordinadora): `async def register_user(...)`
- **Saga** (multi-step distributed transaction con compensation): para sistemas distribuidos.

**Archetypes relacionados**: TODOS los demás. El coordinator es el "verbo principal" que orquesta a getters, setters, validators, side effects. [Repository](#21-repository) es su brazo de persistencia.

**Anti-pattern**: coordinator que NO hace nada (pasa-through trivial al repo). Si no hay lógica, no aporta capa — borra y deja al handler llamar al repo directo.

---

### 21. Repository

**Sinónimos**: DAO (Data Access Object), data mapper.

**Signature pattern**:

```python
class XRepo:
    def __init__(self, db): ...
    async def get(self, id) -> X | None
    async def list(self, filters) -> list[X]
    async def save(self, entity: X) -> X
    async def delete(self, id) -> None
```

**Cómo identificarlo visualmente**:

- Clase con sufijo `Repository`, `Repo`, `DAO`, `Store`
- Métodos = operaciones CRUD sobre UNA entity
- Encapsula queries SQL/ORM
- Vive en `repositories/`, `dao/`, `infra/`

**Qué hace**: abstrae la persistencia. El service no sabe si es Postgres, Mongo o memory — habla con el repo. Permite mockear en tests fácilmente.

**Ejemplo de tus proyectos**:

Tus proyectos NO usan el patrón Repository explícito (los handlers hablan directo con SQLAlchemy via `db.get`, `db.execute`). Eso es **decisión consciente y correcta para proyectos pequeños** — el ORM ya es suficiente abstracción. Repository es valor añadido cuando:

- Tienes 5+ apps que comparten el mismo modelo
- Tests sin DB son críticos (mockeas el repo)
- La query lógica es compleja y reusable

Refactor hipotético de tus contacts:

```python
# Hipotético contacts_repo.py
class ContactsRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_for_user(self, contact_id: int, user_id: int) -> ContactORM | None:
        contact = await self.db.get(ContactORM, contact_id)
        if contact is None or contact.user_id != user_id:
            return None
        return contact

    async def list_for_user(self, user_id: int, sort_by: str) -> list[ContactORM]:
        ...
```

**Variantes**:
- **Repository pattern clásico** (clase con métodos por entity): canónico.
- **Generic repository** (`BaseRepo[X]` con CRUD genérico): cuando entities son uniformes.
- **Repository per aggregate** (DDD): un repo por root aggregate.

**Archetypes relacionados**: [Getter](#5-getter--reader--query) y [Setter](#6-setter--writer--mutator--command) (los métodos del repo SON getters/setters), [Coordinator](#20-coordinator--orchestrator--service) (coordinator usa repos).

**Anti-pattern**: repo que devuelve queryset/statement raw (SQLAlchemy Query). Defeats the purpose — el caller depende de la implementación. Devuelve entities limpias.

---

### 22. Healthcheck

**Sinónimos**: ping, status, liveness/readiness probe.

**Signature pattern**:

```python
@app.get("/health")
async def health() -> dict
@app.get("/ready")
async def ready() -> dict   # readiness con checks de DB/cache
```

**Cómo identificarlo visualmente**:

- Path `/health`, `/healthz`, `/ping`, `/status`, `/ready`
- Sin auth (o auth muy débil)
- Devuelve dict simple `{"status": "ok"}` o detalle de subsistemas
- Llamado por load balancers, Kubernetes, monitoring

**Qué hace**: indica al orquestador si el proceso está vivo (liveness) y/o listo para servir tráfico (readiness). Sin esto: K8s no sabe cuándo reiniciar, LB enruta a instancias muertas.

**Ejemplo de tus proyectos**:

```python
# 04_phone_book_cache_observability/server/app/routers/meta.py
@router.get("/")
async def root() -> dict:
    return {"status": "ok", "service": "phone-book", "version": "0.4.0"}
```

Healthcheck minimal: solo dice "estoy vivo". No comprueba DB ni Redis.

**Variantes**:
- **Liveness check** (¿estoy vivo?): trivial, devuelve 200. Si falla, K8s reinicia.
- **Readiness check** (¿puedo servir?): chequea DB, Redis, dependencias. Si falla, K8s no enruta tráfico (pero NO reinicia).
- **Deep health** (`/health/detailed`): expone estado de cada subsistema. NO público (info leak).

**Archetypes relacionados**: [Handler](#1-handler--route-handler--controller) (es un handler especializado).

**Anti-pattern**: health check que hace queries pesadas a DB en CADA llamada. K8s puede llamarlo cada 5s — cuidado con la carga. Mejor: cachea el resultado 1-5s.

---

## Comparación cruzada — diferenciar pares confusos

| Confusión común | Diferencia clave |
|---|---|
| Validator vs Predicate | Validator raises si mal; Predicate devuelve `bool`. Mismo concepto, distinta convención de comunicación de fallos. |
| Getter vs Repository | Getter es UNA función; Repository es CLASE con muchos getters/setters relacionados a UNA entity. |
| Setter vs Side-effect handler | Setter cambia TU state (DB, cache); Side-effect handler comunica con OTRO sistema (email, métrica, log). |
| Middleware vs Decorator | Middleware = global por request HTTP; Decorator = per-function granular. En FastAPI, **Dependency suele ser mejor que Middleware** para auth (mantiene Swagger + typing). |
| Initializer vs Lifecycle hook | Initializer = la función que prepara algo; Lifecycle hook = el slot del framework donde se llama (lifespan, startup, shutdown). |
| Coordinator vs Handler | Handler traduce HTTP↔dominio; Coordinator orquesta el caso de uso. En proyectos pequeños se fusionan; en grandes se separan. |
| Adapter vs Transformer | Transformer = pura conversión A→B; Adapter = clase rica con varios métodos que defienden tu dominio de un sistema externo. |
| Pipeline stage vs Strategy | Pipeline stage = se EJECUTA en orden con otros (pipeline lineal); Strategy = se SELECCIONA entre alternativas (una vez). |

## Diagrama mental — call graph típico de una request

```
            ┌─────────────────────────────┐
            │  Middleware (correlation, log, rate)   │  archetype 9
            └──────────────┬──────────────┘
                           ▼
            ┌─────────────────────────────┐
            │  Handler (router endpoint)  │  archetype 1
            └──────────────┬──────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Dependency  Validator    Coordinator/Service
          (get_db,    (Pydantic)        archetype 20
          get_user)   archetype 3              │
          archetype 2                          │
                                               ▼
                              ┌────────────────┼────────────────┐
                              ▼                ▼                ▼
                        Repository / Getter  Setter      Side-effect
                        archetype 21,5       archetype 6 archetype 8
                              │                │                │
                              ▼                ▼                ▼
                          Adapter (DB,    Adapter (DB)    Adapter (mail,
                          cache, ext API)                  queue, métrica)
                          archetype 15                     archetype 15
```

Casi cualquier request en cualquier backend tiene esta forma. Si reconoces los archetypes, puedes navegar el código de un proyecto nuevo en MINUTOS, no días.

## Drill de entrenamiento (rutina de 2 semanas)

1. **Semana 1 — predicción asistida**: abre un router de tu `04_phone_book_cache_observability`. Para cada función:
   - Lee SOLO el decorador y la signature (1ª línea). Tapa el body.
   - Predice: archetype, qué hace en 1 frase, qué devuelve, qué errores puede lanzar.
   - Destapa y compara. Anota desviaciones.
2. **Semana 2 — codebase ajeno**: abre un repo OSS Python (FastAPI ejemplos, sqlalchemy/example, etc.). Mismo drill.
3. **Test final**: dado un endpoint que NUNCA viste, sin leer el body, ¿puedes describir su archetype, side effects esperados y los archetypes con los que probablemente colabora? Si sí: cruzaste a Proficient en la dimensión "lectura backend".

## Conexiones

- [[MOC_Programacion]]
- (el doc de project 04 que profundiza el archetype 9)
- (cómo se organizan archivos llenos de archetype 1)

## Resumen mental

> Veintidós archetypes cubren el 95% de funciones que vas a leer en cualquier backend. Para entrenar reconocimiento automático: lee la signature ANTES del body y predice el archetype, qué efectos tiene y con quién colabora; luego comprueba. Cuando aciertes el 80% en código nunca visto, has cruzado el threshold Competent→Proficient en lectura de backend — ya operas con chunks de capa 1, no parseas tokens. Los archetypes vienen en familias relacionadas (handler↔dependency↔validator↔coordinator↔repo) y en pares duales (initializer/cleanup, getter/setter, middleware/decorator). El call graph canónico es: Middleware → Handler → Dependency → Coordinator → (Validator + Repository + Side-effect). Reconócelo de un vistazo y leerás 10x más rápido sin perder comprensión.
