---
title: Shell, Bash y Terminal — pipes, redirecciones y fundamentos
date: 2026-06-12
tags: [programacion/linux, programacion/bash, programacion/shell]
type: nota
status: permanente
source: claude-code
aliases: [bash, shell, terminal linux, pipes linux, redirecciones bash]
---

# Shell, Bash y Terminal

## Modelo mental central

La filosofía Unix (y por tanto Linux) es: **pequeños programas que hacen una sola cosa bien, y que se pueden conectar entre sí**. La *shell* es el pegamento. No es solo un lanzador de comandos; es un entorno de programación completo que orquesta qué datos fluyen desde dónde hacia dónde.

---

## Terminal vs Shell — no es lo mismo

| Concepto | Qué es | Ejemplos |
|---|---|---|
| **Terminal** (emulador) | Programa gráfico que dibuja texto y captura teclado | GNOME Terminal, Kitty, Alacritty, tmux |
| **Shell** | Intérprete de comandos que corre *dentro* del terminal | bash, zsh, fish, dash |
| **Consola** | Terminal físico (TTY) o virtual (`Ctrl+Alt+F2` en Ubuntu) | `/dev/tty1` … `/dev/tty6` |

Cuando abres GNOME Terminal, arrancas un **emulador de terminal** que lanza tu **shell** (por defecto `bash` en Ubuntu). La shell lee lo que escribes, lo interpreta, y ejecuta programas.

```bash
echo $SHELL        # qué shell es tu login shell
echo $0            # qué shell está corriendo ahora mismo
bash --version     # versión de bash (Ubuntu 24.04 trae bash 5.2)
```

---

## Anatomía de un comando

```
comando  [-opciones_cortas]  [--opciones_largas[=valor]]  [argumentos...]
```

Ejemplo diseccionado:

```bash
ls -la --color=auto /etc/apt
#  │  ││  └──────────────── opción larga con valor
#  │  │└────────────────── opción corta 'a' (mostrar ocultos)
#  │  └─────────────────── opción corta 'l' (formato largo)
#  └────────────────────── comando
#                      └── argumento (directorio a listar)
```

**Reglas clave:**
- Opciones cortas: una letra, un guion (`-l`). Se pueden apilar: `-la` ≡ `-l -a`.
- Opciones largas: dos guiones, palabras completas (`--all`). No se apilan.
- El orden de los argumentos casi siempre importa; el de las opciones suele no importar.
- `--` (doble guion solo) marca el fin de las opciones: `rm -- -fichero_raro` evita que `-fichero_raro` se interprete como opción.

---

## Pedir ayuda

```bash
man ls              # manual completo (navegar con j/k, salir con q)
man 5 passwd        # sección 5 del manual (formatos de archivo)
man -k "copy file"  # buscar en todas las páginas de manual por palabra clave

ls --help           # ayuda corta inline (casi todos los GNU tools)
info coreutils      # documentación extendida (alternativa a man)

tldr ls             # resumen práctico con ejemplos (instalar: apt install tldr)
```

**Gotcha:** `man` usa el paginador `less`. Para buscar dentro: `/patron` → `n` siguiente, `N` anterior.

---

## Historial de comandos

```bash
history             # lista numerada de comandos previos
history 20          # los últimos 20
history | grep apt  # filtrar historial

!!                  # re-ejecuta el último comando
!$                  # último argumento del comando anterior
!apt                # re-ejecuta el último comando que empezó con "apt"
!42                 # re-ejecuta el comando número 42 del historial

sudo !!             # truco clásico: repetir último comando con sudo
```

**Ctrl+R — búsqueda inversa (el más útil):**
1. Pulsa `Ctrl+R`
2. Escribe parte del comando que recuerdas
3. La shell muestra el match más reciente
4. `Ctrl+R` de nuevo → match anterior
5. `Enter` para ejecutar, `Esc` o `Ctrl+G` para cancelar

Historial se guarda en `~/.bash_history`. Variables relevantes:
```bash
echo $HISTSIZE       # cuántas líneas guarda en memoria (default 1000)
echo $HISTFILESIZE   # cuántas líneas guarda en disco (default 2000)
```

---

## Atajos de teclado esenciales

