from typing import Dict, List
from models.resolved_ref import ResolvedRef
from models.evidence import Evidence

class EvidenceBuilder:
    """证据构建器 - 根据 view 构建完整的代码证据"""

    def __init__(self, extractor):
        """
        初始化证据构建器

        Args:
            extractor: Extractor 实例
        """
        self.extractor = extractor

    def build(self, need, resolved_ref: ResolvedRef) -> Evidence:
        """
        根据 view 构建完整信息生成 Evidence

        Args:
            need: Need 对象
            resolved_ref: 已解析的引用

        Returns:
            Evidence 对象
        """
        view = need.view
        ref = need.ref

        # 处理缺失和多义情况
        if resolved_ref.is_missing:
            return Evidence.missing(ref, view)

        if resolved_ref.is_ambiguous:
            # 提取suggestions信息
            info = self.extractor.extract(resolved_ref)
            suggestions = info.get('suggestions', [])

            # 直接传递suggestions，保留详细信息
            return Evidence.ambiguous(ref, view, suggestions=suggestions)

        # 确定 source
        if resolved_ref.kind == 'layout':
            source = 'layout'
        else:
            source = resolved_ref.unit_id or 'unknown'

        # 根据 view 生成不同类型的证据
        if view == 'exist':
            return self._build_exist(ref, source, resolved_ref)
        elif view == 'definition':
            return self._build_definition(ref, source, resolved_ref)
        elif view == 'api':
            return self._build_api(ref, source, resolved_ref)
        elif view == 'impl':
            return self._build_impl(ref, source, resolved_ref)
        elif view == 'asm':
            return self._build_asm(ref, source, resolved_ref)
        elif view == 'summary':
            return self._build_summary(ref, source, resolved_ref)
        elif view == 'callchain':
            return self._build_callchain(ref, source, resolved_ref)
        else:
            return Evidence.missing(ref, view)



    def _build_exist(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """构建存在性证据 - 包含位置信息"""
        content = {'status': 'yes'}

        # 添加完整的位置信息
        if resolved_ref.kind == 'symbol':
            info = self.extractor.extract(resolved_ref)
            if 'path' in info:
                content['location'] = info['path']
            # 添加行号信息
            source_code = self.extractor.source_code_map.get(resolved_ref.unit_id)
            if source_code:
                line_number = self._find_symbol_line(source_code, resolved_ref.symbol)
                if line_number:
                    content['location'] = f"{info.get('path', '')}:{line_number}"

        return Evidence.exist(ref, source, True, content.get('location'))

    def _find_symbol_line(self, source_code: str, symbol: str) -> int:
        """在源代码中查找符号定义的行号"""
        lines = source_code.split('\n')
        for i, line in enumerate(lines, 1):
            # 简单匹配符号定义行
            if f'def {symbol}' in line or f'class {symbol}' in line:
                return i
        return None

    def _build_definition(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """构建定义证据 - 保留完整定义"""
        info = self.extractor.extract(resolved_ref)

        content = {
            'kind': info.get('kind'),
            'unit': info.get('unit_id')
        }

        # 添加完整定义
        if 'definition' in info:
            content['definition'] = info['definition']

        return Evidence(
            ref=ref,
            view='definition',
            source=source,
            content=content
        )

    def _build_api(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """构建 API 证据 - 保留完整签名"""
        info = self.extractor.extract(resolved_ref)

        content = {}

        # 根据类型处理
        if resolved_ref.kind == 'unit':
            # 对于unit，列出所有符号的签名
            unit_id = resolved_ref.unit_id
            unit = self.extractor.unit_index.get(unit_id, {})
            symbols = unit.get('symbols', [])

            signatures = []
            for symbol in symbols:
                symbol_name = symbol.get('name')
                symbol_kind = symbol.get('kind', '')
                source_code = self.extractor.source_code_map.get(unit_id)
                if source_code:
                    signature = self.extractor._extract_signature_from_source(
                        source_code, symbol_name, symbol_kind
                    )
                    if signature:
                        signatures.append(signature)

            if signatures:
                content['signatures'] = signatures
        else:
            # 对于symbol，提取签名
            signatures = self.extractor.extract_signatures(resolved_ref)
            if signatures:
                content['signatures'] = signatures

        return Evidence(
            ref=ref,
            view='api',
            source=source,
            content=content
        )

    def _build_impl(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """构建实现证据 - 保留完整实现"""

        if resolved_ref.kind == 'unit':
            # 对于unit，返回所有符号的实现摘要
            unit_id = resolved_ref.unit_id
            unit = self.extractor.unit_index.get(unit_id, {})
            symbols = unit.get('symbols', [])

            implementation = []
            for symbol in symbols:
                symbol_name = symbol.get('name')
                symbol_kind = symbol.get('kind', '')
                symbol_impl = self.extractor.extract_implementation(
                    ResolvedRef(kind='symbol', unit_id=unit_id, symbol=symbol_name, path=resolved_ref.path)
                )
                if symbol_impl:
                    implementation.append({
                        'symbol': symbol_name,
                        'kind': symbol_kind,
                        'implementation': symbol_impl
                    })

            content = {}
            if implementation:
                content['implementation'] = implementation
        else:
            # 原有的symbol处理逻辑
            implementation = self.extractor.extract_implementation(resolved_ref)
            content = {}
            if implementation:
                content['implementation'] = implementation

        return Evidence(
            ref=ref,
            view='impl',
            source=source,
            content=content
        )

    def _build_asm(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """构建汇编证据 - 保留完整汇编信息"""
        asm_info = self.extractor.extract_asm_info(resolved_ref)

        content = {
            'labels': asm_info.get('labels', []),
            'flow': asm_info.get('flow', [])
        }

        return Evidence.asm(ref, source, content)

    def _build_summary(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """构建结构化语义总结 - 键值对形式,不省略关键字段"""
        items = self.extractor.extract_summary(resolved_ref)

        # 根据类型处理
        if resolved_ref.kind == 'unit':
            # 对于unit，提供unit的基本信息
            unit_id = resolved_ref.unit_id
            unit = self.extractor.unit_index.get(unit_id, {})
            items.update({
                'type': unit.get('type', 'unknown'),
                'module': unit.get('module', 'unknown'),
                'role': unit.get('role', 'unknown'),
                'path': unit.get('path', 'unknown'),
                'symbol_count': len(unit.get('symbols', []))
            })
        elif resolved_ref.kind == 'symbol':
            # 对于symbol，确保包含所有关键字段
            info = self.extractor.extract(resolved_ref)
            if 'type' not in items and 'type' in info:
                items['type'] = info['type']
            if 'signature' not in items:
                source_code = self.extractor.source_code_map.get(resolved_ref.unit_id)
                if source_code:
                    signature = self.extractor._extract_signature_from_source(
                        source_code,
                        resolved_ref.symbol,
                        info.get('kind', '')
                    )
                    if signature:
                        items['signature'] = signature

        return Evidence.summary(ref, source, items)

    def _build_callchain(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """构建调用路径 - 保留完整调用链"""
        path = self.extractor.extract_callchain(resolved_ref)

        content = {
            'path': path
        }

        return Evidence.callchain(ref, source, content)
