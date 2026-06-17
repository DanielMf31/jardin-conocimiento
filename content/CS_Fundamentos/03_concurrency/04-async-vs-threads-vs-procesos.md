# 04 — Async vs threads vs procesos: cuándo cada uno

> **Doc 4 (último) del cluster Concurrency**. La pregunta más frecuente: tengo que paralelizar algo, ¿qué uso? Aquí decides.
> **Frecuencia interview**: aparece en system design (cómo escalas) y en preguntas Python específicas (GIL, asyncio).
> **Tiempo de lectura estimado**: 40-60 min.

---

## 1. Las 3 formas de hacer cosas a la vez

Hay 3 modelos para lograr concurrencia:

| Modelo | Aislamiento | Paralelismo real | Coste de crear | Sincronización |
|---|---|---|---|---|
| **Procesos** (multiprocessing) | Total: cada uno con su propia memoria | Sí, en CPUs multi-core | Caro (~ms) | IPC (Queue, Pipe, shared_memory) |
| **Threads** (multithreading) | Comparten memoria del proceso | Sí, salvo Python con GIL | Más barato que procesos (~μs) | Locks/sincronización para evitar races |
| **Async** (event loop / coroutines) | 1 solo thread; las tasks ceden voluntariamente en `await` | No (no hay paralelismo CPU); solo concurrencia I/O | Súper barato (~ns por task) | Sin locks típicos (single-thread) |

**Concurrencia ≠ Paralelismo**:

- **Concurrencia**: estructurar el código para que pueda manejar varias cosas (no necesariamente al mismo tiempo).
- **Paralelismo**: ejecutar cosas literalmente al mismo tiempo (varios cores).

Async es **concurrencia sin paralelismo**. Threads y procesos son ambos.

---

## 2. La regla de oro — I/O bound vs CPU bound

El factor que decide **TODO**:

**I/O bound**: la tarea pasa la mayoría del tiempo esperando algo externo:

- Esperando red (HTTP request, DB query).
- Esperando disco (leer archivo, escribir log).
- Esperando user (input, click).

Mientras espera, la CPU está idle: otra tarea podría ejecutar. Ejemplos: web server, scraper, ETL pipeline, chatbot.

**CPU bound**: la tarea usa CPU constantemente. No espera mucho:

- Encriptación, compresión.
- Procesamiento numérico (numpy, pandas).
- Renderizado, ML training.
- Compilación.

Threads no ayudan en Python (GIL serializa). Ejemplos: image resize, password hash, ray tracing.

**Decisión**:

- I/O bound → async (preferido) o threads.
- CPU bound → procesos (multiprocessing) o C extensions.

---

## 3. Threads — modelo clásico

**Características**:

- Comparten memoria → fácil compartir datos.
- Verdadero paralelismo (excepto Python GIL).
- El SO los planifica con CPU scheduler.
- Context switching tiene coste (~μs).
- Stack típicamente 8 MiB cada uno.

**Cuándo usar**:

- I/O bound en lenguajes sin async maduro (o legacy).
- Cuando necesitas compartir mucho estado (sin overhead IPC).
- Cuando el trabajo es mixto y no quieres dos modelos.

**Cuándo evitar en Python**:

- CPU bound puro → usa multiprocessing.
- Miles de conexiones → asyncio escala mucho mejor.

**En Python**:

```python
import threading
t = threading.Thread(target=func, args=(arg,))
t.start()
t.join()

# Pool gestionado:
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(func, args_list)
```

**En otros lenguajes**:

- **Java**: `Thread`, `ExecutorService`.
- **Go**: goroutines (más ligeras que threads OS, pero conceptualmente similares).
- **Rust**: `std::thread`, `rayon`.
- **C++**: `std::thread`, `std::async`.

**Límite práctico**: ~10K threads OS por proceso. Pasado eso, el context switching domina. Las goroutines llegan a millones (son más ligeras).

---

## 4. Procesos — multiprocessing

**Características**:

- Memoria aislada. Necesitas IPC para compartir.
- Verdadero paralelismo siempre (sin GIL).
- Caros de crear (~ms).
- Cada uno con su Python interpreter (en multiprocessing).

**Cuándo usar**:

- CPU bound en Python (rodear el GIL).
- Aislamiento por seguridad/estabilidad.
- Cuando un crash NO debe tirar todo.

**En Python**:

```python
from multiprocessing import Process, Queue

def worker(q):
    q.put(expensive_computation())

q = Queue()
procs = [Process(target=worker, args=(q,)) for _ in range(4)]
for p in procs: p.start()
for p in procs: p.join()
results = [q.get() for _ in range(4)]

# Pool gestionado:
from multiprocessing import Pool
with Pool(4) as pool:
    results = pool.map(func, args_list)

# ProcessPoolExecutor (concurrent.futures):
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(func, args_list))
```

