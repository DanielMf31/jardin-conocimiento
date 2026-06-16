---
title: Procesado de texto en Linux — grep, sed, awk y pipes
date: 2026-06-12
tags: [programacion/linux, programacion/cli, programacion/bash]
type: nota
status: permanente
source: claude-code
aliases: [grep sed awk, text processing linux, procesado texto unix, pipes linux]
---

# Procesado de texto en Linux — grep, sed, awk y pipes

## Filosofía Unix: todo es texto

Unix fue diseñado con una idea radical: **representar casi todo como texto plano** (logs, configuración, procesos, dispositivos). De ahí surge el principio:

> "Haz una cosa y hazla bien. Conecta programas con pipes."

Un **pipe** `|` toma la salida estándar (stdout) de un programa y la pasa como entrada estándar (stdin) al siguiente. No se escribe nada a disco; la cadena vive en memoria.

```
programa_A | programa_B | programa_C
```

Esto permite componer herramientas simples para hacer tareas complejas sin escribir un script. Es el corazón del trabajo en CLI.

---

## Ver y leer ficheros

### cat — volcar contenido

```bash
cat fichero.txt              # imprime todo el fichero
cat -n fichero.txt           # con números de línea
cat a.txt b.txt > unido.txt  # concatenar dos ficheros
```

Gotcha: `cat fichero | grep patron` es un "Useless Use of Cat". Usa directamente `grep patron fichero`.

### less — paginador interactivo (recomendado para ficheros grandes)

```bash
less /var/log/syslog
less +F /var/log/syslog   # modo "follow" igual que tail -f, Ctrl+C para parar
```

| Tecla | Acción |
|-------|--------|
| `j / k` | Bajar / subir una línea |
| `d / u` | Bajar / subir media página |
| `g / G` | Inicio / final del fichero |
| `/patron` | Buscar hacia adelante |
| `n / N` | Siguiente / anterior resultado |
| `q` | Salir |

### head y tail — primeras/últimas líneas

```bash
head -n 20 fichero.txt      # primeras 20 líneas (default: 10)
tail -n 50 fichero.txt      # últimas 50 líneas
tail -f /var/log/syslog     # seguir en vivo (follow); Ctrl+C para parar
tail -n +5 fichero.txt      # todo excepto las primeras 4 líneas
```

`tail -f` es imprescindible para monitorear logs de aplicaciones, servicios systemd, etc.

### wc — contar

```bash
wc -l fichero.txt    # número de líneas
wc -w fichero.txt    # número de palabras
wc -c fichero.txt    # bytes
wc fichero.txt       # líneas  palabras  bytes  nombre
```

---

## Buscar contenido con grep

### Sintaxis base

```bash
grep "patron" fichero.txt
grep "patron" fichero1.txt fichero2.txt
grep "patron" *.log
```

### Opciones esenciales

| Opción | Significado | Ejemplo |
|--------|-------------|---------|
| `-i` | Ignorar mayúsculas | `grep -i "error" app.log` |
| `-n` | Mostrar número de línea | `grep -n "TODO" *.py` |
| `-r` | Recursivo en directorio | `grep -r "import os" src/` |
| `-v` | Invertir (líneas que NO casan) | `grep -v "^#" config.ini` |
| `-c` | Contar líneas que casan | `grep -c "ERROR" app.log` |
| `-l` | Solo nombres de ficheros que tienen el patrón | `grep -rl "SECRET" .` |
| `-E` | Regex extendida (ERE) | `grep -E "error|warn" app.log` |
| `-o` | Solo la parte que casa (no la línea entera) | `grep -oE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" access.log` |
| `-A n` | n líneas de contexto después del match | `grep -A 3 "Exception" app.log` |
| `-B n` | n líneas de contexto antes del match | `grep -B 2 "FATAL" app.log` |

### Regex básicas en grep

```
.         cualquier carácter
*         cero o más del carácter anterior
^         inicio de línea
$         fin de línea
[abc]     uno de a, b o c
[^abc]    ninguno de a, b, c
\b        límite de palabra (con -E o -w)
```

Con `-E` (ERE) se añaden:

```
+         uno o más
?         cero o uno
{n,m}     entre n y m repeticiones
(a|b)     alternativa: a o b
```

```bash
# Líneas que empiezan con "Error"
grep "^Error" app.log

# Líneas vacías
grep "^$" fichero.txt

# IPs en un log de acceso
grep -oE "([0-9]{1,3}\.){3}[0-9]{1,3}" access.log

# Líneas que terminan en punto y coma
grep ";$" script.sql
```

Gotcha: con `-r` sobre directorios grandes, añade `--include="*.log"` para no escanear binarios:
```bash
grep -r --include="*.py" "def " src/
```

---

## Buscar ficheros con find

### Sintaxis base

```bash
find <directorio_inicio> [condiciones] [acciones]
find . -name "*.log"         # busca desde directorio actual
find /etc -name "*.conf"
```

