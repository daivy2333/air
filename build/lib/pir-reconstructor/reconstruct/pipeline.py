from pir_reconstructor.reconstruct.structure import StructureLayer
from pir_reconstructor.reconstruct.interface import InterfaceLayer
from pir_reconstructor.reconstruct.relations import RelationLayer
from pir_reconstructor.reconstruct.documentation import DocumentationLayer
from pir_reconstructor.reconstruct.audit import AuditLayer
from pir_reconstructor.reconstruct.enrichment import SourceEnrichmentLayer
from pir_reconstructor.errors import ReconstructionError

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