**Opciones de IPC**:

- **Queue / Pipe**: pasar mensajes entre procesos.
- **shared_memory** (Python 3.8+): compartir arrays sin copia.
- **Manager**: objetos compartidos (lento).
- **Files / sockets / DB**: IPC tradicional.

**Overhead de pasar datos**: multiprocessing hace pickle de todos los args para enviarlos al worker. Si pasas datos grandes (DataFrames, arrays) → el pickle es lento. Mejores alternativas: shared_memory, archivos memmap, mensajes pequeños.

**Cuándo multiprocessing NO es ideal**:

- Tu workload tiene mucha shared state.
- Los datos a pasar son enormes (overhead de pickle).
- Necesitas ultra-baja latencia entre workers.

---

## 5. Async / event loop

**Modelo**: un solo thread ejecutando tasks. Cuando una task hace I/O (`await`), el control vuelve al event loop. El event loop ejecuta otra task pendiente. Cuando el I/O completa, retoma la task original.

**No hay**:

- Threads (1 solo).
- Locks típicos (no hay races entre awaits).
- Context switching del SO.

**Sí hay**:

- Coroutines (funciones que pueden suspenderse).
- Tasks (coroutines siendo ejecutadas).
- Event loop (orquesta).

**Python**:

```python
import asyncio

async def fetch(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

async def main():
    results = await asyncio.gather(
        fetch("https://a.com"),
        fetch("https://b.com"),
        fetch("https://c.com"),
    )

asyncio.run(main())
# Las 3 fetches se ejecutan CONCURRENTES (no secuenciales).
# Pero TODO en 1 thread.
```

**Por qué es rápido para I/O**:

- Tradicional: 1 thread por conexión, 1000 conexiones = 1000 threads = thrashing.
- Async: 1 thread, 1000 tasks ligeras (~KB cada una).
- Escala a 100K+ conexiones por proceso.

**Limitación**: si una task hace trabajo CPU sin awaits, **bloquea todo el event loop**. Las demás tasks no avanzan hasta que termine. Por eso async es para I/O, no para CPU.

**Para CPU dentro de async**: usar `run_in_executor()` → manda la tarea a un thread/process pool. asyncio gestiona la espera correctamente.

```python
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(None, cpu_heavy_function, arg)
```

---

## 6. La tabla decisión

| Tarea | Async | Threads | Procesos |
|---|---|---|---|
| Web server (10K cnx) | [OK] ideal | no escala | [NO] overhead |
| HTTP requests masivos | [OK] ideal | ok | [NO] pesado |
| Image processing | [NO] bloquea | GIL | [OK] ideal |
| ML training | [NO] bloquea | [NO] GIL | [OK] ideal |
| DB queries (asyncio) | [OK] ideal | ok | [NO] overhead |
| Background jobs CPU | [NO] bloquea | [NO] GIL | [OK] ideal |
| Real-time UI | [OK] ideal | complejo | [NO] overhead |
| Compute scientific | [NO] bloquea | con C | [OK] ideal |

---

## 7. El patrón híbrido más común

**1 proceso por core + async en cada uno**.

Setup típico de Uvicorn:

```bash
uvicorn main:app --workers 4
```

- 4 procesos Python (1 por core físico).
- Cada proceso corre asyncio (1 thread + event loop).
- Cada proceso atiende miles de conexiones HTTP.

Total: 4 cores × 1000s conexiones = 10K-40K cnx total.

Este es el patrón estándar para web servers Python modernos.

**En otros lenguajes**:

- **Node.js**: el módulo `cluster` hace lo mismo (1 proceso por core).
- **Go**: 1 proceso, el runtime gestiona internamente (M:N scheduler).
- **Rust con tokio**: 1 proceso, work-stealing scheduler.

---

## 8. Async patterns esenciales

### gather — esperar a varias cosas en paralelo

```python
results = await asyncio.gather(
    fetch("https://a.com"),
    fetch("https://b.com"),
    fetch("https://c.com"),
)
# Las 3 ejecutan concurrentes. Termina cuando TODAS terminan.
# Si una falla, propaga la excepción.
```

### TaskGroup (Python 3.11+, recomendado moderno)

```python
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(fetch("a"))
    t2 = tg.create_task(fetch("b"))
# Sale del with cuando ambas terminan.
# Si una falla, cancela las demás. Mejor manejo de errores que gather.
```

### wait_for — con timeout

```python
try:
    result = await asyncio.wait_for(slow_op(), timeout=5.0)
except asyncio.TimeoutError:
    print("Demasiado lento")
```

