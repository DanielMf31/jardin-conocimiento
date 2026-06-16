---
title: Blue Team y Respuesta a Incidentes
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, ciberseguridad/blue-team, ciberseguridad/soc, ciberseguridad/forense, ciberseguridad/incident-response]
type: nota
status: en-progreso
source: claude-code
aliases: [blue team, respuesta incidentes, IR, SOC]
---

# 🛡️ Blue Team y Respuesta a Incidentes

## ¿Por qué existe esto?

Toda arquitectura de seguridad asume que **los atacantes eventualmente entran**. La pregunta no es "¿me van a atacar?" sino "¿cuánto tardaré en darme cuenta, y qué haré?".

El **Blue Team** es la función defensiva: los que monitorizan, detectan, contienen y aprenden de los incidentes. Es el contrapeso del [[07-pentesting-y-ciclo-del-ataque|Red Team]]. Sin Blue Team, los controles de seguridad son ciegos — no sabes si funcionan hasta que algo falla.

Desde la óptica de un desarrollador/ingeniero: entender Blue Team te hace escribir mejor logging, mejores alertas, y aplicaciones más recuperables. No es solo "trabajo del equipo de seguridad".

---

## 🗺️ Panorama: los tres colores

| Equipo | Rol | Mentalidad |
|---|---|---|
| **Red Team** | Ataca (autorizado) para encontrar fallos | Ofensiva — "¿cómo entro?" |
| **Blue Team** | Defiende, monitoriza, responde | Defensiva — "¿qué pasa en mi red?" |
| **Purple Team** | Red + Blue trabajando juntos | Colaborativa — "validamos defensas en tiempo real" |

El **Purple Team** no es un equipo separado sino un modo de operar: el Red Team ataca y el Blue Team observa si sus alertas se disparan. Es la forma más eficiente de mejorar defensas porque cierra el loop inmediatamente.

---

## 🏢 SOC — Security Operations Center

El SOC (Centro de Operaciones de Seguridad) es la "sala de control" defensiva. Puede ser interno, externalizado (MSSP — Managed Security Service Provider) o híbrido.

**Funciones principales:**
- Monitorización 24/7 de alertas y logs
- Triage (clasificación) de eventos: ¿es un falso positivo o un incidente real?
- Escalado y coordinación de respuesta
- Gestión de vulnerabilidades y threat intelligence

**Niveles de analista típicos:**
```
L1 — Triage inicial, filtra ruido, escala lo sospechoso
L2 — Investigación profunda, confirma incidentes
L3 — Threat hunting proactivo, casos complejos, forense
```

Sin un SOC, los logs se generan y nadie los lee — una situación muy común en organizaciones pequeñas y uno de los motivos por los que los atacantes pasan semanas dentro sin ser detectados.

---

## 📊 SIEM — Centralizar y Correlacionar Logs

**SIEM** (Security Information and Event Management) es la tecnología central del Blue Team. Hace dos cosas:

1. **SIM** (Security Information Management): centraliza y almacena logs de todas las fuentes
2. **SEM** (Security Event Management): correlaciona eventos en tiempo real para generar alertas

### ¿Por qué centralizar?

Sin SIEM, para investigar un ataque tendrías que ir máquina por máquina leyendo logs locales. Un atacante puede borrar logs en una máquina comprometida. Con SIEM, los logs ya viajaron a un servidor centralizado antes de que el atacante pudiera borrarlos.

```
Fuentes de log →→→→→→→→→→→→→→→→→ SIEM
  Firewalls         (syslog/CEF)    ↓
  Servidores Linux  (rsyslog)       Normaliza
  Windows AD        (WinEventLog)   Correlaciona
  Apps web          (JSON/nginx)    Alerta
  EDR endpoints     (agente)        Dashboards
  Cloud (AWS/GCP)   (CloudTrail)    ↓
                                  Analista L1
```

### Ejemplos de SIEMs comunes

| SIEM | Notas |
|---|---|
| **Splunk** | El más potente, muy caro, muy usado en enterprise |
| **Elastic SIEM** (ELK Stack) | Open source, muy popular, requiere tuning |
| **Wazuh** | Open source, bueno para empezar/lab |
| **Microsoft Sentinel** | Cloud-native en Azure |
| **QRadar (IBM)** | Enterprise, común en banca |

