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
    后期处理：符号消歧。
    将依赖中的 [name] 尝试匹配到具体的 uX#name
    """
    print("Resolving dependencies...")
    
    # 1. 构建符号查找表 { symbol_name: unit_uid }
    # 注意：如果多个单元定义了同名符号（如 static 函数），这里简单的逻辑会覆盖，
    # 生产环境需要根据 module 作用域进行更精确匹配。
    symbol_map = {}
    for sym in model.symbols:
        symbol_map[sym.name] = sym.unit_uid

    # 2. 修正依赖
    resolved_count = 0
    for dep in model.dependencies:
        target = dep.target
        # 检查是否是待解析格式 [name]
        if target.startswith('[') and target.endswith(']'):
            raw_name = target[1:-1]
            # 尝试在符号表中查找
            if raw_name in symbol_map:
                target_uid = symbol_map[raw_name]
                # 更新依赖目标为精确格式：uX#name
                dep.target = f"{target_uid}#{raw_name}"
                resolved_count += 1
    
    print(f"  - Resolved {resolved_count} internal symbol references.")

def main():
    parser = argparse.ArgumentParser(description="PIR Generator v0.2.1")
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
    print(f"   Stats: {len(model.units)} Units, {len(model.symbols)} Symbols, {len(model.dependencies)} Dependencies")

if __name__ == "__main__":
    main()

# python pirgen.py ./pirgen --name pir_tool --profile python-tool