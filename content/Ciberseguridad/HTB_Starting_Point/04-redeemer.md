---
title: Redeemer (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, redis, base-de-datos, misconfiguracion, tier-0, linux]
type: nota
status: en-progreso
source: claude-code
aliases: [Redeemer HTB, htb-redeemer, redis sin auth]
---

# Redeemer — HTB Starting Point (Tier 0)

**Tier 0 · SO: Linux · Dificultad: Very Easy · Skills: Redis CLI, reconocimiento de puertos no estandar**

Redeemer expone una instancia de Redis sin autenticacion en un puerto no estandar. La flag se obtiene directamente desde la CLI de Redis sin necesidad de explotar ninguna vulnerabilidad de codigo: es un fallo de configuracion puro. Maquina ideal para interiorizar el patron "servicio expuesto sin credenciales".

> HTB Starting Point es un laboratorio legal y autorizado; todo lo practicado aqui se realiza sobre infraestructura propia de Hack The Box con fines educativos.

---

## Objetivo

Conectarse a la base de datos Redis expuesta en la maquina objetivo, enumerar sus claves y leer la flag almacenada en memoria.

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

**Categoria: escaneo de puertos con deteccion de servicio/version.**

Redis escucha por defecto en el puerto `6379/tcp`. Nmap lo identifica como `redis` si el servicio responde al protocolo inline de Redis.

```bash
nmap -sV -p- --min-rate 5000 <IP>
```

| Flag | Proposito |
|---|---|
| `-sV` | Deteccion de version del servicio |
| `-p-` | Escanear los 65535 puertos (no solo los top 1000) |
| `--min-rate 5000` | Acelerar el escaneo en laboratorio |

Salida esperada relevante:

```
6379/tcp open  redis  Redis key-value store
```

> `-p-` es importante aqui: Redis puede estar configurado en un puerto no estandar. Escanear solo los top 1000 puede hacerlo invisible.

---

## Enumeracion

**Categoria: fingerprinting de Redis con el comando `INFO`.**

`INFO` devuelve metadatos del servidor sin requerir autenticacion (cuando no esta configurada). Es el equivalente a un banner grab enriquecido.

```bash
redis-cli -h <IP>
```

Una vez dentro del prompt interactivo de Redis:

```bash
INFO server
```

Esto revela la version de Redis, sistema operativo, tiempo de actividad y directorio de trabajo. Con esta informacion se confirma que no hay `requirepass` activo (de lo contrario la respuesta seria `NOAUTH Authentication required`).

---

## Acceso inicial (foothold)

**Categoria: acceso directo a base de datos sin autenticacion.**

No hay exploit ni vulnerabilidad de codigo. El patron es:

1. Conectar al servicio abierto.
2. Enumerar todas las claves almacenadas.
3. Leer el valor de la clave que contiene la flag.

```bash
# Listar todas las claves en la base de datos activa
KEYS *
```

Respuesta esperada (los nombres exactos pueden variar en la maquina en vivo):

```
1) "flag"
```

```bash
# Leer el valor de la clave
GET flag
```

Esto devuelve directamente el contenido de la flag. Ajusta el nombre de la clave segun lo que devuelva `KEYS *` en tu instancia.

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente desde la base de datos Redis sin necesidad de acceso al sistema operativo subyacente.

---

## Flags

| Flag | Ubicacion | Como obtenerla |
|---|---|---|
| flag | Clave Redis `flag` (o nombre similar) en la DB 0 | `GET flag` desde redis-cli |

Esta maquina tiene una sola flag. Valor: `<flag>` (se obtiene en vivo con el comando anterior).

> Redis no tiene concepto de `user.txt` / `root.txt`; la flag esta directamente en la base de datos en memoria.

---

## Patron y teoria

### El patron: servicio de infraestructura expuesto sin autenticacion

**Categoria de vulnerabilidad: misconfiguracion — credenciales ausentes en servicio de red.**

Redis es una base de datos en memoria disenada para operar en redes internas de confianza (localhost o LAN privada). Su configuracion por defecto historicamente no requeria contrasena, asumiendo que la red la protegia. Cuando se expone a una interfaz publica sin `requirepass`, cualquier cliente puede leer, escribir o borrar todos los datos.

El patron se repite con otros servicios de infraestructura:

| Servicio | Puerto por defecto | Mismo patron |
|---|---|---|
| Redis | 6379 | Sin auth por defecto |
| MongoDB | 27017 | Sin auth en versiones antiguas |
| Elasticsearch | 9200 | Sin auth por defecto |
| Memcached | 11211 | Sin auth |
| Kafka | 9092 | Sin auth por defecto |

Todos comparten la misma asuncion rota: "la red me protege, no necesito auth".

### Como se defiende / como se disena para evitarlo

**Para el dev / purple team:**

1. **`requirepass` siempre activo**, incluso en entornos internos. En Redis 6+ se puede usar ACL para control granular por usuario y comando.

```bash
# En redis.conf
requirepass <contrasena-fuerte>

# Con ACL (Redis 6+)
ACL SETUSER appuser on ><password> ~app:* +GET +SET
```

2. **`bind` a loopback o a la interfaz interna especifica**, nunca a `0.0.0.0` salvo necesidad justificada:

```bash
# redis.conf
bind 127.0.0.1
```

3. **Firewall de red**: aunque Redis tenga auth, el puerto 6379 no deberia ser alcanzable desde internet. En produccion: grupo de seguridad / iptables que solo permita trafico desde la VLAN de la aplicacion.

```bash
# iptables: solo permitir Redis desde la subred de la app
iptables -A INPUT -p tcp --dport 6379 -s 10.0.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 6379 -j DROP
```

4. **TLS** para trafico Redis en transito (Redis 6+ soporta TLS nativo).

5. **Principio de minimo privilegio en la app**: la aplicacion solo debe tener acceso a las claves que necesita (`~prefix:*`), nunca a `KEYS *` (que ademas bloquea el servidor en produccion).

### Por que importa para el disenador

Si tu aplicacion usa Redis como cache de sesiones, broker de tareas (Celery, BullMQ) o almacen de tokens, una instancia expuesta sin auth es una brecha critica: un atacante puede leer sesiones activas, inyectar tareas maliciosas o borrar datos en memoria. El coste de `requirepass` es practicamente cero; el coste de no tenerlo puede ser una filtracion de datos completa.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- — patron general de servicios expuestos sin auth
- — si existe nota sobre el principio
