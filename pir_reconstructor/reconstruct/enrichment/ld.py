# reconstruct/enrichment/ld.py
import re
from typing import Dict
from .base import BaseEnrichmentLayer
from ...pir.model import Symbol, DependencyEdge


class LDEnrichmentLayer(BaseEnrichmentLayer):
    """Linker script-specific enrichment layer."""

    _entry_pattern = re.compile(r'ENTRY\s*\(\s*(\w+)\s*\)')
    _symbol_pattern = re.compile(r'^(\w+)\s*=', re.MULTILINE)

    def _infer_symbols(self):
        """从链接器脚本推断符号"""
        for unit in self.pir.units:
            if unit.type != 'LD':
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            # 提取入口点
            entry_match = self._entry_pattern.search(content)
            if entry_match:
                entry_name = entry_match.group(1)
                self.pir.symbols.append(Symbol(
                    name=entry_name,
                    unit=unit.uid,
                    kind='ld_entry',
                    attributes={}
                ))

            # 提取符号定义
            for match in self._symbol_pattern.finditer(content):
                symbol_name = match.group(1)
                self.pir.symbols.append(Symbol(
                    name=symbol_name,
                    unit=unit.uid,
                    kind='ld_symbol',
                    attributes={}
                ))

    def _infer_dependencies(self):
        """从链接器脚本推断依赖"""
        # 实现链接器脚本特定的依赖推断
        pass

    def _infer_entry_points(self):
        """推断入口点"""
        # 入口点已在 _infer_symbols 中标记
        pass
