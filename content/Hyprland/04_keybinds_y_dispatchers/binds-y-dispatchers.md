---
title: Keybinds y Dispatchers en Hyprland
date: 2026-06-12
tags: [programacion/linux, programacion/hyprland, programacion/wm]
type: nota
status: permanente
source: claude-code
aliases: [hyprland binds, hyprland keybinds, bind dispatcher hyprland, submaps hyprland]
---

# Keybinds y Dispatchers en Hyprland

## Idea central

Un keybind en Hyprland tiene tres partes: **la combinacion de teclas** que lo activa, **el dispatcher** que describe *que accion ejecutar*, y **los argumentos** que parametrizan esa accion. Dominar estos tres elementos permite controlar el WM completamente desde el teclado.

---

## Nota de version: hyprlang vs Lua

Desde Hyprland 0.55 el formato oficial de config es **Lua** (`hl.bind(...)`). Sin embargo, el formato **hyprlang** (`.conf` con `bind = ...`) sigue funcionando por compatibilidad hacia atras — Hyprland carga `hyprland.conf` si no encuentra `hyprland.lua`. Los dotfiles KooL usan hyprlang; todo lo documentado aqui usa esa sintaxis, que es la que tienes activa en `~/.config/hypr/`.

---

## Anatomia de un bind (hyprlang)

```
bind[FLAGS] = MODIFICADORES, TECLA, DISPATCHER, ARGUMENTOS
```

| Campo | Descripcion | Ejemplo |
|---|---|---|
| `FLAGS` | Letras pegadas a `bind` que alteran el comportamiento | `e`, `l`, `d`, `r`, `m`, `n` |
| `MODIFICADORES` | Teclas de modificacion separadas por espacio | `SUPER SHIFT`, `CTRL ALT`, `` (vacio = sin mod) |
| `TECLA` | Nombre xkb del keysym, keycode (`code:10`) o tecla de media | `Q`, `Return`, `mouse:272`, `xf86audioraisevolume` |
| `DISPATCHER` | Accion que Hyprland ejecutara | `exec`, `killactive`, `workspace` |
| `ARGUMENTOS` | Parametros del dispatcher (puede estar vacio) | `kitty`, `1`, `l` |

### Ejemplo real del config KooL

```ini
bindd = $mainMod, Return, Open terminal, exec, $term
#       ^^^^^^^^^  ^^^^^  ^^^^^^^^^^^^  ^^^^  ^^^^^
#       modifiers  tecla  descripcion   dsp   args
```

La variante `bindd` agrega un cuarto campo entre la tecla y el dispatcher: la **descripcion** en texto libre. El script `KeyHints.sh` de KooL la usa para generar la hoja de atajos con `$mainMod H`.

---

## Variantes y flags

Los flags se escriben como letras inmediatamente despues de `bind`, sin espacio ni separador. Pueden combinarse en cualquier orden.

| Variante/Flag | Letra | Comportamiento |
|---|---|---|
| `bind` | — | Estandar: dispara al pulsar la tecla |
| `bindd` | `d` | Igual que `bind` + lleva descripcion textual |
| `binde` | `e` | **Repeat**: se repite mientras la tecla permanece presionada |
| `bindl` | `l` | **Locked**: actua incluso con input inhibitor activo (pantalla de bloqueo) |
| `bindm` | `m` | **Mouse**: bind de raton; usa un argumento menos (no tiene dispatcher de texto) |
| `bindr` | `r` | **Release**: dispara al *soltar* la tecla, no al presionar |
| `bindn` | `n` | **Non-consuming**: el evento de tecla pasa ademas a la ventana activa |

Los flags se combinan libremente. Ejemplos del config KooL:

```ini
# e + l + d = repeat + locked + description (teclas de volumen)
bindeld = , xf86audioraisevolume, volume up, exec, $scriptsDir/Volume.sh --inc

# l + d = locked + description (media keys en pantalla de bloqueo)
bindld = , xf86AudioPlayPause, play/pause, exec, $scriptsDir/MediaCtrl.sh --pause

# e + d = repeat + description (resize de ventanas)
binded = $mainMod SHIFT, left, resize left (-50), resizeactive, -50 0

# m + d = mouse + description (mover/redimensionar con raton)
bindmd = $mainMod, mouse:272, move window, movewindow
bindmd = $mainMod, mouse:273, resize window, resizewindow
```