### Reglas de correlación

El SIEM no detecta amenazas por magia: alguien escribe **reglas de detección**. Ejemplo conceptual:

```
SI: mismo IP de origen
    hace 5+ intentos de login fallidos
    en menos de 60 segundos
    contra 3+ cuentas distintas
ENTONCES: alerta "Posible password spray"
```

Esas reglas son el núcleo del trabajo de detección. Frameworks como **SIGMA** permiten escribir reglas en formato portable entre SIEMs.

---

## 🔍 Logging y Detección — Qué registrar y por qué

### El problema del logging malo

Dos errores opuestos y igual de peligrosos:
- **Loggar demasiado poco**: eres ciego, no puedes investigar nada
- **Loggar demasiado sin filtrar**: te ahogas en ruido, las alertas reales se pierden

### Qué registrar (mínimo defensivo)

| Categoría | Qué capturar | Por qué |
|---|---|---|
| Autenticación | Logins ok, fallidos, cambios de contraseña, MFA | Detectar brute force, credential stuffing |
| Cambios de privilegios | sudo, escalada de roles, nuevos admins | Detectar privilege escalation |
| Acceso a red | Conexiones salientes inusuales, DNS, proxy | Detectar C2 (command & control) |
| Cambios de archivos críticos | /etc/passwd, binarios del sistema | Detectar persistencia |
| Errores de aplicación | 4xx/5xx en masa, excepciones inusuales | Detectar escaneos, SQLi, etc. |

### Calidad de un log útil

Un log útil responde: **¿Quién hizo qué, desde dónde, cuándo, con qué resultado?**

```json
{
  "timestamp": "2026-06-14T10:23:41Z",
  "user": "daniel",
  "action": "login",
  "result": "failure",
  "source_ip": "192.168.1.55",
  "user_agent": "curl/7.88",
  "reason": "invalid_password"
}
```

Un log que solo dice `"Error: login failed"` no sirve para investigar nada.

---

## 🚨 Ciclo de Respuesta a Incidentes (IR)

