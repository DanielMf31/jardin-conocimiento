---
title: Window Rules y Workspace Rules en Hyprland
date: 2026-06-12
tags: [programacion/linux, programacion/hyprland, programacion/wayland]
type: nota
status: permanente
source: claude-code
aliases: [window rules hyprland, windowrule, workspace rules, reglas de ventana]
---

# Window Rules y Workspace Rules en Hyprland

## Concepto fundamental

Una **window rule** es una instrucción que Hyprland evalua **cada vez que una ventana es creada** (o, en algunos casos, cuando cambia de estado). Si la ventana cumple los criterios del *matcher*, se aplica la acción. No son estados persistentes que tú ajustas manualmente: son automatizaciones declarativas.

- Las reglas se procesan **de arriba a abajo**. La última coincidencia gana cuando hay conflicto.
- Una sola ventana puede activar múltiples reglas a la vez (se acumulan).
- Son reactivas: si abres Spotify siempre va al workspace 4, sin que tengas que recordarlo.

> **Trampa de version critica**: desde Hyprland >= 0.53 la sintaxis usa el prefijo `match:` con el **matcher primero**. La sintaxis vieja (`windowrulev2 = accion, class:regex`) ya no es valida en 0.55.x.

---

## Sintaxis 0.55 — estructura general

```hyprlang
windowrule = match:<campo> <valor>[match:<campo2> <valor2>...], <accion> [parametros]
```

**Partes:**
1. `match:<campo> <valor>` — uno o mas criterios de coincidencia separados por coma
2. `<accion> [parametros]` — lo que se aplica si coincide todo

Ejemplos minimos:

```hyprlang
# Un solo matcher, una accion
windowrule = match:class ^(Spotify)$, workspace 4 silent

# Dos matchers (AND logico — ambos deben cumplirse)
windowrule = match:class ^([Ss]team)$ match:title negative:(Steam), float on

# Matcher de tag (etiqueta previa)
windowrule = match:tag settings, float on, center on
```

### Formato de bloque (para reglas complejas con nombre)

Para reglas largas o que quieres nombrar, puedes usar sintaxis de bloque:

```hyprlang
windowrule {
    name = Picture-in-Picture
    match:title = ^(Picture-in-Picture)$
    float = on
    pin = on
    move = 72% 7%
    size = (monitor_w*0.3) (monitor_h*0.3)
    opacity = 0.95 0.75
    keep_aspect_ratio = on
}
```

---

## Matchers — campos disponibles

| Campo | Tipo de valor | Descripcion |
|---|---|---|
| `class` | regex | Clase WM de la ventana (`hyprctl clients` → campo `class`) |
| `title` | regex | Titulo de la ventana en el momento de evaluacion |
| `initialClass` | regex | Clase al inicio (no cambia aunque la app la modifique) |
| `initialTitle` (o `initial_title`) | regex | Titulo al inicio |
| `tag` | glob o regex | Etiqueta asignada previamente con `tag +<nombre>` |
| `xwayland` | `0` / `1` | Es una app XWayland |
| `floating` | `0` / `1` | Esta flotando actualmente |
| `fullscreen` | `0` / `1` | Esta en pantalla completa |
| `pinned` | `0` / `1` | Esta pineada (siempre visible) |
| `focus` | `0` / `1` | Tiene el foco actualmente |
| `workspace` | ID numerico o `name:<nombre>` | Esta en ese workspace |
| `onworkspace` | ID, `name:`, o selector | Selector de workspace avanzado |

### Regex en matchers

Los matchers de texto aceptan expresiones regulares POSIX extendidas:

```hyprlang
# Exacto (recomendado para class)
match:class ^(Spotify)$

# Case-insensitive con alternativas
match:class ^([Ff]irefox|org.mozilla.firefox)$

# Cualquier cosa que empiece con "jetbrains-"
match:class ^(jetbrains-.+)$

# Negativo — NO coincide con ese patron
match:title negative:(Steam)
```

**Regla practica**: para `class` usa siempre `^(valor-exacto)$` para evitar coincidencias parciales inesperadas. Para `title`, a veces conviene sin anclas si el titulo es dinamico.

