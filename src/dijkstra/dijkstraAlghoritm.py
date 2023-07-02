import sys


def dijkstra(graph, start, target):
    distances = {node: sys.maxsize for node in graph.nodes}
    distances[start] = 0
    visited = set()
    previous_vertices = {}
    path_colors = {}

    while len(visited) < len(graph.nodes):
        min_distance = sys.maxsize
        min_node = None

        # Wybieranie wierzchołka o najmniejszej odległości spośród nieodwiedzonych
        for node in graph.nodes:
            if node not in visited and distances[node] < min_distance:
                min_distance = distances[node]
                min_node = node

        # Dodanie odwiedzonego wierzchołka do zbioru
        visited.add(min_node)

        # Aktualizacja odległości dla sąsiadów
        for neighbor in graph.neighbors(min_node):
            edge_length = graph[min_node][neighbor]['length']
            edge_area = graph[min_node][neighbor]['area']
            distance = distances[min_node] + edge_length
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_vertices[neighbor] = min_node
                path_colors[neighbor] = graph[min_node][neighbor]['color']

    path = []
    current_node = target
    while current_node != start:
        path.insert(0, current_node)
        current_node = previous_vertices[current_node]
    path.insert(0, start)

    colors = []
    for i in range(len(path) - 1):
        source = path[i]
        target = path[i + 1]
        edge_color = path_colors[target]
        colors.extend(edge_color)

    return distances[target], path, colors
