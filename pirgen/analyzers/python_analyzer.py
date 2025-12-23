# analyzers/python_analyzer.py
import ast
import os
from .base import BaseAnalyzer
from core.project_model import ProjectModel

class PythonAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, unit_uid: str, model: ProjectModel):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 1. 提取符号 (Class, Function)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    is_entry = node.name == 'main'
                    attrs = {"entry": "true"} if is_entry else {}
                    model.add_symbol(node.name, unit_uid, "func", **attrs)
                elif isinstance(node, ast.ClassDef):
                    model.add_symbol(node.name, unit_uid, "class")

            # 2. 提取依赖 (Import)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        model.add_dependency(unit_uid, "import", f"[{alias.name}]")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    # 简单启发式：如果是相对导入或已知模块，尝试标记为模块依赖
                    # 这里为了演示，统一标记为外部引用 [module]
                    if module:
                        model.add_dependency(unit_uid, "import", f"[{module}]")

        except Exception as e:
            print(f"Warning: Failed to analyze {file_path}: {e}")