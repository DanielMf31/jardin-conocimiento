---
title: Redes en GCP
date: 2026-06-14
tags: [programacion/cloud, programacion/gcp, programacion/redes, programacion/seguridad]
type: nota
status: en-progreso
source: claude-code
aliases: [GCP Redes, VPC GCP, Cloud Networking GCP]
---

# Redes en GCP

## ¿Por qué importa esta capa?

En GCP (y en cualquier cloud), la red es la **columna vertebral invisible** de toda arquitectura. Decide:
- qué puede hablar con qué (segmentación y seguridad)
- cómo llega el tráfico de usuarios a tus servicios (load balancing, CDN)
- cómo salen tus VMs a internet sin IPs públicas (Cloud NAT)
- cómo conectas tu infraestructura on-premise con la nube (conectividad híbrida)

Antes de provisionar una sola VM o base de datos, defines la red. Es el mismo orden que en hardware: primero cablea la placa, luego enchufa los componentes.

> **Analogía técnico**: VPC = bus de comunicación interno de un sistema embebido. Las subredes = módulos separados del bus. Las firewall rules = filtros de dirección en protocolos como CAN bus.

---

## VPC y Subredes

### ¿Qué es una VPC?

**VPC (Virtual Private Cloud)** es una red privada virtual que vive dentro de tu proyecto GCP. Aísla tus recursos del resto del mundo y de otros proyectos. A diferencia de AWS, donde una VPC está limitada a una región, **en GCP una VPC es global por defecto**: puedes tener subredes en varias regiones bajo la misma VPC.

```
VPC (global, dentro de tu proyecto)
├── Subred us-central1     (10.0.0.0/24)
├── Subred europe-west1    (10.0.1.0/24)
└── Subred asia-east1      (10.0.2.0/24)
```

Las VMs en distintas regiones pero en la misma VPC se comunican por IP privada sin salir a internet — GCP usa su red troncal interna.

### Tipos de modo VPC

| Modo | Descripción | Cuándo usar |
|---|---|---|
| **Auto mode** | GCP crea automáticamente una subred por región (10.128.0.0/9) | Proyectos de prueba, aprendizaje rápido |
| **Custom mode** | Tú defines cada subred: CIDR, región, propósito | Producción, control total, evitar overlaps con on-prem |

> **Buena práctica**: usa siempre **custom mode** en entornos reales. El auto mode puede generar conflictos de CIDR con redes on-premise.

### Subredes (Subnets)

Una subred es un rango CIDR dentro de una región. Los recursos (VMs, GKE nodes, etc.) obtienen IPs del pool de esa subred.

```bash
# Crear VPC en modo custom
gcloud compute networks create mi-vpc \
  --subnet-mode=custom \
  --bgp-routing-mode=regional

# Crear subred en us-central1
gcloud compute networks subnets create subred-backend \
  --network=mi-vpc \
  --region=us-central1 \
  --range=10.0.1.0/24

# Listar subredes
gcloud compute networks subnets list --network=mi-vpc
```

**Conceptos clave de subredes:**
- **Primary range**: el CIDR principal para VMs
- **Secondary ranges**: rangos adicionales para pods y servicios de GKE (Kubernetes necesita esto)
- **Private Google Access**: permite que VMs sin IP pública accedan a APIs de GCP (Storage, BigQuery, etc.) sin salir a internet

---

## Firewall Rules

Las firewall rules en GCP son **stateful** (si permites entrada en un puerto, la respuesta de salida se permite automáticamente) y se aplican a nivel de **VPC**, no de subred ni de VM individual. Se dirigen a instancias mediante **network tags** o **service accounts**, lo cual es más flexible que los Security Groups de AWS.

### Estructura de una regla

```
Dirección (ingress/egress) + Prioridad (0-65535) + Acción (allow/deny)
+ Target (a qué VMs aplica: tag, SA, o todas)
+ Source/Dest (de dónde viene / adónde va)
+ Protocolo + Puerto
```

**Prioridad**: número más bajo = mayor prioridad. Default implícito: deny-all en ingress, allow-all en egress.

```bash
# Permitir SSH solo desde una IP de administración
gcloud compute firewall-rules create allow-ssh-admin \
  --network=mi-vpc \
  --direction=INGRESS \
  --priority=1000 \
  --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=203.0.113.5/32 \
  --target-tags=admin-access

# Permitir tráfico HTTP/HTTPS desde cualquier origen a VMs con tag 'web'
gcloud compute firewall-rules create allow-web \
  --network=mi-vpc \
  --direction=INGRESS \
  --priority=1000 \
  --action=ALLOW \
  --rules=tcp:80,tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=web-server

# Ver reglas de una red
gcloud compute firewall-rules list --filter="network=mi-vpc"
```

### Buenas prácticas de firewall

