# 03 — Coherencia de cache en multicore

> 📚 **Doc 3 (último) del cluster Computer Architecture**. Cómo varios cores comparten memoria sin pisarse, y por qué esto es la base oculta de toda concurrencia. Avanzado pero potente.
> 🔥 **Frecuencia interview**: aparece en preguntas de concurrency profundas, lock-free, atomic operations, memory ordering.
> ⏱️ **Tiempo de lectura estimado**: 30-45 min.

---

## 1. El problema en multicore

Un sistema con 8 cores tiene 8 caches L1 distintas (una por core). Si el core 1 escribe la variable `x` en su L1, **¿qué pasa con la copia de `x` en la L1 del core 2?**

Sin coordinación: el core 2 sigue viendo el valor viejo. Inconsistencia. **Cache incoherence**.

**Cache coherence** es el problema de mantener todas las caches sincronizadas, de forma que **lo que un core escribe, los demás eventualmente vean**.

Esto NO se hace en software. Lo hace el **hardware** automáticamente con protocolos de coherencia. Pero tiene **coste real** y entender el coste te ayuda a escribir código eficiente.

---

## 2. MESI — el protocolo más conocido

**MESI** es el protocolo de coherencia clásico. Cada cache line tiene uno de 4 estados:

- **Modified (M)**: este core tiene la copia, está modificada (dirty), nadie más tiene copia.
- **Exclusive (E)**: este core tiene la copia, está limpia (igual a memoria), nadie más tiene copia.
- **Shared (S)**: varios cores tienen la copia, todas iguales y limpias.
- **Invalid (I)**: este core no tiene copia válida (debe pedirla a otro).

Las transiciones entre estados se hacen via **mensajes entre cores** sobre el "bus" del sistema.

### Ejemplo de escenarios

**Escenario 1**: Core 1 lee `x`. No estaba en cache. Trae de RAM. Estado: **E** (exclusive).

**Escenario 2**: Core 2 también lee `x`. Core 1 le pasa la copia. Ambos: estado **S** (shared).

**Escenario 3**: Core 1 escribe `x = 5`. Tiene que invalidar la copia del core 2. Manda mensaje "invalidate x". Core 2 marca su línea como **I**. Core 1 marca **M** (modified).

**Escenario 4**: Core 2 quiere leer `x` ahora. Su copia es **I**. Pregunta al sistema. Core 1 (que tiene M) le envía el valor actualizado. Ambos: **S**.

Cada uno de estos mensajes y transiciones tiene **coste en ciclos**. Aunque sea automático, la "magia" no es gratis.

---

## 3. Variantes: MOESI, MESIF

Las CPUs modernas usan variantes mejoradas:

- **MOESI** (AMD): añade estado **Owned** = una copia es la "fuente de verdad" pero otras pueden tener copias compartidas. Permite forwarding directo entre cores sin tocar memoria.

- **MESIF** (Intel): añade estado **Forward** = solo una copia compartida puede responder a peticiones, evita ráfagas redundantes.

Estos detalles son del fabricante. Para tu código, lo importante es: **hay coordinación entre cores y tiene coste**.

---

## 4. Por qué importa para tu código

### Compartir variables mutables = caro

Si N threads escriben la misma variable, cada escritura **invalida** la copia en los caches de los otros N-1 cores. Cada core que la lea después paga **cache miss + transferencia desde otro core**.

Una variable "calentita" entre threads cuesta órdenes de magnitud más que una variable thread-local.

**Ejemplo**: contador compartido vs contador por thread + suma final.

```python
# Versión A: contador compartido (lento bajo contención)
counter = 0
lock = threading.Lock()
for x in items:
    with lock:
        counter += 1

# Versión B: contadores locales + suma (rápido)
counters = [0] * num_threads
# cada thread incrementa SU contador
total = sum(counters)
```

Versión B no solo evita el lock, evita la pelea de cache lines.

### False sharing — el caso oculto

Visto en doc 02. Dos variables independientes en la misma cache line causan invalidación cruzada aunque cada thread acceda solo a su variable.

**Solución**: alinear variables a cache line boundaries (padding o atributos del compilador).

---

## 5. Memory ordering — el otro mundo

Coherencia garantiza que eventualmente todos los cores vean lo mismo. Pero **el orden** en que ven los cambios depende de la arquitectura.

### El problema con un ejemplo

```c
// Thread 1
x = 1;
flag = true;

// Thread 2
if (flag) {
    print(x);  // ¿qué imprime?
}
```

Tu intuición: imprime 1. Si flag es true, x ya fue asignado.

**Realidad sin memory barriers**:
- La CPU puede **reordenar** writes de Thread 1 (out-of-order execution).
- Thread 2 podría ver `flag = true` ANTES de ver `x = 1`.
- Imprime 0 (el valor inicial).

**Esto es real**. Pasa en hardware moderno.

### Strong vs weak memory models

Las arquitecturas tienen distinto **memory ordering** por defecto:

- **x86 (Intel/AMD)**: relativamente strong. Writes se ven en orden FIFO entre cores. Pero NO garantiza orden total cross-core en algunos casos.

