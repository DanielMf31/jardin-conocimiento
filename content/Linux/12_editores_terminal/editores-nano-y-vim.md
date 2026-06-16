---
title: Editores de terminal — nano y vim
date: 2026-06-12
tags: [programacion/linux, programacion/terminal, programacion/herramientas]
type: nota
status: permanente
source: claude-code
aliases: [nano, vim, editores terminal, vi, editor consola]
---

# Editores de terminal — nano y vim

## Por qué necesitas editar en la terminal

Tarde o temprano vas a estar frente a una situación donde el ratón y el IDE no existen:

- **Servidor remoto via SSH** — sin entorno gráfico, sólo shell.
- **Editar un fichero de configuración como root** — `sudo nano /etc/fstab`. Abrir gedit como root es una mala práctica y muchas veces ni funciona.
- **El sistema arrancó en modo recovery** — sólo tienes una TTY.
- **Rapidez en el día a día** — cambiar una línea en un config sin abrir VS Code tarda 2 segundos, no 10.

Regla práctica: **nano para vivir, vim para sobrevivir**. Aprende nano en 5 minutos. Aprende lo mínimo de vim para no quedar atrapado cuando alguien lo abra por ti.

---

## NANO — el editor amigable

### Abrir nano

```bash
nano fichero.txt          # abre (o crea) el fichero
nano /etc/apt/sources.list  # editar config del sistema (como root si hace falta)
sudo nano /etc/hosts      # con sudo si necesitas permisos
```

Al abrir, ves el contenido **directamente editable** — sin modos, sin ceremonias. Escribes y ya.

### Interfaz de nano

```
  GNU nano 7.x          fichero.txt          Modified

[contenido del fichero aquí — editable directamente]

^G Help    ^O Write Out  ^W Where Is  ^K Cut     ^T Execute
^X Exit    ^R Read File  ^\ Replace   ^U Paste   ^J Justify
```

- `^` = Ctrl. `^O` significa Ctrl+O.
- La barra inferior te recuerda los atajos en todo momento. Es intencionalmente amigable.

### Tabla de atajos esenciales de nano

| Atajo | Acción |
|---|---|
| `Ctrl+O` | **Guardar** (Write Out). Confirma el nombre con Enter. |
| `Ctrl+X` | **Salir**. Si hay cambios sin guardar, pregunta. |
| `Ctrl+X` → `Y` → Enter | Guardar y salir en un flujo |
| `Ctrl+W` | **Buscar** texto (Where Is). Enter para siguiente coincidencia. |
| `Ctrl+\` | Buscar **y reemplazar** |
| `Ctrl+K` | **Cortar** la línea entera (Cut Line) |
| `Ctrl+U` | **Pegar** lo cortado (Uncut/Paste) |
| `Ctrl+K` × N veces | Cortar N líneas consecutivas — se acumulan al pegar |
| `Ctrl+6` | Marcar inicio de selección (luego mueve cursor para seleccionar) |
| `Alt+G` | Ir a número de línea (Go to Line) |
| `Alt+U` | **Deshacer** (Undo) — nano ≥ 2.4 |
| `Alt+E` | **Rehacer** (Redo) |
| `Ctrl+C` | Mostrar posición actual (línea y columna) — NO cierra |
| `Ctrl+_` | Ir a línea:columna específica (alternativa a Alt+G) |
| `Page Up / Page Down` | Desplazarse por el fichero |
| `Ctrl+Home` | Ir al inicio del fichero |
| `Ctrl+End` | Ir al final del fichero |

### Gotcha nano

- `Ctrl+C` en nano **no cierra** el editor, sólo muestra la posición. Para salir: `Ctrl+X`.
- Si guardas con `Ctrl+O`, nano te propone el mismo nombre de fichero — pulsa Enter para confirmar. Si escribes otro nombre, crea un fichero nuevo.
- En servidores remotos puede aparecer como `nano` o como `pico` (eran el mismo editor en origen).

---

## VIM — por qué existe y por qué asusta

vim (Vi IMproved) nació en 1991 y está en **absolutamente todos los sistemas Unix/Linux**, incluso los más mínimos (donde nano puede no estar). Es el editor que encontrarás si alguien ejecuta `git commit` sin configurar `$EDITOR`, o si abres un crontab (`crontab -e`) en un sistema sin configurar.

La razón por la que asusta: **vim es modal**. No hay modo "estoy escribiendo texto". Hay que cambiar de modo explícitamente. Si no lo sabes, pareces estar atrapado.

### Los modos de vim

```
                      ┌─────────────────────┐
                      │    MODO NORMAL       │  ← donde arrancas siempre
                      │  (navegar, operar)   │
                      └──────┬──────┬────────┘
                             │      │
               i / a / o     │      │  :
                             ▼      ▼
                    ┌────────────┐ ┌──────────────┐
                    │   INSERT   │ │   COMANDO    │
                    │ (escribir) │ │ (:w :q :wq)  │
                    └────────────┘ └──────────────┘
                         Esc ──────────┘
