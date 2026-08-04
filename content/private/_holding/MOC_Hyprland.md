---
title: MOC Hyprland
date: 2026-06-12
tags: [programacion/hyprland, programacion/linux, wayland, moc]
type: moc
status: en-progreso
source: claude-code
aliases: [MOC Hyprland, Hyprland MOC]
---

# MOC Hyprland

> Mapa completo de **Hyprland** (compositor Wayland *tiling*) y su ecosistema: teoría interna + configuración práctica. Cluster de docs en `50_Areas/Programacion/Hyprland/`.
>
> Área padre: [[MOC_Linux]]

## Índice y registros vivos
- [[Hyprland/00_README|README del cluster]]
- [[Hyprland/00_Dudas_y_Preguntas|Dudas y Preguntas]] — log de preguntas según trasteo
- [[Hyprland/Recetas_Config|Recetas de config]] — todos los ajustes aplicados (gaps, reglas, atajos…)
- [[Hyprland/Widget_Cosmos|Widget Cosmos]] — hub de simulaciones en canvas + cola de 30 escenas

## Documentación por tema
| # | Tema | Doc |
|---|---|---|
| 01 | Arquitectura Wayland y compositores | [[wayland-y-arquitectura-de-compositores]] |
| 02 | Layouts y gestión de ventanas | [[layouts-y-gestion-de-ventanas]] |
| 03 | Hyprlang y estructura de config | [[hyprlang-y-estructura-de-config]] |
| 04 | Keybinds y dispatchers | [[binds-y-dispatchers]] |
| 05 | Window y workspace rules | [[window-y-workspace-rules]] |
| 06 | Decoraciones y animaciones | [[decoraciones-y-animaciones]] |
| 07 | Ecosistema (waybar, rofi, swww, hyprlock…) | [[ecosistema-hyprland]] |
| 08 | NVIDIA en Wayland e híbrida | [[nvidia-wayland-e-hibrida]] |
| 09 | hyprctl y troubleshooting | [[hyprctl-y-troubleshooting]] |

## Setup de ejemplo
- Hyprland **0.55.3** · dotfiles **KooL (JaKooLit)** · Ubuntu 24.04.
- ASUS TUF F15 · Intel UHD + NVIDIA RTX 4070 en **on-demand** (595-open).
- Config propia en `~/.config/hypr/UserConfigs/`.

## Conexiones
- [[MOC_Linux]] — área padre
- [[MOC_Programacion]] — área raíz
