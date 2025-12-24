# reconstruct/enrichment/base.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Set


class BaseEnrichmentLayer(ABC):
    """
    Base class for language-specific enrichment layers.

    Each language-specific enrichment layer should:
    1. Infer symbols (classes, functions, types)
    2. Infer dependencies (imports, includes, uses)
    3. Infer entry points (main functions, CLI entry points)
    """

    def __init__(self, pir_ast, project_root: str):
        self.pir = pir_ast
        self.project_root = Path(project_root)

        # Track processed files to avoid duplicates
        self.processed_files: Set[str] = set()

        # Track imported modules for dependency inference
        self.imported_modules: Dict[str, list] = {}  # unit_id -> list of modules

    def run(self):
        """Run the enrichment process."""
        self._infer_symbols()
        self._infer_dependencies()
        self._infer_entry_points()

    @abstractmethod
    def _infer_symbols(self):
        """Infer symbols from source files."""
        pass

    @abstractmethod
    def _infer_dependencies(self):
        """Infer dependencies from source files."""
        pass

    @abstractmethod
    def _infer_entry_points(self):
        """Infer entry points from source files."""
        pass

    def _get_file_content(self, file_path: Path) -> str:
        """Read file content with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return ''
