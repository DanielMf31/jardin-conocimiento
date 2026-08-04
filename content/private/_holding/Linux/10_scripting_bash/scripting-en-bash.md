---
title: Scripting en Bash
date: 2026-06-12
tags: [programacion/linux, programacion/bash, programacion/shell]
type: nota
status: permanente
source: claude-code
aliases: [bash scripting, shell scripting, scripts bash]
---

# Scripting en Bash

## Idea central

Bash es un lenguaje de pegamento: orquesta comandos del sistema, no computa. Su modelo de ejecución es radicalmente distinto a Python/C — todo se basa en texto, procesos y exit codes. Las trampas vienen casi siempre del quoting y del word splitting.

---

## 1. Anatomía de un script

```bash
#!/usr/bin/env bash
# Shebang: le dice al kernel con qué intérprete ejecutar este archivo.
# Usar /usr/bin/env bash en vez de /bin/bash: más portable entre sistemas.

set -euo pipefail
# set -e  → aborta si cualquier comando falla (exit code != 0)
# set -u  → aborta si usas una variable no definida (evita bugs silenciosos)
# set -o pipefail → el pipe falla si CUALQUIER comando del pipe falla
#   Sin esto: echo "hola" | false; echo $?  →  0  (¡bug silencioso!)
# Esta línea va SIEMPRE al principio de scripts de producción.

echo "Hola desde bash"
```

### Permisos y formas de ejecutar

```bash
chmod +x script.sh          # dar permiso de ejecución

./script.sh                 # ejecuta en subshell; el shebang determina el intérprete
bash script.sh              # ejecuta en subshell con bash, IGNORA el shebang
source script.sh            # ejecuta en el shell ACTUAL (mismo proceso)
. script.sh                 # equivalente a source
```

| Forma | Subshell | Usa shebang | Hereda y MODIFICA env padre |
|---|---|---|---|
| `./script.sh` | sí | sí | no |
| `bash script.sh` | sí | no | no |
| `source script.sh` | no | no | **sí** |

**Cuándo usar `source`**: cuando el script define variables de entorno o cambia el directorio de trabajo y quieres que persistan en tu shell actual (ej: activar un venv, cargar dotfiles).

---

## 2. Variables

```bash
# Asignación: SIN espacios alrededor del =
nombre="Daniel"           # correcto
nombre = "Daniel"         # ERROR: bash interpreta 'nombre' como comando

# Lectura
echo $nombre              # funciona pero peligroso (word splitting)
echo "$nombre"            # correcto — siempre entre comillas dobles
echo "${nombre}"          # forma canónica — desambigua de texto adyacente
echo "${nombre}_backup"   # imprime "Daniel_backup"

# Variables de entorno vs locales
export PATH="$PATH:/mi/ruta"   # exportar: visible en subprocesos
MI_VAR="solo aquí"             # local al script (no se hereda)

# Variables especiales útiles
echo "$HOME"        # directorio home del usuario
echo "$PWD"         # directorio actual
echo "$USER"        # nombre del usuario actual
echo "$RANDOM"      # número aleatorio 0-32767

# Valores por defecto (muy idiomático)
nombre="${1:-mundo}"          # si $1 está vacío/no existe, usa "mundo"
dir="${TARGET_DIR:-/tmp}"     # útil para variables de entorno opcionales
```

### Por qué SIEMPRE entre comillas

```bash
archivo="mi archivo con espacios.txt"

ls $archivo       # FALLA: bash lo expande a   ls mi archivo con espacios.txt
                  # (3 argumentos separados)

ls "$archivo"     # correcto: un solo argumento con el nombre exacto

# Globbing también sorprende:
patron="*.txt"
echo $patron      # expande los archivos .txt del directorio actual (¡no el string!)
echo "$patron"    # imprime literalmente "*.txt"
```

---

## 3. Sustitución de comandos

```bash
# Capturar la salida de un comando en una variable
fecha=$(date +%Y-%m-%d)
usuario=$(whoami)
lineas=$(wc -l < archivo.txt)

# Anidado
ruta_script=$(dirname "$(realpath "$0")")

# Forma antigua con backticks — evitar: no se puede anidar fácilmente
fecha=`date`   # funciona pero $(...) es superior en todos los sentidos
```

---

## 4. Argumentos del script

```bash
#!/usr/bin/env bash
# Invocado como:  ./script.sh arg1 arg2 arg3

echo "Nombre del script: $0"
echo "Primer argumento:  $1"
echo "Segundo argumento: $2"
echo "Número de args:    $#"
echo "Todos los args:    $@"   # PREFERIR $@ sobre $*

# $@ vs $*
# "$@" → expande a una lista de strings correctamente quoted: "$1" "$2" "$3"
# "$*" → expande a un único string con todos juntos: "$1 $2 $3"
# La diferencia importa cuando los argumentos contienen espacios

# Iterar sobre todos los argumentos de forma segura
for arg in "$@"; do
    echo "Arg: $arg"
done

# Shift: consume $1 y desplaza el resto
while [[ $# -gt 0 ]]; do
    echo "Procesando: $1"
    shift
done
```

