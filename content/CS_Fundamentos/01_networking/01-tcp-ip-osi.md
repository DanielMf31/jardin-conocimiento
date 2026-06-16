# 01 — TCP/IP y modelo OSI

> 📚 **Doc fundacional del cluster Networking**. Lee esto antes que cualquier otro doc de redes. Sin entender capas, encapsulación y three-way handshake, el resto no encaja.
> 🔥 **Frecuencia interview**: aparece directa o indirectamente en CASI TODA system design entrevistas tecnicas.
> ⏱️ **Tiempo de lectura estimado**: 60-90 min con atención.

---

## 1. Por qué un modelo en capas

La comunicación entre dos máquinas en internet involucra muchas cosas: señales eléctricas en cable, conversión a bits, asegurar que llegan, gestionar pérdidas, distinguir aplicaciones, etc. Si todo fuera un solo bloque monolítico, sería ingobernable.

La solución es **dividir en capas** donde cada capa hace UNA cosa y solo habla con la capa de arriba y la de abajo. Cada capa NO sabe lo que hacen las otras — solo respeta el contrato.

**Analogía con mandar una carta**: tú escribes (capa aplicación). La metes en sobre con dirección (capa transporte). El cartero la coge y mete en saca de tu zona (capa red). Camión transporta sacas (capa enlace). Asfalto y carreteras (capa física).

El cartero NO necesita saber qué dice tu carta. Tú NO necesitas saber qué carretera coge el camión. Cada capa hace SU trabajo aislado del resto.

Esto es **abstracción** llevada al extremo. Si mañana cambian los routers físicos, las capas superiores no se enteran. Si mañana inventas un nuevo protocolo de aplicación, las capas inferiores no se enteran.

---

## 2. Los dos modelos: OSI y TCP/IP

Hay dos modelos teóricos. Ambos describen lo mismo, pero con distinto número de capas.

### Modelo OSI — 7 capas (académico, conceptual)

| # | Capa | Ejemplos |
|---|---|---|
| 7 | Aplicación | HTTP, FTP, SMTP, DNS |
| 6 | Presentación | TLS, encoding (UTF-8), compresión |
| 5 | Sesión | login, session management |
| 4 | Transporte | TCP, UDP |
| 3 | Red | IP, ICMP, routing |
| 2 | Enlace de datos | Ethernet, Wi-Fi, MAC address |
| 1 | Física | cable de cobre, fibra, ondas radio |

> 💡 **Mnemotecnia inglesa**: "Please Do Not Throw Sausage Pizza Away" (Physical, Data link, Network, Transport, Session, Presentation, Application).

### Modelo TCP/IP — 4 capas (real, lo que se usa)

| # | Capa | Ejemplos | Equivalente OSI |
|---|---|---|---|
| 4 | Aplicación | HTTP, DNS, FTP, TLS | combina 5, 6, 7 |
| 3 | Transporte | TCP, UDP | OSI 4 |
| 2 | Internet | IP, ICMP | OSI 3 |
| 1 | Enlace | Ethernet, Wi-Fi | OSI 1+2 |

**¿Cuál usar mentalmente?** El que usa la industria de verdad es **TCP/IP de 4 capas**. OSI se enseña en universidad porque es más granular pedagógicamente. En interview, menciona ambos y demuestra que sabes la diferencia.

---

## 3. Encapsulación — el corazón del modelo en capas

Cuando mandas datos por la red, **cada capa añade su propio "sobre" alrededor de los datos** que vienen de la capa de arriba. Esto se llama **encapsulación**.

### Ejemplo concreto: enviar `GET /index.html` por HTTP

Cada capa va añadiendo headers (sobres) alrededor del payload original. En el receptor el proceso es al revés (desencapsulación):

1. Llega el frame Ethernet → quitar header Ethernet → queda IP packet.
2. Quitar header IP → queda TCP segment.
3. Quitar header TCP → queda HTTP request.
4. La aplicación procesa el HTTP request.

**Lo importante a interiorizar**: cada capa **añade overhead** (su propio header). Por eso el "tamaño máximo de payload" depende de qué overhead suman las capas inferiores. **MTU** (Maximum Transmission Unit) típica en Ethernet es **1500 bytes** — de ahí restas headers IP (20B) + TCP (20B) = quedan **1460 bytes** efectivos para tu aplicación por paquete.

