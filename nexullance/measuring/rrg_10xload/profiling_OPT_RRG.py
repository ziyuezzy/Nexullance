import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.RRG import RRGtopo
from Nexullance_OPT import Nexullance_OPT
# from Nexullance_MP import Nexullance_MP
# from Nexullance_IT import Nexullance_IT
import globals as gl
import numpy as np
import time
import tracemalloc
import csv

# this is a script to profile Nexullance_OPT
# objectives: 
# 1. record result (\Phi) under several traffic patterns (uniform and shifts)
# 2. record time consumption
# 3. record maximum RAM

def main():
    # initialize output data file
    filename = f'data_RRG_OPT.csv'

    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'traffic_pattern', 'Lremote_MAX_ECMP_ASP', 'Llocal_MAX_ECMP_ASP', 'Phi_ECMP_ASP[Gbps]', 'Lremote_NEXU_OPT', 'Phi_NEXU[Gbps]', 'init_time[s]', 'solving_time[s]', 'peak_RAM[MB]'])
        

        configs = [(81, 10)]
        # configs = [(64, 9)]
        # configs = [(36, 7), (49, 8), (64, 9), (81, 10) , (100, 11)]
        # configs = [(16, 5), (25, 6), (36, 7), (49, 8), (64, 9), (81, 10) , (100, 11)]
        for V, D in configs:
            # various traffic patterns
            traffic_pattern = "uniform"
            result = profile((V,D), traffic_pattern, 0)
            csvwriter.writerow([V, D, traffic_pattern, result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            csvfile.flush()

            EPR=(D+1)//2
            traffic_pattern = "shift"
            result = profile((V,D), traffic_pattern, EPR)
            csvwriter.writerow([V, D, traffic_pattern+"_1", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            csvfile.flush()

            result = profile((V,D), traffic_pattern, EPR*V//4)
            csvwriter.writerow([V, D, traffic_pattern+"_quater", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            csvfile.flush()

            result = profile((V,D), traffic_pattern, EPR*V//2)
            csvwriter.writerow([V, D, traffic_pattern+"_half", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            csvfile.flush()

            traffic_pattern = "diagonal"
            result = profile((V,D), traffic_pattern, EPR)
            csvwriter.writerow([V, D, traffic_pattern+"_1", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            csvfile.flush()

            result = profile((V,D), traffic_pattern, EPR*V//4)
            csvwriter.writerow([V, D, traffic_pattern+"_quater", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            csvfile.flush()
            # diagonal half is the same as shift half
            # result = profile((V,D), traffic_pattern, EPR*V//2)
            # csvwriter.writerow([V, D, traffic_pattern+"_half", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            # csvfile.flush()
    return

def profile(config: tuple, traffic_pattern: str, _shift: int):
    EPR=(config[1]+1)//2
    _network = RRGtopo(config[0], config[1])
    Cap_remote = 10 #GBps
    Cap_local = 10 #GBps
    M_EPs = None
    if traffic_pattern == "uniform":
        M_EPs = gl.generate_uniform_traffic_pattern(config[0], EPR)
    elif traffic_pattern == "shift":
        M_EPs = gl.generate_shift_traffic_pattern(config[0], EPR, _shift)
    elif traffic_pattern == "diagonal":
        M_EPs = gl.generate_diagonal_traffic_pattern(config[0], EPR, _shift)
    else:
        raise ValueError("Invalidtraffic pattern name")


    # apply simple ECMP_ASP:
    ASP, _ = _network.calculate_all_shortest_paths()
    ECMP_ASP = gl.ECMP(ASP)
    remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
    max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    max_local_link_load = np.max(local_link_flows)/Cap_local
    # adapt the traffic scaling factor to 10x saturation
    traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
    M_EPs = traffic_scaling * M_EPs
    M_R = gl.convert_M_EPs_to_M_R(M_EPs, config[0], EPR)
    remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
    max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    max_local_link_load = np.max(local_link_flows)/Cap_local
    # print("Max remote link load: ", max_remote_link_load)
    # print("Max local link load: ", max_local_link_load)
    ECMP_ASP_Phi=gl.network_total_throughput(M_EPs, max_remote_link_load, max_local_link_load)

    tracemalloc.start()
    start_time = time.time()
    nexu = Nexullance_OPT(_network.nx_graph, M_R, Cap_remote, 0, False)
    nexu.init_model()
    middle_time = time.time()
    Lremote_NEXU_OPT = nexu.solve()
    end_time = time.time()
    peak_RAM = tracemalloc.get_traced_memory()[1]
    Phi_NEXU_OPT = gl.network_total_throughput(M_EPs, Lremote_NEXU_OPT, max_local_link_load)

    # current and peak memory usages are: {tracemalloc.get_traced_memory()} B")

    return [max_remote_link_load, max_local_link_load, ECMP_ASP_Phi, Lremote_NEXU_OPT, Phi_NEXU_OPT, middle_time - start_time, end_time - middle_time, peak_RAM]

if __name__ == '__main__':
    main()