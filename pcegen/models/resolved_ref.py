from dataclasses import dataclass
from typing import Literal, Optional, List, Dict

@dataclass
class ResolvedRef:
    """表示解析后的引用"""
    kind: Literal['unit', 'symbol', 'layout']
    unit_id: Optional[str]  # u<ID> 格式
    symbol: Optional[str]   # 符号名
    path: Optional[str]    # 源文件路径
    suggestions: Optional[List[Dict[str, str]]] = None  # ambiguous时的建议列表

    @property
    def is_missing(self) -> bool:
        return self.kind == 'symbol' and self.symbol is None

    @property
    def is_ambiguous(self) -> bool:
        # 标记为多义的情况
        return self.kind == 'symbol' and self.unit_id is None and self.symbol is not None

