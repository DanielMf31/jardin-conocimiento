---
title: Hyprlang y Estructura de Configuración
date: 2026-06-12
tags: [programacion/hyprland, programacion/linux/wm, programacion/configuracion]
type: nota
status: permanente
source: claude-code
aliases: [hyprlang, hyprland config, configuracion hyprland, hyprland.conf]
---

# Hyprlang y Estructura de Configuración

## Idea central

Hyprlang es el lenguaje de configuración propio de Hyprland (hasta 0.54). En 0.55 fue deprecado en favor de **Lua** — pero tu instalación actual (JaKooLit) usa hyprlang íntegramente, así que este documento lo cubre a fondo. La transición a Lua se documenta al final.

---

## 1. Qué es hyprlang

Hyprlang es un DSL (Domain-Specific Language) diseñado para Hyprland. No es Bash, no es INI, no es TOML. Sus características clave:

- Bloques de categoría con `nombre { }` para agrupar opciones relacionadas.
- Variables con `$nombre = valor` — expansión de texto plano, sin tipado fuerte.
- Directiva `source = ruta` para incluir otros archivos en orden.
- Keywords de primer nivel: `env`, `exec`, `exec-once`, `bind`, `monitor`, `windowrule`, etc.
- **Sin secciones únicas**: la misma categoría puede aparecer en múltiples archivos y Hyprland la **mergea** — no la reemplaza.
- Hot reload automático: Hyprland vigila los archivos y recarga al detectar cambios.

### Nota sobre 0.55+

> A partir de 0.55, hyprlang está **deprecado**. El nuevo sistema usa Lua (`hyprland.lua`).
> Tu config actual sigue siendo hyprlang válido — Hyprland 0.55.3 aún lo soporta pero mostrará
> advertencias en el log. Ver sección §8 para la transición.

---

## 2. Anatomía de un archivo hyprlang

### 2.1 Estructura general

```hyprlang
# Comentario de línea (solo con #)

# Variable global
$mainMod = SUPER

# Keyword de primer nivel
exec-once = waybar

# Variable de entorno
env = XDG_CURRENT_DESKTOP,Hyprland

# Categoría (bloque)
general {
    gaps_in = 5
    gaps_out = 12
    border_size = 2
    col.active_border = rgba(33ccffee) rgba(00ff99ee) 45deg
}

# Categoría anidada
decoration {
    rounding = 10
    blur {
        enabled = true
        size = 6
        passes = 3
    }
}

# Incluir otro archivo
source = ~/.config/hypr/UserConfigs/UserSettings.conf
```

### 2.2 Reglas sintácticas

| Elemento | Forma | Ejemplo |
|---|---|---|
| Comentario | `# texto` | `# esto es un comentario` |
| Asignación | `clave = valor` | `border_size = 2` |
| Variable | `$nombre = valor` | `$mainMod = SUPER` |
| Categoría | `nombre { ... }` | `general { gaps_in = 5 }` |
| Anidamiento | `cat { subcat { } }` | `decoration { blur { size = 6 } }` |
| Include | `source = ruta` | `source = ~/.config/hypr/configs/Keybinds.conf` |
| Env var | `env = NOMBRE,valor` | `env = MOZ_ENABLE_WAYLAND,1` |
| Autostart | `exec-once = cmd` | `exec-once = waybar` |
| Opción de punto | `cat.subclave = val` | `col.active_border = ...` |

**No hay punto y coma.** Un valor por línea. Las llaves `{ }` pueden estar en la misma línea o en la siguiente.

---

## 3. Variables (`$nombre`)

Son expansión de texto puro — se sustituyen literalmente donde se usen:

```hyprlang
$scriptsDir = $HOME/.config/hypr/scripts
$mainMod    = SUPER
$term       = kitty
$files      = thunar

# Uso: se expande en tiempo de parseo
bindd = $mainMod, Return, Open terminal, exec, $term
exec-once = $scriptsDir/Polkit.sh
```

