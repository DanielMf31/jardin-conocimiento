# 01 — Race conditions

> **Doc 1 del cluster Concurrency**. El problema fundamental de la programación concurrente: cuando varias cosas pasan a la vez sin coordinación. Casi todos los bugs de threads vienen de aquí.
> **Frecuencia interview**: aparece SIEMPRE en preguntas de threads/concurrency. La pregunta "incrementa contador de 2 threads" es clásica.
> **Tiempo de lectura estimado**: 40-60 min.

---

## 1. Qué es una race condition

Una **race condition** ocurre cuando el resultado de tu programa depende del **orden de ejecución** de operaciones concurrentes. Si dos threads se "carrean" para acceder al mismo recurso, el resultado puede ser distinto cada ejecución.

**Ejemplo clásico — el contador roto**:

- Variable compartida: `counter = 0`.
- Thread A: `counter = counter + 1` (ejecuta 100 veces).
- Thread B: `counter = counter + 1` (ejecuta 100 veces).
- **Expectativa**: `counter = 200`.
- **Realidad**: `counter = 137` (o 184, o 162, varía cada vez).

¿Por qué?

### El problema visualizado

`counter = counter + 1` parece atómico. **No lo es**. Por debajo se traduce en 3 instrucciones distintas:

1. **Leer** `counter` de memoria a registro CPU.
2. **Incrementar** el registro.
3. **Escribir** el registro de vuelta a memoria.

El SO puede interrumpir entre cualquiera de ellas.

### Trace del bug

```
Estado inicial: counter = 5

Thread A                          Thread B
─────────────                    ─────────────
1. lee counter (5)
                                  1. lee counter (5)   ← AMBOS leyeron 5
2. incrementa (5+1=6)
                                  2. incrementa (5+1=6) ← AMBOS calcularon 6
3. escribe counter=6
                                  3. escribe counter=6  ← AMBOS escribieron 6

Resultado: counter = 6 (debería ser 7).
Una incrementación SE PERDIÓ.
```

Si esto pasa 1000 veces, te pierdes ~30% de los increments.

**El núcleo del problema**: read-modify-write **no es atómico**, y dos threads pueden hacer la lectura ANTES de que cualquiera escriba.

---

## 2. Tipos de race conditions

### 2.1 Lost update (el del contador)

A lee X. B lee X. A escribe X+1. B escribe X+1. La actualización de A se perdió.

**Ejemplos reales**:
- Contadores de visitas web sin lock.
- Saldo bancario actualizado por dos requests concurrentes.
- Inventario de e-commerce (vendiste 1 unidad pero quedan 5 en vez de 4).

### 2.2 Read inconsistency (lectura inconsistente)

A está modificando una struct con varios campos. B lee mientras A va a medias y ve un estado intermedio incoherente.

**Ejemplo**:

- `account = {balance: 100, transactions: [...]}`
- Thread A (transferir 50 a otra cuenta):
  1. `account.balance -= 50` (balance ahora 50).
  2. `account.transactions.append(...)` ← B lee aquí.
  3. ... (otras cosas).
- Thread B vio `balance=50` pero **sin** la transacción correspondiente. Estado inválido.

### 2.3 TOCTOU (Time-Of-Check, Time-Of-Use)

Verificas algo, después actúas. Entre check y action, otro thread cambia el estado.

**Ejemplo pseudo-código**:

```python
if file.exists():           # TOC (time of check)
    data = file.read()      # TOU (time of use)
```

Entre TOC y TOU otro thread/proceso **borró** el archivo. Tu `read()` falla con `FileNotFoundError` aunque "verificaste".

**Ejemplo banco**:

```python
if balance >= amount:       # TOC: balance es 100, amount es 80, OK
    balance -= amount       # TOU: pero entre medio otro hilo
                            #      gastó 50, ahora balance=50
                            #      y restas 80 → balance=-30!
```

