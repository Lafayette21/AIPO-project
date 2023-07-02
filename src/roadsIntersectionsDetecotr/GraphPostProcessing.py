import networkx as nx
import math

class GraphPostProcessor:
    def run(self, graph: nx.Graph):
        self.graph=graph

        cont = True
        while cont:
            cont = False
            for edge in self.graph.edges:
                if self.graph.nodes[edge[0]]['radius']+self.graph.nodes[edge[1]]['radius']>self.graph.edges[edge]['length']:
                    self.merge_nodes(edge)
                    cont = True
                    break
        
        cont = True
        while cont:
            cont = False
            for node in self.graph.nodes:
                if len(self.graph[node])==2:
                    self.remove_node(node)
                    cont = True
                    break

        return self.graph
    

    def merge_nodes(self, edge):
        color:list = self.graph.edges[edge]['color']
        dist = self.graph.edges[edge]['length']
        self.graph.remove_edge(edge[0], edge[1])

        pos1 = self.graph.nodes[edge[0]]['pos']
        pos2 = self.graph.nodes[edge[1]]['pos']
        new_pos = ((pos1[0]+pos2[0])/2,(pos1[1]+pos2[1])/2)

        radius = (self.graph.nodes[edge[0]]['radius'] + self.graph.nodes[edge[1]]['radius'] + dist)/2

        color.extend(self.graph.nodes[edge[0]]['color'])
        color.extend(self.graph.nodes[edge[1]]['color'])

        new_node_name = edge[0]+"_"+edge[1]

        self.graph.add_node(new_node_name, pos=new_pos, radius=radius, color=color)

        for node in edge:
            for neighbor in self.graph.neighbors(node):
                edge_vals = self.graph.edges[(node,neighbor)]
                self.graph.add_edge(new_node_name, neighbor, length = edge_vals['length'], area = edge_vals['area'], color = edge_vals['color'])
        
        self.graph.remove_node(edge[0])
        self.graph.remove_node(edge[1])

    def remove_node(self, node):
        length = 0
        area=0
        color=[]
        edge_nodes = []
        for edge in self.graph[node]:
            edge_data = self.graph[node][edge]
            length+=edge_data["length"]
            area+=edge_data["area"]
            color.extend(edge_data["color"])
            edge_nodes.append(edge)
        color.extend(self.graph.nodes[node]["color"])
        
        self.graph.remove_node(node)
        self.graph.add_edge(edge_nodes[0],edge_nodes[1], length=length, area=area, color=color)