---

## 5. Entrada interactiva

```bash
# Leer una línea del usuario
read -p "Introduce tu nombre: " nombre
echo "Hola, ${nombre}"

# Leer sin mostrar lo escrito (contraseñas)
read -s -p "Contraseña: " pass
echo ""   # salto de línea tras el campo oculto

# Leer con timeout
read -t 10 -p "Tienes 10s: " respuesta || echo "Timeout."
```

---

## 6. Condicionales

### `` vs ``

| Característica | `` (test POSIX) | `` (bash built-in) |
|---|---|---|
| Portabilidad | sh, dash, bash | Solo bash/zsh |
| Word splitting | sí (peligroso) | no |
| Regex con `=~` | no | sí |
| `&&` / `\|\|` dentro | no | sí |
| Recomendado en bash | no | **sí** |

```bash
#!/usr/bin/env bash

archivo="/etc/passwd"
cadena="hola"
numero=42

# ----- Condiciones de fichero -----
if [[ -f "$archivo" ]]; then echo "es fichero regular"; fi
if [[ -d "/etc" ]];     then echo "es directorio"; fi
if [[ -e "$archivo" ]]; then echo "existe (cualquier tipo)"; fi
if [[ -r "$archivo" ]]; then echo "tengo permiso de lectura"; fi
if [[ -z "$cadena" ]];  then echo "string vacío"; fi
if [[ -n "$cadena" ]];  then echo "string no vacío"; fi

# ----- Comparación de strings -----
if [[ "$cadena" == "hola" ]];   then echo "igual"; fi
if [[ "$cadena" != "adios" ]];  then echo "distinto"; fi
if [[ "$cadena" =~ ^h[oa] ]];  then echo "regex match"; fi   # solo [[ ]]

# ----- Comparación de números -----
# Los operadores de string (< >) hacen orden lexicográfico, usar -lt/-gt para nums
if [[ $numero -eq 42 ]]; then echo "igual a 42"; fi
if [[ $numero -lt 100 ]]; then echo "menor que 100"; fi
if [[ $numero -ge 10 ]];  then echo "mayor o igual que 10"; fi
# -eq -ne -lt -le -gt -ge

# ----- if / elif / else -----
if [[ $numero -gt 50 ]]; then
    echo "grande"
elif [[ $numero -gt 20 ]]; then
    echo "mediano"
else
    echo "pequeño"
fi
```

---

## 7. Bucles

```bash
# ----- for sobre lista literal -----
for fruta in manzana pera naranja; do
    echo "$fruta"
done

# ----- for sobre expansión de glob -----
for f in /etc/*.conf; do
    echo "Config: $f"
done

# ----- for aritmético (estilo C) -----
for ((i = 0; i < 5; i++)); do
    echo "i = $i"
done

# ----- for sobre array -----
archivos=("a.txt" "b.txt" "c.txt")
for f in "${archivos[@]}"; do      # siempre con "${...[@]}" para arrays
    echo "$f"
done

# ----- while -----
contador=0
while [[ $contador -lt 5 ]]; do
    echo "$contador"
    ((contador++))
done

# ----- until (inverso de while) -----
until [[ -f /tmp/señal ]]; do
    echo "Esperando..."
    sleep 1
done

# ----- Leer fichero línea a línea (IDIOMÁTICO) -----
while IFS= read -r linea; do
    echo "→ $linea"
done < /etc/hosts
# IFS=  evita que se recorten espacios al inicio/final
# -r    evita que \ al final de línea continúe en la siguiente

# Trampa frecuente: pipe a while abre subshell
# cat fichero | while read linea; do    # MAL: variables internas no persisten
#   total=$((total + 1))                # total se pierde al salir del subshell
# done
# Usar redirección < o process substitution: while read ...; do ... done < <(cmd)
```

---

## 8. Funciones

```bash
#!/usr/bin/env bash

# Definición (dos sintaxis equivalentes)
saludar() {
    local nombre="$1"    # 'local' limita la variable al scope de la función
    echo "Hola, ${nombre}"
}

function despedir {       # alternativa con keyword 'function'
    echo "Adiós, $1"
}

# Llamada (sin paréntesis, igual que un comando)
saludar "Daniel"
despedir "mundo"

# Retorno de valores
# return solo devuelve exit code (0-255), NO un valor
# Para devolver datos: usar echo + captura con $()
sumar() {
    local a="$1"
    local b="$2"
    echo $((a + b))    # "imprimir" el resultado
}

resultado=$(sumar 3 4)
echo "3 + 4 = $resultado"

# Comprobar si una función falló
hacer_copia() {
    cp "$1" "$2" || return 1    # propaga el fallo
    echo "Copia OK"
}

if hacer_copia origen.txt destino.txt; then
    echo "Éxito"
else
    echo "Falló la copia"
fi
```

---

## 9. Exit codes y control de flujo

