---
title: Merge Requests y Code Review en GitLab
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, programacion/git, programacion/colaboracion]
type: nota
status: en-progreso
source: claude-code
aliases: [MR GitLab, merge request, code review GitLab]
---

# Merge Requests y Code Review

## Por qué existe esto (el problema que resuelve)

En un proyecto en solitario empujas directamente a `main`. En equipo eso es un desastre: nadie revisa el código, los errores llegan a producción, y nadie sabe qué cambió ni por qué.

Un **Merge Request (MR)** es la solución: es una **propuesta formal de integración de código** que abre un espacio de conversación antes de que nada llegue a la rama principal. Agrupa el diff del código, el contexto del cambio, la revisión por pares y la ejecución del pipeline, todo en un solo lugar.

> En GitHub se llama **Pull Request (PR)**. Mismo concepto, distinto nombre. Si vienes de GitHub, ya conoces el flujo; GitLab añade algunas capas de control (approvals, merge methods) que son especialmente útiles en equipos profesionales.

El MR no es solo una herramienta de fusión — es la **unidad de trabajo colaborativo** en GitLab. Aquí se detectan bugs, se comparte contexto, se aprende del código ajeno y se mantiene un historial de decisiones.

---

## 1. Crear un Merge Request

### El flujo típico

```
rama feature  →  push  →  abrir MR  →  review  →  aprobación  →  merge a main
```

1. Trabajas en una rama (ver [[03-repos-y-flujo-git]]).
2. Haces push de esa rama al repositorio remoto.
3. GitLab suele mostrarte un botón "Create merge request" directamente en la interfaz tras el push.

### Desde la UI

**GitLab > proyecto > Merge Requests > New merge request**

- **Source branch**: tu rama con los cambios.
- **Target branch**: la rama a la que quieres fusionar (normalmente `main` o `develop`).
- Rellenas el formulario de descripción (ver plantillas más abajo).

### Desde la terminal (atajo rápido)

Cuando haces push, GitLab imprime en la terminal un enlace directo para abrir el MR:

```bash
git push origin feature/login-oauth

# GitLab imprime algo como:
# remote: To create a merge request for feature/login-oauth, visit:
# remote:   https://gitlab.com/tu-grupo/tu-proyecto/-/merge_requests/new?...
```

Haces clic y te lleva al formulario ya pre-rellenado con la rama correcta.

### Campos clave del formulario

| Campo | Qué poner | Por qué importa |
|---|---|---|
| **Título** | Imperativo, concreto. Ej: `Add OAuth login with GitHub` | Es lo que verá el revisor de un vistazo |
| **Descripción** | Contexto, qué cambia, cómo probarlo | Sin esto el revisor tiene que adivinar |
| **Assignee** | Quien lo implementa (tú, normalmente) | Claridad de responsabilidad |
| **Reviewer** | Quien lo revisa | Necesario para los approval rules |
| **Labels** | `backend`, `bug`, `feature`, etc. | Filtrado en el tablero |
| **Milestone** | Sprint o versión objetivo | Planificación (ver [[09-issues-tableros-y-gestion]]) |

---

## 2. Draft / WIP: trabajo en progreso

### El problema

A veces quieres abrir un MR para que el pipeline corra o para pedir feedback temprano, pero **no está listo para mergearse todavía**. Si lo dejas abierto sin marcar, alguien podría fusionarlo por error.

### La solución: Draft

Prefija el título con `Draft:` (o el antiguo `WIP:`):

```
Draft: Add OAuth login with GitHub
```

Efecto: GitLab **bloquea el botón de merge** hasta que marques el MR como "Ready". Ningún approval rule puede saltarse este bloqueo.

Cuándo usarlo:
- Abres el MR pronto para feedback de diseño antes de terminar.
- El pipeline tarda y quieres que corra mientras sigues trabajando.
- Coordinas con otro desarrollador que debe hacer cambios dependientes.

Para pasar de Draft a listo: botón "Mark as ready" en la cabecera del MR, o quitar el prefijo del título.

---

## 3. Plantillas de descripción

### Por qué usar plantillas

