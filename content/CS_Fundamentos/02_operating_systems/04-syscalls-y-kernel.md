# 04 — Syscalls y kernel

> 📚 **Doc 4 del cluster Operating Systems**. La frontera entre tu código y el SO. Cada vez que abres un archivo, lees un socket o creas un proceso, atraviesas esta frontera.
> 🔥 **Frecuencia interview**: pregunta clásica "¿qué pasa cuando llamas read()?", debugging con strace.
> ⏱️ **Tiempo de lectura estimado**: 35-50 min.

---

## 1. User space vs kernel space

**User space**: donde corre TU código (Python, FastAPI, browsers). Privilegios LIMITADOS. No puede acceder hardware directamente. No puede acceder memoria de otros procesos ni del kernel.

**Kernel space**: donde corre el SO mismo (drivers, schedulers, gestión memoria). Privilegios COMPLETOS. Puede acceder TODO el hardware. Puede ver todos los procesos.

**Separación**: CPU tiene "modos" (rings en x86: ring 0 = kernel, ring 3 = user). Hardware FORZARÁ que código user-space no ejecute instrucciones privilegiadas. Si lo intenta → trap → SO lo mata (segfault).

**Propósito**: si user-space pudiera tocar hardware, un bug en una app rompería todo el sistema. La separación es la base de la estabilidad de los SOs modernos.

---

## 2. Qué es un syscall

Un **syscall (system call)** es la forma controlada en que user-space pide al kernel hacer algo que requiere privilegios.

**Ejemplos de cosas que requieren syscall**:
- Leer/escribir archivo (read, write, open).
- Enviar/recibir red (send, recv, socket).
- Crear procesos (fork, exec).
- Allocar memoria del sistema (brk, mmap).
- Esperar señales (wait, signal).
- Cambiar de directorio (chdir).
- Tiempo (gettimeofday, clock_gettime).
- Cualquier cosa que necesite hardware o cross-process.

**Ejemplos que NO necesitan syscall**:
- Aritmética (suma, multiplicación).
- Operaciones en memoria del proceso (acceder array, modificar variables).
- Llamar funciones de tu propio código.
- Cálculos puros.

---

## 3. Cómo funciona un syscall internamente

**Paso a paso (x86-64 Linux)**:

1. TU CÓDIGO llama a una función de libc (read, write, fork...).
2. LIBC pone los parámetros en registros (RDI, RSI, RDX...) y el número del syscall en RAX.
3. LIBC ejecuta la instrucción `SYSCALL` (o `INT 0x80` en x86 viejo).
4. CPU TRAP a kernel mode. Salta a una dirección fija (handler).
5. KERNEL handler:
   - Lee número de syscall de RAX.
   - Busca en la TABLA de syscalls la función correspondiente.
   - Valida parámetros (¡importante! user puede pasar basura).
   - Ejecuta la operación (acceder hardware, modificar estructuras kernel).
   - Pone resultado en RAX.
6. KERNEL ejecuta `SYSRET`. CPU vuelve a user mode, en la instrucción siguiente al SYSCALL.
7. LIBC interpreta el resultado (e.g. -1 = error, mira errno).
8. LIBC devuelve a TU CÓDIGO.

**Coste**:
- Switch user→kernel: ~100ns en CPUs modernas (Meltdown mitigations lo hicieron más caro tras 2018).
- Más el trabajo del syscall mismo.
- Comparado con función normal (~1ns): syscall es ~100x más caro.

---

## 4. Syscalls importantes a conocer

### Procesos

- **`fork()`** → clonar proceso.
- **`exec()`** → reemplazar imagen del proceso (varias variantes: execve, etc.).
- **`wait()` / `waitpid()`** → esperar a hijo.
- **`exit()`** → terminar proceso.
- **`getpid()`** → obtener PID propio.
- **`kill()`** → enviar señal a proceso.

### Archivos

- **`open()`** → abrir archivo, devuelve file descriptor (fd).
- **`close()`** → cerrar fd.
- **`read()`** → leer N bytes de fd.
- **`write()`** → escribir N bytes a fd.
- **`lseek()`** → mover posición del fd.
- **`stat()` / `fstat()`** → info del archivo (tamaño, permisos).
- **`unlink()`** → borrar archivo.
- **`rename()`** → renombrar.
- **`mkdir()` / `rmdir()`** → directorios.

### Memoria

