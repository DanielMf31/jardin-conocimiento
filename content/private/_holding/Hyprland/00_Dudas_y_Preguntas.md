---
title: Hyprland — Dudas y Preguntas (log)
date: 2026-06-12
tags: [programacion/hyprland, dudas, active-recall]
type: nota
status: en-progreso
source: claude-code
aliases: [dudas hyprland, preguntas hyprland]
---

# Hyprland — Dudas y Preguntas

> Log vivo de preguntas que lanzo mientras trasteo. Formato: **P** (pregunta) / **R** (respuesta corta). Las que den para más se promueven a un doc de la carpeta numerada que toque.

---

## 2026-06-12 — primer día con Hyprland

### P: ¿Cuál es la tecla "Super" exactamente?
**R:** La tecla con el **logo de Windows** ⊞, abajo a la izquierda (entre `Ctrl`/`Fn` y `Alt`). En Linux se llama *Super* (o *Meta*). Es el modificador principal: `$mainMod = SUPER` en la config. Se puede cambiar a `ALT`, `CAPS`, etc. → ver.

### P: ¿Qué historia tiene Hyprland? ¿Es un proyecto grande?
**R:** Lo creó **Vaxry** (Vaxerski), siendo adolescente (~2022), como hobby para aprender C++. Despegó por ofrecer lo que los tiling WM clásicos no daban: **animaciones, blur, esquinas redondeadas**. Con el tiempo se independizó de wlroots y escribió su propio backend de render (**aquamarine**) y su stack de librerías (`hyprlang`, `hyprutils`, `hyprlock`, `hypridle`…). Proyecto enorme nacido casi de una sola persona. → ver.

### P: ¿Qué pasó con freedesktop.org / la polémica de Vaxry?
**R:** En 2024 Vaxry fue **expulsado de los espacios de freedesktop.org** (la org que aloja Wayland, las specs xdg, etc.) por un conflicto de **código de conducta**: fd.o consideró problemática la cultura de la comunidad de Hyprland (su Discord); el punto caliente fue **jurisdiccional** — fd.o sancionando conducta ocurrida en espacios *propios* de Hyprland, no en los suyos. Sigue siendo debatido. El software es excelente con independencia del episodio.

### P: ¿Por qué salían "config error in file" al primer arranque?
**R:** Los dotfiles de KooL nombraban 3 opciones que la v0.55.3 renombró/quitó: `misc:vfr` (ahora va solo), `dwindle:pseudotile` (ahora es la tecla SUPER+P), y el dispatcher `togglesplit`. Se comentaron y desaparecieron. **Avisos, no rupturas** → ver.

---

## Conexiones
- [[00_README]] · [[Recetas_Config]] · [[MOC_Hyprland]]
