import networkx as nx

# Tworzenie grafu
from src.dijkstra.Colors import get_combined_color_list
from src.dijkstra.updateGraphLenth import update_edge_lengths
from src.dijkstra.dijkstraAlghoritm import dijkstra

graph = nx.Graph()

# Dodawanie wierzchołków
graph.add_node('A', pos=(0, 0), radius=1, color=['red'])
graph.add_node('B', pos=(1, 1), radius=2, color=['blue'])
graph.add_node('C', pos=(2, 2), radius=1, color=['green'])
graph.add_node('D', pos=(3, 3), radius=1, color=['pink'])
graph.add_node('E', pos=(4, 4), radius=1, color=['yellow'])

# Dodawanie krawędzi
graph.add_edge('A', 'B', length=2, area=4, color=['red'])
graph.add_edge('A', 'D', length=4, area=8, color=['black'])
graph.add_edge('B', 'C', length=3, area=6, color=['blue'])
graph.add_edge('B', 'D', length=3, area=6, color=['yellow'])
graph.add_edge('C', 'E', length=2, area=4, color=['violet'])
graph.add_edge('D', 'C', length=3, area=6, color=['green'])
graph.add_edge('D', 'E', length=4, area=8, color=['white'])

# Wywołanie algorytmu Dijkstry
start_node = 'A'
target_node = 'C'
update_edge_lengths(graph)
shortest_distance, shortest_path, path_colors = dijkstra(graph, start_node, target_node)

combined_color_list = get_combined_color_list(graph, shortest_path, path_colors)

# Wyświetlanie wyników
print(f"Najkrótsza odległość od wierzchołka {start_node} do wierzchołka {target_node}: {shortest_distance}")
print("Najkrótsza ścieżka:", shortest_path)
print("Kolory ścieżek:", path_colors)
print("Kolory:", combined_color_list)
