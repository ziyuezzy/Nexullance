import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.RRG import RRGtopo
# from Nexullance_IT import Nexullance_IT
# from Nexullance_MP import Nexullance_MP
from Nexullance_IT import Nexullance_IT
import globals as gl
import numpy as np
import time
import tracemalloc
import csv
import pickle

# this is a script to profile Nexullance_IT
# objectives: 
# 1. record result (\Phi) under several traffic patterns (uniform and shifts)
# 2. record time consumption
# 3. record maximum RAM

num_method_1 = 4
num_method_2 = 6

def main():

    # initialize output data file
    filename = f'data_RRG_IT_{num_method_1}+{num_method_2}.csv'

    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'traffic_pattern', 'Lremote_MAX_ECMP_ASP', 'Llocal_MAX_ECMP_ASP', 'Phi_ECMP_ASP[Gbps]', 
                            'Lremote_NEXU_IT', 'Phi_NEXU[Gbps]', 'method1_times[s]', 'method1_peak_RAMs[MB]', 'method1_results[Gbps]',
                            'method2_time[s]', 'method2_attempts', 'method2_peak_RAM[MB]'])
        
        # configs = [(16, 5), (25, 6)]
        configs = [(16, 5), (25, 6), (36, 7), (49, 8), (64, 9), (81, 10) , (100, 11)]
        for V, D in configs:
            # various traffic patterns
            traffic_pattern = "uniform"
            result = profile((V,D), traffic_pattern, 0)
            csvwriter.writerow([V, D, traffic_pattern, result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10] ])
            
            EPR=(D+1)//2
            traffic_pattern = "shift"
            result = profile((V,D), traffic_pattern, EPR)
            csvwriter.writerow([V, D, traffic_pattern+"_1", result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10] ])
            
            result = profile((V,D), traffic_pattern, EPR*V//4)
            csvwriter.writerow([V, D, traffic_pattern+"_quater", result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10] ])
            
            result = profile((V,D), traffic_pattern, EPR*V//2)
            csvwriter.writerow([V, D, traffic_pattern+"_half", result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10] ])
            
            traffic_pattern = "diagonal"
            result = profile((V,D), traffic_pattern, EPR)
            csvwriter.writerow([V, D, traffic_pattern+"_1", result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10] ])
            
            result = profile((V,D), traffic_pattern, EPR*V//4)
            csvwriter.writerow([V, D, traffic_pattern+"_quater", result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10] ])
            
            # diagonal half is the same as shift half
            # result = profile((V,D), traffic_pattern, EPR*V//2)
            # csvwriter.writerow([V, D, traffic_pattern+"_half", result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10] ])
            
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
    elif traffic_pattern == "shift":
        M_EPs = gl.generate_shift_traffic_pattern(config[0], EPR, _shift)
    elif traffic_pattern == "diagonal":
        M_EPs = gl.generate_diagonal_traffic_pattern(config[0], EPR, _shift)
    else:
        raise ValueError("Invalidtraffic pattern name")


    # apply simple ECMP:
    ASP = _network.calculate_all_shortest_paths()
    ECMP = gl.ECMP(ASP)
    remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP, EPR, M_EPs)
    max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    max_local_link_load = np.max(local_link_flows)/Cap_local
    # adapt the traffic scaling factor to 10x saturation
    traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
    M_EPs = traffic_scaling * M_EPs
    M_R = gl.convert_M_EPs_to_M_R(M_EPs, config[0], EPR)
    remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP, EPR, M_EPs)
    max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    max_local_link_load = np.max(local_link_flows)/Cap_local
    # print("Max remote link load: ", max_remote_link_load)
    # print("Max local link load: ", max_local_link_load)
    ECMP_Phi=gl.network_total_throughput(M_EPs, max_remote_link_load, max_local_link_load)

    alpha_1 = 40.0
    beta_1 = 0.4
    alpha_2 = 3
    beta_2 = 7
    def weighted_method_1(s: int, d: int, edge_attributes: dict):
        return alpha_1 + edge_attributes['load']**beta_1
    def weighted_method_2(s: int, d: int, edge_attributes: dict):
        return alpha_2 + edge_attributes['load']**beta_2

    nexu_it = Nexullance_IT(_network.nx_graph, M_R, Cap_remote)
    times_method_1, peakRAMs_method_1, time_method_2, peakRAM_method_2, results_method_1 = nexu_it.optimize_and_profile(
    num_method_1, num_method_2, weighted_method_1, weighted_method_2, alt = True)

    Lremote_NEXU_IT=nexu_it.get_result_max_link_load()
    method_2_attempts=nexu_it.get_method_2_attempts()
    Phi_NEXU_IT = gl.network_total_throughput(M_EPs, Lremote_NEXU_IT, max_local_link_load)
    results_method_1 = [gl.network_total_throughput(M_EPs, results_method_1[i], max_local_link_load) for i in range(len(results_method_1))]

    return [max_remote_link_load, max_local_link_load, ECMP_Phi, Lremote_NEXU_IT, Phi_NEXU_IT, 
            times_method_1, [x/1E6 for x in peakRAMs_method_1], results_method_1,
            time_method_2, method_2_attempts, peakRAM_method_2/1E6]

if __name__ == '__main__':
    main()

