import re
from pathlib import Path
from typing import Optional

class LanguageDetector:
    """语言检测器 - 根据文件扩展名和内容自动识别语言"""

    # 文件扩展名到语言的映射
    EXTENSION_MAP = {
        '.py': 'python',
        '.pyx': 'python',
        '.c': 'c',
        '.h': 'c',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.hpp': 'cpp',
        '.hxx': 'cpp',
        '.rs': 'rust',
        '.s': 'asm',
        '.S': 'asm',
        '.asm': 'asm',
        '.ld': 'ld',
        '.lds': 'ld',
    }

    # 语言特征模式
    LANGUAGE_PATTERNS = {
        'python': [
            r'^(def|class|import|from)\s+',
            r'@\w+\s*\(',
            r'if\s+.*:',
            r'for\s+.*in\s+.*:',
        ],
        'c': [
            r'^#include\s*["<]',
            r'^\s*(int|char|void|float|double)\s+\w+\s*\(',
            r'^\s*(typedef|struct|enum|union)\s+\w+',
        ],
        'cpp': [
            r'^#include\s*["<]',
            r'^\s*(class|template|namespace)\s+\w+',
            r'std::\w+',
            r'\b(new|delete)\s+',
            r'->\s*\w+',
        ],
        'rust': [
            r'^\s*(use|mod|fn|struct|enum|impl|trait)\s+',
            r'\blet\s+\w+\s*=',
            r'fn\s+\w+\s*\(',
            r'impl\s+\w+\s+for\s+\w+',
        ],
        'asm': [
            r'^\s*[A-Za-z_][\w.]*\s*:',
            r'^\s*(mov|add|sub|jmp|call|ret)\s+',
            r'\.(section|globl|text|data|bss)',
        ],
    }

    @classmethod
    def detect_from_path(cls, file_path: str) -> Optional[str]:
        """
        根据文件路径检测语言

        Args:
            file_path: 文件路径

        Returns:
            语言标识符（python, c, cpp, rust, asm, ld）
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        # 首先根据扩展名判断
        if ext in cls.EXTENSION_MAP:
            return cls.EXTENSION_MAP[ext]

        return None

    @classmethod
    def detect_from_content(cls, content: str, file_path: Optional[str] = None) -> Optional[str]:
        """
        根据内容检测语言

        Args:
            content: 源代码内容
            file_path: 可选的文件路径（用于扩展名检测）

        Returns:
            语言标识符
        """
        # 如果提供了文件路径，先尝试从扩展名检测
        if file_path:
            lang = cls.detect_from_path(file_path)
            if lang:
                return lang

        # 根据内容特征检测
        scores = {}
        lines = content.split('\n')[:50]  # 只检查前50行

        for lang, patterns in cls.LANGUAGE_PATTERNS.items():
            score = 0
            for line in lines:
                for pattern in patterns:
                    if re.search(pattern, line):
                        score += 1
            scores[lang] = score

        # 返回得分最高的语言
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        return None

    @classmethod
    def get_analyzer_class(cls, language: str) -> str:
        """
        获取语言对应的分析器类名

        Args:
            language: 语言标识符

        Returns:
            分析器类名
        """
        analyzer_map = {
            'python': 'PythonAnalyzer',
            'c': 'CAnalyzer',
            'cpp': 'CppAnalyzer',
            'rust': 'RustAnalyzer',
            'asm': 'ASMAnalyzer',
            'ld': 'LDAnalyzer',
        }
        return analyzer_map.get(language, 'PythonAnalyzer')
