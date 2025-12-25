# reconstruct/enrichment/asm.py
import re
from typing import Dict, Set, Optional
from .base import BaseEnrichmentLayer
from ...pir.model import Symbol, DependencyEdge


class ASMEnrichmentLayer(BaseEnrichmentLayer):
    """Assembly-specific enrichment layer with RISC-V support."""

    # 通用模式
    _label_pattern = re.compile(r'^(\w+):', re.MULTILINE)
    _func_pattern = re.compile(r'^\.global\s+(\w+)', re.MULTILINE)

    # RISC-V 特定模式
    _riscv_ecall_pattern = re.compile(r'ecall', re.IGNORECASE)
    _riscv_csr_pattern = re.compile(r'csrr\w*\s+(\w+),\s*(\w+)', re.IGNORECASE)
    _riscv_mret_pattern = re.compile(r'mret', re.IGNORECASE)
    _riscv_sret_pattern = re.compile(r'sret', re.IGNORECASE)
    _riscv_fence_pattern = re.compile(r'fence(\.i)?', re.IGNORECASE)

    # RISC-V CSR 寄存器集合
    _riscv_csrs = {
        # Machine CSRs
        'mstatus', 'misa', 'medeleg', 'mideleg', 'mie', 'mtvec', 'mcounteren',
        'mscratch', 'mepc', 'mcause', 'mtval', 'mip', 'mcycle', 'minstret',
        'mcycleh', 'minstreth',
        # Supervisor CSRs
        'sstatus', 'sedeleg', 'sideleg', 'sie', 'stvec', 'scounteren',
        'sscratch', 'sepc', 'scause', 'stval', 'sip', 'satp',
        # User CSRs
        'ustatus', 'utvec', 'uscratch', 'uepc', 'ucause', 'utval', 'uip',
        # Timer and Performance Counters
        'mtime', 'mtimeh', 'mtimecmp', 'mtimecmph',
    }

    # RISC-V 特殊符号
    _riscv_entry_points = {'_start', 'trap_entry', 'trap_vector', 'irq_handler'}

    # RISC-V 指令集扩展标识
    _riscv_extensions = {
        'RV32I', 'RV64I', 'RV32M', 'RV64M', 'RV32A', 'RV64A',
        'RV32F', 'RV64F', 'RV32D', 'RV64D', 'RV32C', 'RV64C'
    }

    def __init__(self, pir_ast, project_root: str):
        super().__init__(pir_ast, project_root)
        self.detected_arch: Optional[str] = None
        self.detected_extensions: Set[str] = set()

    def _infer_symbols(self):
        """从汇编文件推断符号，支持 RISC-V 特定符号"""
        for unit in self.pir.units:
            if unit.type not in ('ASM', 'S'):
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            # 检测 RISC-V 架构
            self._detect_riscv_architecture(content, unit)

            # 提取标签
            for match in self._label_pattern.finditer(content):
                label_name = match.group(1)
                attrs = {}

                # 标记 RISC-V 特殊符号
                if label_name in self._riscv_entry_points:
                    attrs['entry'] = 'true'
                    attrs['type'] = 'riscv_entry'

                self.pir.symbols.append(Symbol(
                    name=label_name,
                    unit=unit.uid,
                    kind='label',
                    attributes=attrs
                ))

            # 提取函数
            for match in self._func_pattern.finditer(content):
                func_name = match.group(1)
                attrs = {}

                # 检查是否为中断处理函数
                if self._is_trap_handler(func_name, content):
                    attrs['type'] = 'trap_handler'

                self.pir.symbols.append(Symbol(
                    name=func_name,
                    unit=unit.uid,
                    kind='func',
                    attributes=attrs
                ))

            # 提取 CSR 操作
            self._extract_csr_operations(content, unit)

    def _infer_dependencies(self):
        """从汇编文件推断依赖，支持 RISC-V 特定依赖"""
        for unit in self.pir.units:
            if unit.type not in ('ASM', 'S'):
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            # 检测系统调用
            self._detect_syscalls(content, unit)

            # 检测内存屏障依赖
            self._detect_memory_barriers(content, unit)

    def _infer_entry_points(self):
        """推断入口点，支持 RISC-V 特定入口点"""
        for unit in self.pir.units:
            if unit.type not in ('ASM', 'S'):
                continue

            file_path = self.project_root / unit.path
            if not file_path.exists():
                continue

            content = self._get_file_content(file_path)
            if not content:
                continue

            # 检查 _start 符号
            if '_start' in content:
                for sym in self.pir.symbols:
                    if sym.name == '_start' and sym.unit == unit.uid:
                        sym.attributes['entry'] = 'true'
                        sym.attributes['arch'] = 'riscv'
                        break

            # 检查中断向量表
            if 'trap_vector' in content or 'trap_entry' in content:
                for sym in self.pir.symbols:
                    if sym.name in ('trap_vector', 'trap_entry') and sym.unit == unit.uid:
                        sym.attributes['type'] = 'interrupt_vector'
                        break

    def _detect_riscv_architecture(self, content: str, unit):
        """检测 RISC-V 架构和扩展"""
        # 检测 RISC-V 特征指令
        has_ecall = self._riscv_ecall_pattern.search(content) is not None
        has_csr = self._riscv_csr_pattern.search(content) is not None
        has_mret = self._riscv_mret_pattern.search(content) is not None
        has_sret = self._riscv_sret_pattern.search(content) is not None

        if has_ecall or has_csr or has_mret or has_sret:
            self.detected_arch = 'riscv'
            unit.attributes = unit.attributes or {}
            unit.attributes['arch'] = 'riscv'

            # 检测指令集扩展
            if 'mret' in content.lower():
                self.detected_extensions.add('M')  # Machine mode
            if 'sret' in content.lower():
                self.detected_extensions.add('S')  # Supervisor mode
            if self._riscv_fence_pattern.search(content):
                self.detected_extensions.add('A')  # Atomic instructions

    def _is_trap_handler(self, func_name: str, content: str) -> bool:
        """判断是否为中断/异常处理函数"""
        trap_keywords = {'trap', 'exception', 'interrupt', 'irq', 'handler'}
        return any(kw in func_name.lower() for kw in trap_keywords)

    def _extract_csr_operations(self, content: str, unit):
        """提取 CSR 操作"""
        for match in self._riscv_csr_pattern.finditer(content):
            rd = match.group(1)
            csr = match.group(2).lower()

            if csr in self._riscv_csrs:
                # 创建 CSR 操作符号
                sym_name = f'csr_{csr}'
                self.pir.symbols.append(Symbol(
                    name=sym_name,
                    unit=unit.uid,
                    kind='csr',
                    attributes={
                        'csr_name': csr,
                        'access_mode': 'read' if 'csrr' in match.group(0) else 'write'
                    }
                ))

    def _detect_syscalls(self, content: str, unit):
        """检测系统调用"""
        for match in self._riscv_ecall_pattern.finditer(content):
            # 添加系统调用依赖
            self.pir.edges.append(DependencyEdge(
                src_unit=unit.uid,
                dst_unit=None,
                dst_symbol=None,
                module='kernel',
                dep_kind='syscall',
                target_kind='external'
            ))

    def _detect_memory_barriers(self, content: str, unit):
        """检测内存屏障操作"""
        for match in self._riscv_fence_pattern.finditer(content):
            fence_type = match.group(1) or ''
            # 添加内存屏障符号
            sym_name = f'memory_barrier{fence_type}'
            self.pir.symbols.append(Symbol(
                name=sym_name,
                unit=unit.uid,
                kind='memory_barrier',
                attributes={
                    'barrier_type': fence_type if fence_type else 'rw'
                }
            ))
            
