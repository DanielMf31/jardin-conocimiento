---
title: Seguridad de redes
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, redes/tcp-ip, redes/firewall, redes/vpn, redes/ids]
type: nota
status: en-progreso
source: claude-code
aliases: [network security, seguridad red, redes seguras]
---

# Seguridad de redes

## ¿Por qué existe este documento?

La red es el **campo de batalla primario** de la ciberseguridad. Casi todo ataque —desde robo de credenciales hasta ransomware— atraviesa una red en algún momento: el adversario necesita llegar, moverse lateralmente o exfiltrar datos. Entender cómo funciona TCP/IP a bajo nivel te da el poder de ver exactamente qué ocurre, dónde falla y cómo cerrarlo.

Este documento responde tres preguntas:
1. ¿Cómo está organizada y cómo funciona la red que defiendes?
2. ¿Cómo la atacan?
3. ¿Cómo la proteges?

Todo lo relativo a escaneo de red, sniffing y análisis de tráfico se enmarca en **entornos autorizados** (tu lab, CTFs, red propia). Usar estas técnicas en redes ajenas sin permiso explícito es ilegal en prácticamente todas las jurisdicciones.

---

## 1. Repaso TCP/IP y puertos — el mapa del territorio

### El modelo en capas (TCP/IP de 4 capas)

```
┌─────────────────────────────────────┐
│  Aplicación  (HTTP, DNS, SSH, FTP)  │  ← donde viven los servicios
├─────────────────────────────────────┤
│  Transporte  (TCP / UDP)            │  ← puertos, fiabilidad
├─────────────────────────────────────┤
│  Internet    (IP, ICMP, ARP)        │  ← direccionamiento, enrutamiento
├─────────────────────────────────────┤
│  Acceso red  (Ethernet, Wi-Fi)      │  ← MACs, tramas físicas
└─────────────────────────────────────┘
```

Cada capa añade una cabecera (**encapsulación**). Cuando capturas tráfico con Wireshark, ves estas capas desencapsuladas una a una.

### TCP vs UDP — diferencia clave en seguridad

| Propiedad | TCP | UDP |
|---|---|---|
| Conexión | Orientado a conexión (handshake 3-way) | Sin conexión |
| Fiabilidad | Retransmite paquetes perdidos | Fire-and-forget |
| Uso típico | HTTP/S, SSH, FTP, bases de datos | DNS, VoIP, streaming, VPNs modernas |
| Superficie de ataque | SYN flood, session hijacking | UDP flood, DNS spoofing |

**El handshake TCP de 3 pasos** (SYN → SYN-ACK → ACK) es importante porque:
- Establece el estado de la conexión en ambos extremos.
- Los ataques de **SYN flood** mandan miles de SYN sin completar el ACK, agotando la tabla de estados del servidor (denegación de servicio).

### Puertos y servicios — a qué le disparas

Un puerto (0–65535) identifica el **servicio** dentro de un host. Los más relevantes en seguridad:

| Puerto | Protocolo | Servicio | Riesgo común |
|---|---|---|---|
| 21 | TCP | FTP | Credenciales en claro, anonymous login |
| 22 | TCP | SSH | Fuerza bruta, claves débiles |
| 23 | TCP | Telnet | Todo en claro, obsoleto |
| 25 | TCP | SMTP | Open relay, spam, phishing |
| 53 | UDP/TCP | DNS | Spoofing, amplificación DDoS |
| 80/443 | TCP | HTTP/HTTPS | Ataques web (ver [[04-seguridad-web-owasp]]) |
| 445 | TCP | SMB | EternalBlue, ransomware lateral |
| 3306 | TCP | MySQL | Exposición directa a internet |
| 3389 | TCP | RDP | Fuerza bruta, BlueKeep |

**Regla práctica**: si un puerto está abierto en internet y no hay razón de negocio clara para ello, es superficie de ataque innecesaria. Ciérralo.

---

## 2. Firewalls, NAT y segmentación

### Firewall — el portero

Un **firewall** filtra tráfico según reglas (ACLs — Access Control Lists). Tipos:

| Tipo | Qué inspecciona | Ejemplo |
|---|---|---|
| Packet filter (stateless) | Cabeceras IP/TCP/UDP aisladas | iptables básico |
| Stateful inspection | Estado de la conexión completa | nftables, pfSense |
| Application-layer (L7) | Contenido del protocolo (HTTP, DNS) | Palo Alto, Nginx WAF |
| NGFW (Next-Gen) | IDS/IPS integrado, usuario, aplicación | Fortinet, Checkpoint |

