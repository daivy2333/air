# reconstruct/enrichment/rust.py
import re
from typing import Dict
from .base import BaseEnrichmentLayer
from ...pir.model import Symbol, DependencyEdge


class RustEnrichmentLayer(BaseEnrichmentLayer):
    """
    Rust-specific enrichment layer.

    Extracts symbols, dependencies, and entry points from Rust source files.
    """

    # Pattern for function definitions (requires function body)
    _fn_pattern = re.compile(
        r'^\s*(?:pub\s+)?fn\s+(\w+)\s*[^;{]*\{',
        re.MULTILINE
    )

    # Pattern for struct/enum/trait definitions
    _type_pattern = re.compile(
        r'^\s*(?:pub\s+)?(struct|enum|trait)\s+(\w+)',
        re.MULTILINE
    )

    # Pattern for use paths
    _use_pattern = re.compile(
        r'^\s*use\s+([^;]+);',
        re.MULTILINE
    )

    def _infer_symbols(self):
        """Infer symbols from Rust source files."""
        for unit in self.pir.units:
            if unit.type != 'RUST':
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            # Extract functions
            for match in self._fn_pattern.finditer(content):
                name = match.group(1)
                attrs = {}
                if name == "main":
                    attrs["entry"] = "true"
                self.pir.symbols.append(Symbol(
                    name=name,
                    unit=unit.uid,
                    kind='func',
                    attributes=attrs
                ))

            # Extract types (struct/enum/trait)
            for match in self._type_pattern.finditer(content):
                kind, name = match.groups()
                self.pir.symbols.append(Symbol(
                    name=name,
                    unit=unit.uid,
                    kind=kind,
                    attributes={}
                ))

    def _infer_dependencies(self):
        """Infer dependencies from use statements."""
        for unit in self.pir.units:
            if unit.type != 'RUST':
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            for match in self._use_pattern.finditer(content):
                path = match.group(1).strip()

                # Classify the dependency
                if path.startswith("std::"):
                    dep_kind = "use_std"
                elif path.startswith("crate::"):
                    dep_kind = "use_crate"
                elif path.startswith(("self::", "super::")):
                    dep_kind = "use_relative"
                else:
                    dep_kind = "use_external"

                # Check if this use matches any unit in our project
                matched_unit = None
                for u in self.pir.units:
                    if path in u.module or u.module.endswith(path):
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
                        dep_kind='use',
                        target_kind='unit'
                    ))
                else:
                    # External dependency
                    self.pir.edges.append(DependencyEdge(
                        src_unit=unit.uid,
                        dst_unit=None,
                        dst_symbol=path,
                        module=None,
                        dep_kind='use',
                        target_kind='external'
                    ))

    def _infer_entry_points(self):
        """Infer entry points from Rust source files."""
        # Entry points are already marked in _infer_symbols (main function)
        pass
