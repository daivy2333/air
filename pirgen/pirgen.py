# pirgen.py
import os
import argparse
from collections import defaultdict

from core.project_model import ProjectModel
from core.pir_builder import PIRBuilder
from core.dep_canon import canonicalize_dependencies
from core.profile_canon import ProfileCanonicalizer
from analyzers import get_analyzer


# -----------------------------
# 1. 扫描阶段：只做文件发现
# -----------------------------
IGNORED_DIRS = {'.git', '.idea', '__pycache__', 'build', 'target'}

def discover_source_files(root_path):
    """返回 (file_path, ext) 列表"""
    results = []
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            ext = os.path.splitext(file)[1]
            if get_analyzer(ext):
                results.append(os.path.join(root, file))
    return results


# -----------------------------
# 2. Unit 创建策略（去重）
# -----------------------------
def infer_unit_meta(file_path, project_root):
    rel_path = os.path.relpath(file_path, project_root)
    ext = os.path.splitext(file_path)[1]
    lang = ext[1:].upper()
    if lang == "RS":
        lang = "Rust"

    module = os.path.basename(os.path.dirname(file_path)) or "root"
    return rel_path, lang, module


def scan_project(root_path, model):
    print(f"Scanning project: {root_path}")

    unit_cache = {}  # rel_path -> uid

    for file_path in discover_source_files(root_path):
        rel_path, lang, module = infer_unit_meta(file_path, model.root)

        if rel_path not in unit_cache:
            uid = model.add_unit(
                rel_path,
                lang=lang,
                role="lib",
                module=module
            )
            unit_cache[rel_path] = uid
        else:
            uid = unit_cache[rel_path]

        analyzer = get_analyzer(os.path.splitext(file_path)[1])
        analyzer.analyze(file_path, uid, model)


# -----------------------------
# 3. 依赖消歧（算法优化重点）
# -----------------------------
def resolve_dependencies(model):
    """
    改进点：
    - 预构建 symbol -> [unit_uid] 映射
    - 只处理 [] 包裹的符号
    - 避免重复字符串 split / join
    """
    print("Resolving dependencies...")

    symbol_index = defaultdict(list)
    for sym in model.symbols:
        symbol_index[sym.name].append(sym.unit_uid)

    resolved = 0
    new_all_keys = set()

    for uid, dep_keys in model._unit_dep_keys.items():
        resolved_keys = []

        for key in dep_keys:
            verb, target = key.split(":", 1)

            if target.startswith("[") and target.endswith("]"):
                name = target[1:-1]
                candidates = symbol_index.get(name)

                # 只在“唯一可判定”时消歧
                if candidates and len(candidates) == 1:
                    target = f"{candidates[0]}#{name}"
                    resolved += 1

            new_key = f"{verb}:{target}"
            resolved_keys.append(new_key)
            new_all_keys.add(new_key)

        # 保序去重
        model._unit_dep_keys[uid] = list(dict.fromkeys(resolved_keys))

    model._all_dep_keys = new_all_keys
    print(f"  - Resolved {resolved} internal references")


# -----------------------------
# 4. CLI 主流程
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="PIR Generator v0.3 (optimized)")
    parser.add_argument("path", help="Project root path")
    parser.add_argument("--name", default="my_project")
    parser.add_argument("--profile", default="generic")
    args = parser.parse_args()

    abs_root = os.path.abspath(args.path)
    if not os.path.exists(abs_root):
        print(f"Error: Path {abs_root} does not exist.")
        return

    model = ProjectModel(
        name=args.name,
        root=abs_root,
        profile=args.profile
    )

    scan_project(abs_root, model)
    resolve_dependencies(model)
    canonicalize_dependencies(model)
    model.finalize_dependencies()

    # Apply profile-aware canonicalization (v0.4)
    ProfileCanonicalizer().apply(model)

    builder = PIRBuilder(model)
    pir_content = builder.build()

    output_file = f"{args.name}.pir"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pir_content)

    print("\n✅ PIR generation complete")
    print(f"   Output: {output_file}")
    print(f"   Units: {len(model.units)}")
    print(f"   Symbols: {len(model.symbols)}")
    print(f"   Dependencies: {len(model.dep_pool_items)}")


if __name__ == "__main__":
    main()


# python pirgen.py ./pirgen --name pir_tool --profile python-tool