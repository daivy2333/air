def emit_pipeline_graph(pir):
    """Generate Pipeline/Flow Graph - shows how data/PIR is processed step by step.

    This is a very valuable graph for this project.
    It answers: "How is data/PIR processed step by step?"
    """
    lines = ["digraph PIR_Pipeline {"]
    lines.append("  rankdir=LR;")
    lines.append("  node [fontname=\"monospace\"];")
    lines.append("  edge [fontname=\"monospace\"];")
    lines.append("  fontname=\"monospace\";")
    lines.append("")

    # Identify Layers, Pipeline, and Writers from symbols
    layers = []
    pipeline = None
    writers = []

    for sym in pir.symbols:
        if sym.kind == "class":
            if sym.name.endswith("Layer"):
                layers.append(sym)
            elif sym.name == "ReconstructionPipeline":
                pipeline = sym
            elif any(w in sym.name for w in ("mermaid", "graphviz", "plantuml", "filesystem"):
                writers.append(sym)

    # Track defined nodes
    defined_nodes = set()

    # Define Pipeline node
    if pipeline:
        node_id = f"u{pipeline.unit[1:]}#{pipeline.name}"
        lines.append(f'  {node_id} [label="{pipeline.name}", shape=box, style=filled, fillcolor="#cce5ff"];')
        defined_nodes.add(node_id)

    # Define Layer nodes
    for layer in layers:
        node_id = f"u{layer.unit[1:]}#{layer.name}"
        lines.append(f'  {node_id} [label="{layer.name}", shape=box, style=filled, fillcolor="#cce5ff"];')
        defined_nodes.add(node_id)

    # Define Writers node
    if writers:
        node_id = "Writers"
        lines.append(f'  {node_id} [label="Writers", shape=box, style=filled, fillcolor="#cce5ff"];')
        defined_nodes.add(node_id)

    lines.append("")

    # Infer pipeline flow based on dependencies and naming
    # This is a simplified inference - in production, you'd use more sophisticated analysis

    # Pipeline -> Layers
    if pipeline:
        pipeline_node = f"u{pipeline.unit[1:]}#{pipeline.name}"
        for layer in layers:
            layer_node = f"u{layer.unit[1:]}#{layer.name}"
            lines.append(f'  {pipeline_node} -> {layer_node} [label="uses", style=solid, color="#007bff"];')

    # Layer -> Layer flow (inferred from layer names)
    layer_order = {
        "StructureLayer": 1,
        "InterfaceLayer": 2,
        "RelationLayer": 3,
        "DocumentationLayer": 4,
        "SourceEnrichmentLayer": 5,
        "AuditLayer": 6
    }

    sorted_layers = sorted(layers, key=lambda l: layer_order.get(l.name, 999))
    for i in range(len(sorted_layers) - 1):
        src = sorted_layers[i]
        dst = sorted_layers[i + 1]
        src_node = f"u{src.unit[1:]}#{src.name}"
        dst_node = f"u{dst.unit[1:]}#{dst.name}"
        lines.append(f'  {src_node} -> {dst_node} [label="flow", style=dashed, color="#6c757d"];')

    # Layers -> Writers
    writers_node = "Writers"
    for layer in layers:
        layer_node = f"u{layer.unit[1:]}#{layer.name}"
        lines.append(f'  {layer_node} -> {writers_node} [label="outputs to", style=solid, color="#007bff"];')

    lines.append("}")
    return "\n".join(lines)
