# Audit Report

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
