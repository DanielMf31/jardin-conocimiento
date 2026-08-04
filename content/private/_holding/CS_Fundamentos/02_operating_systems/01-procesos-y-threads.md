# 01 — Procesos y threads

> **Doc 1 del cluster Operating Systems**. Aquí entiendes cómo el SO ejecuta múltiples programas a la vez y cómo un programa puede hacer varias cosas en paralelo.
> **Frecuencia interview**: aparece en concurrency questions, en "¿qué pasa cuando ejecutas X?", y en debugging de performance.
> **Tiempo de lectura estimado**: 50-75 min.

---

## 1. La jerarquía: programa → proceso → thread

**Programa** es el archivo en disco. Bytes de código + datos. Estático. Ejemplo: `/usr/bin/python`, `/home/usuario/script.py`.

**Proceso** es una INSTANCIA en EJECUCIÓN de un programa. Dinámico. Tiene su propio espacio de memoria, file descriptors, etc. Cuando ejecutas `python script.py`, se crea UN proceso. Si lo ejecutas 3 veces en paralelo, hay 3 procesos distintos.

**Thread (hilo)** es una unidad de EJECUCIÓN dentro de un proceso. Comparte memoria con otros threads del mismo proceso. Un proceso Python puede tener 1 thread (default) o N threads.

**Analogía**: programa = receta de cocina (archivo). Proceso = una persona cocinando esa receta (memoria, ingredientes propios). Thread = manos de la persona (varias manos del mismo cocinero comparten los ingredientes; varias personas tienen ingredientes separados).

---

## 2. Anatomía de un proceso (lo que tiene en memoria)

```
DIRECCIÓN ALTA  ┌──────────────────────────┐
                │   STACK                  │  ← variables locales, call frames
                │                          │     crece HACIA ABAJO
                ├──────────────────────────┤
                │     ↓                    │
                │     (espacio libre)      │
                │     ↑                    │
                ├──────────────────────────┤
                │   HEAP                   │  ← memoria dinámica (malloc/new)
                │                          │     crece HACIA ARRIBA
                ├──────────────────────────┤
                │   BSS                    │  ← variables globales sin inicializar
                ├──────────────────────────┤
                │   DATA                   │  ← variables globales inicializadas
                ├──────────────────────────┤
                │   TEXT (code)            │  ← instrucciones del programa
DIRECCIÓN BAJA  └──────────────────────────┘
```

Además del espacio de memoria, el proceso tiene:
- **PID** (Process ID): número único asignado por el SO.
- **PPID** (Parent PID): el que lo creó.
- **File descriptors**: stdin, stdout, stderr + archivos abiertos.
- **Registros del CPU** (cuando está en ejecución).
- **Tabla de signals**.
- **Working directory**.
- **User/group ID** (permisos).
- **Environment variables**.

**Cada proceso tiene su PROPIO espacio de memoria**. El proceso A NO puede leer la memoria del proceso B (el SO + MMU lo impiden — virtual memory, ver doc 02).

**Implicación**: para que dos procesos compartan datos hay que usar **IPC** (Inter-Process Communication): pipes, sockets, shared memory, message queues. Es **costoso**.

---

## 3. Anatomía de un thread

**Threads de un mismo proceso comparten**:
- Espacio de memoria (heap, data, text, BSS).
- File descriptors.
- Working directory.
- Signal handlers.
- Process ID.

**Cada thread tiene su propio**:
- **Stack** (su cadena de call frames).
- Registros del CPU.
- Thread ID (TID).
- Errno.
- Signal mask.

**Implicación**: dos threads del mismo proceso pueden leer/escribir las mismas variables. Esto es **rápido** (no hay IPC) pero **peligroso** (race conditions — ver doc 03_concurrency).

---

## 4. Crear procesos: `fork()` + `exec()`

En Unix, los procesos se crean con un patrón clásico de 2 syscalls:

**`fork()`**: CLONA el proceso actual. El padre y el hijo siguen ejecutándose desde el punto del fork. La única diferencia: `fork()` devuelve `0` al hijo, PID del hijo al padre, `-1` si error.

