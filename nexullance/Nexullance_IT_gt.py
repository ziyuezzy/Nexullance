import networkx as nx
from joblib import Parallel, delayed
from random import sample, shuffle
import time
import tracemalloc
import numpy as np
from graph_tool.all import *

nxGraph = nx.graph.Graph
nxDiGraph = nx.DiGraph

class Nexullance_IT_gt:
    def __init__(self, _nx_graph: nxGraph, _M_R: np.ndarray, _Cap_remote: float, _verbose:bool=False):
        # clear node and edge attributes
        for (n1, n2, d) in _nx_graph.edges(data=True):
            d.clear()
        for (n1, d) in _nx_graph.nodes(data=True):
            d.clear()
        nx_digraph = _nx_graph.to_directed()

        # convert the nx graph to graph_tool graph
        self.gt_graph = Graph(directed=True)
        self.gt_graph.add_vertex(len(nx_digraph.nodes()))
        self.gt_graph.add_edge_list([(n1, n2) for (n1, n2) in nx_digraph.edges()])

        # initialize necessary variables
        self.M_R = _M_R
        self.Cap_remote = _Cap_remote
        self.verbose = _verbose
        self.result_max_link_load: float = 0.0
        self.method_2_attempts: int = 0

        # initialize the data structures for Nexullance_IT step1 and step2:

        self.next_path_id: int = 0
        # the routing table is a dictionary of dictionary of dictionary,
        # the key of the first dictionary is the source node, and the key of the second dictionary is the destination node
        # the key of the third dictionary is the unique ids of paths, and the value is the weight of the path
        self.routing_table: dict = {}
        # hashing path ids to the actual paths,
        self.path_id_to_path: dict = {}
        # the load of edges (EdgePropertyMap)
        self.link_load: EdgePropertyMap = self.gt_graph.new_edge_property("double", val=0.0)
        # the weight of edges (EdgePropertyMap)
        self.link_weight: EdgePropertyMap = self.gt_graph.new_edge_property("double", val=1.0)
        # the path ids that traverse the edges (EdgePropertyMap)
        self.link_path_ids: EdgePropertyMap = self.gt_graph.new_edge_property("object")

    def step1(self, _alpha: float=1.0, _beta: float=1.0):
        
        # first clear the edge properties
        self.link_load.a[:] = 0.0
        self.link_weight.a[:] = 1.0
        for e in self.gt_graph.edges():
            self.link_path_ids[e] = set()
        self.next_path_id=0

        # we iterate through the source nodes to calculate the predicessor map from that source node
        # for now, we can only calculate all shortest paths for each pair of nodes seperately, this is due to the graph-tool library.
        # Alternatively, we could do a single search and determine the shortest paths for all dst nodes (cfr. networkx implementataion) (#TODO)
        all_paths_all_s_d = {}
        for src in self.gt_graph.vertices():
            if self.verbose:
                print(f"Calculating shortest paths from node {src}...")
            dist, pred = shortest_distance(self.gt_graph, source=src, weights=self.link_weight, pred_map=True)
            all_pred = all_predecessors(self.gt_graph, dist, pred, weights=self.link_weight)

            for dst in self.gt_graph.vertices(): 
                all_paths_all_s_d[(src, dst)] = list(all_shortest_paths(self.gt_graph, src, dst, all_preds_map= all_pred))

        for src in self.gt_graph.vertices():
            self.routing_table[src]={}
            for dst in self.gt_graph.vertices():
                self.routing_table[src][dst]={}
                if dst == src:
                    continue
                paths = all_paths_all_s_d[(src, dst)]
                assert(paths)
                for path in paths:
                    path_id = self.next_path_id
                    self.next_path_id += 1
                    self.path_id_to_path[path_id] = path
                    self.routing_table[src][dst][path_id] = 1/len(paths)
                    for i in range(len(path)-1):
                        # e = self.gt_graph.edge(path[i], path[i+1])
                        self.link_path_ids[(path[i], path[i+1])].add(path_id)
                        self.link_load[(path[i], path[i+1])] += self.M_R[self.gt_graph.vertex_index[src], self.gt_graph.vertex_index[dst]]*1/len(paths)/self.Cap_remote  
                        self.link_weight[(path[i], path[i+1])] = self.link_load[(path[i], path[i+1])]**_beta + _alpha
        return np.max(self.link_load.a)


    # Calculating all shortest paths between two nodes in a graph: "all_shortest_paths" API in gt ,
    # contains calling "shortest_distance (single source dijkstra)", then "all_predecessors", and then pass it to "all_shortest_paths"
    def step2(self, _alpha: float, _beta: float, step: float, threshold: float = 0.001,
              min_attempts: int = 50 , max_attempts: int = 100000)-> 'tuple[bool, list]':
        
        max_link_loads = []
        attempts:int = 0
        while True:
            if attempts >= max_attempts:
                if self.verbose:
                    print(f"Maximum number of attempts reached ({max_attempts})")
                return (True, [max_link_loads[-1]])   
            max_link_load = np.max(self.link_load.a)
            max_link_loads.append(max_link_load)
            if (attempts >= min_attempts) and ((np.average(max_link_loads[-min_attempts//2:-1]) - max_link_load) < threshold ):
                if self.verbose:
                    print(f"Convergence achieved after {attempts} attempts")
                return (True, [max_link_loads[-1]])   
            max_loaded_links = [e for e in self.gt_graph.edges() if self.link_load[e] == max_link_load]
            
            success_attempt: bool = False
            for e in max_loaded_links:
                current_paths_id: set = self.link_path_ids[e]
                path_contributions = {} # to be sorted
                for path_id in current_paths_id:
                    path = self.path_id_to_path[path_id]
                    src = path[0]
                    dst = path[-1]
                    path_contributions[path_id] = self.routing_table[src][dst][path_id] * self.M_R[self.gt_graph.vertex_index[src], self.gt_graph.vertex_index[dst]]
                    
                
                for old_path_id in sorted(path_contributions, key=lambda k: path_contributions[k], reverse=True):
                    old_path = self.path_id_to_path[old_path_id]
                    src = old_path[0]
                    dst = old_path[-1]
                    new_paths = list(all_shortest_paths(self.gt_graph, src, dst, weights=self.link_weight))
                    shuffle(new_paths)
                    for new_path in new_paths:
                        if (list(new_path) != list(old_path)):
                            success_attempt = True
                            attempts+=1
                            self.update_paths(old_path_id, old_path, 
                                    new_path, src, dst, step, alpha=_alpha, beta=_beta)
                            break

                    if success_attempt and np.max(self.link_load.a)!= max_link_load:
                        break
                    else:
                        continue

                if success_attempt:
                    break
                else:
                    continue
            if success_attempt:
                continue # go to the next iteration
            else:
                if self.verbose:
                    print("No possible progress, terminating.")
                return (False, [max_link_loads[-1]]) 
            
    def update_paths(self, old_path_id: int, old_path:list, 
                     new_path: list, src:int, dst:int, step:float, alpha:float=1.0, beta:float=1.0):
        old_path_weight = self.routing_table[src][dst][old_path_id]
        # first check whether the new path is already in the routing table
        new_path_exists = False
        new_path_id = None
        delta_weight = None
        
        current_path_dict = self.routing_table[src][dst]
        for path_id, weight in current_path_dict.items():
            if (list(self.path_id_to_path[path_id]) == list(new_path)):
                new_path_exists = True
                new_path_id = path_id
                delta_weight = min([step, old_path_weight, 1-weight])
                self.routing_table[src][dst][new_path_id] += delta_weight
                break
        if not new_path_exists:
            assert(delta_weight is None)
            # if the new path is not in the routing table, give it new id and add it to the graph attributes(later)
            new_path_id = self.next_path_id
            self.next_path_id += 1
            self.path_id_to_path[new_path_id] = new_path
            delta_weight = min([step, old_path_weight])
            assert(new_path_id not in self.routing_table[src][dst])
            self.routing_table[src][dst][new_path_id] = delta_weight

        # update the edge properties of the new links
        for i in range(len(new_path)-1):
            self.link_load[(new_path[i], new_path[i+1])] += delta_weight*self.M_R[self.gt_graph.vertex_index[src], self.gt_graph.vertex_index[dst]]/self.Cap_remote
            self.link_weight[(new_path[i], new_path[i+1])] = self.link_load[(new_path[i], new_path[i+1])]**beta + alpha
            if not new_path_exists:
                self.link_path_ids[(new_path[i], new_path[i+1])].add(new_path_id)

        # update the edge properties of the old links        
        # first handle the weight
        self.routing_table[src][dst][old_path_id] -= delta_weight
        # then handle the link loads
        for i in range(len(old_path)-1):
            self.link_load[(old_path[i], old_path[i+1])] -= delta_weight*self.M_R[self.gt_graph.vertex_index[src], self.gt_graph.vertex_index[dst]]/self.Cap_remote
            self.link_weight[(old_path[i], old_path[i+1])] = self.link_load[(old_path[i], old_path[i+1])]**beta + alpha
            # if the remaining weight of the old path is very small, delete the old path
            if self.routing_table[src][dst][old_path_id] < 0.0001:
                self.link_path_ids[(old_path[i], old_path[i+1])].remove(old_path_id)

        if self.routing_table[src][dst][old_path_id] < 0.0001:
            del self.routing_table[src][dst][old_path_id]
            del self.path_id_to_path[old_path_id]

    def optimize(self, num_step_1:int, alpha_step_1:float  , beta_step_1:float,
                 max_num_step_2: int, alpha_step_2:float  , beta_step_2:float,
                    method_2_min_attempts: int = 50):
        assert(num_step_1 >= 1 and "num_step_1 should be a positive integer greater than 1.")
        results_method_1 = []
        for i in range(num_step_1):
            max_link_load = self.step1(alpha_step_1, beta_step_1)
            results_method_1.append(max_link_load)
            
        self.result_max_link_load = results_method_1[-1]

        self.results_method_2 = []
        tot_attempts = 0
        # each time decreasing the step parameter by a factor of 0.5.
        step = 0.5
        for i in range(max_num_step_2):
            (_continue, max_link_loads) = self.step2(alpha_step_2, 
                    beta_step_2, step, min_attempts=method_2_min_attempts)
            self.results_method_2.extend(max_link_loads)
            step *= 0.5
            if not _continue:
                break
        if self.results_method_2:
            self.result_max_link_load = self.results_method_2[-1]
        return results_method_1, self.results_method_2
    
    def get_result_max_link_load(self):
        return self.result_max_link_load
    
    def get_step_2_iterations(self):
        return len(self.results_method_2)
    
    def get_routing_table(self):
        weighted_path_dict = {}
        for src in self.routing_table:
            int_src = self.gt_graph.vertex_index[src]            
            for dst in self.routing_table[src]:
                int_dst = self.gt_graph.vertex_index[dst]
                if int_src == int_dst:
                    continue
                weighted_path_dict[(int_src, int_dst)] = []
                for path_id in self.routing_table[src][dst]:
                    path = self.path_id_to_path[path_id]
                    weight = self.routing_table[src][dst][path_id]
                    weighted_path_dict[(int_src, int_dst)].append((list(path), weight))
        return weighted_path_dict