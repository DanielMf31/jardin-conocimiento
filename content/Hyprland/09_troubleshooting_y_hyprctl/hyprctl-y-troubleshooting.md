---
title: Hyprctl y Resolución de Problemas
date: 2026-06-12
tags: [programacion/linux, programacion/hyprland, programacion/wayland]
type: nota
status: permanente
source: claude-code
aliases: [hyprctl, hyprland troubleshooting, depuración hyprland, debug hyprland]
---

# Hyprctl y Resolución de Problemas

## Idea central

`hyprctl` es la interfaz de línea de comandos hacia el compositor Hyprland en ejecución. Comunica con el socket Unix de la sesión activa (`/run/user/1000/hypr/<sig>/.socket.sock`). Toda llamada es **síncrona** — spam de llamadas ralentiza el compositor; usa `--batch` para múltiples operaciones.

---

## 1. Subcomandos clave

| Subcomando | Categoría | Qué devuelve / hace |
|---|---|---|
| `version` | info | Versión, commit, ABI, flags de compilación |
| `splash` | info | Frase splash aleatoria del inicio |
| `clients` | info | Todas las ventanas abiertas (clase, título, workspace, geometría, PID…) |
| `activewindow` | info | La ventana con foco ahora mismo |
| `activeworkspace` | info | Workspace activo (ID, monitor, nº ventanas, layout) |
| `workspaces` | info | Todos los workspaces existentes, incluyendo especiales |
| `monitors` | info | Monitores: resolución, refresh, escala, VRR, formato… |
| `devices` | info | Teclados, ratones, touchpad — con layout activo |
| `layers` | info | Surface layers: background, bottom, top, overlay (waybar, swww…) |
| `binds` | info | Todos los keybinds activos con dispatcher y argumento |
| `configerrors` | debug | Errores de parseo de la configuración actual |
| `getoption <sección:clave>` | debug | Valor actual de una opción de config (int, float, color…) |
| `reload` | control | Recarga `hyprland.conf` en caliente (sin reiniciar sesión) |
| `dispatch <dispatcher> [arg]` | control | Ejecuta un dispatcher (equiv. a pulsar un keybind) |
| `keyword <sección:clave> <valor>` | control | Cambia una opción al vuelo, sin editar el archivo |
| `setcursor <theme> <size>` | control | Cambia el tema del cursor en caliente |
| `--batch "cmd1 ; cmd2"` | control | Ejecuta varios comandos de control en una sola llamada |

### Ejemplos reales (sesión activa 2026-06-12, Hyprland 0.55.3)

```bash
# Versión instalada
$ hyprctl version
Hyprland 0.55.3 built from branch  at commit fe5fe79a...
Tag: v0.55.3, commits: 7366

# Ventana activa
$ hyprctl activewindow
Window 5b24f34ebd20 -> ⠐ glossary-programming-technical-terms:
    class:          kitty
    workspace:      1 (1)
    floating:       0
    monitor:        0

# Monitor
$ hyprctl monitors
Monitor eDP-1 (ID 0):
    1920x1080@144.00000 at 0x0
    active workspace: 1 (1)
    scale: 1.00
    vrr: false

# Splash
$ hyprctl splash
Thanks ThatOneCalculator!

# Config errors (salida vacía = sin errores)
$ hyprctl configerrors
(sin salida)

# Cambiar gaps en caliente
$ hyprctl keyword general:gaps_in 8
ok

# Leer una opción
$ hyprctl getoption decoration:rounding
int: 10
set: true

# Batch: dos cambios en una sola llamada IPC
$ hyprctl --batch "keyword general:gaps_in 5 ; keyword general:gaps_out 10"
ok
ok
```

---

## 2. El flag `-j` — JSON para scripting

Casi todo subcomando de info acepta `-j`. La respuesta es JSON parseable.

```bash
# Obtener class y workspace de la ventana activa con jq
$ hyprctl -j activewindow | jq '{class: .class, ws: .workspace.id, float: .floating}'
{
  "class": "kitty",
  "ws": 1,
  "float": false
}

# Listar todos los workspaces con ventanas abiertas
$ hyprctl -j workspaces | jq '.[] | {id, name, windows}'
{"id": 1,  "name": "1",  "windows": 1}
{"id": 2,  "name": "2",  "windows": 1}
{"id": 3,  "name": "3",  "windows": 1}
{"id": -98,"name": "special:scratchpad","windows": 2}

# Address de todas las ventanas flotantes
$ hyprctl -j clients | jq '.[] | select(.floating) | {address, class, workspace: .workspace.name}'
{
  "address": "0x5b24f349d890",
  "class": "kitty",
  "workspace": "special:scratchpad"
}
```

