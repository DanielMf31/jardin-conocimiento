# 05 — Filesystems

> **Doc 5 (último) del cluster Operating Systems**. Cómo el SO organiza datos persistentes en disco. Inodes, journaling, permissions, y por qué `cp archivo` es más complejo de lo que parece.
> **Frecuencia interview**: aparece menos directamente que networking/concurrency, pero crítico para system design (databases, storage).
> **Tiempo de lectura estimado**: 35-50 min.

---

## 1. Qué es un filesystem

Un **filesystem (FS)** es la capa del SO que organiza los bytes en disco como **archivos** y **directorios**. Sin él, el disco sería solo un array de bloques sin estructura.

**Responsabilidades**:
- Organizar bloques en archivos.
- Mantener metadatos (nombre, tamaño, permisos, timestamps).
- Estructurar la jerarquía de directorios.
- Garantizar consistencia ante crashes (journaling).
- Permissions y acceso multi-usuario.
- Performance (caching, prefetching, layout óptimo).

**Ejemplos por plataforma**:

| Plataforma | Filesystems |
|---|---|
| Linux | ext4, btrfs, xfs, zfs |
| macOS | APFS (antes HFS+) |
| Windows | NTFS, exFAT, FAT32 |

---

## 2. Bloques — la unidad fundamental

El disco es un array de **sectores** de tamaño fijo (típicamente 512 bytes en HDDs, 4096 bytes en SSDs modernos — "Advanced Format"). El filesystem agrupa esos sectores en **bloques** (típicamente 4 KiB), que son la unidad mínima de allocation.

**Consecuencias**: un archivo de 1 byte ocupa 4 KiB en disco (un bloque entero). El "block size" tiene un trade-off:

- **Bloque grande**: menos overhead de metadata, peor para archivos pequeños.
- **Bloque pequeño**: mejor uso de espacio, más overhead.

**Millones de archivos pequeños**: un repositorio Git con 100k archivos de 100 bytes cada uno tiene un espacio real de datos de 10 MB pero ocupa 400 MB en disco (cada archivo 1 bloque de 4 KiB). Por esto los packfiles de Git existen.

---

## 3. Inodes — el corazón de Unix filesystems

Un **inode (index node)** es la estructura que contiene **todos los metadatos** de un archivo **excepto el nombre**.

**Qué contiene un inode**:
- Tipo (regular, directory, symlink, device, ...).
- Permissions (rwxrwxrwx).
- Owner (UID), group (GID).
- Size en bytes.
- Timestamps: creation, modification, access.
- Reference count (cuántos hard links apuntan al archivo).
- **Punteros a los bloques** de datos del archivo.

**Qué NO contiene**: el nombre del archivo. El nombre vive en los **directorios**.

**Directorio**: es un tipo especial de "archivo" cuyo contenido es una tabla `nombre → inode_number`. Por ejemplo, `/home/usuario/` contiene entradas como `"Documentos" → inode 12345` y `"Imagenes" → inode 67890`.

**Lookup de `/home/usuario/Documentos/file.txt`**:
1. Abrir `/` (inode 2 típicamente).
2. Buscar `home` en su tabla → inode X.
3. Abrir X (es directorio), buscar `usuario` → inode Y.
4. Abrir Y, buscar `Documentos` → inode Z.
5. Abrir Z, buscar `file.txt` → inode W.
6. Abrir W, leer datos.

Cada nivel implica un lookup más una posible disk read si no está cacheado.

---

## 4. Hard links vs symbolic links

### Hard link

Otro nombre para el **mismo inode**. Ambos nombres apuntan al mismo archivo (mismo inode number). No hay "original" vs "copia": son iguales. Cuando borras uno, el otro sigue (refcount del inode > 0). Cuando refcount llega a 0, los bloques se liberan.

```bash
$ ln archivo1 archivo2
$ ls -i  # ambos tienen mismo inode number
```

**Limitaciones**:
- Solo funcionan dentro del **mismo filesystem**.
- No puedes hacer hard link de directorio (excepto `.` y `..`).