**Solución**: lock toda la operación check+action como **unidad atómica**.

**Vulnerabilidad de seguridad**: TOCTOU es la base de muchos exploits Unix:

```c
if (access(path) == OK)    // check permisos
    open(path);            // otro proceso cambia symlink justo aquí
```

Solución: usar atomic API (open con flags adecuados, no separar check+open).

### 2.4 Write skew (en bases de datos)

Dos transacciones leen el mismo dato, basan su decisión en él y escriben distintas cosas. Cada una "vio" que la otra no había escrito todavía.

**Ejemplo médico**: regla "siempre debe haber al menos 1 médico de guardia". Hay 2 médicos: Alice y Bob, ambos de guardia.

- **Tx A** (Alice quiere irse):
  - `SELECT count(*) FROM doctors WHERE on_call=true` → 2.
  - if `count >= 2`: `UPDATE doctors SET on_call=false WHERE name='Alice'`.
- **Tx B** (Bob quiere irse, simultánea):
  - `SELECT count(*) FROM doctors WHERE on_call=true` → 2.
  - if `count >= 2`: `UPDATE doctors SET on_call=false WHERE name='Bob'`.

Ambas hacen commit. Ahora 0 médicos de guardia. Regla rota.

**Solución**: serializable isolation level (ver doc 05_database_internals).

### 2.5 ABA problem (en concurrencia lock-free)

Thread A lee valor V. Thread B cambia V → otra cosa → de vuelta a V. Thread A no detecta el cambio.

**Caso típico en CAS (compare-and-swap)**: Thread A intenta CAS — si valor es V, cambiar a W. CAS verifica que valor sigue siendo V → sí → cambia. Pero realmente B lo cambió y restauró → A no se entera.

**Solución**: tagged pointers — añadir "versión" al valor. CAS compara `(V, version)`. También hazard pointers, RCU.

**Nivel**: muy avanzado (lock-free programming). Para no crítico.

---

## 3. Por qué race conditions son tan jodidas

1. **No deterministas**: mismo código, mismo input, distinto output. Imposible reproducir consistentemente.
2. **Solo aparecen bajo carga**: en tests con 1 request, todo bien. En producción con 1000 req/s, fallos misteriosos cada hora.
3. **Se esconden en casos raros**: un bug que solo pasa cuando dos threads están en la misma instrucción. Ventana microscópica. Puede manifestarse 1 vez al día.
4. **Síntomas lejanos**: race condition en módulo X causa data corruption en módulo Y, error en Z 5 minutos después.
5. **Debugging altera el timing**: añades `print()` para investigar → el bug desaparece (Heisenbug). Quitas el `print` → vuelve.
6. **Tests normales no las pillan**: tests unitarios típicos ejecutan secuencial, sin contención.

**Conclusión**: prevenirlas SIEMPRE es más barato que debuggearlas. La disciplina de threading > intentar arreglar después.

---

## 4. Cuando NO hay race condition

- **Si el estado es immutable**: constantes, frozen objects, tuples Python. Múltiples readers nunca causan problema. Múltiples threads pueden leer sin lock.
- **Si el acceso es local al thread**: variables locales (en stack del thread) son privadas. Nadie más las ve.
- **Si es un solo thread**: trivial — no hay concurrencia. Por eso async/await en single-threaded es libre de races (asyncio Python) — solo conmuta en awaits explícitos.
- **Si usas operaciones atómicas**: las CPUs modernas tienen instrucciones atomic (CAS, fetch-and-add). En lenguajes: `AtomicInteger` Java, `atomic` Rust, `std::atomic` C++. Python: `queue.Queue` (thread-safe), `threading.Lock` primitivos.

---

## 5. El concepto de "critical section"

**Critical section**: trozo de código donde se accede a estado **compartido**. Si varios threads la ejecutan simultáneamente → race condition.

