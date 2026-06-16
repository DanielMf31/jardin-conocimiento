---
title: Aprender ciberseguridad y carrera
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, ciberseguridad/aprendizaje, ciberseguridad/carrera, ciberseguridad/laboratorio]
type: nota
status: en-progreso
source: claude-code
aliases: [carrera-ciberseg, aprender-hacking-etico, ruta-ciberseguridad]
---

# 🎓 Aprender ciberseguridad y carrera

## Por qué este documento existe

La ciberseguridad tiene una peculiaridad única: **no puedes aprender a defender sin entender cómo se ataca**, y no puedes practicar ofensiva sin un objetivo legal. Esto crea una barrera de entrada que no existe en otras disciplinas de software.

Este documento resuelve esa paradoja: cómo construir un entorno de práctica **propio y legal**, qué plataformas usar, qué certificaciones importan (y cuáles son marketing), y cómo orientar una carrera desde un perfil de ingeniería técnica.

> **Marco ético implícito en todo lo que sigue**: cualquier técnica ofensiva se practica en sistemas propios (VMs locales) o en plataformas que otorgan permiso explícito (TryHackMe, HackTheBox, CTFs). Usar estas técnicas en sistemas ajenos sin autorización escrita es delito en la mayoría de jurisdicciones (Ley de Delitos Informáticos en España: art. 197 bis/ter CP; CFAA en EE.UU.).

---

## 🧭 Panorama: dónde encaja el aprendizaje en el ciclo de la disciplina

```
[Teoría] → [Lab propio] → [Plataformas guiadas] → [CTFs] → [Cert / portafolio] → [Rol profesional]
   ↑                                                                                        |
   └─────────────────── feedback continuo (incidentes reales, nuevas CVEs) ─────────────────┘
```

La ciberseguridad es un campo **adversarial y evolutivo**: los atacantes cambian técnicas constantemente. El aprendizaje nunca termina; lo que cambia es el nivel de abstracción con el que operas.

---

## 🖥️ Montar un laboratorio en VMs

### Por qué un lab propio antes que todo lo demás

Una plataforma online te da acceso limitado y controlado. Un lab propio te permite:
- Romper cosas sin consecuencias y entender por qué se rompieron.
- Experimentar con malware real en entorno aislado (sandbox).
- Construir redes complejas (segmentación, firewalls, VLAN) que no puedes hacer en una VM en la nube de un tercero.

### Arquitectura mínima recomendada

```
Host físico (tu máquina)
├── Red NAT interna (solo VMs, sin salida real a internet)
│   ├── Kali Linux          ← atacante / herramientas
│   ├── DVWA / Metasploitable ← víctimas deliberadamente vulnerables
│   └── Windows (eval)      ← víctima AD, opcional
└── Red Host-only           ← para tráfico entre VMs sin salida
```

**Hypervisores recomendados**: VirtualBox (gratis, multiplataforma) o VMware Workstation Player.

**Regla de oro**: la red de las VMs víctima NUNCA debe ser "Bridged" (conectada a tu red real). Usa siempre NAT interno o Host-only para evitar que el malware de prueba salga.

### VMs atacante

| VM | Qué es | Para qué |
|---|---|---|
| **Kali Linux** | Distro Debian con >600 herramientas preinstaladas | La navaja suiza del pentester |
| **Parrot OS Security** | Alternativa a Kali, más ligera | Lo mismo, gusto personal |
| **REMnux** | Distro para análisis de malware | Ingeniería inversa, sandbox |

Kali es el estándar de facto. Si vienes de hardware/técnico, la CLI de Kali es Debian — nada nuevo si ya usas Linux.

### VMs víctima (deliberadamente vulnerables)

| Objetivo | Descripción | Nivel | Enfoque |
|---|---|---|---|
| **DVWA** (Damn Vulnerable Web App) | App web PHP con vulns OWASP configurables | Principiante | Web (SQLi, XSS, LFI, etc.) |
| **Metasploitable 2 / 3** | VM Ubuntu/Windows con servicios vulnerables | Principiante–Intermedio | Redes, exploits clásicos |
| **VulnHub** | Catálogo de VMs descargables tipo CTF | Variable | Todos los vectores |
| **OWASP WebGoat** | App Java con lecciones interactivas de AppSec | Principiante | Web, didáctico |
| **HackTheBox (labs offline)** | Algunas máquinas retiradas son descargables | Intermedio | Todo |