**En tu config**, `hyprland.conf` define dos variables de ruta fundamentales:

```hyprlang
$configs     = $HOME/.config/hypr/configs
$UserConfigs = $HOME/.config/hypr/UserConfigs
```

Y `configs/Keybinds.conf` define las de la sesión:

```hyprlang
$mainMod    = SUPER
$scriptsDir = $HOME/.config/hypr/scripts
$UserScripts = $HOME/.config/hypr/UserScripts
```

Y `UserConfigs/01-UserDefaults.conf` define las de aplicaciones:

```hyprlang
$term   = kitty
$files  = thunar
$edit   = ${EDITOR:-nano}
$Search_Engine = "https://www.google.com/search?q={}"
```

> `$HOME` y otras variables de entorno del shell están disponibles en hyprlang — se expanden desde el entorno del proceso Hyprland.

---

## 4. Tipos de valores

| Tipo | Descripción | Ejemplos |
|---|---|---|
| `int` | Entero | `border_size = 2`, `passes = 3` |
| `float` | Decimal | `dim_strength = 0.1`, `mfact = 0.5` |
| `bool` | Booleano | `enabled = true`, `natural_scroll = false`, `yes`/`no`, `1`/`0` |
| `string` | Texto libre | `kb_layout = es`, `swallow_regex = ^(kitty)$` |
| `color` | Color (varios formatos) | ver tabla abajo |
| `vec2` | Vector 2D | `monitor = DP-1, 1920x1080, 0x0, 1` (posición es vec2) |
| `gradient` | Gradiente de borde | `rgba(33ccffee) rgba(00ff99ee) 45deg` |

### 4.1 Formatos de color

```hyprlang
col.active_border = rgba(33ccffee)          # RRGGBBAA hex — el más común
col.active_border = rgb(33ccff)             # RRGGBB sin alpha
col.active_border = 0xff33ccff              # 0xAARRGGBB legacy
col.active_border = #33ccff                 # hex CSS (alpha = ff implícito)
```

> **El canal alpha en rgba() va al final** (`33ccff` + `ee`), distinto del CSS estándar.
> En `0x` notation, el alpha va al **principio** (`0xff` = opaco).

### 4.2 Gradientes (para bordes)

```hyprlang
# Gradiente lineal: color1 color2 ... ángulo
col.active_border = rgba(33ccffee) rgba(00ff99ee) 45deg

# Tu UserSettings.conf usa exactamente esto:
col.active_border = rgba(33ccffee) rgba(00ff99ee) 45deg
col.inactive_border = rgba(595959aa)
```

Un gradiente admite más de dos colores. El ángulo es opcional (default 0deg = vertical).

### 4.3 Variables Wallust (colores dinámicos)

Tu `UserDecorations.conf` usa variables como `$color12`, `$color10` que vienen de:

```hyprlang
source = $HOME/.config/hypr/wallust/wallust-hyprland.conf
```

Wallust genera ese archivo con los colores extraídos del wallpaper activo. Hyprlang los expande como variables normales.

### 4.4 `vec2`

Se usa para posiciones, tamaños, etc. Se escribe como `X Y` (espacio separado) o como parámetros posicionales en keywords como `monitor`:

```hyprlang
monitor = DP-1, 1920x1080, 0x0, 1
#                          ^--^ posición vec2
```

---

## 5. Variables de entorno (`env`)

Sintaxis especial — usa coma como separador, no `=`:

```hyprlang
env = NOMBRE_VAR,valor
```

**No** `env = NOMBRE=valor`. La coma es el delimitador.

Hyprland exporta estas variables a todos los procesos que lanza (incluyendo `exec-once`). Son útiles para:

- Forzar backend Wayland en toolkits: `env = QT_QPA_PLATFORM,wayland;xcb`
- Configurar escala: `env = GDK_SCALE,1`
- Cursores: `env = HYPRCURSOR_THEME,Bibata-Modern-Ice`
- NVIDIA: `env = __GLX_VENDOR_LIBRARY_NAME,nvidia`

