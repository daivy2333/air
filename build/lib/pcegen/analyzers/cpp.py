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
        r'(?:(?:static|inline|extern|virtual|override|final|explicit|constexpr|const)\s+)*'
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

    # 访问修饰符正则
    ACCESS_PATTERN = re.compile(r'(public|protected|private)\s*:')

    # 函数调用正则
    CALL_PATTERN = re.compile(r'(\w+)\s*\(')

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
            implementation.append(f"class {symbol_name} {{")

            # 提取字段
            fields = self.extract_class_fields(symbol_name)
            if fields:
                implementation.append("  /* Fields */")
                for field in fields:
                    access = f"{field['access']} " if field['access'] != 'private' else ""
                    static = "static " if field['static'] else ""
                    const = "const " if field['const'] else ""
                    type_str = field['type']
                    name_str = field['name']
                    array_str = field['array'] if field['array'] else ""
                    init_str = f" = {field['init']}" if field['init'] else ""
                    implementation.append(f"  {access}{static}{const}{type_str} {name_str}{array_str}{init_str};")

            # 提取方法
            methods = self.extract_class_methods(symbol_name)
            if methods:
                implementation.append("\n  /* Methods */")
                for method in methods:
                    access = f"{method['access']} " if method['access'] != 'private' else ""
                    static = "static " if method['static'] else ""
                    virtual = "virtual " if method['virtual'] else ""
                    const = "const " if method['const'] else ""
                    override = "override " if method['override'] else ""
                    return_type = method['return'] if method['return'] else "void"
                    args = method['args']
                    implementation.append(f"  {access}{static}{virtual}{return_type} {method['name']}({args}){const}{override};")

            implementation.append('}')
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

        # 匹配方法调用: obj.method(args) 或 ptr->method(args)
        method_pattern = re.compile(r'(\w+)\s*(\.|->)\s*(\w+)\s*\(([^)]*)\)')
        for match in method_pattern.finditer(line):
            obj = match.group(1)
            op = match.group(2)
            method = match.group(3)
            args = match.group(4).strip()
            if method not in self.KEYWORDS:
                calls.append(f"{obj}{op}{method}({args})")

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

            # 提取字段
            fields = self.extract_class_fields(symbol_name)
            if fields:
                behaviors.append(f"  Fields ({len(fields)}):")
                for field in fields:
                    access = f"[{field['access']}] " if field['access'] != 'private' else ""
                    static = "[static] " if field['static'] else ""
                    const = "[const] " if field['const'] else ""
                    type_str = field['type']
                    name_str = field['name']
                    array_str = f"[{field['array']}]" if field['array'] else ""
                    init_str = f" = {field['init']}" if field['init'] else ""
                    behaviors.append(f"    - {access}{static}{const}{type_str} {name_str}{array_str}{init_str}")

            # 提取方法
            methods = self.extract_class_methods(symbol_name)
            if methods:
                behaviors.append(f"  Methods ({len(methods)}):")
                for method in methods:
                    access = f"[{method['access']}] " if method['access'] != 'private' else ""
                    static = "[static] " if method['static'] else ""
                    virtual = "[virtual] " if method['virtual'] else ""
                    const = "[const] " if method['const'] else ""
                    override = "[override] " if method['override'] else ""
                    return_type = method['return'] if method['return'] else "void"
                    args = method['args']
                    behaviors.append(f"    - {access}{static}{virtual}{return_type} {method['name']}({args}){const}{override}")
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

    def extract_class_fields(self, class_name: str) -> List[Dict]:
        """提取类字段"""
        fields = []
        in_class = False
        brace_count = 0
        current_access = 'private'

        for line in self.lines:
            # 查找类定义
            if not in_class:
                match = self.CLASS_PATTERN.search(line)
                if match and match.group('name') == class_name:
                    in_class = True
                    brace_count += line.count('{') - line.count('}')
                    continue

            # 在类体内提取字段
            if in_class:
                brace_count += line.count('{') - line.count('}')

                # 检查访问修饰符
                access_match = self.ACCESS_PATTERN.search(line)
                if access_match:
                    current_access = access_match.group(1)
                    continue

                # 提取字段定义
                line = line.strip()
                if line and not line.startswith('}') and not line.startswith('//') and not line.startswith('/*'):
                    # 匹配字段定义: [static] [const] type name[array] = init;
                    field_match = re.match(
                        r'(?P<static>static\s+)?'
                        r'(?P<const>const\s+)?'
                        r'(?P<type>(?:\w+\s*(?:\*?\s*&?\s*)+)'
                        r'(?P<name>\w+)'
                        r'(?P<array>\[[^\]]+\])?'
                        r'(?:\s*=\s*(?P<init>[^;]+))?',
                        line
                    )
                    if field_match and not re.search(r'fn|class|struct', line):
                        field = {
                            'access': current_access,
                            'static': bool(field_match.group('static')),
                            'const': bool(field_match.group('const')),
                            'type': field_match.group('type').strip(),
                            'name': field_match.group('name'),
                            'array': field_match.group('array') if field_match.group('array') else None,
                            'init': field_match.group('init').strip() if field_match.group('init') else None
                        }
                        fields.append(field)

                if brace_count <= 0:
                    break

        return fields

    def extract_class_methods(self, class_name: str) -> List[Dict]:
        """提取类方法"""
        methods = []
        in_class = False
        brace_count = 0
        current_access = 'private'

        for line in self.lines:
            # 查找类定义
            if not in_class:
                match = self.CLASS_PATTERN.search(line)
                if match and match.group('name') == class_name:
                    in_class = True
                    brace_count += line.count('{') - line.count('}')
                    continue

            # 在类体内提取方法
            if in_class:
                brace_count += line.count('{') - line.count('}')

                # 检查访问修饰符
                access_match = self.ACCESS_PATTERN.search(line)
                if access_match:
                    current_access = access_match.group(1)
                    continue

                # 提取方法定义
                func_match = self.FUNC_PATTERN.search(line)
                if func_match:
                    method = {
                        'access': current_access,
                        'static': 'static' in line,
                        'virtual': 'virtual' in line,
                        'const': 'const' in line and not line.endswith('const;'),
                        'override': 'override' in line,
                        'name': func_match.group('name'),
                        'return': func_match.group('return').strip() if func_match.group('return') else None,
                        'args': func_match.group('args').strip()
                    }
                    methods.append(method)

                if brace_count <= 0:
                    break

        return methods
