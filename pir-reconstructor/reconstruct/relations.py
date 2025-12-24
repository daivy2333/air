from pathlib import Path
from writers.graphviz_arch import emit_arch_graph
from writers.graphviz_module import emit_module_graph
from writers.graphviz_pipeline import emit_pipeline_graph
from writers.mermaid import emit_mermaid
from writers.graphviz import emit_graphviz
from writers.plantuml import emit_plantuml

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