| Práctica | Por qué |
|---|---|
| Usa **network tags** para targets, no "all instances" | Principio de menor privilegio |
| Nunca abras `0.0.0.0/0` en SSH/RDP | Usa IAP (Identity-Aware Proxy) en su lugar |
| Habilita **Firewall Logs** en reglas críticas | Auditoría y detección de anomalías |
| Regla deny explícita con prioridad baja al final | Documenta la intención, aunque el default ya deniegue |

---

## Rutas (Routes)

Las rutas determinan cómo viaja el tráfico dentro y fuera de la VPC. GCP crea rutas automáticas:
- Ruta de **subred local** (dentro de la subred, sin gateway)
- Ruta de **internet** (0.0.0.0/0 → default internet gateway, solo si la VM tiene IP pública o Cloud NAT)

Puedes crear **rutas personalizadas** para dirigir tráfico a una instancia que actúe como appliance/NAT, o para forzar tráfico por una VPN.

```bash
# Ruta personalizada: tráfico a 192.168.0.0/16 pasa por una VM que actúa de router
gcloud compute routes create ruta-on-prem \
  --network=mi-vpc \
  --destination-range=192.168.0.0/16 \
  --next-hop-instance=vm-router \
  --next-hop-instance-zone=us-central1-a \
  --priority=100
```

---

## Cloud Load Balancing

### El problema que resuelve

Un solo servidor no aguanta tráfico variable. Un Load Balancer (LB) distribuye peticiones entre múltiples backends, detecta instancias caídas (health checks) y puede escalar el número de backends automáticamente.

### Taxonomía de load balancers en GCP

GCP tiene varios tipos. La clave es elegir el correcto según **tráfico** y **alcance**:

| Load Balancer | Capa OSI | Scope | Protocolo | Caso de uso típico |
|---|---|---|---|---|
| **Global HTTP(S) LB** | L7 | Global (Anycast) | HTTP/HTTPS, HTTP/2, gRPC | Web apps, APIs REST, necesitas routing por URL o cabeceras |
| **External TCP/UDP Network LB** | L4 | Regional | TCP/UDP | Servidores de juegos, flujos TCP propios, tráfico no-HTTP |
| **Internal HTTP(S) LB** | L7 | Regional | HTTP/HTTPS | Microservicios internos, service mesh entre backends |
| **Internal TCP/UDP LB** | L4 | Regional | TCP/UDP | Bases de datos internas, tráfico TCP privado |
| **SSL Proxy LB** | L4 | Global | SSL/TLS | Terminación TLS sin routing HTTP |

> **Equivalencia AWS**: Global HTTP(S) LB ≈ ALB global. External TCP/UDP ≈ NLB. Internal LB ≈ ALB/NLB internal.

### Global HTTP(S) Load Balancer — el más común

Funciona con **Anycast**: una sola IP global enruta al PoP de GCP más cercano al usuario. Integra:
- **SSL termination** (gestiona certificados, incluso Google-managed certs gratuitos)
- **URL map**: enruta `/api/*` a un backend, `/static/*` a otro (o a Cloud CDN)
- **Cloud Armor** para WAF y protección DDoS
- **Health checks** automáticos

```bash
# Esquema básico (simplificado): backend → backend service → url map → target proxy → forwarding rule

# 1. Crear health check
gcloud compute health-checks create http hc-web \
  --port=80 \
  --request-path=/health

# 2. Backend service (apunta a un instance group)
gcloud compute backend-services create bs-web \
  --protocol=HTTP \
  --health-checks=hc-web \
  --global

gcloud compute backend-services add-backend bs-web \
  --instance-group=mig-web \
  --instance-group-zone=us-central1-a \
  --global

# 3. URL map
gcloud compute url-maps create urlmap-web \
  --default-service=bs-web

# 4. Target HTTP proxy
gcloud compute target-http-proxies create proxy-web \
  --url-map=urlmap-web

# 5. Forwarding rule (la IP global)
gcloud compute forwarding-rules create fr-web \
  --global \
  --target-http-proxy=proxy-web \
  --ports=80
```

---

## Cloud DNS

**Cloud DNS** es el servicio DNS gestionado de GCP. Funciona como Route 53 de AWS. Puedes usarlo para:
- **DNS público**: resolver tu dominio `tuapp.com` desde internet
- **DNS privado**: zonas privadas visibles solo dentro de tu VPC (ideal para nombres internos de servicios)

```bash
# Crear zona DNS pública
gcloud dns managed-zones create zona-web \
  --dns-name=tuapp.com. \
  --description="Zona pública de tuapp.com" \
  --visibility=public

# Crear registro A
gcloud dns record-sets create tuapp.com. \
  --zone=zona-web \
  --type=A \
  --ttl=300 \
  --rrdatas=34.120.1.1

# Zona privada (solo visible dentro de la VPC)
gcloud dns managed-zones create zona-interna \
  --dns-name=interno.corp. \
  --visibility=private \
  --networks=mi-vpc
```