```

| Modo | Cómo entrar | Qué puedes hacer |
|---|---|---|
| **Normal** | `Esc` (siempre funciona) | Navegar, copiar, borrar, buscar |
| **Insertar** | `i`, `a`, `o` (desde Normal) | Escribir texto |
| **Comando** | `:` (desde Normal) | Guardar, salir, reemplazar global |
| **Visual** | `v` (desde Normal) | Seleccionar texto |

**Regla de oro**: cuando no sabes en qué modo estás, pulsa `Esc` una o dos veces. Siempre vuelves a Normal.

### Entrar y salir de vim — lo mínimo vital

```bash
vim fichero.txt    # abrir
vi fichero.txt     # alias clásico (en Ubuntu 24.04, vi es vim)
```

Al abrir, estás en **modo Normal**. El cursor no escribe.

Para **escribir texto**:
- `i` — insertar antes del cursor
- `a` — insertar después del cursor (append)
- `o` — abrir línea nueva debajo y entrar a insertar
- (ves `-- INSERT --` en la barra inferior cuando estás en modo insertar)

Para **volver a Normal**: `Esc`

Para **guardar y salir** (desde Normal, escribe `:`):

| Comando | Acción |
|---|---|
| `:w` | Guardar (write) sin salir |
| `:q` | Salir (quit) — sólo si no hay cambios |
| `:wq` o `:x` | Guardar **y** salir |
| `:q!` | **Salir sin guardar** — el escape de emergencia |
| `:w !sudo tee %` | Guardar fichero de root que abriste sin sudo |

> Si sólo recuerdas una cosa de vim: **`Esc` + `:q!` + Enter** te saca siempre, sin guardar nada.

### Navegación en modo Normal

No uses las flechas del teclado en vim — existen, pero son lentas conceptualmente. La navegación es:

| Tecla | Movimiento |
|---|---|
| `h` | izquierda |
| `j` | abajo |
| `k` | arriba |
| `l` | derecha |
| `w` | siguiente palabra (word) |
| `b` | palabra anterior (back) |
| `0` | inicio de línea |
| `$` | fin de línea |
| `gg` | ir al **inicio** del fichero |
| `G` | ir al **final** del fichero |
| `5G` | ir a la línea 5 (número + G) |
| `Ctrl+F` | página siguiente (Forward) |
| `Ctrl+B` | página anterior (Back) |

### Operaciones de edición en modo Normal

| Tecla | Acción |
|---|---|
| `dd` | Cortar (borrar) línea entera |
| `yy` | Copiar línea entera (yank) |
| `p` | Pegar después del cursor |
| `P` | Pegar antes del cursor |
| `u` | **Deshacer** (undo) |
| `Ctrl+r` | **Rehacer** (redo) |
| `x` | Borrar carácter bajo el cursor |
| `dw` | Borrar desde cursor hasta fin de palabra |
| `D` | Borrar desde cursor hasta fin de línea |
| `cw` | Cambiar palabra (borra y entra a insertar) |
| `.` | Repetir el último cambio |

### Buscar en vim

Desde modo Normal:

```
/patrón    → buscar hacia adelante (Enter para confirmar)
?patrón    → buscar hacia atrás
n          → siguiente coincidencia
N          → coincidencia anterior
```

Ejemplo: buscar "puerto" en un config → `/puerto` + Enter, luego `n` para ir avanzando.

### Mínimo viable para sobrevivir vim

Si te encuentras en vim sin haberlo elegido:

1. `Esc` (uno o dos veces) — asegúrate de estar en Normal.
2. Si **no quieres guardar**: `:q!` + Enter. Fin.
3. Si **sí quieres guardar**: `:wq` + Enter.
4. Si no pasa nada al escribir `:` — estás en Insert. Pulsa `Esc` primero.

---

## Configurar el editor por defecto

Muchas herramientas (git, crontab, visudo, variables de entorno) respetan `$EDITOR`.

### Variable de entorno $EDITOR

```bash
# Ver cuál está configurado ahora
echo $EDITOR

