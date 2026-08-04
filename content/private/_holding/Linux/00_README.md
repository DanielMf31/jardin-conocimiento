---
title: Linux — fundamentos (auto-estudio)
date: 2026-06-12
tags: [programacion/linux, fundamentos]
type: moc
status: en-progreso
source: claude-code
aliases: [Linux fundamentos, Linux básico, fundamentos linux]
---

# Linux — fundamentos para ser proficiente

> Lo básico de Linux que hay que dominar **sí o sí** para moverte con soltura. Estilo denso tipo [[MOC_CS_Fundamentos|CS_Fundamentos]]. Ejemplos sobre **Ubuntu 24.04** (mi sistema).
>
> Mapa del área: [[MOC_Linux]]

## Estructura

```
01_filesystem_y_navegacion/   ← cómo se organiza el sistema (FHS) y moverse por él
02_shell_y_terminal/          ← bash, la terminal, pipes y redirecciones
03_archivos_y_permisos/       ← crear/copiar/mover/enlazar + chmod/chown
04_usuarios_y_sudo/           ← usuarios, grupos, sudo, root
05_procesos_y_systemd/        ← procesos, señales, servicios systemd, journalctl
06_gestion_de_paquetes/       ← apt, dpkg, snap, flatpak, repos
07_procesado_de_texto/        ← grep, sed, awk, find (el corazón del CLI)
08_almacenamiento_y_discos/   ← particiones, montajes, fstab, df/du
09_redes_y_ssh/               ← ip, ss, ssh, scp/rsync, curl
10_scripting_bash/            ← variables, condicionales, bucles, funciones
11_entorno_y_dotfiles/        ← PATH, variables de entorno, .bashrc, dotfiles
12_editores_terminal/         ← nano y vim básico
```

Cada carpeta: un doc denso y práctico (los comandos y conceptos que se usan de verdad).

## Conexiones
- [[MOC_Linux]] — mapa padre
- [[MOC_CS_Fundamentos]] — cluster hermano de teoría CS
- [[Hyprland/00_README|Cluster Hyprland]] — el WM, otra rama de Linux
