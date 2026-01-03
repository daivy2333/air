import re
from typing import Dict, List, Optional, Tuple
from models.resolved_ref import ResolvedRef
from core.language_detector import LanguageDetector

class Extractor:
    """信息提取器 - 从 ResolvedRef 提取最大原始信息集"""

    def __init__(self, pir_data: Dict, source_code_map: Dict[str, str]):
        """
        初始化提取器

        Args:
            pir_data: PIR 数据字典
            source_code_map: 源码映射字典 {unit_id: source_code}
        """
        self.pir_data = pir_data
        self.source_code_map = source_code_map
        self._build_indexes()
        self._init_analyzers()

    def _init_analyzers(self):
        """初始化语言分析器"""
        self.analyzers = {}

        # 为每个unit创建对应的分析器
        for unit in self.pir_data.get('units', []):
            unit_id = unit.get('id')
            source_code = self.source_code_map.get(unit_id)
            path = unit.get('path')

            if source_code and path:
                # 检测语言
                language = LanguageDetector.detect_from_content(source_code, path)

                # 创建对应的分析器
                analyzer_class_name = LanguageDetector.get_analyzer_class(language)
                try:
                    # 动态导入分析器
                    if language == 'python':
                        from analyzers.python import PythonAnalyzer
                        self.analyzers[unit_id] = PythonAnalyzer(source_code, self.pir_data)
                    elif language == 'c':
                        from analyzers.c import CAnalyzer
                        self.analyzers[unit_id] = CAnalyzer(source_code, self.pir_data)
                    elif language == 'cpp':
                        from analyzers.cpp import CppAnalyzer
                        self.analyzers[unit_id] = CppAnalyzer(source_code, self.pir_data)
                    elif language == 'rust':
                        from analyzers.rust import RustAnalyzer
                        self.analyzers[unit_id] = RustAnalyzer(source_code, self.pir_data)
                    elif language == 'asm':
                        from analyzers.asm import ASMAnalyzer
                        self.analyzers[unit_id] = ASMAnalyzer(source_code, self.pir_data)
                    elif language == 'ld':
                        from analyzers.ld import LDAnalyzer
                        self.analyzers[unit_id] = LDAnalyzer(source_code, self.pir_data)
                except Exception as e:
                    print(f"Warning: Failed to initialize analyzer for {unit_id}: {e}")

    def _build_indexes(self):
        """构建索引"""
        self.unit_index = {}
        for unit in self.pir_data.get('units', []):
            self.unit_index[unit.get('id')] = unit

    def extract(self, resolved_ref: ResolvedRef) -> Dict:
        """
        提取最大原始信息集

        Args:
            resolved_ref: 已解析的引用

        Returns:
            包含所有可用信息的字典
        """
        if resolved_ref.is_missing:
            return {'status': 'missing'}

        if resolved_ref.is_ambiguous:
            result = {'status': 'ambiguous'}
            # 如果有建议，添加到结果中
            if resolved_ref.suggestions:
                result['suggestions'] = resolved_ref.suggestions
            return result

        result = {
            'kind': resolved_ref.kind,
            'unit_id': resolved_ref.unit_id,
            'symbol': resolved_ref.symbol,
            'path': resolved_ref.path
        }

        if resolved_ref.kind == 'unit':
            result.update(self._extract_unit_info(resolved_ref.unit_id))
        elif resolved_ref.kind == 'symbol':
            result.update(self._extract_symbol_info(resolved_ref.unit_id, resolved_ref.symbol))
        elif resolved_ref.kind == 'layout':
            result.update(self._extract_layout_info(resolved_ref.symbol))

        return result


    def _extract_unit_info(self, unit_id: str) -> Dict:
        """提取 unit 信息"""
        unit = self.unit_index.get(unit_id, {})

        info = {
            'language': unit.get('language'),
            'type': unit.get('type'),
            'symbols': [s.get('name') for s in unit.get('symbols', [])],
            'entry_points': [s.get('name') for s in unit.get('symbols', []) if s.get('entry', False)]
        }

        # 提取源码
        source_code = self.source_code_map.get(unit_id)
        if source_code:
            info['source_code'] = source_code

        return info

    def _extract_symbol_info(self, unit_id: str, symbol_name: str) -> Dict:
        """提取符号信息"""
        unit = self.unit_index.get(unit_id, {})

        # 查找符号
        symbol_info = None
        for symbol in unit.get('symbols', []):
            if symbol.get('name') == symbol_name:
                symbol_info = symbol
                break

        if not symbol_info:
            return {'status': 'missing'}

        # 从attrs中获取属性
        attrs = symbol_info.get('attrs', {})
        info = {
            'name': symbol_name,
            'type': attrs.get('type'),
            'kind': symbol_info.get('kind', ''),
            'entry': attrs.get('entry', 'false') == 'true',
            'visibility': attrs.get('visibility'),
            'unit_id': unit_id
        }

        # 提取源码中的完整定义
        source_code = self.source_code_map.get(unit_id)
        if source_code:
            definition = self._extract_full_definition(source_code, symbol_name, symbol_info.get('kind', ''))
            if definition:
                info['definition'] = definition

        return info

    def _extract_full_definition(self, source_code: str, symbol_name: str, symbol_kind: str) -> Optional[str]:
        """
        从源码中提取完整的定义（函数、类等）

        Args:
            source_code: 源代码
            symbol_name: 符号名
            symbol_kind: 符号类型（class, func等）

        Returns:
            完整的定义代码，如果未找到则返回None
        """
        if symbol_kind == 'class':
            return self._extract_class_definition(source_code, symbol_name)
        elif symbol_kind == 'func':
            return self._extract_function_definition(source_code, symbol_name)
        return None

    def _extract_class_definition(self, source_code: str, class_name: str) -> Optional[str]:
        """
        提取完整的类定义

        Args:
            source_code: 源代码
            class_name: 类名

        Returns:
            完整的类定义代码
        """
        lines = source_code.split('\n')
        class_pattern = re.compile(r'^\s*class\s+' + re.escape(class_name) + r'\b')

        # 找到类定义的起始行
        start_line = None
        for i, line in enumerate(lines):
            if class_pattern.match(line):
                start_line = i
                break

        if start_line is None:
            return None

        # 提取完整的类定义（包括所有方法）
        indent_level = None
        class_lines = []

        for i in range(start_line, len(lines)):
            line = lines[i]

            # 确定初始缩进级别
            if indent_level is None:
                stripped = line.lstrip()
                if stripped and not stripped.startswith('#'):
                    indent_level = len(line) - len(stripped)

            # 检查是否到达类定义结束
            if indent_level is not None:
                stripped = line.lstrip()
                if stripped and not stripped.startswith('#'):
                    current_indent = len(line) - len(stripped)
                    if current_indent <= indent_level and i > start_line:
                        break

            class_lines.append(line)

        return '\n'.join(class_lines)

    def _extract_function_definition(self, source_code: str, func_name: str) -> Optional[str]:
        """
        提取完整的函数定义

        Args:
            source_code: 源代码
            func_name: 函数名

        Returns:
            完整的函数定义代码
        """
        lines = source_code.split('\n')
        func_pattern = re.compile(r'^\s*def\s+' + re.escape(func_name) + r'\b')

        # 找到函数定义的起始行
        start_line = None
        for i, line in enumerate(lines):
            if func_pattern.match(line):
                start_line = i
                break

        if start_line is None:
            return None

        # 提取完整的函数定义
        indent_level = None
        func_lines = []

        for i in range(start_line, len(lines)):
            line = lines[i]

            # 确定初始缩进级别
            if indent_level is None:
                stripped = line.lstrip()
                if stripped and not stripped.startswith('#'):
                    indent_level = len(line) - len(stripped)

            # 检查是否到达函数定义结束
            if indent_level is not None:
                stripped = line.lstrip()
                if stripped and not stripped.startswith('#'):
                    current_indent = len(line) - len(stripped)
                    if current_indent <= indent_level and i > start_line:
                        break

            func_lines.append(line)

        return '\n'.join(func_lines)

    def _extract_layout_info(self, section_name: str) -> Dict:
        """提取 layout 信息"""
        layout = self.pir_data.get('layout', {})
        section_info = layout.get(section_name, {})

        return {
            'section': section_name,
            'start': section_info.get('start'),
            'size': section_info.get('size'),
            'attributes': section_info.get('attributes', [])
        }

    def extract_signatures(self, resolved_ref: ResolvedRef) -> List[str]:
        """
        提取符号签名列表（使用语言分析器）

        Args:
            resolved_ref: 已解析的引用

        Returns:
            签名列表
        """
        if resolved_ref.kind != 'symbol' or not resolved_ref.unit_id:
            return []

        # 尝试使用语言分析器
        analyzer = self.analyzers.get(resolved_ref.unit_id)
        if analyzer:
            try:
                signature = analyzer.extract_signature(resolved_ref.symbol)
                if signature:
                    return [signature]
            except Exception as e:
                print(f"Warning: Analyzer failed for signature {resolved_ref.unit_id}#{resolved_ref.symbol}: {e}")

        # 回退到通用实现
        unit = self.unit_index.get(resolved_ref.unit_id, {})
        signatures = []

        for symbol in unit.get('symbols', []):
            if symbol.get('name') == resolved_ref.symbol:
                # 从源码中提取签名
                source_code = self.source_code_map.get(resolved_ref.unit_id)
                if source_code:
                    signature = self._extract_signature_from_source(source_code, resolved_ref.symbol, symbol.get('kind', ''))
                    if signature:
                        signatures.append(signature)
                elif 'signature' in symbol:
                    signatures.append(symbol['signature'])

        return signatures

    def _extract_signature_from_source(self, source_code: str, symbol_name: str, symbol_kind: str) -> Optional[str]:
        """
        从源码中提取签名

        Args:
            source_code: 源代码
            symbol_name: 符号名
            symbol_kind: 符号类型

        Returns:
            签名字符串
        """
        lines = source_code.split('\n')

        if symbol_kind == 'class':
            pattern = re.compile(r'^\s*class\s+' + re.escape(symbol_name) + r'\b.*:')
        elif symbol_kind == 'func':
            pattern = re.compile(r'^\s*def\s+' + re.escape(symbol_name) + r'\b.*:')
        else:
            return None

        for line in lines:
            match = pattern.match(line)
            if match:
                return line.strip()

        return None

    def extract_implementation(self, resolved_ref: ResolvedRef) -> List[str]:
        """
        提取完整实现逻辑（使用语言分析器）

        根据符号类型和语言自动选择合适的提取方法：
        - 对于class类型：调用extract_class方法提取完整类定义
        - 对于struct类型：调用extract_struct方法提取完整结构体定义
        - 对于func类型：调用extract_implementation方法提取函数实现

        Args:
            resolved_ref: 已解析的引用

        Returns:
            实现详情列表,保留关键控制流和操作
        """
        if resolved_ref.kind != 'symbol' or not resolved_ref.unit_id:
            return []

        # 尝试使用语言分析器
        analyzer = self.analyzers.get(resolved_ref.unit_id)
        if analyzer:
            try:
                # 获取符号类型
                unit = self.unit_index.get(resolved_ref.unit_id, {})
                symbol_info = None
                for symbol in unit.get('symbols', []):
                    if symbol.get('name') == resolved_ref.symbol:
                        symbol_info = symbol
                        break

                if not symbol_info:
                    return []

                symbol_kind = symbol_info.get('kind', '')

                # 根据符号类型选择合适的提取方法
                if symbol_kind == 'class':
                    # 对于类，尝试使用extract_class方法
                    if hasattr(analyzer, 'extract_class'):
                        class_def = analyzer.extract_class(resolved_ref.symbol)
                        if class_def:
                            return [class_def]
                elif symbol_kind == 'struct':
                    # 对于结构体，尝试使用extract_struct方法
                    if hasattr(analyzer, 'extract_struct'):
                        source_code = self.source_code_map.get(resolved_ref.unit_id)
                        if source_code:
                            struct_def = analyzer.extract_struct(source_code, resolved_ref.symbol)
                            if struct_def:
                                return [struct_def]
                elif symbol_kind == 'func':
                    # 对于函数，使用extract_implementation方法
                    implementation = analyzer.extract_implementation(resolved_ref.symbol)
                    if implementation:
                        return implementation

            except Exception as e:
                print(f"Warning: Analyzer failed for {resolved_ref.unit_id}#{resolved_ref.symbol}: {e}")

        # 回退到通用实现
        source_code = self.source_code_map.get(resolved_ref.unit_id)
        if not source_code:
            return []

        # 提取完整定义
        unit = self.unit_index.get(resolved_ref.unit_id, {})
        symbol_info = None
        for symbol in unit.get('symbols', []):
            if symbol.get('name') == resolved_ref.symbol:
                symbol_info = symbol
                break

        if not symbol_info:
            return []

        definition = self._extract_full_definition(
            source_code,
            resolved_ref.symbol,
            symbol_info.get('kind', '')
        )

        if not definition:
            return []

        # 提取实现详情,保留关键控制流和操作
        return self._extract_implementation_details(definition)


    def _extract_implementation_details(self, definition: str) -> List[str]:
        """
        提取实现详情,保留关键控制流和操作

        检查代码块完整性，确保大括号匹配

        Args:
            definition: 完整定义代码

        Returns:
            实现详情列表
        """
        # 检查代码块完整性
        open_braces = definition.count('{')
        close_braces = definition.count('}')

        # 如果大括号不匹配，尝试扩展范围
        if open_braces != close_braces:
            print(f"Warning: Incomplete code block detected for definition ({{: {open_braces}, }}: {close_braces})")

        lines = definition.split('\n')
        details = []

        # 识别关键控制流（Python和C/C++）
        control_flow_keywords = [
            'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'with',
            'switch', 'case', 'default', 'break', 'continue', 'goto'
        ]

        # 检查是否是dataclass定义
        is_dataclass = '@dataclass' in definition or 'dataclass' in definition

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                continue

            # 跳过装饰器行
            if stripped.startswith('@'):
                continue

            # 对于dataclass，保留字段定义
            if is_dataclass:
                # 匹配字段定义: name: type = value
                field_match = re.match(r'(\w+)\s*:\s*[^=]+(?:\s*=\s*.+)?', stripped)
                if field_match:
                    details.append(stripped)
                    continue

            # 保留关键控制流
            if any(keyword in stripped for keyword in control_flow_keywords):
                details.append(stripped)
            # 保留函数调用
            elif '(' in stripped and ')' in stripped:
                details.append(stripped)
            # 保留赋值和返回语句
            elif '=' in stripped or 'return' in stripped:
                details.append(stripped)
            # 保留类成员声明（C++）
            elif re.match(r'^\s*(public|private|protected):', stripped):
                details.append(stripped)

        return details


    def extract_asm_info(self, resolved_ref: ResolvedRef) -> Dict:
        """
        提取汇编信息（使用语言分析器）

        Args:
            resolved_ref: 已解析的引用

        Returns:
            包含标签和流程的字典
        """
        # 尝试使用语言分析器
        analyzer = self.analyzers.get(resolved_ref.unit_id)
        if analyzer:
            try:
                asm_info = analyzer.extract_asm_info(resolved_ref.symbol)
                if asm_info:
                    return asm_info
            except Exception as e:
                print(f"Warning: Analyzer failed for asm info {resolved_ref.unit_id}#{resolved_ref.symbol}: {e}")

        # 回退到占位符
        return {
            'labels': [resolved_ref.symbol] if resolved_ref.symbol else [],
            'flow': []
        }

    def extract_summary(self, resolved_ref: ResolvedRef) -> Dict[str, str]:
        """
        提取摘要信息

        Args:
            resolved_ref: 已解析的引用

        Returns:
            键值对形式的摘要
        """
        if resolved_ref.kind == 'layout':
            layout_info = self._extract_layout_info(resolved_ref.symbol)
            return {
                'start': str(layout_info.get('start', 'unknown')),
                'size': str(layout_info.get('size', 'unknown'))
            }

        if resolved_ref.kind == 'symbol':
            unit = self.unit_index.get(resolved_ref.unit_id, {})
            symbol_info = None
            for symbol in unit.get('symbols', []):
                if symbol.get('name') == resolved_ref.symbol:
                    symbol_info = symbol
                    break

            summary = {
                'type': symbol_info.get('kind', 'unknown') if symbol_info else 'unknown',
                'unit_id': resolved_ref.unit_id
            }

            # 提取签名
            source_code = self.source_code_map.get(resolved_ref.unit_id)
            if source_code and symbol_info:
                signature = self._extract_signature_from_source(
                    source_code,
                    resolved_ref.symbol,
                    symbol_info.get('kind', '')
                )
                if signature:
                    summary['signature'] = signature

            return summary

        return {}

    def extract_callchain(self, resolved_ref: ResolvedRef, visited: Optional[set] = None, max_depth: int = 10) -> List[str]:
        """
        提取调用链（支持跨unit追踪和递归分析，使用语言分析器）

        Args:
            resolved_ref: 已解析的引用
            visited: 已访问的符号集合（用于避免循环）
            max_depth: 最大递归深度

        Returns:
            调用路径列表
        """
        if resolved_ref.kind != 'symbol' or not resolved_ref.unit_id:
            return []

        # 初始化visited集合
        if visited is None:
            visited = set()

        # 检查递归深度
        if max_depth <= 0:
            return []

        # 避免循环调用
        ref_key = f"{resolved_ref.unit_id}#{resolved_ref.symbol}"
        if ref_key in visited:
            return []
        visited.add(ref_key)

        # 尝试使用语言分析器
        analyzer = self.analyzers.get(resolved_ref.unit_id)
        if analyzer:
            try:
                callchain = analyzer.extract_callchain(resolved_ref.symbol)
                if callchain:
                    # 转换为完整引用格式
                    formatted_chain = []
                    for func in callchain:
                        if '#' not in func:
                            formatted_chain.append(f"{resolved_ref.unit_id}#{func}")
                        else:
                            formatted_chain.append(func)
                    return formatted_chain
            except Exception as e:
                print(f"Warning: Analyzer failed for callchain {resolved_ref.unit_id}#{resolved_ref.symbol}: {e}")

        # 回退到通用实现
        source_code = self.source_code_map.get(resolved_ref.unit_id)
        if not source_code:
            return []

        # 提取函数定义
        unit = self.unit_index.get(resolved_ref.unit_id, {})
        symbol_info = None
        for symbol in unit.get('symbols', []):
            if symbol.get('name') == resolved_ref.symbol:
                symbol_info = symbol
                break

        if not symbol_info:
            return []

        definition = self._extract_full_definition(
            source_code,
            resolved_ref.symbol,
            symbol_info.get('kind', '')
        )

        if not definition:
            return []

        # 分析函数调用
        callchain = [f"{resolved_ref.unit_id}#{resolved_ref.symbol}"]

        # 提取所有函数调用
        called_funcs = self._extract_function_calls_from_code(definition, resolved_ref.unit_id)

        # 对每个调用的函数，递归分析其调用链
        for called_unit_id, called_func in called_funcs:
            called_ref = f"{called_unit_id}#{called_func}"
            if called_ref not in callchain:  # 避免重复
                callchain.append(called_ref)
                # 递归分析被调用函数的调用链
                if called_unit_id in self.unit_index:
                    called_unit = self.unit_index[called_unit_id]
                    for symbol in called_unit.get('symbols', []):
                        if symbol.get('name') == called_func:
                            called_resolved = ResolvedRef(
                                kind='symbol',
                                unit_id=called_unit_id,
                                symbol=called_func,
                                path=called_unit.get('path')
                            )
                            # 递归调用，深度减1
                            sub_chain = self.extract_callchain(
                                called_resolved, 
                                visited.copy(), 
                                max_depth - 1
                            )
                            # 添加子调用链（跳过第一个元素，因为它是当前函数）
                            if len(sub_chain) > 1:
                                callchain.extend(sub_chain[1:])
                            break

        return callchain

    def _extract_function_calls_from_code(self, code: str, unit_id: str) -> List[Tuple[str, str]]:
        """
        从代码中提取所有函数调用

        Args:
            code: 源代码
            unit_id: 当前unit的ID

        Returns:
            [(unit_id, func_name)] 列表
        """
        calls = []
        lines = code.split('\n')

        # 构建所有unit的符号索引（用于跨unit调用查找）
        all_symbols = {}  # symbol_name -> [unit_ids]
        for uid, unit in self.unit_index.items():
            for symbol in unit.get('symbols', []):
                sym_name = symbol.get('name')
                if sym_name not in all_symbols:
                    all_symbols[sym_name] = []
                all_symbols[sym_name].append(uid)

        for line in lines:
            stripped = line.strip()
            # 跳过注释和空行
            if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                continue

            # 检测函数调用模式
            if re.match(r'\w+\(', stripped):
                # 提取被调用的函数名
                match = re.match(r'(\w+)\(', stripped)
                if match:
                    called_func = match.group(1)
                    # 查找该函数在哪个unit中
                    if called_func in all_symbols:
                        # 优先使用当前unit
                        if unit_id in all_symbols[called_func]:
                            calls.append((unit_id, called_func))
                        else:
                            # 使用第一个找到的unit
                            calls.append((all_symbols[called_func][0], called_func))

        return calls

    def extract_behavior(self, resolved_ref: ResolvedRef) -> Optional[str]:
        """
        提取函数/方法的行为描述（使用语言分析器）

        Args:
            resolved_ref: 已解析的引用

        Returns:
            行为描述字符串
        """
        if resolved_ref.kind != 'symbol' or not resolved_ref.unit_id:
            return None

        # 尝试使用语言分析器
        analyzer = self.analyzers.get(resolved_ref.unit_id)
        if analyzer:
            try:
                behavior = analyzer.extract_behavior(resolved_ref.symbol)
                if behavior:
                    return behavior
            except Exception as e:
                print(f"Warning: Analyzer failed for behavior {resolved_ref.unit_id}#{resolved_ref.symbol}: {e}")

        # 回退到占位符实现
        unit = self.unit_index.get(resolved_ref.unit_id, {})
        symbol_info = None
        for symbol in unit.get('symbols', []):
            if symbol.get('name') == resolved_ref.symbol:
                symbol_info = symbol
                break

        if not symbol_info:
            return None

        # 简单的行为描述占位符
        kind = symbol_info.get('kind', '')
        if kind == 'func':
            return f"Function {resolved_ref.symbol} implementation"
        elif kind == 'class':
            return f"Class {resolved_ref.symbol} definition"

        return None

        return None