**Tip de scripting**: si `jq` no está disponible, `python3 -m json.tool` imprime el JSON con indentación. Para filtros, `python3 -c "import sys,json; ..."`.

La firma de instancia se necesita cuando lanzas `hyprctl` desde un script fuera de la sesión Wayland:

```bash
export HYPRLAND_INSTANCE_SIGNATURE=$(ls -t /run/user/$(id -u)/hypr/ | head -1)
hyprctl clients
```

---

## 3. El log de Hyprland

### Ubicación real en 0.55.x

```
/run/user/1000/hypr/<INSTANCE_SIGNATURE>/hyprland.log
```

Donde `<INSTANCE_SIGNATURE>` es algo como `fe5fe79a29ac3adaf3e75560b2f4b7a6d58b31c9_1781291427_2099331386`. El archivo desaparece al cerrar sesión porque vive en tmpfs.

**Para esta sesión:**
```bash
$ ls /run/user/1000/hypr/
fe5fe79a29ac3adaf3e75560b2f4b7a6d58b31c9_1781291427_2099331386/

$ ls -lh /run/user/1000/hypr/$(ls -t /run/user/1000/hypr/ | head -1)/
-rw-rw-r-- hyprland.lock   (15 bytes — PID del compositor)
-rw-rw-r-- hyprland.log    (85 KB tras ~2 h de sesión)
srwxrwxr-x .socket.sock    (IPC principal — hyprctl lo usa)
srwxrwxr-x .socket2.sock   (eventos — para scripts que escuchan)
```

### Cómo leer el log

El log está **desactivado por defecto** a partir de cierta línea de inicio:

```
DEBUG ]: !!!!HEY YOU, YES YOU!!!!: further logs to stdout / logfile are disabled
by default. BEFORE SENDING THIS LOG, ENABLE THEM.
Use debug:disable_logs = false
```

Para activar logging completo, añade en `hyprland.conf`:

```hyprlang
debug {
    disable_logs = false
    # disable_time = false   # añade timestamp en cada línea
}
```

Luego recarga: `hyprctl reload`. Tras ello el log crece rápido — úsalo sólo para depurar.

### Niveles de mensaje

| Prefijo en el log | Significado |
|---|---|
| `DEBUG` | Flujo normal de ejecución |
| `ERR` | Error no fatal (puede continuar) |
| `WARN` | Advertencia — algo puede no funcionar bien |
| `LOG` | Mensaje informativo relevante |
| `CRIT` | Error crítico — suele preceder a un crash |

### Errores irrelevantes en arranque normal

Estos aparecen en cada arranque y **no son problemáticos**:

```
ERR from aquamarine ]: [libseat] Could not connect to socket /run/seatd.sock: Permission denied
```
→ Normal: Hyprland usa logind (systemd), no seatd.

```
ERR from aquamarine ]: drm: getCurrentCRTC: No CRTC 0
```
→ Normal con GPU Intel/híbrida en el arranque inicial.

```
ERR from aquamarine ]: Wayland backend cannot start: wl_display_connect failed
```
→ Normal: Hyprland prueba el backend Wayland anidado y falla (no hay Wayland padre). Recae en DRM correctamente.

```
ERR from aquamarine ]: drm: failed to parse edid
```
→ Común en portátiles sin EDID completo. No afecta funcionamiento.

### Filtrar el log útilmente

```bash
LOG=/run/user/1000/hypr/$(ls -t /run/user/1000/hypr/ | head -1)/hyprland.log

# Ver sólo errores reales del compositor (no de aquamarine)
grep "^ERR \]" "$LOG"

# Ver mensajes de configuración
grep "\[cfg\]" "$LOG"

# Ver errores de windowrule
grep -i "rule\|window\|match" "$LOG" | grep -v "^DEBUG"

# Seguir el log en vivo
tail -f "$LOG"
```

---

## 4. Errores de configuración — diagnóstico y casos reales

### Flujo básico

1. Edita `~/.config/hypr/hyprland.conf` (o un archivo `source`-ado)
2. `hyprctl reload`
3. Si hay error, aparece un **overlay rojo** en pantalla con el mensaje
4. Confirma con: `hyprctl configerrors`
5. El log también muestra la línea exacta si `disable_logs = false`

### Opciones renombradas en 0.45–0.55 (errores frecuentes)

