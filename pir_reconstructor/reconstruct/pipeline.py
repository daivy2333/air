from typing import List
from .structure import StructureLayer
from .interface import InterfaceLayer
from .relations import RelationLayer
from .documentation import DocumentationLayer
from .audit import AuditLayer
from .enrichment import (
    BaseEnrichmentLayer,
    PythonEnrichmentLayer,
    CEnrichmentLayer,
    RustEnrichmentLayer,
    JavaEnrichmentLayer,
    ASMEnrichmentLayer,
    LDEnrichmentLayer,
)
from ..errors import ReconstructionError


class ReconstructionPipeline:
    def __init__(self, pir_ast, output_dir, project_root=None):
        self.pir = pir_ast
        self.output = output_dir
        self.project_root = project_root

    def _get_enrichment_layers(self) -> List[BaseEnrichmentLayer]:
        """获取适用于项目的 enrichment 层"""
        layers = []
        lang_types = {unit.type for unit in self.pir.units}

        # 语言映射到 enrichment 层
        lang_map = {
            'PY': PythonEnrichmentLayer,
            'C': CEnrichmentLayer,
            'CPP': CEnrichmentLayer,
            'RUST': RustEnrichmentLayer,
            'JAVA': JavaEnrichmentLayer,
            'ASM': ASMEnrichmentLayer,
            'S': ASMEnrichmentLayer,
            'LD': LDEnrichmentLayer
        }

        for lang_type, layer_class in lang_map.items():
            if lang_type in lang_types:
                layers.append(layer_class(self.pir, self.project_root))

        return layers

    def run(self):
        """运行重建管道"""
        try:
            print("开始 PIR 重建...")

            # Enrichment 阶段
            print("1. 分析源文件...")
            for i, layer in enumerate(self._get_enrichment_layers(), 1):
                print(f"   处理 {layer.__class__.__name__}...")
                layer.run()

            # Structure 阶段
            print("2. 创建目录结构...")
            StructureLayer(self.pir, self.output).run()

            # Interface 阶段
            print("3. 生成代码接口...")
            InterfaceLayer(self.pir, self.output).run()

            # Relations 阶段
            print("4. 分析依赖关系...")
            RelationLayer(self.pir, self.output).run()

            # Documentation 阶段
            print("5. 生成文档...")
            DocumentationLayer(self.pir, self.output).run()

            # Audit 阶段
            print("6. 审计结果...")
            AuditLayer(self.pir, self.output).run()

            print("✅ 重建完成！")

        except ReconstructionError as e:
            print(f"❌ 重建失败: {e}")
            raise
