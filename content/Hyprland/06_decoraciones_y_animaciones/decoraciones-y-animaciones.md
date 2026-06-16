---
title: Hyprland — Decoraciones y Animaciones
date: 2026-06-12
tags: [programacion/linux, programacion/hyprland, programacion/wm]
type: nota
status: permanente
source: claude-code
aliases: [hyprland decoraciones, hyprland blur, hyprland animaciones, hyprland rounding, hyprland shadow]
---

# Hyprland — Decoraciones y Animaciones

## Idea central

`decoration { }` controla el aspecto visual de las ventanas (redondeo, opacidad, sombra, desenfoque). `animations { }` controla cómo se mueven y transicionan. Ambos bloques son puramente cosméticos pero tienen coste de GPU; entenderlos te permite equilibrar estética y rendimiento.

---

## 1. El bloque `decoration { }`

En Hyprland ≥ 0.42 (y en la 0.55.x actual) **`blur` y `shadow` son sub-bloques**, no claves planas. La estructura completa es:

```ini
decoration {
    rounding         = 10       # Radio de esquinas en píxeles (0 = sin redondeo)
    active_opacity   = 1.0      # Opacidad ventana activa  (0.0–1.0)
    inactive_opacity = 0.9      # Opacidad ventanas inactivas
    fullscreen_opacity = 1.0    # Opacidad en pantalla completa

    dim_inactive  = true        # Oscurecer ventanas inactivas
    dim_strength  = 0.1         # Intensidad del oscurecimiento (0.0–1.0)
    dim_special   = 0.8         # Oscurecimiento del fondo en workspaces especiales

    shadow {
        enabled        = true
        range          = 3          # Tamaño/radio de la sombra en px
        render_power   = 1          # Nitidez: 1 (suave/difusa) → 4 (dura/nítida)
        color          = rgba(1a1a1aee)   # Color sombra ventana activa
        color_inactive = rgba(1a1a1aaa)   # Color sombra ventanas inactivas
    }

    blur {
        enabled           = true
        size              = 6       # Radio del kernel de blur (px)
        passes            = 3       # Número de pasadas (iteraciones)
        new_optimizations = true    # Optimización GPU de caché; siempre true
        xray              = true    # El blur "traspasa" capas semi-transparentes
        ignore_opacity    = true    # Aplica blur incluso si opacity < 1
        special           = true    # Blur en workspace especial (scratchpad)
        popups            = true    # Blur en popups/tooltips
    }
}
```

### 1.1 Referencia rápida de parámetros

| Parámetro | Tipo | Efecto principal | Notas |
|---|---|---|---|
| `rounding` | int | Radio esquinas en px | 0 desactiva; valores >20 raros |
| `active_opacity` | float | Transparencia foco | 1.0 = opaco |
| `inactive_opacity` | float | Transparencia sin foco | 0.85–0.95 es sutil |
| `dim_inactive` | bool | Atenúa ventanas sin foco | Combinable con `inactive_opacity` |
| `dim_strength` | float | Cuánto atenúa | 0.1–0.3 es lo habitual |
| `shadow.range` | int | Radio de la sombra | Valores grandes (~20) con `render_power` alto = sombra material |
| `shadow.render_power` | int (1–4) | Dispersión de la sombra | 1=muy difusa, 4=casi sin blur |
| `blur.size` | int | Tamaño del kernel | Ver coste abajo |
| `blur.passes` | int | Iteraciones de blur | Ver coste abajo |
| `blur.xray` | bool | Blur "ve a través" | Necesario si usas capas de waybar |

### 1.2 Coste de rendimiento del blur

El blur gaussiano de Hyprland es **separable** (horizontal + vertical por pasada), lo que lo hace eficiente, pero el coste escala así:

```
coste ≈ passes × size²  (aproximado)
```

| Configuración | Coste relativo | Sensación |
|---|---|---|
| size=4, passes=1 | muy bajo | blur sutil, apenas perceptible |
| size=6, passes=3 | moderado | blur notable, buen balance (config KooL) |
| size=8, passes=4 | alto | blur pesado, tipo macOS |
| size=12, passes=5 | muy alto | impacto visible en GPU integrada |

