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
import tracemalloc

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
    MP_APST4, _ = _network.calculate_all_paths_within_length(4)
    ECMP_MP_APST4 = gl.ECMP(MP_APST4)

    M_Rs = []
    M_R_names = []
    M_EPs = []
    ECMP_ASP_Phis = []
    Nexullance_MP_ASPT4_Phis = []
    Nexullance_MP_ASPT4_time = []
    Nexullance_MP_ASPT4_peak_RAM = []
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
        # calculate Phi for ECMP_ASP routing
        remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EP)
        max_remote_link_load = np.max(remote_link_flows)/Cap_remote
        max_local_link_load = np.max(local_link_flows)/Cap_local
        ECMP_ASP_Phi=gl.network_total_throughput(M_EP, max_remote_link_load, max_local_link_load)
        ECMP_ASP_Phis.append(ECMP_ASP_Phi)
        # ==============
        # calculate Phi for Nexullance_MP_APST4 routing
        nexu = Nexullance_MP(_network.nx_graph, MP_APST4, M_R, Cap_remote, 0, False)
        tracemalloc.start()
        start_time = time.time()
        nexu.init_model()
        Lremote_NEXU_MP_APST4, _ = nexu.solve()
        end_time = time.time()
        peak_RAM = tracemalloc.get_traced_memory()[1]
        Nexullance_MP_ASPT4_peak_RAM.append(peak_RAM/1024/1024)
        Nexullance_MP_ASPT4_time.append(end_time-start_time)
        tracemalloc.stop()
        print("shift_",{_shift}, " max remote link load for Nexullance_MP = ", Lremote_NEXU_MP_APST4)
        Phi_NEXU_MP_APST4 = gl.network_total_throughput(M_EP, Lremote_NEXU_MP_APST4, max_local_link_load)
        Nexullance_MP_ASPT4_Phis.append(Phi_NEXU_MP_APST4)
        # ==============
        # calculate Phi for Nexullance_IT routing
        nexu_it = Nexullance_IT_interface(V, arcs, M_R, False)
        tracemalloc.start()
        start_time = time.time()
        nexu_it.run()
        end_time = time.time()
        peak_RAM = tracemalloc.get_traced_memory()[1]
        Nexullance_IT_peak_RAM.append(peak_RAM/1024/1024)
        Nexullance_IT_time.append(end_time-start_time)
        tracemalloc.stop()
        Lremote_NEXU_IT = nexu_it.get_max_link_load()
        print("shift_",{_shift}, " max remote link load for Nexullance_IT = ", Lremote_NEXU_IT)
        Phi_NEXU_IT = gl.network_total_throughput(M_EP, Lremote_NEXU_IT, max_local_link_load)
        Nexullance_IT_Phis.append(Phi_NEXU_IT)

        # ==============
        # manage data
        M_EPs.append(M_EP)
        M_Rs.append(M_R)
        max_local_link_loads.append(max_local_link_load)
        M_R_names.append(f"shift_{_shift}")

    M_R_weights = [1/len(M_Rs) for _ in range(len(M_Rs))]

    # calculate Phi for MD_Nexullance_MP_APST4 routing
    md_nexu = MD_Nexullance_MP(_network.nx_graph, MP_APST4, M_Rs, M_R_weights, Cap_remote, 0, False)
    tracemalloc.start()
    start_time = time.time()
    md_nexu.init_model()
    Lremote_for_MRs, weight_path_dict = md_nexu.solve()
    end_time = time.time()
    MD_peak_RAM = tracemalloc.get_traced_memory()[1]/1024/1024
    MD_time = end_time-start_time
    tracemalloc.stop()

    print("resulting weighted max load from MD_Nexullance_MP_APST4 = ", md_nexu.get_weighted_Max_load())
    print("MD_Nexullance_MP_APST4 computing time = ", MD_time, " s")
    print("MD_Nexullance_MP_APST4 peak RAM = ", MD_peak_RAM, " MB")
    MD_MP_Phis = []
    for i, M_EP in enumerate(M_EPs):
        print("shift_",{_shift}, " max remote link load for MD_Nexullance_IT = ", Lremote_for_MRs[i])
        MD_MP_Phis.append(gl.network_total_throughput(M_EP, Lremote_for_MRs[i], max_local_link_loads[i]))

    # pickle output routing tables
    routing_name = f"MD_NEXU_MP_APST_all_shifts"
    pathdict_file=f"{routing_name}_({V},{D})DDFtopo_paths.pickle"
    with open(pathdict_file, 'wb') as handle:
        pickle.dump(gl.clean_up_weighted_paths(weight_path_dict), handle)
    #====================================
    # calculate Phi for MD_Nexullance_IT routing
    md_nexu_it = MD_Nexullance_IT_interface(V, arcs, M_Rs, M_R_weights, False)
    tracemalloc.start()
    start_time = time.time()
    md_nexu_it.run(4, -1, 20000, True)
    end_time = time.time()
    MD_peak_RAM = tracemalloc.get_traced_memory()[1]/1024/1024
    MD_time = end_time-start_time
    tracemalloc.stop()

    print("resulting weighted max load from MD_Nexullance_IT = ", md_nexu_it.get_weighted_max_link_load())
    print("MD_Nexullance_IT computing time = ", MD_time, " s")
    print("MD_Nexullance_IT peak RAM = ", MD_peak_RAM, " MB")
    Lremote_for_MRs = md_nexu_it.get_max_link_loads()
    MD_IT_Phis = []
    for i, M_EP in enumerate(M_EPs):
        print("shift_",{_shift}, " max remote link load for MD_Nexullance_IT = ", Lremote_for_MRs[i])
        MD_IT_Phis.append(gl.network_total_throughput(M_EP, Lremote_for_MRs[i], max_local_link_loads[i]))

    # pickle output routing tables
    routing_name = f"MD_NEXU_IT_all_shifts"
    pathdict_file=f"{routing_name}_({V},{D})DDFtopo_paths.pickle"
    with open(pathdict_file, 'wb') as handle:
        pickle.dump(gl.clean_up_weighted_paths(md_nexu_it.get_routing_table()), handle)
    #====================================


    filename = f'DDF_{V}_{D}_MD_all_shifts.csv'
    # save data to csv file
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'included_M_R', 'M_R_weight', 'Phi_ECMP_ASP', 
                            'Phi_MP', 'time_MP[s]', 'peak_RAM_MP[MB]',
                            'Phi_IT', 'time_IT[s]', 'peak_RAM_IT[MB]',
                            'Phi_MD_MP', 'MD_MP_to_MP', 
                            'Phi_MD_IT', 'MD_IT_to_IT', 'MD_IT_to_MP'])
        csvfile.flush()
        for i in range(len(M_EPs)):
            csvwriter.writerow([V, D, M_R_names[i], M_R_weights[i], ECMP_ASP_Phis[i], 
                                Nexullance_MP_ASPT4_Phis[i], Nexullance_MP_ASPT4_time[i], Nexullance_MP_ASPT4_peak_RAM[i],
                                Nexullance_IT_Phis[i], Nexullance_IT_time[i], Nexullance_IT_peak_RAM[i],
                                MD_MP_Phis[i], MD_MP_Phis[i]/Nexullance_MP_ASPT4_Phis[i],
                                MD_IT_Phis[i], MD_IT_Phis[i]/Nexullance_IT_Phis[i], MD_IT_Phis[i]/Nexullance_MP_ASPT4_Phis[i]
                                ])

if __name__ == '__main__':
    main()