# core/project_model.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple


# -------------------------
# Core IR Nodes
# -------------------------
@dataclass(frozen=True)
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


@dataclass(frozen=True)
class Dependency:
    src_uid: str
    verb: str
    target: str


# -------------------------
# Project Model
# -------------------------
class ProjectModel:
    def __init__(self, name: str, root: str, profile: str):
        self.name = name
        self.root = root
        self.profile = profile  # Legacy profile field (kept for backward compatibility)

        self.langs: Set[str] = set()

        # ---- Units ----
        self.units: List[Unit] = []
        self._path_to_uid: Dict[str, str] = {}

        # ---- Symbols ----
        self.symbols: List[Symbol] = []

        # ---- Dependencies (two-phase) ----
        self._unit_dep_keys: Dict[str, List[str]] = {}
        self._all_dep_keys: Set[str] = set()

        self.dep_pool_items: List[Tuple[str, str, str]] = []
        self.dep_refs: Dict[str, List[str]] = {}

        self.deps_finalized: bool = False

        # ---- Profiles (v0.4 extension) ----
        self.profiles: Dict[str, Dict] = {}  # profile_name -> {confidence, tags}
        self.active_profile: Optional[str] = None  # Current active profile

        # ---- Optional extensions ----
        self.layout_lines: List[str] = []
        self.snippets: List[Tuple[str, str]] = []

    # -------------------------
    # Unit
    # -------------------------
    def add_unit(self, path: str, lang: str, role="lib", module="common") -> str:
        if path in self._path_to_uid:
            return self._path_to_uid[path]

        uid = f"u{len(self.units)}"
        self.units.append(Unit(uid, path, lang, role, module))
        self._path_to_uid[path] = uid
        self.langs.add(lang)
        return uid

    def get_uid_by_path(self, path: str) -> Optional[str]:
        return self._path_to_uid.get(path)

    # -------------------------
    # Symbol
    # -------------------------
    def add_symbol(self, name: str, unit_uid: str, kind: str, **attrs):
        self.symbols.append(Symbol(name, unit_uid, kind, attrs))

    # -------------------------
    # Dependency
    # -------------------------
    def add_dependency(self, src_uid: str, verb: str = None, target: str = None, **kwargs):
        """
        兼容旧接口：
        - add_dependency(uid, verb, target)
        - add_dependency(uid, kind=..., target=...)
        """
        if self.deps_finalized:
            raise RuntimeError("Cannot add dependency after finalize")

        # 兼容旧 kind 参数
        if verb is None:
            verb = kwargs.get("kind")

        if verb is None or target is None:
            raise ValueError("Dependency requires verb/kind and target")

        key = f"{verb}:{target}"
        self._all_dep_keys.add(key)
        # Use set for deduplication during add
        if src_uid not in self._unit_dep_keys:
            self._unit_dep_keys[src_uid] = []
        # Check for duplicates efficiently
        if key not in self._unit_dep_keys[src_uid]:
            self._unit_dep_keys[src_uid].append(key)


    # -------------------------
    # Finalize Dependencies
    # -------------------------
    def finalize_dependencies(self):
        if self.deps_finalized:
            return

        sorted_keys = sorted(self._all_dep_keys)
        key_to_did = {k: f"d{i}" for i, k in enumerate(sorted_keys)}

        self.dep_pool_items = []
        for k in sorted_keys:
            verb, target = k.split(":", 1)
            self.dep_pool_items.append((key_to_did[k], verb, target))

        self.dep_refs = {}
        for uid, keys in self._unit_dep_keys.items():
            self.dep_refs[uid] = [key_to_did[k] for k in keys]

        self.deps_finalized = True