### Condiciones principales

| Condición | Ejemplo | Significado |
|-----------|---------|-------------|
| `-name "*.py"` | `find . -name "*.py"` | Por nombre (glob, case-sensitive) |
| `-iname "*.PY"` | `find . -iname "*.py"` | Por nombre (case-insensitive) |
| `-type f` | `find . -type f` | Solo ficheros regulares |
| `-type d` | `find . -type d` | Solo directorios |
| `-size +10M` | `find . -size +10M` | Más de 10 MB |
| `-size -1k` | `find . -size -1k` | Menos de 1 KB |
| `-mtime -7` | `find . -mtime -7` | Modificado hace menos de 7 días |
| `-mtime +30` | `find . -mtime +30` | Modificado hace más de 30 días |
| `-maxdepth 2` | `find . -maxdepth 2 -name "*.py"` | No bajar más de 2 niveles |
| `! -name "*.log"` | `find . ! -name "*.log"` | Negación |

### Acciones: -exec y -delete

```bash
# Ejecutar un comando por cada resultado
find . -name "*.tmp" -exec rm {} \;
# {} es el placeholder para el nombre de fichero
# \; termina el comando por cada fichero individualmente

# Más eficiente: pasar todos los ficheros juntos a rm
find . -name "*.tmp" -exec rm {} +

# Borrar directamente (equivalente pero más rápido)
find . -name "*.tmp" -delete

# Cambiar permisos a todos los .sh
find . -name "*.sh" -exec chmod +x {} +

# Ver los últimos 5 logs modificados
find /var/log -name "*.log" -mtime -1 | head -5
```

Gotcha: `find` sin `-maxdepth` puede ser muy lento en `/` o en directorios grandes. Siempre busca desde una ruta específica.

---

## Transformar texto con sed

sed (Stream EDitor) lee línea a línea y aplica transformaciones. Su comando más usado es la sustitución.

### Sustitución: `s/patron/reemplazo/flags`

```bash
# Reemplazar primera ocurrencia por línea
sed 's/foo/bar/' fichero.txt

# Reemplazar TODAS las ocurrencias (flag g = global)
sed 's/foo/bar/g' fichero.txt

# Case-insensitive
sed 's/foo/bar/gI' fichero.txt

# Solo mostrar líneas que cambiaron (-n + p)
sed -n 's/foo/bar/p' fichero.txt
```

### -i: editar el fichero in-place

```bash
# Modifica el fichero directamente (¡sin backup!)
sed -i 's/localhost/127.0.0.1/g' config.ini

# Con backup de seguridad (.bak)
sed -i.bak 's/localhost/127.0.0.1/g' config.ini
```

Gotcha: en Ubuntu/Linux, `-i` no necesita argumento. En macOS BSD sed, es obligatorio: `-i ''`.

### Borrar líneas

```bash
# Borrar líneas que contengan "DEBUG"
sed '/DEBUG/d' app.log

# Borrar líneas vacías
sed '/^$/d' fichero.txt

# Borrar líneas 3 a 7
sed '3,7d' fichero.txt

# Borrar comentarios (líneas que empiezan con #)
sed '/^#/d' config.ini
```

### Imprimir rangos de líneas

```bash
sed -n '10,20p' fichero.txt     # imprime líneas 10 a 20
sed -n '/START/,/END/p' log.txt # imprime desde "START" hasta "END"
```

---

## Procesar campos con awk

awk es un lenguaje completo orientado a registros y campos. Perfecto para datos tabulares (logs con columnas, CSVs sencillos, `/proc/meminfo`, etc.).

### Modelo mental

```
awk 'patron { accion }' fichero
```

awk procesa línea a línea. Por cada línea que casa con el patrón, ejecuta la acción. Si no hay patrón, la acción se ejecuta en todas las líneas.

### Variables automáticas

| Variable | Significado |
|----------|-------------|
| `$0` | Línea completa |
| `$1`, `$2`, `$NF` | Campo 1, 2, último campo |
| `NF` | Número de campos en la línea actual |
| `NR` | Número de línea (registro) actual |
| `FS` | Separador de campos (default: espacio/tab) |

### Separador con -F

```bash
# Campos separados por coma (CSV básico)
awk -F',' '{print $1, $3}' datos.csv

# Separador dos puntos (como /etc/passwd)
awk -F':' '{print $1, $3}' /etc/passwd

# Imprimir el último campo de cada línea
awk '{print $NF}' fichero.txt
```

### Patrones y condiciones

```bash
# Líneas donde el campo 3 es mayor que 100
awk '$3 > 100 {print $0}' datos.txt

# Líneas que contienen "ERROR"
awk '/ERROR/ {print NR, $0}' app.log

# BEGIN y END: bloques especiales
awk 'BEGIN {suma=0} {suma += $2} END {print "Total:", suma}' ventas.txt
```

### Ejemplos prácticos de awk

