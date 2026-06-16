---
title: NVIDIA en Wayland y Gráficos Híbridos (Hyprland)
date: 2026-06-12
tags: [programacion/linux/hyprland, programacion/linux/gpu, programacion/linux/wayland]
type: nota
status: permanente
source: claude-code
aliases: [nvidia wayland hyprland, gráficos híbridos hyprland, PRIME on-demand hyprland, nvidia hybrid laptop]
---

# NVIDIA en Wayland y Gráficos Híbridos (Hyprland)

## Idea central

NVIDIA+Wayland fue históricamente problemático por la ausencia de sincronización explícita y soporte GBM. Ambos problemas se resolvieron a partir del driver 495 (GBM) y el driver 555 (explicit sync). En portátiles con gráficos híbridos, la arquitectura correcta para Hyprland es **Intel como GPU primaria + NVIDIA por offload PRIME on-demand**, no al revés.

---

## 1. Por qué NVIDIA + Wayland era problemático

Wayland delega la composición al compositor (aquí, Hyprland). Para funcionar necesita:

| Requisito | Protocolo | Cuándo llegó a NVIDIA |
|---|---|---|
| Buffer sharing con compositors | **GBM** (Generic Buffer Manager) | Driver 495 (oct. 2021) |
| Sincronización de frames sin tearing | **Explicit sync** (`linux-drm-syncobj-v1`) | Driver **555** (jun. 2024) |
| Renderizado del cursor sin CPU | KMS atomic modesetting | Habilitado con `nvidia-drm.modeset=1` |

Antes del driver 555, NVIDIA usaba sincronización **implícita**, que Wayland no entiende de forma nativa. El resultado era: flickering severo, frames fuera de orden, y tearing aleatorio. Con explicit sync en 555+, el compositor y el driver negocian explícitamente cuándo un buffer está listo — el problema desaparece estructuralmente.

> **Tu setup (driver 580.x open):** tienes explicit sync, GBM, y modesetting. La base técnica es sólida.

---

## 2. Módulos open vs propietarios: por qué open en Ada Lovelace

NVIDIA tiene dos sabores de módulos de kernel, ambos con el mismo userspace (`nvidia-utils`, `libnvidia-*`):

| Sabor | Paquete Ubuntu | Recomendado para |
|---|---|---|
| Propietario clásico | `nvidia-dkms` | Kepler–Pascal (700–1000) |
| **Open** (código abierto) | `nvidia-open-dkms` | Turing (16xx/20xx) en adelante |
| Open **obligatorio** | — | Blackwell (50xx) y superior |

Desde el driver 560, NVIDIA recomienda explícitamente los módulos open para Turing+. En Ada Lovelace (RTX 40xx), las ventajas son concretas:

- Soporte nativo de **DMABUF** para CUDA
- **Heterogeneous Memory Management (HMM)**
- Mejor integración con el scheduler de Linux (CPU affinity en GPU faults)
- Mayor velocidad de desarrollo y parches de la comunidad

El kernel module open es literalmente el mismo código fuente interno de NVIDIA compilado con licencia dual MIT/GPL — no es Nouveau ni una reimplementación. El userspace es idéntico al propietario.

> **Tu setup:** `nvidia-595-open` (actualmente ejecutando 580.159.03 según `/proc/driver/nvidia/version`). Correcto para RTX 4070 Laptop (Ada Lovelace). No hay motivo para cambiar a módulos propietarios.

---

## 3. Parámetros de kernel y módulos

### 3.1 `nvidia-drm.modeset=1`

Habilita KMS (Kernel Mode Setting) en el módulo `nvidia-drm`. Sin esto, Wayland no puede usar la NVIDIA para renderizar directamente — el driver no expone el DRM master que necesita el compositor.

**Dónde está en tu sistema** — dos lugares redundantes (ambos necesarios):

