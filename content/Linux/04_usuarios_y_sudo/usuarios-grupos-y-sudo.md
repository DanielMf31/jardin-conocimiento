---
title: Usuarios, grupos y sudo en Linux
date: 2026-06-12
tags: [programacion/linux, programacion/linux/administracion, programacion/linux/seguridad]
type: nota
status: permanente
source: claude-code
aliases: [usuarios linux, grupos linux, sudo, permisos de usuario, multiusuario linux]
---

# Usuarios, grupos y sudo en Linux

## Modelo mental

Linux es un sistema **multiusuario por diseño**: desde los 70, varios usuarios podían conectarse al mismo hardware simultáneamente. Hoy, aunque seas el único humano en tu máquina, el modelo persiste y es la base de toda la seguridad del sistema.

**Regla de oro**: cada proceso corre con la identidad de un usuario. Los permisos de archivos, sockets y dispositivos se comprueban contra esa identidad. No hay excepciones.

---

## root — UID 0

`root` es el superusuario. Su UID (User ID) es **0** y el kernel lo trata de forma especial: salta casi todas las comprobaciones de permisos.

### Por qué NO trabajar como root

| Riesgo | Consecuencia |
|--------|-------------|
| `rm -rf /` sin querer | Borra el sistema completo, sin confirmación |
| Malware ejecutado como root | Control total de la máquina |
| Error en script | Puede dañar cualquier archivo del sistema |
| Sin trazabilidad | Los logs solo muestran "root hizo X", no quién |

**Ubuntu deshabilita la contraseña de root por defecto.** No puedes hacer `su -` directo. En su lugar, uses `sudo`, que añade trazabilidad y te pide TU contraseña.

---

## Tipos de usuarios

### Usuario normal
- UID >= 1000 (convención moderna)
- Tiene directorio home en `/home/<usuario>/`
- Shell interactiva (`/bin/bash`, `/bin/zsh`, etc.)
- Ejemplo: `daniel` (UID 1000 si es el primer usuario creado)

### Usuario de sistema
- UID entre 1 y 999
- Sin directorio home (o uno no estándar como `/var/lib/postgresql/`)
- Shell no interactiva (`/usr/sbin/nologin` o `/bin/false`)
- Corre servicios: `www-data`, `postgres`, `systemd-network`, `docker`
- **No son cuentas para personas.** Son sandboxes de aislamiento para procesos.

```bash
# Ver todos los usuarios con shell real
grep -v nologin /etc/passwd | grep -v false
```

---

## Ver tu propia identidad

```bash
whoami          # Solo el nombre: daniel
id              # uid=1000(daniel) gid=1000(daniel) groups=1000(daniel),4(adm),27(sudo),1001(docker)
groups          # Lista solo los grupos: daniel adm sudo docker
id <usuario>    # Ver identidad de otro usuario (sin necesidad de sudo)
```

La salida de `id` tiene tres partes:
- `uid` — quién eres tú
- `gid` — tu grupo principal (el que aparece en los archivos que creas)
- `groups` — todos los grupos a los que perteneces (determinan acceso adicional)

---

## Dónde vive la informacion de usuarios

> Leer estas rutas es formativo. **Nunca editarlas a mano**: usa `adduser`, `usermod`, `passwd`.

### `/etc/passwd` — directorio de usuarios

```
daniel:x:1000:1000:Daniel,,,:/home/daniel:/bin/bash
```

Campos separados por `:`:
1. Nombre de usuario
2. `x` — contraseña en `/etc/shadow` (fue literal aquí hasta los 90)
3. UID
4. GID principal
5. GECOS (nombre completo, info de contacto — ignorado en la práctica)
6. Directorio home
7. Shell de login

### `/etc/group` — directorio de grupos

```
sudo:x:27:daniel,otrouser
docker:x:999:daniel
```

Campos: nombre, contraseña (obsoleta), GID, lista de miembros. El GID principal de cada usuario está en `/etc/passwd`, no aquí.

### `/etc/shadow` — contraseñas hasheadas

```
daniel:$6$rounds=...:19500:0:99999:7:::
```

- Solo legible por root
- Hash SHA-512 (`$6$`) con sal aleatoria
- Campos de política de expiración de contraseña
- Nunca necesitas leerlo directamente; `passwd` lo gestiona

```bash
# Leer passwd y group (acceso normal)
cat /etc/passwd
cat /etc/group

# Shadow requiere sudo
sudo cat /etc/shadow
```

---

## sudo a fondo

### Qué hace sudo exactamente

`sudo` ("superuser do") es un programa que:
1. Comprueba si el usuario actual tiene permiso para ejecutar el comando solicitado (según `/etc/sudoers`)
2. Te autentica pidiendo **tu propia contraseña** (no la de root)
3. Ejecuta el comando como el usuario objetivo (root por defecto)
4. Registra la acción en el syslog: `AUTH LOG: daniel : TTY=pts/0 ; CMD=/usr/bin/apt update`

