# analyzers/rust_analyzer.py
import re
from .base import BaseAnalyzer
from core.project_model import ProjectModel


class RustAnalyzer(BaseAnalyzer):
    """
    Lightweight Rust analyzer for PIR.

    Design principles:
    - Capture only high-confidence definitions
    - Preserve module boundary semantics
    - Enable dependency factoring at PIR build stage
    """

    # fn 定义（要求有函数体）
    _fn_pattern = re.compile(
        r'^\s*(?:pub\s+)?fn\s+(\w+)\s*[^;{]*\{',
        re.MULTILINE
    )

    # struct / enum / trait 定义
    _type_pattern = re.compile(
        r'^\s*(?:pub\s+)?(struct|enum|trait)\s+(\w+)',
        re.MULTILINE
    )

    # use 路径
    _use_pattern = re.compile(
        r'^\s*use\s+([^;]+);',
        re.MULTILINE
    )

    def analyze(self, file_path: str, unit_uid: str, model: ProjectModel):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            self._analyze_functions(content, unit_uid, model)
            self._analyze_types(content, unit_uid, model)
            self._analyze_uses(content, unit_uid, model)

        except Exception as e:
            print(f"Warning: Rust analysis failed for {file_path}: {e}")

    # ----------------------------
    # Function analysis
    # ----------------------------

    def _analyze_functions(self, content: str, unit_uid: str, model: ProjectModel):
        for match in self._fn_pattern.finditer(content):
            name = match.group(1)

            attrs = {}
            if name == "main":
                attrs["entry"] = "true"

            model.add_symbol(name, unit_uid, "func", **attrs)

    # ----------------------------
    # Type analysis
    # ----------------------------

    def _analyze_types(self, content: str, unit_uid: str, model: ProjectModel):
        for match in self._type_pattern.finditer(content):
            kind, name = match.groups()
            model.add_symbol(name, unit_uid, kind)

    # ----------------------------
    # Use dependency analysis
    # ----------------------------

    def _analyze_uses(self, content: str, unit_uid: str, model: ProjectModel):
        for match in self._use_pattern.finditer(content):
            path = match.group(1).strip()

            if path.startswith("std::"):
                dep_kind = "use_std"
            elif path.startswith("crate::"):
                dep_kind = "use_crate"
            elif path.startswith(("self::", "super::")):
                dep_kind = "use_relative"
            else:
                dep_kind = "use_external"

            model.add_dependency(
                unit_uid,
                "use",
                f"[{path}]",
                kind=dep_kind
            )
