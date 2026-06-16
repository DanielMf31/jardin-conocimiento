---
title: DevSecOps y seguridad de aplicaciones
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, devsecops, appsec, cicd, supply-chain]
type: nota
status: en-progreso
source: claude-code
aliases: [DevSecOps, AppSec, seguridad-en-el-ciclo-de-desarrollo]
---

# 🔒 DevSecOps y seguridad de aplicaciones

## ¿Por qué existe este campo?

El software se construye rápido — sprints de 2 semanas, decenas de dependencias externas, pipelines automáticos que despliegan a producción sin intervención humana. El problema: **la seguridad se solía añadir al final**, como una inspección de calidad antes de entregar. Esto es tardío, caro y poco eficaz.

**DevSecOps** (Development + Security + Operations) es la respuesta: integrar la seguridad como una actividad continua dentro del ciclo de vida del software, exactamente igual que los tests unitarios o el linting. No es un rol ni un equipo — es una cultura y un conjunto de prácticas automatizadas.

> Si un bug de seguridad se detecta en producción, cuesta ~100x más arreglarlo que si se detecta en code review. (Regla de los órdenes de magnitud del NIST.)

---

## 🗺️ Panorama: dónde encaja cada herramienta

```
Código fuente        →  SAST (análisis estático)
                     →  Secrets scanning
                     →  SCA (dependencias / licencias)
                         ↓
Build / CI pipeline  →  DAST (análisis dinámico contra app en ejecución)
                     →  Container scanning
                     →  SBOM generation + firma
                         ↓
Staging / Prod       →  Runtime protection (RASP, WAF)
                     →  Monitorización continua
```

La idea central: **detectar lo antes posible** (shift-left), **no solo al final**.

---

## 1. 🔄 Secure SDLC y "Shift-Left"

**SDLC** (Software Development Life Cycle) es el ciclo de vida del software: requisitos → diseño → desarrollo → pruebas → despliegue → mantenimiento.

**Shift-left** significa mover las actividades de seguridad hacia la izquierda del ciclo (más temprano), en lugar de dejarlas para el final.

### Fases del Secure SDLC

| Fase | Actividad de seguridad | Responsable principal |
|---|---|---|
| Requisitos | Definir requisitos de seguridad y privacidad | Product Owner + Security |
| Diseño | **Threat modeling** (modelado de amenazas) | Arquitecto + Dev |
| Desarrollo | SAST, secrets scanning, code review | Developer |
| Build / CI | SCA, DAST, container scanning | CI/CD pipeline |
| Despliegue | Hardening de infra, secretos en vault | DevOps / SecOps |
| Producción | Monitorización, SIEM, respuesta a incidentes | Blue team |

El "shift-left" no elimina la seguridad en producción — la complementa. Un error común es pensar que automatizar SAST en CI es suficiente; el SDLC seguro cubre todas las capas.

---

## 2. 🔍 SAST — Análisis Estático (Static Application Security Testing)

**Qué es**: Analizar el código fuente (o bytecode compilado) **sin ejecutarlo** para encontrar patrones que representen vulnerabilidades conocidas.

**Qué detecta bien**:
- Inyecciones SQL hardcodeadas (`"SELECT * FROM users WHERE id=" + input`)
- Uso de funciones peligrosas (`strcpy`, `eval`, `exec`)
- Secretos en el código (aunque los secrets scanners son más especializados)
- Flujos de datos no saneados (taint analysis)

**Limitaciones**:
- Alta tasa de **falsos positivos** — el analizador no entiende contexto de negocio
- No detecta vulnerabilidades de configuración ni lógica de negocio
- No ve cómo interactúan componentes externos (base de datos, APIs de terceros)

**Herramientas comunes**:
- `Semgrep` — reglas open-source, muy extensible, fácil de integrar en CI
- `SonarQube` / `SonarCloud` — plataforma más completa, buena para equipos
- `Bandit` — Python específico
- `CodeQL` — de GitHub, muy potente para C/C++/Java/Python/JS
- GitLab SAST — integrado en pipelines `.gitlab-ci.yml` → ver [[MOC_GitLab]]

**En CI/CD (ejemplo conceptual con Semgrep)**:
```yaml
# .gitlab-ci.yml o GitHub Actions
sast:
  stage: test
  script:
    - semgrep --config=auto --error .
  allow_failure: false  # romper el pipeline si hay findings críticos
```

---

## 3. 🌐 DAST — Análisis Dinámico (Dynamic Application Security Testing)

**Qué es**: Atacar la **aplicación en ejecución** como lo haría un atacante externo, sin acceso al código fuente. El escáner envía peticiones HTTP malformadas y observa las respuestas.

**Diferencia clave con SAST**:
- SAST lee el código → ve el problema desde dentro
- DAST prueba la app viva → ve el problema desde fuera (perspectiva del atacante)