**`exec()`**: REEMPLAZA la imagen del proceso actual con un nuevo programa. El proceso sigue siendo el mismo (mismo PID), pero ahora ejecuta otro código.

**Patrón típico**:
```c
pid = fork()
if pid == 0:
    # Soy el hijo
    exec("/usr/bin/ls", ["ls", "-la"])
else:
    # Soy el padre
    wait(pid)  # espera a que el hijo termine
```

**Por qué fork+exec separados** (no un solo `spawn`):
- Entre fork y exec, el hijo puede hacer setup (cerrar fds, cambiar working dir, drop privileges).
- Permite shells redirigir stdin/stdout antes de ejecutar el comando.
- Patrón Unix elegante (cada syscall hace UNA cosa).

**Ejemplos prácticos**:

```python
# En Python
import subprocess
subprocess.run(["ls", "-la"])     # internamente hace fork+exec

# En bash
$ ls -la                           # bash hace fork() y exec("ls")
```

**Optimizaciones**:
- **`vfork()`** y **`posix_spawn()`** — variantes más rápidas para casos comunes (no copian el espacio de memoria del padre porque van a hacer exec inmediato).
- **Copy-on-write**: cuando forkeas, el SO NO copia el espacio de memoria entero (sería lentísimo). Marca las páginas como compartidas. Solo cuando alguno ESCRIBE en una página, se copia (entonces sí). Para fork+exec, casi nunca se copia nada.

---

## 5. Crear threads

**En C (POSIX)**:
```c
pthread_t thread;
pthread_create(&thread, NULL, worker_function, arg);
pthread_join(thread, NULL);
```

**En Python**:
```python
import threading
t = threading.Thread(target=worker_function, args=(arg,))
t.start()
t.join()
```

**Mucho más rápido que crear proceso**: no hay que duplicar memoria, file descriptors, etc.

---

## 6. Estados de un proceso

```
              ┌─────────────┐
              │   NEW       │  recién creado
              └──────┬──────┘
                     │ admitido al scheduler
                     ↓
              ┌─────────────┐
       ┌────→│  READY      │  esperando CPU
       │      └──────┬──────┘
       │             │ scheduler lo elige
       │             ↓
   I/O completes  ┌─────────────┐
       │      ←──│  RUNNING    │  ejecutándose en CPU
       │      ↓   └──────┬──────┘
       │  ┌──────────┐   │
       └─┤ WAITING  │←──┘ pide I/O o lock
          │ (BLOCKED)│
          └──────────┘
                     │
              ┌─────────────┐
              │ TERMINATED  │  acabó (exit() o killed)
              └─────────────┘
```

**Lo que importa entender**:
- Solo UN proceso por core está RUNNING en cada momento. Si tienes 4 cores, máximo 4 procesos RUNNING simultáneamente.
- Los demás están READY (esperando turno) o WAITING (esperando algo, ej: leer disco, recibir paquete).
- El scheduler decide QUÉ proceso READY pasa a RUNNING (ver doc 03).

---

## 7. Context switching — el coste de cambiar de proceso/thread

**Qué es**: el SO suspende un proceso/thread y empieza a ejecutar otro. Tiene que GUARDAR el estado del primero y CARGAR el del siguiente.

**Qué se guarda/carga**:
- Registros del CPU (PC, SP, registros generales).
- Page tables (si cambia de proceso, no de thread).
- TLB se invalida parcialmente (cache de page tables).
- Estado del FPU.

**Coste aproximado**:
- Thread → thread (mismo proceso): ~1-2 microsegundos.
- Process → process: ~5-10 microsegundos (TLB flush).
- Cuando hay muchos cores y cache misses: puede ser MUCHO más.

**Por qué importa**: si tienes miles de threads compitiendo por pocos cores, el SO pasa más tiempo cambiando de contexto que ejecutando código real. Esto es **thrashing**.

Por eso event loops (epoll/asyncio) son más eficientes que 1 thread por conexión: no hay context switching entre tasks asyncio (todas corren en el mismo thread del event loop).

