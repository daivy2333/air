# reconstruct/enrichment/asm.py
import re
from typing import Dict
from .base import BaseEnrichmentLayer
from ...pir.model import Symbol, DependencyEdge


class ASMEnrichmentLayer(BaseEnrichmentLayer):
    """Assembly-specific enrichment layer."""

    _label_pattern = re.compile(r'^(\w+):', re.MULTILINE)
    _func_pattern = re.compile(r'^\.global\s+(\w+)', re.MULTILINE)

    def _infer_symbols(self):
        """从汇编文件推断符号"""
        for unit in self.pir.units:
            if unit.type not in ('ASM', 'S'):
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            # 提取标签
            for match in self._label_pattern.finditer(content):
                label_name = match.group(1)
                self.pir.symbols.append(Symbol(
                    name=label_name,
                    unit=unit.uid,
                    kind='label',
                    attributes={}
                ))

            # 提取函数
            for match in self._func_pattern.finditer(content):
                func_name = match.group(1)
                self.pir.symbols.append(Symbol(
                    name=func_name,
                    unit=unit.uid,
                    kind='func',
                    attributes={}
                ))

    def _infer_dependencies(self):
        """从汇编文件推断依赖"""
        # 实现汇编特定的依赖推断
        pass

    def _infer_entry_points(self):
        """推断入口点"""
        # 识别 _start 等入口点
        pass
