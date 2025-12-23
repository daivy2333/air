# analyzers/rust_analyzer.py
import re
from .base import BaseAnalyzer
from core.project_model import ProjectModel

class RustAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, unit_uid: str, model: ProjectModel):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 1. 提取函数 (fn name)
            # 排除 test 模块中的函数通常比较复杂，这里做简单提取
            fn_pattern = re.compile(r'fn\s+(\w+)\s*<*[^(\n]*\(')
            for match in fn_pattern.finditer(content):
                name = match.group(1)
                if name != "main":
                    model.add_symbol(name, unit_uid, "func")
                else:
                    model.add_symbol(name, unit_uid, "func", entry="true")

            # 2. 提取结构体和枚举 (struct/enum name)
            type_pattern = re.compile(r'(struct|enum|trait)\s+(\w+)')
            for match in type_pattern.finditer(content):
                kind = match.group(1)
                name = match.group(2)
                model.add_symbol(name, unit_uid, kind)

            # 3. 提取 Use 依赖
            use_pattern = re.compile(r'use\s+([\w:]+)(?:;|::)')
            for match in use_pattern.finditer(content):
                target = match.group(1)
                model.add_dependency(unit_uid, "use", f"[{target}]")

        except Exception as e:
            print(f"Warning: Rust analysis failed for {file_path}: {e}")