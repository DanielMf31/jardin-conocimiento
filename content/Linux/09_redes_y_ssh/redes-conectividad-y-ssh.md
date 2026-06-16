---
title: Redes, Conectividad y SSH en Linux
date: 2026-06-12
tags: [programacion/linux, programacion/redes, programacion/ssh]
type: nota
status: permanente
source: claude-code
aliases: [redes linux, ssh linux, conectividad linux, ip route, ssh-keygen]
---

# Redes, Conectividad y SSH en Linux

## Modelo mental mínimo

Antes de tocar ningún comando, necesitas tener claro el vocabulario. La red no es magia negra, tiene exactamente 4 piezas que resolver cada vez que algo falla.

| Concepto | Qué es | Ejemplo |
|---|---|---|
| **Dirección IP** | Identificador único de tu máquina en la red | `192.168.1.42` |
| **Máscara de subred** | Define qué IPs son "vecinas directas" tuyas | `/24` = `255.255.255.0` (256 hosts) |
| **Gateway (puerta de enlace)** | El router al que mandas todo lo que no es local | `192.168.1.1` |
| **DNS** | Traduce nombres (`google.com`) a IPs (`142.250.x.x`) | `8.8.8.8` (Google), `1.1.1.1` (Cloudflare) |

**Flujo de una petición**: tu app → SO → ¿es IP local? → si no: gateway → internet → servidor destino.

**Puerto**: número de 0–65535 que identifica *qué servicio* dentro de una IP. `192.168.1.42:22` = SSH en esa máquina. `192.168.1.42:80` = HTTP.

**TCP vs UDP**: TCP garantiza entrega y orden (web, SSH, correo). UDP no garantiza nada pero es más rápido (DNS, streaming, juegos). En diagnóstico casi siempre te importa TCP.

---

## Ver tu configuración

### Interfaces y direcciones IP

```bash
ip a                    # alias de ip addr show — lista todas las interfaces
ip addr show eth0       # solo la interfaz eth0

# Salida típica:
# 2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
#     inet 192.168.1.42/24 brd 192.168.1.255 scope global eth0
#     inet6 fe80::...
```

En Ubuntu moderno las interfaces ya no se llaman `eth0` sino `enp3s0`, `ens33`, `wlp2s0` (wifi), etc. No te asustes, es solo nomenclatura.

```bash
hostname -I             # solo las IPs, sin ruido — útil en scripts
```

### Tabla de rutas (dónde va cada paquete)

```bash
ip route
ip route show

# Salida típica:
# default via 192.168.1.1 dev eth0        ← tu gateway
# 192.168.1.0/24 dev eth0 proto kernel    ← tu red local
```

La línea `default via X.X.X.X` es tu gateway. Si no aparece, no tienes salida a internet.

### DNS configurado

```bash
cat /etc/resolv.conf
# nameserver 127.0.0.53      ← systemd-resolved (Ubuntu moderno)
# options edns0 trust-ad

resolvectl status           # ver DNS por interfaz (Ubuntu 20.04+)
```

En Ubuntu 20.04+ el DNS pasa por `systemd-resolved` (escucha en `127.0.0.53`). El archivo `/etc/resolv.conf` es un symlink; el DNS real se configura en otro sitio, pero para *ver* qué DNS usa cada interfaz: `resolvectl status`.

---

## Diagnosticar conectividad: el protocolo de 4 preguntas

Cuando "no hay internet", sigue este orden. Cada paso aisla una capa diferente.

### 1. ¿Llego al gateway? (red local)

```bash
ping -c 4 192.168.1.1      # reemplaza con tu gateway real
```

Si falla: problema de cable/wifi, IP mal asignada, o la interfaz está caída (`ip link show`).

### 2. ¿Llego a internet? (routing)

```bash
ping -c 4 8.8.8.8          # Google DNS por IP — sin DNS de por medio
```

Si falla pero el gateway responde: problema de routing en el router o ISP.

### 3. ¿Funciona el DNS? (resolución de nombres)

```bash
ping -c 4 google.com       # usa DNS
dig google.com             # resolución detallada
nslookup google.com        # alternativa más antigua

# Con dig, lo que importa es la sección ANSWER:
# google.com.    300  IN  A  142.250.185.14
```

Si `ping 8.8.8.8` funciona pero `ping google.com` falla: **es el DNS**. No hay problema de red, hay problema de resolución de nombres.

### 4. ¿Llega a un host/puerto específico? (routing fino + firewall)

