import ast
from typing import Optional

def extract_class(source_code: str, class_name: str) -> Optional[str]:
    """提取Python类定义（包含方法）"""
    try:
        tree = ast.parse(source_code)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                # 获取类源代码范围
                lines = source_code.split('\n')
                start_line = node.lineno - 1

                # 找到类结束行
                end_line = start_line
                indent_level = len(lines[start_line]) - len(lines[start_line].lstrip())

                for i in range(start_line + 1, len(lines)):
                    if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= indent_level:
                        end_line = i
                        break
                else:
                    end_line = len(lines)

                # 提取类代码
                class_code = '\n'.join(lines[start_line:end_line])
                return class_code

    except SyntaxError:
        pass

    # 回退到正则匹配
    import re
    pattern = rf'class\s+{class_name}\s*\(?[^:]*\)?:[^"]*"""[^"]*"""|\'\'\'[^\']*\'\'\'[^{{}}]*'
    match = re.search(pattern, source_code, re.DOTALL)
    if match:
        return match.group(0)

    return None