- **`brk()` / `sbrk()`** → expandir/contraer heap.
- **`mmap()` / `munmap()`** → mapear regiones de memoria.
- **`mprotect()`** → cambiar permisos (lectura/escritura/ejecución).

### Red

- **`socket()`** → crear socket.
- **`bind()`** → asociar a IP+puerto.
- **`listen()` / `accept()`** → server pasivo.
- **`connect()`** → cliente activo.
- **`send()` / `recv()`** → enviar/recibir.
- **`shutdown()`** → cerrar dirección de socket.

### I/O multiplexing

- **`select()` / `poll()`** → esperar eventos en múltiples fds (clásico).
- **`epoll_create()` / `epoll_wait()`** → versión escalable Linux.
- **`kqueue()`** → versión BSD/Mac.
- **`io_uring`** → moderno Linux, async I/O verdadera.

### Otros importantes

- **`ioctl()`** → "operaciones del dispositivo" (catch-all).
- **`fcntl()`** → control de file descriptors (set non-blocking, etc.).
- **`clock_gettime()`** → tiempo de alta resolución.
- **`nanosleep()`** → dormir.
- **`sched_yield()`** → ceder CPU.
- **`ptrace()`** → debugging (gdb, strace lo usan).

---

## 5. File descriptors — el concepto unificador Unix

**En Unix, "todo es un archivo"**: archivos regulares, sockets, pipes, devices, terminales, todo se accede via file descriptors.

Un **file descriptor** es un entero pequeño (típicamente 0, 1, 2, ...) que identifica un recurso abierto del proceso.

**3 fds estándar**:
- fd 0 = stdin (entrada estándar).
- fd 1 = stdout (salida estándar).
- fd 2 = stderr (errores estándar).

**Nuevos**: `open()` devuelve el menor entero libre (típicamente 3 para el primero).

**Límite**: cada proceso tiene un límite (`ulimit -n`, default 1024 o 65535). Si lo superas → "Too many open files". Recuerda CERRAR fds.

**Ventaja del modelo**: la misma syscall `read()` funciona para archivo, socket, pipe. Generalidad enorme. Por eso epoll/select toman fds — todos uniformes.

---

## 6. Strace — la herramienta esencial para debugging

`strace` MUESTRA todas las syscalls que un proceso hace. Esencial para entender qué hace un programa, debug de "por qué falla", y aprender qué hace cualquier comando por debajo.

**Ejemplos**:

```bash
$ strace ls /tmp
execve("/bin/ls", ["ls", "/tmp"], 0x...) = 0
brk(NULL)                                = 0x55...
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
fstat(3, {...})                         = 0
mmap(NULL, 12345, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7f...
close(3)                                 = 0
... (cientos más)
openat(AT_FDCWD, "/tmp", O_RDONLY|...)   = 3
getdents64(3, ...)                       = N
close(3)                                 = 0
write(1, "file1.txt\nfile2.txt\n", 20)   = 20

$ strace -e openat python -c "open('/etc/passwd')"
   solo muestra openat syscalls

$ strace -p 1234
   attach a un proceso ya corriendo

$ strace -c ls
   resumen contado: cuántas de cada syscall
```

**Strace es lento**: añade overhead enorme (cada syscall se intercepta). NO usar en producción real-time. Para debugging aislado.

**Alternativas modernas**:
- **`bpftrace`**: más eficiente, más flexible.
- **`perf trace`**: parte del perf de Linux.
- **`dtrace`**: BSD/macOS.

---

## 7. Ltrace — para librerías

`ltrace` es como strace pero para llamadas a **librerías dinámicas**, no syscalls.

```bash
$ ltrace ls
  malloc(...)
  free(...)
  fopen(...)
  ... (funciones de libc, glibc)
```

Útil para entender qué libraries usa un binario y qué functions llama. Menos común que strace.

---

## 8. Syscall vs library function

**Distinción importante**:

**Library function (printf, malloc, fopen)**: definida en una librería (libc). Vive en USER SPACE. Puede o no llamar a syscalls internamente. Ejemplo: `printf("hello")` eventualmente llama `write(1, "hello", 5)`.

**Syscall (write, read, open)**: es la frontera al kernel. Vive en KERNEL SPACE. Llamada via instrucción SYSCALL/INT.

**Por qué distinción**: libc abstrae cosas:
- **Buffering** (printf no llama write inmediato; bufferiza).
- **Conversión de tipos** (printf formatea).
- **Manejo de errores** (errno).