**Tu config** tiene dos capas de env vars:

```
configs/ENVariables.conf      → defaults de JaKooLit (GDK, QT, NVIDIA, etc.)
UserConfigs/ENVariables.conf  → tus overrides (actualmente todo comentado)
```

> Si pones la misma variable dos veces, la **última declaración gana** (misma regla que todo hyprlang).

---

## 6. `exec` vs `exec-once`

| Keyword | Cuándo ejecuta | Cuándo usar |
|---|---|---|
| `exec-once` | Solo al iniciar Hyprland (una vez por sesión) | Daemons, waybar, swww, cliphist, polkit |
| `exec` | En cada reload de config | Scripts que deben re-ejecutarse si cambias config |

```hyprlang
# Solo al inicio de sesión
exec-once = swww-daemon --format xrgb
exec-once = waybar
exec-once = hypridle

# En cada reload (raro — úsalo conscientemente)
exec = $scriptsDir/AlgunaRecarga.sh
```

> **Importante**: `exec-once` lanzado durante un hot reload **no se ejecuta de nuevo** — solo al inicio de la sesión. Los procesos ya corriendo no se reinician.

### Orden de ejecución en tu config

1. `exec-once = $HOME/.config/hypr/initial-boot.sh` — lo primero, antes de cualquier `source`
2. Todos los `exec-once` de `configs/Startup_Apps.conf` (swww, waybar, swaync, etc.)
3. Todos los `exec-once` de `UserConfigs/Startup_Apps.conf` (tus apps por workspace)

Tu `UserConfigs/Startup_Apps.conf`:
```hyprlang
exec-once = [workspace 1 silent] kitty
exec-once = [workspace 2 silent] google-chrome-stable
exec-once = [workspace 3 silent] code
exec-once = [workspace 4 silent] spotify
```

La sintaxis `[workspace N silent]` es un **rule prefix** para exec-once — lanza la app directamente en ese workspace sin cambiar el foco.

---

## 7. La directiva `source` y el sistema de dos capas de JaKooLit

### 7.1 Cómo funciona `source`

```hyprlang
source = /ruta/absoluta/archivo.conf
source = $HOME/.config/hypr/configs/Keybinds.conf   # con variables
source = ~/archivo.conf                               # con tilde (soportado)
```

`source` inserta el contenido del archivo referenciado en ese punto del parseo. Es equivalente a copiar y pegar el archivo en esa línea. El orden importa.

### 7.2 El patrón de dos capas de JaKooLit

JaKooLit separa la config en dos capas con propósitos distintos:

```
~/.config/hypr/
├── configs/              ← CAPA BASE (JaKooLit, no tocar)
│   ├── Keybinds.conf     ← keybinds por defecto
│   ├── SystemSettings.conf ← dwindle, master, input, misc, xwayland...
│   ├── ENVariables.conf  ← env vars del entorno (Qt, GDK, NVIDIA...)
│   ├── Startup_Apps.conf ← daemons del sistema
│   ├── WindowRules.conf  ← reglas de ventana base
│   └── Laptops.conf      ← binds de hardware laptop
│
└── UserConfigs/          ← CAPA USUARIO (tus overrides)
    ├── 01-UserDefaults.conf  ← $term, $files, $edit
    ├── UserSettings.conf     ← overrides de general {} y dwindle {}
    ├── UserDecorations.conf  ← borders, rounding, blur, shadows, opacity
    ├── UserAnimations.conf   ← tu config de animaciones
    ├── UserKeybinds.conf     ← tus keybinds adicionales
    ├── ENVariables.conf      ← tus overrides de env vars
    ├── Startup_Apps.conf     ← tus apps de autostart
    ├── WindowRules.conf      ← tus reglas de ventana adicionales
    ├── WorkSpaceRules.conf   ← reglas de workspace
    ├── Laptops.conf          ← overrides de laptop
    └── LaptopDisplay.conf    ← config de pantalla laptop
```

