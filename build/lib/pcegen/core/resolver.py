import re
from typing import Optional, Dict, List
from models.need import Need
from models.resolved_ref import ResolvedRef

class Resolver:
    """引用解析器 - 将 PCR ref 解析为 ResolvedRef"""

    def __init__(self, pir_data: Dict):
        """
        初始化解析器

        Args:
            pir_data: PIR 数据字典，包含 units, symbols, layout 等信息
        """
        self.pir_data = pir_data
        self._build_indexes()

    def _build_indexes(self):
        """构建索引以加速查找"""
        # 符号索引: symbol -> [unit_ids]
        self.symbol_index: Dict[str, List[str]] = {}

        # 全局唯一符号索引
        self.unique_symbols: Dict[str, str] = {}

        # entry 符号索引
        self.entry_symbols: List[str] = []

        # layout 段名索引
        self.layout_sections: List[str] = []

        # 构建符号索引
        for unit in self.pir_data.get('units', []):
            unit_id = unit.get('id')
            for symbol in unit.get('symbols', []):
                symbol_name = symbol.get('name')
                if symbol_name:
                    if symbol_name not in self.symbol_index:
                        self.symbol_index[symbol_name] = []
                    self.symbol_index[symbol_name].append(unit_id)

                    # 记录 entry 符号
                    if symbol.get('entry', False):
                        self.entry_symbols.append(f"{unit_id}#{symbol_name}")

        # 找出全局唯一符号
        for symbol_name, unit_ids in self.symbol_index.items():
            if len(unit_ids) == 1:
                self.unique_symbols[symbol_name] = unit_ids[0]

        # 构建 layout 索引
        layout = self.pir_data.get('layout', {})
        self.layout_sections = list(layout.keys())

    def resolve(self, need: Need) -> ResolvedRef:
        """
        解析引用，按照 PCR 规范的解析顺序

        解析顺序（冻结）:
        1. u<ID>#<symbol>
        2. u<ID>
        3. layout 段名
        4. symbols 中 entry=true
        5. symbols 中全局唯一符号名

        Args:
            need: Need 对象

        Returns:
            ResolvedRef 对象
        """
        ref = need.ref
        ref_type = need.type

        # 1. 尝试解析 u<ID>#<symbol>
        if '#' in ref:
            parts = ref.split('#', 1)
            unit_id = parts[0]
            symbol_name = parts[1] if len(parts) > 1 else None

            # 验证 unit_id 是否存在
            unit = self._find_unit(unit_id)
            if unit:
                if symbol_name:
                    # 验证符号是否在该 unit 中
                    if self._symbol_in_unit(symbol_name, unit_id):
                        return ResolvedRef(
                            kind='symbol',
                            unit_id=unit_id,
                            symbol=symbol_name,
                            path=unit.get('path')
                        )
                    else:
                        # 符号不在该 unit 中
                        return ResolvedRef(kind='symbol', unit_id=None, symbol=None, path=None)
                else:
                    # 只有 unit_id，没有 symbol
                    return ResolvedRef(
                        kind='unit',
                        unit_id=unit_id,
                        symbol=None,
                        path=unit.get('path')
                    )

        # 2. 尝试解析 u<ID>
        if ref.startswith('u'):
            unit = self._find_unit(ref)
            if unit:
                return ResolvedRef(
                    kind='unit',
                    unit_id=ref,
                    symbol=None,
                    path=unit.get('path')
                )

        # 3. 尝试解析 layout 段名
        if ref_type == 'layout' or ref in self.layout_sections:
            if ref in self.layout_sections:
                return ResolvedRef(
                    kind='layout',
                    unit_id=None,
                    symbol=ref,
                    path=None
                )

        # 4. 尝试在 entry 符号中查找
        # entry符号优先于全局唯一符号，确保正确解析入口点
        if ref_type == 'entry' or ref in [e.split('#')[1] for e in self.entry_symbols]:
            # 查找所有 entry=true 的符号
            matching_entries = []
            for entry_ref in self.entry_symbols:
                if entry_ref.endswith(f'#{ref}'):
                    matching_entries.append(entry_ref)

            if len(matching_entries) == 0:
                # 没有找到entry符号，继续后续查找
                pass
            elif len(matching_entries) == 1:
                # 找到唯一的entry符号
                unit_id = matching_entries[0].split('#')[0]
                unit = self._find_unit(unit_id)
                return ResolvedRef(
                    kind='symbol',
                    unit_id=unit_id,
                    symbol=ref,
                    path=unit.get('path') if unit else None
                )
            else:
                # 多个entry，返回ambiguous并提供建议
                suggestions = []
                for entry_ref in matching_entries:
                    unit_id = entry_ref.split('#')[0]
                    unit = self._find_unit(unit_id)
                    if unit:
                        suggestions.append({
                            'ref': entry_ref,
                            'desc': f"entry in {unit.get('language', '')} ({unit.get('path', '')})"
                        })
                return ResolvedRef(
                    kind='symbol',
                    unit_id=None,
                    symbol=ref,
                    path=None,
                    suggestions=suggestions
                )

        # 5. 尝试在全局唯一符号中查找
        if ref in self.unique_symbols:
            unit_id = self.unique_symbols[ref]
            unit = self._find_unit(unit_id)
            return ResolvedRef(
                kind='symbol',
                unit_id=unit_id,
                symbol=ref,
                path=unit.get('path') if unit else None
            )

        # 6. 尝试在所有符号中查找
        if ref in self.symbol_index:
            unit_ids = self.symbol_index[ref]
            if len(unit_ids) > 1:
                # 多义，提供详细建议
                suggestions = []
                for unit_id in unit_ids:
                    unit = self._find_unit(unit_id)
                    if unit:
                        # 查找符号的详细信息
                        symbol_info = None
                        for symbol in unit.get('symbols', []):
                            if symbol.get('name') == ref:
                                symbol_info = symbol
                                break

                        if symbol_info:
                            kind = symbol_info.get('kind', '')
                            is_entry = symbol_info.get('entry', False)
                            desc_parts = [kind]
                            if is_entry:
                                desc_parts.append('entry')
                            desc_parts.append(f"in {unit.get('language', '')}")

                            suggestions.append({
                                'ref': f"{unit_id}#{ref}",
                                'desc': ' '.join(desc_parts)
                            })

                return ResolvedRef(
                    kind='symbol',
                    unit_id=None,
                    symbol=ref,
                    path=None,
                    suggestions=suggestions
                )
            else:
                unit_id = unit_ids[0]
                unit = self._find_unit(unit_id)
                return ResolvedRef(
                    kind='symbol',
                    unit_id=unit_id,
                    symbol=ref,
                    path=unit.get('path') if unit else None
                )

        # 未找到
        return ResolvedRef(kind='symbol', unit_id=None, symbol=None, path=None)




    def _find_unit(self, unit_id: str) -> Optional[Dict]:
        """根据 unit_id 查找 unit"""
        for unit in self.pir_data.get('units', []):
            if unit.get('id') == unit_id:
                return unit
        return None

    def _symbol_in_unit(self, symbol_name: str, unit_id: str) -> bool:
        """检查符号是否在指定 unit 中"""
        unit = self._find_unit(unit_id)
        if not unit:
            return False

        for symbol in unit.get('symbols', []):
            if symbol.get('name') == symbol_name:
                return True
        return False
