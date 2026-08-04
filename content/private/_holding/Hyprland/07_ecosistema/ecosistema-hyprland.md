---
title: El ecosistema de Hyprland
date: 2026-06-12
tags: [programacion/linux, programacion/hyprland, wayland, ricing]
type: nota
status: permanente
source: claude-code
aliases: [ecosistema hyprland, piezas hyprland, hyprland stack, desktop stack wayland]
---

# El ecosistema de Hyprland

## Idea central

Hyprland es **solo el compositor**: gestiona ventanas, renderiza en Wayland y expone el protocolo. El "escritorio" no existe como entidad monolítica; se ensambla manualmente con herramientas independientes, cada una haciendo una sola cosa (filosofía Unix). Si vienes de GNOME o KDE, este concepto es el mayor cambio mental: **no hay escritorio, hay piezas**.

Esto tiene consecuencias prácticas: si falta una pieza (p. ej. no lanzas `swww-daemon`), el fondo de pantalla simplemente no aparece. Si no lanzas `hypridle`, la pantalla nunca se bloquea sola. Cada pieza es opcional y reemplazable.

---

## Mapa del ecosistema

| Pieza | Categoría | Qué resuelve | Config en KooL/JaKooLit |
|---|---|---|---|
| **waybar** | Barra de estado | Mostrar info del sistema y del WM | `~/.config/waybar/` |
| **rofi** | Lanzador de apps | Buscar y abrir aplicaciones | `~/.config/rofi/` |
| **swww** | Fondo de pantalla | Renderizar wallpaper con transiciones | invocado desde scripts |
| **swaync** | Notificaciones | Recibir y gestionar notificaciones | `~/.config/swaync/` |
| **hyprlock** | Bloqueo de pantalla | Pantalla de bloqueo nativa Hypr | `~/.config/hypr/hyprlock.conf` |
| **hypridle** | Gestión de inactividad | Disparar acciones tras N segundos idle | `~/.config/hypr/hypridle.conf` |
| **wlogout** | Menú de sesión | Apagar / reiniciar / suspender / cerrar sesión | `~/.config/wlogout/` |
| **grim + slurp** | Capturas de pantalla | Capturar pantalla completa o región | invocados por `ScreenShot.sh` |
| **cliphist + wl-copy** | Portapapeles | Historial de portapapeles persistente | invocados desde `Startup_Apps.conf` |
| **hyprcursor** | Cursores | Tema de cursor nativo para Wayland/Hypr | `ENVariables.conf` |
| **xdg-desktop-portal-hyprland** | Portales XDG | Compartir pantalla, selector de archivos | `PortalHyprland.sh` |
| **nwg-look / qt5ct** | Temas de apps | Aplicar temas GTK/Qt a apps gráficas | herramientas externas |
| **wallust** | Theming dinámico | Extraer paleta del wallpaper y propagarla | `~/.config/wallust/` |
| **polkit** | Autenticación | Diálogos de permisos de root | `Polkit.sh` |

---

## Las piezas en detalle

### waybar — la barra de estado

**Qué hace.** Es una barra de estado configurable para Wayland. Muestra módulos: workspaces, reloj, volumen, batería, red, reproductor multimedia, etc. Se comunica con Hyprland vía socket para mostrar el workspace activo en tiempo real.

**Por qué es una pieza aparte.** Hyprland no tiene barra nativa. Cualquier barra compatible con Wayland funciona (también eww, ags, Quickshell…). waybar es la más extendida por su equilibrio entre configurabilidad y complejidad.

**Dónde vive su config (KooL).** `~/.config/waybar/` tiene una estructura extensa:
- `configs/` — múltiples layouts predefinidos (TOP, BOT, LEFT, RIGHT y combinaciones). En KooL se cambia el layout activo con el script `WaybarLayout.sh` que usa rofi para seleccionar.
- `style/` — hojas CSS para el aspecto visual. Hay decenas de estilos incluidos; se cambia con `WaybarStyles.sh`.
- `Modules`, `ModulesCustom`, `ModulesGroups`, `ModulesVertical` — archivos de módulos reutilizables.
- `wallust/colors-waybar.css` — colores generados automáticamente por wallust al cambiar wallpaper.

