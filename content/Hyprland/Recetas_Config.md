---
title: Hyprland — Recetas de configuración (vivo)
date: 2026-06-12
tags: [programacion/hyprland, config, recetas]
type: nota
status: en-progreso
source: claude-code
aliases: [recetas hyprland, config hyprland, tweaks]
---

# Hyprland — Recetas de configuración

> Recetario **vivo** de los ajustes concretos que voy aplicando. Cada receta: qué hace, en qué archivo, y el código. **Regla de oro**: siempre edito en `~/.config/hypr/UserConfigs/` (los `configs/` se sobrescriben al actualizar). Aplicar cambios → `hyprctl reload`.

---

## Estructura de la config (KooL)

Dos capas, la tuya gana porque se carga después:
- `~/.config/hypr/configs/` → defaults de KooL. **No tocar** (se sobrescriben al actualizar).
- `~/.config/hypr/UserConfigs/` → **tu capa**. Aquí editas todo. Se conserva.

→ teoría completa en.

---

## Recetas aplicadas (2026-06-12)

### Gaps + borde de color · `UserSettings.conf`
```ini
general {
    gaps_in = 5          # separación ENTRE ventanas
    gaps_out = 12        # separación con el borde de pantalla
    border_size = 2
    col.active_border = rgba(33ccffee) rgba(00ff99ee) 45deg   # degradado en la ventana activa
    col.inactive_border = rgba(595959aa)
}
```
- Color = `rgba(RRGGBBAA)`, dos colores + ángulo = degradado.

### Ventanas nuevas a la derecha · `UserSettings.conf`
```ini
dwindle {
    force_split = 2      # 0=auto · 1=izq/arriba · 2=der/abajo
}
```

### Apps en su workspace al iniciar · `Startup_Apps.conf`
```ini
exec-once = [workspace 1 silent] kitty
exec-once = [workspace 2 silent] google-chrome-stable
exec-once = [workspace 5 silent] code
exec-once = [workspace 4 silent] spotify
```
- `[workspace N silent]` = ábrelo en el ws N sin saltar la vista.

### Spotify siempre en el ws4 · `WindowRules.conf`
```ini
windowrule = match:class ^(Spotify)$, workspace 4 silent
```
- ⚠️ **Sintaxis 0.55**: `windowrule = match:<campo> <valor>, <acción>` (el `match:` PRIMERO). La sintaxis vieja `windowrule = <acción>, class:^(X)$` ya **no** vale.
- Para saber el `class` de una app: `hyprctl clients`.

→ más reglas en.

### WhatsApp (PWA Chrome) siempre en ws5 · `WindowRules.conf`
```ini
windowrule = match:class ^(chrome-hnpfjngllnobngcgfapefoaidbinmjnm-Default)$, workspace 5 silent
```

### Obsidian siempre en ws3 · `Startup_Apps.conf` + `WindowRules.conf`
```ini
exec-once = [workspace 3 silent] obsidian
windowrule = match:class ^(obsidian)$, workspace 3 silent
```

### Atajo propio: abrir Google · `UserKeybinds.conf`
```ini
bind = $mainMod SHIFT, B, exec, google-chrome-stable --new-window https://www.google.com
```
- `bind = MODS, TECLA, exec, COMANDO`. Antes verifica que la tecla esté libre (SHIFT+G ya era "game mode" de KooL).
- Para mover la ventana enfocada a otro workspace: **SUPER+SHIFT+\<número\>** (`movetoworkspace`).

---

## Fixes / gotchas

- **Errores de config al instalar** (`misc:vfr`, `dwindle:pseudotile`, `togglesplit`): opciones que 0.55 renombró/quitó. Comentadas. →.
- **Terminal nueva "se pone encima"**: era el **scratchpad** (ws especial -98) visible. SUPER+SHIFT+Enter lo oculta y el tiling vuelve a la normalidad. No era un fallo de config.

---

## Conexiones
- [[00_README]] · [[00_Dudas_y_Preguntas]] · [[MOC_Hyprland]]

### Visualizador cava junto a Spotify (ws4) · `Startup_Apps.conf` + `UserKeybinds.conf`
```ini
# Arranque: cava grande en el ws4 (al lado de Spotify)
exec-once = [workspace 4 silent] kitty --class cava -o font_size=20 cava
# Atajo para abrirlo rápido donde estés
bind = $mainMod SHIFT, V, exec, kitty --class cava -o font_size=20 cava
```
- cava = visualizador de espectro (FFT del audio que suena). Corre en una kitty; `font_size` grande = barras más gordas.

### ⚠️ Lección: colocar apps por workspace al iniciar
El prefijo `exec-once = [workspace N silent] app` **falla con apps que se re-lanzan en otro proceso** (Chrome, Electron/VS Code): Hyprland pierde la pista del PID y la ventana cae en el workspace activo. **Solución fiable**: regla de ventana por clase.
```ini
windowrule = match:class ^(google-chrome)$, workspace 2 silent
windowrule = match:class ^(code)$, workspace 5 silent
```
- Clase de VS Code = `code` (minúscula). Verifica siempre con `hyprctl clients`.
- Apps "normales" (kitty) sí funcionan con el prefijo; las raras necesitan regla.

### Lector de libros Foliate (PDF/EPUB) en ws7
```ini
# Regla: Foliate siempre al workspace 7 (cada libro abre en su propia ventana)
windowrule = match:class ^(com\.github\.johnfactotum\.Foliate)$, workspace 7 silent
```
- Foliate instalado por Flatpak (`com.github.johnfactotum.Foliate`) + `flatpak override --user --filesystem=home`.
- Por defecto para `application/pdf` y `application/epub+zip` (`xdg-mime default`).
- Gestor de archivos cambiado a **Nautilus** (SUPER+E). Biblioteca en `~/Libros` (SUPER+SHIFT+L).

