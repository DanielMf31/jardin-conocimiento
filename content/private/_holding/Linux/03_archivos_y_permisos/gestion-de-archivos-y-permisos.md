---
title: Gestión de archivos y permisos en Linux
date: 2026-06-12
tags: [programacion/linux, programacion/linux/archivos, programacion/linux/permisos]
type: nota
status: permanente
source: claude-code
aliases: [permisos linux, chmod, chown, umask, permisos unix, rm -rf, ln simbolico]
---

# Gestión de archivos y permisos en Linux

## Modelo mental de partida

En Linux **todo es un archivo** (archivos regulares, directorios, dispositivos, sockets...). El sistema de permisos se aplica de forma uniforme a todos ellos. Antes de ejecutar cualquier operación, el kernel pregunta: ¿quién eres tú? ¿qué relación tienes con este archivo? ¿tienes permiso para hacer lo que pides?

---

## 1. Operaciones básicas sobre archivos

### Copiar — `cp`

```bash
cp origen destino           # copia un archivo
cp -r directorio/ destino/  # copia recursiva (obligatorio para directorios)
cp -i origen destino        # pregunta antes de sobreescribir (interactive)
cp -v origen destino        # muestra qué está copiando (verbose)
cp -rv directorio/ destino/ # combinación habitual: recursivo + verbose
cp -p origen destino        # preserva permisos, timestamps y propietario
```

**Gotcha**: `cp` sin `-i` sobreescribe en silencio. En scripts de producción, siempre `-i` o comprueba antes con `[ -f destino ]`.

### Mover / renombrar — `mv`

```bash
mv archivo.txt nuevo_nombre.txt   # renombrar
mv archivo.txt /ruta/destino/     # mover
mv -i origen destino              # preguntar si sobreescribe
mv -v origen destino              # verbose
```

`mv` dentro del mismo sistema de archivos es instantáneo (solo actualiza el directorio). Entre sistemas de archivos distintos equivale a `cp` + `rm`.

### Borrar — `rm`

```bash
rm archivo.txt              # borrar archivo
rm -r directorio/           # borrar directorio y todo su contenido
rm -i archivo.txt           # confirmar cada borrado
rm -v archivo.txt           # verbose
```

> **PELIGRO MAXIMO — `rm -rf`**
>
> ```bash
> rm -rf /ruta/a/borrar     # borra sin preguntar, sin papelera, sin vuelta atrás
> ```
>
> No hay "deshacer". Un error tipográfico (`rm -rf / ruta` con espacio) puede arrasar el sistema. Reglas de oro:
> - Nunca ejecutar como root si puedes evitarlo.
> - Comprueba la ruta con `ls` antes.
> - Usa `trash-cli` como alternativa (`trash archivo`) para tener papelera en terminal.
> - En scripts, añade `set -e` y valida que la variable no esté vacía: `rm -rf "${DIR:?variable vacía}"`.

### Crear directorios — `mkdir`

```bash
mkdir nueva_carpeta
mkdir -p ruta/intermedia/nueva    # crea todos los directorios intermedios
mkdir -p proyecto/{src,tests,docs} # expansión de llaves: crea 3 subdirectorios
```

### Eliminar directorios vacíos — `rmdir`

```bash
rmdir directorio_vacio    # falla si tiene contenido (seguro por eso)
```

### Crear / actualizar timestamps — `touch`

```bash
touch archivo.txt         # crea si no existe; actualiza fecha de modificación si existe
touch -t 202601011200 archivo.txt  # fijar timestamp manualmente
```

---

## 2. Enlaces: duros y simbólicos

### Enlace duro (`ln`)

```bash
ln archivo_original enlace_duro
```

- Apunta **directamente al mismo inodo** (los datos en disco).
- No hay "original" vs "enlace": ambos son el mismo archivo con dos nombres.
- Si borras uno, el otro sigue funcionando.
- Limitación: no pueden cruzar sistemas de archivos ni enlazar directorios.

### Enlace simbólico (`ln -s`)

```bash
ln -s /ruta/al/objetivo enlace_simbolico
ln -s ../relativa/ruta  enlace_relativo  # las rutas relativas se resuelven desde donde vive el enlace
```

- Es un archivo especial que **contiene la ruta** al objetivo.
- Si borras el objetivo, el enlace queda "roto" (dangling symlink).
- Puede cruzar sistemas de archivos, puede enlazar directorios.
- `ls -la` muestra `->` hacia el objetivo.

