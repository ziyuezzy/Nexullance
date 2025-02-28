# TODO: first, try to compute ECMP_ASP for different sizes of DDF under a set of
# traffic demand matrices, then compare "Network throughput per EP"

# Then, calculate the average and standard deviation of the "Network throughput" 
# for different sizes of DDF under the same set of traffic demand matrices.

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.DDF import DDFtopo
from nexullance.Nexullance_MP import Nexullance_MP
import globals as gl
import numpy as np
import csv


Cap_remote = 10 #GBps
Cap_local = 10 #GBps

def main():
    # initialize output data file
    filename = f'DDF.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'EPR', 'traffic', 'Phi', 'Phi_per_EP'])

        configs = gl.ddf_configs
        for V, D in configs:
            # various traffic patterns
            EPR = (D+1)//2

            _network = DDFtopo(V, D)
            ASP, _ = _network.calculate_all_shortest_paths()
            APST4, _ = _network.calculate_all_paths_within_length(4)
            ECMP_ASP = gl.ECMP(ASP)

            traffic_pattern = "uniform"
            M_EPs = gl.generate_uniform_traffic_pattern(V, EPR)
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
            M_EPs = traffic_scaling * M_EPs
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            nexu = Nexullance_MP(_network.nx_graph, APST4, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_remote, 0, False)
            nexu.init_model()
            Lremote_NEXU, _ = nexu.solve()
            Phi = gl.network_total_throughput(M_EPs, Lremote_NEXU, max_local_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR)])
            csvfile.flush()

            traffic_pattern = "nearst-neighbour"
            M_EPs = gl.generate_diagonal_traffic_pattern(V, EPR, 1)
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
            M_EPs = traffic_scaling * M_EPs
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            nexu = Nexullance_MP(_network.nx_graph, APST4, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_remote, 0, False)
            nexu.init_model()
            Lremote_NEXU, _ = nexu.solve()
            Phi = gl.network_total_throughput(M_EPs, Lremote_NEXU, max_local_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR)])
            csvfile.flush()

            traffic_pattern = "shift_1"
            M_EPs = gl.generate_shift_traffic_pattern(V, EPR, 1)
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
            M_EPs = traffic_scaling * M_EPs
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            nexu = Nexullance_MP(_network.nx_graph, APST4, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_remote, 0, False)
            nexu.init_model()
            Lremote_NEXU, _ = nexu.solve()
            Phi = gl.network_total_throughput(M_EPs, Lremote_NEXU, max_local_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR)])
            csvfile.flush()

            traffic_pattern = "shift_half"
            M_EPs = gl.generate_half_shift_traffic_pattern(V, EPR)
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
            M_EPs = traffic_scaling * M_EPs
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            nexu = Nexullance_MP(_network.nx_graph, APST4, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_remote, 0, False)
            nexu.init_model()
            Lremote_NEXU, _ = nexu.solve()
            Phi = gl.network_total_throughput(M_EPs, Lremote_NEXU, max_local_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR)])
            csvfile.flush()

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
            nexu = Nexullance_MP(_network.nx_graph, APST4, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_remote, 0, False)
            nexu.init_model()
            Lremote_NEXU, _ = nexu.solve()
            Phi = gl.network_total_throughput(M_EPs, Lremote_NEXU, max_local_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR)])
            csvfile.flush()

            traffic_pattern = "random-permute"
            M_EPs = gl.generate_random_permutation_pattern(V, EPR, 0)
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
            M_EPs = traffic_scaling * M_EPs
            remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_remote_link_load = np.max(remote_link_flows)/Cap_remote
            max_local_link_load = np.max(local_link_flows)/Cap_local
            nexu = Nexullance_MP(_network.nx_graph, APST4, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_remote, 0, False)
            nexu.init_model()
            Lremote_NEXU, _ = nexu.solve()
            Phi = gl.network_total_throughput(M_EPs, Lremote_NEXU, max_local_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR)])
            csvfile.flush()



if __name__ == '__main__':
    main()
