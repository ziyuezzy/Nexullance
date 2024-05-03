import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.RRG import RRGtopo
from Nexullance_IT import Nexullance_IT
import cProfile, pstats
import globals as gl
import numpy as np

num_method_1 = 4
num_method_2 = 0

def main():

    config = (36, 5)
    EPR=(config[1]+1)//2
    _network = RRGtopo(config[0], config[1])
    Cap_remote = 10 #GBps
    Cap_local = 10 #GBps
    M_EPs = gl.generate_uniform_traffic_pattern(config[0], EPR)
    # apply simple ECMP:
    ASP, _ = _network.calculate_all_shortest_paths()
    ECMP = gl.ECMP(ASP)
    remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP, EPR, M_EPs)
    max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    max_local_link_load = np.max(local_link_flows)/Cap_local
    # adapt the traffic scaling factor to 10x saturation
    traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
    M_EPs = traffic_scaling * M_EPs
    M_R = gl.convert_M_EPs_to_M_R(M_EPs, config[0], EPR)
    alpha_1 = 40.0
    beta_1 = 0.4
    alpha_2 = 3
    beta_2 = 7
    def weighted_method_1(s: int, d: int, edge_attributes: dict):
        return alpha_1 + edge_attributes['load']**beta_1
    def weighted_method_2(s: int, d: int, edge_attributes: dict):
        return alpha_2 + edge_attributes['load']**beta_2
    nexu_it = Nexullance_IT(_network.nx_graph, M_R, Cap_remote)
    nexu_it.initialize()
    profiler = cProfile.Profile()
    profiler.enable()
    init_for_method2=False
    for i in range(num_method_1):
        if i == num_method_1-1:
            init_for_method2 = True
        _ = nexu_it.optimization_method_1(init_for_method2, weighted_method_1)

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()


# Sort output by Cumulative time
if __name__ == '__main__':
    main()