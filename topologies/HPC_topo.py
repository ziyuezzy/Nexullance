import networkx as nx
import sys
from itertools import islice
from concurrent.futures import ThreadPoolExecutor
from joblib import Parallel, delayed
MAX_KERNELS = 1 # define maximum threads to run
import numpy as np
import random
from globals import convert_M_EPs_to_M_R, local_link_flows_from_M_EPs


#TODO: check "bfs", "all_pairs_shortest_path" and "Floyd–Warshall algorithm", for speeding up the methods

class HPC_topo():
    
    @classmethod
    def import_child_classes(cls):
        from .DDF import DDFtopo
        from .Slimfly import Slimflytopo
        from .Equality import Equalitytopo
        from .RRG import RRGtopo

    @classmethod
    def get_child_classes(cls):
        cls.import_child_classes()
        return [sub.__name__ for sub in cls.__subclasses__()]
    
    @classmethod
    def initialize_child_instance(cls, child_class_name, *args, **kwargs):
        child_classes = cls.__subclasses__()
        for sub in child_classes:
            if sub.__name__ == child_class_name:
                return sub(*args, **kwargs)
        raise ValueError(f"Class {child_class_name} not found as a child of {cls.__name__}")

    def __init__(self):
        self.nx_graph = nx.Graph()
        self.diameter = None

    # def get_vertices(self):
    #     return list(self.nx_graph.nodes())

    def calculate_k_shortest_paths(self, v1, v2, k):
        return list( islice(nx.shortest_simple_paths(self.nx_graph, v1, v2), k) )

    def calculate_all_k_shortest_paths(self, k):
        vertices = self.nx_graph.nodes()

        # Create a list of all vertex pairs
        vertex_pairs = [(v1, v2) for v1 in vertices for v2 in vertices if v1 != v2]

        # Calculate the average k-shortest path lengths in parallel with custom progress bar
        paths_dict={}

        # Execute the parallel computation
        results = Parallel(n_jobs=MAX_KERNELS)(
            delayed(self.calculate_k_shortest_paths)(v1, v2, k) for v1, v2 in vertex_pairs
        )

        # Process the results as needed
        paths_dict = {}
        for (v1, v2), all_paths in zip(vertex_pairs, results):
            if not all_paths:
                raise ValueError(f"Error, no path found between vertex {v1} and vertex {v2}")
            paths_dict[(v1, v2)] = all_paths

        return paths_dict, f"{k}_SP"

    def calculate_all_paths_within_length(self, max_length): # a single-thread version
        assert(max_length >= self.calculate_diameter())
        paths_dict={}
        vertex_pairs = [(v1, v2) for v1 in self.nx_graph.nodes() for v2 in self.nx_graph.nodes() if v1 != v2]
        for (v1, v2) in vertex_pairs:
            all_paths = []
            # Depth-first search to find all paths from v1 to v2
            def dfs_paths(node, path):
                if node == v2:
                    all_paths.append(path)
                elif len(path) < max_length+1:
                    for neighbor in self.nx_graph.neighbors(node):
                        if neighbor not in path:
                            dfs_paths(neighbor, path + [neighbor])
            dfs_paths(v1, [v1])
            if not all_paths:
                raise ValueError(f"Error, no path found between vertex {v1} and vertex {v2}")
            paths_dict[(v1, v2)]=all_paths
        return paths_dict, f"APST_{max_length}"
    
    def calculate_all_paths_within_length_parallel(self, max_length): # a parallel version of the above algorithm
        assert max_length >= self.calculate_diameter()

        paths_dict = {}
        vertex_pairs = [(v1, v2) for v1 in self.nx_graph.nodes() for v2 in self.nx_graph.nodes() if v1 != v2]

        def dfs_paths(node, path, v2):
            if node == v2:
                return [path]
            elif len(path) < max_length + 1:
                paths = []
                for neighbor in self.nx_graph.neighbors(node):
                    if neighbor not in path:
                        paths += dfs_paths(neighbor, path + [neighbor], v2)
                return paths
            else:
                return []
            
        # Execute the parallel computation
        results = Parallel(n_jobs=MAX_KERNELS)(
            delayed(dfs_paths)( v1, [v1], v2) for v1, v2 in vertex_pairs
        )

        # Process the results as needed
        paths_dict = {}
        for (v1, v2), all_paths in zip(vertex_pairs, results):
            if not all_paths:
                raise ValueError(f"Error, no path found between vertex {v1} and vertex {v2}")
            paths_dict[(v1, v2)] = all_paths

        return paths_dict, f"APST_{max_length}"
    
    def calculate_all_shortest_paths(self): 
        vertices = self.nx_graph.nodes()
        vertex_pairs = [(v1, v2) for v1 in vertices for v2 in vertices if v1 != v2]
        def calculate_shortest_paths(v1, v2):
            return list(nx.all_shortest_paths(self.nx_graph, v1, v2))
        
        # Execute the parallel computation
        results = Parallel(n_jobs=MAX_KERNELS)(
            delayed(calculate_shortest_paths)( v1, v2) for v1, v2 in vertex_pairs
        )

        # Process the results as needed
        paths_dict = {}
        for (v1, v2), all_paths in zip(vertex_pairs, results):
            if not all_paths:
                raise ValueError(f"Error, no path found between vertex {v1} and vertex {v2}")
            paths_dict[(v1, v2)] = all_paths

        return paths_dict, "ASP"

    def calculate_diameter(self):
        if self.diameter:
            return self.diameter
        else:
            #let k = 1, the shortest paths are calculated
            shortest_path_dict, _ = self.calculate_all_k_shortest_paths(1) 
            shortest_path_lengths=[]
            for shortest_path in shortest_path_dict.values():
                shortest_path_lengths.append(len(shortest_path[0])-1)
            diameter=max(shortest_path_lengths)
            self.diameter=diameter
            return diameter
    
    
    def distribute_M_R_on_weighted_paths(self, weighted_path_dict, M_R):
        # traffic matrix should be a 2-D matrix
        assert(len(M_R)==len(M_R[0])==self.nx_graph.number_of_nodes() and 'traffic matrix shape is wrong')
        link_flows = {}
        # initialization
        for u, v in list(self.nx_graph.edges()):
            link_flows[(u, v)]=0
            link_flows[(v, u)]=0
        # start calculation
        for u in list(self.nx_graph.nodes()):
            for v in list(self.nx_graph.nodes()):
                if u==v:
                    continue
                else:
                    weighted_paths=weighted_path_dict[(u, v)]
                    check_sum=0
                    for j, (path, weight) in enumerate(weighted_paths):
                        if j == len(weighted_paths)-1:
                            w=1-check_sum
                            assert(abs(w-weight)<0.01) # rounding errors should be small
                            for i in range(len(path) - 1):
                                vertex1, vertex2 = path[i], path[i + 1]
                                link_flows[(vertex1, vertex2)] += w*M_R[u][v]
                        else:
                            for i in range(len(path) - 1):
                                vertex1, vertex2 = path[i], path[i + 1]
                                link_flows[(vertex1, vertex2)] += weight*M_R[u][v]
                            check_sum += weight

        link_flows = [ v for v in link_flows.values()]
        return link_flows
        
    def distribute_M_EPs_on_weighted_paths(self, weighted_path_dict, EPR, M_EPs):
        M_R = convert_M_EPs_to_M_R(M_EPs, self.nx_graph.number_of_nodes(), EPR)
        remote_link_flows: list = self.distribute_M_R_on_weighted_paths(weighted_path_dict, M_R)
        local_link_flows: list = local_link_flows_from_M_EPs(M_EPs)
        return remote_link_flows, local_link_flows
        

    # def distribute_arbitrary_flow_on_weighted_paths_with_EPs_return_dict(self, path_dict, p, traffic_matrix):
    #     # traffic matrix should be a 2-D matrix
    #     assert(len(traffic_matrix)==len(traffic_matrix[0])==self.nx_graph.number_of_nodes()*p and  'traffic matrix shape is wrong')

    #     #p is the subscription of routers, meaning the number of EPs attached to one router
    #     link_flows = {}
    #     local_link_flows = {}
    #     # initialization
    #     for u, v in list(self.nx_graph.edges()):
    #         link_flows[(u, v)]=0
    #         link_flows[(v, u)]=0
    #     for u in list(self.nx_graph.nodes()):
    #         for EP in range(p):
    #             local_link_flows[(u, -EP-1)]=0 # from router to EP #Note that the '-EP-1' is just for distinguish the EP ids from router ids
    #             local_link_flows[(-EP-1, u)]=0 # from EP to router
    #     # start calculation
    #     for u in list(self.nx_graph.nodes()):
    #         for src_EP in range(p):
    #             for v in list(self.nx_graph.nodes()):
    #                 for dest_EP in range(p):
    #                     if u==v and src_EP==dest_EP:
    #                         continue
    #                     #calculates the absolute id of src and dest EPs
    #                     src_EP_abs=p*u+src_EP
    #                     dest_EP_abs=p*v+dest_EP
    #                     local_link_flows[(-src_EP-1, u)]+=traffic_matrix[src_EP_abs][dest_EP_abs]
    #                     local_link_flows[(v, -dest_EP-1)]+=traffic_matrix[src_EP_abs][dest_EP_abs]
    #                     if u!=v:
    #                         paths=path_dict[(u, v)]
    #                         check_sum=0
    #                         for j, (path, weight) in enumerate(paths):
    #                             if j == len(paths)-1:
    #                                 w=1-check_sum
    #                                 assert(abs(w-weight)<0.01)
    #                                 for i in range(len(path) - 1):
    #                                     vertex1, vertex2 = path[i], path[i + 1]
    #                                     link_flows[(vertex1, vertex2)] += w*traffic_matrix[src_EP_abs][dest_EP_abs]
    #                             else:
    #                                 for i in range(len(path) - 1):
    #                                     vertex1, vertex2 = path[i], path[i + 1]
    #                                     link_flows[(vertex1, vertex2)] += weight*traffic_matrix[src_EP_abs][dest_EP_abs]
    #                                 check_sum += weight

    #     local_link_flows = [ v for v in local_link_flows.values()]
    #     assert(min(local_link_flows)==max(local_link_flows))

    #     return link_flows, min(local_link_flows)


    def set_random_link_failures(self, failure_ratio, seed=0):
        random.seed(seed)
        G=self.nx_graph
        # Get the list of edges in the graph
        assert(0<=failure_ratio<1)
        num_edges_to_delete=int(failure_ratio * G.number_of_edges())
        edges_to_delete = random.sample(G.edges(), num_edges_to_delete)
        # Delete the selected edges
        G.remove_edges_from(edges_to_delete)
        if not nx.is_connected(G):
            raise ValueError("Graph is not connected after the deletions!")
        print(f"{num_edges_to_delete} edge(s) has been deleted from inter-group edge list")
        
        return
    