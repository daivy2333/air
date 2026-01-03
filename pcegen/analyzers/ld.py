import re
from typing import Dict, List, Optional
from analyzers.base import BaseAnalyzer

class LDAnalyzer(BaseAnalyzer):
    """链接器脚本分析器"""

    # 段定义正则
    SECTION_PATTERN = re.compile(
        r'\.'
        r'(?P<name>\w+)\s*'
        r'(?:\(\s*(?P<flags>[^)]*)\s*\))?'
        r'\s*:\s*'
        r'(?:\{(?P<content>[^}]*)\})?'
    )

    # 符号定义正则
    SYMBOL_PATTERN = re.compile(
        r'(?P<name>\w+)\s*=\s*(?P<value>[^;]+);'
    )

    # 内存区域正则
    MEMORY_PATTERN = re.compile(
        r'MEMORY\s*\{([^}]+)\}'
    )

    # 内存区域定义正则
    REGION_PATTERN = re.compile(
        r'(\w+)\s*\(([^)]*)\)\s*:\s*'
        r'ORIGIN\s*=\s*([^,]+)\s*,\s*'
        r'LENGTH\s*=\s*([^\s]+)'
    )

    def __init__(self, source_code: str, pir_data: Dict):
        super().__init__(source_code, pir_data)
        self._preprocess()

    def _preprocess(self):
        """预处理链接器脚本"""
        # 移除注释
        self.code = re.sub(r'/\*.*?\*/', '', self.source_code, flags=re.DOTALL)
        self.code = re.sub(r'//.*', '', self.code)

        # 按行分割
        self.lines = self.code.split('\n')

        # 构建段索引
        self.sections = {}
        # 构建符号索引
        self.symbols = {}
        # 构建内存区域索引
        self.memory_regions = {}
        # 构建段布局索引
        self.section_layouts = {}

        # 解析整个链接器脚本
        self._parse_linker_script()

    def _parse_linker_script(self):
        """解析链接器脚本，提取段布局信息"""
        # 查找 SECTIONS 块
        sections_match = re.search(r'SECTIONS\s*\{([^}]*)\}', self.code, re.DOTALL)
        if sections_match:
            sections_content = sections_match.group(1)
            self._parse_sections_block(sections_content)

        # 提取内存区域定义
        memory_match = self.MEMORY_PATTERN.search(self.code)
        if memory_match:
            self._parse_memory_regions(memory_match.group(1))

        # 提取符号定义
        for line in self.lines:
            symbol_match = self.SYMBOL_PATTERN.search(line)
            if symbol_match:
                symbol_name = symbol_match.group('name')
                symbol_value = symbol_match.group('value').strip()
                self.symbols[symbol_name] = symbol_value

    def _parse_sections_block(self, sections_content: str):
        """解析 SECTIONS 块"""
        # 查找所有段定义
        section_pattern = re.compile(
            r'\.(?P<name>\w+)\s*'
            r'(?:\(\s*(?P<flags>[^)]*)\s*\))?\s*'
            r':\s*'
            r'(?P<address>[^:]+)?\s*'
            r'\{(?P<content>[^}]*)\}'
        )

        for match in section_pattern.finditer(sections_content):
            section_name = match.group('name')
            flags = match.group('flags') or ''
            address = match.group('address') or ''
            content = match.group('content') or ''

            # 解析段属性
            section_info = {
                'name': section_name,
                'flags': self._parse_section_flags(flags),
                'content': content,
                'address': address.strip(),
                'attributes': self._extract_section_attributes(content)
            }
            self.sections[section_name] = section_info

            # 解析段布局
            layout_info = self._parse_section_layout(content)
            if layout_info:
                self.section_layouts[section_name] = layout_info

    def _parse_section_flags(self, flags_str: str) -> Dict[str, bool]:
        """解析段标志"""
        flags = {}
        if not flags_str:
            return flags

        # 常见段标志
        flag_patterns = {
            'ALLOC': 'allocatable',
            'EXEC': 'executable',
            'LOAD': 'loadable',
            'RELOC': 'relocatable',
            'READONLY': 'readonly',
            'CODE': 'code',
            'DATA': 'data',
            'ROM': 'rom'
        }

        for flag_name, flag_key in flag_patterns.items():
            if flag_name in flags_str.upper():
                flags[flag_key] = True

        return flags

    def _extract_section_attributes(self, line: str) -> Dict[str, str]:
        """提取段的其他属性"""
        attributes = {}

        # 提取对齐属性
        align_match = re.search(r'ALIGN\((\d+)\)', line)
        if align_match:
            attributes['alignment'] = align_match.group(1)

        # 提取子段对齐
        subalign_match = re.search(r'SUBALIGN\((\d+)\)', line)
        if subalign_match:
            attributes['subalignment'] = subalign_match.group(1)

        # 提取虚拟地址
        vma_match = re.search(r'AT\s*\(\s*([^)]+)\s*\)', line)
        if vma_match:
            attributes['vma'] = vma_match.group(1).strip()

        # 提取加载地址
        lma_match = re.search(r'\>([^\s]+)', line)
        if lma_match:
            attributes['lma'] = lma_match.group(1)

        return attributes

    def _parse_memory_regions(self, memory_content: str):
        """解析内存区域定义"""
        for match in self.REGION_PATTERN.finditer(memory_content):
            region_name = match.group(1)
            region_attrs = match.group(2)
            origin = match.group(3).strip()
            length = match.group(4).strip()

            self.memory_regions[region_name] = {
                'attributes': region_attrs,
                'origin': origin,
                'length': length
            }

    def extract_signature(self, symbol_name: str) -> Optional[str]:
        """提取符号签名（链接器脚本不适用）"""
        return None

    def extract_implementation(self, symbol_name: str) -> List[str]:
        """提取实现详情（链接器脚本不适用）"""
        return []

    def extract_callchain(self, symbol_name: str) -> List[str]:
        """提取调用链（链接器脚本不适用）"""
        return []

    def extract_asm_info(self, symbol_name: str) -> Dict:
        """提取汇编信息（链接器脚本不适用）"""
        return {
            'labels': [],
            'flow': []
        }

    def get_section_info(self, section_name: str) -> Optional[Dict]:
        """
        获取段信息

        Args:
            section_name: 段名

        Returns:
            段信息字典,包含完整的段属性
        """
        return self.sections.get(section_name)

    def get_all_sections(self) -> List[str]:
        """
        获取所有段名

        Returns:
            段名列表
        """
        return list(self.sections.keys())

    def get_symbol_value(self, symbol_name: str) -> Optional[str]:
        """
        获取符号值

        Args:
            symbol_name: 符号名

        Returns:
            符号值
        """
        return self.symbols.get(symbol_name)

    def get_all_symbols(self) -> Dict[str, str]:
        """
        获取所有符号定义

        Returns:
            符号字典 {name: value}
        """
        return self.symbols

    def get_memory_region(self, region_name: str) -> Optional[Dict]:
        """
        获取内存区域信息

        Args:
            region_name: 内存区域名

        Returns:
            内存区域信息字典
        """
        return self.memory_regions.get(region_name)

    def get_all_memory_regions(self) -> Dict[str, Dict]:
        """
        获取所有内存区域

        Returns:
            内存区域字典 {name: {attributes, origin, length}}
        """
        return self.memory_regions

    def get_layout_info(self) -> Dict:
        """
        获取完整的内存布局信息

        Returns:
            包含所有段和内存区域的布局信息
        """
        return {
            'sections': self.sections,
            'symbols': self.symbols,
            'memory_regions': self.memory_regions
        }
