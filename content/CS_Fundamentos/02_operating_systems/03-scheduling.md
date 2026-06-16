# 03 — Scheduling

> 📚 **Doc 3 del cluster Operating Systems**. Cómo el SO decide QUÉ proceso/thread ejecutar en cada CPU en cada momento. La parte más "viva" del SO.
> 🔥 **Frecuencia interview**: aparece en preguntas de performance, latencia, "¿por qué mi proceso está lento aunque hay CPU?".
> ⏱️ **Tiempo de lectura estimado**: 35-50 min.

---

## 1. El problema del scheduler

**Situación**: 1 CPU (o N cores) en la máquina, 1000 procesos que quieren ejecutarse. El SO debe decidir: ¿quién corre AHORA y por cuánto tiempo?

**Objetivos** (a veces conflictivos):
- **Fairness**: todos los procesos progresan, ninguno muere de hambre.
- **Throughput**: máximo trabajo total completado por unidad de tiempo.
- **Latency**: respuesta rápida (importante para interactivos).
- **Priority**: procesos importantes van primero.
- **Efficiency**: bajo overhead del propio scheduler.

**No hay algoritmo perfecto**. Cada SO elige tradeoffs distintos según workload típico.

---

## 2. Tipos básicos de schedulers

### Preemptive vs cooperative

**Preemptive**: el SO interrumpe procesos cuando quiere (timer interrupt). El proceso NO controla cuándo deja la CPU. Casi todos los SOs modernos (Linux, Windows, macOS).

**Cooperative**: el proceso decide cuándo ceder la CPU (`yield()`). Si un proceso no yield, MONOPOLIZA la CPU. Anti-patrón en SO general. Sí en async/await (asyncio).

### Priority-based vs fair

**Priority-based**: procesos tienen prioridad. Alta prioridad ejecuta primero. Riesgo: starvation de baja prioridad.

**Fair**: todos progresan proporcionalmente. Linux CFS es "fair" (Completely Fair Scheduler).

---

## 3. Algoritmos clásicos de scheduling

### FCFS (First-Come, First-Served)

Cola FIFO. Primer proceso que llega ejecuta hasta terminar.

**Ventaja**: simple, no preemption.
**Desventaja**: efecto convoy (un proceso largo bloquea a todos).

**Problema clásico**: si llega un proceso CPU-bound (1 hora) y luego 1000 procesos cortos (1ms cada uno), TODOS esperan 1 hora.

**Uso**: rare en SOs modernos. Sí en batch processing legacy.

### SJF (Shortest Job First)

Primero el proceso con menor tiempo de CPU estimado.

**Ventaja**: óptimo para average waiting time.
**Desventaja**: necesita ESTIMAR duración (imposible saber a priori). Starvation de procesos largos.

**Variante: SRTF (Shortest Remaining Time First)** — preemptive.

**Uso**: principio teórico, no implementado puro.

### Round Robin (RR)

Cada proceso recibe un TIME SLICE (quantum) fijo. Cuando expira, va al final de la cola, siguiente proceso ejecuta.

**Ventaja**: justo, sin starvation, latencia predecible.
**Desventaja**: overhead de context switching si quantum muy corto. Quantum muy largo = peor latencia interactiva.

**Quantum típico**: 10-100ms.

**Uso**: base de muchos schedulers reales. Linux CFS es variante.

### Priority Scheduling

Cada proceso tiene prioridad (típicamente 0-139 en Linux). Mayor prioridad ejecuta primero.

**Problema**: starvation de baja prioridad.
**Solución**: aging — incrementar prioridad de procesos que esperan mucho.

**Nice values (Unix)**:
- Range -20 (más alta) a +19 (más baja).
- Default 0.
- `$ nice -n 10 mi_proceso` → arranca con nice 10 (menor prioridad).
- `$ renice -n 5 -p PID` → cambia nice de proceso existente.

**Real-time priorities (Linux)**: separadas. SCHED_FIFO, SCHED_RR para tareas críticas (audio, control).
- `$ chrt -f 50 mi_proceso` → real-time, prioridad 50.
- Ojo: real-time mal usado puede colgar el sistema.

### Multilevel Feedback Queue (MLFQ)

Múltiples colas con distintas prioridades. Procesos suben/bajan de cola según comportamiento.

**Reglas**:
- Procesos nuevos en cola de máxima prioridad.
- Si usan TODO su quantum (CPU-bound) → bajan de cola.
- Si bloquean por I/O (interactivos) → mantienen alta prioridad.
- Periódicamente: todos suben (aging anti-starvation).

**Efecto**:
- Procesos interactivos (bash, vim) → siempre rápidos.
- Procesos CPU-bound (compilación) → bajan a colas lentas pero ejecutan.

**Uso**: Windows scheduler clásico. Variantes en macOS.

---

## 4. Linux CFS — Completely Fair Scheduler (el real)

Desde 2007 Linux usa **CFS** (Ingo Molnár). No es estrictamente "fair" pero se acerca.

