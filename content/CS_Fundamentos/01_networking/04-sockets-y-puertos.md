# 04 — Sockets y puertos

> 📚 **Doc 4 del cluster Networking**. Aquí bajamos al nivel de programación. Cómo el SO te da acceso a la red mediante la abstracción de "socket".
> 🔥 **Frecuencia interview**: aparece en system design (puertos well-known, port exhaustion) y en preguntas low-level.
> ⏱️ **Tiempo de lectura estimado**: 40-60 min.

---

## 1. Qué es un socket

**Socket** es la abstracción del SO que representa un **endpoint de comunicación de red**. Es lo que permite a tu programa enviar y recibir datos por red sin manejar bits.

**Analogía**: un socket es como un teléfono. Tienes que crearlo (descolgar), asociarlo a una "dirección" (número de teléfono = IP+puerto), conectar (marcar) o escuchar (esperar llamada), mandar/recibir datos (hablar/escuchar) y cerrar (colgar).

**API clásica**: Berkeley sockets (1983, BSD Unix). Casi todo el mundo usa esta API. Windows tiene Winsock que es casi idéntico.

**Desde Python**:
```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP IPv4
s.connect(("google.com", 80))
s.send(b"GET / HTTP/1.0\r\nHost: google.com\r\n\r\n")
print(s.recv(4096))
s.close()
```

Esto es lo que `requests`, `httpx`, FastAPI, Postgres driver, **TODO** lo de red, hace por debajo. Todos terminan en `socket()` syscalls.

---

## 2. Los 4 valores que IDENTIFICAN una conexión

Cada conexión TCP única en el mundo está identificada por una **tupla de 4 valores**: `(SRC_IP, SRC_PORT, DST_IP, DST_PORT)`.

**Ejemplo**: `(192.168.1.50, 43521, 142.250.184.46, 443)` — tu PC, tu puerto efímero, google, HTTPS.

**Implicación importante**: tu PC puede tener **múltiples conexiones simultáneas al mismo server** (e.g. abres 5 pestañas a google) porque cada una usa un puerto efímero distinto en tu lado. La tupla 4-elementos es siempre única.

---

## 3. Puertos — el "número de teléfono" del proceso

Un **puerto** es un número de 16 bits (0-65535) que identifica QUÉ proceso/servicio en una máquina recibe los datos.

**Rangos de puertos**:

| Rango | Categoría | Notas |
|---|---|---|
| 0–1023 | **Well-known ports** (privilegiados) | Reservados para servicios estándar. Requieren permisos de root/admin para usar (en Linux/Mac). |
| 1024–49151 | **Registered ports** | Asignados por IANA a servicios específicos pero no privilegiados. |
| 49152–65535 | **Dynamic / Ephemeral ports** | Tu SO los asigna automáticamente para conexiones SALIENTES. |

**Lista de puertos well-known IMPORTANTE saber**:

| Puerto | Servicio |
|---|---|
| 20-21 | FTP |
| 22 | SSH |
| 23 | Telnet (deprecated) |
| 25 | SMTP (mail send) |
| 53 | DNS |
| 80 | HTTP |
| 110 | POP3 |
| 143 | IMAP |
| 443 | HTTPS |
| 465 | SMTPS |
| 587 | SMTP submission |
| 993 | IMAPS |
| 995 | POP3S |
| 3306 | MySQL |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 27017 | MongoDB |
| 5672 | RabbitMQ |
| 9092 | Kafka |
| 8000 | dev típico (FastAPI, Django) |
| 3000 | dev típico (Node, React, Next) |
| 8080 | proxy alternativo |

**Para interview**: saber 80/443/22/53/5432/6379 al menos. Aparecen.

---

## 4. El lifecycle de un socket TCP — server side

```python
import socket

# 1. Crear el socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                     ^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^
#                     IPv4              TCP

# 2. (Opcional) permitir reusar la dirección rápido tras un crash
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 3. Bind a una IP+puerto
server.bind(("0.0.0.0", 8000))   # 0.0.0.0 = todas las interfaces

# 4. Empezar a escuchar (con backlog de conexiones pendientes)
server.listen(128)   # 128 = max conexiones en cola sin aceptar

# 5. Loop: aceptar conexiones
while True:
    client_sock, client_addr = server.accept()   # BLOCKING

    # 6. Recibir y enviar datos en el client_sock
    data = client_sock.recv(4096)        # max 4096 bytes
    client_sock.send(b"HTTP/1.1 200 OK\r\n\r\nHello")

    # 7. Cerrar la conexión cliente
    client_sock.close()

# 8. (Cuando se cierra el server)
server.close()
```

