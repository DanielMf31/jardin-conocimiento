# 02 — Locks y mutex

> 📚 **Doc 2 del cluster Concurrency**. La herramienta principal para prevenir race conditions: las primitivas de sincronización que el SO y los runtimes te dan.
> 🔥 **Frecuencia interview**: aparece en preguntas de "implementa thread-safe X", debugging de contención.
> ⏱️ **Tiempo de lectura estimado**: 40-55 min.

---

## 1. La primitiva fundamental: mutex

Un **mutex (MUTual EXclusion)** es un objeto que solo UN thread puede "tener" a la vez. Mientras un thread lo tiene, los otros que lo pidan **esperan**. Cuando lo libera, OTRO thread lo recibe.

**Operaciones básicas**:
- `acquire()` / `lock()`: pedir el mutex. Bloquea si está ocupado.
- `release()` / `unlock()`: devolverlo. Despierta al siguiente esperando.

**Uso típico**:

```python
lock.acquire()
# ... critical section ...
lock.release()
```

**Python idiomático**:

```python
with lock:
    # ... critical section ...
# libera automáticamente al salir (incluso si excepción)
```

**Por qué `with` es importante**: si tu código lanza excepción dentro de la critical section y no usas `with`, el lock NUNCA se libera → deadlock para siempre.

---

## 2. Tipos de locks

### Mutex simple

1 dueño a la vez. Operaciones: lock/unlock. Es la primitiva más básica.

```python
import threading
lock = threading.Lock()
with lock:
    ...
```

**Características**:
- El thread que adquiere debe ser el que libera (en algunas implementaciones).
- **No es reentrante**: si el mismo thread intenta adquirir 2 veces → deadlock.

### Reentrant lock (RLock)

Permite que el **mismo thread** adquiera múltiples veces (cuenta interna). Debe liberar el mismo número de veces.

**Útil cuando**: función A llama a función B, ambas adquieren el mismo lock. Sin RLock, la función B se cuelga porque A ya tiene el lock.

```python
rlock = threading.RLock()

def a():
    with rlock:
        b()

def b():
    with rlock:    # con Lock() normal: deadlock. Con RLock: ok.
        ...
```

**Caveat**: ligeramente más lento que `Lock()` (mantiene contador y owner). Usa `Lock()` siempre que sea posible.

### Read-Write Lock (RWLock / shared-exclusive lock)

Distingue entre **lectores** (muchos a la vez OK) y **escritores** (1 exclusivo).

**Reglas**:
- N readers pueden tener el lock simultáneo.
- Un writer requiere acceso exclusivo (sin readers ni otros writers).

**Uso**: cuando hay muchas lecturas y pocas escrituras. Permite paralelismo de lectores.

**Disponibilidad por lenguaje**:

| Lenguaje | API |
|---|---|
| Python | No built-in en stdlib. Implementar con Condition/Semaphore o usar libs (`aiorwlock`, `readerwriterlock`) |
| C++ | `std::shared_mutex` (C++17) |
| Java | `ReentrantReadWriteLock` |

**Caveat**: starvation de writers si llegan readers continuos.

### Spinlock

En vez de bloquear el thread, "spin" en bucle revisando si el lock se libera:

```c
while (!try_acquire()) { /* busy wait */ }
```

**Ventaja**: si el lock se libera **rápido** (< coste de context switch), el spinlock es más rápido (no paga el switch).

**Desventaja**: quema CPU mientras espera. Si el lock tarda mucho → desperdicio enorme.

**Uso**: solo en kernel y en código donde sabes que la critical section es CORTA. El kernel de Linux usa spinlocks internamente para colas de scheduler. En user space casi nunca lo necesitas.

**Python**: no expone spinlocks (el GIL hace que no tengan sentido).

### Semaphore (semáforo)

Generalización del mutex: contador de "permisos" disponibles. Mutex = semáforo con contador 1 (binary semaphore).

**Operaciones**:
- `acquire()`: si contador > 0, decrementa. Si no, espera.
- `release()`: incrementa contador.

**Uso típico**: limitar concurrencia. Ej: pool de N conexiones DB.

```python
sem = Semaphore(10)   # max 10 simultáneos

def db_query():
    with sem:
        # ... query, max 10 a la vez ...
```

**En Python**:
- `threading.Semaphore(N)`.
- `threading.BoundedSemaphore(N)` — error si haces release más de N veces.

