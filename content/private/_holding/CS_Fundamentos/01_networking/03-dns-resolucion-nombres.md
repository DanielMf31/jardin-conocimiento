# 03 — DNS y resolución de nombres

> **Doc 3 del cluster Networking**. DNS es invisible pero está en TODO. La pregunta *"¿qué pasa cuando escribes google.com en el navegador?"* empieza con DNS.
> **Frecuencia interview**: aparece en system design siempre que hay dominios, CDNs, geo-routing.
> **Tiempo de lectura estimado**: 30-50 min.

---

## 1. Qué es DNS y qué problema resuelve

**DNS (Domain Name System)** es el sistema distribuido para traducir **nombres legibles** (`google.com`) a **direcciones IP** (`142.250.184.46`).

**El problema sin DNS**: para conectar a un server necesitas su IP. Las IPs son números difíciles de recordar, cambian (server se mueve, balanceo, IPv4 → IPv6) y necesitas un "directorio telefónico" de internet.

**La solución**: DNS es un directorio distribuido + jerárquico + caché. Los humanos usan nombres. Las máquinas resuelven a IPs.

**Por qué es jerárquico**: si DNS fuera un solo server gigante con todos los nombres, sería un punto de fallo único y un cuello de botella. Se distribuyó en niveles: root → TLD → autoritative → cliente.

---

## 2. La jerarquía DNS

```
                       ROOT  (.)
                        │
        ┌───────────────┼───────────────┐
       (.com)         (.org)         (.es)         ← TLD (Top-Level Domains)
        │               │              │
   ┌────┼────┐       (.wikipedia)  (.gob)         ← Second-Level
   │    │    │
google amazon facebook
   │
   ┌───┼───┐
   www mail maps                                  ← Subdomains
```

**Niveles**:

- **Root** — el más arriba. 13 root servers en el mundo (`a.root-servers.net` hasta `m.root-servers.net`), pero cada uno son cientos de máquinas repartidas globalmente con anycast.
- **TLD (Top-Level Domain)** — `.com`, `.org`, `.net`, `.es`, `.io`, etc. Gestionados por organizaciones específicas (Verisign para .com, Public Interest Registry para .org, Red.es para .es).
- **Second-Level** — `google.com`, `anthropic.com`, `ucm.es`. Gestionados por el dueño del dominio.
- **Subdomains** — `www.google.com`, `mail.google.com`, `api.google.com`. Bajo control total del dueño del dominio.

**Notación con punto final**: `google.com.` (con el punto al final) es el formato "totalmente cualificado". El punto representa el root. Normalmente se omite.

---

## 3. Tipos de DNS records

| Tipo      | Para qué sirve                                   | Ejemplo                                                                          |
| --------- | ------------------------------------------------ | -------------------------------------------------------------------------------- |
| **A**     | IPv4 address                                     | `google.com → 142.250.184.46`                                                    |
| **AAAA**  | IPv6 address                                     | `google.com → 2607:f8b0:4001:c01::8a`                                            |
| **CNAME** | Canonical Name (alias)                           | `www.google.com → google.com` (redirige conceptualmente al lookup de google.com) |
| **MX**    | Mail eXchange (servers de correo)                | `example.com → mail1.example.com (priority 10), mail2 (priority 20)`             |
| **TXT**   | Texto arbitrario                                 | usado para SPF, DKIM, dominio verification                                       |
| **NS**    | Name Server autoritativo del dominio             | `example.com → ns1.example.com, ns2.example.com`                                 |
| **SOA**   | Start of Authority (metadatos de la zona DNS)    | —                                                                                |
| **PTR**   | reverse lookup (IP → name)                       | `8.8.8.8 → google-public-dns-a.google.com`                                       |
| **SRV**   | service records (qué server provee qué servicio) | usado por SIP, XMPP, AD                                                          |
| **CAA**   | Certificate Authority Authorization              | qué CAs pueden emitir certs para este dominio                                    |

**Ejemplo concreto** — qué tiene `google.com`:

```bash
$ dig google.com

;; ANSWER SECTION:
google.com.  300  IN  A  142.250.184.46

;; el "300" es el TTL (Time To Live en segundos)
```

---

## 4. La resolución paso a paso (¡el flow estrella!)

**Pregunta clásica de interview**: *"explica qué pasa cuando escribes `google.com` en el navegador"*. Empieza con DNS.

**Escenario**: tu PC nunca ha visto google.com antes.