**Objetivo**: garantizar que SOLO UN thread esté en la critical section a la vez. Esto se llama **mutual exclusion (mutex)**.

**Propiedades necesarias para mutex correcto**:
1. **Mutual exclusion**: solo 1 thread dentro.
2. **Progress**: si nadie está dentro, alguien que quiera entrar puede.
3. **Bounded waiting**: nadie espera infinitamente (no starvation).
4. **No assumption** sobre velocidad de threads.

**El mecanismo más usado**: el **lock/mutex** — ver doc 02 del cluster.

---

## 6. Ejemplo concreto en Python — el bug + la solución

```python
import threading

# ============== VERSIÓN ROTA ==============
counter = 0

def increment_unsafe():
    global counter
    for _ in range(100_000):
        counter += 1   # ← race condition aquí

threads = [threading.Thread(target=increment_unsafe) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()

print(counter)
# EXPECTATIVA: 1_000_000
# REALIDAD:    683524 (varía cada vez)


# ============== VERSIÓN CON LOCK ==============
counter = 0
lock = threading.Lock()

def increment_safe():
    global counter
    for _ in range(100_000):
        with lock:           # adquiere lock al entrar al with
            counter += 1     # critical section protegida
        # libera lock al salir del with

threads = [threading.Thread(target=increment_safe) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()

print(counter)
# AHORA: 1_000_000 SIEMPRE
```

> **Sobre el GIL**: en CPython el GIL hace que `counter += 1` SOMETIMES sea atómico (operación simple sobre un int). Pero **NO confíes en el GIL para corrección** — puede no serlo en operaciones más complejas, y **otros runtimes Python (PyPy free-threaded, futuro Python sin GIL) NO lo serán**. Usa locks explícitos siempre.

---

## 7. Ejemplos de race conditions en código real

### Ejemplo 1: lazy initialization rota

```python
# ROTO
_instance = None

def get_instance():
    global _instance
    if _instance is None:        # ← TOCTOU
        _instance = ExpensiveClass()
    return _instance

# SI dos threads entran a la vez:
# Ambos ven _instance is None → ambos crean ExpensiveClass.
# Quedan 2 instancias, no 1. "Singleton" roto.

# CORRECTO con double-checked locking:
import threading
_instance = None
_lock = threading.Lock()

def get_instance():
    global _instance
    if _instance is None:        # check rápido sin lock
        with _lock:
            if _instance is None:  # check de nuevo dentro del lock
                _instance = ExpensiveClass()
    return _instance
```

### Ejemplo 2: increment de dict

```python
# ROTO
counts = {}

def add(key):
    if key in counts:
        counts[key] += 1
    else:
        counts[key] = 1

# Race: dos threads ven key NO está → ambos hacen counts[key] = 1.
# Pierdes uno.

# CORRECTO con defaultdict + lock:
from collections import defaultdict
counts = defaultdict(int)
lock = threading.Lock()

def add(key):
    with lock:
        counts[key] += 1
```

### Ejemplo 3: chequeo de stock

```python
# ROTO en e-commerce
def buy(product_id, qty):
    stock = db.get_stock(product_id)
    if stock >= qty:                       # TOC
        db.set_stock(product_id, stock-qty)  # TOU
        return "OK"
    return "Sin stock"

# Race: dos compradores ven stock=5, ambos compran 5.
# Stock final: -5. "Vendiste" 10 unidades cuando solo había 5.

# CORRECTO:
def buy(product_id, qty):
    # En DB: usar UPDATE con WHERE atomic
    rows = db.execute(
        "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
        (qty, product_id, qty)
    )
    if rows == 0:
        return "Sin stock"
    return "OK"

# DB lock interno garantiza atomicidad del UPDATE+condición.
```

---

## 8. Memory model y reordering (avanzado)

La CPU optimiza tu código **reordenando** instrucciones. La RAM tiene **caches por core** que pueden no estar sincronizados.

