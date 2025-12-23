# analyzers/asm_ld_analyzer.py
import re
import os
from .base import BaseAnalyzer
from core.project_model import ProjectModel

class AsmLdAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, unit_uid: str, model: ProjectModel):
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.ld':
            self._analyze_ld(file_path, unit_uid, model)
        else:
            self._analyze_asm(file_path, unit_uid, model)

    def _analyze_asm(self, file_path, unit_uid, model):
        """处理 .S, .asm 文件"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            
            # 汇编标签匹配 (e.g., "start_kernel:")
            label_pattern = re.compile(r'^(\w+):')
            # 调用指令匹配 (e.g., "call main", "bl main")
            call_pattern = re.compile(r'\s+(?:call|bl|b|jal)\s+(\w+)')

            for line in lines:
                line = line.strip()
                if not line or line.startswith((';', '@', '//', '#')): continue

                # 提取符号
                m_label = label_pattern.match(line)
                if m_label:
                    name = m_label.group(1)
                    model.add_symbol(name, unit_uid, "label")
                
                # 提取依赖 (Call)
                m_call = call_pattern.search(line)
                if m_call:
                    target = m_call.group(1)
                    # 暂时标记为 [target]，后续 resolve 阶段会尝试链接到具体 Unit
                    model.add_dependency(unit_uid, "call", f"[{target}]")

        except Exception as e:
            print(f"Warning: ASM analysis failed: {e}")

    def _analyze_ld(self, file_path, unit_uid, model):
        """处理 .ld 链接脚本，提取 Layout 信息"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 1. 提取入口点
            entry_match = re.search(r'ENTRY\s*\(\s*(\w+)\s*\)', content)
            if entry_match:
                entry_sym = entry_match.group(1)
                model.layout_lines.append(f"ENTRY={entry_sym}")
                # 将 Entry 记录为符号
                model.add_symbol(entry_sym, unit_uid, "ld_entry")

            # 2. 提取简单的段定义 (heuristic)
            # 查找 .text : { ... } 或 .data :
            section_pattern = re.search(r'(\.text|\.data|\.bss)\s*:[^\{]*\{', content)
            if section_pattern:
                 model.layout_lines.append(f"Sections defined in {unit_uid}")

            # 3. 提取基地址 (heuristic)
            # 查找类似 . = 0x80000000; 的赋值
            base_match = re.search(r'\.\s*=\s*(0x[0-9a-fA-F]+)', content)
            if base_match:
                model.layout_lines.append(f"BASE={base_match.group(1)}")

        except Exception as e:
            print(f"Warning: Linker script analysis failed: {e}")