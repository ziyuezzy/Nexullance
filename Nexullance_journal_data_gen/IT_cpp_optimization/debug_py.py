import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.DDF import DDFtopo
from nexullance.Nexullance_IT import Nexullance_IT
import globals as gl
import numpy as np
import csv


Cap_remote = 10 #GBps
Cap_local = 10 #GBps
alpha_1 = 1
beta_1 = 1
alpha_2 = 0.1
beta_2 = 7

def weighted_method_1(s: int, d: int, edge_attributes: dict):
    return alpha_1 + edge_attributes['load']**beta_1
def weighted_method_2(s: int, d: int, edge_attributes: dict):
    return alpha_2 + edge_attributes['load']**beta_2

def main():
    # initialize output data file
    filename = f'DDF.csv'
    config = gl.ddf_configs[-1]
    V = config[0]
    D = config[1]
    EPR = (D+1)//2

    _network = DDFtopo(V, D)
    ASP, _ = _network.calculate_all_shortest_paths()
    ECMP_ASP = gl.ECMP(ASP)

    traffic_pattern = "router-cluster"
    M_EPs = gl.generate_uniform_cluster_pattern(V, EPR, 4) # four clusters
    remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
    max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    max_local_link_load = np.max(local_link_flows)/Cap_local
    # adapt the traffic scaling factor to 10x saturation
    traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
    M_EPs = traffic_scaling * M_EPs
    remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
    max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    max_local_link_load = np.max(local_link_flows)/Cap_local
    nexu = Nexullance_IT(_network.nx_graph, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_remote)
    _, _ = nexu.optimize(1, 6, weighted_method_1, weighted_method_2, V)
    Lremote_NEXU = nexu.get_result_max_link_load()
    Phi = gl.network_total_throughput(M_EPs, Lremote_NEXU, max_local_link_load)
    print(f"phi: {Phi/(V*EPR)}")


if __name__ == '__main__':
    main()