El estándar de la industria (NIST SP 800-61) define 6 fases. Memorizarlas como un ciclo, no como pasos lineales:

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  1. PREPARACIÓN                                 │
│     ↓                                           │
│  2. DETECCIÓN & ANÁLISIS                        │
│     ↓                                           │
│  3. CONTENCIÓN                                  │
│     ↓                                           │
│  4. ERRADICACIÓN                                │
│     ↓                                           │
│  5. RECUPERACIÓN                                │
│     ↓                                           │
│  6. LECCIONES APRENDIDAS ──────────────────────→ vuelve a 1
│                                                 │
└─────────────────────────────────────────────────┘
```

### Fase 1 — Preparación

Lo que haces **antes** de que pase algo. Es la fase más importante y la más ignorada.

- Documentar un **IRP** (Incident Response Plan): quién hace qué, cómo se contacta, qué sistemas son críticos
- Tener **playbooks** por tipo de incidente (ransomware, phishing, exfiltración de datos)
- Definir roles: Incident Manager, analistas, comunicación legal/RRHH/dirección
- Tener logs centralizados y alertas funcionando
- Backups probados (ver sección ransomware)
- **Ejercicios de simulacro** (tabletop exercises): "imagina que hoy hay ransomware, ¿qué hacemos?"

### Fase 2 — Detección y Análisis

Alguien (una alerta, un usuario, un tercero) señala que algo raro pasa. El analista debe:

1. **Clasificar**: ¿es un falso positivo o un incidente real?
2. **Determinar alcance**: ¿qué sistemas están afectados? ¿desde cuándo?
3. **Definir severidad**: ¿crítico, alto, medio, bajo?

Herramientas clave: SIEM, EDR (Endpoint Detection & Response), threat intelligence feeds.

**IOC** (Indicators of Compromise — Indicadores de Compromiso): evidencias de que hubo ataque. Ejemplos:
- Hash MD5/SHA256 de un malware conocido
- IP o dominio de un servidor C2
- Clave de registro de Windows modificada por un RAT

### Fase 3 — Contención

Objetivo: **parar el sangrado** sin destruir evidencias.

- **Contención a corto plazo**: aislar la máquina de la red (no apagarla — perderías memoria RAM con datos valiosos)
- **Contención a largo plazo**: bloquear IPs/dominios maliciosos en firewall, forzar rotación de credenciales comprometidas
- Hacer imagen forense del sistema antes de tocarlo

Error común: apagar la máquina inmediatamente. Pierdes procesos en memoria, conexiones activas, claves de cifrado en RAM — todo lo que necesitas para el forense.

### Fase 4 — Erradicación

Eliminar la causa raíz: borrar el malware, cerrar el vector de entrada (parchear la vulnerabilidad explotada), eliminar cuentas backdoor que haya creado el atacante.

Validar que no queden puertas traseras antes de restaurar servicios.

### Fase 5 — Recuperación

Restaurar sistemas a operación normal de forma controlada:

- Restaurar desde backups limpios (verificados)
- Monitorizar intensamente los sistemas restaurados durante días/semanas
- Comunicar internamente y, si aplica legalmente, a clientes/autoridades (RGPD exige notificación en 72h si hay datos personales afectados)

### Fase 6 — Lecciones Aprendidas

La fase que más se salta y la que más valor aporta a largo plazo.

- **Post-mortem sin culpas** (blameless): ¿qué pasó?, ¿por qué pasó?, ¿cómo lo detectamos o no lo detectamos?
- Actualizar playbooks, mejorar alertas, parchear procesos
- Compartir con el equipo para que todos aprendan

---

## 🔬 Forense Digital Básico

La forense digital es la disciplina de **recolectar y analizar evidencias digitales** preservando su integridad para que sean válidas (en un proceso legal o en una investigación interna).

### Principio fundamental: no contaminar la evidencia

El análisis siempre se hace sobre **copias**, nunca sobre el original. Y cada acción se documenta con timestamp.

### Orden de volatilidad (qué capturar primero)

Los datos más volátiles desaparecen antes si el sistema se apaga:

```
Más volátil (capturar YA)
  1. Registros de CPU, caché
  2. Memoria RAM — procesos, conexiones abiertas, claves de cifrado
  3. Estado de red — conexiones TCP activas, tablas ARP
  4. Procesos en ejecución
  5. Archivos abiertos
  6. Logs del sistema
  7. Disco duro — imágenes forenses
Menos volátil (puede esperar)
```

### Herramientas comunes de forense

| Herramienta | Uso |
|---|---|
| **Autopsy / Sleuth Kit** | Análisis de imágenes de disco (open source) |
| **Volatility** | Análisis de volcados de memoria RAM |
| **Wireshark** | Análisis de capturas de red |
| **dd / dc3dd** | Hacer imágenes bit a bit de discos |
| **FTK (AccessData)** | Suite forense comercial |

### Cadena de custodia

Si la evidencia va a usarse legalmente, cada transferencia/acceso debe documentarse: quién la tocó, cuándo, para qué. Sin cadena de custodia, la evidencia puede ser impugnada.

---

## 🦠 Defensa contra Ransomware

El **ransomware** cifra tus archivos y pide rescate para devolver la clave. Es una de las amenazas más destructivas para organizaciones y particulares.

### Vectores de entrada más comunes

1. Phishing con adjunto malicioso o enlace
2. Explotación de RDP expuesto a internet sin autenticación fuerte
3. Vulnerabilidades sin parchear (EternalBlue fue el vector de WannaCry)
4. Compromiso de la cadena de suministro (software legítimo troyanizado)

### Defensa en profundidad contra ransomware

**Capa 1 — Prevenir la infección inicial**
- Formación antiphishing (simulacros de phishing internos)
- Filtrado de adjuntos y URLs en el correo
- No exponer RDP directamente a internet; usar VPN
- Parcheo rápido de vulnerabilidades críticas

**Capa 2 — Limitar el daño si entra**
- Principio de mínimo privilegio: un usuario de contabilidad no necesita acceso a servidores de producción
- **Segmentación de red**: separar DMZ, servidores, workstations, OT/ICS; el ransomware se propaga por la red, si está segmentada el blast radius es menor
- EDR con capacidad de detección de comportamiento (no solo firmas)
- Deshabilitar macros de Office en usuarios que no las necesitan

**Capa 3 — Recuperar sin pagar el rescate**

La regla **3-2-1 de backups**:

```
3 copias de los datos
  ├── 2 en medios distintos (ej: disco local + NAS)
  └── 1 offsite / offline (ej: cinta física, cloud con versioning)
                               ↑
               Este backup debe ser INACCESIBLE desde la red
               (el ransomware busca y cifra también los backups conectados)
