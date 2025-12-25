from typing import List, Dict, Optional
from .model import Unit, Symbol, Dependency, DependencyEdge, PIRAST

def parse_pir(file_path: str) -> PIRAST:
    """Parse PIR XML-like text file into AST."""
    import re

    ast = PIRAST()

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all blocks at once using regex for better performance
    pattern = r'<(units|symbols|dependencies|dependency-pool)>(.*?)</\1>'
    blocks = dict(re.findall(pattern, content, re.DOTALL))

    # Parse units
    ast.units = _parse_units(blocks.get('units', ''))
    ast.unit_map = {u.uid: u for u in ast.units}

    # Parse symbols
    ast.symbols = _parse_symbols(blocks.get('symbols', ''), ast.unit_map)

    # Parse dependencies
    ast.dependencies = _parse_dependencies(blocks.get('dependency-pool', ''))

    # Parse dependency edges
    ast.edges = _parse_edges(blocks.get('dependencies', ''), ast.unit_map)

    return ast

def _parse_units(content: str) -> List[Unit]:
    """Extract all unit definitions from PIR content."""
    units = []

    # Parse each unit line
    for line in filter(None, (line.strip() for line in content.split('\n'))):
        # Parse: u0: errors.py type=PY role=lib module=pir-reconstructor
        parts = line.split()
        if len(parts) < 5:
            continue

        # Extract uid
        uid_part = parts[0]
        if ':' not in uid_part:
            continue
        uid = uid_part.split(':')[0]

        # Extract path (everything before 'type=')
        path_part = ' '.join(parts[1:])
        type_idx = path_part.find('type=')
        if type_idx == -1:
            continue
        path = path_part[:type_idx].strip()

        # Extract type, role, module
        type_ = None
        role = None
        module = None

        for part in parts[1:]:
            if part.startswith('type='):
                type_ = part[5:]
            elif part.startswith('role='):
                role = part[5:]
            elif part.startswith('module='):
                module = part[7:]

        if type_ and role and module:
            units.append(Unit(
                uid=uid,
                path=path,
                type=type_.upper(),
                role=role,
                module=module
            ))

    return units

def _parse_symbols(content: str, unit_map: Dict[str, Unit]) -> List[Symbol]:
    """Extract all symbol definitions from PIR content."""
    symbols = []

    # Parse each symbol line
    for line in filter(None, (line.strip() for line in content.split('\n'))):
        # Parse: ReconstructionError:u0 class
        parts = line.split()
        if len(parts) < 2:
            continue

        # Extract name and unit
        name_unit = parts[0]
        if ':' not in name_unit:
            continue
        name, unit = name_unit.split(':', 1)

        # Extract kind
        kind = parts[1] if len(parts) > 1 else None

        # Extract attributes
        attrs = {}
        for part in parts[2:]:
            if '=' in part:
                key, value = part.split('=', 1)
                attrs[key] = value

        if kind and unit in unit_map:
            symbols.append(Symbol(
                name=name,
                unit=unit,
                kind=kind,
                attributes=attrs
            ))

    return symbols

def _parse_dependencies(content: str) -> List[Dependency]:
    """Extract all dependency definitions from PIR content."""
    dependencies = []

    # Parse each dependency line
    for line in filter(None, (line.strip() for line in content.split('\n'))):
        # Parse: d0: import:[errors]
        parts = line.split(':', 1)
        if len(parts) != 2:
            continue

        did, expr = parts
        dependencies.append(Dependency(
            did=did.strip(),
            expr=expr.strip()
        ))

    return dependencies

def _parse_edges(content: str, unit_map: Dict[str, Unit]) -> List[DependencyEdge]:
    """Extract all dependency edges from PIR content."""
    edges = []

    # Build dependency pool map
    dep_pool = _parse_dependency_pool(content)

    # Parse each dependency line
    for line in filter(None, (line.strip() for line in content.split('\n'))):
        # Parse: u1->refs:[d10 d2 d3 d7 d0]
        if '->' not in line or ':' not in line:
            continue

        src_part, rest = line.split('->', 1)
        src_unit = src_part.strip()

        # Extract dep_kind and dependency list
        if ':' not in rest:
            continue

        dep_kind_part, deps_list_part = rest.split(':', 1)
        dep_kind = dep_kind_part.strip()

        # Parse dependency list [d10 d2 d3 d7 d0]
        deps_list = deps_list_part.strip()
        if deps_list.startswith('[') and deps_list.endswith(']'):
            deps_list = deps_list[1:-1]
            dep_ids = deps_list.split()

            # Create edges for each dependency
            for dep_id in dep_ids:
                if dep_id in dep_pool:
                    # Resolve dependency from pool
                    dep_expr = dep_pool[dep_id]
                    edge = _resolve_dependency(dep_expr, src_unit, dep_kind)
                    if edge:
                        edges.append(edge)

    return edges

def _parse_dependency_pool(content: str) -> Dict[str, str]:
    """Parse dependency pool and return mapping from dep_id to expression."""
    pool = {}

    for line in filter(None, (line.strip() for line in content.split('\n'))):
        # Parse: d0: import:[errors]
        parts = line.split(':', 1)
        if len(parts) != 2:
            continue

        did, expr = parts
        pool[did.strip()] = expr.strip()

    return pool

def _resolve_dependency(dep_expr: str, src_unit: str, dep_kind: str) -> Optional[DependencyEdge]:
    """Resolve a dependency expression into a DependencyEdge."""
    # Parse different dependency types
    if dep_expr.startswith('import:['):
        # Module import: import:[errors]
        module = dep_expr[8:-1]
        return DependencyEdge(
            src_unit=src_unit,
            dst_unit=None,  # Module imports don't have specific target units
            dst_symbol=None,
            module=module,
            dep_kind=dep_kind,
            target_kind='module'
        )
    elif dep_expr.startswith('ext:['):
        # External dependency: ext:[stdlib:py]
        return DependencyEdge(
            src_unit=src_unit,
            dst_unit=None,
            dst_symbol=dep_expr[4:-1],
            module=None,
            dep_kind=dep_kind,
            target_kind='external'
        )
    elif dep_expr.startswith('sym:'):
        # Symbol reference: sym:u3#ProjectModel
        parts = dep_expr[4:].split('#', 1)
        if len(parts) == 2:
            unit_id, symbol_name = parts
            return DependencyEdge(
                src_unit=src_unit,
                dst_unit=unit_id,
                dst_symbol=symbol_name,
                module=None,
                dep_kind=dep_kind,
                target_kind='symbol'
            )
    elif dep_expr.startswith('ref:'):
        # Unit reference: ref:u3
        unit_id = dep_expr[4:]
        return DependencyEdge(
            src_unit=src_unit,
            dst_unit=unit_id,
            dst_symbol=None,
            module=None,
            dep_kind=dep_kind,
            target_kind='unit'
        )

    return None