**Política por defecto**: siempre **deny-all**, luego abres solo lo necesario. Hacer lo contrario (allow-all y cerrar lo malo) es un error clásico — no sabes lo que no sabes.

```
# Ejemplo conceptual iptables (Linux)
# Rechaza todo por defecto:
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Permite SSH desde red interna:
iptables -A INPUT -s 192.168.1.0/24 -p tcp --dport 22 -m state --state NEW,ESTABLISHED -j ACCEPT
```

### NAT — Network Address Translation

NAT traduce direcciones IP privadas (192.168.x.x, 10.x.x.x, 172.16–31.x.x) a una IP pública. Esto tiene un efecto **secundario** de seguridad: los hosts internos no son directamente alcanzables desde internet (el router descarta paquetes entrantes sin estado previo).

NAT **no es un firewall** — es una consecuencia del agotamiento de IPv4. No confíes en él como única defensa.

### Segmentación y VLANs

**VLAN** (Virtual LAN): divide una red física en redes lógicas separadas a nivel L2 (switch). El tráfico entre VLANs pasa por un router/firewall, donde se pueden aplicar reglas.

```
           ┌──────────────────────────────────────┐
           │             Switch gestionado        │
           │   VLAN 10 (Servidores)  [192.168.10.x]│
           │   VLAN 20 (Usuarios)    [192.168.20.x]│
           │   VLAN 30 (IoT/CCTV)   [192.168.30.x]│
           └──────────────┬───────────────────────┘
                          │ tráfico inter-VLAN
                     [Firewall/Router]
```

**Por qué importa**: si un atacante compromete un dispositivo IoT en VLAN 30, la segmentación impide que acceda directamente a los servidores en VLAN 10. Sin segmentación, un movimiento lateral es trivial.

**DMZ** (Demilitarized Zone): segmento intermedio donde viven los servidores expuestos a internet (web, correo). Separado de la LAN interna con un firewall que filtra en ambas direcciones.

```
Internet ──→ [FW externo] ──→ DMZ (web, mail) ──→ [FW interno] ──→ LAN interna
```

---

## 3. VPN — túneles seguros sobre redes no confiables

**VPN** (Virtual Private Network): crea un canal cifrado sobre una red pública (internet) para que el tráfico viaje protegido.

### Tipos y protocolos

| Protocolo | Capa | Fortaleza | Uso |
|---|---|---|---|
| OpenVPN | L3/L4 | Alta (TLS) | Site-to-site, remote access |
| WireGuard | L3 | Muy alta (ChaCha20) | Moderno, bajo latencia |
| IPSec/IKEv2 | L3 | Alta | Dispositivos móviles, site-to-site |
| L2TP/IPSec | L2+L3 | Media | Legacy, routers corporativos |
| PPTP | L2 | **No usar** — roto desde 2012 | — |

### VPN site-to-site vs remote access

- **Site-to-site**: une dos redes (ej. oficina Madrid ↔ oficina Barcelona). Transparente para los usuarios.
- **Remote access**: el usuario conecta su equipo a la red corporativa desde fuera (teletrabajo).

### Split tunneling — riesgo a conocer

**Split tunneling**: solo el tráfico corporativo va por el túnel VPN; el resto sale directo a internet. Cómodo (menos latencia), pero si el equipo del usuario está comprometido, el atacante tiene acceso a ambas redes.

**Prevención**: política VPN con full-tunnel para usuarios con acceso a sistemas críticos; o Zero Trust Network Access (ZTNA) como evolución moderna.

---

## 4. DNS y sus amenazas

### ¿Qué es DNS y por qué es crítico?

DNS (Domain Name System) traduce nombres (`api.empresa.com`) a IPs. Es la "guía telefónica" de internet. **Es fundamental y frecuentemente mal protegido.**

### DNS Spoofing / Cache Poisoning

**Cómo funciona el ataque**: el atacante inyecta respuestas DNS falsas en la caché de un resolver. El usuario escribe `banco.com` y el DNS le devuelve la IP del atacante → phishing/MITM.

```
Usuario → [Resolver comprometido] → IP falsa (servidor atacante)
                                    ↑
                         respuesta falsificada inyectada
```