```bash
traceroute google.com       # muestra cada salto hasta el destino
tracepath google.com        # similar, sin necesitar root, menos info

# Ver si un puerto está alcanzable:
nc -zv 192.168.1.10 22      # intenta conectar a SSH en esa IP
# o:
curl -v telnet://192.168.1.10:22
```

`traceroute` te dice dónde se rompe el camino: si los primeros saltos responden pero luego hay `* * *`, es firewall del destino o del ISP bloqueando ICMP.

---

## Puertos y sockets abiertos en tu máquina

`ss` es el sucesor moderno de `netstat`. Muestra qué procesos están escuchando o conectados.

```bash
ss -tulpn
# -t  TCP
# -u  UDP
# -l  solo LISTENING (escuchando)
# -p  muestra el proceso (PID y nombre)
# -n  no resolver nombres (más rápido, sin ambigüedades)

# Salida ejemplo:
# Netid  State   Recv-Q  Send-Q  Local Address:Port   Peer Address:Port  Process
# tcp    LISTEN  0       128     0.0.0.0:22            0.0.0.0:*          users:(("sshd",pid=1234,...))
# tcp    LISTEN  0       128     127.0.0.1:27017       0.0.0.0:*          users:(("mongod",pid=...))
```

`0.0.0.0:22` = escucha en **todas** las interfaces. `127.0.0.1:27017` = escucha **solo en localhost** (no accesible desde fuera).

```bash
ss -tulpn | grep :80        # filtrar por puerto específico
ss -tp                      # conexiones TCP activas con proceso
```

---

## Descargar ficheros: curl y wget

### curl — la navaja suiza

```bash
curl https://example.com                    # ver el HTML en stdout
curl -o archivo.html https://example.com   # guardar con nombre propio
curl -O https://example.com/file.tar.gz    # guardar con el nombre del servidor
curl -L https://bit.ly/algo               # seguir redirecciones (302, 301)
curl -I https://example.com               # solo cabeceras HTTP (HEAD request)
curl -s https://api.example.com/json | python3 -m json.tool   # silencioso + pretty JSON
curl --progress-bar -O https://...        # barra de progreso

# Autenticación básica:
curl -u usuario:contraseña https://api.privada.com/endpoint

# POST con JSON:
curl -X POST -H "Content-Type: application/json" \
     -d '{"key": "value"}' https://api.example.com/endpoint
```

### wget — descarga recursiva y robusta

```bash
wget https://example.com/file.tar.gz          # descarga directa
wget -c https://example.com/grande.iso        # continuar descarga interrumpida (-c = continue)
wget -q https://...                           # silencioso (quiet)
wget -r -np https://example.com/docs/         # recursivo, sin subir al padre
```

**Cuándo usar cada uno**: `curl` para APIs, peticiones HTTP elaboradas, ver cabeceras. `wget` para descargas grandes que pueden interrumpirse, o descargas recursivas de sitios estáticos.

---

## SSH a fondo

SSH (Secure Shell) es un protocolo de acceso remoto cifrado. Te da una terminal en otra máquina como si estuvieras sentado delante de ella.

### Conexión básica

```bash
ssh usuario@192.168.1.10
ssh usuario@servidor.dominio.com
ssh -p 2222 usuario@host     # si el servidor no usa el puerto 22 estándar
```

La primera vez te pregunta si confías en la clave del servidor (fingerprint). Escribe `yes`. Esa clave se guarda en `~/.ssh/known_hosts`. Si cambia (reinstalación del servidor), te avisará — es una medida de seguridad real, no un estorbo.

### Autenticación por clave (mejor que contraseña)

**Por qué claves**: una contraseña puede adivinarse por fuerza bruta. Una clave SSH es matemáticamente inviable de romper. Además, no tienes que escribirla cada vez (el agente SSH la recuerda).

#### Generar el par de claves

```bash
ssh-keygen -t ed25519 -C "mi-comentario-descriptivo"
# -t ed25519   algoritmo moderno y seguro (preferir sobre RSA)
# -C           comentario para identificar la clave (aparece al final de la clave pública)

# Genera dos archivos:
# ~/.ssh/id_ed25519      ← CLAVE PRIVADA — nunca la compartas, nunca la saques de tu máquina
# ~/.ssh/id_ed25519.pub  ← clave pública — esta sí se copia al servidor
```

La **passphrase** es opcional pero recomendada: cifra la clave privada en disco. El agente SSH la pide una vez por sesión.

