---
title: Layouts y gestión de ventanas en Hyprland
date: 2026-06-12
tags: [programacion/hyprland, programacion/linux, programacion/wm]
type: nota
status: permanente
source: claude-code
aliases: [hyprland layouts, dwindle, master layout, tiling hyprland, ventanas hyprland]
---

# Layouts y gestión de ventanas en Hyprland

## Idea central

Hyprland organiza las ventanas mediante dos layouts de tiling intercambiables en caliente
(**dwindle** y **master**), permite estados mixtos (tiled / floating / pseudo / fullscreen),
y ofrece grupos (pestañas) y un special workspace (scratchpad) para trabajo no lineal.
Conocer cómo funciona cada pieza te da control total sobre el espacio de pantalla.

---

## 1. Filosofía: tiling vs floating

| Modo | Cuándo usarlo | Cómo activarlo |
|---|---|---|
| **Tiling** (por defecto) | Trabajo principal: código, terminal, browser | Ventana nace en tiling automáticamente |
| **Floating** | Ventanas auxiliares: calculadoras, diálogos, popups | `SUPER + SPACE` (toggle) |
| **Pseudo** | Ventana ocupa espacio en el grid pero mantiene su tamaño "natural" | `SUPER + P` (toggle) |
| **Fullscreen real** | Juegos, vídeo a pantalla completa, presentaciones | `SUPER + SHIFT + F` |
| **Maximize** | Ver una sola ventana sin ocultar waybar/bordes | `SUPER + CTRL + F` |

**Regla práctica:** en un laptop como el ASUS TUF F15 con una sola pantalla, tiling dwindle
cubre el 90 % del flujo de trabajo. Floating se reserva para lo que necesita posición manual.

---

## 2. Los dos layouts de Hyprland

### 2.1 Dwindle — árbol binario de splits

Dwindle es el layout activo en tu setup (`general { layout = dwindle }`).
Funciona como una **BSP (Binary Space Partition)**: cada ventana nueva divide en dos el
nodo en el que aterriza, creando un árbol binario de rectángulos.

#### Cómo se construye el árbol

```
Ventana 1 sola          + Ventana 2               + Ventana 3
┌────────────────┐      ┌────────┬────────┐      ┌────────┬────┬────┐
│                │      │        │        │      │        │ 2  │ 3  │
│       1        │  →   │   1    │   2    │  →   │   1    ├────┴────┤
│                │      │        │        │      │        │   (free)│
└────────────────┘      └────────┴────────┘      └────────┴─────────┘
```

Con `force_split = 2` (tu config), la ventana nueva va **siempre a la derecha/abajo** del
nodo activo, independientemente del tamaño del contenedor.

#### Opciones clave de dwindle

| Opción | Tipo | Default | Tu valor | Qué hace |
|---|---|---|---|---|
| `force_split` | int | `0` | **`2`** | `0` = sigue al ratón; `1` = siempre izq/arriba; `2` = siempre der/abajo |
| `preserve_split` | bool | `false` | **`true`** | Fija la dirección del split (H o V) aunque cambie el ratio W/H del contenedor |
| `smart_split` | bool | `false` | `false` | Split según triángulo donde está el cursor; activa `preserve_split` implícitamente |
| `default_split_ratio` | float | `1.0` | `1.0` | Ratio inicial del split. `1.0` = 50/50; `[0.1–1.9]` |
| `split_bias` | int | `0` | `0` | `0` = la ventana top/left recibe el ratio; `1` = la ventana activa |
| `special_scale_factor` | float | `1.0` | **`0.8`** | Escala de las ventanas en el special workspace; `0.8` = 80 % |
| `smart_resizing` | bool | `true` | `true` | Al redimensionar con ratón, la dirección depende de qué esquina es más cercana |
| `use_active_for_splits` | bool | `true` | `true` | Usa la ventana activa (no el cursor) como pivote para decidir dónde cae la nueva |

