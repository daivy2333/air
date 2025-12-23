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
u9: core/profile_canon.py type=PY role=lib module=core
u10: core/analysis_cache.py type=PY role=lib module=core
u11: core/project_model.py type=PY role=lib module=core
u12: core/pir_builder.py type=PY role=lib module=core
u13: core/dep_canon.py type=PY role=lib module=core
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
u0->refs:[d13]
u1->refs:[d13 d12 d10 d9 d11 d8 d7]
u2->refs:[d13 d1 d12]
u3->refs:[d13 d1 d12]
u4->refs:[d13 d1 d12]
u5->refs:[d13 d12]
u6->refs:[d13 d1 d12]
u7->refs:[d2 d5 d3 d6 d0]
u8->refs:[d13 d1 d12]
u9->refs:[d13]
u10->refs:[d13]
u11->refs:[d13]
u12->refs:[d4]
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
ProfileCanonicalizer:u9 class
AnalysisCache:u10 class
Unit:u11 class
Symbol:u11 class
Dependency:u11 class
ProjectModel:u11 class
PIRBuilder:u12 class
canonicalize_target:u13 func
canonicalize_dependencies:u13 func
</symbols>
<profiles>
  active: python-tool
  python-tool:
    confidence: 0.75
    tags:
      - domain:tooling
      - lib:stdlib
      - runtime:cpython
      - stack:python-tool
    signals:
      - entry-point
      - multi-unit
      - pure-python
      - stdlib
</profiles>
</pir>