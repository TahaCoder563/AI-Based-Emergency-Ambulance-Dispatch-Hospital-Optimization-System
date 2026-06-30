"""
City Graph Model
Builds and manages the city road network using NetworkX.
Nodes = intersections, Edges = roads with distance + traffic weights.
"""

import networkx as nx
import math


class CityGraph:
    """
    Represents the city road network as a weighted graph.
    Nodes are intersections with (x, y) positions.
    Edges are roads with base distance and traffic factor.
    """

    def __init__(self):
        """Initialize an empty city graph."""
        self.graph = nx.Graph()

    def add_intersection(self, node_id, x, y):
        """
        Add an intersection (node) to the city graph.

        Args:
            node_id (str): Unique identifier for the intersection.
            x (float): X coordinate.
            y (float): Y coordinate.
        """
        self.graph.add_node(node_id, pos=(x, y))

    def add_road(self, node1, node2, traffic_factor=1.0):
        """
        Add a road (edge) between two intersections.
        The base weight is the Euclidean distance between nodes.
        The effective weight = base_distance * traffic_factor.

        Args:
            node1 (str): First intersection.
            node2 (str): Second intersection.
            traffic_factor (float): Traffic multiplier (1.0 = clear, up to 3.0 = heavy).
        """
        pos1 = self.graph.nodes[node1]['pos']
        pos2 = self.graph.nodes[node2]['pos']
        base_distance = math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
        weight = base_distance * traffic_factor
        self.graph.add_edge(node1, node2,
                            base_distance=base_distance,
                            traffic_factor=traffic_factor,
                            weight=weight)

    def update_traffic(self, node1, node2, new_traffic_factor):
        """
        Update the traffic factor on a road and recalculate weight.

        Args:
            node1 (str): First intersection.
            node2 (str): Second intersection.
            new_traffic_factor (float): New traffic multiplier.
        """
        if self.graph.has_edge(node1, node2):
            edge = self.graph[node1][node2]
            edge['traffic_factor'] = new_traffic_factor
            edge['weight'] = edge['base_distance'] * new_traffic_factor

    def get_position(self, node):
        """Get the (x, y) position of a node."""
        return self.graph.nodes[node]['pos']

    def get_all_positions(self):
        """Get positions of all nodes as a dict {node: (x, y)}."""
        return nx.get_node_attributes(self.graph, 'pos')

    def euclidean_distance(self, node1, node2):
        """
        Calculate Euclidean distance between two nodes.
        Used as the heuristic h(n) in A* search.

        Args:
            node1 (str): First node.
            node2 (str): Second node.

        Returns:
            float: Euclidean distance.
        """
        pos1 = self.graph.nodes[node1]['pos']
        pos2 = self.graph.nodes[node2]['pos']
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def get_neighbors(self, node):
        """Get all neighbors of a node with edge weights."""
        neighbors = []
        for neighbor in self.graph.neighbors(node):
            weight = self.graph[node][neighbor]['weight']
            neighbors.append((neighbor, weight))
        return neighbors

    def get_nodes(self):
        """Get all nodes in the graph."""
        return list(self.graph.nodes())

    def get_edges(self):
        """Get all edges with their data."""
        return list(self.graph.edges(data=True))
