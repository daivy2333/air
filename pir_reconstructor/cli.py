#!/usr/bin/env python3
"""
PIR Reconstructor CLI
Main entry point for PIR reconstruction tool.
"""

import sys
import argparse
from pathlib import Path

from .pir.parser import parse_pir
from .pir.validator import validate_pir, ValidationError
from .reconstruct.pipeline import ReconstructionPipeline
from .errors import ReconstructionError, ParserError


def main():
    parser = argparse.ArgumentParser(
        description='PIR Reconstructor - Reconstruct projects from PIR specifications'
    )
    parser.add_argument(
        'pir_file',
        type=str,
        help='Path to PIR specification file'
    )
    parser.add_argument(
        'output_dir',
        type=str,
        help='Output directory for reconstructed project'
    )
    parser.add_argument(
        '--project-root',
        type=str,
        default=None,
        help='Project root directory for source code analysis (default: parent of PIR file)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate PIR file without reconstruction'
    )

    args = parser.parse_args()

    try:
        # Determine project root
        if args.project_root is None:
            # Default to parent directory of PIR file
            pir_path = Path(args.pir_file)
            project_root = str(pir_path.parent)
        else:
            project_root = args.project_root

        # Parse PIR file
        print(f"Parsing PIR file: {args.pir_file}")
        pir_ast = parse_pir(args.pir_file)
        print(f"  Found {len(pir_ast.units)} units")
        print(f"  Found {len(pir_ast.symbols)} symbols")
        print(f"  Found {len(pir_ast.dependencies)} dependencies")

        # Validate PIR
        print("Validating PIR structure...")
        validate_pir(pir_ast)
        print("  Validation passed")

        # Exit if only validation requested
        if args.validate_only:
            print("Validation complete. Exiting.")
            return 0

        # Run reconstruction pipeline
        print(f"Running reconstruction pipeline...")
        print(f"  Output directory: {args.output_dir}")
        print(f"  Project root: {project_root}")

        pipeline = ReconstructionPipeline(pir_ast, args.output_dir, project_root)
        pipeline.run()

        print("Reconstruction completed successfully!")
        return 0

    except ValidationError as e:
        print(f"Validation Error: {e}", file=sys.stderr)
        return 1
    except ParserError as e:
        print(f"Parser Error: {e}", file=sys.stderr)
        return 1
    except ReconstructionError as e:
        print(f"Reconstruction Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