Sin libc, programar contra syscalls directos es tedioso. Pero entender DÓNDE está la frontera importa para performance.

**Ejemplo interesante**: `printf("hello")` en bucle 1M veces:
- Sin buffering: 1M syscalls write(). Lento.
- Con buffering (default): pocos syscalls. Mucho más rápido.

Por eso `fflush(stdout)` o "stdout no buffered" cambia comportamiento.

---

## 9. vDSO — el truco para syscalls baratos

**Problema**: `gettimeofday()` es uno de los syscalls más llamados (logging, métricas). Cada call: 100ns de overhead. Si llamas 1M veces, son 100ms.

**Solución: vDSO (virtual Dynamic Shared Object)**. El kernel mappea código suyo READ-ONLY en el espacio de cada proceso. Algunas "syscalls" se pueden ejecutar EN USER SPACE leyendo data que el kernel mantiene actualizada.

**Syscalls que están en vDSO**: `gettimeofday()`, `clock_gettime()`, `getcpu()`, `time()`. Cuando llamas `gettimeofday()` en libc moderna, ejecuta en user mode. ~10x más rápido que syscall real.

**Ver**:
```bash
$ ldd /bin/ls
... linux-vdso.so.1 (0x...)  ← esto
```

No tienes que hacer nada. Es transparente. Pero saber que existe explica por qué `gettimeofday` es muy rápido (no es realmente syscall).

---

## 10. Kernel modules — extender el kernel

**Kernel modules**: código que se carga DENTRO del kernel en runtime. Sin recompilar el kernel. Se ejecuta con privilegios COMPLETOS — un bug aquí puede colgar el SO.

**Ejemplos**:
- Drivers de dispositivos (cargados al insertar USB, etc.).
- Filesystem drivers (ext4, btrfs, ntfs).
- Network protocols (TCP, IPv6).
- Hooks de seguridad.

**Comandos**:
```bash
$ lsmod                    # listar modulos cargados
$ modprobe nombre          # cargar
$ rmmod nombre             # descargar
$ modinfo nombre           # info
```

**Caso típico**: conectas USB → kernel detecta → carga driver del módulo apropiado.

---

## 11. eBPF — el "JavaScript del kernel"

**eBPF (extended Berkeley Packet Filter)** permite ejecutar pequeños programas EN EL KERNEL de forma SEGURA. El kernel verifica el código antes de ejecutarlo (no puede colgar SO).

**Usos**:
- **Networking** (XDP — packet filtering ultra-rápido, faster than iptables).
- **Observability** (tracing programas: bpftrace, bcc tools).
- **Security** (falco, seccomp-bpf).
- **Performance profiling** (perf con eBPF).

**Por qué es revolucionario**: antes, para tracing/filtering complejo necesitabas escribir kernel modules. Ahora: programa eBPF en C/Rust, lo cargas, ejecuta en kernel. Sin reboot. Sin riesgo de crash. Performance casi nativa.

**Usado por**: Cilium (CNI Kubernetes con eBPF), Falco (security), Datadog APM, cualquier observability moderno.

No tienes que escribir eBPF, pero es bueno saber que existe.

---

## 12. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Cada `requests.get(...)` desde tu CLI hace cientos de syscalls:
- `socket()` → crea fd.
- `connect()` → handshake TCP.
- `write()` (varias) → enviar request.
- `epoll_wait()` → esperar response.
- `read()` (varias) → recibir.
- `close()` → cerrar.

Si quieres VER esto: `strace -e trace=network python cli.py`. Te lo muestra todo.

### En entrevistas tecnicas

**Pregunta**: "Qué pasa cuando ejecutas `cat archivo.txt`"

**Respuesta**: bash hace `fork()`. Hijo hace `exec("cat", ["cat", "archivo.txt"])`. Cat hace `open("archivo.txt")` → fd. `read(fd, buffer, N)` en loop. `write(1, buffer, N)` cada chunk. `close(fd)`. Exit. Bash hace `waitpid()` para recoger.

**Pregunta**: "Por qué printf es más lento que write directo"

**Respuesta**: printf hace formato (parsing del format string), buffering, locking. Si solo quieres dump de bytes, write() directo es más eficiente. Pero printf es seguro y ergonómico.

**Pregunta**: "Cómo debug un programa que se cuelga"

