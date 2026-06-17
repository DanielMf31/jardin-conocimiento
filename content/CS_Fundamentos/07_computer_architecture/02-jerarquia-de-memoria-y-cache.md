# 02 — Jerarquía de memoria y cache

> **Doc 2 del cluster Computer Architecture**. La razón #1 por la que dos pieces de código que parecen iguales tienen performance brutalmente distinta. Conocer esto te diferencia como engineer.
> **Frecuencia interview**: aparece en preguntas de performance avanzadas, cache-friendly algorithms, optimización low-level.
> **Tiempo de lectura estimado**: 35-50 min.

---

## 1. La pirámide de memoria

Cualquier ordenador moderno tiene una **jerarquía** de tipos de memoria, ordenada por velocidad y tamaño:

| Nivel | Tamaño típico | Latencia | Coste/GB |
|---|---|---|---|
| Registros | ~1 KB total | <1 ns | — (parte del CPU) |
| L1 cache | 32-64 KB por core | 1-2 ns | muy caro |
| L2 cache | 256 KB - 1 MB por core | 3-10 ns | caro |
| L3 cache | 4-64 MB compartido | 10-40 ns | medio |
| RAM (DDR5) | 8-128 GB | 80-150 ns | barato |
| SSD NVMe | 0.5-8 TB | 50-100 µs | muy barato |
| HDD | 1-20 TB | 5-15 ms | baratísimo |
| Red local | infinita | 0.1-1 ms | depende |
| S3 / cloud | infinita | 50-200 ms | barato |

**La proporción es brutal**: RAM es 100x más lento que L1 cache. SSD es 1000x más lento que RAM. Cada nivel es 10-1000x más lento que el anterior.

**El truco**: el sistema mantiene los datos "calientes" en los niveles más rápidos. Tú escribes código que asume RAM uniforme. La realidad es jerárquica.

---

## 2. Por qué hay caches

Si la RAM es relativamente lenta (~100ns) y la CPU funciona a 3GHz (1 ciclo = 0.3ns), cada acceso a RAM = ~300 ciclos perdidos. **La CPU se queda esperando datos**.

**La solución**: caches L1, L2, L3 entre CPU y RAM. Datos accedidos recientemente se quedan en caches. Próximo acceso → cache hit, rápido.

Sin caches, una CPU moderna sería 100x más lenta. **Las caches son la razón por la que cualquier código va a velocidad razonable**.

---

## 3. Cómo funciona un cache (modelo simplificado)

Cuando la CPU pide leer una dirección de memoria:
1. Mira en L1: ¿está? Si sí → cache hit, devuelve en 1-2 ns.
2. Si no, mira en L2: ¿está? Si sí → cache hit, devuelve en 3-10 ns.
3. Si no, L3: ¿está? Si sí → 10-40 ns.
4. Si no, RAM: 80-150 ns.

Cada miss baja un nivel. Cada hit es ~10-30x más rápido que ir al siguiente nivel.

### Cache lines

Las caches no operan byte a byte. Operan en **cache lines** de **64 bytes** (típico en x86 moderno).

Cuando lees 1 byte que no está en cache, la CPU trae los **64 bytes circundantes** (la cache line entera). Por eso los siguientes accesos secuenciales son cache hits gratis.

**Implicación**: el layout de tus datos importa. Datos que se acceden juntos deben estar en memoria contigua.

---

## 4. Localidad — el principio fundamental

Las caches funcionan porque los programas reales tienen **localidad**:

### Localidad espacial

Si accedes a la dirección X, probablemente accederás pronto a X+1, X+2, etc.

**Por qué**: arrays, structs, código secuencial.

**Implicación**: layouts contiguos. Iterar arrays en orden. Evitar pointer-chasing en estructuras dispersas.

### Localidad temporal

Si accedes a una dirección X, probablemente la accederás de nuevo pronto.

**Por qué**: variables de loop, contadores, headers de structs reutilizados.

**Implicación**: mantener datos "hot" juntos en memoria. Reutilizar registros.

**El código que respeta localidad es 5-100x más rápido que el que no**. No es metáfora.

---

## 5. Ejemplo dramático — orden de loop

Imagina una matriz 2D de 1000x1000 enteros. Sumar todos los elementos.

```c
// Versión A: row-major (rápida)
for (int i = 0; i < N; i++)
    for (int j = 0; j < N; j++)
        sum += matrix[i][j];

// Versión B: column-major (lenta)
for (int j = 0; j < N; j++)
    for (int i = 0; i < N; i++)
        sum += matrix[i][j];
```

C/Python guardan matrices en **row-major** (filas contiguas en memoria). La versión A accede en orden contiguo: cache hits gratis.

La versión B salta `N * sizeof(int)` bytes en cada acceso. Cada uno es cache miss probable. **10-50x más lenta** para matrices grandes.

**Mismo algoritmo, mismo número de operaciones. Pero el patrón de acceso a memoria cambia todo**.

