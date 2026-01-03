import re
from typing import Dict, List, Optional
from analyzers.base import BaseAnalyzer

class CppAnalyzer(BaseAnalyzer):
    """C/C++ 语言源码分析器 - 增强版"""

    # C/C++ 关键字（用于过滤伪函数）
    KEYWORDS = {
        "if", "else", "while", "for", "switch", "case", "default",
        "return", "sizeof", "do", "goto", "break", "continue",
        "new", "delete", "this", "true", "false", "nullptr",
        "static_cast", "dynamic_cast", "const_cast", "reinterpret_cast"
    }

    # 函数签名正则（支持 C++）
    FUNC_PATTERN = re.compile(
        r'(?:template\s*<[^>]*>\s*)?'  # 模板
        r'(?:\b(?:static|inline|extern|virtual|override|final|explicit|constexpr|const)\s+)*'
        r'(?P<return>(?:[\w:]+\s*(?:\*?\s*&?\s*)+))'  # 返回类型（支持指针、引用、命名空间）
        r'(?P<name>\w+)\s*'
        r'\((?P<args>[^)]*)\)'
        r'(?:\s*(?:const|volatile|noexcept|override|final|=\s*0|->\s*[^{;]+))?'  # 尾部限定符
    )

    # 类/结构体定义正则
    CLASS_PATTERN = re.compile(
        r'(?:template\s*<[^>]*>\s*)?'
        r'(?:class|struct|union)\s+'
        r'(?P<name>\w+)'
        r'(?:\s*:\s*(?:public|protected|private)\s+\w+)?'  # 继承
        r'\s*\{'
    )

    # 函数调用正则
    CALL_PATTERN = re.compile(r'\b(\w+)\s*\(')

    # 方法调用正则（obj.method()）
    METHOD_PATTERN = re.compile(r'(\w+)\.(\w+)\s*\(')

    def __init__(self, source_code: str, pir_data: Dict):
        super().__init__(source_code, pir_data)
        self._preprocess()

    def _preprocess(self):
        """预处理源码"""
        # 移除注释
        self.code = re.sub(r'/\*.*?\*/', '', self.source_code, flags=re.DOTALL)
        self.code = re.sub(r'//.*', '', self.code)

        # 按行分割
        self.lines = self.code.split('\n')

    def extract_signature(self, symbol_name: str) -> Optional[str]:
        """提取 C/C++ 函数签名"""
        for line in self.lines:
            match = self.FUNC_PATTERN.search(line)
            if match and match.group('name') == symbol_name:
                return_type = match.group('return').strip()
                args = match.group('args').strip()
                return f"{return_type} {symbol_name}({args})"
        return None

    def extract_implementation(self, symbol_name: str) -> List[str]:
        """提取 C/C++ 函数/类完整实现逻辑"""
        implementation = []
        
        # 检查是否是类/结构体定义
        class_match = re.search(
            r'(?:template\s*<[^>]*>\s*)?'
            r'(?:class|struct)\s+' + re.escape(symbol_name) + r'\s*\{',
            self.code
        )
        
        if class_match:
            # 提取类/结构体定义
            in_class = False
            brace_count = 0
            
            for line in self.lines:
                if not in_class:
                    if re.search(r'(?:class|struct)\s+' + re.escape(symbol_name) + r'\s*\{', line):
                        in_class = True
                        brace_count += line.count('{') - line.count('}')
                        implementation.append(line.strip())
                        continue
                
                if in_class:
                    brace_count += line.count('{') - line.count('}')
                    
                    # 提取类成员
                    stmt = self._extract_cpp_statement(line)
                    if stmt:
                        implementation.append(stmt)
                    
                    if brace_count <= 0:
                        break
        else:
            # 提取函数实现
            in_function = False
            brace_count = 0

            for line in self.lines:
                # 查找函数定义
                if not in_function:
                    match = self.FUNC_PATTERN.search(line)
                    if match and match.group('name') == symbol_name:
                        in_function = True
                        brace_count += line.count('{') - line.count('}')
                        continue

                # 在函数体内提取实现
                if in_function:
                    brace_count += line.count('{') - line.count('}')

                    # 提取关键语句
                    stmt = self._extract_cpp_statement(line)
                    if stmt:
                        implementation.append(stmt)

                    # 函数结束
                    if brace_count <= 0:
                        break

        return implementation

    def _extract_cpp_statement(self, line: str) -> Optional[str]:
        """提取 C/C++ 语句的完整内容"""
        line = line.strip()

        # 跳过空行和注释
        if not line or line.startswith('//') or line.startswith('/*'):
            return None

        # 跳过单行大括号
        if line in ['{', '}']:
            return None

        # 保留关键控制流语句
        if any(keyword in line for keyword in ['if', 'else if', 'for', 'while', 'switch', 'case', 'default', 'break', 'continue', 'return', 'goto', 'try', 'catch', 'throw']):
            return line

        # 保留赋值语句
        if '=' in line and '==' not in line and '!=' not in line and '<=' not in line and '>=' not in line:
            return line

        # 保留函数调用
        if '(' in line and ')' in line:
            return line

        # 保留变量声明（包括 C++ 特性）
        if re.match(r'^(int|char|float|double|void|unsigned|signed|bool|auto|const|std::|string|vector|map|set|list|array)\s+', line):
            return line

        # 保留 new/delete 表达式
        if 'new ' in line or 'delete ' in line:
            return line

        return None

    def extract_callchain(self, symbol_name: str) -> List[str]:
        """提取完整的调用链信息"""
        callchain = []
        in_function = False
        brace_count = 0

        for line in self.lines:
            # 查找函数定义
            if not in_function:
                match = self.FUNC_PATTERN.search(line)
                if match and match.group('name') == symbol_name:
                    in_function = True
                    brace_count += line.count('{') - line.count('}')
                    continue

            # 在函数体内查找调用
            if in_function:
                brace_count += line.count('{') - line.count('}')

                # 查找函数调用,保留完整的调用信息
                calls = self._extract_function_calls(line)
                callchain.extend(calls)

                # 函数结束
                if brace_count <= 0:
                    break

        return callchain

    def _extract_function_calls(self, line: str) -> List[str]:
        """提取一行中的所有函数调用"""
        calls = []
        # 匹配函数调用模式: identifier(args)
        call_pattern = re.compile(r'(\w+)\s*\(([^)]*)\)')

        for match in call_pattern.finditer(line):
            func_name = match.group(1)
            args = match.group(2).strip()
            if func_name not in self.KEYWORDS:
                calls.append(f"{func_name}({args})")

        # 匹配方法调用: obj.method(args)
        method_pattern = re.compile(r'(\w+)\.(\w+)\s*\(([^)]*)\)')
        for match in method_pattern.finditer(line):
            obj = match.group(1)
            method = match.group(2)
            args = match.group(3).strip()
            calls.append(f"{obj}.{method}({args})")

        return calls

    def extract_behavior(self, symbol_name: str) -> List[str]:
        """提取函数/类行为描述"""
        behaviors = []
        in_function = False
        brace_count = 0

        # 检查是否是类定义
        class_match = re.search(
            r'(?:template\s*<[^>]*>\s*)?'
            r'(?:class|struct)\s+' + re.escape(symbol_name) + r'\s*\{',
            self.code
        )

        if class_match:
            # 类行为
            kind = class_match.group(1) if '(' in class_match.group(0) else 'class'
            behaviors.append(f"{kind} {symbol_name} definition")
            return behaviors
        else:
            # 函数行为
            for line in self.lines:
                # 查找函数定义
                if not in_function:
                    match = self.FUNC_PATTERN.search(line)
                    if match and match.group('name') == symbol_name:
                        in_function = True
                        brace_count += line.count('{') - line.count('}')
                        continue

                # 在函数体内提取行为
                if in_function:
                    brace_count += line.count('{') - line.count('}')

                    # 提取关键行为
                    behavior = self._extract_cpp_behavior(line)
                    if behavior:
                        behaviors.append(behavior)

                    # 函数结束
                    if brace_count <= 0:
                        break

        return behaviors

    def _extract_cpp_behavior(self, line: str) -> Optional[str]:
        """提取C++语句的行为描述"""
        line = line.strip()

        # 跳过空行和注释
        if not line or line.startswith('//') or line.startswith('/*'):
            return None

        # 跳过单行大括号
        if line in ['{', '}']:
            return None

        # 控制流
        if any(keyword in line for keyword in ['if', 'else if', 'for', 'while', 'switch', 'case', 'default', 'break', 'continue', 'goto', 'try', 'catch', 'throw']):
            return f"Control flow: {line}"

        # 返回语句
        if 'return' in line:
            return f"Returns: {line}"

        # 赋值
        if '=' in line and '==' not in line and '!=' not in line and '<=' not in line and '>=' not in line:
            return f"Assignment: {line}"

        # 函数调用
        if '(' in line and ')' in line:
            return f"Call: {line}"

        # new/delete 表达式
        if 'new ' in line or 'delete ' in line:
            return f"Memory management: {line}"

        return None

    def extract_asm_info(self, symbol_name: str) -> Dict:
        """提取汇编信息（C/C++ 源码不适用）"""
        return {
            'labels': [],
            'flow': []
        }
