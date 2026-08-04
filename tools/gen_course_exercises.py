#!/usr/bin/env python3
"""Genera notas web autocontenidas por ejercicio para los cursos del Jardin.

Cada curso (curso-c, curso-python, ...) vive fuera de este repo como codigo fuente:
    <cursos>/curso-<x>/material/NN-tema/ejNN_modelo.<ext>   (resuelto)
    <cursos>/curso-<x>/material/NN-tema/ejNN_practica.<ext> (esqueleto con TODO)
    <cursos>/curso-<x>/material/NN-tema/diagramas/ejNN_plantuml.png (solo curso-c)

Este script lee ese material, VERIFICA que el modelo compila, copia el diagrama y
emite una nota Markdown por ejercicio, lista para Quartz, en:
    content/Curso_X/practica/NN-tema/ejNN.md

Las notas son ARTEFACTOS GENERADOS: la fuente de verdad es el material del curso.
No las edites a mano salvo la seccion "Como se resuelve" (marcada con <!-- EXPLICACION -->),
que es prosa docente escrita encima.

Rutas: se derivan de la ubicacion del script (este repo) y de un directorio de cursos
hermano (por defecto ../cursos-publicados). NO se codifica ninguna ruta personal, para
que el script sea seguro en el repo publico.

Uso:
    python3 tools/gen_course_exercises.py c                 # todos los modulos de C
    python3 tools/gen_course_exercises.py c 01-variables    # solo un modulo
    python3 tools/gen_course_exercises.py c --mirror        # ademas, copia solo-lectura en la boveda
    COURSES_ROOT=/otra/ruta python3 tools/gen_course_exercises.py python

Con --mirror, ademas de las notas del jardin escribe una copia de SOLO LECTURA (0444, mirror:true,
banner de "no editar") en <boveda>/40_Proyectos/_Espejo/curso-<x>/practica/, siguiendo el mismo
convenio que scripts/mirror_docs.py del SDS. La boveda excluye _Espejo de sus auditores, asi que los
wikilinks nativos de Quartz conviven ahi sin problema.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]          # jardin-conocimiento/
CONTENT = REPO / "content"
DEFAULT_COURSES = Path(os.environ.get("COURSES_ROOT") or (REPO.parent / "cursos-publicados"))

# Perfil de cada curso. Anade aqui un curso nuevo y el resto funciona igual.
COURSES = {
    "c": {
        "label": "C",
        "src_subdir": "curso-c",
        "content_dir": "Curso_C",
        "ext": ".c",
        "fence": "c",
        "has_diagrams": True,
        # Dos diagramas por ejercicio: flujo/actividad (plantuml) y grafo (graphviz).
        "diagram_suffixes": ["_plantuml.png", "_graphviz.png"],
        # -lm: algunos ejercicios usan math.h (sqrt...). En Linux hace falta enlazar libm;
        # en Dev-C++/MinGW no, pero el flag es inofensivo si no se usa.
        "verify": lambda src, out: ["gcc", "-std=c11", "-Wall", str(src), "-lm", "-o", str(out)],
        "teoria_link": "Curso_C/modelo/{modslug}",
        "indice_link": "Curso_C/00_README",
        "run_hint": "Dev-C++ (Windows): Archivo → Nuevo → Código fuente, pega el código y pulsa F11 "
                    "(compilar y ejecutar). Si ves los acentos raros en la consola, escribe `chcp 65001` "
                    "y vuelve a ejecutar.",
    },
    "python": {
        "label": "Python",
        "src_subdir": "curso-python",
        "content_dir": "Curso_Python",
        "ext": ".py",
        "fence": "python",
        "has_diagrams": False,
        "diagram_suffixes": [],
        "verify": lambda src, out: ["python3", "-m", "py_compile", str(src)],
        "teoria_link": "Curso_Python/modelo/{modslug}",
        "indice_link": "Curso_Python/00_README",
        "run_hint": "Cualquier editor o la web: pega el codigo en un fichero `.py` y ejecutalo con "
                    "`python3 archivo.py` (o el boton de Ejecutar de tu editor).",
    },
}

COLOR = {"verde": "verde", "amarillo": "amarillo", "rojo": "rojo"}


def leading_comment(text: str, fence: str) -> str:
    """Devuelve la cabecera-comentario limpia (sin marcadores) del fichero fuente."""
    lines = text.splitlines()
    block: list[str] = []
    if fence == "c":
        started = False
        for ln in lines:
            if "/*" in ln:
                started = True
            if started:
                block.append(ln)
            if started and "*/" in ln:
                break
    else:  # python: comentarios '#' iniciales
        for ln in lines:
            if ln.strip().startswith("#"):
                block.append(ln)
            elif block:
                break
    cleaned = []
    for ln in block:
        ln = ln.replace("/*", "").replace("*/", "").strip()
        ln = ln.lstrip("*#").strip()
        cleaned.append(ln)
    return "\n".join(cleaned)


def parse_header(header: str) -> dict:
    """Extrae modulo, numero, enunciado y dificultad. Tolera cabeceras multilinea."""
    mod = re.search(r"M[oó]dulo\s*(\d+)\s*:\s*(.+)", header)
    ej = re.search(r"Ejercicio\s*(\d+)", header)
    enun = re.search(r"Enunciado:\s*(.+?)\s*(?:Dificultad:|Compilar:|Ejecutar:|$)", header, re.S)
    dif = re.search(r"Dificultad:\s*(\w+)", header)
    enunciado = re.sub(r"\s+", " ", enun.group(1)).strip() if enun else ""
    return {
        "mod_num": mod.group(1) if mod else "??",
        "mod_title": mod.group(2).strip() if mod else "",
        "ej_num": ej.group(1) if ej else "??",
        "enunciado": enunciado,
        "dificultad": (dif.group(1).lower() if dif else "verde"),
    }


def short_title(enunciado: str, limit: int = 70) -> str:
    """Titulo corto para el H1/frontmatter, a partir del enunciado."""
    t = enunciado.rstrip(". ")
    # cortar en el separador de frase mas temprano (punto, punto y coma o dos puntos)
    cuts = [t.find(s) for s in (";", ": ", ". ") if t.find(s) != -1]
    if cuts:
        t = t[:min(cuts)].strip()
    # soltar un parentesis final solo si lo que queda sigue siendo descriptivo
    if " (" in t:
        head = t.split(" (")[0].strip()
        if len(head) >= 30:
            t = head
    if len(t) > limit:
        t = t[:limit].rsplit(" ", 1)[0] + "…"
    return t[:1].upper() + t[1:]


def verify_compiles(course: dict, src: Path) -> tuple[bool, str]:
    """Compila/valida el modelo. Devuelve (ok, salida)."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "a.out"
        cmd = course["verify"](src, out)
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except FileNotFoundError as e:
            return False, f"herramienta no encontrada: {e}"
        except subprocess.TimeoutExpired:
            return False, "timeout al compilar"
        msg = (p.stderr or p.stdout).strip()
        return p.returncode == 0, msg