### 7.3 Orden de carga en `hyprland.conf`

```hyprlang
# -- SIEMPRE PRIMERO: boot script
exec-once = $HOME/.config/hypr/initial-boot.sh

# -- Variables de ruta
$configs     = $HOME/.config/hypr/configs
$UserConfigs = $HOME/.config/hypr/UserConfigs

# 1. Keybinds base (source dentro de Keybinds.conf carga 01-UserDefaults ANTES)
source = $configs/Keybinds.conf

# 2. Startup: base → usuario
source = $configs/Startup_Apps.conf
source = $UserConfigs/Startup_Apps.conf

# 3. Env vars: base → usuario
source = $configs/ENVariables.conf
source = $UserConfigs/ENVariables.conf

# 4. Laptop: base → usuario
source = $configs/Laptops.conf
source = $UserConfigs/Laptops.conf
source = $UserConfigs/LaptopDisplay.conf

# 5. Window rules: base → usuario
source = $configs/WindowRules.conf
source = $UserConfigs/WindowRules.conf

# 6. System settings (solo base, no tiene capa usuario directa)
source = $configs/SystemSettings.conf

# 7. Decoraciones y animaciones (solo usuario — definen la estética)
source = $UserConfigs/UserDecorations.conf
source = $UserConfigs/UserAnimations.conf

# 8. Keybinds y settings de usuario (overrides finales)
source = $UserConfigs/UserKeybinds.conf
source = $UserConfigs/UserSettings.conf
source = $UserConfigs/01-UserDefaults.conf

# 9. Monitor y workspaces (lo último — override total de geometría)
source = $HOME/.config/hypr/monitors.conf
source = $HOME/.config/hypr/workspaces.conf
```

### 7.4 La regla de oro: lo último gana

Hyprlang no tiene conceptos de "override" explícito. **La última asignación de una clave gana**:

```hyprlang
# configs/SystemSettings.conf carga primero:
general {
    layout = dwindle
    resize_on_border = true
}

# UserConfigs/UserSettings.conf carga después:
general {
    gaps_in = 5       # ← este valor pisa el de SystemSettings si existía
    gaps_out = 12
    border_size = 2
    col.active_border = rgba(33ccffee) rgba(00ff99ee) 45deg
}
```

**El mismo bloque puede abrirse varias veces**. Hyprland hace merge: claves presentes en ambos bloques usan el valor del último; claves solo en el primero se conservan.

Ejemplo concreto de tu config:

| Clave | Valor en `configs/SystemSettings.conf` | Valor en `UserConfigs/UserSettings.conf` | Valor final |
|---|---|---|---|
| `general.layout` | `dwindle` | (no presente) | `dwindle` |
| `general.resize_on_border` | `true` | (no presente) | `true` |
| `general.gaps_in` | (no presente) | `5` | `5` |
| `general.col.active_border` | (no presente) | `rgba(33ccff...) 45deg` | gradiente azul-verde |

---

## 8. Merge de bloques entre archivos

Hyprland no tiene "secciones únicas". Puedes abrir `decoration { }` en 5 archivos distintos y todos se fusionan:

```hyprlang
# archivo A
decoration {
    rounding = 10
    active_opacity = 1.0
}

# archivo B (cargado después)
decoration {
    rounding = 15    # pisa el 10 del archivo A
    blur {
        enabled = true
        size = 6
    }
}

# Resultado efectivo:
decoration {
    rounding = 15           # de B (último)
    active_opacity = 1.0    # de A (B no lo redefinió)
    blur { enabled = true; size = 6 }
}
```

Esto es exactamente lo que hace el patrón JaKooLit: `configs/` pone defaults, `UserConfigs/` añade o pisa selectivamente.