**Consecuencia**: lo que tu código DICE que pasa NO siempre es lo que la CPU EJECUTA. En single-thread esto es invisible (la CPU garantiza efecto observable). En multi-thread, los threads pueden VER cosas en orden raro.

**Ejemplo**:

```
Thread A:
  x = 1
  flag = true

Thread B:
  if flag:
    assert x == 1   ← PUEDE FALLAR si CPU reordenó!
```

**Solución**: **memory barriers (memory fences)** — instrucciones que GARANTIZAN orden. Locks/mutex incluyen barriers automáticamente. En lock-free programming son explícitos (`atomic_thread_fence` en C++).

**Lenguajes modernos**: Java, C++, Rust, C# definen "memory model" formal con garantías happens-before. Si haces todo via locks/atomics, no te tienes que preocupar.

**Python**: no tiene memory model formal documentado. En la práctica, el GIL te salva mucho. Pero NO confíes — usa locks.

---

## 9. Cómo detectar race conditions

**Herramientas**:

1. **Thread Sanitizer (TSan)**: compilar con `-fsanitize=thread` (gcc/clang). Detecta races en runtime durante tests. Para C/C++/Go.
2. **Helgrind (valgrind)**: similar a TSan pero para C/C++.
3. **Java/Scala**: FindBugs, SpotBugs detectan patrones inseguros.
4. **Python**: no hay herramienta automática (GIL complica). Code review + tests específicos de concurrencia. `threading.Lock` con asserts en development.
5. **Stress testing**: ejecutar tu test 10000 veces con thread interleaving aleatorio. Si alguno falla → race condition. En Linux: `stress-ng` para variar carga.

**Review manual — preguntas a hacerte**:
1. ¿Qué estado se comparte entre threads?
2. ¿Cada acceso compartido está protegido por lock?
3. ¿Hay alguna lectura sin lock seguida de decisión?
4. ¿Hay alguna operación read-modify-write sin lock?
5. ¿Algún check seguido de action sin atomicidad?

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

- Si Uvicorn corre con UN solo worker: NO hay race conditions (asyncio es single-threaded).
- Si arrancas con `--workers 4`: cada worker es un proceso separado, cada uno lee/escribe `contacts.json` sin coordinación. **Problema**: dos workers pueden leer simultáneo y sobreescribir los cambios del otro al guardar (lost update). Solución: file locking (`fcntl`), o mejor, mover a SQLite (con WAL) o Postgres.

### En entrevistas tecnicas

**Pregunta clásica**: "Tienes counter compartido por N threads, cada uno incrementa M veces. ¿Resultado?"
- Sin sincronización: indeterminado, < N*M.
- Con lock: N*M.
- Con atomic int: N*M (más rápido que lock).

**Pregunta**: "Diseña sistema de votación concurrente".
- Race condition: contar votos sin perder ninguno.
- Soluciones: lock global (no escala), sharding (cuenta por shard, sumar), Redis INCR (atomic).

**Pregunta**: "¿Por qué tu test pasa en local pero falla en CI?"
- Posible race condition. CI tiene timing distinto, threads se interleavan diferente. Buscar accesos compartidos sin lock.

**Pregunta**: "¿Cómo prevenirías double-charge en pagos?"
- Idempotency key (cliente envía UUID, server detecta duplicado).
- Atomic transaction en DB con unique constraint.
- No hacer "check + insert" sin atomicidad.

### En embebido (perfil HW)

Embedded con interrupts: similar a threads. Una interrupción puede preempt el código main. Necesitas critical sections (disable interrupts) para acceder variables compartidas con ISRs.

---

## 11. Trampas típicas

**Trampa 1 — "Solo afecta a multi-threading"**: no. Multi-process compartiendo recursos (DB, archivos, shared memory). Multi-machine compartiendo BD. Distributed systems es race conditions a otra escala.

