def python_func_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    return f"""
def {sym.name}():  # PIR_ID: {sym.name}:{sym.unit}
    """
    属性: {attrs}
    """
    # AI_TODO: 实现
    pass
"""

def python_class_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    return f"""
class {sym.name}:  # PIR_ID: {sym.name}:{sym.unit}
    """
    属性: {attrs}
    """
    # AI_TODO: 实现
    pass
"""