**Flujo de trabajo típico**:
1. Levantar Kali + Metasploitable en red Host-only.
2. Desde Kali: `nmap -sV <ip_victima>` para enumerar servicios.
3. Identificar servicio vulnerable, buscar exploit, documentar el proceso.
4. Escribir una nota en la bóveda con lo aprendido.

---

## 🌐 Plataformas de práctica online

### OverTheWire — Bandit (CLI/Linux)

**Qué es**: serie de wargames por SSH donde cada nivel es un puzzle Linux.

**Por qué empezar aquí**: si tu base de CLI/Linux es débil, Bandit la solidifica antes de que la falta de fundamentos te frene en plataformas más avanzadas. Cubre: permisos, pipes, variables de entorno, ficheros ocultos, cron, etc.

**URL**: overthewire.org/wargames/bandit

### TryHackMe (THM)

**Perfil**: plataforma guiada, con "rooms" estructuradas en rutas de aprendizaje.

**Por qué es buena para empezar**:
- Muchas rooms tienen pistas y teoría integrada.
- Tiene rutas completas: "Pre-Security", "SOC Level 1", "Jr Penetration Tester".
- VPN + máquinas en la nube: no necesitas lab local para empezar.

**Límite**: las rooms guiadas pueden volverse "seguir instrucciones" sin entender el fondo. Combínala con notas propias.

### HackTheBox (HTB)

**Perfil**: plataforma más competitiva, menos guiada. Máquinas "activas" solo resolubles por ti; máquinas "retiradas" tienen writeups públicos.

**Cuándo usarla**: cuando ya tienes base (después de THM o Bandit). El salto de dificultad es real.

**HTB Academy**: rama educativa de HTB, similar a THM pero más técnica y con contenido profesional actualizado.

### PortSwigger Web Security Academy

**Qué es**: plataforma gratuita de PortSwigger (creadores de Burp Suite) con laboratorios interactivos de seguridad web.

**Por qué es excelente**: cubre todo el OWASP Top 10 con labs progresivos. Es **la** referencia para AppSec web. Cada vulnerabilidad tiene explicación teórica + lab práctico + solución experta.

**URL**: portswigger.net/web-security

**Cuándo usarla**: en paralelo con el estudio de [[04-seguridad-web-owasp]].

### Resumen comparativo

| Plataforma | Nivel entrada | Guiado | Coste | Mejor para |
|---|---|---|---|---|
| OverTheWire Bandit | Cero | No | Gratis | CLI Linux |
| TryHackMe | Principiante | Mucho | Freemium | Ruta estructurada |
| HackTheBox | Intermedio | Poco | Freemium | Práctica real |
| PortSwigger WSA | Principiante | Moderado | Gratis | Web/AppSec |
| VulnHub | Variable | No | Gratis | Lab local |

---

## 🏁 CTFs (Capture The Flag)

### Qué son

Un CTF es una competición de seguridad donde los participantes resuelven retos técnicos para obtener una "bandera" (flag), normalmente una cadena de texto como `flag{s0m3_h4sh}`. Las flags se envían a una plataforma para puntuar.

**Función**: evalúan habilidades técnicas en condiciones de tiempo limitado. Son el equivalente de las olimpiadas de matemáticas para la ciberseguridad.

### Tipos de CTF

| Tipo | Mecánica | Analogía |
|---|---|---|
| **Jeopardy** | Retos independientes por categorías (web, crypto, pwn, forense, misc). Cada reto vale puntos. | Crucigrama técnico |
| **Attack-Defense** | Equipos tienen su propio servidor vulnerable. Debes atacar los de otros y defender el tuyo simultáneamente. | Fútbol: atacas y defiendes |
| **King of the Hill** | Varios equipos compiten por mantener acceso a la misma máquina. | Torre de control |

### Categorías comunes en Jeopardy

