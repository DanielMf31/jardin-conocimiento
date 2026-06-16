#!/usr/bin/env python3
"""Guard de fugas del Jardin de Conocimiento.

Escanea content/ y FALLA (exit 1) si encuentra algo que NO deberia publicarse:
  - Datos personales (usuario/email/host).
  - Cuerpos de clave privada (-----BEGIN ... -----).
  - Referencias a notas privadas (chat-claude-*, fleeting YYYYMMDDHHmm-...).
  - Wikilinks rotos (apuntan a notas que NO estan publicadas -> fugarian su nombre).
  - Posibles contrasenas (32 chars con mayus+minus+digito, tipo wargame).

Uso, desde la raiz del repo:
    python3 tools/check-leaks.py

Conviene ejecutarlo SIEMPRE antes de 'git push'. Si pasa, es seguro publicar.
Este script NO contiene rutas privadas: es seguro tenerlo en el repo publico.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.environ.get("JARDIN_CONTENT") or os.path.join(os.path.dirname(HERE), "content")

PRIVATE_REF = re.compile(r'chat-claude-|chat-gpt-|chat-deepseek-|\bdiario-|\b20\d{10}-')
WIKILINK = re.compile(r'\[\[([^\[\]]+?)\]\]')
KEYBODY = re.compile(r'\bMI[IG][A-Za-z0-9+/]{24,}')
PASS32 = re.compile(r'(?<![A-Za-z0-9])(?=[A-Za-z0-9]{32}(?![A-Za-z0-9]))'
                    r'(?=[A-Za-z0-9]*[a-z])(?=[A-Za-z0-9]*[A-Z])(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{32}')
PERSONAL = re.compile(r'danielmf31|dmf310506|MonterBuntu')
CAREER = re.compile(r'FAANG|Tier [ABC]\b|demeter|nutrici|quotient|25/55/20|meta Google|mecatr|perfil 2e|boredom|cochecito', re.I)


def published(content):
    s = set()
    for dp, _, fns in os.walk(content):
        for fn in fns:
            if not fn.endswith('.md'):
                continue
            s.add(fn[:-3].lower())
            try:
                with open(os.path.join(dp, fn), encoding='utf-8') as f:
                    h = f.read(3000)
                m = re.match(r'^---\n(.*?)\n---', h, re.S)
                if m:
                    am = re.search(r'^aliases:\s*\[(.*)\]', m.group(1), re.M)
                    if am:
                        for a in am.group(1).split(','):
                            a = a.strip().strip('"\'').lower()
                            if a:
                                s.add(a)
            except Exception:
                pass
    return s


def main():
    if not os.path.isdir(CONTENT):
        print(f"No encuentro content/ en: {CONTENT}")
        return 2
    pub = published(CONTENT)
    findings = []
    for dp, _, fns in os.walk(CONTENT):
        for fn in sorted(fns):
            if not fn.endswith('.md'):
                continue
            path = os.path.join(dp, fn)
            rel = os.path.relpath(path, CONTENT)
            with open(path, encoding='utf-8') as f:
                lines = f.read().split('\n')
            fence = False
            for n, line in enumerate(lines, 1):
                s = line.lstrip()
                if s.startswith('```') or s.startswith('~~~'):
                    fence = not fence
                    continue

                def add(kind, frag):
                    findings.append((rel, n, kind, frag[:80]))

                if PERSONAL.search(line):
                    add("DATO PERSONAL", PERSONAL.search(line).group(0))
                if KEYBODY.search(line):
                    add("CLAVE PRIVADA", KEYBODY.search(line).group(0))
                if PRIVATE_REF.search(line):
                    add("REF NOTA PRIVADA", PRIVATE_REF.search(line).group(0))
                if CAREER.search(line):
                    add("MARCO PERSONAL/CARRERA", CAREER.search(line).group(0))
                if not fence:
                    for m in WIKILINK.finditer(line):
                        t = re.split(r'\\?\|', m.group(1))[0].split('#')[0].strip().split('/')[-1].lower()
                        if t not in pub:
                            add("WIKILINK ROTO", m.group(1))
                    for m in PASS32.finditer(line):
                        add("POSIBLE PASSWORD", m.group(0))

    if not findings:
        print("GUARD OK: 0 fugas. content/ listo para publicar.")
        return 0
    print(f"GUARD: {len(findings)} posibles fugas (revisa antes de publicar):\n")
    for rel, n, kind, frag in findings[:300]:
        print(f"  [{kind}] {rel}:{n}  ->  {frag}")
    if len(findings) > 300:
        print(f"  ... y {len(findings) - 300} mas")
    return 1


if __name__ == "__main__":
    sys.exit(main())
