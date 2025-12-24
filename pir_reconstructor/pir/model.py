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
    module: Optional[str]  # For module imports like import:[errors]
    dep_kind: str
    target_kind: str


class PIRAST:
    """
    Root AST object for PIR.
    Parser fills it, Validator consumes it, Emitters read it.
    """
    def __init__(self):
        self.units: List[Unit] = []
        self.symbols: List[Symbol] = []
        self.dependencies: List[Dependency] = []
        self.edges: List[DependencyEdge] = []
        self.unit_map: Dict[str, Unit] = {}