### Condition variables (waits + signals)

Permiten a los threads:
- Esperar a que una **condición** se cumpla (`wait`).
- Despertar a otros cuando la condición cambia (`notify`, `notify_all`).

**Uso típico**: producer-consumer.

```python
condition = threading.Condition()

# Consumer
with condition:
    while not item_available():
        condition.wait()    # libera lock + espera; al despertar, re-adquiere
    item = consume()

# Producer
with condition:
    produce(item)
    condition.notify()      # despierta UN consumer
    # condition.notify_all() despierta a todos
```

**Por qué `while` y no `if`**: spurious wakeups — el thread puede despertarse SIN haber sido notificado. Siempre re-verifica la condición tras `wait`.

### Event

Señal one-time entre threads. Los threads esperan con `event.wait()`. Cuando alguien llama `event.set()`, todos despiertan.

```python
event = threading.Event()

# Worker
event.wait()         # bloquea hasta que se setee
start_processing()

# Coordinator
event.set()          # señal: ya pueden procesar
```

### Barrier

Sincroniza N threads para que todos lleguen a un punto antes de continuar.

**Uso**: simulaciones, parallel algorithms con fases.

```python
barrier = threading.Barrier(parties=4)

def worker():
    do_phase_1()
    barrier.wait()    # espera a los 4 threads aquí
    do_phase_2()      # todos empiezan fase 2 a la vez
```

---

## 3. Atomic operations (sin locks)

Las **instrucciones atómicas de la CPU** garantizan ejecución atómica de ciertas operaciones por hardware, sin necesidad de locks.

**Primitivas comunes**:
- **CAS (Compare-And-Swap)**: si valor es X, cambia a Y. Atómico.
- **FAA (Fetch-And-Add)**: incrementa y devuelve valor anterior. Atómico.
- **LL/SC (Load-Linked/Store-Conditional)**: equivalente RISC.

**Disponibilidad por lenguaje**:

| Lenguaje | API |
|---|---|
| C++ | `std::atomic<int>` |
| Java | `AtomicInteger`, `AtomicReference` |
| Rust | `std::sync::atomic` |
| Go | `sync/atomic` |
| Python | NO atomics built-in. `queue.Queue` thread-safe internamente |

**Ventaja**: 10-100x más rápido que locks para operaciones simples. No hay context switching.

**Desventaja**: solo funciona para operaciones MUY pequeñas (1 variable típicamente). La programación lock-free es altamente compleja (ABA problem, memory ordering). Para casos simples como contadores: úsalo. Para estructuras complejas: locks.

**Ejemplo Java**:

```java
AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();    // atómico, sin lock

// CAS pattern:
while (true) {
    int current = counter.get();
    int next = compute_next(current);
    if (counter.compareAndSet(current, next)) break;
    // si CAS falla (otro thread cambió valor), retry.
}
```

---

## 4. Performance — el coste de los locks

**Coste típico** de un lock acquire/release:

| Escenario | Coste aproximado |
|---|---|
| Sin contención | ~20-50 nanosegundos |
| Con contención, espera corta (puede spinear) | ~100ns - 1μs |
| Con contención, parking del thread (context switch) | ~5-50μs |

**Observaciones**:
- Si tu critical section es < tiempo de un context switch, considera spinlock.
- Si es muy larga (>1ms), no importa el coste del lock.
- Si hay **mucha contención**, replantea el diseño (más fine-grained, lock-free, sharding).

**Contención alta = scaling negativo**: más threads = más contención = peor throughput total. La curva típica: rendimiento sube con N hasta cierto punto, luego BAJA.

**Debugging contention**:
- Linux: `perf lock record / report`.
- Java: `jstack`, JMC.
- Python: `viztracer`, `py-spy`.

---

## 5. Granularidad de locks

| Granularidad | Descripción | Trade-off |
|---|---|---|
| **Coarse-grained** | Un solo lock global protege TODO. Ej: GIL de Python | Simple, fácil razonar. Mata performance bajo carga |
| **Fine-grained** | Muchos locks pequeños, uno por recurso/elemento. Ej: ConcurrentHashMap Java tiene lock por bucket | Mejor paralelismo. Más complejo (riesgo de deadlock por orden de adquisición) |
| **Sharded** | Divide el recurso en N "shards", cada uno con su lock. Ej: counter sharded — N counters separados, suma al leer total | Reduce contención sin complejidad de fine-grained extremo |