---

## 8. Procesos vs threads — cuándo cada uno

**Usa procesos cuando**:
- Aislamiento es crítico (si uno crashea, los demás siguen).
- Quieres usar TODOS los cores con CPU-bound (Python GIL te limita threads).
- Tareas independientes que no comparten estado.
- Seguridad (sandbox).

Ejemplo: Chrome usa 1 proceso por tab/extensión. Si una página crashea, no tira el browser entero.

**Usa threads cuando**:
- Necesitas compartir mucho estado (sin overhead de IPC).
- Tareas relacionadas con datos comunes.
- I/O bound (esperar red/disco).
- Crear/destruir frecuente (threads son ligeros).

Ejemplo: web server tradicional con 1 thread por request. Compartir DB connection pool entre threads del mismo proceso.

**Usa async (1 thread + event loop) cuando**:
- Miles de conexiones I/O-bound concurrentes.
- Quieres evitar context switching overhead.
- Trabajo está dominado por esperar (red, disco).

Ejemplo: Node.js, FastAPI con asyncio, Nginx.

**Usa multiprocessing + threads cuando**:
- Quieres aprovechar todos los cores Y compartir algo de estado.
- Patrón típico: 1 proceso por core, cada uno con threads internos.
- `uvicorn --workers 4` es esto.

---

## 9. El GIL de Python — caso especial importante

**GIL = Global Interpreter Lock**.

**Qué es**: un mutex global en CPython. Solo UN thread puede ejecutar bytecode Python en cada momento.

**Por qué existe**: CPython usa reference counting para garbage collection. Sin GIL, race conditions en refcounts → memory corruption. Mantener GIL fue más simple que reescribir todo el GC.

**Consecuencias**:

**CPU-bound (cálculo puro)**: threads NO ayudan en Python. 4 threads en 4 cores = 1 thread efectivo. Para CPU-bound usa multiprocessing (procesos separados, sin GIL compartido).

**I/O-bound (esperar red, disco)**: threads SÍ ayudan. El GIL se libera durante I/O. Mientras un thread espera red, otro puede ejecutar Python. Para I/O en Python, threads o asyncio funcionan.

**Estado actual (2024-2026)**: PEP 703 propone "GIL opcional" (free-threaded Python). Python 3.13 introdujo experimentalmente. En 5 años puede que el GIL desaparezca. Hoy (2026): asume GIL existe.

**Otros lenguajes sin GIL**: Java, Go, Rust, C++, C# — threads de verdad usan todos los cores. Por eso Python para CPU-bound serio se hace típicamente con C extensions (numpy, scipy liberan el GIL en sus loops C).

---

## 10. Daemon threads / processes

**Daemon**: un thread/proceso "fantasma" que MUERE cuando todos los no-daemon mueren.

**Uso típico**: background workers (logging, métricas, heartbeat) que NO deben impedir que el programa termine.

**En Python**:
```python
t = threading.Thread(target=worker, daemon=True)
t.start()
# cuando main thread termina, t también muere
```

**Procesos daemon (Unix)**: un proceso "desligado" del terminal y del padre. Ejecuta en background. Servicios típicos del SO son daemons: sshd, nginx, postgresql, etc. Por convención su nombre acaba en 'd'.

---

## 11. Zombies y orphans (procesos en estados raros)

**Zombie**: un proceso hijo que terminó pero su padre no ha llamado `wait()` todavía. El SO mantiene su entry en la process table (con su exit code) hasta que el padre lo "recoja" con `wait()`.

Visible en `ps`: estado "Z" o "<defunct>".

**Problema**: si el padre nunca hace `wait()`, los zombies se acumulan. Cada zombie ocupa una entrada en la PID table (limitada).

**Orphan**: un proceso hijo cuyo padre murió antes que él. El proceso 'init' (PID 1) lo "adopta" automáticamente. init periódicamente hace `wait()` para limpiar.

No es problema (init los recoge).

---

## 12. Signals — comunicación asíncrona con procesos