**Cómo se lanza.** `exec-once = waybar` en `configs/Startup_Apps.conf`. Cuando se quiere recargar (p. ej. tras cambiar estilo) se usa `Refresh.sh` o `WaybarStyles.sh`.

---

### rofi — el lanzador

**Qué hace.** Muestra un selector de texto interactivo (dmenu con esteroides). Se usa para: lanzar apps (`rofi -show drun`), cambiar ventanas (`-show window`), portapapeles (`cliphist list | rofi -dmenu`), scripts de configuración de KooL, emoji picker, calculadora, y más.

**Por qué es una pieza aparte.** Hyprland no incluye ningún lanzador. rofi es la alternativa más potente; existe también wofi (nativo Wayland, más simple) y fuzzel (minimalista). En KooL se usa rofi con backend Wayland.

**Dónde vive su config (KooL).** `~/.config/rofi/`:
- `config.rasi` — configuración principal.
- `config-clipboard.rasi`, `config-emoji.rasi`, `config-keybinds.rasi`… — configs específicas por uso.
- `themes/KooL_style-*.rasi` — más de 15 temas visuales seleccionables con `RofiThemeSelector.sh`.
- `wallust/colors-rofi.rasi` — paleta dinámica generada por wallust.

**Uso práctico.** Los scripts de KooL (`ClipManager.sh`, `RofiEmoji.sh`, `KeyBinds.sh`…) todos invocan `rofi -dmenu` con un `-config` apuntando al `.rasi` específico.

---

### swww — fondo de pantalla

**Qué hace.** Renderiza imágenes como fondo de pantalla en Wayland con soporte de transiciones animadas (fade, wipe, grow, etc.). Funciona en modo cliente-servidor: el daemon `swww-daemon` corre en background; el cliente `swww img <path>` le ordena cambiar el wallpaper.

**Por qué es una pieza aparte.** Wayland no tiene concepto de "fondo de escritorio"; hace falta una surface especial en la capa `background`. swww crea esa surface. Alternativa nativa del ecosistema: `hyprpaper` (más simple, sin animaciones, configurado vía `hyprpaper.conf`).

**Dónde vive su config (KooL).** No tiene archivo de config propio; se controla enteramente con argumentos de línea de comandos. En KooL:
- `exec-once = swww-daemon --format xrgb` en `Startup_Apps.conf` arranca el daemon.
- `WallpaperSelect.sh`, `WallpaperRandom.sh`, `WallpaperEffects.sh` son los scripts que llaman a `swww img`.
- `~/.config/hypr/wallpaper_effects/.wallpaper_current` — ruta del wallpaper activo (también usada por hyprlock).
- `WallustSwww.sh` — aplica wallust para regenerar colores tras cambiar wallpaper.

---

### swaync — notificaciones

**Qué hace.** Es el demonio de notificaciones: recibe notificaciones via D-Bus (protocolo `org.freedesktop.Notifications`), las muestra en pantalla y las acumula en un centro de notificaciones (un panel lateral que se abre/cierra). También incluye widgets de "quick settings" configurables (toggles de WiFi, Bluetooth, modo no molestar, etc.).

**Por qué es una pieza aparte.** Wayland no tiene sistema de notificaciones incorporado. Es necesario un proceso que implemente el protocolo D-Bus. En KooL se usa swaync en vez de mako (más simple) o dunst (legacy X11, port Wayland). swaync es más rico en funcionalidades.

**Dónde vive su config (KooL).** `~/.config/swaync/`:
- `config.json` — configuración del comportamiento (posición, timeout, widgets del panel).
- `style.css` — aspecto visual.
- `icons/` e `images/` — recursos gráficos usados en las notificaciones de los scripts.

**Cómo se lanza.** `exec-once = swaync` en `Startup_Apps.conf`. Los scripts de KooL llaman a `notify-send` (que swaync intercepta) para notificar al usuario de acciones (captura guardada, volumen cambiado, etc.).

---

### hyprlock — bloqueo de pantalla

**Qué hace.** Bloquea la sesión mostrando una pantalla personalizable con fondo (wallpaper actual o screenshot), reloj, campo de contraseña y etiquetas con info del sistema (usuario, batería, uptime, clima…).

