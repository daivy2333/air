可以，**排序稳定顺序**最稳的做法是：**先收集依赖 key（verb:target），不立刻分配 dX；在 build 前一次性按 key 排序分配 d0..dn**。这样同一项目在同样输入下，每次生成的 d 编号都一致，diff 极小。

下面给你一套“改动少、行为清晰”的落地方案（只动 `ProjectModel` + `PIRBuilder` + `resolve_dependencies` 一点点）。

---

## 方案：两阶段依赖收集 → 稳定编号 → 输出

### 核心数据结构变化

* 收集阶段：unit 只记录 **依赖 key**（`verb:target`），不记录 dX
* finalize 阶段：对所有 key **排序**，映射成 `d0..`
* 输出阶段：pool 按排序后的 key 输出；refs 按 `d` 输出

---

## 1) 改 `core/project_model.py`

把你现在的“即时分配 did”改成“记录 key + finalize 分配”。

直接按下面方式改（保留你原来的 dataclass 不影响）：

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

        # --- v0.3 stable deps (two-phase) ---
        self._unit_dep_keys: Dict[str, List[str]] = {}   # uX -> ["import:[os]", ...] keep insertion order per unit
        self._all_dep_keys: Set[str] = set()             # global unique keys

        # finalize() 后填充（供 builder 使用）
        self.dep_pool_items: List[Tuple[str, str, str]] = []  # (dX, verb, target) in stable order
        self.dep_refs: Dict[str, List[str]] = {}              # uX -> [dX...]

        # 如果别处还用到旧字段，可先留着（不影响输出）
        self.dependencies: List[Dependency] = []

        self.layout_lines: List[str] = []
        self.snippets: List[tuple] = []

    def add_unit(self, path: str, lang: str, role: str = "lib", module: str = "common") -> str:
        uid = f"u{len(self.units)}"
        self.units.append(Unit(uid, path, lang, role, module))
        self._path_to_uid[path] = uid
        self.langs.add(lang)
        return uid

    def add_symbol(self, name: str, unit_uid: str, kind: str, **attrs):
        self.symbols.append(Symbol(name, unit_uid, kind, attrs))

    def add_dependency(self, src_uid: str, verb: str, target: str):
        # 兼容旧逻辑（可选）
        self.dependencies.append(Dependency(src_uid, verb, target))

        key = f"{verb}:{target}"
        self._all_dep_keys.add(key)
        lst = self._unit_dep_keys.setdefault(src_uid, [])
        if key not in lst:  # 单元内去重 + 稳定顺序
            lst.append(key)

    def finalize_dependencies(self):
        """
        生成稳定的 dX：按 key(verb:target) 字典序排序。
        调用时机：resolve_dependencies 之后、builder 输出之前。
        """
        # 1) 稳定排序 key
        sorted_keys = sorted(self._all_dep_keys)

        # 2) key -> dX
        key_to_did = {k: f"d{i}" for i, k in enumerate(sorted_keys)}

        # 3) 生成 dependency-pool（按排序后的 key 顺序）
        self.dep_pool_items = []
        for k in sorted_keys:
            verb, target = k.split(":", 1)
            did = key_to_did[k]
            self.dep_pool_items.append((did, verb, target))

        # 4) 生成 refs（按 unit 的 key 顺序映射到 did；可选再按 did 排序）
        self.dep_refs = {}
        for uid, keys in self._unit_dep_keys.items():
            self.dep_refs[uid] = [key_to_did[k] for k in keys]

    def get_uid_by_path(self, path: str) -> Optional[str]:
        return self._path_to_uid.get(path)
```

---

## 2) 改 `core/pir_builder.py`

在 `build()` 前调用一次 `model.finalize_dependencies()`，并新增 pool 区块、dependencies 改 refs。

```python
# core/pir_builder.py
from .project_model import ProjectModel

class PIRBuilder:
    def __init__(self, model: ProjectModel):
        self.model = model

    def build(self) -> str:
        # ✅ 稳定编号在输出前一次性完成
        self.model.finalize_dependencies()

        sections = [
            "<pir>",
            self._build_meta(),
            self._build_units(),
            self._build_dependency_pool(),
            self._build_dependencies(),
            self._build_symbols(),
            self._build_layout(),
            self._build_snippets(),
            "</pir>"
        ]
        return "\n".join(filter(None, sections))

    # meta / units / symbols / layout / snippets 你的原实现可复用

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
        for uid in sorted(self.model.dep_refs.keys(), key=lambda x: int(x[1:])):
            refs = self.model.dep_refs[uid]
            if refs:
                lines.append(f"{uid}->refs:[{' '.join(refs)}]")
        lines.append("</dependencies>")
        return "\n".join(lines)
```

---

## 3) 改 `pirgen.py` 的 `resolve_dependencies`（让它适配“key 模式”）

你现在在改 `model.dependencies` 里的 dep.target。
但现在真实数据源是 `model._unit_dep_keys`（key 列表）+ `model._all_dep_keys`（集合）。

最简单：**在 resolve 时把 unit_dep_keys 里的 key 替换掉，然后重建 all_dep_keys**。

直接替换你的 `resolve_dependencies` 为：

```python
def resolve_dependencies(model):
    print("Resolving dependencies...")

    symbol_map = {sym.name: sym.unit_uid for sym in model.symbols}

    resolved = 0
    new_all = set()

    for uid, keys in model._unit_dep_keys.items():
        new_keys = []
        for k in keys:
            verb, target = k.split(":", 1)
            if target.startswith("[") and target.endswith("]"):
                raw = target[1:-1]
                if raw in symbol_map:
                    target = f"{symbol_map[raw]}#{raw}"
                    resolved += 1
            new_k = f"{verb}:{target}"
            new_keys.append(new_k)
            new_all.add(new_k)
        model._unit_dep_keys[uid] = list(dict.fromkeys(new_keys))  # 保序去重

    model._all_dep_keys = new_all
    print(f"  - Resolved {resolved} internal symbol references.")
```

---

## 这样改完你会得到什么效果

* **dX 完全稳定**：由 `sorted(verb:target)` 决定
* 同一依赖（相同 verb+target）只定义一次（pool 去重）
* `<dependencies>` 变成纯 refs 映射，符合 v0.3
* 你现有 analyzer 基本不用动（继续 `add_dependency(uid, "import", "[xxx]")`）

---

如果你愿意再往前走一步（同样保持稳定编号），我建议下一步把 Python 的 `[core.project_model]` 这类 import 尽量解析成 `import:u8`（内部 unit），PIR 会更“项目语义化”。但这属于精度增强，不影响你现在升级 v0.3。

