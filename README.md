# AIR - AI-friendly Project Intermediate Representation

A language-agnostic project structure analyzer that generates PIR (Project Intermediate Representation) optimized for AI/LLM consumption.

## Features

- **Multi-language support**: Python, Rust, C/C++, Java, Assembly
- **Token-optimized output**: Minimal overhead for LLMs
- **Entry point detection**: Automatically identifies main/entry files
- **Dependency resolution**: Tracks call/import/include/use dependencies
- **Analysis caching**: Fast incremental scans

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
```

## PIR Format

```xml
<pir>
<meta>
name: my_project
root: ./src
lang: PY,RUST
</meta>
<units>
u0: src/main.py type=PY role=entry module=src
u1: src/utils.py type=PY module=src
</units>
<dependency-pool>
d0: import:[utils]
</dependency-pool>
<dependencies>
u0:d0
</dependencies>
<symbols>
main:u0 func entry=true
greet:u1 func
</symbols>
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
│   ├── java_analyzer.py
│   └── asm_ld_analyzer.py
└── core/                  # Core modules
    ├── project_model.py
    ├── pir_builder.py
    ├── dep_canon.py
    ├── profile_canon.py
    └── analysis_cache.py
```

## Specification

See `spec/spec.md` for detailed PIR format specification.

## License

MIT
