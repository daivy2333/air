<pir>
<meta>
name: pcegen
root: /home/daivy/projects/air/pcegen
profile: generic
lang: PY
</meta>
<units>
u0: test_pir.py type=PY role=lib module=pcegen
u1: test_resolve.py type=PY role=lib module=pcegen
u2: __init__.py type=PY role=lib module=pcegen
u3: pcegen.py type=PY role=lib module=pcegen
u4: analyzers/asm.py type=PY role=lib module=analyzers
u5: analyzers/cpp.py type=PY role=lib module=analyzers
u6: analyzers/rust.py type=PY role=lib module=analyzers
u7: analyzers/ld.py type=PY role=lib module=analyzers
u8: analyzers/base.py type=PY role=lib module=analyzers
u9: analyzers/python.py type=PY role=lib module=analyzers
u10: analyzers/__init__.py type=PY role=lib module=analyzers
u11: analyzers/c.py type=PY role=lib module=analyzers
u12: models/evidence.py type=PY role=lib module=models
u13: models/need.py type=PY role=lib module=models
u14: models/__init__.py type=PY role=lib module=models
u15: models/resolved_ref.py type=PY role=lib module=models
u16: core/evidence_builder.py type=PY role=lib module=core
u17: core/extractor.py type=PY role=lib module=core
u18: core/language_detector.py type=PY role=lib module=core
u19: core/compressor.py type=PY role=lib module=core
u20: core/__init__.py type=PY role=lib module=core
u21: core/pir_index.py type=PY role=lib module=core
u22: core/pir_parser.py type=PY role=lib module=core
u23: core/resolver.py type=PY role=lib module=core
u24: core/pcr_parser.py type=PY role=lib module=core
u25: core/serializer.py type=PY role=lib module=core
</units>
<dependency-pool>
d0: import:[analyzers.base]
d1: import:[core.evidence_builder]
d2: import:[core.extractor]
d3: import:[core.language_detector]
d4: import:[core.pcr_parser]
d5: import:[core.pir_index]
d6: import:[core.resolver]
d7: import:[core.serializer]
d8: import:[models.evidence]
d9: import:[models.need]
d10: import:[models.resolved_ref]
d11: import:[stdlib:py]
</dependency-pool>
<dependencies>
u0->refs:[d2 d5 d6 d4]
u1->refs:[d5 d6 d4]
u3->refs:[d2 d4 d11 d1 d5 d6 d7]
u4->refs:[d0 d11]
u5->refs:[d0 d11]
u6->refs:[d0 d11]
u7->refs:[d0 d11]
u8->refs:[d11]
u9->refs:[d0 d11]
u11->refs:[d0 d11]
u12->refs:[d11]
u13->refs:[d11]
u15->refs:[d11]
u16->refs:[d10 d8 d11]
u17->refs:[d3 d10 d11]
u18->refs:[d11]
u19->refs:[d10 d8 d11]
u21->refs:[d11]
u22->refs:[d11]
u23->refs:[d9 d10 d11]
u24->refs:[d9 d11]
u25->refs:[d8 d11]
</dependencies>
<symbols>
load_source_code:u3 func
process_pcr:u3 func
main:u3 func entry=true
ASMAnalyzer:u4 class
CppAnalyzer:u5 class
RustAnalyzer:u6 class
LDAnalyzer:u7 class
BaseAnalyzer:u8 class
PythonAnalyzer:u9 class
CAnalyzer:u11 class
Evidence:u12 class
Need:u13 class
ResolvedRef:u15 class
EvidenceBuilder:u16 class
Extractor:u17 class
LanguageDetector:u18 class
Compressor:u19 class
PIRIndex:u21 class
PIRParser:u22 class
Resolver:u23 class
PCRParser:u24 class
PCESerializer:u25 class
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