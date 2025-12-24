<pir>
<meta>
name: pir_reconstructor
root: /home/daivy/projects/air/pir_reconstructor
profile: generic
lang: PY
</meta>
<units>
u0: errors.py type=PY role=lib module=pir_reconstructor
u1: cli.py type=PY role=lib module=pir_reconstructor
u2: __init__.py type=PY role=lib module=pir_reconstructor
u3: pir/validator.py type=PY role=lib module=pir
u4: pir/__init__.py type=PY role=lib module=pir
u5: pir/parser.py type=PY role=lib module=pir
u6: pir/model.py type=PY role=lib module=pir
u7: templates/java.py type=PY role=lib module=templates
u8: templates/python.py type=PY role=lib module=templates
u9: templates/__init__.py type=PY role=lib module=templates
u10: templates/common.py type=PY role=lib module=templates
u11: templates/c.py type=PY role=lib module=templates
u12: reconstruct/interface.py type=PY role=lib module=reconstruct
u13: reconstruct/relations.py type=PY role=lib module=reconstruct
u14: reconstruct/__init__.py type=PY role=lib module=reconstruct
u15: reconstruct/documentation.py type=PY role=lib module=reconstruct
u16: reconstruct/enrichment.py type=PY role=lib module=reconstruct
u17: reconstruct/pipeline.py type=PY role=lib module=reconstruct
u18: reconstruct/audit.py type=PY role=lib module=reconstruct
u19: reconstruct/structure.py type=PY role=lib module=reconstruct
u20: writers/filesystem.py type=PY role=lib module=writers
u21: writers/graphviz.py type=PY role=lib module=writers
u22: writers/graphviz_pipeline.py type=PY role=lib module=writers
u23: writers/graphviz_module.py type=PY role=lib module=writers
u24: writers/mermaid.py type=PY role=lib module=writers
u25: writers/__init__.py type=PY role=lib module=writers
u26: writers/graphviz_pipeline_old.py type=PY role=lib module=writers
u27: writers/graphviz_arch.py type=PY role=lib module=writers
u28: writers/plantuml.py type=PY role=lib module=writers
u29: utils/constants.py type=PY role=lib module=utils
u30: utils/hash.py type=PY role=lib module=utils
u31: utils/ordering.py type=PY role=lib module=utils
u32: utils/__init__.py type=PY role=lib module=utils
</units>
<dependency-pool>
d0: import:[..errors]
d1: import:[..pir.model]
d2: import:[..templates.python]
d3: import:[..utils.constants]
d4: import:[..utils.hash]
d5: import:[..writers.graphviz]
d6: import:[..writers.graphviz_arch]
d7: import:[..writers.graphviz_module]
d8: import:[..writers.graphviz_pipeline]
d9: import:[..writers.mermaid]
d10: import:[..writers.plantuml]
d11: import:[.audit]
d12: import:[.documentation]
d13: import:[.enrichment]
d14: import:[.errors]
d15: import:[.interface]
d16: import:[.model]
d17: import:[.pir.parser]
d18: import:[.pir.validator]
d19: import:[.reconstruct.pipeline]
d20: import:[.relations]
d21: import:[.structure]
d22: import:[pir.model]
d23: import:[stdlib:py]
</dependency-pool>
<dependencies>
u1->refs:[d23 d17 d18 d19 d14]
u3->refs:[d23 d16]
u5->refs:[d23 d16]
u6->refs:[d23]
u12->refs:[d23 d2]
u13->refs:[d23 d6 d7 d8 d9 d5 d10]
u15->refs:[d23]
u16->refs:[d23 d1]
u17->refs:[d21 d15 d20 d12 d11 d13 d0]
u18->refs:[d23 d4 d3]
u19->refs:[d23 d0]
u20->refs:[d23]
u30->refs:[d23]
u31->refs:[d23 d22]
</dependencies>
<symbols>
ReconstructionError:u0 class
ValidationError:u0 class
ParserError:u0 class
LayerError:u0 class
main:u1 func entry=true
ValidationError:u3 class
validate_pir:u3 func
parse_pir:u5 func
Unit:u6 class
Symbol:u6 class
Dependency:u6 class
DependencyEdge:u6 class
PIRAST:u6 class
java_method_template:u7 func
java_class_template:u7 func
python_func_template:u8 func
python_class_template:u8 func
format_attributes:u10 func
generate_pir_comment:u10 func
generate_todo_comment:u10 func
c_func_template:u11 func
c_struct_template:u11 func
InterfaceLayer:u12 class
RelationLayer:u13 class
DocumentationLayer:u15 class
SourceEnrichmentLayer:u16 class
ReconstructionPipeline:u17 class
AuditLayer:u18 class
StructureLayer:u19 class
FileSystemWriter:u20 class
emit_graphviz:u21 func
emit_pipeline_graph:u22 func
emit_module_graph:u23 func
emit_mermaid:u24 func
emit_arch_graph:u27 func
emit_plantuml:u28 func
hash_tree:u30 func
topological_sort:u31 func
stable_sort_by_uid:u31 func
</symbols>
</pir>