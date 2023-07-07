import networkx as nx
from . import Undirected_graph

class RRGtopo(Undirected_graph.Undirected_graph_topo):
    def __init__(self, degree, num_vertices, seed = 0):
        super(RRGtopo, self).__init__()
        self.nx_graph = nx.random_regular_graph(degree, num_vertices, seed=seed)