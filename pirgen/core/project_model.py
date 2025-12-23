# core/project_model.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple

@dataclass
class Unit:
    uid: str          # u0, u1
    path: str         # core/init.c
    lang: str         # C, Python
    role: str         # entry, lib
    module: str       # core

@dataclass
class Symbol:
    name: str
    unit_uid: str
    kind: str         # func, var, class
    attrs: Dict[str, str] = field(default_factory=dict)

# 依赖定义仍可保留，但 v0.3 不再需要全局 Dependency 列表
@dataclass
class Dependency:
    src_uid: str
    verb: str         # call, import
    target: str       # u1, [stdio.h], u1#func_name

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
        
        # 布局和代码片段暂存
        self.layout_lines: List[str] = []
        self.snippets: List[tuple] = [] # (unit_uid, content)

    def add_unit(self, path: str, lang: str, role: str = "lib", module: str = "common") -> str:
        uid = f"u{len(self.units)}"
        unit = Unit(uid, path, lang, role, module)
        self.units.append(unit)
        self._path_to_uid[path] = uid
        self.langs.add(lang)
        return uid

    def add_symbol(self, name: str, unit_uid: str, kind: str, **attrs):
        self.symbols.append(Symbol(name, unit_uid, kind, attrs))

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

    def add_dependency(self, src_uid: str, verb: str, target: str):
        # 兼容旧逻辑（可选）
        self.dependencies.append(Dependency(src_uid, verb, target))

        key = f"{verb}:{target}"
        self._all_dep_keys.add(key)
        lst = self._unit_dep_keys.setdefault(src_uid, [])
        if key not in lst:  # 单元内去重 + 稳定顺序
            lst.append(key)

    def get_uid_by_path(self, path: str) -> Optional[str]:
        return self._path_to_uid.get(path)