### asyncio.Lock — sincronización entre tasks asyncio

```python
lock = asyncio.Lock()

async def critical():
    async with lock:
        # solo 1 task aquí a la vez
        await update_shared_resource()

# Aunque sea single-thread, async puede interleavar tasks en awaits.
# Si compartes estado entre tasks, asyncio.Lock previene problemas.
```

### Queue para producer-consumer

```python
queue = asyncio.Queue(maxsize=100)

async def producer():
    for item in items:
        await queue.put(item)   # bloquea si queue llena

async def consumer():
    while True:
        item = await queue.get()
        process(item)
        queue.task_done()
```

---

## 9. Trampas comunes en cada modelo

### Trampas threads en Python

- **Trampa 1 — "Multi-threading acelera mi cálculo"**: si es CPU-bound puro Python, **no** (GIL). Solo I/O-bound o si llamas a C que libera el GIL.
- **Trampa 2 — "Olvidar join"**: si no haces `t.join()`, el thread sigue corriendo cuando main termina. Si es daemon, muere abrupto. Si no, el programa no termina.
- **Trampa 3 — "Compartir estado mutable sin lock"**: race conditions garantizadas. Ver doc 01.
- **Trampa 4 — "Crear thread por cada task"**: thrashing. Usa `ThreadPoolExecutor`.

### Trampas multiprocessing

- **Trampa 1 — "Esperar que comparta variables globales"**: cada proceso tiene su propia memoria. Las modificaciones no se ven. Usar Queue/shared_memory para comunicar.
- **Trampa 2 — "Pasar objetos no picklables"**: multiprocessing hace pickle de los args. Lambdas, sockets y DB connections fallan. Solución: pasa identificadores, no objetos.
- **Trampa 3 — "Crear pools dentro de fork()"**: en Linux, `fork()` puede llevar a deadlock si el padre tiene threads. Linux 3.17+: usar `spawn` o `forkserver` start method.

### Trampas asyncio

- **Trampa 1 — "Llamar función blocking en código async"**: `time.sleep(5)` bloquea TODO el event loop. Usar `asyncio.sleep(5)`. Si necesitas función blocking, `run_in_executor`.
- **Trampa 2 — "Olvidar await"**:
  - `result = some_async_func()` ← no ejecuta, devuelve coroutine.
  - `result = await some_async_func()` ← correcto.

  Linters (mypy, pyright) detectan esto.
- **Trampa 3 — "Mezclar libraries sync y async"**: `requests` (sync) bloquea el event loop. Usa `httpx` async. `psycopg2` sync bloquea. Usa `asyncpg`. Cualquier I/O en hot path debe ser async-compatible.
- **Trampa 4 — "Async no es más rápido por arte de magia"**: si tu trabajo es CPU, async no ayuda. Si tienes UNA petición lenta, async es igual de lenta para esa petición. Async ayuda con **concurrencia**, no con latencia individual.
- **Trampa 5 — "Async + threads es mejor"**: solo si los threads son para tareas blocking. Si todo es async, no añadas threads.

---

## 10. Performance comparativa (orden de magnitud)

**Web server 10K conexiones simultáneas (I/O bound)**:

| Modelo | Resultado |
|---|---|
| Threads (1 por cnx) | Casi imposible. ~10K threads = thrashing. RIP. |
| Threads pool (100 threads) | Cuello de botella. Latencia alta. |
| Asyncio (1 thread) | Lo maneja fácilmente. Latencia baja. |

→ **Asyncio para I/O concurrente: ganador claro**.

**Cálculo Pi con N decimales (CPU bound)**:

| Modelo | Speedup vs baseline |
|---|---|
| Single thread Python | baseline |
| Threads (10) | 1.0-1.1x (casi igual por GIL) |
| Multiprocessing (10) | 8-10x más rápido (con 10 cores) |
| C extension (numpy) | 50-100x más rápido sin paralelismo |

→ **Para CPU: o procesos o C, NO threads en Python**.

**Pasar array de 100 MB entre workers**:

| Modelo | Tiempo |
|---|---|
| Threads | Instantáneo (memoria compartida) |
| Multiprocessing pickle | ~200ms cada vez |
| Multiprocessing shared_memory | Instantáneo |

→ **Si compartes mucho data: threads gana, o usa shared_memory**.

---

## 11. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

- Uvicorn corre asyncio. Tu API es naturalmente async.
- Si haces operación CPU-heavy (ej: hash 100k passwords) en endpoint, bloqueará el event loop. Toda la API se cuelga durante ese tiempo. Solución: `await loop.run_in_executor(None, hash_passwords, args)`.
- Para escalar: `--workers 4` (4 procesos), cada uno con su event loop.

