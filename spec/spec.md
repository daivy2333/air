# PIR Format Specification

## Overview

PIR (Project Intermediate Representation) is a token-optimized text format for describing project structure, designed for AI/LLM consumption.

## Format

```xml
<pir>
<meta>
name|root|lang
</meta>
<units>
uid|path|lang|[role]|[module]
</units>
<pool>
did|verb|target
</pool>
<deps>
uid|did did...
</deps>
<syms>
name|uid|kind|[attr]...
</syms>
</pir>
```

## Blocks

### `<meta>` - Project Metadata
```
name|root|lang
```
Example: `my_project|./src|C,CPP,H,PY,Rust,S`

### `<units>` - Compilation Units
```
uid|path|lang|[role]|[module]
```
- `role=entry` only for entry points (main files)
- Default role (`lib`) is omitted

Example:
```
u0|cpp_project/calculator.h|H|cpp_project
u3|cpp_project/main.cpp|CPP|entry|cpp_project
```

### `<pool>` - Dependency Pool
```
did|verb|target
```
Verbs: `call`, `import`, `include`, `use`

Resolved dependencies: `did|verb|uid#symbol`
```
d0|call|u26#schedule
d1|import|[utils]
```

### `<deps>` - Unit Dependencies
```
uid|did did...
```
Example: `u0|d26 d24`

### `<syms>` - Symbol Definitions
```
name|uid|kind|[attr]...
```
Kinds: `func`, `class`, `struct`, `label`, `enum`

Example:
```
main|u3|func|entry
Calculator|u15|class
```

## Examples

### Simple Project
```xml
<pir>
<meta>
my_project|./src|PY
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

### Multi-language Project
```xml
<pir>
<meta>
os_kernel|./kernel|C,Rust,S
</meta>
<units>
u0|kernel/boot.S|S|entry|kernel
u1|kernel/main.c|C|kernel
u2|kernel/lib.rs|Rust|kernel
</units>
<pool>
d0|call|u1#start_kernel
d1|import|[stdlib:c]
</pool>
<deps>
u0|d0
u1|d1
</deps>
<syms>
_start|u0|label|entry
main|u1|func|entry
init|u2|func
</syms>
</pir>
```

## Verb Types

| Verb | Description | Example |
|------|-------------|---------|
| `call` | Function call | `u0#main` |
| `import` | Import statement | `[utils]` |
| `include` | Include directive | `[stdio.h]` |
| `use` | Rust use | `[crate::utils]` |

## Symbol Kinds

| Kind | Description |
|------|-------------|
| `func` | Function |
| `class` | Class |
| `struct` | Struct |
| `label` | Assembly label |
| `enum` | Enum |
| `entry` | Entry point marker |
