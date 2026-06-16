---
title: Programación — Glosario propio (definir y relacionar)
date: 2026-05-18
tags: [programacion/referencia, programacion, glosario, vocabulario]
type: glosario
status: vivo
source: claude-code
aliases: [Glosario Programación]
---

# Glosario de Programación — definir y relacionar

> **Para qué existe**: sabes *usar* las cosas pero no *definirlas ni
> relacionarlas* con seguridad. Este glosario es el léxico: una definición
> corta por término + **con qué se relaciona** (lo importante) + dónde está
> explicado a fondo. No re-explica: enlaza a los `docs/` del proyecto.
>
> **Cómo usarlo**: búscalo por letra (alfabético) o por el grafo de Obsidian.
> Lee la entrada, y antes de mirar `Relaciones` intenta tú decir con qué se
> conecta — ese es el músculo que estás entrenando. Si una entrada no te basta,
> abre `Se explica a fondo en`.
>
> Esquema de cada entrada:
> - **Qué es**: definición directa, 1–3 frases.
> - **Para qué**: qué problema resuelve (separa el *qué* del *para qué*).
> - **Relaciones**: con verbos tipados (*se apoya en · se confunde con · es un caso de · lo usa*). `` salta dentro de este glosario.
> - **Categoría** · **Se explica a fondo en**: doc del proyecto, o "canónica aquí".
>
> Complementa (no duplica) el banco de preguntas
>: el
> glosario *define*; el Mastery Bank *verifica que lo entiendes*.

---

## Índice de términos

> Lista rápida. En Obsidian cada palabra es clicable y salta a su entrada.
> **Parte 1** (Booking, alfabético, 97 términos) abajo + **21 sub-variantes**
> con ancla propia · **Parte 2** (CS
> Fundamentos, por área): · · · · · · · · · · **** (Telemetría, 91 términos por subsistema: almacenamiento · Kafka · Airflow · Faust · feature eng. · anomalías · forecasting · MLflow · drift · escala · back-pressure · retención)

### Parte 1 — Booking (alfabético)

- **A**: · · · · · · · · · ·
- **B**: · · ·
- **C**: · · · · · · · · ·
- **D**: · · · · · ·
- **E**: · · · · ·
- **F**: · · ·
- **G**: ·
- **H**: · · ·
- **I**: · · · ·
- **J**: ·
- **K**:
- **L**:
- **M**: · · · · ·
- **N**: · ·
- **O**: ·
- **P**: · · · ·
- **Q**:
- **R**: · · · ·
- **S**: · · · · · ·
- **T**: · · · · ·
- **U**:
- **V**: ·
- **W**: ·
- **X · Y · Z**: —

**Sub-variantes** (caso concreto de una entrada general): · · · · · · · · · · · · · · · · · · · ·

---

## 🗺️ Mapa temático

> Navegación **por relaciones**, no por orden alfabético. Aquí los términos se agrupan por el problema que resuelven, para saltar entre conceptos que viven juntos en la práctica aunque estén lejos en el abecedario. El **orden alfabético / lookup sigue intacto más abajo** (desde `## A`); esto es solo un índice transversal de entrada.

- **Persistencia / BD**: · · · · · · · · · · · · · · · · · · · · · · · — → a fondo:
- **Consultas / índices / paginación**: · · · · · · · · · · · · · · · ·
- **Búsqueda full-text**: · · ·
- **Concurrencia y async**: · · · · · · · — → a fondo:
- **API / Web / HTTP**: · · · · · · · · · · · · · — → a fondo:
- **Auth / Seguridad**: · · · · · · · · · · — → a fondo:
- **Caching / rendimiento**: · · · · · — → a fondo:
- **Mensajería / streaming**: · · · · · · · (detalle por subsistema en Parte 3)
- **Resiliencia / transacciones distribuidas**: · · · · — → a fondo:
- **Testing**: · · · · · · · · ·
- **Infra / Docker**: · · · · · · · · · ·
- **Observabilidad**: · · ·
- **Arquitectura / patrones**: · · · · — → a fondo: ·
- **SO / arquitectura de computadores**: → a fondo: ·
- **Algoritmos**: → a fondo:
- **ML / datos time-series**: (almacenamiento, streaming, feature engineering, forecasting y MLOps con detalle por subsistema en Parte 3)

---

## A

### ACID
**Qué es**: las 4 garantías de una transacción de base de datos: Atomicidad (todo o nada), Consistencia (no rompe constraints), Aislamiento (transacciones concurrentes no se pisan) y Durabilidad (commit = persiste aunque caiga la luz).
**Para qué**: poder razonar sobre qué pasa cuando varias operaciones tocan la BD a la vez sin corromper datos.
**Relaciones**: es propiedad de · su "I" se gradúa con · lo garantiza un como · se rompe a propósito en **Eventual consistency** (sistemas distribuidos).
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#Transactions + ACID + isolation levels]]

### Alembic
**Qué es**: herramienta de *migraciones* para SQLAlchemy: versiona el esquema de la BD en scripts encadenados (`upgrade`/`downgrade`).
**Para qué**: cambiar el esquema de forma reproducible y reversible en todos los entornos (es "git para el esquema").
**Relaciones**: es a la BD lo que al código · genera/aplica · usa el de · su `env.py` se adapta para.
**Categoría**: Migraciones · **Se explica a fondo en**:

### API
**Qué es**: contrato por el que un programa expone funciones/datos a otros programas sin que conozcan su interior. En backend web suele ser HTTP+JSON.
**Para qué**: que clientes (frontend, otros servicios) usen tu lógica sin acoplarse a su implementación.
**Relaciones**: se concreta en s · suele seguir el estilo · viaja sobre · su forma de entrada/salida la valida un · NO es lo mismo que (API = puerta; BD = almacén).
**Categoría**: API/Web · **Se explica a fondo en**:

### API key
**Qué es**: cadena secreta que identifica/autentica a un cliente, enviada normalmente en una cabecera (`X-API-Key`).
**Para qué**: autenticar máquinas/servicios (no usuarios) de forma simple.
**Relaciones**: es una forma de más simple que · se confunde con (la API key no caduca ni lleva claims) · se suele combinar con.
**Categoría**: Auth/Seguridad · **Se explica a fondo en**: — canónica aquí (huérfano)

### Argon2
**Qué es**: algoritmo moderno de *hashing de contraseñas*, deliberadamente lento y con coste de memoria configurable; ganador del Password Hashing Competition.
**Para qué**: guardar contraseñas de forma que un atacante con la BD no pueda revertirlas ni hacer fuerza bruta barata.
**Relaciones**: es un caso de (one-way) · alternativa a bcrypt/scrypt/PBKDF2 · lo usa el flujo de · NO es cifrado (no se "desencripta").
**Categoría**: Auth/Seguridad · **Se explica a fondo en**:

### ASGI
**Qué es**: la interfaz estándar Python asíncrona entre un servidor web y una app (sucesor async de WSGI).
**Para qué**: que FastAPI/Starlette puedan manejar muchas conexiones concurrentes sin un hilo por request.
**Relaciones**: lo implementa el servidor (uvicorn) y lo consume · es la versión async de WSGI · habilita el modelo de la app · en tests se usa un transporte ASGI en memoria (sin red real).
**Categoría**: API/Web · **Se explica a fondo en**: — canónica aquí (huérfano)

### Async / await
**Qué es**: modelo de concurrencia cooperativa de Python: `async def` define una corrutina; `await` cede el control mientras espera I/O para que otra corrutina avance.
**Para qué**: atender miles de operaciones de I/O (DB, red) concurrentes en un solo hilo, sin bloquear.
**Relaciones**: se apoya en el · resuelve el · NO da paralelismo de CPU (eso es multiprocessing) · lo usan, async y `asyncpg`.
**Categoría**: Async/Concurrencia · **Se explica a fondo en**:

### AsyncEngine
**Qué es**: objeto de SQLAlchemy async que gestiona el *pool de conexiones* a la BD; se crea una vez por proceso al importar el módulo.
**Para qué**: hablar con Postgres de forma asíncrona reutilizando conexiones (no abrir una por request).
**Relaciones**: es el en versión async · contiene un · de él cuelga · atado al activo al importarse (origen del gotcha de tests).
**Categoría**: BD · **Se explica a fondo en**:

### AsyncSessionLocal
**Qué es**: *factory* (sessionmaker) que produce sesiones `AsyncSession` ligadas al `AsyncEngine`.
**Para qué**: obtener una unidad de trabajo (sesión) por request para hacer queries/commits.
**Relaciones**: lo crea · produce una · se entrega vía (yield-based) · usa `expire_on_commit=False` por diseño.
**Categoría**: BD · **Se explica a fondo en**:

### Autenticación
**Qué es**: probar *quién eres* (login, token válido).
**Para qué**: que el sistema sepa qué usuario hace la petición.
**Relaciones**: se confunde con (esa decide *qué puedes hacer*) · se implementa con o · su error típico es HTTP 401.
**Categoría**: Auth/Seguridad · **Se explica a fondo en**:

### Autorización
**Qué es**: decidir *qué puede hacer* un usuario ya autenticado (permisos/roles).
**Para qué**: que un usuario normal no pueda borrar recursos de admin.
**Relaciones**: viene después de · en Booking v0.1 se hace con un `is_admin: bool` simple · su error típico es HTTP 403.
**Categoría**: Auth/Seguridad · **Se explica a fondo en**:

## B

### Base de datos
**Qué es**: sistema que almacena, organiza y consulta datos de forma persistente y consistente. En Booking, una *relacional* (tablas con relaciones).
**Para qué**: que los datos sobrevivan al reinicio y se consulten/actualicen con garantías.
**Relaciones**: la *relacional* es un caso → / · se accede vía SQL o un · NO es una (BD = almacén; API = puerta) · se versiona su esquema con.
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#SCHEMA: el modelo relacional en 30 segundos]]

### Bearer token
**Qué es**: token que se envía en la cabecera `Authorization: Bearer <token>`; quien lo "porta" obtiene acceso.
**Para qué**: mandar la credencial en cada request sin reenviar usuario/contraseña.
**Relaciones**: el token suele ser un · "bearer" = sin prueba de posesión extra (por eso no debe filtrarse en URLs/logs) · lo emite el.
**Categoría**: Auth/Seguridad · **Se explica a fondo en**:

### Blocking I/O
**Qué es**: una operación de entrada/salida que detiene el hilo hasta completarse (p. ej. una query síncrona).
**Para qué**: entender por qué un servidor síncrono no escala bajo muchas conexiones.
**Relaciones**: lo opuesto es · el existe para evitarlo · meter código bloqueante en una corrutina mata el (anti-patrón).
**Categoría**: Async/Concurrencia · **Se explica a fondo en**:

## C

### Cache-aside
**Qué es**: patrón donde la app consulta primero la caché; si falla (miss) lee la BD, guarda en caché y devuelve.
**Para qué**: reducir latencia y carga de BD en lecturas repetidas.
**Relaciones**: usa como almacén · necesita (el problema difícil) · sufre · alternativa a read-through/write-through.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

### Cache stampede
**Qué es**: cuando una clave cacheada expira y miles de requests simultáneos van a la BD a la vez a regenerarla.
**Para qué**: anticipar un fallo de disponibilidad típico bajo carga.
**Relaciones**: es un riesgo de · se mitiga con locks/jitter de TTL · relacionado con.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

### CASCADE
**Qué es**: regla de una *foreign key* que propaga el borrado: borrar el padre borra los hijos automáticamente.
**Para qué**: mantener integridad referencial sin código manual (borrar hotel → borra sus rooms).
**Relaciones**: es un comportamiento de · lo aplica el · en Booking forma el "cascade delete tree" User→Hotel→Room.
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#Constraints — las 5 reglas que la DB impone]]

