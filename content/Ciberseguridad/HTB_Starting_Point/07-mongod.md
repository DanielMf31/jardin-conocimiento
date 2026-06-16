---
title: Mongod (HTB Starting Point)
date: 2026-06-15
tags: [ciberseguridad, htb, starting-point, pentesting, mongodb, nosql, misconfiguration, recon]
type: nota
status: en-progreso
source: claude-code
aliases: [mongod htb, mongodb sin auth, nosql expuesto]
---

# Mongod — HTB Starting Point (Tier 0)

**Tier 0 · SO: Linux · Dificultad: Very Easy · Skills: Recon con nmap, cliente MongoDB (mongosh)**

Maquina introductoria que expone MongoDB en su puerto por defecto sin ningun mecanismo de autenticacion. El objetivo es conectarse directamente al servicio y extraer la flag desde la shell de Mongo. Ningun exploit, solo configuracion negligente.

> Este laboratorio es parte de Hack The Box Starting Point, un entorno legal y autorizado para practicar tecnicas de pentesting de forma etica.

---

## Objetivo

Acceder a la base de datos MongoDB expuesta en la maquina victima, localizar la coleccion con la flag y leerla.

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

**Categoria: escaneo de puertos y servicios.**

Empezamos con `nmap` para identificar que servicios estan escuchando. El parametro `-sV` detecta versiones; `-p-` o un rango amplio nos asegura no saltarnos el puerto no estandar si lo hubiera (en esta maquina suele estar en el estandar 27017, pero es buena practica).

```bash
nmap -sV -p 1-65535 --open <IP>
```

Salida relevante esperada:

```
27017/tcp open  mongodb  MongoDB 3.x / 4.x / 5.x
```

Que nos dice nmap:
- **Puerto 27017**: puerto por defecto de MongoDB.
- **Sin banner de autenticacion**: nmap a veces puede enumerar bases de datos directamente si el servicio esta abierto sin auth.

---

## Enumeracion

**Categoria: enumeracion de servicio NoSQL.**

Una vez identificado el puerto, intentamos conectarnos con el cliente oficial. Si la instalacion de MongoDB en tu maquina es reciente, el cliente se llama `mongosh`; en versiones antiguas era `mongo`.

```bash
mongosh <IP>:27017
# o si solo tienes el cliente legacy:
mongo --host <IP> --port 27017
```

Si la conexion abre una shell interactiva (`test>`) sin pedir credenciales, la vulnerabilidad esta confirmada: **MongoDB sin autenticacion, accesible desde la red**.

Listamos todas las bases de datos disponibles:

```bash
show dbs
```

Salida esperada (puede variar, los nombres reales los ves en vivo):

```
admin              0.000GB
config             0.000GB
local              0.000GB
sensitive_information  0.000GB
```

La base de datos `sensitive_information` destaca por su nombre. La seleccionamos:

```bash
use sensitive_information
```

Listamos sus colecciones:

```bash
show collections
```

Salida esperada:

```
flag
```

---

## Acceso inicial (foothold)

**Categoria: lectura directa de datos sin autenticacion.**

No hay foothold en el sentido clasico (no hay shell del SO). El "acceso" es leer la flag directamente desde la base de datos con una query Mongo estandar:

```bash
db.flag.find()
```

Esto devuelve el documento completo de la coleccion `flag`. La flag aparece en el campo correspondiente del documento JSON devuelto. Copia el valor para enviarlo en HTB.

Si quieres una salida mas legible:

```bash
db.flag.find().pretty()
```

---

## Escalada de privilegios

No requiere privesc: la flag se obtiene directamente desde la shell de MongoDB sin necesidad de acceso al sistema operativo ni escalada de permisos.

---

## Flags

| Flag | Ubicacion | Metodo |
|---|---|---|
| Flag unica | Coleccion `flag` en la base de datos `sensitive_information` | `db.flag.find()` desde mongosh |

