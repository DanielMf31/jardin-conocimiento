---
title: DevOps y CI/CD
date: 2026-06-13
tags: [programacion/agile, programacion/devops, programacion/cicd, programacion/automatizacion, programacion/infraestructura]
type: nota
status: en-progreso
source: claude-code
aliases: [DevOps, CI/CD, Integracion Continua]
---

# DevOps y CI/CD

## Por qué existe esto

En el modelo clásico, **Development** (los que escriben código) y **Operations** (los que despliegan y mantienen servidores) eran equipos separados con incentivos opuestos: Dev quería cambiar cosas rápido, Ops quería que nada se rompiese. El resultado: releases lentos, meses entre versiones, y despliegues que eran eventos de alto riesgo con rollback manual.

**DevOps** no es un cargo ni una herramienta. Es una cultura y un conjunto de prácticas para romper ese silo, acortar el ciclo feedback y entregar software de forma fiable y frecuente.

> Analogía hardware: imagina que diseño (quiere iterar) y fabricación (quiere estabilidad) no se hablan hasta el día de producción. DevOps es el equivalente a tener un proceso de prototipado rápido donde ambos equipos colaboran desde el día uno.

---

## El marco CALMS

CALMS es el acrónimo que resume los pilares de DevOps:

| Pilar | Qué significa | Ejemplo concreto |
|---|---|---|
| **C**ulture | Responsabilidad compartida dev+ops. "You build it, you run it." | El mismo equipo que escribe el código atiende las alertas de producción |
| **A**utomation | Automatizar todo lo repetible: tests, builds, deploys | Pipeline que despliega solo cuando pasan los tests |
| **L**ean | Eliminar desperdicio (trabajo sin valor), lotes pequeños | Commits pequeños frecuentes en lugar de un megamerge mensual |
| **M**easurement | Medir todo. Sin datos no hay mejora. | Tiempo de build, tasa de errores, frecuencia de deploy |
| **S**haring | Compartir conocimiento, postmortems, herramientas entre equipos | Runbooks públicos, retrospectivas abiertas |

---

## CI vs CD: el espectro de automatización

Estos tres términos se confunden constantemente. Son etapas de un continuo:

```
Commit → [CI] → Artefacto verificado → [CD Entrega] → Staging → [CD Despliegue] → Producción
```

### Integración Continua (CI — Continuous Integration)

Cada vez que alguien hace push a la rama principal (o abre un PR), se ejecuta automáticamente:

1. Compilación / build
2. Tests unitarios y de integración
3. Análisis estático (linting, tipos)
4. Reporte de cobertura

**Objetivo**: detectar que "tu código roto no me rompe a mí" en minutos, no en días. La integración es continua porque ocurre varias veces al día, no una vez al sprint.

**Regla de oro**: si el build está rojo, arreglarlo es la prioridad número uno de todo el equipo. Un build roto que nadie arregla destruye la confianza en el sistema.

### Entrega Continua (CD — Continuous Delivery)

Extiende CI: además de verificar, el pipeline genera un **artefacto desplegable** (imagen Docker, binario, zip) y lo promueve a un entorno de staging automáticamente. El despliegue a producción sigue siendo **manual** (un botón, una aprobación).

Garantía: en cualquier momento, hay un artefacto listo para producción que pasó todos los checks.

### Despliegue Continuo (CD — Continuous Deployment)

El paso más extremo: si todos los checks pasan, el código **llega a producción automáticamente**, sin intervención humana. Empresas como Amazon hacen decenas de miles de deploys al día así.

No siempre es el objetivo correcto. Requiere madurez alta en tests y observabilidad.

| Práctica | Despliegue a producción | Cuándo usarla |
|---|---|---|
| CI | Manual, ad-hoc | Mínimo viable para cualquier proyecto |
| Continuous Delivery | Manual (botón) | Mayoría de equipos de producto |
| Continuous Deployment | Automático | Alta madurez, excelente cobertura de tests |

---

## Qué es un Pipeline y sus etapas

Un **pipeline** (literalmente "tubería") es la secuencia ordenada de pasos automatizados que transforma un commit en software corriendo en producción. Cada paso recibe el output del anterior.

### Etapas típicas de un pipeline

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Source  │──▶│  Build   │──▶│  Test    │──▶│  Release │──▶│  Deploy  │
│ (commit) │   │(compilar │   │(unit,    │   │(empaquetar│  │(staging, │
│          │   │ lint)    │   │integ,e2e)│   │ imagen)  │   │ prod)    │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

**Source**: el trigger — un push, un PR, un tag de versión, o un cron job.

**Build**: compilar, instalar dependencias, construir la imagen Docker. Si falla aquí, el código ni siquiera arranca.

