import os
import sys
sys.path.append("/users/ziyzhang/topology-research")
from topologies.DDF import DDFtopo
from nexullance.MD_Nexullance_MP.MD_Nexullance_MP import MD_Nexullance_MP
from nexullance.Nexullance_MP import Nexullance_MP
sys.path.append("/users/ziyzhang/topology-research/nexullance/IT_boost/build")
from Nexullance_IT_cpp import Nexullance_IT_interface
from Nexullance_IT_cpp import MD_Nexullance_IT_interface
import globals as gl
import numpy as np
import pickle
import csv
import time
# import tracemalloc
import pandas as pd

Cap_remote = 10 #GBps
Cap_local = 10 #GBps

def main():
    config = gl.ddf_configs[0]
    V = config[0]
    D = config[1]
    EPR = (D+1)//2
    _network = DDFtopo(V, D)
    arcs = _network.generate_graph_arcs()

    ASP, _ = _network.calculate_all_shortest_paths()
    ECMP_ASP = gl.ECMP(ASP)

    M_Rs = []
    M_R_names = []
    M_EPs = []
    ECMP_ASP_Phis = []
    Nexullance_IT_Phis = []
    Nexullance_IT_time = []
    Nexullance_IT_peak_RAM = []
    max_local_link_loads = []

    # # # Define multiple traffic demand matrices:
    # # shifts
    for _shift in range(1, V*EPR):
    # for _shift in range(1, 5):
        M_EP = gl.generate_shift_traffic_pattern(V, EPR, _shift)
        # try to scale the traffic scaling factor to 10x saturation under ECMP_ASP
        remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EP)
        max_remote_link_load = np.max(remote_link_flows)/Cap_remote
        max_local_link_load = np.max(local_link_flows)/Cap_local
        traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
        M_EP = traffic_scaling * M_EP
        M_R = gl.convert_M_EPs_to_M_R(M_EP, V, EPR)
        remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EP)
        max_remote_link_load = np.max(remote_link_flows)/Cap_remote
        max_local_link_load = np.max(local_link_flows)/Cap_local
        # ==============
        # manage data
        M_EPs.append(M_EP)
        M_Rs.append(M_R)
        max_local_link_loads.append(max_local_link_load)
        M_R_names.append(f"shift_{_shift}")
    M_R_weights = [1/len(M_Rs) for _ in range(len(M_Rs))]

    Thresholds = [-0.0001, 0.0, 0.0001, 0.001, 0.01, 0.1, 1.0]
    Time_data = []
    obj_data = []

    for threshold in Thresholds:

        # calculate Phi for MD_Nexullance_IT routing
        md_nexu_it = MD_Nexullance_IT_interface(V, arcs, M_Rs, M_R_weights, False)
        # tracemalloc.start()
        start_time = time.time()
        md_nexu_it.run(4, threshold, 20000, True)
        end_time = time.time()
        # MD_peak_RAM = tracemalloc.get_traced_memory()[1]/1024/1024
        MD_time = end_time-start_time
        # tracemalloc.stop()

        Time_data.append(MD_time)
        obj_data.append(md_nexu_it.get_weighted_max_link_load())

    filename = f'DDF_{V}_{D}_MD_all_shifts_sweep_threshold.csv'
    # save data to csv file
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['threshold', 'time[s]', 'objective_func']) # TODO: number of steps
        csvfile.flush()
        for i, threshold in enumerate(Thresholds):
            csvwriter.writerow([threshold, Time_data[i], obj_data[i]])

if __name__ == '__main__':
    main()