**Prevención:**
- **DNSSEC** (DNS Security Extensions): firma criptográfica de registros DNS. El resolver verifica la firma antes de aceptar la respuesta.
- Usar resolvers modernos con DoH (DNS over HTTPS) o DoT (DNS over TLS): el tráfico DNS va cifrado, impidiendo que un intermediario lo manipule.
- Servidores DNS internos con validación DNSSEC.

### DNS como canal de ataque

- **DNS amplification DDoS**: el atacante manda queries UDP pequeñas con IP origen falsa (de la víctima), el resolver responde con paquetes mucho más grandes → amplificación del ataque.
- **DNS tunneling**: datos exfiltrados o comandos C2 codificados en subdominios DNS. Difícil de detectar porque DNS normalmente pasa firewalls.

---

## 5. Sniffing de red y ataques MITM

### Sniffing — capturar tráfico en la red

Un **sniffer** pone la interfaz de red en **modo promiscuo** (escucha todos los paquetes, no solo los dirigidos a ella). En redes Wi-Fi o con hubs, cualquier host puede ver el tráfico de todos.

**Wireshark** es la herramienta estándar (GUI, gratuita, multiplataforma). `tcpdump` es su equivalente CLI.

Casos de uso legítimos:
- Diagnóstico de red en tu propia infraestructura.
- Análisis de malware en sandbox.
- CTFs y laboratorios.
- Desarrollo y depuración de protocolos.

En redes conmutadas (switches modernos), el switch aísla los dominios de colisión — normalmente solo ves tu propio tráfico. Para capturar más, necesitas: port mirroring (SPAN port configurado por el administrador), o estar en posición MITM.

### MITM — Man-in-the-Middle

El atacante se **interpone** entre dos partes que creen comunicarse directamente:

```
[Víctima] ──→ [Atacante] ──→ [Servidor legítimo]
              ↑ ve y puede modificar todo
```

**Técnicas para llegar a posición MITM:**

| Técnica | Cómo | Capa |
|---|---|---|
| ARP Spoofing/Poisoning | Envía respuestas ARP falsas → víctima asocia la MAC del atacante con la IP del gateway | L2 |
| Rogue AP | Crea un punto de acceso Wi-Fi falso con el mismo SSID | L1/L2 |
| DNS Spoofing | (ver sección anterior) | L7 |
| BGP hijacking | Anuncia prefijos IP ajenos en BGP (nivel ISP) | L3 |

**ARP Spoofing en detalle:**
ARP (Address Resolution Protocol) traduce IPs a MACs en la LAN. No tiene autenticación — cualquier host puede responder a cualquier ARP request. El atacante manda respuestas ARP no solicitadas ("gratuitous ARP") envenenando la caché de la víctima.

**Prevención de MITM:**
- **TLS/HTTPS en todo** (cifrado extremo a extremo — el intermediario ve datos cifrados, no útiles).
- **Certificate Pinning** en apps móviles/críticas.
- **Dynamic ARP Inspection (DAI)** en switches gestionados: valida que las respuestas ARP correspondan a la tabla DHCP.
- **802.1X** (autenticación de puerto): solo dispositivos autenticados pueden conectarse a la red.
- Segmentación de red (reduce el radio de acción del MITM a una VLAN).
- Monitorizar cambios en tablas ARP.

---

## 6. Escaneo de red con nmap (contexto autorizado)

### ¿Qué es nmap y qué hace?

**nmap** (Network Mapper) es la herramienta estándar de descubrimiento de red y auditoría de puertos. En pentesting autorizado y administración de sistemas es esencial.

**IMPORTANTE LEGAL Y ÉTICO**: nmap solo en redes que administras, con permiso escrito explícito, o en entornos de laboratorio/CTF. Escanear redes ajenas sin permiso es delito en la mayoría de países (España: art. 197 bis CP, EE.UU.: CFAA).

### Tipos de escaneo — qué hace cada uno

| Tipo | Flag | Mecanismo | Cuándo usarlo |
|---|---|---|---|
| Ping sweep (host discovery) | `-sn` | ICMP echo + TCP/ARP | Ver qué hosts están activos |
| TCP SYN scan (stealth) | `-sS` | Envía SYN, espera SYN-ACK, manda RST (no completa handshake) | Estándar; menos logs en el destino |
| TCP Connect scan | `-sT` | Completa el handshake de 3 pasos | Cuando no tienes root; más detectable |
| UDP scan | `-sU` | Sonda puertos UDP | Servicios DNS, SNMP, TFTP |
| OS detection | `-O` | Analiza TTL, TCP window size, opciones | Fingerprinting del SO |
| Version detection | `-sV` | Envía probes para identificar servicio y versión | Detectar servicios desactualizados |
| Script scan | `-sC` o `--script` | Ejecuta NSE scripts (Nmap Scripting Engine) | Detección de vulns básicas, enum |
| Aggressive | `-A` | Combina -O -sV -sC + traceroute | Auditoría completa (ruidoso) |

