from reconstruct.structure import StructureLayer
from reconstruct.interface import InterfaceLayer
from reconstruct.relations import RelationLayer
from reconstruct.documentation import DocumentationLayer
from reconstruct.audit import AuditLayer
from reconstruct.enrichment import SourceEnrichmentLayer
from errors import ReconstructionError

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