**Lo importante**: `server.accept()` devuelve un **NUEVO socket** para cada conexión cliente. El socket original `server` sigue escuchando para nuevas conexiones. Por esto un solo proceso puede atender muchas conexiones.

---

## 5. El lifecycle de un socket TCP — client side

```python
import socket

# 1. Crear el socket (igual que server)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. Conectar a un server
client.connect(("142.250.184.46", 443))
# El SO asigna automáticamente un puerto efímero LOCAL para tu lado.

# 3. Enviar y recibir
client.send(b"GET / HTTP/1.0\r\n\r\n")
response = client.recv(4096)

# 4. Cerrar
client.close()
```

---

## 6. UDP sockets — más simple porque no hay conexión

```python
# UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # SOCK_DGRAM = UDP
server.bind(("0.0.0.0", 5000))

while True:
    data, addr = server.recvfrom(4096)   # data + dirección del sender
    server.sendto(b"reply", addr)         # responder al sender


# UDP client
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b"hello", ("server.com", 5000))
data, _ = client.recvfrom(4096)
```

**Diferencias clave UDP vs TCP**:
- No hay `accept()` ni `connect()` en UDP — cada paquete se envía/recibe independiente.
- No hay nuevos sockets por cliente — el mismo socket atiende a TODOS.
- Sin garantía de orden ni entrega — tu app debe lidiar con eso.

---

## 7. Bloqueante vs no-bloqueante (I/O models)

Cuando llamas `socket.recv()`, ¿qué pasa si no hay datos?

### Modo bloqueante (default)

```python
client.recv(4096)   # BLOQUEA hasta que lleguen datos o se cierre la conexión
```

**Problema**: si tu programa atiende a 1000 clientes con 1000 sockets, ¿necesitas 1000 threads (1 por cliente)? Cada uno bloqueado en su `recv`. Para muchas conexiones, **no escala** (memoria + context switching).

### Modo no-bloqueante

```python
client.setblocking(False)
try:
    data = client.recv(4096)
except BlockingIOError:
    # No hay datos AÚN. Continúa con otra cosa.
    pass
```

**Problema**: ahora tienes que estar polling (preguntando "¿hay datos?") constantemente. CPU desperdiciada.

### Solución: I/O multiplexing (`select`, `poll`, `epoll`, `kqueue`)

```python
import selectors

sel = selectors.DefaultSelector()  # usa epoll en Linux, kqueue en Mac
sel.register(client_sock, selectors.EVENT_READ)

while True:
    events = sel.select()  # BLOQUEA hasta que ALGÚN socket tenga datos
    for key, mask in events:
        sock = key.fileobj
        data = sock.recv(4096)   # ahora sí, hay datos seguro
        # procesar...
```

El kernel te avisa cuándo cualquier socket tiene actividad. Esto es lo que permite **un solo thread atendiendo miles de conexiones** (modelo "event loop").

### Async I/O (Python asyncio, JavaScript event loop, Node)

```python
import asyncio

async def handle_client(reader, writer):
    data = await reader.read(4096)   # SUSPENDE esta tarea, otras siguen
    writer.write(b"hello")
    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 8000)
    await server.serve_forever()

asyncio.run(main())
```

`asyncio` por debajo usa epoll/kqueue. Es **azúcar sintáctico** sobre I/O multiplexing. Lo que hace FastAPI/Uvicorn por defecto.

---

## 8. Los 5 I/O models (referencia)

1. **Blocking I/O (síncrono)**: `recv()` bloquea hasta tener datos. 1 thread por conexión.
2. **Non-blocking I/O (con polling)**: `recv()` devuelve inmediato, vacío si no hay datos. App polea constantemente. Mal.
3. **I/O multiplexing (select/poll/epoll)**: pides al kernel "avísame cuando ESTOS sockets tengan datos". 1 thread atiende muchos sockets. Base de Nginx, Node, asyncio.
4. **Signal-driven I/O**: kernel envía señal cuando hay datos. Poco usado.
5. **Asynchronous I/O (true async, AIO en Linux, IOCP en Windows)**: "Empieza esta operación, llámame cuando termine." Realmente solo Windows IOCP lo hace bien. Linux io_uring (moderno) es lo más cercano.

**Para SWE moderno**: dominar I/O multiplexing + async/await es lo importante. Los demás son cultura.

---

## 9. Port exhaustion — el problema oculto

