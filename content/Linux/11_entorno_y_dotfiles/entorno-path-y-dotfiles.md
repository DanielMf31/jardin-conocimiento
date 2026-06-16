---
title: Entorno, PATH y Dotfiles en Linux
date: 2026-06-12
tags: [programacion/linux, programacion/shell, programacion/dotfiles]
type: nota
status: permanente
source: claude-code
aliases: [variables de entorno linux, PATH linux, dotfiles linux, XDG Base Directory]
---

# Entorno, PATH y Dotfiles en Linux

## Idea central

El **entorno** es un conjunto de variables de clave-valor que cada proceso hereda de su padre. Moldea cada comando que ejecutas: dónde busca ejecutables, qué editor abre, en qué idioma habla el sistema. Los dotfiles son la capa que configura ese entorno al arrancar el shell.

---

## 1. Variables de entorno

### Variables locales vs exportadas

```bash
# Variable LOCAL: solo existe en el shell actual, los procesos hijos NO la ven
MI_VAR="hola"

# Variable EXPORTADA: se hereda por todos los procesos hijos
export MI_VAR="hola"
export EDITOR="nvim"

# Definir y exportar en un solo paso
export MI_VAR="hola"

# Ver si una variable está exportada (aparece con "declare -x")
declare -p MI_VAR
```

> **Gotcha**: si defines `FOO=bar` sin `export` y luego lanzas un script, ese script no verá `FOO`. Solo las variables exportadas forman el *entorno* real del proceso hijo.

### Inspeccionar el entorno

```bash
env                  # todas las variables exportadas del proceso actual
printenv             # ídem (más portátil entre shells)
printenv HOME        # valor de una variable concreta
printenv PATH        # muestra el PATH actual
echo $HOME           # expansión de shell (lee la variable del shell, no solo env)
```

`env` y `printenv` muestran solo las **exportadas**. Para ver también las locales del shell usa `set` (mucho ruido — filtra con grep).

### Variables clave que debes conocer

| Variable | Qué contiene | Ejemplo Ubuntu 24.04 |
|---|---|---|
| `$HOME` | Directorio home del usuario | `/home/usuario` |
| `$USER` | Nombre del usuario activo | `usuario` |
| `$SHELL` | Path al shell de login | `/bin/bash` |
| `$PATH` | Lista de dirs de búsqueda de ejecutables | `/usr/local/bin:/usr/bin:/bin:…` |
| `$EDITOR` | Editor de texto preferido | `nvim` |
| `$VISUAL` | Editor visual (mismo uso que $EDITOR en muchos programas) | `nvim` |
| `$LANG` | Locale del sistema | `es_ES.UTF-8` |
| `$XDG_CONFIG_HOME` | Config de usuario (default: `~/.config`) | `/home/usuario/.config` |
| `$XDG_DATA_HOME` | Datos de usuario (default: `~/.local/share`) | `/home/usuario/.local/share` |
| `$XDG_CACHE_HOME` | Caché de usuario (default: `~/.cache`) | `/home/usuario/.cache` |
| `$PWD` | Directorio de trabajo actual | `/home/usuario/proyectos` |
| `$OLDPWD` | Directorio anterior (`cd -` usa esto) | `/tmp` |

---

## 2. Resolución de comandos vía $PATH

### Cómo funciona $PATH

Cuando escribes `nvim`, el shell busca de **izquierda a derecha** en cada directorio de `$PATH` hasta encontrar un ejecutable con ese nombre. El primer match gana.

```bash
# Ver el PATH formateado (un directorio por línea)
echo $PATH | tr ':' '\n'

# Ver qué ejecutable concreto se usaría
which nvim          # /usr/bin/nvim  (busca en $PATH)
type nvim           # puede decir "nvim is /usr/bin/nvim" o "nvim is an alias"
command -v nvim     # más portable en scripts; devuelve path o vacío si no existe
```

`type` es más informativo que `which`: distingue si es un ejecutable, alias, función o builtin.

```bash
type cd             # "cd is a shell builtin"
type ll             # "ll is aliased to 'ls -alF'"
type python3        # "python3 is /usr/bin/python3"
```

### Añadir un directorio al PATH