- **ARM, POWER, RISC-V**: weak ordering. Writes pueden reordenarse libremente entre cores. Necesitas **memory barriers** explícitos para forzar orden.

**Implicación**: código que funciona en x86 puede romperse en ARM. Por eso código multi-threaded portable necesita memory barriers explícitos.

### Memory barriers / fences

Instrucciones que **fuerzan ordering**:

- **`mfence`** (x86): asegura que todos los writes anteriores son visibles antes que los siguientes.
- **`dmb`** (ARM): equivalente.

Lenguajes high-level abstraen esto:

- **C++ `std::atomic` con memory_order**: relaxed, acquire, release, seq_cst.
- **Java `volatile`**: incluye barrier implícito en cada acceso.
- **Rust `std::sync::atomic`**: similar a C++.
- **Python**: el GIL hace que esto sea menos urgente, pero std/asyncio Lock manejan barriers internamente.

---

## 6. Acquire-Release semantics

Modelo simplificado del memory ordering moderno:

- **Acquire** (en una read): garantiza que ningún acceso de memoria POSTERIOR se reordene ANTES de este read.
- **Release** (en una write): garantiza que ningún acceso ANTERIOR se reordene DESPUÉS de este write.

Pattern producer-consumer típico:

```c++
// Thread 1 (producer)
data = 42;
flag.store(true, memory_order_release);  // todos los writes anteriores visibles

// Thread 2 (consumer)
if (flag.load(memory_order_acquire)) {  // todos los reads posteriores ven los writes
    assert(data == 42);  // GARANTIZADO
}
```

Acquire-release es más barato que `seq_cst` (sequentially consistent) y suficiente para la mayoría de patrones.

---

## 7. Atomic operations

**Atomic** = operación que se ejecuta indivisiblemente desde el punto de vista de otros cores.

CPUs modernas tienen instrucciones atómicas hardware:

- **CAS (Compare-And-Swap)**: si el valor es X, cambiar a Y. Atómico.
- **Fetch-and-add**: incrementa y devuelve valor anterior.
- **Lock prefix** (x86): convierte muchas instrucciones en atómicas (`lock add`, etc.).

Las atómicas son la base de:
- Locks/mutex (implementados con CAS).
- Lock-free data structures (queues, hash maps).
- Reference counting (smart pointers).

**Coste**: una atómica es mucho más cara que una operación normal (~10-50 ciclos vs 1). Pero mucho más barata que un lock pesimista (~100-1000 ciclos por contención).

### CAS pattern

```c++
// Incrementar counter atómicamente sin lock
atomic<int> counter;

while (true) {
    int current = counter.load();
    int next = current + 1;
    if (counter.compare_exchange_weak(current, next)) {
        break;  // éxito
    }
    // Si falló (otro thread cambió entre load y CAS), retry
}
```

Esta es la forma "lock-free" de incrementar. Bajo baja contención, mucho más rápido que mutex. Bajo alta contención, similar.

---

## 8. ABA problem

Un caso sutil con CAS. Thread A lee X, hace algo, va a CAS. Entre medio:
- Thread B cambió X → Y → X.
- Thread A ve que X sigue siendo X → CAS triunfa.

Pero **el "X" no es el mismo "X"**. Algo cambió en el medio que A no detectó.

**Ejemplo clásico**: lock-free linked list. A intenta quitar un nodo. B quita el nodo y lo reinserta. A no detecta el cambio porque el puntero es el mismo.

**Soluciones**:
- **Tagged pointers**: añadir versión al puntero. CAS compara puntero + versión.
- **Hazard pointers**: marcar nodos en uso para que nadie los reuse.
- **RCU (Read-Copy-Update)**: mantener versiones viejas hasta que ningún reader las use.

ABA es por qué **lock-free programming es muy difícil**. Para el 99% de casos, usa locks. Solo lock-free cuando profile demuestre que es necesario.

---

## 9. SMP vs NUMA

**SMP (Symmetric Multi-Processing)**: todos los cores acceden a la misma RAM con misma latencia. Caches coherentes.

**NUMA (Non-Uniform Memory Access)**: cada socket tiene su propia RAM. Acceder a RAM remota es 2-3x más lento. Coherencia entre sockets es más cara.

**Para sistemas grandes (servidores con 2+ sockets)**: NUMA es importante. Linux scheduler trata de mantener procesos cerca de su memoria. Tooling como `numactl` permite control fino.

**Para tu portátil o servidor de 1 socket**: NUMA invisible.

---

## 10. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Mostly invisible. Pero saber esto te ayuda a entender por qué:
- Connection pool a Redis es más rápido que abrir conexión por request (cache de objetos hot en RAM cercana).
- Locks Python tienen overhead aunque GIL los hace menos visibles.
- async/await es más rápido que threads para I/O (no hay coherencia de cache que sincronizar).

### En embebido (perfil HW)

Microcontroladores típicamente single-core. Sin coherencia de cache. Pero tienes ISRs (Interrupt Service Routines) que pueden interrumpir tu código main → "cuasi-multi-threading" donde necesitas atomic ops y disable interrupts para regiones críticas.

