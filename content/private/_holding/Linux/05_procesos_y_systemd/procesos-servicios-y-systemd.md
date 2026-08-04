---
title: Procesos, Servicios y systemd
date: 2026-06-12
tags: [programacion/linux, programacion/linux/procesos, programacion/linux/systemd]
type: nota
status: permanente
source: claude-code
aliases: [procesos linux, systemd, servicios linux, ps aux, journalctl]
---

# Procesos, Servicios y systemd

## Modelo mental

**Todo lo que corre en Linux es un proceso.** Cada programa en ejecución tiene un PID (Process ID) único. Los procesos nacen de otros procesos (padre → hijo), formando un árbol. **systemd es el proceso raíz** (PID 1) y de él descienden todos los demás; su trabajo es arrancar y supervisar los *servicios* del sistema.

```
PID 1 (systemd)
├── PID 320 (networkd)
├── PID 410 (sshd)
│   └── PID 1042 (bash) ← sesión tuya
│       └── PID 1099 (python app.py) ← proceso hijo
└── ...
```

---

## 1. Qué es un proceso

| Campo | Significado |
|---|---|
| **PID** | Identificador único del proceso |
| **PPID** | PID del padre (parent) |
| **UID/GID** | Usuario/grupo propietario |
| **Estado** | R, S, D, Z, T (ver tabla debajo) |
| **Nice** | Prioridad de CPU (-20 más alta, +19 más baja) |

### Estados de un proceso

| Código | Estado | Cuándo ocurre |
|---|---|---|
| `R` | Running / Runnable | En CPU o esperando CPU |
| `S` | Sleeping (interruptible) | Esperando E/S, evento; el más común |
| `D` | Uninterruptible sleep | Esperando E/S de disco/red; **no se puede matar** |
| `Z` | Zombie | Terminó pero su padre no recogió el exit code |
| `T` | Stopped | Pausado con Ctrl+Z o señal SIGSTOP |

> **Gotcha:** un proceso en estado `D` (disk wait) no responde a `kill -9`. Solo se resuelve esperando a que termine la E/S o reiniciando.

---

## 2. Ver procesos

### `ps` — snapshot estático

```bash
# Vista tipo BSD: todos los procesos, con usuario y comando completo
ps aux

# Vista tipo SysV: árbol de PIDs con relaciones padre-hijo
ps -ef

# Filtrar por nombre (case-insensitive)
ps aux | grep nginx

# Ver solo mis procesos
ps -u $USER
```

**Columnas de `ps aux`:**

| Columna | Qué es |
|---|---|
| `USER` | Propietario |
| `PID` | ID del proceso |
| `%CPU` | CPU promedio desde que arrancó |
| `%MEM` | RAM usada / RAM total del sistema |
| `VSZ` | Memoria virtual (incluye librerías mapeadas) |
| `RSS` | Memoria física real usada |
| `STAT` | Estado + flags (ej. `Ss`, `R+`) |
| `START` | Hora/fecha de inicio |
| `COMMAND` | Comando con argumentos |

> **Gotcha:** `%CPU` en `ps` es un promedio histórico, no el uso instantáneo. Para uso en tiempo real usa `top`.

### `pgrep` — buscar PID por nombre

```bash
pgrep nginx          # devuelve PID(s)
pgrep -l nginx       # PID + nombre
pgrep -u daniel      # procesos de un usuario
```

### `top` — monitor interactivo

```bash
top
```

Atajos dentro de `top`:

| Tecla | Acción |
|---|---|
| `P` | Ordenar por CPU |
| `M` | Ordenar por memoria |
| `u` | Filtrar por usuario |
| `k` | Matar un proceso (pide PID) |
| `q` | Salir |
| `1` | Ver carga por CPU core |

**Cabecera de `top` — cómo leerla:**

```
top - 10:32:01 up 3 days, load average: 0.52, 0.48, 0.41
Tasks: 234 total,   1 running, 233 sleeping
%Cpu(s):  3.2 us,  0.8 sy,  0.0 ni, 95.6 id,  0.4 wa
MiB Mem :  15847.6 total,   3201.4 free,   8142.2 used
```

- **load average** (1m, 5m, 15m): si supera el número de CPUs, el sistema está saturado.
- **wa** (iowait): porcentaje de tiempo en que la CPU esperó E/S de disco. Si >10% de forma sostenida, el cuello de botella es disco/red.
- **us / sy**: tiempo en espacio de usuario / kernel.

