def emit_graphviz(edges, units):
    """Generate Graphviz DOT format from dependency edges."""
    lines = ["digraph PIR {"]
    lines.append("  rankdir=LR;")
    lines.append("  node [fontname=\"monospace\"];")
    lines.append("  edge [fontname=\"monospace\"];")
    lines.append("  fontname=\"monospace\";")
    lines.append("")

    # Track defined nodes to avoid duplicates
    defined_nodes = set()

    # Define unit nodes first
    for unit in units:
        node_id = f"u{unit.uid[1:]}"
        label = unit.path
        lines.append(f'  {node_id} [label="{label}", shape=box, style=filled, fillcolor="#cce5ff"];')
        defined_nodes.add(node_id)

    lines.append("")

    # Process edges
    for e in edges:
        # Determine target node and type
        if e.dst_unit:
            target_node = f"u{e.dst_unit[1:]}"
            target_type = "unit"
        elif e.dst_symbol:
            # Symbol node: uX#SymbolName
            target_node = f"{e.src_unit[1:]}#{e.dst_symbol}"
            target_type = "symbol"
            # Define symbol node if not already defined
            if target_node not in defined_nodes:
                lines.append(f'  {target_node} [label="{e.dst_symbol}", shape=ellipse, style="filled,dashed", fillcolor="#d4edda"];')
                defined_nodes.add(target_node)
        elif e.module:
            # External node: ext:module_name
            # Replace : with _ as per spec
            escaped_module = e.module.replace(":", "_")
            target_node = f"ext:{escaped_module}"
            target_type = "external"
            # Define external node if not already defined
            if target_node not in defined_nodes:
                lines.append(f'  {target_node} [label="{e.module}", shape=octagon, style="filled,dotted", fillcolor="#f8d7da"];')
                defined_nodes.add(target_node)
        else:
            continue

        # Determine edge style based on dep_kind
        if e.dep_kind == "import":
            edge_style = "solid"
            edge_color = "#007bff"
        elif e.dep_kind == "refs":
            edge_style = "solid"
            edge_color = "#6c757d"
        elif e.dep_kind == "call":
            edge_style = "dashed"
            edge_color = "#28a745"
        elif e.dep_kind == "include":
            edge_style = "dotted"
            edge_color = "#ffc107"
        else:
            edge_style = "solid"
            edge_color = "#6c757d"

        # Generate edge
        src_node = f"u{e.src_unit[1:]}"
        lines.append(f'  {src_node} -> {target_node} [label="{e.dep_kind}", style={edge_style}, color="{edge_color}"];')

    lines.append("}")
    return "\n".join(lines)
