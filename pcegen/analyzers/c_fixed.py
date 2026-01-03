import re
from typing import Dict, List, Optional, Tuple
from analyzers.base import BaseAnalyzer

class CAnalyzer(BaseAnalyzer):
    """C 语言源码分析器 - 增强版"""

    # 函数签名正则
    FUNC_PATTERN = re.compile(
        r'(?:static|inline|extern)\s+)*'
        r'(?P<return>(?:\w+\s*\*?\s+)+'
        r'(?P<name>\w+)\s*'
        r'\((?P<args>[^)]*)\)'
    )

    # 结构体定义正则
    STRUCT_PATTERN = re.compile(
        r'(?:typedef\s+)?'
        r'struct\s+'
        r'(?P<name>\w+)'
        r'\s*\{'
    )

    # 枚举定义正则
    ENUM_PATTERN = re.compile(
        r'enum\s+'
        r'(?P<name>\w+)'
        r'\s*\{'
    )

    # 函数调用正则
    CALL_PATTERN = re.compile(r'(\w+)\s*\(')

    # C 关键字（用于过滤伪函数）
    KEYWORDS = {
        'if', 'else', 'for', 'while', 'switch', 'case', 'default',
        'sizeof', 'return', 'break', 'continue', 'goto',
        'int', 'char', 'float', 'double', 'void', 'unsigned', 'signed',
        'struct', 'enum', 'typedef', 'NULL', 'true', 'false'
    }

    def __init__(self, source_code: str, pir_data: Dict):
        super().__init__(source_code, pir_data)
        self._preprocess()

    def _preprocess(self):
        """预处理源码"""
        # 移除注释（更精确的匹配）
        # 先移除多行注释 /* ... */
        self.code = re.sub(r'/\*.*?\*/', '', self.source_code, flags=re.DOTALL)
        # 再移除单行注释 // ...（但不匹配行首的#预处理指令）
        self.code = re.sub(r'(?<!^)\s*//.*', '', self.code)

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
        """提取 C 函数/结构体/枚举完整实现逻辑"""
        implementation = []

        # 检查是否是结构体定义
        struct_match = re.search(
            r'struct\s+' + re.escape(symbol_name) + r'\s*\{',
            self.code
        )

        if struct_match:
            # 提取结构体定义
            implementation.append(f"struct {symbol_name} {{")

            # 提取字段
            fields = self.extract_struct_fields(symbol_name)
            if fields:
                implementation.append("  /* Fields */")
                for field in fields:
                    type_str = field['type']
                    name_str = field['name']
                    array_str = field['array'] if field['array'] else ""
                    bitfield_str = f" : {field['bitfield']}" if field['bitfield'] else ""
                    implementation.append(f"  {type_str} {name_str}{array_str}{bitfield_str};")

            implementation.append('}')
        else:
            # 检查是否是枚举定义
            enum_match = re.search(
                r'enum\s+' + re.escape(symbol_name) + r'\s*\{',
                self.code
            )

            if enum_match:
                # 提取枚举定义
                implementation.append(f"enum {symbol_name} {{")

                # 提取枚举值
                enum_values = self.extract_enum_values(symbol_name)
                if enum_values:
                    implementation.append("  /* Values */")
                    for value in enum_values:
                        value_str = f" = {value['value']}" if value['value'] else ""
                        implementation.append(f"  {value['name']}{value_str},")

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
        # 匹配函数调用模式: identifier(args) 或 ptr->method(args)
        call_pattern = re.compile(r'(\w+)\s*\(([^)]*)\)')
        pointer_pattern = re.compile(r'(\w+)\s*->\s*(\w+)\s*\(([^)]*)\)')

        # 匹配指针方法调用
        for match in pointer_pattern.finditer(line):
            ptr = match.group(1)
            method = match.group(2)
            args = match.group(3).strip()
            if method not in self.KEYWORDS:
                calls.append(f"{ptr}->{method}({args})")

        # 匹配普通函数调用
        for match in call_pattern.finditer(line):
            func_name = match.group(1)
            args = match.group(2).strip()
            if func_name not in self.KEYWORDS:
                calls.append(f"{func_name}({args})")

        return calls

    def extract_behavior(self, symbol_name: str) -> List[str]:
        """提取函数/结构体行为描述"""
        behaviors = []
        in_function = False
        brace_count = 0

        # 检查是否是结构体定义
        struct_match = re.search(
            r'struct\s+' + re.escape(symbol_name) + r'\s*\{',
            self.code
        )

        if struct_match:
            # 结构体行为
            behaviors.append(f"struct {symbol_name} definition")

            # 提取字段
            fields = self.extract_struct_fields(symbol_name)
            if fields:
                behaviors.append(f"  Fields ({len(fields)}):")
                for field in fields:
                    type_str = field['type']
                    name_str = field['name']
                    array_str = f"[{field['array']}]" if field['array'] else ""
                    bitfield_str = f" : {field['bitfield']}" if field['bitfield'] else ""
                    behaviors.append(f"    - {type_str} {name_str}{array_str}{bitfield_str}")
        else:
            # 检查是否是枚举定义
            enum_match = re.search(
                r'enum\s+' + re.escape(symbol_name) + r'\s*\{',
                self.code
            )

            if enum_match:
                # 枚举行为
                behaviors.append(f"enum {symbol_name} definition")

                # 提取枚举值
                enum_values = self.extract_enum_values(symbol_name)
                if enum_values:
                    behaviors.append(f"  Values ({len(enum_values)}):")
                    for value in enum_values:
                        value_str = f" = {value['value']}" if value['value'] else ""
                        behaviors.append(f"    - {value['name']}{value_str}")
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

    def extract_asm_info(self, symbol_name: str) -> Dict:
        """提取汇编信息（C 源码不适用）"""
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

                # 提取字段定义
                line = line.strip()
                if line and not line.startswith('}'):
                    # 匹配字段定义: type name[array]; 或 type name: bitfield;
                    field_match = re.match(
                        r'(?P<type>(?:\w+\s*\*?\s+)+)'
                        r'(?P<name>\w+)'
                        r'(?P<array>\[[^\]]+\])?'
                        r'(?P<bitfield>\s*:\s*\d+)?'
                        r'\s*;',
                        line
                    )
                    if field_match:
                        field = {
                            'name': field_match.group('name'),
                            'type': field_match.group('type').strip(),
                            'array': field_match.group('array'),
                            'bitfield': field_match.group('bitfield').strip() if field_match.group('bitfield') else None
                        }
                        fields.append(field)

                if brace_count <= 0:
                    break

        return fields

    def extract_enum_values(self, enum_name: str) -> List[Dict]:
        """提取枚举值"""
        values = []
        in_enum = False
        brace_count = 0

        for line in self.lines:
            # 查找枚举定义
            if not in_enum:
                match = self.ENUM_PATTERN.search(line)
                if match and match.group('name') == enum_name:
                    in_enum = True
                    brace_count += line.count('{') - line.count('}')
                    continue

            # 在枚举体内提取值
            if in_enum:
                brace_count += line.count('{') - line.count('}')

                # 提取枚举值定义
                line = line.strip()
                if line and not line.startswith('}'):
                    # 匹配枚举值: name = value, 或 name,
                    value_match = re.match(
                        r'(?P<name>\w+)'
                        r'(?:\s*=\s*(?P<value>[^,\}]+))?'
                        r'\s*,?\s*',
                        line
                    )
                    if value_match:
                        value = {
                            'name': value_match.group('name'),
                            'value': value_match.group('value').strip() if value_match.group('value') else None
                        }
                        values.append(value)

                if brace_count <= 0:
                    break

        return values
