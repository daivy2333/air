def java_method_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    return f"""
    // PIR_ID: {sym.name}:{sym.unit}
    // 属性: {attrs}
    public void {sym.name}() {{
        // AI_TODO: 实现
    }}
"""

def java_class_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    return f"""
// PIR_ID: {sym.name}:{sym.unit}
// 属性: {attrs}
public class {sym.name} {{
    // AI_TODO: 实现
}}
"""
