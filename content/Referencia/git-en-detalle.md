---
title: Git en detalle — guía práctica
date: 2026-06-14
tags: [programacion/git, programacion/herramientas, referencia]
type: nota
status: permanente
source: claude-code
aliases: [git en detalle, git practico, git guia, git comandos]
---

# Git en detalle — guía práctica

## Idea central
Git es un **control de versiones distribuido**: cada copia tiene la historia completa, y trabajas
en local sin red. Esta nota es la **referencia práctica** (comandos y flujos). El **porqué** (cómo
guarda los datos por dentro) está en [[git-por-dentro]] — léelo antes si quieres que todo "encaje".

> Modelo mental clave (de [[git-por-dentro]]): Git guarda **snapshots**, no diffs; una rama es solo
> un **puntero** a un commit; y hay **3 zonas**: *working directory* → *staging (index)* → *repo*.

---

## Configuración inicial (una vez)
```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
git config --global init.defaultBranch main      # rama por defecto 'main'
git config --global pull.rebase false            # o true si prefieres rebase al hacer pull
# alias útiles
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --decorate --all"
```

## El ciclo básico (las 3 zonas)
```bash
git status                 # qué hay modificado / staged
git add archivo.py         # mover cambios a 'staging'
git add -p                 # añadir POR TROZOS (elige qué partes) — muy útil
git commit -m "mensaje"    # snapshot de lo staged
git commit -am "msg"       # add (de lo ya rastreado) + commit en uno
git diff                   # cambios sin stagear (working vs index)
git diff --staged          # cambios staged (index vs último commit)
```

## Ramas
```bash
git branch                 # listar
git switch -c nueva-rama   # crear y cambiar (moderno; antes: git checkout -b)
git switch main            # cambiar de rama
git branch -d rama         # borrar (segura; -D para forzar)
git merge otra-rama        # fusionar 'otra-rama' EN la actual
```
- **Fast-forward**: si no hay divergencia, la rama solo "avanza" el puntero (sin commit de merge).
- **Merge commit**: si ambas divergieron, crea un commit con 2 padres.

## Merge vs Rebase (el tema que más se lía)
| | `merge` | `rebase` |
|---|---|---|
| Qué hace | Une historias con un **commit de merge** | **Reaplica** tus commits encima de otra base |
| Historia | Real, con bifurcaciones | **Lineal**, limpia |
| Cuándo | Integrar ramas compartidas | Poner al día tu rama local antes de un MR |

```bash
git rebase main            # reaplica tu rama encima de main (historia lineal)
git rebase -i HEAD~3        # rebase INTERACTIVO: squash/reword/reorder los últimos 3
```
> **Regla de oro**: **NO rebases commits que ya has publicado/compartido** (reescribes la historia
> y rompes a los demás). Rebase = solo para tu trabajo local aún no empujado.

### Resolver conflictos
1. Git marca los choques en el archivo (`<<<<<<<`, `=======`, `>>>>>>>`).
2. Editas, dejas el resultado correcto, quitas los marcadores.
3. `git add archivo` y luego `git merge --continue` (o `git rebase --continue`).
4. ¿Te liaste? `git merge --abort` / `git rebase --abort` para volver al estado previo.

## Remotos (trabajar con GitHub/GitLab)
```bash
git clone <url>                      # copiar un repo remoto
git remote -v                        # ver remotos (origin…)
git fetch                            # traer cambios remotos SIN fusionar
git pull                             # fetch + merge (o rebase) — actualizar tu rama
git push                             # subir tus commits
git push -u origin mi-rama           # primera vez: crea la rama remota y la enlaza (upstream)
```
- **fetch ≠ pull**: `fetch` solo descarga; `pull` además fusiona. Si quieres ver antes de mezclar, `fetch` + `git log origin/main`.

## ↩ Deshacer cosas (la parte más valiosa)
| Situación | Comando |
|---|---|
| Descartar cambios sin stagear de un archivo | `git restore archivo` |
| Sacar algo de staging (sin perder el cambio) | `git restore --staged archivo` |
| Corregir el **último** commit (mensaje o añadir algo) | `git commit --amend` |
| Deshacer commits **locales** dejando los cambios staged | `git reset --soft HEAD~1` |
| …dejando los cambios en el working dir | `git reset --mixed HEAD~1` (por defecto) |
| …**tirando** los cambios del todo (peligroso) | `git reset --hard HEAD~1` |
| Deshacer un commit **ya publicado** (crea uno inverso) | `git revert <hash>` |
| Borrar archivos no rastreados (limpieza) | `git clean -fd` |

> **Red de seguridad: `git reflog`**. Registra TODOS los movimientos de HEAD; si "perdiste" un
> commit (incluso tras un `reset --hard`), aparece ahí y lo recuperas con `git reset --hard <hash>`
> o `git switch -c rescate <hash>`. Casi nada en Git se pierde de verdad.

## Stash (guardar cambios a medias)
```bash
git stash                  # guarda y limpia el working dir (para cambiar de rama rápido)
git stash pop              # recupera el último stash (y lo borra)
git stash list             # ver la pila de stashes
```

## Otros útiles
```bash
git cherry-pick <hash>     # traer UN commit concreto de otra rama
git tag -a v1.0 -m "..."   # crear un tag (releases)
git log --oneline --graph  # historia compacta y visual
git show <hash>            # ver un commit en detalle
git blame archivo          # quién y cuándo cambió cada línea
git bisect start           # búsqueda binaria del commit que ROMPIÓ algo (bug hunting)
```

## .gitignore
Lista de patrones de lo que Git debe **ignorar** (no rastrear): `__pycache__/`, `.venv/`, `node_modules/`,
`.env`, `*.log`, build/. Crea uno por proyecto (gitignore.io genera plantillas por lenguaje).
> Nunca commitees **secretos** (`.env`, claves). Si ya lo hiciste, no basta con borrarlo: queda
> en la historia → hay que reescribirla (`git filter-repo`) y **rotar el secreto**.

## Buenas prácticas
- **Commits atómicos**: un cambio lógico por commit (más fácil de revisar y de revertir).
- **Mensajes claros**: imperativo y conciso ("Añade validación de email"). Mira *Conventional Commits*
  (`feat:`, `fix:`, `docs:`…) si quieres versionado/automatización.
- **Rama por tarea** → Merge Request → review → merge. (Flujos en [[03-repos-y-flujo-git]] y [[07-practicas-de-ingenieria]].)

## Conexiones
- [[git-por-dentro]] — cómo funciona Git **por dentro** (modelo de objetos, snapshots, las 3 zonas)
- [[MOC_Programacion]] — área raíz (herramienta: Git)
- [[03-repos-y-flujo-git]] · [[04-merge-requests-y-code-review]] — Git aplicado en GitLab ([[MOC_GitLab]])
- [[07-practicas-de-ingenieria]] — workflows de Git en el clúster de Agile/DevOps ([[MOC_Desarrollo_Software]])