```bash
# $? contiene el exit code del ÚLTIMO comando (0 = éxito, !=0 = fallo)
ls /etc/passwd
echo "Exit code: $?"    # 0

ls /no/existe
echo "Exit code: $?"    # 2

# && y || como control de flujo (muy idiomático)
mkdir -p /tmp/mi_dir && echo "Directorio creado"
cd /ruta/invalida || { echo "Error: directorio no existe" >&2; exit 1; }
#                      ^^^ las llaves agrupan comandos; >&2 redirige a stderr

# exit con código explícito
validar_arg() {
    if [[ -z "$1" ]]; then
        echo "Error: argumento requerido" >&2
        exit 1    # convención: 1 = error genérico
    fi
}

# Convenciones de exit codes
# 0   → éxito
# 1   → error genérico
# 2   → uso incorrecto (argumentos mal)
# 126 → permiso denegado para ejecutar
# 127 → comando no encontrado
```

---

## 10. Case

```bash
# Alternativa idiomática al if-elif largo sobre strings
day=$(date +%u)   # 1=lunes ... 7=domingo

case "$day" in
    1|2|3|4|5)
        echo "Día laborable"
        ;;
    6|7)
        echo "Fin de semana"
        ;;
    *)
        echo "Valor inesperado: $day"
        ;;
esac

# Con globs
case "$archivo" in
    *.tar.gz)  echo "Tarball comprimido" ;;
    *.zip)     echo "ZIP" ;;
    *.txt)     echo "Texto plano" ;;
    *)         echo "Tipo desconocido" ;;
esac
```

---

## 11. Arrays (breve)

```bash
# Declaración
frutas=("manzana" "pera" "naranja con espacios")

# Acceso
echo "${frutas[0]}"           # manzana
echo "${frutas[2]}"           # naranja con espacios
echo "${frutas[@]}"           # todos los elementos
echo "${#frutas[@]}"          # número de elementos

# Añadir
frutas+=("kiwi")

# Iterar (siempre con "${array[@]}" para preservar elementos con espacios)
for f in "${frutas[@]}"; do
    echo "$f"
done

# Arrays asociativos (bash 4+)
declare -A colores
colores["rojo"]="#FF0000"
colores["verde"]="#00FF00"
echo "${colores[rojo]}"
```

---

## 12. Las trampas clásicas

| Trampa | Ejemplo problemático | Forma correcta |
|---|---|---|
| Word splitting | `cp $origen $destino` | `cp "$origen" "$destino"` |
| Globbing inesperado | `echo $patron` | `echo "$patron"` |
| Espacios en asignación | `var = "valor"` | `var="valor"` |
| `` con strings vacíos | `[ $var == "x" ]` (falla si vacío) | `` |
| Pipe a while (subshell) | `cmd \| while read l; do x=$l; done` | `while read l; do ...; done < <(cmd)` |
| Comparar números con `<` | `` → false (lexicográfico) | `` |
| `$*` con espacios en args | `for a in "$*"` | `for a in "$@"` |
| No chequear exit codes | `comando; echo "ok"` siempre imprime ok | `set -e` o `|| exit 1` |
| `cd` sin verificar | `cd /ruta; rm -rf *` | `cd /ruta || exit 1` |

---

## 13. Script de ejemplo realista

```bash
#!/usr/bin/env bash
# backup_configs.sh — copia archivos de configuración a un directorio destino
# Uso: ./backup_configs.sh <directorio_destino>
# Ejemplo: ./backup_configs.sh ~/backups/configs

set -euo pipefail

# ---------- Constantes ----------
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONFIGS=(
    "$HOME/.bashrc"
    "$HOME/.bash_profile"
    "$HOME/.gitconfig"
)

# ---------- Funciones ----------
log() {
    # Escribe a stderr con timestamp (no contamina stdout)
    echo "[$(date +%H:%M:%S)] $*" >&2
}

die() {
    log "ERROR: $*"
    exit 1
}

usage() {
    echo "Uso: $0 <directorio_destino>" >&2
    exit 2
}

# ---------- Validación de argumentos ----------
[[ $# -eq 1 ]] || usage

destino="$1"

# ---------- Preparar destino ----------
if [[ ! -d "$destino" ]]; then
    log "Creando directorio: $destino"
    mkdir -p "$destino" || die "No se pudo crear $destino"
fi

# ---------- Copiar archivos ----------
copiados=0
omitidos=0

for cfg in "${CONFIGS[@]}"; do
    if [[ ! -f "$cfg" ]]; then
        log "Omitiendo (no existe): $cfg"
        ((omitidos++))
        continue
    fi

    nombre=$(basename "$cfg")
    destino_archivo="${destino}/${nombre}.${TIMESTAMP}"

    cp "$cfg" "$destino_archivo"
    log "Copiado: $cfg → $destino_archivo"
    ((copiados++))
done

# ---------- Resumen ----------
log "Completado: $copiados copiados, $omitidos omitidos."
echo "$destino"    # stdout limpio: solo el directorio resultado (composable con $())
```

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|índice]]
- [[shell-bash-y-terminal]]
- [[procesado-de-texto-grep-sed-awk]]