Sin plantilla, cada MR tiene una descripción distinta (o vacía). Con plantilla, el equipo siempre incluye la misma información mínima: contexto, cómo probar, checklist de revisión.

### Cómo configurar una plantilla

Crea el archivo en tu repositorio:

```
.gitlab/merge_request_templates/Default.md
```

GitLab cargará automáticamente ese contenido en el campo de descripción al abrir un nuevo MR.

### Ejemplo de plantilla útil

```markdown
## ¿Qué cambia este MR?
<!-- Una o dos frases. Si el título ya lo dice, amplía el contexto aquí. -->

## Motivación / Problema que resuelve
<!-- Por qué es necesario este cambio. Enlaza el issue si existe: Closes #123 -->

## Cómo probarlo
<!-- Pasos para que el revisor pueda verificar el comportamiento -->
1.
2.

## Checklist autor
- [ ] Tests añadidos o actualizados
- [ ] Documentación actualizada si aplica
- [ ] No hay secretos hardcoded
- [ ] El pipeline pasa en local (`docker compose run --rm app pytest`)

## Notas para el revisor
<!-- Áreas donde quieres feedback específico, decisiones de diseño a discutir -->
```

La línea `Closes #123` es especial: cuando el MR se fusiona, GitLab **cierra automáticamente el issue** vinculado.

Puedes tener múltiples plantillas (`.gitlab/merge_request_templates/Feature.md`, `Bugfix.md`, etc.) y elegir cuál usar en el formulario.

---

## 4. Review: hilos y suggestions

### Hilos de comentarios (threads)

El revisor puede comentar en:
- Una línea específica del diff.
- Un bloque de varias líneas.
- El MR en general.

Los comentarios del diff se organizan como **hilos** (threads): tienen una conversación anidada y un estado (`open` / `resolved`). El autor puede marcar un hilo como resuelto cuando ha aplicado el cambio.

**Buena práctica**: GitLab puede configurarse para que el merge esté bloqueado hasta que todos los hilos estén resueltos (`Settings > Merge requests > All threads must be resolved`). Evita fusionar ignorando feedback.

### Suggestions: el superpoder del code review en GitLab

Un revisor puede proponer un cambio de código concreto directamente en el diff:

1. Selecciona líneas en el diff.
2. Hace clic en el icono de "Insert suggestion".
3. Edita el bloque de código en el comentario.

El resultado es un comentario con un bloque especial:

````markdown
```suggestion
const timeout = 5000; // ms
```
````

El autor del MR ve el diff de la suggestion y puede **aplicarla con un clic** ("Apply suggestion"), sin salir de la interfaz. GitLab crea el commit automáticamente.

También se pueden aplicar **múltiples suggestions en batch** ("Apply all suggestions") para no tener decenas de commits triviales.

Cuándo usar suggestions vs comentario libre:
- Typo, nombre de variable, formato → suggestion (el autor aplica en un clic, sin fricción).
- Cambio de arquitectura, pregunta conceptual → comentario libre (necesita discusión).

---

## 5. Approvals y approval rules

### Por qué los approvals

En un equipo de más de dos personas necesitas asegurarte de que alguien con criterio ha revisado el código antes de que llegue a `main`. Los approvals formalizan ese requisito.

### Approval rules

Se configuran en `Settings > Merge requests > Approval rules`:

| Tipo | Ejemplo | Uso |
|---|---|---|
| **Número mínimo de aprobadores** | 2 approvers cualquiera | Control básico |
| **Grupo/usuario específico** | El equipo de `backend` debe aprobar | Especialización |
| **Code owners** | El dueño del módulo afectado | Granularidad por fichero |

**CODEOWNERS**: creas el archivo `CODEOWNERS` en la raíz del repositorio y declaras quién es responsable de qué paths:

```
# Sintaxis: patrón   @usuario_o_grupo
/backend/             @backend-team
/frontend/            @frontend-team
*.sql                 @dba-team
```

Cuando un MR toca esos ficheros, GitLab añade automáticamente al dueño como revisor requerido.

### Estados de approval

