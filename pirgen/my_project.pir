<pir>
<meta>
name: my_project
root: /home/daivy/projects/air/pirgen
profile: generic
lang: PY
</meta>
<units>
u0: min_token.py type=PY role=lib module=pirgen
u1: pirgen.py type=PY role=lib module=pirgen
u2: analyzers/c_analyzer.py type=PY role=lib module=analyzers
u3: analyzers/rust_analyzer.py type=PY role=lib module=analyzers
u4: analyzers/java_analyzer.py type=PY role=lib module=analyzers
u5: analyzers/base.py type=PY role=lib module=analyzers
u6: analyzers/asm_ld_analyzer.py type=PY role=lib module=analyzers
u7: analyzers/__init__.py type=PY role=lib module=analyzers
u8: analyzers/python_analyzer.py type=PY role=lib module=analyzers
u9: core/project_model.py type=PY role=lib module=core
u10: core/pir_builder.py type=PY role=lib module=core
</units>
<dependency-pool>
d0: import:[abc]
d1: import:[analyzers]
d2: import:[argparse]
d3: import:[asm_ld_analyzer]
d4: import:[ast]
d5: import:[base]
d6: import:[c_analyzer]
d7: import:[core.pir_builder]
d8: import:[core.project_model]
d9: import:[dataclasses]
d10: import:[java_analyzer]
d11: import:[os]
d12: import:[project_model]
d13: import:[python_analyzer]
d14: import:[re]
d15: import:[rust_analyzer]
d16: import:[sys]
d17: import:[typing]
</dependency-pool>
<dependencies>
u0->refs:[d11 d16 d2 d14 d4]
u1->refs:[d11 d2 d8 d7 d1]
u2->refs:[d14 d5 d8]
u3->refs:[d14 d5 d8]
u4->refs:[d14 d5 d8]
u5->refs:[d0 d8]
u6->refs:[d14 d11 d5 d8]
u7->refs:[d6 d13 d10 d15 d3]
u8->refs:[d4 d11 d5 d8]
u9->refs:[d9 d17]
u10->refs:[d12]
</dependencies>
<symbols>
is_source_file:u0 func
strip_c_comments:u0 func
minify_c_style:u0 func
minify_python:u0 func
process_directory:u0 func
main:u0 func entry=true
replacer:u0 func
scan_project:u1 func
resolve_dependencies:u1 func
main:u1 func entry=true
CAnalyzer:u2 class
analyze:u2 func
RustAnalyzer:u3 class
analyze:u3 func
JavaAnalyzer:u4 class
analyze:u4 func
BaseAnalyzer:u5 class
analyze:u5 func
AsmLdAnalyzer:u6 class
analyze:u6 func
_analyze_asm:u6 func
_analyze_ld:u6 func
get_analyzer:u7 func
PythonAnalyzer:u8 class
analyze:u8 func
Unit:u9 class
Symbol:u9 class
Dependency:u9 class
ProjectModel:u9 class
__init__:u9 func
add_unit:u9 func
add_symbol:u9 func
finalize_dependencies:u9 func
add_dependency:u9 func
get_uid_by_path:u9 func
PIRBuilder:u10 class
__init__:u10 func
build:u10 func
_build_meta:u10 func
_build_units:u10 func
_build_dependency_pool:u10 func
_build_dependencies:u10 func
_build_symbols:u10 func
_build_layout:u10 func
_build_snippets:u10 func
</symbols>
</pir>