#### force_split en detalle — los 3 valores

```
force_split = 0   (sigue al ratón)
  → La split H/V se decide por el ratio W/H del contenedor en el momento de abrir.
    Si el contenedor es más ancho → split vertical (lado a lado).
    Si es más alto → split horizontal (arriba/abajo).
    Cambia dinámicamente si redimensionas. Sin preserve_split, los splits se reorganizan solos.

force_split = 1   (siempre izquierda/arriba)
  → La ventana nueva ocupa el lado IZQUIERDO o SUPERIOR del split.
    La ventana existente se desplaza a la derecha/abajo.

force_split = 2   (siempre derecha/abajo)  ← TU SETUP
  → La ventana nueva aparece SIEMPRE a la derecha o abajo de la activa.
    La ventana existente permanece donde está.
    Comportamiento predecible: abres terminal → el nuevo panel aparece a su derecha.
```

#### preserve_split — por qué importa

Sin `preserve_split`, dwindle recalcula la dirección del split cada vez que cambias el
tamaño de una ventana. El árbol se "voltea" de forma inesperada. Con `preserve_split = true`
(tu config en `SystemSettings.conf`), la dirección H/V de cada nodo queda **fija** una vez
establecida. Los splits no se reorganizan solos al redimensionar.

#### pseudotile — ventana "fantasma" en el grid

```
Sin pseudo:                    Con pseudo (SUPER + P):
┌──────────┬──────────┐       ┌──────────┬──────────┐
│          │          │       │  ┌────┐  │          │
│    1     │    2     │       │  │ 1  │  │    2     │
│          │          │       │  └────┘  │          │
└──────────┴──────────┘       └──────────┴──────────┘
Ventana 1 llena su mitad.     Ventana 1 ocupa espacio pero
                              mantiene su tamaño natural.
                              El espacio sobrante queda vacío.
```

Útil para aplicaciones que piden un tamaño específico (diálogos de contraseña, ventanas
pequeñas de configuración) sin sacarlas del flujo de tiling.

---

### 2.2 Master Layout — maestro y pila

En el layout master, una o varias ventanas son el **maestro** (zona prominente) y el resto
forman la **pila de esclavos**. Pensado para flujos donde una ventana necesita más espacio
visual permanente (editor principal, browser de referencia).

#### Diagrama de orientaciones

```
orientation = left (default)      orientation = right
┌──────┬──────┬──────┐            ┌──────┬──────┬──────┐
│      │      │      │            │      │      │      │
│MASTER│slave1│slave2│            │slave1│slave2│MASTER│
│      │      │      │            │      │      │      │
└──────┴──────┴──────┘            └──────┴──────┴──────┘

orientation = top                 orientation = center
┌──────────────────────┐          ┌──────┬──────┬──────┐
│       MASTER         │          │      │      │      │
├──────┬──────┬────────┤          │slave1│MASTER│slave2│
│slave1│slave2│ slave3 │          │      │      │      │
└──────┴──────┴────────┘          └──────┴──────┴──────┘
```

#### Opciones clave de master

| Opción | Tipo | Default | Tu valor | Qué hace |
|---|---|---|---|---|
| `mfact` | float | `0.55` | **`0.5`** | Porcentaje de pantalla del maestro. `0.5` = 50/50 |
| `new_status` | string | `"slave"` | **`"master"`** | `"master"` = cada ventana nueva se convierte en maestro; `"slave"` = va a la pila |
| `new_on_top` | bool | `false` | **`true`** | La nueva ventana aparece en la parte superior de la pila |
| `orientation` | string | `"left"` | `"left"` | Posición del área maestra |
| `new_on_active` | string | `"none"` | `"none"` | `"before"`/`"after"` = relativa a la ventana activa |
| `focus_master_on_close` | bool | `false` | `false` | Al cerrar, el foco va al maestro |
| `drop_at_cursor` | bool | `true` | `true` | Al arrastrar, la ventana cae donde está el cursor |

