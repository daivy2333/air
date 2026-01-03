import re

with open('c_module.c', 'r') as f:
    code = f.read()

# 移除注释
code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
code = re.sub(r'//.*', '', code)

# 检查第27个字符
print(f'Character at position 27: {repr(code[27])}')
print(f'Context: {repr(code[20:35])}')