| Atajo | Efecto | Categoría |
|---|---|---|
| `Ctrl+C` | Envía SIGINT al proceso → lo mata | Control de proceso |
| `Ctrl+D` | EOF — cierra el terminal si el prompt está vacío | Control de proceso |
| `Ctrl+Z` | Suspende el proceso (envía SIGTSTP, lo pausa) | Control de proceso |
| `Ctrl+L` | Limpia la pantalla (≡ `clear`) | Pantalla |
| `Ctrl+A` | Va al inicio de la línea | Edición de línea |
| `Ctrl+E` | Va al final de la línea | Edición de línea |
| `Ctrl+U` | Borra desde el cursor hasta el inicio | Edición de línea |
| `Ctrl+K` | Borra desde el cursor hasta el final | Edición de línea |
| `Ctrl+W` | Borra la palabra anterior al cursor | Edición de línea |
| `Alt+B` / `Alt+F` | Salta palabra atrás / adelante | Edición de línea |
| `Tab` | Autocompletar comando, ruta o argumento | Productividad |
| `Tab Tab` | Muestra todas las posibilidades si hay ambigüedad | Productividad |
| `Flecha ↑/↓` | Navega historial | Historial |

**Gotcha Ctrl+Z:** el proceso no muere, solo se *pausa*. Para recuperarlo: `fg` (foreground) o `bg` (background). Para verlos: `jobs`.

---

## STDIN, STDOUT, STDERR

Cada proceso en Linux nace con tres **file descriptors** abiertos:

| FD | Nombre | Descripción | Por defecto apunta a |
|---|---|---|---|
| `0` | STDIN | Entrada estándar | Teclado |
| `1` | STDOUT | Salida estándar | Pantalla |
| `2` | STDERR | Salida de errores | Pantalla |

```
  [Teclado] ──→ STDIN(0) ──→ [Proceso] ──→ STDOUT(1) ──→ [Pantalla]
                                       └──→ STDERR(2) ──→ [Pantalla]
```

El poder del sistema Unix es que estos tres "cables" se pueden reconectar a cualquier archivo o a otro proceso.

---

## Redirecciones

```bash
# STDOUT → archivo (sobreescribe)
ls /etc > listado.txt

# STDOUT → archivo (añade al final)
echo "nueva línea" >> listado.txt

# STDIN desde archivo (el programa lee del archivo en vez del teclado)
sort < nombres.txt

# STDERR → archivo (FD 2)
gcc codigo.c 2> errores.log

# STDOUT y STDERR → mismo archivo (dos formas equivalentes)
make &> build.log
make > build.log 2>&1      # orden importa: primero redirige 1, luego 2→1

# Descartar salida completamente
comando_ruidoso > /dev/null      # descarta solo STDOUT
comando_ruidoso 2> /dev/null     # descarta solo STDERR
comando_ruidoso &> /dev/null     # descarta todo
```

**Gotcha `2>&1`:** el orden es crítico. `cmd 2>&1 > fichero` NO hace lo que esperas (STDERR va a la pantalla, STDOUT al fichero). El correcto es siempre `cmd > fichero 2>&1`.

**`/dev/null`** es el "agujero negro" del sistema: acepta cualquier escritura y devuelve EOF en lectura. Ideal para silenciar salidas que no interesan.

---

## Pipes `|`

El pipe conecta el **STDOUT de un proceso** con el **STDIN del siguiente**. Sin archivos intermedios, en tiempo real (stream).

```
[programa_a] ──STDOUT──→ pipe ──STDIN──→ [programa_b]
```

```bash
# Contar cuántos archivos hay en /etc
ls /etc | wc -l

# Ver los 10 procesos que más CPU consumen
ps aux | sort -k3 -rn | head -10

# Buscar texto en el historial
history | grep "git commit"

# Cadena más larga: listar paquetes instalados, filtrar python, ordenar, paginar
dpkg -l | grep python | sort | less

# Ver solo errores únicos de un log
grep "ERROR" /var/log/syslog | sort | uniq -c | sort -rn
```

**Modelo mental:** cada `|` es una "tubería" entre dos obreros en cadena. El primero produce, el segundo consume. Bash arranca todos en paralelo; el kernel sincroniza el flujo.

**Gotcha:** STDERR no pasa por el pipe. Si un comando intermedio escupe errores, los verás en la pantalla aunque hayas puesto `| siguiente`. Para pasar también STDERR: `cmd 2>&1 | siguiente`.

---

## Operadores de control

```bash
# ';' — ejecuta secuencialmente, sin importar si fallan
apt update ; apt upgrade

# '&&' — ejecuta el segundo SOLO si el primero tuvo éxito (exit code 0)
cd /tmp && rm -rf cache_vieja

# '||' — ejecuta el segundo SOLO si el primero FALLÓ (exit code ≠ 0)
ping -c1 google.com || echo "Sin internet"

# '&' — lanza el comando en BACKGROUND (no bloquea el terminal)
firefox &
sleep 30 &           # verifica con: jobs
```

