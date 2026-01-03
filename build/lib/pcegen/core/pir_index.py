import json
from typing import Dict, List, Optional

class PIRIndex:
    """PIR 索引 - 用于快速查找 PIR 中的信息"""

    def __init__(self, pir_data: Dict):
        """
        初始化 PIR 索引

        Args:
            pir_data: PIR 数据字典
        """
        self.pir_data = pir_data
        self._build_indexes()

    def _build_indexes(self):
        """构建各种索引以加速查找"""
        # unit 索引: unit_id -> unit
        self.unit_index: Dict[str, Dict] = {}
        for unit in self.pir_data.get('units', []):
            self.unit_index[unit.get('id')] = unit

        # 符号索引: symbol_name -> [unit_ids]
        self.symbol_index: Dict[str, List[str]] = {}
        for unit in self.pir_data.get('units', []):
            unit_id = unit.get('id')
            for symbol in unit.get('symbols', []):
                symbol_name = symbol.get('name')
                if symbol_name:
                    if symbol_name not in self.symbol_index:
                        self.symbol_index[symbol_name] = []
                    self.symbol_index[symbol_name].append(unit_id)

        # entry 符号索引
        self.entry_symbols: List[str] = []
        for unit in self.pir_data.get('units', []):
            unit_id = unit.get('id')
            for symbol in unit.get('symbols', []):
                if symbol.get('entry', False):
                    self.entry_symbols.append(f"{unit_id}#{symbol.get('name')}")

        # layout 索引
        self.layout_index = self.pir_data.get('layout', {})

    @classmethod
    def from_file(cls, pir_file: str) -> 'PIRIndex':
        """
        从文件加载 PIR 并构建索引

        Args:
            pir_file: PIR 文件路径

        Returns:
            PIRIndex 实例
        """
        from .pir_parser import PIRParser
        
        with open(pir_file, 'r', encoding='utf-8') as f:
            pir_text = f.read()
        
        parser = PIRParser()
        pir_data = parser.parse(pir_text)
        return cls(pir_data)

    @classmethod
    def from_dict(cls, pir_data: Dict) -> 'PIRIndex':
        """
        从字典构建 PIR 索引

        Args:
            pir_data: PIR 数据字典

        Returns:
            PIRIndex 实例
        """
        return cls(pir_data)

    def get_unit(self, unit_id: str) -> Optional[Dict]:
        """
        获取 unit 信息

        Args:
            unit_id: unit ID

        Returns:
            unit 信息字典，如果不存在则返回 None
        """
        return self.unit_index.get(unit_id)

    def get_symbol_units(self, symbol_name: str) -> List[str]:
        """
        获取包含指定符号的所有 unit ID

        Args:
            symbol_name: 符号名

        Returns:
            unit ID 列表
        """
        return self.symbol_index.get(symbol_name, [])

    def get_entry_symbols(self) -> List[str]:
        """
        获取所有 entry 符号

        Returns:
            entry 符号列表，格式为 u<ID>#<symbol>
        """
        return self.entry_symbols

    def get_layout_sections(self) -> List[str]:
        """
        获取所有 layout 段名

        Returns:
            段名列表
        """
        return list(self.layout_index.keys())

    def get_layout_info(self, section_name: str) -> Optional[Dict]:
        """
        获取 layout 段信息

        Args:
            section_name: 段名

        Returns:
            段信息字典，如果不存在则返回 None
        """
        return self.layout_index.get(section_name)

    def get_pir_data(self) -> Dict:
        """
        获取原始 PIR 数据

        Returns:
            PIR 数据字典
        """
        return self.pir_data
