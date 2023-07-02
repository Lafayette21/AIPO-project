import cv2
import numpy as np
import matplotlib.pyplot as plt
import threading
import networkx as nx
import time
from GraphPostProcessing import GraphPostProcessor

#urzywa obraz o wartościach 0 dla tła i 1 dla drug i skrzyrzoań
#zwraca obraz z osobną wartością dla karzdej drogi i skrzyrzoania oraz listy które wartości to skrzyrzowania a które to drogi
class RoadsIntersectionsDetecotr:    
    def run(self, image):
        self.iterator=1
        self.image = image
        self.thread_list = []
        self.graph = nx.Graph()
        self.graph_lock = threading.Lock()
        self.roads_list = []
        self.intersections_list = []
        self.roads_not_connected = {}

        indexes = [np.argwhere(image == 1)[0]]
        nodeName = f"{self.iterator}"
        self.intersections_list.append(self.iterator)
        self.iterator+=1
        with self.graph_lock:
            self.graph.add_node(nodeName, pos=(indexes[0][1], indexes[0][0]), color=[nodeName], radius=1)

        thread = threading.Thread(target=self.color_road, args=(indexes, self.iterator, nodeName))
        self.iterator+=1
        thread.start()
        self.thread_list.append(thread)

        while self.thread_list:
            thread = self.thread_list.pop(0)
            thread.join()
        
        return image
    
    def color_road(self, indexes, value , startNodeName):
        self.roads_list.append(value)
        neighbor_lists=[[]]
        road_end=False

        road_length = 0
        road_area = len(indexes)

        while len(neighbor_lists)==1:
            indexes2 = set([])
            for (x, y) in indexes:
                self.image[x, y] = value
                indexes2.update(self.find_neighbors_with_value((x, y), 1))
            if indexes2:
                indexes = indexes2
                neighbor_lists = self.divide_into_neighbor_lists(indexes)
                road_length+=1
                road_area+=len(indexes)
            else: 
                road_end = True
                break

        intersection_id=self.iterator
        self.iterator+=1
        self.intersections_list.append(intersection_id)
        nodeName = f"{intersection_id}"

        if road_end:
            neighbours_values , neighbours = self.get_neighbors_values_set(indexes)
            neighbours_values.discard(value)
            if neighbours_values:
                if all(elem in self.roads_list for elem in neighbours_values):
                    if value == max([*neighbours_values, value]):
                        pos, radius = self.color_intersection(neighbours.copy(), intersection_id)
                        with self.graph_lock:
                            self.graph.add_node(nodeName, pos=pos, color = [intersection_id], radius=radius)
                            self.graph.add_edge(startNodeName, nodeName, length = road_length, area = road_area, color = [value])
                        for _ in range(10):
                            time.sleep(0.1)
                            for f_value in neighbours_values:
                                if f_value in self.roads_not_connected:
                                    with self.graph_lock:
                                        self.graph.add_edge(nodeName, self.roads_not_connected[f_value]["name"], 
                                                            length = self.roads_not_connected[f_value]["len"],
                                                            area = self.roads_not_connected[f_value]["area"], 
                                                            color = [f_value])
                                        self.roads_not_connected.pop(f_value)
                    else:
                        self.roads_not_connected[value] = {}
                        self.roads_not_connected[value]["name"] = startNodeName
                        self.roads_not_connected[value]["len"] = road_length
                        self.roads_not_connected[value]["area"] = road_area
                else:
                    print("---",neighbours_values)
                    print(self.intersections_list)
            else:
                pos, radius = self.color_intersection(neighbours.copy(), intersection_id)
                with self.graph_lock:
                    self.graph.add_node(nodeName, pos=pos, color = [intersection_id], radius=radius)
                    self.graph.add_edge(startNodeName, nodeName, length = road_length, area = road_area, color = [value])
        else:
            with self.graph_lock:
                self.graph.add_node(nodeName, color = [intersection_id])
                self.graph.add_edge(startNodeName, nodeName, length = road_length, area = road_area, color = [value])
        
            for sub_indexes in neighbor_lists:
                thread = threading.Thread(target=self.color_road, args=(set(sub_indexes.copy()), self.iterator, nodeName))
                self.iterator+=1
                thread.start()
                self.thread_list.append(thread)

            pos, radius = self.color_intersection(indexes.copy(), intersection_id)
            with self.graph_lock:
                self.graph.nodes[nodeName]['pos'] = pos
                self.graph.nodes[nodeName]['radius'] = radius


    def color_intersection(self, indexes, value):
        average_x = np.mean([point[0] for point in indexes])
        average_y = np.mean([point[1] for point in indexes])

        min_x = min(point[0] for point in indexes)
        max_x = max(point[0] for point in indexes)
        min_y = min(point[1] for point in indexes)
        max_y = max(point[1] for point in indexes)

        radius = int(max(max_x - average_x, max_y - average_y, average_x - min_x, average_y- min_y))

        center = (int(average_y), int(average_x))

        cv2.circle(self.image, center, radius, value, thickness=-1)
        # thread = threading.Thread(target=self.drow_circle_with_delay, args=(center,radius,value))
        # thread.start()
        # self.thread_list.append(thread)

        return (center, radius)

    def drow_circle_with_delay(self, center, radius, value):
        time.sleep(0.1)
        cv2.circle(self.image, center, radius, value, thickness=-1)

    def find_neighbors_with_value(self, pixel, value):
        x, y = pixel
        offsets = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if (dx != 0 or dy != 0)]
        neighbors = [(x + dx, y + dy) for dx, dy in offsets]
        neighbors = [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.image.shape[0] and 0 <= ny < self.image.shape[1]]
        neighbors = [(nx, ny) for nx, ny in neighbors if self.image[nx, ny] == value]

        return neighbors
    
    def divide_into_neighbor_lists(self, pixels):
        neighbor_lists = []

        def is_neighbor(coord1, coord2):
            return abs(coord1[0] - coord2[0]) <= 1 and abs(coord1[1] - coord2[1]) <= 1

        for pixel in pixels:
            neighbors = [pixel]
            for i in range(len(neighbor_lists) - 1, -1, -1):
                if any(is_neighbor(pixel, coord) for coord in neighbor_lists[i]):
                    neighbors.extend(neighbor_lists.pop(i))
            neighbor_lists.append(neighbors)

        return neighbor_lists
    
    def get_neighbors_values_set(self,indexes):
        neighbors_set = set()
        neighbors_values_set = set()
        for (x, y) in indexes:
            offsets = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if (dx != 0 or dy != 0)]
            neighbors = [(x + dx, y + dy) for dx, dy in offsets]
            neighbors = [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.image.shape[0] and 0 <= ny < self.image.shape[1]]
            neighbors_set.update(neighbors)
            neighbors_values = [self.image[nx, ny] for nx, ny in neighbors]
            neighbors_values_set.update(neighbors_values)
        neighbors_values_set.discard(0)
        return (neighbors_values_set, neighbors_set)