```
# /etc/modprobe.d/nvidia.conf
options nvidia-drm modeset=1 fbdev=1
options nvidia NVreg_PreserveVideoMemoryAllocations=1
```

```
# /etc/default/grub  →  GRUB_CMDLINE_LINUX
rd.driver.blacklist=nouveau modprobe.blacklist=nouveau nvidia-drm.modeset=1
```

`fbdev=1` habilita el framebuffer KMS (necesario para algunos casos de consola virtual con NVIDIA primaria; en tu setup on-demand es inofensivo).

### 3.2 `NVreg_PreserveVideoMemoryAllocations=1`

Instruye al driver a **preservar el contenido de VRAM durante la suspensión** (S3/S4). Sin esto, al despertar desde suspend la VRAM se corrompe y Hyprland produce pantalla negra o crash. Crítico en portátiles.

Para que la suspensión funcione de extremo a extremo también se deben activar los servicios systemd del driver:

```bash
sudo systemctl enable nvidia-suspend.service
sudo systemctl enable nvidia-hibernate.service
sudo systemctl enable nvidia-resume.service
```

### 3.3 Blacklist nouveau

```
# /etc/default/grub
rd.driver.blacklist=nouveau modprobe.blacklist=nouveau
```

Nouveau y el driver propietario/open no pueden coexistir. El blacklist garantiza que solo carga el driver NVIDIA.

---

## 4. Gráficos híbridos PRIME — los tres modos

`prime-select` gestiona qué GPU "dirige" el sistema. Los tres modos tienen consecuencias muy distintas:

| Modo | Quién renderiza | Quién muestra | Consumo batería | Monitores externos |
|---|---|---|---|---|
| `nvidia` | NVIDIA | NVIDIA | Alto (NVIDIA siempre activa) | Fácil (NVIDIA controla todos) |
| `intel` | Intel | Intel | Bajo (NVIDIA nunca activa) | Solo los conectados al iGPU |
| `on-demand` | **Intel** (compositor) | Intel | Bajo en reposo | Depende del MUX |

En modo **on-demand**, la Intel renderiza el escritorio y Wayland compositor; la NVIDIA está en D3cold (apagada) hasta que una aplicación la solicita explícitamente. Es el modo correcto para Hyprland en portátil.

> **Tu sistema:** `prime-select query` → `on-demand`. ✓

---

## 5. Por qué on-demand + Intel primaria es la arquitectura correcta para Hyprland

Hyprland usa **aquamarine** como backend DRM (desde ~0.45). Aquamarine necesita elegir una GPU primaria para toda la composición. El problema con NVIDIA como primaria en híbrida:

1. **NVIDIA no soporta Multi-GPU bien en Wayland**: no implementa correctamente los protocolos de buffer sharing para pasar frames al display engine del iGPU cuando es necesario.
2. **Mayor consumo**: NVIDIA activa siempre aunque no haya carga 3D.
3. **Compatibilidad rota con algunas apps**: muchas apps Wayland asumen GBM con el driver del display primario.

Con Intel como primaria:
- Hyprland renderiza ventanas y animaciones en i915 (estable, sin issues de sync).
- NVIDIA queda disponible para offload bajo demanda.
- La batería se beneficia de los estados de energía D3cold de la NVIDIA cuando está ociosa.

### Identificación de devices en tu máquina

```
/dev/dri/card1  →  NVIDIA RTX 4070  (PCI 0000:01:00.0, vendor 0x10de)
/dev/dri/card2  →  Intel UHD        (PCI 0000:00:02.0, vendor 0x8086)
```

Rutas estables (recomendadas sobre `card1`/`card2` que pueden cambiar):

```
/dev/dri/by-path/pci-0000:01:00.0-card  →  NVIDIA
/dev/dri/by-path/pci-0000:00:02.0-card  →  Intel
```

---

## 6. `AQ_DRM_DEVICES` — decirle a Hyprland qué GPU usar