**Test**: la etapa más crítica. Se suele estructurar en capas por velocidad:
- Tests unitarios (segundos) — primero, fallan rápido
- Tests de integración (minutos) — comprueban que los módulos encajan
- Tests E2E / smoke tests (más lentos) — simulan un usuario real

**Release**: empaquetar el artefacto versionado. En proyectos con Docker: `docker build` + `docker push` al registry.

**Deploy**: aplicar el artefacto al entorno. Puede incluir estrategias como:
- **Blue/Green**: dos entornos idénticos; cambias el tráfico de golpe de Blue a Green. Rollback instantáneo.
- **Canary**: mandas el 5% del tráfico a la nueva versión, observas métricas, y vas subiendo. Rollback granular.
- **Rolling update**: reemplazas instancias una a una. El estándar en Kubernetes.

---

## Infraestructura como Código (IaC)

**Problema**: si configuras tu servidor a mano (por SSH, por consola web), esa configuración es conocimiento tácito. No es reproducible, no está versionada, y si el servidor muere, tardas horas en reconstruirlo.

**IaC** (Infrastructure as Code) significa describir la infraestructura en archivos de texto versionados en git, igual que el código de la aplicación.

```
# Ejemplo Terraform — crear una instancia en AWS
resource "aws_instance" "api_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  tags = { Name = "api-prod" }
}
```

Herramientas principales:

| Herramienta | Nivel | Uso típico |
|---|---|---|
| **Terraform** | Infraestructura (VMs, redes, DBs) | Provisionar recursos en cloud |
| **Ansible** | Configuración (qué tiene instalado el server) | Idempotente, sin agente |
| **Docker Compose** | Entorno local multi-contenedor | Desarrollo y staging simple |
| **Helm** | Aplicaciones en Kubernetes | Deploy de charts de K8s |

**Principio clave — idempotencia**: aplicar el mismo archivo IaC 10 veces debe producir el mismo resultado que aplicarlo una vez. Si el recurso ya existe con la configuración correcta, no hace nada.

---

## Feature Flags

**Feature flag** (también llamado feature toggle): un interruptor en el código que activa o desactiva funcionalidad en runtime, sin necesidad de un nuevo deploy.

```python
# Pseudocódigo
if feature_flags.is_enabled("nuevo_dashboard", user_id):
    return render_new_dashboard()
else:
    return render_old_dashboard()
```

Para qué sirven:

- **Trunk-based development**: merge código incompleto a main sin que los usuarios lo vean. Separas "deploy" de "release".
- **Canary releases controladas**: activas la feature solo para el 10% de usuarios, sin tocar la infraestructura.
- **Kill switch**: si algo falla en producción, apagas la feature en segundos sin rollback de código.
- **Testing A/B**: muestras variante A a la mitad de usuarios, variante B a la otra mitad.

Cuándo NO usar feature flags: para experimentos permanentes que nunca se limpian. Los flags acumulados se convierten en deuda técnica. Cada flag tiene fecha de expiración.

---

## Observabilidad: saber qué pasa en producción

**Monitorización** te dice si algo está roto. **Observabilidad** te permite entender *por qué* está roto, incluso ante fallos que nunca habías visto antes.

Los tres pilares (las "tres trazas"):

### Logs

Registros de eventos discretos con timestamp. El más básico.

```
2026-06-13T10:23:45Z ERROR user_id=42 action=checkout msg="Payment gateway timeout"
```

Reglas de buen logging:
- Logs estructurados (JSON), no strings planos
- Nivel correcto: DEBUG para desarrollo, INFO para eventos normales, ERROR para fallos reales
- Incluir contexto (user_id, request_id, traza de correlación)
- No loguear datos sensibles (tokens, contraseñas)

Herramientas: ELK Stack (Elasticsearch + Logstash + Kibana), Loki + Grafana, CloudWatch.

### Métricas

Series temporales de valores numéricos agregados. Permiten dashboards y alertas.

Tipos fundamentales:
- **Counter**: solo sube (requests totales, errores totales)
- **Gauge**: sube y baja (uso de CPU, conexiones abiertas)
- **Histogram**: distribución de valores (latencia de requests por percentil)

Los **cuatro golden signals** de Google SRE para monitorizar cualquier servicio:

| Signal | Qué mide | Ejemplo |
|---|---|---|
| **Latency** | Tiempo de respuesta | p99 de requests < 500ms |
| **Traffic** | Demanda sobre el sistema | Requests por segundo |
| **Errors** | Tasa de fallos | % de HTTP 5xx |
| **Saturation** | Qué tan "lleno" está | CPU al 90%, cola de DB larga |

Herramienta estándar: Prometheus (recolección) + Grafana (visualización).

### Trazas Distribuidas

En un sistema de microservicios, una petición del usuario puede pasar por 10 servicios distintos. Un **trace** (traza) es el registro de todo ese viaje, con tiempos en cada salto.