obraz = cv2.imread("obraz2.png", 0)
_, obraz = cv2.threshold(obraz, 128, 1, cv2.THRESH_BINARY)
obraz = 1-obraz
obraz2 = np.array(obraz)

detector = RoadsIntersectionsDetecotr()
obraz2 = detector.run(obraz2)

# for node in graph.nodes:
#     try:
#         print(graph.nodes[node]['color'])
#     except:
#         pass

graph = detector.graph

plt.subplot(2,2,1)
plt.imshow(obraz, cmap='gray')

plt.subplot(2,2,2)
node_positions = nx.get_node_attributes(graph, 'pos')
nx.draw(graph, pos=node_positions, with_labels=True,  width=2.0, edge_color='red')

for edge in graph.edges:
    edge_length = graph.edges[edge]['length']
    x = (node_positions[edge[0]][0] + node_positions[edge[1]][0]) / 2  # x-coordinate for text position
    y = (node_positions[edge[0]][1] + node_positions[edge[1]][1]) / 2  # y-coordinate for text position
    plt.text(x, y, str(edge_length), color='white', fontsize=10, ha='center', va='center')

plt.imshow(obraz2, cmap='cubehelix')

graphPostProcessor = GraphPostProcessor()
graph = graphPostProcessor.run(detector.graph)

plt.subplot(2,2,3)
node_positions = nx.get_node_attributes(graph, 'pos')
nx.draw(graph, pos=node_positions, with_labels=True,  width=2.0, edge_color='red')

for edge in graph.edges:
    edge_length = graph.edges[edge]['length']
    x = (node_positions[edge[0]][0] + node_positions[edge[1]][0]) / 2  # x-coordinate for text position
    y = (node_positions[edge[0]][1] + node_positions[edge[1]][1]) / 2  # y-coordinate for text position
    plt.text(x, y, str(edge_length), color='white', fontsize=10, ha='center', va='center')

plt.imshow(obraz2, cmap='cubehelix')
plt.show()

#nodes : {pos, radius , color:[]}
#edges : {length , area, color:[]}