- **Web**: vulnerabilidades en aplicaciones web (SQLi, SSRF, deserialization).
- **Crypto**: criptografía rota o mal implementada (ver [[02-criptografia]]).
- **Pwn (Binary Exploitation)**: desbordamientos de buffer, ROP chains — vinculado a [[08-vulnerabilidades-y-explotacion]].
- **Reversing**: ingeniería inversa de binarios.
- **Forensics**: análisis de volcados de memoria, capturas de red (PCAP), logs.
- **Misc / OSINT**: retos de inteligencia en fuentes abiertas.

### Dónde encontrar CTFs

- **CTFtime.org**: calendario global de CTFs activos y pasados.
- **PicoCTF**: orientado a estudiantes, excelente para empezar.
- **NahamCon CTF**, **HackTheBox CTF**, **Google CTF**: varios niveles.

### Cómo aprovechar un CTF al máximo

1. Resuelve lo que puedas durante el evento.
2. Después del evento, lee **writeups** de los retos que no resolviste.
3. Reproduce el reto con el writeup como guía para entender el razonamiento.
4. **Escribe tu propio writeup**: solidifica el conocimiento y construye portafolio.

---

## 📜 Certificaciones por nivel

### Por qué importan (y cuándo no importan)

Las certificaciones son señales de credibilidad, especialmente al entrar al mercado. No sustituyen el portafolio técnico, pero abren puertas en procesos de selección formales (empresas grandes, administración pública, contratistas de defensa).

**Regla práctica**: una cert sin habilidades reales es papel mojado en una entrevista técnica. Pero habilidades sin cert pueden frenarte en el filtro de RRHH.

### Mapa de certificaciones

```
PRINCIPIANTE
├── CompTIA Security+          ← fundamentos amplios, muy reconocida en EE.UU./UK
├── eJPT (eLearnSecurity)      ← primera cert práctica de pentesting, asequible
└── CompTIA Network+           ← si la base de redes es débil

INTERMEDIO
├── CEH (EC-Council)           ← conocida pero criticada por ser teórica; útil para GRC/compliance
├── PNPT (TCM Security)        ← práctica, bien valorada en la comunidad, más barata que OSCP
├── CompTIA PenTest+           ← nivel medio, más completa que Security+
└── eWPT (eLearnSecurity)      ← web pentesting intermedio

AVANZADO
├── OSCP (Offensive Security)  ← gold standard del pentesting; examen de 24h práctico
├── OSEP / OSED / OSWE         ← especializaciones Offensive Security (evasión, exploit dev, web)
└── GPEN / GWAPT (GIAC)        ← muy respetadas, caras; orientadas a empresa

CLOUD SECURITY
├── AWS Security Specialty     ← si tu stack es AWS
├── GCP Professional Cloud Security ← Google Cloud
└── CCSP (ISC2)                ← amplia, multi-cloud, orientada a arquitectura

GESTIÓN / GRC
├── CISSP (ISC2)               ← para roles de arquitectura/gestión; requiere experiencia
└── CISM (ISACA)               ← gestión de seguridad de la información
```

### Detalle de las más relevantes para empezar

| Cert | Formato | Dificultad | Precio aprox. | Para qué sirve |
|---|---|---|---|---|
| **CompTIA Security+** | Test teórico | Bajo-Medio | ~370 USD | Abrir puertas en empresas grandes, base sólida |
| **eJPT** | Examen práctico online | Bajo | ~200 USD | Primera cert de pentesting sin prerequisitos |
| **PNPT** | Report de pentest real | Medio | ~400 USD | Acreditar pentesting con portafolio real |
| **OSCP** | 24h lab + report | Alto | ~1499 USD | El más respetado del sector; sin atajos |
| **CEH** | Test teórico + labs | Medio | ~1000 USD+ | Compliance, contratistas; menos valorada técnicamente |

**Opinión directa sobre CEH**: la comunidad técnica la considera inferior a OSCP/PNPT en rigor. Es útil en contextos de compliance o empresas que la exigen por contrato, no como señal de habilidad técnica real.

---

## 👥 Roles en ciberseguridad

### El espectro ofensivo–defensivo