**Idea central**: mantén el "vruntime" (virtual runtime) de cada proceso. Es el tiempo que ha ejecutado, ajustado por su prioridad (nice). Siempre ejecutar el proceso con MENOR vruntime (el "más atrasado").

**Estructura**: procesos en un RED-BLACK TREE indexado por vruntime. Operaciones O(log n). El leftmost node es el siguiente a ejecutar.

**Cálculo de time slice**: no es fijo. Depende de:
- Número de procesos runnable.
- Configuración (`sched_min_granularity_ns`, `sched_latency_ns`).
- Prioridad relativa.

**Efecto práctico**:
- 100 procesos CPU-bound iguales → cada uno 1% del CPU.
- 1 proceso CPU + 1 interactivo → interactivo recibe casi todo lo que pide (poco), y CPU-bound usa el resto.

**Ventajas sobre MLFQ**:
- Más predecible.
- Sin colas (todo es vruntime).
- Más fair matemáticamente.

**Nuevo: EEVDF** (Earliest Eligible Virtual Deadline First) — Linux 6.6+ (2023). Sucesor planeado de CFS. Mejor para latencia + más justo. Usa "deadline-based" en vez de "vruntime-based".

---

## 5. CPU affinity — fijar procesos a cores

**Por defecto**: el scheduler puede mover un proceso entre cores libremente. Cada migración invalida cache → coste.

**CPU affinity**: fijar un proceso a un core (o conjunto de cores) específico. Evita migración → cache amistoso → mejor performance para hot loops.

**En Linux**:
```bash
$ taskset -c 0,1 mi_proceso     # ejecuta en cores 0 y 1
$ taskset -p 0x3 PID             # asigna mask 0x3 (cores 0,1) a PID
```

Programáticamente: `sched_setaffinity()`.

**Cuándo usarlo**:
- Aplicaciones de baja latencia (HFT, audio).
- DB workers (cada uno en su core).
- Real-time embebido.

**Cuándo no**:
- Apps generales (deja que el SO optimice).
- Si tienes pocos procesos vs cores (no hay pelea).

---

## 6. NUMA — Non-Uniform Memory Access

En máquinas grandes (multi-socket): cada CPU socket tiene su propio bank de RAM "local". Acceder al RAM de OTRO socket es 2-3x más lento.

**NUMA awareness**: scheduler intenta mantener proceso + su memoria en mismo NUMA node. Migración cross-NUMA es costosa.

**Relevante para**: servers con 2-8 CPUs físicos (no laptops). DBs grandes (Postgres tiene NUMA tuning).

**Herramientas**:
```bash
$ numactl --cpunodebind=0 --membind=0 mi_proceso
$ numastat  # ver tráfico NUMA
```

---

## 7. I/O scheduling — el otro scheduler

Además del CPU scheduler, hay un **I/O scheduler** que decide el orden de operaciones a disco/dispositivos.

**Problema**: múltiples procesos piden read/write simultáneos al mismo disco. Disco solo atiende uno a la vez. Orden óptimo depende del tipo (HDD: minimizar seek; SSD: paralelo).

**Algoritmos Linux**:
- **noop**: FIFO, sin reordering. Bueno para SSDs.
- **deadline**: garantiza max latency, prioriza reads sobre writes.
- **cfq** (Completely Fair Queueing): histórico, fair entre procesos.
- **mq-deadline, kyber, bfq**: modernos, multi-queue para SSDs/NVMe.

**Ver/cambiar**:
```bash
$ cat /sys/block/sda/queue/scheduler
[mq-deadline] kyber bfq none
```

---

## 8. Real-time scheduling

**Real-time ≠ "muy rápido". Real-time = predecible/determinista**. Garantiza que tarea crítica ejecuta antes de su DEADLINE.

**Linux soporta**:
- **SCHED_FIFO**: prioridad fija, sin time slicing. Hasta que bloquees o termines.
- **SCHED_RR**: como FIFO pero con quantum (round-robin entre prioridades iguales).
- **SCHED_DEADLINE**: especifica (período, deadline, runtime). El SO lo respeta.

**Uso**:
- Audio en vivo (Jack, ardour).
- Robótica.
- SCADA, industrial.
- Trading de baja latencia.

**Alternativas**:
- PREEMPT_RT patch para Linux (kernel mainline desde 6.12).
- Xenomai, RTAI: extensiones real-time clásicas.
- FreeRTOS, Zephyr: para embebidos.

**Cuidado**: un proceso real-time mal escrito puede COLGAR la máquina (no cede CPU). Por eso requiere root.

---

## 9. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Uvicorn corre con prioridad normal (nice 0). Si subes `--workers 4`, son 4 procesos compitiendo por cores via CFS. Si tu container está en un sistema cargado, pueden ser preemptados constantemente. Esto introduce latencia variable en tus requests. Para un toy project no importa. En production con SLAs estrictos sí.

### En entrevistas tecnicas