Un **signal** es un mensaje asíncrono al proceso.

**Signals comunes**:

| Signal | Número | Significado |
|---|---|---|
| `SIGTERM` | 15 | "termina educadamente" (puedes hacer cleanup) |
| `SIGKILL` | 9 | "muere YA" (no se puede ignorar, sin cleanup) |
| `SIGINT` | 2 | Ctrl+C en terminal |
| `SIGSTOP` / `SIGCONT` | — | pausar/reanudar |
| `SIGSEGV` | 11 | segmentation fault (acceso inválido a memoria) |
| `SIGCHLD` | — | notifica al padre que un hijo cambió de estado |

**Desde terminal**:
```bash
$ kill -TERM 1234        # SIGTERM al PID 1234
$ kill -9 1234           # SIGKILL (force)
$ pkill -f "nombre"      # mata por nombre
```

**En Python**:
```python
import signal
signal.signal(signal.SIGTERM, handler_function)
# cuando llegue SIGTERM, llama a handler_function
```

**Docker stop**: manda SIGTERM al PID 1 del container. Espera 10s default. Si no muere, manda SIGKILL. Por eso tu app debe manejar SIGTERM para shutdown limpio.

---

## 13. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

**Proceso**: Uvicorn corre como un proceso Python.

**Threads vs async**: Uvicorn por defecto usa **asyncio** (1 thread + event loop). Si lo arrancas con `--workers 4`, son 4 procesos separados (cada uno con su event loop), comunicándose via SO_REUSEPORT en el puerto 8000.

**Docker**: tu container es un proceso (a veces más). Cuando haces `docker compose down`, Docker manda SIGTERM. FastAPI maneja el SIGTERM para hacer shutdown limpio (cerrar conexiones DB, terminar requests pendientes).

### En problema NeetCode 207 (Course Schedule)

Lo que estudias en concurrency teóricamente es un caso específico de scheduling — exactamente lo que el SO hace con procesos/threads.

### Para embebido (tu IoT)

Si embebido tiene un proceso watchdog + un proceso que lee sensores + un proceso que envía datos → ya estás haciendo arquitectura multi-proceso. Saber sobre signals es importante (¿cómo apagas el sistema limpio? SIGTERM coordinado).

### En entrevistas tecnicas

**Pregunta**: "¿Diferencia entre proceso y thread?"

**Respuesta**: aislamiento de memoria, costo de creación, costo de IPC vs shared mem.

**Pregunta**: "¿Qué pasa cuando ejecutas `python script.py` en bash?"

**Respuesta**: bash hace `fork()`. Hijo hace `exec("/usr/bin/python", ["python","script.py"])`. Bash espera con `wait()`. Hijo carga script.py y ejecuta.

**Pregunta**: "¿Por qué Python no es bueno para CPU-bound multithreading?"

**Respuesta**: GIL. Solo 1 thread ejecuta bytecode a la vez. Para CPU-bound usar multiprocessing o C extensions.

**Pregunta**: "¿Cómo escala tu API a 10K conexiones?"

**Respuesta**: NO con thread per request (~10K threads = thrashing). Con event loop (asyncio) + N workers (1 por core). Cada worker maneja miles de conexiones via epoll.

---

## 14. Trampas típicas

**"Threads son siempre más rápidos que procesos"**: para tareas SHARED-STATE I/O bound: sí, threads más rápidos. Para CPU-bound en Python: NO (GIL). Para aislamiento: procesos siempre.

**"Más threads = más rápido"**: hasta cierto punto. Pasado el número de cores + I/O wait, añadir threads solo añade context switching overhead. Punto óptimo típicamente: cores × (1 + wait_ratio).

**"`fork()` es lento porque copia toda la memoria"**: no con copy-on-write moderno. Solo se copian páginas que se modifican. fork+exec es muy eficiente (no se copia nada en práctica).

**"Daemon threads se cierran limpio"**: NO. Mueren ABRUPTAMENTE cuando el main termina. Sin cleanup. No los uses para tareas que necesiten flush a disco/red.

