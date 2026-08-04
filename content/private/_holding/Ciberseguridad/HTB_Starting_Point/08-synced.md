---
title: Synced (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, rsync, linux, recon, misconfiguracion]
type: nota
status: en-progreso
source: claude-code
aliases: [HTB Synced, synced htb, rsync sin auth]
---

# Synced — HTB Starting Point (Tier 0)

**Tier 0 · SO: Linux · Dificultad: Very Easy · Skills: rsync, reconocimiento de servicios**

Synced expone un demonio `rsync` mal configurado con un modulo publico accesible sin autenticacion. Basta con enumerar los modulos disponibles y descargar la flag directamente. Es el caso canonico de servicio de sincronizacion expuesto en red sin ningun control de acceso.

> Hack The Box Starting Point es un laboratorio etico y autorizado. Todos los ejercicios se realizan en entornos controlados y dentro de los terminos de servicio de HTB.

---

## Objetivo

Obtener la flag alojada en el servidor Linux accediendo al servicio `rsync` sin credenciales.

---

## Acceso a la maquina (paso previo)

Antes de atacar nada necesitas conectarte a la red de HTB y arrancar la maquina para obtener su **IP**:

1. **Descarga tu VPN** desde el panel de HTB (Starting Point -> *Connect* -> descarga el `.ovpn`).
2. **Conectate a la VPN** y dejala corriendo en una terminal aparte:
   ```bash
   sudo openvpn starting_point_<tu_usuario>.ovpn
   ```
3. **Lanza la maquina** en la web (boton *Spawn Machine*). HTB te dara una **IP** (tipo `10.129.x.x`).
4. Comprueba que llegas a ella:
   ```bash
   ping -c2 <IP>
   ```
5. En el resto de este writeup, **sustituye `<IP>` por la IP que te toque** (es dinamica: cambia cada vez que lanzas la maquina).

> Alternativa sin VPN: el **Pwnbox** (Kali en el navegador que ofrece HTB) ya viene conectado a la red; solo lanzas la maquina y usas su IP directamente.

## Reconocimiento

**Categoria: escaneo de puertos y deteccion de servicios.**

Lanzar `nmap` contra la maquina para identificar que servicios estan expuestos:

```bash
nmap -sV -p- --min-rate 5000 <IP>
```

Flags relevantes:
- `-sV` — intenta identificar la version del servicio en cada puerto abierto.
- `-p-` — escanea los 65535 puertos (no solo los 1000 comunes por defecto).
- `--min-rate 5000` — acelera el escaneo; ajusta si la conexion VPN es inestable.

Salida esperada (fragmento):

```
PORT    STATE SERVICE VERSION
873/tcp open  rsync   (protocol version 31)
```

El puerto **873** es el puerto estandar del demonio `rsync`. No hay SSH abierto ni ninguna otra puerta de entrada: el unico vector es rsync.

---

## Enumeracion

**Categoria: listado de modulos rsync.**

`rsync` organiza los recursos compartidos en **modulos** (equivalente a los shares de SMB o los exports de NFS). Para listar los modulos disponibles sin autenticacion:

```bash
rsync --list-only rsync://<IP>/
```

Salida esperada:

```
public         	Anonymous Share
```

Hay un modulo llamado `public` accesible de forma anonima. Para ver su contenido:

```bash
rsync --list-only rsync://<IP>/public/
```

Salida esperada (puede variar ligeramente):

```
drwxr-xr-x          4,096 2021/xx/xx xx:xx:xx .
-rw-r--r--             33 2021/xx/xx xx:xx:xx flag.txt
```

El archivo `flag.txt` esta directamente en la raiz del modulo.

---

## Acceso inicial (foothold)

**Categoria: descarga de archivo via rsync anonimo.**

No hay explotacion de vulnerabilidad de memoria ni inyeccion de codigo: el servicio simplemente permite descargar archivos sin pedir credenciales.

```bash
rsync rsync://<IP>/public/flag.txt .
```

Esto descarga `flag.txt` al directorio actual de tu maquina atacante. Lee la flag:

```bash
cat flag.txt
```

La salida es la flag de la maquina.

> Si quisieras descargar todo el modulo de una vez: `rsync -av rsync://<IP>/public/ ./loot/`

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente desde el modulo rsync publico. No hay acceso shell al sistema ni usuario intermedio que escalar.

---

## Flags

| Flag | Ubicacion en el servidor | Como obtenerla |
|---|---|---|
| flag.txt | `/` del modulo `public` en rsync | `rsync rsync://<IP>/public/flag.txt .` |

Esta maquina tiene **una sola flag**. No hay separacion `user.txt` / `root.txt` porque no se obtiene shell: la flag se extrae directamente via rsync.

Valor: `<flag>` (sustituye por el valor real al ejecutar contra tu instancia en HTB).

---

## Patron y teoria

### El patron: servicio de sincronizacion expuesto sin autenticacion

`rsync` es una herramienta de sincronizacion de archivos entre maquinas. En modo demonio escucha en el puerto 873 y sirve **modulos**: rutas del sistema de archivos del servidor con una etiqueta y permisos configurables.

El patron de fallo es siempre el mismo:

1. El administrador instala `rsync` para backups internos o despliegues.
2. No configura autenticacion (`auth users` / `secrets file` en `rsyncd.conf`).
3. No restringe el acceso por IP (`hosts allow`).
4. El puerto queda expuesto a la red (o a internet).
5. Cualquiera puede listar y descargar (o incluso subir) archivos.

Este patron es analogo a:
- **FTP anonimo** — acceso sin credenciales al servidor de archivos.
- **SMB con shares sin contrasena** — shares accesibles por null session.
- **NFS con exports sin restriccion de host** — montaje libre desde cualquier IP.

La categoria general es **misconfiguracion de servicio de acceso a archivos**.

### Como se defiende / como lo disenar bien (purple team / dev)

**En `rsyncd.conf`**, cada modulo debe tener:

```ini
[public]
    path = /srv/rsync/public
    auth users = deploy_user
    secrets file = /etc/rsyncd.secrets
    hosts allow = 10.0.0.0/24
    read only = yes
```

Puntos clave:

| Control | Por que importa |
|---|---|
| `auth users` + `secrets file` | Exige usuario y contrasena para acceder al modulo |
| `hosts allow` | Restringe el acceso por IP/CIDR; bloquea acceso desde internet |
| `read only = yes` | Aunque el atacante se autentique, no puede escribir archivos |
| Firewall a nivel de red | El puerto 873 no deberia ser accesible desde redes no confiables |

**Como desarrollador**, si usas rsync en tu pipeline CI/CD o en backups:
- Nunca expongas el puerto 873 en el grupo de seguridad / firewall de tu servidor de produccion.
- Prefiere rsync sobre SSH (`rsync -e ssh ...`) en lugar del demonio rsync: hereda la autenticacion SSH y no requiere configurar `rsyncd.conf`.
- Si necesitas el demonio, usa autenticacion y `hosts allow` siempre.

**Como auditor / pentester**, rsync es un objetivo rapido en reconocimiento:
```bash
# Deteccion en nmap con scripts NSE
nmap -p 873 --script rsync-list-modules <IP>
```

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[03-seguridad-de-redes]] — puertos, servicios y exposicion de red
- [[06-seguridad-de-sistemas-y-hardening]] — misconfiguracion de servicios, principio de minimo privilegio
- [[07-pentesting-y-ciclo-del-ataque]] — fase de reconocimiento y enumeracion
- [[08-vulnerabilidades-y-explotacion]] — patron misconfiguracion vs vulnerabilidad de codigo