```bash
# Descubrir hosts activos en tu red:
nmap -sn 192.168.1.0/24

# Escaneo básico de un host (tus propios servidores):
nmap -sS -sV -p 1-1000 192.168.1.10

# Escaneo completo autorizado con detección de OS y scripts:
nmap -A -p- 192.168.1.10

# Solo ver puertos TCP más comunes + versiones:
nmap -sV --top-ports 100 192.168.1.10
```

### Cómo leer la salida

```
PORT     STATE    SERVICE    VERSION
22/tcp   open     ssh        OpenSSH 8.2p1 Ubuntu
80/tcp   open     http       nginx 1.18.0
443/tcp  open     ssl/https
3306/tcp filtered mysql
8080/tcp closed   http-alt
```

- **open**: servicio escuchando y accesible.
- **closed**: puerto responde (host activo), pero sin servicio.
- **filtered**: firewall está bloqueando/descartando — no hay respuesta.

**Lo que busca un defensor con nmap**: ¿hay puertos abiertos que no deberían estar? ¿versiones desactualizadas? Escanea tu propia infraestructura periódicamente antes de que lo haga alguien con malas intenciones.

---

## 7. IDS e IPS — detectar y bloquear intrusiones

### Definiciones

- **IDS** (Intrusion Detection System): **detecta** y **alerta** sobre actividad sospechosa. Pasivo — no bloquea.
- **IPS** (Intrusion Prevention System): detecta **y bloquea** en tiempo real. Activo — está en línea con el tráfico.

### Tipos por posición

| Tipo | Dónde vive | Qué ve |
|---|---|---|
| NIDS/NIPS | En la red (tap o SPAN port) | Tráfico de red en tránsito |
| HIDS/HIPS | En el host (agente) | Procesos, archivos, syscalls del host |

### Métodos de detección

| Método | Cómo funciona | Ventaja | Limitación |
|---|---|---|---|
| Basado en firmas | Compara tráfico contra patrones conocidos (como antivirus) | Rápido, bajo FP para amenazas conocidas | Ciega ante ataques 0-day o variantes nuevas |
| Basado en anomalías | Aprende el baseline normal; alerta cuando algo se desvía | Puede detectar amenazas desconocidas | Alto false positive rate al inicio |
| Basado en reglas/heurística | Reglas lógicas (si X ocurre Y veces en Z segundos → alerta) | Flexible, comprensible | Requiere mantenimiento manual |

### Herramientas open source

- **Snort**: IDS/IPS basado en firmas, ampliamente usado, reglas de la comunidad Snort/ET.
- **Suricata**: alternativa moderna a Snort, multihilo, soporte de reglas Snort + YAML.
- **Zeek** (antes Bro): más orientado a análisis de comportamiento y generación de logs estructurados.
- **OSSEC / Wazuh**: HIDS con agentes en hosts; Wazuh añade SIEM integrado.

### Evasión de IDS — entender para defender

Saber cómo los atacantes evaden IDS ayuda a configurarlos mejor:
- **Fragmentación IP**: el atacante divide el payload en fragmentos pequeños esperando que el IDS no los reensemble.
- **Cifrado**: tráfico TLS es opaco para IDS de red (solución: TLS inspection en el firewall/IPS).
- **Polimorfismo de payloads**: modificar el exploit para que no coincida con la firma.
- **Timing lento**: el escaneo muy lento puede no superar umbrales de alerta.

---

## 8. Cómo se defiende una red — visión global

### Defensa en profundidad (Defense in Depth)

Nunca dependas de una sola capa. Si el firewall falla, debe haber otra barrera. Modelo de capas:

```
Internet
   │
[Firewall perimetral + IPS]
   │
  DMZ
   │
[Firewall interno]
   │
LAN segmentada en VLANs
   │
[IDS de red (NIDS)]   [HIDS en cada servidor]
   │
Hosts endurecidos (ver [[06-seguridad-de-sistemas-y-hardening]])
```

### Lista de control para defender una red

