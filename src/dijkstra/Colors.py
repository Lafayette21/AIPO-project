def get_combined_color_list(graph, node_names, edge_colors):
    combined_colors = []
    for i, node_name in enumerate(node_names):
        colors = graph.nodes[node_name]['color']
        for color in colors:
            combined_colors.append(color)
        if i < len(edge_colors):
            combined_colors.append(edge_colors[i])
    return combined_colors
