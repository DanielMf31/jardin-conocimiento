---
title: Widget Cosmos (hub de simulaciones)
date: 2026-06-13
tags: [programacion/hyprland, programacion/javascript, widgets, canvas]
type: nota
status: en-progreso
source: claude-code
aliases: [Cosmos, widget cosmos, hub simulaciones]
---

# 🌌 Widget Cosmos — hub de simulaciones

> Widget de escritorio propio: una ventana Chrome en modo `--app` (sin bordes) que renderiza
> **escenas/simulaciones** en HTML5 Canvas. Arquitectura modular: cada simulación es un archivo
> independiente que se autorregistra. Vive en `~/.config/hypr/UserScripts/solar-widget/`.

## 🧱 Arquitectura

```
solar-widget/
├── index.html            # carga css + utils + todas las escenas + main.js
├── css/style.css
└── js/
    ├── utils.js          # objeto global SW: registro, helpers, mundo
    ├── main.js           # camara (zoom-fit/pan/zoom), bucle BLINDADO, controles, cache de escenas
    └── scenes/*.js       # una simulacion por archivo: SW.register('Nombre', factory)
```

- **Coordenadas de mundo** centradas en (0,0); `SW.WORLD` (=320) es la extensión de referencia.
  La cámara (centrado contain-fit + arrastre + rueda) la aplica `main.js`; las escenas no tocan
  el tamaño de pantalla.
- **Bucle blindado**: `update`/`draw` van en try/catch; una escena que falle **no tumba al resto**.
- **Cache de escenas**: al cambiar de escena se **conserva su estado** (el laberinto no reinicia, etc.).
- **Sin emojis** en interfaz ni código del widget (regla fija).

### Contrato de una escena
```js
SW.register('Nombre', function () {
  const params = { foo: 50 };                 // valores por defecto de sus controles
  return {
    controls: [ { id:'foo', label:'Foo', min:1, max:100, step:1, value:50 } ], // opcional
    params,                                    // main.js muta params[id] al mover el slider
    update(dt, speed) { /* dt seg; speed = multiplicador global; lee params.foo */ },
    draw(ctx) { /* dibuja en coords de mundo centradas en (0,0) */ },
  };
});
```
Helpers en `SW`: `TAU`, `rand(a,b)`, `clamp(v,a,b)`, `glow(ctx,x,y,r,interno,externo)`,
`makeStars(n)`/`drawStars(ctx,stars)`, `mouse{x,y}` (px pantalla), `worldMouse{x,y}` (coords mundo).

## 🎛️ Controles (barra inferior)
- **Selector** de escena (desplegable; escala a muchas escenas).
- **Velocidad** (slider universal; multiplicador de la simulación).
- **Reset** — recrea la escena activa desde cero.
- **Opciones** — popover con los controles **propios** de la escena activa (de su `controls`).
- Ratón: arrastrar = mover · rueda = zoom · doble clic = centrar. Algunas escenas (péndulo)
  se pueden **agarrar** con el ratón.

## ⌨️ Lanzamiento
- `SUPER+ALT+S` → `solar_toggle.sh`: **toggle** de una instancia (mostrar/ocultar).
- `SUPER+SHIFT+ALT+W` → `widget_menu.sh` (rofi): elige escena → `solar_open.sh` abre una
  **instancia NUEVA** en el workspace actual. **Multi-instancia**: tantos widgets como quieras,
  en cualquier workspace (truco: URL única `?i=timestamp` fuerza ventana nueva en Chrome).
- Regla de flotado por clase: `chrome-.*solar-widget_index.*` en `WindowRules.conf`.

## ✅ Escenas implementadas
Sistema Solar · Agujero Negro · Púlsar · Laberinto (ratón cenital busca queso) · ECG ·
Doble Péndulo (cadena Verlet de N eslabones, arrastrable) · N-Body · Game of Life ·
Tabla Periódica (interactiva) · Boids (con auto-reset si circula).

## 🧪 Ideas / cola de simulaciones (30)

**Física**: 1 Tela/cortina · 2 Fluido 2D · 3 Ondas en agua · 4 Gas de partículas ·
5 Cuna de Newton · 6 Campo magnético · 7 Refracción óptica · 8 Cuerda vibrante ·
9 Tiro parabólico · 10 Slingshot gravitatorio.

**Caos y matemáticas**: 11 Atractor de Lorenz · 12 Curvas de Lissajous · 13 Hormiga de Langton ·
14 Reacción-difusión (Gray-Scott) · 15 Conjunto de Julia · 16 Juego del caos (Sierpinski) ·
17 Mapa logístico · 18 Cuencas magnéticas.

**Vida artificial / biología**: 19 Depredador-presa (Lotka-Volterra) · 20 Colonia de hormigas ·
21 L-systems · 22 Physarum · 23 Epidemia SIR · 24 Banco de peces con depredador.

**Química / materia**: 25 Agregación DLA · 26 Difusión de gases · 27 Autoensamblaje.

**Algoritmos visuales (CS)**: 28 Visualizador de ordenación · 29 Pathfinding A* · 30 Quadtree.

## 🔧 Otros widgets del escritorio
- **Pomodoro** (`pomodoro_widget.py`, GTK) — `SUPER+SHIFT+D`.
- **Vinilo** (`vinyl_widget.py`, GTK; disco girando + barras cava) — `SUPER+SHIFT+Y`.
- Ambos también en el menú rofi de widgets.

## Conexiones
- [[MOC_Hyprland]]
- [[Hyprland/Recetas_Config|Recetas de config]] — keybinds y reglas de ventana aplicadas