**Por qué tu contraseña y no la de root**: root no tiene contraseña en Ubuntu. Pero también es mejor práctica: si un atacante ya tiene tu sesión abierta, no obtiene la contraseña de root con un keylogger.

### Timeout de sudo

Después de autenticarte, sudo "recuerda" que eres tú durante **15 minutos** (configurable). En ese ventana no vuelve a pedir contraseña.

```bash
sudo -k          # Invalidar el timestamp ahora mismo
sudo -v          # Renovar el timestamp sin ejecutar nada
```

### `/etc/sudoers` y `sudoers.d/`

```bash
sudo visudo      # SIEMPRE editar con visudo, nunca con un editor directo
                 # visudo valida la sintaxis antes de guardar
```

Formato de una regla:

```
# usuario  HOSTS=(como_quien)  COMANDOS
daniel     ALL=(ALL:ALL)       ALL
%sudo      ALL=(ALL:ALL)       ALL    # % = grupo
```

- `ALL=(ALL:ALL) ALL` — desde cualquier host, como cualquier usuario:grupo, cualquier comando
- El grupo `sudo` tiene esta regla en Ubuntu por defecto

Archivos en `/etc/sudoers.d/` se incluyen automáticamente. Úsalos para reglas de paquetes o usuarios específicos sin tocar el archivo principal.

```bash
# Ejemplo: permitir a daniel reiniciar nginx sin contraseña
# En /etc/sudoers.d/nginx-restart:
daniel ALL=(root) NOPASSWD: /usr/bin/systemctl restart nginx
```

### `sudo comando` vs `sudo -i` vs `sudo su`

| Forma | Qué hace | Cuándo usarla |
|-------|----------|---------------|
| `sudo <cmd>` | Ejecuta un comando como root, en tu shell actual | La forma normal; preferida |
| `sudo -i` | Shell de login de root (carga su `.profile`, cambia `HOME`) | Mantenimiento prolongado como root |
| `sudo -s` | Shell de root sin cargar su perfil (`HOME` sigue siendo el tuyo) | Menos habitual |
| `sudo su -` | Llama a `su` con privilegios sudo; equivale a `sudo -i` | Evitar; redundante |
| `su <usuario>` | Cambia a ese usuario (pide su contraseña) | Cambiar a otro usuario normal |

**Gotcha**: `sudo -i` cambia el `PATH` y el directorio de trabajo a los de root. Scripts que asumen el entorno del usuario pueden comportarse diferente.

### sudo vs su

- `su` pide la contraseña del usuario **objetivo**. En Ubuntu, root no tiene contraseña, así que `su -` falla por defecto.
- `sudo` pide la contraseña del usuario **actual** y comprueba permisos en sudoers.
- Prefiere siempre `sudo` para trazabilidad y por diseño del sistema Ubuntu.

---

## Gestionar usuarios

### Crear usuarios

```bash
# adduser — wrapper interactivo, crea home, pide contraseña (recomendado)
sudo adduser daniel

# useradd — comando de bajo nivel, requiere opciones manuales
sudo useradd -m -s /bin/bash -U daniel    # -m: crea home, -s: shell, -U: crea grupo propio
sudo passwd daniel                         # Establecer contraseña por separado
```

**Diferencia clave**: `adduser` es un script Perl/Python que llama a `useradd` internamente y hace lo que la mayoría quiere por defecto. En scripts automatizados o sistemas no-Debian, `useradd` es más portable.

### Añadir a un grupo — `usermod -aG`

```bash
sudo usermod -aG docker daniel     # Añadir al grupo docker
sudo usermod -aG sudo,video daniel # Múltiples grupos a la vez
```

**Gotcha crítico**: los cambios de grupo no afectan a las sesiones ya abiertas. Debes **cerrar sesión y volver a entrar** (o usar `newgrp docker` para esa terminal) para que el nuevo grupo surta efecto. `id` mostrará el cambio solo en la nueva sesión.

### Cambiar contraseña

```bash
passwd            # Cambiar TU contraseña
sudo passwd daniel  # Cambiar la de otro usuario (root)
sudo passwd -l daniel  # Bloquear cuenta (lock)
sudo passwd -u daniel  # Desbloquear
```

### Eliminar usuarios

```bash
sudo deluser daniel              # Elimina el usuario, conserva /home/daniel
sudo deluser --remove-home daniel  # También borra el home
sudo deluser daniel docker        # Solo quitar del grupo docker (sin borrar usuario)
```

### Modificar usuario existente

```bash
sudo usermod -s /bin/zsh daniel     # Cambiar shell
sudo usermod -d /nuevo/home daniel  # Cambiar directorio home
sudo usermod -l nuevo_nombre daniel # Renombrar (no mueve el home)
sudo chfn daniel                    # Editar campos GECOS interactivamente
```

---

## El grupo `sudo` en Ubuntu

En Ubuntu, **pertenecer al grupo `sudo` es lo que te da acceso a sudo**, gracias a esta línea en `/etc/sudoers`:

```
%sudo   ALL=(ALL:ALL) ALL
```