| Nombre antiguo | Nombre actual (0.55.x) | Sección |
|---|---|---|
| `misc:vfr` | eliminado / ahora es `render:vrr` por monitor | misc → render |
| `dwindle:pseudotile` | sigue existiendo como opción de sección, pero el **dispatcher** cambió | — |
| `togglesplit` (dispatcher) | sigue siendo `togglesplit` pero requiere dwindle activo | dispatchers |
| `general:col.active_border` | misma clave, pero sintaxis de color cambió a `rgba(...)` | general |

**Verificación directa**:
```bash
# ¿Existe misc:vfr en esta versión?
$ hyprctl getoption misc:vfr
no such option

# ¿Y render:vrr?
$ hyprctl getoption misc:disable_logs
int: 1      ← debug:disable_logs está en 1 (activado = logs off)
set: false
```

### Ejemplo: error "config error in file"

Si ves en el overlay:
```
Config error in file /home/usuario/.config/hypr/configs/SystemSettings.conf:85
vfr = true → unknown variable
```

Acción:
```bash
# 1. Localizar la línea
grep -n "vfr" ~/.config/hypr/configs/SystemSettings.conf
# 85:  vfr = true

# 2. Comentar o eliminar
# vfr = true   ← comentado hasta encontrar el equivalente correcto

# 3. Recargar
hyprctl reload
hyprctl configerrors   # debería estar vacío
```

---

## 5. Depurar una window rule que no aplica

### Paso 1 — Verificar la class real con `hyprctl clients`

La fuente de verdad es `class` e `initialClass` (lo que Wayland/XWayland reporta), **no** lo que aparece en el título.

```bash
$ hyprctl clients
Window 5b24f34ebd20 -> ⠐ glossary-programming-technical-terms:
    class:         kitty          ← usa ESTO en la regla
    initialClass:  kitty
    title:         ⠐ glossary-programming-technical-terms
    xwayland:      0
```

O con JSON para ver todo de una:
```bash
$ hyprctl -j clients | jq '.[] | {class, initialClass, title, xwayland}'
```

### Paso 2 — Verificar la sintaxis de la regla (0.55 usa `windowrule v2+`)

```hyprlang
# Formato moderno (0.55):
windowrule = match:class ^(kitty)$, tag +terminal

# Formato antiguo (deprecated pero aún soportado):
windowrulev2 = float, class:^(kitty)$
```

### Paso 3 — Casos comunes de fallo

| Síntoma | Causa probable | Fix |
|---|---|---|
| Regla ignorada | `class` no coincide (regex case-sensitive) | `hyprctl clients` → copiar `class` exacto |
| Regla ignorada | `initialClass` vs `class` difieren (título cambia) | Usar `match:initialClass` |
| Regla ignorada | App es XWayland (`xwayland: 1`) y la regex no coincide | Probar `xwayland:1` como condición adicional |
| Regla aplicada al revés | Orden de reglas (la última que coincide gana en algunos casos) | Revisar orden en el archivo |
| Ventana flotante inesperada | La app pide flotar via XDG shell hints | Añadir `windowrule = tile, class:^(miapp)$` |

### Paso 4 — Habilitar debug de windowrules en el log

```hyprlang
debug {
    disable_logs = false
}
```

Luego buscar en el log:
```bash
grep -i "windowrule\|matchrule\|applying rule" "$LOG"
```

---

## 6. Caso real: ventana que aparece flotante en workspace -98

### El problema

`hyprctl clients` muestra:
```
Window 5b24f349d890 -> ~:
    workspace: -98 (special:scratchpad)
    floating:  1
```

El **workspace ID -98** es siempre `special:scratchpad` (o cualquier special workspace con ese nombre). Las ventanas en workspaces especiales aparecen flotantes **por diseño**: los special workspaces se superponen al workspace normal y sus ventanas no participan en el layout tiling.

### Por qué ocurre

- Algún keybind envía la ventana con `movetoworkspace, special` o `movetoworkspace, special:scratchpad`
- En los dotfiles KooL: `$mainMod SHIFT U` → `movetoworkspace, special`
- El scratchpad se invoca/oculta con `$mainMod U` → `togglespecialworkspace`

### Verificar

```bash
$ hyprctl -j workspaces | jq '.[] | select(.id < 0)'
{
  "id": -98,
  "name": "special:scratchpad",
  "windows": 2,
  "monitorID": 0
}
```

### Si quieres sacar la ventana del scratchpad