Esto es lo que hace que NumPy `arr.sum(axis=0)` vs `arr.sum(axis=1)` tengan performance distinta. O que iterar `pandas.DataFrame` por filas sea lentísimo.

---

## 6. Cache-friendly data structures

### Arrays vs linked lists

Arrays son **cache-friendly** por excelencia: memoria contigua, localidad espacial perfecta.

Linked lists son **cache-hostile**: cada nodo está en una zona random de memoria. Cada `node = node.next` es probable cache miss.

**Para datos que iteras secuencialmente, array > linked list, casi siempre**. Aunque la teoría diga "linked list es O(1) insertar".

Esto es por qué `std::vector` (C++) suele superar a `std::list` incluso para inserciones, hasta tamaños sorprendentemente grandes.

### Struct of Arrays (SoA) vs Array of Structs (AoS)

```c
// AoS — cada item junto, todos sus campos
struct Particle { float x, y, z; float vx, vy, vz; };
Particle particles[1000000];

// SoA — un array por campo
struct Particles {
    float x[1000000];
    float y[1000000];
    float z[1000000];
    float vx[1000000];
    float vy[1000000];
    float vz[1000000];
};
```

Si solo iteras posiciones (x, y, z) y no velocidades:
- AoS trae a cache 24 bytes por particle (incluyendo vx,vy,vz que no usas).
- SoA solo trae 12 bytes (x, y, z).

SoA usa 2x menos cache para queries específicas. **GPUs y código SIMD prefieren SoA**.

Para queries que usan TODOS los campos a la vez, AoS gana. Depende del workload.

### HashMap vs sorted array

Para tablas pequeñas (<100 elementos), un sorted array con binary search puede superar a un hashmap. Razón: el hashmap salta a buckets dispersos (cache miss), mientras que el binary search en array contiguo aprovecha localidad.

Esto explota a la mayoría de developers. La intuición "O(1) > O(log N)" ignora cache effects.

---

## 7. False sharing — el bug oculto en multi-threading

Cuando dos threads escriben **variables distintas** en la misma cache line, las CPUs tienen que **sincronizar la cache line** entre cores. Cada escritura invalida el cache del otro core.

**Ejemplo**:

```c
struct Counters { int a; int b; };  // ambos en misma cache line de 64 bytes
Counters counters;

// Thread 1
for (int i = 0; i < 1M; i++)
    counters.a++;

// Thread 2
for (int i = 0; i < 1M; i++)
    counters.b++;
```

Aunque a y b son variables independientes, el thread 1 invalida la cache line del thread 2 en cada incremento. Performance: como si fuera una sola variable compartida.

**Solución**: padding entre las variables para que estén en cache lines distintas.

```c
struct Counters {
    int a;
    char pad1[60];  // padding hasta llenar la cache line
    int b;
};
```

False sharing es un bug real en código multi-threaded. Causa "scaling negativo" — añadir threads ralentiza el código.

---

## 8. Prefetching — la CPU adivina

CPUs modernas tienen **hardware prefetchers**: detectan patrones de acceso y traen datos futuros a cache antes de que los pidas.

Si iteras un array secuencialmente, el prefetcher detecta el patrón y trae la siguiente cache line en background. Por eso loops sobre arrays son tan rápidos.

Si tu acceso es **aleatorio o no detectable** (linked list, hash table), el prefetcher no ayuda. Cada acceso paga latencia completa.

Algunos compiladores e intrinsics permiten **prefetch manual** (`__builtin_prefetch` en GCC). Útil para casos muy específicos donde sabes el patrón futuro pero el hardware no lo detecta.

---

## 9. Cache replacement policies

Cuando un cache se llena, la CPU tiene que **evictar** algo para meter lo nuevo. La policy determina qué:

- **LRU (Least Recently Used)**: tira lo menos usado recientemente. Lo más común.
- **PLRU (Pseudo-LRU)**: aproximación más barata de implementar en hardware.
- **Random**: simple, sorprendentemente bueno para algunos workloads.

Estas son decisiones de hardware, no programables. Pero entender que **el cache evicta cuando se llena** te ayuda a diseñar code que cabe en cache.

---

## 10. Working set — cuánto cache necesita tu código

El **working set** es el conjunto de datos que tu código accede activamente en una ventana de tiempo.

- Si working set **cabe en L1** (32 KB): ultra rápido.
- Si cabe en L2 (256 KB - 1 MB): muy rápido.
- Si cabe en L3 (decenas de MB): rápido.
- Si excede L3 → empieza a ir a RAM en cada acceso → mucho más lento.

**Diseñar para que el hot path quepa en cache** es la optimización más impactante para código compute-heavy.

**Ejemplo**: bucket sort de N enteros entre [0, K). Si K cabe en L2, mucho más rápido que K mayor que L3.

---

## 11. NUMA — la jerarquía a nivel servidor

En servidores con varios CPUs (multi-socket), cada socket tiene su **propia RAM** físicamente cercana. Acceder a la RAM de OTRO socket es 2-3x más lento.

Esto se llama **NUMA** (Non-Uniform Memory Access). Linux scheduler intenta mantener procesos cerca de su memoria.