```
Ofensivo                    Mixto                   Defensivo
   |                          |                          |
Red Team              Purple Team                 Blue Team
Pentester             AppSec Engineer             SOC Analyst
Bug Hunter            GRC Analyst                 DFIR Analyst
                                                  Threat Hunter
```

### Descripción de roles

| Rol | Qué hace | Habilidades clave | Cert típica |
|---|---|---|---|
| **Red Team** | Simula atacantes reales en operaciones largas y sigilosas | OSCP, AD, evasión de EDR | OSCP, CRTO |
| **Pentester** | Pruebas de intrusión acotadas por contrato (scope definido) | Metodología, reporting, web, redes | OSCP, PNPT |
| **Bug Bounty Hunter** | Caza vulnerabilidades en programas públicos (HackerOne, Bugcrowd) | Web profundo, creatividad, OSINT | — (portafolio) |
| **AppSec Engineer** | Integra seguridad en el ciclo de desarrollo (DevSecOps) | SAST/DAST, threat modeling, code review | CSSLP, eWPT |
| **Blue Team / SOC Analyst** | Monitoriza, detecta y responde a incidentes | SIEM (Splunk, ELK), threat intel, logs | Security+, BTL1 |
| **DFIR (Digital Forensics & IR)** | Investiga incidentes, recupera evidencia digital | Forense de disco/memoria, PCAP, timelines | GCFE, GCFA |
| **Threat Hunter** | Busca proactivamente amenazas no detectadas en el entorno | TTPs, MITRE ATT&CK, anomaly detection | GCIA |
| **GRC Analyst** | Gobernanza, riesgo y cumplimiento normativo (ISO 27001, ENS, GDPR) | Normativas, auditoría, gestión de riesgos | CISM, CISSP, ISO Lead Auditor |
| **Purple Team** | Combina red y blue: usa técnicas ofensivas para mejorar defensas | Ambos lados, comunicación | Ambos perfiles |

### Desde técnico/hardware: ventajas y rutas naturales

Tu perfil de ingeniería tiene ventajas específicas:
- **OT/ICS Security** (seguridad de sistemas industriales, SCADA, PLCs): rarísimo encontrar alguien que entienda tanto el hardware como la ciberseguridad. Muy demandado y mal cubierto.
- **Firmware/Embedded Security**: análisis de firmware de routers, IoT, microcontroladores.
- **AppSec / DevSecOps**: si desarrollas software (como tu app web), integrar seguridad desde el diseño es tu camino más directo.

---

## 🗺️ Ruta recomendada de autoaprendizaje

Esta ruta asume punto de partida técnico (Linux básico, algo de programación) pero poca base de seguridad.

### Fase 0 — Fundamentos (4–8 semanas)

- [ ] Leer [[01-fundamentos-y-mentalidad]]: mentalidad adversarial, CIA Triad, terminología.
- [ ] OverTheWire Bandit: niveles 0–20 (CLI Linux sólida).
- [ ] TryHackMe: ruta "Pre-Security" completa.
- [ ] Conceptos de [[03-seguridad-de-redes]]: TCP/IP, DNS, HTTP/S, puertos comunes.

### Fase 1 — Base técnica (2–4 meses)

- [ ] TryHackMe: ruta "Jr Penetration Tester".
- [ ] PortSwigger Web Security Academy: módulos SQLi, XSS, IDOR, SSRF (ver [[04-seguridad-web-owasp]]).
- [ ] Montar lab: Kali + DVWA + Metasploitable en VirtualBox.
- [ ] Primer CTF: PicoCTF (categorías web y forensics primero).
- [ ] Leer [[05-identidad-auth-y-secretos]] y [[06-seguridad-de-sistemas-y-hardening]].

### Fase 2 — Práctica real (3–6 meses)

- [ ] HackTheBox: 10 máquinas retiradas con writeup + 5 sin writeup.
- [ ] PortSwigger: completar todas las categorías.
- [ ] Escribir 3–5 writeups propios (portafolio público en GitHub o blog).
- [ ] Estudiar [[07-pentesting-y-ciclo-del-ataque]] y [[08-vulnerabilidades-y-explotacion]].
- [ ] Considerar eJPT o PNPT como primera certificación.

