太好了，你给的这几份代码已经够我把 **v0.2.1 → v0.3（dependency-pool + refs）** 的升级方案落到“可直接改代码”的层面了。下面我给你一套**最小侵入式改法**：Analyzer 基本不用动（继续调用 `add_dependency`），主要改 `ProjectModel` 和 `PIRBuilder`，外加把 `resolve_dependencies` 调整到适配新结构。

---

## 你要改的点一览

### ✅ 目标输出（v0.3）

* 新增区块：`<dependency-pool>`
* `<dependencies>` 变成：`uX->refs:[d0 d1 ...]`
* 依赖定义统一集中去重：`dX: verb:target`

### ✅ 代码层改动最少的策略

* `model.add_dependency(src, verb, target)` 保持接口不变
* 但内部不再 append `Dependency(...)` 到 list，而是：

  * 把 `verb:target` 去重进 pool（分配 `dX`）
  * 把 `dX` 记到该 unit 的 refs 列表中

---

## 1) 修改 `core/project_model.py`（核心）

把 `Dependency` dataclass 保留也行（但不再用于全局 list），建议新增这三样：

* `dep_pool: Dict[str, str]`：key=`"verb:target"` → `dX`
* `dep_pool_items: List[tuple[str,str,str]]`：按顺序保存 `(dX, verb, target)` 供输出
* `dep_refs: Dict[str, List[str]]`：`uX -> [d0, d5, ...]`

### ✅ 推荐实现（直接替换/增量改）

```python
# core/project_model.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple

@dataclass
class Unit:
    uid: str
    path: str
    lang: str
    role: str
    module: str

@dataclass
class Symbol:
    name: str
    unit_uid: str
    kind: str
    attrs: Dict[str, str] = field(default_factory=dict)

# 依赖定义仍可保留，但 v0.3 不再需要全局 Dependency 列表
@dataclass
class Dependency:
    src_uid: str
    verb: str
    target: str

class ProjectModel:
    def __init__(self, name: str, root: str, profile: str):
        self.name = name
        self.root = root
        self.profile = profile
        self.langs: Set[str] = set()

        self.units: List[Unit] = []
        self._path_to_uid: Dict[str, str] = {}

        self.symbols: List[Symbol] = []

        # v0.3: dependency pool + refs
        self._dep_key_to_did: Dict[str, str] = {}                 # "verb:target" -> "dX"
        self.dep_pool_items: List[Tuple[str, str, str]] = []      # (dX, verb, target) keep order
        self.dep_refs: Dict[str, List[str]] = {}                  # uX -> [dX, dY...]

        # 兼容旧字段：如果你别处还在用 model.dependencies，可以先保留（但不用于输出）
        self.dependencies: List[Dependency] = []

        self.layout_lines: List[str] = []
        self.snippets: List[tuple] = []  # (unit_uid, content)

    def add_unit(self, path: str, lang: str, role: str = "lib", module: str = "common") -> str:
        uid = f"u{len(self.units)}"
        unit = Unit(uid, path, lang, role, module)
        self.units.append(unit)
        self._path_to_uid[path] = uid
        self.langs.add(lang)
        return uid

    def add_symbol(self, name: str, unit_uid: str, kind: str, **attrs):
        self.symbols.append(Symbol(name, unit_uid, kind, attrs))

    def _intern_dependency(self, verb: str, target: str) -> str:
        key = f"{verb}:{target}"
        did = self._dep_key_to_did.get(key)
        if did is None:
            did = f"d{len(self.dep_pool_items)}"
            self._dep_key_to_did[key] = did
            self.dep_pool_items.append((did, verb, target))
        return did

    def add_dependency(self, src_uid: str, verb: str, target: str):
        # 保留旧 list（可选）
        self.dependencies.append(Dependency(src_uid, verb, target))

        did = self._intern_dependency(verb, target)
        lst = self.dep_refs.setdefault(src_uid, [])
        if did not in lst:   # 去重（保持稳定输出）
            lst.append(did)

    def get_uid_by_path(self, path: str) -> Optional[str]:
        return self._path_to_uid.get(path)
```

