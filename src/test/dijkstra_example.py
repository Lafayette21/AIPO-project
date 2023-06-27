import sys

from src.dijkstra.dijkstraAlghoritm import dijkstra

graph = {
    'A': {'B': 2, 'D': 4},
    'B': {'C': 3, 'D': 3},
    'C': {'E': 2},
    'D': {'C': 3, 'E': 4},
    'E': {},
}

start_vertex = 'A'
target_vertex = 'C'
shortest_distance = dijkstra(graph, start_vertex, target_vertex)

if shortest_distance == sys.maxsize:
    shortest_distance = None

print(f'Najkrótsza odległość z wierzchołka {start_vertex} do wierzchołka {target_vertex}: {shortest_distance}')
