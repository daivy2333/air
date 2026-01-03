import ast
from typing import Dict, List, Optional
from analyzers.base import BaseAnalyzer

class PythonAnalyzer(BaseAnalyzer):
    """Python 源码分析器 - 增强版"""

    def __init__(self, source_code: str, pir_data: Dict):
        super().__init__(source_code, pir_data)
        self.tree = None
        try:
            self.tree = ast.parse(source_code)
        except SyntaxError:
            pass

    def extract_signature(self, symbol_name: str) -> Optional[str]:
        """提取 Python 函数/类签名，包括类型注解"""
        if not self.tree:
            return None

        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == symbol_name:
                    return self._extract_function_signature(node)
            elif isinstance(node, ast.ClassDef):
                if node.name == symbol_name:
                    return self._extract_class_signature(node)

        return None

    def _extract_function_signature(self, node: ast.FunctionDef) -> str:
        """提取函数签名"""
        args = []
        # 普通参数
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f': {ast.unparse(arg.annotation)}'
            args.append(arg_str)

        # 默认参数
        defaults = node.args.defaults
        if defaults:
            for i, default in enumerate(defaults):
                idx = len(args) - len(defaults) + i
                if idx >= 0:
                    args[idx] += f' = {ast.unparse(default)}'

        # *args
        if node.args.vararg:
            vararg = node.args.vararg.arg
            if node.args.vararg.annotation:
                vararg += f': {ast.unparse(node.args.vararg.annotation)}'
            args.append(f'*{vararg}')

        # **kwargs
        if node.args.kwarg:
            kwarg = node.args.kwarg.arg
            if node.args.kwarg.annotation:
                kwarg += f': {ast.unparse(node.args.kwarg.annotation)}'
            args.append(f'**{kwarg}')

        # 返回类型
        return_type = ''
        if node.returns:
            return_type = f' -> {ast.unparse(node.returns)}'

        # 装饰器
        decorators = self._extract_decorators(node)
        decorator_str = '\n'.join(decorators) + '\n' if decorators else ''

        func_type = 'async def' if isinstance(node, ast.AsyncFunctionDef) else 'def'
        return f"{decorator_str}{func_type} {node.name}({', '.join(args)}){return_type}"

    def _extract_class_signature(self, node: ast.ClassDef) -> str:
        """提取类签名"""
        bases = []
        for base in node.bases:
            bases.append(ast.unparse(base))

        # 类型参数 (Python 3.12+)
        type_params = ''
        if hasattr(node, 'type_params') and node.type_params:
            type_param_strs = [ast.unparse(tp) for tp in node.type_params]
            type_params = f'[{", ".join(type_param_strs)}]'

        # 装饰器
        decorators = self._extract_decorators(node)
        decorator_str = '\n'.join(decorators) + '\n' if decorators else ''

        if bases:
            return f"{decorator_str}class {node.name}{type_params}({', '.join(bases)})"
        return f"{decorator_str}class {node.name}{type_params}"

    def _extract_decorators(self, node) -> List[str]:
        """提取装饰器"""
        decorators = []
        for decorator in node.decorator_list:
            try:
                decorators.append('@' + ast.unparse(decorator))
            except:
                pass
        return decorators

    def extract_implementation(self, symbol_name: str) -> List[str]:
        """提取 Python 函数完整实现逻辑"""
        if not self.tree:
            return []

        implementation = []

        for node in ast.walk(self.tree):
            # 处理dataclass
            if isinstance(node, ast.ClassDef):
                if node.name == symbol_name:
                    # 检查是否是dataclass
                    is_dataclass = any(
                        decorator.id == 'dataclass' 
                        for decorator in node.decorator_list 
                        if isinstance(decorator, ast.Name)
                    )

                    if is_dataclass:
                        # 提取dataclass字段
                        for stmt in node.body:
                            if isinstance(stmt, ast.AnnAssign):
                                # 字段定义: name: type = value
                                field_str = ast.unparse(stmt).strip()
                                if field_str:
                                    implementation.append(field_str)
                            elif isinstance(stmt, ast.FunctionDef):
                                # 提取方法
                                method_str = ast.unparse(stmt).strip()
                                if method_str:
                                    implementation.append(method_str)
                    else:
                        # 普通类，提取方法
                        for stmt in node.body:
                            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                method_str = ast.unparse(stmt).strip()
                                if method_str:
                                    implementation.append(method_str)
                    break

            # 处理函数
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == symbol_name:
                    # 提取函数体中的关键语句
                    for stmt in node.body:
                        stmt_str = self._extract_statement_details(stmt)
                        if stmt_str:
                            implementation.append(stmt_str)
                    break

        return implementation

    def _extract_class_info(self, node: ast.ClassDef) -> List[str]:
        """提取类信息（字段和方法）"""
        info = []

        # 提取装饰器
        decorators = self._extract_decorators(node)
        info.extend(decorators)

        # 检查是否是dataclass
        is_dataclass = any(
            decorator.id == 'dataclass'
            for decorator in node.decorator_list
            if isinstance(decorator, ast.Name)
        )

        if is_dataclass:
            # 提取dataclass字段
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign):
                    # 字段定义: name: type = value
                    field_str = ast.unparse(stmt).strip()
                    if field_str:
                        info.append(field_str)
                elif isinstance(stmt, ast.FunctionDef):
                    # 提取方法
                    method_str = ast.unparse(stmt).strip()
                    if method_str:
                        info.append(method_str)
        else:
            # 普通类，提取字段和方法
            fields = self._extract_class_fields(node)
            if fields:
                info.append("# Fields:")
                for field in fields:
                    info.append(f"  {field['name']}: {field['type'] if field['type'] else 'Any'}")
                    if field['value']:
                        info.append(f"    = {field['value']}")

            # 提取方法
            for stmt in node.body:
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_info = self._extract_method_info(stmt)
                    info.append(f"\n  # Method: {stmt.name}")
                    info.extend([f"    {line}" for line in method_info])

        return info

    def _extract_statement_details(self, stmt) -> Optional[str]:
        """提取语句的完整详情"""
        try:
            return ast.unparse(stmt).strip()
        except:
            return None

    def _extract_class_fields(self, node: ast.ClassDef) -> List[Dict]:
        """提取类字段（包括类型注解）"""
        fields = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                # 带类型注解的字段: name: type = value
                field = {
                    'name': item.target.id if hasattr(item.target, 'id') else '',
                    'type': self._get_annotation(item.annotation),
                    'value': self._get_expr_value(item.value) if item.value else None
                }
                fields.append(field)
            elif isinstance(item, ast.Assign):
                # 普通赋值字段
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        field = {
                            'name': target.id,
                            'type': None,
                            'value': self._get_expr_value(item.value)
                        }
                        fields.append(field)
        return fields

    def _extract_method_info(self, node: ast.FunctionDef) -> List[str]:
        """提取方法信息"""
        info = []

        # 提取装饰器
        decorators = self._extract_decorators(node)
        if decorators:
            info.extend(decorators)

        # 提取签名
        signature = self._extract_function_signature(node)
        info.append(signature)

        # 提取方法体
        for stmt in node.body:
            stmt_str = self._extract_statement_details(stmt)
            if stmt_str:
                info.append(f"    {stmt_str}")

        return info

    def _get_annotation(self, annotation) -> Optional[str]:
        """获取类型注解字符串"""
        try:
            return ast.unparse(annotation) if annotation else None
        except:
            return None

    def _get_expr_value(self, expr) -> Optional[str]:
        """获取表达式值"""
        try:
            return ast.unparse(expr) if expr else None
        except:
            return None

    def extract_callchain(self, symbol_name: str) -> List[str]:
        """提取完整的调用链信息"""
        if not self.tree:
            return []

        callchain = []

        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == symbol_name:
                    # 查找函数调用,保留完整的调用信息
                    for stmt in ast.walk(node):
                        if isinstance(stmt, ast.Call):
                            call_info = self._extract_call_info(stmt)
                            if call_info:
                                callchain.append(call_info)
                    break

        return callchain

    def _extract_call_info(self, call_node: ast.Call) -> Optional[str]:
        """提取函数调用的完整信息"""
        try:
            if isinstance(call_node.func, ast.Name):
                return f"{call_node.func.id}({ast.unparse(call_node.args)})"
            elif isinstance(call_node.func, ast.Attribute):
                obj = ast.unparse(call_node.func.value)
                attr = call_node.func.attr
                args = ast.unparse(call_node.args)
                return f"{obj}.{attr}({args})"
        except:
            return None

    def extract_behavior(self, symbol_name: str) -> List[str]:
        """提取函数/类行为描述"""
        if not self.tree:
            return []

        behaviors = []

        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == symbol_name:
                    # 分析函数体，提取关键行为
                    for stmt in node.body:
                        behavior = self._extract_behavior_from_stmt(stmt)
                        if behavior:
                            behaviors.append(behavior)
                    break
            elif isinstance(node, ast.ClassDef):
                if node.name == symbol_name:
                    # 分析类，提取关键行为
                    behaviors.append(f"Class {symbol_name} definition")

                    # 提取字段
                    fields = self._extract_class_fields(node)
                    if fields:
                        behaviors.append(f"  Fields ({len(fields)}):")
                        for field in fields:
                            type_str = f": {field['type']}" if field['type'] else ""
                            value_str = f" = {field['value']}" if field['value'] else ""
                            behaviors.append(f"    - {field['name']}{type_str}{value_str}")

                    # 提取方法
                    methods = [stmt for stmt in node.body if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    if methods:
                        behaviors.append(f"  Methods ({len(methods)}):")
                        for method in methods:
                            decorators = self._extract_decorators(method)
                            decorator_str = f" [{', '.join(decorators)}]" if decorators else ""
                            behaviors.append(f"    - {method.name}{decorator_str}")
                    break

        return behaviors

    def _extract_behavior_from_stmt(self, stmt) -> Optional[str]:
        """从语句中提取行为描述"""
        try:
            stmt_str = ast.unparse(stmt).strip()

            # 控制流
            if isinstance(stmt, (ast.If, ast.For, ast.While, ast.With)):
                return f"Control flow: {stmt_str}"
            # 返回语句
            elif isinstance(stmt, ast.Return):
                return f"Returns: {stmt_str}"
            # 赋值
            elif isinstance(stmt, ast.Assign):
                return f"Assignment: {stmt_str}"
            # 函数调用
            elif isinstance(stmt, ast.Call):
                return f"Call: {stmt_str}"
            # 异常处理
            elif isinstance(stmt, (ast.Try, ast.Raise)):
                return f"Exception handling: {stmt_str}"

            return None
        except:
            return None

    def extract_class(self, class_name: str) -> Optional[str]:
        """提取Python类定义（包含方法）"""
        try:
            tree = ast.parse(self.source_code)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    # 获取类源代码范围
                    lines = self.source_code.split('\n')
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
        match = re.search(pattern, self.source_code, re.DOTALL)
        if match:
            return match.group(0)

        return None

    def extract_asm_info(self, symbol_name: str) -> Dict:
        """提取汇编信息（Python 不适用）"""
        return {
            'labels': [],
            'flow': []
        }