---

## 2) 修改 `core/pir_builder.py`（新增 pool + 改 dependencies 输出）

你现在 build 顺序是：
meta → units → dependencies → symbols → layout → snippets

v0.3 要变成：
meta → units → dependency-pool → dependencies → symbols → layout(optional)

### ✅ 推荐改法（最少改动）

```python
# core/pir_builder.py
from .project_model import ProjectModel

class PIRBuilder:
    def __init__(self, model: ProjectModel):
        self.model = model

    def build(self) -> str:
        sections = [
            "<pir>",
            self._build_meta(),
            self._build_units(),
            self._build_dependency_pool(),   # ✅ 新增
            self._build_dependencies(),      # ✅ 改写为 refs
            self._build_symbols(),
            self._build_layout(),
            self._build_snippets(),
            "</pir>"
        ]
        return "\n".join(filter(None, sections))

    def _build_meta(self) -> str:
        langs = ",".join(sorted(self.model.langs))
        return (
            "<meta>\n"
            f"name: {self.model.name}\n"
            f"root: {self.model.root}\n"
            f"profile: {self.model.profile}\n"
            f"lang: {langs}\n"
            "</meta>"
        )

    def _build_units(self) -> str:
        lines = ["<units>"]
        for u in self.model.units:
            lines.append(f"{u.uid}: {u.path} type={u.lang} role={u.role} module={u.module}")
        lines.append("</units>")
        return "\n".join(lines)

    def _build_dependency_pool(self) -> str:
        if not self.model.dep_pool_items:
            return ""
        lines = ["<dependency-pool>"]
        for did, verb, target in self.model.dep_pool_items:
            lines.append(f"{did}: {verb}:{target}")
        lines.append("</dependency-pool>")
        return "\n".join(lines)

    def _build_dependencies(self) -> str:
        if not self.model.dep_refs:
            return ""
        lines = ["<dependencies>"]
        # 为了稳定 diff：按 uX 排序输出
        for uid in sorted(self.model.dep_refs.keys(), key=lambda x: int(x[1:])):
            refs = self.model.dep_refs[uid]
            if refs:
                # 也可以排序 refs 保持稳定：refs = sorted(refs, key=lambda x: int(x[1:]))
                lines.append(f"{uid}->refs:[{' '.join(refs)}]")
        lines.append("</dependencies>")
        return "\n".join(lines)

    def _build_symbols(self) -> str:
        if not self.model.symbols:
            return ""
        lines = ["<symbols>"]
        for s in self.model.symbols:
            attr_str = " " + ", ".join([f"{k}={v}" for k, v in s.attrs.items()]) if s.attrs else ""
            lines.append(f"{s.name}:{s.unit_uid} {s.kind}{attr_str}")
        lines.append("</symbols>")
        return "\n".join(lines)

    def _build_layout(self) -> str:
        if not self.model.layout_lines:
            return ""
        lines = ["<layout>"] + self.model.layout_lines + ["</layout>"]
        return "\n".join(lines)

    def _build_snippets(self) -> str:
        if not self.model.snippets:
            return ""
        lines = ["<code-snippets>"]
        for uid, content in self.model.snippets:
            lines.append(f'<snippet unit="{uid}">')
            lines.append("<![CDATA[")
            lines.append(content.strip())
            lines.append("]]>")
            lines.append("</snippet>")
        lines.append("</code-snippets>")
        return "\n".join(lines)
```

---

## 3) 修改 `pirgen.py` 的 `resolve_dependencies`（非常关键）

你现在的 `resolve_dependencies(model)` 是直接改 `model.dependencies` 里 `dep.target`。
但升级后真正用于输出的是 **pool**（`dep_pool_items`）+ **refs**，所以你需要把“消歧逻辑”作用在 pool 上（否则 builder 输出仍是旧 target）。