---

## Tags — etiquetas para agrupar apps

El sistema de tags permite asignar categorias a ventanas y luego aplicar reglas a toda la categoria:

```hyprlang
# PASO 1 — Asignar tag (normalmente al inicio del archivo)
windowrule = match:class ^([Ff]irefox|org.mozilla.firefox)$, tag +browser
windowrule = match:class ^(kitty|Alacritty)$, tag +terminal

# PASO 2 — Aplicar regla al tag (puede estar en otro archivo)
windowrule = match:tag browser, opacity 0.99 0.8
windowrule = match:tag terminal, opacity 0.9 0.7
```

Ventajas: anadir una nueva app al grupo `browser` solo requiere una linea de tag; no hay que duplicar todas las reglas de opacity, workspace, etc.

---

## Acciones — catalogo completo

### Posicion y geometria

| Accion | Parametros | Ejemplo |
|---|---|---|
| `float on/off` | — | `float on` |
| `tile` | — | fuerza modo tileado |
| `center on/off` | — | centra la ventana flotante |
| `move` | `x y` (px o %) | `move 100 50` / `move 72% 7%` |
| `size` | `w h` (px, %, o `monitor_w/h*factor`) | `size 800 600` / `size (monitor_w*0.7) (monitor_h*0.6)` |
| `minsize` | `w h` | tamano minimo |
| `maxsize` | `w h` | tamano maximo |
| `keep_aspect_ratio on/off` | — | mantiene proporcion al redimensionar |

**Variables de monitor en `size`/`move`:**
- `monitor_w` — ancho del monitor activo
- `monitor_h` — alto del monitor activo

### Workspace

| Accion | Parametros | Descripcion |
|---|---|---|
| `workspace` | `N` | mueve al workspace N al crear |
| `workspace N silent` | — | mueve sin cambiar el foco al workspace N |
| `workspace name:codigo` | — | workspace por nombre |

```hyprlang
# Spotify al workspace 9, sin robar el foco
windowrule = match:class ^(Spotify)$, workspace 9 silent
```

### Visibilidad y comportamiento

| Accion | Parametros | Descripcion |
|---|---|---|
| `pin on/off` | — | ventana siempre visible en todos los workspaces |
| `fullscreen` | `0` (maximize) / `1` (fullscreen real) | fuerza modo fullscreen |
| `no_focus on/off` | — | la ventana nunca recibe foco automatico |
| `no_initial_focus on/off` | — | no recibe foco al crearse (util para tooltips de IDEs) |
| `stayfocused` | — | no pierde foco si se hace clic fuera |
| `group` | `set` / `lock` / `new` / `barred` / `deny` | controla comportamiento de grupos |

### Apariencia

| Accion | Parametros | Descripcion |
|---|---|---|
| `opacity` | `activo [inactivo]` | `opacity 0.9 0.7` (activo=0.9, inactivo=0.7) |
| `no_blur on/off` | — | desactiva el blur para esta ventana |
| `rounding` | numero | radio de esquinas en px (sobreescribe global) |
| `bordercolor` | color(es) | `bordercolor rgba(ff0000ff)` |
| `bordersize` | numero | grosor del borde en px |
| `nodim` | — | no se oscurece al perder foco |
| `noanim` | — | sin animaciones para esta ventana |

### Comportamiento del sistema

| Accion | Parametros | Descripcion |
|---|---|---|
| `idle_inhibit` | `none` / `always` / `focus` / `fullscreen` | inhibe el idle/screensaver |
| `suppressevent` | `fullscreen` / `maximize` / `activatefocus` / `activate` | ignora ciertos eventos de la ventana |
| `xray on/off` | — | la ventana no aplica blur a lo de detras |
| `immediate` | — | fuerza presentacion directa (sin VRR) |

---

## Como obtener class y title de una ventana

**Este paso es obligatorio antes de escribir cualquier regla.**