Para apps grandes (DBs, JVMs), ignorar NUMA mata performance. Hay tooling (`numactl`, NUMA-aware allocators) para gestionarlo.

Para apps normales en hardware típico (1 socket), NUMA es invisible.

---

## 12. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

A nivel app Python, mostly invisible. Pero cuando manipules numpy arrays grandes, la diferencia entre operaciones row-wise vs col-wise importa.

### En embebido (perfil HW)

Microcontroladores típicamente tienen mucho menos cache (KB en vez de MB). El working set tiene que ser pequeño. Diseño de buffers, evitar fragmentación, layouts contiguos son críticos.

### En entrevistas tecnicas

**Pregunta clásica**: "Por qué iterar matriz por filas vs columnas tiene performance distinta".

Tu respuesta: row-major layout en memoria. Iterar por filas respeta localidad espacial → cache hits. Por columnas salta `N*sizeof` bytes → cache miss en cada acceso.

**Pregunta sobre estructuras**: "Cuándo elegirías std::vector vs std::list".

Vector casi siempre. List solo si haces inserts/removals constantes en medio Y nunca iteras (raro). Vector aprovecha cache, list es pointer-chasing.

**Pregunta avanzada**: "Por qué tu app multi-threaded no escala".

Posibilidades: contention de locks (obvio), false sharing (oculto), workload no paralelizable, GIL Python. Profile para identificar.

**Pregunta sobre optimization**: "Optimiza este loop que va lento".

1. Profile primero. ¿Es realmente este loop el cuello?
2. ¿Datos contiguos? Layout matters.
3. ¿Branch predictable? Branchless si no.
4. ¿Cabe en cache el working set?
5. ¿Vectorizable con SIMD?

---

## 13. Trampas típicas

**"Acceder a una variable es instantáneo"**: NO. Si está en RAM y no en cache, es 100ns. En SSD, 100µs. La intuición de "memoria uniforme" es falsa.

**"O(1) siempre es mejor que O(log N)"**: para tamaños pequeños, cache effects pueden invertir el orden. Sorted array con binary search puede ganar a hashmap para N pequeño.

**"Linked lists son eficientes"**: cache-hostile. Para iteración, vector siempre gana hasta tamaños grandes.

**"Más threads = más rápido"**: false sharing puede hacer que más threads sean MÁS LENTOS. Profile para detectar.

**"El compilador no puede optimizar layout"**: el compilador respeta lo que escribes. Layout en memoria lo decides tú con tus structs y arrays.

**"NUMA es problema de servidores enterprise"**: aplica a cualquier sistema multi-socket. Para tu portátil con 1 CPU físico, irrelevante.

**"Premature optimization es la raíz de todo mal"** (Knuth): cita malinterpretada. Knuth se refería a optimización SIN MEDICIÓN. Conocer cómo funciona la CPU te permite escribir código que **por defecto** sea cache-friendly. Eso no es premature optimization.

---

## 14. Preguntas típicas de interview

**Por qué row-major iteration es más rápido**: cubierto sección 5.

**Cache lines**: 64 bytes típicamente. Lecturas siempre traen cache line completa. Layout contiguo importa.

**Localidad espacial vs temporal**: espacial = cerca en memoria. Temporal = cerca en tiempo. Las caches explotan ambas.

**False sharing**: dos threads escribiendo variables distintas en misma cache line → invalidación constante → scaling negativo. Solución: padding.

**Working set**: datos accedidos activamente. Si cabe en cache, rápido.

**Por qué array > linked list en cache**: contiguo vs disperso. Prefetcher ayuda con array, no con list.

---

## 15. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Pirámide de memoria con latencias relativas (registers → L1 → L2 → L3 → RAM → disco).
- Por qué existen caches (RAM es 100x más lenta que L1).
- Cache lines (64 bytes) y localidad espacial.
- Localidad espacial vs temporal y por qué importan.
- Por qué iterar matriz row-major vs column-major tiene 10-50x diferencia.
- Por qué array supera a linked list en cache.
- False sharing y cómo prevenirlo.
- Working set y diseñar para que quepa en cache.

Si no puedes → relee.

---

## Conexiones

- [[01-cpu-pipeline-y-registros]] — branch prediction y SIMD relacionados
- [[03-coherencia-cache-multicore]] — cómo se sincronizan caches entre cores
- [[../02_operating_systems/02-memoria-virtual-paging]] — TLB es parte de la jerarquía
- [[../03_concurrency/01-race-conditions]] — false sharing es race oculto
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **What every programmer should know about memory** (Ulrich Drepper, 2007) — el clásico.
- **CSAPP** capítulo 6 (Memory Hierarchy).
- **Agner Fog optimization manuals** — gratis, brutal.
- **Mechanical Sympathy** (mechanical-sympathy.blogspot.com, Martin Thompson) — cache-aware programming.
- **`perf stat -e cache-misses,cache-references`** — medir cache misses reales en tu código.
- **`valgrind --tool=cachegrind`** — simulación detallada de cache.