---

## 9. Hot reload y autoreload

Hyprland vigila todos los archivos cargados vía `source` (y el `hyprland.conf` principal) con `inotify`. Cuando detecta un cambio en disco:

1. Re-parsea todo el árbol de configuración desde `hyprland.conf`.
2. Aplica los cambios sin reiniciar la sesión.
3. Los `exec-once` **no se re-ejecutan**.
4. Los `exec` (sin `-once`) **sí se re-ejecutan**.
5. Los `bind` se recalculan — keybinds nuevos se activan, borrados desaparecen.

**Flujo de trabajo recomendado**:
1. Edita el archivo en `UserConfigs/`.
2. Guarda → Hyprland recarga automáticamente en ~1s.
3. Si el cambio no se aplica, revisar log: `journalctl --user -u hyprland -n 50`.

---

## 10. `hyprctl keyword` — probar cambios en caliente

Para experimentar con valores **sin editar archivos** y sin esperar reload:

```bash
# Sintaxis general
hyprctl keyword <categoria>:<clave> <valor>

# Ejemplos concretos
hyprctl keyword general:gaps_in 8
hyprctl keyword decoration:rounding 15
hyprctl keyword general:col.active_border "rgba(ff6600ee)"
hyprctl keyword cursor:zoom_factor 1.5
hyprctl keyword misc:disable_hyprland_logo false

# Categoría anidada (blur dentro de decoration)
hyprctl keyword decoration:blur:size 10
hyprctl keyword decoration:blur:passes 4

# Ver el valor actual de una opción
hyprctl getoption general:gaps_in
hyprctl getoption decoration:rounding
```

> `hyprctl keyword` es temporal — dura hasta el próximo reload. Para persistir, edita el archivo.

**Batch** (múltiples cambios de golpe, más eficiente):
```bash
hyprctl --batch "keyword general:gaps_in 8 ; keyword general:gaps_out 16 ; keyword decoration:rounding 12"
```

Tu `Keybinds.conf` usa esto en el zoom del escritorio:
```hyprlang
bindd = $mainMod ALT, mouse_down, zoom in, exec, hyprctl keyword cursor:zoom_factor "..."
```

---

## 11. Otros archivos notables en tu estructura

| Archivo | Propósito |
|---|---|
| `wallust/wallust-hyprland.conf` | Generado por wallust con variables `$color0`–`$color15` del wallpaper |
| `monitors.conf` | Reglas de monitor (`monitor = ,preferred,auto,1`) |
| `workspaces.conf` | Reglas de workspace (actualmente vacío) |
| `animations/` | Presets de animación seleccionables con el script `Animations.sh` |
| `Monitor_Profiles/` | Perfiles de monitor alternativos |
| `application-style.conf` | Estilos de aplicación (Qt/GTK theming) |
| `initial-boot.sh` | Script ejecutado una vez al inicio (antes que cualquier `source`) |

---

## 12. Transición a Lua en 0.55

En Hyprland 0.55, la config principal pasó de `hyprland.conf` (hyprlang) a `hyprland.lua` (Lua estándar). El API cambia:

```lua
-- lua equivalente de bloques
hl.config.general.gaps_in = 5
hl.config.decoration.rounding = 10

-- env vars
hl.env("QT_QPA_PLATFORM", "wayland;xcb")

-- exec-once
hl.exec_once("waybar")

-- source
require("UserConfigs.UserSettings")   -- o dofile(...)

-- bind
hl.bind({ "SUPER" }, "Return", "exec", "kitty")
```

**Tu estado actual**: JaKooLit 0.55.3 todavía usa hyprlang. Mientras funcione, no hay urgencia de migrar. Cuando migres, el proceso es reescribir `hyprland.conf` → `hyprland.lua` manteniendo la misma lógica de dos capas.

---

## Conexiones

- [[00_README]]
- [[Recetas_Config]]
- [[MOC_Hyprland]]
