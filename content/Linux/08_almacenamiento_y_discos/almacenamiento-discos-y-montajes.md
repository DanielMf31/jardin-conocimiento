---
title: Almacenamiento, discos y montajes en Linux
date: 2026-06-12
tags: [programacion/linux, programacion/linux/storage, programacion/linux/filesystem]
type: nota
status: permanente
source: claude-code
aliases: [discos linux, montajes linux, almacenamiento linux, fstab, lsblk, particiones linux]
---

# Almacenamiento, discos y montajes en Linux

## La cadena mental fundamental

Antes de tocar ningún comando, interioriza esta cadena. Cada eslabón depende del anterior:

```
Dispositivo de bloques  →  Partición  →  Sistema de ficheros  →  Punto de montaje
   /dev/nvme0n1              p8             ext4                      /
   (el disco físico)      (trozo del disco) (cómo se organiza         (dónde lo ves en el árbol)
                                             dentro de ese trozo)
```

**Dispositivo de bloques**: el kernel expone cada disco como un fichero en `/dev/`. Es solo una interfaz de lectura/escritura cruda — ni siquiera sabe qué hay dentro.

**Partición**: división lógica del disco. El disco tiene una tabla de particiones (GPT en sistemas modernos o MBR en legado) que dice "del sector X al sector Y existe la partición 3".

**Sistema de ficheros**: estructura que se escribe *dentro* de una partición para organizar datos en ficheros, directorios, permisos, fechas. Sin formatear, una partición es bytes vacíos.

**Punto de montaje**: directorio del árbol VFS de Linux donde se "engancha" ese sistema de ficheros. A partir de ese momento, acceder a `/` o `/home` es acceder al disco subyacente.

> Regla de oro: en Linux **todo es un fichero** y **todo está en un árbol único**. No hay `C:\` ni `D:\`. Los discos se integran en ramas del árbol.

---

## Tu disco real: NVMe 953 GB

Tu máquina tiene un solo disco físico NVMe. Así lo ve Linux:

```
nvme0n1       953,9G   ← disco completo
├─nvme0n1p1    100M    vfat     /boot/efi     ← ESP: arranque UEFI (compartido Windows/Ubuntu)
├─nvme0n1p2     16M    (sin fs) ---           ← MSR de Windows (reservado, no tocar)
├─nvme0n1p3    500G    ntfs     ---           ← Windows C:\ (desde Ubuntu se ve pero no se monta por defecto)
├─nvme0n1p4      1M    ext4     ---           ← partición pequeña (posible GRUB legacy o Ubuntu anterior)
├─nvme0n1p5    449M    ext4     ---           ← /boot de Ubuntu (kernel e initramfs)
├─nvme0n1p6    553M    ntfs     ---           ← partición Windows auxiliar (Recuperación o datos)
├─nvme0n1p7    7,6G    swap     [SWAP]        ← área de intercambio (RAM virtual)
└─nvme0n1p8  445,2G   ext4     /             ← sistema raíz de Ubuntu (donde vives)
```

### Nomenclatura NVMe vs SATA

| Tipo de disco | Ejemplo dispositivo | Ejemplo partición 3 |
|---|---|---|
| NVMe (PCIe) | `/dev/nvme0n1` | `/dev/nvme0n1p3` |
| SATA / USB (antiguo) | `/dev/sda` | `/dev/sda3` |
| Segundo disco SATA | `/dev/sdb` | `/dev/sdb1` |

`nvme0` = primer controlador NVMe; `n1` = primer namespace (casi siempre hay solo uno). Las particiones usan `p` antes del número: `p1`, `p2`… En SATA el número va directo: `sda1`, `sda2`…

---

## Ver discos y particiones (solo lectura)

### `lsblk` — árbol de dispositivos de bloques

```bash
lsblk                              # vista básica: nombre, tamaño, tipo, mountpoint
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,LABEL   # columnas adicionales
lsblk -f                           # añade UUID y sistema de ficheros
```

`lsblk` lee `/sys/block/` — es instantáneo y no necesita root.

### `fdisk -l` — tabla de particiones (requiere sudo)

```bash
sudo fdisk -l /dev/nvme0n1
```

Muestra el tipo de tabla (GPT/MBR), tamaños exactos en sectores y el tipo de cada partición. Útil para ver flags como `EFI System` o `Linux swap`.

> `fdisk` en modo `-l` es **solo lectura**. El peligro está en entrar al modo interactivo sin `-l`. Si alguna vez lo haces sin querer, escribe `q` + Enter para salir sin guardar.

### `blkid` — UUID y tipos de sistema de ficheros

```bash
sudo blkid
sudo blkid /dev/nvme0n1p8
```

Ejemplo de salida:
```
/dev/nvme0n1p8: UUID="a1b2c3d4-..." TYPE="ext4" PARTUUID="..."
```

El UUID es un identificador único e inmutable del sistema de ficheros. Fundamental para `/etc/fstab`.

---

## Sistemas de ficheros: qué existe y para qué

| FS | Uso principal | Notas |
|---|---|---|
| **ext4** | Sistema raíz y /home en Ubuntu | Journaling, maduro, rápido en HDD/SSD. Tu `/` es ext4. |
| **btrfs** | Alternativa moderna en Fedora/openSUSE | Copy-on-write, snapshots nativos, RAID por software. Más complejo. |
| **ntfs** | Disco de Windows | Ubuntu puede leer/escribir via `ntfs-3g`. Evita modificar la partición de Windows en arranque rápido activo. |
| **vfat / FAT32** | `/boot/efi`, pendrives | Sin permisos Unix. Compatibilidad universal. Tu `nvme0n1p1` es vfat. |
| **squashfs** | Snaps de Ubuntu | Solo lectura, comprimido. Los `loopX` que ves en `lsblk` son snaps montados. |
| **swap** | Área de intercambio | No es un FS navegable. Extensión de RAM en disco. |
| **tmpfs** | `/tmp`, `/run` | Solo en RAM, se borra al reiniciar. Rapidísimo. |

### ext4 en detalle (tu FS del día a día)

- **Journaling**: antes de escribir datos, anota la operación en un diario. Si la máquina se apaga a mitad, al reiniciar puede revertir operaciones incompletas. Evita corrupción.
- **Inodos**: cada fichero/directorio tiene un inodo con metadatos (permisos, propietario, fechas, punteros a bloques). El contenido y los metadatos están separados.
- **Límites prácticos**: ficheros hasta 16 TiB, volumen hasta 1 EiB.

---

## Montar y desmontar

### El concepto de montaje

"Montar" es pedirle al kernel que tome un sistema de ficheros y lo enganche en un directorio existente (el punto de montaje). A partir de ese momento, todo lo que escribas en ese directorio va al disco subyacente.

```bash
# Ver qué está montado ahora mismo
mount | grep -v loop       # filtramos los loops de snap para no saturar
findmnt                    # árbol más legible
findmnt /dev/nvme0n1p8     # info de una partición concreta
```

### Dónde se montan las cosas

| Directorio | Uso convencional |
|---|---|
| `/mnt/` | Montajes temporales manuales por el administrador |
| `/media/<usuario>/` | Automontaje de USBs, DVDs, discos externos (lo hace `udisks2`/GNOME) |
| `/` | El sistema raíz (siempre montado desde el arranque) |

### Automontaje de USBs en Ubuntu Desktop

Ubuntu usa `udisks2` + `udev`: cuando conectas un USB, el sistema lo detecta, lo monta automáticamente en `/media/usuario/<label>/` y aparece en el gestor de ficheros. No necesitas hacer nada manual.

Para ver los montajes activos de un USB recién conectado:

```bash
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT,LABEL
```

### Montar/desmontar manualmente (cuando necesitas)

```bash
# Montar un pendrive que no se automontó
sudo mount /dev/sdb1 /mnt/pendrive