**El problema**: cada conexión saliente usa un puerto efímero local. Rango efímero: ~28000 puertos típicamente (32768-60999 default Linux). Si abres miles de conexiones rápido y no se cierran bien, AGOTAS los puertos. El error típico es `EADDRNOTAVAIL` / "Cannot assign requested address".

**Cuándo pasa**:
- Tests de carga (10000 requests rápidas).
- Microservices que abren conexión nueva por request en lugar de pool.
- Conexiones en TIME_WAIT acumuladas (TIME_WAIT = ~60s tras close).

**Soluciones**:
- **Connection pooling** (reutilizar conexiones).
- Aumentar rango efímero: `net.ipv4.ip_local_port_range = 10000 65535`.
- `SO_REUSEADDR` + tuneo TCP TIME_WAIT.
- Para descargas masivas: usar fewer larger connections.

**En práctica**: HTTP libraries como `requests`, `httpx`, `urllib3` tienen connection pools por defecto. Si haces 1000 requests al mismo server, REUSAN conexiones TCP. Solo abres 1-N nuevas, no 1000.

---

## 10. SO_REUSEADDR y SO_REUSEPORT

**`SO_REUSEADDR`**: permite hacer bind a un puerto que está en TIME_WAIT. Cuando cierras un server y reinicias, el puerto puede estar "ocupado" 60s en TIME_WAIT. Sin esto, no puedes reiniciar. Casi siempre se pone en server sockets.

**`SO_REUSEPORT`**: permite que múltiples procesos hagan bind al MISMO puerto. El kernel reparte conexiones entrantes entre ellos. Útil para load balancing entre workers (`uvicorn --workers N` usa esto). Linux 3.9+, no portable a todos los sistemas.

---

## 11. Connection pooling — patrón crítico

**Sin pool**, cada request:
- `socket → connect → handshake TCP → handshake TLS → request → close`.
- Latencia: 100-200ms en cada request por handshakes.
- Port exhaustion en alta carga.

**Con pool**, mantienes N conexiones abiertas a destinos comunes. Cada request las reusa. Solo handshakes en la primera vez. Latencia: <10ms en requests subsecuentes. No hay port exhaustion.

**Ejemplos de pool**:
- HTTP: `requests`, `httpx`, `urllib3` (default tienen pool).
- DB: SQLAlchemy + asyncpg, psycopg pool.
- Redis: `redis-py` BlockingConnectionPool.
- Custom: cualquier cliente serio implementa pool.

**Cuándo tienes que pensarlo**:
- Microservices llamándose entre sí: USA POOL.
- Conexiones a DB: USA POOL.
- Llamadas a APIs externas en bucle: USA POOL.

---

## 12. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

**Server**: Uvicorn crea un socket TCP en bind 0.0.0.0:8000, hace listen, accept en loop. Para cada request crea (no nuevo socket — reutiliza el de la conexión) un task asyncio.

**Cliente** (`cli.py` con `requests`): por defecto usa connection pool — si haces 5 requests seguidas al mismo localhost:8000, reusa la misma conexión TCP.

**Docker**: el `ports: "8000:8000"` mapea el puerto del host al del container. Tu PC ve un socket en 127.0.0.1:8000, pero por debajo es un proxy a la IP del container en su network privada.

### En interview

**Pregunta**: "¿Cuántas conexiones puede atender un servidor a la vez?"

**Respuesta**: con bloqueante 1 thread/conexión → ~10K antes de saturar. Con I/O multiplexing (epoll/asyncio) → 100K-1M conexiones por proceso (C10K problem ya resuelto). El cuello deja de ser threads y pasa a ser ancho de banda + memoria por conexión.

**Pregunta**: "¿Por qué tu API se queda sin puertos en load test?"

**Respuesta**: port exhaustion en el lado cliente (puertos efímeros). Cada conexión usa un puerto local. 28K puertos / 60s de TIME_WAIT → ~466 conexiones nuevas por segundo máximo sostenido sin pool. Solución: connection pooling.

### En embebido (tu IoT)

Tu protocolo binario probablemente abre un socket TCP/UDP custom. Saber sobre TIME_WAIT, port exhaustion y connection reuse te ahorra bugs de "el sensor pierde conexión cada N horas".

---

## 13. Trampas típicas

**"Cada request abre nueva conexión TCP"**: no con connection pool. `requests`, `httpx`, drivers DB todos pool. Si NO usas pool, sí. Y te quedas sin puertos rápido.

