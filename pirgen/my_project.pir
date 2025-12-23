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
d0: import:[.asm_ld_analyzer]
d1: import:[.base]
d2: import:[.c_analyzer]
d3: import:[.java_analyzer]
d4: import:[.project_model]
d5: import:[.python_analyzer]
d6: import:[.rust_analyzer]
d7: import:[abc]
d8: import:[analyzers]
d9: import:[argparse]
d10: import:[ast]
d11: import:[collections]
d12: import:[core.pir_builder]
d13: import:[core.project_model]
d14: import:[dataclasses]
d15: import:[os]
d16: import:[re]
d17: import:[sys]
d18: import:[typing]
</dependency-pool>
<dependencies>
u0->refs:[d15 d17 d9 d16 d10]
u1->refs:[d15 d9 d11 d13 d12 d8]
u2->refs:[d16 d1 d13]
u3->refs:[d16 d1 d13]
u4->refs:[d16 d1 d13]
u5->refs:[d7 d13]
u6->refs:[d16 d15 d1 d13]
u7->refs:[d2 d5 d3 d6 d0]
u8->refs:[d10 d15 d1 d13]
u9->refs:[d14 d18]
u10->refs:[d4]
</dependencies>
<symbols>
is_source_file:u0 func
strip_c_comments:u0 func
minify_c_style:u0 func
minify_python:u0 func
process_directory:u0 func
main:u0 func entry=true
discover_source_files:u1 func
infer_unit_meta:u1 func
scan_project:u1 func
resolve_dependencies:u1 func
main:u1 func entry=true
CAnalyzer:u2 class
RustAnalyzer:u3 class
JavaAnalyzer:u4 class
BaseAnalyzer:u5 class
AsmLdAnalyzer:u6 class
get_analyzer:u7 func
PythonAnalyzer:u8 class
Unit:u9 class
Symbol:u9 class
Dependency:u9 class
ProjectModel:u9 class
PIRBuilder:u10 class
</symbols>
</pir>