**Por qué es una pieza aparte.** El bloqueo de pantalla no es responsabilidad del compositor; es un proceso separado que crea una surface de capa `overlay` que captura toda la entrada. hyprlock es la solución oficial del ecosistema Hypr, diseñada para funcionar sin fricciones con Hyprland. Alternativa: `swaylock`.

**Dónde vive su config (KooL).**
- `~/.config/hypr/hyprlock.conf` — configuración principal (< 1080p).
- `~/.config/hypr/hyprlock-2k.conf` — variante para resoluciones ≥ 1440p.
- El archivo carga `source = ~/.config/hypr/wallust/wallust-hyprland.conf` para usar los colores del wallpaper activo.
- El fondo apunta a `wallpaper_effects/.wallpaper_current`.
- Etiquetas configuradas: fecha, hora (formato 12h), usuario, teclado activo, batería, uptime, clima (desde cache `~/.cache/.weather_cache`).

**Cómo se activa.** `LockScreen.sh` llama a `loginctl lock-session`, que hypridle también llama tras el timeout. `hypridle.conf` tiene en el bloque `general`: `lock_cmd = pidof hyprlock || hyprlock`.

---

### hypridle — gestión de inactividad

**Qué hace.** Monitoriza la inactividad del usuario (sin teclado ni ratón) y dispara comandos configurables cuando se superan umbrales de tiempo. También reacciona a `before_sleep_cmd` (antes de suspender) y `after_sleep_cmd` (al reanudar).

**Por qué es una pieza aparte.** Hyprland no gestiona ahorro de energía ni bloqueo automático. hypridle es el daemon oficial del ecosistema Hypr para esto. Alternativa: `swayidle`.

**Dónde vive su config (KooL).** `~/.config/hypr/hypridle.conf`:

```
general {
    lock_cmd = pidof hyprlock || hyprlock
    before_sleep_cmd = loginctl lock-session
    after_sleep_cmd = hyprctl dispatch dpms on
}
listener { timeout = 540;  on-timeout = notify-send "...idle!" }   # 9 min → aviso
listener { timeout = 600;  on-timeout = loginctl lock-session }    # 10 min → bloqueo
# (comentados) timeout 630 → dpms off;  timeout 1200 → systemctl suspend
```

**Cómo se lanza.** `exec-once = hypridle` en `Startup_Apps.conf`. El script `Hypridle.sh` permite activarlo/desactivarlo desde waybar o el menú rápido (`pkill hypridle` o relanzarlo).

---

### wlogout — menú de sesión

**Qué hace.** Muestra una pantalla de pantalla completa con botones para: cerrar sesión, bloquear, suspender, hibernar, reiniciar y apagar. Es una capa Wayland (`layer-shell`) que ocupa toda la pantalla.

**Por qué es una pieza aparte.** No existe un menú de apagado en Hyprland. Cualquier solución basada en X11 (como los de XFCE o GNOME) no funcionaría correctamente. wlogout implementa `wlr-layer-shell-unstable`.

**Dónde vive su config (KooL).**
- `~/.config/wlogout/layout` — define los botones y sus acciones.
- `~/.config/wlogout/style.css` — aspecto visual.
- `~/.config/wlogout/icons/` — iconos de los botones (lock, logout, power, restart, sleep, hibernate).
- `Wlogout.sh` — wrapper que detecta la resolución del monitor activo y ajusta parámetros `-T` y `-B` (margen superior e inferior) para que los botones escalen bien en cualquier resolución.

---

### grim + slurp — capturas de pantalla

**Qué hace cada uno.**
- `grim` — captura toda la pantalla (o una región con `-g`) y escribe a stdout o archivo.
- `slurp` — muestra un selector de región interactivo en pantalla; imprime las coordenadas a stdout.

Se usan juntos en pipe: `grim -g "$(slurp)" archivo.png`.

**Por qué son dos herramientas separadas.** En Unix, composición de herramientas simples. `grim` solo sabe capturar; `slurp` solo sabe seleccionar una región. Cada una puede usarse sola (captura completa sin selección, o selección para otro propósito).