**Trampa 2 — "Mi operación es 'casi atómica', no necesita lock"**: casi atómico = no atómico = race condition. El "casi" desaparece bajo carga.

**Trampa 3 — "El GIL me protege en Python"**: solo bytecode operations simples. `+=` en int sí. `+=` en lista podría no. No confíes — usa locks.

**Trampa 4 — "Hago read sin lock pero solo write con lock"**: read sin lock puede ver estado inconsistente (campo a medias actualizado). Necesitas RWLock o lock para AMBOS.

**Trampa 5 — "Si añado más threads, va más rápido"**: si la critical section serializa, MÁS threads = MÁS contención = MÁS LENTO. El óptimo no es siempre N=cores.

**Trampa 6 — "Tests pasan, no hay race"**: tests con 1 thread NUNCA detectarán races. Necesitas stress testing con concurrencia real.

**Trampa 7 — "Async/await tiene races"**: en single-thread Python asyncio, NO entre awaits. Pero SÍ si tu task hace await en medio de operación crítica y otra task entra y ve estado intermedio.

---

## 12. Preguntas típicas de interview

**Pregunta 1 — "Qué es una race condition"**: cuando el resultado depende del orden de ejecución de operaciones concurrentes sobre estado compartido.

**Pregunta 2 — "Por qué `counter += 1` no es atómico"**: son 3 instrucciones — leer, incrementar, escribir. El SO puede interrumpir entre cualquiera. Threads pueden interleavar y pisar updates.

**Pregunta 3 — "Diferencia entre TOCTOU y lost update"**:
- TOCTOU: check + action, estado cambia entre medio.
- Lost update: dos writes, uno se pisa.
- Ambos son tipos de race conditions.

**Pregunta 4 — "Cómo prevenir race conditions"**: mutual exclusion (locks). Operaciones atómicas. Estado inmutable. Single-thread + async. Message passing.

**Pregunta 5 — "Por qué tu app a veces da resultados raros bajo carga"**: probablemente race condition. El debugger no lo encuentra (heisenbug). Análisis: identificar estado compartido, asegurar acceso protegido.

**Pregunta 6 — "Diferencia entre race condition y deadlock"**:
- Race: sin lock o lock mal puesto, resultados inconsistentes.
- Deadlock: locks puestos pero adquiridos en orden que se bloquean mutuamente. Threads esperan eternamente.
- (Ver doc 03 deadlock-livelock.)

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Qué es una race condition con un ejemplo concreto.
- Por qué `counter += 1` no es atómico (3 instrucciones).
- Tipos: lost update, TOCTOU, write skew, ABA.
- Por qué son no-deterministas y difíciles de debuggear.
- Concepto de critical section y mutual exclusion.
- Cuándo NO hay race (immutable, local, single-thread).
- Cómo se previene (locks, atomic ops, estado inmutable).
- Por qué tests normales no las detectan.
- Heisenbugs: por qué los prints las "arreglan".

Si no puedes → relee.

---

## Conexiones

- [[02-locks-y-mutex]] — solución estándar a races
- [[03-deadlock-livelock]] — problemas que causan los locks mal usados
- [[04-async-vs-threads-vs-procesos]] — modelos que evitan races
- [[../02_operating_systems/01-procesos-y-threads]] — threads comparten memoria → races
- [[../05_database_internals/03-isolation-levels]] — race conditions en DBs
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **OSTEP** capítulo 26 (Concurrency intro). GRATIS pages.cs.wisc.edu/~remzi/OSTEP/
- **The Little Book of Semaphores** (Allen Downey) — gratis, denso pero buenísimo.
- **Java Concurrency in Practice** (Brian Goetz) — biblia. Java, conceptos universales.
- **C++ Concurrency in Action** (Anthony Williams) — para C++ moderno.
- **`helgrind`, `tsan`** — detectores automáticos.
- **rr (record-replay)** — debugger que captura ejecuciones no-deterministas.