### En entrevistas tecnicas

- **Pregunta**: "Cómo escalas tu API a 100K conexiones" → asyncio + 1 proceso por core (Uvicorn workers). Stateless servers detrás de load balancer. Horizontal scaling.
- **Pregunta**: "Por qué asyncio en vez de threads para web" → asyncio: 1 thread atiende miles de conexiones vía epoll. Threads: límite ~10K threads OS, context switching costoso. Memoria por task asyncio (~KB) << thread (~MB).
- **Pregunta**: "Cuándo usar multiprocessing en Python" → CPU-bound (rodear GIL). Cada proceso = 1 core efectivo. Caveat: overhead de pickle al pasar args.
- **Pregunta**: "Diferencia entre concurrency y parallelism" → concurrency: estructurar para manejar varias cosas (no necesariamente simultáneo). Parallelism: ejecutar simultáneo (varios cores). Async = concurrencia sin paralelismo.
- **Pregunta**: "Cuándo NO usar async" → CPU bound puro. Una sola request lenta (no hay nada que paralelizar). Equipo no familiarizado con async (productividad baja).

### Para embebido (perfil HW)

Si tu embebido tiene un loop principal que lee sensores y envía:

- Sensores en threads (cada uno I/O bound).
- Procesamiento en proceso separado (CPU).
- Coordinador vía queues.

O en async (si los drivers de los sensores son async-compatible).

---

## 12. Preguntas típicas de interview

- **Pregunta 1 — "Diferencia entre process, thread, coroutine"**: process: aislado, propia memoria. Thread: comparte memoria del proceso. Coroutine: función que puede suspenderse, ejecutada en event loop single-thread.
- **Pregunta 2 — "GIL: qué es y consecuencias"**: lock global en CPython. Solo 1 thread ejecuta bytecode. CPU-bound multi-threading no escala. I/O sí (libera GIL).
- **Pregunta 3 — "Cuándo asyncio vs threading vs multiprocessing"**: tabla decisión sección 6.
- **Pregunta 4 — "Cómo evitar bloquear el event loop"**: no llamar blocking ops directamente. Usar async libraries. Para CPU heavy: `run_in_executor` a un process pool.
- **Pregunta 5 — "Por qué Node.js es popular para web"**: misma respuesta que Python asyncio: I/O concurrency con event loop. Node tuvo async desde el día 1; Python lo añadió tarde (3.4+, maduró en 3.7+).
- **Pregunta 6 — "Cómo escalas a millones de conexiones"**: async + epoll/kqueue. C10K problem resuelto. Para C10M: kernel bypass (DPDK), userspace TCP.

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- 3 modelos: procesos, threads, async — diferencias clave.
- Concurrency vs parallelism.
- I/O bound vs CPU bound — cómo decide cuál usar.
- GIL Python: por qué los threads no aceleran CPU.
- Async: por qué single-thread escala a 100K conexiones.
- Patrón "1 proceso por core + async" para web servers.
- Tradeoffs: shared state vs aislamiento, overhead de creación, IPC.
- Trampas comunes: blocking en async, sin lock en threads, pickle en mp.
- `run_in_executor`: cómo combinar async + threads/procesos.

Si no puedes → relee.

---

## ¡Cluster Concurrency completado!

Has completado el tercer Tier 1. Resumen:

- `01-race-conditions` → el problema fundamental.
- `02-locks-y-mutex` → herramientas para sincronizar.
- `03-deadlock-livelock` → cuando las herramientas se vuelven contra ti.
- `04-async-vs-threads-procesos` → cuándo cada modelo.

**Próximo cluster sugerido**: `04_system_design_patterns/` (load balancing, caching, queues, CDN, rate limiting).

---

## Conexiones

- [[01-race-conditions]] — async + tasks pueden tener races lógicas
- [[02-locks-y-mutex]] — async tiene asyncio.Lock equivalente
- [[03-deadlock-livelock]] — async puede tener deadlocks lógicos
- [[../02_operating_systems/01-procesos-y-threads]] — base
- [[../02_operating_systems/03-scheduling]] — schedulers OS vs userspace
- [[../01_networking/04-sockets-y-puertos]] — I/O multiplexing es base de async
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Python asyncio docs** (docs.python.org/3/library/asyncio.html) — referencia oficial.
- **Async Python: A Complete Walkthrough** (Real Python) — buen tutorial.
- **The C10K Problem** (kegel.com/c10k.html) — paper histórico.
- **Concurrency is not Parallelism** (Rob Pike, talk YouTube) — clásico Go talk, conceptos universales.
- **`htop`, `py-spy`, `viztracer`** — profiling.
- **Yarl, asyncio, anyio, httpx** — librerías Python async.
