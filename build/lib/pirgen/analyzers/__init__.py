# analyzers/__init__.py
from .c_analyzer import CAnalyzer
from .python_analyzer import PythonAnalyzer
from .java_analyzer import JavaAnalyzer
from .rust_analyzer import RustAnalyzer
from .asm_ld_analyzer import AsmLdAnalyzer

ANALYZER_MAP = {
    # C/C++
    '.c': CAnalyzer(),
    '.cpp': CAnalyzer(),
    '.cc': CAnalyzer(),
    '.h': CAnalyzer(),
    '.hpp': CAnalyzer(),
    # Python
    '.py': PythonAnalyzer(),
    # Java
    '.java': JavaAnalyzer(),
    # Rust
    '.rs': RustAnalyzer(),
    # ASM & Linker
    '.s': AsmLdAnalyzer(),
    '.asm': AsmLdAnalyzer(),
    '.ld': AsmLdAnalyzer(),
    '.lds': AsmLdAnalyzer(),
}

def get_analyzer(ext):
    return ANALYZER_MAP.get(ext.lower())