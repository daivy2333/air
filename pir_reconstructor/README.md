# PIR Reconstructor

A tool for reconstructing projects from PIR (Project Intermediate Representation) specifications.

## Features

- Parse PIR text/XML specifications into AST
- Validate PIR structure and references
- Reconstruct project structure with five-layer pipeline
  - Structure Layer: Generate file and directory structure
  - Interface Layer: Generate symbol skeletons
  - Relation Layer: Generate dependency diagrams (Mermaid/Graphviz/PlantUML)
  - Documentation Layer: Generate API documentation
  - Audit Layer: Generate audit reports and hashes
- Deterministic output with hash verification
- Multi-language support (Python, C, Java, Assembly, Rust)

## Installation

```bash
cd pir-reconstructor
pip install -r requirements.txt
```

## Usage

```bash
python cli.py <pir_file> <output_dir>
```

### Options

- `--validate-only`: Only validate the PIR file without reconstruction

### Example

```bash
python cli.py example.pir output/
```

## Project Structure

```
pir-reconstructor/
├── cli.py                 # Main CLI entry point
├── pir/
│   ├── parser.py          # PIR parser
│   ├── validator.py       # PIR validator
│   └── model.py           # Data models
├── reconstruct/
│   ├── pipeline.py        # Reconstruction pipeline
│   ├── structure.py       # Structure layer
│   ├── interface.py       # Interface layer
│   ├── relations.py       # Relations layer
│   ├── documentation.py   # Documentation layer
│   └── audit.py           # Audit layer
├── templates/
│   ├── python.py          # Python templates
│   ├── c.py               # C templates
│   ├── java.py            # Java templates
│   └── common.py          # Common utilities
├── writers/
│   ├── filesystem.py      # File system writer
│   ├── mermaid.py         # Mermaid writer
│   ├── graphviz.py        # Graphviz writer
│   └── plantuml.py        # PlantUML writer
├── utils/
│   ├── hash.py            # Hash utilities
│   ├── ordering.py        # Sorting utilities
│   └── constants.py       # Constants
└── errors.py              # Error definitions
```

## PIR Specification

PIR (Project Intermediate Representation) is a text-based format for describing project structure, symbols, and dependencies.

### Unit Definition

```
unit u0 {
    path: analyzers/base.py
    type: PY
    role: MODULE
    module: core
}
```

### Symbol Definition

```
symbol analyze {
    unit: u0
    kind: func
    attributes: {
        visibility: public
        static: true
    }
}
```

### Dependency Definition

```
dependency d0 {
    expr: import:[core.dep_canon]
}
```

### Dependency Edge

```
edge {
    src: u0
    dst_unit: u1
    dep_kind: import
    target_kind: unit
}
```

## Output Structure

The reconstructed project will have the following structure:

```
output/
├── src/                   # Source code
│   └── ...
├── diagrams/              # Dependency diagrams
│   ├── dependencies.mmd   # Mermaid
│   ├── dependencies.dot   # Graphviz
│   └── dependencies.puml  # PlantUML
├── docs/                  # Documentation
│   ├── README.md
│   └── api.md
└── .pir-metadata/         # Metadata and audit
    ├── output-hash.txt
    ├── pir-version.txt
    ├── reverse-spec-version.txt
    └── audit-report.md
```

## License

MIT
