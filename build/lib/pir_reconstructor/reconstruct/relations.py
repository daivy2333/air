from pathlib import Path
from typing import List, Dict, Set
from ..writers.graphviz_arch import emit_arch_graph
from ..writers.graphviz_module import emit_module_graph
from ..writers.graphviz_pipeline import emit_pipeline_graph
from ..writers.mermaid import emit_mermaid
from ..writers.graphviz import emit_graphviz
from ..writers.plantuml import emit_plantuml
from .layout import extract_memory_layout

class RelationLayer:

    def __init__(self, pir, output):
        self.pir = pir
        self.edges = pir.edges
        self.units = pir.units
        self.output = Path(output)

    def run(self):
        # Create diagrams directory
        diagrams_dir = self.output / "diagrams"
        diagrams_dir.mkdir(parents=True, exist_ok=True)

        # Generate Architecture Graph (default, main, most important)
        arch_content = emit_arch_graph(self.pir)
        (diagrams_dir / "architecture.dot").write_text(arch_content)

        # Generate Module/Import Graph (local analysis)
        module_content = emit_module_graph(self.pir)
        (diagrams_dir / "modules.dot").write_text(module_content)

        # Generate Pipeline/Flow Graph (very valuable for this project)
        pipeline_content = emit_pipeline_graph(self.pir)
        (diagrams_dir / "pipeline.dot").write_text(pipeline_content)

        # Generate Mermaid diagram (legacy, for compatibility)
        mermaid_content = emit_mermaid(self.edges, self.units)
        (diagrams_dir / "dependencies.mmd").write_text(mermaid_content)

        # Generate PlantUML diagram (legacy, for compatibility)
        plantuml_content = emit_plantuml(self.edges, self.units)
        (diagrams_dir / "dependencies.puml").write_text(plantuml_content)

        # Generate RISC-V specific diagrams if detected
        if self._is_riscv_project():
            self._generate_riscv_diagrams(diagrams_dir)

    def _is_riscv_project(self) -> bool:
        """检测是否为 RISC-V 项目"""
        # 检查是否有 RISC-V 特定的符号
        riscv_symbols = {'_start', 'trap_vector', 'trap_entry', 'irq_handler'}
        found = any(sym.name in riscv_symbols for sym in self.pir.symbols)

        # 检查是否有 RISC-V 特定的依赖
        has_riscv_deps = any(
            edge.dep_kind == 'syscall' or 
            edge.module == 'kernel'
            for edge in self.pir.edges
        )

        # 检查是否有 RISC-V 特定的单位路径
        has_riscv_paths = any(
            'riscv' in unit.path.lower() or 
            unit.path.endswith('.ld')
            for unit in self.pir.units
        )

        return found or has_riscv_deps or has_riscv_paths

    def _generate_riscv_diagrams(self, diagrams_dir: Path):
        """生成 RISC-V 特定的图表"""
        # 生成内存布局图
        memory_layout = extract_memory_layout(self.pir)
        memory_graph = self._generate_memory_layout_graph(memory_layout)
        (diagrams_dir / "memory_layout.dot").write_text(memory_graph)

        # 生成系统调用流程图
        syscall_graph = self._generate_syscall_flow_graph()
        (diagrams_dir / "syscall_flow.dot").write_text(syscall_graph)

    def _generate_memory_layout_graph(self, layout: Dict) -> str:
        """生成内存布局的 Graphviz 图"""
        lines = [
            'digraph MemoryLayout {',
            '    rankdir=TB;',
            '    node [shape=record, style=filled, fillcolor=lightblue];',
            '',
            '    // Memory Regions',
        ]

        # 添加内存区域
        if 'regions' in layout:
            for name, region in layout['regions'].items():
                lines.append(f'    {name} [label="{{{name}|Origin: {region.origin}|Length: {region.length}}}"];')

        lines.append('')
        lines.append('    // Sections')

        # 添加段
        if 'sections' in layout:
            for section in layout['sections']:
                lines.append(f'    {section.replace(".", "_")} [label="{section}", shape=box];')

        lines.append('')
        lines.append('    // Entry Point')

        if layout.get('entry_point'):
            lines.append(f"    entry [label=\"Entry: {layout['entry_point']}\", shape=ellipse, color=red];")

        lines.append('}')

        return '\n'.join(lines)

    def _generate_syscall_flow_graph(self) -> str:
        """生成系统调用流程的 Graphviz 图"""
        lines = [
            'digraph SyscallFlow {',
            '    rankdir=TB;',
            '    node [shape=box, style=filled, fillcolor=lightyellow];',
            '',
            '    // System Call Flow',
            '    user_app [label="User Application"];',
            '    ecall [label="ECALL Instruction", shape=ellipse, color=red];',
            '    trap_handler [label="Trap Handler"];',
            '    syscall_dispatch [label="Syscall Dispatcher"];',
            '    syscall_table [label="Syscall Table"];',
            '    syscall_impl [label="Syscall Implementation"];',
            '    kernel_return [label="Return to User"];',
            '',
            '    // Flow edges',
            '    user_app -> ecall [label="make syscall"];',
            '    ecall -> trap_handler [label="trap"];',
            '    trap_handler -> syscall_dispatch [label="analyze cause"];',
            '    syscall_dispatch -> syscall_table [label="lookup syscall"];',
            '    syscall_table -> syscall_impl [label="call handler"];',
            '    syscall_impl -> kernel_return [label="result"];',
            '    kernel_return -> user_app [label="mret/sret"];',
            '',
            '    // Styling',
            '    {rank=same; user_app; ecall;}',
            '    {rank=same; trap_handler; syscall_dispatch;}',
            '    {rank=same; syscall_table; syscall_impl;}',
            '}'
        ]

        return '\n'.join(lines)