```bash
# Metodo 1: listar todas las ventanas abiertas
hyprctl clients

# Metodo 2: JSON para parsear con jq
hyprctl clients -j | jq '.[] | {class: .class, title: .title, initialClass: .initialClass}'

# Metodo 3: clase de la ventana con foco activo
hyprctl activewindow | grep -E "class|title"
```

Salida de `hyprctl clients` relevante:
```
Window ... -> titulo de ventana:
    at: 960,540
    class: Spotify          <-- usa esto en match:class
    title: Spotify Premium  <-- usa esto en match:title
    initialClass: Spotify   <-- clase al lanzar
    ...
```

> Para apps con clase variable (ej: chromium apps instaladas), usa `match:initialClass` — es mas estable que `class`.

---

## Workspace Rules

Las workspace rules definen **comportamiento por defecto de un workspace**, independientemente de que ventana haya en el.

```hyprlang
workspace = <selector>, <opcion>:<valor>, <opcion>:<valor>...
```

### Selectores de workspace

| Selector | Ejemplo | Que selecciona |
|---|---|---|
| Numero | `1` | workspace con ID 1 |
| Nombre | `name:codigo` | workspace nombrado "codigo" |
| Rango | `r[2-5]` | workspaces 2 al 5 |
| Monitor | `m[DP-1]` o `m[desc:Samsung...]` | todos los ws de ese monitor |
| Con ventanas tileadas | `w[t1]` | ws con al menos 1 ventana tileada |

### Opciones disponibles

| Opcion | Tipo | Descripcion |
|---|---|---|
| `monitor` | nombre/desc | fija el ws a un monitor especifico |
| `default` | `true`/`false` | ws por defecto al conectar un monitor |
| `persistent` | `true`/`false` | el ws existe aunque este vacio |
| `layout` | `dwindle`/`master` | layout por defecto |
| `gapsin` | numero | gaps internos (entre ventanas) |
| `gapsout` | numero | gaps externos (con borde del monitor) |
| `border` | `true`/`false` | muestra bordes de ventana |
| `bordersize` | numero | grosor de borde |
| `rounding` | `true`/`false` | esquinas redondeadas |
| `decorate` | `true`/`false` | decoraciones (sombras, blur) |
| `shadow` | `true`/`false` | sombras |
| `defaultName` | string | nombre que aparece en la barra |

### Ejemplos practicos

```hyprlang
# Workspace 1 siempre en monitor principal, siempre existe
workspace = 1, monitor:HDMI-A-1, persistent:true, default:true

# Workspace gaming: sin gaps, sin bordes, fullscreen directo
workspace = name:gaming, gapsin:0, gapsout:0, border:false, rounding:false

# Workspace coding: layout master por defecto
workspace = name:codigo, layout:master, monitor:DP-1

# Workspaces 7-9: sin decoraciones (para rendimiento)
workspace = r[7-9], decorate:false, shadow:false
```

---

## Layer Rules

Las layer rules se aplican a **capas del compositor** (barras, launchers, notificaciones, overlays), no a ventanas normales.

```hyprlang
layerrule = match:namespace <namespace>, <accion>
```

### Namespaces comunes (KooL dotfiles)

| Namespace | Componente |
|---|---|
| `rofi` | Lanzador Rofi |
| `notifications` | Centro de notificaciones (swaync) |
| `quickshell:overview` | Overview de Quickshell |
| `waybar` | Barra Waybar |
| `hyprpicker` | Color picker |

### Acciones de layer rules

```hyprlang
# Blur en el launcher
layerrule = match:namespace rofi, blur on

# Blur en notificaciones con umbral de alpha
layerrule = match:namespace notifications, blur on
layerrule = match:namespace quickshell:overview, ignore_alpha 0.5

# Desactivar animaciones en una capa
layerrule = match:namespace waybar, noanim
```

---

## Recetario practico

### Spotify al workspace 9, sin robar foco

```hyprlang
windowrule = match:class ^(Spotify)$, workspace 9 silent
```

### Calculadora: flotante, centrada, tamano fijo

```hyprlang
windowrule = match:class ^(org.gnome.Calculator|qalculate-gtk)$, float on
windowrule = match:class ^(org.gnome.Calculator|qalculate-gtk)$, center on
windowrule = match:class ^(org.gnome.Calculator|qalculate-gtk)$, size 400 600
```

