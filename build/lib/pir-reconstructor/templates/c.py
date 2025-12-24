def c_func_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    return f"""
/* PIR_ID: {sym.name}:{sym.unit} */
/* 属性: {attrs} */
void {sym.name}(void) {{
    /* AI_TODO: 实现 */
}}
"""

def c_struct_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    return f"""
/* PIR_ID: {sym.name}:{sym.unit} */
/* 属性: {attrs} */
struct {sym.name} {{
    /* AI_TODO: 实现 */
}};
"""
