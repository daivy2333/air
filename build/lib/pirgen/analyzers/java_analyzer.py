# analyzers/java_analyzer.py
import re
from .base import BaseAnalyzer
from ..core.project_model import ProjectModel

class JavaAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, unit_uid: str, model: ProjectModel):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            # 简单的逐行正则匹配
            # 1. 提取 Class/Interface 定义
            class_pattern = re.compile(r'^\s*(?:public\s+)?(?:abstract\s+)?(class|interface|enum)\s+(\w+)')
            
            # 2. 提取 Import
            import_pattern = re.compile(r'^\s*import\s+([\w\.]+);')

            for line in lines:
                line = line.strip()
                # 跳过注释
                if line.startswith("//") or line.startswith("*"):
                    continue

                # 匹配符号定义
                match_class = class_pattern.search(line)
                if match_class:
                    kind = match_class.group(1) # class/interface
                    name = match_class.group(2)
                    # Java 中 public class 往往是该文件的主要入口
                    attrs = {"entry": "true"} if "public" in line else {}
                    model.add_symbol(name, unit_uid, kind, **attrs)

                # 匹配依赖
                match_import = import_pattern.search(line)
                if match_import:
                    target = match_import.group(1)
                    # 记录对外部包或类的依赖
                    model.add_dependency(unit_uid, "import", f"[{target}]")

        except Exception as e:
            print(f"Warning: Java analysis failed for {file_path}: {e}")