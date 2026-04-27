# AIR - Project Structure Analyzer for AI

## Overview

AIR (AI Intermediate Representation) generates a structured, token-optimized summary of any codebase. Designed for AI coding assistants (Claude, Claw, etc.) to quickly understand project structure without reading all files.

## Quick Start

```bash
# Analyze project
air /path/to/project

# Output: project.pir (current directory)
```

## CLI Options

| Option | Description |
|--------|-------------|
| `path` | Project root path (required) |
| `--name` | Output filename (default: my_project) |
| `--no-cache` | Force fresh analysis |
| `--ignore/-i` | Exclude directories (glob supported) |

```bash
# Full example
air ./myproject --name myproject --ignore tests --ignore examples

# Ignore multiple patterns
air ./project -i "test*" -i "vendor" -i "docs"
```

## PIR Format

PIR is a compact XML-like format:

```xml
<pir>
<meta>
my_project|./src|PY,Rust,C
</meta>
<units>
u0|src/main.rs|Rust|entry|src
u1|src/lib.rs|Rust|src
u2|src/main.c|C|src
</units>
<pool>
d0|call|u0#main
d1|import|[std::fmt]
</pool>
<deps>
u0|d0
u1|d1
</deps>
<syms>
main|u0|func|entry
init|u1|func
</syms>
</pir>
```

### Block Definitions

| Block | Description |
|-------|-------------|
| `<meta>` | Project name, root path, languages |
| `<units>` | Source files (uid, path, type, role, module) |
| `<pool>` | Dependency definitions (call, import, include, use) |
| `<deps>` | Which unit depends on which pool item |
| `<syms>` | Symbols (functions, classes, structs, labels) |

### Field Positions (units)

```
uid|path|lang|[role]|[module]
```

- `role=entry` = entry point (main file)
- Default role (`lib`) = library/internal file
- `module` = parent directory name

### Pool Verbs

| Verb | Meaning | Example |
|------|---------|---------|
| `call` | Function call | `call:u0#main` |
| `import` | Import statement | `import:[utils]` |
| `include` | C/C++ include | `include:[stdio.h]` |
| `use` | Rust use | `use:[crate::utils]` |

### Symbol Kinds

| Kind | Description |
|------|-------------|
| `func` | Function |
| `class` | Class |
| `struct` | Struct |
| `label` | Assembly label |
| `enum` | Enum |
| `entry` | Entry point marker |

## Example Workflow

### 1. Analyze a project
```bash
$ air ./my_c_project --name my_c
✅ PIR generated: my_c.pir
   Units: 12 | Symbols: 45 | Deps: 28
```

### 2. Read the PIR
The AI reads `my_c.pir` to understand:
- Project structure (units, modules)
- Entry points (role=entry)
- Dependencies (pool, deps)
- Available symbols (functions, structs)

### 3. Query specific files
With PIR info, AI can:
- Identify which file contains `process_data`
- Find all functions in a module
- Trace call dependencies

## Default Ignored Directories

```
.git, .idea, __pycache__, build, target,
node_modules, .venv, venv, .env,
tests, test, __tests__, .pytest_cache,
examples, docs, doc, dist, .dist
```

## For Claw Integration

### Basic Integration
```python
import subprocess

def analyze_project(project_path):
    result = subprocess.run(
        ["air", project_path, "--name", "analysis"],
        capture_output=True,
        text=True
    )
    with open("analysis.pir") as f:
        return f.read()
```

### With Ignore Patterns
```python
def analyze_for_ai(project_path):
    # Exclude test files and vendor code
    subprocess.run([
        "air", project_path,
        "--name", "analysis",
        "--ignore", "tests",
        "--ignore", "test_*",
        "--ignore", "vendor",
        "--ignore", "__pycache__"
    ])
```

## Specification

See `spec/spec.md` for detailed format specification.
