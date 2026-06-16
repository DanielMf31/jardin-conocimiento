---
title: Fundamentos y mentalidad de la ciberseguridad
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, fundamentos, mentalidad]
type: nota
status: en-progreso
source: claude-code
aliases: [fundamentos seguridad, mentalidad hacker, CIA triada]
---

# 🛡️ Fundamentos y mentalidad de la ciberseguridad

## ¿Por qué este documento existe?

La ciberseguridad no es una capa que se añade al final de un proyecto. Es una forma de pensar sobre sistemas: quién puede hacer qué, qué pasa si algo falla, y cómo detectar cuando alguien actúa fuera de los límites esperados. Este documento establece el marco mental desde el cual leer todo lo demás del clúster.

---

## 🌐 ¿Qué es la ciberseguridad?

**Ciberseguridad** es la práctica de proteger sistemas, redes, datos y personas frente a accesos no autorizados, daños o ataques. No se limita a software: incluye hardware, personas (ingeniería social), procesos y políticas.

> Como ingeniero de técnico/sistemas: piensa en seguridad como la disciplina de "tolerancia a fallos maliciosos". El fallo no es aleatorio — hay un adversario que lo busca activamente.

Tres disciplinas principales que se solapan:

| Disciplina | Enfoque | Ejemplo |
|---|---|---|
| **Blue team** (defensa) | Monitorear, detectar, responder | SIEM, firewalls, hardening |
| **Red team** (ataque ético) | Encontrar fallos antes que el adversario | Pentesting, CTFs |
| **Purple team** | Colaboración activa rojo+azul | Simulaciones de ataque controladas |

---

## 🔺 La Tríada CIA

El modelo más fundamental de la seguridad. Toda amenaza ataca una o más de estas tres propiedades:

```
         Confidencialidad
               /\
              /  \
             /    \
            /  CIA \
           /________\
   Integridad     Disponibilidad
```

### Confidencialidad
Solo quien está autorizado puede acceder a la información.
- **Amenaza**: robo de credenciales, escuchas (eavesdropping), fugas de datos.
- **Control**: cifrado, control de acceso, clasificación de datos.

### Integridad
Los datos no han sido modificados sin autorización (ni por error, ni por ataque).
- **Amenaza**: man-in-the-middle, inyección SQL, corrupción de binarios.
- **Control**: hashes criptográficos (SHA-256), firmas digitales, control de versiones.

### Disponibilidad
El sistema está accesible para quienes lo necesitan cuando lo necesitan.
- **Amenaza**: DDoS (Distributed Denial of Service), ransomware, fallos de infraestructura.
- **Control**: redundancia, backups, rate limiting, CDN.

> **Regla práctica**: cuando analices un incidente, pregunta siempre "¿cuál de los tres pilares fue vulnerado?". Ayuda a priorizar la respuesta.

---

## 🗺️ Threat Modeling — Modelar amenazas

**Threat modeling** (modelado de amenazas) es el proceso estructurado de identificar qué puede salir mal en un sistema antes de que ocurra. No es opcional en proyectos serios.

### El proceso en 4 preguntas (marco PASTA / simplificado)

1. **¿Qué estamos construyendo?** — Diagrama del sistema: componentes, flujos de datos, límites de confianza.
2. **¿Qué puede salir mal?** — Enumerar amenazas. Framework STRIDE (ver abajo).
3. **¿Qué hacemos al respecto?** — Controles para mitigar cada amenaza.
4. **¿Hemos cubierto bien?** — Validar que los controles son proporcionales al riesgo.

### Framework STRIDE

Mnemónico para categorizar amenazas (creado por Microsoft):

| Letra | Amenaza (inglés) | Qué significa | Vulnera CIA |
|---|---|---|---|
| **S** | Spoofing | Suplantar identidad | Confidencialidad |
| **T** | Tampering | Modificar datos | Integridad |
| **R** | Repudiation | Negar haber realizado una acción | Integridad |
| **I** | Information Disclosure | Revelar datos privados | Confidencialidad |
| **D** | Denial of Service | Impedir el acceso | Disponibilidad |
| **E** | Elevation of Privilege | Obtener permisos superiores | Los tres |

---

## 🎯 Superficie de ataque y vectores de ataque

**Superficie de ataque** (attack surface): todo punto de un sistema donde un atacante podría intentar entrar o extraer datos. Cuanto más grande, más riesgo.

Tipos de superficie:
- **Digital**: puertos abiertos, APIs, formularios web, dependencias de software.
- **Humana**: empleados, phishing, ingeniería social.
- **Física**: acceso a hardware, USB maliciosos, instalaciones.

**Vector de ataque**: el camino concreto que usa un atacante para explotar la superficie.

```
Superficie de ataque (todo lo expuesto)
       |
       +-- Vector 1: Puerto 22 SSH con contraseña débil
       +-- Vector 2: Formulario web sin sanitizar inputs
       +-- Vector 3: Email de phishing al empleado
       +-- Vector N: ...
```

