from pathlib import Path

class DocumentationLayer:

    def __init__(self, pir, output):
        self.pir = pir
        self.output = Path(output)

    def run(self):
        # Create docs directory
        docs_dir = self.output / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Generate README
        self._generate_readme(docs_dir)

        # Generate API documentation
        self._generate_api_docs(docs_dir)

    def _generate_readme(self, docs_dir):
        readme_content = f"""# Reconstructed Project

This project was reconstructed from PIR specification.

## Project Structure

- Units: {len(self.pir.units)}
- Symbols: {len(self.pir.symbols)}
- Dependencies: {len(self.pir.dependencies)}

## Generated Files

- Source code in `src/`
- Dependency diagrams in `diagrams/`
- API documentation in `docs/api.md`

## Metadata

- PIR Version: v1
- Reconstruction Spec Version: v1
"""
        (docs_dir / "README.md").write_text(readme_content)

    def _generate_api_docs(self, docs_dir):
        api_content = "# API Documentation\n\n"

        # Group symbols by unit
        unit_symbols = {}
        for sym in self.pir.symbols:
            if sym.unit not in unit_symbols:
                unit_symbols[sym.unit] = []
            unit_symbols[sym.unit].append(sym)

        # Generate documentation for each unit
        for unit_id, symbols in unit_symbols.items():
            unit = self.pir.unit_map[unit_id]
            api_content += f"## {unit.path}\n\n"

            for sym in symbols:
                api_content += f"### {sym.name}\n\n"
                api_content += f"- **Kind**: {sym.kind}\n"
                api_content += f"- **Unit**: {unit_id}\n"

                if sym.attributes:
                    api_content += "- **Attributes**:\n"
                    for key, value in sym.attributes.items():
                        api_content += f"  - `{key}`: {value}\n"

                api_content += "\n"

        (docs_dir / "api.md").write_text(api_content)