**Paso 1 — Browser cache**: browser tiene cache local DNS. Mira: ¿conozco google.com? No. Pasa al SO.

**Paso 2 — OS cache**: el SO (Linux/Mac/Windows) también cachea. Mira: ¿conozco? No. Pasa a `/etc/hosts`.

**Paso 3 — `/etc/hosts`**: archivo local con mappings hardcoded. Útil para development, no para producción. No. Pasa al resolver DNS configurado.

**Paso 4 — Recursive resolver** (típicamente tu ISP o 8.8.8.8): tu PC tiene configurado un "DNS resolver" (puedes verlo: `cat /etc/resolv.conf` en Linux). Le pregunta a este resolver: "¿qué IP tiene google.com?". El resolver tiene su propia caché. Si la respuesta está cacheada y no expirado el TTL → la devuelve directamente. Si NO está cacheada → empieza la búsqueda recursiva (siguientes pasos).

**Paso 5 — Root server query**: resolver pregunta a un root server: "¿quién sabe de .com?". Root responde: "los TLD servers de .com están en a.gtld-servers.net, b.gtld-servers.net...".

**Paso 6 — TLD server query**: resolver pregunta a TLD server de .com: "¿quién sabe de google.com?". TLD responde: "los autoritativos son ns1.google.com, ns2.google.com...".

**Paso 7 — Authoritative server query**: resolver pregunta a `ns1.google.com`: "¿qué A record tiene google.com?". Authoritative responde: "google.com → 142.250.184.46, TTL 300".

**Paso 8 — Cache + return**: resolver cachea la respuesta (TTL 300s). Resolver devuelve la IP a tu PC. Tu PC cachea localmente. Tu browser cachea. Browser empieza la conexión TCP a 142.250.184.46:443.

**Diagrama visual**:

```
[Tu PC]
   │
   │ "¿google.com?"
   ↓
[Recursive resolver (8.8.8.8)]  ←── caché propia
   │
   ├──→ [Root server]: "¿quién sabe .com?"
   │    ←── "ve a a.gtld-servers.net"
   │
   ├──→ [TLD .com]: "¿quién sabe google.com?"
   │    ←── "ve a ns1.google.com"
   │
   └──→ [Authoritative ns1.google.com]: "¿IP de google.com?"
        ←── "142.250.184.46"
   │
   │ "142.250.184.46"
   ↓
[Tu PC]
```

**Optimización clave: TTL + caché**. La mayoría de queries reales NO recorren todo este árbol. Se resuelven en el caché del resolver.

---

## 5. Tipos de queries DNS

**Recursive query**: "Resuélvelo TÚ y dame la respuesta final". Lo que tu PC pregunta a tu resolver (8.8.8.8). El resolver hace todo el trabajo.

**Iterative query**: "Dame lo que sepas, yo sigo preguntando". Lo que el resolver pregunta a root, TLD, authoritative. Cada uno responde con "no lo sé pero ve aquí".

Normalmente: cliente → resolver es recursive. Resolver → root/TLD/authoritative es iterative.

---

## 6. TTL — Time To Live

El **TTL** indica cuántos segundos se puede cachear esta respuesta. Lo define el dueño del dominio en el DNS authoritative.

**Valores típicos**:
- `300` (5 min) — cambios rápidos, mucho tráfico DNS.
- `3600` (1 hora) — balance típico.
- `86400` (1 día) — cambios raros, ahorro de tráfico.

**Trade-off**:
- TTL **bajo**: cambios se propagan rápido (e.g. fallo de server, cambias IP). Pero más carga en DNS authoritative y más latencia (no aprovechas caches lejanos).
- TTL **alto**: caches eficientes (menos queries DNS) y menor latencia para clientes recurrentes. Pero cambios tardan en propagarse (problemático en outages).

**Estrategia real**: antes de un cambio planeado de IP, bajar TTL a 60s con tiempo. Después del cambio + estabilización, subir TTL otra vez.

---

## 7. DNS caching — donde realmente vive el rendimiento

Hay varios niveles de cache, de más cerca a más lejos:

1. **Browser DNS cache** (Chrome, Firefox) — tamaño pequeño, vida corta (típicamente 1 min en Chrome).
2. **OS DNS cache** (systemd-resolved en Linux, mDNSResponder en Mac) — más grande, más vida.
3. **Router de tu casa** (a veces cachea).
4. **ISP / Recursive resolver** (8.8.8.8, 1.1.1.1, ISP) — el cache MÁS importante. Sirve a millones de clientes.
5. **Authoritative servers** — no son cache, son la fuente de verdad.

