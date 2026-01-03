from typing import List
from models.evidence import Evidence

class PCESerializer:
    """PCES 文档序列化器"""

    def serialize(self, evidences: List[Evidence]) -> str:
        """
        将 Evidence 列表序列化为 PCES 文本

        Args:
            evidences: Evidence 对象列表

        Returns:
            PCES 文本
        """
        lines = ['<pcir>']

        for evidence in evidences:
            lines.append('<evidence>')
            lines.append(f'ref: {evidence.ref}')
            lines.append(f'view: {evidence.view}')
            lines.append(f'source: {evidence.source}')
            lines.append('content:')

            # 序列化 content
            for key, value in evidence.content.items():
                # 特殊处理代码内容（definition、implementation等），保持缩进
                if key in ['definition', 'implementation', 'code']:
                    lines.append(f'  {key}:')
                    for code_line in str(value).split('\n'):
                        lines.append(f'    {code_line}')
                elif isinstance(value, list):
                    lines.append(f'  {key}:')
                    for item in value:
                        lines.append(f'    - {item}')
                elif isinstance(value, dict):
                    lines.append(f'  {key}:')
                    for dict_key, dict_value in value.items():
                        lines.append(f'    {dict_key}: {dict_value}')
                else:
                    lines.append(f'  {key}: {value}')

            lines.append('</evidence>')

        lines.append('</pcir>')

        return '\n'.join(lines)

    def serialize_evidence(self, evidence: Evidence) -> str:
        """
        序列化单个 Evidence

        Args:
            evidence: Evidence 对象

        Returns:
            单个 evidence 的 PCES 文本
        """
        lines = [
            '<evidence>',
            f'ref: {evidence.ref}',
            f'view: {evidence.view}',
            f'source: {evidence.source}',
            'content:'
        ]

        # 序列化 content
        for key, value in evidence.content.items():
            # 特殊处理代码内容
            if key in ['definition', 'implementation', 'code']:
                lines.append(f'  {key}:')
                for code_line in str(value).split('\n'):
                    lines.append(f'    {code_line}')
            elif isinstance(value, list):
                lines.append(f'  {key}:')
                for item in value:
                    lines.append(f'    - {item}')
            elif isinstance(value, dict):
                lines.append(f'  {key}:')
                for dict_key, dict_value in value.items():
                    lines.append(f'    {dict_key}: {dict_value}')
            else:
                lines.append(f'  {key}: {value}')

        lines.append('</evidence>')

        return '\n'.join(lines)