```bash
# Solo para la sesión actual (no persiste)
export PATH="$HOME/.local/bin:$PATH"

# Para persistir: añadir en ~/.bashrc (o ~/.profile, ver sección 3)
# Añadir al FINAL de ~/.bashrc:
export PATH="$HOME/.local/bin:$PATH"
```

> **Gotcha**: pon tu directorio al **principio** de $PATH si quieres que tus binarios tengan prioridad sobre los del sistema. Ponlo al final si solo quieres que sea un fallback.

> **Gotcha**: nunca hagas `PATH="$HOME/.local/bin"` sin incluir `$PATH` — perderías todos los directorios del sistema y el shell dejará de encontrar comandos básicos.

---

## 3. Ficheros de arranque de Bash

Esta es la fuente de confusión más clásica de Linux. El comportamiento depende del **tipo de shell**:

### Tipos de shell

| Tipo | Cuándo ocurre | Lee estos ficheros |
|---|---|---|
| **Login shell** | Al hacer login (TTY, SSH, `bash --login`) | `/etc/profile` → `~/.profile` → `~/.bash_profile` (o `~/.bash_login`) |
| **Interactiva no-login** | Terminal gráfica (GNOME Terminal, Alacritty, Kitty…) | `/etc/bash.bashrc` → `~/.bashrc` |
| **No interactiva** | Script ejecutado (`bash script.sh`), cron | Casi nada (solo `$BASH_ENV` si está definido) |

### El patrón canónico en Ubuntu

Ubuntu hace algo inteligente: `~/.profile` incluye esta línea:
```bash
# Si ~/.bashrc existe, léelo
if [ -n "$BASH_VERSION" ]; then
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
fi
```

Esto significa que en Ubuntu **todo termina leyendo `~/.bashrc`**, tanto en login shells como en terminales gráficas. Por eso es el fichero principal donde poner configuración.

### Resumen práctico

```
¿Dónde poner las cosas?

  export PATH, EDITOR, variables de entorno  →  ~/.bashrc  (o ~/.profile si es solo para login)
  alias y funciones                          →  ~/.bashrc
  configuración específica de bash           →  ~/.bashrc
  variables que deben estar en login shells  →  ~/.profile
```

> **Gotcha**: `~/.bash_profile` tiene prioridad sobre `~/.profile` para Bash. Si existe `~/.bash_profile` y NO incluye `. ~/.bashrc`, tu terminal gráfica tendrá un entorno diferente a tu login shell. Ubuntu no crea `~/.bash_profile` por defecto precisamente para evitar esto.

### Recargar cambios sin reiniciar

```bash
source ~/.bashrc    # recarga el fichero en el shell actual
. ~/.bashrc         # equivalente, notación POSIX
```

---

## 4. Alias y funciones en .bashrc

### Alias

Un alias es un atajo de texto: el shell lo expande antes de ejecutar.

```bash
# Ver todos los alias activos
alias

# Definir un alias (en terminal o en ~/.bashrc para que persista)
alias ll='ls -alF --color=auto'
alias gs='git status'
alias grep='grep --color=auto'

# Eliminar un alias temporalmente
unalias ll

# Ver qué hay detrás de un alias
type ll
```

> **Gotcha**: los alias solo funcionan en shells interactivas. En scripts usa funciones.

### Funciones

Las funciones sí funcionan en scripts y permiten lógica más compleja:

```bash
# En ~/.bashrc
mkcd() {
    mkdir -p "$1" && cd "$1"
}

# Uso:
mkcd proyectos/nuevo-dir
```

---

## 5. Estándar XDG Base Directory

El estándar XDG define dónde deben vivir los ficheros de configuración, datos y caché de las aplicaciones. Evita que `$HOME` se llene de carpetas `.miapp` sueltas.

| Directorio XDG | Variable | Default | Qué va aquí |
|---|---|---|---|
| Config | `$XDG_CONFIG_HOME` | `~/.config` | Configuración del usuario |
| Datos | `$XDG_DATA_HOME` | `~/.local/share` | Datos persistentes (plugins, themes…) |
| Caché | `$XDG_CACHE_HOME` | `~/.cache` | Datos regenerables (no hacer backup) |
| Estado | `$XDG_STATE_HOME` | `~/.local/state` | Historial, logs ligeros |
| Binarios | — | `~/.local/bin` | Ejecutables del usuario (añadir al PATH) |

