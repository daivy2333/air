# analyzers/c_analyzer.py
import re
from .base import BaseAnalyzer
from core.project_model import ProjectModel

class CAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, unit_uid: str, model: ProjectModel):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 1. 简单的正则提取函数定义 (返回类型 + 函数名 + 括号)
            # 这是一个非常简化的正则，仅作演示
            func_pattern = re.compile(r'^\w+\s+(\w+)\s*\(', re.MULTILINE)
            for match in func_pattern.finditer(content):
                func_name = match.group(1)
                if func_name not in ['if', 'while', 'for', 'switch']:
                    attrs = {}
                    if func_name == 'main': attrs['entry'] = 'true'
                    model.add_symbol(func_name, unit_uid, "func", **attrs)

            # 2. 提取 #include
            include_pattern = re.compile(r'#include\s*[<"]([^>"]+)[>"]')
            for match in include_pattern.finditer(content):
                header = match.group(1)
                # 区分系统头文件和本地头文件略复杂，这里统一处理
                model.add_dependency(unit_uid, "include", f"[{header}]")

        except Exception as e:
            print(f"Warning: Failed to analyze {file_path}: {e}")