### `htop` — top mejorado (instalar si no hay)

```bash
sudo apt install htop
htop
```

Ventajas: colores, scroll, F-keys para filtrar/matar, arrastre de columnas.

---

## 3. Foreground, Background y control de jobs

### Conceptos

- **Foreground (fg):** el proceso ocupa la terminal; Ctrl+C lo termina, Ctrl+Z lo pausa.
- **Background (bg):** corre sin ocupar la terminal; el shell imprime `[1] PID`.
- **Job:** un proceso (o pipeline) gestionado por el shell actual.

### Comandos

```bash
# Lanzar en background desde el inicio
python servidor.py &         # shell imprime [1] 1234

# Ver jobs activos en la terminal actual
jobs
jobs -l                      # incluye PID

# Traer job al foreground
fg %1                        # %1 = job número 1

# Enviar job pausado al background
Ctrl+Z → bg %1

# Desacoplar proceso del shell (sobrevive si cierras terminal)
nohup python servidor.py &

# Desacoplar proceso ya corriendo (bg) del shell
disown %1
disown -a                    # todos los jobs
```

> **Gotcha:** Si lanzas algo en background sin `nohup` o `disown`, muere cuando cierras la terminal. Usa `tmux` o `screen` para sesiones persistentes.

---

## 4. Señales

Las señales son mensajes del kernel o del usuario a un proceso. Las más importantes:

| Señal | Número | Comportamiento por defecto | Cuándo usar |
|---|---|---|---|
| `SIGTERM` | 15 | Terminación elegante (el proceso puede limpiar) | Primera opción siempre |
| `SIGKILL` | 9 | Muerte inmediata, no interceptable | Proceso colgado que no responde a SIGTERM |
| `SIGHUP` | 1 | Recarga configuración (en daemons) | Recargar nginx, sshd sin reiniciar |
| `SIGSTOP` | 19 | Pausar (no interceptable) | — |
| `SIGCONT` | 18 | Reanudar proceso pausado | — |
| `SIGINT` | 2 | Interrupción (= Ctrl+C) | — |

### Comandos para enviar señales

```bash
# SIGTERM (por defecto) — siempre intenta esto primero
kill 1234
kill -15 1234
kill -SIGTERM 1234

# SIGKILL — último recurso
kill -9 1234
kill -SIGKILL 1234

# Por nombre de proceso
pkill nginx              # SIGTERM a todos los procesos llamados nginx
pkill -9 nginx           # SIGKILL
killall firefox          # similar a pkill, más estricto en el nombre exacto

# SIGHUP — recargar config sin reiniciar
kill -HUP $(pgrep nginx)
```

> **Regla práctica:** usa siempre `kill PID` (SIGTERM) primero. Espera 5-10 segundos. Solo si el proceso sigue vivo usa `kill -9`. Un SIGKILL no deja que el proceso cierre ficheros ni libere recursos, lo que puede dejar datos corruptos.

### Prioridad — nice y renice

```bash
# Lanzar con prioridad baja (+10 → menos prioritario)
nice -n 10 make -j4

# Cambiar prioridad de proceso ya corriendo (requiere sudo para bajar nice)
renice -n 5 -p 1234         # PID 1234 a nice 5
sudo renice -n -5 -p 1234   # nice negativo = más prioritario (solo root)
```

Rango: `-20` (más CPU) a `+19` (menos CPU). El valor por defecto es `0`.

---

## 5. systemd — gestor de servicios

### Qué es

systemd es el **PID 1**: el primer proceso que arranca el kernel y del que desciende todo lo demás. Se encarga de:

1. Arrancar servicios en el orden correcto (resolviendo dependencias).
2. Reiniciar servicios que fallan.
3. Centralizar los logs (journald).
4. Gestionar el ciclo de vida del sistema (apagar, reiniciar, suspender).

### Units — la unidad de trabajo de systemd

Todo en systemd se modela como una *unit*. Los tipos más comunes:

| Tipo | Extensión | Para qué |
|---|---|---|
| Service | `.service` | Daemons y procesos (nginx, sshd, docker) |
| Timer | `.timer` | Equivalente a cron |
| Socket | `.socket` | Activación por socket |
| Mount | `.mount` | Puntos de montaje |
| Target | `.target` | Grupos de units (como runlevels) |