#### Cambiar entre layouts en caliente

Tu dotfiles tiene `SUPER + ALT + L` que llama al script `ChangeLayout.sh`, el cual alterna
entre dwindle y master sin reiniciar Hyprland. Los keybinds de J/K también se reconfiguran
dinámicamente mediante `KeybindsLayoutInit.sh`.

---

## 3. Estados de una ventana

### 3.1 Tabla de estados

| Estado | Descripción | Toggle / cómo llegar |
|---|---|---|
| **Tiled** | Gestionada por el layout activo | Estado por defecto al abrir |
| **Floating** | Posición y tamaño libres, por encima del tiling | `SUPER + SPACE` |
| **Pseudo** | En el árbol pero con tamaño natural | `SUPER + P` |
| **Fullscreen real** (modo 2) | Ocupa toda la pantalla, sin bordes ni waybar | `SUPER + SHIFT + F` |
| **Maximize** (modo 1) | Ocupa el espacio de trabajo, waybar visible | `SUPER + CTRL + F` |
| **Pinned** | Floating que aparece en todos los workspaces | via window rule o dispatcher |

### 3.2 Fullscreen real vs Maximize — la diferencia exacta

Hyprland tiene dos dimensiones de fullscreen desacopladas:

- **Estado interno** (lo que Hyprland hace con la ventana):
  - `0` = normal, `1` = maximize, `2` = fullscreen real, `3` = maximize+fullscreen
- **Estado cliente** (lo que la app cree que está haciendo):
  - Mismo enum. Por defecto ambos se sincronizan.

```bash
# Fullscreen real — pantalla completa, waybar oculto
hyprctl dispatch fullscreen 0   # ó bind: SUPER + SHIFT + F → fullscreen (sin args)

# Maximize — ocupa workspace, waybar visible
hyprctl dispatch fullscreen 1   # ó bind: SUPER + CTRL + F → fullscreen, 1
```

**Caso práctico:** Chromium en modo fullscreen entra en "presentación" y oculta la UI.
Para evitarlo (ver vídeo sin que el browser "sepa" que está en fullscreen):
```bash
# Hyprland lo pone fullscreen pero le dice al cliente que está en modo normal
hyprctl dispatch fullscreenstate 2 0
```

---

## 4. Grupos de ventanas (pestañas en dwindle)

Los grupos convierten varias ventanas en una sola celda del layout, navegable como pestañas.
Son propios de dwindle pero funcionan en cualquier layout.

```
Sin grupo:                      Con grupo (SUPER + G):
┌──────────┬──────────┐        ┌──────────┬──────────┐
│          │          │        │ [A] [B]  │          │
│    A     │    B     │   →    │          │    C     │
│          │          │        │    A     │          │
└──────────┴──────────┘        └──────────┴──────────┘
                                SUPER+Tab: A ↔ B (dentro del grupo)
```

### Keybinds de grupos (tu config)

| Keybind | Dispatcher | Acción |
|---|---|---|
| `SUPER + G` | `togglegroup` | Crear/disolver grupo con la ventana activa |
| `SUPER + Tab` | `changegroupactive f` | Siguiente ventana en el grupo |
| `SUPER + SHIFT + Tab` | `changegroupactive b` | Ventana anterior en el grupo |
| `SUPER + CTRL + K` | `moveintogroup l` | Mover ventana activa al grupo de la izquierda |
| `SUPER + CTRL + L` | `moveintogroup r` | Mover ventana activa al grupo de la derecha |
| `SUPER + CTRL + H` | `moveoutofgroup` | Sacar la ventana activa del grupo |

### Window rules para grupos

```ini
# Abrir app directamente como grupo
windowrule = group set, ^(my-app)$

# Abrir como grupo nuevo (barred: no entrar en grupos existentes)
windowrule = group new, ^(my-app)$

# Prohibir que una ventana entre en un grupo
windowrule = group deny, ^(dialog-app)$
```

