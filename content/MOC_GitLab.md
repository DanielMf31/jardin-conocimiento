---
title: MOC GitLab
date: 2026-06-14
tags: [programacion/gitlab, programacion/devops, moc]
type: moc
status: en-progreso
source: claude-code
aliases: [MOC GitLab, GitLab MOC]
---

# 🦊 MOC GitLab

> Mapa de **GitLab**: la plataforma DevOps todo-en-uno. Conceptos (grupos, permisos, MRs),
> **CI/CD a fondo** (lo que más renta aprender) y **autoalojamiento**.
> Clúster de docs en `50_Areas/Ingenieria/Programacion/GitLab/`.
>
> 📍 Área padre: [[MOC_Programacion]] · Clúster hermano: [[MOC_Desarrollo_Software]] (Agile/DevOps)

## 📓 Índice y registros vivos
- [[GitLab/00_README|README del clúster]] — qué es y cómo recorrerlo
- [[GitLab/00_Dudas_y_Preguntas|Dudas y Preguntas]] — log de dudas

## 📚 Documentación por tema
| # | Tema | Doc |
|---|---|---|
| 01 | Qué es GitLab y ediciones (SaaS vs autoalojado, CE/EE) | [[01-que-es-gitlab]] |
| 02 | Conceptos: grupos, proyectos y permisos | [[02-conceptos-grupos-proyectos-permisos]] |
| 03 | Repositorios y flujo git (GitLab Flow, protected branches) | [[03-repos-y-flujo-git]] |
| 04 | Merge Requests y code review | [[04-merge-requests-y-code-review]] |
| 05 | **CI/CD — Fundamentos** ⭐ (`.gitlab-ci.yml`, pipelines) | [[05-gitlab-cicd-fundamentos]] |
| 06 | Runners (executors, registrar el tuyo) | [[06-runners]] |
| 07 | **CI/CD avanzado** ⭐ (environments, CD, templates, DAG) | [[07-cicd-avanzado]] |
| 08 | Container Registry, paquetes y Pages | [[08-registry-paquetes-y-pages]] |
| 09 | Issues, tableros y gestión ágil | [[09-issues-tableros-y-gestion]] |
| 10 | Autoalojamiento (Omnibus/Docker, arquitectura, exponer seguro) | [[10-autoalojamiento]] |
| 11 | Administración (backups, upgrades) | [[11-administracion-backups-upgrades]] |
| 12 | GitLab vs alternativas (Forgejo/GitHub): qué aprender | [[12-gitlab-vs-alternativas]] |

## 🎓 Roadmap de aprendizaje
1. **Base**: [[01-que-es-gitlab]] → [[02-conceptos-grupos-proyectos-permisos]] → [[03-repos-y-flujo-git]] → [[04-merge-requests-y-code-review]].
2. **El plato fuerte (lo que más renta)** ⭐: [[05-gitlab-cicd-fundamentos]] → [[06-runners]] → [[07-cicd-avanzado]]. Practícalo en **GitLab.com gratis** sobre un proyecto de.
3. **Si vas a autoalojar (homelab)**: [[10-autoalojamiento]] → [[11-administracion-backups-upgrades]]. Valora **Forgejo** (ligero) vs GitLab CE → [[12-gitlab-vs-alternativas]].
4. El resto (08, 09) según necesidad.

> Idea clave: lo valioso de mercado son los **conceptos de CI/CD** (transfieren a GitHub Actions). Aprende CI en SaaS gratis; autoaloja algo ligero.

## Conexiones
- [[MOC_Programacion]] — área raíz
- [[MOC_Desarrollo_Software]] — Agile/DevOps (CI/CD conceptual: [[08-devops-y-cicd]])
- — proyectos donde practicar pipelines