Las unit files del sistema viven en `/lib/systemd/system/`. Tus personalizaciones en `/etc/systemd/system/` (tienen prioridad).

---

## 6. systemctl — gestionar servicios

### Comandos de consulta (solo lectura)

```bash
# Estado de un servicio (incluye últimas líneas de log)
systemctl status nginx
systemctl status ssh

# Listar todos los servicios activos
systemctl list-units --type=service

# Listar todos (activos + inactivos + fallidos)
systemctl list-units --type=service --all

# Ver si un servicio está habilitado para arrancar en boot
systemctl is-enabled nginx
systemctl is-active nginx

# Ver el fichero de unit (config del servicio)
systemctl cat nginx
```

### Comandos de gestión (requieren sudo)

```bash
sudo systemctl start nginx       # iniciar ahora
sudo systemctl stop nginx        # parar ahora
sudo systemctl restart nginx     # parar + iniciar
sudo systemctl reload nginx      # recargar config sin parar (si el servicio lo soporta)

sudo systemctl enable nginx      # activar en boot
sudo systemctl disable nginx     # desactivar en boot
sudo systemctl enable --now nginx  # activar + iniciar ya (forma idiomática)
```

> **Gotcha:** `enable` no inicia el servicio ahora, solo lo marca para el próximo arranque. `enable --now` hace las dos cosas a la vez.

### Servicios de usuario (`--user`)

Relevante para entornos de escritorio (Hyprland, waybar, pipewire, etc.): servicios que corren con tu usuario, sin privilegios de root.

```bash
# Gestión con --user
systemctl --user status waybar
systemctl --user restart pipewire
systemctl --user enable --now ssh-agent

# Los unit files de usuario van en:
# ~/.config/systemd/user/
```

---

## 7. journalctl — leer los logs

journald centraliza los logs de todos los servicios systemd. A diferencia de los ficheros planos de `/var/log/`, los logs de journal son binarios con metadatos ricos.

```bash
# Todos los logs del boot actual
journalctl -b

# Logs de un servicio concreto
journalctl -u nginx
journalctl -u nginx -b          # solo del boot actual
journalctl -u nginx -n 50       # últimas 50 líneas
journalctl -u nginx -f          # follow (tiempo real, como tail -f)

# Filtrar por prioridad (0=emerg … 7=debug)
journalctl -p err               # errores y superiores
journalctl -p warning -u nginx

# Logs desde hace X tiempo
journalctl --since "1 hour ago"
journalctl --since "2026-06-12 09:00" --until "2026-06-12 10:00"

# Logs del boot anterior (útil para diagnosticar crasheos)
journalctl -b -1

# Logs de usuario
journalctl --user -u waybar
```

> **Gotcha:** `journalctl` pagina con `less` por defecto. Usa `journalctl ... | cat` si quieres la salida sin paginación (para `grep`, scripts, etc.).

---

## 8. Flujo de diagnóstico típico

Cuando algo no funciona:

```
1. systemctl status <servicio>       → ¿está activo? ¿cuál es el error inmediato?
2. journalctl -u <servicio> -n 100   → historial de logs
3. journalctl -u <servicio> -f       → observar en tiempo real mientras reproduces el problema
4. ps aux | grep <proceso>           → ¿está corriendo? ¿cuántos PIDs?
5. kill -HUP <PID>                   → intentar recarga antes de reiniciar
6. sudo systemctl restart <servicio> → reinicio limpio si todo falla
```

---

## Resumen rápido de comandos

| Tarea | Comando |
|---|---|
| Ver todos los procesos | `ps aux` |
| Monitor en tiempo real | `top` / `htop` |
| Buscar PID por nombre | `pgrep -l nombre` |
| Matar proceso (elegante) | `kill PID` |
| Matar proceso (forzado) | `kill -9 PID` |
| Estado de servicio | `systemctl status nginx` |
| Iniciar / parar servicio | `sudo systemctl start/stop nginx` |
| Activar en boot | `sudo systemctl enable --now nginx` |
| Ver logs de servicio | `journalctl -u nginx -f` |
| Logs con errores | `journalctl -p err -b` |

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|índice]]
- [[shell-bash-y-terminal]]
- [[usuarios-grupos-y-sudo]]
