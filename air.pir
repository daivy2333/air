<pir>
<meta>
name: air
root: /home/daivy/projects/air
profile: generic
lang: PY
</meta>
<units>
u0: out_app.py type=PY role=lib module=air
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
u15: pir_reconstructor/errors.py type=PY role=lib module=pir_reconstructor
u16: pir_reconstructor/cli.py type=PY role=lib module=pir_reconstructor
u17: pir_reconstructor/__init__.py type=PY role=lib module=pir_reconstructor
u18: pir_reconstructor/pir/validator.py type=PY role=lib module=pir
u19: pir_reconstructor/pir/__init__.py type=PY role=lib module=pir
u20: pir_reconstructor/pir/parser.py type=PY role=lib module=pir
u21: pir_reconstructor/pir/model.py type=PY role=lib module=pir
u22: pir_reconstructor/templates/java.py type=PY role=lib module=templates
u23: pir_reconstructor/templates/python.py type=PY role=lib module=templates
u24: pir_reconstructor/templates/__init__.py type=PY role=lib module=templates
u25: pir_reconstructor/templates/common.py type=PY role=lib module=templates
u26: pir_reconstructor/templates/c.py type=PY role=lib module=templates
u27: pir_reconstructor/reconstruct/interface.py type=PY role=lib module=reconstruct
u28: pir_reconstructor/reconstruct/relations.py type=PY role=lib module=reconstruct
u29: pir_reconstructor/reconstruct/__init__.py type=PY role=lib module=reconstruct
u30: pir_reconstructor/reconstruct/documentation.py type=PY role=lib module=reconstruct
u31: pir_reconstructor/reconstruct/enrichment.py type=PY role=lib module=reconstruct
u32: pir_reconstructor/reconstruct/pipeline.py type=PY role=lib module=reconstruct
u33: pir_reconstructor/reconstruct/audit.py type=PY role=lib module=reconstruct
u34: pir_reconstructor/reconstruct/structure.py type=PY role=lib module=reconstruct
u35: pir_reconstructor/writers/filesystem.py type=PY role=lib module=writers
u36: pir_reconstructor/writers/graphviz.py type=PY role=lib module=writers
u37: pir_reconstructor/writers/graphviz_pipeline.py type=PY role=lib module=writers
u38: pir_reconstructor/writers/graphviz_module.py type=PY role=lib module=writers
u39: pir_reconstructor/writers/mermaid.py type=PY role=lib module=writers
u40: pir_reconstructor/writers/__init__.py type=PY role=lib module=writers
u41: pir_reconstructor/writers/graphviz_pipeline_old.py type=PY role=lib module=writers
u42: pir_reconstructor/writers/graphviz_arch.py type=PY role=lib module=writers
u43: pir_reconstructor/writers/plantuml.py type=PY role=lib module=writers
u44: pir_reconstructor/utils/constants.py type=PY role=lib module=utils
u45: pir_reconstructor/utils/hash.py type=PY role=lib module=utils
u46: pir_reconstructor/utils/ordering.py type=PY role=lib module=utils
u47: pir_reconstructor/utils/__init__.py type=PY role=lib module=utils
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
d0: import:[..core.project_model]
d1: import:[..errors]
d2: import:[..pir.model]
d3: import:[..templates.python]
d4: import:[..utils.constants]
d5: import:[..utils.hash]
d6: import:[..writers.graphviz]
d7: import:[..writers.graphviz_arch]
d8: import:[..writers.graphviz_module]
d9: import:[..writers.graphviz_pipeline]
d10: import:[..writers.mermaid]
d11: import:[..writers.plantuml]
d12: import:[.analyzers]
d13: import:[.app]
d14: import:[.asm_ld_analyzer]
d15: import:[.audit]
d16: import:[.base]
d17: import:[.c_analyzer]
d18: import:[.core.analysis_cache]
d19: import:[.core.dep_canon]
d20: import:[.core.pir_builder]
d21: import:[.core.profile_canon]
d22: import:[.core.project_model]
d23: import:[.documentation]
d24: import:[.enrichment]
d25: import:[.errors]
d26: import:[.interface]
d27: import:[.java_analyzer]
d28: import:[.model]
d29: import:[.pir.parser]
d30: import:[.pir.validator]
d31: import:[.pirgen]
d32: import:[.project_model]
d33: import:[.python_analyzer]
d34: import:[.reconstruct.pipeline]
d35: import:[.relations]
d36: import:[.rust_analyzer]
d37: import:[.structure]
d38: import:[air.services.forward]
d39: import:[air.services.reverse]
d40: import:[analyzers]
d41: import:[core.dep_canon]
d42: import:[core.pir_builder]
d43: import:[core.profile_canon]
d44: import:[core.project_model]
d45: import:[errors]
d46: import:[forward]
d47: import:[pir.model]
d48: import:[pir.parser]
d49: import:[pir.validator]
d50: import:[pir_reconstructor.errors]
d51: import:[pir_reconstructor.pir.parser]
d52: import:[pir_reconstructor.pir.validator]
d53: import:[pir_reconstructor.reconstruct.pipeline]
d54: import:[pirgen.analyzers]
d55: import:[pirgen.core.dep_canon]
d56: import:[pirgen.core.pir_builder]
d57: import:[pirgen.core.profile_canon]
d58: import:[pirgen.core.project_model]
d59: import:[pirgen]
d60: import:[reconstruct.pipeline]
d61: import:[reverse]
d62: import:[stdlib:py]
</dependency-pool>
<dependencies>
u0->refs:[d62 d46 d61]
u16->refs:[d62 d29 d30 d34 d25]
u18->refs:[d62 d28]
u20->refs:[d62 d28]
u21->refs:[d62]
u27->refs:[d62 d3]
u28->refs:[d62 d7 d8 d9 d10 d6 d11]
u30->refs:[d62]
u31->refs:[d62 d2]
u32->refs:[d37 d26 d35 d23 d15 d24 d1]
u33->refs:[d62 d5 d4]
u34->refs:[d62 d1]
u35->refs:[d62]
u45->refs:[d62]
u46->refs:[d62 d47]
u48->refs:[d62 d38 d39]
u49->refs:[d13]
u52->refs:[d62 d58 d56 d55 d57 d54 d59]
u53->refs:[d62 d51 d52 d53 d50]
u55->refs:[d62]
u56->refs:[d62]
u57->refs:[d62]
u58->refs:[d62]
u59->refs:[d62 d44 d42 d41 d43 d40]
u60->refs:[d62 d48 d49 d60 d45]
u61->refs:[d31]
u62->refs:[d62]
u63->refs:[d62 d22 d20 d19 d21 d18 d12]
u64->refs:[d62 d16 d0]
u65->refs:[d62 d16 d0]
u66->refs:[d62 d16 d0]
u67->refs:[d62 d0]
u68->refs:[d62 d16 d0]
u69->refs:[d17 d33 d27 d36 d14]
u70->refs:[d62 d16 d0]
u71->refs:[d62]
u73->refs:[d62]
u74->refs:[d62]
u75->refs:[d32]
u77->refs:[d62]
u78->refs:[d62]
u79->refs:[d62]
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