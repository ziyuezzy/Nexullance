import lp_load_balancing.LP_gurobi as LP
# import pickle
import topologies.Slimfly as Slimfly
import globals as gl
import time
import tracemalloc
from statistics import mean


configs=[(32, 6)]
config=configs[0]
topo_name='slimfly'

print(f"======== begin simulation for {topo_name} {config} with all shortest paths========")

tracemalloc.start()
start_time = time.time()

_network = Slimfly.Slimflytopo(config[0], config[1])
_result, edgelist, paths_dict =gl.calculate_data_shortest_paths(_network, config)
print("before LP optimization, shortest-path routing leads to link load distribution (min, ave, max):", _result['link_load_statistics'])

# path_length_restriction=6
# print(f"======== begin simulation for {topo_name} {config} with path_length_restriction={path_length_restriction}========")

# tracemalloc.start()
# start_time = time.time()

# _network = Slimfly.Slimflytopo(config[0], config[1])
# _result, edgelist, paths_dict =gl.calculate_data_paths_within_length(_network, config, path_length_restriction)
# print("before LP optimization, shortest-path routing leads to link load distribution (min, ave, max):", _result['link_load_statistics'])

end_time_1 = time.time()

print(f"flow-level simulation done for {topo_name} {config} with shortest path routing, \n \
    execution time is {end_time_1-start_time} s,\n  \
    current and peak memory usages are: {tracemalloc.get_traced_memory()} B")

all_weighted_paths, result_link_loads=LP.Solve_load_balancing(paths_dict,edgelist,_verbose=False)
end_time_2 = time.time()

link_load_dict=_network.distribute_uniform_flow_on_weighted_paths(all_weighted_paths)
_load_dict=list(link_load_dict.values())
_load_min=min(_load_dict)
_load_max=max(_load_dict)
_load_mean=mean(_load_dict)
print("after LP optimization, link load distribution is (min, ave, max):", _load_min, _load_mean, _load_max)

print(f"load balance optimization done, \n \
    execution time is {end_time_2-end_time_1} s,\n  \
    current and peak memory usages are: {tracemalloc.get_traced_memory()} B")


tracemalloc.stop()