# reconstruct/enrichment/c.py
import re
from typing import Dict
from .base import BaseEnrichmentLayer
from ...pir.model import Symbol, DependencyEdge


class CEnrichmentLayer(BaseEnrichmentLayer):
    """
    C-specific enrichment layer.

    Extracts symbols, dependencies, and entry points from C source files.
    """

    # C keywords (for filtering pseudo-functions)
    C_KEYWORDS = {
        "if", "else", "while", "for", "switch", "case",
        "return", "sizeof", "do", "goto"
    }

    # Pattern for function definitions
    _func_pattern = re.compile(
        r'^\s*(?:static\s+|extern\s+|inline\s+)?'   # modifiers
        r'(?:\w+\s+)+?'                              # return type
        r'(\w+)\s*'                                  # function name
        r'\([^;]*\)\s*\{',                         # parameters + function body start
        re.MULTILINE
    )

    # Pattern for struct definitions
    _struct_pattern = re.compile(
        r'^\s*(?:typedef\s+)?struct\s+(\w+)',
        re.MULTILINE
    )

    # Pattern for includes
    _include_pattern = re.compile(
        r'^\s*#include\s*(<[^>]+>|"[^"]+")',
        re.MULTILINE
    )

    def _infer_symbols(self):
        """Infer symbols from C source files."""
        for unit in self.pir.units:
            if unit.type != 'C':
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            # Extract functions
            for match in self._func_pattern.finditer(content):
                func_name = match.group(1)
                if func_name not in self.C_KEYWORDS:
                    attrs = {}
                    if func_name == "main":
                        attrs["entry"] = "true"
                    self.pir.symbols.append(Symbol(
                        name=func_name,
                        unit=unit.uid,
                        kind='func',
                        attributes=attrs
                    ))

            # Extract structs
            for match in self._struct_pattern.finditer(content):
                struct_name = match.group(1)
                self.pir.symbols.append(Symbol(
                    name=struct_name,
                    unit=unit.uid,
                    kind='struct',
                    attributes={}
                ))

    def _infer_dependencies(self):
        """Infer dependencies from include statements."""
        for unit in self.pir.units:
            if unit.type != 'C':
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            for match in self._include_pattern.finditer(content):
                raw = match.group(1)

                if raw.startswith("<"):
                    header = raw[1:-1]
                    dep_type = "include_sys"
                else:
                    header = raw[1:-1]
                    dep_type = "include_local"

                # Check if this include matches any unit in our project
                matched_unit = None
                for u in self.pir.units:
                    if header in u.path or u.path.endswith(header):
                        matched_unit = u
                        break

                # Create dependency edge
                if matched_unit:
                    # Internal dependency
                    self.pir.edges.append(DependencyEdge(
                        src_unit=unit.uid,
                        dst_unit=matched_unit.uid,
                        dst_symbol=None,
                        module=None,
                        dep_kind='include',
                        target_kind='unit'
                    ))
                else:
                    # External dependency
                    self.pir.edges.append(DependencyEdge(
                        src_unit=unit.uid,
                        dst_unit=None,
                        dst_symbol=header,
                        module=None,
                        dep_kind='include',
                        target_kind='external'
                    ))

    def _infer_entry_points(self):
        """Infer entry points from C source files."""
        # Entry points are already marked in _infer_symbols (main function)
        pass
