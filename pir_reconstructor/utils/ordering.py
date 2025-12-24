from typing import List, Set, Dict
from pir.model import Unit, DependencyEdge

def topological_sort(units: List[Unit], edges: List[DependencyEdge]) -> List[Unit]:
    """
    Perform topological sort on units based on dependency edges.
    Returns units in an order where dependencies come before dependents.
    """
    # Build adjacency list and in-degree count
    graph: Dict[str, List[str]] = {u.uid: [] for u in units}
    in_degree: Dict[str, int] = {u.uid: 0 for u in units}

    # Build graph from edges
    for edge in edges:
        if edge.dst_unit and edge.dst_unit in graph:
            graph[edge.dst_unit].append(edge.src_unit)
            in_degree[edge.src_unit] += 1

    # Initialize queue with nodes having no dependencies
    queue = [uid for uid, degree in in_degree.items() if degree == 0]
    result: List[Unit] = []

    # Process nodes in topological order
    unit_map = {u.uid: u for u in units}

    while queue:
        # Sort queue for deterministic output
        queue.sort()
        current = queue.pop(0)
        result.append(unit_map[current])

        # Decrease in-degree for dependent nodes
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check for cycles
    if len(result) != len(units):
        raise ValueError("Circular dependency detected in units")

    return result

def stable_sort_by_uid(units: List[Unit]) -> List[Unit]:
    """
    Sort units by their uid in a stable, deterministic manner.
    """
    return sorted(units, key=lambda u: int(u.uid[1:]))