Visualización del proceso de encapsulación:

```
APLICACIÓN (HTTP):
  ┌─────────────────────────────────┐
  │ GET /index.html HTTP/1.1        │  ← payload aplicación
  │ Host: example.com               │
  └─────────────────────────────────┘
              ↓ pasa a transporte

TRANSPORTE (TCP):
  ┌──────────┬─────────────────────────────────┐
  │ TCP hdr  │ GET /index.html HTTP/1.1        │
  │ src=43521│ Host: example.com               │
  │ dst=80   │                                 │
  └──────────┴─────────────────────────────────┘
              ↓ pasa a internet

INTERNET (IP):
  ┌──────────┬──────────┬─────────────────────────────────┐
  │ IP hdr   │ TCP hdr  │ GET /index.html HTTP/1.1        │
  │ src=10.0.│          │                                 │
  │ dst=93.X │          │                                 │
  └──────────┴──────────┴─────────────────────────────────┘
              ↓ pasa a enlace

ENLACE (Ethernet):
  ┌──────────┬──────────┬──────────┬───────────────────────┬─────┐
  │ Eth hdr  │ IP hdr   │ TCP hdr  │ HTTP payload          │ FCS │
  │ src=MAC1 │          │          │                       │     │
  │ dst=MAC2 │          │          │                       │     │
  └──────────┴──────────┴──────────┴───────────────────────┴─────┘
              ↓ a la físical (bits sobre el cable)
```

---

## 4. Las capas TCP/IP en detalle

### Capa 1 — Enlace (Link layer)

**Qué hace**: mover bits entre dos máquinas físicamente conectadas (mismo cable, mismo Wi-Fi).

**Identificadores**: **MAC address** (48 bits, formato `aa:bb:cc:dd:ee:ff`). Único por interfaz de red. Asignado por el fabricante.

**Protocolos típicos**: Ethernet (cable RJ45), Wi-Fi (802.11), PPP (módems antiguos).

**Lo que importa para SWE**: prácticamente nada en el día a día. Solo entender que existe.

### Capa 2 — Internet (IP)

**Qué hace**: rutear paquetes entre cualquier par de máquinas en internet, atravesando muchos saltos (routers).

**Identificadores**: **IP address**.
- **IPv4** (32 bits, formato `192.168.1.10`) — escasos, ya agotados oficialmente.
- **IPv6** (128 bits, formato `2001:db8::1`) — adopción progresiva.

**Lo que es CRÍTICO entender**: IP es **unreliable y connectionless**. Un paquete IP puede perderse, llegar duplicado, o llegar en desorden. IP NO se preocupa por nada de eso. Por eso se inventó TCP encima — TCP da garantías que IP no.

**Header IP simplificado** (lo que necesitas saber):

| Campo | Significado |
|---|---|
| `src IP` | de dónde viene |
| `dst IP` | a dónde va |
| `TTL` | Time To Live (cuántos saltos antes de descartarse) |
| `protocol` | qué hay arriba (TCP=6, UDP=17, ICMP=1) |
| `fragment info` | si el paquete es muy grande, se trocea |

**Routing**: cómo un paquete sabe llegar de Madrid a Tokio. Tu PC → router de tu casa → ISP local → ISP regional → backbone Tier-1 → submarine cable → backbone asiático → ISP japonés → router final → servidor destino. Cada router consulta su **tabla de routing**. Esto es **Border Gateway Protocol (BGP)** a nivel global, **OSPF/RIP** a nivel local.

### Capa 3 — Transporte (TCP/UDP)

**Qué hace**: permitir que **aplicaciones distintas en la misma máquina** se comuniquen sin pisarse, y dar garantías que IP no da.

**Identificadores**: **puertos** (16 bits, 0-65535). Ver doc 04 sobre sockets+puertos.

**Comparativa TCP vs UDP**:

| | **TCP** | **UDP** |
|---|---|---|
| Connection | sí (handshake) | no |
| Reliability | sí (retransmission) | no |
| Order | sí (sequence numbers) | no |
| Speed | más lento | más rápido |
| Overhead | 20+ bytes header | 8 bytes header |
| Casos de uso | HTTP, SSH, DB | DNS, video streaming, gaming, VoIP |

