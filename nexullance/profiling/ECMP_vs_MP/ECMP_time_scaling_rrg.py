import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
from topologies.RRG import RRGtopo
from Nexullance_MP import Nexullance_MP
# from Nexullance_IT import Nexullance_IT
import globals as gl
import numpy as np
import time
# import tracemalloc
import csv
import pickle

# this is a script to compare the computing time of:
# ECMP_ASP and Nexullance_MP_ASP
# ECMP_APST_4 and Nexullance_MP_APST_4

def main():
    # initialize output data file
    traffic_pattern = "shift_half"
    filename = f'data_RRG_time_scaling_{traffic_pattern}.csv'
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'time_ASP', 'time_APST_4', 'time_MP_ASP', 'time_MP_APST_4'])
        
        configs = [(16, 5), (25, 6), (36, 7), (49, 8), (64, 9), (81, 10) , (100, 11)]
        for V, D in configs:
            # various traffic patterns
            result = profile((V,D), traffic_pattern, 0)
            csvwriter.writerow([V, D, result[0], result[1], result[2], result[3]])
            csvfile.flush()
    return

def profile(config: tuple, traffic_pattern: str, _shift: int):
    EPR=(config[1]+1)//2
    _network = RRGtopo(config[0], config[1])
    Cap_remote = 10 #GBps
    Cap_local = 10 #GBps
    M_EPs = None
    if traffic_pattern == "uniform":
        M_EPs = gl.generate_uniform_traffic_pattern(config[0], EPR)
    elif traffic_pattern == "shift_half":
        M_EPs = gl.generate_half_shift_traffic_pattern(config[0], EPR)
    elif traffic_pattern == "shift":
        M_EPs = gl.generate_shift_traffic_pattern(config[0], EPR, _shift)
    elif traffic_pattern == "diagonal":
        M_EPs = gl.generate_diagonal_traffic_pattern(config[0], EPR, _shift)
    else:
        raise ValueError("Invalidtraffic pattern name")


    # apply simple ECMP_ASP: (to make sure the input matrix for all nexu methods are the same)
    start_time = time.time()
    ASP, _ = _network.calculate_all_shortest_paths()
    ASP_time = time.time() - start_time

    start_time = time.time()
    APST4 = _network.calculate_all_paths_within_length(4)
    APST4_time = time.time() - start_time

    ECMP_ASP = gl.ECMP(ASP)
    remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
    max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    max_local_link_load = np.max(local_link_flows)/Cap_local
    # adapt the traffic scaling factor to 10x saturation
    traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
    M_EPs = traffic_scaling * M_EPs
    M_R = gl.convert_M_EPs_to_M_R(M_EPs, config[0], EPR)
    # remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
    # max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    # max_local_link_load = np.max(local_link_flows)/Cap_local
    # print("Max remote link load: ", max_remote_link_load)
    # print("Max local link load: ", max_local_link_load)
    # ECMP_ASP_Phi=gl.network_total_throughput(M_EPs, max_remote_link_load, max_local_link_load)
    # # apply simple ECMP_MP_APST4:
    # ECMP_MP_APST4 = gl.ECMP(MP_APST4)
    # remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_MP_APST4, EPR, M_EPs)
    # max_remote_link_load_APST_4 = np.max(remote_link_flows)/Cap_remote
    # max_local_link_load_APST_4 = np.max(local_link_flows)/Cap_local
    # ECMP_MP_APST4_Phi=gl.network_total_throughput(M_EPs, max_remote_link_load_APST_4, max_local_link_load_APST_4)

    start_time = time.time()
    nexu = Nexullance_MP(_network.nx_graph, ASP, M_R, Cap_remote, 0, False)
    nexu.init_model()
    _, _ = nexu.solve()
    NEXU_MP_MP_ASP_time = time.time() - start_time

    start_time = time.time()
    nexu = Nexullance_MP(_network.nx_graph, APST4, M_R, Cap_remote, 0, False)
    nexu.init_model()
    _, _ = nexu.solve()
    NEXU_MP_MP_APST4_time = time.time() - start_time
    
    return [ASP_time, APST4_time, NEXU_MP_MP_ASP_time, NEXU_MP_MP_APST4_time]

if __name__ == '__main__':
    main()