**Cascade**: cliente → mira cache 1 → si miss, mira 2 → si miss, mira 3... Hasta llegar al authoritative.

**Implicación**: cuando cambias un DNS record, no se actualiza inmediatamente en el mundo. Tarda tanto como el TTL más largo en los caches que lo tengan. Por eso siempre se dice "puede tardar hasta 24-48h en propagar".

---

## 8. Resolvers públicos famosos

| IP | Servicio | Notas |
|---|---|---|
| `8.8.8.8` | Google Public DNS | El más conocido |
| `8.8.4.4` | Google secundario | — |
| `1.1.1.1` | Cloudflare DNS | Privacy-focused, log retention 24h |
| `1.0.0.1` | Cloudflare secundario | — |
| `9.9.9.9` | Quad9 | Filtra dominios maliciosos por defecto |
| `208.67.222.222` | OpenDNS | Filtros parental control |
| ISP de tu casa | — | Suele ser por defecto, varía calidad |

**Para development/casa**: 1.1.1.1 (Cloudflare) suele ser el más rápido y respeta privacidad. 8.8.8.8 también muy rápido pero Google guarda logs.

**Configurar en tu PC**: `/etc/resolv.conf` en Linux/Mac. En Linux moderno está gestionado por systemd-resolved o NetworkManager.

---

## 9. DNS sobre HTTPS (DoH) y DNS sobre TLS (DoT)

DNS tradicional va **en plano** (UDP puerto 53, sin cifrar). Cualquiera en el camino (ISP, gobierno, hotel WiFi) puede ver QUÉ dominios visitas.

**DNS-over-HTTPS (DoH)**:
- Queries DNS encapsuladas en HTTPS.
- Puerto 443 (igual que web normal — indistinguible).
- Servidores: Cloudflare (`https://cloudflare-dns.com/dns-query`), Google (`https://dns.google/dns-query`).
- Usado por Firefox y Chrome modernos.

**DNS-over-TLS (DoT)**:
- Similar pero sobre TLS directo (puerto 853).
- Más común a nivel SO que browser.

**Por qué importa**:
- **Privacidad**: tu ISP no sabe qué dominios visitas.
- **Integridad**: no se pueden inyectar respuestas falsas en el camino.

**Contra**: centraliza confianza en pocos providers (Cloudflare, Google). Dificulta filtrado a nivel red (parental control, corporate firewall).

---

## 10. DNS y CDNs / load balancing geo

DNS es **fundamental** para CDNs y geo-routing.

**Caso 1 — CDN simple**: `user.com` queries → resolver → CDN devuelve IP del POP más cercano. Mismo nombre, distintas IPs según geo del cliente. Por ejemplo, user en España resuelve `cdn.example.com` → IP en Madrid; user en Tokio resuelve el mismo nombre → IP en Tokio.

**Caso 2 — Failover**: si datacenter principal cae, DNS authoritative cambia el A record a backup datacenter. TTL bajo (60s) acelera failover.

**Caso 3 — Round-robin DNS** (load balancing barato): `api.example.com → A: 10.0.0.1, A: 10.0.0.2, A: 10.0.0.3`. El resolver entrega los 3, el cliente prueba el primero (típicamente). Diferentes resolvers ven distinto orden → balanceo. Caveat: si un server cae, los clientes con esa IP cacheada fallan hasta que el TTL expire. Por eso load balancers L7 son mejores.

---

## 11. Aplicación al perfil del usuario

### En tu Phone Book FastAPI

Cuando tu CLI hace `requests.get("http://localhost:8000/")`, `localhost` no usa DNS público — se resuelve via `/etc/hosts` (mapping `127.0.0.1`). Si pusieras un dominio real (`http://api.miproyecto.com:8000/`), pasaría por el flujo completo.

### Cuando despliegues en cloud