**Cuándo usar cada uno**:
- **TCP**: cuando necesitas que llegue todo y en orden (descargas, transacciones, web).
- **UDP**: cuando prefieres velocidad y puedes perder algunos paquetes (video en directo, juegos online — perder un frame es mejor que esperarlo).

### Capa 4 — Aplicación

**Qué hace**: lo que ve el usuario / programador.

**Protocolos típicos**: HTTP/HTTPS (puerto 80/443), FTP (21), SMTP (25), IMAP/POP3 (143/110), DNS (53), SSH (22), WebSocket sobre HTTP.

Cuando programas en FastAPI o `requests`, estás en esta capa. Las inferiores las gestiona el SO + kernel + drivers.

---

## 5. TCP three-way handshake — el clásico

Antes de que TCP transfiera datos, **establece una conexión** con un protocolo de 3 mensajes. Esto se llama **three-way handshake** y aparece en CASI todas las interviews.

```
CLIENTE                                    SERVIDOR
   │                                          │
   │  ──────────  SYN (seq=X)  ────────────→  │   "Quiero hablar contigo"
   │                                          │
   │  ←────  SYN-ACK (seq=Y, ack=X+1)  ────   │   "OK, hablemos"
   │                                          │
   │  ──────────  ACK (ack=Y+1)  ──────────→  │   "Recibido, empezamos"
   │                                          │
   │  ════════ DATOS bidireccionales ═══════  │
```

**Trace paso a paso**:

**Paso 1 — SYN (synchronize)**: cliente envía paquete TCP con flag SYN=1. Incluye un sequence number aleatorio inicial X (por ejemplo X=1000). Cliente: "Hola, mi seq inicial es 1000. ¿Quieres hablar?"

**Paso 2 — SYN-ACK (synchronize + acknowledge)**: server recibe el SYN, decide aceptar. Server responde con flags SYN=1 + ACK=1. Su propio seq inicial Y (por ejemplo Y=5000). Su ack = X+1 = 1001 ("recibí tu SYN, espero el byte 1001"). Server: "Vale, mi seq inicial es 5000. Reconozco tu SYN."

**Paso 3 — ACK (acknowledge)**: cliente confirma recepción del SYN del server. Su ack = Y+1 = 5001. Cliente: "Recibido tu SYN-ACK. Empecemos a hablar."

A partir de aquí, ambos pueden enviar datos. Cada paquete de datos incluye un sequence number (para ordenar) y un ack number (para confirmar lo recibido).

### Por qué 3 pasos y no 2

Uno podría pensar: "¿no bastaría con SYN del cliente y ACK del server?". No. Razón: el server también necesita confirmar que su propio canal de envío funciona.

Si hubiera solo 2 pasos (cliente envía SYN, server responde ACK), el server no sabría si el cliente recibió su ACK. Si el cliente no recibió, el server estaría enviando datos al vacío.

Con 3 pasos, el cliente confirma haber recibido el ACK del server. Ahora ambos están seguros de que la comunicación bidireccional funciona.

### Cierre — el four-way handshake

Para cerrar la conexión hay un **four-way handshake** (FIN, ACK, FIN, ACK). Cada lado cierra su dirección de comunicación independientemente. Menos preguntado en interview pero menciónalo si te preguntan por close.

---

## 6. TCP sliding window — control de flujo

TCP no envía paquetes uno a uno esperando ACK de cada uno (sería lentísimo). Usa **ventanas deslizantes**.

**La idea**: el receptor le dice al sender "puedes enviarme hasta N bytes sin esperar ACK". Esto es la "advertised window". El sender envía hasta llenar esa ventana. Conforme recibe ACKs, "desliza" la ventana hacia adelante.

**Ejemplo con window de 4 paquetes**:

- T=0: Sender envía paquetes 1, 2, 3, 4 (ventana llena, espera).
- T=1: Recibe ACK de 1 → window slides → puede enviar paquete 5.
- T=2: Recibe ACK de 2 → puede enviar paquete 6.
- ...

**Por qué importa**: optimiza throughput. Si la red tiene mucha latencia (e.g. 100ms), enviar de uno en uno significa máximo 10 paquetes/segundo. Con window de 100 paquetes, son 1000 paquetes/segundo.

---

## 7. TCP retransmission y congestion control

**Retransmission**: si sender no recibe ACK de un paquete tras un timeout (RTO), retransmite el paquete. Asumimos que se perdió.

