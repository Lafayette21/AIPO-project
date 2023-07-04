def convert_graph_to_input(graph):
    input_graph = {}

    for node in graph.nodes():
        input_graph[node] = {}

    for edge in graph.edges():
        source, target = edge
        edge_data = graph.edges[edge]
        length = edge_data.get('length', None)
        if target not in input_graph[source]:
            input_graph[source][target] = length

    return input_graph
