import networkx as nx
from . import HPC_topo

class RRGtopo(HPC_topo.HPC_topo):
    # def __init__(self, degree, num_vertices, seed = 0):
    #     super(RRGtopo, self).__init__()
    #     self.nx_graph = nx.random_regular_graph(degree, num_vertices, seed=seed)

    # def __init__(self, edgelist):
    #     super(RRGtopo, self).__init__()
    #     # create the embedded graph
    #     graph = nx.Graph()
    #     graph.add_edges_from(edgelist)
    #     self.nx_graph = graph

    def __init__(self, *args, **kwargs):
        if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int):
            super(RRGtopo, self).__init__()
            degree=args[1]
            num_vertices=args[0]
            self.nx_graph = nx.random_regular_graph(degree, num_vertices, seed=0)

        elif len(args) == 1 and isinstance(args[0], list):
            super(RRGtopo, self).__init__()
            # create the embedded graph
            graph = nx.Graph()
            graph.add_edges_from(args[0])
            self.nx_graph = graph
        else:
            raise ValueError('Input arguements not accepted.')