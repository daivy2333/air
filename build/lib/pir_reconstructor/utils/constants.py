"""Constants for PIR reconstruction."""

# Supported unit types
UNIT_TYPES = {
    'PY': 'Python',
    'C': 'C',
    'JAVA': 'Java',
    'ASM': 'Assembly',
    'LD': 'Linker Script',
    'RS': 'Rust'
}

# Symbol kinds
SYMBOL_KINDS = {
    'func': 'Function',
    'class': 'Class',
    'var': 'Variable',
    'const': 'Constant'
}

# Dependency kinds
DEP_KINDS = {
    'import': 'Import',
    'call': 'Call',
    'inherit': 'Inheritance',
    'implement': 'Implementation',
    'external': 'External'
}

# Target kinds
TARGET_KINDS = {
    'unit': 'Unit',
    'symbol': 'Symbol',
    'module': 'Module',
    'external': 'External'
}

# File extensions by unit type
FILE_EXTENSIONS = {
    'PY': '.py',
    'C': '.c',
    'JAVA': '.java',
    'ASM': '.asm',
    'LD': '.ld',
    'RS': '.rs'
}

# Metadata directory name
METADATA_DIR = '.pir-metadata'

# Version information
PIR_VERSION = 'v1'
RECONSTRUCT_SPEC_VERSION = 'v1'
