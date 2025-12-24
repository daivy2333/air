<pir>
<meta>
name: my_project
root: /home/daivy/projects/air
profile: generic
lang: PY
</meta>
<units>
u0: app.py type=PY role=lib module=air
u1: re/src/min_token.py type=PY role=lib module=src
u2: re/src/pirgen.py type=PY role=lib module=src
u3: re/src/analyzers/c_analyzer.py type=PY role=lib module=analyzers
u4: re/src/analyzers/rust_analyzer.py type=PY role=lib module=analyzers
u5: re/src/analyzers/java_analyzer.py type=PY role=lib module=analyzers
u6: re/src/analyzers/base.py type=PY role=lib module=analyzers
u7: re/src/analyzers/asm_ld_analyzer.py type=PY role=lib module=analyzers
u8: re/src/analyzers/__init__.py type=PY role=lib module=analyzers
u9: re/src/analyzers/python_analyzer.py type=PY role=lib module=analyzers
u10: re/src/core/profile_canon.py type=PY role=lib module=core
u11: re/src/core/analysis_cache.py type=PY role=lib module=core
u12: re/src/core/project_model.py type=PY role=lib module=core
u13: re/src/core/pir_builder.py type=PY role=lib module=core
u14: re/src/core/dep_canon.py type=PY role=lib module=core
u15: pir-reconstructor/errors.py type=PY role=lib module=pir-reconstructor
u16: pir-reconstructor/cli.py type=PY role=lib module=pir-reconstructor
u17: pir-reconstructor/__init__.py type=PY role=lib module=pir-reconstructor
u18: pir-reconstructor/pir/validator.py type=PY role=lib module=pir
u19: pir-reconstructor/pir/__init__.py type=PY role=lib module=pir
u20: pir-reconstructor/pir/parser.py type=PY role=lib module=pir
u21: pir-reconstructor/pir/model.py type=PY role=lib module=pir
u22: pir-reconstructor/templates/java.py type=PY role=lib module=templates
u23: pir-reconstructor/templates/python.py type=PY role=lib module=templates
u24: pir-reconstructor/templates/__init__.py type=PY role=lib module=templates
u25: pir-reconstructor/templates/common.py type=PY role=lib module=templates
u26: pir-reconstructor/templates/c.py type=PY role=lib module=templates
u27: pir-reconstructor/reconstruct/interface.py type=PY role=lib module=reconstruct
u28: pir-reconstructor/reconstruct/relations.py type=PY role=lib module=reconstruct
u29: pir-reconstructor/reconstruct/__init__.py type=PY role=lib module=reconstruct
u30: pir-reconstructor/reconstruct/documentation.py type=PY role=lib module=reconstruct
u31: pir-reconstructor/reconstruct/enrichment.py type=PY role=lib module=reconstruct
u32: pir-reconstructor/reconstruct/pipeline.py type=PY role=lib module=reconstruct
u33: pir-reconstructor/reconstruct/audit.py type=PY role=lib module=reconstruct
u34: pir-reconstructor/reconstruct/structure.py type=PY role=lib module=reconstruct
u35: pir-reconstructor/writers/filesystem.py type=PY role=lib module=writers
u36: pir-reconstructor/writers/graphviz.py type=PY role=lib module=writers
u37: pir-reconstructor/writers/graphviz_pipeline.py type=PY role=lib module=writers
u38: pir-reconstructor/writers/graphviz_module.py type=PY role=lib module=writers
u39: pir-reconstructor/writers/mermaid.py type=PY role=lib module=writers
u40: pir-reconstructor/writers/__init__.py type=PY role=lib module=writers
u41: pir-reconstructor/writers/graphviz_pipeline_old.py type=PY role=lib module=writers
u42: pir-reconstructor/writers/graphviz_arch.py type=PY role=lib module=writers
u43: pir-reconstructor/writers/plantuml.py type=PY role=lib module=writers
u44: pir-reconstructor/utils/constants.py type=PY role=lib module=utils
u45: pir-reconstructor/utils/hash.py type=PY role=lib module=utils
u46: pir-reconstructor/utils/ordering.py type=PY role=lib module=utils
u47: pir-reconstructor/utils/__init__.py type=PY role=lib module=utils
u48: air/app.py type=PY role=lib module=air
u49: air/__main__.py type=PY role=lib module=air
u50: air/__init__.py type=PY role=lib module=air
u51: air/services/__init__.py type=PY role=lib module=services
u52: air/services/forward.py type=PY role=lib module=services
u53: air/services/reverse.py type=PY role=lib module=services
u54: 初版/canon_config1.py type=PY role=lib module=初版
u55: 初版/normal.py type=PY role=lib module=初版
u56: 初版/d_3.py type=PY role=lib module=初版
u57: 初版/os.py type=PY role=lib module=初版
u58: 初版/d.py type=PY role=lib module=初版
u59: services/forward.py type=PY role=lib module=services
u60: services/reverse.py type=PY role=lib module=services
u61: pirgen/__init__.py type=PY role=lib module=pirgen
u62: pirgen/min_token.py type=PY role=lib module=pirgen
u63: pirgen/pirgen.py type=PY role=lib module=pirgen
u64: pirgen/analyzers/c_analyzer.py type=PY role=lib module=analyzers
u65: pirgen/analyzers/rust_analyzer.py type=PY role=lib module=analyzers
u66: pirgen/analyzers/java_analyzer.py type=PY role=lib module=analyzers
u67: pirgen/analyzers/base.py type=PY role=lib module=analyzers
u68: pirgen/analyzers/asm_ld_analyzer.py type=PY role=lib module=analyzers
u69: pirgen/analyzers/__init__.py type=PY role=lib module=analyzers
u70: pirgen/analyzers/python_analyzer.py type=PY role=lib module=analyzers
u71: pirgen/core/profile_canon.py type=PY role=lib module=core
u72: pirgen/core/__init__.py type=PY role=lib module=core
u73: pirgen/core/analysis_cache.py type=PY role=lib module=core
u74: pirgen/core/project_model.py type=PY role=lib module=core
u75: pirgen/core/pir_builder.py type=PY role=lib module=core
u76: pirgen/core/dep_canon.py type=PY role=lib module=core
u77: ir规范/os.py type=PY role=lib module=ir规范
u78: ir规范/os2.py type=PY role=lib module=ir规范
u79: ir规范/pirgen.py type=PY role=lib module=ir规范
</units>
<dependency-pool>
d0: import:[.app]
d1: import:[.asm_ld_analyzer]
d2: import:[.base]
d3: import:[.c_analyzer]
d4: import:[.java_analyzer]
d5: import:[.project_model]
d6: import:[.python_analyzer]
d7: import:[.rust_analyzer]
d8: import:[air.services.forward]
d9: import:[air.services.reverse]
d10: import:[analyzers]
d11: import:[core.analysis_cache]
d12: import:[core.dep_canon]
d13: import:[core.pir_builder]
d14: import:[core.profile_canon]
d15: import:[core.project_model]
d16: import:[errors]
d17: import:[forward]
d18: import:[pir.model]
d19: import:[pir.parser]
d20: import:[pir.validator]
d21: import:[pirgen.analyzers]
d22: import:[pirgen.core.dep_canon]
d23: import:[pirgen.core.pir_builder]
d24: import:[pirgen.core.profile_canon]
d25: import:[pirgen.core.project_model]
d26: import:[pirgen.pirgen]
d27: import:[reconstruct.audit]
d28: import:[reconstruct.documentation]
d29: import:[reconstruct.enrichment]
d30: import:[reconstruct.interface]
d31: import:[reconstruct.pipeline]
d32: import:[reconstruct.relations]
d33: import:[reconstruct.structure]
d34: import:[reverse]
d35: import:[stdlib:py]
d36: import:[templates.python]
d37: import:[utils.constants]
d38: import:[utils.hash]
d39: import:[writers.graphviz]
d40: import:[writers.graphviz_arch]
d41: import:[writers.graphviz_module]
d42: import:[writers.graphviz_pipeline]
d43: import:[writers.mermaid]
d44: import:[writers.plantuml]
</dependency-pool>
<dependencies>
u0->refs:[d35 d17 d34]
u16->refs:[d35 d19 d20 d31 d16]
u18->refs:[d35 d18]
u20->refs:[d35 d18]
u21->refs:[d35]
u27->refs:[d35 d36]
u28->refs:[d35 d40 d41 d42 d43 d39 d44]
u30->refs:[d35]
u31->refs:[d35 d18]
u32->refs:[d33 d30 d32 d28 d27 d29 d16]
u33->refs:[d35 d38 d37]
u34->refs:[d35 d16]
u35->refs:[d35]
u45->refs:[d35]
u46->refs:[d35 d18]
u48->refs:[d35 d8 d9]
u49->refs:[d0]
u52->refs:[d35 d25 d23 d22 d24 d21 d26]
u53->refs:[d35 d19 d20 d31 d16]
u55->refs:[d35]
u56->refs:[d35]
u57->refs:[d35]
u58->refs:[d35]
u59->refs:[d35 d15 d13 d12 d14 d10]
u60->refs:[d35 d19 d20 d31 d16]
u62->refs:[d35]
u63->refs:[d35 d15 d13 d12 d14 d11 d10]
u64->refs:[d35 d2 d15]
u65->refs:[d35 d2 d15]
u66->refs:[d35 d2 d15]
u67->refs:[d35 d15]
u68->refs:[d35 d2 d15]
u69->refs:[d3 d6 d4 d7 d1]
u70->refs:[d35 d2 d15]
u71->refs:[d35]
u73->refs:[d35]
u74->refs:[d35]
u75->refs:[d5]
u77->refs:[d35]
u78->refs:[d35]
u79->refs:[d35]
</dependencies>
<symbols>
main:u0 func entry=true
ReconstructionError:u15 class
ValidationError:u15 class
ParserError:u15 class
LayerError:u15 class
main:u16 func entry=true
ValidationError:u18 class
validate_pir:u18 func
parse_pir:u20 func
Unit:u21 class
Symbol:u21 class
Dependency:u21 class
DependencyEdge:u21 class
PIRAST:u21 class
java_method_template:u22 func
java_class_template:u22 func
python_func_template:u23 func
python_class_template:u23 func
format_attributes:u25 func
generate_pir_comment:u25 func
generate_todo_comment:u25 func
c_func_template:u26 func
c_struct_template:u26 func
InterfaceLayer:u27 class
RelationLayer:u28 class
DocumentationLayer:u30 class
SourceEnrichmentLayer:u31 class
ReconstructionPipeline:u32 class
AuditLayer:u33 class
StructureLayer:u34 class
FileSystemWriter:u35 class
emit_graphviz:u36 func
emit_pipeline_graph:u37 func
emit_module_graph:u38 func
emit_mermaid:u39 func
emit_arch_graph:u42 func
emit_plantuml:u43 func
hash_tree:u45 func
topological_sort:u46 func
stable_sort_by_uid:u46 func
main:u48 func entry=true
run_forward:u52 func
run_reverse:u53 func
CanonicalizationConfig:u54 class
ProjectPacker:u55 class
main:u55 func entry=true
classify:u56 func
strip_comments:u56 func
minify_c:u56 func
parse_funcs:u56 func
parse_includes:u56 func
main:u56 func entry=true
classify:u57 func
strip_c_comments:u57 func
minify_c:u57 func
minify_ld:u57 func
minify_asm:u57 func
parse_funcs:u57 func
parse_includes:u57 func
main:u57 func entry=true
is_binary_file:u58 func
remove_comments:u58 func
process_directory:u58 func
main:u58 func entry=true
run_forward:u59 func
run_reverse:u60 func
is_source_file:u62 func
strip_c_comments:u62 func
minify_c_style:u62 func
minify_python:u62 func
process_directory:u62 func
main:u62 func entry=true
discover_source_files:u63 func
infer_unit_meta:u63 func
scan_project:u63 func
resolve_dependencies:u63 func
main:u63 func entry=true
CAnalyzer:u64 class
RustAnalyzer:u65 class
JavaAnalyzer:u66 class
BaseAnalyzer:u67 class
AsmLdAnalyzer:u68 class
get_analyzer:u69 func
PythonAnalyzer:u70 class
ProfileCanonicalizer:u71 class
AnalysisCache:u73 class
Unit:u74 class
Symbol:u74 class
Dependency:u74 class
ProjectModel:u74 class
PIRBuilder:u75 class
canonicalize_target:u76 func
canonicalize_dependencies:u76 func
classify:u77 func
strip_c_comments:u77 func
minify_c:u77 func
minify_asm:u77 func
parse_funcs:u77 func
parse_includes:u77 func
parse_ld:u77 func
main:u77 func entry=true
classify:u78 func
strip_c_comments:u78 func
minify_c:u78 func
minify_asm:u78 func
parse_funcs:u78 func
parse_includes:u78 func
parse_ld:u78 func
main:u78 func entry=true
detect_lang:u79 func
walk:u79 func
main:u79 func entry=true
</symbols>
<profiles>
  active: python-framework
  python-framework:
    confidence: 0.8
    tags:
      - domain:language-tooling
      - runtime:cpython
      - stack:python-framework
    signals:
      - layered-architecture
      - multi-module
      - semantic-classes
</profiles>
</pir>