---

## Modificadores disponibles

| Nombre en config | Tecla fisica |
|---|---|
| `SUPER` | Tecla Windows / Command |
| `SHIFT` | Shift |
| `CTRL` o `CONTROL` | Control |
| `ALT` | Alt izquierdo |
| `ALT_R` | Alt Gr (derecho) |
| `SUPER_L` / `SUPER_R` | Super izquierdo / derecho (para bindr sobre mod solo) |
| `` (vacio) | Sin modificador |

En los dotfiles KooL: `$mainMod = SUPER`. Combinaciones tipicas: `$mainMod SHIFT`, `$mainMod CTRL`, `$mainMod ALT`, `CTRL ALT`.

---

## Como averiguar el nombre de una tecla

### wev (Wayland Event Viewer)

La herramienta recomendada para Wayland. Instala con:

```bash
sudo apt install wev    # Ubuntu/Debian
```

Ejecuta `wev` en una terminal, pulsa la tecla y lee la salida:

```
[14:     wl_keyboard] key: serial: ..., time: ..., key: 28, state: 1 (pressed)
                       sym: t            (0x74), utf8: 't'
```

El campo `sym:` es el **keysym xkb** — ese es el nombre que va en el config. El campo `key:` es el keycode raw.

### Keycodes directos

Si el keysym falla (por ejemplo con teclas de teclados no-QWERTY), usa el keycode prefijado con `code:`:

```ini
# Los numericos 1-9 en QWERTY tienen keycodes 10-19
bindd = $mainMod, code:10, workspace 1, workspace, 1
bindd = $mainMod, code:11, workspace 2, workspace, 2
```

### Teclas de media

Se referencian por nombre xkb sin `XF86` mayuscula en algunos casos. KooL usa minusculas mixtas:

```ini
, xf86audioraisevolume, ...
, xf86AudioPlayPause, ...
, xf86Sleep, ...
, xf86Rfkill, ...
```

Ambas capitalizaciones suelen funcionar. Si hay dudas, `wev` muestra el nombre exacto.

---

## Catalogo de dispatchers

### Ventanas

| Dispatcher | Argumentos | Descripcion |
|---|---|---|
| `exec` | comando (shell) | Ejecuta un comando via `sh -c` |
| `killactive` | — | Cierra la ventana activa con gracia (SIGTERM) |
| `togglefloating` | — | Alterna flotante/tiled en la ventana activa |
| `fullscreen` | `0` (fullscreen) / `1` (maximize) | Pantalla completa o maximizado |
| `fakefullscreen` | — | Fullscreen visual sin cambiar estado interno |
| `pseudo` | — | Pseudo-tiling (dwindle): reserva espacio pero no ocupa todo |
| `centerwindow` | — | Centra la ventana flotante en la pantalla |
| `pin` | — | Fija la ventana en todos los workspaces (como "always on top" global) |
| `resizeactive` | `dx dy` (pixeles, negativos=encoge) | Redimensiona la ventana activa |
| `movewindow` | `l/r/u/d` | Mueve la ventana en la disposicion tiled |
| `swapwindow` | `l/r/u/d` | Intercambia la ventana activa con la vecina |
| `setprop` | `prop valor` | Modifica una propiedad dinamica de la ventana |
| `bringactivetotop` | — | Sube la ventana activa al tope del z-order |
| `cyclenext` | — | Cicla el foco a la siguiente ventana |

### Workspaces

| Dispatcher | Argumentos | Descripcion |
|---|---|---|
| `workspace` | selector | Salta al workspace indicado (ver tabla de selectores) |
| `movetoworkspace` | selector | Mueve la ventana activa al workspace y salta ahi |
| `movetoworkspacesilent` | selector | Mueve la ventana al workspace *sin* saltar |
| `togglespecialworkspace` | nombre (opcional) | Alterna el workspace especial (scratchpad) |
| `movecurrentworkspacetomonitor` | `l/r/u/d` | Mueve el workspace actual al monitor en esa direccion |

### Foco y monitores

| Dispatcher | Argumentos | Descripcion |
| --- | --- | --- |
| `movefocus` | `l/r/u/d` | Mueve el foco en esa direccion |
| `focusmonitor` | nombre / direccion | Mueve el foco a otro monitor |

### Grupos (tabs)