### Symbolic link (symlink, soft link)

Un archivo especial que **contiene un path** a otro archivo. No es el mismo inode. Si borras el original, el symlink queda "roto" (dangling).

```bash
$ ln -s /ruta/al/original alias
$ ls -l alias  # muestra "alias -> /ruta/al/original"
```

**Ventajas**:
- Cross-filesystem.
- Pueden apuntar a directorios.
- Visibles como links (transparente vs hard link).

### Uso típico

- **Hard link**: deduplicación de archivos idénticos (rsync).
- **Symlink**: aliases, alternatives (`/usr/bin/python → python3.12`).

---

## 5. File permissions — el modelo Unix clásico

El modelo Unix usa **9 bits por archivo + 3 especiales**:

```
rwxrwxrwx
↑↑↑↑↑↑↑↑↑
user|grp|others
```

Donde `r = read (4)`, `w = write (2)`, `x = execute / cd into (1)`.

**Notación octal**:

| Octal | Permisos |
|---|---|
| 755 | rwxr-xr-x |
| 644 | rw-r--r-- |
| 700 | rwx------ |

**chmod**:

```bash
$ chmod 755 archivo
$ chmod u+x archivo  # añade x al user
$ chmod -R 644 carpeta  # recursivo
```

**Owner + group**:

```bash
$ chown user:group archivo
$ chown -R alice:devs /home/alice/proyecto
```

**3 bits especiales**:

| Bit | Octal | Efecto |
|---|---|---|
| setuid | 4000 | Al ejecutar, el proceso corre con UID del owner del archivo. Ej: `/usr/bin/passwd` es setuid root para modificar `/etc/shadow` |
| setgid | 2000 | Igual pero con grupo |
| sticky | 1000 | En directorio, solo el owner puede borrar sus archivos (típico `/tmp`) |

**Umask**: máscara de bits que se **restan** al crear archivos nuevos. Default 022 → archivos nuevos son `666 - 022 = 644`. Para más privacy: `umask 077` → solo user puede leer.

**Más allá de Unix permissions**: ACLs (Access Control Lists) permiten reglas más finas (usuario X tiene rw, grupo Y solo r). En Linux: `setfacl`, `getfacl`. SELinux y AppArmor para mandatory access control.

---

## 6. Open file description vs file descriptor

La separación entre file descriptor y open file description es elegante:

- Cada **proceso** tiene una tabla de **file descriptors** (enteros 0, 1, 2, ...).
- Cada fd apunta a una **open file description** (entrada del kernel).
- Cada open file description contiene:
  - Inode al que apunta.
  - Posición actual (offset).
  - Modo (read, write, append).
  - Flags (non-blocking, etc.).

**Cada `open()` crea una nueva open file description**. Aunque sea el mismo archivo, dos `open()` diferentes tienen offsets independientes.

**`dup()` duplica fd**: el fd nuevo apunta a la **misma** open file description (mismo offset). Útil para redirección (`dup2` → stdout a archivo).

**Consecuencia**:
- Si dos procesos hacen `open()` del mismo archivo, tienen offsets independientes.
- Si proceso A hace `dup(fd_a) → fd_b`, ambos comparten offset.

---

## 7. Journaling — supervivencia ante crashes

**Problema sin journaling**: el filesystem está modificando metadatos cuando se va la luz. Resultado: inconsistencia (el inode dice "tiene 100 bytes" pero los bloques apuntados están vacíos o corruptos). Recovery: `fsck` escanea TODO el FS (horas para discos grandes).

**Con journaling**: antes de modificar el FS real, se escribe lo que se **va a hacer** en un "journal" (log secuencial al inicio del disco). Si hay crash, basta con replay del journal al reiniciar (segundos).

**Modos**:
- **Journal data (full)**: el journal incluye metadata + data. Más lento, más seguro.
- **Ordered (default ext4)**: journal solo metadata; los datos se escriben antes.
- **Writeback**: journal solo metadata, sin garantía de orden con data.

**Ventaja**: mount tras crash es rápido y FS consistente.