**DNS peering**: permite que una VPC resuelva zonas DNS de otra VPC. Útil en arquitecturas hub-and-spoke.

---

## Cloud CDN

**Cloud CDN** (Content Delivery Network) cachea contenido en los PoPs (puntos de presencia) de Google en todo el mundo. Se integra directamente con el **Global HTTP(S) Load Balancer** — lo activas como una opción del backend service, no es un servicio separado.

**Qué cachea**: respuestas con cabeceras `Cache-Control: public` y métodos GET/HEAD. Archivos estáticos (JS, CSS, imágenes), respuestas de APIs que no cambien frecuentemente.

```bash
# Activar CDN en un backend service existente
gcloud compute backend-services update bs-web \
  --enable-cdn \
  --global

# Invalidar caché (cuando actualizas el contenido)
gcloud compute url-maps invalidate-cdn-cache urlmap-web \
  --path="/static/*" \
  --global
```

**Cache keys**: por defecto incluyen host, protocolo y URL. Puedes customizarlas para excluir query params irrelevantes o incluir cabeceras específicas.

| Situación | Recomendación CDN |
|---|---|
| Assets estáticos con versioning (`app.v2.js`) | CDN con TTL largo (1 año) |
| HTML dinámico | No usar CDN o TTL muy corto |
| APIs con respuestas compartidas entre usuarios | CDN con cache key sin cookies |
| Contenido por usuario (autenticado) | No cachear o Signed URLs |

---

## Cloud NAT

**El problema**: las VMs en subredes privadas (sin IP pública) no pueden salir a internet para descargar paquetes, llamar APIs externas, etc. Tampoco queremos exponerlas con IP pública.

**Cloud NAT** (Network Address Translation) resuelve esto: actúa como gateway de salida para VMs sin IP pública, traduciendo su IP privada a una IP pública compartida. Es **totalmente gestionado** (no hay VM gateway que mantener) y **no permite conexiones entrantes** desde internet (solo salida iniciada desde dentro).

```bash
# Necesita un Cloud Router primero
gcloud compute routers create router-nat \
  --network=mi-vpc \
  --region=us-central1

# Crear Cloud NAT
gcloud compute routers nats create nat-gateway \
  --router=router-nat \
  --region=us-central1 \
  --auto-allocate-nat-external-ips \
  --nat-all-subnet-ip-ranges
```

**Cloud Router** es el componente que gestiona las rutas dinámicas (BGP). Es necesario tanto para Cloud NAT como para Cloud VPN y Interconnect.

---

## Conectividad Híbrida

Cuando necesitas conectar tu red on-premise (datacenter, oficina, hardware físico) con tu VPC en GCP.

### VPC Peering

Conecta **dos VPCs de GCP** (pueden estar en proyectos distintos) a nivel de red privada. No pasa por internet. No comparte rutas transitivas (A↔B y B↔C no implica A↔C).

```bash
# En el proyecto A
gcloud compute networks peerings create peering-a-b \
  --network=vpc-a \
  --peer-project=proyecto-b \
  --peer-network=vpc-b

# En el proyecto B (debe hacerse desde ambos lados)
gcloud compute networks peerings create peering-b-a \
  --network=vpc-b \
  --peer-project=proyecto-a \
  --peer-network=vpc-a
```

**Limitación importante**: los CIDRs de las dos VPCs no pueden solaparse. Planifica el direccionamiento IP antes de hacer peering.

### Cloud VPN

Túnel IPSec cifrado entre tu red on-premise y tu VPC. Pasa por internet público pero cifrado. Adecuado para cargas de trabajo no críticas en latencia o como backup de Interconnect.

| Tipo VPN | Descripción | SLA |
|---|---|---|
| **Classic VPN** | Un túnel, gateway estático | 99.9% |
| **HA VPN** | Dos túneles redundantes, BGP dinámico | 99.99% |

```bash
# Crear HA VPN gateway
gcloud compute vpn-gateways create vpn-gw-ha \
  --network=mi-vpc \
  --region=us-central1

# Crear Cloud Router para BGP
gcloud compute routers create router-vpn \
  --network=mi-vpc \
  --region=us-central1 \
  --asn=65001

# (Luego configuras los tunnels y sesiones BGP con los parámetros del lado on-prem)
```

### Cloud Interconnect

Conexión física dedicada entre tu datacenter y la red de Google. No pasa por internet. Menor latencia y mayor ancho de banda que VPN.

