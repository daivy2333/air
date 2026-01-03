import re
from typing import Dict, List, Optional
from analyzers.base import BaseAnalyzer

class ASMAnalyzer(BaseAnalyzer):
    """汇编代码分析器 - 支持多架构"""

    # 标签正则（支持更多格式）
    LABEL_PATTERN = re.compile(r'^([A-Za-z_][\w]*):')

    # 指令正则
    INSTRUCTION_PATTERN = re.compile(
        r'^\s*'
        r'(?:[A-Za-z_][\w]*:\s+)?'  # 可选标签
        r'(?P<opcode>[A-Za-z.]+)'  # 操作码（支持点号，如RISC-V的fadd.d）
        r'(?:\s+(?P<operands>[^;#]*))?'  # 操作数
    )

    # 控制流指令（扩展到支持更多架构）
    CONTROL_FLOW = {
        # x86/x86_64
        'jmp', 'je', 'jne', 'jz', 'jnz', 'jg', 'jl', 'jge', 'jle',
        'ja', 'jb', 'jae', 'jbe', 'call', 'ret', 'loop', 'iret',
        # RISC-V
        'beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu', 'jal', 'jalr',
        # ARM
        'b', 'bl', 'bx', 'blx',
        # 通用
        'br', 'bra'
    }

    # 系统调用指令
    SYSCALL_INSTRUCTIONS = {
        'syscall', 'int', 'svc', 'ecall', 'ebreak', 'eret', 'mret'
    }

    # 内存操作指令
    MEMORY_INSTRUCTIONS = {
        'mov', 'ldr', 'str', 'ld', 'st', 'lw', 'sw', 'lb', 'sb', 'lh', 'sh',
        'push', 'pop', 'lea', 'load', 'store'
    }

    def __init__(self, source_code: str, pir_data: Dict):
        super().__init__(source_code, pir_data)
        self._preprocess()

    def _preprocess(self):
        """预处理汇编代码"""
        # 移除注释
        self.code = re.sub(r';.*', '', self.source_code)

        # 按行分割
        self.lines = self.code.split('\n')

        # 构建标签索引
        self.label_index = {}
        for i, line in enumerate(self.lines):
            match = self.LABEL_PATTERN.match(line)
            if match:
                label = match.group(1)
                self.label_index[label] = i

    def extract_signature(self, symbol_name: str) -> Optional[str]:
        """提取汇编函数签名（不适用）"""
        return None

    def extract_behavior(self, symbol_name: str) -> List[str]:
        """提取汇编函数行为描述"""
        behaviors = []

        # 查找标签位置
        if symbol_name not in self.label_index:
            return behaviors

        start_line = self.label_index[symbol_name]

        # 分析指令
        for i in range(start_line, len(self.lines)):
            line = self.lines[i].strip()
            if not line or line.startswith('.'):
                continue

            # 遇到下一个标签则停止
            if self.LABEL_PATTERN.match(line) and i > start_line:
                break

            match = self.INSTRUCTION_PATTERN.match(line)
            if match:
                opcode = match.group('opcode').lower()
                behavior = self._analyze_instruction(opcode)
                if behavior:
                    behaviors.append(behavior)
                    if len(behaviors) >= 6:
                        break

        return behaviors

    def _analyze_instruction(self, opcode: str) -> Optional[str]:
        """分析单条指令"""
        opcode_lower = opcode.lower()

        # 栈操作
        if opcode_lower in ['push', 'pop', 'pusha', 'popa', 'pushf', 'popf']:
            return 'manipulates stack'

        # 数据移动
        elif opcode_lower in ['mov', 'lea', 'movsx', 'movzx', 'movsxd', 'cmov']:
            return 'moves data'

        # 算术运算
        elif opcode_lower in ['add', 'sub', 'mul', 'div', 'imul', 'idiv', 'neg', 
                           'inc', 'dec', 'adc', 'sbb']:
            return 'performs arithmetic'

        # 逻辑运算
        elif opcode_lower in ['and', 'or', 'xor', 'not', 'shl', 'shr', 'sar', 'rol', 'ror']:
            return 'performs logic operation'

        # 比较
        elif opcode_lower in ['cmp', 'test']:
            return 'compares values'

        # 分支（x86）
        elif opcode_lower in ['jmp', 'je', 'jne', 'jz', 'jnz', 'jg', 'jl', 'jge', 'jle',
                           'ja', 'jb', 'jae', 'jbe', 'loop']:
            return 'branches'

        # 分支（RISC-V）
        elif opcode_lower in ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']:
            return 'branches'

        # 跳转和链接（RISC-V/ARM）
        elif opcode_lower in ['jal', 'jalr', 'b', 'bl', 'bx', 'blx']:
            return 'branches or calls'

        # 函数调用
        elif opcode_lower == 'call':
            return 'calls function'

        # 返回
        elif opcode_lower in ['ret', 'iret', 'eret', 'mret']:
            return 'returns'

        # 系统调用
        elif opcode_lower in self.SYSCALL_INSTRUCTIONS:
            return 'system call'

        # 原子操作
        elif opcode_lower in ['lock', 'xadd', 'cmpxchg', 'lr', 'sc', 'amoswap', 'amoadd']:
            return 'atomic operation'

        # 内存操作
        elif opcode_lower in self.MEMORY_INSTRUCTIONS:
            return 'accesses memory'

        # 标志操作
        elif opcode_lower in ['clc', 'stc', 'cmc', 'cld', 'std']:
            return 'manipulates flags'

        # 浮点运算
        elif opcode_lower.startswith('f') or opcode_lower.startswith('d'):
            return 'performs floating-point operation'

        # SIMD操作
        elif opcode_lower.startswith(('sse', 'avx', 'mmx')):
            return 'performs SIMD operation'

        return None

    def extract_callchain(self, symbol_name: str) -> List[str]:
        """提取调用链"""
        callchain = []

        # 查找标签位置
        if symbol_name not in self.label_index:
            return callchain

        start_line = self.label_index[symbol_name]

        # 查找调用指令（支持多种架构）
        for i in range(start_line, len(self.lines)):
            line = self.lines[i].strip()

            # 跳过空行和注释
            if not line or line.startswith(';') or line.startswith('#'):
                continue

            # 跳过伪指令
            if line.startswith('.'):
                continue

            # 遇到下一个标签则停止
            if self.LABEL_PATTERN.match(line) and i > start_line:
                break

            match = self.INSTRUCTION_PATTERN.match(line)
            if match:
                opcode = match.group('opcode').lower()
                operands = match.group('operands') or ''

                # 处理不同架构的调用指令
                if opcode in ['call', 'jal', 'jalr', 'bl', 'blx']:
                    # 提取调用的目标
                    if opcode == 'call':
                        target = operands.strip().split()[0]
                    elif opcode in ['jal', 'jalr']:
                        # RISC-V: jal rd, offset 或 jalr rd, rs1, offset
                        parts = operands.split(',')
                        if len(parts) >= 2:
                            target = parts[-1].strip()
                        else:
                            target = operands.strip()
                    else:  # bl, blx
                        # ARM: bl label
                        target = operands.strip()

                    if target and target not in ['zero', 'x0', 'ra', 'x1']:  # 排除特殊寄存器
                        callchain.append(target)

        return callchain

    def extract_behavior(self, symbol_name: str) -> List[str]:
        """提取汇编函数行为描述"""
        behaviors = []

        # 查找标签位置
        if symbol_name not in self.label_index:
            return behaviors

        start_line = self.label_index[symbol_name]

        # 首先添加标签本身的信息
        behaviors.append(f"assembly label: {symbol_name}")

        # 分析指令
        for i in range(start_line, len(self.lines)):
            line = self.lines[i].strip()

            # 跳过空行和注释
            if not line or line.startswith(';') or line.startswith('#'):
                continue

            # 跳过伪指令
            if line.startswith('.'):
                continue

            # 遇到下一个标签则停止
            if self.LABEL_PATTERN.match(line) and i > start_line:
                break

            match = self.INSTRUCTION_PATTERN.match(line)
            if match:
                opcode = match.group('opcode').lower()
                behavior = self._analyze_instruction(opcode)
                if behavior:
                    behaviors.append(behavior)
                    if len(behaviors) >= 10:  # 限制行为描述数量
                        break

        return behaviors

    def extract_implementation(self, symbol_name: str) -> List[str]:
        """提取汇编函数实现"""
        implementation = []

        # 查找标签位置
        if symbol_name not in self.label_index:
            return implementation

        start_line = self.label_index[symbol_name]

        # 提取指令直到下一个标签或文件结束
        for i in range(start_line, len(self.lines)):
            line = self.lines[i].strip()

            # 跳过空行和注释
            if not line or line.startswith(';') or line.startswith('#'):
                continue

            # 保留伪指令和段定义（以.开头的行）
            if line.startswith('.'):
                implementation.append(line)
                continue

            # 遇到下一个标签则停止
            if self.LABEL_PATTERN.match(line) and i > start_line:
                break

            # 保留所有指令
            match = self.INSTRUCTION_PATTERN.match(line)
            if match:
                implementation.append(line)
            else:
                # 保留其他非空行（可能是伪指令或其他汇编指令）
                implementation.append(line)

        return implementation

    def extract_asm_info(self, symbol_name: str) -> Dict:
        """提取完整的汇编信息"""
        labels = []
        flow = []
        instructions = []

        # 查找标签位置
        if symbol_name not in self.label_index:
            return {'labels': labels, 'flow': flow, 'instructions': instructions}

        start_line = self.label_index[symbol_name]
        labels.append(symbol_name)

        # 分析控制流和所有指令
        for i in range(start_line, len(self.lines)):
            line = self.lines[i].strip()

            # 跳过空行和注释
            if not line or line.startswith(';') or line.startswith('#'):
                continue

            # 保留伪指令和段定义
            if line.startswith('.'):
                instructions.append(line)
                continue

            # 遇到下一个标签则停止
            if self.LABEL_PATTERN.match(line) and i > start_line:
                break

            match = self.INSTRUCTION_PATTERN.match(line)
            if match:
                opcode = match.group('opcode').lower()
                operands = match.group('operands') or ''

                # 保留所有指令
                instruction = f"{opcode} {operands.strip()}".strip()
                instructions.append(instruction)

                # 记录控制流（包括 RISC-V 特定指令）
                if opcode in self.CONTROL_FLOW:
                    # 提取跳转目标
                    target = self._extract_branch_target(opcode, operands)
                    if target:
                        flow.append(f"{opcode} {target}")
                    else:
                        flow.append(instruction)
            else:
                # 保留其他非空行
                instructions.append(line)

        return {
            'labels': labels,
            'flow': flow,
            'instructions': instructions
        }

    def _extract_branch_target(self, opcode: str, operands: str) -> Optional[str]:
        """提取分支指令的目标标签"""
        if not operands:
            return None

        # RISC-V 分支指令格式: beq rs1, rs2, offset
        # RISC-V 跳转指令格式: jal rd, offset 或 jalr rd, rs1, offset
        if opcode in ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']:
            # 最后一个操作数是偏移量/标签
            parts = operands.split(',')
            if len(parts) >= 3:
                return parts[-1].strip()
        elif opcode in ['jal', 'jalr']:
            parts = operands.split(',')
            if len(parts) >= 2:
                return parts[-1].strip()

        return None
