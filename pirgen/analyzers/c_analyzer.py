# analyzers/c_analyzer.py
import re
from .base import BaseAnalyzer
from ..core.project_model import ProjectModel


# C 关键字（用于过滤伪函数）
C_KEYWORDS = {
    "if", "else", "while", "for", "switch", "case",
    "return", "sizeof", "do", "goto"
}


class CAnalyzer(BaseAnalyzer):
    """
    Lightweight C source analyzer for PIR generation.

    Design principles:
    - Be conservative: prefer missing symbols over false positives
    - Preserve structure for later dependency factoring
    - Avoid overfitting to full C grammar
    - Support multiline continuation and modern C++ features
    """

    _func_pattern = re.compile(
        r'^\s*'
        r'(?:template\s*<\w[^>]*>\s*)?'
        r'(?:static\s+|extern\s+|inline\s+|constexpr\s+)?'
        r'(?:'
        r'(?:\w+\s+)+?'
        r'|'
        r'auto\s+'
        r')'
        r'(\w+)\s*'
        r'\([^)]*\)\s*'
        r'(?:->[^{]+)?'
        r'\{',
        re.MULTILINE
    )

    _include_pattern = re.compile(
        r'^\s*#include\s*(<[^>]+>|"[^"]+")',
        re.MULTILINE
    )

    @staticmethod
    def _join_continuation_lines(content: str) -> str:
        lines = content.split('\n')
        result = []
        i = 0
        while i < len(lines):
            line = lines[i]
            while line.endswith('\\') and i + 1 < len(lines):
                line = line[:-1] + lines[i + 1]
                i += 1
            if line.strip().startswith('template') and line.rstrip().endswith('>') and i + 1 < len(lines):
                line = line + ' ' + lines[i + 1].strip()
                i += 1
            result.append(line)
            i += 1
        return '\n'.join(result)

    def analyze(self, file_path: str, unit_uid: str, model: ProjectModel):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            joined_content = self._join_continuation_lines(content)
            self._analyze_functions(joined_content, unit_uid, model)
            self._analyze_includes(joined_content, unit_uid, model)

        except Exception as e:
            print(f"Warning: Failed to analyze {file_path}: {e}")

    # ----------------------------
    # Function analysis
    # ----------------------------

    def _analyze_functions(self, content: str, unit_uid: str, model: ProjectModel):
        for match in self._func_pattern.finditer(content):
            func_name = match.group(1)

            if func_name in C_KEYWORDS:
                continue

            attrs = {}
            if func_name == "main":
                attrs["entry"] = "true"

            model.add_symbol(func_name, unit_uid, "func", **attrs)

    # ----------------------------
    # Include analysis
    # ----------------------------

    def _analyze_includes(self, content: str, unit_uid: str, model: ProjectModel):
        for match in self._include_pattern.finditer(content):
            raw = match.group(1)

            if raw.startswith("<"):
                header = raw[1:-1]
                dep_type = "include_sys"
            else:
                header = raw[1:-1]
                dep_type = "include_local"

            # 现在仍然输出为 include，
            # 但 dep_type 已经可以用于后续归约
            model.add_dependency(unit_uid, "include", f"[{header}]", kind=dep_type)
