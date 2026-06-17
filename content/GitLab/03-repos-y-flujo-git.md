---
title: Repositorios y flujo git en GitLab
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/git, programacion/control-versiones]
type: nota
status: en-progreso
source: claude-code
aliases: [gitlab-repos, flujo-git-gitlab, git-workflow-gitlab]
---

# Repositorios y flujo Git en GitLab

## ¿Por qué importa esto?

Un repositorio Git es solo un árbol de versiones. GitLab añade la capa social y de proceso encima: quién puede tocar qué rama, cómo se propone un cambio, cómo se aprueba, cómo se etiqueta una versión. El flujo que elijas aquí **determina la velocidad del equipo, el riesgo de regresar bugs y la legibilidad del historial**. Conocer los tres modelos principales te hace transferible a cualquier empresa, porque es el lenguaje común de los equipos de software.

---

## Anatomía de un repositorio GitLab

### Qué contiene un repo (más allá del código)

Cuando creas un proyecto en GitLab (ver [[02-conceptos-grupos-proyectos-permisos]]), obtienes automáticamente:

| Elemento | Descripción rápida |
|---|---|
| **Repositorio Git** | El historial de commits, ramas y tags |
| **Default branch** | La rama "oficial" (normalmente `main`) |
| **Protected branches** | Ramas con restricciones de escritura/merge |
| **Tags** | Punteros inmutables a commits (base de las releases) |
| **Issues / MRs** | Vinculados al repositorio (cierre automático con commits) |

### Default branch

La rama que Git y GitLab consideran "la verdad". Efectos concretos:
- Es la rama que clonas por defecto (`git clone`)
- Es la que muestra la UI al entrar al proyecto
- Es desde donde parten las reglas de CI/CD si no se configura otro trigger
- GitLab la protege automáticamente (no permite force-push)

> Se puede cambiar en **Settings → Repository → Default branch**. Hazlo antes de que alguien clone por primera vez, para no crear confusión con historiales divergentes.

---

## Protected Branches — el guardián del código estable

### El problema que resuelven

Sin protección, cualquier desarrollador con acceso `Developer` puede hacer `git push --force origin main` y **reescribir el historial de todos**. Las protected branches son reglas que impiden eso.

### Qué puedes controlar

| Regla | Descripción |
|---|---|
| **Allowed to merge** | Quién puede cerrar un Merge Request a esta rama (rol mínimo: Maintainer, Developer, nadie) |
| **Allowed to push and merge** | Quién puede hacer push directo sin MR |
| **Allowed to force push** | Casi siempre: nadie (desactívalo siempre en `main`) |
| **Code owner approval** | Requiere aprobación del propietario del archivo (definido en `CODEOWNERS`) |

### Configuración mínima recomendada para cualquier proyecto

```
main (o master):
  - Allowed to merge: Maintainers
  - Allowed to push: No one
  - Force push: desactivado

develop (si usas Git Flow):
  - Allowed to merge: Developers + Maintainers
  - Allowed to push: No one
  - Force push: desactivado
```

> En **Settings → Repository → Protected branches** puedes añadir un patrón como `release/*` para proteger todas las ramas de release de golpe.

---

## Modelos de flujo de ramas — el núcleo de la decisión

Antes de escribir una línea de código en equipo, hay que decidir **cómo se ramifica**. No hay una respuesta universal; hay trade-offs.

### Comparativa de los tres modelos principales

| Criterio | **Trunk-Based Development** | **GitLab Flow** | **Git Flow** |
|---|---|---|---|
| Número de ramas largas | 1 (`main`) | 2-3 (`main` + `production` + opcional `staging`) | 5 mínimo (`main`, `develop`, `feature/*`, `release/*`, `hotfix/*`) |
| Frecuencia de integración | Varias veces al día | Cada MR aprobado | Cuando `develop` está listo para release |
| Adecuado para | Equipos con CI/CD maduro y feature flags | Proyectos web con varios entornos | Software con versiones paralelas (SemVer estricto) |
| Complejidad de merge | Baja | Media | Alta (cherry-picks, backports) |
| Riesgo de "merge hell" | Muy bajo | Bajo | Alto si las features duran semanas |
| Requiere feature flags | Sí (para features incompletas en `main`) | Opcional | No |

### Trunk-Based Development