> **Principio de reducción**: si no usas un servicio, ciérralo. Cada puerto abierto, endpoint expuesto o dependencia añadida es superficie nueva.

---

## 🏗️ Principios fundamentales de diseño seguro

Estos principios son transferibles a cualquier sistema. Son la base de todas las decisiones de seguridad.

### 1. Defensa en profundidad (Defense in Depth)

No dependas de un único control de seguridad. Si una capa falla, la siguiente detiene el ataque.

```
[ Firewall perimetral ]
      |
[ WAF — Web Application Firewall ]
      |
[ Autenticación fuerte (MFA) ]
      |
[ Autorización granular (RBAC) ]
      |
[ Cifrado de datos en reposo ]
      |
[ Logs + alertas (SIEM) ]
```

Analogía técnico: como un sistema con redundancia en sensores críticos — no confías en un único sensor para una decisión de seguridad.

### 2. Mínimo privilegio (Principle of Least Privilege — PoLP)

Cada usuario, proceso o componente debe tener exactamente los permisos que necesita para su función, y nada más.

- Un microservicio de lectura de base de datos no necesita permisos de escritura.
- Un script de backup no necesita acceso root al sistema completo.
- Un usuario nuevo no necesita ser administrador.

**Cómo prevenirlo/aplicarlo**: revisar permisos regularmente (privilege review), usar roles en lugar de usuarios directos, aplicar RBAC (Role-Based Access Control).

### 3. Assume Breach (Asumir que ya han entrado)

Diseña el sistema asumiendo que el perímetro ya ha sido comprometido. La pregunta no es "¿cómo evito que entren?" sino "¿qué pueden hacer una vez dentro, y cómo lo detecto?".

Consecuencias prácticas:
- Segmentar la red internamente (no todo en la misma VLAN).
- Cifrar datos incluso en tráfico interno.
- Monitorear actividad interna, no solo el perímetro.
- Implementar Zero Trust: ningún dispositivo o usuario es confiable por defecto, ni siquiera dentro de la red corporativa.

### 4. Seguridad por diseño (Security by Design)

La seguridad no se añade al final como un parche. Se integra en las decisiones de arquitectura desde el inicio.

- Elegir bibliotecas con buen historial de seguridad.
- Diseñar APIs que no expongan más datos de los necesarios.
- Incluir threat modeling antes de escribir código.
- Revisar dependencias de terceros (supply chain attacks).

### 5. Fail Secure (Fallar de forma segura)

Cuando algo falla, el sistema debe caer al estado más seguro posible, no al más permisivo.

Ejemplo malo: si el sistema de autenticación falla, permite el acceso por defecto.
Ejemplo bueno: si el sistema de autenticación falla, deniega el acceso y registra el error.

---

## 👤 Actores de amenaza (Threat Actors)

Saber quién te puede atacar cambia radicalmente qué controles priorizar.

| Actor | Motivación | Sofisticación | Ejemplo |
|---|---|---|---|
| **Script kiddie** | Diversión, reputación | Baja (usa herramientas existentes) | Ataque DDoS con herramienta descargada |
| **Cibercriminal** | Dinero | Media-alta | Ransomware, fraude, robo de datos |
| **Hacktivista** | Ideología | Variable | Deface de webs, filtraciones |
| **Insider malicioso** | Venganza, dinero | Alta (acceso legítimo) | Empleado disgustado con acceso a DB |
| **APT (Advanced Persistent Threat)** | Espionaje, sabotaje (estado-nación) | Muy alta | Stuxnet, ataques a infraestructura crítica |
| **Investigador de seguridad** | Mejorar la seguridad | Alta | Bug bounties, disclosure responsable |

> En proyectos personales y pequeñas apps: el adversario más probable es oportunista (script kiddie buscando vulnerabilidades conocidas con scanners automáticos). No te obsesiones con APTs, pero tampoco ignores lo básico.

---

## ⚖️ Ética y legalidad — Reglas de oro

Este es el límite que separa al profesional de seguridad del criminal. No es negociable.

### La regla fundamental

> **Solo puedes testear sistemas que te pertenecen o para los cuales tienes autorización EXPLÍCITA y ESCRITA del propietario.**

Sin excepción. "Curiosidad" o "quería ver si podía" no es defensa legal.

### Los sombreros (hats) — modelo de clasificación

| Sombrero | Descripción | Legal |
|---|---|---|
| **White hat** (sombrero blanco) | Hacker ético. Trabaja con permiso, reporta vulnerabilidades de forma responsable. | Sí |
| **Grey hat** | Busca vulnerabilidades sin permiso pero sin intención maliciosa. Suele notificar al afectado. | Zona gris legal — puede tener consecuencias penales |
| **Black hat** | Ataca sin permiso con fines maliciosos (robo, daño, extorsión). | No |

