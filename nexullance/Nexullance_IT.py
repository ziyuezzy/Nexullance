import networkx as nx
from joblib import Parallel, delayed
Graph = nx.graph.Graph

class Nexullance_IT:
    def __init__(self, _nx_graph: Graph, _M_R: list, _Cap_remote: float, _solver:int=0, _verbose:bool=False):
        self.nx_graph = _nx_graph
        self.M_R: list = _M_R
        self.solver: int = _solver
        self.verbose: bool = _verbose
        self.Cap_remote: float = _Cap_remote

        # prepare for access
        self.vertex_pairs = [(v1, v2) for v1 in _nx_graph.nodes() for v2 in _nx_graph.nodes() if v1 != v2]

        # clear node and edge attributes
        for (n1, n2, d) in self.nx_graph.edges(data=True):
            d.clear()
        for (n1, n2, d) in self.nx_graph.nodes(data=True):
            d.clear()

    def initialization(self):
        # initialize the data structures.
        # the routing table is a dictionary of dictionary (to be the same as networkx)
        # the key of the first dictionary is the source node, and the key of the second dictionary is the destination node
        # the value of the second dictionary contains the unique ids of paths, and the weight of the path
        
        self.next_path_id: int = 0
        self.routing_table : dict = {}
        # another dictionary maps from the unique id of a path to the actual path itself.
        self.path_id_to_path: dict = {}
        # link loads are stored in a the edge attributes in the nx graph: "load"
        # meanwhile, another edge attribute "path_ids" is added to store the unique ids of the paths that pass through this link.
        # now we initialize the edge attributes in the nx graph:
        for (n1, n2, d) in self.nx_graph.edges(data=True):
            d['load'] = 0
            d['path_ids'] = []

        # execute optimization_method_1 without weights #TODO
        # equivalently, the routing table is initialized with ECMP-ASP
        
        pass

    # for experimenting the combination of different methods, 
    # copy.deepcopy() could be used after applying the methods
     
    def optimization_method_1(self):#TODO
        # weighted dijkstra algorithm to find the least-weighted paths (for ties, apply ECMP) for all s-d pairs.
        
        pass

    def optimization_method_2(self, step: float):#TODO
        # optimization_method_2 is more fine-grained than optimization_method_1,
        # it takes the maximum loaded link, and then find alternative routes for the flows
        # that pass by this link by executing a weighted dijkstra algorithm.
        
        # 'step parameter is the maximum path weight transfer in one iteration
        pass

    # a weighted dijkstra algorithm to find the least-weighted path for all s-d pairs.
    def least_weighted_paths_for_all_s_d(self, _G: Graph, _weights: function, algorithm: str, MAX_KERNELS: int) -> dict:
        if algorithm == "dijkstra" or algorithm == "bellman-ford": 
            # only two options to pass to netowrkx
            paths_dict = {}
            for u in _G.nodes():
                paths_dict[u] = {}

            def calculate_shortest_paths(v1, v2):
                return list(nx.all_shortest_paths(_G, v1, v2, _weights, algorithm))
                
            if MAX_KERNELS == 1:
                # do not parallelize
                for (v1, v2) in self.vertex_pairs:
                    all_paths = calculate_shortest_paths(v1, v2)
                    if not all_paths:
                        raise ValueError(f"Error, no path found between vertex {v1} and vertex {v2}")
                    paths_dict[v1][v2] = all_paths
                
            elif MAX_KERNELS > 1:
                # parallelize the computation
                results = Parallel(n_jobs=MAX_KERNELS)(
                    delayed(calculate_shortest_paths)(v1, v2) for v1, v2 in self.vertex_pairs
                )
                for (v1, v2), all_paths in zip(self.vertex_pairs, results):
                    if not all_paths:
                        raise ValueError(f"Error, no path found between vertex {v1} and vertex {v2}")
                    paths_dict[v1][v2] = all_paths
            else:
                raise ValueError("MAX_KERNELS need to be a positive integer.")
        else:
            raise ValueError("Invalid algorithm choice.")
        
        return paths_dict

    def least_weighted_paths_for_pair(self,_G: Graph, _s: int, _d: int, _weights: function, algorithm: str) -> dict:
        # the following algorithms return only one least-weighted path that the algorithm encouters,
        # alternatively, find all least-weighted paths and then arbitrate.

        if algorithm == "dijkstra":
            # use dijkstra algorithm
            return nx.dijkstra_path(_G, _s, _d, weight=_weights)
        elif algorithm == "bellman-ford":
            # use bellman-ford algorithm
            return nx.bellman_ford_path(_G, _s, _d, weight=_weights)
        elif algorithm == "bidirectional-dijkstra":
            # use bidirectinal dijkstra algorithm, 
            # but this might have some problem with floating numbers
            return nx.bidirectional_dijkstra(_G, _s, _d, weight=_weights)
        else:
            raise ValueError("Invalid algorithm choice.")


def weight_function( s: int, d: int, edge_attributes: dict):
    # define the weight function for the dijkstra or the bellman-ford algorithm.
    alpha: float = 1.0
    beta: float = 10.0
    # return 1
    return edge_attributes['a']
