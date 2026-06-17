# 03 — Deadlock y livelock

> **Doc 3 del cluster Concurrency**. El otro lado de los locks: cuando se vuelven contra ti. Deadlocks son el bug clásico de threading.
> **Frecuencia interview**: aparece en preguntas "diseña sistema sin deadlock", problema dining philosophers.
> **Tiempo de lectura estimado**: 30-45 min.

---

## 1. Qué es un deadlock

Un **deadlock** ocurre cuando dos o más threads/procesos esperan mutuamente recursos que el otro tiene. Ninguno avanza y el sistema queda parcialmente o totalmente colgado.

**Ejemplo mínimo (2 threads, 2 locks)**:

- Thread A adquiere `L1`, luego intenta adquirir `L2`.
- Thread B adquiere `L2`, luego intenta adquirir `L1`.
- Si A llega a su segundo lock cuando B ya tiene `L2`, y B llega a su segundo lock cuando A ya tiene `L1`, **ambos se bloquean para siempre**.

**Analogía humana**: dos personas en un pasillo estrecho, una hacia el norte y otra hacia el sur. Cada una se mueve a un lado para dejar pasar a la otra, pero ambas eligen el mismo lado. Mueven al otro lado y otra vez coinciden. Pueden quedar bloqueadas eternamente.

---

## 2. Las 4 condiciones de Coffman (necesarias para deadlock)

Edsger Coffman demostró que un deadlock requiere **TODAS estas 4 condiciones** simultáneamente:

| # | Condición | Descripción | Cómo evitarla |
|---|---|---|---|
| 1 | **Mutual exclusion** | Al menos un recurso solo permite un poseedor a la vez | Si todo es shareable → no hay deadlock posible |
| 2 | **Hold and wait** | Un thread tiene un recurso y está esperando otro | Pedir todos los locks al inicio → no hay hold-and-wait |
| 3 | **No preemption** | Un recurso no se puede arrebatar al thread que lo tiene; el owner debe liberarlo voluntariamente | En DBs sí hay preemption: la víctima de un deadlock se "kill" |
| 4 | **Circular wait** | Existe un ciclo entre threads esperando recursos: T1 espera de T2, T2 de T3, …, Tn de T1 | Adquirir todos los locks en el mismo orden → no puede haber ciclo |

**Consecuencia**: para prevenir deadlock basta con **romper UNA** de las 4 condiciones.

---

## 3. El dining philosophers — problema clásico

**Escenario (Dijkstra, 1965)**: 5 filósofos sentados en una mesa redonda, con 5 tenedores entre ellos (uno entre cada par). Cada filósofo necesita 2 tenedores (izquierdo y derecho) para comer; cuando termina, deja ambos.

```
        F1
      /    \
   T5        T1
   /          \
  F5          F2
   \          /
   T4        T2
      \    /
        F3 - T3 - F4
```

**Problema**: si todos cogen su tenedor izquierdo al mismo tiempo:

- F1 tiene T1, espera T5.
- F2 tiene T2, espera T1.
- F3 tiene T3, espera T2.
- F4 tiene T4, espera T3.
- F5 tiene T5, espera T4.

Circular wait → deadlock.

**Soluciones**:

- **A) Orden global**: numerar los tenedores. El filósofo coge siempre el de menor número primero. F5 cogería T4 antes que T5, rompiendo el ciclo.
- **B) Resource hierarchy**: el filósofo solo puede coger los 2 tenedores si ambos están libres (atomic check). Si no, suelta el primero y espera. Equivale a try-lock.
- **C) Asymmetric**: filósofos pares cogen izquierdo primero, impares derecho primero. La asimetría rompe el ciclo.
- **D) Arbiter (mutex global)**: solo 4 filósofos pueden estar "intentando" comer al mismo tiempo (semáforo con N=4). Garantiza que al menos uno consigue 2 tenedores.

---

## 4. Cómo prevenir deadlocks en práctica

### Estrategia 1: orden global de adquisición (lo más común)

**Regla**: todo el código del sistema adquiere los locks en el mismo orden. Si todos adquieren `L1` antes que `L2` (donde `L1 < L2` según algún criterio), no puede haber circular wait → no hay deadlock.

**Python idiomático**: asignar IDs a los locks y adquirir en orden de ID.

```python
def transfer(a, b, amount):
    locks = sorted([a.lock, b.lock], key=id)
    with locks[0]:
        with locks[1]:
            a.balance -= amount
            b.balance += amount
```

**Ejemplo real**: el kernel Linux define un orden estricto de locks (documentado).

### Estrategia 2: try-lock con timeout

En vez de adquirir bloqueando, intentar con timeout. Si falla → soltar locks ya adquiridos y reintentar.

```python
if not lock.acquire(timeout=1.0):
    release_other_locks()
    retry()
```

- **Ventaja**: rompe deadlocks si suceden (uno suelta y reintenta).
- **Desventaja**: puede causar livelock si no hay backoff aleatorio.

### Estrategia 3: hold no locks

Si puedes diseñar tu código para nunca mantener más de 1 lock a la vez, el deadlock es imposible.

