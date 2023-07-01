import cv2
import numpy as np
import matplotlib.pyplot as plt
import threading
import networkx as nx

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

        indexes = [np.argwhere(image == 1)[0]]
        nodeName = f"{self.iterator}"
        self.intersections_list.append(self.iterator)
        self.iterator+=1
        with self.graph_lock:
            self.graph.add_node(nodeName, pos=(indexes[0][1], indexes[0][0]))

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

        while len(neighbor_lists)==1:
            indexes2 = set([])
            for (x, y) in indexes:
                self.image[x, y] = value
                indexes2.update(self.find_neighbors_with_value((x, y), 1))
            if indexes2:
                indexes = indexes2
                neighbor_lists = self.divide_into_neighbor_lists(indexes)
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
                        pos = self.color_intersection(neighbours.copy(), intersection_id)
                        with self.graph_lock:
                            self.graph.add_node(nodeName, pos=pos)
                            self.graph.add_edge(startNodeName, nodeName)
                        #     for node in neighbours_values:
                        #         self.graph.add_edge(f"{node}", nodeName)
                        print(neighbours_values)
                    else:
                        print(neighbours_values)
                else:
                    print("---",neighbours_values)
                    print(self.intersections_list)
            else:
                pos = self.color_intersection(neighbours.copy(), intersection_id)
                with self.graph_lock:
                    self.graph.add_node(nodeName, pos=pos)
                    self.graph.add_edge(startNodeName, nodeName)
        else:
            with self.graph_lock:
                self.graph.add_node(nodeName)
                self.graph.add_edge(startNodeName, nodeName)
        
            for sub_indexes in neighbor_lists:
                thread = threading.Thread(target=self.color_road, args=(set(sub_indexes.copy()), self.iterator, nodeName))
                self.iterator+=1
                thread.start()
                self.thread_list.append(thread)

            pos = self.color_intersection(indexes.copy(), intersection_id)
            with self.graph_lock:
                self.graph.nodes[nodeName]['pos'] = pos


    def color_intersection(self, indexes, value):
        average_x = np.mean([point[0] for point in indexes])
        average_y = np.mean([point[1] for point in indexes])

        min_x = min(point[0] for point in indexes)
        max_x = max(point[0] for point in indexes)
        min_y = min(point[1] for point in indexes)
        max_y = max(point[1] for point in indexes)

        radius = max(max_x - average_x, max_y - average_y, average_x - min_x, average_y- min_y)

        center = (int(average_y), int(average_x))
        cv2.circle(self.image, center, int(radius), value, thickness=-1)
        return center

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

unThresholder = RoadsIntersectionsDetecotr()
obraz2 = unThresholder.run(obraz2)

plt.subplot(1,2,1)
plt.imshow(obraz, cmap='gray')
plt.subplot(1,2,2)
node_positions = nx.get_node_attributes(unThresholder.graph, 'pos')
nx.draw(unThresholder.graph, pos=node_positions, with_labels=True,  width=2.0, edge_color='red')
plt.imshow(obraz2, cmap='cubehelix')
plt.show()