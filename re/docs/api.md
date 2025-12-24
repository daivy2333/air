# API Documentation

## min_token.py

### is_source_file

- **Kind**: func
- **Unit**: u0

### strip_c_comments

- **Kind**: func
- **Unit**: u0

### minify_c_style

- **Kind**: func
- **Unit**: u0

### minify_python

- **Kind**: func
- **Unit**: u0

### process_directory

- **Kind**: func
- **Unit**: u0

### main

- **Kind**: func
- **Unit**: u0
- **Attributes**:
  - `entry`: true

## pirgen.py

### discover_source_files

- **Kind**: func
- **Unit**: u1

### infer_unit_meta

- **Kind**: func
- **Unit**: u1

### scan_project

- **Kind**: func
- **Unit**: u1

### resolve_dependencies

- **Kind**: func
- **Unit**: u1

### main

- **Kind**: func
- **Unit**: u1
- **Attributes**:
  - `entry`: true

## analyzers/c_analyzer.py

### CAnalyzer

- **Kind**: class
- **Unit**: u2

## analyzers/rust_analyzer.py

### RustAnalyzer

- **Kind**: class
- **Unit**: u3

## analyzers/java_analyzer.py

### JavaAnalyzer

- **Kind**: class
- **Unit**: u4

## analyzers/base.py

### BaseAnalyzer

- **Kind**: class
- **Unit**: u5

## analyzers/asm_ld_analyzer.py

### AsmLdAnalyzer

- **Kind**: class
- **Unit**: u6

## analyzers/__init__.py

### get_analyzer

- **Kind**: func
- **Unit**: u7

## analyzers/python_analyzer.py

### PythonAnalyzer

- **Kind**: class
- **Unit**: u8

## core/profile_canon.py

### ProfileCanonicalizer

- **Kind**: class
- **Unit**: u9

## core/analysis_cache.py

### AnalysisCache

- **Kind**: class
- **Unit**: u10

## core/project_model.py

### Unit

- **Kind**: class
- **Unit**: u11

### Symbol

- **Kind**: class
- **Unit**: u11

### Dependency

- **Kind**: class
- **Unit**: u11

### ProjectModel

- **Kind**: class
- **Unit**: u11

## core/pir_builder.py

### PIRBuilder

- **Kind**: class
- **Unit**: u12

## core/dep_canon.py

### canonicalize_target

- **Kind**: func
- **Unit**: u13

### canonicalize_dependencies

- **Kind**: func
- **Unit**: u13

