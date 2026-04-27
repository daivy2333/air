"""Tests for Assembly/Linker Script analyzer.

Tests cover:
- Multi-architecture support (ARM, x86, RISC-V)
- Global and local labels
- x86 conditional jumps
- Linker script parsing
"""

import tempfile
import os
import pytest
from pirgen.analyzers.asm_ld_analyzer import AsmLdAnalyzer
from pirgen.core.project_model import ProjectModel


class TestAsmLdAnalyzer:
    def setup_method(self):
        self.analyzer = AsmLdAnalyzer()

    def _analyze_asm_file(self, content: str) -> ProjectModel:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".S", delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        model = ProjectModel("test", "/tmp", "asm")
        uid = model.add_unit(path, "ASM", "src")
        self.analyzer.analyze(path, uid, model)

        os.unlink(path)
        return model

    def _analyze_ld_file(self, content: str) -> ProjectModel:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ld", delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        model = ProjectModel("test", "/tmp", "ld")
        uid = model.add_unit(path, "LD", "src")
        self.analyzer.analyze(path, uid, model)

        os.unlink(path)
        return model


class TestAsmAnalyzer(TestAsmLdAnalyzer):
    def test_arm_basic_label(self):
        content = """
.section .text
.global _start

_start:
    mov sp, #0x4000
    bl main

main:
    push {lr}
    bl helper_func
    pop {lr}
    bx lr

helper_func:
    bx lr
"""
        model = self._analyze_asm_file(content)
        symbols = [s.name for s in model.symbols]
        
        assert "_start" in symbols
        assert "main" in symbols
        assert "helper_func" in symbols

    def test_arm_branch_instructions(self):
        content = """
func1:
    bl func2
    b func3
    beq func4
    bx lr

func2:
func3:
func4:
    bx lr
"""
        model = self._analyze_asm_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[func2]" in targets
        assert "[func3]" in targets
        assert "[func4]" in targets

    def test_arm_conditional_branch(self):
        content = """
check:
    cmp r0, #0
    beq zero_handler
    bne nonzero_handler
    bgt greater_handler
    blt less_handler

zero_handler:
nonzero_handler:
greater_handler:
less_handler:
    bx lr
"""
        model = self._analyze_asm_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[zero_handler]" in targets
        assert "[nonzero_handler]" in targets
        assert "[greater_handler]" in targets
        assert "[less_handler]" in targets

    def test_riscv_labels(self):
        content = """
.section .text
.global _start

_start:
    li sp, 0x80000000
    jal main

main:
    jal ra, helper
    ret

helper:
    jal ra, process
    ret

process:
    ret
"""
        model = self._analyze_asm_file(content)
        symbols = [s.name for s in model.symbols]
        
        assert "_start" in symbols
        assert "main" in symbols
        assert "helper" in symbols
        assert "process" in symbols

    def test_riscv_jal_instructions(self):
        content = """
entry:
    jal ra, func1
    jal func2
    jalr ra, func3
    ret

func1:
func2:
func3:
    ret
"""
        model = self._analyze_asm_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[func1]" in targets
        assert "[func2]" in targets
        assert "[func3]" in targets

    def test_riscv_conditional_branch(self):
        content = """
compare:
    beq x1, x2, equal
    bne x1, x2, different
    bgt x1, x2, greater
    blt x1, x2, less
    beqz x1, is_zero
    bnez x2, not_zero

equal:
different:
greater:
less:
is_zero:
not_zero:
    ret
"""
        model = self._analyze_asm_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[equal]" in targets
        assert "[different]" in targets
        assert "[greater]" in targets
        assert "[less]" in targets
        assert "[is_zero]" in targets
        assert "[not_zero]" in targets

    def test_x86_basic_label(self):
        content = """
.section .text
.global _start

_start:
    mov esp, 0x4000
    call main
    ret

main:
    call helper
    ret

helper:
    ret
"""
        model = self._analyze_asm_file(content)
        symbols = [s.name for s in model.symbols]
        
        assert "_start" in symbols
        assert "main" in symbols
        assert "helper" in symbols

    def test_x86_call_instructions(self):
        content = """
func:
    call func2
    jmp func3
    ret

func2:
func3:
    ret
"""
        model = self._analyze_asm_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[func2]" in targets
        assert "[func3]" in targets

    def test_x86_conditional_jumps(self):
        content = """
compare:
    cmp eax, ebx
    je equal
    jne different
    jg greater
    jl less
    jge greater_or_equal
    jle less_or_equal
    ja above
    jb below
    jz zero_flag
    jnz not_zero_flag

equal:
different:
greater:
less:
greater_or_equal:
less_or_equal:
above:
below:
zero_flag:
not_zero_flag:
    ret
"""
        model = self._analyze_asm_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[equal]" in targets
        assert "[different]" in targets
        assert "[greater]" in targets
        assert "[less]" in targets
        assert "[greater_or_equal]" in targets
        assert "[less_or_equal]" in targets
        assert "[above]" in targets
        assert "[below]" in targets

    def test_x86_loop_instructions(self):
        content = """
loop_test:
    loop loop_body
    loope loop_body
    loopne loop_body

loop_body:
    ret
"""
        model = self._analyze_asm_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[loop_body]" in targets

    def test_local_numeric_label_filtered(self):
        content = """
func:
1:
    mov eax, 1
    jmp 1b
2:
    mov eax, 2
    jmp 2f
    ret
"""
        model = self._analyze_asm_file(content)
        symbols = [s.name for s in model.symbols]
        
        assert "1" not in symbols
        assert "2" not in symbols
        assert "func" in symbols

    def test_local_tmp_label_filtered(self):
        content = """
func:
.Ltmp1:
    mov eax, 1
.Ltmp2:
    mov eax, 2
.LCFI0:
    ret
"""
        model = self._analyze_asm_file(content)
        symbols = [s.name for s in model.symbols]
        
        assert ".Ltmp1" not in symbols
        assert ".Ltmp2" not in symbols
        assert ".LCFI0" not in symbols
        assert "func" in symbols

    def test_label_with_special_chars(self):
        content = """
global_func:
.local_func:
$special_label:
_mixed_label:
    ret
"""
        model = self._analyze_asm_file(content)
        symbols = [s.name for s in model.symbols]
        
        assert "global_func" in symbols
        assert ".local_func" in symbols
        assert "$special_label" in symbols
        assert "_mixed_label" in symbols

    def test_preprocessor_line_skipped(self):
        content = """
# 1 "test.S"
# 2 "test.S" 1

real_func:
    ret
"""
        model = self._analyze_asm_file(content)
        symbols = [s.name for s in model.symbols]
        assert "real_func" in symbols

    def test_inline_comment_handling(self):
        content = """
func1:  // This is a comment
    call func2  ; semicolon comment
    call func3  @ ARM comment
    call func4  # hash comment
    ret

func2:
func3:
func4:
    ret
"""
        model = self._analyze_asm_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[func2]" in targets
        assert "[func3]" in targets
        assert "[func4]" in targets

    def test_register_filtering(self):
        content = """
func:
    call ra    # Should be filtered (RISC-V return address)
    call sp    # Should be filtered (stack pointer)
    call eax   # Should be filtered (x86 register)
    call real_func
    ret

real_func:
    ret
"""
        model = self._analyze_asm_file(content)
        model.finalize_dependencies()
        
        dep_items = model.dep_pool_items
        targets = [d[2] for d in dep_items]
        
        assert "[ra]" not in targets
        assert "[sp]" not in targets
        assert "[eax]" not in targets
        assert "[real_func]" in targets

    def test_empty_file(self):
        content = ""
        model = self._analyze_asm_file(content)
        assert len(model.symbols) == 0

    def test_only_comments(self):
        content = """
# This is a comment
// Another comment
; ARM comment
"""
        model = self._analyze_asm_file(content)
        assert len(model.symbols) == 0


