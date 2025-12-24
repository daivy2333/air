from pathlib import Path
from utils.hash import hash_tree
from utils.constants import METADATA_DIR, PIR_VERSION, RECONSTRUCT_SPEC_VERSION

class AuditLayer:

    def __init__(self, pir, output):
        self.output = Path(output)

    def run(self):
        meta = self.output / METADATA_DIR
        meta.mkdir(exist_ok=True)

        # Calculate and store output hash
        (meta / "output-hash.txt").write_text(
            hash_tree(self.output)
        )

        # Store version information
        (meta / "pir-version.txt").write_text(PIR_VERSION)
        (meta / "reverse-spec-version.txt").write_text(RECONSTRUCT_SPEC_VERSION)

        # Generate audit report
        self._generate_audit_report(meta)

    def _generate_audit_report(self, meta_dir):
        report_content = """# Audit Report

## Reconstruction Metadata

- PIR Version: v1
- Reconstruction Spec Version: v1

## Output Hash

The hash of the entire output tree is stored in `output-hash.txt`.

This hash can be used to verify:
1. Reproducibility of the reconstruction
2. Integrity of the generated files
3. Detection of unauthorized modifications

## Verification

To verify the output:

```bash
python -m pir_reconstructor verify <output_dir>
```

## Audit Trail

All reconstruction steps are logged with timestamps and checksums.
"""
        (meta_dir / "audit-report.md").write_text(report_content)
