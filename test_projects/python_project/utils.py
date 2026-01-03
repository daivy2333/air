"""工具函数模块"""


def greet(name):
    """生成问候语"""
    return f"Hello, {name}!"


def format_result(expression, result):
    """格式化计算结果"""
    return f"{expression} = {result}"


def validate_number(value):
    """验证数字是否有效"""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