**Consejos de rendimiento:**
- `new_optimizations = true` cachea el resultado del blur entre frames cuando la ventana no se mueve; **actívalo siempre**.
- Si tienes GPU integrada (Intel/AMD iGPU), empieza con `passes=2, size=5`.
- `xray = true` aumenta el coste porque obliga a redibujar capas inferiores, pero es visualmente correcto para paneles semi-transparentes.
- Si el blur causa tearing o lag en `wlr-gamma-control`, prueba desactivar `popups` primero.

---

## 2. El sistema de animaciones

### 2.1 Sintaxis de la línea `animation`

```
animation = NOMBRE, ACTIVO, VELOCIDAD, CURVA [ESTILO]
```

| Campo | Tipo | Descripción |
|---|---|---|
| `NOMBRE` | string | Qué evento anima (ver §2.3) |
| `ACTIVO` | 0 o 1 | 0 desactiva esa animación específica |
| `VELOCIDAD` | float | Duración inversa: **mayor número = más rápido** (≈ 1/décimas de segundo) |
| `CURVA` | string | Nombre de una `bezier` definida previamente (o `default`) |
| `ESTILO` | string | Tipo de movimiento (ver §2.4); algunos eventos no lo admiten |

> Ejemplo: `animation = windows, 1, 6, wind, slide`
> → ventanas activas, habilitado, velocidad 6, curva "wind", estilo slide.

### 2.2 Curvas Bézier cúbicas

```
bezier = nombre, x0, y0, x1, y1
```

Los cuatro valores son los **puntos de control** de una curva cúbica de Bézier, idénticos a los de `cubic-bezier()` en CSS. El punto inicial es siempre (0,0) y el final (1,1); tú defines los dos puntos intermedios.

```
         velocidad
           ▲
        1 -|          ●  (1,1) fin
           |        ╱
           |      ╱   ← la forma de esta curva es lo que defines
           |    ╱
        0 -| ●          → tiempo normalizado (0→1)
              (0,0) inicio
```

**Cómo leer los valores:**

| Patrón | Valores típicos | Sensación |
|---|---|---|
| Ease-out suave | `0.0, 0.0, 0.2, 1.0` | Arranca rápido, frena al final |
| Ease-in-out | `0.4, 0.0, 0.6, 1.0` | Gradual en ambos extremos |
| Overshoot (rebote) | `0.05, 0.9, 0.1, 1.05` | Supera el destino y vuelve (y1 > 1) |
| Linear | `1.0, 1.0, 1.0, 1.0` | Velocidad constante |
| Elástico agresivo | `0.5, -0.5, 0.68, 1.5` | Rebote pronunciado (y0 < 0 = arranque inverso) |

