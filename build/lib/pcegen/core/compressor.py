from typing import Dict, List
from models.resolved_ref import ResolvedRef
from models.evidence import Evidence

class Compressor:
    """信息压缩器 - 根据 view 将原始信息压缩为最小证据"""

    def __init__(self, extractor):
        """
        初始化压缩器

        Args:
            extractor: Extractor 实例
        """
        self.extractor = extractor

    def compress(self, need, resolved_ref: ResolvedRef) -> Evidence:
        """
        根据 view 压缩信息生成 Evidence

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
            return Evidence.ambiguous(ref, view)

        # 确定 source
        if resolved_ref.kind == 'layout':
            source = 'layout'
        else:
            source = resolved_ref.unit_id or 'unknown'

        # 根据 view 生成不同类型的证据
        if view == 'exist':
            return self._compress_exist(ref, source, resolved_ref)
        elif view == 'definition':
            return self._compress_definition(ref, source, resolved_ref)
        elif view == 'api':
            return self._compress_api(ref, source, resolved_ref)
        elif view == 'impl':
            return self._compress_impl(ref, source, resolved_ref)
        elif view == 'asm':
            return self._compress_asm(ref, source, resolved_ref)
        elif view == 'summary':
            return self._compress_summary(ref, source, resolved_ref)
        elif view == 'callchain':
            return self._compress_callchain(ref, source, resolved_ref)
        else:
            return Evidence.missing(ref, view)

    def _compress_exist(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """压缩为存在性证据"""
        return Evidence.exist(ref, source, True)

    def _compress_definition(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """压缩为定义证据 - 保留完整定义"""
        # 提取完整信息
        info = self.extractor.extract(resolved_ref)

        # 构建content
        content = {}

        if 'definition' in info:
            content['code'] = info['definition']
        elif 'source_code' in info:
            content['code'] = info['source_code']

        if 'kind' in info:
            content['kind'] = info['kind']

        if 'unit_id' in info:
            content['unit'] = info['unit_id']

        return Evidence(
            ref=ref,
            view='definition',
            source=source,
            content=content
        )

    def _compress_api(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """压缩为 API 证据 - 保留完整签名"""
        info = self.extractor.extract(resolved_ref)

        content = {}

        # 提取签名
        signatures = self.extractor.extract_signatures(resolved_ref)
        if signatures:
            content['signatures'] = signatures

        # 如果有完整定义，也包含进来
        if 'definition' in info:
            content['code'] = info['definition']

        return Evidence(
            ref=ref,
            view='api',
            source=source,
            content=content
        )

    def _compress_impl(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """压缩为实现证据 - 保留完整实现"""
        info = self.extractor.extract(resolved_ref)

        content = {}

        # 保留完整实现代码
        if 'definition' in info:
            content['code'] = info['definition']

        # 提取行为描述
        behavior = self.extractor.extract_behavior(resolved_ref)
        if behavior:
            content['behavior'] = behavior

        return Evidence(
            ref=ref,
            view='impl',
            source=source,
            content=content
        )

    def _compress_asm(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """压缩为汇编级摘要"""
        asm_info = self.extractor.extract_asm_info(resolved_ref)

        content = {
            'labels': asm_info.get('labels', []),
            'flow': asm_info.get('flow', [])
        }

        return Evidence.asm(ref, source, content)

    def _compress_summary(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """压缩为结构化语义总结 - 键值对形式"""
        items = self.extractor.extract_summary(resolved_ref)
        return Evidence.summary(ref, source, items)

    def _compress_callchain(self, ref: str, source: str, resolved_ref: ResolvedRef) -> Evidence:
        """压缩为调用路径"""
        path = self.extractor.extract_callchain(resolved_ref)
        content = {
            'path': path
        }
        return Evidence.callchain(ref, source, content)
