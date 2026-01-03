from dataclasses import dataclass
from typing import Literal

@dataclass
class Need:
    """表示 PCR 中的一个 <need> 请求"""
    type: Literal['unit', 'symbol', 'layout', 'entry']
    ref: str
    view: Literal['exist', 'definition', 'api', 'impl', 'asm', 'summary', 'callchain']