**No existe el "grey hat inofensivo" desde el punto de vista legal.** Acceder a un sistema sin autorización es delito en la mayoría de jurisdicciones (en España: Código Penal arts. 197 bis y ter), independientemente de la intención.

### Disclosure responsable (Responsible Disclosure)

Cuando encuentras una vulnerabilidad en un sistema ajeno (sin haberlo buscado):
1. No la explotas.
2. Contactas al propietario/equipo de seguridad de forma privada.
3. Les das tiempo razonable para parchear (normalmente 90 días, convención de Google Project Zero).
4. Si no responden, puedes publicarla (full disclosure) o notificar a una autoridad de coordinación (CERT).

Muchas empresas tienen programas de **Bug Bounty** (recompensa por bugs) — es la forma legítima y remunerada de hacer esto.

### Entornos donde practicar LEGALMENTE

- **Tus propias VMs** (laboratorio local con Kali Linux, Metasploitable, DVWA, VulnHub).
- **CTFs (Capture The Flag)**: competiciones de seguridad con sistemas diseñados para ser atacados. (HackTheBox, TryHackMe, PicoCTF, CTFtime.org).
- **Plataformas de práctica online**: HackTheBox, TryHackMe, PortSwigger Web Security Academy.
- **Bug Bounty**: HackerOne, Bugcrowd — sistemas reales pero con permiso explícito del propietario.
- **Tus propios proyectos**: la app web, scripts personales, tu propio servidor.

---

## 🧠 Mentalidad del defensor vs. del atacante

La seguridad efectiva requiere pensar como ambos:

**Mentalidad del atacante (necesaria para defender bien)**:
- "¿Cómo puedo abusar de esta funcionalidad?"
- "¿Qué pasa si envío datos inesperados aquí?"
- "¿Qué supuestos está haciendo el sistema que puedo violar?"

**Mentalidad del defensor**:
- "¿Cuál es el impacto si esto falla?"
- "¿Cómo detecto que está pasando?"
- "¿Cuánto tarda en detectarse y responderse?"

> Esta dualidad — pensar como atacante para construir mejores defensas — es la esencia del hacking ético y del rol de red team. No son opuestos; son complementarios.

---

## Errores comunes del principiante

- **Seguridad por oscuridad**: creer que ocultar cómo funciona el sistema lo protege. No es un control válido — es un complemento a lo sumo.
- **Confiar en el cliente**: nunca validar solo en frontend. El atacante puede enviar peticiones directas al servidor.
- **Asumir que "nadie me va a atacar a mí"**: los scanners automáticos atacan todo internet indiscriminadamente.
- **Un solo factor de autenticación**: las contraseñas se roban, se filtran, se adivinan. MFA es necesario.
- **No actualizar dependencias**: la mayoría de vulnerabilidades explotadas son conocidas y tienen parche disponible.
- **Logs inexistentes**: sin logs no puedes detectar ni investigar incidentes.

---

## 🛠️ Aplícalo / Practica

### Laboratorio mínimo (nivel 0)
1. Instala una VM con **Kali Linux** (distribución orientada a pentesting, con herramientas preinstaladas).
2. Levanta una VM con **Metasploitable 2** (sistema vulnerable diseñado para practicar) en red interna.
3. Practica escaneo con `nmap` y exploración de servicios en Metasploitable — sin salir de tu red local.

### CTFs para empezar
- **TryHackMe** (thm.io): salas guiadas, nivel principiante, muy didáctico.
- **PicoCTF**: orientado a estudiantes, excelente para criptografía y reversing básico.
- **PortSwigger Web Security Academy**: gratuito, el mejor recurso para seguridad web (OWASP Top 10 con labs interactivos).

### Asegura tus propios proyectos
- Aplica threat modeling básico a tu **app web**: ¿qué pasa si alguien accede a la API sin auth? ¿Los endpoints validan permisos por usuario?
- Revisa que no hay secretos en tu repo (ver [[05-identidad-auth-y-secretos]]).
- Activa MFA en GitHub, correo y cualquier servicio crítico.

### Lectura recomendada
- "The Web Application Hacker's Handbook" — referencia clásica.
- OWASP Top 10 (gratuito en owasp.org) — empezar por aquí para web.
- "Hacking: The Art of Exploitation" — si quieres entender a bajo nivel (C, shellcode, memoria).

---

## Conexiones

- [[MOC_Ciberseguridad]]
- [[02-criptografia]]
- [[03-seguridad-de-redes]]
- [[04-seguridad-web-owasp]]
- [[05-identidad-auth-y-secretos]]
- [[06-seguridad-de-sistemas-y-hardening]]
- [[07-pentesting-y-ciclo-del-ataque]]
- [[09-devsecops-y-appsec]]
- [[10-blue-team-y-respuesta-incidentes]]
- [[11-privacidad-y-opsec]]
- [[12-aprender-y-carrera]]
- [[MOC_CS_Fundamentos]]
- [[MOC_Desarrollo_Software]]
