# core/profile_riscv.py
"""
RISC-V OS 专用的 Profile 配置

包含：
- RISC-V 特定的内存布局信息
- 常见段定义（.text, .data, .bss, .rodata 等）
- RISC-V 特有的符号约定（如 _start, trap_vector 等）
- 系统调用接口规范
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass


@dataclass
class RISCVMemoryLayout:
    """RISC-V 内存布局配置"""
    # 内存区域定义
    regions: Dict[str, Dict[str, str]]

    # 段定义
    sections: List[Dict[str, any]]

    # 特殊符号定义
    symbols: Dict[str, str]


# RISC-V 标准内存布局
RISCV_STANDARD_LAYOUT = RISCVMemoryLayout(
    regions={
        'ram': {
            'origin': '0x80000000',
            'length': '128M',
            'attributes': 'wxa!ri'
        },
        'rom': {
            'origin': '0x20000000',
            'length': '16M',
            'attributes': 'rx!w'
        }
    },
    sections=[
        {
            'name': '.text',
            'region': 'ram',
            'align': 4,
            'flags': 'ax'
        },
        {
            'name': '.rodata',
            'region': 'ram',
            'align': 4,
            'flags': 'a'
        },
        {
            'name': '.data',
            'region': 'ram',
            'align': 4,
            'flags': 'wa'
        },
        {
            'name': '.bss',
            'region': 'ram',
            'align': 4,
            'flags': 'wa'
        },
        {
            'name': '.stack',
            'region': 'ram',
            'align': 16,
            'flags': 'wa'
        },
        {
            'name': '.heap',
            'region': 'ram',
            'align': 16,
            'flags': 'wa'
        }
    ],
    symbols={
        '_start': '0x80000000',
        '_stack_start': '0x80000000',
        '_stack_end': '0x80001000',
        '_heap_start': '0x80001000',
        '_heap_end': '0x88000000',
        'trap_vector': '0x80000100',
    }
)


# RISC-V 特殊符号集合
RISCV_SPECIAL_SYMBOLS = {
    # 入口点
    '_start',
    # 中断/异常处理
    'trap_vector',
    'trap_entry',
    'irq_handler',
    'exception_handler',
    # 系统调用
    'syscall_table',
    'syscall_handler',
    # 内存管理
    '_stack_start',
    '_stack_end',
    '_heap_start',
    '_heap_end',
}


# RISC-V CSR 寄存器定义
RISCV_CSR_REGISTERS = {
    # Machine Information Registers
    'mvendorid': 0xF11,
    'marchid': 0xF12,
    'mimpid': 0xF13,
    'mhartid': 0xF14,

    # Machine Trap Setup
    'mstatus': 0x300,
    'misa': 0x301,
    'medeleg': 0x302,
    'mideleg': 0x303,
    'mie': 0x304,
    'mtvec': 0x305,
    'mcounteren': 0x306,

    # Machine Trap Handling
    'mscratch': 0x340,
    'mepc': 0x341,
    'mcause': 0x342,
    'mtval': 0x343,
    'mip': 0x344,

    # Machine Timer/Cycle
    'mcycle': 0xB00,
    'minstret': 0xB02,

    # Supervisor Trap Setup
    'sstatus': 0x100,
    'sedeleg': 0x102,
    'sideleg': 0x103,
    'sie': 0x104,
    'stvec': 0x105,
    'scounteren': 0x106,

    # Supervisor Trap Handling
    'sscratch': 0x140,
    'sepc': 0x141,
    'scause': 0x142,
    'stval': 0x143,
    'sip': 0x144,

    # Supervisor Address Translation
    'satp': 0x180,
}


# RISC-V 中断/异常原因码
RISCV_EXCEPTION_CODES = {
    # Instruction address misaligned
    'misaligned_fetch': 0x0,
    # Instruction access fault
    'fetch_access': 0x1,
    # Illegal instruction
    'illegal_instruction': 0x2,
    # Breakpoint
    'breakpoint': 0x3,
    # Load address misaligned
    'misaligned_load': 0x4,
    # Load access fault
    'load_access': 0x5,
    # Store/AMO address misaligned
    'misaligned_store': 0x6,
    # Store/AMO access fault
    'store_access': 0x7,
    # Environment call from U-mode
    'ecall_u': 0x8,
    # Environment call from S-mode
    'ecall_s': 0x9,
    # Environment call from M-mode
    'ecall_m': 0xB,
    # Instruction page fault
    'fetch_page_fault': 0xC,
    # Load page fault
    'load_page_fault': 0xD,
    # Store/AMO page fault
    'store_page_fault': 0xF,
}


# RISC-V 指令集扩展
RISCV_EXTENSIONS = {
    'I': 'Integer',
    'M': 'Multiply/Divide',
    'A': 'Atomic',
    'F': 'Single-Precision Float',
    'D': 'Double-Precision Float',
    'C': 'Compressed',
    'G': 'General (IMAFD)',
}


def get_riscv_extension_name(code: str) -> Optional[str]:
    """获取 RISC-V 扩展的名称"""
    return RISCV_EXTENSIONS.get(code.upper())


def is_riscv_special_symbol(name: str) -> bool:
    """检查是否为 RISC-V 特殊符号"""
    return name in RISCV_SPECIAL_SYMBOLS


def get_csr_address(name: str) -> Optional[int]:
    """获取 CSR 寄存器地址"""
    return RISCV_CSR_REGISTERS.get(name.lower())


def get_exception_code(name: str) -> Optional[int]:
    """获取异常原因码"""
    return RISCV_EXCEPTION_CODES.get(name.lower())
