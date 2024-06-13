import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
# sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.RRG import RRGtopo
from MD_Nexullance.MD_Nexullance_MP import MD_Nexullance_MP
from nexullance.Nexullance_MP import Nexullance_MP
import globals as gl
import numpy as np
import pickle
import csv
import time
import tracemalloc

def main():
    # parse inputs: should contain two integers: V and D
    assert(len(sys.argv) == 3)
    V = int(sys.argv[1])
    D = int(sys.argv[2])
    # TODO: input MRs and MR weights

    EPR = (D+1)//2
    _network = RRGtopo(V, D)
    Cap_remote = 10 #GBps
    Cap_local = 10 #GBps

    ASP, _ = _network.calculate_all_shortest_paths()
    ECMP_ASP = gl.ECMP(ASP)
    MP_APST4, _ = _network.calculate_all_paths_within_length(4)
    ECMP_MP_APST4 = gl.ECMP(MP_APST4)

    M_Rs = []
    M_R_names = []
    M_EPs = []
    ECMP_ASP_Phis = []
    Nexullance_MP_ASPT4_Phis = []
    Nexullance_MP_ASPT4_time = []
    Nexullance_MP_ASPT4_peak_RAM = []
    max_local_link_loads = []


    # # # Define multiple traffic demand matrices:

    # # # uniform
    # M_EP = gl.generate_uniform_traffic_pattern(V, EPR)
    # # try to scale the traffic scaling factor to 10x saturation under ECMP_ASP
    # remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EP)
    # max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    # max_local_link_load = np.max(local_link_flows)/Cap_local
    # traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
    # M_EP = traffic_scaling * M_EP
    # M_R = gl.convert_M_EPs_to_M_R(M_EP, V, EPR)
    # # calculate Phi for ECMP_ASP routing
    # remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EP)
    # max_remote_link_load = np.max(remote_link_flows)/Cap_remote
    # max_local_link_load = np.max(local_link_flows)/Cap_local
    # ECMP_ASP_Phi=gl.network_total_throughput(M_EP, max_remote_link_load, max_local_link_load)
    # # calculate Phi for Nexullance_MP_APST4 routing
    # nexu = Nexullance_MP(_network.nx_graph, MP_APST4, M_R, Cap_remote, 0, False)
    # tracemalloc.start()
    # start_time = time.time()
    # nexu.init_model()
    # Lremote_NEXU_MP_MP_APST4, _ = nexu.solve()
    # end_time = time.time()
    # peak_RAM = tracemalloc.get_traced_memory()[1]
    # Nexullance_MP_ASPT4_peak_RAM.append(peak_RAM/1024/1024)
    # Nexullance_MP_ASPT4_time.append(end_time-start_time)
    # tracemalloc.stop()
    # Phi_NEXU_MP_APST4 = gl.network_total_throughput(M_EP, Lremote_NEXU_MP_MP_APST4, max_local_link_load)
    # # manage data
    # ECMP_ASP_Phis.append(ECMP_ASP_Phi)
    # Nexullance_MP_ASPT4_Phis.append(Phi_NEXU_MP_APST4)
    # M_EPs.append(M_EP)
    # M_Rs.append(M_R)
    # max_local_link_loads.append(max_local_link_load)
    # M_R_names.append("uniform")

    # # shifts
    for _shift in range(1, V*EPR):
        M_EP = gl.generate_shift_traffic_pattern(V, EPR, _shift)
        # try to scale the traffic scaling factor to 10x saturation under ECMP_ASP
        remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EP)
        max_remote_link_load = np.max(remote_link_flows)/Cap_remote
        max_local_link_load = np.max(local_link_flows)/Cap_local
        traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
        M_EP = traffic_scaling * M_EP
        M_R = gl.convert_M_EPs_to_M_R(M_EP, V, EPR)
        # calculate Phi for ECMP_ASP routing
        remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EP)
        max_remote_link_load = np.max(remote_link_flows)/Cap_remote
        max_local_link_load = np.max(local_link_flows)/Cap_local
        ECMP_ASP_Phi=gl.network_total_throughput(M_EP, max_remote_link_load, max_local_link_load)
        # calculate Phi for Nexullance_MP_APST4 routing
        nexu = Nexullance_MP(_network.nx_graph, MP_APST4, M_R, Cap_remote, 0, False)
        tracemalloc.start()
        start_time = time.time()
        nexu.init_model()
        Lremote_NEXU_MP_MP_APST4, _ = nexu.solve()
        end_time = time.time()
        peak_RAM = tracemalloc.get_traced_memory()[1]
        Nexullance_MP_ASPT4_peak_RAM.append(peak_RAM/1024/1024)
        Nexullance_MP_ASPT4_time.append(end_time-start_time)
        tracemalloc.stop()
        Phi_NEXU_MP_APST4 = gl.network_total_throughput(M_EP, Lremote_NEXU_MP_MP_APST4, max_local_link_load)
        # manage data
        ECMP_ASP_Phis.append(ECMP_ASP_Phi)
        Nexullance_MP_ASPT4_Phis.append(Phi_NEXU_MP_APST4)
        M_EPs.append(M_EP)
        M_Rs.append(M_R)
        max_local_link_loads.append(max_local_link_load)
        M_R_names.append(f"shift_{_shift}")

    M_R_weights = [1/len(M_Rs) for _ in range(len(M_Rs))]

    nexu = MD_Nexullance_MP(_network.nx_graph, MP_APST4, M_Rs, M_R_weights, Cap_remote, 0, False)
    tracemalloc.start()
    start_time = time.time()
    nexu.init_model()
    Lremote_for_MRs, weight_path_dict = nexu.solve()
    end_time = time.time()
    MMR_peak_RAM = tracemalloc.get_traced_memory()[1]/1024/1024
    MMR_time = end_time-start_time
    tracemalloc.stop()

    MMR_Phis = []
    for i, M_EP in enumerate(M_EPs):
        MMR_Phis.append(gl.network_total_throughput(M_EP, Lremote_for_MRs[i], max_local_link_loads[i]))

    # pickle output routing tables
    routing_name = f"NEXU_MP_APST_all_shifts"
    pathdict_file=f"{routing_name}_({V},{D})RRGtopo_paths.pickle"
    with open(pathdict_file, 'wb') as handle:
        pickle.dump(gl.clean_up_weighted_paths(weight_path_dict), handle)

    filename = f'RRG_{V}_{D}_MP_MMR_all_shifts.csv'
    # save data to csv file
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['included_M_R', 'Phi_ECMP_ASP', 
                            'Phi_MP_APST4', 'Phi_MP_MMR_APST4', 'MMR_to_MP_ratio',
                            'time_MP_APST4[s]', 'peak_RAM_MP_APST4[MB]', 
                            'time_MP_MMR_APST4[s]', 'peak_RAM_MP_MMR_APST4[s][MB]'])
        # csvfile.flush()
        for i in range(len(M_EPs)):
            csvwriter.writerow([M_R_names[i], ECMP_ASP_Phis[i], 
                                Nexullance_MP_ASPT4_Phis[i], MMR_Phis[i], MMR_Phis[i]/Nexullance_MP_ASPT4_Phis[i],
                                Nexullance_MP_ASPT4_time[i], Nexullance_MP_ASPT4_peak_RAM[i],
                                0, 0])
            # csvfile.flush()
        csvwriter.writerow([ "total" , 0, 
                0, 0, 0,
                0, 0,
                MMR_time, MMR_peak_RAM])
        # csvfile.flush()

if __name__ == '__main__':
    main()