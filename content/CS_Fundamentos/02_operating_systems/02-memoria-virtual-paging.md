# 02 — Memoria virtual y paging

> **Doc 2 del cluster Operating Systems**. La abstracción más elegante del SO: cada proceso cree que tiene toda la memoria de la máquina para él solo. Pero el hardware MMU + el SO orquestan la mentira.
> **Frecuencia interview**: aparece en preguntas de "¿qué pasa cuando tu proceso pide memoria?", debugging OOM, performance tuning.
> **Tiempo de lectura estimado**: 50-70 min.

---

## 1. El problema que resuelve la memoria virtual

**Sin virtual memory**:
- Cada proceso pediría direcciones físicas reales.
- Procesos podrían leer/escribir memoria de otros (sin aislamiento).
- Si el RAM está fragmentado (huecos), un proceso grande no entra aunque haya espacio total suficiente.
- Si pides más RAM de la que hay, el programa muere.

**Con virtual memory**:
- Cada proceso ve su PROPIO espacio de direcciones lineal de 0 a 2^N.
- El SO + MMU traducen direcciones virtuales → físicas en cada acceso.
- **Aislamiento**: proceso A NO puede tocar memoria del proceso B.
- Memoria física puede estar fragmentada — el proceso no se entera.
- Puede usar más memoria virtual que RAM física (swap a disco).

**Cada proceso tiene SU PROPIO mapping**. Por eso `0x7fff5fbff8c0` en un proceso apunta a algo distinto que esa misma dirección en otro proceso.

---

## 2. Address space sizes

**32-bit**: direcciones de 32 bits → 2^32 = 4 GiB de espacio virtual por proceso. Aunque tu PC tenga solo 2 GB RAM, cada proceso ve 4 GiB. Limitación REAL: máximo ~2-3 GiB usables por proceso (resto reservado para kernel).

**64-bit**: direcciones de 64 bits, pero solo 48 se usan en x86-64 actual → 2^48 = 256 TiB de espacio virtual por proceso. Prácticamente infinito para apps normales.

**Por qué 64-bit ganó**: no es solo "más RAM". Es eliminar la pesadilla de fragmentación, permitir mmap de archivos enormes, y simplificar address layout.

---

## 3. Paging — la idea central

En vez de mappear DIRECCIÓN A DIRECCIÓN (caro), mappeamos **PÁGINAS a FRAMES**.

**Vocabulario clave**:
- **Página** (page): bloque de tamaño FIJO (típicamente 4 KiB) en memoria virtual. Identificada por su número de página.
- **Frame** (page frame): bloque del MISMO tamaño en memoria física.
- **Page table**: estructura del SO que mappea virtual page number → physical frame number. Una page table POR PROCESO.
- **Offset dentro de la página**: las direcciones se dividen en `(page_number, offset_within_page)`. El offset NO se traduce (es el mismo en virtual y físico).

**Ejemplo 32-bit con páginas de 4 KiB**:
- Dirección virtual: `0xABCDE123`.
- Page number: `0xABCDE` (top 20 bits).
- Offset: `0x123` (bottom 12 bits, porque 4KiB = 2^12).
- SO traduce: page 0xABCDE → frame 0x12345.
- Dirección física: `0x12345123`.

---

## 4. Address translation paso a paso

Cada acceso a memoria pasa por la **MMU (Memory Management Unit)**, que es hardware:

1. CPU genera dirección virtual: `0xABCDE123`.
2. MMU separa: page_number=`0xABCDE`, offset=`0x123`.
3. MMU consulta page table del proceso actual:
   - ¿Page `0xABCDE` está mapeada?
     - SÍ → obtener frame number (e.g. `0x12345`).
     - NO → **PAGE FAULT** (interrupt al SO, ver sección 6).
4. MMU compone dirección física: `0x12345123`.
5. CPU accede a esa dirección física en RAM.

**Esto pasa en CADA acceso**. Miles de millones por segundo. Si fuera lento, el sistema sería inservible.