El primer usuario creado durante la instalación se añade automáticamente. Los siguientes usuarios creados con `adduser` no se añaden solos; debes hacerlo manualmente:

```bash
sudo usermod -aG sudo nuevo_usuario
```

En Fedora/Red Hat el grupo equivalente se llama `wheel`. En Arch es configurable.

---

## Grupos importantes en escritorio Ubuntu / Hyprland

| Grupo | Propósito | Necesitas estar si... |
|-------|-----------|----------------------|
| `sudo` | Acceso a sudo | Siempre (usuario principal) |
| `adm` | Leer logs de sistema (`/var/log/`) | Quieres leer syslog sin sudo |
| `video` | Acceso a `/dev/video*` y aceleración GPU | Webcam, captura, OpenGL/Vulkan directo |
| `input` | Acceso a `/dev/input/*` (teclado, ratón, gamepad) | Hyprland/Wayland sin X11, herramientas de gamepad |
| `audio` | Acceso a dispositivos ALSA (`/dev/snd/`) | ALSA directo (PipeWire/PulseAudio no lo necesitan) |
| `plugdev` | Montar dispositivos removibles sin sudo | Pendrives, cámaras en distros antiguas |
| `docker` | Usar Docker sin sudo | Desarrollo con Docker (equivale a root de facto — cuidado) |
| `kvm` | Acceso a `/dev/kvm` | Virtualización con QEMU/libvirt |
| `dialout` | Puertos serie (`/dev/ttyUSB*`, `/dev/ttyACM*`) | Microcontroladores (Arduino, ESP32, PlatformIO) |

**Advertencia `docker`**: añadir un usuario al grupo `docker` le permite montar cualquier directorio del host con permisos de root dentro del contenedor. Trátalo con la misma seriedad que sudo.

---

## Gotchas frecuentes

```bash
# Gotcha 1: sudo env no hereda tu PATH
sudo which python3          # Puede dar un python diferente al tuyo
sudo env PATH="$PATH" cmd   # Pasar tu PATH explicitamente

# Gotcha 2: sudo con redirección — esto FALLA
sudo echo "texto" > /etc/archivo   # El > lo ejecuta tu shell, no root
# Solución:
echo "texto" | sudo tee /etc/archivo
echo "texto" | sudo tee -a /etc/archivo  # Append

# Gotcha 3: grupos nuevos solo en nueva sesión
sudo usermod -aG docker $USER
# Ahora mismo: docker no está en `id`
newgrp docker   # Abre sub-shell con docker activo, solo para esa terminal
# O simplemente: logout y login

# Gotcha 4: adduser vs useradd en scripts
# useradd no crea home por defecto → añade -m siempre en scripts
```

---

## Buenas practicas de seguridad

1. **Trabaja siempre como usuario normal.** Eleva solo cuando es necesario y por el menor tiempo posible.
2. **No uses `NOPASSWD` para comandos amplios** en sudoers. Restríngelo al comando exacto si debes.
3. **Audita periodicamente los miembros de `sudo` y `docker`**: `getent group sudo docker`
4. **No compartas cuentas.** Un usuario por persona, incluso en servidores personales. Los logs solo tienen valor si la identidad es única.
5. **Contraseña robusta en tu usuario**: es la única barrera antes de sudo.
6. **Cuentas de servicio sin shell interactiva**: si creas un usuario para un script/daemon, usa `/usr/sbin/nologin` como shell.
7. **`visudo` siempre**: un sudoers con error de sintaxis puede dejarte sin acceso al sistema.

---

## Referencia rapida de comandos

```bash
# Identidad
whoami                      # Nombre usuario actual
id                          # uid, gid, grupos
groups                      # Solo nombres de grupos
id <usuario>                # Identidad de otro usuario

# Archivos del sistema
cat /etc/passwd             # Lista de usuarios
cat /etc/group              # Lista de grupos
sudo cat /etc/shadow        # Hashes de contraseñas (solo root)
getent passwd <usuario>     # Consultar usuario (funciona con LDAP también)
getent group <grupo>        # Consultar grupo

# Gestión de usuarios
sudo adduser <nombre>                  # Crear usuario interactivo
sudo deluser <nombre>                  # Eliminar usuario
sudo deluser --remove-home <nombre>    # Eliminar con home
sudo usermod -aG <grupo> <usuario>     # Añadir a grupo
sudo usermod -s /bin/zsh <usuario>     # Cambiar shell
passwd                                 # Cambiar propia contraseña
sudo passwd <usuario>                  # Cambiar contraseña de otro

# sudo
sudo <comando>              # Ejecutar como root
sudo -u <usuario> <cmd>     # Ejecutar como otro usuario
sudo -i                     # Shell interactiva de root
sudo -k                     # Invalidar timestamp (pedir contraseña de nuevo)
sudo visudo                 # Editar sudoers de forma segura
```

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|indice Linux]]
- [[gestion-de-archivos-y-permisos]]
- [[procesos-servicios-y-systemd]]