### Cuándo usar cada uno

| Situación | Tipo de enlace |
|---|---|
| Alias de ejecutables en `/usr/local/bin` | Simbólico |
| Versionado: `python3 -> python3.12` | Simbólico |
| Archivos de config que deben vivir en dos sitios | Simbólico |
| Copia de seguridad "sin duplicar datos" en el mismo disco | Duro |
| Referencia que debe sobrevivir al renombrado del origen | Duro |

---

## 3. El sistema de permisos Unix

### 3.1 Tres actores: usuario / grupo / otros

Cada archivo tiene:
- **Propietario** (`user`, `u`): quien lo creó (normalmente).
- **Grupo** (`group`, `g`): un grupo del sistema al que pertenece el archivo.
- **Otros** (`others`, `o`): cualquier usuario que no sea el propietario ni miembro del grupo.

El kernel comprueba en orden: ¿eres el propietario? → aplica permisos de `u`. ¿Perteneces al grupo? → aplica `g`. Si no, aplica `o`.

### 3.2 Tres permisos: r / w / x

| Letra | Valor | Sobre ARCHIVO | Sobre DIRECTORIO |
|---|---|---|---|
| `r` (read) | 4 | Leer contenido | Listar (`ls`) |
| `w` (write) | 2 | Modificar / borrar contenido | Crear, renombrar, borrar archivos dentro |
| `x` (execute) | 1 | Ejecutar como programa | **Entrar** (`cd`) y acceder a rutas dentro |

> El permiso `x` en un directorio es el permiso de **atravesarlo**. Sin `x`, no puedes `cd` ni acceder a nada dentro, aunque tengas `r`. Con solo `x` (sin `r`) puedes entrar pero no listar. El caso habitual es `rx` juntos.

### 3.3 Leer la salida de `ls -l` — los 10 caracteres

```
-rwxr-xr--  1 daniel developers 4096 Jun 12 10:00 script.sh
^  ^  ^  ^
|  |  |  └── otros    (r--)
|  |  └───── grupo    (r-x)
|  └──────── propietario (rwx)
└─────────── tipo de archivo
```

**Carácter de tipo**:
| Char | Tipo |
|---|---|
| `-` | archivo regular |
| `d` | directorio |
| `l` | enlace simbólico |
| `c` | dispositivo de caracteres |
| `b` | dispositivo de bloques |
| `p` | named pipe |
| `s` | socket |

### 3.4 Permisos en octal

Cada triada `rwx` se convierte a un dígito sumando: r=4, w=2, x=1.

```
rwx = 4+2+1 = 7
r-x = 4+0+1 = 5
r-- = 4+0+0 = 4
--- = 0
```

El permiso completo se expresa como **tres dígitos** (uno por triada):

| Octal | Triada | Significado habitual |
|---|---|---|
| `7` | `rwx` | total |
| `6` | `rw-` | leer y escribir |
| `5` | `r-x` | leer y ejecutar |
| `4` | `r--` | solo lectura |
| `0` | `---` | sin acceso |

### Tabla de combinaciones frecuentes

| Permiso | Archivos | Directorios |
|---|---|---|
| `755` | ejecutable público (`rwxr-xr-x`) | directorio navegable por todos |
| `644` | archivo de texto/config (`rw-r--r--`) | — (inusual en dirs) |
| `600` | clave SSH privada (`rw-------`) | solo el propietario entra |
| `700` | script privado (`rwx------`) | directorio totalmente privado |
| `777` | todo para todos — **evitar** | todo para todos — **evitar** |
| `664` | compartido en grupo (`rw-rw-r--`) | archivos editables por grupo |

---

## 4. Modificar permisos y propietario

### `chmod` — cambiar permisos

**Notación octal** (directa, ideal para scripts):
```bash
chmod 755 script.sh
chmod 644 config.txt
chmod -R 755 directorio/   # recursivo (mayúscula -R)
```

**Notación simbólica** (legible, ideal para cambios puntuales):
```bash
chmod u+x script.sh        # añadir ejecutar al propietario
chmod go-w archivo.txt     # quitar escritura a grupo y otros
chmod a+r documento.pdf    # añadir lectura a todos (a = all = ugo)
chmod u=rw,go=r config     # asignar exactamente: propietario rw, resto r
```

Operadores simbólicos: `+` añade, `-` quita, `=` asigna exactamente.

