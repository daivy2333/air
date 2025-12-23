import os, re, argparse, pathlib

# ========= CONFIG =========

IGNORE_DIRS = {'.git', 'build', 'dist', '__pycache__', '.vscode', 'node_modules', 'target'}

LANG_RULES = {
    'C': {
        'ext': {'.c', '.h'},
        'include': r'#include\s+[<"](.+?)[>"]',
        'symbol': r'\b[a-zA-Z_][\w\s\*]*\s+([a-zA-Z_]\w*)\s*\(',
    },
    'CPP': {
        'ext': {'.cpp', '.hpp', '.cc', '.hh'},
        'include': r'#include\s+[<"](.+?)[>"]',
        'symbol': r'\b[a-zA-Z_][\w:<>\s\*&]+?\s+([a-zA-Z_]\w*)\s*\(',
    },
    'PY': {
        'ext': {'.py'},
        'include': r'^(?:from\s+([\w\.]+)|import\s+([\w\.]+))',
        'symbol': r'^\s*def\s+([a-zA-Z_]\w*)',
    },
    'JAVA': {
        'ext': {'.java'},
        'include': r'import\s+([\w\.]+)',
        'symbol': r'\b(class|interface)\s+([A-Z]\w*)',
    },
    'RUST': {
        'ext': {'.rs'},
        'include': r'use\s+([\w:]+)',
        'symbol': r'\bfn\s+([a-zA-Z_]\w*)',
    },
    'ASM': {
        'ext': {'.s', '.S'},
        'include': r'#include\s+[<"](.+?)[>"]',
        'symbol': r'^\s*([a-zA-Z_]\w*):',
    },
    'LD': {
        'ext': {'.ld'},
        'symbol': r'([a-zA-Z_]\w*)\s*=',
    }
}

PROFILE_HINTS = {
    '.rs': 'rust-cargo',
    '.java': 'java-gradle',
    '.py': 'python',
    '.c': 'c-make',
    '.S': 'os-riscv'
}

# ========= CORE =========

def detect_lang(path):
    ext = path.suffix
    for lang, rule in LANG_RULES.items():
        if ext in rule['ext']:
            return lang
    return None

def walk(root):
    for r, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in IGNORE_DIRS]
        for f in fs:
            yield pathlib.Path(r) / f

def main(root, out):
    root = pathlib.Path(root).resolve()

    units = []
    deps = []
    symbols = []
    layout = []
    langs = set()

    unit_id = {}
    uid = 0
    profile = None

    for p in walk(root):
        lang = detect_lang(p)
        if not lang:
            continue

        rel = str(p.relative_to(root))
        u = f'u{uid}'
        uid += 1

        unit_id[rel] = u
        units.append((u, rel, lang))
        langs.add(lang)

        if not profile:
            profile = PROFILE_HINTS.get(p.suffix, 'generic')

        try:
            src = p.read_text(errors='ignore')
        except:
            continue

        rule = LANG_RULES[lang]

        # includes / imports
        if 'include' in rule:
            for m in re.findall(rule['include'], src, re.M):
                target = m[0] if isinstance(m, tuple) else m
                deps.append(f'{u}->include:[{target}]')

        # symbols
        if 'symbol' in rule:
            for m in re.findall(rule['symbol'], src, re.M):
                name = m[-1] if isinstance(m, tuple) else m
                symbols.append(f'{name}:{u}')

        # ld layout
        if lang == 'LD':
            for sec in re.findall(r'\.(\w+)\s*:[^{]*\{', src):
                layout.append(f'.{sec}:{u}')

    # ========= OUTPUT =========

    with open(out, 'w') as o:
        o.write('<pir>\n')

        o.write('<meta>\n')
        o.write(f'name:{root.name}\n')
        o.write(f'root:{root}\n')
        o.write(f'profile:{profile or "generic"}\n')
        o.write(f'lang:{",".join(sorted(langs))}\n')
        o.write('</meta>\n\n')

        o.write('<units>\n')
        for u, p, l in units:
            o.write(f'{u}:{p} type={l}\n')
        o.write('</units>\n\n')

        o.write('<dependencies>\n')
        for d in sorted(set(deps)):
            o.write(d + '\n')
        o.write('</dependencies>\n\n')

        o.write('<symbols>\n')
        for s in sorted(set(symbols)):
            o.write(s + '\n')
        o.write('</symbols>\n\n')

        if layout:
            o.write('<layout>\n')
            for l in layout:
                o.write(l + '\n')
            o.write('</layout>\n\n')

        o.write('</pir>\n')

# ========= CLI =========

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('dir')
    ap.add_argument('-o', default='project.pir')
    args = ap.parse_args()
    main(args.dir, args.o)