Cuando necesitas operar con varios recursos:

1. Adquirir lock 1, leer lo que necesitas, soltar.
2. Adquirir lock 2, leer lo que necesitas, soltar.
3. Procesar fuera de locks.
4. Adquirir locks (en orden) para escribir cambios atómicamente.

**Problema**: el estado puede haber cambiado entre lecturas. Necesitas verificar invariantes al final (optimistic locking, MVCC).

### Estrategia 4: lock-free / shared-nothing

Sin locks compartidos no hay deadlock. **Opciones**:

- Cada thread tiene sus propios datos (no compartidos).
- Comunicación vía message passing (channels, queues).
- Operaciones atómicas en vez de locks.
- Actor model (Erlang, Akka).

Go promueve este enfoque: *"Don't communicate by sharing memory; share memory by communicating."*

### Estrategia 5: detección + recovery (las DBs lo hacen)

En vez de **prevenir**, **detectar** los deadlocks y matar a una víctima.

**Postgres**: periódicamente (default 1s) detecta ciclos en su grafo de espera. Si detecta uno → hace KILL a una transacción (`deadlock_timeout`). Devuelve error al cliente, que debe reintentar.

- **Pros**: permite código natural sin orden estricto de locks.
- **Contras**: tienes que manejar deadlock errors en tu app.

---

## 5. Livelock — el primo malicioso del deadlock

En un **livelock**, los threads están "activos" (no bloqueados) pero **no progresan**. Continuamente reaccionan a cambios del otro y no avanzan.

**Analogía humana**: pasillo estrecho. A se mueve a la izquierda para pasar; B también se mueve a la izquierda para pasar a A. A se mueve a la derecha; B también. Ad infinitum. Ambos "trabajan" pero ninguno avanza.

**Ejemplo técnico**: estrategia "try-lock + retry sin backoff":

- Thread A intenta `L1` + `L2`. Falla en `L2` → suelta `L1`, retry.
- Thread B intenta `L2` + `L1`. Falla en `L1` → suelta `L2`, retry.
- Si ambos reintentan al mismo tiempo siempre → siempre fallan.

**Solución**: **randomized backoff** — tras fallar, esperar un tiempo aleatorio antes de reintentar. La probabilidad de re-fallar simultáneamente tiende a 0 a la larga.

**Ejemplo histórico**: Ethernet CSMA/CD usa **exponential backoff**. Si hay colisión, espera `random(2^n)` tiempo, y `n` se incrementa con cada colisión.

---

## 6. Starvation — un thread nunca progresa

En **starvation** un thread es continuamente postergado por otros. No es un deadlock (el sistema avanza), pero ese thread nunca ejecuta.

**Causas comunes**:

- Priority scheduling sin aging (la baja prioridad nunca llega).
- RWLock con writers preferidos: readers continuos starvean writers (o al revés).
- Fairness mal diseñada en queues.

**Ejemplo RWLock**: si el lock favorece readers y llegan reader requests continuos, el writer espera infinitamente. Solución: writer-preferring RWLock o queueing fair.

**Ejemplo priority**: procesos low-priority no se ejecutan si hay constantes high-priority. Solución: **aging** — incrementar la prioridad de procesos que llevan mucho esperando.

---

## 7. Priority inversion (caso específico de starvation)

**Escenario**: 3 threads — H (alta prioridad), M (media), L (baja).

- L tiene un lock.
- H necesita el mismo lock → espera a L.
- M está corriendo (más prioridad que L).
- L no recibe CPU porque M lo bloquea.
- H espera "infinito" a L.

**Efecto**: H, la prioridad más alta, está bloqueada por M, prioridad media, vía L. La jerarquía se **invirtió**.

**Caso histórico famoso**: Mars Pathfinder (1997). El sistema robótico se colgaba periódicamente. Causa: priority inversion en VxWorks (RTOS). Solución aplicada: priority inheritance.

**Priority inheritance protocol**: cuando H espera un lock que L tiene, L "hereda" la prioridad de H. L corre con prioridad de H, completa rápido y libera. M no puede preempt a L (que ahora tiene prioridad H).

**Priority ceiling**: cada lock tiene una prioridad máxima asignada. Quien adquiere el lock recibe esa prioridad temporalmente.

**Linux**: soporta priority inheritance en mutexes (PI mutexes). Las apps real-time deben usarlos.

---

## 8. Cómo detectar deadlocks en producción

**Síntomas**:

- Procesos colgados sin actividad CPU.
- Spikes de latency.
- Threads en estado "waiting" indefinido.

**Herramientas**:

- **Python**: `py-spy dump --pid PID` muestra el stack trace de todos los threads. Si hay deadlock, verás threads bloqueados en `lock.acquire()`.
- **Java**: `jstack PID` detecta deadlocks automáticamente y los reporta.
- **Linux general**:

  ```bash
  gdb -p PID
  (gdb) thread apply all bt
  ```

  Mira qué hace cada thread.