**Desventaja**: cada escritura es 2x (journal + lugar real). Algo más lento.

**Ejemplos**:
- **ext4**: journaling (default mode "ordered").
- **xfs**: journaling (más enfocado a metadata).
- **btrfs**: copy-on-write (no journaling tradicional, pero similares garantías).

---

## 8. Copy-on-write filesystems (btrfs, zfs, APFS)

En vez de journaling, usan **copy-on-write (CoW)**: cada modificación NUNCA sobreescribe en sitio. Escribe nueva copia y actualiza el puntero a la nueva copia.

**Propiedades**:
- Snapshots gratis (mantén el puntero antiguo).
- Clones rápidos (no copia datos, solo metadatos).
- Atomicidad nativa (escribe completa o no escribe).
- Sin necesidad de fsck (estructura siempre consistente).

**Desventajas**:
- Más fragmentación con el tiempo.
- Más complejo (más bugs históricos).
- Más uso de espacio si hay snapshots largos.

**Ejemplos**:
- **btrfs** (Linux, default Fedora workstation).
- **zfs** (FreeBSD, Solaris, opcional Linux). Production-grade.
- **APFS** (macOS desde 2017).

**Uso típico**:
- Backups (snapshots periódicos).
- VMs (clones rápidos).
- DBs que aprovechan transacciones nativas.

---

## 9. fsync, fdatasync, write() — durabilidad real

`write()` **no garantiza** que los datos lleguen al disco. Solo los pone en el page cache del kernel. El kernel los flusha a disco "cuando le venga bien" (background).

**Consecuencia**: tu programa puede llamar a `write()` y "todo bien", pero si la luz se va antes del flush, los datos se **pierden**.

**Para garantizar persistencia**:

| Syscall | Qué garantiza |
|---|---|
| `fsync(fd)` | Flush datos + metadata del archivo a disco |
| `fdatasync(fd)` | Solo datos (sin metadata como timestamps) |
| `sync()` | Flush TODO. Lento |

**Casos que lo requieren**:
- Bases de datos (Postgres llama a fsync constantemente).
- Editor de texto al guardar (Word, vim).
- Sistemas que prometen "tu transacción se completó".

**Casos que no**:
- Tu app vuelca bytes al log de debug. Acepta perder los últimos KBs.
- Caches (no importa perderlos).

**Performance**: fsync es **caro** — ~ms en SSDs, decenas de ms en HDDs. Si llamas fsync por cada `write()`, el throughput cae brutalmente. Estrategia: **batchear** (write N cosas, fsync una vez).

**En Python**: `os.fsync(fd)` explícito. `open()` con `buffering=1` fuerza line-buffered (no fsync, solo flush libc).

---

## 10. Tipos de filesystems modernos

### Disk filesystems (datos en disco)

| FS | Notas |
|---|---|
| ext4 | Default Linux desktop/server. Maduro, estable |
| xfs | Mejor para archivos grandes, paralelismo (RHEL default) |
| btrfs | CoW, snapshots, RAID built-in. Aún tiene caveats |
| zfs | Enterprise-grade, integridad fuerte. Linux licensing tricky |
| ntfs | Windows |
| apfs | macOS moderno |
| exfat | Cross-platform USB sticks (sin journaling) |
| fat32 | Legacy, 4 GB max file |

### Memory filesystems (datos en RAM)

- **tmpfs**: `/tmp` en muchos Linux (swap-backed). Súper rápido. Se pierde al reiniciar.
- **ramfs**: puro RAM, sin límite (puede colgar si llenas RAM).

### Network filesystems

- **nfs**: Network FS estándar Unix.
- **smb/cifs**: Network FS de Windows / Samba.
- **sshfs**: mount via SSH (lento pero seguro).
- **s3fs / goofys**: mount S3 buckets (con limitaciones).

### Special / pseudo filesystems

- **procfs (`/proc`)**: expone info del kernel y procesos como archivos.
- **sysfs (`/sys`)**: info sobre dispositivos.
- **devtmpfs (`/dev`)**: device files.
- **cgroup2**: control groups.