**Una sola rama larga**. Los desarrolladores integran a `main` al menos una vez al día, en commits pequeños. Las features incompletas se ocultan con feature flags (un `if (featureEnabled("nuevo-dashboard"))` en código).

```
main  ●─────●─────●─────●─────●   ← todos integran aquí
       ↑     ↑     ↑
    Dev A  Dev B  Dev A  (branches de horas, no días)
```

**Cuándo usarlo:** equipos con cobertura de tests alta, CI que corre en minutos y capacidad de hacer feature flags. Startups de software web. Común en Google, Facebook.

**Cuándo NO:** equipos pequeños sin tests, software embebido con releases largas, proyectos donde el cliente controla cuándo se despliega.

### GitLab Flow (recomendado como punto de entrada)

Diseñado por el propio GitLab. Añade ramas de entorno (`staging`, `production`) sobre trunk-based. El código solo llega a producción cuando se promueve de rama en rama.

```
feature/login ──────────────────── MR ──────►
                                            main ──── MR ──► production
feature/dashboard ──────────────── MR ──────►
```

El flujo concreto:
1. Creas `feature/mi-cambio` desde `main`
2. Haces commits y abres un Merge Request a `main`
3. Se aprueba, se mergea → CI despliega a staging
4. Cuando staging es estable, se abre MR de `main` a `production`
5. Merge a `production` → CI despliega a producción

**Cuándo usarlo:** proyectos web con al menos dos entornos (staging + prod), equipos de 3-20 personas, cuando quieres más control que trunk-based sin la burocracia de Git Flow.

### Git Flow

El modelo clásico de Vincent Driessen (2010). Dos ramas permanentes (`main` y `develop`) y tres tipos de ramas temporales.

```
main      ●────────────────────────────●─────●
           \                          /     /
develop     ●────●────●────────────●       /
                  \         /           /
feature/X          ●───────●           /
                                      /
release/1.0        ●─────────────●───●
                                  \
hotfix/critical                    ●────●
```

**Cuándo usarlo:** librerías con SemVer (`1.2.3`), software con instalaciones en cliente (no puedes actualizar todos a la vez), proyectos con soporte a múltiples versiones simultáneas (ej. LTS).

**Cuándo NO:** aplicaciones web con despliegue continuo. El overhead de ramas y cherry-picks mata la velocidad.

---

## Tags y Releases

### Tags — punteros inmutables al historial

Un tag en Git es como un marcador en el tiempo: apunta a un commit específico y **no se mueve**. Esto los hace ideales para marcar versiones.

```bash
# Crear un tag ligero (solo apunta al commit)
git tag v1.0.0

# Crear un tag anotado (tiene autor, fecha, mensaje — recomendado para releases)
git tag -a v1.0.0 -m "Release 1.0.0: primera versión estable"

# Subir el tag a GitLab
git push origin v1.0.0

# Subir todos los tags pendientes
git push origin --tags
```

**Convenio SemVer:** `v{MAJOR}.{MINOR}.{PATCH}`
- `MAJOR`: cambio incompatible con versión anterior
- `MINOR`: nueva funcionalidad compatible hacia atrás
- `PATCH`: corrección de bug compatible hacia atrás

### Releases en GitLab

Una Release es un tag + assets (binarios, changelogs, links). Se crea desde:
- **UI:** Repository → Tags → Create release
- **API de GitLab:** útil para automatizarlo desde CI/CD
- **`.gitlab-ci.yml`** con el job `release`:

```yaml
# Fragmento de .gitlab-ci.yml para crear release automática
release_job:
  stage: release
  image: registry.gitlab.com/gitlab-org/release-cli:latest
  rules:
    - if: $CI_COMMIT_TAG  # Solo corre cuando hay un tag
  script:
    - echo "Creando release para $CI_COMMIT_TAG"
  release:
    tag_name: $CI_COMMIT_TAG
    name: "Release $CI_COMMIT_TAG"
    description: "$(cat CHANGELOG.md)"  # O texto estático
```

> La variable `$CI_COMMIT_TAG` es inyectada por GitLab cuando el pipeline se dispara por un tag. Ver [[05-gitlab-cicd-fundamentos]] para entender las variables de CI.

---

## El flujo de trabajo diario: rama → push → Merge Request

Este es el ciclo que repites decenas de veces en un proyecto real.

### Paso a paso