class TestLdAnalyzer(TestAsmLdAnalyzer):
    def test_entry_symbol(self):
        content = """
ENTRY(_start)

SECTIONS
{
    . = 0x80000000;
}
"""
        model = self._analyze_ld_file(content)
        
        entry_syms = [s for s in model.symbols if s.kind == "ld_entry"]
        assert len(entry_syms) == 1
        assert entry_syms[0].name == "_start"
        
        assert "ENTRY=_start" in model.layout_lines

    def test_base_address(self):
        content = """
. = 0x80000000;
"""
        model = self._analyze_ld_file(content)
        assert "BASE=0x80000000" in model.layout_lines

    def test_base_address_decimal(self):
        content = """
. = 1048576;
"""
        model = self._analyze_ld_file(content)
        assert "BASE=1048576" in model.layout_lines

    def test_sections(self):
        content = """
SECTIONS
{
    .text : { *(.text) }
    .data : { *(.data) }
    .bss : { *(.bss) }
}
"""
        model = self._analyze_ld_file(content)
        
        assert any("SECTIONS=" in line for line in model.layout_lines)
        assert ".text" in model.layout_lines[0]
        assert ".data" in model.layout_lines[0]
        assert ".bss" in model.layout_lines[0]

    def test_provide_symbol(self):
        content = """
PROVIDE(__stack_top = .);
PROVIDE(__heap_start = .);
"""
        model = self._analyze_ld_file(content)
        
        provide_syms = [s for s in model.symbols if s.kind == "ld_symbol"]
        sym_names = [s.name for s in provide_syms]
        
        assert "__stack_top" in sym_names
        assert "__heap_start" in sym_names

    def test_symbol_assignment(self):
        content = """
__bss_start = .;
__end = .;
"""
        model = self._analyze_ld_file(content)
        
        ld_syms = [s for s in model.symbols if s.kind == "ld_symbol"]
        sym_names = [s.name for s in ld_syms]
        
        assert "__bss_start" in sym_names
        assert "__end" in sym_names

    def test_complex_linker_script(self):
        content = """
ENTRY(main)

. = 0x10000;

SECTIONS
{
    .text : { *(.text*) }
    .rodata : { *(.rodata*) }
    .data : { *(.data*) }
    .bss : { *(.bss*) }
}

PROVIDE(__text_start = .);
PROVIDE(__data_end = .);

__heap_base = .;
"""
        model = self._analyze_ld_file(content)
        
        entry_syms = [s for s in model.symbols if s.kind == "ld_entry"]
        assert len(entry_syms) == 1
        assert entry_syms[0].name == "main"
        
        assert "ENTRY=main" in model.layout_lines
        assert "BASE=0x10000" in model.layout_lines
        assert any("SECTIONS=" in line for line in model.layout_lines)

    def test_empty_linker_script(self):
        content = ""
        model = self._analyze_ld_file(content)
        assert len(model.symbols) == 0

    def test_lds_extension(self):
        content = """
ENTRY(start)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".lds", delete=False) as f:
            f.write(content)
            f.flush()
            path = f.name

        model = ProjectModel("test", "/tmp", "ld")
        uid = model.add_unit(path, "LD", "src")
        self.analyzer.analyze(path, uid, model)

        os.unlink(path)
        
        entry_syms = [s for s in model.symbols if s.kind == "ld_entry"]
        assert len(entry_syms) == 1