**Qué detecta bien**:
- XSS (Cross-Site Scripting)
- Inyecciones (SQL, comandos) que se manifiestan en la respuesta HTTP
- Problemas de configuración (cabeceras de seguridad ausentes, TLS débil)
- Exposición de rutas no documentadas

**Limitaciones**:
- Necesita una instancia viva de la app (staging, no producción directa)
- Más lento que SAST (envía peticiones reales)
- Puede generar carga o datos basura en la base de datos

**Herramientas comunes**:
- `OWASP ZAP` (Zed Attack Proxy) — open source, integrable en CI
- `Burp Suite` — estándar de la industria para pentesters (versión Community gratuita)
- `Nikto` — scanner de configuraciones web
- GitLab DAST — integrado, lanza ZAP automáticamente

**Flujo típico en CI**:
```
Deploy a staging → ejecutar DAST → revisar report → merge a main
```

---

## 4. 📦 SCA — Análisis de Composición de Software (Software Composition Analysis)

**Qué es**: Auditar las **dependencias de terceros** (librerías, paquetes npm/pip/maven) para detectar vulnerabilidades conocidas (CVEs) y problemas de licencias.

**Por qué importa**: El código que escribes es una fracción pequeña de lo que ejecutas. Un proyecto Python típico tiene 50-200 dependencias transitivas (dependencias de dependencias). Si una de ellas tiene una CVE crítica, tu app es vulnerable aunque tu código sea perfecto.

> Ejemplo real: Log4Shell (CVE-2021-44228) afectó a millones de apps Java porque todas usaban Log4j, muchas sin saberlo directamente (era dependencia transitiva).

**Qué analiza**:
- Vulnerabilidades en paquetes directos y transitivos
- Licencias incompatibles (ej: una librería GPL en un proyecto propietario)
- Versiones obsoletas con soporte terminado (EOL)

**Herramientas**:
- `Dependabot` (GitHub) — abre PRs automáticamente cuando hay CVEs
- `Snyk` — SCA + SAST + container scanning
- `OWASP Dependency-Check` — open source, soporta Java, .NET, Python, etc.
- `pip-audit` — Python
- `npm audit` — Node.js (integrado en npm)
- GitLab Dependency Scanning — integrado en CI

**En la práctica**:
```bash
# Python
pip-audit

# Node.js
npm audit --audit-level=high

# Revisar solo vulnerabilidades críticas y altas, no bloquear por low
```

---

## 5. 🕵️ Secrets Scanning

**Qué es**: Detectar credenciales, tokens, API keys, contraseñas o cualquier secreto hardcodeado en el código o en el historial de git.

**Por qué es crítico**: Un secreto en el repositorio es una brecha inmediata. GitHub indexa repositorios públicos en segundos; existen bots que los escanean continuamente. Incluso en repositorios privados, un exfiltrado del repo expone todos los secretos del historial.

**Regla de oro**: **Un secreto que tocó git está comprometido**. No basta con borrarlo en un commit posterior — queda en el historial. Hay que rotarlo (generar uno nuevo e invalidar el antiguo).

**Herramientas**:
- `git-secrets` — prevención pre-commit (bloquea el commit si detecta patrones)
- `truffleHog` — escanea historial completo de git, detecta entropía alta (señal de secretos)
- `detect-secrets` (Yelp) — crea un baseline y alerta de nuevas adiciones
- `gitleaks` — muy usado en CI, rápido
- GitLab Secret Detection — integrado en pipelines

**Pre-commit hook (prevención local)**:
```bash
# Instalar pre-commit
pip install pre-commit

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/zricethezav/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

**Si ya está en el historial**:
1. Rotar el secreto inmediatamente (invalidar el antiguo)
2. Usar `git filter-repo` o BFG Repo Cleaner para reescribir la historia
3. Forzar a todos los colaboradores a hacer `git clone` de nuevo
4. Auditar quién tuvo acceso al repo para evaluar el impacto

---

## 6. 🔗 Supply Chain Security

**Qué es**: La seguridad de la **cadena de suministro** de software — todo lo que viene de fuera: dependencias, imágenes base de contenedores, herramientas de build, plugins del CI.

**El problema**: Cuando instalas `npm install axios` o `pip install requests`, confías en que ese paquete y todos los que instala a su vez son seguros. Un atacante puede comprometer esa cadena de varias formas.

### Vectores de ataque en la supply chain

| Ataque | Descripción | Ejemplo real |
|---|---|---|
| **Typosquatting** | Publicar paquete con nombre casi igual al legítimo | `colourama` vs `colorama` en PyPI |
| **Dependency confusion** | Nombre de paquete interno coincide con uno público malicioso | Ataque de Alex Birsan (2021) |
| **Compromiso del upstream** | El paquete legítimo es hackeado en su cuenta | `event-stream` (npm, 2018) |
| **Malicious PR** | Contribución maliciosa aceptada en un proyecto OSS | XZ Utils (2024, CVE-2024-3094) |
| **Build tool hijack** | Comprometer el CI/CD en sí | SolarWinds (2020) |

### Mitigaciones

**1. Pinning de versiones exactas**:
```
# Malo: instala "cualquier versión compatible"
requests>=2.0

