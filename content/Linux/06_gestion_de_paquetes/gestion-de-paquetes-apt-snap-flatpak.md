---
title: Gestión de paquetes en Linux (apt, dpkg, snap, flatpak)
date: 2026-06-12
tags: [programacion/linux, programacion/linux/paquetes, programacion/devops]
type: nota
status: permanente
source: claude-code
aliases: [apt, dpkg, snap, flatpak, package manager linux, gestor paquetes linux]
---

# Gestión de paquetes en Linux (apt, dpkg, snap, flatpak)

## Idea central

Un **gestor de paquetes** es la capa de software que resuelve, descarga, instala y actualiza programas y sus dependencias de forma atómica y reproducible — el equivalente a una tienda de aplicaciones con versionado, firmas criptográficas y rollback.

## ¿Por qué no simplemente descargar un .exe como en Windows?

| Windows (clásico) | Linux con gestor |
|---|---|
| Descargas el binario del sitio del fabricante | El paquete viene de repositorios auditados |
| Dependencias incluidas dentro del instalador | Dependencias compartidas entre paquetes (ahorro de espacio y parches centralizados) |
| Actualizar = volver a descargar cada app | `apt upgrade` actualiza TODO el sistema de una vez |
| Desinstalar deja basura en el registro | `apt purge` elimina programa + configuración |
| Sin firma verificada por defecto | Cada repositorio tiene clave GPG; apt la verifica |

**Dependencia**: si `app-X` necesita `libfoo 2.x`, el gestor instala `libfoo` automáticamente antes. Si otra app ya la usa, la comparte. Esto es la *resolución de dependencias*.

---

## Arquitectura: repositorios

Un **repositorio** (repo) es un servidor HTTP que publica paquetes con índices firmados.

```
┌──────────────────────┐
│  Repo Ubuntu (main)  │  ← Mantenido por Canonical
│  Repo Ubuntu (universe)│ ← Mantenido por la comunidad
│  PPA de terceros     │  ← Añadidos manualmente
└──────────────┬───────┘
               │ HTTPS + firma GPG
        ┌──────▼──────┐
        │  APT (alto nivel) │  ← Resuelve dependencias
        │  dpkg (bajo nivel)│  ← Instala el .deb en disco
        └─────────────┘
```

### Configuración de repos en Ubuntu 24.04 (formato deb822)

Ubuntu 24.04 usa el nuevo formato **deb822** (`.sources`) en lugar del antiguo `sources.list`.

Archivo principal: `/etc/apt/sources.list.d/ubuntu.sources`

```
# Ver el contenido (read-only):
cat /etc/apt/sources.list.d/ubuntu.sources
```

Fragmento típico:

```yaml
Types: deb deb-src
URIs: http://es.archive.ubuntu.com/ubuntu/
Suites: noble noble-updates noble-backports
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
```

| Campo | Significado |
|---|---|
| `Types: deb` | Paquetes binarios (lo que instalas) |
| `Types: deb-src` | Código fuente (para compilar o auditar) |
| `Suites` | Versión de Ubuntu + canales de actualización |
| `Components` | `main` (libre, soporte Canonical), `universe` (libre, comunidad), `restricted` (drivers privativos), `multiverse` (no libre) |

### Añadir un PPA (Personal Package Archive)

```bash
# Añade el repo y su clave GPG automáticamente
sudo add-apt-repository ppa:nombre/repo

# Después actualizar índices:
sudo apt update
```

Los PPAs guardan su clave en `/etc/apt/keyrings/` y su definición en `/etc/apt/sources.list.d/`.

---

## APT a fondo

APT (*Advanced Package Tool*) es la interfaz de alto nivel. Opera sobre la base de datos de índices descargada con `apt update`.

### Comandos esenciales

```bash
# --- ÍNDICES Y ACTUALIZACIÓN ---
apt update               # Descarga índices frescos de todos los repos (no instala nada)
apt upgrade              # Actualiza paquetes instalados; NO elimina ni añade nuevos
apt full-upgrade         # Como upgrade pero puede quitar paquetes si es necesario

# --- INSTALACIÓN Y ELIMINACIÓN ---
apt install <paquete>    # Instala + dependencias
apt remove <paquete>     # Elimina binario, deja ficheros de configuración
apt purge <paquete>      # Elimina binario + configuración (limpio)
apt autoremove           # Elimina dependencias huérfanas (ya no requeridas por nadie)

# --- BÚSQUEDA E INFORMACIÓN (read-only) ---
apt search <palabra>     # Busca en nombres y descripciones
apt show <paquete>       # Muestra versión, dependencias, descripción
apt list --installed     # Lista todos los paquetes instalados
apt list --upgradable    # Muestra los que tienen actualización disponible
```

### `update` vs `upgrade` vs `full-upgrade` — diferencias clave

| Comando | Qué hace | ¿Elimina paquetes? |
|---|---|---|
| `apt update` | Solo actualiza la lista de versiones disponibles | No |
| `apt upgrade` | Instala versiones nuevas de lo ya instalado | No |
| `apt full-upgrade` | Como upgrade + resuelve conflictos agresivamente | Sí (si es necesario) |

**Gotcha**: ejecutar `apt upgrade` sin `apt update` previo usa índices desactualizados. Siempre: `update` → `upgrade`.

---

## dpkg — el nivel bajo

`dpkg` instala ficheros `.deb` directamente en el sistema de archivos. APT lo usa por debajo; tú lo usas cuando recibes un `.deb` descargado a mano.