def note_markdown(course: dict, meta: dict, modslug: str,
                  modelo_src: str, practica_src: str,
                  diagram_names: list, explicacion: str, date: str) -> str:
    key_label = course["label"]
    mod, num = meta["mod_num"], meta["ej_num"]
    dif = meta["dificultad"]
    title = short_title(meta["enunciado"])
    fence = course["fence"]
    alias = f"{fence}-m{mod}-ej{num}"
    teoria = course["teoria_link"].format(modslug=modslug)
    indice = course["indice_link"]

    diagram_block = ""
    if diagram_names:
        # Ruta ROOT-ABSOLUTA a proposito: los diagramas se llaman igual en cada modulo
        # (ejNN_plantuml.png), y la resolucion "shortest" de Quartz no puede desambiguar
        # un nombre suelto -> lo resolveria mal. La ruta completa desde content/ si es unica.
        # (En el espejo, to_mirror la reescribe a nombre suelto para que Obsidian la resuelva
        #  en la misma carpeta.)
        parts = []
        for name in diagram_names:
            src = f"/{course['content_dir']}/practica/{modslug}/{name}"
            kind = "grafo" if "graphviz" in name else "actividad"
            parts.append(f"![Diagrama de flujo ({kind}) del ejercicio {num}]({src})")
        head = "## Diagramas de flujo" if len(diagram_names) > 1 else "## Diagrama de flujo"
        diagram_block = f"{head}\n\n" + "\n\n".join(parts) + "\n\n"

    # El titulo va entre comillas dobles en el frontmatter YAML: las comillas dobles
    # que traiga el enunciado romperian la cadena, asi que se pasan a comillas simples.
    fm_title = f"{key_label} · Módulo {mod} · Ej {num} — {title}".replace('"', "'")

    return f"""---
title: "{fm_title}"
date: {date}
tags: [programacion/{fence}, curso/{fence}, curso/{fence}/ejercicio, dificultad/{COLOR.get(dif, dif)}]
type: nota
status: permanente
source: generado
aliases: [{alias}]
---

# Ejercicio {num} — {title}

Dificultad: {dif} · Módulo {mod} ({meta["mod_title"]})

## Enunciado

{meta["enunciado"]}

{diagram_block}## Cómo se resuelve

<!-- EXPLICACION -->
{explicacion}

## Para practicar — cópialo en Dev-C++

Pega este esqueleto y completa los `TODO`. Es la mejor forma de aprender: inténtalo antes de mirar la solución.

```{fence}
{practica_src.rstrip()}
```

## Solución — cópiala y ejecútala

```{fence}
{modelo_src.rstrip()}
```

## Cómo usarlo

{course["run_hint"]}

## Conexiones

- [[{teoria}|Teoría del módulo]]
- [[{indice}|Índice del curso]]
"""