### Celery
**Qué es**: sistema de *task queue* distribuida para Python: ejecuta trabajo en *workers* fuera del request HTTP.
**Para qué**: mover tareas lentas (emails, pagos, jobs) a segundo plano para no bloquear la respuesta.
**Relaciones**: usa un · tiene workers + s + · su scheduler es Beat · alternativa a RQ/Dramatiq.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

### Cola (queue)
**Qué es**: estructura FIFO donde se encolan mensajes/tareas para que un consumidor los procese después.
**Para qué**: desacoplar quién produce trabajo de quién lo ejecuta, y absorber picos.
**Relaciones**: la gestiona un · la consumen workers de · lo que falla repetidamente va a una.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

### Composite index
**Qué es**: índice sobre varias columnas en orden; acelera filtros/orden que usan esas columnas por su prefijo (regla de la columna líder).
**Para qué**: que queries con varios filtros o paginación por cursor no hagan *full scan*.
**Relaciones**: es un caso de · habilita determinista · se valida con.
**Categoría**: BD · **Se explica a fondo en**:

### conftest.py
**Qué es**: archivo especial de pytest que define *fixtures* y *hooks* compartidos, descubierto automáticamente por los tests de su carpeta.
**Para qué**: centralizar el andamiaje de tests (DB, cliente, usuarios) sin importarlo en cada test.
**Relaciones**: contiene s · se carga solo (no se importa) · en Booking resuelve el gotcha de con `loop_scope="session"`.
**Categoría**: Testing · **Se explica a fondo en**:

### Connection pool
**Qué es**: conjunto de conexiones a la BD ya abiertas y reutilizables, gestionado por el engine.
**Para qué**: abrir una conexión TCP+auth a Postgres es caro; el pool las recicla en vez de crear/destruir por request.
**Relaciones**: lo administra el · evita el coste por-request · su agotamiento causa timeouts bajo carga.
**Categoría**: BD · **Se explica a fondo en**:

### Correlation ID
**Qué es**: identificador único que se genera por request y viaja en logs/llamadas para seguir una operación de punta a punta.
**Para qué**: depurar en producción ("¿qué pasó con ESTA petición?") atravesando servicios.
**Relaciones**: lo emite · es clave en sistemas con /colas (el request y el job comparten ID) · base de la *observabilidad*.
**Categoría**: Observabilidad · **Se explica a fondo en**:

### Cursor pagination
**Qué es**: paginar usando un "puntero" al último elemento (keyset) en vez de `OFFSET`.
**Para qué**: paginar de forma estable y O(1) sobre datasets grandes (sin duplicados ni saltos cuando hay inserciones).
**Relaciones**: alternativa a · necesita un determinista · usa comparación de tuplas en SQL · el cursor puede ser keyset puro u *opaque* (base64).
**Categoría**: Búsqueda/Datos · **Se explica a fondo en**:

## D

### DAG
**Qué es**: grafo dirigido acíclico; en orquestación (Airflow) modela tareas (nodos) y dependencias (aristas).
**Para qué**: definir pipelines de datos con orden, reintentos y scheduling.
**Relaciones**: lo ejecuta un orquestador (Airflow) · sus nodos son *tasks* · es central en el proyecto de **Telemetría** (tanda 2).
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**: — Telemetría (pendiente de siembra)

### Dead Letter Queue (DLQ)
**Qué es**: cola/topic destino para mensajes o tareas que fallan repetidamente y no se pueden procesar.
**Para qué**: no perder ni bloquear la cola con mensajes "venenosos"; inspeccionarlos aparte.
**Relaciones**: complementa una normal · la usan y Kafka · se llega tras agotar s.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

### Dependency injection
**Qué es**: patrón en que un componente recibe sus dependencias desde fuera en vez de crearlas él. En FastAPI, vía `Depends()`.
**Para qué**: desacoplar, reutilizar (sesión DB, usuario actual) y poder sustituir dependencias en tests (*override*).
**Relaciones**: en FastAPI usa `Depends` y deps yield-based · entrega la y el usuario autenticado · habilita el de testing · cachea por request.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

### Dependency override
**Qué es**: mecanismo de FastAPI para sustituir una dependencia por otra en tests (p. ej. DB de test).
**Para qué**: testear endpoints sin tocar recursos reales.
**Relaciones**: se apoya en · es técnica de **Testing** · alternativa a mockear a mano.
**Categoría**: Testing · **Se explica a fondo en**:

### Docker
**Qué es**: tecnología de *contenedores*: empaqueta app + dependencias + runtime en una unidad que corre igual en cualquier máquina.
**Para qué**: "funciona en mi máquina" deja de ser un problema; entornos reproducibles.
**Relaciones**: construye una desde un · varios contenedores se orquestan con · NO es una VM (comparte kernel).
**Categoría**: Infra/Docker · **Se explica a fondo en**:

### Dockerfile
**Qué es**: receta de texto con los pasos para construir una imagen (base, copiar código, instalar deps, comando de arranque).
**Para qué**: definir de forma versionada y reproducible cómo se empaqueta la app.
**Relaciones**: produce una · lo usa / · su `ENTRYPOINT` suele correr migraciones y arrancar el server.
**Categoría**: Infra/Docker · **Se explica a fondo en**: — canónica aquí (huérfano)

### docker-compose
**Qué es**: herramienta para definir y levantar varios servicios (api, db, redis) y su red/volúmenes en un solo archivo YAML.
**Para qué**: levantar todo el stack local con un comando, con dependencias y healthchecks.
**Relaciones**: orquesta es de · gestiona y · usa `depends_on` para el orden de arranque.
**Categoría**: Infra/Docker · **Se explica a fondo en**: — canónica aquí (huérfano)

## E

### Eager loading
**Qué es**: cargar relaciones del ORM por adelantado en la misma query (selectinload/joinedload) en vez de bajo demanda.
**Para qué**: eliminar el (1 query en vez de N+1).
**Relaciones**: lo opuesto es *lazy loading* (trampa en) · resuelve · `selectinload` vs `joinedload` según cardinalidad.
**Categoría**: Búsqueda/Datos · **Se explica a fondo en**:

### Endpoint
**Qué es**: una ruta+método HTTP concreta de la API (`POST /auth/login`) con su lógica asociada (handler).
**Para qué**: exponer una operación específica de la API al cliente.
**Relaciones**: es la unidad de una · lo enruta un *router* de · valida entrada/salida con · recibe deps por.
**Categoría**: API/Web · **Se explica a fondo en**:

### Engine
**Qué es**: objeto de SQLAlchemy que representa la fuente de conexiones a una BD y traduce ORM↔SQL.
**Para qué**: punto único de acceso a la BD con pool gestionado.
**Relaciones**: su versión async es · contiene · lo crea/lee `app/db.py` como singleton.
**Categoría**: BD · **Se explica a fondo en**:

### Environment variable
**Qué es**: variable del entorno del proceso (`DATABASE_URL`, `SECRET_KEY`) leída en runtime, no hardcodeada.
**Para qué**: configurar la app por entorno (dev/prod) sin tocar el código ni filtrar secretos al repo.
**Relaciones**: la inyecta /el SO · la lee `app/config.py` · clave en *gestión de secretos*.
**Categoría**: Infra/Docker · **Se explica a fondo en**: — canónica aquí (huérfano)

### Event loop
**Qué es**: el bucle que ejecuta corrutinas: cuando una hace `await` de I/O, el loop pasa a otra que esté lista.
**Para qué**: dar concurrencia de I/O en un solo hilo (base de async).
**Relaciones**: lo conduce · el queda atado al loop activo al importarse (causa del gotcha de pytest, resuelto con `loop_scope="session"`).
**Categoría**: Async/Concurrencia · **Se explica a fondo en**:

### EXPLAIN
**Qué es**: comando SQL que muestra el *plan de ejecución* de una query (qué índices usa, si hace seq scan). `EXPLAIN ANALYZE` además la ejecuta y mide.
**Para qué**: diagnosticar por qué una query es lenta.
**Relaciones**: revela si se usa un · herramienta para detectar y *full scans* · se complementa con `pg_stat_statements`.
**Categoría**: BD · **Se explica a fondo en**:

## F

### FastAPI
**Qué es**: framework web Python async para construir APIs; valida con Pydantic y genera OpenAPI automáticamente.
**Para qué**: exponer una HTTP rápida, tipada y autodocumentada.
**Relaciones**: corre sobre · usa para · su superpoder es · enruta s.
**Categoría**: API/Web · **Se explica a fondo en**:

### Fixture
**Qué es**: función de pytest que prepara (y limpia) algo que un test necesita (DB limpia, cliente, usuario), inyectada por nombre.
**Para qué**: dar a cada test un estado controlado y aislado sin repetir setup.
**Relaciones**: vive en · tiene *scope* (function/session) · su `yield` separa setup de teardown · es aplicada a tests.
**Categoría**: Testing · **Se explica a fondo en**:

### Foreign key (FK)
**Qué es**: columna que referencia la *primary key* de otra tabla, imponiendo integridad referencial.
**Para qué**: garantizar que un room siempre apunta a un hotel que existe.
**Relaciones**: apunta a una · puede tener regla · base de los JOINs · la verifica el (IntegrityError si se viola).
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#Constraints — las 5 reglas que la DB impone]]

### Full-Text Search (FTS)
**Qué es**: búsqueda por palabras/relevancia sobre texto (no `LIKE`), usando un índice de términos. En Postgres: `tsvector`/`tsquery`.
**Para qué**: buscar "playa" y encontrar "Sol Beach Resort" ordenado por relevancia.
**Relaciones**: usa + + GIN · `ts_rank` ordena por relevancia · alternativa ligera a Elasticsearch (ver ADR-0003).
**Categoría**: Búsqueda/Datos · **Se explica a fondo en**:

## G

### GIN index
**Qué es**: tipo de índice de Postgres ("Generalized Inverted Index") óptimo para valores compuestos como `tsvector` o JSONB.
**Para qué**: que el FTS encuentre documentos por término en tiempo logarítmico.
**Relaciones**: es un caso de · habilita · alternativa a GiST (GIN = lecturas estáticas rápidas).
**Categoría**: Búsqueda/Datos · **Se explica a fondo en**:

### Git
**Qué es**: sistema de control de versiones distribuido: historia de cambios del código en commits y ramas.
**Para qué**: versionar, colaborar y revertir el código con seguridad.
**Relaciones**: es a código lo que al esquema de BD · base de los flujos de PR/review (cf. proceso de CL en grandes empresas).
**Categoría**: Infra/Docker · **Se explica a fondo en**: — canónica aquí (huérfano)

## H

