def emit_module_graph(pir):
    """Generate Module/Import Graph - shows what modules depend on whom.

    This is a local analysis graph, not the default output.
    It answers: "What does a particular module depend on?"
    """
    lines = ["digraph PIR_Modules {"]
    lines.append("  rankdir=LR;")
    lines.append("  node [fontname=\"monospace\"];")
    lines.append("  edge [fontname=\"monospace\"];")
    lines.append("  fontname=\"monospace\";")
    lines.append("")

    # Group units by module
    module_units = {}
    for unit in pir.units:
        module = unit.module
        if module not in module_units:
            module_units[module] = []
        module_units[module].append(unit)

    # Track defined nodes to avoid duplicates
    defined_nodes = set()

    # Define module nodes
    for module_name in sorted(module_units.keys()):
        # Use first unit's ID as representative
        first_unit = module_units[module_name][0]
        node_id = f"mod_{module_name.replace('.', '_')}"
        lines.append(f'  {node_id} [label="{module_name}", shape=box, style=filled, fillcolor="#cce5ff"];')
        defined_nodes.add(node_id)

    lines.append("")

    # Define stdlib node (merged standard library)
    stdlib_imports = set()
    for e in pir.edges:
        if e.module and e.module in ("sys", "typing", "os", "pathlib", "argparse", "ast", "dataclasses"):
            stdlib_imports.add(e.module)

    if stdlib_imports:
        lines.append('  stdlib [label="Python stdlib", shape=box, style=filled, fillcolor="#f8d7da"];')
        defined_nodes.add("stdlib")

    lines.append("")

    # Process edges - show module-level dependencies
    processed_edges = set()

    for e in pir.edges:
        # Only process import edges
        if e.dep_kind != "import":
            continue

        src_unit = pir.unit_map.get(e.src_unit)
        if not src_unit:
            continue

        src_module = src_unit.module
        src_node = f"mod_{src_module.replace('.', '_')}"

        # Determine target
        if e.dst_unit:
            dst_unit = pir.unit_map.get(e.dst_unit)
            if dst_unit:
                dst_module = dst_unit.module
                dst_node = f"mod_{dst_module.replace('.', '_')}"

                # Skip self-references
                if src_module == dst_module:
                    continue

                # Skip duplicate edges
                edge_key = (src_node, dst_node)
                if edge_key in processed_edges:
                    continue
                processed_edges.add(edge_key)

                lines.append(f'  {src_node} -> {dst_node} [label="import", style=solid, color="#007bff"];')

        elif e.module:
            # Check if it's a stdlib import
            if e.module in ("sys", "typing", "os", "pathlib", "argparse", "ast", "dataclasses"):
                dst_node = "stdlib"

                # Skip duplicate edges
                edge_key = (src_node, dst_node)
                if edge_key in processed_edges:
                    continue
                processed_edges.add(edge_key)

                lines.append(f'  {src_node} -> {dst_node} [label="import", style=solid, color="#007bff"];')

    lines.append("}")
    return "\n".join(lines)
