
import re

# 读取文件
with open('main.cpp', 'r', encoding='utf-8') as f:
    code = f.read()

# 移除注释
code_no_comments = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
code_no_comments = re.sub(r'//.*', '', code_no_comments)

print('Original code length:', len(code))
print('Code without comments length:', len(code_no_comments))

# 检查括号平衡
count = 0
for i, char in enumerate(code_no_comments):
    if char == '(':
        count += 1
    elif char == ')':
        count -= 1
    if count < 0:
        print(f'Unbalanced at position {i}: {repr(char)}')
        print(f'Context: {repr(code_no_comments[max(0, i-20):i+20])}')
        break
print(f'Final count: {count}')

# 检查中文字符周围是否有括号
chinese_chars = []
for i, char in enumerate(code):
    if ord(char) > 127:  # 非ASCII字符
        chinese_chars.append((i, repr(char)))

if chinese_chars:
    print('\nChinese characters found:')
    for pos, char in chinese_chars[:10]:  # 只显示前10个
        context_start = max(0, pos-10)
        context_end = min(len(code), pos+10)
        print(f'Position {pos}: {char}')
        print(f'Context: {repr(code[context_start:context_end])}')