**"`kill -9` es la forma normal de parar un proceso"**: [NO]. SIGKILL (-9) NO permite cleanup. La app no puede liberar locks, flush buffers, cerrar conexiones DB. Usa siempre SIGTERM (-15) primero. -9 solo cuando -15 no responde tras unos segundos.

**"asyncio es más rápido que threads siempre"**: solo para I/O-bound. Para CPU-bound, asyncio NO ayuda (sigue siendo 1 thread). Async ≠ paralelismo.

**"Cada container es 1 proceso"**: por convención sí (1 container = 1 servicio = 1 proceso). Pero técnicamente puedes tener N procesos (con supervisord, etc.). Anti-pattern: mejor 1 container por proceso, orquestar con compose.

---

## 15. Preguntas típicas de interview

**"Diferencia entre proceso y thread en 2 frases"** — proceso: instancia de programa con su propio espacio de memoria. Thread: unidad de ejecución dentro de un proceso, comparte memoria con otros threads del mismo proceso.

**"Cuándo usar multiprocessing vs threading vs asyncio en Python"** — multiprocessing: CPU-bound, evitar GIL, paralelismo real. Threading: I/O-bound legacy code, compartir estado simple. Asyncio: muchas conexiones I/O concurrentes, quieres event loop.

**"Cómo funciona `fork()`"** — clona el proceso. Padre recibe PID del hijo, hijo recibe 0. Copy-on-write hace que sea barato. Típicamente seguido de exec().

**"Qué es un context switch y por qué importa"** — el SO suspende un thread y carga otro. Implica guardar/restaurar registros, page tables, etc. Coste ~1-10μs. Si hay miles de threads, el overhead suma y degrada throughput (thrashing).

**"Qué es el GIL en Python"** — lock global que serializa ejecución de bytecode Python. Threads Python no son verdadero paralelismo para CPU. Para CPU usar multiprocessing o C extensions (numpy).

**"Diferencia entre SIGTERM y SIGKILL"** — SIGTERM: termina educadamente, app puede capturar y limpiar. SIGKILL: el SO mata sin previo aviso, app no puede capturarlo.

**"Cómo evitarías zombies en tu programa"** — llamar `wait()` / `waitpid()` en el padre tras cada hijo. En Python, `subprocess.run()` lo hace automático. Daemon: hacer doble fork (el segundo nieto es adoptado por init).

---

## 16. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Programa vs proceso vs thread.
- Anatomía de memoria de un proceso (text/data/bss/heap/stack).
- Qué comparten threads y qué tienen propio.
- `fork()` + `exec()` pattern y por qué separados.
- Estados de un proceso (Ready, Running, Waiting, Terminated).
- Context switching y su coste.
- Cuándo usar procesos vs threads vs async.
- El GIL de Python: qué es y consecuencias.
- Signals: SIGTERM vs SIGKILL, cómo capturar.
- Zombies y orphans.

Si no puedes → relee la sección.

---

## Conexiones

- [[02-memoria-virtual-paging]] — cómo cada proceso tiene su espacio aislado
- [[03-scheduling]] — cómo el SO elige qué proceso ejecutar
- [[04-syscalls-y-kernel]] — fork(), exec(), wait() son syscalls
- [[../03_concurrency/01-race-conditions]] — problemas al compartir entre threads
- [[../03_concurrency/04-async-vs-threads-vs-procesos]] — comparativa profunda
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]
- — Docker + signals

## Recursos externos

- **Operating Systems: Three Easy Pieces** (Arpaci-Dusseau, GRATIS pages.cs.wisc.edu/~remzi/OSTEP/) — capítulos 4-7 (Procesos, API, Limited Direct Execution, Scheduling).
- **The Linux Programming Interface** (Michael Kerrisk) — la biblia POSIX/Linux. Denso, referencia.
- **Modern Operating Systems** (Tanenbaum) — clásico universitario.
- **strace, ltrace, ps, top, htop** — herramientas para inspeccionar procesos.
- **`man 2 fork`, `man 2 exec`, `man 7 signal`** — documentación oficial Unix.
