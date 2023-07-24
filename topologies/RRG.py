import networkx as nx
from . import HPC_topo

class RRGtopo(HPC_topo.HPC_topo):
    def __init__(self, degree, num_vertices, seed = 0):
        super(RRGtopo, self).__init__()
        self.nx_graph = nx.random_regular_graph(degree, num_vertices, seed=seed)