```
Request usuario
  └─ API Gateway (12ms)
       └─ Auth Service (3ms)
       └─ Product Service (45ms)
            └─ Database query (40ms)  ← aquí está el cuello de botella
```

Herramienta estándar: OpenTelemetry (instrumentación) + Jaeger o Zipkin (visualización).

---

## Ejemplo real: pipeline con GitHub Actions

GitHub Actions es la opción más accesible para proyectos personales y equipos pequeños. Los pipelines se definen en archivos YAML dentro de `.github/workflows/`.

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-and-build:
    runs-on: ubuntu-latest  # runner: VM Ubuntu en la nube de GitHub

    steps:
      # 1. Descargar el código
      - name: Checkout código
        uses: actions/checkout@v4

      # 2. Instalar Python
      - name: Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      # 3. Instalar dependencias
      - name: Instalar dependencias
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      # 4. Linting
      - name: Lint con ruff
        run: ruff check .

      # 5. Tests con cobertura
      - name: Tests
        run: pytest --cov=app --cov-report=xml

      # 6. Build imagen Docker (solo en main, no en PRs)
      - name: Build Docker image
        if: github.ref == 'refs/heads/main'
        run: docker build -t mi-app:${{ github.sha }} .

      # 7. Push al registry (solo en main)
      - name: Push al registry
        if: github.ref == 'refs/heads/main'
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker push mi-app:${{ github.sha }}
```

**Puntos clave del ejemplo**:
- `on: pull_request` — corre CI en cada PR para verificar antes de mergear
- `if: github.ref == 'refs/heads/main'` — el build y push solo ocurren al llegar a main
- `secrets.DOCKER_PASSWORD` — los credentials nunca están en el código, viven en GitHub Secrets

---

## Cuándo aplicar cada práctica

| Situación | Mínimo recomendable |
|---|---|
| Proyecto personal / side project | CI con tests + linting en GitHub Actions |
| Equipo pequeño (2-5 devs) | CI + Continuous Delivery a staging |
| Producto con usuarios reales | Lo anterior + observabilidad básica (logs + métricas) |
| Equipo maduro / microservicios | CI/CD completo + IaC + trazas distribuidas + feature flags |

### Errores comunes

- **Pipeline que nunca falla**: si no has escrito tests que puedan fallar, el pipeline es teatro. Mide cobertura real.
- **Build verde = "está bien"**: CI solo verifica lo que tienes testeado. Un 30% de cobertura con CI verde no es garantía.
- **Secrets en el código**: el error más común al empezar. Usa variables de entorno y el sistema de secrets de tu plataforma (GitHub Secrets, AWS SSM).
- **Pipeline lentísimo**: si tarda 40 minutos nadie lo usará. Paraleliza jobs, usa cache de dependencias, separa tests lentos.
- **No limpiar feature flags**: acumulan complejidad. Cada flag debe tener dueño y fecha de revisión.
- **Observabilidad como afterthought**: instrumentar después de que algo falla en producción es tarde. Diseña los logs y métricas desde el principio.

---

## Aplícalo a tus proyectos

### app web (FastAPI + React + Docker)

El proyecto ya tiene Docker Compose. El siguiente paso natural:

1. **CI inmediato**: crea `.github/workflows/ci.yml` con:
   - `pytest` sobre el backend FastAPI
   - `npm run build` + `tsc --noEmit` sobre el frontend TypeScript
   - Lint: `ruff` (Python) + `eslint` (TS)

2. **Secrets**: el `.env` que tienes sin commitear es correcto. Mapea esas variables a GitHub Secrets para el pipeline.

3. **Observabilidad básica**: FastAPI ya emite logs estructurados. Añade `prometheus-fastapi-instrumentator` para exponer métricas en `/metrics` sin apenas código. Luego Prometheus + Grafana con un `docker-compose.override.yml`.

4. **Feature flag sencillo**: si quieres experimentar con una vista nueva del dashboard de producto, una variable de entorno `ENABLE_NEW_DASHBOARD=true` es un feature flag manual válido para empezar.

### proyecto embebido (PlatformIO / embebido)

El concepto aplica aunque el target sea hardware:

- CI que compila el firmware con PlatformIO en Actions: `pio run -e <environment>`
- Tests unitarios de la lógica (sin hardware) con `Unity` o `googletest` vía native environment
- Artefactos versionados: el `.bin` del firmware se sube como GitHub Release asset al crear un tag

---

## Conexiones

- [[MOC_Desarrollo_Software]]
- [[01-sdlc-e-historia]]
- [[02-manifiesto-agil]]
- [[07-practicas-de-ingenieria]]
- [[09-metricas-y-seguimiento]]
- [[11-equipo-retros-y-antipatrones]]
- [[12-herramientas-y-certificaciones]]
