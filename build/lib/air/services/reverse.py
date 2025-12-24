"""
Reverse service for PIR reconstruction
Wraps pir-reconstructor functionality
"""
import sys
from pathlib import Path

# Add pir-reconstructor to path
recon_path = Path(__file__).parent.parent.parent.parent / "pir-reconstructor"
sys.path.insert(0, str(recon_path))

from pir.parser import parse_pir
from pir.validator import validate_pir, ValidationError
from reconstruct.pipeline import ReconstructionPipeline
from errors import ReconstructionError, ParserError


def run_reverse(
    pir_path: str,
    output_dir: str,
    project_root: str | None = None,
    validate_only: bool = False
):
    """
    Run reverse reconstruction from PIR

    Args:
        pir_path: Path to PIR specification file
        output_dir: Output directory for reconstructed project
        project_root: Project root directory (optional, defaults to parent of PIR file)
        validate_only: If True, only validate PIR without reconstruction

    Returns:
        None if validate_only is True, otherwise the ReconstructionPipeline instance
    """
    # Determine project root
    if project_root is None:
        pir_file = Path(pir_path)
        project_root = str(pir_file.parent)

    # Parse PIR file
    pir_ast = parse_pir(pir_path)

    # Validate PIR
    validate_pir(pir_ast)

    # Exit if only validation requested
    if validate_only:
        return None

    # Run reconstruction pipeline
    pipeline = ReconstructionPipeline(pir_ast, output_dir, project_root)
    pipeline.run()

    return pipeline