Aquamarine detecta GPUs automáticamente por orden del bus PCI. A veces el orden no es el deseado. `AQ_DRM_DEVICES` sobreescribe eso:

```ini
# En ENVariables.conf (o env global antes de que arranque Hyprland)
# Sintaxis: primaria:secundaria  (separadas por :)
env = AQ_DRM_DEVICES,/dev/dri/by-path/pci-0000:00:02.0-card:/dev/dri/by-path/pci-0000:01:00.0-card
```

Esto pone **Intel como primaria** (renderiza el compositor) y **NVIDIA como secundaria** (disponible para offload).

**Importante:** usar rutas `by-path` en lugar de `card0`/`card1`. Los números de card son asignados por orden de probe del kernel y pueden cambiar entre arranques o con actualizaciones del kernel.

**Con uwsm** (si se usa systemd para lanzar Hyprland): exportar en `~/.config/uwsm/env-hyprland` en lugar de en el config de Hyprland, para que el entorno systemd lo herede correctamente.

> **Tu setup actual:** los NVIDIA vars están comentados en `ENVariables.conf` y `prime-select` está en on-demand. Si aquamarine está seleccionando la Intel como primaria automáticamente (lo más probable dado el orden PCI), puede que `AQ_DRM_DEVICES` no sea necesario. Si ves la NVIDIA como renderizador principal en `hyprctl monitors`, añade la variable.

---

## 7. Variables de entorno NVIDIA — cuáles aplican en tu setup

Esta es la parte más confusa. La respuesta depende del modo PRIME.

### Variables que NO debes activar en on-demand + Intel primaria

| Variable | Por qué NO |
|---|---|
| `GBM_BACKEND=nvidia-drm` | Fuerza GBM a usar NVIDIA para todo. Rompe en on-demand donde el compositor corre en Intel. Útil solo en modo NVIDIA puro. |
| `__GLX_VENDOR_LIBRARY_NAME=nvidia` | Fuerza GLX a NVIDIA para todas las apps. Innecesario y contraproducente en on-demand. |
| `LIBVA_DRIVER_NAME=nvidia` | Útil para VA-API en NVIDIA, pero puede interferir con la aceleración de video en Intel cuando es primaria. Evaluar por app. |

### Variables que SÍ pueden ser útiles selectivamente

| Variable | Valor | Cuándo |
|---|---|---|
| `NVD_BACKEND` | `direct` | Habilita el backend de decodificación de video directo de NVIDIA (ffmpeg/mpv). Activar si usas hardware decode con NVIDIA. |
| `ELECTRON_OZONE_PLATFORM_HINT` | `auto` | Fuerza apps Electron/Chromium a usar Wayland nativo. Resuelve flickering en VS Code, Discord, etc. Aplica siempre. |
| `__NV_PRIME_RENDER_OFFLOAD` | `1` | Se usa para lanzar apps específicas en NVIDIA (ver sección siguiente). No activar globalmente. |
| `AQ_NO_MODIFIERS` | `1` | Deshabilita DRM modifiers. Solo como workaround de último recurso si hay artifacts. |
| `AQ_MGPU_NO_EXPLICIT` | `1` | Deshabilita explicit sync en buffers multi-GPU. Solo si hay bugs específicos con buffers entre GPUs. |

> **Nota:** `WLR_DRM_NO_ATOMIC` y variables `WLR_*` son del backend wlroots antiguo. **No aplican a Hyprland 0.45+ con aquamarine.** No las uses.

---

## 8. Lanzar aplicaciones en la NVIDIA (offload)

En modo on-demand, la NVIDIA se activa para una app específica mediante variables de entorno:

### `prime-run` (la forma simple)

```bash
prime-run glxgears           # lanzar con NVIDIA
prime-run steam              # Steam en NVIDIA
prime-run %command%          # en opciones de launch de Steam
```

`prime-run` es un wrapper que setea las variables necesarias:

