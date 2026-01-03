import re
from typing import Dict, List, Optional
from analyzers.base import BaseAnalyzer

class CAnalyzer(BaseAnalyzer):
    """C 语言源码分析器"""

    # 函数签名正则
    FUNC_PATTERN = re.compile(
        r'(?:(?:static|inline|extern)\s+)*'
        r'(?P<return>\w+\s*\*?)\s+'
        r'(?P<name>\w+)\s*'
        r'\((?P<args>[^)]*)\)'
    )

    # 函数调用正则
    CALL_PATTERN = re.compile(r'(\w+)\s*\(')

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
        """提取 C 函数签名"""
        for line in self.lines:
            match = self.FUNC_PATTERN.search(line)
            if match and match.group('name') == symbol_name:
                return_type = match.group('return').strip()
                args = match.group('args').strip()
                return f"{return_type} {symbol_name}({args})"
        return None

    def extract_implementation(self, symbol_name: str) -> List[str]:
        """提取 C 函数/结构体完整实现逻辑"""
        implementation = []

        # 检查是否是结构体定义
        struct_match = re.search(
            r'struct\s+' + re.escape(symbol_name) + r'\s*\{',
            self.code
        )

        if struct_match:
            # 提取结构体定义
            in_struct = False
            brace_count = 0

            for line in self.lines:
                if not in_struct:
                    if re.search(r'struct\s+' + re.escape(symbol_name) + r'\s*\{', line):
                        in_struct = True
                        brace_count += line.count('{') - line.count('}')
                        implementation.append(line.strip())
                        continue

                if in_struct:
                    brace_count += line.count('{') - line.count('}')

                    # 提取结构体成员
                    stmt = self._extract_c_statement(line)
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
                    stmt = self._extract_c_statement(line)
                    if stmt:
                        implementation.append(stmt)

                    # 函数结束
                    if brace_count <= 0:
                        break

        return implementation

    def _extract_c_statement(self, line: str) -> Optional[str]:
        """提取 C 语句的完整内容"""
        line = line.strip()

        # 跳过空行和注释
        if not line or line.startswith('//') or line.startswith('/*'):
            return None

        # 跳过单行大括号
        if line in ['{', '}']:
            return None

        # 保留关键控制流语句
        if any(keyword in line for keyword in ['if', 'else if', 'for', 'while', 'switch', 'case', 'default', 'break', 'continue', 'return', 'goto']):
            return line

        # 保留赋值语句
        if '=' in line and '==' not in line and '!=' not in line and '<=' not in line and '>=' not in line:
            return line

        # 保留函数调用
        if '(' in line and ')' in line:
            return line

        # 保留变量声明
        if re.match(r'^(int|char|float|double|void|unsigned|signed|struct|enum|typedef)\s+', line):
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
            calls.append(f"{func_name}({args})")

        return calls

    def extract_behavior(self, symbol_name: str) -> List[str]:
        """提取函数行为描述"""
        behaviors = []
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

            # 在函数体内提取行为
            if in_function:
                brace_count += line.count('{') - line.count('}')

                # 提取关键行为
                behavior = self._extract_c_behavior(line)
                if behavior:
                    behaviors.append(behavior)

                # 函数结束
                if brace_count <= 0:
                    break

        return behaviors

    def _extract_c_behavior(self, line: str) -> Optional[str]:
        """提取C语句的行为描述"""
        line = line.strip()

        # 跳过空行和注释
        if not line or line.startswith('//') or line.startswith('/*'):
            return None

        # 跳过单行大括号
        if line in ['{', '}']:
            return None

        # 控制流
        if any(keyword in line for keyword in ['if', 'else if', 'for', 'while', 'switch', 'case', 'default', 'break', 'continue', 'return', 'goto']):
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

        return None

    def extract_header_symbols(self) -> List[Dict]:
        """
        提取头文件中的符号（宏定义、typedef、函数声明等）

        Returns:
            符号列表，每个符号包含name和kind
        """
        symbols = []

        # 宏定义正则
        macro_pattern = re.compile(r'#define\s+(\w+)\s*(?:\([^)]*\))?')

        # typedef正则
        typedef_pattern = re.compile(r'typedef\s+(?:struct\s+)?(\w+)\s+(\w+)')

        # 函数声明正则（不包含实现）
        func_decl_pattern = re.compile(
            r'(?:static|inline|extern)?\s*\w+\s*\*?\s*(\w+)\s*\([^)]*\)\s*;'
        )

        # 枚举定义正则
        enum_pattern = re.compile(r'enum\s+(\w+)\s*\{')

        # 全局变量声明正则
        var_decl_pattern = re.compile(r'extern\s+\w+\s+(\w+)\s*(?:\[.*?\])?\s*;')

        for line in self.lines:
            stripped = line.strip()

            # 跳过注释和空行
            if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
                continue

            # 提取宏定义
            macro_match = macro_pattern.search(line)
            if macro_match:
                symbols.append({
                    'name': macro_match.group(1),
                    'kind': 'macro'
                })
                continue

            # 提取typedef
            typedef_match = typedef_pattern.search(line)
            if typedef_match:
                symbols.append({
                    'name': typedef_match.group(2),
                    'kind': 'typedef'
                })
                continue

            # 提取枚举定义
            enum_match = enum_pattern.search(line)
            if enum_match:
                symbols.append({
                    'name': enum_match.group(1),
                    'kind': 'enum'
                })
                continue

            # 提取函数声明（不包含实现）
            func_decl_match = func_decl_pattern.search(line)
            if func_decl_match and '{' not in line:
                symbols.append({
                    'name': func_decl_match.group(1),
                    'kind': 'func'
                })
                continue

            # 提取全局变量声明
            var_decl_match = var_decl_pattern.search(line)
            if var_decl_match:
                symbols.append({
                    'name': var_decl_match.group(1),
                    'kind': 'var'
                })
                continue

        return symbols

    def extract_asm_info(self, symbol_name: str) -> Dict:
        """提取汇编信息（C 源码不适用）"""
        return {
            'labels': [],
            'flow': []
        }


    def extract_struct(self, source_code: str, struct_name: str) -> Optional[str]:
        """提取C结构体定义"""
        # 匹配 struct name { ... };
        patterns = [
            rf'struct\s+{struct_name}\s*{{([^}}]+)}};',
            rf'typedef\s+struct\s+(\w+\s+)?{struct_name}\s*{{([^}}]+)}}',
        ]

        for pattern in patterns:
            match = re.search(pattern, source_code, re.DOTALL)
            if match:
                # 提取字段
                fields_text = match.group(1) if len(match.groups()) == 1 else match.group(2)
                fields = self._extract_fields(fields_text)

                # 构建完整定义
                struct_def = f"struct {struct_name} {{\n"
                for field in fields[:10]:  # 最多10个字段，避免太长
                    struct_def += f"    {field}\n"
                struct_def += "};"
                return struct_def

        return None

    def _extract_fields(self, fields_text: str) -> List[str]:
        """提取字段列表"""
        fields = []
        for line in fields_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                if ';' in line:
                    fields.append(line.strip(';'))
                elif line:  # 多行定义
                    fields.append(line)
        return fields