### ✅ 最稳妥做法：在 resolve 时同时更新 pool 和映射

实现思路：

* 遍历 `model.dep_pool_items`
* 对 target 是 `[name]` 的，尝试解析成 `uX#name`
* 如果变了：

  * pool 里的 key 变了 → dX 可能需要重新分配
  * 同时所有 refs 里引用旧 dX 的要改成新 dX

这一步做“全量重建”最简单、最不容易出错：
把当前 refs 表和 pool 全部“重新喂一遍 intern”。

### ✅ 直接可用版本（替换 `resolve_dependencies`）

```python
def resolve_dependencies(model):
    """
    v0.3 版本：对 dependency-pool 做消歧，然后重建 pool + refs，保证输出一致。
    """
    print("Resolving dependencies (v0.3)...")

    symbol_map = {}
    for sym in model.symbols:
        symbol_map[sym.name] = sym.unit_uid

    # 1) 收集“当前 unit->(verb,target)”的使用关系
    unit_edges = {}  # uX -> list[(verb,target)]
    for uid, dids in model.dep_refs.items():
        unit_edges[uid] = []
        for did in dids:
            # did -> (verb,target)
            # 在 dep_pool_items 里找：为了效率可做个字典
            pass

    did_to_vt = {did: (verb, target) for did, verb, target in model.dep_pool_items}

    for uid, dids in model.dep_refs.items():
        edges = []
        for did in dids:
            verb, target = did_to_vt[did]
            # 消歧：把 [name] -> uX#name
            if target.startswith('[') and target.endswith(']'):
                raw_name = target[1:-1]
                if raw_name in symbol_map:
                    target_uid = symbol_map[raw_name]
                    target = f"{target_uid}#{raw_name}"
            edges.append((verb, target))
        unit_edges[uid] = edges

    # 2) 清空并重建 pool + refs（稳定且一致）
    model._dep_key_to_did.clear()
    model.dep_pool_items.clear()
    model.dep_refs.clear()

    for uid in sorted(unit_edges.keys(), key=lambda x: int(x[1:])):
        for verb, target in unit_edges[uid]:
            model.add_dependency(uid, verb, target)

    print("  - Dependency pool & refs rebuilt.")
```

> 这个实现里我直接用 `model.add_dependency` 重建，所以去重/编号策略仍由 model 控制，非常干净。

---

## 4) PythonAnalyzer：可选增强（让 import 更像“内部引用”，不是全是外部）

你现在 `import` 都写成 `[module]`，这会导致：

* 项目内部模块也变成外部依赖
* `resolve_dependencies` 只能解析 `[symbol]`，解析不了 `[core.project_model]` 这种模块依赖

增强方向（可选，但很值）：

* `import core.project_model` 若能映射到某个 unit（比如 `core/project_model.py`）
  你就可以直接产出：`import:u8`（内部单元依赖），而不是 `[core.project_model]`

你现在 `ProjectModel` 有 `get_uid_by_path(path)`，但没有 “module -> path” 的索引。
如果你愿意做这一步，我建议在 scan 时建立一个 `module_name -> uid` 映射（按 rel_path 推导 Python module 名），然后 PythonAnalyzer 解析 import 时尝试命中它。

不过这步不做也不影响 v0.3 合规，只是精度更高。

---

## 5) 一句话验证你升级是否成功

升级后生成的 `.pir` 文件里应该出现：

* 有 `<dependency-pool>` 区块
* `<dependencies>` 里面只有 `->refs:[d...]`
* 同一个 `[os]` 这种依赖只在 pool 里出现一次，但可能被多个 unit 引用

---

如果你想，我还能顺手帮你把 **dX 编号稳定化**（按 `verb:target` 字典序编号，保证每次生成 diff 极小），以及把 Python import 尽可能解析成内部 `uX`。你只要告诉我：你更希望 dX 是“首次出现顺序”还是“排序稳定顺序”。