O condensado con tags:

```hyprlang
windowrule = match:class ^(org.gnome.Calculator|qalculate-gtk)$, tag +calc
windowrule = match:tag calc, float on, center on, size 400 600
```

### Navegador al workspace 2

```hyprlang
# Asumiendo que ya tienes el tag +browser definido (como en KooL)
windowrule = match:tag browser, workspace 2 silent
```

### Opacidad diferenciada activo/inactivo por categoria

```hyprlang
windowrule = match:tag terminal, opacity 0.95 0.75
windowrule = match:tag browser, opacity 1.0 0.85
windowrule = match:tag projects, opacity 0.95 0.80
```

> `opacity <activo> <inactivo>` — el segundo valor se aplica cuando la ventana pierde el foco.

### Picture-in-Picture flotante, pineado, esquina superior derecha

```hyprlang
windowrule {
    name = Picture-in-Picture
    match:title = ^(Picture-in-Picture)$
    float = on
    pin = on
    move = 72% 7%
    size = (monitor_w*0.28) (monitor_h*0.28)
    opacity = 1.0 0.85
    keep_aspect_ratio = on
}
```

### Dialogo de una app — no robar foco, flotante

```hyprlang
# Popups de VSCode que no son la ventana principal
windowrule = match:class (codium|VSCodium) match:title negative:(.*codium.*|.*VSCodium.*), float on
```

### Inhibir idle en pantalla completa

```hyprlang
windowrule = idle_inhibit fullscreen, match:class ^(.*)$
```

### App de sistema siempre en monitor secundario

```hyprlang
workspace = name:monitoreo, monitor:HDMI-A-2
windowrule = match:class ^(gnome-system-monitor)$, workspace name:monitoreo silent
```

---

## Orden de prioridades y depuracion

**Regla de precedencia**: se procesan de arriba a abajo; la ultima coincidencia para una misma accion gana. Para acciones acumulativas (como multiples tags), se acumulan todas.

**Depurar reglas que no funcionan:**

```bash
# Ver todas las ventanas con sus datos
hyprctl clients -j | jq '.[] | {class, title, workspace: .workspace.name}'

# Ver reglas activas para la ventana con foco
hyprctl activewindow

# Recargar config sin reiniciar
hyprctl reload

# Ver errores de parsing en el log
journalctl --user -u hyprland -f
# O:
cat ~/.local/share/hyprland/hyprland.log | grep -i "error\|warn"
```

**Errores frecuentes:**

| Problema | Causa probable | Solucion |
|---|---|---|
| La regla no se aplica | Regex incorrecta | Verificar con `hyprctl clients` el class exacto |
| La regla se aplica a ventanas que no quieres | Regex demasiado amplia | Anadir `^(` y `)$` para anclar |
| `workspace N silent` roba foco igual | El `silent` requiere que el ws no este activo | Confirmar que no tienes ese ws abierto |
| Tooltip/popup de IDE recibe foco | Falta `no_initial_focus` | Anadir regla con `match:class ^(jetbrains-.+)$, no_initial_focus on` |
| App xwayland no obedece `size` | Algunas apps XWayland ignoran resize externo | Probar con `suppressevent maximize` |

---

## Donde editar en KooL dotfiles

| Archivo | Proposito |
|---|---|
| `~/.config/hypr/UserConfigs/WindowRules.conf` | **Tus reglas personales** — edita aqui |
| `~/.config/hypr/configs/WindowRules.conf` | Defaults y ejemplos de KooL — no editar directamente |

Flujo recomendado:
1. Lanzar la app objetivo
2. `hyprctl clients | grep -A5 "class"` para anotar el `class` exacto
3. Abrir `UserConfigs/WindowRules.conf`
4. Anadir la regla con la sintaxis `match:`
5. `hyprctl reload`
6. Verificar comportamiento

---

## Conexiones

- [[00_README]]
- [[Recetas_Config]]
- [[MOC_Hyprland]]
