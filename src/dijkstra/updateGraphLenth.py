def update_edge_lengths(graph):
    for u, v in graph.edges:
        edge_length = graph[u][v]['length']
        edge_area = graph[u][v]['area']
        if edge_length == 0:
            updated_length = 0
        else:
            updated_length = edge_length / (0.1 * edge_area / (edge_length + 1))
        graph[u][v]['length'] = updated_length