No hay `user.txt` ni `root.txt` en esta maquina; la flag se extrae directamente de MongoDB. El valor exacto es `<flag>` (lo obtendras al ejecutar el comando contra la maquina en vivo).

---

## Patron y teoria

**Este es el nucleo del aprendizaje.**

### El patron: servicio de base de datos expuesto sin autenticacion

**Categoria de vulnerabilidad: Misconfiguration — servicio de datos expuesto a red sin auth.**

MongoDB, Redis, Elasticsearch y otros sistemas NoSQL/de cache tienen en comun que en su configuracion por defecto (o en configuraciones negligentes) **escuchan en todas las interfaces (`0.0.0.0`) sin requerir credenciales**. Esto no es una vulnerabilidad del software en si, es una decision de despliegue erronea.

El patron que se repite en la realidad (no solo en HTB):
1. Desarrollador levanta MongoDB localmente para desarrollo, sin auth.
2. La instancia termina en produccion (cloud VM, contenedor) con la misma configuracion.
3. El puerto 27017 queda expuesto a internet o a la red interna.
4. Cualquiera con `mongosh` puede leer (y escribir) todos los datos.

Este vector fue responsable de miles de filtraciones masivas entre 2017 y 2019 (campanas de "MongoDB Apocalypse" y ataques de ransomware sobre bases de datos NoSQL expuestas).

### Como se defiende / como lo disenas bien (perspectiva dev/purple team)

**1. Habilitar autenticacion desde el principio.**

En `mongod.conf`:

```yaml
security:
  authorization: enabled
```

Y crear un usuario administrador antes de exponer el servicio:

```bash
use admin
db.createUser({
  user: "adminUser",
  pwd: "contrasena_fuerte",
  roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
})
```

**2. Bind solo a localhost o a la interfaz correcta.**

```yaml
net:
  bindIp: 127.0.0.1
```

Si la app necesita conectarse desde otro host, usa una red privada o VPN, nunca expongas el puerto directamente a internet.

**3. Firewall a nivel de infraestructura.**

Incluso con auth activa, el puerto 27017 no debe ser accesible desde internet. Regla de seguridad en profundidad: firewall + auth + red privada.

**4. En Docker/Compose (contexto del proyecto app web).**

Si usas MongoDB en `docker-compose.yml`, define la red como interna y NO publiques el puerto al host en produccion:

```yaml
# MAL (expone al host):
ports:
  - "27017:27017"

# BIEN (solo accesible entre contenedores de la misma red):
expose:
  - "27017"
```

Y siempre con variables de entorno para credenciales:

```yaml
environment:
  MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
  MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
```

**5. Auditoria rapida de tu infraestructura.**

```bash
# Desde fuera: ver si el puerto responde sin credenciales
mongosh <IP>:27017 --eval "db.adminCommand({ listDatabases: 1 })"

# Desde el servidor: ver a que interfaces esta bindeado mongo
ss -tlnp | grep 27017
```

### Resumen del modelo mental

```
Servicio de datos  →  ¿escucha en 0.0.0.0?  →  ¿sin auth?  →  filtracion total
                   →  bind localhost + auth + firewall  →  superficie de ataque minima
```

La defensa no es oscuridad (cambiar puerto), es autenticacion + red restringida + firewall en capas.

---

## Conexiones

- [[HTB_Starting_Point/00_README]]
- [[MOC_Ciberseguridad]]
- [[12-aprender-y-carrera]]
- [[MOC_Programacion]]

### Notas de teoria relacionadas (crear si no existen)

- `nosql-mongodb-fundamentos.md` — arquitectura de documentos, colecciones, queries basicas
- `misconfiguration-servicios-expuestos.md` — patron general de servicios mal configurados (MongoDB, Redis, Elasticsearch)
- `docker-compose-seguridad-redes.md` — redes internas vs puertos publicados en Compose

---

*Fuente: laboratorio oficial HTB Starting Point Tier 0 — Mongod. Solucion basada en el flujo estandar guiado por HTB.*