**Dónde vive su config (KooL).** `~/.config/hypr/scripts/ScreenShot.sh` orquesta todos los modos:

| Flag | Comportamiento |
|---|---|
| `--now` | Captura pantalla completa, copia al portapapeles |
| `--area` | Selección con slurp, guarda y copia |
| `--win` | Captura ventana activa (coordenadas desde `hyprctl activewindow`) |
| `--active` | Captura ventana activa, nombra el archivo con la clase de la app |
| `--swappy` | Selección con slurp, abre en swappy para anotar |
| `--in5` / `--in10` | Captura completa con cuenta atrás de 5/10 segundos |

Tras capturar, el script notifica con `notify-send` y ofrece acciones (Abrir / Eliminar). Las capturas se guardan en `~/Pictures/Screenshots/`.

---

### cliphist + wl-copy — historial de portapapeles

**Qué hace.** En Wayland el portapapeles es efímero: si cierras la app que copió algo, el contenido desaparece. `cliphist` resuelve esto:
- `wl-paste --watch cliphist store` — escucha el portapapeles y guarda cada copia nueva en `~/.cache/cliphist/db`.
- `cliphist list | rofi -dmenu | cliphist decode | wl-copy` — flujo para seleccionar una entrada del historial y pegarla.

`wl-copy` / `wl-paste` son las herramientas CLI de `wl-clipboard` para interactuar con el portapapeles Wayland.

**Dónde vive su config (KooL).**
```
# En Startup_Apps.conf:
exec-once = wl-paste --type text --watch cliphist store
exec-once = wl-paste --type image --watch cliphist store
```
`ClipManager.sh` usa rofi con `config-clipboard.rasi`. Atajos: `Ctrl+Del` para borrar una entrada, `Alt+Del` para limpiar todo el historial.

---

### hyprcursor — cursores nativos

**Qué hace.** Es el formato de tema de cursor nativo de Hyprland. A diferencia de los cursores Xcursor (formato legacy de X11), hyprcursor usa SVG vectoriales a múltiples escalas, lo que evita el problema de cursores borrosos en monitores HiDPI o con escalado fraccional.

**Por qué es una pieza aparte.** Los temas de cursor en Wayland se configuran mediante variables de entorno; cada toolkit (GTK, Qt, XWayland) los interpreta por su cuenta. hyprcursor añade una capa por encima que Hyprland entiende directamente.

**Dónde vive su config (KooL).** En `configs/ENVariables.conf`:
```
env = HYPRCURSOR_THEME,Bibata-Modern-Ice
env = HYPRCURSOR_SIZE,24
```
El tema `Bibata-Modern-Ice` necesita tener su variante hyprcursor instalada (los temas hyprcursor se colocan en `~/.local/share/icons/` igual que los Xcursor, pero con la carpeta `hyprcursors/` dentro).

---

### xdg-desktop-portal-hyprland — los portales

**Qué hace.** Implementa la especificación XDG Desktop Portal para Hyprland. Los "portales" son interfaces D-Bus que permiten a las aplicaciones sandboxed (Flatpak, apps de escritorio) acceder a recursos del sistema de forma controlada:
- **Compartir pantalla** (`ScreenCast`) — lo que usa Google Meet, OBS, etc.
- **Selector de archivos** (`FileChooser`) — el diálogo nativo de "Abrir archivo".
- **Capturas de pantalla** (`Screenshot`).
- **Apariencia** (`Settings`) — notifica a las apps el tema oscuro/claro.

**Por qué es una pieza aparte.** El sistema de portales es independiente del compositor; cada compositor necesita su implementación. `xdg-desktop-portal-hyprland` (xdph) es la implementación oficial para Hyprland. Sin él, compartir pantalla en videollamadas simplemente no funciona.

**Dónde vive su config (KooL).** `scripts/PortalHyprland.sh` — script que mata cualquier portal previo (incluidos el de GNOME o el de wlr que puedan estar corriendo) y lanza xdph + `xdg-desktop-portal`. En `Startup_Apps.conf` la línea está comentada porque normalmente systemd lo arranca automáticamente:
```
#exec-once = $scriptsDir/PortalHyprland.sh
```
Se activa manualmente si hay problemas con compartir pantalla.