**Pregunta**: "Por qué mi proceso de Python tarda más de lo esperado, aunque tiene un solo thread?"

**Respuesta**: posibles razones: GIL (si threads), context switching (si muchos procesos compitiendo), priority (nice subió), I/O wait (no es CPU el cuello), garbage collection pauses.

**Pregunta**: "Qué pasa si arrancas un proceso con SCHED_FIFO prioridad 99 que entra en bucle infinito?"

**Respuesta**: cuelga el sistema (en single-CPU). Es por qué real-time requiere root. En multi-core, ocupa 1 core entero pero los demás siguen.

**Pregunta**: "Diferencia entre nice y real-time priority"

**Respuesta**: nice (-20 a +19): hint al CFS. Procesos siempre comparten CPU. Real-time (1-99): supera a TODO lo no-real-time. SCHED_FIFO/RR.

**Pregunta**: "Cómo dar prioridad a tu proceso frente a otros"

**Respuesta**: nice (suave): `renice -n -10 -p PID` (requiere root para negativos). taskset (afinidad): aislar en core dedicado. ionice: para I/O priority. cgroups: control fino con CPU shares.

### En embebido (perfil HW)

Si embebido tiene loops de control (e.g. 100Hz sensor reading), las latencias del scheduler estándar pueden no ser suficientes. Para eso existe FreeRTOS o PREEMPT_RT.

---

## 10. Trampas típicas

**"Más cores siempre = más rápido"**: solo si tu app PARALELIZA. Single-threaded no se beneficia de N cores. Ley de Amdahl: aceleración limitada por fracción serial.

**"Nice -20 hace mi proceso instantáneo"**: nice es relativo. Si TODOS tus procesos son nice -20, ninguno gana. Solo importa diferencia frente a otros.

**"Real-time = más rápido"**: real-time = predecible. Throughput puede ser PEOR (más overhead). Es para latencia garantizada, no rendimiento promedio.

**"El scheduler es perfectamente justo"**: nada lo es. Hay efectos de cache, NUMA, frequency scaling. Mismo workload puede dar resultados distintos en cada run.

**"Más threads = más concurrencia"**: threads compiten por cores y sufren context switching. Threads > cores generalmente NO ayuda (excepto I/O bound).

**"Time slice es siempre 100ms"**: Linux CFS lo calcula dinámico según carga. Puede ser 1ms o 50ms.

---

## 11. Preguntas típicas de interview

**"Diferencia entre preemptive y cooperative scheduling"** — preemptive: SO interrumpe. Cooperative: proceso decide ceder. SOs modernos preemptive. Async/await es cooperative dentro de un thread.

**"Cómo Linux scheduler decide qué proceso ejecutar"** — CFS: red-black tree por vruntime. Ejecuta el menor vruntime. Ajustado por nice value y carga.

**"Qué es starvation y cómo evitarla"** — cuando proceso baja prioridad nunca ejecuta porque siempre hay alta prioridad esperando. Soluciones: aging, fair queueing, time-bounded priorities.

**"Diferencia entre throughput y latency"** — throughput: trabajo total / tiempo. Latency: tiempo individual de respuesta. A veces conflictivos: optimizar throughput puede empeorar latency.

**"Por qué importa CPU affinity"** — migración entre cores invalida cache (L1/L2 son per-core). Cache miss caro. Affinity mantiene workload en mismo core, cache hot, mejor performance para hot loops.

**"Qué pasa si hago `sleep(0)` en un loop"** — yield al scheduler. Otros procesos runnable ejecutan. No es busy-wait pero sigue consumiendo schedule slots. Mejor `sleep(microseconds)` o usar event-driven.

---

## 12. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué scheduler es necesario (más procesos que cores).
- Preemptive vs cooperative.
- Algoritmos clásicos: FCFS, SJF, RR, Priority, MLFQ.
- Linux CFS: idea de vruntime.
- Nice values y prioridades.
- Real-time scheduling: cuándo y peligros.
- Context switching coste.
- CPU affinity y por qué importa cache.
- Starvation y aging.

Si no puedes → relee.

---

## Conexiones

- [[01-procesos-y-threads]] — quién recibe scheduling
- [[02-memoria-virtual-paging]] — context switch implica cambiar page tables
- [[04-syscalls-y-kernel]] — sched_yield, nice, sched_setaffinity son syscalls
- [[../03_concurrency/04-async-vs-threads-vs-procesos]] — schedulers de userspace (asyncio)
- [[../07_computer_architecture/02-jerarquia-de-memoria-y-cache]] — por qué affinity importa
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **OSTEP** capítulos 7-10 (Scheduling). GRATIS.
- **Linux CFS Design**: kernel.org/doc/html/latest/scheduler/sched-design-CFS.html
- **`htop`, `top`, `ps`, `taskset`, `nice`, `chrt`** — herramientas reales.
- **`schedviz`** (Google) — visualizador de scheduling traces.
- **Brendan Gregg's blog** — performance tuning Linux, denso pero gold.
