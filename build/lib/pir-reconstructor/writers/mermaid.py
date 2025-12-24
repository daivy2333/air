def emit_mermaid(edges, units):
    """Generate Mermaid diagram from dependency edges."""
    lines = ["graph TD"]

    # Track defined nodes to avoid duplicates
    defined_nodes = set()

    # Define unit nodes first
    for unit in units:
        node_id = f"u{unit.uid[1:]}"
        label = unit.path
        lines.append(f"  {node_id}[\"{label}\"]")
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
                lines.append(f"  {target_node}[\"{e.dst_symbol}\"]")
                defined_nodes.add(target_node)
        elif e.module:
            # External node: ext:module_name
            # Replace : with _ as per spec
            escaped_module = e.module.replace(":", "_")
            target_node = f"ext:{escaped_module}"
            # Define external node if not already defined
            if target_node not in defined_nodes:
                lines.append(f"  {target_node}[\"{e.module}\"]")
                defined_nodes.add(target_node)
        else:
            continue

        # Determine edge style based on dep_kind
        if e.dep_kind == "import":
            line_style = "==="
        elif e.dep_kind == "refs":
            line_style = "-->"
        elif e.dep_kind == "call":
            line_style = "-.->"
        elif e.dep_kind == "include":
            line_style = "-.-"
        else:
            line_style = "-->"

        # Generate edge
        src_node = f"u{e.src_unit[1:]}"
        lines.append(f"  {src_node} {line_style}|{e.dep_kind}| {target_node}")

    return "\n".join(lines)