---

## 5. Mover, redimensionar e intercambiar ventanas

### 5.1 Tabla de dispatchers de ventana — los más usados

| Dispatcher (hyprlang) | Dispatcher (Lua API) | Descripción |
|---|---|---|
| `movefocus, l/r/u/d` | `hl.dsp.focus({direction})` | Mover el foco en dirección |
| `movewindow, l/r/u/d` | `hl.dsp.window.move({direction})` | Mover ventana en el árbol |
| `swapwindow, l/r/u/d` | `hl.dsp.window.swap({direction})` | Intercambiar posición con la vecina |
| `resizeactive, dx dy` | `hl.dsp.window.resize({x,y,relative=true})` | Redimensionar ventana activa |
| `togglefloating` | `hl.dsp.window.float({action="toggle"})` | Toggle floating |
| `fullscreen [0/1/2]` | `hl.dsp.window.fullscreen({mode,action})` | Cambiar estado fullscreen |
| `pseudo` | `hl.dsp.window.pseudo()` | Toggle pseudotile |
| `killactive` | `hl.dsp.window.close()` | Cerrar ventana (graceful) |
| `movetoworkspace, N` | `hl.dsp.window.move({workspace=N,follow=true})` | Mover + seguir a workspace |
| `movetoworkspacesilent, N` | `hl.dsp.window.move({workspace=N,follow=false})` | Mover sin seguir |
| `cyclenext` | `hl.dsp.window.cycle_next()` | Foco a siguiente ventana |
| `layoutmsg, swapwithmaster` | `hl.dsp.layout("swapwithmaster")` | Intercambiar con maestro (master layout) |
| `splitratio, ±delta` | `hl.dsp.layout("splitratio ±0.1")` | Ajustar ratio del split activo |
| `togglesplit` | `hl.dsp.layout("togglesplit")` | Cambiar split H↔V (requiere preserve_split) |
| `togglegroup` | `hl.dsp.group.toggle()` | Toggle grupo |
| `changegroupactive, f/b` | `hl.dsp.group.next()` / `.prev()` | Navegar en grupo |

> **Nota sobre la API Lua:** desde Hyprland ~0.45+ existe la API Lua para config, pero la
> sintaxis `.conf` (hyprlang) sigue funcionando en 0.55.x. Tu dotfiles KooL/JaKooLit usa
> la sintaxis `.conf` clásica — todo lo de esta tabla aplica directamente.

### 5.2 Tus keybinds de movimiento y redimensión

```ini
# Foco
SUPER + ←/→/↑/↓        → movefocus l/r/u/d

# Mover en el árbol (cambia posición en el tiling)
SUPER + CTRL + ←/→/↑/↓  → movewindow l/r/u/d

# Intercambiar con vecina (swap posiciones)
SUPER + ALT + ←/→/↑/↓   → swapwindow l/r/u/d

# Redimensionar (repeating: mantener pulsado)
SUPER + SHIFT + ←/→/↑/↓  → resizeactive ±50px

# Mover/redimensionar con ratón
SUPER + LMB drag         → movewindow
SUPER + RMB drag         → resizewindow
```

### 5.3 Ajustar el split ratio manualmente

```bash
# Expandir la ventana activa un 10 %
hyprctl dispatch splitratio 0.1

# Encogerla un 10 %
hyprctl dispatch splitratio -0.1

# Fijar ratio exacto al 60/40
hyprctl dispatch splitratio exact 1.2

# En master layout: mfact
hyprctl dispatch layoutmsg "mfact +0.05"
hyprctl dispatch layoutmsg "mfact exact 0.65"
```

Tu config también tiene `SUPER + M` → `splitratio 0.3` para ampliar agresivamente la
ventana activa con una sola tecla.

---

## 6. Navegación de foco

### 6.1 Follow mouse vs teclado

