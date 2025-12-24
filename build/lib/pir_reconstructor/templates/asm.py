def asm_label_template(sym):
    return f"""
# PIR_ID: {sym.name}:{sym.unit}
{sym.name}:
# AI_TODO: 实现汇编代码
"""

def asm_func_template(sym):
    return f"""
# PIR_ID: {sym.name}:{sym.unit}
.global {sym.name}
{sym.name}:
# AI_TODO: 实现函数
    ret
"""