Cuando hagas T1.4 (deploy a Fly.io o GCP), tendrás que:
1. Comprar un dominio (Namecheap, Cloudflare Registrar, ~10€/año).
2. Configurar DNS records (A → IP del cloud, o CNAME → fly.dev URL).
3. Esperar propagación (segundos a horas según TTL).
4. Configurar HTTPS (Let's Encrypt validará via DNS o HTTP).

### En interview

**Pregunta**: "¿qué pasa cuando escribes google.com?"

**Respuesta**: empieza con DNS resolution — tu PC pregunta al resolver configurado, que recursivamente pregunta a root, TLD .com, y authoritative de google.com hasta obtener la IP. Las respuestas se cachean según TTL. Después empieza el TCP three-way handshake a esa IP en puerto 443 (HTTPS), seguido del TLS handshake, y finalmente la HTTP request.



---

## 12. Trampas típicas

**"DNS es solo para resolver A records"**: no. Hay decenas de tipos (MX, TXT, CNAME, SRV, etc.). En interview, conocer 5-6 tipos te diferencia.

**"Cambiar el DNS se propaga al instante"**: no. Tarda hasta el TTL más largo cacheado en el mundo. Bajar TTL ANTES del cambio es buena práctica.

**"DNS usa TCP"**: por defecto UDP puerto 53 (más rápido, queries pequeñas). Cae a TCP cuando la respuesta es >512 bytes (poco común históricamente, más con DNSSEC y respuestas grandes). DoH usa TCP/443 (HTTPS). DoT usa TCP/853.

**"DNS es seguro"**: DNS plano NO está cifrado. Cualquiera en el camino ve tus queries. Las respuestas pueden ser falsificadas (DNS spoofing). Soluciones: DoH/DoT (cifra), DNSSEC (firma respuestas).

**"El TTL lo controla el cliente"**: no. Lo define el dueño del dominio en el record. Algunos clientes ignoran TTL muy bajos por seguridad/abuso.

**"CNAME apunta a una IP"**: no. CNAME apunta a OTRO NOMBRE. Tu PC tiene que hacer otro lookup para resolver ese nombre a IP. Un CNAME no puede ser el record raíz de un dominio (apex/root) — limitación técnica.

---

## 13. Cosas típicas que preguntan en interview

**"¿Qué pasa cuando escribes google.com?"** — ya cubierto arriba. Mencionar DNS, TCP, TLS, HTTP en orden.

**"Diferencia entre A y CNAME"** — A: nombre → IP directa. CNAME: nombre → otro nombre (alias). Requiere lookup adicional.

**"¿Cómo funciona un CDN?"** — DNS resuelve el nombre del CDN a la IP del POP más cercano (geo-DNS). El cliente conecta a ese POP. Si el contenido está cacheado, se sirve. Si no, el POP lo pide al origin y lo cachea.

**"¿Cómo harías un failover de servidor?"** — si es a nivel DNS: TTL bajo, monitorear servers, cambiar A record. Mejor: load balancer + health checks + IPs anycast (BGP). DNS failover tiene latencia del TTL.

**"¿Por qué hay 13 root servers?"** — por límite original del UDP packet (512 bytes con DNS). Cada uno es realmente cientos de máquinas con anycast. Hay 13 NOMBRES (a.root-servers.net hasta m.), no 13 máquinas.

---

## 14. Resumen mental — checklist

Dominas este doc si puedes explicar en menos de 2 minutos sin mirar:

- Por qué DNS existe y qué resuelve.
- La jerarquía: root → TLD → authoritative.
- Los flujos recursive vs iterative.
- El paso a paso completo de resolver google.com (8 pasos sección 4).
- Tipos de records: A, AAAA, CNAME, MX, TXT, NS (al menos 4).
- Qué es TTL y el tradeoff alto vs bajo.
- Caches DNS (browser, OS, resolver) y por qué propagación tarda.
- DoH/DoT y por qué importan.
- Cómo CDNs usan DNS para geo-routing.

Si no puedes → relee la sección.

---

## Conexiones

- [[01-tcp-ip-osi]] — DNS corre sobre UDP/TCP típicamente
- [[02-http-y-evolucion]] — DNS resuelve antes que HTTP empiece
- [[04-sockets-y-puertos]] — puerto 53 es DNS
- [[05-tls-https]] — TLS valida que conectas al server correcto (cert chain)
- [[../00_README]]
- [[../../../../30_MOCs/MOC_CS_Fundamentos]]
- — networking en Docker (DNS interno entre containers)

## Recursos externos

- **dig + nslookup** — herramientas CLI para inspeccionar DNS. `dig google.com` te muestra todo el flujo.
- **DNS for Rocket Scientists** (zytrax.com/books/dns/) — gratis online, denso pero completo.
- **Cloudflare Learning Center DNS** (cloudflare.com/learning/dns/) — buena introducción visual.
- **High Performance Browser Networking** (hpbn.co) — capítulo DNS.
- **`dnsperf`** — medir performance de resolvers.