### Fase 3 — Especialización (6+ meses)

- [ ] Elegir vector según interés (ver tabla de roles):
  - Web/AppSec → PortSwigger avanzado, BSCP cert, [[09-devsecops-y-appsec]].
  - Pentesting general → preparación OSCP (labs de Offensive Security).
  - Blue Team → [[10-blue-team-y-respuesta-incidentes]], BTL1, Splunk fundamentals.
  - OT/ICS → cursos específicos de ICS security (SANS ICS515).
- [ ] Participar en CTFs de nivel intermedio (HTB CTF, NahamCon).
- [ ] Buscar bug bounty en programas con scope amplio (HackerOne, Intigriti).

### Hitos de referencia temporal

| Hito | Tiempo estimado desde cero |
|---|---|
| CLI Linux cómoda, conceptos de red | 1–2 meses |
| Primera máquina HTB resuelta solo | 3–5 meses |
| eJPT aprobado | 4–6 meses |
| 20 máquinas HTB + writeups | 8–12 meses |
| OSCP | 12–18 meses desde cero técnico |

---

## ⚠️ Errores comunes al aprender ciberseguridad

- **Tutorial hell**: ver 50 videos sin practicar. La práctica activa en lab/plataformas es lo que construye habilidad.
- **Saltar a OSCP sin base**: OSCP sin haber resuelto 20–30 máquinas HTB es tirar dinero.
- **Copiar writeups sin entender**: anota qué hizo el exploit y por qué funcionó, no solo el comando.
- **Ignorar el reporte**: en el mundo real, un pentest sin informe claro no existe. Practica escribir reportes desde el principio.
- **Obsesionarse con tools**: Metasploit y Burp son amplificadores, no sustituyen entender la vulnerabilidad subyacente.
- **No leer documentación oficial**: CVE Details, MITRE ATT&CK, OWASP son fuentes primarias, no posts de blog.

---

## 🛠️ Aplícalo / Practica

### Lab inmediato (esta semana)

1. Instala VirtualBox + descarga Kali Linux (imagen pre-built en kali.org/get-kali/#kali-virtual-machines).
2. Descarga Metasploitable 2 (sourceforge.net/projects/metasploitable/).
3. Configura ambas en red Host-only.
4. Desde Kali: `nmap -sV 192.168.56.x` (ajusta IP). Documenta los servicios que encuentres.

### En tus proyectos actuales

- **app web (FastAPI + React)**: aplica [[09-devsecops-y-appsec]] — revisa dependencias con `pip audit` y `npm audit`, revisa que los secretos no estén en el repo (ver [[05-identidad-auth-y-secretos]]).
- **proyecto embebido (PlatformIO/embedded)**: busca si hay credenciales hardcoded en el firmware; explora conceptos de firmware security.

### CTFs para empezar ahora

- PicoCTF (picoctf.org): permanentemente disponible, ideal para primeras flags.
- OverTheWire Bandit nivel 0: `ssh bandit0@bandit.labs.overthewire.org -p 2220` (password: bandit0).

### Recursos adicionales gratuitos

- **TCM Security YouTube**: cursos gratuitos de pentesting (Heath Adams).
- **John Hammond YouTube**: walkthroughs de CTFs y conceptos.
- **MITRE ATT&CK Framework** (attack.mitre.org): base de conocimiento de tácticas y técnicas reales de atacantes.
- **HackTricks** (book.hacktricks.xyz): referencia técnica enorme, usada como cheatsheet en CTFs.

---

## Conexiones

- [[MOC_Ciberseguridad]]
- [[01-fundamentos-y-mentalidad]]
- [[02-criptografia]]
- [[03-seguridad-de-redes]]
- [[04-seguridad-web-owasp]]
- [[05-identidad-auth-y-secretos]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[07-pentesting-y-ciclo-del-ataque]]
- [[08-vulnerabilidades-y-explotacion]]
- [[09-devsecops-y-appsec]]
- [[10-blue-team-y-respuesta-incidentes]]
- [[11-privacidad-y-opsec]]
- [[MOC_Desarrollo_Software]]
- [[MOC_CS_Fundamentos]]