---

### nwg-look + qt5ct/qt6ct — temas de apps GTK y Qt

**Qué hace.** Las apps de escritorio (GTK3, GTK4, Qt5, Qt6) usan sus propios sistemas de temas. En GNOME/KDE hay un daemon que propaga el tema automáticamente. En Hyprland hay que configurarlo manualmente.

- **nwg-look** — GUI para configurar el tema GTK (equivalente a `lxappearance` pero nativo Wayland). Escribe en `~/.config/gtk-3.0/settings.ini` y `~/.config/gtk-4.0/settings.ini`.
- **qt5ct / qt6ct** — apps de configuración para temas Qt (estilo, fuentes, iconos). Activadas con `env = QT_QPA_PLATFORMTHEME,qt5ct` en `ENVariables.conf`.
- **Kvantum** — motor de temas SVG para Qt. `~/.config/Kvantum/` está presente en la instalación.

**Por qué son piezas aparte.** Cada toolkit tiene su propio sistema de temas. No hay un mecanismo unificado en Wayland. La coherencia visual (que GTK y Qt tengan el mismo aspecto) requiere configurar ambos por separado.

---

### wallust — theming dinámico desde el wallpaper

**Qué hace.** Analiza el wallpaper activo, extrae una paleta de colores dominantes y genera archivos de configuración de color para múltiples herramientas, actualizando el tema de todo el escritorio automáticamente al cambiar el fondo.

**Por qué es una pieza aparte.** Es una capa de automatización, no una funcionalidad del WM. Alternativa más conocida: `pywal` (Python, más lento). wallust está escrito en Rust.

**Dónde vive su config (KooL).** `~/.config/wallust/wallust.toml` define:
- `backend = "kmeans"` — algoritmo de extracción de colores.
- `palette = "dark16"` — esquema de colores (dark, light, harddark…).
- `[templates]` — mapeo de plantillas a destinos. Al correr `wallust run <imagen>` regenera:
  - `~/.config/hypr/wallust/wallust-hyprland.conf` — colores para Hyprland y hyprlock.
  - `~/.config/rofi/wallust/colors-rofi.rasi` — colores para rofi.
  - `~/.config/waybar/wallust/colors-waybar.css` — colores para waybar.
  - `~/.config/kitty/kitty-themes/01-Wallust.conf` — tema para kitty.
  - `~/.config/ghostty/wallust.conf` — tema para ghostty.
  - `~/.config/quickshell/qml_color.json` — colores para quickshell.

El script `WallustSwww.sh` combina `swww img` con `wallust run` para cambiar wallpaper y tema en un solo paso.

---

### polkit — autenticación de privilegios

**Qué hace.** Cuando una app necesita permisos de root (p. ej. montar un disco, cambiar la red), lanza un diálogo de contraseña. En entornos de escritorio completos (GNOME) hay un agente polkit integrado. En Hyprland hay que lanzar uno manualmente.

**Por qué es una pieza aparte.** Sin agente polkit activo, las apps que necesiten elevación de privilegios fallan silenciosamente o muestran errores de D-Bus.

**Dónde vive su config (KooL).** `scripts/Polkit.sh` detecta qué agente polkit está disponible (`/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1`, `/usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1`, o `lxpolkit`) y lanza el primero que encuentre. Se ejecuta con `exec-once = $scriptsDir/Polkit.sh` en `Startup_Apps.conf`.

---

## Cómo todo se integra: el arranque

El arranque del escritorio sigue este flujo, orquestado desde `hyprland.conf` y `Startup_Apps.conf`:

```
Hyprland arranca
 ├── exec-once = dbus-update-activation-environment ...   ← propaga vars a D-Bus/systemd
 ├── exec-once = swww-daemon --format xrgb              ← daemon de wallpaper
 ├── exec-once = swaync                                  ← demonio de notificaciones
 ├── exec-once = waybar                                  ← barra de estado
 ├── exec-once = hypridle                                ← daemon de inactividad
 ├── exec-once = Polkit.sh                               ← agente de autenticación
 ├── exec-once = nm-applet + nm-tray                     ← bandeja de red
 ├── exec-once = wl-paste --watch cliphist store (x2)    ← historial portapapeles
 ├── exec-once = Dropterminal.sh kitty                   ← terminal dropdown precargado
 ├── exec-once = Hyprsunset.sh init                      ← temperatura de color
 └── exec-once = KeybindsLayoutInit.sh                   ← inicializa layout de teclado
```