| Dispatcher | Argumentos | Descripcion |
|---|---|---|
| `togglegroup` | — | Crea/destruye un grupo con la ventana activa |
| `changegroupactive` | `f` (forward) / `b` (back) | Cicla entre ventanas del grupo |
| `moveintogroup` | `l/r/u/d` | Mueve la ventana activa al grupo en esa direccion |
| `moveoutofgroup` | — | Saca la ventana activa de su grupo |
| `lockgroups` | `lock/unlock/toggle` | Bloquea el grupo (no acepta nuevas ventanas) |

### Layouts (Master/Dwindle)

| Dispatcher | Argumentos | Descripcion |
|---|---|---|
| `layoutmsg` | mensaje | Envia mensaje al layout activo |
| `pseudo` | — | Toggle pseudo-tiling (solo Dwindle) |

Mensajes de `layoutmsg` para **Master Layout**:

| Mensaje | Efecto |
|---|---|
| `swapwithmaster` | Intercambia la ventana activa con el master |
| `addmaster` | Promueve la ventana al area master |
| `removemaster` | Degrada la ventana del area master |
| `orientationleft/right/top/bottom/center` | Cambia la orientacion del master |

Ejemplos reales del config KooL:

```ini
bindd = $mainMod CTRL, D, remove master, layoutmsg, removemaster
bindd = $mainMod, I,    add master,      layoutmsg, addmaster
bindd = $mainMod CTRL, Return, swap with master, layoutmsg, swapwithmaster
```

### Submaps

| Dispatcher | Argumentos | Descripcion |
|---|---|---|
| `submap` | nombre / `reset` | Entra al submap indicado o vuelve al global con `reset` |

### Sistema

| Dispatcher | Argumentos | Descripcion |
|---|---|---|
| `exit` | — | Cierra Hyprland |
| `pass` | clase de ventana (regex) | Reenvía el shortcut a una ventana concreta |
| `dpms` | `on/off/toggle [monitor]` | Enciende/apaga monitores (DPMS) |

---

## Selectores de workspace

| Selector | Ejemplo | Significado |
|---|---|---|
| ID absoluto | `1`, `5`, `10` | Workspace con ese numero |
| Relativo | `+1`, `-1`, `+3` | Relativo al workspace actual |
| Relativo en monitor | `m+1`, `m-1` | Siguiente/anterior en el mismo monitor |
| Entre abiertos | `e+1`, `e-1` | Cicla solo entre workspaces que tienen ventanas |
| Por nombre | `name:Web` | Workspace con ese nombre |
| Anterior | `previous` | Workspace en el que estabas antes |
| Primero vacio | `empty` | Primer workspace sin ventanas |
| Especial | `special`, `special:magic` | Workspace scratchpad |

Ejemplos del config KooL:

```ini
# Scroll con raton cicla entre workspaces abiertos
bindd = $mainMod, mouse_down, next workspace,     workspace, e+1
bindd = $mainMod, mouse_up,   previous workspace, workspace, e-1

# Tab salta al siguiente workspace del monitor
bindd = $mainMod, tab,       next workspace,     workspace, m+1
bindd = $mainMod SHIFT, tab, previous workspace, workspace, m-1
```

---

## Submaps: modos de teclado

Un submap es un modo modal donde se activa un conjunto alternativo de binds y se desactivan los globales. Es el equivalente a los "modes" de i3/Sway.

### Patron basico

```ini
# 1. Bind que entra al submap
bind = $mainMod ALT, R, submap, resize

# 2. Declaracion del submap
submap = resize

# Binds dentro del submap (binde = repeat para que funcione manteniendo pulsado)
binde = , right, resizeactive,  50  0
binde = , left,  resizeactive, -50  0
binde = , up,    resizeactive,  0 -50
binde = , down,  resizeactive,  0  50

# Salida OBLIGATORIA - sin esto quedas atrapado
bind = , escape, submap, reset

# 3. Fin del submap
submap = reset
```

**Regla critica:** todo submap debe tener al menos un bind de salida (`submap, reset`). Si te quedas atrapado: `hyprctl dispatch submap reset` desde otra terminal o tty.

### Submap para pasar teclado a VM

Del archivo `UserKeybinds.conf` de KooL (comentado, listo para activar):

```ini
# Entra en modo passthrough: todas las teclas van a la VM
bind = $mainMod ALT, P, submap, passthru
submap = passthru
# La misma combo sale del modo
bind = $mainMod ALT, P, submap, reset
submap = reset
```

