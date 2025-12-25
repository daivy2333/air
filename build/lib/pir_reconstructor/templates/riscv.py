# RISC-V 专用汇编模板
def riscv_label_template(sym):
    """RISC-V 标签模板"""
    return f"""
# PIR_ID: {sym.name}:{sym.unit}
{sym.name}:
# AI_TODO: 实现 RISC-V 标签
"""

def riscv_func_template(sym):
    """RISC-V 函数模板"""
    return f"""
# PIR_ID: {sym.name}:{sym.unit}
.global {sym.name}
{sym.name}:
    # 保存返回地址和帧指针
    addi sp, sp, -16
    sd ra, 8(sp)
    sd fp, 0(sp)

    # TODO: 实现 RISC-V 函数体

    # 恢复返回地址和帧指针
    ld ra, 8(sp)
    ld fp, 0(sp)
    addi sp, sp, 16
    ret
"""

def riscv_csr_template(sym):
    """RISC-V CSR 操作模板"""
    return f"""
# PIR_ID: {sym.name}:{sym.unit}
.global {sym.name}
{sym.name}:
    # CSR 操作示例
    # csrr rd, csr     # 读取 CSR
    # csrw csr, rs1    # 写入 CSR
    # csrs csr, rs1    # 置位 CSR
    # csrc csr, rs1    # 清零 CSR
    ret
"""

def riscv_trap_template(sym):
    """RISC-V 中断/异常处理模板"""
    return f"""
# PIR_ID: {sym.name}:{sym.unit}
.global {sym.name}
{sym.name}:
    # 保存上下文
    addi sp, sp, -256
    sd x1, 0(sp)    # ra
    sd x5, 8(sp)    # t0
    # ... 保存其他寄存器

    # 读取 cause 寄存器
    csrr t0, mcause
    # TODO: 根据 cause 处理不同的异常

    # 恢复上下文
    ld x1, 0(sp)
    ld x5, 8(sp)
    # ... 恢复其他寄存器
    addi sp, sp, 256
    mret
"""

def riscv_memory_barrier_template(sym):
    """RISC-V 内存屏障指令模板"""
    return f"""
# PIR_ID: {sym.name}:{sym.unit}
.global {sym.name}
{sym.name}:
    # 内存屏障指令
    # fence rw, rw    # 读写屏障
    # fence.i         # 指令同步屏障
    ret
"""