### FUSE (Filesystem in USERSPACE)

Permite escribir filesystems en user space. Ejemplos: sshfs, encfs, gocryptfs, ntfs-3g. Más fácil que kernel module, pero más lento.

---

## 11. Page cache — por qué tu segundo `cat` es instantáneo

**Page cache**: cuando lees un archivo, el kernel cachea los bloques en RAM. La próxima lectura es un cache hit y no toca disco.

**Efecto visible**:

```bash
$ time cat /var/log/syslog > /dev/null
real  0m0.500s   ← primera vez, lee de disco

$ time cat /var/log/syslog > /dev/null
real  0m0.020s   ← segunda vez, lee de RAM cache
```

**Write behind**: `write()` pone datos en cache. El kernel los flusha a disco después. Por eso `write()` es muy rápido (no espera disco).

**El cache es todo lo que no está en uso**: Linux usa "free RAM" como page cache. Por eso `free -h` muestra "available" alto aunque "used" sea alto. Si tu app pide RAM, el kernel libera cache automáticamente.

**Control**:

```bash
echo 3 > /proc/sys/vm/drop_caches   # forzar liberar cache (debug)
```

- `posix_fadvise()` → hint al kernel sobre patrones de acceso.
- `O_DIRECT` en `open()` → bypass page cache (DBs lo usan a veces).

---

## 12. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

- `data/contacts.json` se lee/escribe vía syscalls open/read/write/close.
- Volume bind mount Docker (`./data:/app/data`) hace que el archivo viva en tu host pero el container lo ve.
- Sin `os.fsync(fd)` después de `json.dump()`, si el container se mata abruptamente, los últimos cambios pueden perderse (page cache no flusheada). Para tu use case OK. Para DBs no.

### En entrevistas tecnicas

**Pregunta**: "Diferencia entre hard link y symlink".
- Hard link: otro nombre del mismo inode (mismo FS).
- Symlink: archivo que contiene el path a otro (cross-FS).

**Pregunta**: "Por qué `rm -rf /` es tan peligroso".
- Borra recursivamente. Los inodes se desreferencian (refcount 0 → bloques liberados). Después, el filesystem no tiene metadatos para recuperar. Algunas distros añaden flag `--preserve-root` como protección.

**Pregunta**: "Por qué tu DB es tan rápida en escrituras".
- Page cache: writes van a RAM, flush async.
- WAL (Write-Ahead Log): journaling propio de la DB encima del FS.
- Group commit: agrupar fsync de varias transacciones.

**Pregunta**: "Qué pasa cuando llamas `write()` y luego se va la luz".
- Datos pueden estar en page cache (no en disco). Se pierden.
- `fsync()` los fuerza a disco. Caro pero garantía real.

### Para embebido (perfil HW)

Embedded suele NO tener filesystem (graba directo a flash). Si usa SD card, tiene FAT32 (limitado, sin journaling — corruptible). Mejor para embedded: F2FS, ext4, o filesystems específicos para flash (JFFS2, YAFFS).

---

## 13. Trampas típicas

**Trampa 1 — "rm libera espacio inmediatamente"**: casi siempre sí, pero si el archivo está abierto por otro proceso, los bloques NO se liberan hasta que ese proceso lo cierre. Por eso `df` puede mostrar disco lleno aunque acabes de borrar archivos grandes (algún proceso los tiene abiertos).

**Trampa 2 — "Capacidad usada en `du` = capacidad usada en `df`"**: no exacto. `du` suma archivos que ves, `df` cuenta bloques realmente. Diferencias por:
- Archivos abiertos pero borrados (df cuenta, du no).
- Hard links (du puede contar 2 veces si usas `-L`).
- Filesystem overhead (inodes, journals).

**Trampa 3 — "JSON/binary file en disco siempre actualiza atómico"**: NO. `open(file, "w")` + `write()` puede dejar el archivo a medio escribir si crashea. Patrón seguro:
1. Escribir a tempfile.
2. `fsync(tempfile)`.
3. `rename(tempfile, original)` ← rename es atómico en mismo FS.

