import re
from typing import Dict, List, Optional
from analyzers.base import BaseAnalyzer

class RustAnalyzer(BaseAnalyzer):
    """Rust 语言源码分析器 - 增强版"""

    # 函数签名正则
    FUNC_PATTERN = re.compile(
        r'(?:pub\s+)?'
        r'(?:unsafe\s+)?'
        r'(?:extern\s+"[^"]*"\s+)?'
        r'fn\s+'
        r'(?P<name>\w+)'
        r'\s*'
        r'\((?P<args>[^)]*)\)'
        r'(?:\s*->\s*(?P<return>[^\{]+))?'
    )

    # 函数调用正则
    CALL_PATTERN = re.compile(r'\b(\w+)\s*\(')

    # Rust 关键字（用于过滤伪函数）
    KEYWORDS = {
        'if', 'else', 'match', 'Some', 'None', 'Ok', 'Err',
        'Vec', 'String', 'Box', 'Option', 'Result', 'println', 'print'
    }

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
        """提取 Rust 函数签名"""
        for line in self.lines:
            match = self.FUNC_PATTERN.search(line)
            if match and match.group('name') == symbol_name:
                args = match.group('args').strip()
                return_type = match.group('return')

                if return_type:
                    return_type = return_type.strip()
                    return f"fn {symbol_name}({args}) -> {return_type}"
                else:
                    return f"fn {symbol_name}({args})"
        return None

    def extract_implementation(self, symbol_name: str) -> List[str]:
        """提取 Rust 函数/结构体/枚举完整实现逻辑"""
        implementation = []
        in_block = False
        brace_count = 0

        # 检查是否是结构体/枚举
        struct_match = re.search(
            r'(?:pub\s+)?(struct|enum|union)\s+' + re.escape(symbol_name) + r'\s*\{',
            self.code
        )

        if struct_match:
            # 提取结构体/枚举定义
            kind = struct_match.group(1)
            implementation.append(f"{kind} {symbol_name} {{")

            for line in self.lines:
                if not in_block:
                    if re.search(r'(?:pub\s+)?' + re.escape(kind) + r'\s+' + re.escape(symbol_name), line):
                        in_block = True
                        brace_count += line.count('{') - line.count('}')
                        continue

                if in_block:
                    brace_count += line.count('{') - line.count('}')
                    
                    # 提取字段定义
                    line = line.strip()
                    if line and not line.startswith('}'):
                        # 保留字段定义: pub name: type, 或 name: type,
                        if re.match(r'(?:pub\s+)?\w+\s*:\s*[^,\{]+', line):
                            implementation.append(line)
                        # 保留方法定义
                        elif re.match(r'(?:pub\s+)?fn\s+', line):
                            implementation.append(line)
                        # 保留 impl 块
                        elif re.match(r'impl\s+', line):
                            implementation.append(line)

                    if brace_count <= 0:
                        implementation.append('}')
                        break
        else:
            # 提取函数实现
            in_function = False
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
                    stmt = self._extract_rust_statement(line)
                    if stmt:
                        implementation.append(stmt)

                    # 函数结束
                    if brace_count <= 0:
                        break

        return implementation

    def _extract_rust_statement(self, line: str) -> Optional[str]:
        """提取 Rust 语句的完整内容"""
        line = line.strip()

        # 跳过空行和注释
        if not line or line.startswith('//') or line.startswith('/*'):
            return None

        # 跳过单行大括号
        if line in ['{', '}']:
            return None

        # 保留关键控制流语句
        if any(keyword in line for keyword in ['if', 'else if', 'else', 'match', 'loop', 'for', 'while', 'break', 'continue', 'return']):
            return line

        # 保留赋值语句
        if '=' in line and '==' not in line and '!=' not in line and '<=' not in line and '>=' not in line:
            return line

        # 保留函数调用
        if '(' in line and ')' in line:
            return line

        # 保留变量声明
        if 'let ' in line:
            return line

        # 保留 unsafe 块
        if 'unsafe' in line:
            return line

        # 保留宏调用
        if '!' in line:
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
        # 匹配函数调用模式: identifier(args) 或 method_call(args)
        call_pattern = re.compile(r'(\w+)\s*\(([^)]*)\)')

        for match in call_pattern.finditer(line):
            func_name = match.group(1)
            # 过滤掉 Rust 关键字和类型
            if func_name not in self.KEYWORDS:
                args = match.group(2).strip()
                calls.append(f"{func_name}({args})")

        # 匹配方法调用: obj.method(args)
        method_pattern = re.compile(r'(\w+)\.(\w+)\s*\(([^)]*)\)')
        for match in method_pattern.finditer(line):
            obj = match.group(1)
            method = match.group(2)
            # 过滤掉 Rust 关键字和类型
            if method not in self.KEYWORDS:
                args = match.group(3).strip()
                calls.append(f"{obj}.{method}({args})")

        return calls

    def extract_behavior(self, symbol_name: str) -> List[str]:
        """提取函数/结构体行为描述"""
        behaviors = []
        in_block = False
        brace_count = 0

        # 检查是否是结构体/枚举
        struct_match = re.search(
            r'(?:pub\s+)?(struct|enum|union)\s+' + re.escape(symbol_name) + r'\s*\{',
            self.code
        )

        if struct_match:
            # 结构体/枚举行为
            kind = struct_match.group(1)
            behaviors.append(f"{kind} {symbol_name} definition")
            return behaviors
        else:
            # 函数行为
            in_function = False
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
                    behavior = self._extract_rust_behavior(line)
                    if behavior:
                        behaviors.append(behavior)

                    # 函数结束
                    if brace_count <= 0:
                        break

        return behaviors

    def _extract_rust_behavior(self, line: str) -> Optional[str]:
        """提取Rust语句的行为描述"""
        line = line.strip()

        # 跳过空行和注释
        if not line or line.startswith('//') or line.startswith('/*'):
            return None

        # 跳过单行大括号
        if line in ['{', '}']:
            return None

        # 控制流
        if any(keyword in line for keyword in ['if', 'else if', 'else', 'match', 'loop', 'for', 'while', 'break', 'continue']):
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

        # unsafe 块
        if 'unsafe' in line:
            return f"Unsafe block: {line}"

        return None

    def extract_asm_info(self, symbol_name: str) -> Dict:
        """提取汇编信息（Rust 源码不适用）"""
        return {
            'labels': [],
            'flow': []
        }

    def extract_struct_fields(self, struct_name: str) -> List[Dict]:
        """提取结构体字段"""
        fields = []
        in_struct = False
        brace_count = 0

        for line in self.lines:
            # 查找结构体定义
            if not in_struct:
                match = self.STRUCT_PATTERN.search(line)
                if match and match.group('name') == struct_name:
                    in_struct = True
                    brace_count += line.count('{') - line.count('}')
                    continue

            # 在结构体内提取字段
            if in_struct:
                brace_count += line.count('{') - line.count('}')

                # 提取字段定义: pub name: type, 或 name: type,
                line = line.strip()
                if line and not line.startswith('}'):
                    # 匹配字段定义
                    field_match = re.match(
                        r'(?:pub\s+)?(?P<name>\w+)\s*:\s*(?P<type>[^,=]+)(?:\s*=\s*(?P<default>[^,]+))?',
                        line
                    )
                    if field_match:
                        field = {
                            'name': field_match.group('name'),
                            'type': field_match.group('type').strip(),
                            'visibility': 'public' if 'pub' in line else 'private',
                            'default': field_match.group('default').strip() if field_match.group('default') else None
                        }
                        fields.append(field)

                if brace_count <= 0:
                    break

        return fields

    def extract_impl_methods(self, type_name: str) -> List[Dict]:
        """提取impl块中的方法"""
        methods = []
        in_impl = False
        brace_count = 0
        impl_trait = None

        for line in self.lines:
            # 查找impl块
            if not in_impl:
                match = self.IMPL_PATTERN.search(line)
                if match and match.group('type') == type_name:
                    in_impl = True
                    impl_trait = match.group('trait')
                    brace_count += line.count('{') - line.count('}')
                    continue

            # 在impl块内提取方法
            if in_impl:
                brace_count += line.count('{') - line.count('}')

                # 提取方法定义
                func_match = self.FUNC_PATTERN.search(line)
                if func_match:
                    method = {
                        'name': func_match.group('name'),
                        'args': func_match.group('args').strip(),
                        'return_type': func_match.group('return').strip() if func_match.group('return') else None,
                        'visibility': 'public' if 'pub' in line else 'private',
                        'unsafe': 'unsafe' in line,
                        'async': 'async' in line,
                        'trait': impl_trait
                    }
                    methods.append(method)

                if brace_count <= 0:
                    break

        return methods