| Tipo | Ancho de banda | Cuándo usar |
|---|---|---|
| **Dedicated Interconnect** | 10 Gbps o 100 Gbps por circuito | Datacenter propio co-ubicado con PoP de Google |
| **Partner Interconnect** | 50 Mbps a 50 Gbps | Usas un ISP partner de Google; más flexible geográficamente |
| **Cross-Cloud Interconnect** | 10 o 100 Gbps | Conectar GCP con AWS/Azure directamente |

Interconnect es costoso (se paga por puerto + tráfico). Justificado si mueves terabytes/día o necesitas latencia predecible para workloads críticos.

### Tabla de decisión: ¿qué conectividad usar?

| Necesidad | Solución |
|---|---|
| Conectar dos VPCs en GCP (mismo o distinto proyecto) | VPC Peering |
| On-prem → GCP, tráfico moderado, presupuesto limitado | Cloud VPN HA |
| On-prem → GCP, alta disponibilidad, gran volumen | Dedicated/Partner Interconnect |
| Múltiples VPCs con conectividad centralizada y transitiva | Shared VPC o NCC (Network Connectivity Center) |
| GCP ↔ AWS/Azure directamente | Cross-Cloud Interconnect |

---

## Cómo se conecta una arquitectura típica

Ejemplo: aplicación web con backend y base de datos.

```
Internet
    │
    ▼
[Cloud Armor WAF]
    │
    ▼
[Global HTTP(S) Load Balancer]  ← IP Anycast global
    │              │
    ▼              ▼
[MIG Web]      [Cloud CDN]  ← assets estáticos
(tag: web)
    │
    ▼ (IP privada, misma VPC)
[MIG Backend]
(tag: backend)
    │
    ▼ (IP privada)
[Cloud SQL / Memorystore]
(sin IP pública)

Firewall rules:
- allow-web:     0.0.0.0/0 → tag:web → tcp:443
- allow-backend: tag:web → tag:backend → tcp:8080
- allow-db:      tag:backend → tag:db → tcp:5432
- deny-all:      resto → DROP

Cloud NAT:
- tag:backend y tag:db salen a internet para updates/APIs
  sin IP pública expuesta
```

---

## Errores y costes comunes

| Error | Consecuencia | Prevención |
|---|---|---|
| CIDRs solapados entre VPCs o con on-prem | Peering/VPN falla o enruta mal | Planifica el espacio IP desde el inicio; documenta en un registro |
| Firewall rule `0.0.0.0/0` en SSH | Escaneos, ataques brute-force | Usa IAP Tunneling (`gcloud compute ssh` sin IP pública) |
| No activar Private Google Access en subredes privadas | VMs sin IP pública no alcanzan APIs GCP | Activarlo al crear la subred |
| CDN sin invalidación al desplegar | Usuarios ven contenido antiguo | Automatiza `invalidate-cdn-cache` en el pipeline CI/CD |
| Classic VPN en lugar de HA VPN | Downtime durante mantenimiento Google | Usa siempre HA VPN en producción |
| Egress entre regiones o hacia internet | Costes sorpresa en la factura | Revisa el pricing de egress; Cloud NAT también tiene coste por GB procesado |

**Free tier relevante**:
- Cloud VPN: 1 túnel VPN gratis los primeros 12 meses (nivel prueba)
- Egress: 1 GB/mes gratuito hacia internet desde todas las regiones
- Cloud DNS: primeras 1.000 millones de consultas/mes a $0.40 (no es gratis, pero barato)

---

## Aplícalo / Práctica

1. **Lab básico VPC**: crea una VPC custom con dos subredes en regiones distintas. Lanza una VM en cada subred. Verifica que se pingen por IP privada sin abrir puertos a internet (usa IAP para SSH).

2. **Firewall con tags**: crea tres VMs (`web`, `backend`, `db`) con network tags. Configura reglas de firewall para que solo `web` reciba tráfico externo, `web→backend` y `backend→db` sean los únicos flujos permitidos internamente.

3. **Cloud NAT**: en la subred de `db`, elimina la IP pública de la VM. Configura Cloud NAT y verifica que puede hacer `curl https://example.com` sin IP pública.

4. **Load Balancer HTTP(S)**: monta un Managed Instance Group con 2 VMs nginx. Ponle un Global HTTP(S) LB delante. Verifica que si matas una VM, el tráfico sigue fluyendo.

5. **VPC Peering**: crea dos proyectos GCP (o dos VPCs en el mismo proyecto), haz peering, y verifica conectividad privada entre VMs de distintas VPCs.

---

## Conexiones

- [[MOC_GCP]]
- [[01-fundamentos-cloud-y-gcp]]
- [[02-iam-y-seguridad]]
- [[03-computo]]
- [[05-almacenamiento]]
- [[06-bases-de-datos]]
- [[08-contenedores-y-serverless]]
- [[09-devops-iac-observabilidad]]
- [[11-costes-y-buenas-practicas]]
- [[MOC_Ciberseguridad]]
- [[MOC_Desarrollo_Software]]
