def python_func_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    attrs_str = f"\n    属性: {attrs}" if attrs else ""
    return f"""

def {sym.name}():  # PIR_ID: {sym.name}:{sym.unit}{attrs_str}
    # AI_TODO: 实现
    pass
"""

def python_class_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    attrs_str = f"\n    属性: {attrs}" if attrs else ""
    return f"""

class {sym.name}:  # PIR_ID: {sym.name}:{sym.unit}{attrs_str}
    # AI_TODO: 实现
    pass
"""