**Regla de oro**: empieza coarse. Si profileas y ves contención → hazlo fine-grained donde duela.

---

## 6. Lock-free vs wait-free

**Lock-free**:
- Nunca hay deadlock. Si un thread se cuelga, el sistema progresa.
- Garantía: en cualquier momento, **algún** thread progresa.
- Implementado con atomics + retry loops (CAS).

**Wait-free**:
- Garantía aún más fuerte: **todos** los threads progresan en N pasos.
- Sin retries. Muy difícil de implementar.
- Casi nadie lo usa en la práctica.

**Ejemplos de lock-free**:
- Concurrent queues (Disruptor, MichaelScott queue).
- Atomic counters.
- Some data structures (skip lists, hash maps).

**Cuándo usar lock-free**:
- Performance crítico (HFT, sistemas real-time).
- Donde no puedes permitirte bloqueos.

**Cuándo no**:
- Casi siempre. Los locks normales son suficientes y mucho más simples.
- Bugs en lock-free son demoledores y casi imposibles de debuggear.

---

## 7. Deadlock — el peligro principal de los locks (preview)

**Deadlock**: dos o más threads esperando mutuamente, ninguno avanza.

**Ejemplo mínimo**:

- Thread A:
  - `lock(L1)`
  - `lock(L2)`
- Thread B:
  - `lock(L2)`
  - `lock(L1)`

**Timing malo**:
1. A adquiere L1.
2. B adquiere L2.
3. A intenta L2 → espera (B lo tiene).
4. B intenta L1 → espera (A lo tiene).
5. **Ambos bloqueados para siempre**.

**Prevención básica**: adquirir locks SIEMPRE en el mismo orden. Si todo el código adquiere L1 ANTES que L2, deadlock imposible.

(Ver doc 03-deadlock-livelock para más detalle.)

---

## 8. Patrones thread-safe en Python stdlib

- **`queue.Queue`**: cola FIFO thread-safe. Ideal producer-consumer. `q.put(item)` y `q.get()` son thread-safe.
- **`queue.LifoQueue`, `queue.PriorityQueue`**: variantes — stack y priority.
- **`collections.deque`**: append/popleft son O(1) y atómicos en CPython (gracias al GIL). Rápido para queues simples sin necesidad de bloqueo extra.
- **`threading.local()`**: storage **por thread**. Cada thread ve su propia copia. Útil para contexts (request id, db connection, etc.).

```python
data = threading.local()
def worker():
    data.x = 42        # solo este thread ve esto
    do_stuff()
```

- **`concurrent.futures.ThreadPoolExecutor`**: pool gestionado. Submit tasks, recibe Futures. Internamente usa locks correctamente.

---

## 9. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

- FastAPI con asyncio: NO necesitas locks típicos para datos en memoria (todo en single thread). Pero SÍ los necesitas si:
  - Usas thread pool para tareas síncronas (e.g. blocking DB driver).
  - Compartes recursos entre tasks asyncio que pueden interleavar en awaits.
- Para tu phonebook con JSON: si haces guarda async + tienes múltiples requests modificando, considera `asyncio.Lock`.

### En entrevistas tecnicas

**Pregunta**: "Implementa thread-safe Singleton".
- Double-checked locking pattern (sección 7 doc anterior).
- En Python moderno: usar `functools.lru_cache` o módulo (singleton implícito).

**Pregunta**: "Cómo implementas un connection pool thread-safe".
- Semaphore para limitar concurrencia + lock para gestionar lista de conexiones.
- O usar `queue.Queue` como pool (put = devolver, get = adquirir).

**Pregunta**: "Cuándo usar lock vs atomic vs lock-free".
- Operación simple sobre 1 variable: atomic.
- Critical section pequeña: spinlock o lock simple.
- Critical section grande: lock simple.
- Performance crítico extremo: considerar lock-free (con cuidado).

**Pregunta**: "Reader-writer lock vs mutex normal".
- RWLock permite N lecturas concurrentes, 1 escritura exclusiva. Útil cuando lecturas dominan vastly.
- Si writes son frecuentes, mutex normal puede ser igual o más rápido.

---

## 10. Trampas típicas