ESP32 tiene 2 cores (Xtensa LX6 dual-core). Ahí sí necesitas pensar en coherencia. FreeRTOS provee primitivas (xQueueSendFromISR, mutex with interrupt disable).

### En entrevistas tecnicas

**Pregunta clásica**: "Diferencia entre concurrency y parallelism a nivel hardware".

Concurrency: múltiples tasks intercaladas en tiempo (1 core).
Parallelism: múltiples ejecuciones físicamente simultáneas (multi-core).

**Pregunta sobre coherencia**: "Por qué no escala añadiendo más cores siempre".

Cache coherence overhead: writes a variables compartidas invalidan caches de otros cores. Más cores = más invalidaciones = scaling sub-lineal.

**Pregunta avanzada**: "Cómo prevenir false sharing".

Padding entre variables thread-local. `alignas(64)` en C++. `@Contended` en Java (con flag). Diseñar layouts donde cada thread tiene su cache line.

**Pregunta sobre lock-free**: "Cuándo usar lock-free vs locks".

Lock-free: muy alta contención + necesitas no bloquear (real-time). Pero MUY difícil de hacer correctamente. Locks: 99% de casos, son suficientes.

---

## 11. Trampas típicas

**"La memoria es uniforme"**: jerárquica. Latencias 1ns a 100ms según nivel. Y entre cores hay coordinación con coste.

**"Compartir datos entre threads es gratis"**: cuesta cache invalidation cada write. Variables locales son órdenes de magnitud más baratas.

**"Atomic ops son gratis"**: ~10-50 ciclos cada una. Mucho menos que un mutex (100-1000) pero mucho más que un acceso normal (1).

**"Lock-free es siempre mejor"**: NO. Más complejo, ABA problem, memory ordering bugs. Para 99% de casos, locks son suficientes y mucho más simples.

**"x86 garantiza orden estricto"**: parcialmente. Garantiza más que ARM pero no orden total cross-core. Código portable necesita barriers.

**"CAS resuelve todo"**: solo operaciones simples sobre 1 variable. Para estructuras complejas, lock-free programming es brutal.

**"NUMA es overkill para mí"**: para portátil / servidor pequeño, sí. Para servidores grandes, ignorarlo mata performance.

---

## 12. Preguntas típicas de interview

**¿Qué es cache coherence?**: protocolo hardware para mantener caches de varios cores sincronizadas.

**MESI**: Modified, Exclusive, Shared, Invalid. Estados de cache lines en multicore.

**False sharing**: dos variables distintas en misma cache line causan invalidaciones cruzadas. Solución: padding.

**Memory ordering — strong vs weak**: x86 strong, ARM weak. Código portable necesita memory barriers explícitos.

**Atomic operations**: instrucciones hardware indivisibles. CAS, fetch-add. Más caras que ops normales pero base de locks/lock-free.

**ABA problem**: CAS no detecta cambios que se revirtieron. Solución: tagged pointers, hazard pointers.

**Cuándo lock-free**: muy alta contención + no puedes bloquear. Para resto: locks normales.

---

## 13. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué multicore necesita coherencia (caches separadas por core).
- MESI: 4 estados y transiciones básicas.
- Coste real de compartir variables mutables entre threads.
- False sharing y solución (padding).
- Strong vs weak memory ordering (x86 vs ARM).
- Acquire-release semantics.
- Atomic operations: CAS, fetch-add.
- ABA problem y por qué lock-free es difícil.
- NUMA en sistemas grandes.

Si no puedes → relee.

---

## ¡Cluster Computer Architecture completado! 🎉

3 docs:
- `01-cpu-pipeline-y-registros` — pipeline, branch prediction, SIMD, OoO.
- `02-jerarquia-de-memoria-y-cache` — caches, localidad, layout matters.
- `03-coherencia-cache-multicore` — MESI, false sharing, memory ordering.

**Próximo**: cluster 08 (Security — 4 docs).

---

## Conexiones

- [[01-cpu-pipeline-y-registros]] — out-of-order execution causa reordering visible
- [[02-jerarquia-de-memoria-y-cache]] — coherencia es cache-level
- [[../03_concurrency/01-race-conditions]] — esto es la base hardware
- [[../03_concurrency/02-locks-y-mutex]] — mutex implementado con atomic ops
- [[../03_concurrency/04-async-vs-threads-vs-procesos]] — async evita coherencia (single-thread)
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **CSAPP** capítulo 6.7-6.8 (Multi-core caches).
- **A Primer on Memory Consistency and Cache Coherence** (Sorin et al., Morgan Claypool) — el libro de referencia.
- **Concurrency primer** (en preshing.com) — Jeff Preshing's blog, lectura obligatoria sobre memory ordering.
- **C++ memory model** (en cppreference) — referencia técnica.
- **Java Memory Model FAQ** (cs.umd.edu).
- **Mechanical Sympathy** blog — Martin Thompson sobre cache-aware programming.
