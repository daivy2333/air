"""
Forward service for PIR generation
Wraps pirgen functionality
"""
import os
import sys
from pathlib import Path

# Add pirgen to path
pirgen_path = Path(__file__).parent.parent / "pirgen"
sys.path.insert(0, str(pirgen_path))

from core.project_model import ProjectModel
from core.pir_builder import PIRBuilder
from core.dep_canon import canonicalize_dependencies
from core.profile_canon import ProfileCanonicalizer
from analyzers import get_analyzer


def run_forward(
    source_path: str,
    out: str | None = None,
    profile: str | None = None,
    name: str | None = None,
    use_cache: bool = True
):
    """
    Run forward PIR generation

    Args:
        source_path: Path to source project directory
        out: Output PIR file path (optional)
        profile: Profile name for canonicalization (optional)
        name: Project name (optional)
        use_cache: Whether to use analysis cache (default: True)

    Returns:
        Path to generated PIR file
    """
    abs_root = os.path.abspath(source_path)
    if not os.path.exists(abs_root):
        raise ValueError(f"Path {abs_root} does not exist")

    # Import and use pirgen's scan_project
    from pirgen import scan_project, resolve_dependencies

    model = ProjectModel(
        name=name or os.path.basename(abs_root),
        root=abs_root,
        profile=profile or "generic"
    )

    scan_project(abs_root, model, use_cache=use_cache)
    resolve_dependencies(model)
    canonicalize_dependencies(model)
    model.finalize_dependencies()

    # Apply profile-aware canonicalization
    ProfileCanonicalizer().apply(model)

    builder = PIRBuilder(model)
    pir_content = builder.build()

    # Determine output path
    if out is None:
        out = f"{model.name}.pir"

    with open(out, "w", encoding="utf-8") as f:
        f.write(pir_content)

    return out
