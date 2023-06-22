import sys

def dijkstra(graph, start, target):
    distances = {vertex: sys.maxsize for vertex in graph}
    distances[start] = 0
    visited = []

    while len(visited) < len(graph):
        min_distance = sys.maxsize
        min_vertex = None

        for vertex in graph:
            if vertex not in visited and distances[vertex] < min_distance:
                min_distance = distances[vertex]
                min_vertex = vertex

        visited.append(min_vertex)

        if min_vertex == target:
            break

        if min_vertex is not None:
            for neighbor, weight in graph[min_vertex].items():
                distance = distances[min_vertex] + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance

    return distances[target]

graph = {
    'A': {'B': 2, 'D': 4},
    'B': {'C': 3, 'D': 3},
    'C': {'E': 2},
    'D': {'C': 3, 'E': 4},
    'E': {},
}

start_vertex = 'C'
target_vertex = 'B'
shortest_distance = dijkstra(graph, start_vertex, target_vertex)

if shortest_distance == sys.maxsize:
    shortest_distance = None

print(f'Najkrótsza odległość z wierzchołka {start_vertex} do wierzchołka {target_vertex}: {shortest_distance}')
