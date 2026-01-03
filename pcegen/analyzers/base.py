from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class BaseAnalyzer(ABC):
    """分析器基类"""

    def __init__(self, source_code: str, pir_data: Dict):
        """
        初始化分析器

        Args:
            source_code: 源代码文本
            pir_data: PIR 数据
        """
        self.source_code = source_code
        self.pir_data = pir_data

    @abstractmethod
    def extract_signature(self, symbol_name: str) -> Optional[str]:
        """
        提取符号签名

        Args:
            symbol_name: 符号名

        Returns:
            签名字符串，如果不存在则返回 None
        """
        pass

    @abstractmethod
    def extract_implementation(self, symbol_name: str) -> List[str]:
        """
        提取实现逻辑

        Args:
            symbol_name: 符号名

        Returns:
            实现详情列表
        """
        pass

    def extract_class(self, class_name: str) -> Optional[str]:
        """
        提取类定义（可选实现）

        Args:
            class_name: 类名

        Returns:
            完整的类定义代码，如果不支持则返回 None
        """
        return None

    def extract_struct(self, source_code: str, struct_name: str) -> Optional[str]:
        """
        提取结构体定义（可选实现）

        Args:
            source_code: 源代码
            struct_name: 结构体名

        Returns:
            完整的结构体定义代码，如果不支持则返回 None
        """
        return None

    def extract_header_symbols(self) -> List[Dict]:
        """
        提取头文件中的符号（可选实现）

        Args:
            无

        Returns:
            符号列表，每个符号包含name和kind
        """
        return []

    @abstractmethod
    def extract_behavior(self, symbol_name: str) -> List[str]:
        """
        提取行为描述

        Args:
            symbol_name: 符号名

        Returns:
            行为描述列表，每条不超过一行
        """
        pass

    @abstractmethod
    def extract_callchain(self, symbol_name: str) -> List[str]:
        """
        提取调用链

        Args:
            symbol_name: 符号名

        Returns:
            调用路径列表，格式为 u<ID>#symbol
        """
        pass

    @abstractmethod
    def extract_asm_info(self, symbol_name: str) -> Dict:
        """
        提取汇编信息

        Args:
            symbol_name: 符号名

        Returns:
            包含 labels 和 flow 的字典
        """
        pass


