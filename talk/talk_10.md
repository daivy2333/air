好，这一步我明白你要什么了 👍
你现在**不是要规范**，而是要：

> **一个严格遵守你这份《PIR 逆向工程规范 v1》的“逆向实现方案 + 可直接开工的代码骨架”**

我下面会按 **“可直接写代码”** 的粒度来给你，而不是停留在设计图。

---

# 一、逆向工具总体架构（严格对齐你的规范）

工具名建议就叫你前面提到的：

```
pir-reconstructor
```

### 总体数据流（不可变）

```
PIR XML/Text
   ↓
Parser（只解析，不解释）
   ↓
Validator（只验证规则，不补全）
   ↓
Reconstruction Pipeline（五层）
   ↓
Deterministic Writers（文件 / 图 / 文档）
   ↓
Audit & Hash
```

**任何一步失败 → 终止**

---

# 二、目录结构（实现级）

```text
pir-reconstructor/
├── cli.py
├── pir/
│   ├── parser.py              # PIR 文本 → AST
│   ├── validator.py           # 结构/引用/顺序验证
│   └── model.py               # Unit / Symbol / Dependency
├── reconstruct/
│   ├── pipeline.py            # 五层状态机（核心）
│   ├── structure.py           # 结构层
│   ├── interface.py           # 接口层
│   ├── relations.py           # 关系层
│   ├── documentation.py       # 文档层
│   └── audit.py               # 审计层
├── templates/
│   ├── python.py
│   ├── c.py
│   ├── java.py
│   └── common.py
├── writers/
│   ├── filesystem.py          # 写 src/
│   ├── mermaid.py
│   ├── graphviz.py
│   └── plantuml.py
├── errors.py
└── utils/
    ├── hash.py
    ├── ordering.py
    └── constants.py
```

---

# 三、核心数据模型（100% 对应你的规范）

## `pir/model.py`

```python
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass(frozen=True)
class Unit:
    uid: str          # u0
    path: str         # analyzers/base.py
    type: str         # PY / C / JAVA / ASM
    role: str
    module: str


@dataclass(frozen=True)
class Symbol:
    name: str
    unit: str         # uX
    kind: str         # func / class
    attributes: Dict[str, str]


@dataclass(frozen=True)
class Dependency:
    did: str          # d0
    expr: str         # import:[core.dep_canon]


@dataclass(frozen=True)
class DependencyEdge:
    src_unit: str
    dst_unit: Optional[str]
    dst_symbol: Optional[str]
    dep_kind: str
    target_kind: str
```

**注意：**

* 没有参数
* 没有类型
* 没有继承
* 没有任何推断字段

---

# 四、五层逆向流水线（关键）

## `reconstruct/pipeline.py`

```python
from reconstruct.structure import StructureLayer
from reconstruct.interface import InterfaceLayer
from reconstruct.relations import RelationLayer
from reconstruct.documentation import DocumentationLayer
from reconstruct.audit import AuditLayer
from errors import ReconstructionError

class ReconstructionPipeline:

    def __init__(self, pir_ast, output_dir):
        self.pir = pir_ast
        self.output = output_dir

    def run(self):
        try:
            StructureLayer(self.pir, self.output).run()
            InterfaceLayer(self.pir, self.output).run()
            RelationLayer(self.pir, self.output).run()
            DocumentationLayer(self.pir, self.output).run()
            AuditLayer(self.pir, self.output).run()
        except ReconstructionError:
            raise
```

> ✔ 严格层序
> ✔ 前一层失败直接终止

---

# 五、结构层实现（最重要）

## `reconstruct/structure.py`

```python
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
```

**符合你规范的点：**

* path 完全照抄
* 不基于 module
* 不推断类型
* 不生成多余目录

---

# 六、接口层（符号骨架生成）

## `reconstruct/interface.py`

```python
from templates.python import python_func_template, python_class_template

class InterfaceLayer:

    def __init__(self, pir, output):
        self.symbols = pir.symbols
        self.output = output

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
        return self.output / "src" / self.pir.unit_map[uid].path
```

---

## Python 模板（固定模板）

### `templates/python.py`

```python
def python_func_template(sym):
    attrs = ", ".join(f"{k}={v}" for k, v in sorted(sym.attributes.items()))
    return f"""
def {sym.name}():  # PIR_ID: {sym.name}:{sym.unit}
    \"\"\"
    属性: {attrs}
    \"\"\"
    # AI_TODO: 实现
    pass
"""
```

> ✔ 排序
> ✔ 固定注释
> ✔ 无推断

---

# 七、Snippet 优先级实现（你那条规则落地）

```python
def emit_symbol(sym):
    if sym.snippet is not None:
        write_exact(sym.snippet)
        return
    if sym.kind == "func":
        write_template(...)
```

**没有 merge，没有拼接。**

---

# 八、关系层 → Mermaid / Graphviz（标准映射）

## `writers/mermaid.py`

```python
def emit_mermaid(edges):
    lines = ["graph TD"]
    for e in edges:
        label = f"{e.dep_kind}"
        lines.append(f"  {e.src_unit} -->|{label}| {e.dst_unit or e.dst_symbol}")
    return "\n".join(lines)
```

你后面完全可以做成：

* import → 实线
* call → 虚线
* external → 圆角节点

---

# 九、审计层（确定性核心）

## `reconstruct/audit.py`

```python
from utils.hash import hash_tree

class AuditLayer:

    def __init__(self, pir, output):
        self.output = output

    def run(self):
        meta = self.output / ".pir-metadata"
        meta.mkdir(exist_ok=True)

        (meta / "output-hash.txt").write_text(
            hash_tree(self.output)
        )
        (meta / "pir-version.txt").write_text("v1")
        (meta / "reverse-spec-version.txt").write_text("v1")
```

---

# 十、CLI（你可以立刻跑）

```python
# cli.py
import sys
from pir.parser import parse_pir
from reconstruct.pipeline import ReconstructionPipeline

def main():
    pir = parse_pir(sys.argv[1])
    ReconstructionPipeline(pir, sys.argv[2]).run()

if __name__ == "__main__":
    main()