```bash
# 1. Sincroniza tu main local con el remoto
git checkout main
git pull origin main

# 2. Crea tu rama de feature desde main (nombre descriptivo con prefijo)
git checkout -b feature/autenticacion-jwt
# Convención de nombres:
#   feature/   → nueva funcionalidad
#   fix/       → corrección de bug
#   hotfix/    → fix urgente en producción
#   chore/     → mantenimiento (deps, lint, refactor)
#   docs/      → solo documentación

# 3. Trabaja: haz commits pequeños y con mensaje descriptivo
git add src/auth/jwt.py
git commit -m "feat(auth): añadir validación de JWT en middleware"
# Sigue Conventional Commits: tipo(scope): descripción
# Tipos: feat, fix, docs, chore, refactor, test, ci

# 4. Sube la rama a GitLab
git push origin feature/autenticacion-jwt

# 5. GitLab te sugiere crear un MR → ábrelo desde la UI o con la URL que imprime
# Para abrir MR directamente desde CLI:
git push origin feature/autenticacion-jwt -o merge_request.create \
  -o merge_request.target=main \
  -o merge_request.title="feat(auth): autenticación JWT" \
  -o merge_request.remove_source_branch
```

### Qué ocurre en el Merge Request (resumen)

Ver [[04-merge-requests-y-code-review]] para el detalle completo. En síntesis:

1. El MR dispara el **pipeline de CI** (tests, lint, build)
2. Los revisores hacen **code review** con comentarios inline
3. Si todo pasa: **merge** (estrategia configurable: merge commit, squash, fast-forward)
4. La rama de feature se elimina (activar "Delete source branch" en el MR)
5. Si cerraste un issue con `Closes #42` en el mensaje del MR, **el issue se cierra solo**

### Estrategias de merge — cuál elegir

| Estrategia | Resultado | Cuándo |
|---|---|---|
| **Merge commit** | Preserva el historial de la branch + commit de merge | Features grandes, historial trazable |
| **Squash and merge** | Todos los commits de la branch → 1 solo commit | Features pequeñas, historial limpio en `main` |
| **Fast-forward** | Sin commit de merge; historial lineal | Proyectos que priorizan historial lineal, requiere rebase previo |

> Configura la estrategia por defecto en **Settings → Merge requests → Merge method**. Squash es buena opción por defecto para equipos medianos.

---

## Errores comunes

| Error | Causa | Solución |
|---|---|---|
| `remote: GitLab: You are not allowed to push code to protected branches` | Intentaste hacer push directo a `main` | Crea una branch y abre un MR |
| `Updates were rejected because the tip of your current branch is behind` | Alguien mergeó antes que tú | `git pull --rebase origin main` en tu branch, luego push |
| Tags duplicados en remoto | Creaste el tag localmente con el mismo nombre que ya existe | `git push origin :refs/tags/v1.0.0` (borra remoto) y vuelve a subir |
| MR con miles de líneas cambiadas | Feature demasiado grande, reviews imposibles | Divide en MRs más pequeños ("stacked MRs") |
| Ramas antiguas sin mergear acumuladas | Nadie las limpia | GitLab puede auto-borrar ramas al mergear; también hay `git remote prune origin` |

---

## Aplícalo a tus proyectos

### app web (React + FastAPI + Docker)

- Usa **GitLab Flow** con ramas `main` (staging auto) y `production`
- Protege `main` y `production`: solo Maintainer puede mergear
- Prefijos de rama: `feature/`, `fix/`, `chore/`
- Tags en cada release desplegada a producción: `v0.1.0`, `v0.2.0`...
- En el MR de cada feature, añade `Closes #<issue>` para cerrar automáticamente el issue del tablero

### proyecto embebido (PlatformIO / embebido)

- Considera **Git Flow**: el firmware tiene versiones numeradas que el hardware físico debe soportar
- `develop` para integración continua de features de sensores
- `release/1.x` para preparar firmwares estables
- Tags obligatorios antes de flashear a dispositivos en campo: `fw-v1.2.0`
- Protected branches especialmente importante: un push accidental a `main` podría desplegar firmware incorrecto

---

## Conexiones

- [[MOC_GitLab]]
- [[01-que-es-gitlab]]
- [[02-conceptos-grupos-proyectos-permisos]]
- [[04-merge-requests-y-code-review]]
- [[05-gitlab-cicd-fundamentos]]
- [[09-issues-tableros-y-gestion]]
- [[MOC_Desarrollo_Software]]
