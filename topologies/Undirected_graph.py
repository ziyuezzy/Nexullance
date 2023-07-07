import networkx as nx
import sys
from itertools import islice
from concurrent.futures import ThreadPoolExecutor
from joblib import Parallel, delayed
MAX_KERNELS = 12 # define maximum threads to run

class Undirected_graph_topo:
    def __init__(self):
        self.nx_graph = nx.Graph()
        self.diameter = None

    # def get_vertices(self):
    #     return list(self.nx_graph.nodes())

    def calculate_k_shortest_paths(self, v1, v2, k):
        return list( islice(nx.shortest_simple_paths(self.nx_graph, v1, v2), k) )

    def calculate_all_k_shortest_path_length(self, k):
        vertices = self.nx_graph.nodes()

        # Create a list of all vertex pairs
        vertex_pairs = [(v1, v2) for v1 in vertices for v2 in vertices if v1 != v2]

        # Calculate the average k-shortest path lengths in parallel with custom progress bar
        paths_dict={}

        with ThreadPoolExecutor(max_workers=MAX_KERNELS) as executor:
            futures = []
            for v1, v2 in vertex_pairs:
                future = executor.submit(self.calculate_k_shortest_paths, v1, v2, k)
                futures.append((v1, v2, future))

            for v1, v2, future in futures:
                all_paths = future.result()
                if not all_paths:
                    raise ValueError(f"Error, no path found between vertex {v1} and vertex {v2}")
                paths_dict[(v1, v2)] = all_paths

        return paths_dict

    def distribute_flow_on_paths(self, path_dict):
        link_loads = {}
        for u, v in list(self.nx_graph.edges()):
            link_loads[(u, v)]=0
            link_loads[(v, u)]=0
        for paths in path_dict.values():
            k = float(len(paths))
            for path in paths:
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    link_loads[(u, v)] += 1 / k
        return link_loads

    def calculate_all_paths_within_length(self, max_length): # a single-thread version
        assert(max_length <= self.calculate_diameter())
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
        return paths_dict
    
    def calculate_all_paths_within_length_parallel(self, max_length): # a parallel version of the above algorithm
        assert max_length <= self.calculate_diameter()

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

        with ThreadPoolExecutor(max_workers=MAX_KERNELS) as executor:
            futures = []
            for v1, v2 in vertex_pairs:
                future = executor.submit(dfs_paths, v1, [v1], v2)
                futures.append((v1, v2, future))

            for v1, v2, future in futures:
                all_paths = future.result()
                if not all_paths:
                    raise ValueError(f"Error, no path found between vertex {v1} and vertex {v2}")
                paths_dict[(v1, v2)] = all_paths

        return paths_dict

    def calculate_diameter(self):
        if self.diameter:
            return self.diameter
        else:
            #let k = 1, the shortest paths are calculated
            shortest_path_dict = self.calculate_all_k_shortest_path_length(1) 
            shortest_path_lengths=[]
            for shortest_path in shortest_path_dict.values():
                shortest_path_lengths.append(len(shortest_path[0])-1)
            diameter=max(shortest_path_lengths)
            self.diameter=diameter
            return diameter
