import networkx as nx
import sys
from itertools import islice
from concurrent.futures import ThreadPoolExecutor
from joblib import Parallel, delayed
MAX_KERNELS = 6 # define maximum threads to run
import numpy as np

#TODO: check "bfs", "all_pairs_shortest_path" and "Floyd–Warshall algorithm", for speeding up the methods

class HPC_topo:
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

        return paths_dict

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
        return paths_dict
    
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

        return paths_dict
    
    # def calculate_all_paths_within_length_parallel_2(self, max_length): 
    #     #another parallel algorithm by chatgpt, using iterative DFS to avoid memory overhead
    #     assert max_length >= self.calculate_diameter()

    #     def iterative_dfs_paths(start, end, max_length):
    #         stack = [(start, [start])]
    #         all_paths = []
    #         while stack:
    #             node, path = stack.pop()
    #             if node == end:
    #                 all_paths.append(path)
    #             elif len(path) < max_length + 1:
    #                 for neighbor in self.nx_graph.neighbors(node):
    #                     if neighbor not in path:
    #                         stack.append((neighbor, path + [neighbor]))
    #         return all_paths

    #     vertex_pairs = [(v1, v2) for v1 in self.nx_graph.nodes() for v2 in self.nx_graph.nodes() if v1 != v2]

    #     # Calculate the paths in parallel
    #     results = Parallel(n_jobs=MAX_KERNELS)(
    #         delayed(iterative_dfs_paths)(v1, v2, max_length) for v1, v2 in vertex_pairs
    #     )

    #     # Process the results as needed
    #     paths_dict = {}
    #     for (v1, v2), all_paths in zip(vertex_pairs, results):
    #         if not all_paths:
    #             raise ValueError(f"Error, no path found between vertex {v1} and vertex {v2}")
    #         paths_dict[(v1, v2)] = all_paths
    #         # print(f"number of paths found for s-d ({v1}, {v2}) is {len(all_paths)}")

    #     return paths_dict


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

        return paths_dict

    def calculate_diameter(self):
        if self.diameter:
            return self.diameter
        else:
            #let k = 1, the shortest paths are calculated
            shortest_path_dict = self.calculate_all_k_shortest_paths(1) 
            shortest_path_lengths=[]
            for shortest_path in shortest_path_dict.values():
                shortest_path_lengths.append(len(shortest_path[0])-1)
            diameter=max(shortest_path_lengths)
            self.diameter=diameter
            return diameter
    
    def distribute_uniform_flow_on_paths(self, path_dict): # equivalent to '1 EP per router'
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
    
    def distribute_uniform_flow_on_weighted_paths(self, path_dict):
        link_loads = {}
        for u, v in list(self.nx_graph.edges()):
            link_loads[(u, v)]=0
            link_loads[(v, u)]=0
        for paths in path_dict.values():
            check_sum=0
            for j, (path, weight) in enumerate(paths):
                if j == len(paths)-1:
                    w=1-check_sum
                    assert(abs(w-weight)<0.01)
                    for i in range(len(path) - 1):
                        u, v = path[i], path[i + 1]
                        link_loads[(u, v)] += w
                else:
                    for i in range(len(path) - 1):
                        u, v = path[i], path[i + 1]
                        link_loads[(u, v)] += weight
                    check_sum += weight
        return link_loads
    
    def distribute_uniform_flow_on_weighted_paths_with_EPs(self, path_dict, p):
        #p is the subscription of routers, meaning the number of EPs attached to one router
        link_loads = {}
        local_link_load = {}
        # initialization
        for u, v in list(self.nx_graph.edges()):
            link_loads[(u, v)]=0
            link_loads[(v, u)]=0
        for u in list(self.nx_graph.nodes()):
            for EP in range(p):
                local_link_load[(u, -EP-1)]=0 # from router to EP #Note that the '-EP-1' is just for distinguish the EP ids from router ids
                local_link_load[(-EP-1, u)]=0 # from EP to router
        # start calculation
        for u in list(self.nx_graph.nodes()):
            for src_EP in range(p):
                for v in list(self.nx_graph.nodes()):
                    for dest_EP in range(p):
                        if u==v and src_EP==dest_EP:
                            continue
                        local_link_load[(u, -src_EP-1)]+=1
                        local_link_load[(-dest_EP-1, v)]+=1
                        if u!=v:
                            paths=path_dict[(u, v)]
                            check_sum=0
                            for j, (path, weight) in enumerate(paths):
                                if j == len(paths)-1:
                                    w=1-check_sum
                                    assert(abs(w-weight)<0.01)
                                    for i in range(len(path) - 1):
                                        vertex1, vertex2 = path[i], path[i + 1]
                                        link_loads[(vertex1, vertex2)] += w
                                else:
                                    for i in range(len(path) - 1):
                                        vertex1, vertex2 = path[i], path[i + 1]
                                        link_loads[(vertex1, vertex2)] += weight
                                    check_sum += weight

        link_loads = [ v for v in link_loads.values()]
        local_link_load = [ v for v in local_link_load.values()]
        assert(min(local_link_load)==max(local_link_load))

        return link_loads, min(local_link_load)


    def distribute_arbitrary_flow_on_weighted_paths_with_EPs(self, path_dict, p, traffic_matrix):
        # traffic matrix should be a 2-D matrix
        assert(len(traffic_matrix)==len(traffic_matrix[0])==self.nx_graph.number_of_nodes()*p and  'traffic matrix shape is wrong')

        #p is the subscription of routers, meaning the number of EPs attached to one router
        link_loads = {}
        local_link_load = {}
        # initialization
        for u, v in list(self.nx_graph.edges()):
            link_loads[(u, v)]=0
            link_loads[(v, u)]=0
        for u in list(self.nx_graph.nodes()):
            for EP in range(p):
                local_link_load[(u, -EP-1)]=0 # from router to EP #Note that the '-EP-1' is just for distinguish the EP ids from router ids
                local_link_load[(-EP-1, u)]=0 # from EP to router
        # start calculation
        for u in list(self.nx_graph.nodes()):
            for src_EP in range(p):
                for v in list(self.nx_graph.nodes()):
                    for dest_EP in range(p):
                        if u==v and src_EP==dest_EP:
                            continue
                        #calculates the absolute id of src and dest EPs
                        src_EP_abs=p*u+src_EP
                        dest_EP_abs=p*v+dest_EP
                        local_link_load[(-src_EP-1, u)]+=traffic_matrix[src_EP_abs][dest_EP_abs]
                        local_link_load[(v, -dest_EP-1)]+=traffic_matrix[src_EP_abs][dest_EP_abs]
                        if u!=v:
                            paths=path_dict[(u, v)]
                            check_sum=0
                            for j, (path, weight) in enumerate(paths):
                                if j == len(paths)-1:
                                    w=1-check_sum
                                    assert(abs(w-weight)<0.01)
                                    for i in range(len(path) - 1):
                                        vertex1, vertex2 = path[i], path[i + 1]
                                        link_loads[(vertex1, vertex2)] += w*traffic_matrix[src_EP_abs][dest_EP_abs]
                                else:
                                    for i in range(len(path) - 1):
                                        vertex1, vertex2 = path[i], path[i + 1]
                                        link_loads[(vertex1, vertex2)] += weight*traffic_matrix[src_EP_abs][dest_EP_abs]
                                    check_sum += weight

        link_loads = [ v for v in link_loads.values()]
        local_link_load = [ v for v in local_link_load.values()]
        assert(min(local_link_load)==max(local_link_load))

        return link_loads, min(local_link_load)

    def distribute_arbitrary_flow_on_paths_with_EPs(self, path_dict, p, traffic_matrix):
        # traffic matrix should be a 2-D matrix
        assert(len(traffic_matrix)==len(traffic_matrix[0])==self.nx_graph.number_of_nodes()*p and  'traffic matrix shape is wrong')

        #p is the subscription of routers, meaning the number of EPs attached to one router
        link_loads = {}
        local_link_load = {}
        # initialization
        for u, v in list(self.nx_graph.edges()):
            link_loads[(u, v)]=0
            link_loads[(v, u)]=0
        for u in list(self.nx_graph.nodes()):
            for EP in range(p):
                local_link_load[(u, -EP-1)]=0 # from router to EP #Note that the '-EP-1' is just for distinguish the EP ids from router ids
                local_link_load[(-EP-1, u)]=0 # from EP to router
        # start calculation
        for u in list(self.nx_graph.nodes()):
            for src_EP in range(p):
                for v in list(self.nx_graph.nodes()):
                    for dest_EP in range(p):
                        if u==v and src_EP==dest_EP:
                            continue
                        #calculates the absolute id of src and dest EPs
                        src_EP_abs=p*u+src_EP
                        dest_EP_abs=p*v+dest_EP
                        local_link_load[(-src_EP-1, u)]+=traffic_matrix[src_EP_abs][dest_EP_abs]
                        local_link_load[(v, -dest_EP-1)]+=traffic_matrix[src_EP_abs][dest_EP_abs]
                        if u!=v:
                            paths=path_dict[(u, v)]
                            k = float(len(paths))
                            for path in paths:
                                for i in range(len(path) - 1):
                                    vertex1, vertex2 = path[i], path[i + 1]
                                    link_loads[(vertex1, vertex2)] += traffic_matrix[src_EP_abs][dest_EP_abs] * 1 / k 

        link_loads = [ v for v in link_loads.values()]
        local_link_load = [ v for v in local_link_load.values()]
        assert(min(local_link_load)==max(local_link_load))

        return link_loads, min(local_link_load)

    def distribute_uniform_flow_on_paths_with_EP(self, path_dict, p):
        #p is the subscription of routers, meaning the number of EPs attached to one router
        link_loads = {}
        local_link_load = {}
        # initialization
        for u, v in list(self.nx_graph.edges()):
            link_loads[(u, v)]=0
            link_loads[(v, u)]=0
        for u in list(self.nx_graph.nodes()):
            for EP in range(p):
                local_link_load[(u, -EP-1)]=0 # from router to EP #Note that the '-EP-1' is just for distinguish the EP ids from router ids
                local_link_load[(-EP-1, u)]=0 # from EP to router
        # start calculation
        for u in list(self.nx_graph.nodes()):
            for src_EP in range(p):
                for v in list(self.nx_graph.nodes()):
                    for dest_EP in range(p):
                        if u==v and src_EP==dest_EP:
                            continue
                        local_link_load[(u, -src_EP-1)]+=1
                        local_link_load[(-dest_EP-1, v)]+=1
                        if u!=v:
                            paths=path_dict[(u, v)]
                            k = float(len(paths))
                            for path in paths:
                                for i in range(len(path) - 1):
                                    vertex1, vertex2 = path[i], path[i + 1]
                                    link_loads[(vertex1, vertex2)] += 1 / k

        # #calculate total flow and normalize the link load numbers
        # total_flows = self.nx_graph.number_of_nodes()*p * (self.nx_graph.number_of_nodes()*p-1)
        # link_occupancy_rate=[v / total_flows for v in link_loads.values()]
        # local_link_occupancy_rate=[v / total_flows for v in local_link_load.values()]

        link_loads = [ v for v in link_loads.values()]
        local_link_load = [ v for v in local_link_load.values()]
        assert(min(local_link_load)==max(local_link_load))

        return link_loads, min(local_link_load)
        # return link_occupancy_rate, local_link_occupancy_rate, link_loads, local_link_load
                


    def distribute_uniform_random_flow_on_paths(self, path_dict, std ,seed=0):
        #std is the standard deviation of the uniform random distribution
        link_loads = {}
        for u, v in list(self.nx_graph.edges()):
            link_loads[(u, v)]=0
            link_loads[(v, u)]=0

        np.random.seed(seed)
        normal_dist = np.random.normal(1, std, len(link_loads))
        for i in len(link_loads):
            if normal_dist[i] < 0:
                normal_dist[i] = 0
        for count, paths in enumerate(path_dict.values()):
            k = float(len(paths))
            for path in paths:
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    link_loads[(u, v)] += normal_dist[count] / k
        return link_loads
    
    def s_d_bw_dist(self, paths_dict, link_load_dict):
        bw_dict={}
        for s_d, paths in paths_dict.items():
            s_d_bw=0
            for path in paths:
                bw_list=[]
                for i in range(len(path)-1):
                    u, v = path[i], path[i + 1]
                    bw_list.append(1/link_load_dict[(u, v)])
                min_bw=min(bw_list)
                s_d_bw+=min_bw
            bw_dict[s_d]=s_d_bw
        return bw_dict
