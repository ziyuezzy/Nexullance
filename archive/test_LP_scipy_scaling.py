from globals import *
import topologies.RRG as RRG
import cvxpy as cp
# import pickle
import lp_load_balancing.LP_scipy as LP
import time
import tracemalloc


sf_configs=[(9, 4), (16, 5), (25, 6), (36, 7), (49, 8), (64, 9), (81, 10)]
config=sf_configs[6]
topo_name='jellyfish'

print(f"======== begin simulation for {topo_name} {config}========")

tracemalloc.start()
start_time = time.time()

_network = RRG.RRGtopo(config[0], config[1])
_result, edgelist, paths_dict =calculate_data_shortest_paths(_network, config)
print("before LP optimization, link load distribution is (min, ave, max):", _result['link_load_statistics'])

end_time_1 = time.time()

print(f"flow-level simulation done for {topo_name} {config}, \n \
    execution time is {end_time_1-start_time} s,\n  \
    current and peak memory usages are: {tracemalloc.get_traced_memory()} B")

all_weighted_paths=LP_cvspy.Solve_load_balancing(paths_dict,edgelist,_verbose=False)
end_time_2 = time.time()

link_load_dict=_network.distribute_uniform_flow_on_weighted_paths(all_weighted_paths)
_load_dict=list(link_load_dict.values())
_load_min=min(_load_dict)
_load_max=max(_load_dict)
_load_mean=mean(_load_dict)
print("after LP optimization, link load distribution is (min, ave, max):", _load_min, _load_mean, _load_max)

print(f"load balance optimization done, \n \
    execution time of the simplex solver is {end_time_2-end_time_1} s,\n  \
    current and peak memory usages are: {tracemalloc.get_traced_memory()} B")


tracemalloc.stop()