# Bueno: versión exacta + hash de integridad
requests==2.31.0 --hash=sha256:abcdef...
```

**2. SBOM (Software Bill of Materials)**:
Un inventario estructurado de todos los componentes de tu software (nombre, versión, licencia, proveedor). Formatos estándar: **SPDX** y **CycloneDX**.

```bash
# Generar SBOM para Python con syft
syft . -o spdx-json > sbom.json

# Para imagen Docker
syft nginx:latest -o cyclonedx-json > sbom-image.json
```

Sirve para: auditorías de seguridad, cumplimiento (Executive Order 14028 en EEUU lo exige para software gubernamental), respuesta rápida ante incidentes (¿usamos Log4j? ¿en qué versión?).

**3. Firma de artefactos (Sigstore / Cosign)**:
```bash
# Firmar imagen de contenedor
cosign sign --key cosign.key ghcr.io/user/myapp:latest

# Verificar firma antes de desplegar
cosign verify --key cosign.pub ghcr.io/user/myapp:latest
```

**4. Política de dependencias**:
- Preferir dependencias con alta actividad de mantenimiento
- Revisar el número de mantenedores (un único mantenedor = riesgo)
- Evaluar reputación antes de añadir una dependencia nueva

---

## 7. ⚙️ Seguridad en pipelines CI/CD

El pipeline de CI/CD es infraestructura crítica. Quien controla el pipeline puede modificar lo que se despliega. Es un vector de ataque de alto valor.

### Principios de seguridad en CI/CD

**Least privilege (mínimo privilegio)**:
- Los runners del CI no deben tener acceso a producción directamente
- Separar credenciales por entorno: el pipeline de staging no debe poder desplegar en producción

**Secretos en CI**:
- Usar el gestor de secretos del CI (GitHub Secrets, GitLab CI Variables protegidas) — nunca hardcodear en el `.yml`
- Marcar variables como `masked` (no aparecen en logs) y `protected` (solo en ramas protegidas)
- Preferir OIDC / Workload Identity Federation sobre credenciales estáticas (el CI obtiene tokens temporales, no hay secreto que robar)

**Principio de inmutabilidad**:
- Pinear las versiones de las actions/jobs de terceros al **hash SHA del commit**, no a un tag (los tags son mutables)
```yaml
# Malo: el tag v3 puede moverse a un commit diferente
- uses: actions/checkout@v3

# Bueno: hash inmutable
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
```

**Separación de entornos**:
```
feature branch → build + SAST + tests unitarios
main branch    → todo lo anterior + DAST + SCA + deploy a staging
tag/release    → sign + SBOM + deploy a producción (con aprobación manual)
```

**Auditoría**:
- Registrar qué cambios se desplegaron, cuándo y por qué pipeline
- Alertar si alguien modifica el `.gitlab-ci.yml` o el `Dockerfile` fuera del proceso normal

---

## 8. 🧩 Threat Modeling de aplicaciones

**Qué es**: Un proceso estructurado para identificar, antes de escribir código (o al diseñar una feature), qué puede salir mal desde el punto de vista de seguridad.

**Por qué hacerlo**: Es la actividad de seguridad más barata en relación al impacto. Descubrir en la fase de diseño que una API expone datos sensibles cuesta horas; descubrirlo en producción después de una brecha cuesta meses y reputación.

### Marco STRIDE

El más utilizado. Clasifica las amenazas en 6 categorías:

| Letra | Amenaza | Propiedad violada | Ejemplo |
|---|---|---|---|
| **S** | Spoofing (suplantación) | Autenticación | Falsificar un JWT |
| **T** | Tampering (manipulación) | Integridad | Modificar un request en tránsito |
| **R** | Repudiation (repudio) | No-repudio | Un usuario niega haber hecho una acción |
| **I** | Information disclosure | Confidencialidad | Stack trace con rutas internas expuesto |
| **D** | Denial of Service | Disponibilidad | Flood de requests a una API sin rate limiting |
| **E** | Elevation of privilege | Autorización | Un usuario normal accede a endpoint de admin |

### Proceso mínimo (4 pasos)

1. **Diagramar el sistema**: DFD (Data Flow Diagram) — qué datos fluyen entre qué componentes, dónde están los límites de confianza (trust boundaries)
2. **Identificar amenazas**: Para cada flujo y componente, aplicar STRIDE
3. **Priorizar**: Por probabilidad × impacto (CVSS simplificado)
4. **Mitigar o aceptar**: Decidir un control para cada amenaza, o documentar por qué se acepta el riesgo

**Herramientas**:
- `OWASP Threat Dragon` — diagramas DFD con amenazas integradas (open source)
- Microsoft Threat Modeling Tool — bueno para arquitecturas Microsoft
- `Threatspec` — amenazas como anotaciones en el código

**Ejemplo de DFD simplificado (texto)**:
```
[Usuario] --HTTPS--> [API Gateway] ---> [App Server] ---> [DB]
             ^                ^
             |                |
        Trust boundary    Trust boundary
    (internet / interno)  (app / datos)