### Widget Pomodoro en waybar
- Script: `~/.config/hypr/UserScripts/Pomodoro.sh` (status/toggle/reset/skip; estado en `~/.cache/pomodoro.state`).
- Módulo `custom/pomodoro` en `~/.config/waybar/UserModules`, añadido a `modules-left` del bar activo.
- CSS (rojo trabajo / verde descanso) en `style.css`. Clic=iniciar/pausar, der=reset, medio=saltar. 25/5, largo 15 cada 4.

### Widget flotante Pomodoro (Python+GTK) en ws7
- App: `~/.config/hypr/UserScripts/pomodoro_widget.py` (GTK3). Comparte estado con la barra vía `Pomodoro.sh` (set/toggle/reset/skip).
- Reglas (clase `pomodoro-widget`): `float on`, `size 420 360`, `center on`, `workspace 7 silent`.
- Toggle: `pomodoro_widget_toggle.sh` → **SUPER+SHIFT+D**.
- ⚠️ Sintaxis 0.55: las reglas booleanas son `float on` / `center on` (con "on"), no `float`/`center` a secas.

### Widget flotante Vinilo (now playing, Python+GTK+cairo)
- App: `~/.config/hypr/UserScripts/vinyl_widget.py`. Coge la carátula vía `playerctl` (mpris:artUrl), la descarga y la pinta como disco que **gira con cairo mientras suena** (se para al pausar). Título/artista + controles ⏮⏯⏭.
- Reglas (clase `vinyl-widget`): `float on`, `size 300 440`, `center on` (sin workspace fijo → aparece donde estés).
- Toggle: `vinyl_widget_toggle.sh` → **SUPER+SHIFT+Y**.

### Vinilo v2: flotante, disco + cava, fluido
- Ahora **flotante** (no fullscreen): `float on`, `size 720 480`, `center on`.
- Incorpora **cava integrado** (lee `~/.config/cava/config-raw` en modo raw/ascii y dibuja las barras al lado del disco).
- **Fluidez**: los metadatos (`playerctl metadata`) se leen en un **hilo aparte** + carátula en hilo → el hilo gráfico (rotación 60 fps) nunca se bloquea.
- ⚠️ Bug que tuve: `playerctl -F` sin el subcomando `metadata` da error de uso → usar `playerctl metadata [--format ...]`.

### Alias de Claude · `.bashrc`
```bash
alias cl='claude'
alias clc='claude --continue'
```

### Vinilo con tamaño condicional (toggle inteligente)
- `vinyl_widget_toggle.sh` cuenta ventanas del workspace activo (`hyprctl activeworkspace -j` → `windows`) ANTES de abrir.
- Solo (0 otras) → grande `resizewindowpixel exact 1720 960` + centrado. Con compañía → pequeño `460 340` en esquina.
- Regla estática solo `float on`; el tamaño/posición lo pone el script con `hyprctl dispatch resizewindowpixel/movewindowpixel ... ,address:$addr`.
- ⚠️ GTK no encoge una ventana por debajo del mínimo de su contenido → bajar los `set_size_request` del disco/cava para poder hacerlo pequeño.

### Alias bóveda + vinilo 50/50
- `.bashrc`: `alias obs='cd <ruta-vault>'` (saltar a la bóveda). Evitar `obsidian` (lanza la app).
- Vinilo: `top = Gtk.Box(..., homogeneous=True)` y `set_size_request` iguales en disco y cava → celdas 50/50 exactas en grande y pequeño.
- ⚠️ Al probar widgets desde un shell efímero, lánzalos con `setsid` (o vía keybind de Hyprland) o mueren por SIGHUP al salir el shell.

### Kitty makeover + grabador de pantalla
- Kitty: `~/.config/kitty/current-theme.conf` (Catppuccin Mocha) + bloque en `kitty.conf` (`include current-theme.conf`, `background_opacity 0.85`, `window_padding_width 12`, pestañas powerline, `cursor_shape beam`). Recargar: `pkill -SIGUSR1 -x kitty`. `cursor_trail` requiere kitty ≥0.36.
- Grabar pantalla: `~/.config/hypr/UserScripts/RecordToggle.sh` (toggle wf-recorder, SIGINT para finalizar el mp4) → guarda en `~/Videos/Grabaciones`. Atajo **SUPER+ALT+G**. Requiere `sudo apt install wf-recorder`. Zona con `wf-recorder -g "$(slurp)"`, audio con `--audio`.

### Widget Sistema Solar (JS + HTML5 Canvas, modo app de Chrome)
- `~/.config/hypr/UserScripts/solar-widget/index.html` (canvas autocontenido: órbitas a velocidad angular ∝ 1/periodo real, sombra día/noche con gradiente, estilo cartoon, slider de velocidad ×0–×5).
- Se abre como **app** con `google-chrome-stable --app=file://.../index.html` (ventana sin pestañas) + `.desktop` "Sistema Solar" en el lanzador.
- Chrome ignora `--class` en modo app → la clase real es `chrome-<ruta>-Default`; capturada con `hyprctl clients` y usada en la regla (`float on`, `size 660 730`, `center on`).
- Toggle: `solar_toggle.sh` (closewindow si abierto, lanzar si no) → **SUPER+ALT+S**.
- 💡 Lección: para widgets GRÁFICOS/animados, JS+Canvas en ventana app de Chrome > Python+GTK (animación, gradientes y iteración visual mucho más fáciles; previsualizas en el navegador). AGS no aporta para canvas.