### Conexión con tus dotfiles de Hyprland

Hyprland sigue el estándar XDG. Por eso toda su configuración vive en:

```
~/.config/hypr/
    hyprland.conf       # config principal
    hyprpaper.conf      # fondo de pantalla
    ...
```

Cuando ves `$XDG_CONFIG_HOME` en documentación de cualquier herramienta moderna (Neovim, Alacritty, Waybar, wofi…), significa `~/.config`. Verificarlo:

```bash
echo $XDG_CONFIG_HOME   # si está vacío, el default es ~/.config
ls ~/.config            # verás hypr/, nvim/, alacritty/, etc.
```

---

## 6. Dotfiles: qué son y por qué versionarlos

### Qué son los dotfiles

Los **dotfiles** son los ficheros de configuración de tu entorno. Su nombre empieza por `.` (punto), por eso eran "invisibles" con `ls` tradicional. Incluyen:

```
~/.bashrc               # config del shell
~/.config/hypr/         # Hyprland
~/.config/nvim/         # Neovim
~/.config/alacritty/    # emulador de terminal
~/.gitconfig            # Git
~/.ssh/config           # SSH (¡cuidado con las claves!)
```

### Por qué versionarlos con git

- Reproducibilidad: reconstruyes tu entorno en una máquina nueva en minutos
- Historial: puedes revertir cambios que rompen algo
- Backup natural de tu configuración
- Compartir configuraciones entre máquinas

### Estrategia básica: repo con symlinks

```bash
# 1. Crear el repo
mkdir ~/dotfiles && cd ~/dotfiles && git init

# 2. Mover ficheros al repo y crear symlinks
mv ~/.bashrc ~/dotfiles/bashrc
ln -s ~/dotfiles/bashrc ~/.bashrc

mv ~/.config/hypr ~/dotfiles/hypr
ln -s ~/dotfiles/hypr ~/.config/hypr

# 3. Verificar que el symlink funciona
ls -la ~/.bashrc
# lrwxrwxrwx 1 usuario ... .bashrc -> /home/usuario/dotfiles/bashrc
```

### Estrategia avanzada: bare repo (sin symlinks)

```bash
# Inicializar un bare repo en ~/.dotfiles
git init --bare $HOME/.dotfiles

# Alias para gestionarlo (añadir a ~/.bashrc)
alias dotfiles='git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'

# Uso normal de git pero con 'dotfiles' en lugar de 'git'
dotfiles add ~/.bashrc
dotfiles commit -m "add bashrc"
dotfiles push
```

> **Ventaja del bare repo**: no necesitas symlinks; los ficheros quedan en su ubicación original. Es la estrategia preferida por la comunidad (ver Hacker News "bare git repo dotfiles").

### Qué NO versionar en dotfiles

- `~/.ssh/id_rsa`, `~/.ssh/id_ed25519` — claves privadas SSH
- `~/.netrc` — credenciales de red
- Ficheros con tokens o API keys
- `~/.cache/` — datos regenerables y pesados

Añade un `.gitignore` al repo de dotfiles para protegerte.

---

## Modelo mental: resumen

```
Proceso hijo hereda entorno del padre
        ↓
Shell de login lee ~/.profile (que llama a ~/.bashrc en Ubuntu)
        ↓
Terminal gráfica lee ~/.bashrc directamente
        ↓
~/.bashrc define: PATH, EDITOR, alias, funciones, prompt
        ↓
Cada comando se busca en $PATH de izquierda a derecha
        ↓
Las apps modernas guardan config en ~/.config (XDG)
        ↓
Los dotfiles son esos ficheros — versiónalos
```

---

## Comandos de referencia rápida (READ-ONLY)

```bash
env                         # ver entorno completo
printenv VAR                # ver una variable
echo $PATH | tr ':' '\n'   # PATH línea a línea
which COMANDO               # path del ejecutable
type COMANDO                # tipo: ejecutable, alias, builtin, función
command -v COMANDO          # portable: path o vacío
declare -p VAR              # info sobre una variable
alias                       # ver todos los alias activos
ls -la ~/.config            # ver configs XDG
ls -la ~/.local/bin         # ver binarios del usuario
```

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|índice]]
- [[shell-bash-y-terminal]]
- [[Hyprland/Recetas_Config|dotfiles de Hyprland]]
