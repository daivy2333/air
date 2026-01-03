import re

with open('c_module.c', 'r') as f:
    code = f.read()

# 移除注释
code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
code = re.sub(r'//.*', '', code)

print('Processed code:')
print(code)
print('\nChecking for unbalanced parentheses...')

# 检查括号平衡
count = 0
for i, char in enumerate(code):
    if char == '(':
        count += 1
    elif char == ')':
        count -= 1
    if count < 0:
        print(f'Unbalanced at position {i}: {char}')
        print(f'Context: {code[max(0, i-20):i+20]}')
        break
print(f'Final count: {count}')