- **Approved**: el revisor ha dado su visto bueno.
- **Pending**: esperando aprobación.
- **Revoked**: el revisor retiró su aprobación (ocurre automáticamente si el autor hace push de nuevos commits, si el proyecto está configurado así).

La opción "Reset approvals on push" es recomendable: evita que un MR aprobado antes de un cambio importante se fusione sin nueva revisión.

---

## 6. Métodos de merge

Cuando el MR está listo, tienes tres formas de fusionar. La elección afecta al historial de Git, que es permanente.

### Comparativa

| Método | Historial resultante | Cuándo usarlo |
|---|---|---|
| **Merge commit** | Preserva toda la historia de la rama + un commit de merge | Equipos que quieren trazabilidad completa |
| **Squash and merge** | Aplasta todos los commits de la rama en UNO solo | Ramas con muchos commits de "arreglando typo", historial limpio en `main` |
| **Rebase and merge** | Replay de los commits de la rama sobre `main`, sin commit de merge | Historial lineal, sin "bubbles" de merge |

Visualización esquemática:

```
# Estado inicial
main:    A---B
feature:     C---D---E

# Merge commit
main:    A---B-------F   (F = commit de merge)
                 /
feature:     C---D---E

# Squash
main:    A---B---CDE     (CDE = un solo commit nuevo con todos los cambios)

# Rebase
main:    A---B---C'--D'--E'   (commits re-aplicados sobre B, sin merge commit)
```

**Recomendación práctica**: empieza con **Squash** para proyectos personales o equipos pequeños. Historial limpio en `main`, fácil de leer con `git log --oneline`. Reserva el Merge commit para cuando necesites auditar cada commit individual (ej. cumplimiento regulatorio).

Puedes configurar el método por defecto en `Settings > Merge requests > Merge method`, y también dejarlo a elección del autor MR por MR.

---

## 7. Merge when pipeline succeeds

### El problema

El pipeline tarda 10 minutos. Haces clic en merge, te vas a hacer otra cosa, y cuando vuelves el pipeline había fallado y GitLab no mergeó. Tienes que volver a hacer merge.

### La solución

Botón **"Merge when pipeline succeeds"**: le dices a GitLab "cuando el pipeline de este MR pase, fusiónalo automáticamente". Puedes cerrar la pestaña.

Si el pipeline falla, GitLab **no** fusiona y te notifica.

Requisito: el pipeline debe estar corriendo en el momento de hacer clic. Si aún no ha empezado, el botón no aparece.

---

## 8. Resolver conflictos

### Qué es un conflicto

Ocurre cuando dos ramas modificaron las mismas líneas del mismo fichero. Git no puede decidir solo cuál prevalece.

```
<<<<<<< HEAD (main)
const timeout = 3000;
=======
const timeout = 5000;
>>>>>>> feature/new-timeout
```

### Resolver desde la UI de GitLab

GitLab ofrece un editor de conflictos visual en el MR (pestaña "Conflicts"):

- Ves las dos versiones lado a lado.
- Eliges cuál prevalece línea a línea, o editas manualmente el resultado final.
- Haces clic en "Commit to source branch".

Limitación: el editor visual solo funciona con conflictos de texto en ficheros que GitLab puede renderizar. Para conflictos binarios o complejos, toca resolverlos en local.

### Resolver en local (más control)

```bash
# Estás en tu rama feature
git fetch origin
git rebase origin/main   # o git merge origin/main, según tu flujo

# Git se detiene en el conflicto
# Editas el fichero, resuelves los marcadores <<<< ==== >>>>
git add archivo-con-conflicto.py
git rebase --continue    # o git commit si usaste merge

git push origin feature/mi-rama --force-with-lease
# --force-with-lease es más seguro que --force: falla si alguien más pushó mientras tanto
```

---

## 9. Buenas practicas de code review

### Para el autor del MR

**Antes de abrir:**
- El MR resuelve UNA cosa. Si tienes dos cambios no relacionados, abre dos MRs.
- Revisa tu propio diff antes de pedir review. Caza los errores obvios tú mismo.
- Escribe una descripción que responda: ¿qué cambia? ¿por qué? ¿cómo probarlo?
- El pipeline debe pasar antes de pedir review (salvo Draft para feedback temprano).

