from pathlib import Path
from ..templates import (
    python as py_tmpl,
    c as c_tmpl,
    rust as rust_tmpl,
    java as java_tmpl,
    asm as asm_tmpl,
    ld as ld_tmpl
)

class InterfaceLayer:
    def __init__(self, pir, output):
        self.symbols = pir.symbols
        self.output = Path(output)
        self.unit_map = pir.unit_map
        self.template_registry = self._init_template_registry()

    def _init_template_registry(self):
        """初始化模板注册表"""
        return {
            'PY': {
                'func': py_tmpl.python_func_template,
                'class': py_tmpl.python_class_template,
                'var': py_tmpl.python_var_template if hasattr(py_tmpl, 'python_var_template') else None,
                'const': py_tmpl.python_const_template if hasattr(py_tmpl, 'python_const_template') else None
            },
            'C': {
                'func': c_tmpl.c_func_template,
                'struct': c_tmpl.c_struct_template,
                'var': c_tmpl.c_var_template if hasattr(c_tmpl, 'c_var_template') else None,
                'const': c_tmpl.c_const_template if hasattr(c_tmpl, 'c_const_template') else None
            },
            'CPP': {
                'func': c_tmpl.c_func_template,
                'struct': c_tmpl.c_struct_template,
                'var': c_tmpl.c_var_template if hasattr(c_tmpl, 'c_var_template') else None,
                'const': c_tmpl.c_const_template if hasattr(c_tmpl, 'c_const_template') else None
            },
            'RUST': {
                'func': rust_tmpl.rust_func_template,
                'struct': rust_tmpl.rust_struct_template,
                'enum': rust_tmpl.rust_enum_template,
                'trait': rust_tmpl.rust_trait_template
            },
            'JAVA': {
                'func': java_tmpl.java_method_template,
                'class': java_tmpl.java_class_template
            },
            'ASM': {
                'label': asm_tmpl.asm_label_template,
                'func': asm_tmpl.asm_func_template
            },
            'LD': {
                'ld_entry': ld_tmpl.ld_entry_template,
                'ld_symbol': ld_tmpl.ld_symbol_template
            }
        }

    def run(self):
        """按语言分组处理符号"""
        # 按语言分组并去重
        lang_symbols = {}
        seen = set()  # 用于去重的集合，存储 (name, unit, kind) 元组

        for sym in self.symbols:
            unit_type = self.unit_map[sym.unit].type
            key = (sym.name, sym.unit, sym.kind)

            # 如果这个符号已经处理过，跳过
            if key in seen:
                continue

            seen.add(key)

            if unit_type not in lang_symbols:
                lang_symbols[unit_type] = []
            lang_symbols[unit_type].append(sym)

        # 为每种语言生成代码
        for lang_type, symbols in lang_symbols.items():
            self._emit_language(lang_type, symbols)

    def _emit_language(self, lang_type, symbols):
        """为特定语言生成代码"""
        for sym in symbols:
            self._emit_symbol(sym, lang_type)

    def _emit_symbol(self, sym, lang_type):
        """生成单个符号的代码"""
        if lang_type not in self.template_registry:
            return

        kind_templates = self.template_registry[lang_type]
        if sym.kind not in kind_templates:
            return

        template_func = kind_templates[sym.kind]
        if template_func is None:
            return

        snippet = template_func(sym)

        file_path = self._unit_to_file(sym.unit)
        with open(file_path, "a") as f:
            f.write("\n" + snippet)

    def _unit_to_file(self, uid):
        return self.output / "src" / self.unit_map[uid].path