# ---------------------------------------------------------------------------
# Espejo de solo lectura hacia la boveda (mismo convenio que mirror_docs.py)
# ---------------------------------------------------------------------------

def resolve_espejo(vault: str | None) -> Path | None:
    """Localiza <boveda>/40_Proyectos/_Espejo. Vault explicito, o desde el local.json del SDS."""
    if vault:
        espejo = Path(vault) / "40_Proyectos/_Espejo"
    else:
        local = REPO.parent / "software-development-system" / "config" / "local.json"
        if not local.exists():
            return None
        cfg = json.loads(local.read_text(encoding="utf-8"))
        espejo = Path(cfg["vaultPath"]) / cfg.get("mirrorRoot", "40_Proyectos/_Espejo")
    return espejo if espejo.is_dir() else None


def write_ro(dest: Path, content) -> None:
    """Escribe un fichero de solo lectura (0444). Aflojar, escribir, apretar."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        os.chmod(dest, 0o644)
    if isinstance(content, bytes):
        dest.write_bytes(content)
    else:
        dest.write_text(content, encoding="utf-8")
    os.chmod(dest, 0o444)


def to_mirror(md: str, source_rel: str) -> str:
    """Convierte una nota del jardin en su copia-espejo de la boveda (solo lectura)."""
    m = re.match(r"^---\n(.*?)\n---\n", md, re.S)
    fm_block, body = (m.group(1), md[m.end():]) if m else ("", md)
    kept = [ln for ln in fm_block.split("\n")
            if ln.split(":", 1)[0].strip() not in ("type", "status", "source")]
    fm = "\n".join(kept).rstrip()
    fm += ("\ntype: espejo\nstatus: espejo\nsource: mirror-generado\n"
           f"mirror: true\nmirror_source: {source_rel}")
    banner = ("<!-- FICHERO GENERADO — NO EDITAR. Fuente de verdad: "
              f"jardin-conocimiento/{source_rel} (se regenera desde el curso). -->")
    # En el jardin las imagenes van con ruta root-absoluta (Quartz); en la boveda el PNG
    # esta junto a la nota, asi que se deja el nombre suelto para que Obsidian lo resuelva.
    body = re.sub(r"\]\(/[^)]*/([^/)]+\.png)\)", r"](\1)", body)
    return f"---\n{fm}\n---\n\n{banner}\n\n{body.lstrip()}"


def rebuild_index(course: dict, practica_dir: Path, date: str) -> str:
    """Regenera practica/00_README.md con los enlaces a las notas existentes. Devuelve su texto."""
    label = course["label"]
    fence = course["fence"]
    indice = course["indice_link"]
    rows = []
    for moddir in sorted(p for p in practica_dir.iterdir() if p.is_dir()):
        notes = sorted(moddir.glob("ej*.md"))
        if not notes:
            continue
        rows.append(f"\n### Módulo {moddir.name}\n")
        for n in notes:
            m = re.search(r"^title:\s*\"(.+)\"", n.read_text(encoding="utf-8"), re.M)
            t = m.group(1) if m else n.stem
            # en la lista del modulo, mostrar solo "Ej NN — ..." (el prefijo curso/modulo sobra).
            # OJO: variable propia (no 'label', que es la etiqueta del curso y la pisaria).
            lbl = re.sub(r"^.*?(Ej\s*\d+\s*—)", r"\1", t)
            link = f"{course['content_dir']}/practica/{moddir.name}/{n.stem}"
            rows.append(f"- [[{link}|{lbl}]]")
    body = "\n".join(rows) if rows else "_Aún no hay ejercicios generados._"
    text = f"""---
title: "Curso de {label} — práctica (ejercicios resueltos)"
date: {date}
tags: [programacion/{fence}, curso/{fence}, curso/{fence}/ejercicio, meta]
type: nota
status: permanente
source: generado
aliases: [practica-{fence}, ejercicios-{fence}]
---

# Curso de {label} — práctica

Una nota por ejercicio: enunciado, diagrama de flujo, explicación y el código listo para
copiar. Puedes resolverlo desde el navegador, sin descargar nada.
{body}

## Conexiones

