import re
from typing import List
from models.need import Need

class PCRParser:
    """PCR 文档解析器"""

    def __init__(self):
        self.need_pattern = re.compile(
            r'<need>\s*type:\s*(\w+)\s*ref:\s*(\S+)\s*view:\s*(\w+)\s*</need>',
            re.MULTILINE
        )

    def parse(self, pcr_text: str) -> List[Need]:
        """
        解析 PCR 文本，返回 Need 列表

        Args:
            pcr_text: PCR 文本内容

        Returns:
            Need 对象列表，顺序与 PCR 中 <need> 顺序一致
        """
        needs = []

        # 提取 <pcr> 标签内容
        pcr_match = re.search(r'<pcr>(.*?)</pcr>', pcr_text, re.DOTALL)
        if not pcr_match:
            return needs

        pcr_content = pcr_match.group(1)

        # 匹配所有 <need> 标签
        matches = self.need_pattern.finditer(pcr_content)

        for match in matches:
            need_type = match.group(1)
            ref = match.group(2)
            view = match.group(3)

            # 验证类型
            valid_types = ['unit', 'symbol', 'layout', 'entry']
            if need_type not in valid_types:
                continue

            # 验证 view
            valid_views = ['exist', 'definition', 'api', 'impl', 'asm', 'summary', 'callchain']
            if view not in valid_views:
                continue

            needs.append(Need(type=need_type, ref=ref, view=view))

        return needs

    def validate(self, pcr_text: str) -> bool:
        """
        验证 PCR 文本格式是否正确

        Args:
            pcr_text: PCR 文本内容

        Returns:
            是否格式正确
        """
        # 检查基本标签结构
        if '<pcr>' not in pcr_text or '</pcr>' not in pcr_text:
            return False

        # 检查是否包含至少一个 <need>
        if '<need>' not in pcr_text or '</need>' not in pcr_text:
            return False

        # 尝试解析
        needs = self.parse(pcr_text)
        return len(needs) > 0
