import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.Polarfly import PFtopo
sys.path.append("/users/ziyzhang/topology-research/nexullance/IT_boost/build")
from Nexullance_IT_cpp import Nexullance_IT_interface
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

def main():

    # initialize output data file
    filename = f'data_PF_IT.csv'

    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'traffic_pattern', 'Phi_NEXU[GBps]', 'solving_time[s]', 'peak_RAM[MB]'])
        configs = gl.pf_regular_configs
        for V, D in configs:
            if V > 150:
                break
            # various traffic patterns
            traffic_pattern = "uniform"
            result = profile((V,D), traffic_pattern, 0)
            csvwriter.writerow([V, D, traffic_pattern, result[0], result[1], result[2] ])
            
            EPR=(D+1)//2
            traffic_pattern = "shift"
            result = profile((V,D), traffic_pattern, EPR)
            csvwriter.writerow([V, D, traffic_pattern+"_1", result[0], result[1], result[2] ])
            
            result = profile((V,D), traffic_pattern, EPR*V//4)
            csvwriter.writerow([V, D, traffic_pattern+"_quater", result[0], result[1], result[2] ])
            
            result = profile((V,D), traffic_pattern, EPR*V//2)
            csvwriter.writerow([V, D, traffic_pattern+"_half", result[0], result[1], result[2] ])
            
            traffic_pattern = "diagonal"
            result = profile((V,D), traffic_pattern, EPR)
            csvwriter.writerow([V, D, traffic_pattern+"_1", result[0], result[1], result[2] ])
            
            result = profile((V,D), traffic_pattern, EPR*V//4)
            csvwriter.writerow([V, D, traffic_pattern+"_quater", result[0], result[1], result[2] ])
            
            # diagonal half is the same as shift half
            # result = profile((V,D), traffic_pattern, EPR*V//2)
            # csvwriter.writerow([V, D, traffic_pattern+"_half", result[0], result[1], result[2] ])
            
            csvfile.flush()
    return

def profile(config: tuple, traffic_pattern: str, _shift: int):
    EPR=(config[1]+1)//2
    _network = PFtopo(config[0], config[1])
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
    ASP, _ = _network.calculate_all_shortest_paths()
    arcs = _network.generate_graph_arcs()
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

    ave_peak_RAM = 0
    ave_time = 0
    reptition = 10
    for i in range(reptition):
        tracemalloc.start()
        # run Nexullance_IT
        nexu_it = Nexullance_IT_interface(config[0], arcs, M_R, False)
        start_time = time.time()
        nexu_it.run()
        end_time = time.time()
        time_IT = end_time - start_time
        peak_RAM = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        ave_peak_RAM += peak_RAM
        ave_time += time_IT
    ave_peak_RAM /= reptition
    ave_time /= reptition

    Lremote_NEXU_IT=nexu_it.get_max_link_load()
    Phi_NEXU_IT = gl.network_total_throughput(M_EPs, Lremote_NEXU_IT, max_local_link_load)
    
    return [Phi_NEXU_IT, ave_time, ave_peak_RAM/1E6]

if __name__ == '__main__':
    main()

