def asm_label_template(sym):
    """通用汇编标签模板"""
    return f"""
# PIR_ID: {sym.name}:{sym.unit}
{sym.name}:
# AI_TODO: 实现汇编代码
"""

def asm_func_template(sym):
    """通用汇编函数模板"""
    return f"""
# PIR_ID: {sym.name}:{sym.unit}
.global {sym.name}
{sym.name}:
# AI_TODO: 实现函数
    ret
"""

# RISC-V 特定模板导入
try:
    from . import riscv
    riscv_label_template = riscv.riscv_label_template
    riscv_func_template = riscv.riscv_func_template
    riscv_csr_template = riscv.riscv_csr_template
    riscv_trap_template = riscv.riscv_trap_template
    riscv_memory_barrier_template = riscv.riscv_memory_barrier_template
except ImportError:
    pass
