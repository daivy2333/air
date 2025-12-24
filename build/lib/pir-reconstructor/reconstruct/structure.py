from pathlib import Path
from errors import ReconstructionError

class StructureLayer:

    def __init__(self, pir, output):
        self.units = pir.units
        self.root = Path(output) / "src"

    def run(self):
        for unit in self.units_in_order():
            self._emit_unit(unit)

    def units_in_order(self):
        return sorted(self.units, key=lambda u: int(u.uid[1:]))

    def _emit_unit(self, unit):
        path = self.root / unit.path
        path.parent.mkdir(parents=True, exist_ok=True)

        if unit.type in ("PY", "C", "JAVA", "RS"):
            path.write_text("")   # 骨架后续填
        elif unit.type in ("ASM", "LD"):
            path.write_text(f"// Empty {unit.type} file\n")
        else:
            path.write_text("// Unknown type\n")