# Desmontar (el dispositivo debe estar libre, sin procesos usando ficheros de ahí)
sudo umount /mnt/pendrive
# o por punto de montaje
sudo umount /media/usuario/NOMBRE

# Si umount dice "device is busy":
lsof +D /mnt/pendrive      # qué proceso tiene ficheros abiertos ahí
# o simplemente cierra la terminal que tenía el directorio como cwd
```

> **Nunca desconectes un USB sin desmontar antes** en sistemas con escrituras pendientes. En escritura frecuente puedes perder datos o corromper el FS.

---

## `/etc/fstab`: el mapa de montajes permanentes

`/etc/fstab` le dice al sistema qué montar automáticamente al arrancar.

```bash
cat /etc/fstab
```

### Formato de cada línea

```
<dispositivo>   <punto-montaje>   <tipo-fs>   <opciones>   <dump>   <pass>
```

Ejemplo real de tu sistema (aproximado):

```
UUID=a1b2c3d4-xxxx  /          ext4    errors=remount-ro   0   1
UUID=b2c3d4e5-xxxx  /boot/efi  vfat    umask=0077          0   1
UUID=c3d4e5f6-xxxx  none       swap    sw                  0   0
```

| Campo | Qué significa |
|---|---|
| `UUID=...` | Identificador único del FS (más seguro que `/dev/sdaX` que puede cambiar) |
| Punto de montaje | Donde se enganchará; `/` para la raíz, `none` para swap |
| Tipo FS | `ext4`, `vfat`, `swap`, `ntfs`, `auto`… |
| Opciones | `defaults`, `ro` (solo lectura), `noexec`, `errors=remount-ro`… |
| dump | 0 = no usar `dump` para backups (obsoleto, siempre 0) |
| pass | Orden de `fsck` al arrancar: 1 = raíz (primero), 2 = resto, 0 = no verificar |

### Riesgo crítico: no edites fstab sin saber lo que haces

Un error en `/etc/fstab` puede impedir que el sistema arranque. Si necesitas editarlo:

1. Haz una copia antes: `sudo cp /etc/fstab /etc/fstab.bak`
2. Verifica la sintaxis sin reiniciar: `sudo mount -a` (monta todo lo que esté en fstab pero no montado aún)
3. Si algo falla, tendrás una sesión de emergencia con acceso root para revertir.

---

## Espacio en disco

### `df -h` — espacio libre por sistema de ficheros montado

```bash
df -h                    # todos los FS montados (en formato legible)
df -h /                  # solo la raíz
df -h --type=ext4        # solo FS ext4
```

Salida típica:
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p8  438G   45G  371G  11% /
tmpfs           7,7G  2,1M  7,7G   1% /run
/dev/nvme0n1p1   96M   36M   60M  38% /boot/efi
```

