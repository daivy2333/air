# reconstruct/enrichment/java.py
import re
from typing import Dict
from .base import BaseEnrichmentLayer
from ...pir.model import Symbol, DependencyEdge


class JavaEnrichmentLayer(BaseEnrichmentLayer):
    """Java-specific enrichment layer."""

    _class_pattern = re.compile(
        r'^\s*(?:public\s+)?(?:abstract\s+)?class\s+(\w+)',
        re.MULTILINE
    )

    _method_pattern = re.compile(
        r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s]+)?\s*\{',
        re.MULTILINE
    )

    def _infer_symbols(self):
        """从 Java 源文件推断符号"""
        for unit in self.pir.units:
            if unit.type != 'JAVA':
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            # 提取类
            for match in self._class_pattern.finditer(content):
                class_name = match.group(1)
                self.pir.symbols.append(Symbol(
                    name=class_name,
                    unit=unit.uid,
                    kind='class',
                    attributes={}
                ))

            # 提取方法
            for match in self._method_pattern.finditer(content):
                method_name = match.group(1)
                attrs = {}
                if method_name == "main":
                    attrs["entry"] = "true"
                self.pir.symbols.append(Symbol(
                    name=method_name,
                    unit=unit.uid,
                    kind='func',
                    attributes=attrs
                ))

    def _infer_dependencies(self):
        """从 import 语句推断依赖"""
        # 实现类似 Python 和 C 的依赖推断
        pass

    def _infer_entry_points(self):
        """推断入口点"""
        # main 方法已在 _infer_symbols 中标记
        pass