### Submap de "modo limpio" (deshabilita todos los binds temporalmente)

```ini
bind = $mainMod, F12, submap, clean
submap = clean
bind = $mainMod, F12, submap, reset
submap = reset
```

---

## Binds de raton

Con el flag `m` (`bindm`) el bind usa la posicion del raton en lugar de una tecla, y no lleva dispatcher de texto:

```ini
# Mover ventana arrastrando con SUPER + boton izquierdo
bindmd = $mainMod, mouse:272, move window,   movewindow
# Redimensionar arrastrando con SUPER + boton derecho
bindmd = $mainMod, mouse:273, resize window, resizewindow
```

Codigos de botones: `272` = LMB, `273` = RMB, `274` = MMB.

---

## Tres ejemplos de binds propios utiles

### 1. Captura de pantalla con seleccion de area (ya en KooL, muestra el patron)

```ini
bindd = $mainMod SHIFT, Print, screenshot area, exec, $scriptsDir/ScreenShot.sh --area
```

### 2. Workspace especial como scratchpad rapido

```ini
# Mueve la ventana activa al scratchpad sin seguirla
bindd = $mainMod SHIFT, U, move to special, movetoworkspace, special
# Toggle: lo muestra/oculta en el monitor actual
bindd = $mainMod, U, toggle special,      togglespecialworkspace,
```

### 3. Zoom de escritorio con scroll (ya en KooL, patron tipico)

```ini
bindd = $mainMod ALT, mouse_down, zoom in,  exec, hyprctl keyword cursor:zoom_factor \
  "$(hyprctl getoption cursor:zoom_factor | awk 'NR==1{f=$2; if(f<1)f=1; print f*2.0}')"
bindd = $mainMod ALT, mouse_up,   zoom out, exec, hyprctl keyword cursor:zoom_factor \
  "$(hyprctl getoption cursor:zoom_factor | awk 'NR==1{f=$2; if(f<1)f=1; print f/2.0}')"
```

---

## Flujo de trabajo: anadir un bind propio

1. Abre `~/.config/hypr/UserConfigs/UserKeybinds.conf`
2. Si vas a reasignar una combo existente, primero desvinculala:
   ```ini
   unbind = $mainMod, Return, Open terminal, exec, $term
   ```
3. Escribe el nuevo bind usando `bindd` (incluye descripcion para que aparezca en `$mainMod H`):
   ```ini
   bindd = $mainMod, Return, Open terminal, exec, ghostty
   ```
4. Recarga la config: `hyprctl reload` (o `$mainMod ALT R` en KooL).
5. Verifica con `hyprctl binds | grep -i "Return"` que el bind se registro.

> **Atencion:** los binds son case-sensitive para `unbind`. `unbind = ..., Tab` != `unbind = ..., tab`.

---

## Referencia rapida: combos KooL por defecto

| Combo | Accion |
|---|---|
| `SUPER + Return` | Terminal (`$term`) |
| `SUPER + D` | App launcher (rofi) |
| `SUPER + Q` | Cerrar ventana activa |
| `SUPER + H` | Hoja de atajos (KeyHints.sh) |
| `SUPER + SPACE` | Toggle flotante |
| `SUPER + SHIFT + F` | Fullscreen |
| `SUPER + CTRL + F` | Maximize (fullscreen 1) |
| `SUPER + G` | Toggle grupo |
| `SUPER + Tab` | Cambiar pestaña en grupo |
| `SUPER + P` | Toggle pseudo (Dwindle) |
| `SUPER + U` | Toggle workspace especial |
| `SUPER + flechas` | Mover foco |
| `SUPER + CTRL + flechas` | Mover ventana (tiled) |
| `SUPER + ALT + flechas` | Swap ventana |
| `SUPER + SHIFT + flechas` | Redimensionar |
| `SUPER + [1-0]` | Ir al workspace 1-10 |
| `SUPER + SHIFT + [1-0]` | Mover ventana a workspace 1-10 |
| `SUPER + CTRL + [1-0]` | Mover silenciosamente a workspace 1-10 |
| `ALT + Tab` | Ciclar siguiente ventana |
| `CTRL + ALT + L` | Bloquear pantalla |
| `CTRL + ALT + Delete` | Salir de Hyprland |

---

## Conexiones

- [[00_README]]
- [[MOC_Hyprland]]