```ini
input {
  follow_mouse = 1   # 0=no sigue, 1=foco sigue al cursor, 2=igual pero sin cambio de workspace
}
```

Tu config tiene `follow_mouse = 1`: mover el ratón sobre una ventana la focaliza
automáticamente. Los keybinds de foco (`SUPER + flechas`) también funcionan en paralelo.

### 6.2 Navegación especial

| Keybind | Dispatcher | Cuándo usarlo |
|---|---|---|
| `ALT + Tab` | `cyclenext` + `bringactivetotop` | Ciclar ventanas floating; sube la activa |
| `SUPER + Tab` | `workspace m+1` | Workspace siguiente en el monitor |
| `SUPER + SHIFT + Tab` | `workspace m-1` | Workspace anterior |
| `SUPER + ,` / `.` | `workspace e+1/e-1` | Siguiente workspace con contenido |

---

## 7. Special Workspace (Scratchpad)

### 7.1 Qué es

El special workspace es un workspace **oculto y global** que se puede mostrar/ocultar sobre
cualquier workspace activo. Equivale al "scratchpad" de i3/sway. Las ventanas que viven ahí
**no cuentan** como ocupadas en el workspace principal y siguen corriendo cuando están ocultas.

```
Workspace 1 (visible)         + Special Workspace (overlay al invocar)
┌─────────────────────────┐   ┌─────────────────────────┐
│  [terminal] [browser]   │   │  ┌───────────────────┐  │
│                         │ → │  │  terminal flotante │  │
│                         │   │  │  (special ws)      │  │
└─────────────────────────┘   │  └───────────────────┘  │
                              └─────────────────────────┘
                              SUPER + U para mostrar/ocultar
```

### 7.2 Por qué las ventanas "flotan apiladas" en el special workspace

Este es un comportamiento que probablemente has encontrado como bug: abres varias ventanas
en el special workspace y aparecen apiladas (una encima de la otra), no en tiling.

**La causa:** el special workspace tiene su propio "mini-layout" pero por defecto las
ventanas se tratan como **floating** dentro de él. El parámetro `special_scale_factor`
en dwindle (`0.8` en tu config) las escala al 80 % del monitor, pero si no hay reglas
explícitas de tiling, cada ventana nueva aterriza centrada encima de la anterior.

**La solución correcta:** añadir una workspace rule para el special workspace:

```ini
# En ~/.config/hypr/UserConfigs/WorkSpaceRules.conf
workspace = special, gapsin:10, gapsout:20, bordersize:2
```

O mover las ventanas al special workspace con `movetoworkspacesilent, special` en lugar
de abrirlas directamente ahí, para que hereden el estado tiled del workspace de origen.

### 7.3 Tus keybinds de special workspace

```ini
SUPER + SHIFT + U  → movetoworkspace, special    # enviar ventana al scratchpad
SUPER + U          → togglespecialworkspace,      # mostrar/ocultar el scratchpad
```

### 7.4 Special workspaces con nombre (múltiples scratchpads)

Puedes tener varios scratchpads con nombre diferente:

```ini
# Enviar a scratchpad "música"
bind = SUPER ALT, M, movetoworkspace, special:musica

# Mostrar/ocultar scratchpad "música"
bind = SUPER, M, togglespecialworkspace, musica

# Workspace rule para ese scratchpad
workspace = special:musica, on-created-empty:spotify
```

Límite: hasta 97 special workspaces simultáneos.

---

## 8. Dispatch messages para layouts (layoutmsg)

El dispatcher `layoutmsg` envía comandos específicos al layout activo.

### Dwindle — mensajes disponibles