```bash
# Lo que hace prime-run internamente:
__NV_PRIME_RENDER_OFFLOAD=1 \
__NV_PRIME_RENDER_OFFLOAD_PROVIDER=NVIDIA-G0 \
__GLX_VENDOR_LIBRARY_NAME=nvidia \
__VK_LAYER_NV_optimus=NVIDIA_only \
VK_DRIVER_FILES=/usr/share/vulkan/icd.d/nvidia_icd.json \
<tu_aplicación>
```

### Alternativa manual (Vulkan)

```bash
__NV_PRIME_RENDER_OFFLOAD=1 __VK_LAYER_NV_optimus=NVIDIA_only vulkaninfo
```

### Verificar qué GPU está usando una app

```bash
nvidia-smi   # muestra procesos activos usando NVIDIA
# o dentro de una app OpenGL:
glxinfo | grep "OpenGL renderer"
```

---

## 9. Monitores externos y el MUX

Los monitores externos en portátiles se conectan por hardware a una de las dos GPUs (o a ambas a través de un MUX switch):

**ASUS TUF F15 FX507VI — sin MUX físico visible en BIOS**:
- El puerto HDMI y Thunderbolt/USB-C pueden estar cableados a la NVIDIA o a la Intel según el modelo exacto.
- En modo `on-demand` con Intel primaria, si un monitor externo está cableado a la NVIDIA, Hyprland puede no detectarlo correctamente o mostrar pantalla negra.
- **Diagnóstico:** `hyprctl monitors` — si el monitor externo no aparece, prueba cambiar `prime-select` a `nvidia` temporalmente para confirmar que el cable físico va a la NVIDIA.
- Si el monitor externo necesita NVIDIA, considera activar `AQ_DRM_DEVICES` con NVIDIA como primaria solo cuando lo uses, o explorar si el BIOS tiene opción "dGPU mode" / MUX.

---

## 10. Resumen de tu configuración y por qué está bien

| Componente | Tu valor | Correcto porque |
|---|---|---|
| `prime-select` | `on-demand` | Intel renderiza Hyprland, NVIDIA en D3cold por defecto |
| Driver | `nvidia-595-open` (580.x) | Open recomendado para Ada; tiene explicit sync y GBM |
| `nvidia-drm.modeset=1` | En grub y modprobe | Habilita KMS, necesario para Wayland |
| `NVreg_PreserveVideoMemoryAllocations=1` | En modprobe | Suspensión funcional |
| Blacklist nouveau | En grub | Evita conflicto con driver open |
| Variables NVIDIA en ENVariables | Todas comentadas | Correcto: con Intel primaria no se fuerzan globalmente |
| `fbdev=1` | En modprobe | Inofensivo, útil para consola VT |

### Qué podrías añadir opcionalmente

```ini
# ENVariables.conf — añadir si quieres decode HW con NVIDIA
# env = NVD_BACKEND,direct

# Siempre útil para Electron apps
env = ELECTRON_OZONE_PLATFORM_HINT,auto

# Si aquamarine no elige Intel automáticamente (verificar con hyprctl monitors)
env = AQ_DRM_DEVICES,/dev/dri/by-path/pci-0000:00:02.0-card:/dev/dri/by-path/pci-0000:01:00.0-card

# Para lanzar juegos/apps pesadas en NVIDIA (no global):
# prime-run <app>  o añadir __NV_PRIME_RENDER_OFFLOAD=1 en el .desktop
```

---

## Fuente

Investigación con Hyprland Wiki (https://wiki.hypr.land/Nvidia/), Multi-GPU Wiki, DeepWiki, GamingOnLinux, NVIDIA developer blog. Anclado en el sistema real (ASUS TUF F15 FX507VI, driver 580.159.03 open, `prime-select on-demand`). Fecha: 2026-06-12.

---

## Conexiones

- [[00_README]]
- [[MOC_Hyprland]]
