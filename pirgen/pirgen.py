# pirgen.py
import os
import argparse
from core.project_model import ProjectModel
from core.pir_builder import PIRBuilder
from analyzers import get_analyzer

def scan_project(root_path, model):
    """遍历目录并运行分析器"""
    print(f"Scanning root: {root_path}")
    for root, dirs, files in os.walk(root_path):
        # 过滤常见无关目录
        dirs[:] = [d for d in dirs if d not in {'.git', '.idea', '__pycache__', 'build', 'target'}]

        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            
            analyzer = get_analyzer(ext)
            if analyzer:
                rel_path = os.path.relpath(file_path, model.root)
                lang = ext[1:].upper()
                if lang == 'RS': lang = 'Rust'
                
                # 简单模块推断：取父目录名
                module_name = os.path.basename(os.path.dirname(file_path))
                
                uid = model.add_unit(rel_path, lang=lang, role="lib", module=module_name)
                analyzer.analyze(file_path, uid, model)

def resolve_dependencies(model):
    """
    v0.3 stable deps: 对 _unit_dep_keys 做消歧，然后重建 _all_dep_keys。
    """
    print("Resolving dependencies...")
    
    symbol_map = {sym.name: sym.unit_uid for sym in model.symbols}

    resolved = 0
    new_all = set()

    for uid, keys in model._unit_dep_keys.items():
        new_keys = []
        for k in keys:
            verb, target = k.split(":", 1)
            if target.startswith("[") and target.endswith("]"):
                raw = target[1:-1]
                if raw in symbol_map:
                    target = f"{symbol_map[raw]}#{raw}"
                    resolved += 1
            new_k = f"{verb}:{target}"
            new_keys.append(new_k)
            new_all.add(new_k)
        model._unit_dep_keys[uid] = list(dict.fromkeys(new_keys))  # 保序去重

    model._all_dep_keys = new_all
    print(f"  - Resolved {resolved} internal symbol references.")

    


def main():
    parser = argparse.ArgumentParser(description="PIR Generator v0.3")
    parser.add_argument("path", help="Project root path")
    parser.add_argument("--name", help="Project name", default="my_project")
    parser.add_argument("--profile", help="Build profile (e.g. os-riscv, web-java)", default="generic")
    args = parser.parse_args()

    abs_root = os.path.abspath(args.path)
    if not os.path.exists(abs_root):
        print(f"Error: Path {abs_root} does not exist.")
        return

    # 1. 初始化
    model = ProjectModel(name=args.name, root=abs_root, profile=args.profile)
    
    # 2. 扫描分析
    scan_project(abs_root, model)
    
    # 3. 依赖消歧 (新增步骤)
    resolve_dependencies(model)
    
    # 4. 构建输出
    builder = PIRBuilder(model)
    pir_content = builder.build()
    
    output_file = f"{args.name}.pir"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pir_content)
    
    print(f"\n✅ PIR generation complete. Saved to {output_file}")
    print(f"   Stats: {len(model.units)} Units, {len(model.symbols)} Symbols, {len(model.dep_pool_items)} Dependencies")

if __name__ == "__main__":
    main()

# python pirgen.py ./pirgen --name pir_tool --profile python-tool