| Mensaje | Descripción |
|---|---|
| `splitratio [±delta\|exact N]` | Ajusta el ratio del split. Delta relativo o valor exacto [0.1–1.9] |
| `togglesplit` | Alterna split H↔V. Requiere `preserve_split = true` |
| `swapsplit` | Intercambia los dos sub-árboles del split activo |
| `preselect [l\|r\|u\|d]` | Override one-shot: la próxima ventana abre en esa dirección |
| `movetoroot [window]` | Mueve la ventana a la raíz del árbol del workspace |

### Master — mensajes disponibles

| Mensaje | Descripción |
|---|---|
| `swapwithmaster [master\|child\|auto]` | Intercambia activa con maestro |
| `focusmaster [master\|auto\|previous]` | Focaliza el maestro |
| `addmaster` / `removemaster` | Añade/quita maestros |
| `cyclenext [loop\|noloop]` / `cycleprev` | Navega la pila |
| `swapnext` / `swapprev` | Intercambia con el siguiente/anterior en pila |
| `mfact [±delta\|exact N]` | Cambia el ratio del maestro |
| `orientationleft/right/top/bottom/center` | Cambia la orientación del maestro |
| `orientationcycle [left top right bottom]` | Cicla entre orientaciones específicas |
| `rollnext` / `rollprev` | Rota el siguiente/anterior de la pila al maestro |

```bash
# Ejemplos de uso directo desde terminal:
hyprctl dispatch layoutmsg swapwithmaster
hyprctl dispatch layoutmsg "mfact +0.1"
hyprctl dispatch layoutmsg orientationtop
hyprctl dispatch layoutmsg "preselect r"   # próxima ventana irá a la derecha
```

---

## 9. Resumen visual — flujo de decisión al abrir una ventana

```
¿Qué hago cuando abro una nueva ventana?
                     │
          ¿layout activo?
         /             \
    dwindle            master
       │                  │
  force_split=2        new_status=master (tu config)
  → siempre der/abajo  → nueva ventana = nuevo maestro
       │                  │
  preserve_split=true  mfact=0.5
  → split queda fijo   → 50% para el maestro
       │
  ¿ventana especial?
  /    |    \
float  pseudo  group
SUPER  SUPER   SUPER
+SPC   +P      +G
```

---

## 10. Referencia rápida — keybinds de gestión de ventanas en tu setup

| Keybind | Acción |
|---|---|
| `SUPER + SPACE` | Toggle floating |
| `SUPER + P` | Toggle pseudotile (dwindle) |
| `SUPER + G` | Toggle grupo (pestañas) |
| `SUPER + SHIFT + F` | Fullscreen real |
| `SUPER + CTRL + F` | Maximize |
| `SUPER + Q` | Cerrar ventana |
| `SUPER + flechas` | Mover foco |
| `SUPER + CTRL + flechas` | Mover ventana en el árbol |
| `SUPER + ALT + flechas` | Intercambiar ventana con vecina |
| `SUPER + SHIFT + flechas` | Redimensionar (±50 px, repeating) |
| `SUPER + ALT + L` | Toggle layout dwindle ↔ master |
| `SUPER + M` | splitratio 0.3 (ampliar ventana activa) |
| `SUPER + Tab` | Cambiar ventana activa en grupo (forward) |
| `SUPER + SHIFT + Tab` | Cambiar ventana activa en grupo (back) |
| `SUPER + CTRL + K/L` | Mover ventana dentro de un grupo izq/der |
| `SUPER + CTRL + H` | Sacar ventana del grupo |
| `SUPER + SHIFT + U` | Enviar ventana al special workspace |
| `SUPER + U` | Toggle special workspace (scratchpad) |
| `SUPER + CTRL + Return` | Swap con maestro (master layout) |
| `SUPER + I` | Añadir maestro (master layout) |
| `SUPER + CTRL + D` | Eliminar maestro (master layout) |
| `SUPER + LMB drag` | Mover ventana con ratón |
| `SUPER + RMB drag` | Redimensionar ventana con ratón |

---

## Conexiones

- [[00_README]]
- [[Recetas_Config]]
- [[MOC_Hyprland]]
