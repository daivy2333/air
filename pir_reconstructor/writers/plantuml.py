def emit_plantuml(edges, units):
    """Generate PlantUML diagram from dependency edges."""
    lines = ["@startuml"]
    lines.append("left to right direction")
    lines.append("skinparam monochrome true")
    lines.append("skinparam shadowing false")
    lines.append("skinparam nodesep 10")
    lines.append("skinparam ranksep 20")
    lines.append("")

    # Track defined nodes to avoid duplicates
    defined_nodes = set()

    # Define unit nodes first
    for unit in units:
        node_id = f"u{unit.uid[1:]}"
        label = unit.path
        lines.append(f'component "{label}" as {node_id} #cce5ff')
        defined_nodes.add(node_id)

    lines.append("")

    # Process edges
    for e in edges:
        # Determine target node and type
        if e.dst_unit:
            target_node = f"u{e.dst_unit[1:]}"
        elif e.dst_symbol:
            # Symbol node: uX#SymbolName
            target_node = f"{e.src_unit[1:]}#{e.dst_symbol}"
            # Define symbol node if not already defined
            if target_node not in defined_nodes:
                lines.append(f'interface "{e.dst_symbol}" as {target_node} #d4edda')
                defined_nodes.add(target_node)
        elif e.module:
            # External node: ext:module_name
            # Replace : with _ as per spec
            escaped_module = e.module.replace(":", "_")
            target_node = f"ext:{escaped_module}"
            # Define external node if not already defined
            if target_node not in defined_nodes:
                lines.append(f'node "{e.module}" as {target_node} #f8d7da')
                defined_nodes.add(target_node)
        else:
            continue

        # Determine arrow style based on dep_kind
        if e.dep_kind == "import":
            arrow = "-->"
        elif e.dep_kind == "refs":
            arrow = "-->"
        elif e.dep_kind == "call":
            arrow = "..>"
        elif e.dep_kind == "include":
            arrow = "..|>"
        else:
            arrow = "-->"

        # Generate edge
        src_node = f"u{e.src_unit[1:]}"
        lines.append(f'{src_node} {arrow} {target_node} : {e.dep_kind}')

    lines.append("@enduml")
    return "\n".join(lines)