**Combinar `&&` y `||` como if/else:**
```bash
comando && echo "OK" || echo "FALLO"
```

**Exit codes:** todo comando devuelve un número al terminar. `0` = éxito. Cualquier otro valor = error. Ver el último: `echo $?`.

---

## Sustitución de comandos `$(...)`

Captura la salida de un comando y la inserta en otro comando (o variable).

```bash
# Forma moderna (preferida)
echo "Hoy es $(date +%F)"
echo "Hay $(ls | wc -l) archivos aquí"

# Asignar a variable
mi_directorio=$(pwd)
kernel=$(uname -r)
echo "Kernel: $kernel"

# Forma antigua con backticks (evitar — no se anidan bien)
echo `date`   # equivalente pero obsoleto
```

**Gotcha:** la sustitución captura STDOUT, no STDERR. Los errores siguen yendo a la pantalla. Si el comando falla, la variable queda vacía (o con output parcial).

---

## Quoting — el tema que más confunde

La shell interpreta caracteres especiales (`$`, `*`, `?`, `~`, `&`, `|`, `>`, `<`, `;`, espacios...) ANTES de pasarlos al programa. El quoting controla qué interpreta la shell y qué pasa literal.

| Tipo | Sintaxis | Qué expande | Qué protege |
|---|---|---|---|
| Sin comillas | `hola mundo` | Todo ($var, glob *, ~) | Nada — el espacio parte en dos argumentos |
| Comillas dobles | `"hola mundo"` | `$var`, `$(cmd)`, `` `cmd` `` | Espacios, glob, ~, ; |
| Comillas simples | `'hola mundo'` | **Nada** — todo literal | Todo absolutamente |
| Backslash | `hola\ mundo` | Escapa el carácter siguiente | Solo ese carácter |

```bash
nombre="Daniel López"

echo $nombre          # MALO si hay espacios: puede partir en argumentos separados
echo "$nombre"        # BIEN: preserva el espacio, expande la variable
echo '$nombre'        # Imprime literalmente: $nombre
echo "precio: \$5"    # Escapa el $ con backslash dentro de dobles

# Glob sin comillas — la shell expande ANTES de pasar al comando
ls *.txt              # shell expande *.txt → ls a.txt b.txt c.txt
ls "*.txt"            # pasa literalmente "*.txt" a ls (busca un archivo llamado *.txt)

# Caso real donde falla no usar comillas:
archivo="mi archivo.txt"
cat $archivo          # ERROR: cat recibe "mi" y "archivo.txt" como dos argumentos
cat "$archivo"        # CORRECTO
```

**Regla práctica:** pon siempre variables entre comillas dobles (`"$var"`) a menos que deliberadamente quieras que los espacios partan argumentos o que los globs se expandan.

---

## Flujo completo — ejemplo integrador

```bash
# "Dame los 5 usuarios que más espacio ocupan en /home, excluyendo root,
#  y guarda el resultado con timestamp"

du -sh /home/* 2>/dev/null \
  | grep -v root \
  | sort -rh \
  | head -5 \
  | tee resultado_$(date +%F).txt
```

Desglose:
- `du -sh /home/*` — uso de disco de cada home; `2>/dev/null` descarta errores de permisos
- `| grep -v root` — excluye líneas con "root"
- `| sort -rh` — ordena por tamaño humano, mayor primero
- `| head -5` — primeros 5
- `| tee fichero` — escribe en fichero Y sigue mostrando en pantalla (tee = bifurcador de pipe)

---

## Gotchas resumidos

1. **`>` sobreescribe sin avisar.** Si el archivo existía, se borra su contenido. Usa `>>` para añadir.
2. **El pipe ignora STDERR.** Añade `2>&1` antes del pipe si necesitas pasar errores.
3. **`Ctrl+Z` no mata.** Pausa el proceso; sigue vivo. Usa `fg`, `bg` o `kill %1`.
4. **Las comillas simples son absolutas.** Dentro de `'...'` no hay expansión de ningún tipo.
5. **`&&` y `||` son cortocircuito.** Como en C: el segundo operando puede no ejecutarse.
6. **`$()` anida, los backticks no.** Prefiere siempre `$(...)` para sustitución.

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|índice]]
- [[scripting-en-bash]]
- [[procesado-de-texto-grep-sed-awk]]
