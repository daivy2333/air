from dataclasses import dataclass
from typing import Literal, Optional, List, Dict, Any

@dataclass
class Evidence:
    """表示 PCES 中的一个 <evidence> 响应"""
    ref: str
    view: Literal['exist', 'definition', 'api', 'impl', 'asm', 'summary', 'callchain']
    source: Literal['u<ID>', 'layout', 'unknown']
    content: Dict[str, Any]

    @classmethod
    def missing(cls, ref: str, view: str, reason: str = None) -> 'Evidence':
        """创建缺失证据"""
        content = {'status': 'missing'}
        if reason:
            content['reason'] = reason
        return cls(
            ref=ref,
            view=view,
            source='unknown',
            content=content
        )

    @classmethod
    def ambiguous(cls, ref: str, view: str, candidates: List[str] = None, suggestions: List[Dict[str, str]] = None) -> 'Evidence':
        """创建多义证据"""
        content = {'status': 'ambiguous'}

        # 优先使用suggestions，因为它包含更详细的信息
        if suggestions:
            content['suggestions'] = suggestions
        elif candidates:
            content['candidates'] = candidates

        return cls(
            ref=ref,
            view=view,
            source='unknown',
            content=content
        )


    @classmethod
    def exist(cls, ref: str, source: str, exists: bool, location: str = None) -> 'Evidence':
        """创建存在性证据"""
        content = {'status': 'yes' if exists else 'no'}
        if location:
            content['location'] = location
        return cls(
            ref=ref,
            view='exist',
            source=source,
            content=content
        )

    @classmethod
    def definition(cls, ref: str, source: str, kind: str, unit: str, definition: str = None) -> 'Evidence':
        """创建定义证据"""
        content = {
            'kind': kind,
            'unit': unit
        }
        if definition:
            content['definition'] = definition
        return cls(
            ref=ref,
            view='definition',
            source=source,
            content=content
        )

    @classmethod
    def api(cls, ref: str, source: str, content: Dict[str, Any]) -> 'Evidence':
        """创建 API 证据"""
        return cls(
            ref=ref,
            view='api',
            source=source,
            content=content
        )

    @classmethod
    def impl(cls, ref: str, source: str, implementation: List[str]) -> 'Evidence':
        """创建实现详情证据"""
        return cls(
            ref=ref,
            view='impl',
            source=source,
            content={
                'implementation': implementation
            }
        )

    @classmethod
    def asm(cls, ref: str, source: str, content: Dict[str, Any]) -> 'Evidence':
        """创建汇编证据"""
        return cls(
            ref=ref,
            view='asm',
            source=source,
            content=content
        )

    @classmethod
    def summary(cls, ref: str, source: str, items: Dict[str, str]) -> 'Evidence':
        """创建摘要证据"""
        return cls(
            ref=ref,
            view='summary',
            source=source,
            content=items
        )

    @classmethod
    def callchain(cls, ref: str, source: str, content: Dict[str, Any]) -> 'Evidence':
        """创建调用链证据"""
        return cls(
            ref=ref,
            view='callchain',
            source=source,
            content=content
        )