- [[{indice}|Índice y teoría del curso]]
"""
    (practica_dir / "00_README.md").write_text(text, encoding="utf-8")
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera notas por ejercicio para un curso del Jardin.")
    ap.add_argument("course", choices=sorted(COURSES), help="clave del curso (c, python, ...)")
    ap.add_argument("module", nargs="?", help="modulo concreto (p. ej. 01-variables); por defecto, todos")
    ap.add_argument("--courses-root", default=str(DEFAULT_COURSES),
                    help="directorio que contiene curso-<x>/ (por defecto ../cursos-publicados)")
    ap.add_argument("--mirror", action="store_true",
                    help="ademas, escribir una copia de solo lectura en la boveda (40_Proyectos/_Espejo)")
    ap.add_argument("--vault", default=None,
                    help="ruta de la boveda (si se omite, se lee del local.json del SDS)")
    args = ap.parse_args()

    espejo = None
    if args.mirror:
        espejo = resolve_espejo(args.vault)
        if espejo is None:
            print("AVISO: --mirror pedido pero no localizo la boveda/_Espejo; me salto el espejo.",
                  file=sys.stderr)

    course = COURSES[args.course]
    date = datetime.date.today().isoformat()
    src_material = Path(args.courses_root) / course["src_subdir"] / "material"
    if not src_material.is_dir():
        print(f"ERROR: no encuentro el material del curso en {src_material}", file=sys.stderr)
        return 2

    dest_practica = CONTENT / course["content_dir"] / "practica"
    dest_practica.mkdir(parents=True, exist_ok=True)

    modules = [src_material / args.module] if args.module else sorted(
        p for p in src_material.iterdir() if p.is_dir())

    total, failed, mirrored = 0, [], 0
    esp_practica = (espejo / course["src_subdir"] / "practica") if espejo else None
    for moddir in modules:
        if not moddir.is_dir():
            print(f"AVISO: modulo inexistente: {moddir}", file=sys.stderr)
            continue
        out_moddir = dest_practica / moddir.name
        out_moddir.mkdir(parents=True, exist_ok=True)
        modelos = sorted(moddir.glob(f"ej*_modelo{course['ext']}"))
        for modelo_path in modelos:
            num = re.search(r"ej(\d+)_modelo", modelo_path.name).group(1)
            practica_path = moddir / f"ej{num}_practica{course['ext']}"
            modelo_src = modelo_path.read_text(encoding="utf-8")
            practica_src = practica_path.read_text(encoding="utf-8") if practica_path.exists() else ""
            meta = parse_header(leading_comment(modelo_src, course["fence"]))

            ok, msg = verify_compiles(course, modelo_path)
            status = "OK " if ok else "FALLA"
            if not ok:
                failed.append(f"{moddir.name}/ej{num}: {msg.splitlines()[0] if msg else '?'}")
            warn = " (con avisos)" if ok and msg else ""

            diagram_names = []
            if course["has_diagrams"]:
                for suf in course["diagram_suffixes"]:
                    dpng = moddir / "diagramas" / f"ej{num}{suf}"
                    if dpng.exists():
                        name = f"ej{num}{suf}"
                        shutil.copy2(dpng, out_moddir / name)
                        diagram_names.append(name)

            note = out_moddir / f"ej{num}.md"
            # conservar la explicacion ya redactada si el fichero existe
            explicacion = "_Explicación pendiente de redactar._"
            if note.exists():
                prev = note.read_text(encoding="utf-8")
                m = re.search(r"<!-- EXPLICACION -->\n(.*?)\n## Para practicar", prev, re.S)
                if m and m.group(1).strip() and "pendiente" not in m.group(1):
                    explicacion = m.group(1).strip()

            md = note_markdown(course, meta, moddir.name, modelo_src, practica_src,
                               diagram_names, explicacion, date)
            note.write_text(md, encoding="utf-8")
            total += 1
            print(f"  [{status}{warn}] {note.relative_to(CONTENT)}  ({meta['dificultad']})")

            if esp_practica is not None:
                source_rel = f"content/{course['content_dir']}/practica/{moddir.name}/ej{num}.md"
                emod = esp_practica / moddir.name
                write_ro(emod / f"ej{num}.md", to_mirror(md, source_rel))
                for name in diagram_names:
                    write_ro(emod / name, (out_moddir / name).read_bytes())
                mirrored += 1

    idx_text = rebuild_index(course, dest_practica, date)
    if esp_practica is not None:
        idx_rel = f"content/{course['content_dir']}/practica/00_README.md"
        write_ro(esp_practica / "00_README.md", to_mirror(idx_text, idx_rel))
    print(f"\nGeneradas {total} notas en {dest_practica.relative_to(REPO)}. Indice regenerado.")
    if espejo is not None:
        print(f"Espejo (solo lectura): {mirrored} notas en {esp_practica}")
    if failed:
        print(f"\n{len(failed)} ejercicio(s) NO compilan (revisa el material fuente):", file=sys.stderr)
        for f in failed:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("Todos los modelos compilan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