**Congestion control** (varios algoritmos):
- **Slow start**: empieza con window pequeña, dobla cada RTT.
- **Congestion avoidance**: cuando se acerca al límite, crece linealmente.
- **Fast retransmit**: si recibe 3 ACKs duplicados, retransmite sin esperar timeout.
- **Algoritmos modernos**: CUBIC (Linux default), BBR (Google, mejor en redes con loss).

No necesitas saber el detalle implementación, pero sí saber que TCP **se adapta a la congestión** y por eso es robusto pero más lento que UDP.

---

## 8. TCP vs UDP — cuándo cada uno

**Usa TCP cuando**:
- Necesitas garantía de entrega (HTTP, SSH, DB queries, file transfer).
- Necesitas orden (descargar archivo, ver web).
- Puedes tolerar latencia añadida del handshake.
- Caso típico: 95% de aplicaciones SWE.

**Usa UDP cuando**:
- Velocidad importa más que confiabilidad.
- Perder algunos paquetes es aceptable.
- Casos: video streaming en directo, gaming online (Counter-Strike), VoIP, DNS queries, métricas de telemetría.
- Quieres construir tu propia capa de confiabilidad encima (ej: QUIC sobre UDP — base de HTTP/3).

**Casos híbridos**: HTTP/3 usa QUIC sobre UDP (porque UDP es más rápido y QUIC añade su propia confiabilidad mejor que TCP). Esto es un cambio importante de los últimos años.

---

## 9. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Cuando tu cliente CLI hace `requests.post("http://localhost:8000/contacts", json={...})`, lo que ocurre por debajo:

1. **DNS** resuelve `localhost` → `127.0.0.1` (capa aplicación → ver doc 03).
2. **TCP three-way handshake** establece conexión cliente↔servidor en puerto 8000.
3. **HTTP request** se envía como payload TCP (capa aplicación encapsulada).
4. **IP** rutea los paquetes (en localhost es trivial, mismo host).
5. **TCP** asegura que llegan en orden, retransmite si pierde alguno.
6. **Server** desencapsula, FastAPI procesa, genera response.
7. **Misma cadena al revés** para la respuesta.
8. **TCP four-way handshake** cierra conexión (o se reutiliza si keep-alive).

Si Docker está en medio (caso del Phone Book): tu container tiene su propio stack TCP/IP, **port forwarding** del host al container hace de "router" minimal.

### En tus problemas NeetCode

No directamente, pero el problema **271 Encode and Decode Strings** que ya hiciste es **conceptualmente idéntico al problema de TCP**: cómo serializar varios mensajes para que el receptor sepa dónde acaba uno y empieza el siguiente. La solución (length-prefix encoding) es exactamente lo que hace tu protocolo embebido y lo que hacen muchos protocolos binarios reales.

### En embebido (tu proyecto IoT)

Tu protocolo binario sobre TCP/UDP es la versión "raw" de lo que hace HTTP encima de TCP. Entender capas te ayuda a explicar bien embebido en una interview: *"diseñé un protocolo de aplicación binario, encapsulado sobre TCP/UDP, con length-prefix framing porque los streams TCP no preservan boundaries de mensaje"*.

---

## 10. Trampas típicas y malentendidos

**"TCP garantiza que mi mensaje completo llega"**: TCP garantiza un **stream de bytes ordenado y confiable**. NO garantiza "boundaries de mensaje". Si envías "HELLO" y luego "WORLD", el receptor puede leer "HELLOWORLD" todo junto, o "HELL" + "OWORLD", o "H" + "ELLOWO" + "RLD". Por eso necesitas **framing** (length-prefix, delimiter, etc.) en tu protocolo de aplicación.

**"UDP es siempre más rápido que TCP"**: en redes con mucho packet loss, UDP puede ser más LENTO porque tu aplicación tiene que reimplementar retransmission peor que TCP. TCP está muy optimizado tras décadas. UDP solo es más rápido cuando puedes IGNORAR pérdidas (video en vivo).

**"Localhost no usa TCP/IP"**: SÍ lo usa. Pasa por el "loopback interface" pero todo el stack TCP/IP se ejecuta. Por eso 127.0.0.1 también necesita handshake. Es solo que NO sale por la tarjeta de red física.