```bash
# Imprimir columnas 1 y 4 de ps aux
ps aux | awk '{print $1, $4}'

# Suma de la columna 5 de un fichero
awk '{suma += $5} END {print suma}' datos.txt

# Usuarios del sistema con UID >= 1000 (campo 3 de /etc/passwd)
awk -F':' '$3 >= 1000 {print $1, $3}' /etc/passwd

# Promedio de la columna 2
awk '{suma += $2; n++} END {print "Promedio:", suma/n}' datos.txt
```

---

## Utilidades de columna y orden

### cut — extraer columnas por posición o delimitador

```bash
cut -d',' -f1,3 datos.csv     # campos 1 y 3, separador coma
cut -d':' -f1 /etc/passwd     # solo nombres de usuario
cut -c1-10 fichero.txt        # caracteres 1 al 10 de cada línea
```

### sort — ordenar líneas

```bash
sort fichero.txt              # alfabético
sort -r fichero.txt           # orden inverso
sort -n numeros.txt           # numérico
sort -k2 -n tabla.txt         # por campo 2, numérico
sort -u fichero.txt           # eliminar duplicados al ordenar
```

### uniq — eliminar duplicados consecutivos (necesita sort previo)

```bash
sort fichero.txt | uniq          # eliminar duplicados
sort fichero.txt | uniq -c       # contar ocurrencias
sort fichero.txt | uniq -d       # solo líneas duplicadas
```

### tr — traducir/borrar caracteres

```bash
echo "Hola Mundo" | tr 'a-z' 'A-Z'   # minúsculas a mayúsculas
echo "a:b:c" | tr ':' ','             # cambiar separador
cat fichero.txt | tr -d '\r'           # eliminar retornos de carro Windows
echo "aabbcc" | tr -s 'a-z'           # comprimir repetidos: "abc"
```

### column — alinear en columnas

```bash
cat /etc/passwd | column -t -s':'    # tabla alineada, separador ':'
mount | column -t                    # salida de mount alineada
```

### xargs — construir y ejecutar comandos desde stdin

```bash
# Borrar todos los .log que encuentra find
find . -name "*.log" | xargs rm

# Con espacios en nombres de fichero, usar null-separated
find . -name "*.log" -print0 | xargs -0 rm

# Ejecutar en paralelo (4 procesos)
cat urls.txt | xargs -P 4 wget

# Pasar argumento en posición específica con -I
cat ficheros.txt | xargs -I{} cp {} /backup/
```

---

## Recetas de pipes reales

### 1. Los 10 procesos que más RAM consumen

```bash
ps aux --sort=-%mem | head -11 | awk '{printf "%-20s %s%%\n", $11, $4}'
```

### 2. Contar errores por tipo en un log

```bash
grep -oE "ERROR|WARN|FATAL" app.log | sort | uniq -c | sort -rn
```

### 3. Buscar y reemplazar en varios ficheros (con backup)

```bash
find . -name "*.py" -exec sed -i.bak 's/old_function/new_function/g' {} +
```

### 4. IPs que más veces aparecen en un log de acceso

```bash
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10
```

### 5. Ver qué puertos están escuchando (con nombres de proceso)

```bash
ss -tlnp | awk 'NR>1 {print $4, $6}' | column -t
```

### 6. Listar los ficheros más grandes de un directorio

```bash
find . -type f -printf "%s\t%p\n" | sort -rn | head -20 | awk '{printf "%.1f MB\t%s\n", $1/1048576, $2}'
```

### 7. Extraer todos los correos de un fichero

```bash
grep -oE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" fichero.txt | sort -u
```

### 8. Monitorear en vivo errores mientras aparecen

```bash
tail -f /var/log/syslog | grep --line-buffered -i "error\|fail\|warn"
```

Nota: `--line-buffered` fuerza flush línea a línea en pipes con `tail -f`.

---

## Tabla de referencia rápida

| Herramienta | Para qué | Comando típico |
|-------------|----------|----------------|
| `grep` | Buscar líneas por patrón | `grep -rn "patron" dir/` |
| `find` | Buscar ficheros | `find . -name "*.py" -mtime -7` |
| `sed` | Sustituir/borrar texto | `sed -i 's/old/new/g' file` |
| `awk` | Procesar campos/columnas | `awk '{print $1, $NF}' file` |
| `cut` | Extraer columna por delimitador | `cut -d',' -f2 csv` |
| `sort` | Ordenar líneas | `sort -rn file` |
| `uniq` | Contar/eliminar duplicados | `sort file \| uniq -c` |
| `tr` | Traducir caracteres | `tr 'a-z' 'A-Z'` |
| `wc` | Contar líneas/palabras | `wc -l file` |
| `xargs` | Construir comandos desde stdin | `find . -name "*.tmp" \| xargs rm` |

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|índice]]
- [[shell-bash-y-terminal]]
- [[scripting-en-bash]]