#### Copiar la clave pública al servidor

```bash
ssh-copy-id usuario@servidor          # método automático — el más cómodo
# equivale a hacer:
cat ~/.ssh/id_ed25519.pub | ssh usuario@servidor "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

Después de `ssh-copy-id`, podrás entrar sin contraseña (o solo con la passphrase local, que el agente gestiona).

#### Agente SSH

```bash
eval "$(ssh-agent -s)"     # arrancar el agente (en la sesión actual)
ssh-add ~/.ssh/id_ed25519  # añadir clave al agente — pide passphrase una sola vez

ssh-add -l                 # ver claves cargadas en el agente
```

En Ubuntu con entorno gráfico el agente suele arrancar automáticamente y GNOME Keyring gestiona las claves. En servidores sin GUI, o en tmux/screen, puede que necesites lanzarlo a mano.

### Configuración de alias: ~/.ssh/config

En lugar de escribir `ssh usuario@192.168.1.10 -p 2222 -i ~/.ssh/clave_especial` cada vez, creas un alias en `~/.ssh/config`:

```
# ~/.ssh/config

Host dev
    HostName 192.168.1.10
    User ubuntu
    Port 2222
    IdentityFile ~/.ssh/id_ed25519

Host servidor-produccion
    HostName srv.miempresa.com
    User deploy
    IdentityFile ~/.ssh/id_ed25519_prod
    ForwardAgent yes          # propaga el agente SSH (útil para git en servidor remoto)

Host *
    ServerAliveInterval 60    # envía keepalive cada 60s para evitar desconexiones
    ServerAliveCountMax 3
```

```bash
chmod 600 ~/.ssh/config       # IMPORTANTE: debe tener permisos restrictivos
ssh dev                       # conecta con todos los parámetros del bloque "dev"
```

**Gotcha de permisos**: SSH es muy estricto. Si `~/.ssh/` o sus archivos tienen permisos demasiado abiertos, SSH se niega a funcionar. Regla rápida:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519       # clave privada
chmod 644 ~/.ssh/id_ed25519.pub   # clave pública
chmod 600 ~/.ssh/authorized_keys  # en el servidor
chmod 600 ~/.ssh/config
```

---

## Transferir ficheros

### scp — copia simple sobre SSH

```bash
# Local → remoto
scp archivo.txt usuario@servidor:/ruta/destino/

# Remoto → local
scp usuario@servidor:/ruta/archivo.txt ./local/

# Directorios (-r recursivo)
scp -r ./mi_proyecto/ usuario@servidor:/home/usuario/
```

`scp` es simple y funciona. Pero tiene un problema: no sabe qué ya existe en el destino, siempre copia todo.

### rsync — sincronización inteligente

rsync solo transfiere los **bloques que han cambiado**. Para proyectos grandes o backups, la diferencia es abismal.

```bash
rsync -avz --progress ./proyecto/ usuario@servidor:/destino/

# Flags esenciales:
# -a  archive: preserva permisos, timestamps, symlinks, recursivo
# -v  verbose: muestra qué se transfiere
# -z  comprime en tránsito (ahorra ancho de banda)
# --progress  barra de progreso por fichero

# Borrar en destino lo que ya no existe en origen (sincronización real):
rsync -avz --delete ./proyecto/ usuario@servidor:/destino/

# Dry-run: ver qué haría SIN ejecutar nada:
rsync -avz --dry-run --delete ./proyecto/ usuario@servidor:/destino/

# Local a local (sin SSH) — igualmente útil:
rsync -av /origen/ /destino/
```

**Gotcha del slash final**: `rsync src/ dst/` copia el *contenido* de `src` dentro de `dst`. `rsync src dst/` copia la *carpeta* `src` dentro de `dst` (crea `dst/src/`). El slash importa.

---

## Diagnóstico rápido: chuleta mental

```
¿Algo no conecta?

1. ip a                    → ¿tengo IP? ¿la interfaz está UP?
2. ip route                → ¿tengo gateway?
3. ping -c 4 <gateway>     → ¿llego al router?
4. ping -c 4 8.8.8.8       → ¿llego a internet (sin DNS)?
5. dig google.com          → ¿el DNS funciona?
6. ss -tulpn               → ¿el servicio destino está escuchando?
7. nc -zv <host> <puerto>  → ¿puedo llegar a ese puerto?
```

---

## Conexiones

- [[MOC_Linux]]
- [[Linux/00_README|índice]]
- [[procesos-servicios-y-systemd]]