> Truco: usa [cubic-bezier.com](https://cubic-bezier.com) para visualizar la curva antes de copiar los valores.

**Curvas definidas en la config KooL:**

```ini
bezier = wind,      0.05, 0.9,  0.1,  1.05   # overshoot suave — ventanas principales
bezier = winIn,     0.1,  1.1,  0.1,  1.1    # entrada con rebote
bezier = winOut,    0.3, -0.3,  0,    1      # salida con arranque inverso
bezier = liner,     1,    1,    1,    1      # lineal puro — border/ángulo
bezier = overshot,  0.05, 0.9,  0.1,  1.05   # alias de wind — workspaces
bezier = smoothOut, 0.5,  0,    0.99, 0.99   # fade out suave
bezier = smoothIn,  0.5, -0.5,  0.68, 1.5    # fade in elástico
```

### 2.3 Nombres de animación disponibles

| Nombre | Qué anima | Acepta estilo |
|---|---|---|
| `global` | Todas (interruptor maestro) | no |
| `windows` | Ventanas (genérico) | sí |
| `windowsIn` | Apertura de ventana | sí |
| `windowsOut` | Cierre de ventana | sí |
| `windowsMove` | Mover/redimensionar ventana | sí |
| `border` | Animación del borde activo | no |
| `borderangle` | Rotación del gradiente del borde | sí (`loop` / `once`) |
| `fade` | Fundidos (genérico) | no |
| `fadeIn` | Fundido al abrir | no |
| `fadeOut` | Fundido al cerrar | no |
| `fadeSwitch` | Fundido al cambiar foco | no |
| `fadeShadow` | Fundido de la sombra | no |
| `fadeDim` | Transición de dim_inactive | no |
| `workspaces` | Cambio de workspace (genérico) | sí |
| `workspacesIn` | Entrando a un workspace | sí |
| `workspacesOut` | Saliendo de un workspace | sí |
| `specialWorkspace` | Workspace especial (scratchpad) | sí |

> `windowsIn`/`windowsOut`/`workspacesIn`/`workspacesOut` requieren Hyprland ≥ 0.42.

### 2.4 Estilos disponibles

| Estilo | Compatible con | Descripción |
|---|---|---|
| `slide` | windows, workspaces | Deslizamiento direccional |
| `slidevert` | windows, workspaces | Deslizamiento vertical |
| `popin` | windows | Escala desde el centro (zoom in/out) |
| `gnomed` | windows | Variante de popin estilo GNOME |
| `fade` | windows | Solo fundido (sin movimiento) |
| `loop` | borderangle | Rotación continua del ángulo |
| `once` | borderangle | Rotación una sola vez |

---

## 3. Presets de ejemplo

### Preset A — Snappy (rápido y directo, ideal para trabajo)

```ini
animations {
    enabled = yes

    bezier = snappy,   0.0, 0.0, 0.2, 1.0   # ease-out estándar
    bezier = linear,   1.0, 1.0, 1.0, 1.0

    animation = windows,     1, 4, snappy, slide
    animation = windowsIn,   1, 3, snappy, popin
    animation = windowsOut,  1, 3, snappy, popin
    animation = windowsMove, 1, 4, snappy, slide
    animation = fade,        1, 3, snappy
    animation = workspaces,  1, 3, snappy, slide
    animation = border,      1, 2, linear
}
```

> Velocidades altas (3–4), sin overshoot, slide/popin limpio.
> Sensación: profesional, sin distracciones.

### Preset B — Suave / fluido (estético, para mostrar el escritorio)

```ini
animations {
    enabled = yes

    bezier = fluid,   0.4, 0.0, 0.2, 1.0    # material design ease
    bezier = bounce,  0.05, 0.9, 0.1, 1.05  # ligero overshoot
    bezier = fadeOut, 0.5, 0.0, 0.99, 0.99

    animation = windows,     1, 7, bounce, slide
    animation = windowsIn,   1, 6, bounce, slide
    animation = windowsOut,  1, 4, fadeOut, slide
    animation = windowsMove, 1, 6, fluid, slide
    animation = fade,        1, 5, fadeOut
    animation = workspaces,  1, 6, bounce, slide
    animation = border,      1, 1, fluid
    animation = borderangle, 1, 180, fluid, loop
}
```

> Velocidades medias (5–7), overshoot sutil en bounce, borderangle rotatorio.
> Sensación: escritorio vivo, KDE/macOS-like.

---

## 4. Cómo afecta a la sensación de fluidez

- **Velocidad demasiado baja (1–2)**: las animaciones se arrastran; el escritorio parece lento aunque el hardware sea rápido.
- **Velocidad demasiado alta (>8)**: las animaciones son tan cortas que el ojo no las registra; podrías desactivarlas y el efecto sería similar.
- **Overshoot (y1 > 1.0)**: da sensación de peso y "física"; atractivo pero puede cansar si trabajas muchas horas.
- **`slide` vs `popin`**: slide es más informativo (indica dirección), popin es más centrado/minimalista. Para workspaces, slide refuerza el modelo mental de "escritorios en fila".
- **`dim_inactive` + `inactive_opacity`**: el dimming separa visualmente el foco del contexto; con `dim_strength = 0.1` es casi imperceptible pero mejora el enfoque cognitivo. Superponer dim Y opacidad baja (0.7) puede resultar en ventanas demasiado apagadas.

---

## Conexiones

- [[00_README]]
- [[Recetas_Config]]
- [[MOC_Hyprland]]
