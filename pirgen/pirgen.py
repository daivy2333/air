import os
import argparse
import fnmatch
from collections import defaultdict

from .core.project_model import ProjectModel, Unit
from .core.pir_builder import PIRBuilder
from .core.dep_canon import canonicalize_dependencies
from .core.analysis_cache import AnalysisCache
from .analyzers import get_analyzer

DEFAULT_IGNORED = {
    ".git",
    ".idea",
    "__pycache__",
    "build",
    "target",
    "node_modules",
    ".venv",
    "venv",
    ".env",
    "tests",
    "test",
    "__tests__",
    ".pytest_cache",
    "examples",
    "docs",
    "doc",
    "dist",
    ".dist",
}

USER_IGNORED = set()


def discover_source_files(root_path):
    results = []
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [
            d
            for d in dirs
            if d not in DEFAULT_IGNORED
            and d not in USER_IGNORED
            and not any(fnmatch.fnmatch(d, p) for p in USER_IGNORED)
        ]
        for file in files:
            ext = os.path.splitext(file)[1]
            if get_analyzer(ext):
                results.append(os.path.join(root, file))
    return results


def infer_unit_meta(file_path, project_root):
    rel_path = os.path.relpath(file_path, project_root)
    ext = os.path.splitext(file_path)[1]
    lang = ext[1:].upper()
    if lang == "RS":
        lang = "Rust"
    module = os.path.basename(os.path.dirname(file_path)) or "root"
    return rel_path, lang, module


def sync_entry_roles(model):
    entry_uids = {s.unit_uid for s in model.symbols if s.attrs.get("entry") == "true"}
    for i, unit in enumerate(model.units):
        if unit.uid in entry_uids and unit.role == "lib":
            model.units[i] = Unit(unit.uid, unit.path, unit.lang, "entry", unit.module)


def scan_project(root_path, model, use_cache=True):
    print(f"Scanning project: {root_path}")

    cache = AnalysisCache(model.root) if use_cache else None
    cache_hits = 0
    cache_misses = 0
    unit_cache = {}

    for file_path in discover_source_files(root_path):
        rel_path, lang, module = infer_unit_meta(file_path, model.root)

        if rel_path not in unit_cache:
            uid = model.add_unit(rel_path, lang=lang, role="lib", module=module)
            unit_cache[rel_path] = uid
        else:
            uid = unit_cache[rel_path]

        analyzer = get_analyzer(os.path.splitext(file_path)[1])
        if not analyzer:
            continue

        if cache:
            cached = cache.load(file_path, lang)
            if cached:
                for s in cached.get("symbols", []):
                    model.add_symbol(s["name"], uid, s["kind"], **s.get("attrs", {}))
                for k in cached.get("deps", []):
                    verb, target = k.split(":", 1)
                    model.add_dependency(uid, verb, target)
                cache_hits += 1
                continue
            cache_misses += 1

        analyzer.analyze(file_path, uid, model)

        if cache:
            cache.save(
                file_path,
                lang,
                {
                    "unit": {"role": "lib", "module": module},
                    "symbols": [
                        {"name": s.name, "kind": s.kind, "attrs": s.attrs}
                        for s in model.symbols
                        if s.unit_uid == uid
                    ],
                    "deps": model._unit_dep_keys.get(uid, []),
                },
            )

    if cache:
        print(f"  Cache hits: {cache_hits}, misses: {cache_misses}")


def resolve_dependencies(model):
    print("Resolving dependencies...")

    symbol_index = defaultdict(list)
    for sym in model.symbols:
        symbol_index[sym.name].append(sym.unit_uid)

    resolved = 0
    dropped = 0
    new_all_keys = set()

    for uid, dep_keys in model._unit_dep_keys.items():
        resolved_keys = []

        for key in dep_keys:
            verb, target = key.split(":", 1)

            if target.startswith("[") and target.endswith("]"):
                name = target[1:-1]
                candidates = symbol_index.get(name)

                if candidates and len(candidates) == 1:
                    target = f"{candidates[0]}#{name}"
                    resolved += 1
                elif verb == "call":
                    dropped += 1
                    continue

            new_key = f"{verb}:{target}"
            resolved_keys.append(new_key)
            new_all_keys.add(new_key)

        model._unit_dep_keys[uid] = list(dict.fromkeys(resolved_keys))

    model._all_dep_keys = new_all_keys
    print(f"  - Resolved {resolved} references, dropped {dropped} unresolvable")


def main():
    global USER_IGNORED

    parser = argparse.ArgumentParser(description="AIR - AI Project Analyzer")
    parser.add_argument("path", help="Project root path")
    parser.add_argument("--name", default="my_project")
    parser.add_argument("--no-cache", action="store_true", help="Disable cache")
    parser.add_argument(
        "--ignore",
        "-i",
        action="append",
        default=[],
        dest="ignore_patterns",
        help="Ignore directories matching pattern (can be used multiple times)",
    )
    args = parser.parse_args()

    USER_IGNORED = set(args.ignore_patterns)

    abs_root = os.path.abspath(args.path)
    if not os.path.exists(abs_root):
        print(f"Error: Path {abs_root} does not exist.")
        return

    model = ProjectModel(name=args.name, root=abs_root, profile="generic")

    scan_project(abs_root, model, use_cache=not args.no_cache)
    sync_entry_roles(model)
    resolve_dependencies(model)
    canonicalize_dependencies(model)
    model.finalize_dependencies()

    builder = PIRBuilder(model)
    pir_content = builder.build()

    output_file = f"{args.name}.pir"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pir_content)

    ignored = DEFAULT_IGNORED | USER_IGNORED
    print(f"\n✅ PIR generated: {output_file}")
    print(
        f"   Units: {len(model.units)} | Symbols: {len(model.symbols)} | Deps: {len(model.dep_pool_items)}"
    )
    if args.ignore_patterns:
        print(f"   Ignored patterns: {', '.join(args.ignore_patterns)}")


if __name__ == "__main__":
    main()
