# core/project_model.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set

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
        self.dependencies: List[Dependency] = []
        self.symbols: List[Symbol] = []
        
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

    def add_dependency(self, src_uid: str, verb: str, target: str):
        self.dependencies.append(Dependency(src_uid, verb, target))

    def get_uid_by_path(self, path: str) -> Optional[str]:
        return self._path_to_uid.get(path)