### Handler
**Qué es**: la función que ejecuta la lógica de un endpoint (recibe request validada, orquesta servicios, devuelve respuesta).
**Para qué**: separar "qué ruta" de "qué se hace" en esa ruta.
**Relaciones**: implementa un · recibe deps por · delega en *services* · es uno de los *archetypes* de función backend.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**: [[archetipos-funciones-backend#Por qué importa]]

### Hashing
**Qué es**: función *one-way* que transforma una entrada en un valor fijo irreversible; misma entrada → mismo hash.
**Para qué**: guardar contraseñas sin poder revertirlas; verificar sin almacenar el secreto.
**Relaciones**: para passwords se usa (lento a propósito) · NO es cifrado (no hay "deshash") · se confunde con encoding ( sí es reversible).
**Categoría**: Auth/Seguridad · **Se explica a fondo en**:

### Healthcheck
**Qué es**: endpoint/comando que reporta si un servicio está vivo y/o listo (`/health`).
**Para qué**: que Docker/orquestador sepa cuándo un servicio está sano y pueda arrancar dependientes.
**Relaciones**: lo usa `depends_on` de · se distingue *liveness* vs *readiness* · base de la *observabilidad*.
**Categoría**: Observabilidad · **Se explica a fondo en**:

### HTTP
**Qué es**: protocolo petición/respuesta sobre el que viaja la web: método (GET/POST…), ruta, cabeceras, cuerpo, código de estado.
**Para qué**: que cliente y API se comuniquen con una semántica común.
**Relaciones**: lo expone una vía s · sus códigos: 2xx ok, 401, 403, 404, 409, 422 · transporta.
**Categoría**: API/Web · **Se explica a fondo en**: — canónica aquí (huérfano)

## I

### Idempotencia
**Qué es**: propiedad de una operación que, ejecutada N veces, deja el mismo estado que ejecutada 1 vez.
**Para qué**: poder reintentar con seguridad (pagos, webhooks, tareas) sin duplicar efectos.
**Relaciones**: clave en s,, webhooks y Stripe (*idempotency keys*) · NO es lo mismo que "solo una vez" (es "reintentable sin daño").
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

### Imagen Docker
**Qué es**: snapshot inmutable y versionable (SO base + deps + código) desde el que se arrancan contenedores.
**Para qué**: distribuir y arrancar la app idéntica en cualquier sitio.
**Relaciones**: se construye desde un · un es una instancia en ejecución de una imagen · la usa.
**Categoría**: Infra/Docker · **Se explica a fondo en**: — canónica aquí (huérfano)

### Índice
**Qué es**: estructura auxiliar (normalmente B-tree) que acelera la búsqueda por ciertas columnas, a coste de espacio y escrituras más lentas.
**Para qué**: que `WHERE`/`ORDER BY`/JOIN no recorran toda la tabla.
**Relaciones**: caso multi-columna → · para FTS → · su uso se verifica con · habilita.
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#Indexes — el corazón de la performance]]

### Isolation level
**Qué es**: cuánto se aíslan transacciones concurrentes (Read Committed, Repeatable Read, Serializable…); a más aislamiento, menos anomalías pero más coste.
**Para qué**: elegir el equilibrio correcto entre correctitud concurrente y rendimiento (clave en reservas).
**Relaciones**: es la "I" de · gradúa anomalías (dirty/non-repeatable/phantom) · Serializable + retry resuelve el double-booking · se configura en.
**Categoría**: BD · **Se explica a fondo en**:

## J

### JOIN
**Qué es**: operación SQL que combina filas de dos tablas según una condición (normalmente FK = PK). INNER/LEFT/RIGHT/FULL.
**Para qué**: leer datos relacionados en una sola query (hotel + sus rooms).
**Relaciones**: se apoya en · evita el (alternativa al lazy loading) · el ORM lo genera con `selectinload`/`joinedload`.
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#JOINs — los 4 + cuándo cada uno]]

### JWT (JSON Web Token)
**Qué es**: token firmado (header.payload.signature) que lleva *claims* (p. ej. user id, expiración); el servidor lo verifica sin guardar sesión.
**Para qué**: autenticación *stateless*: el token prueba quién eres en cada request.
**Relaciones**: se envía como · se firma con HS256 (simétrico, Booking) o RS256 · hay dos: y · NO está cifrado (es legible: no metas secretos).
**Categoría**: Auth/Seguridad · **Se explica a fondo en**:

## K

### Keyset
**Qué es**: técnica de paginación que filtra por `(columna_orden, id) > último_visto` usando un índice, en vez de `OFFSET`.
**Para qué**: paginar en O(1) estable; es el motor de la cursor pagination.
**Relaciones**: es la base de · se confunde con OFFSET (keyset no "salta" filas, las acota) · exige.
**Categoría**: Búsqueda/Datos · **Se explica a fondo en**:

## L

### Liveness vs Readiness
**Qué es**: dos health checks: *liveness* = "¿el proceso está vivo?" (si no, reiniciar); *readiness* = "¿puede atender tráfico ya?" (si no, no enrutarle).
**Para qué**: que el orquestador reinicie lo colgado pero no mande tráfico a algo que aún no tiene DB.
**Relaciones**: ambos son s · readiness suele comprobar dependencias (DB/Redis) · usado por `depends_on`/orquestadores.
**Categoría**: Observabilidad · **Se explica a fondo en**:

## M

### Mapped / mapped_column
**Qué es**: sintaxis declarativa de SQLAlchemy 2.0 para definir columnas tipadas en un modelo ORM (`Mapped[int]`, `mapped_column(...)`).
**Para qué**: declarar el esquema con tipos Python verificables y autocompletado.
**Relaciones**: define un · `Mapped[int | None]` = columna NULLable · el ORM lo traduce a DDL/SQL.
**Categoría**: BD · **Se explica a fondo en**: [[01-sqlalchemy-2-async-patterns#Mapped[] + mapped_column — el estilo declarativo 2.0]]

### Message broker
**Qué es**: intermediario que recibe mensajes de productores y los entrega a consumidores (Redis, Kafka, RabbitMQ).
**Para qué**: desacoplar servicios y absorber picos mediante colas.
**Relaciones**: gestiona s · lo usa (Redis como broker) · base del patrón productor/consumidor.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

### Middleware
**Qué es**: capa que envuelve cada request/response para lógica transversal (logging, CORS, auth, correlation id) antes/después del handler.
**Para qué**: aplicar comportamiento común a todas las rutas sin repetirlo.
**Relaciones**: se ejecuta alrededor del · distinto de (middleware = todas las rutas; dep = la que la pide) · típico sitio del.
**Categoría**: API/Web · **Se explica a fondo en**:

### Migración
**Qué es**: script versionado que aplica un cambio de esquema (`upgrade`) y sabe revertirlo (`downgrade`), encadenado por revisión.
**Para qué**: evolucionar el esquema de forma reproducible en todos los entornos.
**Relaciones**: la gestiona · la aplica el `entrypoint.sh` al arrancar · `autogenerate` la propone comparando modelos vs BD.
**Categoría**: Migraciones · **Se explica a fondo en**:

### Modelo (ORM)
**Qué es**: clase Python que representa una tabla; sus atributos son columnas y relaciones.
**Para qué**: trabajar con filas como objetos en vez de SQL crudo.
**Relaciones**: lo define · lo gestiona la · se confunde con (modelo = persistencia; schema = validación/IO).
**Categoría**: BD · **Se explica a fondo en**: [[01-sqlalchemy-2-async-patterns#Mapped[] + mapped_column — el estilo declarativo 2.0]]

### Multi-tenant
**Qué es**: un mismo sistema sirve a múltiples "dueños" aislando sus datos. En Booking v0.1, vía `owner_id` + `is_admin`.
**Para qué**: que cada usuario solo vea/gestione lo suyo.
**Relaciones**: se implementa con `owner_id` y · base de la · evoluciona a roles/tablas dedicadas.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

## N

### N+1 query problem
**Qué es**: antipatrón donde cargar N objetos dispara 1 query + N queries (una por relación), matando el rendimiento.
**Para qué**: reconocer la causa nº1 de endpoints lentos con ORM.
**Relaciones**: se causa por *lazy loading* · se resuelve con / · se detecta con /conteo de queries.
**Categoría**: Búsqueda/Datos · **Se explica a fondo en**:

### Non-blocking I/O
**Qué es**: operación de I/O que no detiene el hilo: inicia y deja que el event loop siga con otra cosa hasta que esté lista.
**Para qué**: base técnica de la concurrencia async.
**Relaciones**: lo opuesto de · lo orquesta el · lo expone.
**Categoría**: Async/Concurrencia · **Se explica a fondo en**:

### Normalización
**Qué es**: organizar las tablas (1NF/2NF/3NF) para eliminar redundancia y anomalías de actualización.
**Para qué**: que un dato viva en un solo sitio (sin copias inconsistentes).
**Relaciones**: se apoya en / · su opuesto deliberado es la *denormalización* (rendimiento) · contexto del diseño de esquema relacional.
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#Normalization — 1NF / 2NF / 3NF brief]]

## O

### OFFSET pagination
**Qué es**: paginar con `LIMIT n OFFSET m`; salta m filas y devuelve n.
**Para qué**: paginación simple; aceptable en datasets pequeños/estables.
**Relaciones**: alternativa (peor a escala) a · su problema: O(m) y duplicados/saltos si hay inserciones · se confunde con.
**Categoría**: Búsqueda/Datos · **Se explica a fondo en**:

### ORM
**Qué es**: capa que mapea tablas↔objetos y genera SQL por ti (SQLAlchemy).
**Para qué**: trabajar con datos en Python sin escribir SQL a mano (la mayor parte del tiempo).
**Relaciones**: define s · ejecuta vía / · *genera* SQL (cuando algo falla, lees SQL) · su trampa cara: lazy loading async /.
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#ORM ↔ SQL — qué SQL genera SQLAlchemy]]

## P

### PostgreSQL
**Qué es**: RDBMS open-source robusto; el motor de BD de Booking. Extensible (FTS, JSONB, TimescaleDB).
**Para qué**: almacenar datos relacionales con garantías ACID y features avanzadas.
**Relaciones**: es un caso de · da / · soporta e s GIN · se accede vía /`asyncpg`.
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#Postgres-specific things que aparecen en Booking]]

### Primary key (PK)
**Qué es**: columna(s) que identifican unívocamente cada fila; no nula y única.
**Para qué**: poder referenciar y distinguir filas sin ambigüedad.
**Relaciones**: la referencia una · base de · suele ser un serial autogenerado.
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#Constraints — las 5 reglas que la DB impone]]

### Prometheus
**Qué es**: sistema de métricas que hace *scrape* periódico de un endpoint `/metrics` y guarda series temporales.
**Para qué**: medir el sistema (latencia, throughput, errores) y alertar.
**Relaciones**: tipos: counter/gauge/histogram · ojo con la *cardinalidad* (labels) · se visualiza en Grafana · pilar de la *observabilidad* junto a logs y health.
**Categoría**: Observabilidad · **Se explica a fondo en**:

### Pydantic
**Qué es**: librería de validación/serialización por tipos: defines un modelo y valida/coacciona datos de entrada y salida.
**Para qué**: que datos inválidos no entren a tu lógica (422 automático) y que la salida tenga forma controlada.
**Relaciones**: define el que usa · v2 cambió API (`from_attributes`) · distinto de (uno valida IO, el otro persiste).
**Categoría**: Validación · **Se explica a fondo en**:

### pytest
**Qué es**: framework de testing de Python: funciones `test_*`, asserts planos, fixtures y markers.
**Para qué**: verificar el comportamiento del código de forma automatizada y repetible.
**Relaciones**: usa s y · con `pytest-asyncio` corre tests (gotcha del) · base de la práctica TDD.
**Categoría**: Testing · **Se explica a fondo en**:

## Q

### Query builder
**Qué es**: API para construir queries SQL de forma programática y componible (filtros condicionales, joins, order dinámico) en vez de strings.
**Para qué**: construir búsquedas complejas/variables (filtros opcionales) sin concatenar SQL ni arriesgar inyección.
**Relaciones**: parte del (SQLAlchemy `select`) · permite filtros agrupables reusables · soporta y explícitos.
**Categoría**: Búsqueda/Datos · **Se explica a fondo en**:

## R

### Rate limiting
**Qué es**: límite de peticiones por cliente/ventana de tiempo (p. ej. 250 req/min por API key).
**Para qué**: proteger el servicio de abuso/DoS y repartir capacidad.
**Relaciones**: suele apoyarse en · se combina con · responde HTTP 429 al exceder.
**Categoría**: API/Web · **Se explica a fondo en**: — canónica aquí (huérfano)

### RDBMS
**Qué es**: sistema gestor de bases de datos relacionales: tablas, relaciones, SQL y garantías ACID (PostgreSQL, MySQL).
**Para qué**: almacenar datos estructurados con integridad y consultas relacionales.
**Relaciones**: caso concreto → · impone // · da · se accede vía o SQL.
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#SCHEMA: el modelo relacional en 30 segundos]]

### Redis
**Qué es**: almacén clave-valor en memoria, rapidísimo; sirve como caché, broker de colas y backend de rate limiting.
**Para qué**: latencia sub-milisegundo para caché/colas/contadores.
**Relaciones**: soporte de · broker de · backend de · NO sustituye a la BD (volátil por defecto).
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

### REST
**Qué es**: estilo de diseño de APIs HTTP basado en recursos (`/hotels/{id}`), métodos (GET/POST/PUT/DELETE) y códigos de estado, *stateless*.
**Para qué**: APIs predecibles y uniformes que cualquier cliente entiende.
**Relaciones**: es un estilo de sobre · alternativa a RPC/GraphQL · cada recurso+método = un.
**Categoría**: API/Web · **Se explica a fondo en**: — canónica aquí (huérfano)

### Retry
**Qué es**: reintentar automáticamente una operación que falló por causa transitoria, con backoff.
**Para qué**: resiliencia ante fallos pasajeros (red, lock, 5xx) sin intervención manual.
**Relaciones**: exige para ser seguro · lo usan, webhooks y SERIALIZABLE · agotados los reintentos →.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

## S

### Saga
**Qué es**: patrón para transacciones distribuidas: una secuencia de pasos locales, cada uno con su *acción compensatoria* si algo falla después.
**Para qué**: mantener consistencia entre servicios (p. ej. pago) sin un 2-phase-commit global.
**Relaciones**: alternativa a 2PC · compensa en vez de hacer rollback global · requiere · usado en el flujo de pagos (v0.4).
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

### Schema (Pydantic)
**Qué es**: modelo Pydantic que define la forma de entrada/salida de un endpoint y la valida/serializa.
**Para qué**: que la API rechace datos mal formados (422) y exponga solo los campos previstos (no filtrar el hash).
**Relaciones**: lo define y lo usa · distinto de · `from_attributes` lo conecta a objetos ORM.
**Categoría**: Validación · **Se explica a fondo en**:

### Session (ORM)
**Qué es**: unidad de trabajo de SQLAlchemy: rastrea objetos, agrupa cambios y los confirma (`commit`) o revierte (`rollback`) en una transacción.
**Para qué**: agrupar operaciones de BD coherentemente por request.
**Relaciones**: la produce · envuelve una · se entrega por · `expire_on_commit=False` para usar objetos tras commit.
**Categoría**: BD · **Se explica a fondo en**:

### Soft delete
**Qué es**: marcar una fila como borrada (`deleted_at`/`is_deleted`) en vez de eliminarla físicamente.
**Para qué**: conservar histórico/auditoría y poder "deshacer".
**Relaciones**: opuesto a *hard delete* · obliga a filtrar `WHERE deleted_at IS NULL` en todas las queries · usa columnas *timezone-aware*.
**Categoría**: BD · **Se explica a fondo en**: — canónica aquí (huérfano)

### SQL
**Qué es**: lenguaje declarativo para consultar/modificar bases de datos relacionales (SELECT/INSERT/UPDATE/DELETE + JOIN/WHERE/GROUP BY).
**Para qué**: pedir datos describiendo *qué* quieres, no *cómo* obtenerlos.
**Relaciones**: lo genera el por ti · lo ejecuta el · su plan se inspecciona con.
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#PATTERNS — los 4 grupos de SQL operations]]

### SQLAlchemy
**Qué es**: el ORM/toolkit de BD de Python; en Booking, su variante async (2.0, `Mapped[]`).
**Para qué**: definir modelos, construir queries y gestionar conexiones sin SQL crudo.
**Relaciones**: provee /,, y · migraciones con · genera.
**Categoría**: BD · **Se explica a fondo en**:

### structlog
**Qué es**: librería de *logging estructurado* (JSON con campos) en vez de texto plano, con contexto e IDs.
**Para qué**: logs consultables/filtrables y trazables por request en producción.
**Relaciones**: emite el · pilar de *observabilidad* junto a y · alternativa a logging stdlib/loguru (ADR-0010).
**Categoría**: Observabilidad · **Se explica a fondo en**:

## T

### Token de acceso
**Qué es**: JWT de vida corta que autoriza llamadas a la API.
**Para qué**: probar identidad en cada request sin reenviar credenciales.
**Relaciones**: es un enviado como · se renueva con el · corto a propósito (limita el daño si se filtra).
**Categoría**: Auth/Seguridad · **Se explica a fondo en**:

### Token de refresco
**Qué es**: token de vida larga cuyo único uso es obtener un nuevo *access token* (y, idealmente, rotar).
**Para qué**: no obligar al usuario a re-loguear cada pocos minutos, manteniendo access tokens cortos.
**Relaciones**: complementa el · es un · "rotación" = emitir uno nuevo en cada refresh (mejor postura de seguridad).
**Categoría**: Auth/Seguridad · **Se explica a fondo en**:

### Transacción
**Qué es**: conjunto de operaciones de BD que se confirman juntas (`commit`) o se deshacen juntas (`rollback`): unidad atómica.
**Para qué**: que un fallo a mitad no deje datos inconsistentes.
**Relaciones**: tiene propiedades · su concurrencia se gradúa con · la abre/cierra la.
**Categoría**: BD · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#Transactions + ACID + isolation levels]]

### tsquery / tsvector
**Qué es**: tipos de Postgres para FTS: `tsvector` = documento tokenizado/normalizado; `tsquery` = la consulta de términos a casar.
**Para qué**: buscar por palabras con stemming y relevancia, no `LIKE`.
**Relaciones**: indexados con · `plainto_/websearch_to_tsquery` parsean input de usuario · `ts_rank` ordena · base de.
**Categoría**: Búsqueda/Datos · **Se explica a fondo en**:

### TTL
**Qué es**: "time to live": tiempo tras el cual una entrada cacheada expira.
**Para qué**: equilibrar frescura de datos vs carga de BD; acotar datos obsoletos.
**Relaciones**: parámetro de / · TTL uniforme causa (se mitiga con jitter) · relacionado con.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

## U

### Unidad de trabajo (Unit of Work)
**Qué es**: patrón donde una sesión acumula los cambios de objetos y los persiste atómicamente al final (commit).
**Para qué**: tratar muchos cambios como una sola transacción coherente.
**Relaciones**: lo implementa la de · envuelve una · relacionado con *identity map*.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

## V

### Validación
**Qué es**: comprobar que los datos de entrada cumplen forma/reglas antes de procesarlos; en FastAPI la hace Pydantic (devuelve 422 si no).
**Para qué**: que datos inválidos no lleguen a la lógica/BD (defensa en el borde).
**Relaciones**: la hace vía · distinta de la validación de la BD (constraints/IntegrityError) · su error HTTP es 422.
**Categoría**: Validación · **Se explica a fondo en**:

### Volumen (Docker)
**Qué es**: almacenamiento persistente gestionado por Docker, independiente del ciclo de vida del contenedor.
**Para qué**: que los datos de Postgres sobrevivan a recrear el contenedor.
**Relaciones**: lo declara · su mal estado causó el bug "permission denied for schema public" (volumen viejo con otras credenciales) · NO confundir con.
**Categoría**: Infra/Docker · **Se explica a fondo en**:

## W

### Walking skeleton
**Qué es**: implementación mínima pero *end-to-end* de un sistema (todas las capas conectadas aunque cada una sea trivial).
**Para qué**: validar pronto que la arquitectura completa funciona y tener algo desplegable desde el día 1.
**Relaciones**: filosofía de arranque de Booking y **Telemetría** · opuesto a construir capa por capa sin integrar.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

### Webhook
**Qué es**: HTTP POST que un servicio externo (Stripe) te envía cuando ocurre un evento, en vez de que tú lo consultes (*polling*).
**Para qué**: enterarte de eventos asíncronos (pago confirmado) sin sondear.
**Relaciones**: hay que verificar su *firma* · debe ser (se reintentan) · opuesto a polling · clave en el flujo de pagos.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

## X · Y · Z

### (vacío todavía)

---

## Conceptos transversales (sin letra fija)

### Base64
**Qué es**: codificación reversible de bytes a texto ASCII (URL-safe en cursores/tokens). NO es cifrado ni hashing.
**Para qué**: meter datos binarios donde solo cabe texto (cursor opaco, partes de un JWT).
**Relaciones**: se confunde con (base64 es reversible; hash no) · usado por el cursor *opaque* de y por.
**Categoría**: Utilidades · **Se explica a fondo en**: — canónica aquí (huérfano)

### Timezone-aware
**Qué es**: marca de tiempo que incluye su zona horaria (UTC), frente a una "naive" sin zona.
**Para qué**: evitar bugs de horas al comparar/almacenar fechas entre regiones.
**Relaciones**: convención de columnas de fecha en Booking · clave en (`deleted_at`) y reservas · `server_default` la fija en BD.
**Categoría**: Utilidades · **Se explica a fondo en**: [[sql-y-bases-de-datos-fundamentos#Postgres-specific things que aparecen en Booking]]

### Invalidación de caché
**Qué es**: decidir cuándo y cómo borrar/actualizar una entrada cacheada para que no sirva datos obsoletos.
**Para qué**: el lado difícil de cachear ("solo hay dos cosas difíciles…"): correctitud de la caché.
**Relaciones**: parte de · estrategias: por, por evento, por clave · ADR-0009.
**Categoría**: Arquitectura/Patrones · **Se explica a fondo en**:

---

## Sub-variantes Booking (desglose)

> Variantes concretas que antes vivían dentro de una entrada general. Cada una
> es ahora **entrada propia con su ancla** (`` resuelve). Formato
> compacto: definición + **⤴ padre** (la entrada general de la que es caso).

### SELECT
Cláusula que **proyecta** qué columnas devuelve una query. *Para qué*: pedir solo lo que necesitas (vs `SELECT *`). ⤴ · **A fondo**: [[sql-y-bases-de-datos-fundamentos]]

### WHERE
Cláusula que **filtra filas** por predicado. *Para qué*: el `if` del SQL; usa el si el predicado es selectivo. ⤴

### GROUP BY
Agrupa filas por columna(s) para aplicar agregados (`COUNT`, `SUM`). *Rel*: se combina con `HAVING` (filtrar grupos). ⤴

### EXISTS (subconsulta)
Predicado booleano "¿hay al menos una fila?"; corta en el primer match. *Rel*: el query del solapamiento de reservas. ⤴

### HS256 vs RS256
Algoritmos de firma JWT: HS256 = simétrico (un secreto compartido); RS256 = asimétrico (privada firma, pública verifica). *Para qué*: RS256 cuando varios servicios verifican sin compartir secreto. ⤴ · **A fondo**: [[04-jwt-y-session-management]]

### Port mapping
Mapear puerto host→contenedor (`8000:8000`). *Rel*: cómo accedes al desde fuera de Docker. ⤴

### selectinload vs joinedload
Dos estrategias de: `selectinload` = 2ª query con `IN` (colecciones); `joinedload` = un `JOIN` (to-one). *Para qué*: matar el sin cargar de más. ⤴ · **A fondo**: [[sql-y-bases-de-datos-fundamentos]]

### plainto_tsquery / websearch_to_tsquery
Convierten texto de usuario a `tsquery`: `plainto_` = AND de términos; `websearch_` = sintaxis tipo buscador (comillas, `or`, `-`). ⤴

### ts_rank
Función que **puntúa** la relevancia de un match full-text para ordenarlo. *Rel*: el `ORDER BY` de la búsqueda. ⤴

### GiST (índice)
Índice generalizado para datos no escalares (rangos, geometría, FTS). *Rel*: alternativa a según el tipo. ⤴

### expire_on_commit
Flag de la `Session` SQLAlchemy: si `True`, tras `commit` los objetos quedan *expired* y la próxima lectura recarga. *Rel*: causa accesos lazy inesperados post-commit. ⤴

### server_default vs default
`default` lo pone Python al insertar; `server_default` lo pone Postgres (`DEFAULT` en DDL). *Para qué*: `server_default` aplica también a filas creadas fuera del ORM. ⤴

### IntegrityError
Excepción al violar una constraint (UNIQUE, FK, NOT NULL). *Para qué*: cómo el ORM te avisa de un duplicado/huérfano. ⤴

### Celery Beat
Scheduler de Celery que **encola tareas periódicas** (cron interno). *Rel*: el "reloj" que dispara jobs recurrentes. ⤴

### Modelo de concurrencia de worker (prefork/gevent)
Cómo un worker Celery ejecuta tareas: `prefork` (procesos, CPU) vs `gevent`/`eventlet` (greenlets, I/O). *Rel*: misma decisión que **I/O-bound vs CPU-bound**. ⤴

### loop_scope
Parámetro pytest-asyncio que ata fixtures/tests a un mismo event loop (`"session"`). *Para qué*: evita "Event loop is closed" con engine async global. ⤴

### ASGITransport
Transporte de `httpx` que llama a la app ASGI **en proceso** (sin red ni servidor). *Para qué*: tests de endpoints rápidos y deterministas. ⤴

### Marker (pytest)
Etiqueta sobre un test (`@pytest.mark.asyncio`, `slow`) para seleccionar/configurar. *Rel*: cómo el `conftest` inyecta `loop_scope`. ⤴

### Dependencia con yield (FastAPI)
Dependencia que hace setup, `yield` el recurso, y cleanup tras la response (patrón sesión-por-request). *Rel*: es el ciclo de vida de la inyectada. ⤴

### Idempotency key
Clave única que el cliente manda para que reintentar una operación no la duplique (pagos). *Rel*: implementa sobre un POST. ⤴ · **A fondo**:

### PaymentIntent (estados)
Objeto Stripe que modela el ciclo de un cobro (`requires_payment_method` → `requires_confirmation` → `succeeded`). *Rel*: la máquina de estados que tu webhook escucha. ⤴

---

# Parte 2 — CS Fundamentos (teoría transversal)

> Vocabulario de `CS_Fundamentos/`, organizado **por área** (no alfabético: aquí
> el objetivo es *entender lo que hemos tratado* por dominio). Formato compacto:
> **término** — qué es · *para qué* · *rel*: relaciones (`**X**` salta a la
> Parte 1) · → doc donde se explica a fondo (enlace a nivel de documento).
> Categorías nuevas: Redes · Sistemas Operativos · Concurrencia · System Design ·
> BD internals/NoSQL · Distribuidos · Arquitectura HW · Seguridad · Compiladores · Algoritmos.

## Redes

### Capas y transporte (TCP/IP) — [[01-tcp-ip-osi]]
- **Modelo OSI / TCP-IP** — modelo en capas (OSI 7 académico; TCP/IP 4 real). *Rel*: enmarca /TCP/IP. → [[01-tcp-ip-osi#2. Los dos modelos: OSI y TCP/IP]]
- **Encapsulación** — cada capa envuelve los datos de la superior con su cabecera. *Rel*: explica por qué un paquete tiene "capas de sobre". → [[01-tcp-ip-osi#3. Encapsulación — el corazón del modelo en capas]]
- **IP** — capa de Internet: direccionar y enrutar paquetes best-effort. *Rel*: debajo de TCP/UDP. → [[01-tcp-ip-osi#Capa 2 — Internet (IP)]]
- **TCP** — transporte fiable orientado a conexión (orden, retransmisión, control de flujo/congestión). *Rel*: lo usan y; vs UDP. → [[01-tcp-ip-osi#Capa 3 — Transporte (TCP/UDP)]]
- **UDP** — transporte sin conexión ni garantías, overhead mínimo (DNS, video). *Rel*: opuesto a TCP. → [[01-tcp-ip-osi#8. TCP vs UDP — cuándo cada uno]]
- **Three-way handshake** — SYN/SYN-ACK/ACK para abrir conexión TCP. *Rel*: por qué abrir conexión "cuesta" →. → [[01-tcp-ip-osi#5. TCP three-way handshake — el clásico]]
- **Four-way handshake (cierre)** — FIN/ACK ×2 para cerrar limpio una conexión TCP. *Rel*: estado TIME_WAIT, relacionado con **Port exhaustion**. → [[01-tcp-ip-osi#Cierre — el four-way handshake]]
- **Sliding window** — control de flujo: cuántos bytes en vuelo sin ACK. *Rel*: por qué el throughput tiene tope. → [[01-tcp-ip-osi#6. TCP sliding window — control de flujo]]
- **Congestion control / retransmission** — TCP baja el ritmo ante pérdida y reenvía lo perdido. *Rel*: por qué la latencia varía. → [[01-tcp-ip-osi#7. TCP retransmission y congestion control]]

### HTTP — [[02-http-y-evolucion]]
- **HTTP request / response (anatomía)** — línea (método+ruta) + headers + body / status + headers + body. *Rel*: lo que valida. → [[02-http-y-evolucion#2. Anatomía de un HTTP request]]
- **Métodos HTTP (verbos REST)** — GET/POST/PUT/PATCH/DELETE y su semántica. *Rel*: base de y del. → [[02-http-y-evolucion#4. Métodos HTTP — los verbos REST]]
- **Idempotencia HTTP** — GET/PUT/DELETE idempotentes; POST no. *Rel*: amplía; clave en. → [[02-http-y-evolucion#Idempotencia — concepto clave]]
- **Status codes** — 2xx/3xx/4xx/5xx (401/403/404/409/422/429…). *Rel*: 401, 403, 422. → [[02-http-y-evolucion#5. Status codes — los 5 grupos]]
- **Headers HTTP** — metadatos de request/response (Authorization, Content-Type, Cache-Control…). *Rel*: transporta el. → [[02-http-y-evolucion#6. Headers importantes que debes conocer]]
- **HTTP/1.1 vs 2 vs 3** — texto/1-conexión → multiplexado binario → sobre QUIC/UDP. *Rel*: amplía. → [[02-http-y-evolucion#11. Comparativa rápida HTTP/1.1 vs 2 vs 3]]
- **Cookies y sesiones** — estado en cliente; alternativa stateful al. → [[02-http-y-evolucion#12. Cookies y sesiones]]
- **CORS** — política del navegador para peticiones cross-origin. *Rel*: se gestiona con. → [[02-http-y-evolucion#13. CORS — el dolor de cabeza típico]]

### DNS — [[03-dns-resolucion-nombres]]
- **DNS** — traduce nombres → IPs jerárquicamente. *Rel*: previo a abrir el **Socket** TCP. → [[03-dns-resolucion-nombres#1. Qué es DNS y qué problema resuelve]]
- **Jerarquía DNS (root → TLD → autoritativo)** — quién resuelve qué nivel del nombre. → [[03-dns-resolucion-nombres#2. La jerarquía DNS]]
- **Registros DNS (A, AAAA, CNAME, MX, TXT)** — tipos de mapeo de un dominio. → [[03-dns-resolucion-nombres#3. Tipos de DNS records]]
- **Resolución DNS paso a paso** — recursive resolver → root → TLD → autoritativo → IP. *Rel*: latencia inicial de toda request. → [[03-dns-resolucion-nombres#4. La resolución paso a paso (¡el flow estrella!)]]
- **Query recursiva vs iterativa** — quién hace el trabajo de seguir la cadena. → [[03-dns-resolucion-nombres#5. Tipos de queries DNS]]
- **DNS caching / TTL** — cada nivel cachea según TTL; por qué un cambio "tarda en propagar". *Rel*: mismo concepto TTL que. → [[03-dns-resolucion-nombres#7. DNS caching — donde realmente vive el rendimiento]]
- **DoH / DoT** — DNS cifrado sobre HTTPS/TLS (privacidad). → [[03-dns-resolucion-nombres#9. DNS sobre HTTPS (DoH) y DNS sobre TLS (DoT)]]
- **DNS geo / load balancing** — el mismo nombre resuelve a IPs distintas por región. *Rel*: capa previa a **Load balancer**/CDN. → [[03-dns-resolucion-nombres#10. DNS y CDNs / load balancing geo]]

### Puertos y sockets (lo que pediste) — [[04-sockets-y-puertos]]
- **Socket** — extremo de comunicación; API del SO para hablar por red. *Rel*: lo abren uvicorn/Postgres; lo crea una **Syscall**. → [[04-sockets-y-puertos#1. Qué es un socket]]
- **4-tupla de conexión** — (IP origen, puerto origen, IP destino, puerto destino) identifica unívocamente una conexión. *Rel*: por qué muchos clientes comparten el puerto 443 del server sin colisionar. → [[04-sockets-y-puertos#2. Los 4 valores que IDENTIFICAN una conexión]]
- **Puerto** — nº (0–65535) que identifica un servicio en una máquina (80/443/5432). *Rel*: lo mapea; lo usa el. → [[04-sockets-y-puertos#3. Puertos — el "número de teléfono" del proceso]]
- **Lifecycle socket server** — socket → bind → listen → accept (por cada cliente). *Rel*: cómo un server atiende a muchos. → [[04-sockets-y-puertos#4. El lifecycle de un socket TCP — server side]]
- **Lifecycle socket cliente** — socket → connect → send/recv → close. → [[04-sockets-y-puertos#5. El lifecycle de un socket TCP — client side]]
- **Bloqueante vs no-bloqueante (I/O)** — el socket espera (bloquea el hilo) o retorna ya y avisas luego. *Rel*: raíz de /. → [[04-sockets-y-puertos#7. Bloqueante vs no-bloqueante (I/O models)]]
- **I/O multiplexing (select/poll/epoll/kqueue)** — vigilar miles de sockets con un solo hilo. *Rel*: el motor real bajo el. → [[04-sockets-y-puertos#Solución: I/O multiplexing (`select`, `poll`, `epoll`, `kqueue`)]]
- **Los 5 I/O models** — blocking, non-blocking, multiplexed, signal-driven, async. *Rel*: marco para situar asyncio. → [[04-sockets-y-puertos#8. Los 5 I/O models (referencia)]]
- **Port exhaustion** — quedarse sin puertos efímeros por exceso de conexiones cortas/TIME_WAIT. *Rel*: por qué importa el. → [[04-sockets-y-puertos#9. Port exhaustion — el problema oculto]]
- **SO_REUSEADDR / SO_REUSEPORT** — reusar dirección/puerto (reinicios rápidos, balanceo entre procesos). → [[04-sockets-y-puertos#10. SO_REUSEADDR y SO_REUSEPORT]]
- **Connection pooling (red)** — reutilizar conexiones abiertas en vez de abrir/cerrar por request. *Rel*: el porqué de de la BD. → [[04-sockets-y-puertos#11. Connection pooling — patrón crítico]]

### TLS / HTTPS — [[05-tls-https]]
- **TLS / HTTPS** — cifrado+autenticación sobre TCP que protege HTTP. *Rel*: usa y criptografía. → [[05-tls-https#1. Por qué necesitamos TLS]]
- **Cifrado simétrico** — misma clave cifra y descifra (rápido, el grueso de TLS). *Rel*: vs asimétrico. → [[05-tls-https#Cifrado simétrico]]
- **Cifrado asimétrico (clave pública)** — par pública/privada; base de la autenticación TLS. *Rel*: amplía **Hashing vs cifrado**. → [[05-tls-https#Cifrado asimétrico (clave pública)]]
- **Diffie-Hellman** — acordar una clave secreta por un canal público sin transmitirla. *Para qué*: forward secrecy. → [[05-tls-https#Diffie-Hellman key exchange]]
- **Certificate chain / X.509** — cadena de confianza dominio→CA raíz. *Rel*: el "Certificado/CA". → [[05-tls-https#3. Certificate chain — cómo confías en un server]]
- **TLS 1.3 handshake** — negociación de claves+identidad antes de cifrar (1-RTT). *Rel*: detalle en Seguridad. → [[05-tls-https#4. TLS handshake (TLS 1.3) — paso a paso]]
- **SNI** — el cliente indica qué dominio quiere en el handshake (varios certs, una IP). → [[05-tls-https#5. SNI — Server Name Indication]]
- **mTLS** — TLS mutuo: también el cliente presenta certificado. *Para qué*: auth servicio-a-servicio. → [[05-tls-https#7. mTLS — mutual TLS]]
- **HSTS** — fuerza HTTPS en el navegador (no degradar a HTTP). → [[05-tls-https#9. HSTS — Strict Transport Security]]

## Sistemas Operativos

### Procesos e hilos — [[01-procesos-y-threads]]
- **Programa → proceso → hilo** — jerarquía: código en disco → instancia en ejecución con memoria propia → flujo dentro del proceso. → [[01-procesos-y-threads#1. La jerarquía: programa → proceso → thread]]
- **Anatomía de un proceso** — code/data/heap/stack + tabla de fds + espacio de direcciones aislado. *Rel*: lo aísla la **Memoria virtual**. → [[01-procesos-y-threads#2. Anatomía de un proceso (lo que tiene en memoria)]]
- **Hilo (thread)** — ejecución que comparte memoria con su proceso. *Rel*: origen de **Race condition**; en Python limitado por el **GIL**. → [[01-procesos-y-threads#3. Anatomía de un thread]]
- **fork() + exec()** — crear proceso (copia) y reemplazar su imagen por otro programa. *Rel*: cómo nace todo proceso Unix. → [[01-procesos-y-threads#4. Crear procesos: `fork()` + `exec()`]]
- **Estados de un proceso** — new/ready/running/waiting/terminated. *Rel*: lo gestiona el **Scheduler**. → [[01-procesos-y-threads#6. Estados de un proceso]]
- **Context switch** — guardar/restaurar estado para alternar procesos/hilos. *Rel*: por qué demasiada concurrencia tiene coste. → [[01-procesos-y-threads#7. Context switching — el coste de cambiar de proceso/thread]]
- **Procesos vs hilos** — aislamiento+paralelismo (CPU) vs concurrencia barata con memoria compartida (I/O). *Rel*: ver **Async vs threads vs procesos**. → [[01-procesos-y-threads#8. Procesos vs threads — cuándo cada uno]]
- **GIL (Python)** — un solo hilo ejecuta bytecode a la vez en CPython. *Rel*: por qué CPU-bound usa procesos y I/O usa; conecta con **Runtime / VM**. → [[01-procesos-y-threads#9. El GIL de Python — caso especial importante]]
- **Zombie / orphan** — proceso muerto sin reapear / proceso cuyo padre murió. *Rel*: por qué `wait()` importa. → [[01-procesos-y-threads#11. Zombies y orphans (procesos en estados raros)]]
- **Signals** — notificación asíncrona a un proceso (SIGTERM/SIGKILL/SIGINT). *Rel*: por qué el `entrypoint`/uvicorn maneja SIGTERM para cierre limpio. → [[01-procesos-y-threads#12. Signals — comunicación asíncrona con procesos]]

### Memoria virtual — [[02-memoria-virtual-paging]]
- **Memoria virtual** — cada proceso ve un espacio de direcciones propio mapeado a RAM física. *Rel*: aislamiento + ilusión de más memoria. → [[02-memoria-virtual-paging#1. El problema que resuelve la memoria virtual]]
- **Paging / address translation** — memoria en páginas; la MMU traduce virtual→física vía page tables. → [[02-memoria-virtual-paging#3. Paging — la idea central]]
- **Page fault** — acceder a una página no residente; el SO la trae (lento). *Rel*: por qué el primer acceso "cuesta". → [[02-memoria-virtual-paging#6. Page faults — cuando la página no está en RAM]]
- **Swap** — usar disco como RAM extra cuando falta memoria (degrada mucho). → [[02-memoria-virtual-paging#7. Swap — cuando RAM no alcanza]]
- **mmap** — mapear un archivo a memoria y accederlo como array. *Rel*: técnica de I/O eficiente. → [[02-memoria-virtual-paging#8. mmap — mapear archivos en memoria]]
- **malloc/free (heap)** — reserva/liberación dinámica en el heap del proceso. *Rel*: bajo el `new`/GC de los lenguajes. → [[02-memoria-virtual-paging#10. Heap allocation — qué hace malloc/free]]
- **OOM killer** — Linux mata procesos cuando se agota la RAM. *Rel*: por qué un contenedor "se cae" sin error claro. → [[02-memoria-virtual-paging#12. OOM killer — cuando se acaba la RAM (Linux)]]
- **cgroups / memory limits** — el kernel limita recursos por grupo (cómo Docker limita CPU/RAM). *Rel*: límites de. → [[02-memoria-virtual-paging#13. Cgroups y memory limits (cómo Docker limita memoria)]]

### Scheduling — [[03-scheduling]]
- **Scheduler** — decide qué hilo corre y cuándo. *Rel*: subyace al (un hilo cooperativo encima del scheduler). → [[03-scheduling#1. El problema del scheduler]]
- **Preemptive vs cooperative** — el SO interrumpe vs la tarea cede voluntariamente. *Rel*: asyncio es cooperativo. → [[03-scheduling#Preemptive vs cooperative]]
- **FCFS / SJF / Round Robin / Priority / MLFQ** — algoritmos clásicos de planificación. → [[03-scheduling#3. Algoritmos clásicos de scheduling]]
- **Linux CFS** — el scheduler real de Linux (fair, por *vruntime*). → [[03-scheduling#4. Linux CFS — Completely Fair Scheduler (el real)]]
- **CPU affinity** — fijar un proceso a cores concretos. *Rel*: rendimiento/caché. → [[03-scheduling#5. CPU affinity — fijar procesos a cores]]
- **NUMA** — la latencia de memoria depende de qué core la accede. *Rel*: conecta con **Jerarquía de memoria / caché**. → [[03-scheduling#6. NUMA — Non-Uniform Memory Access]]

### Syscalls y kernel — [[04-syscalls-y-kernel]]
- **User space vs kernel space** — separación de privilegios app/núcleo. *Rel*: por qué cruzar al kernel cuesta. → [[04-syscalls-y-kernel#1. User space vs kernel space]]
- **Syscall** — petición al kernel de un recurso privilegiado (red/disco/procesos). *Rel*: un **Socket** se crea con syscalls. → [[04-syscalls-y-kernel#2. Qué es un syscall]]
- **File descriptor** — entero que referencia un fichero/socket abierto ("todo es un fichero"). *Rel*: agotarlos cuelga el server. → [[04-syscalls-y-kernel#5. File descriptors — el concepto unificador Unix]]
- **strace** — traza las syscalls de un proceso (debugging "qué está pidiendo al SO"). → [[04-syscalls-y-kernel#6. Strace — la herramienta esencial para debugging]]
- **Syscall vs función de librería** — la libc envuelve syscalls; no toda llamada cruza al kernel. → [[04-syscalls-y-kernel#8. Syscall vs library function]]
- **eBPF** — ejecutar código sandbox en el kernel (observabilidad/red). *Rel*: tracing moderno. → [[04-syscalls-y-kernel#11. eBPF — el "JavaScript del kernel"]]

### Filesystems — [[05-filesystems]]
- **Filesystem** — cómo el SO organiza ficheros en bloques con metadatos. → [[05-filesystems#1. Qué es un filesystem]]
- **Inode** — estructura con los metadatos de un fichero (no su nombre). *Rel*: base de hard/symlinks. → [[05-filesystems#3. Inodes — el corazón de Unix filesystems]]
- **Hard link vs symlink** — otro nombre al mismo inode vs puntero a una ruta. → [[05-filesystems#4. Hard links vs symbolic links]]
- **Permisos Unix** — modelo user/group/other × rwx. *Rel*: el bug "permission denied for schema public" era de esta familia (ownership). → [[05-filesystems#5. File permissions — el modelo Unix clásico]]
- **Journaling** — log de cambios para sobrevivir a un crash sin corromper el FS. *Rel*: misma idea que **WAL (Write-Ahead Log)**. → [[05-filesystems#7. Journaling — supervivencia ante crashes]]
- **fsync / durabilidad** — forzar que los datos lleguen a disco de verdad. *Rel*: la "D" de depende de esto. → [[05-filesystems#9. fsync, fdatasync, write — durabilidad real]]
- **Page cache** — el SO cachea en RAM bloques de disco (por qué el 2º `cat` es instantáneo). *Rel*: caché a nivel SO, distinta de. → [[05-filesystems#11. Page cache — por qué tu segundo `cat` es instantáneo]]

## Concurrencia (teoría)

### Race conditions — [[01-race-conditions]]
- **Race condition** — el resultado depende del orden no determinista de operaciones concurrentes sobre estado compartido. *Rel*: el double-booking; se previene con locks o.
- **Sección crítica** — el trozo de código que solo un hilo debe ejecutar a la vez. *Rel*: lo protege un **Lock / Mutex**.
- **Lost update** — dos escrituras concurrentes; una pisa a la otra (el bug del contador). *Rel*: lo evita optimistic/pessimistic locking.
- **TOCTOU** — *Time-Of-Check / Time-Of-Use*: compruebas y actúas, pero algo cambió entre medias. *Rel*: el bug de tu `_cleanup_db`/reservas.
- **Write skew** — dos transacciones leen y deciden con datos que la otra invalida (anomalía SERIALIZABLE). *Rel*: ver.
- **ABA problem** — un valor pasa A→B→A y un CAS no lo detecta (lock-free). *Rel*: **Coherencia de caché (multicore)**.

### Locks y primitivas — [[02-locks-y-mutex]]
- **Lock / Mutex** — serializa el acceso a una sección crítica. *Rel*: alternativa pesimista a; RAII (`lock_guard`).
- **Reentrant lock (RLock)** — el mismo hilo puede re-adquirirlo sin auto-bloquearse.
- **Read-Write lock** — muchos lectores o un escritor (no ambos). *Para qué*: optimizar cargas read-heavy.
- **Semáforo** — permite N accesos concurrentes (no 1). *Para qué*: limitar un pool de recursos.
- **Condition variable** — esperar/avisar sobre una condición (productor-consumidor). *Rel*:.
- **Atomic / CAS** — operación indivisible sin lock (compare-and-swap). *Rel*: base de lock-free; **ABA problem**.

### Deadlock — [[03-deadlock-livelock]]
- **Deadlock** — varias partes se bloquean mutuamente para siempre. *Rel*: las 4 condiciones de Coffman.
- **Condiciones de Coffman** — exclusión mutua + hold&wait + no preemption + espera circular (las 4 a la vez). *Para qué*: romper una previene el deadlock.
- **Orden global de locks** — adquirir siempre en el mismo orden: la prevención más usada.
- **Livelock / Starvation** — cambian sin progresar / un hilo nunca obtiene el recurso. *Rel*: priority inversion.

### Modelos de concurrencia — [[04-async-vs-threads-vs-procesos]]
- **Async vs threads vs procesos** — I/O cooperativo / hilos preemptivos / aislamiento+paralelismo. *Rel*: fundamento de,, **GIL**.
- **I/O-bound vs CPU-bound** — la regla de oro para elegir: I/O→async, CPU→procesos. *Rel*: por qué el **GIL** no estorba en I/O.
- **gather / TaskGroup** — lanzar varias corrutinas en paralelo y esperar a todas. *Rel*: patrón asyncio idiomático.
- **asyncio.Lock / Queue** — sincronización y productor-consumidor entre tasks del mismo loop. *Rel*:.

## System Design (patrones)

### Load balancing — [[01-load-balancing]]
- **Load balancer** — reparte tráfico entre instancias. *Rel*: delante de tus s; usa.
- **Layer 4 vs Layer 7** — balancear por TCP/IP vs por contenido HTTP (ruta, header). *Rel*: capas del **Modelo OSI / TCP-IP**.
- **Algoritmos de balanceo** — round-robin, least-connections, least-response-time, P2C, consistent hashing.
- **Consistent hashing** — repartir claves entre nodos minimizando remapeo al añadir/quitar nodos. *Rel*: clave en **Sharding / partición**/caché distribuida.
- **Sticky sessions** — atar un cliente a un backend (estado local). *Rel*: anti-patrón vs stateless/.
- **TLS termination** — el LB descifra TLS y habla HTTP claro por dentro. *Rel*: **TLS / HTTPS**.

### Caching — [[02-caching-strategies]]
- **Patrones de caché** — cache-aside / read-through / write-through / write-behind. *Rel*: (Parte 1) es uno.
- **Eviction policy** — qué tirar cuando la caché se llena (LRU, LFU, FIFO).
- **Hot key** — una clave concentra tráfico desproporcionado. *Rel*:.
- **Cache penetration** — consultas de claves que no existen pasan siempre a BD. *Para qué*: por qué cachear también "no encontrado".
- **Hit ratio** — % de aciertos de caché: la métrica que mide si vale la pena.

### Message queues — [[03-message-queues]]
- **Queue vs Pub/Sub** — punto-a-punto (un consumidor) vs difusión (N suscriptores). *Rel*: generaliza /.
- **Log-based (Kafka)** — log append-only particionado y releíble (no se borra al consumir). *Rel*: base de Telemetría (tanda 2).
- **Garantías de entrega** — at-most-once / at-least-once / exactly-once. *Rel*: at-least-once exige.
- **Backpressure** — el consumidor lento frena al productor para no reventar memoria.
- **Outbox pattern** — publicar eventos vía la propia BD para no perderlos. *Rel*:, consistencia.

### CDN / Rate limiting — [[04-cdn-y-edge]] · [[05-rate-limiting]]
- **CDN / edge** — servidores cerca del usuario que cachean estático. *Rel*: caché geográfica; **DNS geo / load balancing**.
- **Edge computing** — ejecutar lógica en el edge, no solo cachear.
- **Algoritmos de rate limiting** — fixed/sliding window, token bucket, leaky bucket. *Rel*: la teoría tras el de Parte 1.
- **Rate limiting distribuido** — contadores centralizados en vs aproximación local+sync.

## BD internals y NoSQL (lo que pediste)

### Índices y motor — [[01-b-trees-y-indexing]]
- **B-tree / B+tree** — árbol balanceado que indexa rangos en O(log n); el índice por defecto. *Rel*: implementa el de Parte 1.
- **LSM-tree** — alternativa write-optimized (Cassandra, RocksDB): escribe a memoria+log y compacta. *Rel*: vs B-tree (read-optimized).
- **Clustered vs secondary index** — el primario ordena la tabla físicamente; el secundario apunta a él.
- **Covering index** — el índice contiene todas las columnas de la query → no toca la tabla (*index-only scan*).
- **Selectividad** — cuán único es un valor: un índice solo ayuda si es selectivo. *Rel*: por qué a veces lo ignora.

### ACID / transacciones — [[02-acid-transactions]]
- **ACID (interno)** — cómo el motor implementa A/D (WAL, undo/redo). *Rel*: profundiza.
- **WAL (Write-Ahead Log)** — escribir el cambio al log antes que a los datos → durabilidad y recovery. *Rel*: misma idea que journaling de FS.
- **Undo log / MVCC** — deshacer cambios / multiversión: lectores no bloquean escritores. *Rel*: por qué Postgres es concurrente.
- **2PC (two-phase commit)** — commit atómico entre nodos (prepare→commit). *Rel*: alternativa pesada a.

### Isolation — [[03-isolation-levels]]
- **Las 4 anomalías** — dirty read, non-repeatable read, phantom, write skew. *Para qué*: qué previene cada nivel.
- **Niveles SQL** — READ UNCOMMITTED/COMMITTED, REPEATABLE READ, SERIALIZABLE. *Rel*: profundiza.
- **Snapshot Isolation / SSI** — cada txn ve un snapshot; SSI detecta conflictos serializables. *Rel*: el modo de Postgres.
- **SELECT FOR UPDATE** — lock pesimista explícito de filas. *Rel*: pesimista vs optimista (versioning).

### Replicación / sharding — [[04-replication-y-sharding]]
- **Replicación (single/multi-leader, leaderless)** — copias para disponibilidad y lecturas. *Rel*: trade-off con **Teorema CAP**.
- **WAL shipping / logical replication** — métodos de replicar (enviar el log vs filas lógicas).
- **Sync vs async replication** — confirmar tras réplica (seguro, lento) vs no (rápido, riesgo de pérdida).
- **Sharding / shard key** — partir datos por clave entre nodos; la clave decide hotspots. *Rel*: **Consistent hashing**.
- **Read replica / failover** — escalar lecturas; promover réplica si cae el líder.

### SQL vs NoSQL — [[05-sql-vs-nosql-tradeoffs]]
- **Los 5 modelos** — relacional / documento / clave-valor / columnar (wide-column) / grafo.
- **BD documental** — documentos JSON sin esquema fijo (MongoDB). *Rel*: NoSQL.
- **BD clave-valor** — mapa distribuido (Redis, DynamoDB). *Rel*:.
- **BD columnar (wide-column)** — Cassandra/ClickHouse: analítica y escritura masiva. *Rel*: vs row-store.
- **BD de grafos** — nodos+aristas de primera clase (Neo4j): relaciones profundas.
- **BASE** — Basically Available, Soft state, Eventual consistency: el anti-. *Rel*: **Eventual consistency**.
- **Polyglot persistence** — usar varias BD según el caso (no "una para todo").
- **NewSQL** — escala horizontal con garantías SQL/ACID (CockroachDB, Spanner).

## Sistemas Distribuidos

### CAP / consenso — [[01-cap-pacelc]] · [[02-consensus-paxos-raft]]
- **Teorema CAP** — ante partición, eliges Consistencia o Disponibilidad. *Rel*: NoSQL suele ser AP (**BASE**).
- **PACELC** — además, sin partición eliges Latencia o Consistencia. *Para qué*: el trade-off existe siempre.
- **Linealizabilidad** — toda lectura ve la última escritura confirmada (consistencia fuerte).
- **Consenso (Paxos / Raft)** — N nodos acuerdan un valor pese a fallos. *Rel*: base de un líder/orden común.
- **Quorum** — mayoría (N/2+1) necesaria para decidir; garantiza solapamiento read/write.
- **Leader election / term** — elegir líder y versionar mandatos (Raft).

### Consistencia / tracing — [[03-eventual-consistency]] · [[04-distributed-tracing]]
- **Eventual consistency** — las réplicas convergen "con el tiempo"; lecturas pueden ver datos viejos. *Rel*: la "E" de **BASE**.
- **Replication lag** — retraso réplica vs líder; el síntoma visible de async replication.
- **Conflict resolution (LWW / CRDT / vector clocks)** — resolver escrituras concurrentes en multi-master.
- **Distributed tracing** — seguir una request por N servicios con trace/span id. *Rel*: generaliza el.
- **Span / trace / sampling** — unidad de trabajo / árbol de spans / qué % guardas. *Rel*: OpenTelemetry.
- **Logs vs metrics vs traces** — los 3 pilares de observabilidad. *Rel*: / / tracing.

## Arquitectura de computadores

### CPU — [[01-cpu-pipeline-y-registros]]
- **Registros / pipeline** — la memoria más rápida; la CPU solapa fases de instrucciones. *Para qué*: por qué los saltos cuestan.
- **Branch prediction** — la CPU adivina el camino de un `if`; fallar vacía el pipeline. *Rel*: por qué el código predecible vuela.
- **Out-of-order / superescalar** — reordenar y ejecutar >1 instrucción por ciclo.
- **SIMD** — una instrucción opera sobre un vector de datos. *Rel*: vectorización (NumPy).
- **Speculative execution** — ejecutar antes de saber si hace falta (origen de Spectre/Meltdown).

### Memoria y caché — [[02-jerarquia-de-memoria-y-cache]]
- **Jerarquía de memoria** — registros < L1/L2/L3 < RAM < disco (más lento y grande al bajar). *Rel*: por qué `vector` > lista enlazada.
- **Cache line** — la caché mueve bloques (~64 B), no bytes sueltos. *Rel*: localidad espacial.
- **Localidad temporal/espacial** — reusar datos recientes y contiguos: la razón física de muchas optimizaciones.
- **SoA vs AoS** — *Struct of Arrays* vs *Array of Structs*: layout que decide el rendimiento de caché.
- **False sharing** — dos cores escriben variables distintas en la misma cache line → contención oculta. *Rel*: **Coherencia de caché (multicore)**.
- **Prefetching** — la CPU adelanta datos que cree que usarás.

### Multicore — [[03-coherencia-cache-multicore]]
- **Coherencia de caché (MESI)** — mantener consistentes las cachés por core. *Rel*: por qué compartir estado mutable es caro.
- **Memory ordering / barriers** — el HW reordena accesos; las *fences* lo impiden donde importa.
- **Acquire-release / CAS / ABA** — semántica atómica para lock-free. *Rel*: **Atomic / CAS**, **ABA problem**.
- **SMP vs NUMA** — memoria uniforme vs latencia según el core. *Rel*: **NUMA** de scheduling.

## Seguridad

### Cripto y TLS — [[01-tls-handshake-detallado]] · [[02-hashing-vs-cifrado]]
- **TLS 1.3 handshake (detallado)** — ECDHE + certificado + Finished en 1-RTT. *Rel*: profundiza **TLS / HTTPS**.
- **Forward secrecy** — robar la clave del server hoy no descifra tráfico pasado (ECDHE efímero).
- **Hashing vs cifrado** — one-way irreversible vs reversible con clave. *Rel*: amplía; vs (encoding).
- **Salt / pepper** — aleatorio por password / secreto global: por qué dos passwords iguales no comparten hash. *Rel*:.
- **Cifrado simétrico vs asimétrico (AES / RSA-ECC)** — misma clave (rápido) vs par pública/privada (acuerdo/firma).
- **AEAD** — cifrado que además autentica (detecta manipulación): el modo correcto moderno.
- **Firma digital** — probar autoría/integridad con clave privada. *Rel*: cómo se firma un.

### OWASP / auth — [[03-owasp-top-10]] · [[04-jwt-y-session-management]]
- **OWASP Top 10** — las 10 vulnerabilidades web críticas (2021). *Para qué*: checklist de qué no hacer.
- **Broken Access Control (A01)** — saltarse (IDOR): la nº1 actual. *Rel*: el anti-leak de rooms.
- **Injection / SQL injection (A03)** — input no sanitizado ejecutado como código/SQL. *Rel*: el / lo previenen.
- **SSRF (A10)** — forzar al server a hacer requests a destinos internos.
- **Sessions vs JWT (trade-offs)** — stateful revocable vs stateless escalable. *Rel*: profundiza.
- **Revocation problem (JWT)** — un JWT válido no se puede "desinvalidar" fácil. *Rel*: por qué access tokens cortos + con rotación.
- **Almacenamiento de token en cliente** — localStorage vs cookie HttpOnly+SameSite vs memoria (el debate XSS/CSRF).
- **OAuth 2.0 / OIDC** — delegar autenticación/autorización a un proveedor. *Rel*: ecosistema sobre.

## Compiladores e intérpretes

### Front-end — [[01-lexer-parser-ast]]
- **Lexer (tokenización)** — texto → tokens. *Para qué*: primera fase; base de syntax highlighting.
- **Parser** — tokens → árbol según una gramática; maneja precedencia/asociatividad.
- **AST** — árbol abstracto del programa (sin ruido sintáctico). *Rel*: sobre él operan linters/formatters (ruff, clang-format).
- **Semantic analysis** — comprobar tipos/scopes tras parsear; de aquí salen muchos errores de compilación.

### Runtime — [[02-runtime-y-vm]]
- **Tree-walking vs bytecode interpreter** — recorrer el AST vs compilar a bytecode y ejecutarlo en una VM (CPython).
- **VM stack-based vs register-based** — cómo la VM pasa operandos. *Rel*: bytecode de Python.
- **JIT compilation** — compilar a código máquina en caliente según el uso real (PyPy, V8, JVM). *Rel*: por qué JS/Java son rápidos pese a dinámicos.
- **AOT compilation** — compilar todo antes de ejecutar (C/C++/Go). *Rel*: tu roadmap C++.
- **Garbage collection** — liberar memoria automáticamente (refcount, mark-sweep, generacional). *Rel*: por qué C++ NO tiene GC (RAII) y Python sí.
- **Por qué Python es "lento"** — dinámico + interpretado + GIL + boxing. *Rel*: **GIL**, cuándo bajar a C++.

## Algoritmos

- **Dijkstra** — camino más corto desde un origen en grafo de pesos no negativos (greedy + cola de prioridad). *Para qué*: ruta óptima (mapas, redes). *Rel*: heap = `priority_queue`; patrón grafo+heap de NeetCode. → [[01-dijkstra]]
- **Pesos no negativos (restricción)** — Dijkstra falla con aristas negativas (ahí: Bellman-Ford). *Para qué*: saber cuándo NO aplicarlo. → [[01-dijkstra]]
- **Reconstrucción de camino** — guardar predecesores para devolver la ruta, no solo la distancia. → [[01-dijkstra]]

---

# Parte 3 — Telemetría (por subsistema)

> Vocabulario del proyecto `08_telemetry_platform` (planificado; sus `docs/01-12`
> ya lo definen a fondo). Organizado **por subsistema** (un sub-bloque por doc),
> mismo formato compacto que Parte 2: definición + *para qué/rel* + → doc.

## Almacenamiento time-series —
- **TimescaleDB** — extensión de Postgres para series temporales (Postgres que aguanta GB/día). *Rel*: misma SQL/, otro motor de storage. →
- **Hypertable** — tabla virtual particionada automáticamente por tiempo en *chunks*. *Para qué*: insertar/consultar a escala sin gestionar particiones a mano.
- **Chunk** — partición física (rango de tiempo) de una hypertable; unidad de retención/compresión.
- **Continuous aggregate** — vista materializada incremental que pre-agrega (ej. medias 5-min). *Rel*: caché de agregados; Grafana siempre apunta aquí, no a raw.
- **Compresión columnar nativa** — recomprime chunks viejos a formato columnar (10-20×). *Rel*: trade-off espacio vs latencia de query.
- **Retention / compression policy** — jobs que comprimen o tiran chunks por edad. *Rel*: cost control; ver **Tiered storage**.
- **BRIN index** — índice de rango por bloque, diminuto, ideal para datos ordenados por tiempo. *Rel*: contrasta con el B-tree del.
- **time_bucket / gapfill** — agrupar por ventana temporal y rellenar huecos de la serie.

## Streaming / Kafka —
- **Kafka** — log distribuido replicado (no una cola tradicional): los mensajes no se borran al consumir. *Rel*: generaliza / pero releíble.
- **Topic / partition / broker** — canal lógico / unidad de paralelismo y orden / nodo del clúster. *Rel*: el orden solo se garantiza *por partición*.
- **Record (key+value+offset+timestamp)** — el mensaje; la *key* decide la partición.
- **Offset** — posición del consumidor en la partición ("por dónde voy"). *Rel*: lo commitea el consumer group.
- **Consumer group** — conjunto de consumidores que se reparten particiones (scaling horizontal de consumo).
- **Leader / follower / ISR** — réplica que sirve / réplicas que copian / réplicas en sync (durabilidad). *Rel*: replicación; ver **Teorema CAP** (Parte 2).
- **Replication factor** — nº de copias de cada partición.
- **Retention / log compaction** — borrar por edad/tamaño vs conservar el último valor por key.
- **KRaft** — modo sin Zookeeper (Kafka gestiona su propio consenso). *Rel*: consenso Raft (Parte 2).
- **Idempotent producer** — productor que evita duplicados al reintentar. *Rel*:.
- **Consumer lag** — cuánto va por detrás el consumidor (mensajes sin procesar). *Rel*: señal de **Back-pressure**.
- **DLQ (Kafka)** — topic para mensajes que fallan repetidamente. *Rel*: el patrón de.

## Orquestación / Airflow —
- **Airflow** — orquestador de pipelines batch programados (DAGs en Python). *Rel*: usa como executor; el "cron con dependencias".
- **DAG (Airflow)** — grafo dirigido acíclico de tareas. *Rel*: el genérico aplicado a orquestación.
- **Operator** — plantilla de tarea (PythonOperator, BashOperator…). *Rel*: ladrillo del DAG.
- **Task / dependency** — instancia de trabajo y su orden (`a >> b`).
- **Las 4 nociones de tiempo** — `logical/data interval`, `start_date`, `execution`, `run` (la confusión clásica).
- **Schedule / data interval** — cada cuánto corre y qué ventana de datos procesa.
- **Sensor (Airflow)** — tarea que espera a una condición (poke/reschedule).
- **Pool** — límite de concurrencia compartido entre tareas.
- **XCom** — canal para pasar valores pequeños entre tareas.
- **Backfill** — re-ejecutar el pasado para rangos históricos. *Rel*: exige (la disciplina nº1 aquí).
- **CeleryExecutor** — ejecutar tareas en workers Celery distribuidos.

## Stream processing / Faust —
- **Stream processing** — procesar eventos uno a uno en continuo (vs batch). *Rel*: el cambio de paradigma vs Airflow.
- **Faust** — librería de stream processing en Python (estilo Kafka Streams). *Rel*: consume topics de **Kafka**.
- **Agent (Faust)** — consumidor tipado con DSL que procesa un stream.
- **Table (Faust)** — estado gestionado, respaldado por un *changelog topic*.
- **Windowing** — agregaciones sobre ventanas de tiempo.
- **Tumbling / hopping / sliding window** — sin solape / con solape fijo / dirigida por evento.
- **Watermark** — heurística de "hasta cuándo esperar eventos tardíos" antes de cerrar una ventana.
- **Stream-stream / stream-table join** — unir dos streams (con ventana) o un stream con estado (lookup).
- **Stateless vs stateful** — sin estado (escala trivial) vs con estado (changelog, rebalance).
- **Exactly-once semantics** — cada evento afecta el resultado una sola vez. *Rel*: contrasta con at-least-once.

## Feature engineering time-series —
- **Time features** — hora/día/mes/estación derivados del timestamp.
- **Encoding cíclico (sin/cos)** — codificar variables circulares (hora 23→0) sin salto artificial. *Rel*: el detalle crítico que casi todos fallan.
- **Lag features** — valor del propio sensor N pasos atrás (1h, 24h, 7d).
- **Rolling stats** — media/desv. en ventana deslizante; *per-sensor* para no mezclar sensores.
- **Differencing** — restar el valor anterior para quitar tendencia (estacionariedad).
- **FFT features** — features del dominio frecuencial (periodicidades).
- **Cross-sensor features** — correlaciones espaciales entre sensores.
- **Decomposition (trend/seasonal/residual)** — separar la serie en componentes.
- **Temporal leak** — usar futuro para predecir el pasado (el bug que infla métricas). *Rel*: lo evita walk-forward.
- **Pandas vs Polars** — performance del feature engineering a escala.

## Anomaly detection —
- **Anomaly detection** — detectar lecturas fuera de patrón sin etiquetas. *Rel*: no supervisado.
- **Isolation Forest** — aísla anomalías con árboles aleatorios (lo raro se separa antes).
- **contamination / n_estimators / max_samples** — hiperparámetros clave (proporción esperada de anomalías, nº árboles, muestreo).
- **Anomaly score** — puntuación de "rareza" para rankear.
- **One-Class SVM / Autoencoder / LOF** — alternativas (frontera, error de reconstrucción, densidad local).
- **z-score / IQR / modified z-score** — baselines estadísticos.
- **Modelo global vs per-sensor vs per-type** — un modelo para todo vs uno por sensor/tipo (trade-off).

## Forecasting —
- **Forecasting** — predecir valores futuros de la serie.
- **Walk-forward validation** — validar avanzando en el tiempo (no k-fold, que filtra futuro). *Rel*: corrige el **Temporal leak**.
- **TimeSeriesSplit / expanding window** — splits temporales respetando el orden.
- **Recursive / direct / MIMO** — estrategias multi-step (realimentar predicción / un modelo por horizonte / salida vectorial).
- **Persistence / seasonal naive baseline** — baselines de cordura antes de modelos complejos.
- **XGBoost / LSTM** — modelos avanzados (gradient boosting / red recurrente) para la progresión.

## MLflow / MLOps —
- **MLflow** — tracking de experimentos + registro de modelos + serving.
- **Run / experiment** — ejecución registrada (params, métricas, artifacts) / grupo de runs.
- **Autologging** — registrar params/métricas/modelo automáticamente por framework.
- **Model flavor** — formato portable del modelo (sklearn, pytorch, pyfunc…).
- **Model signature** — esquema declarado de entrada/salida del modelo.
- **Model Registry / stages** — versionado y promoción (Staging→Production).

## Drift detection —
- **Drift** — la distribución de datos/relación cambia respecto al entrenamiento. *Rel*: por qué un modelo se degrada sin tocar el código.
- **Input / concept / prediction / performance drift** — los 4 tipos (entrada, relación, salida, métrica).
- **KS test / Chi-square / PSI / Wasserstein / JS divergence** — tests estadísticos para detectarlo.
- **Evidently** — librería de reports y test suites de drift (CI-friendly).
- **Reference vs current window** — distribución base vs actual que se comparan.

## Escala y cuellos de botella —
- **Bottleneck** — el componente que se rompe primero al escalar (lo demás no importa hasta resolverlo).
- **Scale ceiling** — capacidad máxima de un componente antes de saturar.
- **Throughput / latency / concurrency / storage** — las 4 dimensiones de escala.
- **Build at 5 GB/día, design for 50 GB/día** — el principio: construir simple pero sin decisiones que impidan ×10.
- **readings/sec** — la métrica de carga del sistema (1500 → 15.000).

## Back-pressure y buffering —
- **Back-pressure** — mecanismo para que un consumidor lento frene al productor. *Rel*: **Consumer lag** es su síntoma.
- **Producer-consumer mismatch** — el productor genera más rápido de lo que el consumidor procesa.
- **Buffering / drop / block / spill-to-disk** — las 4 estrategias canónicas ante saturación.
- **Bounded vs unbounded buffer** — cola con límite (segura) vs sin límite (revienta memoria). *Rel*: `asyncio.Queue` acotada.
- **Kafka como buffer** — usar la retención del log como colchón casi infinito.

## Retención, compresión y coste —
- **Tiered storage (hot/warm/cold)** — SSD local / comprimido / archivo S3-MinIO según edad del dato.
- **Time-based vs size-based retention** — tirar por edad vs por tamaño.
- **drop_chunks()** — borrado eficiente por chunk (no `DELETE` fila a fila).
- **Aggregation as compression** — conservar agregados y tirar el raw (la mayor palanca de coste).
- **Sampling** — guardar un % del histórico viejo en lugar de todo.
- **Las 4 palancas de cost control** — retención · compresión · tiering · agregación.

---

## Pendientes de siembra (tandas siguientes)

> No materializo entradas vacías masivas (CLAUDE.md: "no sobre-estructures").
> Estos términos se añaden a su sitio cuando se trabajen, con el mismo esquema.

**Tandas posteriores**: vocabulario de los demás Build_Things (phone_book,
build-your-own-redis, go_learning, cpp_learning) según se trabajen.

## Conexiones

- [[00_README]] — doctrina de Referencia (este glosario es su capa léxica)
- [[MOC_Programacion]] — punto de entrada del área
- [[sql-y-bases-de-datos-fundamentos]] · [[archetipos-funciones-backend]] · [[debugging-python-fastapi-sqlalchemy]] — docs temáticas hermanas
- — verificación de dominio (complementa, no duplica)
