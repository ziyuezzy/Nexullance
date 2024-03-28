import nexullance.LP_gurobi as LP
import pickle
import topologies.RRG as RRG
import globals as gl
import time
import tracemalloc

tracemalloc.start()
start_time = time.time()


config=(722,29)
EPR=15
topo='jellyfish'
_network=RRG.RRGtopo(config[0], config[1])
edge_list=list(_network.nx_graph.edges())

uniform_traffic_matrix=gl.generate_uniform_traffic_pattern(config[0], EPR)
M_R_uniform=gl.convert_M_EPs_to_M_R(uniform_traffic_matrix, config[0], EPR)

results, _, path_dict = gl.calculate_data_shortest_paths(_network, config)
link_flows, local_link_flows=_network.distribute_arbitrary_flow_on_paths_with_EPs(path_dict, EPR, uniform_traffic_matrix)
print(f'predicted saturation load (before optimization) = {local_link_flows/max(link_flows)}')
# display(results)
all_weighted_paths, result_link_flows=LP.Solve_load_balancing(path_dict, edge_list,M_R_uniform, _verbose=1)
link_flows, local_link_flows=_network.distribute_arbitrary_flow_on_weighted_paths_with_EPs(all_weighted_paths, EPR, uniform_traffic_matrix)
print(f'predicted saturation load (after optimization) = {local_link_flows/max(link_flows)}')


end_time = time.time()
print(f"load balance optimization done, \n \
    execution time is {end_time-start_time} s,\n  \
    current and peak memory usages are: {tracemalloc.get_traced_memory()} B")
tracemalloc.stop()