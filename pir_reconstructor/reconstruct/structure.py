from pathlib import Path
from ..errors import ReconstructionError

class StructureLayer:
    def __init__(self, pir, output):
        self.units = pir.units
        self.root = Path(output) / "src"
        self.file_headers = self._init_file_headers()

    def _init_file_headers(self):
        """初始化文件头模板"""
        return {
            'PY': '"""\nPIR 重建文件\nAI_TODO: 实现具体功能\n"""',
            'C': '/*\n* PIR 重建文件\n* AI_TODO: 实现具体功能\n*/',
            'CPP': '/*\n* PIR 重建文件\n* AI_TODO: 实现具体功能\n*/',
            'RUST': '// PIR 重建文件\n// AI_TODO: 实现具体功能',
            'JAVA': '/**\n* PIR 重建文件\n* AI_TODO: 实现具体功能\n*/',
            'ASM': '# PIR 重建文件\n# AI_TODO: 实现具体功能',
            'LD': '/* PIR 重建链接器脚本 */\n/* AI_TODO: 实现具体功能 */',
            'H': '/**\n* PIR 重建头文件\n* AI_TODO: 实现具体功能\n*/'
        }

    def run(self):
        for unit in self.units_in_order():
            self._emit_unit(unit)

    def units_in_order(self):
        return sorted(self.units, key=lambda u: int(u.uid[1:]))

    def _emit_unit(self, unit):
        path = self.root / unit.path
        path.parent.mkdir(parents=True, exist_ok=True)

        # 获取文件头
        header = self.file_headers.get(unit.type, "// Unknown type\n")

        # 写入文件
        path.write_text(header)
