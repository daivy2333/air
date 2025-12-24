"""Common template utilities."""

def format_attributes(attributes):
    """Format attributes dictionary into a sorted string."""
    return ", ".join(f"{k}={v}" for k, v in sorted(attributes.items()))

def generate_pir_comment(sym):
    """Generate standard PIR identification comment."""
    return f"// PIR_ID: {sym.name}:{sym.unit}"

def generate_todo_comment():
    """Generate standard TODO comment."""
    return "// AI_TODO: 实现"