> Los `tmpfs` y los `loop` (snaps) aparecen también. Filtra con `df -h --type=ext4` para ver solo el disco real.

### `du` — espacio ocupado por directorio o fichero

```bash
du -sh /home/usuario          # tamaño total de tu home
du -sh /var/log                  # cuánto ocupan los logs
du -sh /*  2>/dev/null           # tamaño de cada directorio raíz (ignora errores de permisos)
du -xh --max-depth=1 /home/usuario  # subdirectorios de primer nivel, sin cruzar particiones
```

`-x` es importante: limita `du` al mismo sistema de ficheros, evitando que "entre" en montajes externos.

### `ncdu` — navegador interactivo de espacio (muy recomendado)

```bash
# Instalar si no está:
sudo apt install ncdu

# Analizar tu home:
ncdu /home/usuario

# Analizar todo el sistema sin cruzar particiones:
sudo ncdu -x /
```

`ncdu` escanea recursivamente y te da una interfaz TUI donde puedes navegar con flechas y ver qué carpetas/ficheros "engordan" el disco. Ideal para limpiar antes de que el disco se llene.

---

## Swap: RAM virtual en disco

El swap es un área del disco que el kernel usa como extensión de RAM cuando la RAM física se llena. Tu sistema tiene `nvme0n1p7` de 7,6 GB dedicada a swap (también puede ser un swapfile en lugar de partición).

```bash
# Ver el estado del swap:
free -h
swapon --show

# Ver cuánto swap se está usando en tiempo real:
vmstat 1 5            # columnas si, so = swap in / swap out
```

**Swappiness**: parámetro del kernel (0-100) que controla el "entusiasmo" para mandar páginas a swap antes de que la RAM se llene. Ubuntu por defecto: 60. En SSD NVMe con abundante RAM puedes bajarlo:

```bash
cat /proc/sys/vm/swappiness    # ver valor actual
```

> Swap en NVMe es rápido comparado con HDD, pero sigue siendo órdenes de magnitud más lento que RAM. Si el sistema está swapeando constantemente, necesitas más RAM o menos procesos.

---

## Aplicación práctica: Timeshift y snapshots

`ext4` no tiene snapshots nativos, pero **Timeshift** crea backups incrementales del sistema raíz usando `rsync` (o `btrfs` si tu FS fuera btrfs).

```bash
# Ver si Timeshift está instalado:
which timeshift

# Listar snapshots existentes (no los crea, solo los lista):
sudo timeshift --list
```

Los snapshots de Timeshift se guardan en una partición ext4 (normalmente en la partición del sistema). Permiten restaurar el sistema completo si una actualización o cambio de configuración rompe algo. Es el equivalente a los "puntos de restauración" de Windows pero más robusto.

---

## Gotchas y errores comunes

| Situación | Causa probable | Solución |
|---|---|---|
| `df` no muestra el pendrive | No montado | `lsblk` para ver si está reconocido, montar manualmente o via gestor de ficheros |
| `umount: device is busy` | Proceso o terminal con CWD dentro del montaje | `lsof +D /mnt/X` o cambiar de directorio antes de desmontar |
| `du` tarda mucho o da cifras raras | Entra en otros FS montados | Usar `-x` para limitar al FS actual |
| Disco ntfs de Windows no montable | Windows en "arranque rápido" (hibernación parcial) | Desde Windows: desactivar arranque rápido (`powercfg /h off`) y reiniciar correctamente |
| `lsblk` muestra 40+ líneas de loops | Snaps de Ubuntu | Filtrar: `lsblk -e7` (excluye loop devices tipo 7) |
| Sistema no arranca tras editar fstab | Error de sintaxis o UUID incorrecto | Arrancar en modo recovery, montar `/` en ro y restaurar fstab.bak |

```bash
# Truco: lsblk sin loops
lsblk -e 7 -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,LABEL
```

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|Índice de Linux]]
- [[filesystem-fhs-y-navegacion]]
