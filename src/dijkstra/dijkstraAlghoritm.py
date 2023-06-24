import sys


def check_if_is_in_target(vertex, target):
    if vertex == target:
        return True
    return False


def update_distances(graph, distances, min_vertex):
    for neighbor, weight in graph[min_vertex].items():
        distance = distances[min_vertex] + weight
        if distance < distances[neighbor]:
            distances[neighbor] = distance


def dijkstra(graph, start, target):
    distances = {vertex: sys.maxsize for vertex in graph}
    distances[start] = 0
    visited = []

    while len(visited) < len(graph):
        min_distance = sys.maxsize
        min_vertex = None

        # Wybieranie wierzchołka o najmniejszej odległości spośród nieodwiedzonych
        for vertex in graph:
            if vertex not in visited and distances[vertex] < min_distance:
                min_distance = distances[vertex]
                min_vertex = vertex

        # Dodanie odwiedzonego wierzchołka do listy
        visited.append(min_vertex)

        if check_if_is_in_target(min_vertex, target):
            return distances[target]

        if min_vertex is not None:
            update_distances(graph, distances, min_vertex)

    return distances[target]
