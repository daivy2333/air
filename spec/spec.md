# PIR Format Specification v1.1

## Overview

PIR (Project Intermediate Representation) is a text-based format for describing project structure, optimized for AI/LLM consumption.

## Format Structure

```xml
<pir>
<meta>
name: <project-name>
root: <relative-path>
lang: <languages>
</meta>
<units>
u0: <path> type=<LANG> [role=entry] module=<name>
...
</units>
<dependency-pool>
d0: <verb>:<target>
...
</dependency-pool>
<dependencies>
u0:d0 d1 d2
...
</dependencies>
<symbols>
<name>:<uid> <kind> [attr=value]
...
</symbols>
</pir>
```

## Blocks

### `<meta>` - Project Metadata
| Field | Description |
|-------|-------------|
| `name` | Project identifier (ASCII, no spaces) |
| `root` | Relative root path |
| `lang` | Languages: PY, C, CPP, RS, JAVA, H, S |

### `<units>` - Compilation Units
```
u<ID>: <path> type=<LANG> [role=entry] module=<name>
```
- `role=entry` only for entry points (e.g., main files)
- Default role (lib) is omitted

### `<dependency-pool>` - Dependency Pool
```
d<ID>: <verb>:<target>
```
Verbs: `call`, `import`, `include`, `use`

Resolved dependencies use `u<ID>#<symbol>` format:
```
d0: call:u26#schedule
```

### `<dependencies>` - Unit Dependencies
```
u<ID>:<dep-id> [<dep-id>...]
```

### `<symbols>` - Symbol Definitions
```
<name>:<unit-id> <kind> [attr=value]
```
Kinds: `func`, `class`, `struct`, `label`, `enum`

## Examples

### Simple Project
```xml
<pir>
<meta>
name: my_project
root: ./src
lang: PY
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

### Multi-language Project
```xml
<pir>
<meta>
name: os_kernel
root: ./kernel
lang: C,Rust,S
</meta>
<units>
u0: boot.S type=S role=entry module=kernel
u1: main.c type=C module=kernel
u2: lib.rs type=Rust module=kernel
</units>
<dependency-pool>
d0: call:u1#start_kernel
d1: include:[stdlib:c]
</dependency-pool>
<dependencies>
u0:d0
u1:d1
</dependencies>
<symbols>
_start:u0 label
main:u1 func entry=true
init:u2 func
</symbols>
</pir>
```

## Verb Types

| Verb | Description | Example |
|------|-------------|---------|
| `call` | Function/method call | `call:u0#main` |
| `import` | Python/Rust import | `import:[utils]` |
| `include` | C/C++ include | `include:[stdio.h]` |
| `use` | Rust use statement | `use:[crate::utils]` |

## Symbol Kinds

| Kind | Description |
|------|-------------|
| `func` | Function definition |
| `class` | Class definition |
| `struct` | Struct definition |
| `label` | Assembly label |
| `enum` | Enum definition |
| `entry` | Entry point attribute |