```
Para cada flecha y caja: ¿qué pasa si este canal es interceptado? ¿si este componente es comprometido?

---

## 9. 🛡️ Cómo prevenirlo — resumen práctico

| Problema | Control principal | Herramienta sugerida |
|---|---|---|
| Vulnerabilidad en mi código | SAST en PR | Semgrep, CodeQL |
| Vulnerabilidad en dependencias | SCA + Dependabot | pip-audit, Snyk |
| Secreto en el código | Secrets scanning pre-commit | gitleaks, detect-secrets |
| Dependencia maliciosa | Pinning + SBOM + verificar hashes | syft, pip hash |
| Pipeline comprometido | Mínimo privilegio + OIDC + pin SHA | Configuración CI |
| Diseño inseguro | Threat modeling antes de implementar | OWASP Threat Dragon |
| App con vulnerabilidades en runtime | DAST en staging | OWASP ZAP |

---

## Errores comunes

- **"SAST es suficiente"**: No — SAST solo ve el código propio; necesitas SCA para dependencias y DAST para la app real.
- **Ignorar dependencias transitivas**: La vulnerabilidad raramente está en el paquete directo que instalaste, sino en sus dependencias.
- **Secrets en variables de entorno del sistema de CI pero sin marcar como masked**: Aparecen en los logs en texto plano.
- **Tratar todos los findings como bloqueantes**: El 60-70% de findings de SAST pueden ser falsos positivos. Define severidades mínimas para bloquear (Critical, High) y registra los aceptados.
- **No rotar secretos después de una exposición**: Borrar el secreto del historial no lo invalida en el servicio externo.
- **Pipelines con permisos de producción en todos los branches**: Un branch de feature comprometido puede desplegar a producción.

---

## 🧪 Aplícalo / practica

### En tus propios proyectos
- Añade `pip-audit` o `npm audit` al CI de la y revisa los findings actuales
- Configura `gitleaks` como pre-commit hook en todos tus repositorios
- Genera un SBOM de la imagen Docker de tu app (`syft`) y guárdalo como artefacto del pipeline
- Haz un threat modeling de 1 hora sobre la API de producto: dibuja el DFD y aplica STRIDE

### CTFs y labs
- **WebGoat** (OWASP) — app deliberadamente vulnerable para practicar SAST/DAST conceptualmente
- **Juice Shop** (OWASP) — app con vulnerabilidades reales, buena para probar ZAP contra ella en local
- **HackTheBox / TryHackMe** — salas de DevSecOps y AppSec (buscar "CI/CD", "supply chain")
- **SLSA Framework** (slsa.dev) — leer los niveles y entender qué garantías da cada uno sobre la supply chain

### Explorar GitLab Security
- Activar el pipeline de SAST y Dependency Scanning en un proyecto propio (ver [[MOC_GitLab]])
- Revisar el Security Dashboard de GitLab y entender los campos: severity, confidence, location

---

## Conexiones

- [[MOC_Ciberseguridad]]
- [[MOC_GitLab]] — Security scanning integrado en pipelines `.gitlab-ci.yml`
- [[MOC_Desarrollo_Software]] — SDLC, CI/CD, arquitectura de aplicaciones
- [[07-pentesting-y-ciclo-del-ataque]] — el DAST tiene raíces en técnicas de pentesting
- [[04-seguridad-web-owasp]] — las vulnerabilidades que detecta DAST/SAST (XSS, SQLi, etc.)
- [[05-identidad-auth-y-secretos]] — gestión de secretos: vaults, rotación, OIDC
- [[08-vulnerabilidades-y-explotacion]] — CVEs, CVSS, cómo se puntúan las vulnerabilidades que SCA encuentra
- [[10-blue-team-y-respuesta-incidentes]] — cuando una brecha de supply chain llega a producción
- [[06-seguridad-de-sistemas-y-hardening]] — hardening de la infra donde corren los pipelines
- [[01-fundamentos-y-mentalidad]] — por qué shift-left y defense-in-depth son la base filosófica de DevSecOps
