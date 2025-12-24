from .structure import StructureLayer
from .interface import InterfaceLayer
from .relations import RelationLayer
from .documentation import DocumentationLayer
from .audit import AuditLayer
from .enrichment import SourceEnrichmentLayer
from ..errors import ReconstructionError

class ReconstructionPipeline:

    def __init__(self, pir_ast, output_dir, project_root=None):
        self.pir = pir_ast
        self.output = output_dir
        self.project_root = project_root

    def run(self):
        try:
            SourceEnrichmentLayer(self.pir, self.project_root).run()
            StructureLayer(self.pir, self.output).run()
            InterfaceLayer(self.pir, self.output).run()
            RelationLayer(self.pir, self.output).run()
            DocumentationLayer(self.pir, self.output).run()
            AuditLayer(self.pir, self.output).run()
        except ReconstructionError:
            raise
