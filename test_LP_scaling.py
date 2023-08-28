from globals import *
import topologies.Slimfly as Slimfly
import cvxpy as cp
# import pickle
import lp_load_balancing.LP as LP
import time
import tracemalloc

sf_configs=[(18, 5), (32, 6), (98, 11), (242, 17)]
topo_name='slimfly'

for config in sf_configs:

    print(f"======== begin simulation for {topo_name} {config}========")

    tracemalloc.start()
    start_time = time.time()

    _network = Slimfly.Slimflytopo(config[0], config[1])
    _result, edgelist, paths_dict =calculate_data_paths_within_length(_network, config, 2)

    end_time_1 = time.time()

    print(f"flow-level simulation done for {topo_name} {config}, \n \
        execution time is {end_time_1-start_time} s,\n  \
        current and peak memory usages are: {tracemalloc.get_traced_memory()} B")

    LP.Solve_load_balancing(paths_dict,edgelist)

    end_time_2 = time.time()


    print(f"load balance optimization done, \n \
        execution time is {end_time_2-end_time_1} s,\n  \
        current and peak memory usages are: {tracemalloc.get_traced_memory()} B")


    tracemalloc.stop()