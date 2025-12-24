<pir>
<meta>
name: my_project
root: /home/aidlux/air/pirgen
profile: generic
lang: PY
</meta>
<units>
u0: pirgen.py type=PY role=lib module=pirgen
u1: min_token.py type=PY role=lib module=pirgen
u2: core/pir_builder.py type=PY role=lib module=core
u3: core/project_model.py type=PY role=lib module=core
u4: core/analysis_cache.py type=PY role=lib module=core
u5: core/dep_canon.py type=PY role=lib module=core
u6: core/profile_canon.py type=PY role=lib module=core
u7: analyzers/base.py type=PY role=lib module=analyzers
u8: analyzers/c_analyzer.py type=PY role=lib module=analyzers
u9: analyzers/rust_analyzer.py type=PY role=lib module=analyzers
u10: analyzers/java_analyzer.py type=PY role=lib module=analyzers
u11: analyzers/python_analyzer.py type=PY role=lib module=analyzers
u12: analyzers/asm_ld_analyzer.py type=PY role=lib module=analyzers
u13: analyzers/__init__.py type=PY role=lib module=analyzers
</units>
<dependency-pool>
d0: import:[.asm_ld_analyzer]
d1: import:[.base]
d2: import:[.c_analyzer]
d3: import:[.java_analyzer]
d4: import:[.project_model]
d5: import:[.python_analyzer]
d6: import:[.rust_analyzer]
d7: import:[analyzers]
d8: import:[core.analysis_cache]
d9: import:[core.dep_canon]
d10: import:[core.pir_builder]
d11: import:[core.profile_canon]
d12: import:[core.project_model]
d13: import:[stdlib:py]
</dependency-pool>
<dependencies>
u0->refs:[d13 d12 d10 d9 d11 d8 d7]
u1->refs:[d13]
u2->refs:[d4]
u3->refs:[d13]
u4->refs:[d13]
u6->refs:[d13]
u7->refs:[d13 d12]
u8->refs:[d13 d1 d12]
u9->refs:[d13 d1 d12]
u10->refs:[d13 d1 d12]
u11->refs:[d13 d1 d12]
u12->refs:[d13 d1 d12]
u13->refs:[d2 d5 d3 d6 d0]
</dependencies>
<symbols>
discover_source_files:u0 func
infer_unit_meta:u0 func
scan_project:u0 func
resolve_dependencies:u0 func
main:u0 func entry=true
is_source_file:u1 func
strip_c_comments:u1 func
minify_c_style:u1 func
minify_python:u1 func
process_directory:u1 func
main:u1 func entry=true
PIRBuilder:u2 class
Unit:u3 class
Symbol:u3 class
Dependency:u3 class
ProjectModel:u3 class
AnalysisCache:u4 class
canonicalize_target:u5 func
canonicalize_dependencies:u5 func
ProfileCanonicalizer:u6 class
BaseAnalyzer:u7 class
CAnalyzer:u8 class
RustAnalyzer:u9 class
JavaAnalyzer:u10 class
PythonAnalyzer:u11 class
AsmLdAnalyzer:u12 class
get_analyzer:u13 func
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