```

**Offline** es clave. Un backup en un NAS montado permanentemente puede ser cifrado igual que el resto. Los backups en cinta o cloud con "object lock" (inmutabilidad) sobreviven.

**Probar los backups regularmente**: un backup no probado es un backup cuya integridad desconoces. Haz restauraciones de prueba periódicas.

---

## 🔴🔵🟣 Red Team vs Blue Team vs Purple Team (en detalle)

| Aspecto | Red Team | Blue Team | Purple Team |
|---|---|---|---|
| Objetivo | Encontrar caminos de ataque | Detectar y responder | Cerrar el gap entre ambos |
| Mentalidad | Adversarial, creativo | Analítico, sistemático | Colaborativo |
| Herramientas típicas | Metasploit, Burp, Cobalt Strike | SIEM, EDR, IDS/IPS | Ambas |
| Output | Informe de pentest, cadenas de ataque | Alertas, playbooks actualizados | Cobertura de detección mejorada |
| Frecuencia | Puntual (anual/semestral) | Continuo | Continuo o en sprints |

El **Red Team** en un contexto profesional no es "hackear libremente" — opera bajo un **Rules of Engagement** (RoE) firmado que define scope exacto, sistemas excluidos, horas de operación y canales de comunicación de emergencia. Esto es lo que separa el pentesting autorizado del delito.

---

## Errores comunes en Blue Team

- **Alert fatigue** (fatiga de alertas): demasiados falsos positivos hacen que los analistas ignoren las alertas reales. La calidad de las reglas de detección importa tanto como la cantidad.
- **No tener playbooks**: cuando pasa un incidente real, no es el momento de improvisar.
- **Backups no probados**: descubrir que el backup está corrupto durante un ransomware es devastador.
- **Logs sin centralizar**: si el atacante borra logs locales, pierdes la evidencia.
- **Asumir que la contención = apagar la máquina**: pierdes evidencias volátiles críticas.
- **Saltar la fase de lecciones aprendidas**: el mismo vector se repite en el siguiente incidente.

---

## Aplícalo / Practica 🧪

**CTFs y laboratorios:**
- **Blue Team Labs Online** (blueteamlabs.online): laboratorios específicos de análisis de logs, forense e IR
- **LetsDefend** (letsdefend.io): simulador de SOC, analiza alertas reales en un entorno simulado
- **TryHackMe** — rutas "SOC Level 1", "Incident Response", "Digital Forensics"
- **DFIR.training** — recursos de forense digital

**En tu entorno propio:**
- Monta un stack ELK o Wazuh en VMs locales y envíale logs de tus proyectos
- Configura logging estructurado (JSON) en tu app web → simula ataques y mira qué ves en los logs
- Implementa la regla 3-2-1 para tus proyectos personales (ya tienes el script de backup rsync + rclone — verifica que el bucket de Google Drive tenga versioning activado)
- Haz un tabletop exercise mental: "si mi VPS con la app web fuera comprometido mañana, ¿qué haría?"

**Para leer:**
- NIST SP 800-61r2 — Computer Security Incident Handling Guide (gratis, PDF oficial)
- MITRE ATT&CK — matriz de técnicas de ataque con sugerencias de detección por cada una

---

## Conexiones

- [[MOC_Ciberseguridad]]
- [[01-fundamentos-y-mentalidad]]
- [[03-seguridad-de-redes]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[07-pentesting-y-ciclo-del-ataque]]
- [[08-vulnerabilidades-y-explotacion]]
- [[09-devsecops-y-appsec]]
- [[11-privacidad-y-opsec]]
- [[MOC_Desarrollo_Software]]