**Trampa 4 — "Permisos del archivo siempre son los del owner"**: no con setuid, ACLs, SELinux contexts. En Docker, el UID dentro del container puede ser distinto del host (pero archivos en volume bind mount comparten UID numérico).

**Trampa 5 — "Filesystem full = no puedo escribir"**: aunque haya espacio, puedes quedarte sin **inodes** (cada archivo necesita uno). Si tienes millones de archivos pequeños → posible "No space left on device" por inodes, no por bytes.

```bash
$ df -i  # muestra inode usage
```

**Trampa 6 — "tmpfs es más rápido que SSD"**: sí. tmpfs vive en RAM. Pero se pierde al reiniciar. Útil para archivos temporales (compilación, caches).

---

## 14. Preguntas típicas de interview

**Pregunta 1 — "Qué es un inode"**: estructura con metadatos del archivo (excepto nombre) y punteros a sus bloques de datos. Núcleo de los Unix filesystems.

**Pregunta 2 — "Diferencia entre hard link y symlink"**: ya cubierto en sección 4.

**Pregunta 3 — "Cómo funciona el page cache"**: el kernel cachea bloques leídos en RAM. Próximas lecturas son cache hits. Writes van primero a cache (write-behind). `fsync` fuerza flush.

**Pregunta 4 — "Por qué fsync es importante para DBs"**: garantiza durabilidad. Sin fsync, después de `write()` se puede perder ante crash. Las DBs llaman a fsync para garantizar ACID.

**Pregunta 5 — "Cómo prevenir corrupción de archivos al escribir"**: atomic rename pattern — write tempfile + fsync + rename. Rename es atómico en mismo filesystem.

**Pregunta 6 — "Qué es journaling y por qué importa"**: log secuencial de cambios pendientes antes de aplicarlos. Permite recovery rápido tras crash. Trade-off: writes 2x.

---

## 15. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Filesystem: qué problema resuelve.
- Bloques y por qué archivos pequeños desperdician espacio.
- Inode: qué contiene y qué no (no el nombre).
- Hard link vs symlink: diferencias y casos de uso.
- Permisos Unix: rwxrwxrwx, octal, chmod.
- Page cache: por qué el segundo `cat` es instantáneo.
- fsync: cuándo es necesario, cuándo es caro.
- Journaling: qué resuelve.
- Atomic write pattern (tempfile + rename).
- tmpfs: qué es y cuándo usarlo.

Si no puedes → relee.

---

## ¡Cluster Operating Systems completado!

Has completado el segundo Tier 1. Resumen de lo dominado:

| Doc | Contenido |
|---|---|
| 01-procesos-y-threads | procesos, threads, fork/exec, GIL, signals |
| 02-memoria-virtual-paging | virtual memory, paging, TLB, page faults, mmap |
| 03-scheduling | schedulers, CFS, nice, real-time, affinity |
| 04-syscalls-y-kernel | user/kernel space, syscalls, fds, strace, vDSO |
| 05-filesystems | inodes, journaling, page cache, fsync |

**Próximo cluster**: `03_concurrency/` — race conditions, locks, deadlocks, async vs threads vs procesos.

---

## Conexiones

- [[01-procesos-y-threads]] — procesos manejan archivos via fds
- [[02-memoria-virtual-paging]] — page cache es parte de virtual memory system
- [[04-syscalls-y-kernel]] — open/read/write/fsync son syscalls
- [[../05_database_internals/02-acid-transactions]] — DBs construyen ACID encima de FS
- [[../05_database_internals/01-b-trees-y-indexing]] — DB indexes en disco
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]

## Recursos externos

- **OSTEP** capítulos 39-43 (Persistencia, FS). GRATIS.
- **The Linux Programming Interface** capítulos sobre archivos.
- **`man inode`, `man 7 path_resolution`, `man 2 open`** — referencias.
- **`du`, `df`, `ls -li`, `stat`, `lsof`, `ncdu`** — herramientas inspección.
- **`Designing Data-Intensive Applications`** capítulo 3 (Storage and Retrieval) — FS desde óptica DB.