**Trampa 1 — "Lock garantiza que no hay race conditions"**: solo si TODOS los accesos al recurso usan el MISMO lock. Si un acceso sin lock se cuela, la race condition vuelve.

**Trampa 2 — "Más locks = más seguridad"**: más locks = más complejidad = más probabilidad de deadlock. Usa el mínimo necesario.

**Trampa 3 — "Lock global no escala pero es correcto"**: sí, pero con suficiente contención el sistema se vuelve secuencial. Para escalar: fine-grained o sharded.

**Trampa 4 — "Adquirir y olvidar liberar"**: usa `with lock:` SIEMPRE. Si haces acquire/release manual y hay excepción entre medio → lock nunca se libera → deadlock.

**Trampa 5 — "Spinlock siempre es más rápido"**: solo para critical sections cortas + bajo contention. Si esperas mucho o hay alta contention → quema CPU sin beneficio. Usa lock normal.

**Trampa 6 — "Atomic int en Python con `threading.Lock`"**: es overkill (y más lento) si solo incrementa contador. Mejor: contador no-thread-safe protegido por GIL para `+=` en int (cuidado con el caveat). O usar `multiprocessing.Value('i', 0, lock=True)` cross-process.

**Trampa 7 — "Notificar sin haber adquirido el lock"**: `Condition.notify()` debe llamarse mientras tienes el lock asociado. Si no, el comportamiento es indefinido.

---

## 11. Preguntas típicas de interview

**Pregunta 1 — "Diferencia entre mutex y semáforo"**:
- Mutex: 1 owner a la vez (binario).
- Semáforo: contador de N permisos. Mutex es semáforo con N=1.

**Pregunta 2 — "Diferencia entre Lock y RLock"**:
- Lock: no reentrante. Mismo thread adquiriendo 2 veces → deadlock.
- RLock: reentrante con contador. Usa cuando funciones recursivas o pueden llamarse mutuamente con mismo lock.

**Pregunta 3 — "Cuándo usarías RWLock vs mutex"**:
- RWLock cuando reads >> writes y quieres paralelismo de lectores.
- Mutex normal cuando writes son frecuentes o critical section corta.

**Pregunta 4 — "Qué es double-checked locking y para qué sirve"**: para lazy initialization thread-safe sin penalización de lock en cada call. Check sin lock (rápido) → si null, lock + check de nuevo + create.

**Pregunta 5 — "Cómo protegerías una estructura de datos con muchos accesos"**:
- Si reads dominan: RWLock.
- Si todo balanceado: locks fine-grained (lock por bucket en hashmap).
- Para counters: AtomicInteger.
- Para queues: lock-free queue ya implementada (ConcurrentLinkedQueue Java).

**Pregunta 6 — "Diferencia entre lock-free y wait-free"**:
- Lock-free: algún thread progresa siempre.
- Wait-free: TODOS los threads progresan en N steps.
- Wait-free es más fuerte y casi imposible de implementar.

---

## 12. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Qué es un mutex y cuándo usarlo (proteger critical section).
- Diferencia Lock vs RLock vs Semáforo.
- RWLock: cuándo y por qué.
- Condition variables: por qué `while` no `if` (spurious wakeups).
- Atomic operations: cuándo son alternativa válida a locks.
- Granularidad: coarse vs fine vs sharded — trade-offs.
- Coste de un lock acquire (ns con/sin contention).
- Lock-free vs wait-free, cuándo lock-free.
- Por qué `with lock:` siempre (vs acquire/release manual).
- Patrón producer-consumer con Condition o `queue.Queue`.

Si no puedes → relee.

---

## Conexiones

- [[01-race-conditions]] — el problema que los locks resuelven
- [[03-deadlock-livelock]] — el problema que los locks pueden CAUSAR
- [[04-async-vs-threads-vs-procesos]] — alternativas que evitan locks
- [[../02_operating_systems/01-procesos-y-threads]] — threads que necesitan sincronización
- [[../05_database_internals/02-acid-transactions]] — locks a nivel DB
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **Java Concurrency in Practice** (Goetz) — ya mencionado, biblia.
- **The Little Book of Semaphores** (Downey, gratis greenteapress.com).
- **OSTEP** capítulos 28-31 (Locks, Semaphores, Condition Variables). GRATIS.
- **`perf lock`, `mutrace`** — debugging de contención de locks.
- **`py-spy`** — profiling Python con visualización de contention.