**Aceleración: TLB (Translation Lookaside Buffer)**. Cache hardware de translations recientes. ~64-512 entradas. Hit ratio típico 99%+. Sin TLB, la CPU pasaría tiempo accediendo page tables.

---

## 5. Multi-level page tables (cómo se organizan en práctica)

**Problema**: page table simple para 32-bit: 2^20 entradas × 4 bytes = 4 MiB POR PROCESO. Si tienes 1000 procesos, son 4 GiB solo en page tables. Inviable. Para 64-bit es astronómico.

**Solución**: page tables JERÁRQUICAS (multi-level). La mayoría de páginas no están mapeadas (proceso usa <1% del espacio virtual). Estructura jerárquica permite no asignar entradas inútiles.

**x86-64 usa 4 niveles**: dirección 48 bits = 9 + 9 + 9 + 9 + 12 (offset).

```
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ PML4 idx │ PDPT idx │ PD idx   │ PT idx   │ offset   │
│ 9 bits   │ 9 bits   │ 9 bits   │ 9 bits   │ 12 bits  │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

Mecanismo de traducción:
- CR3 register (per-process) → apunta a PML4 table.
- PML4[idx1] → PDPT table.
- PDPT[idx2] → PD table.
- PD[idx3] → PT table.
- PT[idx4] → frame number.

4 lecturas de memoria por translation (sin TLB hit). Por eso TLB es crítico.

**Optimización: HUGE PAGES**. En vez de 4 KiB, usar páginas de 2 MiB o 1 GiB. Menos entries en TLB necesarias para cubrir misma memoria. Útil para databases, JVM heaps grandes, ML.

---

## 6. Page faults — cuando la página no está en RAM

Una **page fault** ocurre cuando el proceso accede una página que NO está actualmente en RAM física.

**Tipos de page fault**:

**Minor (soft) fault**: la página existe pero no está mapeada todavía. Ejemplo: primera vez que accedes a memoria recién malloc'd. El SO crea el mapping al instante. Rápido (~1 μs).

**Major (hard) fault**: la página está en disco (swap o archivo mapeado), no en RAM. El SO debe leerla de disco. LENTO (~10ms = 10000x más lento que RAM). En SSDs es ~0.1ms. En HDDs es 10ms.

**Invalid page fault**: el proceso accede a memoria que NO debería (e.g. NULL pointer). El SO mata el proceso con SIGSEGV (segmentation fault).

**Por qué importa**: page faults mayores son **carísimas**. Si tu programa hace muchas, está "swappeando" y el rendimiento cae brutal. Indicador: alto `system time` en `top`, alto `pswpin`/`pswpout` en `vmstat`.

---

## 7. Swap — cuando RAM no alcanza

**Swap space**: una partición o archivo en disco que el SO usa como "RAM extra". Cuando RAM se llena, SO mueve páginas de RAM a swap (page out). Cuando se necesitan, las trae de vuelta (page in) — page fault major.

**Ventaja**: permite ejecutar más procesos que RAM física.

**Desventaja**: disco es 10-100K veces más lento que RAM. Si SO está swappeando constantemente → "thrashing". Sistema se cuelga.

**Cuándo usar swap**:
- Sistemas con RAM ajustada — actúa como "buffer" para picos.
- Sistemas con apps que usan ráfagas grandes de memoria temporal.

**Cuándo evitar**:
- Servers de producción con DBs (ej: Redis) — quieres que TODO esté en RAM.
- Si hay swap y el SO decide swappear Redis → latencias absurdas.
- Solución: `swapoff -a` o configurar Redis con `--maxmemory`.

**Swappiness**: `/proc/sys/vm/swappiness` (Linux). Valor 0-100. Default 60. Más alto = SO más agresivo swappeando. Para servers: ajustar a 10 o menos.

---

## 8. mmap — mapear archivos en memoria

**`mmap`** es una syscall que mappea un archivo (o región) directamente en el espacio de memoria del proceso. Lees/escribes el "archivo" como si fuera array.

**Ventajas**:
- El SO carga páginas BAJO DEMANDA (solo lo que tocas).
- Cero copies (no read() a buffer + procesar).
- Múltiples procesos pueden mapear el MISMO archivo (shared memory).

**Uso típico**:
- Bases de datos (Postgres usa mmap para algunos accesos).
- Archivos enormes que no caben en RAM (procesar gigabytes).
- IPC: shared memory entre procesos (compartir un archivo en `/dev/shm`).
- Cargar binarios ejecutables (el código del programa se mmap-ea).

**En Python**:
```python
import mmap
with open("big.bin", "r+b") as f:
    mm = mmap.mmap(f.fileno(), 0)
    print(mm[1000:2000])  # lee bytes 1000-2000 sin cargar archivo entero
    mm.close()
