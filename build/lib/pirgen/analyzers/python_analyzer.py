# analyzers/python_analyzer.py
import ast
import os
from .base import BaseAnalyzer
from ..core.project_model import ProjectModel


class PythonAnalyzer(BaseAnalyzer):
    """
    Python analyzer for PIR.

    Design goals:
    - Export only module-level API symbols
    - Preserve import semantics for dependency factoring
    - Avoid AST noise (methods, locals, tests)
    """

    def analyze(self, file_path: str, unit_uid: str, model: ProjectModel):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            tree = ast.parse(content)
            self._analyze_symbols(tree, unit_uid, model)
            self._analyze_imports(tree, file_path, unit_uid, model)

        except Exception as e:
            print(f"Warning: Failed to analyze {file_path}: {e}")

    # ----------------------------
    # Symbol analysis
    # ----------------------------

    def _analyze_symbols(self, tree: ast.Module, unit_uid: str, model: ProjectModel):
        for node in tree.body:
            # 顶层函数
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue

                attrs = {}
                if node.name == "main":
                    attrs["entry"] = "true"

                model.add_symbol(node.name, unit_uid, "func", **attrs)

            # 顶层类
            elif isinstance(node, ast.ClassDef):
                if node.name.startswith("_"):
                    continue

                model.add_symbol(node.name, unit_uid, "class")

    # ----------------------------
    # Import analysis
    # ----------------------------

    def _analyze_imports(
        self,
        tree: ast.Module,
        file_path: str,
        unit_uid: str,
        model: ProjectModel,
    ):
        for node in tree.body:
            # import xxx
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    kind = self._classify_import(name)
                    model.add_dependency(
                        unit_uid,
                        "import",
                        f"[{name}]",
                        kind=kind,
                    )

            # from xxx import yyy
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                level = node.level or 0

                if level > 0:
                    kind = "import_relative"
                    target = "." * level + (module or "")
                else:
                    kind = self._classify_import(module)
                    target = module

                if target:
                    model.add_dependency(
                        unit_uid,
                        "import",
                        f"[{target}]",
                        kind=kind,
                    )

    # ----------------------------
    # Import classification
    # ----------------------------

    def _classify_import(self, module: str) -> str:
        if not module:
            return "import_unknown"

        root = module.split(".", 1)[0]

        if root in {"os", "sys", "re", "ast", "typing", "dataclasses", "abc"}:
            return "import_std"

        if root.startswith("_"):
            return "import_private"

        return "import_external"
