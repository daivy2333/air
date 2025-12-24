<pir>
<meta>
name: pirgen
root: /home/daivy/projects/air/pirgen
profile: generic
lang: PY
</meta>
<units>
u0: __init__.py type=PY role=lib module=pirgen
u1: min_token.py type=PY role=lib module=pirgen
u2: pirgen.py type=PY role=lib module=pirgen
u3: analyzers/c_analyzer.py type=PY role=lib module=analyzers
u4: analyzers/rust_analyzer.py type=PY role=lib module=analyzers
u5: analyzers/java_analyzer.py type=PY role=lib module=analyzers
u6: analyzers/base.py type=PY role=lib module=analyzers
u7: analyzers/asm_ld_analyzer.py type=PY role=lib module=analyzers
u8: analyzers/__init__.py type=PY role=lib module=analyzers
u9: analyzers/python_analyzer.py type=PY role=lib module=analyzers
u10: core/profile_canon.py type=PY role=lib module=core
u11: core/__init__.py type=PY role=lib module=core
u12: core/analysis_cache.py type=PY role=lib module=core
u13: core/project_model.py type=PY role=lib module=core
u14: core/pir_builder.py type=PY role=lib module=core
u15: core/dep_canon.py type=PY role=lib module=core
</units>
<dependency-pool>
d0: import:[..core.project_model]
d1: import:[.analyzers]
d2: import:[.asm_ld_analyzer]
d3: import:[.base]
d4: import:[.c_analyzer]
d5: import:[.core.analysis_cache]
d6: import:[.core.dep_canon]
d7: import:[.core.pir_builder]
d8: import:[.core.profile_canon]
d9: import:[.core.project_model]
d10: import:[.java_analyzer]
d11: import:[.pirgen]
d12: import:[.project_model]
d13: import:[.python_analyzer]
d14: import:[.rust_analyzer]
d15: import:[stdlib:py]
</dependency-pool>
<dependencies>
u0->refs:[d11]
u1->refs:[d15]
u2->refs:[d15 d9 d7 d6 d8 d5 d1]
u3->refs:[d15 d3 d0]
u4->refs:[d15 d3 d0]
u5->refs:[d15 d3 d0]
u6->refs:[d15 d0]
u7->refs:[d15 d3 d0]
u8->refs:[d4 d13 d10 d14 d2]
u9->refs:[d15 d3 d0]
u10->refs:[d15]
u12->refs:[d15]
u13->refs:[d15]
u14->refs:[d12]
</dependencies>
<symbols>
is_source_file:u1 func
strip_c_comments:u1 func
minify_c_style:u1 func
minify_python:u1 func
process_directory:u1 func
main:u1 func entry=true
discover_source_files:u2 func
infer_unit_meta:u2 func
scan_project:u2 func
resolve_dependencies:u2 func
main:u2 func entry=true
CAnalyzer:u3 class
RustAnalyzer:u4 class
JavaAnalyzer:u5 class
BaseAnalyzer:u6 class
AsmLdAnalyzer:u7 class
get_analyzer:u8 func
PythonAnalyzer:u9 class
ProfileCanonicalizer:u10 class
AnalysisCache:u12 class
Unit:u13 class
Symbol:u13 class
Dependency:u13 class
ProjectModel:u13 class
PIRBuilder:u14 class
canonicalize_target:u15 func
canonicalize_dependencies:u15 func
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