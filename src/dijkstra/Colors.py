def get_combined_color_list(graph, node_names, edge_colors):
    combined_colors = []
    for i, node_name in enumerate(node_names):
        combined_colors.append(graph.nodes[node_name]['color'][0]) #TODO: Append all not one
        if i < len(edge_colors):
            combined_colors.append(edge_colors[i])
    return combined_colors