```bash
# Enfocar la ventana primero, luego moverla al workspace normal
hyprctl dispatch focuswindow address:0x5b24f349d890
hyprctl dispatch movetoworkspace 1
```

### Si una ventana "normal" cae en -98 sin querer

Revisar si tiene una window rule que la manda al special workspace:
```bash
grep -rn "special\|scratchpad" ~/.config/hypr/configs/WindowRules*.conf
```

---

## 7. Recuperación cuando Hyprland no arranca o la sesión se rompe

### Escenario A — Error de config, pantalla negra o loop de reinicios

Hyprland arranca, falla al parsear el config, y o bien muestra overlay rojo o bien cae de vuelta a GDM.

**Solución desde GDM:**
1. En la pantalla de login de GDM, haz clic en el engranaje (⚙) junto al usuario
2. Selecciona **GNOME (Xorg)** o **GNOME** en lugar de Hyprland
3. Inicia sesión en GNOME
4. Abre terminal y corrige el config:
   ```bash
   nano ~/.config/hypr/hyprland.conf
   # o el archivo que rompiste
   ```
5. Cierra sesión → vuelve a elegir Hyprland en GDM

### Escenario B — Sesión colgada, compositor no responde

La sesión de Hyprland sigue viva pero todo está congelado.

1. Cambia a TTY: `Ctrl + Alt + F3`
2. Inicia sesión en el TTY con usuario y contraseña
3. Matar el compositor:
   ```bash
   pkill -9 Hyprland
   # o por PID
   cat /run/user/1000/hypr/$(ls -t /run/user/1000/hypr/ | head -1)/hyprland.lock
   kill -9 <PID>
   ```
4. Vuelve a la pantalla de GDM: `Ctrl + Alt + F1` (o F2)
5. GDM debería aparecer. Si no: `sudo systemctl restart gdm`

### Escenario C — Config tan rota que no puedes editar bien

Timeshift al rescate:

```bash
# Desde TTY o GNOME:
sudo timeshift --restore
# Selecciona el snapshot anterior al cambio problemático
# Timeshift restaura /home y / según la config del snapshot
```

O de forma más quirúrgica, solo restaurar el config:
```bash
# Listar snapshots
sudo timeshift --list

# Montar un snapshot sin restaurar (solo para copiar archivos)
# Los snapshots Timeshift están en /run/timeshift/backup/timeshift/snapshots/
sudo ls /run/timeshift/backup/timeshift/snapshots/
# Copiar solo el config de hypr
sudo cp -r /run/timeshift/backup/timeshift/snapshots/<fecha>/localhost/home/usuario/.config/hypr ~/.config/hypr-backup
cp -r ~/.config/hypr-backup/configs/SystemSettings.conf ~/.config/hypr/configs/
hyprctl reload
```

### Escenario D — Hyprland no arranca desde cero (post-instalación o post-update)

```bash
# Desde TTY, iniciar Hyprland manualmente para ver el error en stdout:
Hyprland 2>&1 | tee /tmp/hypr-debug.log
# Lee el log para ver qué falla
cat /tmp/hypr-debug.log | grep -E "ERR|CRIT|error"
```

### Comandos de emergencia desde TTY

```bash
# Ver última sesión de Hyprland
cat /run/user/1000/hypr/$(ls -t /run/user/1000/hypr/ | head -1)/hyprland.log 2>/dev/null \
    || echo "Sesión terminada, log ya no existe"

# Ver logs del sistema (GDM, Wayland, etc.)
journalctl -b --no-pager | grep -i "hypr\|wayland\|gdm" | tail -40

# Reiniciar GDM si está colgado
sudo systemctl restart gdm
```

---

## 8. Referencia rápida de dispatchers útiles para troubleshooting

```bash
# Mover ventana activa al workspace 2
hyprctl dispatch movetoworkspace 2

# Sacar una ventana del scratchpad (por address)
hyprctl dispatch movetoworkspace 1,address:0x5b24f349d890

# Forzar foco en una ventana concreta
hyprctl dispatch focuswindow class:kitty

# Cambiar layout en caliente
hyprctl dispatch setlayout dwindle
hyprctl dispatch setlayout master

# Pseudo-tile en dwindle (equivalente al toggle del keybind)
hyprctl dispatch togglefloating

# Toggle pseudo (ventana tiled que actúa como flotante en size)
hyprctl dispatch pseudo

# Matar la ventana activa desde terminal
hyprctl dispatch killactive
```

---

## Conexiones

- [[00_README]]
- [[MOC_Hyprland]]
