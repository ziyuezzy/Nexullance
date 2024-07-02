# first, try to compute ECMP_ASP for different sizes of DDF under a set of
# traffic demand matrices, then compare "Network throughput per EP"

# Then, calculate the average and standard deviation of the "Network throughput" 
# for different sizes of DDF under the same set of traffic demand matrices.

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.DDF import DDFtopo
import globals as gl
import numpy as np
import csv

# add the path to the Nexullance_IT c++ library
sys.path.append("/users/ziyzhang/topology-research/nexullance/IT_boost/build")
from Nexullance_IT_cpp import Nexullance_IT_interface, MD_Nexullance_IT_interface

Cap_remote = 10 #GBps
Cap_local = 10 #GBps

def main():
    # initialize output data file
    filename = f'DDF.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'EPR', 'traffic', 'Phi', 'Phi_per_EP', 'i_conv'])

        configs = [gl.ddf_configs[0]]
        for V, D in configs:
            # various traffic patterns
            EPR = (D+1)//2

            _network = DDFtopo(V, D)
            arcs = _network.generate_graph_arcs()
            ASP, _ = _network.calculate_all_shortest_paths()
            ECMP_ASP = gl.ECMP(ASP)



            traffic_pattern = "shift_2"
            M_EPs = gl.generate_shift_traffic_pattern(V, EPR, 2)

            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
            M_EPs = traffic_scaling * M_EPs
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local

            # run Nexullance_IT
            nexu_it = Nexullance_IT_interface(V, arcs, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), True)
            nexu_it.set_parameters(4.6419767269134455, 6.593203706205871)
            nexu_it.run()
            Lremote_NEXU = nexu_it.get_max_link_load()
            print("average path length: ",nexu_it.get_average_path_length())

            Phi = gl.network_total_throughput(M_EPs, Lremote_NEXU, max_local_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), nexu_it.get_num_attempts_step_2()])
            csvfile.flush()


            # nexu_it = MD_Nexullance_IT_interface(V, arcs, [gl.convert_M_EPs_to_M_R(M_EPs, V, EPR)], [1.0], True)
            # nexu_it.set_parameters(4.6419767269134455, 6.593203706205871)
            # nexu_it.run()
            # Lremote_NEXU = nexu_it.get_weighted_max_link_load()
            # print("average path length: ",nexu_it.get_average_path_length())

            # Phi = gl.network_total_throughput(M_EPs, Lremote_NEXU, max_local_link_load)
            # csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), nexu_it.get_num_attempts_step_2()])
            # csvfile.flush()


if __name__ == '__main__':
    main()
