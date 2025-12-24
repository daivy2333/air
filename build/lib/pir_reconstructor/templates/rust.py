def rust_func_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    return f"""
// PIR_ID: {sym.name}:{sym.unit}
// 属性: {attrs}
fn {sym.name}() {{
    // AI_TODO: 实现
}}
"""

def rust_struct_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    return f"""
// PIR_ID: {sym.name}:{sym.unit}
// 属性: {attrs}
struct {sym.name} {{
    // AI_TODO: 实现字段
}}
"""

def rust_enum_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    return f"""
// PIR_ID: {sym.name}:{sym.unit}
// 属性: {attrs}
enum {sym.name} {{
    // AI_TODO: 实现变体
}}
"""

def rust_trait_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    return f"""
// PIR_ID: {sym.name}:{sym.unit}
// 属性: {attrs}
trait {sym.name} {{
    // AI_TODO: 实现方法
}}
"""