### `chown` — cambiar propietario (y/o grupo)

```bash
sudo chown nuevo_usuario archivo.txt
sudo chown nuevo_usuario:nuevo_grupo archivo.txt
sudo chown :nuevo_grupo archivo.txt    # solo cambiar grupo
sudo chown -R usuario:grupo directorio/
```

Requiere `sudo` salvo que seas root. Un usuario normal no puede `chown` a otro usuario.

### `chgrp` — cambiar solo el grupo

```bash
sudo chgrp developers proyecto/
sudo chgrp -R www-data /var/www/html/
```

Equivalente a `chown :grupo`. Puedes usarlo sin sudo si eres el propietario y perteneces al grupo destino.

---

## 5. `umask` — permisos por defecto al crear archivos

`umask` define qué permisos se **restan** de los máximos al crear nuevos archivos.

```bash
umask            # mostrar umask actual (ej: 0022)
umask 027        # cambiar temporalmente (en sesión actual)
```

Máximos base: `666` para archivos, `777` para directorios.

```
umask 022:
  archivos:     666 - 022 = 644  (rw-r--r--)
  directorios:  777 - 022 = 755  (rwxr-xr-x)

umask 027:
  archivos:     666 - 027 = 640  (rw-r-----)
  directorios:  777 - 027 = 750  (rwxr-x---)
```

> Nota: la resta es bit a bit (operación AND con el complemento), no aritmética pura. El resultado en la práctica es el mismo para valores estándar.

Para que persista, añadir `umask 022` (o el valor deseado) a `~/.bashrc` o `~/.profile`.

---

## 6. Bits especiales: setuid, setgid, sticky bit

Aparecen en la posición de `x` como `s` o `t`:

```
-rwsr-xr-x   # setuid activado (s en posición de x del propietario)
drwxrwxrwt   # sticky bit activado (t en posición de x de otros)
```

| Bit | Octal | Sobre ejecutable | Sobre directorio |
|---|---|---|---|
| **setuid** | `4xxx` | Se ejecuta con los permisos del **propietario** (no del que lo lanza). Ej: `passwd`, `sudo`. | Sin efecto relevante |
| **setgid** | `2xxx` | Se ejecuta con el grupo del archivo | Nuevos archivos heredan el **grupo del directorio** (útil en carpetas compartidas) |
| **sticky bit** | `1xxx` | Obsoleto en archivos | Solo el propietario del archivo (o root) puede **borrar** archivos dentro. Ej: `/tmp` |

```bash
chmod u+s ejecutable      # activar setuid
chmod g+s directorio/     # activar setgid en directorio
chmod +t /tmp             # activar sticky bit
chmod 1755 /tmp           # sticky + rwxr-xr-x en octal
```

```bash
# Encontrar archivos con setuid (auditoría de seguridad):
find /usr/bin -perm -4000 -ls
```

---

## 7. Comandos de inspección (solo lectura)

```bash
ls -l archivo              # permisos, propietario, grupo, tamaño, fecha
ls -la directorio/         # incluye archivos ocultos
stat archivo               # todo sobre el inodo: permisos, timestamps, inodo nº
id                         # quién soy yo: uid, gid, grupos
groups                     # grupos a los que pertenezco
getfacl archivo            # ACLs extendidas (si el sistema las usa)
namei -l /ruta/completa    # permisos de cada componente de la ruta
```

---

## 8. Gotchas frecuentes

- **Borrar un archivo sin permiso `w` en el directorio padre**: el permiso de borrado lo controla el directorio, no el archivo. Puedes borrar un archivo de solo lectura si tienes `w` en su directorio.
- **`chmod -R 777 .`**: nunca en producción. Abre vulnerabilidades de escalada de privilegios.
- **`chown` vs `chmod`**: `chown` cambia a quién aplican los permisos; `chmod` cambia qué están permitidos.
- **Enlace simbólico roto**: `ls -la` lo muestra en rojo; `readlink enlace` muestra a qué apunta.
- **Permisos en `/tmp`**: el sticky bit evita que usuarios borrén archivos ajenos aunque tengan `w` en el directorio.
- **Directorio sin `x`**: aunque `r` te permita listar nombres, sin `x` no puedes acceder a ningún archivo dentro (ni leer, ni abrir).

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|índice]]
- [[filesystem-fhs-y-navegacion]]
- [[usuarios-grupos-y-sudo]]
