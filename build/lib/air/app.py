#!/usr/bin/env python3
"""
AIR - Application Interface Center
Unified entry point for forward (PIR generation) and reverse (reconstruction) operations
"""
import argparse
import sys

from air.services.forward import run_forward
from air.services.reverse import run_reverse
from air.services.peek import run_peek


def main():
    parser = argparse.ArgumentParser(
        prog="air",
        description="AIR - Unified interface for PIR generation and reconstruction"
    )
    subparsers = parser.add_subparsers(dest="cmd", required=True, help="Command to execute")

    # Forward command (PIR generation)
    fwd_parser = subparsers.add_parser("forward", help="Generate PIR from source code")
    fwd_parser.add_argument(
        "src",
        help="Path to source project directory"
    )
    fwd_parser.add_argument(
        "-o", "--out",
        help="Output PIR file path (default: <project_name>.pir)"
    )
    fwd_parser.add_argument(
        "--profile",
        default="generic",
        help="Profile name for canonicalization (default: generic)"
    )
    fwd_parser.add_argument(
        "--name",
        help="Project name (default: directory name)"
    )
    fwd_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable analysis cache"
    )

    # Reverse command (reconstruction)
    rev_parser = subparsers.add_parser("reverse", help="Reconstruct project from PIR")
    rev_parser.add_argument(
        "pir",
        help="Path to PIR specification file"
    )
    rev_parser.add_argument(
        "output_dir",
        help="Output directory for reconstructed project"
    )
    rev_parser.add_argument(
        "--project-root",
        help="Project root directory (default: parent of PIR file)"
    )
    rev_parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate PIR without reconstruction"
    )

    # Peek command (PCES generation)
    peek_parser = subparsers.add_parser("peek", help="Generate PCES from PCR")
    peek_parser.add_argument(
        "pcr",
        help="Path to PCR file"
    )
    peek_parser.add_argument(
        "--source-dir",
        help="Directory containing source code (default: current directory)"
    )
    peek_parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)"
    )

    args = parser.parse_args()

    try:
        if args.cmd == "forward":
            output_file = run_forward(
                source_path=args.src,
                out=args.out,
                profile=args.profile,
                name=args.name,
                use_cache=not args.no_cache
            )
            print(f"✅ PIR generation complete")
            print(f"   Output: {output_file}")

        elif args.cmd == "reverse":
            result = run_reverse(
                pir_path=args.pir,
                output_dir=args.output_dir,
                project_root=args.project_root,
                validate_only=args.validate_only
            )

            if args.validate_only:
                print("✅ PIR validation passed")
            else:
                print(f"✅ Reconstruction complete")
                print(f"   Output directory: {args.output_dir}")

        elif args.cmd == "peek":
            output_file = run_peek(
                pcr_path=args.pcr,
                source_dir=args.source_dir,
                output=args.output
            )
            print(f"✅ PCES generation complete")
            print(f"   Output: {output_file}")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