**"0.0.0.0 es una IP"**: no es una IP destino. Es un wildcard que dice "bind a TODAS las interfaces de esta máquina". El paquete real lleva la IP específica que recibió la conexión.

**"127.0.0.1 y localhost son lo mismo"**: casi siempre sí, pero localhost es un NOMBRE que se resuelve via `/etc/hosts`. Puedes cambiarlo. Y localhost puede resolver a IPv6 ::1 también según config.

**"TIME_WAIT es un bug"**: no, es necesario por TCP spec. Asegura que paquetes retrasados de la conexión cerrada no confunden a una conexión nueva en el mismo tuple. SO_REUSEADDR + tuneo es la solución, no quitar TIME_WAIT.

**"Threads son la única forma de concurrencia"**: threads, async/await, multiprocessing, event loops, todos válidos. Cuándo cada uno depende del workload (I/O bound vs CPU bound).

**"Bind a puerto < 1024 sin root"**: Linux/Mac requieren root o capability `CAP_NET_BIND_SERVICE`. Por eso webservers como nginx arrancan como root, hacen bind a 80, y luego "drop privileges" a www-data.

---

## 14. Cosas típicas que preguntan en interview

**"¿Qué es un socket?"** — endpoint de comunicación de red (la abstracción del SO). Cada socket TCP tiene 2 lados, identificados por (IP+port). Cada conexión completa por (src_ip, src_port, dst_ip, dst_port).

**"Diferencia entre TCP socket y UDP socket"** — TCP requiere connect/accept (orientado a conexión). UDP es sendto/recvfrom (sin conexión). TCP usa SOCK_STREAM, UDP usa SOCK_DGRAM.

**"¿Cómo escala un server a millones de conexiones?"** — no con threads (1:1 no escala más allá ~10K). Con I/O multiplexing (epoll/kqueue) + event loop. Modelo C10K resuelto en 2000s, ahora apuntamos a C10M.

**"¿Qué pasa cuando 2 procesos hacen bind al mismo puerto?"** — sin SO_REUSEPORT: el segundo da EADDRINUSE. Con SO_REUSEPORT (Linux 3.9+): el kernel reparte conexiones entre ambos.

**"¿Por qué tu API se queda colgada en alta carga?"** — causas comunes: file descriptors agotados (ulimit -n), port exhaustion (puertos efímeros), connection pool exhausted, DB connection pool exhausted, thread pool del runtime exhausted. Hay que medir cuál.

**"Diferencia entre puerto well-known y efímero"** — well-known: 0-1023, reservados, requieren privileges. Efímeros: 49152-65535 (estándar) o 32768+ (Linux), asignados por el SO automático para conexiones salientes.

---

## 15. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Qué es un socket conceptualmente.
- La tupla 4-elementos que identifica una conexión TCP.
- Rangos de puertos: well-known (0-1023), registered (1024-49151), efímeros (49152-65535).
- Lifecycle de socket TCP server: socket→bind→listen→accept→close.
- Lifecycle de socket TCP client: socket→connect→close.
- Por qué accept() devuelve un nuevo socket.
- I/O bloqueante vs no-bloqueante vs multiplexing.
- El C10K problem y por qué async/epoll lo resuelve.
- Port exhaustion: qué es y cómo evitarlo (connection pool).
- 6-8 puertos well-known típicos (80, 443, 22, 53, 5432, 6379, etc.).

Si no puedes → relee la sección.

---

## Conexiones

- [[01-tcp-ip-osi]] — sockets implementan TCP/UDP
- [[02-http-y-evolucion]] — HTTP corre sobre sockets TCP
- [[03-dns-resolucion-nombres]] — DNS usa puerto 53 (UDP típico)
- [[05-tls-https]] — TLS añade capa de cifrado encima del socket
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]
- — `requests` por debajo es socket
- [[../03_concurrency/04-async-vs-threads-vs-procesos]] — modelos de concurrencia para sockets

## Recursos externos

- **Beej's Guide to Network Programming** (beej.us/guide/bgnet/) — clásico, gratis, en C pero conceptos universales.
- **Python socket docs** (docs.python.org/3/library/socket.html) — referencia + ejemplos.
- **The C10K problem** (kegel.com/c10k.html) — paper histórico sobre escalar conexiones.
- **High Performance Browser Networking** capítulo TCP (hpbn.co).
- **`netstat`, `ss`, `lsof`** — herramientas para inspeccionar sockets activos en tu sistema.
- **`tcpdump` + Wireshark** — capturar tráfico real, ver headers TCP.
