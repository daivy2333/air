def emit_arch_graph(pir):
    """Generate PIR Architecture Graph - shows module structure and core dependency topology.

    This is the default, main, and most important graph.
    It answers: What is the project's "module structure + core dependency topology"?
    """
    lines = ["digraph PIR_Arch {"]
    lines.append("  rankdir=LR;")
    lines.append("  node [fontname=\"monospace\"];")
    lines.append("  edge [fontname=\"monospace\"];")
    lines.append("  fontname=\"monospace\";")
    lines.append("")

    # Track defined nodes to avoid duplicates
    defined_nodes = set()

    # Define unit nodes first
    for unit in pir.units:
        node_id = f"u{unit.uid[1:]}"
        label = unit.path
        lines.append(f'  {node_id} [label="{label}", shape=box, style=filled, fillcolor="#cce5ff"];')
        defined_nodes.add(node_id)

    lines.append("")

    # Process edges - only structural dependencies
    for e in pir.edges:
        # Only show unit-to-unit dependencies (structural)
        if not e.dst_unit or e.dst_symbol:
            continue

        # Only show import/refs dependencies (not call/include)
        if e.dep_kind not in ("import", "refs"):
            continue

        src_node = f"u{e.src_unit[1:]}"
        dst_node = f"u{e.dst_unit[1:]}"

        # Determine edge style
        if e.dep_kind == "import":
            edge_style = "solid"
            edge_color = "#007bff"
        else:  # refs
            edge_style = "solid"
            edge_color = "#6c757d"

        lines.append(f'  {src_node} -> {dst_node} [label="{e.dep_kind}", style={edge_style}, color="{edge_color}"];')

    lines.append("}")
    return "\n".join(lines)