```bash
# --- INSTALACIÓN DE .deb DESCARGADO (requiere sudo) ---
sudo dpkg -i fichero.deb          # Instala el .deb
sudo apt install -f               # Repara dependencias rotas si dpkg las dejó pendientes

# --- CONSULTA (read-only, sin sudo) ---
dpkg -l                           # Lista todos los paquetes instalados (estado + versión)
dpkg -l "nombre*"                 # Filtra por patrón glob
dpkg -L <paquete>                 # Lista TODOS los ficheros que instaló ese paquete
dpkg --configure -a               # Termina configuraciones interrumpidas (sudo)
```

### Leer la salida de `dpkg -l`

```
ii  curl   7.88.1  amd64  command line tool for transferring data
^^  ←── estado
|
ii = instalado y ok
rc = eliminado pero configuración aún existe (candidato a purge)
un = no instalado
```

### Relación APT ↔ dpkg

```
apt install curl
    │
    ├─ resuelve dependencias
    ├─ descarga .deb al caché (/var/cache/apt/archives/)
    └─ llama a dpkg -i internamente
```

APT es el "project manager"; dpkg es el "obrero". Puedes hablar directamente al obrero (dpkg), pero pierde la resolución de dependencias.

---

## SNAP

**Snap** es el formato de paquetes de Canonical. El binario + todas sus dependencias van dentro de un único fichero comprimido (`.snap`), montado como sistema de archivos de solo lectura.

```bash
# Read-only
snap list                          # Paquetes snap instalados
snap find <nombre>                 # Busca en la Snap Store
snap info <paquete>                # Versión, canales disponibles, tamaño

# Con privilegios
sudo snap install <paquete>        # Instala
sudo snap remove <paquete>        # Elimina
sudo snap refresh                  # Actualiza todos los snaps
```

### Confinamiento (confinement)

| Nivel | Significado |
|---|---|
| `strict` | Aislado del sistema; accede solo a lo permitido por interfaces declaradas |
| `classic` | Acceso casi total al sistema (como apt); requiere aprobación en la tienda |
| `devmode` | Sin restricciones; solo para desarrollo |

```bash
snap info firefox | grep confinement   # Ver nivel de confinamiento
```

**Gotcha**: los snaps montan en `/snap/` y se autoactualiz­an en segundo plano. Esto puede romper apps en producción si no se fija un canal/versión.

---

## FLATPAK

**Flatpak** es el estándar de la comunidad (freedesktop.org), independiente de la distro. Funciona igual que snap conceptualmente (app + runtime aislado), pero su arquitectura es más abierta.

**Flathub** es el repositorio principal: `https://flathub.org`

```bash
# Configuración (una vez, read-only para verificar):
flatpak remotes                    # Lista repositorios flatpak configurados

# Read-only
flatpak list                       # Apps flatpak instaladas
flatpak search <nombre>            # Busca en los remotes configurados
flatpak info <app-id>              # Detalles de una app instalada

# Con privilegios
flatpak install flathub <app-id>   # Instala desde Flathub
flatpak uninstall <app-id>         # Elimina
flatpak update                     # Actualiza todos los flatpaks
```

---

## ¿Cuándo usar cada formato?

| Situación | Formato recomendado |
|---|---|
| Software del sistema, librerías, herramientas CLI | **apt** siempre |
| App de escritorio que no está en repos oficiales | **Flatpak** (mejor sandboxing, más neutral) |
| App de Canonical (Ubuntu Make, etc.) o si solo existe en Snap Store | **snap** |
| Recibes un `.deb` de un proveedor (VS Code, Chrome…) | **dpkg -i** + agregar su repo para futuras actualizaciones |
| Necesitas versión muy reciente de una app | PPA o Flatpak |

**Regla práctica**: apt > flatpak > snap para apps de escritorio. Para herramientas de sistema, apt siempre.

### Diferencias estructurales clave

| | apt/dpkg | snap | flatpak |
|---|---|---|---|
| Dependencias compartidas | Sí (entre paquetes) | No (bundleadas) | Parcial (runtimes compartidos) |
| Actualizaciones | Manual (`apt upgrade`) | Automáticas | Manual (`flatpak update`) |
| Sandboxing | No | Sí (strict/classic) | Sí (portals) |
| Espacio en disco | Eficiente | Mayor (bundle) | Mayor (bundle) |
| Fuente | Repos Ubuntu + PPAs | Snap Store (Canonical) | Flathub + otros remotes |

---

## Mantener el sistema al día y limpio

```bash
# Rutina de actualización completa
sudo apt update && sudo apt full-upgrade

# Limpiar caché de paquetes descargados
sudo apt clean          # Borra todo /var/cache/apt/archives/
sudo apt autoclean      # Borra solo versiones obsoletas del caché

# Eliminar dependencias huérfanas
sudo apt autoremove

# Buscar paquetes en estado "rc" (eliminados pero con configs)
dpkg -l | grep "^rc"
# Purgar todos de una vez:
dpkg -l | grep "^rc" | awk '{print $2}' | sudo xargs dpkg --purge
```

---

## Gotchas y errores frecuentes

| Error | Causa | Solución |
|---|---|---|
| `E: Could not get lock /var/lib/dpkg/lock` | Otra instancia de apt corriendo (o crash previo) | Esperar; si está muerto: `sudo rm /var/lib/dpkg/lock*` |
| `dpkg: dependency problems` tras `dpkg -i` | dpkg no resuelve deps | `sudo apt install -f` |
| `NO_PUBKEY XXXXXXXX` al hacer `apt update` | Clave GPG del repo no importada | `sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys <KEY>` o re-añadir el repo |
| Snap no abre archivos del home | Confinamiento strict bloquea acceso | Revisar permisos: `snap connections <paquete>` |
| `apt upgrade` no actualiza un paquete | Paquete "held" o hay conflicto | `apt-mark showhold`; usar `full-upgrade` si es seguro |

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|índice]]
- [[procesos-servicios-y-systemd]]
