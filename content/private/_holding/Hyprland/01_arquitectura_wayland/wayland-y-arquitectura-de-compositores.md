---
title: Wayland y arquitectura de compositores
date: 2026-06-12
tags: [programacion/linux, programacion/hyprland, programacion/wayland]
type: nota
status: permanente
source: claude-code
aliases: [wayland arquitectura, compositor wayland, X11 vs Wayland, aquamarine hyprland]
---

# Wayland y arquitectura de compositores

## Idea central

Wayland no es un "servidor gráfico" al estilo de X11; es un **protocolo** que define cómo los clientes (apps) hablan con un **compositor** que hace de servidor, renderizador y gestor de ventanas a la vez. Hyprland es ese compositor, y desde ~0.42 usa **aquamarine** —su propio backend— para hablar directamente con el kernel y la GPU, sin depender de wlroots.

---

## 1. ¿Qué es un servidor gráfico?

Un servidor gráfico es el proceso que:

1. Habla con el kernel para controlar la pantalla (modo, resolución, sincronía vertical).
2. Recibe eventos de input (teclado, ratón, touchpad).
3. Arbitra qué proceso puede dibujar en qué región.
4. Compone los buffers de las apps en la imagen final y la manda al display.

En Linux el núcleo de este pipeline siempre ha sido el subsistema **DRM/KMS** del kernel.

---

## 2. X11 — el modelo clásico

```
App A ──┐
App B ──┤──► Servidor X (Xorg) ──► GPU (driver DRI/DRM) ──► pantalla
App C ──┘         │
                  └── Gestor de ventanas (proceso separado: i3, openbox…)
```

| Característica | X11 |
|---|---|
| Protocolo | Bidi TCP/IP (incluso en local via socket) |
| Rendering | La app puede pedir al servidor X que dibuje (X primitives) **o** dibujar ella misma (DRI) |
| Gestor de ventanas | Proceso separado; Xorg delega decoraciones y foco |
| Seguridad | Cualquier app puede leer eventos de teclado de otras (**keylogging trivial**) |
| Escalado HiDPI | Afterthought; cada app escala por su cuenta → inconsistencias |
| Tearing | Posible; VSync opcional y complejo de coordinar |
| Pantallas múltiples | RANDR/XINERAMA, legacy y frágil |

X11 lleva ~40 años de capas de compatibilidad. Es potente pero su modelo de seguridad es plano: todas las apps que abren una misma pantalla X pueden espiarse entre sí.

---

## 3. Wayland — el modelo moderno

```
App A ──► libwayland-client ──► socket Unix ──► Compositor (Hyprland)
App B ──► libwayland-client ──► socket Unix ──┘        │
                                                        ▼
                                               EGL/GBM ──► GPU ──► pantalla
                                               libinput ──► eventos
```

**El compositor ES el servidor.** No hay proceso Xorg separado: Hyprland habla directamente con DRM/KMS para controlar el display y con libinput para el input. Las apps solo ven su propio buffer; no pueden leer el de las demás.

### Principios clave

| Principio | Detalle |
|---|---|
| **Aislamiento de buffers** | Cada cliente renderiza en su propio buffer (SHM o GBM/EGL). El compositor los combina. |
| **Compositor = servidor + WM** | No hay separación: Hyprland decide layout, decoraciones, foco y compositing. |
| **Sin X primitives** | El protocolo solo mueve buffers y eventos; el dibujo es 100% responsabilidad del cliente. |
| **Escalado nativo** | El compositor comunica el scale factor al cliente; cada buffer ya llega a la resolución correcta. |
| **Sin tearing por diseño** | El compositor sincroniza con el flip de pantalla (page flip DRM) antes de presentar. |
| **Seguridad** | Un cliente no puede recibir eventos de teclado de otra ventana sin permiso explícito. |

---

## 4. Pipeline completo: app → compositor → GPU → pantalla

```
┌──────────────────────────────────────────────────────────────────┐
│  ESPACIO DE USUARIO                                              │
│                                                                  │
│  ┌─────────┐  wl_surface  ┌──────────────────────────────────┐  │
│  │   App   │─────────────►│         HYPRLAND (compositor)    │  │
│  │ (GTK4 / │  wl_buffer   │  ┌────────────┐  ┌───────────┐  │  │
│  │  Qt6 /  │◄─────────────│  │ Protocolo  │  │  Layout   │  │  │
│  │  SDL2…) │              │  │  Wayland   │  │  (dwindle/│  │  │
│  └─────────┘              │  │ (negociado │  │   master) │  │  │
│                           │  │ en el boot)│  └───────────┘  │  │
│  ┌─────────┐              │  └────────────┘        │         │  │
│  │XWayland │──X11─►XWM───►│                        ▼         │  │
│  │(apps X) │              │  ┌─────────────────────────────┐ │  │
│  └─────────┘              │  │     aquamarine (backend)    │ │  │
│                           │  │  ┌──────────┐ ┌──────────┐  │ │  │
│                           │  │  │ DRM/KMS  │ │ libinput │  │ │  │
│                           │  └──┴────┬─────┴─┴────┬─────┘  │  │
│                           └──────────│─────────────│────────┘  │
└──────────────────────────────────────│─────────────│───────────┘
                                       ▼             ▼
                               ┌──────────────┐  ┌──────────┐
                               │  GPU (EGL /  │  │ /dev/    │
                               │  GBM / Mesa) │  │ input/*  │
                               └──────┬───────┘  └──────────┘
                                      │ page flip
                                      ▼
                               ┌──────────────┐
                               │  Pantalla    │
                               │  (CRTC/eDP-1)│
                               └──────────────┘
```