# Cambiar temporalmente (sólo para la sesión actual)
export EDITOR=nano

# Cambiar permanentemente — añadir a ~/.bashrc o ~/.bash_profile
echo 'export EDITOR=nano' >> ~/.bashrc
source ~/.bashrc
```

### update-alternatives (Ubuntu/Debian)

Ubuntu gestiona el binario `/usr/bin/editor` con el sistema de alternativas:

```bash
# Ver qué editor está configurado como predeterminado
sudo update-alternatives --display editor

# Cambiar el editor del sistema de forma interactiva
sudo update-alternatives --config editor
# Muestra una lista numerada; escribe el número de nano y Enter.
```

Esto afecta a herramientas que llaman a `editor` o `sensible-editor` (como `visudo` si no tiene `$EDITOR` seteado).

### Para git concretamente

```bash
git config --global core.editor nano
# o
git config --global core.editor "vim"
```

---

## Cuándo usar cada uno

| Situación | Editor recomendado | Por qué |
|---|---|---|
| Editar un fichero de config rápido | **nano** | Sin fricción, sin modos |
| Servidor remoto donde sólo existe vi | **vim** (mínimo vital) | No hay alternativa |
| Editar crontab o sudoers | **nano** (tras configurar $EDITOR) | Menos riesgo de guardar accidentalmente algo roto |
| Edición pesada en terminal (refactor, macros) | **vim** | Su potencia lo justifica cuando ya lo conoces |
| Sistema de recovery / initramfs | **vim** o **busybox vi** | nano puede no estar |
| git commit / rebase interactivo | **nano** (para empezar) | Evita confusión con modos de vim |

---

## Gotchas generales

- **vim en modo reemplazar**: si pulsas `Insert` en modo Normal, entras a `-- REPLACE --` (sobreescribe caracteres). Sal con `Esc`.
- **vim pide contraseña de sudo en `:w`**: si abriste un fichero sin permisos, usa `:w !sudo tee %` para guardar igualmente.
- **nano en SSH con Ctrl+S**: en algunos terminales `Ctrl+S` congela el flujo de terminal (XOFF). Si nano deja de responder, `Ctrl+Q` lo desbloquea.
- **`vi` vs `vim`**: en Ubuntu 24.04, `vi` es un alias de `vim`. En sistemas mínimos puede ser `vi` real (busybox), que tiene menos funciones. Los comandos `:wq` y `:q!` funcionan en ambos.
- **Modos de vim en neovim**: si en algún servidor ves `nvim`, los comandos son idénticos — neovim es un fork compatible.

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|índice Linux]]
- [[shell-bash-y-terminal]]
- [[entorno-path-y-dotfiles]]