**Durante la review:**
- Responde a todos los comentarios, aunque sea para explicar por qué no aplicas el cambio.
- Distingue entre "voy a cambiarlo" (marcar hilo como resuelto tras aplicar) y "no estoy de acuerdo" (discutir en el hilo).
- No fuerces el merge sin aprobación por "urgencia". La urgencia es una deuda que pagas en bugs.

### Para el revisor

**Qué revisar (por orden de importancia):**

1. **Corrección**: ¿hace lo que dice que hace? ¿hay casos borde no cubiertos?
2. **Seguridad**: ¿hay inputs sin validar, secretos hardcodeados, inyecciones posibles?
3. **Tests**: ¿cubren los casos relevantes?
4. **Diseño**: ¿la abstracción tiene sentido? ¿hay acoplamiento innecesario?
5. **Legibilidad**: nombres claros, comentarios donde no es obvio.
6. **Formato/estilo**: solo si no hay linter. Si hay linter, el pipeline lo detecta; no lo menciones.

**Cómo comunicarse:**

| Prefijo en comentario | Significado | Acción esperada |
|---|---|---|
| `nit:` | Nitpick, opcional | El autor puede ignorarlo sin explicación |
| `suggestion:` | Propuesta concreta | Usar la feature de suggestions si es código |
| `question:` | No entiendo, explícame | El autor responde, sin cambio necesario |
| (sin prefijo) | Cambio requerido | El autor debe resolverlo antes del merge |

Esto no es un estándar oficial de GitLab, pero es convención ampliamente usada. Reduce la fricción comunicativa enormemente.

**Velocidad de review**: responde en menos de 24h en horario laboral. Un MR abandonado es trabajo tirado. Si no puedes revisar, di cuándo podrás.

**Tono**: el código se critica, no la persona. "Este nombre de variable no describe bien su propósito" en vez de "este nombre es horrible".

---

## Errores comunes

| Error | Consecuencia | Solución |
|---|---|---|
| MR gigante (500+ líneas) | Nadie lo revisa bien, los bugs se cuelan | Divide en MRs más pequeños desde el principio |
| Fusionar sin esperar el pipeline | Ramas rotas en `main` | Usa "Merge when pipeline succeeds" |
| Resolver conflictos en `main` directamente | Historial sucio, riesgo de pérdida | Siempre resuelve en tu rama feature |
| Ignorar comentarios de review | Deuda técnica acumulada, mal ambiente de equipo | Responde a todo, aunque sea para declinar con argumento |
| Squash de un MR con commits ya referenciados en issues | Pierdes la trazabilidad | En ese caso usa Merge commit |
| `git push --force` sin `--lease` | Puedes sobrescribir commits de otro | Usa siempre `--force-with-lease` |

---

## Aplícalo a tus proyectos

**app web (FastAPI + React + Docker):**
- Crea `.gitlab/merge_request_templates/Default.md` con el checklist de la sección 3, añadiendo un paso: "El pipeline de Docker build pasa".
- Configura "All threads must be resolved" y "Reset approvals on push" en Settings.
- Usa **Squash** como método de merge: los commits de desarrollo ("fix typo", "arreglando import") no aportan en el historial de `main`.
- Cuando trabajes en features grandes (ej. módulo de tracking Na/K), abre el MR en Draft desde el primer día para que el pipeline corra continuamente.

**proyecto embebido (PlatformIO/C++):**
- Si trabajas en solitario, el MR sigue siendo útil como registro de decisiones. La descripción queda en el historial para "tu yo de dentro de 6 meses".
- Usa CODEOWNERS si en el futuro hay colaboradores: los ficheros de configuración de hardware merecen revisión especializada.

---

## Conexiones

- [[MOC_GitLab]]
- [[03-repos-y-flujo-git]]
- [[05-gitlab-cicd-fundamentos]]
- [[09-issues-tableros-y-gestion]]
- [[02-conceptos-grupos-proyectos-permisos]]
- [[07-cicd-avanzado]]
- [[MOC_Desarrollo_Software]]