**"Las direcciones IP son únicas globalmente"**: las IPs PRIVADAS (10.x, 172.16-31.x, 192.168.x) NO son únicas. Tu router en casa hace **NAT** (Network Address Translation): todas las máquinas de tu LAN comparten una sola IP pública hacia fuera.

**"El modelo OSI describe internet"**: internet usa TCP/IP, no OSI. OSI es un modelo conceptual académico que se enseña por su granularidad pedagógica, pero el stack real son las 4 capas TCP/IP.

---

## 11. Cosas típicas que preguntan en interview

**"¿Qué pasa cuando escribes google.com en el navegador y das Enter?"**

Es la pregunta clásica. Espera que toques: DNS resolution (capa aplicación), TCP handshake (capa transporte), TLS handshake si HTTPS (capa aplicación, sobre TCP), HTTP request (capa aplicación), routing IP (capa internet), render del HTML. Sirve para evaluar AMPLITUD de conocimiento. No vayas demasiado profundo en uno; toca todos a nivel medio.

**"Diferencia entre TCP y UDP, ¿cuándo cada uno?"**

Respuesta esperada en este doc, sección 8.

**"¿Qué pasa si dos clientes envían SYN al mismo tiempo al server?"**

Cada SYN se procesa independientemente — el server responde con SYN-ACK a cada uno. Las conexiones se identifican por el "tuple" (src_ip, src_port, dst_ip, dst_port).

**"¿Por qué HTTP usa TCP y no UDP?"**

Necesita garantía de entrega y orden. Una página HTML parcial o desordenada es inutilizable. UDP requeriría reimplementar todo. HTTP/3 cambia esto: usa QUIC sobre UDP, pero QUIC reimplementa garantías similares a TCP optimizadas para web.

**"¿Cómo funciona NAT?"**

Tu router mantiene una tabla (private_ip:port ↔ public_ip:port). Cuando sales: traduce src_ip a la pública del router. Cuando entra respuesta: traduce dst_ip a la privada de tu PC. Es por esto que dos PCs en tu LAN pueden compartir una sola IP pública.

**"Diferencia entre congestion control y flow control"**

Flow control protege al **receiver** (no le inundes si su buffer está lleno). Lo controla la "advertised window" del receiver. Congestion control protege a la **red** (no satures los routers intermedios). Lo controla el sender adaptándose a las pérdidas.

---

## 12. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Las 4 capas del modelo TCP/IP y qué hace cada una.
- La diferencia entre OSI y TCP/IP (y por qué se usa el segundo).
- Qué es encapsulación con un ejemplo concreto.
- Three-way handshake paso a paso (SYN, SYN-ACK, ACK).
- Por qué TCP es reliable y IP no.
- TCP vs UDP: 3 diferencias y cuándo cada uno.
- TCP sliding window: para qué sirve.
- La trampa del TCP stream sin boundaries (necesitas framing).
- Qué es NAT y por qué existe.

Si no puedes → relee la sección correspondiente y prueba de nuevo en 2 días.

---

## Conexiones

- [[02-http-y-evolucion]] — siguiente capa arriba (aplicación)
- [[03-dns-resolucion-nombres]] — cómo se resuelven nombres antes del TCP
- [[04-sockets-y-puertos]] — cómo programar TCP/UDP desde código
- [[05-tls-https]] — cómo se cifra TCP (TLS encima)
- [[../00_README]] — cluster CS Fundamentos
- [[../../../../30_MOCs/MOC_CS_Fundamentos]] — hoja de ruta del cluster
- [[../../LeetCode/01_Arrays_Hashing/271-encode-and-decode-strings]] — length-prefix framing aplicado
- — donde usas requests sobre TCP

## Recursos externos

- **Kurose & Ross — Computer Networking: A Top-Down Approach** — capítulos 1-3 cubren todo este doc en profundidad.
- **Stanford CS144** (curso gratis YouTube) — implementas tu propio TCP en C++. Si te apetece profundidad real.
- **Beej's Guide to Network Programming** (beej.us/guide/bgnet/) — clásico, gratis, programación con sockets.
- **Wireshark** — herramienta para CAPTURAR tráfico TCP/IP real y ver los headers. Instalar y jugar 30 min vale más que leer 10 docs.
- **RFC 793** (TCP original) — denso pero la fuente. Solo si te interesa profundidad.
- **High Performance Browser Networking** (Ilya Grigorik, GRATIS online en hpbn.co) — moderno, web-focused.
