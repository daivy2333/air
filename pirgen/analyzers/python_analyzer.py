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

            type_checking_nodes = self._find_type_checking_blocks(tree)

            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith("_"):
                        continue

                    attrs = {}
                    if node.name == "main":
                        attrs["entry"] = "true"

                    model.add_symbol(node.name, unit_uid, "func", **attrs)
                    self._process_nested_symbols(node, unit_uid, model)

                elif isinstance(node, ast.ClassDef):
                    if node.name.startswith("_"):
                        continue

                    model.add_symbol(node.name, unit_uid, "class")
                    self._process_nested_symbols(node, unit_uid, model)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.name
                        kind = self._classify_import(name)
                        if node in type_checking_nodes:
                            kind = "import_type_checking"
                        model.add_dependency(
                            unit_uid,
                            kind=kind,
                            target=f"[{name}]",
                        )

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    level = node.level or 0

                    if level > 0:
                        kind = "import_relative"
                        target = "." * level + (module or "")
                    else:
                        kind = self._classify_import(module)
                        target = module

                    if node in type_checking_nodes:
                        kind = "import_type_checking"

                    if target:
                        model.add_dependency(
                            unit_uid,
                            kind=kind,
                            target=f"[{target}]",
                        )

        except Exception as e:
            print(f"Warning: Failed to analyze {file_path}: {e}")

    def _process_nested_symbols(self, node, unit_uid: str, model: ProjectModel):
        for child in ast.walk(node):
            if child is node:
                continue
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not child.name.startswith("_"):
                    model.add_symbol(child.name, unit_uid, "func", nested="true")
            elif isinstance(child, ast.ClassDef):
                if not child.name.startswith("_"):
                    model.add_symbol(child.name, unit_uid, "class", nested="true")

    def _find_type_checking_blocks(self, tree: ast.AST) -> set:
        result = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                test = node.test
                if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
                    for child in node.body:
                        result.add(child)
                        for subchild in ast.walk(child):
                            result.add(subchild)
                elif (
                    isinstance(test, ast.Attribute)
                    and test.attr == "TYPE_CHECKING"
                    and isinstance(test.value, ast.Name)
                    and test.value.id == "typing"
                ):
                    for child in node.body:
                        result.add(child)
                        for subchild in ast.walk(child):
                            result.add(subchild)
        return result

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