```

**Desventaja**: page faults invisibles (lentos en disco lento). Más complejo si el archivo cambia mientras lo lees.

---

## 9. Memory-mapped I/O y kernel space

**Kernel space vs user space**: el SO se reserva una porción del espacio virtual de cada proceso para código y datos del kernel. Usuario NO puede acceder (privilegio).

**En x86-64 Linux**:
- User space: `0x0000_0000_0000_0000` - `0x0000_7FFF_FFFF_FFFF` (~128 TiB).
- Kernel space: `0xFFFF_8000_0000_0000` - `0xFFFF_FFFF_FFFF_FFFF` (~128 TiB).
- Hueco intermedio: direcciones inválidas (canonical address rule).

**Syscall = transición user → kernel**: cuando llamas a syscall (read, write, fork...), CPU cambia a "kernel mode". Privilegio elevado, puede acceder kernel space. Tras syscall, vuelve a "user mode". Switch tiene coste (~100 ns).

---

## 10. Heap allocation — qué hace malloc/free

**Libc malloc**: tu app pide N bytes. Libc maneja el heap y devuelve un puntero.

**Internamente**:
- Mantiene listas de bloques libres por tamaño.
- Si tiene un bloque libre que cabe → te lo da (rápido).
- Si no → pide al kernel más memoria con `brk()` o `mmap()`.

**brk vs mmap**:
- **`brk()`**: expande/contrae el heap (segmento contiguo). Bueno para allocations pequeñas frecuentes.
- **`mmap()`**: mapea regiones grandes nuevas. Bueno para allocations >128 KiB típicamente.

**Por qué free no libera inmediatamente a SO**: free marca el bloque como libre internamente, pero NO devuelve memoria al SO hasta que se acumule suficiente o uses tcmalloc/jemalloc. Por eso un proceso puede mantener "picos" de RAM que liberó técnicamente.

**Allocators alternativos**:
- **tcmalloc** (Google): mejor multi-threaded.
- **jemalloc** (FreeBSD/Facebook): menos fragmentación.
- **mimalloc** (Microsoft): muy rápido.

Diferencias en: thread-local caches, fragmentación, locking.

**En Python**: Python usa su propio allocator (pymalloc) para objects pequeños. Para grandes, llama directo a malloc del SO. Garbage collector adicional para reference cycles.

---

## 11. Shared memory entre procesos

Procesos normalmente tienen memoria aislada. Para compartir explícitamente:

**Opción 1 — POSIX shared memory**: `shm_open()` crea un objeto compartido. Múltiples procesos lo mmap-ean. Comparten datos sin IPC overhead.

**Opción 2 — System V shared memory** (legacy): `shmget()`, `shmat()`. Más viejo, todavía usado.

**Opción 3 — mmap de archivo**: múltiples procesos mmap el mismo archivo (con `MAP_SHARED`). Cambios visibles a todos.

**Opción 4 — Anonymous mmap + fork**: padre hace mmap `MAP_SHARED MAP_ANONYMOUS` antes del fork. Hijos heredan el mapping. Compartido sin archivo.

**Caveat: sincronización**. Compartir memoria SIN locks → race conditions. Necesitas mutex compartido (también via shared memory) o atomic ops. Ver doc 03_concurrency/02-locks-y-mutex.

**En Python 3.8+**: `multiprocessing.shared_memory.SharedMemory`. Para pasar arrays grandes entre procesos sin pickle overhead.

---

## 12. OOM killer — cuando se acaba la RAM (Linux)

**OOM (Out Of Memory) killer**: cuando Linux no puede satisfacer una request de memoria, en lugar de rechazarla (lo que rompería apps mal escritas), el kernel ELIGE algún proceso y lo MATA.

**Criterio del OOM score**: procesos puntúan según:
- Cuánta memoria usan (más memoria = más probable víctima).
- Cuánto tiempo llevan corriendo (procesos jóvenes = más víctimas).
- Configuración manual (`oom_score_adj` en `/proc/PID`).

Algunos procesos "intocables": init (PID 1), procesos críticos del kernel.

**Cómo saber si te pasó**:
```bash
$ dmesg | grep -i "oom"
$ journalctl -k | grep -i "killed process"
```

**Cómo prevenir**:
- Configurar limits (ulimit, cgroups, Docker `--memory`).
- Monitorear uso de RAM.
- Ajustar `oom_score_adj` para procesos críticos: `-1000` = inmune.
- En Kubernetes: configurar memory requests/limits.

---

## 13. Cgroups y memory limits (cómo Docker limita memoria)

**Cgroups (Control Groups)**: mecanismo del kernel Linux para limitar y aislar recursos (CPU, memoria, I/O, red, etc.) por GRUPO de procesos.

**Uso**: Docker, Kubernetes, systemd, todos usan cgroups.

```bash
$ docker run --memory 512m mi_app
```

Crea cgroup con limit 512 MiB. Si app excede → OOM kill DENTRO del cgroup. Esto es independiente del OOM kill global del sistema.

**Efectos**:
- Tu container Java/Python necesita saber el limit del cgroup, no la RAM total del host. Lenguajes modernos lo detectan.
- Antes de Java 11, JVM veía la RAM HOST → reservaba demasiado → OOM. Bug famoso del Java en containers.

---

## 14. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Tu container Docker tiene un cgroup con limit (configurable con `--memory`). Si tu Python proceso se queda corto, el OOM killer DEL container lo mata. Ver con `docker stats` el uso de memoria.

### En entrevistas tecnicas

**Pregunta**: "Qué pasa cuando llamas `malloc(1MB)` en C"

**Respuesta**: libc decide: tiene espacio en heap → te lo da. Si no, llama `brk()` (heap chico) o `mmap()` (chunk grande). El kernel asigna VIRTUAL pages. La memoria física NO se asigna hasta que la TOQUES (lazy allocation, copy-on-write con páginas zero). Cuando accedes la primera vez → minor page fault → se asigna frame físico.

**Pregunta**: "Por qué tu app de 1 GB Python ocupa 2 GB en `top`?"

**Respuesta**: RSS (Resident Set Size) cuenta páginas en RAM. Mucho más que tus datos: Python interpreter overhead (~30-50 MB), importadas C libraries (numpy, scipy son cientos de MB), page cache shared (si lees archivos), heap fragmentation (libc no devuelve memoria al SO hasta big chunks). Diferencia VSS vs RSS: VSS es virtual, RSS es físico residente.

**Pregunta**: "Por qué usar 1 thread + asyncio vs 1000 threads"

**Respuesta**: 1000 threads = 1000 stacks de 8 MiB cada uno = 8 GiB de virtual memory reservada (aunque solo se commit cuando se usa). Más context switching overhead. asyncio: 1 thread, miles de tasks ligeros (~KB cada uno).

### Para embebido (perfil HW)

Embedded systems tienen MUY POCA RAM (KBs en MCUs). Saber sobre virtual memory te ayuda a entender por qué embedded NO la tiene típicamente (MMU es cara, paging requires RAM extra para tables). FreeRTOS es flat memory.

---

## 15. Trampas típicas

**"RAM total = suma de RAM de procesos en `top`"**: NO. `top` muestra RSS por proceso. Pero las páginas SHARED (libc, etc.) se cuentan en CADA proceso. La suma sobreestima.

**"Free RAM = lo que dice `free`"**: Linux usa RAM "libre" para PAGE CACHE (cache de archivos). El verdadero "available" es cached + free + buffers. Por eso `free -h` muestra "available" separado.

**"Más RAM siempre es mejor"**: hasta cierto punto. Si tu app cabe en RAM y no swapea, más RAM no ayuda. Mejor invertir en RAM más rápida (DDR5) o más cores.

**"Mi proceso pide 1 GB, ergo me come 1 GB"**: no con allocation lazy. `mmap(1GB)` es virtual. Solo páginas tocadas ocupan RAM física.

**"Liberar memoria con `free()` la devuelve al SO"**: no siempre. Libc puede mantenerla en su pool interno. Para forzar devolución: `malloc_trim(0)` (Linux) o usar jemalloc.

**"Page fault siempre es malo"**: minor faults son normales (parte del lazy allocation). Major faults (swap) son malos.

**"Con 64-bit no hay límite de memoria"**: hay límite por:
- RAM física + swap.
- Configuración cgroups / ulimit.
- 48 bits realmente usados (256 TiB).
- Address space layout (ASLR reserva regiones).

---

## 16. Preguntas típicas de interview

**"Por qué virtual memory existe"** — aislamiento entre procesos, abstracción del hardware, permitir más memoria virtual que física, simplificar linker (loaders).

**"Diferencia entre virtual y physical address"** — virtual: lo que ve el proceso. Physical: lo que está en el chip RAM. MMU traduce en cada acceso.

**"Qué pasa cuando hay un page fault"** — CPU genera interrupt al SO. SO determina:
- Inválido (NULL pointer): SIGSEGV, mata proceso.
- Minor: página existe pero no mapeada todavía. Crea mapping.
- Major: página en swap o disco. Lee de disco (lento), restaura.

Tras manejar, CPU reintenta la instrucción que faltó.

**"Diferencia entre stack y heap"** — stack: variables locales, automático, rápido, limitado (8 MiB típico). Heap: memoria dinámica (malloc), manual (en C) o GC (Python), más lento, más grande.

**"Cómo previenes que tu Python use demasiada memoria"** — memory profiler (memray, memory_profiler, tracemalloc). Generators en vez de listas grandes. Procesar streaming (no cargar archivo entero). Usar arrays numpy / dataclasses con `__slots__`. En container: limit con Docker `--memory`.

**"Qué es copy-on-write y dónde se usa"** — optimización: clonar memoria sin copiar realmente. Marca páginas como COW. Cuando alguno escribe, ENTONCES copia. Se usa en `fork()` (no copia memoria padre), en mmap `MAP_PRIVATE`, en filesystems modernos (btrfs, zfs).

---

## 17. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Virtual address vs physical address y por qué se separan.
- Page, frame, page table — qué son.
- Cómo se hace una translation (página + offset).
- Por qué multi-level page tables (memoria de tables sería absurda).
- TLB y por qué importa para performance.
- Page fault: minor vs major vs invalid.
- Swap: qué es, cuándo es problema.
- mmap: qué resuelve, casos de uso.
- Por qué `free()` no siempre devuelve memoria al SO.
- OOM killer y cgroups (Docker memory limits).

Si no puedes → relee la sección.

---

## Conexiones

- [[01-procesos-y-threads]] — cada proceso tiene su page table
- [[03-scheduling]] — context switch implica cambiar page table
- [[04-syscalls-y-kernel]] — brk(), mmap(), shm_open() son syscalls
- [[../03_concurrency/02-locks-y-mutex]] — sincronizar acceso a shared memory
- [[../07_computer_architecture/02-jerarquia-de-memoria-y-cache]] — TLB es parte del cache hierarchy
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **OSTEP** capítulos 13-23 (Virtualización de memoria, completo). GRATIS pages.cs.wisc.edu/~remzi/OSTEP/
- **CSAPP** capítulo 9 (Memoria virtual). Bryant & O'Hallaron.
- **What every programmer should know about memory** (Ulrich Drepper, 2007) — denso pero brutal.
- **`pmap`, `vmstat`, `/proc/PID/maps`, `/proc/PID/smaps`** — inspeccionar memoria de procesos.
- **`memray`, `tracemalloc`** — profiling Python.
