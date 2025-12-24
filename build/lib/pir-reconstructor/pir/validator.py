from typing import List, Set, Dict
from pir_reconstructor.pir.model import Unit, Symbol, Dependency, DependencyEdge, PIRAST

class ValidationError(Exception):
    """Raised when PIR validation fails."""
    pass

def validate_pir(pir: PIRAST) -> None:
    """Validate the PIR AST structure and references."""
    _validate_units(pir.units)
    _validate_symbols(pir.symbols, pir.unit_map)
    _validate_dependencies(pir.dependencies)
    _validate_edges(pir.edges, pir.unit_map, pir.symbols)

def _validate_units(units: List[Unit]) -> None:
    """Validate unit definitions."""
    uid_set: Set[str] = set()

    for unit in units:
        # Check unique uid
        if unit.uid in uid_set:
            raise ValidationError(f"Duplicate unit uid: {unit.uid}")
        uid_set.add(unit.uid)

        # Check uid format
        if not unit.uid.startswith('u'):
            raise ValidationError(f"Invalid unit uid format: {unit.uid}")

        # Check valid type
        valid_types = {'PY', 'C', 'JAVA', 'ASM', 'LD', 'RS'}
        if unit.type not in valid_types:
            raise ValidationError(f"Invalid unit type: {unit.type}")

def _validate_symbols(symbols: List[Symbol], unit_map: Dict[str, Unit]) -> None:
    """Validate symbol definitions and their references."""
    for sym in symbols:
        # Check unit reference exists
        if sym.unit not in unit_map:
            raise ValidationError(f"Symbol {sym.name} references non-existent unit: {sym.unit}")

        # Check valid kind
        valid_kinds = {'func', 'class', 'var', 'const'}
        if sym.kind not in valid_kinds:
            raise ValidationError(f"Invalid symbol kind: {sym.kind}")

def _validate_dependencies(deps: List[Dependency]) -> None:
    """Validate dependency definitions."""
    did_set: Set[str] = set()

    for dep in deps:
        # Check unique did
        if dep.did in did_set:
            raise ValidationError(f"Duplicate dependency id: {dep.did}")
        did_set.add(dep.did)

        # Check did format
        if not dep.did.startswith('d'):
            raise ValidationError(f"Invalid dependency id format: {dep.did}")

        # Check expr format
        if not dep.expr or ':' not in dep.expr:
            raise ValidationError(f"Invalid dependency expression: {dep.expr}")

def _validate_edges(edges: List[DependencyEdge], unit_map: Dict[str, Unit], symbols: List[Symbol]) -> None:
    """Validate dependency edges and their references."""
    for edge in edges:
        # Check source unit exists
        if edge.src_unit not in unit_map:
            raise ValidationError(f"Edge references non-existent source unit: {edge.src_unit}")

        # Check destination unit or symbol exists
        if edge.dst_unit and edge.dst_unit not in unit_map:
            raise ValidationError(f"Edge references non-existent destination unit: {edge.dst_unit}")

        if edge.dst_symbol:
            # Verify symbol exists
            symbol_exists = any(s.name == edge.dst_symbol for s in symbols)
            if not symbol_exists:
                raise ValidationError(f"Edge references non-existent symbol: {edge.dst_symbol}")

        # Check at least one destination is specified
        # For module imports, dst_unit and dst_symbol can be None if module is specified
        if not edge.dst_unit and not edge.dst_symbol and not edge.module:
            raise ValidationError(f"Edge must specify either dst_unit, dst_symbol, or module")
