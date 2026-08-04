---
title: Filesystem, FHS y Navegación en Linux
date: 2026-06-12
tags: [programacion/linux, programacion/linux/filesystem, programacion/linux/navegacion]
type: nota
status: permanente
source: claude-code
aliases: [FHS Linux, árbol de directorios Linux, navegación Linux, filesystem Linux]
---

# Filesystem, FHS y Navegación en Linux

## Modelo mental: un solo árbol, sin letras de unidad

En Windows cada disco tiene una letra (`C:\`, `D:\`). En Linux existe **un único árbol** con raíz `/`. Los discos, USBs y particiones se *montan* como ramas de ese árbol — no crean nuevas raíces.

```
/
├── etc/         ← configuración del sistema
├── home/
│   └── usuario/   ← tu espacio personal
├── usr/
│   ├── bin/     ← programas de usuario
│   └── lib/
├── var/         ← datos variables (logs, bases de datos)
├── tmp/         ← temporales (se borra al reiniciar)
├── dev/         ← dispositivos como archivos
├── proc/        ← estado del kernel (virtual, en RAM)
└── ...
```

> Gotcha: la barra `/` es tanto el separador de ruta **como** el directorio raíz. `/etc` = el directorio `etc` dentro de la raíz `/`.

---

## FHS — Filesystem Hierarchy Standard

El FHS define qué va en cada directorio. No es arbitrario; respetar la jerarquía permite que cualquier herramienta sepa dónde buscar.

| Directorio | Propósito | Ejemplos reales |
|---|---|---|
| `/` | Raíz del árbol. Todo cuelga de aquí. | — |
| `/bin` → `/usr/bin` | Binarios esenciales de usuario | `ls`, `cat`, `bash`, `python3` |
| `/sbin` → `/usr/sbin` | Binarios de administración (sistema) | `fdisk`, `ip`, `useradd` |
| `/usr` | Recursos de usuario de solo lectura | subdirs: `bin/`, `lib/`, `share/`, `local/` |
| `/usr/local` | Software instalado **a mano** (fuera de apt) | binarios propios, compilaciones locales |
| `/etc` | Configuración del sistema (texto plano) | `apt/sources.list`, `fstab`, `hostname`, `ssh/sshd_config` |
| `/home` | Directorios personales de cada usuario | `/home/usuario/` |
| `/root` | Home del usuario `root` (separado de `/home`) | — |
| `/var` | Datos variables: logs, colas, bases de datos | `/var/log/syslog`, `/var/lib/apt/`, `/var/cache/` |
| `/tmp` | Archivos temporales; se vacía al reiniciar | ficheros de sesión, locks |
| `/dev` | Dispositivos representados como archivos | `/dev/sda` (disco), `/dev/null`, `/dev/tty` |
| `/proc` | Sistema de archivos virtual — estado del kernel y procesos | `/proc/cpuinfo`, `/proc/meminfo`, `/proc/1234/` |
| `/sys` | Interfaz al kernel para hardware y drivers | nodos de dispositivo, parámetros del kernel |
| `/mnt` | Punto de montaje manual temporal | `sudo mount /dev/sdb1 /mnt` |
| `/media` | Montajes automáticos (USB, CD) | `/media/usuario/MiUSB/` |
| `/opt` | Software de terceros autocontenido | `/opt/google/chrome/`, `/opt/vscode/` |
| `/lib` → `/usr/lib` | Bibliotecas compartidas (.so) del sistema | — |
| `/boot` | Kernel, initrd, GRUB | `vmlinuz-*`, `initrd.img-*`, `grub/` |
| `/snap` | Paquetes snap montados en loopback | solo en Ubuntu con snapd |

> `/bin`, `/sbin`, `/lib` son hoy **symlinks** a sus equivalentes en `/usr/` en Ubuntu 24.04 (consolidación desde Debian Bookworm). El comportamiento visible es idéntico.

### Por qué importa

- Quieres instalar un script tuyo sin apt → `/usr/local/bin/` (en tu `PATH`, no pisas paquetes).
- Buscas la config de un servicio → siempre en `/etc/<nombre>/`.
- Los logs de un servicio que falla → `/var/log/<nombre>/` o `journalctl`.

---

## Rutas: absolutas vs relativas

| Tipo | Empieza con | Ejemplo |
|---|---|---|
| **Absoluta** | `/` | `/home/usuario/Documentos/notas.md` |
| **Relativa** | nombre o `.` `..` | `Documentos/notas.md` (desde tu home) |

### Atajos de ruta imprescindibles

| Símbolo | Significa | Ejemplo de uso |
|---|---|---|
| `.` | Directorio actual | `./script.sh` — ejecutar script aquí |
| `..` | Directorio padre | `cd ../otro-proyecto` |
| `~` | Home del usuario actual | `cd ~/Documentos` ≡ `cd /home/usuario/Documentos` |
| `-` | Directorio anterior (para `cd`) | `cd -` — volver al dir anterior |
| `~usuario` | Home de otro usuario | `~root` = `/root` |

---

## Comandos de navegación

### `pwd` — dónde estás

```bash
$ pwd
/home/usuario/Documentos/Proyectos_personales
```

### `cd` — cambiar de directorio

```bash
cd /etc                  # absoluta
cd Documentos            # relativa (desde tu posición actual)
cd ..                    # sube un nivel
cd ../..                 # sube dos niveles
cd ~                     # va a tu home
cd -                     # alterna con el directorio anterior
```

> Gotcha: `cd` sin argumentos también va a `~`. Útil cuando te pierdes.

### `ls` — listar contenido

```bash
ls                       # listado básico
ls -l                    # formato largo (permisos, dueño, tamaño, fecha)
ls -la                   # incluye ocultos (empiezan con .)
ls -lh                   # tamaños legibles (K, M, G)
ls -lt                   # ordena por fecha de modificación, más reciente primero
ls -ltr                  # ídem pero más antiguo primero (útil para logs)
ls -R                    # recursivo (muestra subdirectorios)
ls -d */                 # solo directorios del nivel actual
ls /etc/*.conf           # acepta globbing (ver más abajo)
```

#### Anatomía de `ls -l`

```
$ ls -lh /etc/ | head -5
total 1,5M
-rw-r--r--  1 root root  3,4K jul  5  2023 adduser.conf
drwxr-xr-x  9 root root   12K jun 12 15:35 apparmor.d
-rw-r--r--  1 root root 2,3K mar 31  2024 bash.bashrc
drwxr-xr-x  9 root root  4,0K dic 28 19:51 apt
```

```
[tipo+permisos]  [enlaces]  [dueño]  [grupo]  [tamaño]  [fecha]  [nombre]
drwxr-xr-x         9        root      root      4,0K    dic 28   apt
│└────────┘
│ rwx = dueño puede leer/escribir/ejecutar
│  r-x = grupo puede leer/ejecutar
│   r-x = otros pueden leer/ejecutar
└── d = directorio  (- = archivo regular, l = symlink, c = char device, b = block device)
```

### `tree` — vista de árbol

No viene instalado por defecto; instalar con `sudo apt install tree`.

```bash
tree                     # árbol desde el directorio actual
tree -L 2                # máximo 2 niveles de profundidad
tree -a                  # incluye ocultos
tree -d                  # solo directorios
tree /etc -L 1           # árbol de /etc, un nivel
```

---

## Globbing (comodines del shell)

El shell **expande** los comodines antes de pasarlos al comando. No es regex.

| Patrón | Significado | Ejemplo |
|---|---|---|
| `*` | Cualquier cadena (incluido vacío) | `ls *.md` — todos los .md |
| `?` | Exactamente un carácter | `ls nota?.md` — `nota1.md`, `notaA.md`… |
| `[abc]` | Un carácter de la lista | `ls archivo[123].txt` |
| `[a-z]` | Un carácter del rango | `ls [a-z]*.sh` |
| `[!abc]` | Un carácter que NO está en la lista | `ls [!0-9]*` — no empieza por dígito |
| `{a,b,c}` | Expansión de llaves (literal, no glob) | `mkdir {src,tests,docs}` |
| `**` | Recursivo (requiere `shopt -s globstar`) | `ls **/*.py` — todos los .py en subdirs |

```bash
# Ejemplos prácticos
ls /etc/*.conf           # todos los .conf en /etc
ls /var/log/apt/         # ver logs de apt
cp notas_{v1,v2}.md bak/ # copia notas_v1.md y notas_v2.md
mv informe_202[45]*.pdf archivos/   # mueve informes de 2024 y 2025
```

> Gotcha: si el patrón no coincide con nada, Bash devuelve el patrón literal (no error). Usa `shopt -s nullglob` para obtener lista vacía en vez del patrón.

---

## Autocompletado con Tab

| Acción | Resultado |
|---|---|
| `Tab` una vez | Completa si hay una sola opción |
| `Tab` dos veces | Muestra todas las opciones posibles |
| `Tab` en mitad de ruta | Completa directorios y archivos |
| `Tab` tras comando | Completa subcomandos (en muchos programas) |

Funciona para: comandos, rutas, variables de entorno (`$HO` + Tab → `$HOME`), y flags en programas que lo soporten.

---

## Inspeccionar archivos: `file` y `stat`

### `file` — tipo real del archivo (no se fía de la extensión)

```bash
$ file CLAUDE.md /bin/ls /dev/null
CLAUDE.md: Unicode text, UTF-8 text
/bin/ls:   ELF 64-bit LSB pie executable, x86-64, dynamically linked, stripped
/dev/null: character special (1/3)
```

Útil cuando un archivo "no abre" — puede tener la extensión equivocada o ser binario.

### `stat` — metadatos completos (inode, permisos, tiempos)

```bash
$ stat CLAUDE.md
  Fichero: CLAUDE.md
  Tamaño: 7481        Bloques: 16    Bloque E/S: 4096   fichero regular
Device: 259,8  Inode: 2654196  Links: 1
Acceso: (0664/-rw-rw-r--)  Uid: (1000/usuario)  Gid: (1000/usuario)
Acceso:       2026-06-12 14:20:57
Modificación: 2026-04-26 21:14:27   ← último cambio de contenido (mtime)
Cambio:       2026-04-26 21:14:27   ← último cambio de metadatos (ctime)
Creación:     2026-04-26 21:14:27   ← birthtime (no siempre disponible)
```

Tres tiempos distintos:
- **atime** — último acceso (lectura). A menudo desactivado para rendimiento (`noatime` en `/etc/fstab`).
- **mtime** — última modificación del contenido. Es el que usa `ls -lt`.
- **ctime** — último cambio de metadatos (permisos, dueño, nombre). No es "creation time".

---

## Inodos y enlaces (concepto breve)

Cada archivo tiene un **inode**: una entrada en la tabla del sistema de archivos que guarda metadatos + punteros a los bloques de datos. El nombre del archivo es solo una etiqueta que apunta al inode.

```
nombre_archivo → inode → bloques de datos en disco
```

Tipos de enlace:

| Tipo | Comando | Comparte inode | Cruza FS | Si se borra el original |
|---|---|---|---|---|
| **Hard link** | `ln original alias` | Sí | No | El alias sigue funcionando |
| **Symlink** (soft) | `ln -s original alias` | No | Sí | El alias queda roto |

```bash
ln -s /ruta/original /ruta/alias   # symlink típico (como acceso directo)
ls -l alias                        # muestra: alias -> /ruta/original
```

> Los symlinks rotos son una fuente común de errores. `ls -la` los muestra en rojo en la mayoría de terminales.

---

## Resumen de comandos clave

| Comando | Para qué sirve |
|---|---|
| `pwd` | Ver ruta actual |
| `cd <ruta>` | Cambiar de directorio |
| `cd -` | Volver al directorio anterior |
| `ls -lah` | Listado completo con ocultos y tamaños legibles |
| `ls -lt` | Ordenar por fecha de modificación |
| `tree -L 2` | Vista de árbol con profundidad controlada |
| `file <archivo>` | Tipo real del archivo |
| `stat <archivo>` | Metadatos completos (inode, tiempos, permisos) |
| `ln -s` | Crear symlink |

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|índice]]
- [[shell-bash-y-terminal]]
- [[gestion-de-archivos-y-permisos]]
- [[almacenamiento-discos-y-montajes]]
