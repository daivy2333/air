import re
import os
from .base import BaseAnalyzer
from ..core.project_model import ProjectModel

class AsmLdAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, unit_uid: str, model: ProjectModel):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".ld" or ext == ".lds":
            self._analyze_ld(file_path, unit_uid, model)
        else:
            self._analyze_asm(file_path, unit_uid, model)

    # ------------------------
    # ASM
    # ------------------------
    _re_preproc = re.compile(r'^\s*#\s*(?:\d+|line\b)', re.IGNORECASE)

    # 更“通用”的 label：允许 . $ _，但排除纯数字与 .L*（局部/临时）
    _re_label = re.compile(r'^\s*([A-Za-z_.$][\w.$]*):\s*(?:[#;@/].*)?$')
    _re_local_numeric_label = re.compile(r'^\s*(\d+):')
    _re_local_tmp_label = re.compile(r'^\s*(\.L[\w.$]*):')

    # 指令抓取：尽量通用多架构
    # 形如：
    #   call foo
    #   bl foo
    #   b foo
    #   j foo / jmp foo
    #   jal ra, foo / jal x1, foo / jal foo
    #   bne x1, x2, foo
    #   beqz x1, foo
    # 只抓“最后一个操作数像符号”的情况
    _re_branch_or_call = re.compile(
        r'^\s*(?P<op>'
        r'call|bl|blr|jal|jalr|jsr|bsr|jmp|j|b|bra|br|'
        r'beq|bne|bgt|bge|blt|ble|beqz|bnez|cbz|cbnz'
        r')\b'
        r'(?P<args>.*)$',
        re.IGNORECASE
    )

    # 从参数串里提取一个“看起来像符号”的目标（尽量不误抓寄存器/立即数）
    _re_symbol_operand = re.compile(r'([A-Za-z_.$][\w.$]*)')

    def _strip_inline_comment(self, s: str) -> str:
        """
        去掉行内注释（尽量通用但保守）：
        - ';' '@' '//' 常见注释起始
        - '#' 只在它前面是空白时当注释（避免立即数 '#1' 这种）
        """
        # 先处理 // 注释
        s = re.split(r'//', s, maxsplit=1)[0]

        # ; 或 @ 注释
        s = re.split(r'[;@]', s, maxsplit=1)[0]

        # '#' 注释：仅当前面是空白或行首
        m = re.search(r'(^|\s)#', s)
        if m:
            s = s[:m.start()].rstrip()
        return s.strip()

    def _analyze_asm(self, file_path: str, unit_uid: str, model: ProjectModel):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for raw in f:
                    if not raw.strip():
                        continue
                    # 跳过预处理行（# 1 "file" 之类）
                    if self._re_preproc.match(raw):
                        continue

                    line = self._strip_inline_comment(raw)
                    if not line:
                        continue

                    # 过滤局部/临时 label： 1: 2: 以及 .Lxxx:
                    if self._re_local_numeric_label.match(line):
                        continue
                    if self._re_local_tmp_label.match(line):
                        continue

                    # 提取 label
                    m_label = self._re_label.match(line)
                    if m_label:
                        name = m_label.group(1)
                        model.add_symbol(name, unit_uid, "label")
                        continue  # label 行通常不同时是指令行

                    # 提取 branch/call（尽量通用）
                    m = self._re_branch_or_call.match(line)
                    if not m:
                        continue

                    op = m.group("op").lower()
                    args = m.group("args").strip()
                    if not args:
                        continue

                    # 提取“目标符号”：通常是最后一个像符号的 token
                    # 例如：bne x1, x2, target  / jal ra, target
                    # 我们抓所有 symbol-like operand，取最后一个
                    syms = self._re_symbol_operand.findall(args)
                    if not syms:
                        continue
                    target = syms[-1]

                    # 极少数情况下会误抓到寄存器名（如 ra/x1/sp）
                    # 做一个保守过滤：常见寄存器名列表
                    if target.lower() in {
                        "ra","sp","gp","tp","fp","pc",
                        "x0","x1","x2","x3","x4","x5","x6","x7","x8","x9",
                        "x10","x11","x12","x13","x14","x15","x16","x17","x18","x19",
                        "x20","x21","x22","x23","x24","x25","x26","x27","x28","x29","x30","x31",
                        "lr"
                    }:
                        continue

                    # 仍然用你现有的 verb 集合：统一记为 call（你说“已经能用”且要通用）
                    model.add_dependency(unit_uid, "call", f"[{target}]")

        except Exception as e:
            print(f"Warning: ASM analysis failed: {e}")

    # ------------------------
    # LD
    # ------------------------
    def _analyze_ld(self, file_path: str, unit_uid: str, model: ProjectModel):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 1) ENTRY(symbol)
            entry_match = re.search(r'ENTRY\s*\(\s*([A-Za-z_.$][\w.$]*)\s*\)', content)
            if entry_match:
                entry_sym = entry_match.group(1)
                model.layout_lines.append(f"ENTRY={entry_sym}")
                model.add_symbol(entry_sym, unit_uid, "ld_entry")

            # 2) BASE: . = 0x80000000;
            base_match = re.search(r'\.\s*=\s*(0x[0-9a-fA-F]+|\d+)\s*;', content)
            if base_match:
                model.layout_lines.append(f"BASE={base_match.group(1)}")

            # 3) Sections: 收集常见段名（findall，避免只匹配一次）
            sections = re.findall(r'^\s*(\.[A-Za-z_][\w.]*)\s*:\s*(?:[^{\n]*\{)?', content, flags=re.MULTILINE)
            # 去掉常见伪匹配（太短/不是段）
            sections = [s for s in sections if s.startswith(".")]
            if sections:
                # 稳定输出：去重并排序
                uniq = sorted(set(sections))
                model.layout_lines.append(f"SECTIONS={','.join(uniq)}")
                model.layout_lines.append(f"SECTIONS_FROM={unit_uid}")

            # 4) 常见 ld 符号定义：
            # PROVIDE(SYM = .); 或 PROVIDE(SYM = expr);
            for sym in re.findall(r'PROVIDE\s*\(\s*([A-Za-z_.$][\w.$]*)\s*=', content):
                model.add_symbol(sym, unit_uid, "ld_symbol")

            # SYM = .; / SYM = expr;
            for sym in re.findall(r'^\s*([A-Za-z_.$][\w.$]*)\s*=\s*\.\s*;', content, flags=re.MULTILINE):
                model.add_symbol(sym, unit_uid, "ld_symbol")

        except Exception as e:
            print(f"Warning: Linker script analysis failed: {e}")
