# reconstruct/enrichment/python.py
import ast
from typing import Dict
from .base import BaseEnrichmentLayer
from ...pir.model import Symbol, DependencyEdge


class PythonEnrichmentLayer(BaseEnrichmentLayer):
    """
    Python-specific enrichment layer.

    Extracts symbols, dependencies, and entry points from Python source files.
    """

    def _infer_symbols(self):
        """Infer symbols from Python source files."""
        for unit in self.pir.units:
            if unit.type != 'PY':
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            try:
                tree = ast.parse(content)

                # Extract classes and functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        self.pir.symbols.append(Symbol(
                            name=node.name,
                            unit=unit.uid,
                            kind='class',
                            attributes=self._extract_class_attributes(node)
                        ))
                    elif isinstance(node, ast.FunctionDef):
                        self.pir.symbols.append(Symbol(
                            name=node.name,
                            unit=unit.uid,
                            kind='func',
                            attributes=self._extract_func_attributes(node)
                        ))

            except Exception:
                # Skip files that can't be parsed
                continue

    def _infer_dependencies(self):
        """Infer dependencies from import statements."""
        for unit in self.pir.units:
            if unit.type != 'PY':
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            try:
                tree = ast.parse(content)

                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._process_import(unit.uid, alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            self._process_import(unit.uid, f"{module}.{alias.name}" if alias.name != '*' else module)

            except Exception:
                # Skip files that can't be parsed
                continue

    def _infer_entry_points(self):
        """Infer entry points from Python source files."""
        for unit in self.pir.units:
            if unit.type != 'PY':
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            try:
                tree = ast.parse(content)

                # Check for main function
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == 'main':
                        # Mark as entry point
                        for sym in self.pir.symbols:
                            if sym.name == 'main' and sym.unit == unit.uid:
                                sym.attributes['entry'] = 'true'
                                break

                # Check for if __name__ == "__main__"
                if '__main__' in content:
                    # Find the main function or the last function
                    for sym in reversed(self.pir.symbols):
                        if sym.unit == unit.uid and sym.kind == 'func':
                            sym.attributes['entry'] = 'true'
                            break

                # Check for argparse usage (CLI entry point)
                if 'argparse' in content or 'click' in content:
                    for sym in self.pir.symbols:
                        if sym.unit == unit.uid and sym.kind == 'func':
                            sym.attributes['cli_entry'] = 'true'
                            break

            except Exception:
                # Skip files that can't be parsed
                continue

    def _process_import(self, src_unit: str, import_name: str):
        """Process an import and create dependency edges."""
        # Normalize the import name
        normalized = import_name.split('.')[0]

        # Check if this import matches any unit in our project
        matched_unit = None
        for unit in self.pir.units:
            # Check if the import matches the unit's module
            if normalized in unit.module or unit.module in normalized:
                matched_unit = unit
                break

        # Create dependency edge
        if matched_unit:
            # Internal dependency
            self.pir.edges.append(DependencyEdge(
                src_unit=src_unit,
                dst_unit=matched_unit.uid,
                dst_symbol=None,
                module=None,
                dep_kind='import',
                target_kind='unit'
            ))
        else:
            # External dependency
            self.pir.edges.append(DependencyEdge(
                src_unit=src_unit,
                dst_unit=None,
                dst_symbol=normalized,
                module=None,
                dep_kind='import',
                target_kind='external'
            ))

    def _extract_class_attributes(self, node: ast.ClassDef) -> Dict[str, str]:
        """Extract attributes from a class definition."""
        attrs = {}

        # Check for decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                attrs['decorator'] = decorator.name
            elif isinstance(decorator, ast.Attribute):
                attrs['decorator'] = f"{decorator.value.id}.{decorator.attr}"

        return attrs

    def _extract_func_attributes(self, node: ast.FunctionDef) -> Dict[str, str]:
        """Extract attributes from a function definition."""
        attrs = {}

        # Check for decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                attrs['decorator'] = decorator.name
            elif isinstance(decorator, ast.Attribute):
                attrs['decorator'] = f"{decorator.value.id}.{decorator.attr}"

        # Check if it's a method (first parameter is 'self' or 'cls')
        if node.args.args and node.args.args[0].arg in ('self', 'cls'):
            attrs['method'] = 'true'

        return attrs
