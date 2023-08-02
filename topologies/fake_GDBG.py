from . import HPC_topo
import networkx as nx

# keep the edge list of GDBG, but connect with bidirectional links, see what happens

class fakeGDBGtopo(HPC_topo.HPC_topo):
    # def __init__(self, num_vertices, degree):
    #     super(fakeGDBGtopo, self).__init__()
    #     self.nx_graph = nx.Graph()        
    #     assert(num_vertices > degree)
    #     # Create a list of edges
    #     edges = []    
    #     for v in range(num_vertices):
    #         for e in range(degree):
    #             if v != (degree*v+e)%num_vertices: #exclude self-loop arcs
    #                 edges.extend([(v, (degree*v+e)%num_vertices)])
    #     self.nx_graph.add_edges_from(edges)

    def __init__(self, *args, **kwargs):
        if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int):
            super(fakeGDBGtopo, self).__init__()
            num_vertices=args[0]
            degree=args[1]
            self.nx_graph = nx.Graph()        
            assert(num_vertices > degree)
            # Create a list of edges
            edges = []    
            for v in range(num_vertices):
                for e in range(degree):
                    if v != (degree*v+e)%num_vertices: #exclude self-loop arcs
                        edges.extend([(v, (degree*v+e)%num_vertices)])
            self.nx_graph.add_edges_from(edges)

        elif len(args) == 1 and isinstance(args[0], list):
            super(fakeGDBGtopo, self).__init__()
            # create the embedded graph
            graph = nx.Graph()
            graph.add_edges_from(args[0])
            self.nx_graph = graph
        else:
            raise ValueError('Input arguements not accepted.')