---

## 5. Cómo Hyprland habla con el kernel: DRM/KMS

**DRM (Direct Rendering Manager)** es el subsistema del kernel Linux que gestiona el acceso a la GPU y al display hardware. Se divide en dos partes:

- **DRM propiamente dicho**: gestión de memoria de GPU, command submission, sincronización (fences).
- **KMS (Kernel Mode Setting)**: controla los conectores físicos (HDMI, eDP), CRTCs (scanout engines) y planos. Permite al compositor setear resolución/refresh sin pasar por Xorg.

Hyprland abre `/dev/dri/cardN` (acceso KMS) y `/dev/dri/renderDN` (acceso render). En tu sistema el GPU NVIDIA usa ambos nodos.

```conf
# ENVariables.conf (KooL/JaKooLit dotfiles)
# env = AQ_DRM_DEVICES,/dev/dri/card1:/dev/dri/card0
# card0 → Intel UHD (iGPU, scanout principal)
# card1 → RTX 4070 (dGPU, render on-demand)
```

---

## 6. Cómo habla con la GPU: EGL y GBM

| Capa | Rol |
|---|---|
| **Mesa** | Implementación open-source de OpenGL/Vulkan/EGL para Intel y (parcialmente) NVIDIA |
| **GBM (Generic Buffer Management)** | API de Mesa para asignar buffers gráficos en VRAM compatibles con KMS. Es el "malloc de la GPU". |
| **EGL** | API de Khronos que inicializa el contexto OpenGL/ES sobre un display nativo (aquí, un `gbm_device`). |
| **DMA-BUF** | Mecanismo del kernel para compartir buffers entre procesos/drivers sin copias (zero-copy). |

Pipeline de render de un frame:

1. Hyprland pide a GBM un buffer para el plano de pantalla.
2. Importa ese buffer en EGL como `EGLImage`.
3. Renderiza todos los wl_surface de los clientes sobre ese buffer (con shaders OpenGL).
4. Llama a DRM page-flip: el kernel swapea el buffer activo al siguiente vsync.
5. La pantalla escanea el nuevo buffer. Sin tearing.

---

## 7. Input: libinput

**libinput** es la biblioteca que abstrae todos los dispositivos de entrada en Linux (teclado, ratón, touchpad, stylus). Hyprland (vía aquamarine) abre los nodos `/dev/input/eventN` directamente, sin pasar por Xorg ni evdev manual.

libinput maneja:
- Aceleración del puntero (configurable en Hyprland con `input { accel_profile }`)
- Gesto multitouch del touchpad
- Tap-to-click, scroll natural, etc.

```conf
# Ejemplo de tu setup (UserSettings.conf puede incluir):
# input {
#     touchpad {
#         natural_scroll = true
#         tap-to-click = true
#     }
# }
```

---

## 8. aquamarine — el backend propio de Hyprland

Hasta ~0.41, Hyprland usaba **wlroots** (biblioteca C para construir compositores Wayland). Desde **0.42** (completado en 0.45+) Hyprland es completamente independiente y usa **aquamarine**.

### ¿Qué es aquamarine?

> "A very light linux rendering backend library implementing only the low-level KMS/DRM/etc rendering backends."

| Comparación | wlroots | aquamarine |
|---|---|---|
| Scope | Compositor completo (protocolos + backend) | Solo backend de bajo nivel |
| Idioma | C | C++ |
| Protocolo Wayland | Incluido | **No** — Hyprland implementa los protocolos por su cuenta |
| Dependencias | Muchas | Mínimas |
| Portabilidad | DRM + backend Wayland (nested) | DRM o nested Wayland |

Aquamarine puede correr Hyprland **en una TTY** (modo DRM nativo) **o dentro de otra sesión Wayland** (modo nested, útil para debug). Tu configuración usa DRM nativo.

Variables de debug de aquamarine disponibles en tu `ENVariables.conf`:

```conf
# env = AQ_TRACE,1                          # log verboso
# env = AQ_DRM_DEVICES,/dev/dri/card1:...   # forzar orden de GPUs
# env = AQ_NO_MODIFIERS,1                   # deshabilitar DRM modifiers (debug)
```

---

## 9. XWayland — compatibilidad con apps X11

