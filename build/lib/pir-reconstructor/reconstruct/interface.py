from pathlib import Path
from pir_reconstructor.templates.python import python_func_template, python_class_template

class InterfaceLayer:

    def __init__(self, pir, output):
        self.symbols = pir.symbols
        self.output = Path(output)
        self.unit_map = pir.unit_map

    def run(self):
        for sym in self.symbols:
            self._emit_symbol(sym)

    def _emit_symbol(self, sym):
        file_path = self._unit_to_file(sym.unit)

        if sym.kind == "func":
            snippet = python_func_template(sym)
        elif sym.kind == "class":
            snippet = python_class_template(sym)
        else:
            return

        with open(file_path, "a") as f:
            f.write("\n" + snippet)

    def _unit_to_file(self, uid):
        return self.output / "src" / self.unit_map[uid].path
