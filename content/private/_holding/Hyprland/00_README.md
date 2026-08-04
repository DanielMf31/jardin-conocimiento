---
title: Hyprland — auto-estudio y configuración
date: 2026-06-12
tags: [programacion/linux, programacion/hyprland, wayland, ricing]
type: moc
status: en-progreso
source: claude-code
aliases: [hypr, WM, ricing]
---

# Hyprland — auto-estudio y configuración

> Cluster de **teoría + práctica** sobre Hyprland (compositor Wayland *tiling*) y su ecosistema. Documenta **cómo funciona por dentro** y **cómo configurarlo**, anclado a mi instalación real.
>
> **Punto de entrada del área**: [[MOC_Hyprland]]
>
> **Filosofía**: igual que [[00_README|CS_Fundamentos]] pero para el WM. Si la pregunta es *"¿cómo lo configuro?"* → **Recetas_Config**. Si es *"¿por qué funciona así?"* → las carpetas numeradas.

## Cómo uso esta carpeta

- **[[00_Dudas_y_Preguntas]]** → donde suelto preguntas según trasteo; se responden y quedan registradas (active recall después).
- **[[Recetas_Config]]** → recetario vivo de los ajustes concretos que voy aplicando (gaps, reglas, atajos…).
- **Carpetas numeradas** → docs densos de referencia por tema.

## Estructura

```
01_arquitectura_wayland/      ← cómo funciona Wayland y un compositor por dentro
02_layouts_y_ventanas/        ← dwindle/master, tiling, splits, floating   (mi interés)
03_configuracion_hyprlang/    ← el lenguaje de config, variables, sourcing, hot reload
04_keybinds_y_dispatchers/    ← binds, dispatchers, submaps
05_window_workspace_rules/    ← reglas por ventana y por workspace
06_decoraciones_y_animaciones/← blur, redondeo, sombras, animaciones, bezier
07_ecosistema/                ← waybar, rofi, swww, hyprlock, hypridle, portals
08_nvidia_e_hibrida/          ← NVIDIA en Wayland, gráficos híbridos, env vars
09_troubleshooting_y_hyprctl/ ← hyprctl, logs, errores de config, depuración
```

## Mi setup (contexto para releer dentro de 2 años)

- **Hardware**: ASUS TUF Gaming F15 FX507VI · Intel UHD (Raptor Lake) + NVIDIA RTX 4070 Laptop · pantalla 1080p 144 Hz.
- **SO**: Ubuntu 24.04 LTS · GDM · arranque dual con Windows.
- **Gráficos**: híbrida en modo **on-demand** (Intel primaria, NVIDIA por offload) · driver **595-open**.
- **Hyprland**: v0.55.3 · dotfiles **KooL (JaKooLit)** · mi config propia en `~/.config/hypr/UserConfigs/`.
- **Seguridad**: snapshot Timeshift "Sistema sano antes de Hyprland" como punto de retorno.

## Conexiones

- [[MOC_Hyprland]] — área padre
- [[00_README|CS_Fundamentos]] — cluster hermano de teoría CS