**Respuesta**: `strace -p PID` para ver qué syscall está bloqueando. Si está en `read()` de socket → esperando datos red. Si está en `futex_wait` → esperando lock (deadlock posible). Si está en `nanosleep` → durmiendo legítimo.

**Pregunta**: "Por qué usar epoll vs select"

**Respuesta**: select: O(N) por call, FD_SETSIZE limit (1024 default). epoll: O(1) por evento, escala a millones de fds. Linux only (kqueue es BSD/Mac).

### En embebido (perfil HW)

Embedded sin kernel "real" (FreeRTOS) NO tiene syscalls como Linux. Las "API calls" son funciones directas en el mismo espacio. Más rápido, menos seguro. Por eso un crash en task FreeRTOS puede tirar todo.

---

## 13. Trampas típicas

**"Todo lo de libc es syscall"**: no. Muchas funciones de libc son puro user-space (strcmp, memcpy). Solo las que necesitan recursos del SO hacen syscall.

**"Syscalls son siempre lentos"**: ~100ns cada uno. Para una función llamada millones de veces es mucho. Para una llamada ocasional es invisible. Optimizar lo medido, no lo asumido.

**"Cerrar fds es opcional"**: no. Tienes límite (`ulimit -n`). Olvidarlo causa "Too many open files" cuando tu app lleva tiempo corriendo.

**"stdout es lo mismo que printf"**: printf BUFFERIZA. Si tu programa crashea sin flush, los datos se pierden. Por eso a veces parece que "no imprimió nada antes de fallar". Soluciones: `setbuf(stdout, NULL)`, `python -u`, `PYTHONUNBUFFERED=1`.

**"strace no afecta al programa"**: sí lo hace. Cada syscall se intercepta → 10-100x más lento. No usar strace para profilear performance real.

**"El kernel ve mis variables"**: no. El kernel NO puede leer arbitrariamente memoria del proceso. Tu syscall pasa POINTERS y el kernel valida que sean accesibles via `copy_from_user()` / `copy_to_user()`. Sin esa validación, attacker podría leer kernel memory.

---

## 14. Preguntas típicas de interview

**"Qué es un syscall y por qué existen"** — frontera entre user space y kernel. Permite operaciones privilegiadas de forma controlada. Aislamiento + estabilidad.

**"Cómo funciona internamente un syscall"** — instrucción SYSCALL → trap → kernel mode → handler busca en tabla → ejecuta → SYSRET → user mode.

**"Por qué Linux es más rápido que Windows en syscalls"** — históricamente Linux tenía syscalls más ligeros y vDSO más agresivo. Tras Meltdown, la diferencia se redujo (KPTI). Hoy ambos son comparables.

**"Qué es un file descriptor"** — entero pequeño que identifica un recurso abierto del proceso. Unifica acceso a archivos, sockets, pipes, devices.

**"Diferencia entre syscall y context switch"** — syscall: transición user→kernel del MISMO proceso. Context switch: cambio entre PROCESOS distintos. Syscall puede causar context switch si bloquea.

**"Cómo prevenir Too many open files"** — cerrar fds (with statement Python). Aumentar `ulimit -n`. Connection pooling (reutilizar). Monitorear con `lsof`.

---

## 15. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- User space vs kernel space — por qué la separación.
- Qué es un syscall, ejemplos típicos.
- Cómo se ejecuta un syscall (trap → handler → return).
- Diferencia entre syscall y library function.
- File descriptors y por qué "todo es archivo".
- strace: para qué sirve y cómo usarlo.
- vDSO: el truco para syscalls baratos.
- eBPF: qué resuelve y por qué es importante moderno.

Si no puedes → relee.

---

## Conexiones

- [[01-procesos-y-threads]] — fork/exec/wait son syscalls
- [[02-memoria-virtual-paging]] — mmap/brk son syscalls
- [[03-scheduling]] — sched_yield es syscall
- [[05-filesystems]] — open/read/write son syscalls
- [[../01_networking/04-sockets-y-puertos]] — socket/bind/connect/accept son syscalls
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **The Linux Programming Interface** (Michael Kerrisk) — la biblia. ~1500 páginas, denso.
- **`man 2 nombre_syscall`** — documentación oficial cada syscall.
- **strace, ltrace, perf trace, bpftrace** — herramientas.
- **OSTEP** capítulos sobre syscalls y limited direct execution.
- **Brendan Gregg's blog** — eBPF, perf, observability.
- **`Linux Kernel Map`** (kernelmap.com) — visualizar qué hay en el kernel.
