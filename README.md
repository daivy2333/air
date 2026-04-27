# AIR - AI-friendly Project Intermediate Representation

A language-agnostic project structure analyzer that generates PIR (Project Intermediate Representation) optimized for AI/LLM consumption.

## Features

- **Multi-language support**: Python, Rust, C/C++, Assembly
- **Token-optimized output**: Minimal overhead for LLMs
- **Entry point detection**: Automatically identifies main/entry files
- **Dependency resolution**: Tracks call/import/include/use dependencies
- **Analysis caching**: Fast incremental scans
- **Flexible ignore**: Exclude directories from analysis

## Installation

```bash
pip install . --user
```

## Usage

```bash
# Basic usage
air /path/to/project

# Specify output name
air /path/to/project --name my_project

# Disable cache
air /path/to/project --no-cache

# Ignore directories (supports glob patterns)
air /path/to/project --ignore test_projects
air /path/to/project --ignore "test*" --ignore "examples"
```

### Default Ignored Directories

```
.git, .idea, __pycache__, build, target,
node_modules, .venv, venv, .env,
tests, test, __tests__, .pytest_cache,
examples, docs, doc, dist, .dist
```

## PIR Format

```xml
<pir>
<meta>
my_project|./src|PY,Rust
</meta>
<units>
u0|src/main.py|PY|entry|src
u1|src/utils.py|PY|src
</units>
<pool>
d0|import|[utils]
</pool>
<deps>
u0|d0
</deps>
<syms>
main|u0|func|entry
greet|u1|func
</syms>
</pir>
```

## Project Structure

```
pirgen/
├── pirgen.py              # CLI entry point
├── __init__.py            # Package init
├── analyzers/             # Language analyzers
│   ├── base.py
│   ├── python_analyzer.py
│   ├── c_analyzer.py
│   ├── rust_analyzer.py
│   └── asm_ld_analyzer.py
└── core/                  # Core modules
    ├── project_model.py
    ├── pir_builder.py
    ├── dep_canon.py
    └── analysis_cache.py
```

## Specification

See `spec/spec.md` for detailed PIR format specification.

## License

MIT
