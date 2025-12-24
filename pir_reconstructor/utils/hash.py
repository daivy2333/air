import hashlib
from pathlib import Path

def hash_tree(directory: Path) -> str:
    """
    Calculate a deterministic hash of all files in a directory tree.
    Files are processed in sorted order to ensure deterministic results.
    """
    if not isinstance(directory, Path):
        directory = Path(directory)

    if not directory.exists():
        return ""

    hasher = hashlib.sha256()

    # Get all files and sort them
    files = sorted(directory.rglob('*'))

    for file_path in files:
        if file_path.is_file():
            # Add relative path to hash
            rel_path = file_path.relative_to(directory)
            hasher.update(str(rel_path).encode('utf-8'))

            # Add file content to hash
            with open(file_path, 'rb') as f:
                hasher.update(f.read())

    return hasher.hexdigest()