Las apps que solo hablan X11 (muchos juegos, apps legacy, algunas de desarrollo) no pueden conectarse directamente al socket Wayland. **XWayland** resuelve esto:

```
App X11 ──► XWayland (servidor X completo) ──► wl_surface ──► Hyprland
                    │
                    └── XWM (X Window Manager interno de Hyprland)
                        gestiona decoraciones y foco de ventanas X
```

- XWayland arranca como cliente Wayland normal. Hyprland lo lanza automáticamente al detectar una app X11.
- Internamente hay una dependencia circular: XWayland es cliente Wayland de Hyprland, pero Hyprland es cliente X11 de XWayland (para el XWM). Hyprland gestiona esto con cuidado.
- Las apps X11 **no saben** que están en Wayland; ven un servidor X estándar.
- Limitaciones: input de teclado global funciona distinto, escalado HiDPI es imperfecto (por eso existen las `env = GDK_SCALE` en tu `ENVariables.conf`).

```conf
# ENVariables.conf — fix de escala para apps XWayland con monitor scaling:
# env = GDK_SCALE,1
# env = QT_SCALE_FACTOR,1
```

---

## 10. Protocolos Wayland

Un "protocolo" Wayland es un conjunto de interfaces (en XML) que define los mensajes que pueden intercambiar cliente y compositor. Se negocian en el `wl_registry` al conectarse.

### Capas de protocolos

| Capa | Ejemplos | Quién los define |
|---|---|---|
| **Core** | `wl_compositor`, `wl_surface`, `wl_shm`, `wl_seat` | freedesktop.org (libwayland) |
| **wayland-protocols** | `xdg-shell` (ventanas normales), `xdg-output`, `wp-presentation-time` | freedesktop.org (oficial, lento) |
| **wlr-protocols** | `zwlr_layer_shell_v1` (barras, overlays), `zwlr_screencopy_v1` | Originally wlroots; adoptados por Hyprland |
| **hyprland-protocols** | `hyprland_toplevel_export_v1`, `hyprland_global_keybinds_v1`, `hyprland_surface_v1` | Hyprland propio |

El protocolo más importante para apps normales es **xdg-shell**, que define `xdg_surface` + `xdg_toplevel` (ventana normal) y `xdg_popup` (menús/tooltips).

**zwlr_layer_shell_v1** es lo que usa tu barra (Waybar) para anclarse en un borde de pantalla sin que Hyprland la trate como ventana flotante.

---

## 11. xdg-desktop-portal y portals

En X11, una app podía abrir cualquier archivo del sistema o capturar cualquier ventana directamente. En Wayland esto está bloqueado. Los **portals** son la solución: procesos intermediarios con interfaz D-Bus que elevan permisos bajo consentimiento explícito del usuario.

```
App (p. ej. OBS) ──D-Bus──► xdg-desktop-portal (portal genérico)
                                    │
                             implementación específica del compositor
                                    │
                        xdg-desktop-portal-hyprland (XDPH)
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
            PipeWire (screen capture)     Qt picker (file open)
```

### Portals que provee XDPH

| Portal | Funcionalidad |
|---|---|
| `ScreenCast` | Captura de pantalla/ventana vía PipeWire (OBS, Discord, Zoom) |
| `RemoteDesktop` | Control remoto con acceso a input |
| `FileChooser` | Selector de archivos nativo del sistema |
| `Screenshot` | Captura estática |

**Por qué se necesita PipeWire**: el compositor no puede dar acceso directo a su framebuffer a las apps. PipeWire actúa de bus multimedia: XDPH exporta el contenido de pantalla como un stream PipeWire, y la app (OBS, navegador para screenshare) consume ese stream.

XDPH arranca automáticamente por D-Bus cuando Hyprland inicia. Si no funciona:

```bash
# Verificar que corre:
systemctl --user status xdg-desktop-portal-hyprland

# Verificar PipeWire y wireplumber:
systemctl --user status pipewire wireplumber
```

---

## 12. X11 vs Wayland — tabla resumen

| Aspecto | X11 | Wayland |
|---|---|---|
| Modelo | Cliente habla con servidor X separado | Cliente habla directo con el compositor |
| Seguridad input | Cualquier app puede leer teclado de otras | Aislado; el compositor es árbitro |
| Rendering | X puede dibujar por ti O el cliente (DRI) | El cliente siempre dibuja su propio buffer |
| Tearing | Posible sin VSync explícito | Eliminado por diseño (page flip en vsync) |
| Escalado HiDPI | Frágil, por app | Nativo en el protocolo (`wl_output.scale`) |
| Network transparency | Sí (X11 por TCP) | No (por diseño; screenshare vía PipeWire) |
| Captura de pantalla | Directa (cualquier app) | Solo vía portals + PipeWire |
| Compositing | Opcional (COMPOSITE extension) | Obligatorio; el compositor es el renderer |
| Apps legacy | Nativas | Via XWayland |

---

## Conexiones

- [[00_README]]
- [[MOC_Hyprland]]
