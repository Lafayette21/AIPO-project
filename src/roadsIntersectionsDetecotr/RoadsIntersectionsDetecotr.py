import cv2
import numpy as np
import matplotlib.pyplot as plt
import threading
import networkx as nx
import time
from GraphPostProcessing import GraphPostProcessor

#urzywa obraz o wartościach 0 dla tła i 1 dla drug i skrzyrzoań
#zwraca obraz z osobną wartością dla karzdej drogi i skrzyrzoania oraz gotowy graf z odpowiednimi wartościami
#nodes : {pos, radius , color:[]}
#edges : {length , area, color:[]}
class RoadsIntersectionsDetecotr:    
    def __init__(self, image):
        self.iterator=2
        self.image = image
        self.thread_list = []
        self.graph = nx.Graph()
        self.graph_lock = threading.Lock()
        self.roads_list = []
        self.intersections_list = []
        self.roads_not_connected = {}
        self.neighbour_offsets = [(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if (dx != 0 or dy != 0)]


    #Uruchomienie detekcji drug i skrzyrzowań
    def run(self):
        # znajdź pierwszy piksel drogi
        indexes = [np.argwhere(self.image == 1)[0]]

        #stwórz pierszey node grafu
        nodeName = f"{self.iterator}"
        self.intersections_list.append(self.iterator)
        self.iterator+=1
        with self.graph_lock:
            self.graph.add_node(nodeName, pos=(indexes[0][1], indexes[0][0]), color=[nodeName], radius=1)

        #stworzenie wątku który zacznie malować droge od pierwszego pixela
        thread = threading.Thread(target=self.color_road_recursive_multithread, args=(indexes, self.iterator, nodeName))
        self.iterator+=1
        thread.start()
        self.thread_list.append(thread)

        #dąłącznie do wszytkich wątków po kolei aż wszystkie nie zostaną wykonane
        while self.thread_list:
            thread = self.thread_list.pop(0)
            thread.join()
        
        return (self.image, self.graph)
    
    # funkcja kolorująca droge
    def color_road_recursive_multithread(self, indexes, value , startNodeName):
        #dodanie drogi do listy dróg
        self.roads_list.append(value)

        #inicajlizacja urzywanych wartości do kreacji drogi
        neighbors_lists=[[]]
        road_end=False
        road_length = 0
        road_area = len(indexes)

        #kolorowanie drogi do puki znajdą się niepokolorowane pixele drogi lub skrzyrzowanie
        #skrzyrzowanie zostaje znalesione jeśji znaloziono wiecej niż jedną grupe sąsiadów
        while len(neighbors_lists)==1:
            indexes2 = set([])
            for (x, y) in indexes:
                self.image[x, y] = value
                #snalezeinie wszystkich sąsiadów będących niepokolorowną drogą do aktualnie posiadanych punktów
                indexes2.update(self.find_neighbors_with_value((x, y), 1))
            if indexes2:
                indexes = indexes2
                #podzielenie sąsiadów na grpuy sąsiadów
                neighbors_lists = self.divide_into_neighbor_lists(indexes)
                road_length+=1
                road_area+=len(indexes)
            else: 
                road_end = True
                break

        # Inicjalizacja wartości dla nowego skrzyrzowania
        intersection_id=self.iterator
        self.iterator+=1
        self.intersections_list.append(intersection_id)
        nodeName = f"{intersection_id}"

        # jeśli koniec drogi
        if road_end:
            #znalezienie sąsiadów ostanich punktów i ich w\rtości
            neighbours_values , neighbours = self.get_neighbors_values_set(indexes)

            #usunięcie wartości własnej i wartości startowego node
            neighbours_values.discard(value)
            neighbours_values.discard(int(startNodeName))

            #jeśli pozostali sąsiedzi z inną wartością niż własna lub pusta to odpowiedznie dołaczenie drogi
            if neighbours_values:
                #jesli pozostałe wartości to wartości drogi to stworzenie nowego skrzyrzownaia między nimi i dołączenie wszytkich tych drug do niego
                if all(elem in self.roads_list for elem in neighbours_values):
                    #stworzenie nowego skrzyrzownaia tylko przez thread zawierający droge o najwyrzszej wattości
                    if value == max([*neighbours_values, value]):
                        pos, radius = self.color_intersection(neighbours.copy(), intersection_id)
                        with self.graph_lock:
                            self.graph.add_node(nodeName, pos=pos, color = [intersection_id], radius=radius)
                            self.graph.add_edge(startNodeName, nodeName, length = road_length, area = road_area, color = [value])
                        #pruby połaczenia przeciwnych drug do nowo stworzonego skrzyrzowania
                        for _ in range(10):
                            if neighbours_values:
                                time.sleep(0.1)
                                for f_value in neighbours_values:
                                    if f_value in self.roads_not_connected:
                                        with self.graph_lock:
                                            self.graph.add_edge(nodeName, self.roads_not_connected[f_value]["name"], 
                                                                length = self.roads_not_connected[f_value]["len"],
                                                                area = self.roads_not_connected[f_value]["area"], 
                                                                color = [f_value])
                                        self.roads_not_connected.pop(f_value)
                                        neighbours_values.pop(f_value)
                                        
                            else: break
                    #jeśli nie thread z drogą o najwyrzszej wartości dodanie wartości drogi do słownika nie połaczonych dróg
                    else:
                        self.roads_not_connected[value] = {}
                        self.roads_not_connected[value]["name"] = startNodeName
                        self.roads_not_connected[value]["len"] = road_length
                        self.roads_not_connected[value]["area"] = road_area
                else:
                    neighbours_values -= set(self.roads_list)
                    #jesśli pozostała tylko jedna wartość skrzyrzowania połączenie drogi do tego skrzyrzowania
                    if len(neighbours_values) == 1:
                        time.sleep(0.1)
                        self.graph.add_edge(startNodeName, f"{list(neighbours_values)[0]}", length = road_length, area = road_area, color = [value])
                    #jeśli pozostały inne wartości to nieobsługiwany narazie bład, pomiajny(nie powinien sie nigdy wydażyć)
                    else:
                        print(f"Detestion error on road {value} that starts from node{startNodeName}")
                        print(neighbours_values)
            #Jeśli brak wartości sąsiadów to znaczy że koniec drgoi, stworzenie nowego node będącego końcem drogi
            else:
                pos, radius = self.color_intersection(neighbours.copy(), intersection_id)
                with self.graph_lock:
                    self.graph.add_node(nodeName, pos=pos, color = [intersection_id], radius=radius)
                    self.graph.add_edge(startNodeName, nodeName, length = road_length, area = road_area, color = [value])
        #Znaleziono skrzyrzowanie
        else:
            #obliczenie wartości i naryswoanie nowgo skrzyrzowania
            pos, radius = self.color_intersection(indexes.copy(), intersection_id)
            #pobranie wartości wszystkich sąsiadó skrzyrzowania
            intersection_neighbours = self.find_all_circle_neighbours(pos, radius, intersection_id)
            #podzielenie sąsiadów na grpuy sąsiadów
            neighbors_lists = self.divide_into_neighbor_lists(intersection_neighbours)

            #dodaenie nowego węzła w miejscu skrzyrzowania
            with self.graph_lock:
                self.graph.add_node(nodeName, color = [intersection_id], pos=pos, radius=radius)
                self.graph.add_edge(startNodeName, nodeName, length = road_length, area = road_area, color = [value])
        
            #ponowne uruchomienie kolorowania drogi dla wszytkich grup sąsiadów w nowych wątkach
            for sub_neighbors in neighbors_lists:
                thread = threading.Thread(target=self.color_road_recursive_multithread, args=(set(sub_neighbors.copy()), self.iterator, nodeName))
                self.iterator+=1
                thread.start()
                self.thread_list.append(thread)

    #wyliczenie środka skrzyrzownia i narusowanie go
    def color_intersection(self, indexes, value):
        average_x = np.mean([point[0] for point in indexes])
        average_y = np.mean([point[1] for point in indexes])

        min_x = min(point[0] for point in indexes)
        max_x = max(point[0] for point in indexes)
        min_y = min(point[1] for point in indexes)
        max_y = max(point[1] for point in indexes)

        radius = int(max(max_x - average_x, max_y - average_y, average_x - min_x, average_y- min_y))+1

        center = (int(average_y), int(average_x))

        cv2.circle(self.image, center, radius, value, thickness=-1)

        return (center, radius)

    #znalerzienie wszytkich sąsiadów skrzyrzownaia będących nipomalowaną drogą
    def find_all_circle_neighbours(self, center, radius, value):
        neighbours = set()
        for i in range(center[1]-radius-1,center[1]+radius+2):
            for j in range(center[0]-radius-1,center[0]+radius+2):
                if self.point_in_image((i,j)) and self.image[i,j] == 1:
                    n = self.find_neighbors_with_value((i,j), value)
                    if n:
                        neighbours.add((i,j))
        return neighbours

    #Sprawdzenie czy punkt znajduje sie w obrazie
    def point_in_image(self, point):
        return 0 <= point[0] < self.image.shape[0] and 0 <= point[1] < self.image.shape[1]

    #zanelzinie wszytkich sąsiadów pixela posiadających daną wartość
    def find_neighbors_with_value(self, pixel, value):
        x, y = pixel
        neighbors = [(x + dx, y + dy) for dx, dy in self.neighbour_offsets]
        neighbors = [point for point in neighbors if self.point_in_image(point)]
        neighbors = [point for point in neighbors if self.image[point] == value]

        return neighbors
    
    #podzielenie sąsiadó na grupy sąsiadów
    def divide_into_neighbor_lists(self, pixels):
        neighbors_lists = []

        def is_neighbor(coord1, coord2):
            return abs(coord1[0] - coord2[0]) <= 1 and abs(coord1[1] - coord2[1]) <= 1

        for pixel in pixels:
            neighbors = [pixel]
            for i in range(len(neighbors_lists) - 1, -1, -1):
                if any(is_neighbor(pixel, coord) for coord in neighbors_lists[i]):
                    neighbors.extend(neighbors_lists.pop(i))
            neighbors_lists.append(neighbors)

        return neighbors_lists
    
    #znalezienie wszystkich sasiadów listy punktów i wszystkaich ich wartości nie liczac wartości tła
    def get_neighbors_values_set(self,indexes):
        neighbors_set = set()
        neighbors_values_set = set()
        for (x, y) in indexes:
            neighbors = [(x + dx, y + dy) for dx, dy in self.neighbour_offsets]
            neighbors = [point for point in neighbors if self.point_in_image(point)]
            neighbors_set.update(neighbors)
            neighbors_values = [self.image[point] for point in neighbors]
            neighbors_values_set.update(neighbors_values)
        neighbors_values_set.discard(0)
        return (neighbors_values_set, neighbors_set)

    def postProces(self):
        graphPostProcessor = GraphPostProcessor()
        self.graph = graphPostProcessor.run(self.graph)

    def backup(self):
        self.backup_graph=self.graph.copy()
        self.backup_image=self.image.copy()
        self.backup_iterator=self.iterator

    def load_backup(self):
        self.graph=self.backup_graph.copy()
        self.image=self.backup_image.copy()
        self.iterator=self.backup_iterator
    
    def color_road(self, value):
        self.roads_list.append(value)

        #inicajlizacja urzywanych wartości do kreacji drogi
        neighbors_lists=[[]]
        road_end=False
        road_length = 0
        road_area = len(indexes)

        #kolorowanie drogi do puki znajdą się niepokolorowane pixele drogi lub skrzyrzowanie
        #skrzyrzowanie zostaje znalesione jeśji znaloziono wiecej niż jedną grupe sąsiadów
        while len(neighbors_lists)==1:
            indexes2 = set([])
            for (x, y) in indexes:
                self.image[x, y] = value
                #snalezeinie wszystkich sąsiadów będących niepokolorowną drogą do aktualnie posiadanych punktów
                indexes2.update(self.find_neighbors_with_value((x, y), 1))
            if indexes2:
                indexes = indexes2
                #podzielenie sąsiadów na grpuy sąsiadów
                neighbors_lists = self.divide_into_neighbor_lists(indexes)
                road_length+=1
                road_area+=len(indexes)
            else: 
                road_end = True
                break      

    def add_point_to_grpah(self, point):
        roads_points = np.argwhere(self.image > 1)
        distances = np.linalg.norm(roads_points - point, axis=1)
        nearest_index = np.argmin(distances)
        nearest_point = roads_points[nearest_index]
        print(nearest_point)
        value = self.image[tuple(nearest_point)]
        # cv2.circle(self.image, (point[1],point[0]), 10, 100, thickness=-1)
        cv2.circle(self.image, (nearest_point[1],nearest_point[0]), 10, 100, thickness=-1)

        found_edge=None
        for edge in self.graph.edges:
            if value in self.graph.edges[edge]['color']:
                found_edge=edge
        
        if found_edge:
            self.graph.remove_edge(found_edge)



        




obraz = cv2.imread("roadsIntersectionsDetecotr/obraz2.png", 0)
_, obraz = cv2.threshold(obraz, 128, 1, cv2.THRESH_BINARY)
obraz = 1-obraz
obraz2 = np.array(obraz)

detector = RoadsIntersectionsDetecotr(obraz2)
obraz2, graph = detector.run()

plt.subplot(2,2,1)
plt.imshow(obraz, cmap='gray')

plt.subplot(2,2,2)
node_positions = nx.get_node_attributes(graph, 'pos')
nx.draw(graph, pos=node_positions, with_labels=True,  width=2.0, edge_color='red')

for edge in graph.edges:
    edge_length = graph.edges[edge]['color']
    x = (node_positions[edge[0]][0] + node_positions[edge[1]][0]) / 2 
    y = (node_positions[edge[0]][1] + node_positions[edge[1]][1]) / 2 
    plt.text(x, y, str(edge_length), color='white', fontsize=10, ha='center', va='center')

plt.imshow(obraz2, cmap='cubehelix')

detector.postProces()
detector.add_point_to_grpah((int(obraz.shape[0]/2),int(obraz.shape[1]/2)))

plt.subplot(2,2,3)
node_positions = nx.get_node_attributes(graph, 'pos')
nx.draw(graph, pos=node_positions, with_labels=True,  width=2.0, edge_color='red')

for edge in graph.edges:
    edge_length = graph.edges[edge]['color']
    x = (node_positions[edge[0]][0] + node_positions[edge[1]][0]) / 2 
    y = (node_positions[edge[0]][1] + node_positions[edge[1]][1]) / 2
    plt.text(x, y, str(edge_length), color='white', fontsize=10, ha='center', va='center')

plt.imshow(obraz2, cmap='cubehelix')
plt.show()