- **DBs (Postgres, MySQL)**: `SHOW ENGINE INNODB STATUS` (MySQL) o `pg_stat_activity` (Postgres). Los logs típicamente contienen "deadlock detected".
- **Linux kernel**: `/proc/PID/wchan` muestra dónde está esperando un proceso.

---

## 9. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

- Si usas single asyncio, no hay deadlocks típicos (no hay locks de threads).
- Si añades múltiples workers o pools de threads, ojo con el orden de adquisición de DB locks.

### En entrevistas tecnicas

- **Pregunta clásica**: "Diseña un sistema sin deadlock con N recursos" → adquirir en orden global (numérico). Romper circular wait.
- **Pregunta**: "Dining philosophers, soluciónalo" → cualquiera de las 4 estrategias (orden, atomic, asimetría, arbiter).
- **Pregunta**: "Diferencia deadlock, livelock, starvation":
  - Deadlock: bloqueados sin actividad.
  - Livelock: activos pero no avanzan.
  - Starvation: un thread no progresa por priority/scheduling.
- **Pregunta**: "Cómo manejas deadlock detection vs prevention":
  - Prevention: orden estricto de adquisición. Coste: complejidad de diseño.
  - Detection: detectar y matar la víctima. Coste: la app debe reintentar.
  - Las DBs hacen detection. Las apps típicas hacen prevention.
- **Pregunta**: "Qué es priority inversion y cómo prevenirla" → threads de menor prioridad bloquean a los de mayor prioridad vía lock. Solución: priority inheritance (mutexes PI en Linux).

---

## 10. Trampas típicas

- **Trampa 1 — "Si solo tengo 1 lock, no hay deadlock"**: cierto, pero tu app puede crecer y añadir más locks sin que te des cuenta.
- **Trampa 2 — "Reentrant lock (RLock) elimina deadlock"**: solo elimina el self-deadlock (mismo thread re-adquiriendo). No previene deadlock cross-thread con varios locks.
- **Trampa 3 — "Try-lock con retry resuelve todo"**: puede causar livelock si no hay backoff. Y consume CPU. Mejor diseño: orden global de adquisición.
- **Trampa 4 — "Las DBs no pueden tener deadlocks"**: sí pueden. Postgres y MySQL detectan y matan transacciones. Tu código debe manejar deadlock errors (`40P01` en Postgres) y reintentar.
- **Trampa 5 — "Async/await elimina deadlocks"**: puede crear nuevos tipos. Si la task A espera la task B que espera la task A, aunque ambas sean single-threaded asyncio → mismo problema conceptual.
- **Trampa 6 — "Más threads = mejor"**: más threads + más locks = más probabilidad de deadlock. Profiling primero, escalado después.

---

## 11. Preguntas típicas de interview

- **Pregunta 1 — "Las 4 condiciones de Coffman para deadlock"**: mutual exclusion, hold-and-wait, no preemption, circular wait. Romper una previene deadlock.
- **Pregunta 2 — "Cómo prevenir deadlock"**: orden global de adquisición de locks; try-lock con backoff; mantener no más de 1 lock; lock-free / shared-nothing.
- **Pregunta 3 — "Diferencia deadlock vs livelock"**: deadlock = threads bloqueados sin progreso; livelock = activos cambiando estado mutuamente, sin avanzar.
- **Pregunta 4 — "Dining philosophers"**: problema clásico. Soluciones: orden, atomic, asimetría, arbiter.
- **Pregunta 5 — "Priority inversion"**: thread de alta prioridad bloqueado por uno de baja vía lock. Causa: el priority scheduler ejecuta el de prioridad media. Solución: priority inheritance.
- **Pregunta 6 — "Cómo Postgres maneja deadlocks"**: detection vía grafo de espera. Si detecta ciclo → kill víctima. El cliente recibe error y debe retry transaction.

---

## 12. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Qué es deadlock con ejemplo mínimo (2 threads, 2 locks).
- Las 4 condiciones de Coffman.
- Dining philosophers y al menos 1 solución.
- Estrategias de prevención (orden global, try-lock, hold no locks).
- Livelock: qué es y diferencia con deadlock.
- Starvation y aging.
- Priority inversion y priority inheritance.
- Cómo las DBs detectan/recuperan de deadlocks.
- Cómo detectar deadlocks en producción (py-spy, jstack).

Si no puedes → relee.

---

## Conexiones

- [[01-race-conditions]] — el problema que llevó a usar locks
- [[02-locks-y-mutex]] — herramientas que pueden causar deadlock
- [[04-async-vs-threads-vs-procesos]] — async puede tener deadlocks lógicos
- [[../02_operating_systems/03-scheduling]] — priority y starvation
- [[../05_database_internals/02-acid-transactions]] — DBs y deadlock detection
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **OSTEP** capítulo 32 (Common Concurrency Problems). GRATIS.
- **The Little Book of Semaphores** (Downey) — dining philosophers + mucho más.
- **`py-spy`, `jstack`, `gdb`** — debugging de deadlocks en producción.
- **Mars Pathfinder priority inversion** — caso histórico, instructivo.
- **Postgres deadlock_timeout docs** — postgresql.org/docs.