- [ ] **Inventario**: saber qué hay en la red (nmap periódico autorizado, CMDB).
- [ ] **Segmentación**: VLANs por función (servidores, usuarios, IoT, invitados, gestión).
- [ ] **Firewall con política deny-all**: solo los puertos necesarios, en la dirección necesaria.
- [ ] **Parcheo**: versiones de servicios actualizadas (nmap -sV te muestra versiones expuestas).
- [ ] **VPN para acceso remoto**: no exponer RDP/SSH directamente a internet.
- [ ] **DNSSEC + DoH/DoT**: resolver DNS seguro.
- [ ] **DAI + DHCP Snooping** en switches gestionados para prevenir ARP spoofing.
- [ ] **802.1X** o NAC (Network Access Control) para controlar qué endpoints se conectan.
- [ ] **IDS/IPS**: alertas sobre escaneos, exploits conocidos, comportamientos anómalos.
- [ ] **Logs centralizados y SIEM**: correlacionar eventos (ver [[10-blue-team-y-respuesta-incidentes]]).
- [ ] **Cifrado en tránsito**: TLS en todo, no solo en la web pública.
- [ ] **Zero Trust**: no confiar en nada por estar dentro de la red; autenticar y autorizar cada acceso.

### Errores comunes

| Error | Consecuencia | Corrección |
|---|---|---|
| Firewall con política allow-all + blacklist | Atacante usa un puerto que no bloqueaste | Invertir: deny-all + whitelist |
| DMZ inexistente | Servidor web comprometido → acceso directo a LAN | Implementar DMZ |
| Telnet/FTP abiertos | Credenciales en claro capturables con Wireshark | Sustituir por SSH/SFTP |
| VLAN sin firewall entre ellas | Movimiento lateral libre | Routing inter-VLAN a través de firewall |
| IDS pero sin monitorización | Alertas que nadie lee | SOC o al menos alertas a correo/Slack |
| VPN con split-tunnel sin control | Endpoint infectado como pivote | Full-tunnel o ZTNA |
| DNS público interno | DNS spoofing, exfiltración por DNS | Resolver interno + validación + DoT |

---

## Aplícalo / practica

### En tu laboratorio (VMs)

1. **Montar una red segmentada con VLANs**: usa VirtualBox o VMware con varias VMs y configura un firewall pfSense entre segmentos.
2. **Captura con Wireshark**: captura el handshake TCP de una conexión HTTP (sin TLS). Observa la diferencia con HTTPS — solo ves datos cifrados.
3. **ARP Spoofing en lab**: en una red de VMs aislada, usa `arpspoof` (paquete dsniff en Linux) para interceptar tráfico entre dos VMs. Luego activa DAI en el switch virtual y comprueba que ya no funciona.
4. **nmap en tu red doméstica**: escanea tu propio router y los dispositivos de tu red. ¿Qué puertos ves? ¿Hay servicios inesperados?
5. **Snort/Suricata en Kali/Ubuntu**: instala Suricata en modo IDS (no inline) con reglas ET Open. Genera tráfico de prueba y revisa las alertas.

### CTFs y plataformas

- **TryHackMe**: salas "Pre-Security", "Network Fundamentals", "Wireshark 101", "Nmap", "Firewall" — todas con labs interactivos en el navegador.
- **HackTheBox Starting Point**: máquinas que incluyen enumeración de red.
- **PicoCTF**: categoría "forensics" tiene retos de análisis de pcap con Wireshark.
- **Vulnhub**: VMs descargables para practicar escaneo y explotación en tu lab.

### En tus propios proyectos (app web, etc.)

- Revisa que ningún puerto de base de datos (3306 MongoDB, Redis 6379) esté expuesto fuera de la red Docker interna.
- En `docker-compose.yml`, no mapear puertos internos al host a menos que sea necesario (`127.0.0.1:3306:3306` mejor que `0.0.0.0:3306:3306`).
- Usa redes Docker separadas por servicio (ver [[09-devsecops-y-appsec]]).

---

## Conexiones

- [[MOC_Ciberseguridad]]
- [[MOC_CS_Fundamentos]]
- [[01-fundamentos-y-mentalidad]]
- [[02-criptografia]]
- [[04-seguridad-web-owasp]]
- [[05-identidad-auth-y-secretos]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[07-pentesting-y-ciclo-del-ataque]]
- [[09-devsecops-y-appsec]]
- [[10-blue-team-y-respuesta-incidentes]]