xdg-desktop-portal-hyprland normalmente lo arranca systemd automáticamente; hay un script manual de rescate (`PortalHyprland.sh`) si falla.

---

## Variables de entorno clave (ENVariables.conf)

Las variables de entorno son el pegamento entre las piezas y el toolkit subyacente:

| Variable | Valor | Efecto |
|---|---|---|
| `XDG_CURRENT_DESKTOP` | `Hyprland` | Identifica el DE para apps y portales |
| `XDG_SESSION_TYPE` | `wayland` | Fuerza modo Wayland en apps |
| `GDK_BACKEND` | `wayland,x11,*` | GTK prefiere Wayland, cae a X11 |
| `QT_QPA_PLATFORM` | `wayland;xcb` | Qt prefiere Wayland |
| `QT_QPA_PLATFORMTHEME` | `qt5ct` / `qt6ct` | Gestores de tema Qt activos |
| `HYPRCURSOR_THEME` | `Bibata-Modern-Ice` | Tema de cursor nativo Hypr |
| `HYPRCURSOR_SIZE` | `24` | Tamaño del cursor |
| `MOZ_ENABLE_WAYLAND` | `1` | Firefox en modo Wayland nativo |
| `ELECTRON_OZONE_PLATFORM_HINT` | `auto` | VSCode y apps Electron en Wayland |

---

## Tabla de archivos de referencia rápida

| Necesito cambiar... | Archivo/script |
|---|---|
| Layout o estilo de la barra | `WaybarLayout.sh` / `WaybarStyles.sh` |
| Wallpaper | `WallpaperSelect.sh` (selección) / `WallpaperRandom.sh` |
| Tema de colores | `WallustSwww.sh` (wallpaper + tema) |
| Cuando se bloquea la pantalla | `~/.config/hypr/hypridle.conf` (timeouts) |
| Aspecto de la pantalla de bloqueo | `~/.config/hypr/hyprlock.conf` |
| Tema de cursor | `configs/ENVariables.conf` → `HYPRCURSOR_THEME` |
| Tema rofi | `RofiThemeSelector.sh` |
| Tema GTK | `nwg-look` (GUI) |
| Tema Qt | `qt5ct` / `qt6ct` (GUI) |
| Botones del menú de apagado | `~/.config/wlogout/layout` |
| Captura de pantalla | `ScreenShot.sh --area` / `--now` / etc. |
| Portapapeles | `ClipManager.sh` (rofi) |

---

## Errores comunes relacionados con el ecosistema

| Síntoma | Causa probable | Solución |
|---|---|---|
| Fondo negro al iniciar | `swww-daemon` no corriendo o sin wallpaper inicial | Verificar `exec-once = swww-daemon` y script de wallpaper |
| Pantalla nunca se bloquea | `hypridle` no corre | `exec-once = hypridle` en Startup_Apps |
| Compartir pantalla no funciona en videollamadas | xdg-desktop-portal-hyprland falla | Correr `PortalHyprland.sh` manualmente; verificar `XDG_CURRENT_DESKTOP=Hyprland` |
| Apps GTK ignoraron el tema oscuro | nwg-look no aplicado o falta `GTK_THEME` | Correr `nwg-look`, guardar cambios |
| Cursor borroso en HiDPI | Usando tema Xcursor sin variante hyprcursor | Instalar versión hyprcursor del tema, configurar `HYPRCURSOR_THEME` |
| Portapapeles vacío al cerrar una app | `cliphist` no corriendo | Verificar `wl-paste --watch cliphist store` en Startup_Apps |
| Diálogos de autenticación no aparecen | Sin agente polkit | Verificar `Polkit.sh` en Startup_Apps |

---

## Conexiones

- [[00_README]]
- [[MOC_Hyprland]]
