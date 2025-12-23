# core/analysis_cache.py
"""
Analysis Cache for PIR Generator

Caches analysis results per file to enable incremental builds.
Only caches the analyzer output (unit meta, symbols, deps),
not the final ProjectModel or PIR output.
"""

import json
import hashlib
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class AnalysisCache:
    """
    File-level analysis cache.

    Each source file gets one cache entry based on its content hash.
    Cache entries contain:
    - unit metadata
    - symbols
    - dependency keys
    """

    CACHE_VERSION = "pir-analyzer-v1"

    def __init__(self, root: str):
        """
        Initialize cache with project root.

        Args:
            root: Project root directory
        """
        self.root = os.path.join(root, ".pir-cache", "v1")

    def file_hash(self, path: str) -> str:
        """
        Calculate SHA256 hash of file content.

        Args:
            path: Path to the file

        Returns:
            Hex digest of SHA256 hash
        """
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def _get_cache_file(self, path: str, lang: str) -> str:
        """
        Get cache file path for a source file.

        Args:
            path: Source file path
            lang: Language identifier (PY, C, Rust, JAVA)

        Returns:
            Path to cache file
        """
        h = self.file_hash(path)
        lang_dir = lang.lower()
        return os.path.join(self.root, lang_dir, h + ".json")

    def load(self, path: str, lang: str) -> Optional[Dict[str, Any]]:
        """
        Load cached analysis for a file.

        Args:
            path: Source file path
            lang: Language identifier

        Returns:
            Cached data dict or None if not found/invalid
        """
        cache_file = self._get_cache_file(path, lang)

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Verify cache version
            if data.get("version") != self.CACHE_VERSION:
                return None

            # Verify hash matches
            if data.get("hash") != self.file_hash(path):
                return None

            return data
        except (json.JSONDecodeError, IOError, KeyError):
            return None

    def save(self, path: str, lang: str, data: Dict[str, Any]) -> None:
        """
        Save analysis result to cache.

        Args:
            path: Source file path
            lang: Language identifier
            data: Analysis result to cache
        """
        cache_file = self._get_cache_file(path, lang)
        lang_dir = os.path.dirname(cache_file)

        # Create language directory if needed
        os.makedirs(lang_dir, exist_ok=True)

        # Prepare cache entry
        cache_entry = {
            "version": self.CACHE_VERSION,
            "file": os.path.relpath(path, os.path.dirname(self.root).rstrip(os.sep)),
            "hash": self.file_hash(path),
            "lang": lang,
            "timestamp": datetime.utcnow().isoformat(),
            **data
        }

        # Write cache file
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_entry, f, indent=2, sort_keys=True)

    def invalidate(self, path: str, lang: str) -> None:
        """
        Invalidate cache for a specific file.

        Args:
            path: Source file path
            lang: Language identifier
        """
        cache_file = self._get_cache_file(path, lang)
        if os.path.exists(cache_file):
            os.remove(cache_file)

    def clear(self) -> None:
        """
        Clear all cache entries.
        """
        if os.path.exists(self.root):
            import shutil
            shutil.rmtree(self.root)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats (hits, misses, total_entries, etc.)
        """
        stats = {
            "total_entries": 0,
            "by_language": {},
            "total_size_bytes": 0
        }

        if not os.path.exists(self.root):
            return stats

        for lang_dir in os.listdir(self.root):
            lang_path = os.path.join(self.root, lang_dir)
            if not os.path.isdir(lang_path):
                continue

            count = 0
            size = 0
            for cache_file in os.listdir(lang_path):
                if cache_file.endswith(".json"):
                    count += 1
                    size += os.path.getsize(os.path.join(lang_path, cache_file))

            stats["by_language"][lang_dir] = {
                "entries": count,
                "size_bytes": size
            }
            stats["total_entries"] += count
            stats["total_size_bytes"] += size

        return stats
